// S03 · 第 1 场：中近景，奶奶拿着一块西瓜（合作方画的 anim_03_grandma_watermelon 候选），看一眼趴在竹席上玩手机的小满（画外左边）。
// 停电前：日光灯的冷白光从头顶照下来，左边电视的光一闪一闪地打在她脸上；背景是虚掉的屋子（bg_01 后墙一带）。镜头慢慢推近。
import { renderPaint, loadImg } from '../paintshot.js';
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
    const br = 1 + 0.004 * Math.sin(t * 1.9);
    const look = sstep(1.2, 2.0, t);               // 抬眼看一下小满（整张图往左偏一点点）
    return [{ img: '/assets/chars/g03_watermelon.png', x: 560 - 10 * look, y: 70 + 4 * Math.sin(t * 1.9), sc: 0.86 * br, rot: -0.012 * look }];
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
  cam: (t) => { const z = 1 + 0.06 * sstep(0, 6, t); return { x: 960 + 40 * sstep(0, 6, t), y: 520, fit: z }; },
};
export async function renderFrame(ctx, t, W, H) { shot.bg = await bg(); return renderPaint(ctx, t, W, H, shot); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
