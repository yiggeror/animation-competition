// 小满造型检查：固有色 | 剪影（缩小看也要读得出姿势） | 简单打光（右前方暖光 + 左后方冷光）。参数带 n 时中间改为法线
import * as XM from './xiaoman.js';
import { Cards } from './cards.js';

export async function render(ctx, arg, W, H) {
  const s = parseFloat(arg || '11');   // 每厘米像素
  const showN = /n/.test(arg || '');
  const panels = 3, pw = W / panels;
  ctx.fillStyle = '#6b6560'; ctx.fillRect(0, 0, W, H);
  const cards = new Cards(W, H);
  for (let k = 0; k < panels; k++) {
    const ox = pw * k + pw * 0.3, oy = H * 0.7;
    const map = ([x, y]) => [ox + x * s, oy - y * s];
    cards.addAll(XM.parts(map, {}, s), 2.0);
  }
  const a = cards.a.getImageData(0, 0, W, H), n = cards.n.getImageData(0, 0, W, H);
  const out = ctx.getImageData(0, 0, W, H);
  const L1 = norm([0.75, 0.35, 0.35]), L2 = norm([-0.8, 0.3, -0.2]);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = (y * W + x) * 4, al = a.data[i + 3] / 255;
    if (!al) continue;
    const panel = Math.floor(x / pw);
    let r, g, b;
    if (panel === 0) { r = a.data[i]; g = a.data[i + 1]; b = a.data[i + 2]; }
    else if (panel === 1) { if (showN) { r = n.data[i]; g = n.data[i + 1]; b = n.data[i + 2]; } else { r = 24; g = 20; b = 22; } }
    else {
      const N = [n.data[i] / 127.5 - 1, n.data[i + 1] / 127.5 - 1, n.data[i + 2] / 127.5 - 1];
      const d1 = Math.max(0, N[0] * L1[0] + N[1] * L1[1] + N[2] * L1[2]), d2 = Math.max(0, N[0] * L2[0] + N[1] * L2[1] + N[2] * L2[2]);
      const lr = 0.08 + d1 * 1.25 + d2 * 0.25, lg = 0.08 + d1 * 0.95 + d2 * 0.35, lb = 0.1 + d1 * 0.65 + d2 * 0.6;
      r = 255 * Math.pow(Math.pow(a.data[i] / 255, 2.2) * lr, 1 / 2.2);
      g = 255 * Math.pow(Math.pow(a.data[i + 1] / 255, 2.2) * lg, 1 / 2.2);
      b = 255 * Math.pow(Math.pow(a.data[i + 2] / 255, 2.2) * lb, 1 / 2.2);
    }
    out.data[i] = out.data[i] * (1 - al) + r * al; out.data[i + 1] = out.data[i + 1] * (1 - al) + g * al; out.data[i + 2] = out.data[i + 2] * (1 - al) + b * al;
  }
  ctx.putImageData(out, 0, 0);
  ctx.font = `${Math.round(H * 0.03)}px "Noto Sans SC"`; ctx.fillStyle = '#efe6d8';
  ['固有色（2D 设计）', showN ? '由轮廓算出的法线' : '剪影', '简单打光：右前方暖光 + 左后方冷光'].forEach((t, k) => ctx.fillText(t, pw * k + pw * 0.06, H * 0.95));
}
function norm(v) { const l = Math.hypot(...v); return v.map((x) => x / l); }
