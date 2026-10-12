// 新造型设定：小满、奶奶（剪纸片式铆接纸人，侧面），三种画法并排
import * as XC from './xiaoman.js';
import * as NC from './nainai.js';
import { drawPieces, silk } from './render.js';
export function render(ctx, arg, W, H) {
  ctx.fillStyle = '#f2e9d8'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#3b2c25'; ctx.font = '60px "Ma Shan Zheng"'; ctx.fillText('新造型：剪纸片式的纸人', 50, 92);
  ctx.fillStyle = '#7a6a5c'; ctx.font = '24px "Noto Sans SC"';
  ctx.fillText('民间剪纸、年画娃娃的造型语言；身体一片片铆接（像皮影），每片长度固定，动起来不会被拉长、扭坏。同一组纸片，三种画法：', 50, 136);
  const styles = [['paper', 'A 剪纸片'], ['silhouette', 'B 剪影'], ['gongbi', 'C 工笔']];
  styles.forEach(([st, name], i) => {
    const x0 = 40 + i * 620, y0 = 170, w = 600, h = 880;
    ctx.save();
    ctx.beginPath(); ctx.roundRect(x0, y0, w, h, 18); ctx.clip();
    if (st === 'silhouette') { const g = ctx.createLinearGradient(0, y0, 0, y0 + h); g.addColorStop(0, '#1f2a4d'); g.addColorStop(0.6, '#8a6a58'); g.addColorStop(1, '#f2b866'); ctx.fillStyle = g; }
    else ctx.fillStyle = st === 'gongbi' ? '#ecdcbc' : '#e6d8bf';
    ctx.fillRect(x0, y0, w, h);
    const s = 5.2, floor = y0 + h - 70;
    const n = NC.pieces({ x: x0 + 190, y: floor - 63 * s, s, face: { eye: 'smile' } });
    const x = XC.pieces({ x: x0 + 420, y: floor - 30 * s, s, face: { eye: 'open' } });
    drawPieces(ctx, [...n.pieces, ...x.pieces], st, { s, shadow: [-4, 6], rim: { dir: [1, -0.4], rgb: '255,210,150', a: 0.9, w: 6 } });
    if (st === 'gongbi') silk(ctx, W, H, 0.14);
    ctx.restore();
    ctx.fillStyle = st === 'silhouette' ? '#f4e6cc' : '#3b2c25'; ctx.font = '34px "Noto Sans SC"'; ctx.textAlign = 'center'; ctx.fillText(name, x0 + w / 2, y0 + 50); ctx.textAlign = 'left';
  });
}
