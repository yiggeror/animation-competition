import * as X from '../chars/xiaoman.js';
import { setBoil } from '../lib/draw.js';
export function render(ctx, arg, W, H) {
  setBoil(0);
  ctx.fillStyle = '#f4ecdf'; ctx.fillRect(0, 0, W, H);
  X.draw(ctx, 'front', { x: 330, y: H - 60, s: 7.4 });
  X.draw(ctx, 'side', { x: 900, y: H - 60, s: 7.4 });
  X.draw(ctx, 'back', { x: 1480, y: H - 60, s: 7.4 });
}
