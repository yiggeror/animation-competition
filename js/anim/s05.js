// 2-3 手机特写（3 秒）：电量 1%，拇指狂按，2.42 屏幕一暗、2.5 全黑，拇指停住，黑屏停半秒再切近景。取原 js/code/s05.js 的 0.63–3.63 秒。
import * as S from '../code/s05.js';
export const DURATION = 3, OFFSET = 0.63;   // 原片 3.05 屏幕变暗 → 本镜 2.42；黑屏 2.5～3.0 共 12 帧（Astra 10-18 建议，原来只有 2 帧）
export async function renderFrame(ctx, t, W, H) { return S.renderFrame(ctx, t + OFFSET, W, H); }
