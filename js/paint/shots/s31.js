// S31 · 第 12 场：关灯以后。床单又被后台的马灯照亮。
// A 0～7.5 秒：小满站在床单前（合作方画的 anim_33_xiaoman_flashlight_face v2：正面略左、吐舌头做鬼脸，右手在下巴下面攥着手电，
//   左手举着一根签子；抠图 assets/chars/x31_flashlight_face.png）。承接 S30，手电开镜已经亮着，光从下巴往上照——鬼脸；
//   4.5～7 秒举着乌龟晃一晃。乌龟举在亮着的床单前面，看到的是透光的颜色。
//   图里手电是个灰色的占位短筒：按 S09 那只手电（红筒、镀铬灯头）重画在原来的位置上，灯头朝上、不顶下巴，手指那一层盖在手电上面。
// B 7.5～14 秒：切到床单正面（WebGL 引擎）：鹤跳起来，乌龟从右边爬进来，俩互相点头——又演起来了。笛子回来（audio/build.py）。
import { loadImg } from '../paintshot.js';
import { renderShot } from '../../lamp/s06_key.js';
import { CAM_B } from '../../lamp/shots/shotkit.js';
import { makeTurtle, turtlePose } from '../../lamp/turtle.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, cranePoseOf, mixNeck, craneRods, turtleRods } from '../../lamp/choreo.js';
import { drawPuppet, solve, pointOn } from '../../puppet.js';
export const DURATION = 14;
const T_B = 7.5, T_BOB = 0.6;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const W = 1920, H = 1080;
let TURTLE = null;

// ---------------------------------------------------------------- B：床单正面
function sheet(t, env) {
  TURTLE ||= makeTurtle();
  const u = Math.max(0, t - T_B);
  const walkIn = sstep(0, 3.0, u), stop = sstep(2.8, 3.2, u);
  const tx = 2.35 - 0.6 * walkIn, tz = 0.46;
  const nodT = Math.sin(Math.PI * sstep(4.4, 5.4, u));
  const tPose = turtlePose(u, { facing: -1, walk: 1 - stop, neckOut: 0.3 + 0.5 * stop, headTilt: 0.35 * nodT, rootAngle: 0.04 * Math.sin(u * 3) * (1 - stop) });
  const bob = Math.sin(u * 2 * Math.PI * 0.8);
  const bow = Math.sin(Math.PI * sstep(3.4, 4.4, u));
  let neck = mixNeck(NECK_UP, NECK_LOW, 0.35 + 0.25 * bob);
  neck = mixNeck(neck, NECK_DOWN, 0.8 * bow);
  const root = [1.18 + 0.03 * Math.sin(u * 2 * Math.PI * 0.4), 0.66 + 0.01 * bob];
  return [
    { pup: TURTLE, pose: tPose, root: [tx, tz], dist: 0.004, rods: turtleRods([tx, tz]) },
    { pup: env.crane, pose: cranePoseOf(neck, { mode: 'two' }, 0.04 + 0.05 * bob, 1), root, dist: 0.004, rods: craneRods(env.RODS, root) },
  ];
}
const camB = (t) => { const k = sstep(T_B, DURATION, t); return { ...CAM_B, pos: [CAM_B.pos[0], CAM_B.pos[1] + 0.25 * k, CAM_B.pos[2]] }; };

// ---------------------------------------------------------------- A：小满做鬼脸
// 图（1024×1536）→ 画面：缩放 XS，左上角 (XO, YO)
const XS = 0.78, XO = 250, YO = 60;
// 手电轴：灯头一端（拳头上沿）到尾端（拳头下沿），图像素；筒宽 30
const FL = { top: [471, 581], bot: [486, 713], w: 30 };
const FIST = [[428, 590], [455, 575], [500, 580], [520, 640], [512, 716], [470, 722], [430, 700]];
const isGray = (r, g, b) => { const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return mx - mn < 28 && mx > 70 && mx < 215; };
let XM = null;
async function xm() {
  if (XM) return XM;
  const im = await loadImg('/assets/chars/x31_flashlight_face.png');
  const base = new OffscreenCanvas(im.width, im.height), bx = base.getContext('2d'); bx.drawImage(im, 0, 0);
  // 手指那一层：拳头范围里除了灰色占位筒以外的像素
  const fing = new OffscreenCanvas(im.width, im.height), fx = fing.getContext('2d');
  fx.save(); fx.beginPath(); FIST.forEach(([x, y], i) => (i ? fx.lineTo(x, y) : fx.moveTo(x, y))); fx.closePath(); fx.clip(); fx.drawImage(im, 0, 0); fx.restore();
  const id = fx.getImageData(400, 560, 140, 180), D = id.data;
  for (let i = 0; i < D.length; i += 4) if (isGray(D[i], D[i + 1], D[i + 2])) D[i + 3] = 0;
  // 灰占位筒的尾端比新筒身偏左；只清掉这个局部的灰面/黑色筒底线。
  // 用同一行右侧的原裙料补底，保留彩色手指；新手电仍在手指下合成。
  const tail = new Path2D();
  [[475, 687], [485, 686], [489, 691], [496, 711], [488, 715], [466, 715], [458, 710], [461, 701]].forEach(([x, y], i) => i ? tail.lineTo(x, y) : tail.moveTo(x, y)); tail.closePath();
  const patch = bx.getImageData(450, 680, 60, 40), P = patch.data;
  for (let y = 686; y < 716; y++) for (let x = 458; x < 497; x++) {
    if (!bx.isPointInPath(tail, x + 0.5, y + 0.5)) continue;
    const p = ((y - 680) * 60 + x - 450) * 4;
    if (Math.max(P[p], P[p + 1], P[p + 2]) - Math.min(P[p], P[p + 1], P[p + 2]) >= 65) continue;
    const cloth = ((y - 680) * 60 + 505 - 450) * 4;
    P[p] = P[cloth]; P[p + 1] = P[cloth + 1]; P[p + 2] = P[cloth + 2];
    D[((y - 560) * 140 + x - 400) * 4 + 3] = 0;
  }
  bx.putImageData(patch, 450, 680);
  fx.putImageData(id, 400, 560);
  // 拳头粗遮罩还带进了下方的裙子圆点，曾把新筒尾截成“灰缝 + 悬空黑线”。
  // 沿最后一根手指和掌缘的外侧裁掉这部分衣料，保留前景手指轮廓。
  fx.save(); fx.globalCompositeOperation = 'destination-out'; fx.beginPath();
  [[473, 690], [484, 688], [490, 694], [528, 692], [528, 742], [451, 742], [451, 714], [461, 703]].forEach(([x, y], i) => i ? fx.lineTo(x, y) : fx.moveTo(x, y)); fx.closePath(); fx.fill(); fx.restore();
  return (XM = { im, base, fing });
}
// 手电（S09 那一只）：灯头朝上，镀铬反光碗比筒粗一点
function flashlight(x) {
  const [a, b] = [FL.top, FL.bot], ang = Math.atan2(b[0] - a[0], b[1] - a[1]), len = Math.hypot(b[0] - a[0], b[1] - a[1]);
  x.save(); x.translate(a[0], a[1]); x.rotate(-ang); x.lineJoin = 'round';
  const w = FL.w / 2;
  x.fillStyle = '#c42f28'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 3;
  x.beginPath(); x.rect(-w, 0, 2 * w, len + 4); x.fill(); x.stroke();
  x.fillStyle = 'rgba(255,200,190,0.35)'; x.fillRect(-w + 5, 2, 5, len);
  x.fillStyle = '#2a1d18'; x.beginPath(); x.roundRect(-w + 1, len + 2, 2 * w - 2, 9, 3); x.fill();          // 尾盖
  // 灯头：一截镀铬的颈，再往上张开成反光碗
  const g = x.createLinearGradient(-22, 0, 22, 0); g.addColorStop(0, '#7d8288'); g.addColorStop(0.35, '#eef0f2'); g.addColorStop(0.6, '#b9bec4'); g.addColorStop(1, '#6f747a');
  x.fillStyle = g;
  x.beginPath(); x.moveTo(-w, 2); x.lineTo(-w, -8); x.lineTo(-22, -34); x.lineTo(22, -34); x.lineTo(w, -8); x.lineTo(w, 2); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = '#e9eef5'; x.beginPath(); x.ellipse(0, -34, 22, 4, 0, 0, 7); x.fill(); x.stroke();
  x.restore();
}
const lensAt = () => { const [a, b] = [FL.top, FL.bot], ang = Math.atan2(b[0] - a[0], b[1] - a[1]); return [a[0] - 34 * Math.sin(ang), a[1] - 34 * Math.cos(ang)]; };   // 灯头碗口（手电坐标里的 (0, -34)）
let BG = null;
async function sheetBg() {
  if (BG) return BG;
  // 床单（虚）：用 B 段开头那一帧的床单，低分辨率渲一张再大幅模糊
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const s = new OffscreenCanvas(960, 540), sx = s.getContext('2d');
  await renderShot(sx, T_B, 960, 540, { sheet, cam: { ...CAM_B, pos: [CAM_B.pos[0] - 0.5, CAM_B.pos[1] + 0.3, CAM_B.pos[2]] }, cards: null });
  x.filter = 'blur(14px)'; x.drawImage(s, -40, -30, W + 80, H + 60);
  return (BG = c);
}
// 剧本第 12 场：手电一直亮着，只是此前被日光灯淹没；这里没有再次开灯。
const on = (t) => 1 + 0.03 * Math.sin(t * 37);
async function renderA(ctx, t, w, h) {
  const X = await xm(), bg = await sheetBg();
  const k = w / W;
  ctx.save(); ctx.setTransform(k, 0, 0, k, 0, 0);
  ctx.drawImage(bg, 0, 0);
  // 小满（图坐标里合成）：底图 → 手电 → 手指；再乘她身上的光
  const IW = X.im.width, IH = X.im.height;
  const alb = new OffscreenCanvas(IW, IH), ax = alb.getContext('2d');
  ax.drawImage(X.base, 0, 0); flashlight(ax); ax.drawImage(X.fing, 0, 0);
  const L = new OffscreenCanvas(IW, IH), lx = L.getContext('2d');
  lx.fillStyle = 'rgb(30,26,30)'; lx.fillRect(0, 0, IW, IH);                                // 屋里黑；她背对着亮床单，正面只有床单反过来的一点暖光
  lx.globalCompositeOperation = 'lighter';
  const back = lx.createLinearGradient(IW, 0, 0, 0); back.addColorStop(0, 'rgba(80,52,26,1)'); back.addColorStop(1, 'rgba(26,16,8,1)');
  lx.fillStyle = back; lx.fillRect(0, 0, IW, IH);
  const o = on(t);
  if (o > 0) {
    const le = lensAt();
    // 从下巴底下往上打：下巴、脖子最亮，到眼睛已经暗一半，额头、头发几乎照不到——鬼脸的光
    const g = lx.createRadialGradient(le[0], le[1] - 10, 6, le[0], le[1] - 20, 330);
    g.addColorStop(0, `rgba(255,255,255,${o})`); g.addColorStop(0.18, `rgba(225,235,255,${0.95 * o})`); g.addColorStop(0.5, `rgba(150,165,200,${0.5 * o})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    lx.fillStyle = g; lx.fillRect(0, 0, IW, IH);
  }
  ax.globalCompositeOperation = 'multiply'; ax.drawImage(L, 0, 0);
  ax.globalCompositeOperation = 'destination-in'; ax.drawImage(X.base, 0, 0);   // 底图本来就包含拳头和手电的位置，用它一张当轮廓（连画两张 destination-in 会只剩交集）
  ax.globalCompositeOperation = 'source-over'; flashlightLitTop(ax, o);
  // 轻轻晃（吐舌头做鬼脸的那股劲）
  const sway = 0.012 * Math.sin(t * 2.3), bob = 6 * Math.sin(t * 4.6) * sstep(T_BOB, T_BOB + 0.4, t);
  ctx.save(); ctx.translate(XO + 400, YO + 1400 * XS); ctx.rotate(sway); ctx.translate(-(XO + 400), -(YO + 1400 * XS));
  ctx.translate(XO, YO + bob); ctx.scale(XS, XS);
  // 乌龟：举在亮床单前面，看到透光的颜色（正片叠底到床单上）
  TURTLE ||= makeTurtle();
  const wig = sstep(4.5, 4.8, t) * (1 - sstep(6.8, 7.1, t));
  const tPose = turtlePose(t, { facing: -1, walk: wig, speed: 2.2, neckOut: 0.5 + 0.3 * wig, rootAngle: 0.25 * wig * Math.sin((t - 4.5) * 9) });
  const tsol = solve(TURTLE, tPose), pm = pointOn(TURTLE, tsol, 'shell', [0, 40]);
  const rodTop = [948 + 40 * wig * Math.sin((t - 4.5) * 9), 452 - 14 * wig * Math.abs(Math.sin((t - 4.5) * 9))], TK = 0.85;
  ctx.save(); ctx.globalCompositeOperation = 'multiply';
  ctx.translate(rodTop[0] + pm[0] * TK, rodTop[1] + pm[1] * TK); ctx.scale(TK, -TK); drawPuppet(ctx, TURTLE, tPose, 't'); ctx.restore();
  ctx.strokeStyle = '#2a1d18'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(880, 548); ctx.lineTo(...rodTop); ctx.stroke();
  ctx.drawImage(alb, 0, 0);
  ctx.restore();
  // 手电往上打的光：灯头一团亮、空气里一道淡淡的光
  if (o > 0) {
    const le = lensAt(), p = [XO + le[0] * XS, YO + le[1] * XS + bob];
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], 60); g.addColorStop(0, `rgba(240,246,255,${0.8 * o})`); g.addColorStop(1, 'rgba(240,246,255,0)');
    ctx.fillStyle = g; ctx.fillRect(p[0] - 60, p[1] - 60, 120, 120); ctx.restore();
  }
  // 暗角、颗粒
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.restore();
}
// 灯头碗口自己亮（不被压暗）
function flashlightLitTop(x, o) {
  if (o <= 0) return;
  const le = lensAt(); x.save(); x.globalCompositeOperation = 'lighter';
  x.fillStyle = `rgba(230,238,255,${0.7 * o})`; x.beginPath(); x.ellipse(le[0], le[1], 20, 4, 0, 0, 7); x.fill(); x.restore();
}

export async function renderFrame(ctx, t, w, h) {
  if (t < T_B) return renderA(ctx, t, w, h);
  return renderShot(ctx, t, w, h, { sheet, cam: camB(t), cards: null });
}
export async function render(ctx, arg, w, h) {
  let t = +arg || 0;
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); t = o.t ?? 0; }
  return renderFrame(ctx, t, w, h);
}
