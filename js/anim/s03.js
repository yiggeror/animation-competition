// 1-4 奶奶中近景（4 秒）：剥着豆，眼睛先抬起来看小满，头跟着抬、嘴角带笑；拿起一块西瓜往小满那边推过去；手停在那儿等。
import { closeShot, grandmaFront } from './close.js';
import { key, blink, EASE } from './kit.js';
import { ik2 } from '../lib/draw.js';
export const DURATION = 4;
const K = 13, AT = [1010, 1480];
const SH_L = [-14.6, -103.5];   // 奶奶右肩（画面左）
// 肘从"朝外"转到"朝下"：在空间里是绕"肩—手"这条线转半圈，正面看肘先往这条线上收（朝镜头）再从另一边出来，
// 不是一帧里突然翻过去。w = 0 时跟 bend -1 一样，w = 1 时跟 bend +1 一样，所以两头的关键姿势不变。
function swivel(P, hand, w) {
  const a = P.lean || 0, cs = Math.cos(a), sn = Math.sin(a), p = [-14.6, -103.5 + 1.2 + 75];   // 正面奶奶右肩（画面左），绕髋部 (0, -75) 转 lean
  const S = [p[0] * cs - p[1] * sn, -75 + p[0] * sn + p[1] * cs];
  const r = ik2(S, hand, 21.5, 19.5, -1), d = [r.end[0] - S[0], r.end[1] - S[1]], L = Math.hypot(d[0], d[1]), u = [d[0] / L, d[1] / L];
  const c = (r.joint[0] - S[0]) * u[0] + (r.joint[1] - S[1]) * u[1], C = [S[0] + u[0] * c, S[1] + u[1] * c], k = Math.cos(Math.PI * w);
  return { elbow: [C[0] + (r.joint[0] - C[0]) * k, C[1] + (r.joint[1] - C[1]) * k], hand: r.end };
}
function palm(h) { const dx = h[0] - SH_L[0], dy = h[1] - SH_L[1], d = Math.hypot(dx, dy); return [h[0] + dx / d * 5, h[1] + dy / d * 5 + 37 - 3, 0.1, 8.5]; }
export function pose(t) {
  const look = key(t, [[0, [0, 0.6]], [0.4, [0, 0.6]], [0.6, [-0.7, -0.1], 'out'], [4, [-0.7, -0.1]]]);
  const lift = key(t, [[0.55, 0], [1.05, 1, 'io']]);
  const smile = key(t, [[0.7, 0.2], [1.1, 0.5], [3.4, 0.5], [3.9, 0.3]]);
  const brow = key(t, [[2.4, 0], [2.7, 0.35, 'out'], [4, 0.3]]);
  // 右手（画面左）：剥豆 → 豆荚丢回盆 → 往下伸去拿盘里的西瓜 → 端起来往左边推
  // 递瓜：肘往下收，手心朝上托着瓜，往画面左下方送过去（不是肘抬高、瓜挂在腕边）
  const hL = key(t, [[0, [-5, -78]], [0.3, [-4, -79]], [1.0, [-4, -79]], [1.25, [-8, -76]], [1.45, [-8, -76]], [1.8, [-30, -78], 'io'], [1.9, [-30, -78]], [2.35, [-38, -80], 'out'], [4, [-38, -80]]]);
  const hR = key(t, [[0, [6, -79]], [0.3, [5, -80]], [1.0, [5, -80]], [1.4, [9, -77]], [4, [9, -77]]]);
  const melonOn = t >= 1.9;
  return {
    P: { y: 37, seated: true, head: { nod: 0.5 * (1 - lift), turn: -0.3 * lift, tilt: 0.04 * lift }, lean: 0.03 * (1 - lift),
      armL: { ...swivel({ lean: 0.03 * (1 - lift) }, hL, EASE.io(Math.min(1, Math.max(0, (t - 1.45) / 0.35)))), hp: t >= 1.9 ? 'rest' : 'pinch' }, armR: { hand: hR, hp: 'pinch' },
      face: { look, smile, brow, open: 0.9, blink: blink(t, [3.1]) } },
    melonAt: melonOn ? palm(hL) : null,   // 瓜坐在掌心上：手腕沿小臂方向再往前 5 厘米、往上 3 厘米
    plate: melonOn ? null : [-30, -38],                                 // 盘子放在身边的小凳上，取瓜那一下在画面里
  };
}
const shot = closeShot({
  bgKey: 'room_gm', bgCrop: [900, 180, 640, 360], blur: 16,
  layers: async (t) => { const s = pose(t); return [grandmaFront(s.P, { k: K, at: AT, plate: s.plate, melonAt: s.melonAt })]; },
  light: () => ({ ambient: [0.62, 0.66, 0.72], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.55, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.3, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 5 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
