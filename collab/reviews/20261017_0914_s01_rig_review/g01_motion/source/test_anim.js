// 骨架变形的动作试片：node tools/js/frames.cjs js/rig/test_anim.js 输出目录 --fps 24 --w 600 --h 1000 --to 4 --mp4 x.mp4
// 奶奶剥毛豆：两只手一捏一掰（每 1.2 秒一颗），头跟着手低一下，每 4 秒抬眼看一下前面（小满），身子随呼吸起伏
import { loadRig, render as warp } from './warp.js';
export const DURATION = 6;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
export function grandmaBeans(t) {
  const ph = (t % 1.2) / 1.2;                                   // 剥一颗的相位
  const pinch = Math.sin(ph * Math.PI * 2), snap = Math.exp(-Math.pow((ph - 0.55) * 9, 2));
  const look = sstep(0.0, 0.35, (t % 4) - 2.4) * (1 - sstep(0.9, 1.3, (t % 4) - 2.4));   // 抬眼看一眼
  const br = Math.sin(t / 3.6 * 2 * Math.PI);
  return {
    spine: { rot: 0.008 * br - 0.02 * look, sy: 1 + 0.005 * br },
    neck: { rot: 0.02 * snap - 0.05 * look },
    head: { rot: 0.025 * pinch * (1 - look) - 0.07 * look },
    upperarm_near: { rot: 0.02 * pinch }, forearm_near: { rot: 0.05 * pinch + 0.04 * snap }, hand_near: { rot: 0.08 * snap },
    upperarm_far: { rot: -0.015 * pinch }, forearm_far: { rot: -0.04 * pinch - 0.05 * snap }, hand_far: { rot: -0.1 * snap },
  };
}
export async function renderFrame(ctx, t, W, H) {
  const B = await loadRig('g01_beans'), c = warp(B, grandmaBeans(t));
  ctx.fillStyle = '#ddd'; ctx.fillRect(0, 0, W, H);
  const k = Math.min(W / c.width, H / c.height); ctx.drawImage(c, (W - c.width * k) / 2, (H - c.height * k) / 2, c.width * k, c.height * k);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
