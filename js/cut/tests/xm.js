import * as XC from '../xiaoman.js';
import { drawPieces, silk } from '../render.js';
export function render(ctx, arg, W, H) {
  const styles = ['paper', 'silhouette', 'gongbi'];
  styles.forEach((st, i) => {
    const x0 = i * 640;
    ctx.save();
    ctx.beginPath(); ctx.rect(x0, 0, 640, H); ctx.clip();
    ctx.fillStyle = st === 'silhouette' ? '#e9b26a' : st === 'gongbi' ? '#efe2c6' : '#e9dcc4';
    if (st === 'silhouette') { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#2a3557'); g.addColorStop(1, '#f2b866'); ctx.fillStyle = g; }
    ctx.fillRect(x0, 0, 640, H);
    const s = 6.2;
    const a = XC.pieces({ x: x0 + 200, y: 700, s: s * 1.15, face: { eye: 'open' } });
    const b = XC.pieces({ x: x0 + 420, y: 860, s: s * 1.15, seated: true, face: { eye: 'wide', mouth: 'open' }, armN: { hand: [x0 + 520, 800], hp: 'relax' } });
    drawPieces(ctx, [...a.pieces, ...b.pieces.map((p) => ({ ...p, group: 'xm2' }))], st, { s, rim: { dir: [1, -0.4], rgb: '255,210,150', a: 0.9, w: 6 } });
    if (st === 'gongbi') silk(ctx, W, H, 0.1);
    ctx.restore();
  });
}
