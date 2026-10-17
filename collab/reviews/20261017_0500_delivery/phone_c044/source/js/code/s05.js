// S05 · 第 2 场特写：停电后的手机。开头接 S02 的结尾（推近在电量上）：闪电标志"啵"地消失，2% 变成红色的 1%，一闪一闪；
// 镜头拉开，小满两只拇指狂按，想把这一局打完——屏幕一黑。黑了以后右拇指又戳了两下。屋里没灯，只有屏幕发光。
// 手和手机同 S02（phone_img.js，合作方画的 anim_02_hands_phone_a）。
import { renderPhoneImg, pressAt } from './phone_img.js';
import { sstep } from './phone.js';
export const DURATION = 4;
const T_OFF = 3.05;
const MASH = []; for (let p = 1.15; p < T_OFF - 0.05; p += 0.14 + 0.03 * Math.sin(p * 13)) MASH.push(p);
const PRESS = [...MASH, 3.4, 3.72];
export function state(t) {
  const pull = sstep(0.95, 1.75, t);
  const bolt = t < 0.35 ? 1 : t < 0.47 ? 1 + 0.25 * Math.sin((t - 0.35) / 0.12 * Math.PI) : 0;   // 闪电先胀一下再消失
  const level = t < 0.85 ? 2 : 1;
  const off = t < T_OFF ? 1 : t < T_OFF + 0.08 ? 0.35 : 0;   // 先暗一下，再全黑
  const shake = sstep(1.1, 1.3, t) * (t < T_OFF ? 1 : 0);
  const press = pressAt(t, PRESS);
  // 左拇指在方向键上来回猛搓；屏幕黑了以后慢下来、停住
  const dpad = shake * 0.9 * Math.sin(t * 2 * Math.PI * 3.4) + (1 - shake) * 0.2 * Math.sin(t * 2.2) * (t < T_OFF ? 1 : 0.3);
  return {
    t, light: 'dark', screenOn: off,
    cam: { x: 1185 - (1185 - 836) * pull, y: 232 + (452 - 232) * pull, zoom: 1.9 - (1.9 - 1.07) * pull },
    phone: { dx: 4 * shake * Math.sin(t * 31), dy: 3 * shake * Math.sin(t * 27), rot: 0.006 * shake * Math.sin(t * 17) },
    game: { t: t + 7, jumps: MASH.filter((_, i) => i % 3 === 0).map((p) => p + 7), dpadPressed: Math.abs(dpad) > 0.5 || shake > 0.5, jumpPressed: press > 0.5 },
    status: { level, bolt: Math.max(0, bolt), blink: level <= 1 },
    press, dpad,
  };
}
export async function renderFrame(ctx, t, W, H) { return renderPhoneImg(ctx, W, H, state(t)); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
