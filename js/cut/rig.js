// 剪纸片人物的骨架：一片片纸用铆钉连起来（和皮影一样），每片纸的长度固定，只能绕铆钉转——所以四肢永远不会被拉长、扭坏。
// 约定：每片的局部坐标里，肢体"自然下垂"时沿 +y 方向；角度为正 = 画面上顺时针转。
import { M } from '../lib/figure.js';

// parts: [{ name, parent, at:[x,y] 在父片局部坐标里的铆点 }]；pose.angles[name] 相对父片的角度
// root: { x, y, s, flip(-1 面朝左), a } → 返回每片纸的世界变换矩阵
export function fk(parts, angles, root) {
  const out = {};
  const R0 = M.chain(M.t(root.x, root.y), M.s(root.s * (root.flip ?? 1), root.s), M.r(root.a ?? 0));
  for (const p of parts) {
    const base = p.parent ? out[p.parent].M : R0;
    const ang = angles[p.name] ?? 0;
    const Mx = M.chain(base, M.t(p.at[0], p.at[1]), M.r(ang));
    out[p.name] = { M: Mx, abs: (p.parent ? out[p.parent].abs : (root.a ?? 0)) + ang };
  }
  return out;
}

// 两节肢体的 IK：给肩（世界坐标）、手的目标、两节长度，算出相对父片的两个角度。
// bend = -1 时肘在"前进方向顺时针一侧"（侧面面朝 +x 时：伸手向前，肘朝下；垂手，肘朝后）。
// 够不着时整条胳膊伸直指向目标——长度永远不变。
export function limbIK(S, W, l1, l2, bend, parentAbs, flip = 1) {
  let dx = (W[0] - S[0]) * flip, dy = W[1] - S[1];
  let d = Math.hypot(dx, dy);
  const dMax = l1 + l2 - 1e-3, dMin = Math.abs(l1 - l2) + 1e-3;
  d = Math.min(Math.max(d, dMin), dMax);
  const a = Math.atan2(dy, dx);
  const A = Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))));
  const ua = a - bend * A;                       // 上臂方向（画面角度）
  const E = [Math.cos(ua) * l1, Math.sin(ua) * l1];
  const fa = Math.atan2(Math.sin(a) * d - E[1], Math.cos(a) * d - E[0]);   // 前臂方向
  // "下垂 = +y" 的约定：方向角 θ 对应的片角 = θ - π/2
  const upperAbs = ua - Math.PI / 2, foreAbs = fa - Math.PI / 2;
  return { upper: upperAbs - parentAbs, fore: foreAbs - upperAbs };
}

// 变换局部点
export const ap = (Mx, pts) => M.apAll(Mx, pts);
export const ap1 = (Mx, p) => M.ap(Mx, p);

// 胶囊形（肢体）：从 (0,0) 往 +y 长 len，宽 w0 → w1，两头圆
export function capsule(len, w0, w1, n = 7) {
  const out = [];
  for (let i = 0; i <= n; i++) { const a = Math.PI + (i / n) * Math.PI; out.push([Math.cos(a) * w0 / 2, Math.sin(a) * w0 / 2]); }
  for (let i = 0; i <= n; i++) { const a = (i / n) * Math.PI; out.push([Math.cos(a) * w1 / 2, len + Math.sin(a) * w1 / 2]); }
  return out;
}
export function circle(cx, cy, r, n = 18) {
  const out = [];
  for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
  return out;
}
// 五瓣小花（梅花）的轮廓，用来镂空
export function plum(cx, cy, r, rot = 0) {
  const out = [];
  for (let i = 0; i < 20; i++) {
    const a = rot + (i / 20) * Math.PI * 2;
    const rr = r * (0.62 + 0.38 * Math.abs(Math.cos((a - rot) * 2.5)));
    out.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
  }
  return out;
}
// 四瓣碎花
export function petal4(cx, cy, r, rot = 0.4) {
  const out = [];
  for (let i = 0; i < 16; i++) {
    const a = rot + (i / 16) * Math.PI * 2;
    const rr = r * (0.45 + 0.55 * Math.abs(Math.cos((a - rot) * 2)));
    out.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
  }
  return out;
}
// 点是否在多边形里（排镂空花纹时用）
export function inside(p, poly) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i], b = poly[j];
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < ((b[0] - a[0]) * (p[1] - a[1])) / (b[1] - a[1]) + a[0]) c = !c;
  }
  return c;
}
// 在一片纸的轮廓里按网格排镂空花纹（离边留出 margin）
export function pattern(poly, step, r, make, margin = 1.2, jitter = 0.5) {
  const xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]);
  const out = [];
  let row = 0;
  for (let y = Math.min(...ys) + step * 0.5; y < Math.max(...ys); y += step * 0.87, row++) {
    for (let x = Math.min(...xs) + (row % 2) * step * 0.5; x < Math.max(...xs); x += step) {
      const ok = [[0, 0], [margin + r, 0], [-margin - r, 0], [0, margin + r], [0, -margin - r]].every(([dx, dy]) => inside([x + dx, y + dy], poly));
      if (ok) out.push(make(x + Math.sin(row * 3.1 + x) * jitter * 0.2, y, r, row));
    }
  }
  return out;
}
