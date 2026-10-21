// 片头：黑场里亮起一块被马灯照着的床单，片名"奶奶的皮影"像皮影一样从灯前贴近床单——先大而虚，再变小变清楚
// （和第 6 场鹤亮相同一个光学关系：偶离灯越近影子越大越虚，贴上床单才清楚）。最后整块暗下去，切进第 1 场。
export const DURATION = 5;
const TITLE = '奶奶的皮影';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
let CLOTH = null;

// 床单的布纹（经纬线 + 几道竖褶），只算一次
function cloth(W, H) {
  if (CLOTH && CLOTH.width === W) return CLOTH;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const img = x.createImageData(W, H), d = img.data;
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const cols = new Float32Array(W), rows = new Float32Array(H);
  for (let i = 0; i < W; i++) cols[i] = (rnd() - 0.5) * 7;
  for (let j = 0; j < H; j++) rows[j] = (rnd() - 0.5) * 7;
  const folds = [0.18, 0.34, 0.57, 0.71, 0.88].map((p, k) => ({ p: p * W, w: (0.03 + 0.02 * (k % 2)) * W, a: k % 2 ? 9 : -11 }));
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    let v = 128 + cols[i] + rows[j] + (rnd() - 0.5) * 6;
    for (const f of folds) v += f.a * Math.exp(-(((i - f.p) / f.w) ** 2)) * (0.6 + 0.4 * Math.sin(j / H * 3 + f.p));
    const o = (j * W + i) * 4; d[o] = d[o + 1] = d[o + 2] = v; d[o + 3] = 255;
  }
  x.putImageData(img, 0, 0);
  return (CLOTH = c);
}

export function renderFrame(ctx, t, W, H) {
  const k = W / 1920;
  const on = sstep(0.2, 1.1, t) * (1 - sstep(4.25, 4.95, t));           // 灯亮起 / 最后暗下去
  const fl = 1 + 0.035 * Math.sin(t * 7.3) + 0.025 * Math.sin(t * 12.7 + 1); // 火苗轻轻晃
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  if (on <= 0) return;
  // 床单受光：灯在床单后面偏左上，热点暖黄，往边上落到暗橙
  ctx.save();
  const g = ctx.createRadialGradient(W * 0.46, H * 0.4, 0, W * 0.5, H * 0.5, W * 0.62);
  g.addColorStop(0, `rgb(${Math.round(250 * fl)},${Math.round(226 * fl)},${Math.round(178 * fl)})`);
  g.addColorStop(0.45, 'rgb(214,164,104)'); g.addColorStop(1, 'rgb(70,38,16)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.55; ctx.drawImage(cloth(W, H), 0, 0);
  ctx.restore();
  // 片名的影子：签子把字送到床单上。u=0 离灯近（大、虚、淡），u=1 贴上床单（原大、清楚、深）
  const u = sstep(0.9, 3.0, t);
  const scale = 1.75 - 0.75 * u, blur = (34 * (1 - u) ** 1.5 + 0.6) * k, a = 0.25 + 0.65 * u;
  const drift = (1 - u) * 26 * k;                                         // 贴近时略往下沉一点，像手送过来
  ctx.save();
  ctx.translate(W / 2, H * 0.5 - drift); ctx.scale(scale, scale);
  ctx.filter = `blur(${blur.toFixed(1)}px)`;
  ctx.font = `${Math.round(H * 0.15)}px "Ma Shan Zheng"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = `rgba(52,22,8,${a})`; ctx.fillText(TITLE, 0, 0);
  // 牛皮透一点暖红色：清楚以后字心里浮出一层淡淡的透光
  if (u > 0.6) { ctx.filter = `blur(${(2.5 * k).toFixed(1)}px)`; ctx.fillStyle = `rgba(150,52,20,${0.28 * sstep(0.6, 1, u)})`; ctx.fillText(TITLE, 0, 0); }
  ctx.restore();
  // 暗角；灯的亮暗用整体压黑来做（不降透明度，暖色不发灰）
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.98);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.62)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  if (on < 1) { ctx.fillStyle = `rgba(0,0,0,${1 - on})`; ctx.fillRect(0, 0, W, H); }
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
