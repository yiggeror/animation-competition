// S03 · 第 1 场：中近景，奶奶拿着一块西瓜，看一眼趴在竹席上玩手机的小满（画外左边），把瓜往前递了递，又收回来自己咬一口、嚼。
// 停电前：日光灯的冷白光从头顶照下来，左边电视的光一闪一闪地打在她脸上；背景是虚掉的屋子（bg_01 后墙一带）。镜头慢慢推近。
import { renderPaint, loadImg } from '../paintshot.js';
import { flipLayer, flipNrm } from '../../rig/flipbook.js';
export const DURATION = 6;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
let BG = null;
async function bg() {
  if (BG) return BG;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.filter = 'blur(16px)'; x.drawImage(im, 900, 180, 640, 360, -80, -60, 2080, 1200);   // 后墙、鹤画、条案一带
  return (BG = c);
}
// 电视的光：一闪一闪（画面切换）
const tv = (t) => 0.55 + 0.25 * Math.sin(t * 3.1) + 0.2 * Math.sin(t * 7.7 + 1) + (Math.sin(t * 1.3) > 0.85 ? 0.3 : 0);
const shot = {
  size: [1920, 1080],
  layers: async (t) => {
    // 逐帧：看小满 → 递瓜 → 收回 → 咬（3.8 秒脆响）→ 退瓜 → 嚼（assets/flips/g03_watermelon.flip.json）；不再整张图摇摆
    return [{ img: await flipLayer('g03_watermelon', t), nrm: await flipNrm('g03_watermelon', t), x: 560, y: 70, sc: 0.86 }];
  },
  light: (t) => ({
    ambient: [0.62, 0.66, 0.72],
    lights: [
      { x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.55, falloff: 1.2 },       // 头顶的日光灯
      { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.35 * tv(t), falloff: 1.5 },   // 左边电视
    ],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  glow: () => [],
  // 镜头中心从 540 起、随推近上移到 520：原来一开始就在 520，背景画布只有 1080 高，开头顶上露出约 20 像素黑边
  cam: (t) => { const k = sstep(0, 6, t), z = 1 + 0.06 * k; return { x: 960 + 40 * k, y: 540 - 20 * k, fit: z }; },
};
export async function renderFrame(ctx, t, W, H) { shot.bg = await bg(); return renderPaint(ctx, t, W, H, shot); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
