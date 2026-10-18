// 1-4 奶奶中近景（4 秒）·画的版本：7 张旧关键姿势（k05 用修过盘位的副本）+ Astra 新补的态，按 docs/keyframes/opening_plan.json 的曝光表换张。
// 20 态齐：7 张旧画 + 13 张新补（A 段头眼 4、放荚 1、B 段取瓜递瓜 5、C 段等待眨眼 4）。
import { drawnShot } from './drawn.js';
export const DURATION = 4;
const G = '/assets/chars/g03/';
export const SHEET = [[G + 'S03_grandma_k01_F005_t0.20', 0], [G + 'S03_F009_local_composite_v1', 9], [G + 'S03_grandma_k02_F013_t0.55', 13], [G + 'S03_F017_local_composite_v1', 17], [G + 'S03_F021_local_composite_v1', 21],
  [G + 'S03_grandma_k03_F026_t1.10', 26], [G + 'S03_F030_local_composite_v1', 30], [G + 'S03_grandma_k04_F034_t1.40', 34], [G + 'S03_F037', 37], [G + 'S03_F040', 40],
  [G + 'S03_k05_fixed_plate_candidate_v4', 44], [G + 'S03_F048', 48], [G + 'S03_F052', 52], [G + 'S03_F055', 55], [G + 'S03_grandma_k06_F058_t2.40', 58], [G + 'F065_candidate', 65], [G + 'F074_candidate', 74], [G + 'F075_candidate', 75], [G + 'F076_candidate', 76],
  [G + 'S03_grandma_k07_F079_t3.30', 79]];
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_gm', bgCrop: [900, 180, 640, 360],
  light: () => ({ ambient: [0.66, 0.69, 0.75], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.45, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.22, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 4 }),
  cam: () => ({ x: 960, y: 540, fit: 1.04 }),
});
