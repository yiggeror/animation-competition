// S15 · 第 6 场：鹤亮相。前 3 秒，奶奶把鹤从离床单 35 厘米的地方慢慢推过来——床单上一个又大又虚的影子渐渐变小、变清楚，
// "贴"上床单；然后接第 6 场关键镜头的亮相（低头 → 扬起脖子 → 收住），小满从抱着胳膊到看呆了。
import { makeShot } from './shotkit.js';
import { cranePose, cards06, CRANE_ROOT, RODS, raiseAt } from '../s06_key.js';
import { sstep } from '../choreo.js';
export const DURATION = 8;
const T0 = 3;   // 贴上床单用的时间；之后的动作 = 关键镜头的 0～5 秒
const sheet = (t, env) => {
  const u = Math.max(0, t - T0);
  const dist = 0.004 + 0.34 * (1 - sstep(0, T0, t)) ** 1.6;
  const root = [CRANE_ROOT[0] - 0.05 * (1 - sstep(0, T0, t)), CRANE_ROOT[1] + 0.005 * Math.sin(u * 1.7) - 0.012 * (1 - Math.min(1, raiseAt(u)))];
  return [{ pup: env.crane, pose: cranePose(u), root, dist, rods: RODS.map((r) => ({ ...r, hand: r.hand(root) })) }];
};
const cards = (CARDS, cam, t) => cards06(CARDS, cam, Math.max(0, t - T0));
export const { render, renderFrame } = makeShot({ sheet, cards });
