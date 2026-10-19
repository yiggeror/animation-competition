// 一笔画成的人物：人物由一组柔软的闭合形状（躯干、袖子、手、头、头发……）组成，画法像动画师一口气画下来——
//   1. 先把所有形状描一遍双倍宽的墨线；
//   2. 再按前后顺序平涂上色，后画的颜色盖住前面形状的内侧墨线。
// 结果是整个人只有一条连续的外轮廓，关节处没有拼接缝。动画师会画的内线（袖子压在胸前、刘海压在额头）
// 用 inner 选项补：只在"压住了前面已画的形状"的地方描线。
// 光：rim() 在面向光源的一侧加一道亮边；shadeFrom() 在背光一侧压一层暗色（都按真实光源方向算）。
import { catmull, resample, wobble, toPath, brush, curScale, ink, inkScale } from './draw.js';

const POOL = [];
function scratch(i, w, h) {
  let c = POOL[i];
  if (!c) c = POOL[i] = new OffscreenCanvas(w, h);
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  const x = c.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0);
  x.globalCompositeOperation = 'source-over';
  x.globalAlpha = 1;
  x.filter = 'none';
  x.clearRect(0, 0, w, h);
  return [c, x];
}

export class Figure {
  // o: { lw: 外轮廓线宽（屏幕像素）, amp: 抖动, seed, ink }
  constructor(ctx, o = {}) {
    this.ctx = ctx;
    this.lw = o.lw ?? 3;
    this.amp = o.amp ?? 0.7;
    this.seed = o.seed ?? 1;
    this.ink = o.ink || ink();
    this.parts = [];
    this.ops = [];
    this.lights = [];
    this.n = 0;
    this.defer = !!o.defer;
  }
  // 闭合形状。o: { fill, z, smooth(默认 true), per, outline(默认 true), lwMul, inner, innerLw, innerColor, seed, alpha }
  part(name, pts, o = {}) {
    if (!pts || pts.length < 3) return null;
    const p = { kind: 'part', name, pts, o, z: o.z ?? 0, i: this.n++ };
    this.parts.push(p); this.ops.push(p);
    return p;
  }
  // 细节线（衣褶、五官……），可裁到某些形状里。o: { z, clip, lw, color, profile, closed, fill, smooth, alpha }
  detail(pts, o = {}) { if (pts && pts.length >= 2) this.ops.push({ kind: 'detail', pts, o, z: o.z ?? 100, i: this.n++ }); }
  // 任意绘制（暗部、花纹），裁到 clip 指定的形状里
  paint(fn, o = {}) { this.ops.push({ kind: 'paint', fn, o, z: o.z ?? 100, i: this.n++ }); }
  // 亮边：dir = 指向光源的屏幕方向（像素），w = 亮边宽（像素）
  rim(o) { this.lights.push({ type: 'rim', ...o }); }
  // 背光面：在远离光源的一侧压暗
  shadeFrom(o) { this.lights.push({ type: 'shade', ...o }); }

  _prep() {
    const ctx = this.ctx, s = curScale(ctx);
    for (const p of this.parts) {
      let q = p.pts;
      if (p.o.smooth !== false) q = catmull(q, true, p.o.per ?? 5);
      q = resample(q, (p.o.seg ?? 5) / s, true);
      q = wobble(ctx, q, (p.o.seed ?? p.i * 7 + 3) + this.seed * 101, p.o.amp ?? this.amp);
      p.path = toPath(q, true);
    }
    this.ops.sort((a, b) => a.z - b.z || a.i - b.i);
  }
  _union(names, before = null) {
    const path = new Path2D();
    let any = false;
    for (const p of this.parts) {
      if (before && !before.has(p)) continue;
      if (names && names !== 'all' && !names.includes(p.name)) continue;
      path.addPath(p.path); any = true;
    }
    return any ? path : null;
  }
  draw() {
    if (!this.parts.length) return;
    const ctx = this.ctx;
    this._prep();
    const s = curScale(ctx);
    const lw = (this.lw * inkScale()) / s;
    ctx.save();
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    // 1) 整体外轮廓：双倍宽墨线垫在最底下
    ctx.strokeStyle = this.ink;
    for (const p of this.parts) {
      if (p.o.outline === false) continue;
      ctx.lineWidth = lw * 2 * (p.o.lwMul ?? 1);
      ctx.stroke(p.path);
    }
    // 2) 按前后顺序上色、补内线、画细节
    const drawn = new Set();
    for (const op of this.ops) {
      if (op.kind === 'part') {
        const o = op.o;
        if (o.fill) {
          ctx.save();
          if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
          ctx.fillStyle = o.fill; ctx.fill(op.path);
          ctx.restore();
        }
        if (o.inner) {
          const under = this._union(o.inner === true ? 'all' : o.inner, drawn);
          if (under) {
            ctx.save(); ctx.clip(under);
            ctx.strokeStyle = o.innerColor || this.ink;
            ctx.lineWidth = lw * (o.innerLw ?? 0.85);
            ctx.stroke(op.path);
            ctx.restore();
          }
        }
        drawn.add(op);
      } else {
        const o = op.o;
        let clip = null;
        if (o.clip) { clip = this._union(o.clip); if (!clip) continue; }
        ctx.save();
        if (clip) ctx.clip(clip);
        if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
        if (op.kind === 'paint') op.fn(ctx);
        else if (o.fill) {
          let q = o.smooth === false ? op.pts : catmull(op.pts, true, 5);
          q = wobble(ctx, resample(q, 5 / s, true), o.seed ?? op.i, (o.amp ?? this.amp) * 0.7);
          const path = toPath(q, true);
          ctx.fillStyle = o.fill; ctx.fill(path);
          if (o.lw !== 0) { ctx.strokeStyle = o.color || this.ink; ctx.lineWidth = ((o.lw ?? this.lw * 0.7) * inkScale()) / s; ctx.stroke(path); }
        } else {
          brush(ctx, op.pts, { lw: o.lw ?? this.lw * 0.8, color: o.color || this.ink, profile: o.profile || 'taper', seed: o.seed ?? op.i + this.seed, smooth: o.smooth, amp: o.amp ?? 0.35 });
        }
        ctx.restore();
      }
    }
    ctx.restore();
    this.m = ctx.getTransform();
    if (!this.defer) this.drawLights();
  }
  // 亮边、背光面可以推迟到光照图叠底之后再画（不然亮边也会被压暗）：new Figure(ctx, { defer: true })，最后调 drawLights()
  drawLights() { for (const L of this.lights) this._light(L); }
  // 亮边 / 背光面：把轮廓整体平移，相减得到一侧的月牙形，再上色合成
  _light(L) {
    const ctx = this.ctx, W = ctx.canvas.width, H = ctx.canvas.height;
    const m = this.m || ctx.getTransform();
    const parts = this.parts.filter((p) => (!L.only || L.only.includes(p.name)) && !(L.except && L.except.includes(p.name)));
    if (!parts.length) return;
    const sil = new Path2D();
    for (const p of parts) sil.addPath(p.path);
    const k = W / 1920;
    const [acc, ac] = scratch(0, W, H);
    const dirs = L.dirs || [L.dir];
    for (const d0 of dirs) {
      const len = Math.hypot(d0[0], d0[1]) || 1;
      const w = (L.w ?? 6) * k;
      // rim：轮廓减去"往背光方向平移后的轮廓" → 面向光源一侧的边；shade：反过来
      const sgn = L.type === 'rim' ? -1 : 1;
      const dx = (d0[0] / len) * w * sgn, dy = (d0[1] / len) * w * sgn;
      const [tmp, tc] = scratch(1, W, H);
      tc.setTransform(m); tc.fillStyle = '#fff'; tc.fill(sil);
      tc.globalCompositeOperation = 'destination-out';
      tc.setTransform(new DOMMatrix([1, 0, 0, 1, dx, dy]).multiply(m));
      tc.fill(sil);
      ac.globalCompositeOperation = 'lighter';
      ac.drawImage(tmp, 0, 0);
    }
    ac.globalCompositeOperation = 'source-in';
    ac.fillStyle = `rgb(${L.rgb})`;
    ac.fillRect(0, 0, W, H);
    ctx.save();
    ctx.setTransform(m); ctx.clip(sil);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = L.mode || (L.type === 'rim' ? 'screen' : 'multiply');
    ctx.globalAlpha = L.a ?? (L.type === 'rim' ? 0.8 : 0.5);
    if (L.blur) ctx.filter = `blur(${L.blur * k}px)`;
    ctx.drawImage(acc, 0, 0);
    ctx.restore();
  }
}

// ---------------------------------------------------------------- 造型工具
// 沿一条脊线的管子（四肢、袖子、马尾），宽度沿 u∈[0,1] 变化；返回闭合轮廓和两条边
export function tube(spine, widths, o = {}) {
  const sp = resample(o.smooth === false ? spine : catmull(spine, false, 8), o.step ?? 0.8, false);
  const n = sp.length, L = [], R = [];
  const wAt = typeof widths === 'function' ? widths : (u) => profile(widths, u);
  for (let i = 0; i < n; i++) {
    const a = sp[Math.max(0, i - 1)], b = sp[Math.min(n - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
    const w = wAt(i / (n - 1));
    const wl = Array.isArray(w) ? w[0] : w, wr = Array.isArray(w) ? w[1] : w;
    L.push([sp[i][0] - dy * wl, sp[i][1] + dx * wl]);
    R.push([sp[i][0] + dy * wr, sp[i][1] - dx * wr]);
  }
  const cap = (c, from, to, dirFrom, k) => {
    const out = [];
    const r = Math.hypot(from[0] - to[0], from[1] - to[1]) / 2;
    for (let i = 1; i < 8; i++) {
      const t = i / 8, b = Math.sin(Math.PI * t) * r * k;
      out.push([from[0] + (to[0] - from[0]) * t + dirFrom[0] * b, from[1] + (to[1] - from[1]) * t + dirFrom[1] * b]);
    }
    return out;
  };
  const dirAt = (i, j) => { const dx = sp[i][0] - sp[j][0], dy = sp[i][1] - sp[j][1], d = Math.hypot(dx, dy) || 1; return [dx / d, dy / d]; };
  const outl = [];
  if (o.capStart !== 'flat') outl.push(...cap(sp[0], R[0], L[0], dirAt(0, 1), o.capStartK ?? 1));
  outl.push(...L);
  if (o.capEnd !== 'flat') outl.push(...cap(sp[n - 1], L[n - 1], R[n - 1], dirAt(n - 1, n - 2), o.capEndK ?? 1));
  for (let i = n - 1; i >= 0; i--) outl.push(R[i]);
  return { outline: outl, left: L, right: R, spine: sp };
}
export function profile(w, u) {
  if (u <= w[0][0]) return w[0][1];
  for (let i = 1; i < w.length; i++) {
    if (u <= w[i][0]) {
      const k = (u - w[i - 1][0]) / (w[i][0] - w[i - 1][0]);
      const e = k * k * (3 - 2 * k);
      const a = w[i - 1][1], b = w[i][1];
      return Array.isArray(a) ? [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e] : a + (b - a) * e;
    }
  }
  return w[w.length - 1][1];
}
// 2D 仿射变换（和 canvas 一样：[a,b,c,d,e,f]）
export const M = {
  I: [1, 0, 0, 1, 0, 0],
  mul: (A, B) => [A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3], A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5]],
  t: (x, y) => [1, 0, 0, 1, x, y],
  r: (a) => [Math.cos(a), Math.sin(a), -Math.sin(a), Math.cos(a), 0, 0],
  s: (x, y = x) => [x, 0, 0, y, 0, 0],
  chain: (...ms) => ms.reduce((A, B) => M.mul(A, B), M.I),
  ap: (A, p) => [A[0] * p[0] + A[2] * p[1] + A[4], A[1] * p[0] + A[3] * p[1] + A[5]],
  apAll: (A, pts) => pts.map((p) => M.ap(A, p)),
};
