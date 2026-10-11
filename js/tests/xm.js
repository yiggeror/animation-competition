// 测试：小满正面，几种表情
import * as XMN from '../chars/xiaoman.js';
import { setBoil } from '../lib/draw.js';
export function render(ctx, arg, W, H) {
  setBoil(0);
  ctx.fillStyle = '#f4ecdf'; ctx.fillRect(0, 0, W, H);
  const faces = [{}, { smile: 0.9, mouth: 0.6, happyEyes: 1, blush: 0.9 }, { open: 1.15, mouth: 0.7, smile: -0.1, brow: 1, look: [0, -0.6] }, { smile: -0.6, frown: 1, look: [0.8, 0], blush: 0.2 }];
  faces.forEach((f, i) => {
    XMN.draw(ctx, 'front', { x: 260 + i * 470, y: H - 60, s: 7.0, face: f, head: { tilt: i === 3 ? -0.08 : 0 } });
  });
}
