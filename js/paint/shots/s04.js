// S04 · 第 2 场：停电（临时版：只拍东西，两人一起的全景等小满的图）。
// A 0～2.6 秒：电视特写（屋子底图 bg_01 里的老电视），日光灯下屏幕放着动画片；0.6 秒"啪"——日光灯灭，
//   显像管的画面先压成一道亮横线、再缩成一个亮点，慢慢熄掉；屋里一下子黑成月光的蓝。
// B 2.6～8 秒：从正下方往上看天花板上的吊扇（程序画），断了电越转越慢；旁边的日光灯管黑着；月光从左边窗口斜进来。
// 吊扇减速和 audio/build.py 的吊扇声一样按 exp(-(t-0.6)/2.2) 衰减。
import { renderPaint, loadImg } from '../paintshot.js';
export const DURATION = 8;
const T_CUT = 0.6, T_B = 2.6;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const W = 1920, H = 1080;
const lit = (t) => (t < T_CUT ? 1 : 0);
const moon = (t) => sstep(T_CUT + 0.3, T_CUT + 1.6, t);

// ---------------------------------------------------------------- A：电视
const TV = { src: [60, 320, 340, 191] };                 // 底图里取的范围（x, y, 宽, 高）
const k = W / TV.src[2];
const SCR = [[202, 365], [282, 367], [280, 472], [202, 472]].map(([x, y]) => [(x - TV.src[0]) * k, (y - TV.src[1]) * k]);
let TVBG = null;
async function tvBg() {
  if (TVBG) return TVBG;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(2px)'; x.drawImage(im, ...TV.src, 0, 0, W, TV.src[3] * k); x.filter = 'none';
  return (TVBG = c);
}
// 屏幕：动画片（天、太阳、一只跑来跑去的小东西），扫描线；断电后压成线 → 点 → 熄
function screen(x, t) {
  const [a, b, c, d] = SCR, cx = (a[0] + b[0] + c[0] + d[0]) / 4, cy = (a[1] + b[1] + c[1] + d[1]) / 4;
  const sw = (b[0] - a[0] + c[0] - d[0]) / 2, sh = (d[1] - a[1] + c[1] - b[1]) / 2;
  const u = t - T_CUT;
  let sy = 1, sx = 1, bright = 1, alpha = 1;
  if (u > 0) { sy = Math.max(0.006, 1 - u / 0.1); bright = 1 + 2 * Math.min(1, u / 0.1); if (u > 0.1) { sx = Math.max(0.012, 1 - (u - 0.1) / 0.14); } if (u > 0.24) alpha = Math.max(0, 1 - (u - 0.24) / 1.3); }
  if (alpha <= 0) return;
  x.save(); x.globalAlpha = alpha;
  x.beginPath(); x.roundRect(a[0] + 8, a[1] + 10, sw - 16, sh - 18, 46); x.clip();                 // 显像管玻璃是鼓的、圆角
  if (u > 0.1) x.globalCompositeOperation = 'lighter';
  x.translate(cx, cy); x.scale(sx, sy);
  if (u <= 0.1) {
    const g = x.createLinearGradient(0, -sh / 2, 0, sh / 2); g.addColorStop(0, '#5aa9e6'); g.addColorStop(0.65, '#9fd6f5'); g.addColorStop(0.66, '#7cc56a'); g.addColorStop(1, '#4e9a45');
    x.fillStyle = g; x.fillRect(-sw / 2, -sh / 2, sw, sh);
    x.fillStyle = '#ffe680'; x.beginPath(); x.arc(sw * 0.25, -sh * 0.25, sh * 0.1, 0, 7); x.fill();
    const px = -sw * 0.35 + ((t * 0.35) % 1) * sw * 0.7, hop = Math.abs(Math.sin(t * 7)) * sh * 0.08;
    x.fillStyle = '#ff8a3d'; x.beginPath(); x.ellipse(px, sh * 0.12 - hop, sw * 0.07, sh * 0.06, 0, 0, 7); x.fill();
    x.fillStyle = 'rgba(0,0,0,0.12)'; for (let yy = -sh / 2; yy < sh / 2; yy += 6) x.fillRect(-sw / 2, yy, sw, 2);   // 扫描线
    if (u > 0) { x.fillStyle = `rgba(255,255,255,${Math.min(1, u / 0.1)})`; x.fillRect(-sw / 2, -sh / 2, sw, sh); }
  } else {
    const r = Math.max(sw, sh) * 0.6, g = x.createRadialGradient(0, 0, 0, 0, 0, r); g.addColorStop(0, `rgba(255,255,255,${Math.min(1, bright)})`); g.addColorStop(0.15, 'rgba(220,235,255,0.9)'); g.addColorStop(1, 'rgba(160,190,255,0)');
    x.fillStyle = g; x.fillRect(-sw / 2, -sh / 2, sw, sh);
  }
  x.restore();
}
const shotA = {
  size: [W, H],
  layers: async () => [],
  light: (t) => ({
    ambient: lit(t) ? [0.64, 0.67, 0.72] : [0.025 + 0.02 * moon(t), 0.03 + 0.025 * moon(t), 0.05 + 0.05 * moon(t)],
    lights: [{ x: 1030, y: 560, r: 1100, color: [0.55, 0.7, 1.0], i: t < T_CUT ? 0.35 + 0.1 * Math.sin(t * 9) : Math.max(0, 0.6 * (1 - (t - T_CUT) / 0.5)), falloff: 1.6 }],
    exposure: 1.0, vignette: lit(t) ? 0.3 : 0.5, grain: lit(t) ? 5 : 8,
  }),
  glow: () => [],
  emit: (x, t) => screen(x, t),
  cam: (t) => ({ x: W / 2 + 20 * sstep(0, T_B, t), y: 520, fit: 1.0 + 0.04 * sstep(0, T_B, t) }),
};

// ---------------------------------------------------------------- B：吊扇（从正下方往上看，程序画）
const HUB = [960, 540];
let CEIL = null;
function ceiling() {
  if (CEIL) return CEIL;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  let seed = 17; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  // 望板：一条条木板 + 两根大梁 + 檩条
  for (let y = -40, i = 0; y < H + 40; y += 64, i++) { const v = 0.85 + 0.25 * rnd(); x.fillStyle = `rgb(${Math.round(112 * v)},${Math.round(80 * v)},${Math.round(54 * v)})`; x.fillRect(0, y, W, 62); x.fillStyle = 'rgba(40,25,15,0.6)'; x.fillRect(0, y + 62, W, 2); }
  for (const bx of [330, 1590]) { x.fillStyle = '#5b3d27'; x.fillRect(bx - 70, 0, 140, H); x.strokeStyle = '#3e2a1e'; x.lineWidth = 4; x.strokeRect(bx - 70, -10, 140, H + 20); }
  // 日光灯管（黑着）
  x.save(); x.translate(960, 870); x.rotate(-0.05);
  x.fillStyle = '#d9d6cc'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 4; x.beginPath(); x.roundRect(-520, -34, 1040, 68, 10); x.fill(); x.stroke();
  x.fillStyle = '#eef0ee'; x.beginPath(); x.roundRect(-480, -18, 960, 36, 18); x.fill(); x.stroke();
  x.restore();
  return (CEIL = c);
}
// 扇叶转过的角度：断电前每秒 3.5 圈，断电后按 2.2 秒的时间常数减速
const OMEGA = 2 * Math.PI * 3.5, TAU = 2.2;
const fanAng = (t) => (t < T_CUT ? OMEGA * t : OMEGA * T_CUT + OMEGA * TAU * (1 - Math.exp(-(t - T_CUT) / TAU)));
const fanSpeed = (t) => (t < T_CUT ? OMEGA : OMEGA * Math.exp(-(t - T_CUT) / TAU));
function fan(t) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const a0 = fanAng(t), sp = fanSpeed(t), smear = Math.min(1.4, sp / 24), N = smear > 0.04 ? 8 : 1;
  x.translate(...HUB);
  for (let b = 0; b < 3; b++) for (let s2 = 0; s2 < N; s2++) {
    x.save(); x.rotate(a0 + b * 2 * Math.PI / 3 - smear * s2 / N); x.globalAlpha = N > 1 ? 1.8 / N : 1;
    x.fillStyle = '#4a4a48'; x.fillRect(90, -12, 170, 24);                                         // 铁片叶臂
    x.fillStyle = '#e6dcc2'; x.strokeStyle = '#3e2a1e'; x.lineWidth = N > 1 ? 0 : 4;              // 扇叶：长条、末端圆
    x.beginPath(); x.moveTo(220, -52); x.lineTo(820, -64); x.quadraticCurveTo(880, 0, 820, 64); x.lineTo(220, 52); x.closePath(); x.fill(); if (N === 1) x.stroke();
    x.restore();
  }
  // 电机底盖（米色圆盖 + 一道红线 + 中间的螺丝帽）
  x.globalAlpha = 1; x.fillStyle = '#e8dfc8'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 5; x.beginPath(); x.arc(0, 0, 150, 0, 7); x.fill(); x.stroke();
  x.strokeStyle = '#c4543e'; x.lineWidth = 8; x.beginPath(); x.arc(0, 0, 118, 0, 7); x.stroke();
  x.fillStyle = '#d2c7ac'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 3; x.beginPath(); x.arc(0, 0, 46, 0, 7); x.fill(); x.stroke();
  return c;
}
const shotB = {
  size: [W, H],
  layers: async (t) => [{ img: fan(t), x: 0, y: 0, sc: 1 }],
  light: (t) => ({
    ambient: [0.04, 0.05, 0.09],
    lights: [{ x: -300, y: 400, r: 2300, color: [0.5, 0.62, 0.95], i: 0.6, falloff: 1.4 }],   // 窗口进来的月光
    exposure: 1.0, vignette: 0.55, grain: 8,
  }),
  glow: () => [],
  cam: (t) => ({ x: W / 2, y: H / 2, fit: 1.0 + 0.04 * sstep(T_B, 8, t) }),
};

export async function renderFrame(ctx, t, w, h) {
  if (t < T_B) { shotA.bg = await tvBg(); return renderPaint(ctx, t, w, h, shotA); }
  shotB.bg = ceiling(); return renderPaint(ctx, t, w, h, shotB);
}
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
