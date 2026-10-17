// S26 · 第 9 场（第一个高潮）：小满把手电架在木箱上，手伸进光里比出小狗——床单上一大片冷白的光斑，光斑里一只狗影；
// 小狗冲着鹤汪汪叫，鹤吓一跳拔腿就跑，小狗追；乌龟爬到狗背上骑着，几个一起越演越快、越来越闹。
import { makeShot, CAM_B } from './shotkit.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { makeDog, dogPose, rootForShadow } from '../handdog.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck, sstep, craneRods, turtleRods } from '../choreo.js';
export const DURATION = 18;
let TURTLE = null, DOG = null;
const F = [1.50, 0.9, 0.80], DOG_D = 0.40;            // 手电（x, 离床单, z）、手离床单的距离
// 越演越快：时间先按 1 倍走，10 秒以后逐渐加到 1.8 倍
const tempo = (t) => t + 0.8 * Math.max(0, t - 10) ** 2 / 16;

export function cast(t, env) {
  TURTLE ||= makeTurtle(); DOG ||= makeDog(1.0);
  const u = tempo(t);
  // ---- 狗影的位置（床单上）：从光斑右边探进来，冲鹤叫，追着鹤跑来跑去
  const chase = sstep(2.0, 6.0, t), back = sstep(6.5, 10.0, t);
  let sx = 2.12 - 0.27 * sstep(0, 1.5, t) - 0.55 * chase + 0.45 * back + 0.08 * Math.sin(u * 2.2) * sstep(10, 12, t);
  let sz = 0.70 + 0.04 * Math.abs(Math.sin(u * 5.5)) * sstep(1.5, 3, t);
  const facing = back > 0.5 && t < 12 ? 1 : -1;        // 回头追的时候掉个头
  const dogRoot = rootForShadow(F, DOG_D, sx, sz);
  const bark = Math.max(sstep(1.0, 1.3, t) * (1 - sstep(2.4, 2.8, t)), 0.6 * sstep(9.5, 10.5, t));
  const dPose = dogPose(u, { bark, pant: 1 - bark, facing, rootAngle: 0.12 * Math.sin(u * 5.5) * sstep(1.5, 3, t) });
  // ---- 鹤：吓一跳（脖子一下子竖直），拔腿往左跑，再被追着往右跑
  const scare = sstep(1.4, 1.6, t);
  const cx = 1.08 - 0.38 * chase + 0.40 * back + 0.06 * Math.sin(u * 3) * sstep(11, 13, t);
  const running = (t > 2.0 && t < 6.0) || (t > 6.5 && t < 10) || t > 11;
  const ph = u * 2 * Math.PI * 1.6;
  let neck = mixNeck(NECK_LOW, NECK_UP, 0.4 + 0.6 * scare);
  neck = neck.map((v, i) => v + (running ? 0.05 * Math.sin(ph + i * 0.3) : 0));
  const cRoot = [cx, 0.68 + (running ? 0.015 * Math.abs(Math.sin(ph)) : 0)];
  const cPose = cranePoseOf(neck, running ? { mode: 'walk', ph } : { mode: 'two' }, 0.05 + (running ? 0.06 : 0) - 0.05 * scare * (1 - chase), back > 0.5 && t < 11 ? 1 : (chase > 0.3 ? -1 : 1));
  // ---- 乌龟：先在右边慢慢爬，6 秒起爬到狗背上骑着（跟着狗影的头顶走）
  const ride = sstep(6.0, 7.0, t);
  const walkX = 1.95 - 0.1 * sstep(0, 6, t);
  // 狗背上：狗影头顶往后一点；乌龟离床单近（影子清楚），要换算成乌龟自己平面里的位置——直接放在狗影的位置上方
  const tx = walkX * (1 - ride) + (sx - facing * 0.06) * ride, tz = 0.45 * (1 - ride) + (sz + 0.17) * ride;
  const tPose = turtlePose(u, { facing: ride > 0.5 ? facing : -1, walk: ride > 0.5 ? 0.3 : 1, neckOut: 0.5 + 0.4 * ride, rootAngle: 0.1 * Math.sin(u * 5.5) * ride });
  const turtle = { pup: TURTLE, pose: tPose, root: [tx, tz], dist: 0.004, rods: turtleRods([tx, tz]) };
  const craneA = { pup: env.crane, pose: cPose, root: cRoot, dist: 0.004, rods: craneRods(env.RODS, cRoot) };
  const dog = { pup: DOG, pose: dPose, root: dogRoot, dist: DOG_D };
  return { turtle, craneA, dog };
}

let LAST = null;
const sheet = (t, env) => { LAST = cast(t, env); return [LAST.turtle, LAST.craneA]; };   // 马灯照出来的：皮影（狗的手离马灯远、在光锥外，不挡马灯）
const flash = () => ({ pos: F, r: 0.62, I: 0.16, color: [0.72, 0.86, 1.0], actors: [LAST.turtle, LAST.craneA, LAST.dog] });   // 手电照出来的：皮影 + 狗
export const { render, renderFrame } = makeShot({ sheet, flash, cam: CAM_B });
