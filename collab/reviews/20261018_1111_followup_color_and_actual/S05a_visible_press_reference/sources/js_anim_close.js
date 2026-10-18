// 近景公用：虚化的屋子做背景，人物用正面，跟场景吃同一套光（paint 管线）。
import { renderPaint, loadImg } from '../paint/paintshot.js';
import { blurredBg, charLayer, melon, phone } from './kit.js';
const BG = {};
export async function roomBg(key, crop, blur = 16) {
  if (BG[key]) return BG[key];
  const im = await loadImg('bg_01_room_wide');
  return (BG[key] = blurredBg(im, ...crop, 1920, 1080, blur));
}
export function closeShot(o) {
  return {
    size: [1920, 1080],
    layers: o.layers,
    light: o.light,
    glow: o.glow || (() => []),
    emit: o.emit,
    cam: o.cam || (() => ({ x: 960, y: 540, fit: 1 })),
    async render(ctx, t, W, H) { this.bg = await roomBg(o.bgKey, o.bgCrop, o.blur); return renderPaint(ctx, t, W, H, this); },
  };
}
// 奶奶正面坐着、腰以上：髋部以下用一块"腿面"（裤子色，坐着时大腿朝镜头）盖住，盆放在腿上
export function grandmaFront(P, { k, at, bowl = true, plate = null, melonAt = null, bite = 0 }) {
  const lap = (x) => {
    x.save(); x.globalCompositeOperation = 'destination-out'; x.fillRect(-80, -36, 160, 60); x.restore();
    x.fillStyle = '#3e4454'; x.strokeStyle = '#3b2c25'; x.lineWidth = 0.5;
    x.beginPath(); x.moveTo(-21, -38); x.quadraticCurveTo(-24, -20, -26, 0); x.lineTo(26, 0); x.quadraticCurveTo(24, -20, 21, -38); x.closePath(); x.fill(); x.stroke();
    if (plate) { x.fillStyle = '#f3efe6'; x.beginPath(); x.ellipse(plate[0], plate[1], 11, 2.6, 0, 0, 7); x.fill(); x.stroke(); melon(x, plate[0] + 1, plate[1] - 3, 1.45, 8); }
    if (bowl) {
      x.fillStyle = '#f3efe6'; x.beginPath(); x.ellipse(0, -36, 19, 4.5, 0, 0, Math.PI); x.lineTo(-19, -36); x.closePath(); x.fill(); x.stroke();
      x.fillStyle = '#7fae4f'; x.beginPath(); x.ellipse(0, -36, 17.5, 3.8, 0, Math.PI, 0); x.fill();
      x.strokeStyle = '#2f4f7a'; x.lineWidth = 0.9; x.beginPath(); x.ellipse(0, -36, 19, 4.5, 0, Math.PI, 0); x.stroke();
    }
    if (melonAt) melon(x, melonAt[0], melonAt[1], melonAt[2] ?? 0, melonAt[3] ?? 9, bite);
  };
  return charLayer('n', 'front', P, { box: [0, 0, 1920, 1080], k, at, ss: 1, after: lap });
}
export function xiaomanFront(P, { k, at, phoneLit = null }) {
  return charLayer('x', 'front', P, { box: [0, 0, 1920, 1080], k, at, ss: 1,
    after: phoneLit == null ? null : (x) => phone(x, 0, -66, 0, phoneLit) });
}

