// S27 · 第 10 场：硬切进惨白——日光灯"嗒嗒"闪两下亮了，满屋白光把床单照透，皮影的影子一下子淡得几乎看不见；
// 两个皮影停在半空（演的人也愣住了），过一会儿才慢慢垂下来。
import { makeShot, CAM_B } from './shotkit.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck, sstep, craneRods, turtleRods } from '../choreo.js';
export const DURATION = 5;
let TURTLE = null;
// 闪：亮 0.12 秒、灭 0.10、亮 0.08、灭 0.22，0.52 秒起一直亮（刚亮时略过亮再稳住）
export const fluorAt = (t) => {
  if (t < 0.12) return 1; if (t < 0.22) return 0.05; if (t < 0.30) return 0.9; if (t < 0.52) return 0.05;
  return 1 + 0.15 * Math.exp(-(t - 0.52) * 3);
};
const sheet = (t, env) => {
  TURTLE ||= makeTurtle();
  const droop = sstep(2.5, 4.5, t);                                   // 愣了一会儿，皮影慢慢垂下去
  const tx = 1.75, tz = 0.62 - 0.12 * droop;
  const tPose = turtlePose(0.7, { facing: -1, walk: 0, neckOut: 0.8, rootAngle: 0.25 - 0.2 * droop });
  const neck = mixNeck(mixNeck(NECK_UP, NECK_LOW, 0.3), NECK_LOW, droop);
  const root = [1.10, 0.70 - 0.04 * droop];
  return [
    { pup: TURTLE, pose: tPose, root: [tx, tz], dist: 0.02, rods: turtleRods([tx, tz]) },
    { pup: env.crane, pose: cranePoseOf(neck, { mode: 'two' }, 0.1 - 0.06 * droop, 1), root, dist: 0.006, rods: craneRods(env.RODS, root) },
  ];
};
// 灯一亮，屋里一下子亮了好几倍：曝光跟着往下收（但收得不够快——第一下是刺眼的白）
const exp = (t) => 1 / (1 + 1.6 * Math.min(1, fluorAt(t)) * (0.6 + 0.4 * Math.min(1, Math.max(0, (t - 0.52) / 0.8))));
export const { render, renderFrame } = makeShot({ sheet, cam: CAM_B, fluor: fluorAt, exp });
