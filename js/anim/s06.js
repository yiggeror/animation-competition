// 2-5 插座特写（86 帧 ≈ 3.58 秒）：原 js/paint/shots/s06.js（8 秒）分段调速。插两次（第二次先吹一口，有升级），盯着插座看一下就切。
// 第三次狠插跟第二次结果一样、没有新信息，10-18 删掉（Astra 审片意见）。新 → 原：拔 0.4→1.0，插 1.2→1.8，拔 2.0→3.0，吹 2.4→3.4，插 2.9→3.9，盯着 3.15–3.58 → 4.4–5.55
import * as S from '../paint/shots/s06.js';
export const DURATION = 86 / 24;   // 86 帧（3.58 秒），镜头时长要是整帧
export const MAP = [[0, 0.6], [0.4, 1.0], [1.2, 1.8], [2.0, 3.0], [2.4, 3.4], [2.9, 3.9], [3.15, 4.4], [3.6, 5.6]];
export function oldT(t) {
  for (let i = 1; i < MAP.length; i++) if (t <= MAP[i][0]) { const [a, b] = [MAP[i - 1], MAP[i]]; return a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]); }
  return MAP[MAP.length - 1][1];
}
export async function renderFrame(ctx, t, W, H) { return S.renderFrame(ctx, oldT(t), W, H); }
