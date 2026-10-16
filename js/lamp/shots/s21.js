// S21 · 第 8 场：小满手忙脚乱地操纵乌龟，乌龟一会儿贴着床单、一会儿离开床单——影子忽大忽小、忽清忽虚；
// 鹤在一边"笑"得前仰后合（奶奶操纵）。
import { makeShot, CAM_B } from './shotkit.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck, sstep, craneRods, turtleRods } from '../choreo.js';
export const DURATION = 6;
let TURTLE = null;
const sheet = (t, env) => {
  TURTLE ||= makeTurtle();
  // 乌龟离床单的距离：在 0.4 厘米和 25 厘米之间乱晃（影子跟着放大、变虚），身子也歪来歪去
  const d = 0.004 + 0.24 * Math.max(0, Math.sin(t * 2.3) * Math.sin(t * 1.1 + 0.6));
  const tx = 1.62 + 0.10 * Math.sin(t * 1.7), tz = 0.70 + 0.08 * Math.sin(t * 2.9);   // 举高一点：离开床单时影子往外放大，别冲出床单
  const tPose = turtlePose(t, { facing: -1, walk: 0.6, neckOut: 0.3 + 0.3 * Math.sin(t * 3), rootAngle: 0.35 * Math.sin(t * 2.1) });
  // 鹤笑：脖子一仰一合，身子前仰后合
  const laugh = Math.sin(t * 8.5);
  let neck = mixNeck(NECK_UP, NECK_LOW, 0.45 + 0.35 * laugh);
  neck[12] += 0.35 * laugh;
  const root = [1.05, 0.66 + 0.01 * Math.abs(laugh)];
  return [
    { pup: TURTLE, pose: tPose, root: [tx, tz], dist: d, rods: turtleRods([tx, tz]) },
    { pup: env.crane, pose: cranePoseOf(neck, { mode: 'two' }, 0.04 + 0.12 * laugh, 1), root, dist: 0.004, rods: craneRods(env.RODS, root) },
  ];
};
export const { render, renderFrame } = makeShot({ sheet, cam: CAM_B });
