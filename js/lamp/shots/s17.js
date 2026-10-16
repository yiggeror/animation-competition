// S17 · 第 7 场：乌龟从右边爬进来；鹤低头去啄，乌龟一缩头——啄了个空；再啄，一头撞在龟壳上，晕乎乎地晃；乌龟慢慢探出头。
import { renderShot, DEBUG } from '../s06_key.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, cranePoseOf, mixNeck, sstep, craneRods, turtleRods } from '../choreo.js';

export const DURATION = 14;
export const CAM_B = { pos: [1.32, -2.35, 0.78], target: [1.32, 0, 0.86], hfov: 52 };
let TURTLE = null;

// 啄一下：t0 开始低头，0.35 秒到底，停 0.15 秒，再 0.6 秒抬回来；返回 0..1
const peck = (t, t0, down = 0.35, hold = 0.15, up = 0.6) => {
  const u = t - t0; if (u < 0) return 0;
  if (u < down) return sstep(0, down, u); if (u < down + hold) return 1; return 1 - sstep(down + hold, down + hold + up, u);
};

export function sheet(t, env) {
  TURTLE ||= makeTurtle();
  // ---- 乌龟：0～5 秒爬进来，停下；缩头 / 探头
  const tx = 2.55 - 0.62 * sstep(0, 5.0, t), tz = 0.45;
  const walking = t < 5.0 ? 1 : 0;
  let neckOut = 0.55 * sstep(4.6, 5.2, t);
  neckOut *= 1 - sstep(5.75, 5.85, t) + sstep(7.3, 7.8, t);          // 第一次啄：缩头，过一会儿又探出来
  neckOut *= 1 - sstep(8.35, 8.45, t);                                // 第二次啄：又缩
  neckOut += 0.7 * sstep(11.5, 12.6, t) * (1 + 0.08 * Math.sin(t * 9)); // 最后慢慢探出头，一颤一颤（像在笑）
  const tPose = turtlePose(t, { facing: -1, walk: walking, neckOut: Math.min(1, neckOut), headTilt: 0.1 });
  // ---- 鹤
  const look = sstep(2.8, 4.2, t);                                     // 发现了，低头看
  const p1 = peck(t, 5.5), p2 = peck(t, 8.2, 0.3, 0.05, 0.25);
  const hit = t > 8.5 ? Math.exp(-(t - 8.5) * 1.2) : 0;                 // 撞上之后
  const dizzy = sstep(8.6, 9.0, t) * (1 - sstep(11.8, 13.5, t));
  const amp = sstep(8.6, 9.0, t) * (1 - sstep(10.6, 12.4, t));        // 晕的幅度：撞完最大，慢慢缓过来
  let neck = mixNeck(NECK_UP, NECK_LOW, look);
  neck = mixNeck(neck, NECK_DOWN, Math.max(p1, p2 * 0.78));             // 第二下撞在龟壳上，比到水面浅
  // 晕：脖子一节节传着晃（像在画圈），头跟着转；身子左右打晃，膝盖发软
  neck = neck.map((v, i) => v + amp * 0.10 * Math.sin(t * 6 + i * 0.45) * (i < 12 ? 1 : 3.5) + dizzy * 0.02 * Math.sin(t * 3 + i));
  const sway = amp * Math.sin(t * 4.2);
  const recoil = hit * 0.05 * Math.sin((t - 8.5) * 14);                 // 撞上那一下往回弹
  const root = [1.30 - 0.03 * sstep(8.5, 8.7, t) + 0.02 * sstep(9, 12, t) + recoil * 0.3 + 0.022 * amp * Math.sin(t * 4.2 + 0.9), 0.66 + 0.005 * Math.sin(t * 1.7) - 0.008 * amp * Math.abs(Math.sin(t * 4.2))];
  // 撞上以后收着的那条腿放下来，两条腿撑着（0.3 秒过渡，不跳帧）
  const cPose = cranePoseOf(neck, { mode: 'stand', swing: 0.12 * hit * Math.sin((t - 8.5) * 6) }, 0.04 + recoil + 0.15 * sway, 1);
  const two = cranePoseOf(neck, { mode: 'two' }).angles, k2 = sstep(8.6, 8.9, t) * (1 - sstep(12.6, 13.2, t));
  for (const j of ['tibia_near', 'tarsus_near', 'foot_near', 'tibia_far', 'tarsus_far', 'foot_far']) cPose.angles[j] += (two[j] - cPose.angles[j]) * k2;
  // 两条腿轮流打软
  cPose.angles.tibia_near += amp * 0.16 * Math.sin(t * 4.2); cPose.angles.tarsus_near -= amp * 0.2 * Math.max(0, Math.sin(t * 4.2));
  cPose.angles.tibia_far -= amp * 0.16 * Math.sin(t * 4.2); cPose.angles.tarsus_far -= amp * 0.2 * Math.max(0, -Math.sin(t * 4.2));
  return [
    { pup: TURTLE, pose: tPose, root: [tx, tz], dist: 0.004, rods: turtleRods([tx, tz]) },
    { pup: env.crane, pose: cPose, root, dist: 0.004, rods: craneRods(env.RODS, root) },
  ];
}

const shot = { cam: CAM_B, cards: null, sheet };
export async function render(ctx, arg, W, H) {
  let t = +arg || 0;
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); t = o.t ?? 0; }
  return renderShot(ctx, t, W, H, shot);
}
export async function renderFrame(ctx, t, W, H) { return renderShot(ctx, t, W, H, shot); }
