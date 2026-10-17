// S05 · 第 2 场特写：停电后的手机。开头接 S04 的暗屋全景：已经断电7.4秒，充电标志已消失，电量为1%；
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
  // 停电发生在S04 +0.6秒，不能在S05又显示6帧充电或重复一次掉电。
  const bolt = 0;
  const level = 1;
  const off = t < T_OFF ? 1 : t < T_OFF + 0.08 ? 0.35 : 0;   // 先暗一下，再全黑
  const shake = sstep(1.1, 1.3, t) * (t < T_OFF ? 1 : 0);
  // 狂按：每下间隔 0.11～0.17 秒，按下 0.025 + 停 0.035 + 抬 0.04 秒，每下之间都有抬起来的帧
  const press = t < T_OFF ? pressAt(t, MASH, { dn: 0.025, hold: 0.035, up: 0.04 }) : pressAt(t, PRESS.slice(MASH.length));
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
