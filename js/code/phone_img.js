// 手机特写（S02、S05）的新画法：用合作方画的 anim_02_hands_phone_a（俯拍、小满两只手横握手机、屏幕是绿幕）。
// 绿幕抠掉，换成程序画的游戏画面（phone.js 的 drawGame / drawStatus）；右拇指（按起跳键）和左拇指（按方向键）各自切成一层，
// 左拇指按方向键时绕指根转一点点；右拇指按起跳键时换成图 B 里落到屏幕上的拇指（key_thumb.py 抠的）。抬着的拇指在屏幕上的影子由程序补。底下是竹席。
// 坐标都是这张图的像素（1672×940），镜头 cam = { x, y, zoom }：画面中心对着图上 (x, y)，zoom 1 = 整张图铺满画面宽。
import { mat, setScreen, drawGame, drawStatus, lit } from './phone.js';
const IW = 1672, IH = 940;
export const SCR = { x0: 325, y0: 166, w: 1018, h: 438 };          // 屏幕在图上的范围（抠绿幕时量的）
// 两个拇指在屏幕上的部分（多边形）和指根（转动中心）
const THUMB_R = { poly: [[1190, 326], [1342, 326], [1342, 530], [1296, 530], [1190, 430]], pivot: [1352, 452] };
const THUMB_L = { poly: [[326, 396], [472, 396], [472, 500], [400, 540], [326, 566]], pivot: [312, 528] };
setScreen(SCR.w, SCR.h, [128, 286], [886, 214]);                   // 方向键、起跳键在两个拇指下面
let IMG = null;
const bmp = async (f) => createImageBitmap(await (await fetch(`/assets/chars/${f}.png`)).blob());
async function img() { return (IMG ||= await bmp('h02_phone')); }
// 按下去的右拇指：合作方的图 B（同一张手，只有右拇指落到屏幕上），tools/key_thumb.py 抠出拇指和贴着的接触影
let THB = null;
async function thumbB() { return (THB ||= { skin: await bmp('h02_thumb_b'), shadow: await bmp('h02_thumb_b_shadow'), region: await bmp('h02_thumb_b_region') }); }

// 一层：整张手图（去掉两个拇指） / 只有一个拇指
function layer(im, keep, cut) {
  const c = new OffscreenCanvas(IW, IH), x = c.getContext('2d');
  x.save();
  if (keep) { x.beginPath(); keep.forEach(([px, py], i) => (i ? x.lineTo(px, py) : x.moveTo(px, py))); x.closePath(); x.clip(); }
  x.drawImage(im, 0, 0); x.restore();
  if (cut) { x.globalCompositeOperation = 'destination-out'; for (const p of cut) { x.beginPath(); p.forEach(([px, py], i) => (i ? x.lineTo(px, py) : x.moveTo(px, py))); x.closePath(); x.fill(); } }
  return c;
}
let LAYERS = null;
async function layers() {
  if (LAYERS) return LAYERS;
  const im = await img();
  const base = layer(im, null, [THUMB_R.poly, THUMB_L.poly]);
  // 按下时用的底图：再挖掉右手那一块（换成图 B 的右手）；遮罩图的亮度当透明度用
  const TB = await thumbB(), rm = new OffscreenCanvas(IW, IH), rx = rm.getContext('2d');
  rx.drawImage(TB.region, 0, 0); const id = rx.getImageData(0, 0, IW, IH), D = id.data; for (let i = 0; i < D.length; i += 4) D[i + 3] = D[i]; rx.putImageData(id, 0, 0);
  const baseB = new OffscreenCanvas(IW, IH), bx = baseB.getContext('2d'); bx.drawImage(base, 0, 0); bx.globalCompositeOperation = 'destination-out'; bx.drawImage(rm, 0, 0);
  return (LAYERS = { base, baseB, tr: layer(im, THUMB_R.poly), tl: layer(im, THUMB_L.poly) });
}
const rotAbout = (x, p, a) => { x.translate(p[0], p[1]); x.rotate(a); x.translate(-p[0], -p[1]); };

// st = { t, light: 'fluor'|'dark', screenOn 0..1, cam, phone:{dx,dy,rot}, game, status, press（右拇指 0..1）, dpad（左拇指 -1..1） }
export async function renderPhoneImg(ctx, W, H, st) {
  const L = await layers(), TB = await thumbB();
  const dark = st.light === 'dark', scr = st.screenOn;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const k = (W / IW) * st.cam.zoom;
  ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.translate(-st.cam.x, -st.cam.y);
  // 竹席 + 环境光
  ctx.save(); ctx.filter = 'blur(2px)'; ctx.drawImage(mat(), -500, -400, 2700, 1770); ctx.restore();
  const amb = dark ? [0.05, 0.06, 0.095] : [0.92, 0.95, 1.0];
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = `rgb(${amb.map((v) => Math.round(255 * Math.pow(v, 1 / 2.2))).join(',')})`; ctx.fillRect(-600, -500, 2900, 1950); ctx.restore();
  // 手机整体（手和手机一起微微晃）
  const P = st.phone;
  ctx.translate(IW / 2 + P.dx, IH / 2 + P.dy); ctx.rotate(P.rot); ctx.translate(-IW / 2, -IH / 2);
  if (!dark) {   // 日光灯在头顶：手机和手在竹席上投一块软影子
    ctx.save(); ctx.translate(18, 26); ctx.filter = 'blur(26px)'; ctx.globalAlpha = 0.45;
    ctx.drawImage(L.base, 0, 0); ctx.restore();
  } else if (scr > 0) {   // 停电：屏幕往外溢的冷光
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createRadialGradient(SCR.x0 + SCR.w / 2, SCR.y0 + SCR.h / 2, 120, SCR.x0 + SCR.w / 2, SCR.y0 + SCR.h / 2, 980);
    g.addColorStop(0, `rgba(70,110,160,${0.5 * scr})`); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(-400, -400, 2500, 1700); ctx.restore();
  }
  // 充电线：从手机左下角（被左手压着）弯出去
  ctx.save(); ctx.lineCap = 'round';
  const cab = new Path2D(); cab.moveTo(360, 610); cab.bezierCurveTo(320, 760, 160, 760, -120, 980);
  ctx.strokeStyle = '#4a2e1f'; ctx.lineWidth = 22; ctx.stroke(cab);
  ctx.strokeStyle = lit('#f2f2ee', dark ? [0.12 + 0.12 * scr, 0.14 + 0.16 * scr, 0.2 + 0.25 * scr] : amb); ctx.lineWidth = 15; ctx.stroke(cab); ctx.restore();
  // 屏幕：游戏画面（亮着时自发光） / 黑屏（反一点光）
  ctx.save();
  const mask = new Path2D(); mask.roundRect(SCR.x0 - 2, SCR.y0 - 2, SCR.w + 4, SCR.h + 4, 34); ctx.clip(mask);
  ctx.translate(SCR.x0, SCR.y0);
  if (scr > 0.001) {
    drawGame(ctx, st.game); drawStatus(ctx, { ...st.status, t: st.t });
    if (scr < 1) { ctx.fillStyle = `rgba(0,0,0,${1 - scr})`; ctx.fillRect(0, 0, SCR.w, SCR.h); }
  } else { ctx.fillStyle = '#060709'; ctx.fillRect(0, 0, SCR.w, SCR.h); }
  ctx.fillStyle = '#0a0a0c'; ctx.beginPath(); ctx.arc(26, SCR.h / 2, 10, 0, 7); ctx.fill();   // 前摄像头挖孔
  const gl = ctx.createLinearGradient(SCR.w * 0.2, 0, SCR.w * 0.55, SCR.h); const ga = scr > 0.001 ? 0.06 : 0.08;
  gl.addColorStop(0, 'rgba(255,255,255,0)'); gl.addColorStop(0.5, `rgba(220,235,255,${ga})`); gl.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = gl; ctx.fillRect(0, 0, SCR.w, SCR.h);
  ctx.restore();
  // 拇指在屏幕上的影子（日光灯在头顶，抬起时影子离得远一点、虚一点）
  // 右拇指：抬着时用 A 的拇指（往下按的半程跟着转一点），按到底（press ≥ 0.5）换成 B 的拇指和它的接触影
  const pr = st.press ?? 0, dp = st.dpad ?? 0, down = pr >= 0.5;
  const aR = -0.09 * Math.min(1, pr * 2), aL = 0.03 * dp;
  if (!dark) {
    ctx.save(); ctx.clip(mask); ctx.filter = `blur(${12 - 6 * pr}px)`; ctx.globalAlpha = 0.3;
    if (!down) { ctx.save(); ctx.translate(-10 + 6 * pr, 16 - 9 * pr); rotAbout(ctx, THUMB_R.pivot, aR); ctx.drawImage(L.tr, 0, 0); ctx.restore(); }
    ctx.save(); ctx.translate(10, 16); rotAbout(ctx, THUMB_L.pivot, aL); ctx.drawImage(L.tl, 0, 0); ctx.restore();
    ctx.restore();
  }
  if (down) { ctx.save(); ctx.clip(mask); ctx.globalAlpha = dark ? 0.2 : 1; ctx.drawImage(TB.shadow, 0, 0); ctx.restore(); }   // 停电时光是屏幕自己发的，只剩一点贴着的接触暗
  // 手（三层），按光照压色：日光灯下原色；停电时只有屏幕的冷光，手成了暗剪影
  const hands = new OffscreenCanvas(IW, IH), hx = hands.getContext('2d');
  hx.drawImage(down ? L.baseB : L.base, 0, 0);
  hx.save(); rotAbout(hx, THUMB_L.pivot, aL); hx.drawImage(L.tl, 0, 0); hx.restore();
  if (down) hx.drawImage(TB.skin, 0, 0);
  else { hx.save(); rotAbout(hx, THUMB_R.pivot, aR); hx.drawImage(L.tr, 0, 0); hx.restore(); }
  if (dark) {
    const m = new OffscreenCanvas(IW, IH); m.getContext('2d').drawImage(hands, 0, 0);   // 三层合起来的轮廓（压色后用它把透明处还原）
    const kk = [0.1 + 0.16 * scr, 0.11 + 0.2 * scr, 0.16 + 0.3 * scr].map((v) => Math.round(255 * Math.pow(v, 1 / 2.2)));
    hx.globalCompositeOperation = 'multiply'; hx.fillStyle = `rgb(${kk.join(',')})`; hx.fillRect(0, 0, IW, IH);
    hx.globalCompositeOperation = 'destination-in'; hx.drawImage(m, 0, 0);
    if (scr > 0) {   // 压在屏幕上的两个拇指离屏幕最近，被照得最亮；往外到手掌、手腕慢慢暗下去
      hx.globalCompositeOperation = 'source-atop';
      for (const p of [[1250, 420], [400, 470]]) {
        const g = hx.createRadialGradient(p[0], p[1], 20, p[0], p[1], 330);
        g.addColorStop(0, `rgba(150,185,225,${0.38 * scr})`); g.addColorStop(1, 'rgba(150,185,225,0)');
        hx.fillStyle = g; hx.fillRect(0, 0, IW, IH);
      }
    }
  }
  ctx.drawImage(hands, 0, 0);
  ctx.restore();
  // 暗角、颗粒
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${dark ? 0.6 : 0.3})`); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let seed = Math.floor(st.t * 24) * 7919 + 17;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (rnd() - 0.5) * 6; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
// 按键：presses 按下的时刻 → 0..1。默认 0.06 秒按下去，停 0.06，0.12 秒抬起来；
// 狂按时用短的（o = { dn, hold, up }），每下之间必须有抬起来的帧（24 帧/秒，一帧 0.042 秒）
export function pressAt(t, presses, o = {}) {
  const dn = o.dn ?? 0.06, hold = o.hold ?? 0.06, up = o.up ?? 0.12;
  let v = 0;
  for (const p of presses) { const u = t - p; if (u > -dn && u < hold + up) v = Math.max(v, u < 0 ? (u + dn) / dn : u < hold ? 1 : 1 - (u - hold) / up); }
  return v;
}
