// 剪纸片的"一张张纸"：人物、布景都由若干闭合的纸片组成（已经变换到画面坐标）。
// 同一组纸片可以用三种画法画出来，方便比较：
//   paper     剪纸片：彩纸分层，纸边受光，下层有柔和投影，镂空处露出下一层的颜色，纸有纤维纹理
//   silhouette 剪影：所有纸片是一整块深色剪影，镂空处透光，面向光源的边被勾亮
//   gongbi    工笔：细而匀的铁线描勾整体轮廓，矿物色平涂，边缘一层层渲染加深
//
// 纸片 piece：{ pts, z, fill, under?, holes?: [pts...], slits?: [{pts, w}], dots?: [{c, r, fill}], group?, name?, emissive?, flat? }（都是画面像素）
//   pts/holes 是控制点（会做 Catmull-Rom 平滑，flat: true 时不平滑）；slits 是刻出来的细缝（w 厘米）；dots 是小圆片（眼珠、腮红、扣子）。
import { catmull } from '../lib/draw.js';

const POOL = {};
function scratch(key, W, H) {
  let c = POOL[key];
  if (!c) c = POOL[key] = new OffscreenCanvas(W, H);
  if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
  const x = c.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none';
  x.clearRect(0, 0, W, H);
  return [c, x];
}

// 纸纹：一张随机纤维的灰度图，正片叠底用
let FIBER = null;
function fiber() {
  if (FIBER) return FIBER;
  const N = 256, c = new OffscreenCanvas(N, N), x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, N, N);
  let s = 7;
  const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 900; i++) {
    const px = rnd() * N, py = rnd() * N, a = rnd() * Math.PI, l = 3 + rnd() * 14;
    x.strokeStyle = `rgba(110,90,70,${0.05 + rnd() * 0.12})`;
    x.lineWidth = 0.5 + rnd() * 0.8;
    x.beginPath(); x.moveTo(px, py); x.lineTo(px + Math.cos(a) * l, py + Math.sin(a) * l); x.stroke();
  }
  for (let i = 0; i < 2500; i++) { x.fillStyle = `rgba(120,100,80,${rnd() * 0.08})`; x.fillRect(rnd() * N, rnd() * N, 1.2, 1.2); }
  return (FIBER = c);
}

function pathOf(pts, flat, per = 4) {
  const q = flat ? pts : catmull(pts, true, per);
  const p = new Path2D();
  q.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y)));
  p.closePath();
  return p;
}
function slitPath(pts) {
  const q = pts.length > 2 ? catmull(pts, false, 5) : pts;
  const p = new Path2D();
  q.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y)));
  return p;
}
function prep(pc) {
  if (pc._p) return pc;
  pc._p = pathOf(pc.pts, pc.flat);
  pc._full = new Path2D(pc._p);
  if (pc.holes?.length) {
    pc._cut = new Path2D(pc._p);
    for (const h of pc.holes) pc._cut.addPath(pathOf(h, pc.flatHoles ?? false, 3));
  }
  return pc;
}

// opts: { s: 每厘米多少像素（细缝宽度用）, shadow: [dx, dy] 像素, ink, rim: {dir, rgb, a, w}, silhouette: 颜色 }
export function drawPieces(ctx, pieces, style, opts = {}) {
  const list = pieces.filter(Boolean).map(prep).sort((a, b) => a.z - b.z);
  if (style === 'silhouette') return silhouette(ctx, list, opts);
  if (style === 'gongbi') return gongbi(ctx, list, opts);
  return paper(ctx, list, opts);
}

// ------------------------------------------------------------------ 剪纸片
function paper(ctx, list, o) {
  const s = o.s ?? 6;
  const sh = o.shadow ?? [s * 0.35, s * 0.55];
  const pat = ctx.createPattern(fiber(), 'repeat');
  for (const pc of list) {
    // 1. 投在下面各层上的影子
    if (!pc.noShadow) {
      ctx.save();
      ctx.translate(sh[0] * (pc.lift ?? 1), sh[1] * (pc.lift ?? 1));
      ctx.filter = `blur(${(o.shadowBlur ?? s * 0.35) * (pc.lift ?? 1)}px)`;
      ctx.fillStyle = o.shadowColor ?? 'rgba(38,22,12,0.34)';
      ctx.fill(pc._cut || pc._p, 'evenodd');
      ctx.restore();
    }
    ctx.save();
    // 2. 镂空下面那层的颜色
    if (pc.under && pc._cut) { ctx.fillStyle = pc.under; ctx.fill(pc._p); }
    // 3. 纸
    ctx.fillStyle = pc.fill;
    ctx.fill(pc._cut || pc._p, 'evenodd');
    // 4. 纸纹 + 纸边
    ctx.clip(pc._p);
    if (!pc.emissive) {
      ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = pc.fiber ?? 0.55;
      ctx.fillStyle = pat; ctx.fill(pc._p);
      ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    }
    ctx.strokeStyle = 'rgba(255,250,236,0.26)'; ctx.lineWidth = Math.max(1, s * 0.18); ctx.stroke(pc._p);
    // 镂空的边：里面一圈暗（纸有厚度）
    if (pc._cut) {
      ctx.strokeStyle = 'rgba(40,24,14,0.38)'; ctx.lineWidth = Math.max(1, s * 0.2);
      for (const h of pc.holes) ctx.stroke(pathOf(h, pc.flatHoles ?? false, 3));
    }
    ctx.restore();
    // 5. 刻缝、小圆片
    for (const sl of pc.slits || []) {
      ctx.save(); ctx.clip(pc._p);
      ctx.strokeStyle = sl.color ?? 'rgba(46,28,18,0.82)'; ctx.lineWidth = Math.max(0.8, sl.w); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.stroke(slitPath(sl.pts));
      ctx.restore();
    }
    for (const d of pc.dots || []) {
      ctx.save();
      if (d.shadow !== false) { ctx.translate(sh[0] * 0.3, sh[1] * 0.3); ctx.fillStyle = 'rgba(38,22,12,0.25)'; ctx.beginPath(); ctx.ellipse(d.c[0], d.c[1], d.r * (d.sx ?? 1), d.r * (d.sy ?? 1), d.rot ?? 0, 0, Math.PI * 2); ctx.fill(); ctx.translate(-sh[0] * 0.3, -sh[1] * 0.3); }
      ctx.fillStyle = d.fill; ctx.beginPath(); ctx.ellipse(d.c[0], d.c[1], d.r * (d.sx ?? 1), d.r * (d.sy ?? 1), d.rot ?? 0, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }
}

// ------------------------------------------------------------------ 剪影
function silhouette(ctx, list, o) {
  const W = ctx.canvas.width, H = ctx.canvas.height, s = o.s ?? 6;
  const [L, lc] = scratch('sil', W, H);
  lc.setTransform(ctx.getTransform());
  const col = o.silhouette ?? '#1a1420';
  for (const pc of list) {
    if (pc.emissive) continue;
    lc.globalCompositeOperation = 'source-over';
    lc.fillStyle = pc.silFill ?? col;
    lc.fill(pc._p);
    // 镂空透光（只在这一片的范围里挖）
    if (pc._cut && !pc.noSilHoles) {
      lc.globalCompositeOperation = 'destination-out';
      for (const h of pc.holes) lc.fill(pathOf(h, pc.flatHoles ?? false, 3));
    }
    lc.globalCompositeOperation = 'destination-out';
    for (const sl of pc.slits || []) if (sl.sil !== false) { lc.lineWidth = Math.max(1, sl.w * 0.9); lc.lineCap = 'round'; lc.strokeStyle = '#000'; lc.stroke(slitPath(sl.pts)); }
    for (const d of pc.dots || []) if (d.sil) { lc.fillStyle = '#000'; lc.beginPath(); lc.ellipse(d.c[0], d.c[1], d.r * (d.sx ?? 1), d.r * (d.sy ?? 1), d.rot ?? 0, 0, Math.PI * 2); lc.fill(); }
  }
  // 亮边：剪影整体平移、相减，面向光源一侧留下一道边
  if (o.rim) {
    const [R, rc] = scratch('silrim', W, H);
    rc.drawImage(L, 0, 0);
    rc.globalCompositeOperation = 'destination-out';
    const k = W / 1920, w = (o.rim.w ?? 5) * k, d = o.rim.dir, len = Math.hypot(d[0], d[1]) || 1;
    rc.drawImage(L, (-d[0] / len) * w, (-d[1] / len) * w);
    rc.globalCompositeOperation = 'source-in';
    rc.fillStyle = `rgb(${o.rim.rgb})`; rc.fillRect(0, 0, W, H);
    lc.setTransform(1, 0, 0, 1, 0, 0);
    lc.globalCompositeOperation = 'source-atop';
    lc.globalAlpha = o.rim.a ?? 0.9;
    lc.filter = `blur(${(o.rim.blur ?? 1) * k}px)`;
    lc.drawImage(R, 0, 0);
    lc.filter = 'none'; lc.globalAlpha = 1;
  }
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(L, 0, 0); ctx.restore();
}

// ------------------------------------------------------------------ 工笔
function gongbi(ctx, list, o) {
  const s = o.s ?? 6;
  const ink = o.ink ?? '#231915';
  const lw = Math.max(1.7, (o.lw ?? 0.3) * s);
  ctx.save();
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  // 整体外轮廓：所有纸片先描双倍宽的线，再上色（重叠处的内线被盖住）——同一组的人物只有一条连续的外轮廓
  const groups = {};
  for (const pc of list) (groups[pc.group ?? pc.name ?? '_'] ||= []).push(pc);
  for (const g of Object.values(groups)) {
    ctx.strokeStyle = ink; ctx.lineWidth = lw * 2;
    for (const pc of g) if (!pc.noLine) ctx.stroke(pc._p);
  }
  for (const pc of list) {
    ctx.save();
    ctx.filter = 'saturate(0.72) sepia(0.18)';   // 矿物色：偏灰、偏暖
    if (pc.under && pc._cut) { ctx.fillStyle = pc.under; ctx.fill(pc._p); }
    ctx.fillStyle = pc.fill; ctx.fill(pc._cut || pc._p, 'evenodd');
    ctx.filter = 'none';
    ctx.clip(pc._p);
    // 渲染：边缘往里一层层加深
    if (!pc.emissive && !pc.flatColor) {
      ctx.filter = `blur(${s * 0.9}px)`;
      ctx.strokeStyle = pc.shade ?? 'rgba(70,40,30,0.32)'; ctx.lineWidth = s * 2.2; ctx.stroke(pc._p);
      ctx.filter = 'none';
    }
    // 内线：压在别的纸片上的那部分边（袖口、领子、刘海）
    if (pc.inner) { ctx.strokeStyle = ink; ctx.lineWidth = lw * 0.9; ctx.stroke(pc._p); }
    if (pc._cut) { ctx.strokeStyle = ink; ctx.lineWidth = lw * 0.7; for (const h of pc.holes) ctx.stroke(pathOf(h, pc.flatHoles ?? false, 3)); }
    for (const sl of pc.slits || []) { ctx.strokeStyle = sl.inkColor ?? ink; ctx.lineWidth = Math.max(0.8, Math.min(sl.w, lw * 1.1)); ctx.stroke(slitPath(sl.pts)); }
    ctx.restore();
    for (const d of pc.dots || []) {
      ctx.fillStyle = d.fill; ctx.beginPath(); ctx.ellipse(d.c[0], d.c[1], d.r * (d.sx ?? 1), d.r * (d.sy ?? 1), d.rot ?? 0, 0, Math.PI * 2); ctx.fill();
      if (d.line) { ctx.strokeStyle = ink; ctx.lineWidth = lw * 0.6; ctx.stroke(); }
    }
  }
  ctx.restore();
}

// 绢的纹理（工笔画面最后叠一层）
export function silk(ctx, W, H, a = 0.16) {
  const N = 6;
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.globalAlpha = a;
  ctx.strokeStyle = 'rgb(150,130,100)';
  ctx.lineWidth = 1;
  for (let x = 0; x < W; x += N) { ctx.beginPath(); ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); ctx.stroke(); }
  for (let y = 0; y < H; y += N) { ctx.beginPath(); ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); ctx.stroke(); }
  ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(214,196,160,0.35)'; ctx.fillRect(0, 0, W, H); ctx.restore();
}
