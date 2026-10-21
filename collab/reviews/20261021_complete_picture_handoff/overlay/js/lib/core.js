// 基础数学：插值、缓动、关键帧、弹簧、确定性噪声。
// 全片的每一帧都是时间 t 的纯函数，所以这里所有"随机"都来自固定种子的哈希。

export const TAU = Math.PI * 2;
export const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
export const lerp = (a, b, k) => a + (b - a) * k;
export const unlerp = (a, b, v) => clamp((v - a) / (b - a));
export const remap = (v, a, b, c, d) => lerp(c, d, unlerp(a, b, v));
export const smoothstep = (k) => k * k * (3 - 2 * k);

export const EASE = {
  linear: (k) => k,
  in: (k) => k * k,
  out: (k) => 1 - (1 - k) * (1 - k),
  io: (k) => (k < 0.5 ? 2 * k * k : 1 - 2 * (1 - k) * (1 - k)),
  in3: (k) => k * k * k,
  out3: (k) => 1 - (1 - k) ** 3,
  io3: (k) => (k < 0.5 ? 4 * k * k * k : 1 - 4 * (1 - k) ** 3),
  sine: (k) => 0.5 - 0.5 * Math.cos(Math.PI * k),
  // 冲过头再回来（落定的动作）
  outBack: (k) => { const s = 1.6; const u = k - 1; return 1 + (s + 1) * u * u * u + s * u * u; },
  // 先往反方向蓄一下再出发（预备动作）
  inBack: (k) => { const s = 1.4; return (s + 1) * k * k * k - s * k * k; },
  step: (k) => (k < 1 ? 0 : 1),
};

// 关键帧：[[t, 值, 缓动名?], ...]，缓动作用在"到达这个关键帧"的那一段。值可以是数、数组或对象。
function mix(a, b, k) {
  if (typeof a === 'number') return a + (b - a) * k;
  if (Array.isArray(a)) return a.map((v, i) => mix(v, b[i], k));
  if (a && typeof a === 'object') {
    const o = { ...a };
    for (const key in b) o[key] = key in a ? mix(a[key], b[key], k) : b[key];
    return o;
  }
  return k < 1 ? a : b;
}
export function key(t, frames) {
  if (t <= frames[0][0]) return frames[0][1];
  for (let i = 1; i < frames.length; i++) {
    const f = frames[i];
    if (t < f[0]) {
      const p = frames[i - 1];
      const e = typeof f[2] === 'function' ? f[2] : EASE[f[2] || 'io'];
      return mix(p[1], f[1], e((t - p[0]) / (f[0] - p[0])));
    }
  }
  return frames[frames.length - 1][1];
}

// 从 t0 开始由 from 弹向 to 的阻尼振荡
export function spring(t, t0, from, to, freq = 2.5, damp = 0.35) {
  if (t <= t0) return from;
  const w = TAU * freq, d = t - t0;
  return to + (from - to) * Math.exp(-damp * w * d) * Math.cos(w * Math.sqrt(1 - damp * damp) * d);
}
// 在 t0 受到一下冲击后的衰减摆动（0 → amp → 0）
export function kick(t, t0, amp = 1, freq = 3, damp = 0.3) {
  if (t <= t0) return 0;
  const w = TAU * freq, d = t - t0;
  return amp * Math.exp(-damp * w * d) * Math.sin(w * d);
}

// ---- 确定性噪声
export function hash(n) {
  n = (n | 0) ^ 0x27d4eb2d;
  n = Math.imul(n ^ (n >>> 15), 0x2c1b3c6d);
  n = Math.imul(n ^ (n >>> 12), 0x297a2d39);
  n ^= n >>> 15;
  return (n >>> 0) / 4294967296;
}
export const hash2 = (a, b) => hash(Math.imul(a | 0, 73856093) ^ Math.imul(b | 0, 19349663));
export function noise1(x, seed = 0) {
  const i = Math.floor(x), f = x - i;
  return lerp(hash2(i, seed), hash2(i + 1, seed), smoothstep(f)) * 2 - 1;
}
export function fbm1(x, seed = 0) {
  return noise1(x, seed) * 0.6 + noise1(x * 2.13, seed + 11) * 0.28 + noise1(x * 4.37, seed + 23) * 0.12;
}

// 眨眼：给定一串眨眼时刻，返回 0（睁）…1（闭）
export function blink(t, times, dur = 0.14) {
  for (const t0 of times) {
    const k = (t - t0) / dur;
    if (k >= 0 && k <= 1) return Math.sin(Math.PI * k) ** 0.6;
  }
  return 0;
}
