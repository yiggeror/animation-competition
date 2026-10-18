// 1-3 小满近景（2.5 秒）·画的版本：3 张旧表情（专注 / 紧张 / 松口气）+ 新补的眨眼三帧，按 opening_plan.json 换张；F016 复用专注。
// 原画是 K14 的头肩近景，这里推近到动态分镜的 K19 一带。手机在画面下沿外，蓝白的光从下往上（跟代码版 S02a 同一套光）。
import { drawnShot } from './drawn.js';
export const DURATION = 2.5;
const X = '/assets/chars/x02a/';
export const SHEET = [[X + 'S02a_k01_focus', 0], [X + 'S02a_F013', 13], [X + 'S02a_F014', 14], [X + 'S02a_F015', 15], [X + 'S02a_k01_focus', 16],
  [X + 'S02a_k02_tense', 25], [X + 'S02a_k03_relief', 46]];
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  light: () => ({ ambient: [0.5, 0.52, 0.58], lights: [{ x: 960, y: 1250, r: 1100, color: [0.6, 0.78, 1.0], i: 0.6, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.3, falloff: 1.4 }], exposure: 1.0, vignette: 0.35, grain: 5 }),
  emit: (x) => { const g = x.createRadialGradient(960, 1130, 10, 960, 1130, 520); g.addColorStop(0, 'rgba(170,210,255,0.4)'); g.addColorStop(1, 'rgba(170,210,255,0)'); x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(400, 600, 1120, 480); x.restore(); },
  cam: () => ({ x: 960, y: 470, fit: 1.25 }),
});

