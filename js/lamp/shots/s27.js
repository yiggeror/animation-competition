// S27 · 第 10 场：硬切进惨白——日光灯"嗒嗒"闪两下亮了，满屋白光把床单照透，皮影的影子一下子淡得几乎看不见；
// 皮影停在 S26 最后的样子（演的人也愣住了），过一会儿才慢慢垂下来。
import { makeShot, CAM_B } from './shotkit.js';
import { NECK_LOW, cranePoseOf, sstep, craneRods, turtleRods } from '../choreo.js';
import { cast as cast26, DURATION as DUR26 } from './s26.js';
export const DURATION = 5;
// 闪：亮 0.12 秒、灭 0.10、亮 0.08、灭 0.22，0.52 秒起一直亮（刚亮时略过亮再稳住）
export const fluorAt = (t) => {
  if (t < 0.12) return 1; if (t < 0.22) return 0.05; if (t < 0.30) return 0.9; if (t < 0.52) return 0.05;
  return 1 + 0.15 * Math.exp(-(t - 0.52) * 3);
};
// 接 S26：所有皮影从 S26 最后一帧（第 18 秒）的位置、朝向、腿姿开始，先定住（演的人愣住了），2.5 秒起慢慢垂下去。
// 狗影跟着手电的光斑一起被日光灯冲掉，乌龟还停在刚才"骑"的位置，被签子吊在半空。
const sheet = (t, env) => {
  const E = cast26(DUR26, env);
  const droop = sstep(2.5, 4.5, t);
  const tu = E.turtle, cr = E.craneA;
  const tRoot = [tu.root[0], tu.root[1] - 0.14 * droop];
  const tPose = { ...tu.pose, rootAngle: tu.pose.rootAngle * (1 - droop) + 0.2 * droop };
  const cAng = { ...cr.pose.angles };
  const low = cranePoseOf(NECK_LOW, { mode: 'two' }, 0.04, cr.pose.facing).angles;
  for (const k of Object.keys(cAng)) cAng[k] += ((low[k] ?? cAng[k]) - cAng[k]) * droop;
  const cRoot = [cr.root[0], cr.root[1] - 0.04 * droop];
  return [
    { ...tu, pose: tPose, root: tRoot, rods: turtleRods(tRoot) },
    { ...cr, pose: { ...cr.pose, angles: cAng, rootAngle: cr.pose.rootAngle * (1 - droop) + 0.04 * droop }, root: cRoot, rods: craneRods(env.RODS, cRoot) },
  ];
};
// 灯一亮，屋里一下子亮了好几倍：曝光跟着往下收（但收得不够快——第一下是刺眼的白）
const exp = (t) => 1 / (1 + 1.6 * Math.min(1, fluorAt(t)) * (0.6 + 0.4 * Math.min(1, Math.max(0, (t - 0.52) / 0.8))));
export const { render, renderFrame } = makeShot({ sheet, cam: CAM_B, fluor: fluorAt, exp });
