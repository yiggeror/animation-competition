// S08 试接（10-18 用户："先用上试试吧"）：用户给的那张图（奶奶胸前，左手托火柴盒、右手捏火柴）直接当手部近景。
// 0.2 秒火柴头着火（火苗、火光是代码加的），火光照亮两只手，闪一闪。只是看双手在场景光里的效果，不是 S08 定稿。
import { renderPaint, loadImg } from '../paint/paintshot.js';
import { flameShape } from '../code/s08.js';
export const DURATION = 1.5;
const S = 1920 / 1717, OY = 28, TIP = [938 * S, 624 * S + OY];        // 火柴头（原图 938, 624）
const fl = (t) => 1 + 0.07 * Math.sin(t * 9.3) + 0.05 * Math.sin(t * 17.7) + 0.03 * Math.sin(t * 31);
const m = (t) => (t < 0.2 ? 0 : t < 0.4 ? 1.6 - (t - 0.2) * 3.75 : 0.85 + 0.06 * Math.sin(t * 19));
let BG = null;
async function bg() {
  if (BG) return BG;
  const room = await loadImg('bg_01_room_wide'), c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.filter = 'blur(26px)'; x.drawImage(room, 1000, 200, 600, 340, -80, -60, 2080, 1200);
  return (BG = c);
}
const shot = {
  size: [1920, 1080],
  layers: async () => [{ img: '/assets/chars/g08u/s08_user_hands_scene.png', x: 0, y: OY, sc: S }],
  light: (t) => {
    const k = m(t), L = [];
    if (k > 0) L.push({ x: TIP[0], y: TIP[1] - 30, r: 1100 * (0.85 + 0.2 * k), color: [1.0, 0.64, 0.32], i: (0.7 + 0.5 * k) * fl(t), falloff: 1.8 });
    return { ambient: [0.10, 0.11, 0.16], lights: L, exposure: 1.0, vignette: 0.55, grain: 7 };
  },
  glow: (t) => (m(t) > 0 ? [{ x: TIP[0], y: TIP[1] - 30, r: 160 * (0.7 + 0.4 * m(t)), color: [255, 190, 110], a: 0.5, core: 0.25 }] : []),
  emit: (x, t) => { const k = m(t); if (k > 0) flameShape(x, [TIP[0], TIP[1] + 4], 0.9 * k, t); },
  async render(ctx, t, W, H) { this.bg = await bg(); return renderPaint(ctx, t, W, H, this); },
};
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
