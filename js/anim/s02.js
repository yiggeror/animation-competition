// 1-2 手机特写（2.5 秒）：游戏画面、电量 2%、充电标。取原 js/code/s02.js 的 1.5–4.0 秒（镜头正往屏幕推）。
import * as S from '../code/s02.js';
export const DURATION = 2.5, OFFSET = 1.5;
export async function renderFrame(ctx, t, W, H) { return S.renderFrame(ctx, t + OFFSET, W, H); }
