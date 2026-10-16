// 手的姿势测试 2：握东西的几种角度（找插插头、拿手电时好看的视角）
import { drawHand, POSES, orient } from './hand3d.js';
export async function render(ctx, arg, W, H) {
  ctx.fillStyle = '#e9dcc6'; ctx.fillRect(0, 0, W, H);
  const views = [];
  for (const yaw of [-0.9, -0.5, 0, 0.5]) for (const roll of [-1.4, -0.8]) views.push([yaw, 0.35, roll]);
  const cols = 4, rows = 2, cw = W / cols, rh = H / rows;
  views.forEach(([y, p, r], k) => {
    const i = Math.floor(k / 2), j = k % 2;
    const R = orient(y, p, r);
    const h = drawHand(ctx, { side: 1, pose: POSES.grip, R, at: [cw * (i + 0.35), rh * (j + 0.6)], px: rh / 26, forearm: 12, sleeve: '#c94f3d', sleeveAt: 7, scale: 0.8 });
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.beginPath(); ctx.arc(...h.grip, 4, 0, 7); ctx.fill();
    ctx.fillStyle = '#333'; ctx.font = '15px sans-serif'; ctx.fillText(`yaw ${y} roll ${r}`, cw * i + 6, rh * j + 18);
  });
}
