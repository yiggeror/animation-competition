// 1-5 小满中近景（1.5 秒）：奶奶的手把西瓜推到她跟前（前景、画面右边），她头也不抬，摇一下头，眼睛不离手机。
import { closeShot, xiaomanFront } from './close.js';
import { key, melon } from './kit.js';
export const DURATION = 1.5;
export function pose(t) {
  const turn = key(t, [[0.35, 0], [0.5, -0.28, 'out'], [0.68, 0.24, 'io'], [0.85, 0, 'io']]);
  return { head: { nod: 0.55, turn }, face: { open: 0.85, look: [0, 0.85], smile: -0.15, brow: -0.15, frown: 0.25 } };
}
const shot = closeShot({
  bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  layers: async (t) => [xiaomanFront(pose(t), { k: 11, at: [860, 1760] })],
  light: () => ({ ambient: [0.5, 0.52, 0.58], lights: [{ x: 860, y: 1200, r: 1000, color: [0.6, 0.78, 1.0], i: 0.6, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.3, falloff: 1.4 }], exposure: 1.0, vignette: 0.32, grain: 5 }),
  emit: (x, t) => {
    // 前景：奶奶的手端着西瓜伸进画面（虚焦）
    const s = key(t, [[0, 0], [0.3, 1, 'out']]);
    x.save(); x.filter = 'blur(6px)'; x.translate(1920 + 260 - 560 * s, 900); x.scale(28, 28);
    x.fillStyle = '#e9c3a6'; x.beginPath(); x.ellipse(5, 2, 7, 4, -0.2, 0, 7); x.fill(); x.fillRect(5, 0, 20, 6);
    melon(x, -2, -3, -0.3, 11); x.restore();
  },
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
