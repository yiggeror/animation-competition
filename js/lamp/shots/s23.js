// S23 · 第 8 场：乌龟慢慢伸长脖子，一口咬住鹤的嘴；鹤僵住，然后使劲甩头，乌龟被甩得晃来晃去也不松口。
import { makeShot, CAM_B } from './shotkit.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, cranePoseOf, mixNeck, sstep, craneRods, turtleRods } from '../choreo.js';
export const DURATION = 5;
let TURTLE = null;
export const sheet = (t, env) => {
  TURTLE ||= makeTurtle();
  const bite = sstep(1.2, 1.6, t);
  const shake = sstep(2.4, 2.6, t) * Math.sin((t - 2.4) * 16) * (1 - sstep(4.2, 4.8, t));
  const tx = 1.84 + 0.03 * shake, tz = 0.46 + 0.04 * Math.abs(shake);
  const tPose = turtlePose(t, { facing: -1, walk: 0, neckOut: Math.min(1, sstep(0, 1.3, t)), bite: 1 - bite * 0.7, headTilt: 0.35 + 0.3 * bite, rootAngle: 0.15 * shake });
  // 鹤：低头凑近（0～1 秒），被咬住后僵住（1.6～2.4），然后甩头
  let neck = mixNeck(NECK_LOW, NECK_DOWN, 0.8 * sstep(0, 1.0, t));
  neck = neck.map((v, i) => v + 0.12 * shake * (i < 12 ? 0.4 : 1));
  const root = [1.18 - 0.02 * bite + 0.015 * shake, 0.66];
  return [
    { pup: TURTLE, pose: tPose, root: [tx, tz], dist: 0.004, rods: turtleRods([tx, tz]) },
    { pup: env.crane, pose: cranePoseOf(neck, { mode: 'two' }, 0.04 - 0.06 * bite + 0.06 * shake, 1), root, dist: 0.004, rods: craneRods(env.RODS, root) },
  ];
};
export const { render, renderFrame } = makeShot({ sheet, cam: CAM_B });
