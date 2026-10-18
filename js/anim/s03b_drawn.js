// 1-6 奶奶近景（2 秒）·画的版本：Astra 按 S03b 骨架参考画的 14 张，按曝光表换张（快动作一张停 2～3 帧，最后停 10 帧）。
// 背景是虚化的屋子（跟代码版 S03b 同一块），场景光只乘一次。画稿原生 1670～1672×941，左上对齐、等比放到 1920 宽，不拉伸。
import { closeShot } from './close.js';
export const DURATION = 2;
// 原件在 collab/reviews/20261018_0730_s03b_14_candidates/ 和 20261018_0751_s03b_four_repairs/；这里用 tools/clean_drawing.py 清过透明边的副本（头发外圈那层深色半透明边去掉了）
const A = '/assets/chars/g03b/', R = '/assets/chars/g03b/';
// [文件, 从第几帧起]。d04/d09/d10 用补修版；d12 两次都没过（往右过冲），WIP 里先让 d11 多停 3 帧顶上，等新 d12
export const SHEET = [[A + 'd01_f00', 0], [A + 'd02_f04', 4], [A + 'd03_f06', 6], [R + 'd04_f08_repair01_original', 8], [A + 'd05_f10', 10], [A + 'd06_f12', 12], [A + 'd07_f15', 15],
  [A + 'd08_f17', 17], [R + 'd09_f19_repair_call01', 19], [R + 'd10_f22_repair_call02', 22], [A + 'd11_f25', 25], [A + 'd13_f32', 32], [A + 'd14_f38', 38]];
export const pick = (t) => { const f = Math.floor(t * 24 + 1e-6); let k = SHEET[0][0]; for (const [n, f0] of SHEET) if (f >= f0) k = n; return k; };
const shot = closeShot({
  bgKey: 'room_gm', bgCrop: [900, 180, 640, 360], blur: 16,
  layers: async (t) => [{ img: pick(t) + '.png', x: 0, y: 0, sc: 1920 / 1672 }],
  light: () => ({ ambient: [0.66, 0.69, 0.75], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.45, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.22, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 4 }),
  cam: () => ({ x: 900, y: 450, fit: 1.2 }),   // 画稿是中景，推近到跟 S03b 一样的近景（脸和手瓜在画面中间）
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
