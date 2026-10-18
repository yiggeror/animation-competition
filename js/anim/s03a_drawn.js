// 1-5 小满近景（1.5 秒）·画的版本：Astra 画的整头转向（头、颈、耳一起转开约 30° 再回来，不是只扭脸），按曝光表换张；
// 前景是奶奶托瓜的右手（单独一张画），从画面右下角斜着伸进来，第 8 帧到位后停住；离镜头近，做一点虚焦。
// 手的落点用 Astra 在 1672×941 画布里给的：整张等比 0.46，左上角 (847.46, 613.74)，不旋转。
import { drawnShot } from './drawn.js';
import { loadImg } from '../paint/paintshot.js';
import { key } from './kit.js';
export const DURATION = 1.5;
const X = '/assets/chars/x03a/', H = '/assets/chars/x03a/', S = 1920 / 1672;
// 000×8 008×3 011×3 014×3 017×4 021×2 023×2 025×3 028×8；九张均已锁版，14/17/21/23/25采用同一局部校色v2，勿混旧暖版
export const SHEET = [[X + 'S03a_F000', 0], [X + 'S03a_F008', 8], [X + 'S03a_F011', 11], [X + 'S03a_F014', 14], [X + 'S03a_F017', 17], [X + 'S03a_F021', 21], [X + 'S03a_F023', 23], [X + 'S03a_F025', 25], [X + 'S03a_F028', 28]];
let HAND = null;
async function hand() {
  if (HAND) return HAND;
  const im = await loadImg(H + 'S03a_foreground_grandma_right_hand_melon_RGBA.png');
  const c = new OffscreenCanvas(im.width + 40, im.height + 40), x = c.getContext('2d');
  x.filter = 'blur(6px)'; x.drawImage(im, 20, 20);                     // 前景虚焦（在原图尺寸上模糊，缩小后约 3 像素）
  return (HAND = c);
}
export const renderFrame = drawnShot({
  sheet: SHEET, bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  light: () => ({ ambient: [0.5, 0.52, 0.58], lights: [{ x: 960, y: 1250, r: 1100, color: [0.6, 0.78, 1.0], i: 0.6, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.3, falloff: 1.4 }], exposure: 1.0, vignette: 0.35, grain: 5 }),
  emit: (x) => { const g = x.createRadialGradient(960, 1130, 10, 960, 1130, 520); g.addColorStop(0, 'rgba(170,210,255,0.4)'); g.addColorStop(1, 'rgba(170,210,255,0)'); x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(400, 600, 1120, 480); x.restore(); },
  over: async (t) => {
    const u = key(t, [[0, 0], [8 / 24, 1, 'out']]), h = await hand();
    const dx = (1 - u) * 520, dy = (1 - u) * 420;                       // 从右下角外面伸进来
    return [{ img: h, x: (847.46 - 20 * 0.46) * S + dx, y: (613.74 - 20 * 0.46) * S + dy, sc: 0.46 * S }];
  },
  cam: () => ({ x: 960, y: 540, fit: 1.0 }),   // 不推近：手的落点是按整张画布给的，推近会把手瓜裁出画
});
