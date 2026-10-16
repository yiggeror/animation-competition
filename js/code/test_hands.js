// 手的姿势测试：几种姿势 × 两个角度（手背朝镜头 / 侧面）
import { drawHand, POSES, orient } from './hand3d.js';
export async function render(ctx, arg, W, H) {
  ctx.fillStyle = '#e9dcc6'; ctx.fillRect(0, 0, W, H);
  const names = ['flat', 'relaxed', 'grip', 'fist', 'pinch', 'point', 'dog'];
  const views = [orient(0, 0, 0), orient(1.2, 0, -0.3), orient(-0.4, -0.9, 0.5)];
  const cw = W / names.length, rh = H / views.length;
  names.forEach((n, i) => views.forEach((R, j) => {
    drawHand(ctx, { side: 1, pose: POSES[n], R, at: [cw * (i + 0.5), rh * (j + 0.82)], px: rh / 30, forearm: 10, sleeve: j === 1 ? '#c94f3d' : null });
    ctx.fillStyle = '#333'; ctx.font = '16px sans-serif'; ctx.fillText(n, cw * i + 6, rh * j + 18);
  }));
}
