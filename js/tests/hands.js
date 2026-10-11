// 测试：手的几种姿势，放大看
import { Figure, M } from '../lib/figure.js';
import { hand, HAND_POSES } from '../chars/hand.js';
import { setBoil } from '../lib/draw.js';
export function render(ctx, arg, W, H) {
  setBoil(0);
  ctx.fillStyle = '#f4ecdf'; ctx.fillRect(0, 0, W, H);
  const names = Object.keys(HAND_POSES);
  names.forEach((n, i) => {
    const x = 180 + (i % 4) * 440, y = 260 + Math.floor(i / 4) * 460;
    for (const [k, ang] of [[0, Math.PI / 2], [1, 0]]) {
      ctx.save(); ctx.translate(x + k * 210, y); ctx.scale(28, 28);
      const fig = new Figure(ctx, { lw: 3.2 });
      hand(fig, M.chain(M.t(0, 0), M.r(ang)), n, { size: 4.4, skin: '#f8dac2', z: 0, name: 'h', lw: 3.2, line: '#ecbb9e', ink: '#3b2c25' });
      fig.draw();
      ctx.restore();
    }
    ctx.fillStyle = '#3b2c25'; ctx.font = '28px "Noto Sans SC"'; ctx.fillText(n, x - 60, y - 120);
  });
}
