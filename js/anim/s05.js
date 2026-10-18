// 2-3 手机特写（3 秒）：充电标消失、电量 1%，拇指狂按，2.8 屏幕黑掉。取原 js/code/s05.js 的 0.25–3.25 秒。
import * as S from '../code/s05.js';
export const DURATION = 3, OFFSET = 0.25;
export async function renderFrame(ctx, t, W, H) { return S.renderFrame(ctx, t + OFFSET, W, H); }
