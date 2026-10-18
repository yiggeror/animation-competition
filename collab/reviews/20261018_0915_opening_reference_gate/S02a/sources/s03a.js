// 1-5 小满中近景（1.5 秒）：奶奶的手托着西瓜从前景（画面右下、镜头这一侧）递到她下巴前，她头也不抬，脸往旁边一偏，眼睛不离手机。
import { closeShot, xiaomanFront } from './close.js';
import { key, melon } from './kit.js';
export const DURATION = 1.5;
// 趴着、手肘撑在席子上：两只手在胸前下方捧着手机（出画），所以胳膊往里收，不是垂在身体两边
export function pose(t) {
  const turn = key(t, [[0.7, 0], [0.82, -0.16, 'out'], [1.0, -0.16], [1.2, 0, 'io']]);   // 瓜到跟前后，脸往旁边小小一偏（"不要"），眼睛不离手机，再转回来接着玩
  return { head: { nod: 0.55, turn }, armL: { hand: [-4, -52], hp: 'grip' }, armR: { hand: [4, -52], hp: 'grip' }, face: { open: 0.85, look: [0, 0.85], smile: -0.15, brow: -0.15, frown: 0.25 } };
}
const shot = closeShot({
  bgKey: 'room_low', bgCrop: [200, 300, 900, 420], blur: 18,
  layers: async (t) => [xiaomanFront(pose(t), { k: 17.5, at: [880, 2130] })],   // 跟 S02a 同一个机位、略松一点：只到肩膀，手和手机在画面下沿外
  light: () => ({ ambient: [0.5, 0.52, 0.58], lights: [{ x: 860, y: 1200, r: 1000, color: [0.6, 0.78, 1.0], i: 0.6, falloff: 1.3 }, { x: 900, y: -300, r: 1600, color: [0.9, 0.95, 1], i: 0.3, falloff: 1.4 }], exposure: 1.0, vignette: 0.32, grain: 5 }),
  emit: (x, t) => {
    { const g = x.createRadialGradient(880, 1130, 10, 880, 1130, 480); g.addColorStop(0, 'rgba(170,210,255,0.5)'); g.addColorStop(1, 'rgba(170,210,255,0)'); x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(340, 620, 1080, 460); x.restore(); }   // 手机的光
    // 前景：奶奶的右手托着西瓜，从镜头这一侧（画面右下角，离镜头最近）往上递到她下巴前面（虚焦）。
    // 奶奶坐在小满对面、就在镜头旁边，所以手是从前景伸进来的，不是从画面右边横着进来。
    const s = key(t, [[0, 0], [0.32, 1, 'out']]), wob = key(t, [[0.32, 0], [0.42, 1, 'out'], [0.6, 0, 'io']]);
    x.save(); x.filter = 'blur(7px)'; x.translate(1560 - 330 * s, 1330 - 400 * s - 6 * wob); x.rotate(-0.55 + 0.25 * s); x.scale(30, 30);
    x.fillStyle = '#e9c3a6'; x.strokeStyle = '#3b2c25'; x.lineWidth = 0.25;
    x.beginPath(); x.moveTo(-6, 4); x.lineTo(14, 22); x.lineTo(24, 14); x.lineTo(4, -3); x.closePath(); x.fill();     // 小臂（往右下伸出画外）
    x.beginPath(); x.ellipse(-1, 1.5, 7.5, 4.6, -0.15, 0, 7); x.fill();                                              // 手掌（掌心朝上）
    x.beginPath(); x.ellipse(-7.4, -1.6, 2.2, 1.5, -0.9, 0, 7); x.fill();                                            // 拇指扶着瓜边
    melon(x, -2, -3.4, 0, 11); x.restore();
  },
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
