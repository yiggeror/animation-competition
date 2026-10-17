// S04 · 第 2 场：停电。
// A 0～2.6 秒：电视特写（屋子底图 bg_01 里的老电视），日光灯下屏幕放着动画片；0.6 秒"啪"——日光灯灭，
//   显像管的画面先压成一道亮横线、再缩成一个亮点，慢慢熄掉；屋里一下子黑成月光的蓝。
// B 2.6～8 秒：切回 S01 的全景，屋里黑成月光的蓝：吊扇越转越慢、扇叶一片片看得清了；小满手里的手机还亮着，照着她的脸；
//   奶奶停下手里的豆子坐在暗里；月光从左边窗口斜进来。
// 吊扇减速和 audio/build.py 的吊扇声一样按 exp(-(t-0.6)/2.2) 衰减。
import { renderPaint, loadImg } from '../paintshot.js';
import { flipLayer, flipNrm } from '../../rig/flipbook.js';
import { GM, XM, COIL, FAN, COILC, SHADOWS } from './s01.js';
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

// ---------------------------------------------------------------- B：全景，黑下来的堂屋（同 S01 的机位和人）
const BW = 1672, BH = 941;
// 扇叶转过的角度：断电前每秒 3.5 圈，断电后按 2.2 秒的时间常数减速
const OMEGA = 2 * Math.PI * 3.5, TAU = 2.2;
const fanAng = (t) => (t < T_CUT ? OMEGA * t : OMEGA * T_CUT + OMEGA * TAU * (1 - Math.exp(-(t - T_CUT) / TAU)));
const fanSpeed = (t) => (t < T_CUT ? OMEGA : OMEGA * Math.exp(-(t - T_CUT) / TAU));
// 吊扇的三片扇叶（侧面看，压扁的椭圆轨迹）；转得快时拖残影
function blades(t) {
  const c = new OffscreenCanvas(BW, BH), x = c.getContext('2d');
  const a0 = fanAng(t), smear = Math.min(1.4, fanSpeed(t) / 24), N = smear > 0.04 ? 8 : 1;
  x.translate(FAN[0], FAN[1] + 12);
  for (let b = 0; b < 3; b++) for (let s2 = 0; s2 < N; s2++) {
    const a = a0 + b * 2 * Math.PI / 3 - smear * s2 / N, cx = Math.cos(a), sy = Math.sin(a) * 0.14;
    x.globalAlpha = N > 1 ? 1.6 / N : 1; x.fillStyle = '#d8cfb6'; x.strokeStyle = '#3e2a1e'; x.lineWidth = N > 1 ? 0 : 1.5;
    x.beginPath(); x.moveTo(cx * 40, sy * 40 - 3); x.lineTo(cx * 175, sy * 175 - 5); x.lineTo(cx * 175, sy * 175 + 5); x.lineTo(cx * 40, sy * 40 + 3); x.closePath(); x.fill(); if (N === 1) x.stroke();
  }
  return c;
}
const PHONE = [XM.x + 1428 * XM.sc, XM.y + 560 * XM.sc];          // 小满手里的手机（底图坐标）
const shotB = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    return [
      { img: SHADOWS, x: 0, y: 0, sc: 1, alpha: 0.4 },
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      { img: await flipLayer('x01_prone_phone_s04', t, 'x01_prone_phone'), nrm: await flipNrm('x01_prone_phone_s04', t), x: XM.x, y: XM.y, sc: XM.sc },   // 逐帧，和 S01 同一组图、本镜自己的时间表
      { img: await flipLayer('g01_beans_s04', t, 'g01_beans'), nrm: await flipNrm('g01_beans_s04', t), x: GM.x, y: GM.y, sc: GM.sc, ox: 304, oy: 1348 },   // 奶奶：灭灯后停下手里的豆子，抬头看
      { img: blades(t), x: 0, y: 0, sc: 1 },
    ];
  },
  light: (t) => ({
    ambient: [0.022, 0.026, 0.045],
    lights: [{ x: PHONE[0], y: PHONE[1] - 6, r: 130, color: [0.6, 0.75, 1.0], i: 1.1, falloff: 1.8 }],     // 小满的手机还亮着
    shafts: [{ poly: [[0, 170], [150, 120], [760, 760], [330, 941], [0, 941]], color: [0.5, 0.62, 0.95], i: 0.3 * moon(t), soft: 70 }],   // 窗口进来的月光
    exposure: 1.0, vignette: 0.5, grain: 8,
  }),
  glow: (t) => [{ x: PHONE[0], y: PHONE[1], r: 26, color: [170, 205, 255], a: 0.7, core: 0.3 }, { x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  cam: (t) => { const k = sstep(T_B, 8, t); return { x: BW / 2 - 40, y: BH / 2 + 20, fit: 1.08 + 0.04 * k }; },
};

export async function renderFrame(ctx, t, w, h) {
  if (t < T_B) { shotA.bg = await tvBg(); return renderPaint(ctx, t, w, h, shotA); }
  return renderPaint(ctx, t, w, h, shotB);
}
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
