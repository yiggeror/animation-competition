// 2-4 小满近景（2.5 秒）：屏幕一黑，脸也跟着黑了（只剩月光）。0.3 愣住，眼睛瞪大；1.0 "不是吧"——嘴张开、眉头皱起；1.8 猛按电源键（肩一顶）。
import { closeShot, xiaomanFront } from './close.js';
import { key, blink } from './kit.js';
export const DURATION = 2.5;
export function pose(t) {
  const f = key(t, [
    [0, { open: 0.85, look: [0, 0.85], brow: 0.1, worry: 0, mouth: 0, frown: 0, smile: 0.1 }],
    [0.25, { open: 0.85, look: [0, 0.85], brow: 0.1, worry: 0, mouth: 0, frown: 0, smile: 0.1 }],
    [0.4, { open: 1.3, look: [0, 0.6], brow: 0.8, worry: 0, mouth: 0.1, frown: 0, smile: 0 }, 'out'],
    [0.95, { open: 1.3, look: [0, 0.6], brow: 0.8, worry: 0, mouth: 0.1, frown: 0, smile: 0 }],
    [1.15, { open: 1.0, look: [0, 0.75], brow: 0.3, worry: 0.9, mouth: 0.55, frown: 0, smile: -0.4 }, 'out'],
    [2.5, { open: 1.0, look: [0, 0.75], brow: 0.3, worry: 0.9, mouth: 0.3, frown: 0, smile: -0.4 }],
  ]);
  const jab = key(t, [[1.75, 0], [1.85, 1, 'out'], [2.0, 0.2], [2.1, 1, 'out'], [2.3, 0.2]]);
  return { head: { nod: key(t, [[0.25, 0.55], [0.4, 0.3, 'out'], [1.1, 0.45]]) + 0.06 * jab, tilt: key(t, [[0.95, 0], [1.15, 0.08]]) }, shrug: 0.6 * jab, face: { ...f, blink: blink(t, [1.55]) } };
}
const shot = closeShot({
  bgKey: 'room_low_dark', bgCrop: [200, 300, 900, 420], blur: 18,
  layers: async (t) => [xiaomanFront(pose(t), { k: 14, at: [960, 1940] })],
  light: () => ({ ambient: [0.1, 0.12, 0.18], lights: [], shafts: [{ poly: [[0, 0], [700, 0], [1400, 1080], [0, 1080]], color: [0.5, 0.62, 0.95], i: 0.35, soft: 120 }], exposure: 1.0, vignette: 0.5, grain: 8 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
