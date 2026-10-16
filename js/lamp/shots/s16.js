// S16 · 第 6 场：鹤亮相之后在水边踱几步，停下来梳毛，再低头啄一口水；镜头慢慢推近。
import { makeShot } from './shotkit.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, NECK_PREEN, cranePoseOf, mixNeck, sstep, craneRods } from '../choreo.js';
export const DURATION = 8;
const sheet = (t, env) => {
  const walk = t < 3.2 ? 1 : 0, ph = t * 2 * Math.PI * 1.0;   // 每秒两步，踩在配乐的拍子上（120 拍/分）
  const x = 1.02 + 0.30 * sstep(0, 3.2, t);
  let neck = mixNeck(NECK_UP, NECK_LOW, 0.25 + 0.15 * Math.sin(ph) * walk);
  neck = mixNeck(neck, NECK_PREEN, sstep(3.5, 4.1, t) * (1 - sstep(5.2, 5.8, t)));
  neck = neck.map((v, i) => v + (i > 8 ? 0.08 * Math.sin(t * 11) * sstep(4.1, 4.3, t) * (1 - sstep(5.0, 5.2, t)) : 0));   // 梳毛：头在背上蹭
  neck = mixNeck(neck, NECK_DOWN, sstep(6.0, 6.5, t) * (1 - sstep(6.9, 7.6, t)));
  const root = [x, 0.66 + 0.012 * Math.abs(Math.sin(ph)) * walk];
  const legs = walk ? { mode: 'walk', ph } : { mode: 'two' };
  return [{ pup: env.crane, pose: cranePoseOf(neck, legs, 0.04 + 0.03 * Math.sin(ph) * walk, 1), root, dist: 0.004, rods: craneRods(env.RODS, root) }];
};
const cam = (t) => { const k = sstep(0, 8, t); return { pos: [1.30, -2.6 + 0.45 * k, 0.80], target: [1.30, 0, 0.86], hfov: 52 }; };
export const { render, renderFrame } = makeShot({ sheet, cam });
