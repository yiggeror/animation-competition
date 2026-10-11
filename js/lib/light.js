// 光照图：先画好线稿和固有色，再把一张"光照图"用正片叠底盖上去。
// 光照图 = 环境光 + 每个光源（马灯、月光、手电、日光灯）的照度；每个光源可以挖掉被挡住的部分（投影）。
// 发光体本身（火苗、灯罩、屏幕、透光的床单）在叠底之后用"加亮"画，所以它们比白纸还亮。

let main = null;
function canvasLike(i, w, h) {
  main ||= [];
  let c = main[i];
  if (!c) c = main[i] = new OffscreenCanvas(w, h);
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  return c;
}

export class LightMap {
  // ctx：主画布；ambient：'r,g,b'（0–255，255 = 不压暗）
  constructor(ctx, ambient = '60,60,70') {
    this.ctx = ctx;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    this.cv = canvasLike(0, W, H);
    this.c = this.cv.getContext('2d');
    this.m = ctx.getTransform();
    const c = this.c;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.globalCompositeOperation = 'source-over';
    c.globalAlpha = 1; c.filter = 'none';
    c.fillStyle = `rgb(${ambient})`;
    c.fillRect(0, 0, W, H);
    c.setTransform(this.m);
    c.globalCompositeOperation = 'lighter';
  }
  // 一个光源单独画在临时层上，可以先挖掉影子再加到光照图里。fn(c) 在局部坐标里画光；occlude(c) 画挡光的形状
  light(fn, occlude = null, blur = 0) {
    const W = this.cv.width, H = this.cv.height;
    const t = canvasLike(1, W, H), tc = t.getContext('2d');
    tc.setTransform(1, 0, 0, 1, 0, 0); tc.globalCompositeOperation = 'source-over'; tc.globalAlpha = 1; tc.filter = 'none';
    tc.clearRect(0, 0, W, H);
    tc.setTransform(this.m);
    fn(tc);
    if (occlude) {
      const s = canvasLike(2, W, H), sc = s.getContext('2d');
      sc.setTransform(1, 0, 0, 1, 0, 0); sc.globalCompositeOperation = 'source-over'; sc.filter = 'none'; sc.clearRect(0, 0, W, H);
      sc.setTransform(this.m); sc.fillStyle = '#000';
      occlude(sc);
      tc.setTransform(1, 0, 0, 1, 0, 0);
      tc.globalCompositeOperation = 'destination-out';
      if (blur) tc.filter = `blur(${blur}px)`;
      tc.drawImage(s, 0, 0);
      tc.filter = 'none';
    }
    const c = this.c;
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.globalCompositeOperation = 'lighter'; c.drawImage(t, 0, 0); c.restore();
  }
  // 径向光（点光源）：r = 衰减半径，sx/sy 拉成椭圆
  point(x, y, r, rgb, a = 1, sx = 1, sy = 1, occlude = null, blur = 0) {
    this.light((c) => radial(c, x, y, r, rgb, a, sx, sy), occlude, blur);
  }
  poly(pts, rgb, a = 1, blur = 0) {
    const c = this.c;
    c.save();
    if (blur) c.filter = `blur(${blur}px)`;
    c.fillStyle = `rgba(${rgb},${a})`;
    c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath(); c.fill();
    c.restore();
  }
  fill(rgb, a = 1) {
    const c = this.c;
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.fillStyle = `rgba(${rgb},${a})`; c.fillRect(0, 0, this.cv.width, this.cv.height); c.restore();
  }
  apply() {
    const m = this.ctx;
    m.save(); m.setTransform(1, 0, 0, 1, 0, 0);
    m.globalCompositeOperation = 'multiply';
    m.drawImage(this.cv, 0, 0);
    m.restore();
  }
}

// 平滑的钟形衰减（不出现光圈）
export function radial(c, x, y, r, rgb, a = 1, sx = 1, sy = 1) {
  if (a <= 0.002 || r <= 0) return;
  c.save();
  c.translate(x, y); c.scale(sx, sy);
  const g = c.createRadialGradient(0, 0, 0, 0, 0, r);
  for (const [u, k] of [[0, 1], [0.15, 0.9], [0.3, 0.72], [0.5, 0.45], [0.7, 0.2], [0.85, 0.07], [1, 0]]) g.addColorStop(u, `rgba(${rgb},${a * k})`);
  c.fillStyle = g;
  c.fillRect(-r, -r, 2 * r, 2 * r);
  c.restore();
}
// 加亮的光晕（画在主画布上，叠底之后）
export function glow(ctx, x, y, r, rgb, a = 1, sx = 1, sy = 1) {
  if (a <= 0.002) return;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  ctx.translate(x, y); ctx.scale(sx, sy);
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, r);
  g.addColorStop(0, `rgba(${rgb},${a})`);
  g.addColorStop(0.3, `rgba(${rgb},${a * 0.4})`);
  g.addColorStop(1, `rgba(${rgb},0)`);
  ctx.fillStyle = g;
  ctx.fillRect(-r, -r, 2 * r, 2 * r);
  ctx.restore();
}
