// 1-4 奶奶中近景（4 秒）：剥着豆，眼睛先抬起来看小满，头跟着抬、嘴角带笑；拿起一块西瓜往小满那边推过去；手停在那儿等。
import { closeShot, grandmaFront } from './close.js';
import { key, blink } from './kit.js';
export const DURATION = 4;
const K = 13, AT = [1010, 1480];
export function pose(t) {
  const look = key(t, [[0, [0, 0.6]], [0.4, [0, 0.6]], [0.6, [-0.7, -0.1], 'out'], [4, [-0.7, -0.1]]]);
  const lift = key(t, [[0.55, 0], [1.05, 1, 'io']]);
  const smile = key(t, [[0.7, 0.2], [1.1, 0.5], [3.4, 0.5], [3.9, 0.3]]);
  const brow = key(t, [[2.4, 0], [2.7, 0.35, 'out'], [4, 0.3]]);
  // 右手（画面左）：剥豆 → 豆荚丢回盆 → 往下伸去拿盘里的西瓜 → 端起来往左边推
  const hL = key(t, [[0, [-5, -78]], [0.3, [-4, -79]], [1.0, [-4, -79]], [1.25, [-8, -76]], [1.45, [-8, -76]], [1.8, [-30, -70], 'io'], [1.9, [-30, -70]], [2.35, [-40, -86], 'out'], [4, [-40, -86]]]);
  const hR = key(t, [[0, [6, -79]], [0.3, [5, -80]], [1.0, [5, -80]], [1.4, [9, -77]], [4, [9, -77]]]);
  const melonOn = t >= 1.9;
  return {
    P: { y: 37, seated: true, head: { nod: 0.5 * (1 - lift), turn: -0.3 * lift, tilt: 0.04 * lift }, lean: 0.03 * (1 - lift),
      armL: { hand: hL, hp: 'pinch' }, armR: { hand: hR, hp: 'pinch' },
      face: { look, smile, brow, open: 0.9, blink: blink(t, [3.1]) } },
    melonAt: melonOn ? [hL[0] - 3, hL[1] + 37 - 4, 0.3, 9] : null,
    plate: melonOn ? null : [-30, -30],
  };
}
const shot = closeShot({
  bgKey: 'room_gm', bgCrop: [900, 180, 640, 360], blur: 16,
  layers: async (t) => { const s = pose(t); return [grandmaFront(s.P, { k: K, at: AT, plate: s.plate, melonAt: s.melonAt })]; },
  light: () => ({ ambient: [0.62, 0.66, 0.72], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.55, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.3, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 5 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
