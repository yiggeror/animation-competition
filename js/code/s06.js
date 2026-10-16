// S06 · 第 2 场：墙脚插座特写（月光）。小满的右手拔下充电器，翻过来看看，插回去；没反应——再拔，举起来吹一口，再插；
// 停住，瞪着；最后一次拔出来、往回一收、狠狠插回去（必须停在"插着"的状态，第 10 场手机才能自己充电）。手松开，退出画面。
// 动作时间和 audio/build.py 里 S06 的插头声对齐：1.0 拔、1.8 插、3.0 拔、3.4 吹、3.9 插、6.4 狠插。
// 画法：墙、插座、插头、手都是代码画的平涂 + 深棕线；光是从左上窗口照进来的月光（墙上一块带窗格影子的亮斑），其余是蓝黑。
import { drawHand, POSES, mixPose, orient, shade } from './hand3d.js';
export const DURATION = 8;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;

// 墙（旧石灰墙）+ 踢脚 + 水泥地，缓存
let WALL = null;
function wall() {
  if (WALL) return WALL;
  const c = new OffscreenCanvas(RW, RH), x = c.getContext('2d');
  let seed = 11; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  x.fillStyle = '#d8d0c0'; x.fillRect(0, 0, RW, RH);
  // 斑驳：一层层淡淡的水渍和脏印
  for (let i = 0; i < 70; i++) {
    const cx = rnd() * RW, cy = rnd() * RH * 0.8, r = 40 + rnd() * 220;
    const g = x.createRadialGradient(cx, cy, 0, cx, cy, r);
    const dark = rnd() < 0.6; g.addColorStop(0, dark ? 'rgba(120,105,80,0.10)' : 'rgba(255,250,235,0.10)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(cx - r, cy - r, 2 * r, 2 * r);
  }
  // 墙脚返潮的一道深色
  const g2 = x.createLinearGradient(0, RH * 0.66, 0, RH * 0.8); g2.addColorStop(0, 'rgba(110,95,70,0)'); g2.addColorStop(1, 'rgba(110,95,70,0.28)');
  x.fillStyle = g2; x.fillRect(0, RH * 0.6, RW, RH * 0.2);
  // 细裂纹
  x.strokeStyle = 'rgba(90,75,55,0.35)'; x.lineWidth = 1.5;
  for (let i = 0; i < 6; i++) { let px = rnd() * RW, py = rnd() * RH * 0.6; x.beginPath(); x.moveTo(px, py); for (let k = 0; k < 8; k++) { px += (rnd() - 0.3) * 40; py += rnd() * 30; x.lineTo(px, py); } x.stroke(); }
  // 踢脚线（刷了一道灰绿的漆）和水泥地
  x.fillStyle = '#8f9a8a'; x.fillRect(0, RH * 0.8, RW, RH * 0.06);
  x.strokeStyle = LINE; x.lineWidth = 3; x.beginPath(); x.moveTo(0, RH * 0.8); x.lineTo(RW, RH * 0.8); x.moveTo(0, RH * 0.86); x.lineTo(RW, RH * 0.86); x.stroke();
  x.fillStyle = '#8a8478'; x.fillRect(0, RH * 0.86, RW, RH * 0.14);
  for (let i = 0; i < 400; i++) { x.fillStyle = `rgba(${rnd() < 0.5 ? '60,55,48' : '170,165,150'},0.25)`; x.fillRect(rnd() * RW, RH * 0.86 + rnd() * RH * 0.14, 2 + rnd() * 3, 2); }
  return (WALL = c);
}

// 插座：86 型五孔面板（上面两孔、下面三孔），旧了有点发黄。中心在 (cx, cy)，边长 s
const SOCK = { cx: 1240, cy: 560, s: 300 };
function socket(x) {
  const { cx, cy, s } = SOCK;
  x.save(); x.translate(cx, cy);
  x.fillStyle = 'rgba(0,0,0,0.25)'; x.beginPath(); x.roundRect(-s / 2 + 8, -s / 2 + 12, s, s, 26); x.fill();   // 面板在墙上的一点影子
  x.fillStyle = '#ece6d3'; x.strokeStyle = LINE; x.lineWidth = 4; x.beginPath(); x.roundRect(-s / 2, -s / 2, s, s, 26); x.fill(); x.stroke();
  x.strokeStyle = 'rgba(74,46,31,0.35)'; x.lineWidth = 2; x.beginPath(); x.roundRect(-s / 2 + 18, -s / 2 + 18, s - 36, s - 36, 16); x.stroke();
  x.fillStyle = 'rgba(160,140,90,0.18)'; x.beginPath(); x.ellipse(s * 0.18, s * 0.2, s * 0.3, s * 0.22, 0.4, 0, 7); x.fill();   // 发黄的印子
  x.fillStyle = '#2b2620';
  const slot = (px, py, w, h, a = 0) => { x.save(); x.translate(px, py); x.rotate(a); x.beginPath(); x.roundRect(-w / 2, -h / 2, w, h, 3); x.fill(); x.restore(); };
  slot(-38, -62, 12, 36); slot(38, -62, 12, 36);                                     // 两孔
  slot(0, 22, 12, 34); slot(-44, 70, 12, 34, 0.55); slot(44, 70, 12, 34, -0.55);     // 三孔
  x.restore();
}

// 充电器插头：白色小方块 + 两片铜插脚 + 尾巴上的线。pos 是插头背面中心（画面坐标），d 是离面板多远（像素，0 = 插到底），ang 是转动
const PLUG = { w: 128, h: 104 };
function plug(x, pos, d, ang, L, pinsOut) {
  x.save(); x.translate(pos[0], pos[1]); x.rotate(ang);
  // 插脚（从插头前面伸出，插进去时被面板挡住）
  if (pinsOut > 0) {
    x.fillStyle = shade('#d8b35a', L); x.strokeStyle = LINE; x.lineWidth = 2.5;
    for (const yy of [-38, 38]) { x.beginPath(); x.rect(PLUG.w, yy - 6, Math.min(52, pinsOut), 12); x.fill(); x.stroke(); }
  }
  // 插头身子：前窄后宽一点（有一点立体），亮面 + 背光面
  x.fillStyle = shade('#f1efe8', L); x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(0, -PLUG.h / 2 + 6); x.lineTo(PLUG.w, -PLUG.h / 2); x.lineTo(PLUG.w, PLUG.h / 2); x.lineTo(0, PLUG.h / 2 - 6); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = shade('#c9c5ba', L); x.beginPath(); x.moveTo(0, PLUG.h / 2 - 6); x.lineTo(PLUG.w, PLUG.h / 2); x.lineTo(PLUG.w, PLUG.h / 2 - 22); x.lineTo(0, PLUG.h / 2 - 24); x.closePath(); x.fill();
  x.restore();
}
function cable(x, from, L) {
  // 线从插头背面出来，往左下垂出画面
  const p = new Path2D(); p.moveTo(from[0], from[1]);
  p.bezierCurveTo(from[0] - 120, from[1] + 30, from[0] - 160, from[1] + 260, from[0] - 420, RH + 40);
  x.lineCap = 'round'; x.strokeStyle = LINE; x.lineWidth = 24; x.stroke(p); x.strokeStyle = shade('#efefea', L); x.lineWidth = 16; x.stroke(p);
}

// 插头离面板的距离（像素）和手的状态，随时间
function action(t) {
  let d = 0, lift = 0, turn = 0, shake = 0;
  const pull = (t0, t1, dist) => sstep(t0, t1, t) * dist;
  if (t < 1.0) d = 0;
  else if (t < 1.8) d = pull(1.0, 1.14, 150) * (1 - sstep(1.66, 1.8, t));
  else if (t < 3.0) d = 0;
  else if (t < 3.9) { d = pull(3.0, 3.12, 170) * (1 - sstep(3.78, 3.9, t)); lift = sstep(3.1, 3.32, t) * (1 - sstep(3.5, 3.78, t)); }
  else if (t < 5.6) d = 0;
  else if (t < 6.4) d = pull(5.6, 5.75, 120) + pull(5.85, 6.2, 90) - (210 * sstep(6.26, 6.4, t)) * (t > 6.26 ? 1 : 0);
  d = Math.max(0, d);
  turn = 0.35 * Math.sin(Math.PI * sstep(1.15, 1.65, t));                // 翻过来看看
  turn += 0.04 * Math.sin(t * 40) * sstep(5.0, 5.3, t) * (1 - sstep(5.5, 5.6, t));   // 气得手发抖
  if (t > 6.4) shake = Math.exp(-(t - 6.4) * 9) * Math.sin((t - 6.4) * 60);
  const grip = t < 6.7 ? 1 : 1 - 0.45 * sstep(6.7, 6.95, t);              // 松手（半握着退出去）
  const enter = sstep(-0.1, 0.55, t), leave = sstep(6.8, 7.4, t);
  return { d, lift, turn, shake, grip, enter, leave };
}

export async function renderFrame(ctx, t, W, H) {
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  const A = action(t);
  const camShake = A.shake * 4;
  const Z = 1.5, FX = SOCK.cx - 140, FY = SOCK.cy - 40;                  // 镜头推近，画面中心对着插座偏左
  ctx.translate(RW / 2 + camShake, RH / 2 - camShake * 0.6); ctx.scale(Z, Z); ctx.translate(-FX, -FY);
  // ---- 底：墙
  ctx.drawImage(wall(), 0, 0);
  // ---- 插座、插头（插头从面板左边伸过来：插脚朝右）
  socket(ctx);
  const moon = [0.52, 0.62, 0.86];                                       // 月光里的颜色系数
  const base = [SOCK.cx - 38 - PLUG.w - A.d, SOCK.cy - 62 + 38 - 38];    // 插头背面中心：对准上面两孔
  const lift = A.lift;
  const pos = [base[0] - 150 * lift, base[1] - 230 * lift];
  // 插头的线
  cable(ctx, [pos[0] + 6, pos[1] + 8], moon);
  plug(ctx, [pos[0], pos[1]], A.d, A.turn * 0.6 - 0.25 * lift, moon, A.d + 150 * lift);
  // ---- 手：右手握住插头的后半截，手背朝镜头
  const pose = mixPose(POSES.relaxed, POSES.pinch, A.grip);
  const R = orient(0.35, 0.55, -1.2 + A.turn);
  const px = 38;
  const probe = drawHand(ctx, { dry: true, side: 1, pose, R, at: [0, 0], px, scale: 0.78 });
  // 拇指尖和食指尖的中点捏在插头后半截
  const pinch = [(probe.thumbTip[0] + probe.indexTip[0]) / 2, (probe.thumbTip[1] + probe.indexTip[1]) / 2];
  const gripAt = [pos[0] + 34, pos[1] - 6];
  let at = [gripAt[0] - pinch[0], gripAt[1] - pinch[1]];
  at = [at[0] - (1 - A.enter) * 700 - A.leave * 800, at[1] + (1 - A.enter) * 120 + A.leave * 200];
  drawHand(ctx, { side: 1, pose, R, at, px, scale: 0.78, skin: '#fdc9a7', skinShade: '#e3a283', light: moon, shadeK: 0.9, forearm: 14, lineW: 2.6, shadeA: 0.3 });
  // ---- 月光：左上窗口投下来的一块亮斑（带窗格的影子），其余压成蓝黑
  const lm = new OffscreenCanvas(RW, RH), lx = lm.getContext('2d');
  lx.fillStyle = 'rgb(28,34,52)'; lx.fillRect(0, 0, RW, RH);
  lx.save(); lx.filter = 'blur(26px)';
  lx.fillStyle = 'rgb(255,255,255)';
  const quad = [[760, 130], [1700, 230], [1600, 960], [640, 860]];
  lx.beginPath(); quad.forEach((q, i) => (i ? lx.lineTo(...q) : lx.moveTo(...q))); lx.closePath(); lx.fill();
  lx.fillStyle = 'rgb(40,48,70)';                                          // 窗格的影子：一竖一横
  lx.beginPath(); lx.moveTo(1150, 160); lx.lineTo(1205, 165); lx.lineTo(1120, 930); lx.lineTo(1065, 925); lx.closePath(); lx.fill();
  lx.beginPath(); lx.moveTo(700, 500); lx.lineTo(1650, 590); lx.lineTo(1645, 630); lx.lineTo(695, 540); lx.closePath(); lx.fill();
  lx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(lm, 0, 0); ctx.restore();
  // 冷色调一下，空气里一点灰尘
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  let seed = 5; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 60; i++) {
    const x0 = 700 + rnd() * 900, y0 = 150 + rnd() * 750, ph = rnd() * 6;
    const xx = x0 + 18 * Math.sin(t * 0.4 + ph), yy = y0 + 12 * Math.sin(t * 0.3 + ph * 2);
    ctx.fillStyle = `rgba(150,170,210,${0.08 + 0.08 * rnd()})`; ctx.beginPath(); ctx.arc(xx, yy, 1.5 + rnd() * 2, 0, 7); ctx.fill();
  }
  ctx.restore();
  ctx.restore();
  // 暗角
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  const v = ctx.createRadialGradient(RW * 0.55, RH * 0.5, RH * 0.3, RW * 0.5, RH * 0.5, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 3;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 7; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
