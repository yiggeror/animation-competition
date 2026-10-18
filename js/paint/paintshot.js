// 屋内镜头的渲染："背景图 + 人物图 + 程序打光"（第 1–4、10–13 场）。
// 背景和人物是合作 AI 画的平光图（白天室内、光线平均）；夜里的明暗全部由程序加：
//   1. 固有色：背景 + 人物（各自的位置、缩放、小动作）合成一张图
//   2. 光照图：环境底色（日光灯的冷白 / 停电的蓝黑） + 光源（马灯的暖光晕、月光从窗口斜进来的光柱、手电的光锥），
//      光源会闪（火苗）；光照图在线性空间里算，再和固有色相乘
//   3. 发光的东西直接加上去：马灯的火苗和玻璃罩、电视屏、手机屏
//   4. 空气里被照亮的灰尘、颗粒、暗角；镜头可以平移和推拉
// 一个镜头 = { bg, size:[W,H]（背景图的像素尺寸）, layers(t), light(t), glow(t), emit?(ctx,t), cam(t) }，坐标都是背景图的像素。
const cache = {};
export async function loadImg(name) {
  if (cache[name]) return cache[name];
  const r = await fetch(name.includes('/') ? name : `/assets/paint/${name}.png`);
  if (!r.ok) return (cache[name] = null);
  return (cache[name] = await createImageBitmap(await r.blob()));
}

// 占位背景（背景图还没交的时候用）：一间简单的屋子，墙、地、窗
export function placeholderBg(W, H) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.fillStyle = '#d9cbb4'; x.fillRect(0, 0, W, H * 0.62);
  x.fillStyle = '#9a8a74'; x.fillRect(0, H * 0.62, W, H * 0.38);
  x.fillStyle = '#5d6f86'; x.fillRect(W * 0.08, H * 0.18, W * 0.16, H * 0.26);
  x.strokeStyle = '#6b4f34'; x.lineWidth = W * 0.008; x.strokeRect(W * 0.08, H * 0.18, W * 0.16, H * 0.26);
  x.fillStyle = '#7a5a3c'; x.fillRect(W * 0.62, H * 0.2, W * 0.2, H * 0.48);
  x.fillStyle = '#3a3a3a'; x.fillRect(W * 0.3, H * 0.4, W * 0.14, H * 0.12);
  x.fillStyle = '#c9b48c'; x.fillRect(W * 0.3, H * 0.66, W * 0.34, H * 0.14);
  return c;
}

const srgb2lin = (v) => Math.pow(v / 255, 2.2);
const lin2srgb = (v) => Math.round(255 * Math.pow(Math.max(0, Math.min(1, v)), 1 / 2.2));

// 光照描述：
// { ambient:[r,g,b]（线性，0..1 左右）, lights:[{ x, y, r（半径，像素）, color:[r,g,b], i（强度）, falloff? }],
//   shafts:[{ poly:[[x,y]...]（光柱的四边形）, color, i, soft（边缘羽化像素） }],
//   cone:{ x, y, ang, spread, len, color, i }（手电） }
function lightMap(W, H, L) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  // 在线性空间里叠加：先在一张浮点数组上算，再写回（2D 画布不支持浮点，叠加次数不多，直接按像素算）
  const buf = new Float32Array(W * H * 3);
  const a = L.ambient || [0, 0, 0];
  for (let i = 0; i < W * H; i++) { buf[i * 3] = a[0]; buf[i * 3 + 1] = a[1]; buf[i * 3 + 2] = a[2]; }
  for (const l of L.lights || []) {
    const x0 = Math.max(0, Math.floor(l.x - l.r)), x1 = Math.min(W, Math.ceil(l.x + l.r)), y0 = Math.max(0, Math.floor(l.y - l.r)), y1 = Math.min(H, Math.ceil(l.y + l.r));
    const fo = l.falloff ?? 2.0;
    for (let y = y0; y < y1; y++) for (let xx = x0; xx < x1; xx++) {
      const d = Math.hypot(xx - l.x, y - l.y) / l.r; if (d >= 1) continue;
      // 近处亮、远处暗：平方反比的软化版本，在半径处正好衰减到 0
      const k = l.i * (1 - d) ** fo / (1 + 8 * d * d), i = (y * W + xx) * 3;
      buf[i] += l.color[0] * k; buf[i + 1] += l.color[1] * k; buf[i + 2] += l.color[2] * k;
    }
  }
  // 光柱和手电：先画到一张灰度遮罩上（用画布的多边形和模糊），再按颜色加进去
  const extras = [];
  for (const s of L.shafts || []) {
    const m = new OffscreenCanvas(W, H), mx = m.getContext('2d');
    mx.filter = `blur(${s.soft ?? 20}px)`; mx.fillStyle = '#fff';
    mx.beginPath(); s.poly.forEach(([px, py], j) => (j ? mx.lineTo(px, py) : mx.moveTo(px, py))); mx.closePath(); mx.fill();
    extras.push([m, s.color, s.i]);
  }
  if (L.cone) {
    const k = L.cone, m = new OffscreenCanvas(W, H), mx = m.getContext('2d');
    const g = mx.createRadialGradient(k.x, k.y, 0, k.x, k.y, k.len);
    g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.6, 'rgba(255,255,255,0.5)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    mx.filter = `blur(${k.soft ?? 12}px)`; mx.fillStyle = g;
    mx.beginPath(); mx.moveTo(k.x, k.y); mx.arc(k.x, k.y, k.len, k.ang - k.spread, k.ang + k.spread); mx.closePath(); mx.fill();
    extras.push([m, k.color, k.i]);
  }
  for (const [m, col, inten] of extras) {
    const d = m.getContext('2d').getImageData(0, 0, W, H).data;
    // getImageData 给的是未预乘的颜色：模糊/渐变边上 alpha 很小的像素 RGB 仍是 255，要乘 alpha 才是真实覆盖（合作方查出 S10 光柱的硬亮宽边）
    for (let i = 0; i < W * H; i++) { const v = d[i * 4] / 255 * d[i * 4 + 3] / 255 * inten; if (v > 0) { buf[i * 3] += col[0] * v; buf[i * 3 + 1] += col[1] * v; buf[i * 3 + 2] += col[2] * v; } }
  }
  return buf;
}

// 人物按法线受光（原来只有一张平的光照图乘上去，人物像贴上去的）：按场景里各盏灯对这个人的贡献算出主光方向，
// 朝光的一侧提亮、背光的一侧压暗（法线朝镜头的地方不变，整体不变暗）；灯在头顶时再加一点上亮下暗。
// 法线图的编码同 tools/card_soft.py：RGB = (n * 0.5 + 0.5) * 255，y 朝上。
function shadeLayer(L, img, nrm, Lt) {
  const w = img.width, h = img.height;
  const cx = L.x + (w / 2 - (L.ox || 0)) * L.sc, cy = L.y + (h / 2 - (L.oy || 0)) * L.sc;
  let lx = 0, ly = 0, lz = 0, tot = 0;
  for (const l of Lt.lights || []) {
    const d = Math.hypot(cx - l.x, cy - l.y) / l.r; if (d >= 1) continue;
    const k = l.i * (1 - d) ** (l.falloff ?? 2.0) / (1 + 8 * d * d) * (l.color[0] + l.color[1] + l.color[2]) / 3;
    const dx = l.x - cx, dy = cy - l.y, n = Math.hypot(dx, dy) || 1;
    lx += k * 0.8 * dx / n; ly += k * 0.8 * dy / n; lz += k * 0.6; tot += k;
  }
  if (tot <= 1e-4) return img;
  const ln = Math.hypot(lx, ly, lz); lx /= ln; ly /= ln; lz /= ln;
  const amb = ((Lt.ambient || [0, 0, 0]).reduce((a, b) => a + b, 0)) / 3, ratio = tot / (tot + amb);
  const ks = 2.6 * ratio, kv = ly > 0.3 ? 0.3 * ratio : 0;
  const c = new OffscreenCanvas(w, h), x = c.getContext('2d');
  x.drawImage(img, 0, 0); const id = x.getImageData(0, 0, w, h), D = id.data;
  const nc = new OffscreenCanvas(w, h), nx = nc.getContext('2d'); nx.drawImage(nrm, 0, 0, w, h);
  const N = nx.getImageData(0, 0, w, h).data;
  for (let yy = 0, i = 0; yy < h; yy++) {
    const fv = 1 + kv * (0.5 - yy / h);
    for (let xx = 0; xx < w; xx++, i += 4) {
      if (D[i + 3] === 0 || N[i + 3] === 0) continue;
      const dot = (N[i] / 127.5 - 1) * lx + (N[i + 1] / 127.5 - 1) * ly + (N[i + 2] / 127.5 - 1) * lz;
      const f = Math.min(1.4, Math.max(0.55, (1 + ks * (dot - lz)) * fv));
      D[i] = Math.min(255, D[i] * f); D[i + 1] = Math.min(255, D[i + 1] * f); D[i + 2] = Math.min(255, D[i + 2] * f);
    }
  }
  x.putImageData(id, 0, 0);
  return c;
}

// 接地影子：图层的剪影（黑色、只取 alpha）钉在它最低的那一行（脚、贴地的身子）上投到地面，再模糊，画在图层下面，之后跟场景一起乘光照图。
// 全景里人物脚下没有影子会像贴上去的。sy < 0：影子往镜头这边倒（灯在人后面/头顶偏后），越小越扁；sy > 0：往后倒；
// 趴着、躺着的人用 sy = 1、dy 两三像素：影子就在身子正下方露一圈。skew：影子越远越往旁边偏（灯在左边就给正数）。
const SIL = new WeakMap();
function silhouette(img) {
  if (SIL.has(img)) return SIL.get(img);
  const w = img.width, h = img.height, c = new OffscreenCanvas(w, h), x = c.getContext('2d');
  x.drawImage(img, 0, 0); const A = x.getImageData(0, 0, w, h).data;
  let base = 0; for (let yy = h - 1; yy >= 0 && !base; yy--) for (let xx = 0; xx < w; xx++) if (A[(yy * w + xx) * 4 + 3] > 128) { base = yy; break; }
  x.globalCompositeOperation = 'source-in'; x.fillStyle = '#000'; x.fillRect(0, 0, w, h);
  const s = { c, base }; SIL.set(img, s); return s;
}
function contactShadow(ax, L, img) {
  const k = L.contact, s = silhouette(img), sc = L.sc, base = k.base ?? s.base, by = L.y + base * sc;   // 贴地线（背景坐标），脚和影子在这里接上
  ax.save(); ax.globalAlpha = k.a ?? 0.35; ax.filter = `blur(${k.blur ?? 5}px)`;
  ax.translate(L.x + (k.dx || 0), by + (k.dy || 0)); if (k.skew) ax.transform(1, 0, k.skew, 1, 0, 0);
  ax.scale((L.flip ? -1 : 1) * sc, sc * (k.sy ?? -0.08)); ax.translate(0, -base);
  ax.drawImage(s.c, 0, 0); ax.restore();
}

// 渲染一帧。shot.layers(t) → [{ img, nrm?, x, y, sc, rot?, alpha?, flip?, clip?, contact? }]（contact = { a, blur, sy, skew, dx, dy, base? }：接地影子）（img 的像素 (0,0) 落在背景 (x, y)，缩放 sc；给了法线图 nrm 就按场景灯光打明暗）
export async function renderPaint(ctx, t, W, H, shot) {
  const [BW, BH] = shot.size;
  const bg = (typeof shot.bg === 'string' ? await loadImg(shot.bg) : shot.bg) || (cache['__ph'] ||= placeholderBg(BW, BH));   // bg 可以是素材名，也可以是现成的画布
  // 1. 固有色（背景坐标）
  const alb = new OffscreenCanvas(BW, BH), ax = alb.getContext('2d');
  ax.imageSmoothingQuality = 'high';   // 人物图缩得很小（0.14～0.24 倍），默认的低质量缩小会把细线断成一粒一粒（Astra 实测 S01 小满腿内侧）
  ax.drawImage(bg, 0, 0, BW, BH);
  const Lt = shot.light(t);
  for (const L of (await shot.layers?.(t)) || []) {
    let img = typeof L.img === 'string' ? await loadImg(L.img) : L.img; if (!img) continue;
    if (L.nrm) img = shadeLayer(L, img, L.nrm, Lt);
    if (L.contact) contactShadow(ax, L, img);
    ax.save(); ax.globalAlpha = L.alpha ?? 1;
    ax.translate(L.x, L.y); if (L.rot) ax.rotate(L.rot); ax.scale((L.flip ? -1 : 1) * L.sc, L.sc);
    if (L.clip) { ax.beginPath(); L.clip.forEach(([px, py], j) => (j ? ax.lineTo(px, py) : ax.moveTo(px, py))); ax.closePath(); ax.clip(); }
    ax.drawImage(img, L.ox ? -L.ox : 0, L.oy ? -L.oy : 0);
    if (L.overlay) L.overlay(ax);
    ax.restore();
  }
  // 2. 光照图 × 固有色（在线性空间里），再加发光
  const lm = lightMap(BW, BH, Lt);
  const id = ax.getImageData(0, 0, BW, BH), D = id.data, exp = Lt.exposure ?? 1;
  for (let i = 0, j = 0; i < D.length; i += 4, j += 3) {
    D[i] = lin2srgb(srgb2lin(D[i]) * lm[j] * exp); D[i + 1] = lin2srgb(srgb2lin(D[i + 1]) * lm[j + 1] * exp); D[i + 2] = lin2srgb(srgb2lin(D[i + 2]) * lm[j + 2] * exp);
  }
  ax.putImageData(id, 0, 0);
  // 3. 发光：火苗、玻璃罩、屏幕（叠加）
  ax.save(); ax.globalCompositeOperation = 'lighter';
  for (const g of shot.glow?.(t) || []) {
    const gr = ax.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.r);
    gr.addColorStop(0, `rgba(${g.color.join(',')},${g.a ?? 1})`); gr.addColorStop(g.core ?? 0.25, `rgba(${g.color.join(',')},${(g.a ?? 1) * 0.5})`); gr.addColorStop(1, `rgba(${g.color.join(',')},0)`);
    ax.fillStyle = gr; ax.fillRect(g.x - g.r, g.y - g.r, 2 * g.r, 2 * g.r);
  }
  ax.restore();
  // 3b. 自己画的发光体/不受光照的东西（火苗的形状、烟）：shot.emit(ctx, t)，背景坐标
  if (shot.emit) { ax.save(); shot.emit(ax, t); ax.restore(); }
  // 4. 镜头：平移、推拉（cam = { x, y, zoom }：画面中心对着背景的 (x, y)，zoom = 画面像素 / 背景像素）
  const cam0 = shot.cam?.(t) || { x: BW / 2, y: BH / 2, fit: 1 };
  const cam = { ...cam0, zoom: cam0.fit != null ? cam0.fit * W / BW : cam0.zoom };   // fit：相对"背景宽度正好铺满画面"的倍数（和输出分辨率无关）
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ctx.translate(W / 2, H / 2); ctx.scale(cam.zoom, cam.zoom); ctx.translate(-cam.x, -cam.y);
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(alb, 0, 0);
  ctx.restore();
  // 暗角和颗粒
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 0.95);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${Lt.vignette ?? 0.35})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let seed = Math.floor(t * 24) * 7919 + 13;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const gs = Lt.grain ?? 6;
  for (let i = 0; i < G.length; i += 4) { const n = (rnd() - 0.5) * gs; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
