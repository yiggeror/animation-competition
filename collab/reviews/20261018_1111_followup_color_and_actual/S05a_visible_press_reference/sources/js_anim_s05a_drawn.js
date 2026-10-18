// 2-4 小满近景（2.5 秒，停电后）·画的版本：Astra 画的 9 态（F000 复用专注），按曝光表换张。
// 光：屋里黑了，只有窗外月光从画面左边斜进来（跟代码版 S05a 同一套，环境光略提，表情要看得清）；手机已经黑屏，不再有屏幕光。
import { drawnShot } from './drawn.js';
export const DURATION = 2.5;
const X = '/assets/chars/x05a/';
export const SHEET = [[X + 'S05a_F000', 0], [X + 'S05a_F010', 10], [X + 'S05a_F014', 14], [X + 'S05a_F024', 24], [X + 'S05a_F028', 28],
  [X + 'S05a_F044', 44], [X + 'S05a_F046', 46], [X + 'S05a_F050', 50], [X + 'S05a_F052_v3', 52]];
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_low_dark', bgCrop: [200, 300, 900, 420], blur: 18,
  light: () => ({ ambient: [0.16, 0.18, 0.26], lights: [], shafts: [{ poly: [[0, 0], [700, 0], [1400, 1080], [0, 1080]], color: [0.5, 0.62, 0.95], i: 0.42, soft: 120 }], exposure: 1.0, vignette: 0.5, grain: 8 }),
  cam: () => ({ x: 960, y: 470, fit: 1.25 }),
});

