import * as N from '../chars/nainai.js';
import * as X from '../chars/xiaoman.js';
import { setBoil } from '../lib/draw.js';
export function render(ctx, arg, W, H) {
  setBoil(0);
  ctx.fillStyle = '#f4ecdf'; ctx.fillRect(0, 0, W, H);
  N.draw(ctx, 'front', { x: 300, y: H - 50, s: 6.0 });
  N.draw(ctx, 'side', { x: 820, y: H - 50, s: 6.0 });
  N.draw(ctx, 'back', { x: 1300, y: H - 50, s: 6.0 });
  X.draw(ctx, 'side', { x: 1700, y: H - 50, s: 6.0 });
}
