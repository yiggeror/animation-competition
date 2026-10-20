// 1-5 小满近景（1.5 秒）·画的版本：Astra 画的整头转向（头、颈、耳一起转开约 30° 再回来，不是只扭脸），按曝光表换张；
// 10-19 用户：奶奶坐在凳子上，离席子一两米，瓜不可能递到小满眼前。前景的手瓜去掉：奶奶在 S03 坐着把瓜朝她伸过去，
// 这里小满只是往画面右边（奶奶那边）瞟一眼、摇头，不出现递到跟前的瓜。
import { drawnShot } from './drawn.js';
export const DURATION = 1.5;
const X = '/assets/chars/x03a/';
// 000×8 008×3 011×3 014×3 017×4 021×2 023×2 025×3 028×8；九张均已锁版，14/17/21/23/25采用同一局部校色v2，勿混旧暖版
export const SHEET = [[X + 'S03a_F000', 0], [X + 'S03a_F008', 8], [X + 'S03a_F011', 11], [X + 'S03a_F014', 14], [X + 'S03a_F017', 17], [X + 'S03a_F021', 21], [X + 'S03a_F023', 23], [X + 'S03a_F025', 25], [X + 'S03a_F028', 28]];
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  light: () => ({ ambient: [0.5, 0.52, 0.58], lights: [{ x: 960, y: 1250, r: 1100, color: [0.6, 0.78, 1.0], i: 0.6, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.3, falloff: 1.4 }], exposure: 1.0, vignette: 0.35, grain: 5 }),
  emit: (x) => { const g = x.createRadialGradient(960, 1130, 10, 960, 1130, 520); g.addColorStop(0, 'rgba(170,210,255,0.4)'); g.addColorStop(1, 'rgba(170,210,255,0)'); x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(400, 600, 1120, 480); x.restore(); },
  cam: () => ({ x: 960, y: 540, fit: 1.0 }),
});
