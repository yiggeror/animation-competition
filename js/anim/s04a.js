// 2-2 蚊香特写（2 秒）：吊扇停了，烟不再被吹散，从斜着飘慢慢变成一根直直往上升的细线。全片第一个安静下来的画面。
import { key } from './kit.js';
export const DURATION = 2;
export async function renderFrame(ctx, t, W, H) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0b0f1a'); g.addColorStop(0.62, '#141a28'); g.addColorStop(1, '#1d2433');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // 月光落在地上的一块
  const m = ctx.createRadialGradient(W * 0.3, H * 0.86, 20, W * 0.3, H * 0.86, W * 0.5); m.addColorStop(0, 'rgba(90,110,170,0.35)'); m.addColorStop(1, 'rgba(90,110,170,0)');
  ctx.fillStyle = m; ctx.fillRect(0, 0, W, H);
  const cx = W * 0.5, cy = H * 0.8;
  // 蚊香：铁架 + 绿盘香（透视成扁椭圆）
  ctx.save(); ctx.translate(cx, cy); ctx.scale(1, 0.32);
  ctx.strokeStyle = '#3d6a43'; ctx.lineWidth = 14 / 0.6;
  ctx.beginPath(); for (let a = 0; a < 6 * Math.PI; a += 0.05) { const r = 12 + a * 15; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } ctx.stroke();
  ctx.restore();
  ctx.strokeStyle = '#555'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(cx - 160, cy + 70); ctx.lineTo(cx + 160, cy + 70); ctx.moveTo(cx, cy); ctx.lineTo(cx, cy + 70); ctx.stroke();
  // 头上一点红
  const tip = [cx + 300, cy + 10];
  const gl = ctx.createRadialGradient(...tip, 0, ...tip, 30); gl.addColorStop(0, 'rgba(255,120,60,1)'); gl.addColorStop(1, 'rgba(255,80,30,0)'); ctx.fillStyle = gl; ctx.fillRect(tip[0] - 30, tip[1] - 30, 60, 60);
  // 烟：风的影响 wind 从 1 降到 0，烟从斜飘变成直线
  const wind = key(t, [[0, 1], [1.4, 0, 'out']]);
  ctx.save(); ctx.lineCap = 'round';
  for (let k = 0; k < 3; k++) {
    ctx.strokeStyle = `rgba(210,215,230,${0.35 - k * 0.1})`; ctx.lineWidth = 2 + k * 3;
    ctx.beginPath(); ctx.moveTo(...tip);
    for (let s = 1; s <= 40; s++) { const u = s / 40; const sway = (wind * 22 + 3) * Math.sin(u * 8 - t * (2 + wind * 3) + k) * u; ctx.lineTo(tip[0] + wind * 260 * u * u + sway, tip[1] - 700 * u); }
    ctx.stroke();
  }
  ctx.restore();
}
