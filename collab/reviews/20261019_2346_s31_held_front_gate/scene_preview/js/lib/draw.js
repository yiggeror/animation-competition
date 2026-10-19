// 手绘感的基本笔触：样条、重采样、抖动（一秒 12 张的"线条呼吸"）、带压感的毛笔线、平涂。
// 坐标是局部单位（通常是厘米），线宽、抖动幅度按屏幕像素给，画的时候用当前变换的缩放换算。
import { hash2, noise1, clamp, TAU } from './core.js';

export const INK = '#3b2c25';
const S = { boil: 0, inkScale: 1, ink: INK };
export const BOIL_FPS = 12;
export function setBoil(t) { S.boil = Math.floor(t * BOIL_FPS + 1e-6); }
export function boil() { return S.boil; }
export function setInkScale(k) { S.inkScale = k; }
export function inkScale() { return S.inkScale; }
export function setInk(c) { S.ink = c || INK; }
export function ink() { return S.ink; }

export function curScale(ctx) {
  const m = ctx.getTransform();
  return Math.sqrt(Math.abs(m.a * m.d - m.b * m.c)) || 1;
}

// ---------------------------------------------------------------- 点列
export function ellipsePts(cx, cy, rx, ry, n = 40, rot = 0) {
  const c = Math.cos(rot), s = Math.sin(rot), out = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU, x = Math.cos(a) * rx, y = Math.sin(a) * ry;
    out.push([cx + x * c - y * s, cy + x * s + y * c]);
  }
  return out;
}
export function arcPts(cx, cy, rx, ry, a0, a1, n = 16) {
  const out = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * (i / n); out.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); }
  return out;
}
export function rrectPts(x, y, w, h, r, n = 4) {
  r = Math.min(r, w / 2, h / 2);
  const out = [];
  const corner = (cx, cy, a0) => { for (let i = 0; i <= n; i++) { const a = a0 + (i / n) * (Math.PI / 2); out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
  corner(x + w - r, y + r, -Math.PI / 2); corner(x + w - r, y + h - r, 0); corner(x + r, y + h - r, Math.PI / 2); corner(x + r, y + r, Math.PI);
  return out;
}

// Catmull-Rom 样条（穿过每个控制点）
export function catmull(pts, closed = true, per = 6) {
  const n = pts.length;
  if (n < 3) return pts.slice();
  const out = [], last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p1 = pts[i], p2 = pts[(i + 1) % n];
    const p0 = closed || i > 0 ? pts[(i - 1 + n) % n] : p1;
    const p3 = closed || i < n - 2 ? pts[(i + 2) % n] : p2;
    for (let j = 0; j < per; j++) {
      const t = j / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((k) => 0.5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
}
// 按弧长等距重采样
export function resample(pts, step, closed = false) {
  const src = closed ? [...pts, pts[0]] : pts;
  const cum = [0];
  for (let i = 1; i < src.length; i++) cum.push(cum[i - 1] + Math.hypot(src[i][0] - src[i - 1][0], src[i][1] - src[i - 1][1]));
  const L = cum[cum.length - 1];
  const n = Math.max(closed ? 3 : 1, Math.round(L / step));
  const out = [];
  let j = 1;
  for (let i = 0; i < (closed ? n : n + 1); i++) {
    const d = (i / n) * L;
    while (j < cum.length - 1 && cum[j] < d) j++;
    const k = (d - cum[j - 1]) / (cum[j] - cum[j - 1] || 1);
    out.push([src[j - 1][0] + (src[j][0] - src[j - 1][0]) * k, src[j - 1][1] + (src[j][1] - src[j - 1][1]) * k]);
  }
  return out;
}
export function polyLength(pts) {
  let L = 0;
  for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return L;
}

// 抖动：沿弧长的低频噪声（不是逐点乱跳），每"一张"（1/12 秒）换一次，像手绘动画里线条的呼吸。
export function wobble(ctx, pts, seed = 1, amp = 0.8) {
  const a = (amp * S.inkScale) / curScale(ctx);
  if (a === 0) return pts;
  const s = curScale(ctx), b = S.boil * 17.31 + seed * 3.7;
  let d = 0;
  return pts.map((p, i) => {
    if (i) d += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]) * s;
    const u = d * 0.045 + b;
    return [p[0] + noise1(u, seed) * a, p[1] + noise1(u + 91.7, seed + 5) * a];
  });
}

// 用中点二次曲线把点连成光滑路径
export function addPath(path, pts, closed = true) {
  const n = pts.length;
  if (n < 2) return path;
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  if (closed) {
    const m0 = mid(pts[n - 1], pts[0]);
    path.moveTo(m0[0], m0[1]);
    for (let i = 0; i < n; i++) { const m = mid(pts[i], pts[(i + 1) % n]); path.quadraticCurveTo(pts[i][0], pts[i][1], m[0], m[1]); }
    path.closePath();
  } else {
    path.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < n - 1; i++) { const m = mid(pts[i], pts[i + 1]); path.quadraticCurveTo(pts[i][0], pts[i][1], m[0], m[1]); }
    path.lineTo(pts[n - 1][0], pts[n - 1][1]);
  }
  return path;
}
export function toPath(pts, closed = true) { return addPath(new Path2D(), pts, closed); }

// ---------------------------------------------------------------- 画
// 平涂 + 描边的形状。o: { fill, stroke, lw(屏幕像素), closed, seed, amp, smooth, per }
export function shape(ctx, pts, o = {}) {
  if (!pts || pts.length < 2) return;
  const closed = o.closed !== false;
  const s = curScale(ctx);
  let p = o.smooth === false ? pts : catmull(pts, closed, o.per ?? 5);
  p = resample(p, (o.seg ?? 6) / s, closed);
  p = wobble(ctx, p, o.seed ?? 1, o.amp ?? 0.7);
  const path = toPath(p, closed);
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  if (o.fill && closed) { ctx.fillStyle = o.fill; ctx.fill(path); }
  if (o.stroke !== false && o.lw !== 0) {
    ctx.strokeStyle = o.stroke || S.ink;
    ctx.lineWidth = ((o.lw ?? 2.6) * S.inkScale) / s;
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.stroke(path);
  }
  ctx.restore();
  return path;
}
export function line(ctx, pts, o = {}) { return shape(ctx, pts, { ...o, closed: false, fill: null }); }

// 毛笔线：宽度随压感曲线变化的填充带。profile: 'taper' 两头尖 | 'in' 渐粗 | 'out' 渐细 | 'flat' | 函数
export const PROFILE = {
  taper: (u) => Math.pow(Math.sin(Math.PI * clamp(0.04 + u * 0.92)), 0.6),
  in: (u) => Math.pow(clamp(u * 1.4), 0.55),
  out: (u) => Math.pow(clamp((1 - u) * 1.4), 0.55),
  flat: () => 1,
  soft: (u) => 0.6 + 0.4 * Math.sin(Math.PI * u),
};
export function brush(ctx, pts, o = {}) {
  if (!pts || pts.length < 2) return;
  const s = curScale(ctx);
  const w = ((o.lw ?? 2.6) * S.inkScale) / s;
  let p = o.smooth === false ? pts : catmull(pts, false, 5);
  p = resample(p, Math.max(0.6, o.seg ?? 3) / s, false);
  p = wobble(ctx, p, o.seed ?? 3, o.amp ?? 0.45);
  const prof = typeof o.profile === 'function' ? o.profile : PROFILE[o.profile || 'taper'];
  const n = p.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = p[Math.max(0, i - 1)], b = p[Math.min(n - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
    const hw = (w / 2) * Math.max(0.1, prof(i / (n - 1)));
    L.push([p[i][0] - dy * hw, p[i][1] + dx * hw]);
    R.push([p[i][0] + dy * hw, p[i][1] - dx * hw]);
  }
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.fillStyle = o.color || S.ink;
  ctx.beginPath();
  ctx.moveTo(L[0][0], L[0][1]);
  for (let i = 1; i < n; i++) ctx.lineTo(L[i][0], L[i][1]);
  for (let i = n - 1; i >= 0; i--) ctx.lineTo(R[i][0], R[i][1]);
  ctx.closePath();
  ctx.fill();
  if (o.caps !== false) {
    for (const [q, u] of [[p[0], 0], [p[n - 1], 1]]) {
      const r = (w / 2) * Math.max(0.1, prof(u));
      ctx.beginPath(); ctx.arc(q[0], q[1], r, 0, TAU); ctx.fill();
    }
  }
  ctx.restore();
}

// 不抖的平涂（光、影、大面积底色）
export function fillPoly(ctx, pts, fill, smooth = false) {
  ctx.fillStyle = fill;
  ctx.beginPath();
  if (smooth) { ctx.fill(toPath(pts, true)); return; }
  pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
  ctx.closePath();
  ctx.fill();
}

// 两节骨的 IK：返回关节位置。bend = +1/-1 决定往哪边弯
export function ik2(root, target, l1, l2, bend = 1) {
  const dx = target[0] - root[0], dy = target[1] - root[1];
  const d = clamp(Math.hypot(dx, dy), Math.abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3);
  const a = Math.atan2(dy, dx);
  const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
  const ja = a - bend * A;
  const end = [root[0] + Math.cos(a) * d, root[1] + Math.sin(a) * d];
  return { joint: [root[0] + Math.cos(ja) * l1, root[1] + Math.sin(ja) * l1], end };
}

export function lerpP(a, b, k) { return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k]; }
export function rotP(p, a, c = [0, 0]) {
  const cs = Math.cos(a), sn = Math.sin(a), x = p[0] - c[0], y = p[1] - c[1];
  return [c[0] + x * cs - y * sn, c[1] + x * sn + y * cs];
}
export function addP(a, b, k = 1) { return [a[0] + b[0] * k, a[1] + b[1] * k]; }
