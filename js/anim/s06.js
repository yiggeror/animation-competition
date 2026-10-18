// 2-5 插座特写（5 秒）：原 js/paint/shots/s06.js（8 秒）分段调速。动作段基本原速，只压短中间盯着插座的那段停顿。
// 新 → 原：拔 0.4→1.0，插 1.2→1.8，拔 2.0→3.0，吹 2.4→3.4，插 2.9→3.9，盯着 3.15–3.45 → 4.4–5.75，狠插 4.05→6.4
import * as S from '../paint/shots/s06.js';
export const DURATION = 5;
export const MAP = [[0, 0.6], [0.4, 1.0], [1.2, 1.8], [2.0, 3.0], [2.4, 3.4], [2.9, 3.9], [3.15, 4.4], [3.45, 5.75], [4.05, 6.4], [5.0, 7.35]];
export function oldT(t) {
  for (let i = 1; i < MAP.length; i++) if (t <= MAP[i][0]) { const [a, b] = [MAP[i - 1], MAP[i]]; return a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]); }
  return MAP[MAP.length - 1][1];
}
export async function renderFrame(ctx, t, W, H) { return S.renderFrame(ctx, oldT(t), W, H); }
