import * as XC from '../xiaoman.js';
import * as NC from '../nainai.js';
import { drawPieces, silk } from '../render.js';
export function render(ctx, arg, W, H) {
  const styles = ['paper', 'silhouette', 'gongbi'];
  styles.forEach((st, i) => {
    const x0 = i * 640;
    ctx.save();
    ctx.beginPath(); ctx.rect(x0, 0, 640, H); ctx.clip();
    if (st === 'silhouette') { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#2a3557'); g.addColorStop(1, '#f2b866'); ctx.fillStyle = g; }
    else ctx.fillStyle = st === 'gongbi' ? '#efe2c6' : '#e9dcc4';
    ctx.fillRect(x0, 0, 640, H);
    const s = 5.4;
    const n = NC.pieces({ x: x0 + 230, y: H - 60 - 63 * s, s, face: { eye: 'smile' } });
    const x = XC.pieces({ x: x0 + 470, y: H - 60 - 30 * s, s, face: { eye: 'open' } });
    drawPieces(ctx, [...n.pieces, ...x.pieces], st, { s, rim: { dir: [1, -0.4], rgb: '255,210,150', a: 0.9, w: 6 } });
    if (st === 'gongbi') silk(ctx, W, H, 0.1);
    ctx.restore();
  });
}
