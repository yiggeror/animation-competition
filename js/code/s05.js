// S05 · 第 2 场特写：停电后的手机。开头接 S02 的结尾（推近在电量上）：闪电标志"啵"地消失，2% 变成红色的 1%，一闪一闪；
// 镜头拉开，小满两只拇指狂按，想把这一局打完——屏幕一黑。黑了以后拇指又戳了两下。屋里没灯，只有屏幕发光。
import { renderPhone, thumbAt, sstep, DPAD, JUMP } from './phone.js';
export const DURATION = 4;
const T_OFF = 3.05;
const MASH = []; for (let p = 1.15; p < T_OFF - 0.05; p += 0.14 + 0.03 * Math.sin(p * 13)) MASH.push(p);
const PRESS = [...MASH, 3.4, 3.72];
export function state(t) {
  const R = thumbAt(t, PRESS, [JUMP[0] + 6, JUMP[1] + 4], { ox: 6 * Math.sin(t * 23) * sstep(1.1, 1.3, t) * (t < T_OFF ? 1 : 0) });
  const LP = MASH.filter((_, i) => i % 2).map((p) => p + 0.05);
  const L = thumbAt(t, LP, [DPAD[0] + 10, DPAD[1]], { wiggle: 40 * sstep(1.0, 1.3, t) * (t < T_OFF ? 1 : 0.1), wf: 9 });
  const pull = sstep(0.95, 1.75, t);
  const bolt = t < 0.35 ? 1 : t < 0.47 ? 1 + 0.25 * Math.sin((t - 0.35) / 0.12 * Math.PI) : 0;   // 闪电先胀一下再消失
  const level = t < 0.85 ? 2 : 1;
  const off = t < T_OFF ? 1 : t < T_OFF + 0.08 ? 0.35 : 0;   // 先暗一下，再全黑
  const shake = sstep(1.1, 1.3, t) * (t < T_OFF ? 1 : 0);
  return {
    t, light: 'dark', screenOn: off,
    cam: { x: 1290 - 330 * pull, y: 335 + 225 * pull, zoom: 1.8 - 0.8 * pull },
    phone: { x: 960 + 5 * shake * Math.sin(t * 31), y: 560 + 4 * shake * Math.sin(t * 27), rot: -0.035 + 0.01 * shake * Math.sin(t * 17) },
    game: { t: t + 7, jumps: MASH.filter((_, i) => i % 3 === 0).map((p) => p + 7), dpadPressed: L.pressed || shake > 0.5, jumpPressed: R.pressed },
    status: { level, bolt: Math.max(0, bolt), blink: level <= 1 },
    hands: { L, R },
  };
}
export async function renderFrame(ctx, t, W, H) { renderPhone(ctx, W, H, state(t)); }
export async function render(ctx, arg, W, H) { renderPhone(ctx, W, H, state(+arg || 0)); }
