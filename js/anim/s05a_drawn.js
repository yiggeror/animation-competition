// 2-4 小满近景（2.5 秒，停电后）·画的版本：Astra 画的前五态 + 新尾（手机举进画、按两下侧键、再整体泄气），按曝光表换张。
// 机位：000–027 跟原来一样；028–035 小拉、往下移，让手机进画；036 以后固定。
// 光：屋里黑了，只有窗外月光从画面左边斜进来（跟代码版 S05a 同一套，环境光略提，表情要看得清）；手机已经黑屏，不再有屏幕光。
import { drawnShot } from './drawn.js';
import { key } from './kit.js';
export const DURATION = 2.5;
const X = '/assets/chars/x05a/';
// 036×1 037×2 039×3（第一按）042×2（松开）044×3 047×2（第二按，047 与 044 同一张）；049/052/055（泄气、看插座）还在画，先由 047 顶着
export const SHEET = [[X + 'S05a_F000', 0], [X + 'S05a_F010', 10], [X + 'S05a_F014', 14], [X + 'S05a_F024', 24], [X + 'S05a_F028', 28],
  [X + 'S05a_F036', 36], [X + 'S05a_F037', 37], [X + 'S05a_F039', 39], [X + 'S05a_F042', 42], [X + 'S05a_F044', 44]];
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_low_dark', bgCrop: [200, 300, 900, 420], blur: 18,
  light: () => ({ ambient: [0.16, 0.18, 0.26], lights: [], shafts: [{ poly: [[0, 0], [700, 0], [1400, 1080], [0, 1080]], color: [0.5, 0.62, 0.95], i: 0.42, soft: 120 }], exposure: 1.0, vignette: 0.5, grain: 8 }),
  cam: (t) => { const u = key(t, [[28 / 24, 0], [36 / 24, 1, 'io']]); return { x: 960, y: 470 + 90 * u, fit: 1.25 - 0.21 * u }; },
});
