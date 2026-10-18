// 1-6 奶奶近景（2 秒）：把西瓜收回来，自己咬一口（0.6 "咔嚓"），嚼着，脸上淡淡的"随你"，眼睛看向别处。
import { closeShot, grandmaFront } from './close.js';
import { key, blink } from './kit.js';
export const DURATION = 2;
const K = 17, AT = [1000, 1700];
export function pose(t) {
  const hand = key(t, [[0, [-30, -88]], [0.4, [-6, -112], 'io'], [0.75, [-6, -112]], [1.1, [-10, -100], 'io'], [2, [-10, -100]]]);
  const mouth = key(t, [[0.35, 0], [0.5, 0.55, 'out'], [0.6, 0.05, 'in'], [2, 0]]);
  const chew = t > 0.7 && t < 1.7 ? 0.28 * Math.max(0, Math.sin((t - 0.7) * Math.PI * 4)) : 0;
  const look = key(t, [[0, [-0.5, 0]], [0.5, [0, 0.2]], [0.9, [0.45, 0.1], 'io'], [2, [0.45, 0.1]]]);
  return {
    P: { y: 37, seated: true, head: { nod: key(t, [[0.3, 0], [0.55, 0.12], [1, 0.05]]), turn: key(t, [[0, -0.25], [0.6, 0], [1.1, 0.15]]) },
      armL: { hand, hp: 'pinch' }, armR: { hand: [9, -77], hp: 'pinch' },
      face: { mouth, puff: chew, look, open: key(t, [[0.8, 0.9], [1.1, 0.68]]), smile: key(t, [[0, 0.3], [0.9, 0.1]]), blink: blink(t, [1.55]) } },
    bite: t > 0.6 ? 1 : 0,
    melonAt: [hand[0] - 3, hand[1] + 37 - 4 + (t > 0.6 ? 2 : 0), 0.3 + 0.9 * key(t, [[0, 0], [0.45, 1]]), 9],
  };
}
const shot = closeShot({
  bgKey: 'room_gm', bgCrop: [900, 180, 640, 360], blur: 16,
  layers: async (t) => { const s = pose(t); return [grandmaFront(s.P, { k: K, at: AT, bowl: false, melonAt: s.melonAt, bite: s.bite })]; },
  light: () => ({ ambient: [0.62, 0.66, 0.72], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.55, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.3, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 5 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
