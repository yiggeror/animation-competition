// 1-1 全景（3.5 秒）：夏夜堂屋，吊扇转、蚊香烟被风吹斜、电视亮着。小满趴在竹席上玩手机，奶奶坐矮凳剥毛豆。
// 节拍：0.5 奶奶掐开豆荚（"啪"），1.5 豆子落盆（"嗒嗒"），2.5 伸手去拿下一个；小满小腿晃两下（0.6、1.8），手一直在按。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC, FAN } from '../paint/shots/s01.js';
import { charLayer, key, kick, bowl, stool, phone } from './kit.js';
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
// 小满（侧面、趴着、头朝右）
export function xiaomanPhone(t, swings = [0.6, 1.8]) {
  let n = 0, f = 0;
  for (const s of swings) { n += key(t, [[s, 0], [s + 0.25, 1, 'out'], [s + 0.55, 0, 'io']]); f += key(t, [[s + 0.15, 0], [s + 0.4, 1, 'out'], [s + 0.7, 0, 'io']]); }
  const tap = Math.sin(t * 26) * 0.4;
  return { y: 36, lean: 1.2, head: { tilt: -0.9 },
    legN: { foot: [-36 + 6 * n, -64 - 6 * n], knee: [-21, -42] }, legF: { foot: [-28 - 5 * f, -68 + 5 * f], knee: [-21, -43] },
    armN: { elbow: [36, -37.5], hand: [49, -50 + tap], hp: 'grip' }, armF: { elbow: [33, -38], hand: [47, -51 - tap], hp: 'grip' },
    face: { look: [0.8, 0.6], smile: 0 } };
}
export const GM_AT = [935, 775], GM_K = 2.77, XM_AT = [540, 670], XM_K = 1.97;
export const gmLayer = (P, t, extra = {}) => charLayer('n', 'side', P, { box: [780, 470, 1060, 790], k: GM_K, at: GM_AT, flip: true,
  before: (x) => stool(x, -2), after: (x) => bowl(x, 24, -47, 26), ...extra });   // 盆放在腿上（道具用地面坐标，不跟 pose.y 走）
export const xmLayer = (P, t, extra = {}) => charLayer('x', 'side', P, { box: [440, 560, 700, 690], k: XM_K, at: XM_AT,
  after: (x) => { phone(x, 50, -15, -0.6, extra.lit ?? 1); }, ...extra });
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => [
    { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
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
