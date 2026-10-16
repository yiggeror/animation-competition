// S02 · 第 1 场特写：俯拍小满横握的手机，正在玩跑酷小游戏，拇指一下下点起跳；镜头慢慢推向右上角——电量 2%，插着电（闪电标志）。
// 日光灯在头顶，竹席亮，手机和手在竹席上有一块软影子。
import { renderPhone, thumbAt, sstep, DPAD, JUMP, RW, RH } from './phone.js';
export const DURATION = 4;
const PRESS = [0.45, 1.35, 2.2, 3.05];
export function state(t) {
  const R = thumbAt(t, PRESS, [JUMP[0] + 6, JUMP[1] + 4]);
  const L = thumbAt(t, [], [DPAD[0] + 10, DPAD[1]], { wiggle: 26, wf: 2.6, hover: 0.25 });
  const k = sstep(0.2, 4.0, t);
  // 跳的时候手跟着一歪（小孩玩游戏的习惯）
  const tilt = PRESS.reduce((a, p) => a + 0.012 * Math.exp(-((t - p - 0.2) ** 2) / 0.02), 0);
  return {
    t, light: 'fluor', screenOn: 1,
    cam: { x: 960 + 330 * k, y: 560 - 225 * k, zoom: 1.0 + 0.8 * k },
    phone: { x: 960 + 4 * Math.sin(t * 1.3), y: 560 + 3 * Math.sin(t * 1.7), rot: -0.035 + tilt + 0.004 * Math.sin(t * 0.9) },
    game: { t: t + 3, jumps: PRESS.map((p) => p + 3), dpadPressed: true, jumpPressed: R.pressed },
    status: { level: 2, bolt: 1, blink: false },
    hands: { L, R },
  };
}
export async function renderFrame(ctx, t, W, H) { renderPhone(ctx, W, H, state(t)); }
export async function render(ctx, arg, W, H) { renderPhone(ctx, W, H, state(+arg || 0)); }
