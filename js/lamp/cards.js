// 卡片：2D 画好的形状 → 固有色 + 法线 + 材质/深度三张图，交给着色器在场景的光里计算。
// 法线从轮廓算：每块形状做一次精确的欧氏距离变换，离边越远"鼓"得越高（圆弧截面），
// 所以边缘的法线是横着的（被侧光、逆光勾出亮边），中间朝着镜头。这是"压扁的立体"，不是 3D 建模。
//
// 部件 part：{ path: Path2D（画面像素）, fill: 颜色, R: 圆鼓半径（像素）, tilt: [x, y] 法线偏向, mat: 材质号, extra: 0..1,
//            detail(ctx): 在这块形状上画细节（只进固有色）, shadow: 投在下面部件上的接触阴影（像素）, noNormal: 只画颜色 }
// 材质号：0 普通 1 皮肤 2 头发 3 布（有绒毛逆光） 4 眼睛高光（映着床单） 7 牛皮（马灯透过来）

export const MAT_STEP = 30;
const POOL = {};
function scratch(key, W, H) {
  let c = POOL[key];
  if (!c) c = POOL[key] = new OffscreenCanvas(W, H);
  if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
  const x = c.getContext('2d', { willReadFrequently: true });
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none';
  x.clearRect(0, 0, W, H);
  return [c, x];
}

// 一维平方距离变换（Felzenszwalb & Huttenlocher）
function dt1(f, n, d, v, z) {
  let k = 0; v[0] = 0; z[0] = -Infinity; z[1] = Infinity;
  for (let q = 1; q < n; q++) {
    let s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
    while (s <= z[k]) { k--; s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]); }
    k++; v[k] = q; z[k] = s; z[k + 1] = Infinity;
  }
  k = 0;
  for (let q = 0; q < n; q++) { while (z[k + 1] < q) k++; const dq = q - v[k]; d[q] = dq * dq + f[v[k]]; }
}
// 形状内部每个像素到边的距离（像素）。inside: Uint8Array（1 = 在形状里）
export function edt(inside, w, h) {
  const INF = 1e10, n = Math.max(w, h);
  const f = new Float64Array(n), d = new Float64Array(n), v = new Int32Array(n), z = new Float64Array(n + 1);
  const g = new Float64Array(w * h);
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) f[y] = inside[y * w + x] ? INF : 0;
    dt1(f, h, d, v, z);
    for (let y = 0; y < h; y++) g[y * w + x] = d[y];
  }
  const out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) f[x] = g[y * w + x];
    dt1(f, w, d, v, z);
    for (let x = 0; x < w; x++) out[y * w + x] = Math.sqrt(d[x]);
  }
  return out;
}

// 由一块形状的 alpha 算法线贴图（RGBA：法线编码 + alpha）
function normalTile(alpha, w, h, R, tilt = [0, 0], flat = 0) {
  const inside = new Uint8Array(w * h);
  for (let i = 0; i < w * h; i++) inside[i] = alpha[i * 4 + 3] > 127 ? 1 : 0;
  const d = edt(inside, w, h);
  // 圆弧截面的高度；再轻轻模糊一下，免得中轴线上出现折痕
  const hgt = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) { const u = Math.min(d[i] + 0.5, R) / R; hgt[i] = inside[i] ? R * Math.sqrt(Math.max(0, 1 - (1 - u) * (1 - u))) : 0; }
  const bl = boxBlur(boxBlur(hgt, w, h, Math.max(1, Math.round(R * 0.12))), w, h, Math.max(1, Math.round(R * 0.12)));
  const out = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    const a = alpha[i * 4 + 3];
    if (!a) continue;
    const xl = Math.max(0, x - 1), xr = Math.min(w - 1, x + 1), yu = Math.max(0, y - 1), yd = Math.min(h - 1, y + 1);
    // 边上（距离很小）用形状自己的梯度方向，保证轮廓处法线是横的
    let hx = (bl[y * w + xr] - bl[y * w + xl]) / (xr - xl), hy = (bl[yd * w + x] - bl[yu * w + x]) / (yd - yu);
    if (d[i] < 1.6) {
      const gx = d[y * w + xr] - d[y * w + xl], gy = d[yd * w + x] - d[yu * w + x], gl = Math.hypot(gx, gy) || 1;
      hx = (gx / gl) * 6; hy = (gy / gl) * 6;
    }
    let nx = -hx + tilt[0], ny = hy + tilt[1], nz = 1 + flat;
    const l = Math.hypot(nx, ny, nz);
    out[i * 4] = ((nx / l) * 0.5 + 0.5) * 255; out[i * 4 + 1] = ((ny / l) * 0.5 + 0.5) * 255; out[i * 4 + 2] = ((nz / l) * 0.5 + 0.5) * 255;
    out[i * 4 + 3] = a;
  }
  return out;
}
function boxBlur(src, w, h, r) {
  const tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) { let s = 0; for (let x = -r; x <= r; x++) s += src[y * w + Math.min(w - 1, Math.max(0, x))];
    for (let x = 0; x < w; x++) { tmp[y * w + x] = s / (2 * r + 1); s += src[y * w + Math.min(w - 1, x + r + 1)] - src[y * w + Math.max(0, x - r)]; } }
  for (let x = 0; x < w; x++) { let s = 0; for (let y = -r; y <= r; y++) s += tmp[Math.min(h - 1, Math.max(0, y)) * w + x];
    for (let y = 0; y < h; y++) { out[y * w + x] = s / (2 * r + 1); s += tmp[Math.min(h - 1, y + r + 1) * w + x] - tmp[Math.max(0, y - r) * w + x]; } }
  return out;
}

export class Cards {
  constructor(W, H) {
    this.W = W; this.H = H;
    const mk = () => { const c = new OffscreenCanvas(W, H); const x = c.getContext('2d'); return [c, x]; };
    [this.alb, this.a] = mk(); [this.nrm, this.n] = mk(); [this.mat, this.m] = mk();
  }
  clear() { for (const x of [this.a, this.n, this.m]) { x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, this.W, this.H); } }
  // 一个人物的所有部件（从后往前）。同一 group 的部件（比如上臂、前臂、拳头）合成一个轮廓算法线，
  // 这样手腕、膝盖、脚踝这些地方是一整块连续的肉，不会出现"木偶关节"那样的接缝；颜色和细节仍然按部件画。
  addAll(parts, depth) {
    const groups = {};
    for (const p of parts) if (p.group && !p.noNormal) (groups[p.group] ||= []).push(p);
    const tiles = {};
    for (const [g, ps] of Object.entries(groups)) {
      let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity;
      for (const p of ps) { a = Math.min(a, p.bbox[0]); b = Math.min(b, p.bbox[1]); c = Math.max(c, p.bbox[2]); d = Math.max(d, p.bbox[3]); }
      const x0 = Math.max(0, Math.floor(a) - 4), y0 = Math.max(0, Math.floor(b) - 4);
      const x1 = Math.min(this.W, Math.ceil(c) + 4), y1 = Math.min(this.H, Math.ceil(d) + 4);
      const w = x1 - x0, h = y1 - y0;
      if (w <= 0 || h <= 0) continue;
      const mc = new OffscreenCanvas(w, h), mx = mc.getContext('2d', { willReadFrequently: true });
      mx.translate(-x0, -y0); mx.fillStyle = '#fff';
      for (const p of ps) mx.fill(p.path, p.rule || 'nonzero');
      const alpha = mx.getImageData(0, 0, w, h).data;
      const lead = ps.find((p) => p.groupR) || ps[0];
      const tile = normalTile(alpha, w, h, Math.max(1.5, lead.groupR ?? lead.R), lead.tilt, lead.flat || 0);
      const cv = new OffscreenCanvas(w, h);
      cv.getContext('2d').putImageData(new ImageData(tile, w, h), 0, 0);
      tiles[g] = { cv, x0, y0, mask: mc, shadow: (ps.find((p) => p.shadow) || {}).shadow };
    }
    // 同一组的部件合起来只往下面的东西投一次接触阴影（在组里第一块画之前），组内部件之间不互相投——
    // 不然手的影子落在前臂上，手腕处就多出一道暗边，像接缝
    const shadowed = {};
    for (const p of parts) {
      const t = p.group ? tiles[p.group] : null;
      if (t && t.shadow && !shadowed[p.group]) {
        shadowed[p.group] = true;
        const sh = t.shadow;
        this.a.save();
        this.a.globalCompositeOperation = 'source-atop';
        this.a.filter = `blur(${sh[2] ?? 4}px)`;
        this.a.globalAlpha = sh[3] ?? 0.45;
        const [bc, bx] = scratch('gsh', t.mask.width, t.mask.height);
        bx.drawImage(t.mask, 0, 0); bx.globalCompositeOperation = 'source-in'; bx.fillStyle = '#000'; bx.fillRect(0, 0, bc.width, bc.height);
        this.a.drawImage(bc, t.x0 + sh[0], t.y0 + sh[1]);
        this.a.restore();
      }
      this.add(p, depth, t, !!t);
    }
    this.cleanMat(parts);
  }
  // 一张画好的人物图当作一块卡片：固有色、法线、材质三张图（tools/card_maps.py 算好），按图片像素 → 画面像素的映射画上去。
  // 卡片是一块竖着的平面，斜着看有透视：把图竖着切成几条，每条用自己的仿射变换（strips: [{x0, x1, m:[a,b,c,d,e,f]}]，x 是图片像素）。
  addImage(maps, strips, depth) {
    const { W, H } = this;
    const draw = (ctx, img) => {
      for (const st of strips) {
        ctx.save();
        ctx.setTransform(...st.m);
        if (strips.length > 1) { ctx.beginPath(); ctx.rect(st.x0 - 0.6, -2, st.x1 - st.x0 + 1.2, img.height + 4); ctx.clip(); }
        ctx.drawImage(img, 0, 0);
        ctx.restore();
      }
    };
    draw(this.a, maps.alb);
    draw(this.n, maps.nrm);
    // 材质：R 通道是深度，每次按这一帧的深度填
    const [mc, mx] = scratch('imgmat', W, H);
    draw(mx, maps.mat);
    const id = mx.getImageData(0, 0, W, H), D = id.data, dr = Math.round((depth / 8) * 255);
    for (let i = 0; i < D.length; i += 4) if (D[i + 3]) D[i] = dr;
    mx.putImageData(id, 0, 0);
    this.m.drawImage(mc, 0, 0);
    // 缩放插值会在材质交界处混出中间值，和部件一样清理掉
    let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity;
    for (const st of strips) for (const [x, y] of [[st.x0, 0], [st.x1, 0], [st.x0, maps.alb.height], [st.x1, maps.alb.height]]) {
      const X = st.m[0] * x + st.m[2] * y + st.m[4], Y = st.m[1] * x + st.m[3] * y + st.m[5];
      a = Math.min(a, X); b = Math.min(b, Y); c = Math.max(c, X); d = Math.max(d, Y);
    }
    this.cleanMat([{ bbox: [a, b, c, d] }]);
    return [a, b, c, d];
  }
  // 材质图上，两种材质交界处抗锯齿会混出中间值（比如皮肤 30 和眼睛高光 120 混成 75，会被当成"布"打光）。
  // 把这些像素换成旁边干净像素的材质号——材质边界不需要抗锯齿，颜色和法线本来就是平滑的。
  cleanMat(parts) {
    let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity;
    for (const p of parts) { a = Math.min(a, p.bbox[0]); b = Math.min(b, p.bbox[1]); c = Math.max(c, p.bbox[2]); d = Math.max(d, p.bbox[3]); }
    const x0 = Math.max(0, Math.floor(a) - 2), y0 = Math.max(0, Math.floor(b) - 2), x1 = Math.min(this.W, Math.ceil(c) + 2), y1 = Math.min(this.H, Math.ceil(d) + 2);
    const w = x1 - x0, h = y1 - y0;
    if (w <= 0 || h <= 0) return;
    const img = this.m.getImageData(x0, y0, w, h), D = img.data;
    const clean = (g) => { const r = g % MAT_STEP; return r <= 3 || r >= MAT_STEP - 3; };
    const src = new Uint8ClampedArray(D);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      if (!D[i + 3] || clean(src[i + 1])) continue;
      let best = -1;
      for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [1, -1], [-1, 1], [-2, 0], [2, 0], [0, -2], [0, 2]]) {
        const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
        const j = (yy * w + xx) * 4; if (src[j + 3] > 200 && clean(src[j + 1])) { best = j; break; }
      }
      if (best >= 0) { D[i + 1] = Math.round(src[best + 1] / MAT_STEP) * MAT_STEP; D[i] = src[best]; D[i + 2] = src[best + 2]; }
    }
    this.m.putImageData(img, x0, y0);
  }
  // depth：离镜头的距离（米）；gtile：这块所在组合起来算好的法线（有的话）
  add(part, depth, gtile = null, noShadow = false) {
    const { W, H } = this;
    const path = part.path;
    // 包围盒（多留一点边）
    const bb = part.bbox;
    const x0 = Math.max(0, Math.floor(bb[0]) - 4), y0 = Math.max(0, Math.floor(bb[1]) - 4);
    const x1 = Math.min(W, Math.ceil(bb[2]) + 4), y1 = Math.min(H, Math.ceil(bb[3]) + 4);
    const w = x1 - x0, h = y1 - y0;
    if (w <= 0 || h <= 0) return;
    // 接触阴影：这块形状在下面部件上投一点模糊的暗影
    if (part.shadow && !noShadow) {
      const [s, sx] = scratch('sh', W, H);
      sx.fillStyle = '#000'; sx.fill(path, part.rule || 'nonzero');
      this.a.save();
      this.a.globalCompositeOperation = 'source-atop';
      this.a.filter = `blur(${part.shadow[2] ?? 4}px)`;
      this.a.globalAlpha = part.shadow[3] ?? 0.45;
      this.a.drawImage(s, part.shadow[0], part.shadow[1]);
      this.a.restore();
    }
    // 固有色 + 细节
    this.a.save();
    this.a.fillStyle = part.fill; this.a.fill(path, part.rule || 'nonzero');
    if (part.detail) { this.a.clip(path, part.rule || 'nonzero'); part.detail(this.a); }
    this.a.restore();
    if (part.noNormal) return;
    // 法线（keepNormal：不改下面的法线，只换材质——比如眼睛里的高光点）
    if (part.keepNormal) {
    } else if (gtile) {
      this.n.save(); this.n.clip(path, part.rule || 'nonzero'); this.n.drawImage(gtile.cv, gtile.x0, gtile.y0); this.n.restore();
    } else {
      const [mc, mx] = scratch('mask', w, h);
      mx.translate(-x0, -y0); mx.fillStyle = '#fff'; mx.fill(path, part.rule || 'nonzero');
      const alpha = mx.getImageData(0, 0, w, h).data;
      const tile = normalTile(alpha, w, h, Math.max(1.5, part.R), part.tilt, part.flat || 0);
      const [tc, tx] = scratch('tile', w, h);
      tx.putImageData(new ImageData(tile, w, h), 0, 0);
      this.n.drawImage(tc, x0, y0);
    }
    // 材质：R = 深度/8，G = 材质号 × 30（间隔拉大：部件边缘抗锯齿混合时 8 位取整会把 1 舍成 0，
    // 那一圈像素就被当成别的材质打光，显出一道"关节缝"），B = extra
    this.m.save();
    this.m.fillStyle = `rgb(${Math.round((depth / 8) * 255)},${(part.mat || 0) * MAT_STEP},${Math.round((part.extra || 0) * 255)})`;
    this.m.fill(path, part.rule || 'nonzero');
    this.m.restore();
  }
}

// 路径的包围盒
export function bboxOf(pts) {
  let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity;
  for (const [x, y] of pts) { if (x < a) a = x; if (y < b) b = y; if (x > c) c = x; if (y > d) d = y; }
  return [a, b, c, d];
}
