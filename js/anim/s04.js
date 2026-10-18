// 2-1 全景（3 秒）：0.3 "啪"——灯灭、电视缩成一个亮点、吊扇慢慢减速，月光从窗口斜进来。
// 0.5 奶奶手停在半空，1.2 抬头看灯；小满一动不动——还在玩（手机还亮着）。这个反差就是笑点。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC, FAN } from '../paint/shots/s01.js';
import { key } from './kit.js';
import { grandmaPeel, xiaomanPhone, gmLayer, xmLayer, XM_AT, XM_K } from './s01.js';
export const DURATION = 3;
const BW = 1672, BH = 941, CUT = 0.3;
const PHONE = [XM_AT[0] + 50 * XM_K, XM_AT[1] - 15 * XM_K];
const fanSpin = (t) => (t < CUT ? 1 : Math.exp(-(t - CUT) / 1.4));
export function grandmaStop(t) {
  const P = grandmaPeel(Math.min(t, 0.45));          // 手停在掐豆荚的那一下
  const up = key(t, [[0.9, 0], [1.25, 0.6, 'out'], [1.4, 1, 'io']]);
  return { ...P, head: { nod: 0.45 - 0.85 * up, tilt: -0.18 - 0.1 * up }, face: { look: [0.3, -0.8 * up], open: 1 + 0.2 * up, mouth: 0.15 * up } };
}
export const darkLight = (t, phoneLit = 1) => ({
  ambient: [0.05, 0.06, 0.09],
  lights: phoneLit > 0 ? [{ x: PHONE[0], y: PHONE[1] - 6, r: 140, color: [0.6, 0.75, 1.0], i: 1.1 * phoneLit, falloff: 1.8 }] : [],
  shafts: [{ poly: [[0, 170], [150, 120], [760, 760], [330, 941], [0, 941]], color: [0.5, 0.62, 0.95], i: 0.38, soft: 70 }],
  exposure: 1.0, vignette: 0.5, grain: 8,
});
const brightLight = { ambient: [0.64, 0.67, 0.73], lights: [{ x: 780, y: 60, r: 1500, color: [0.94, 0.97, 1.0], i: 0.32, falloff: 1.4 }, { x: 300, y: 440, r: 700, color: [0.55, 0.7, 1.0], i: 0.35, falloff: 1.6 }], exposure: 1.0, vignette: 0.3, grain: 5 };
export function fan(x, spin) {
  x.save(); x.translate(FAN[0], FAN[1] + 12); x.scale(1, 0.14);
  if (spin > 0.3) for (let k = 0; k < 3; k++) { x.fillStyle = `rgba(225,215,190,${0.18 * Math.min(1, spin * 1.4)})`; x.beginPath(); x.ellipse(0, 0, 175 - k * 4, 175 - k * 4, 0, 0, 7); x.fill(); }
  else { x.fillStyle = 'rgba(70,60,50,0.8)'; for (let b = 0; b < 3; b++) { const a = b * 2.09 + (1 - spin) * 9; x.save(); x.rotate(a); x.fillRect(40, -5, 135, 10); x.restore(); } }
  x.restore();
}
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => [
    { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
    xmLayer(xiaomanPhone(t, [0.5]), t),
    gmLayer(t < CUT ? grandmaPeel(t) : grandmaStop(t), t),
  ],
  light: (t) => (t < CUT ? brightLight : darkLight(t)),
  glow: (t) => (t < CUT ? [] : [{ x: PHONE[0], y: PHONE[1], r: 26, color: [170, 205, 255], a: 0.7, core: 0.3 }, { x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }]),
  emit: (x, t) => {
    // 电视：灭的一瞬间缩成一个亮点再消失
    if (t < CUT) { x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = 'rgba(110,150,210,0.1)'; x.beginPath(); x.roundRect(206, 370, 72, 98, 10); x.fill(); x.restore(); }
    else { const u = key(t, [[CUT, 0], [CUT + 0.35, 1]]); if (u < 1) { const r = 34 * (1 - u) + 2; x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = `rgba(220,235,255,${1 - u * 0.7})`; x.beginPath(); x.ellipse(242, 419, r, r * (1 - u) + 1.5, 0, 0, 7); x.fill(); x.restore(); } }
    fan(x, fanSpin(t));
  },
  cam: (t) => ({ x: BW / 2 - 20, y: BH / 2 + 12, fit: 1.04 }),
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
