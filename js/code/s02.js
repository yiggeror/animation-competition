// S02 · 第 1 场特写：俯拍小满横握的手机，正在玩跑酷小游戏，右拇指一下下点起跳；镜头慢慢推向右上角——电量 2%，插着电（闪电标志）。
// 手和手机是合作方画的 anim_02_hands_phone_a（phone_img.js 抠了绿幕、拆出两个拇指）；日光灯在头顶，竹席亮，手机和手在竹席上有一块软影子。
import { renderPhoneImg, pressAt } from './phone_img.js';
import { sstep } from './phone.js';
export const DURATION = 4;
const PRESS = [0.45, 1.35, 2.2, 3.05];
export function state(t) {
  const k = sstep(0.2, 4.0, t);
  // 跳的时候手跟着一歪（小孩玩游戏的习惯）
  const tilt = PRESS.reduce((a, p) => a + 0.008 * Math.exp(-((t - p - 0.2) ** 2) / 0.02), 0);
  const press = pressAt(t, PRESS);
  return {
    t, light: 'fluor', screenOn: 1,
    cam: { x: 836 + (1185 - 836) * k, y: 452 + (232 - 452) * k, zoom: 1.07 + (1.9 - 1.07) * k },
    phone: { dx: 3 * Math.sin(t * 1.3), dy: 2.5 * Math.sin(t * 1.7), rot: tilt + 0.003 * Math.sin(t * 0.9) },
    game: { t: t + 3, jumps: PRESS.map((p) => p + 3), dpadPressed: true, jumpPressed: press > 0.5 },
    status: { level: 2, bolt: 1, blink: false },
    press, dpad: 0.35 * Math.sin(t * 2.6),
  };
}
export async function renderFrame(ctx, t, W, H) { return renderPhoneImg(ctx, W, H, state(t)); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
