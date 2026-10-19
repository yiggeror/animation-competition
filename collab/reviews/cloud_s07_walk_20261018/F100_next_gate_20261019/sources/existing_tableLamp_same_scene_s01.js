// 1-1 全景（3.5 秒）：夏夜堂屋，吊扇转、蚊香烟被风吹斜、电视亮着。小满趴在竹席上玩手机，奶奶坐矮凳剥毛豆。
// 节拍：0.5 奶奶掐开豆荚（"啪"），1.5 豆子落盆（"嗒嗒"），2.5 伸手去拿下一个；小满小腿晃两下（0.6、1.8），手一直在按。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC, FAN } from '../paint/shots/s01.js';
import { lamp as drawLamp, LX, LB } from '../code/s08.js';
import { charLayer, key, kick, bowl, stool, legFK, XM_LEG, shoulderSide, ARM } from './kit.js';
export const DURATION = 3.5;
const BW = 1672, BH = 941;
const tv = (t) => 0.3 + 0.12 * Math.sin(t * 3.1) + 0.08 * Math.sin(t * 7.7 + 1) + (Math.sin(t * 1.3) > 0.85 ? 0.15 : 0);
// 奶奶（侧面、坐着、面朝左）
export function grandmaPeel(t) {
  const hn = key(t, [[0, [27, -82]], [0.42, [27, -82]], [0.5, [31, -80], 'out'], [1.1, [31, -80]], [1.35, [29, -76]], [1.7, [29, -76]], [2.3, [27, -81]], [2.6, [35, -70], 'io'], [3.5, [35, -70]]]);
  const hf = key(t, [[0, [24, -84]], [0.42, [24, -84]], [0.5, [20, -85], 'out'], [1.1, [20, -85]], [1.35, [22, -80]], [1.7, [22, -80]], [2.3, [24, -84]], [3.5, [24, -84]]]);
  return { y: 37, seated: true, lean: 0.3 + 0.02 * kick(t, 0.5, 1, 4, 0.4), head: { nod: 0.45, tilt: -0.18 },
    armN: { hand: hn, hp: 'pinch' }, armF: { hand: hf, hp: 'pinch' }, legN: { foot: [33, -41.6] }, legF: { foot: [29, -41.6] } };
}
// 小满（侧面、趴着、头朝右，手肘撑在竹席上）。骨头长度固定：大腿贴着席子，小腿绕膝盖往上翘；上臂从肩膀落到席子上的肘，小臂往前端着手机。
// o.lean 上身抬多高（1.42 ≈ 胸口离席几厘米），o.fa 小臂角度（负 = 往上抬），o.shinN / o.shinF 小腿角度（-π/2 = 竖直朝上）。
export const XM_FLOOR = -36;                 // 趴着时 pose.y = 36，席面在人物坐标 y = -36
export function xmProne(o = {}) {
  const P = { y: 36, lean: o.lean ?? 1.42, head: { tilt: -0.85, ...(o.head || {}) } };
  const legs = {};
  for (const [sd, hip, sh] of [['N', XM_LEG.hipN, o.shinN ?? -2.25], ['F', XM_LEG.hipF, o.shinF ?? -2.35]]) {
    const r = legFK(hip, Math.PI - 0.2, sh, XM_LEG.thigh, XM_LEG.shin);
    legs['leg' + sd] = { knee: r.knee, foot: r.foot, footRot: sh - Math.PI / 2 + 0.9 };   // 脚背顺着小腿往后绷
  }
  const arms = {};
  for (const [sd, fa] of [['N', (o.fa ?? -0.6) + (o.tapN ?? 0)], ['F', (o.fa ?? -0.6) - 0.06 + (o.tapF ?? 0)]]) {
    const S = shoulderSide('x', P, sd), ey = XM_FLOOR - 1.8;                       // 肘落在席面上
    const e = Math.asin(Math.min(1, (ey - S[1]) / ARM.x[0])), E = [S[0] + Math.cos(e) * ARM.x[0], ey];
    const Wp = [E[0] + Math.cos(fa) * ARM.x[1], E[1] + Math.sin(fa) * ARM.x[1]];
    arms['arm' + sd] = { elbow: E, hand: Wp, hp: o.hp || 'grip', ...(o['arm' + sd] || {}) };
  }
  const W = arms.armN.hand, fa = o.fa ?? -0.6;
  return { ...P, ...legs, ...arms, face: { look: [0.8, 0.6], smile: 0, ...(o.face || {}) },
    phoneAt: [W[0] + Math.cos(fa) * 3, W[1] + Math.sin(fa) * 3 - XM_FLOOR, -0.12] };   // 手机：地面坐标，屏幕朝她的脸（侧面看是一条薄片）
}
export function xiaomanPhone(t, swings = [0.6, 1.8]) {
  let n = 0, f = 0;
  for (const s of swings) { n += key(t, [[s, 0], [s + 0.25, 1, 'out'], [s + 0.55, 0, 'io']]); f += key(t, [[s + 0.15, 0], [s + 0.4, 1, 'out'], [s + 0.7, 0, 'io']]); }
  const tap = Math.sin(t * 26) * 0.05;
  return xmProne({ shinN: -2.25 + 0.5 * n, shinF: -2.35 + 0.45 * f, tapN: tap, tapF: -tap });
}
// 侧面看的手机：一条薄片，屏幕那面朝上（朝她的脸）
export function phoneSide(x, at, lit = 1) {
  x.save(); x.translate(at[0], at[1]); x.rotate(at[2] || 0);
  x.fillStyle = '#1f1f24'; x.strokeStyle = '#111'; x.lineWidth = 0.3; x.beginPath(); x.roundRect(-6.5, -0.7, 13, 1.4, 0.5); x.fill(); x.stroke();
  if (lit > 0) { x.fillStyle = `rgba(150,200,255,${0.9 * lit})`; x.fillRect(-6, -0.8, 12, 0.4); }
  x.restore();
}
// 八仙桌（画面右下）上放着的马灯和火柴盒：开场就摆在那儿，停电后奶奶走过去拿（S07），下一镜点亮（S08）。lift = 被拿起来多少（像素）
export const LAMP_AT = [1262, 642], LAMP_S = 0.17;
export function tableLamp(lift = 0) {
  const c = new OffscreenCanvas(220, 200), x = c.getContext('2d');
  x.translate(110, 170 - lift); x.scale(-LAMP_S, LAMP_S); x.translate(-LX, -LB); drawLamp(x, 0, false);
  x.setTransform(1, 0, 0, 1, 0, 0); x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 1; x.beginPath(); x.rect(150, 162, 18, 7); x.fill(); x.stroke();   // 火柴盒
  return { img: c, x: LAMP_AT[0] - 110, y: LAMP_AT[1] - 170, sc: 1 };
}
export const GM_AT = [935, 775], GM_K = 2.77, XM_AT = [540, 670], XM_K = 1.97;
export const gmLayer = (P, t, extra = {}) => charLayer('n', 'side', P, { box: [780, 470, 1060, 790], k: GM_K, at: GM_AT, flip: true,
  before: (x) => stool(x, -2), after: (x) => bowl(x, 24, -47, 26), ...extra });   // 盆放在腿上（道具用地面坐标，不跟 pose.y 走）
export const xmLayer = (P, t, extra = {}) => charLayer('x', 'side', P, { box: [440, 560, 700, 690], k: XM_K, at: XM_AT,
  after: (x) => { if (P.phoneAt) phoneSide(x, P.phoneAt, extra.lit ?? 1); }, ...extra });
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => [
    { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
    tableLamp(),
    xmLayer(xiaomanPhone(t), t),
    gmLayer(grandmaPeel(t), t),
  ],
  light: (t) => ({
    ambient: [0.64, 0.67, 0.73],
    lights: [
      { x: 780, y: 60, r: 1500, color: [0.94, 0.97, 1.0], i: 0.32, falloff: 1.4 },
      { x: 300, y: 440, r: 700, color: [0.55, 0.7, 1.0], i: tv(t), falloff: 1.6 },
    ],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  glow: (t) => [{ x: 241, y: 418, r: 70, color: [150, 190, 255], a: 0.25 * tv(t), core: 0.5 }, { x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x, t) => {
    x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = `rgba(110,150,210,${0.25 * tv(t)})`; x.beginPath(); x.roundRect(206, 370, 72, 98, 10); x.fill(); x.restore();
    x.save(); x.translate(FAN[0], FAN[1] + 12); x.scale(1, 0.14);
    for (let k = 0; k < 3; k++) { x.fillStyle = 'rgba(225,215,190,0.18)'; x.beginPath(); x.ellipse(0, 0, 175 - k * 4, 175 - k * 4, 0, 0, 7); x.fill(); }
    x.restore();
    // 蚊香的烟：吊扇的风把它吹斜、吹散
    x.save(); x.lineCap = 'round';
    for (let k = 0; k < 3; k++) {
      x.strokeStyle = `rgba(215,215,220,${0.2 - k * 0.055})`; x.lineWidth = 1 + k * 1.5;
      x.beginPath(); const p0 = [COIL[0] - 20, COIL[1] - 1]; x.moveTo(...p0);
      for (let s = 1; s <= 24; s++) { const u = s / 24; x.lineTo(p0[0] + 45 * u * u + 12 * Math.sin(u * 9 - t * 3 + k) * u, p0[1] - 70 * u); }
      x.stroke();
    }
    x.restore();
  },
  cam: (t) => { const k = t / DURATION; return { x: BW / 2 - 20 * k, y: BH / 2 + 12 * k, fit: 1.0 + 0.04 * k }; },
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
