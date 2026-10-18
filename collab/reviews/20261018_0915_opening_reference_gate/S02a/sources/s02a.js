// 1-3 小满近景（2.5 秒）：脸被手机屏幕照蓝，盯着屏幕。1.0 游戏里差点输——眉毛一挑、嘴抿紧；1.8 躲过去了——嘴角一撇。
import { closeShot, xiaomanFront } from './close.js';
import { key, blink } from './kit.js';
export const DURATION = 2.5;
export function face(t) {
  const f = key(t, [
    [0, { open: 0.85, look: [0, 0.85], brow: 0, worry: 0, smile: 0, frown: 0.15, mouth: 0 }],
    [0.95, { open: 0.85, look: [0, 0.85], brow: 0, worry: 0, smile: 0, frown: 0.15, mouth: 0 }],
    [1.08, { open: 1.15, look: [0.1, 0.9], brow: 0.75, worry: 0.45, smile: -0.35, frown: 0, mouth: 0 }, 'out'],
    [1.7, { open: 1.1, look: [0.1, 0.9], brow: 0.7, worry: 0.4, smile: -0.35, frown: 0, mouth: 0 }],
    [1.9, { open: 0.85, look: [0, 0.85], brow: 0.1, worry: 0, smile: 0.4, frown: 0, mouth: 0 }, 'out'],
    [2.5, { open: 0.85, look: [0, 0.85], brow: 0.1, worry: 0, smile: 0.4, frown: 0, mouth: 0 }],
  ]);
  return { ...f, blink: blink(t, [0.55]) };
}
export function pose(t) {
  const jerk = key(t, [[0.95, 0], [1.08, 1, 'out'], [1.7, 1], [1.95, 0]]);
  const nodBob = 0.04 * Math.sin(t * 9) * (t < 1 ? 1 : 0.3);
  return { head: { nod: 0.55 - 0.25 * jerk + nodBob, tilt: -0.04 + 0.03 * jerk, turn: 0 }, shrug: 0.4 * jerk, face: face(t) };
}
const shot = closeShot({
  bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  layers: async (t) => [xiaomanFront(pose(t), { k: 19, at: [960, 2273] })],
  // 手机在画面下方：一团蓝白的光
  emit: (x, t) => { const g = x.createRadialGradient(960, 1130, 10, 960, 1130, 520); g.addColorStop(0, 'rgba(170,210,255,0.55)'); g.addColorStop(1, 'rgba(170,210,255,0)'); x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(400, 600, 1120, 480); x.restore(); },
  light: () => ({ ambient: [0.42, 0.44, 0.5], lights: [{ x: 960, y: 1250, r: 1100, color: [0.6, 0.78, 1.0], i: 0.75, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.25, falloff: 1.4 }], exposure: 1.0, vignette: 0.35, grain: 5 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
