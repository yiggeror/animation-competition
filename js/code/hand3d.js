// 可以摆姿势的手（2.5D）：手掌、四指、拇指按真实比例放在一个三维的手坐标系里，由关节角度算出每节的位置，再正交投影到画面。
// 画法和手机特写一致：每根手指是一条连贯的平滑轮廓（不出现关节接缝），手掌和前臂合成一个外轮廓，深棕描边 + 平涂 + 背光一侧压暗；
// 指甲只在手背朝向镜头时画。
// 手坐标系（右手；左手把 x 取反）：原点在手腕中心，+y 指向手指，+x 指向拇指一侧，+z 是手背朝外。单位厘米。
// 世界坐标：X 向右，Y 向上，Z 朝向镜头（越大越近）。
const V = {
  add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]],
  sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]],
  mul: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2],
  cross: (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]],
  norm: (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; },
};
// 绕任意轴转（罗德里格斯）
function rot(v, axis, ang) {
  const k = V.norm(axis), c = Math.cos(ang), s = Math.sin(ang);
  return V.add(V.add(V.mul(v, c), V.mul(V.cross(k, v), s)), V.mul(k, V.dot(k, v) * (1 - c)));
}
// 欧拉角 → 3×3 矩阵（先绕 Z 转 roll，再绕 X 转 pitch，再绕 Y 转 yaw）；返回把手坐标转到世界坐标的函数
export function orient(yaw = 0, pitch = 0, roll = 0) {
  return (v) => rot(rot(rot(v, [0, 0, 1], roll), [1, 0, 0], pitch), [0, 1, 0], yaw);
}

// 手的尺寸（成年女性；小孩乘 0.78 左右）
const FINGERS = {
  index: { mcp: [2.7, 8.7], len: [4.2, 2.4, 1.9], w: [1.85, 1.6, 1.42] },
  middle: { mcp: [0.85, 9.0], len: [4.7, 2.8, 2.0], w: [1.9, 1.65, 1.45] },
  ring: { mcp: [-1.0, 8.6], len: [4.4, 2.7, 2.0], w: [1.75, 1.55, 1.38] },
  little: { mcp: [-2.75, 7.7], len: [3.4, 2.0, 1.75], w: [1.55, 1.38, 1.25] },
};
const THUMB = { cmc: [2.4, 2.2, -0.6], len: [4.2, 3.1, 2.5], w: [2.6, 2.1, 1.75] };

// 姿势：f.<名>: [掌指, 近节, 远节] 弯曲角（弧度，往手心弯为正），splay（四指张开）；
// thumb: { tip: 拇指尖的目标位置（手坐标）, pole: 指间关节往哪边鼓, adduct: 掌骨往掌面收的程度 }
export const POSES = {
  flat: { f: { index: [0.05, 0.05, 0.03], middle: [0.05, 0.05, 0.03], ring: [0.06, 0.06, 0.04], little: [0.08, 0.08, 0.05] }, splay: 0.04, thumb: { tip: [7.2, 7.0, -0.6], pole: [0.3, 0.2, 1] } },
  relaxed: { f: { index: [0.25, 0.35, 0.2], middle: [0.3, 0.45, 0.25], ring: [0.35, 0.55, 0.3], little: [0.4, 0.6, 0.35] }, splay: 0.06, thumb: { tip: [5.6, 8.0, -2.4], pole: [0.6, 0, 0.8] } },
  fist: { f: { index: [1.45, 1.7, 0.9], middle: [1.5, 1.75, 0.9], ring: [1.5, 1.75, 0.9], little: [1.45, 1.7, 0.85] }, splay: 0, thumb: { tip: [-0.2, 7.6, -3.6], pole: [0.5, 0.3, 0.8], adduct: 1 } },
  grip: { f: { index: [1.0, 1.3, 0.7], middle: [1.1, 1.4, 0.75], ring: [1.15, 1.45, 0.8], little: [1.2, 1.5, 0.8] }, splay: 0, thumb: { tip: [0.8, 9.2, -4.2], pole: [0.6, 0.2, 0.8], adduct: 0.6 } },
  pinch: { f: { index: [0.7, 0.9, 0.4], middle: [0.9, 1.2, 0.6], ring: [1.1, 1.4, 0.7], little: [1.2, 1.5, 0.75] }, splay: 0.02, thumb: { tip: [2.6, 13.4, -3.0], pole: [0.7, 0, 0.7] } },
  point: { f: { index: [0.0, 0.05, 0.02], middle: [1.45, 1.7, 0.9], ring: [1.5, 1.75, 0.9], little: [1.45, 1.7, 0.85] }, splay: 0, thumb: { tip: [-0.2, 7.6, -3.6], pole: [0.5, 0.3, 0.8], adduct: 1 } },
  // 手影小狗（右手）：四指并拢伸直是嘴筒子，小指往下放是下巴，拇指竖起来是耳朵
  dog: { f: { index: [0.05, 0.05, 0.02], middle: [0.05, 0.05, 0.02], ring: [0.15, 0.1, 0.05], little: [0.9, 0.2, 0.1] }, splay: -0.02, thumb: { tip: [3.6, 10.6, 3.2], pole: [1, 0, 0] } },
};
export function mixPose(A, B, k) {
  const L = (a, b) => a + (b - a) * k;
  const f = {};
  for (const n of Object.keys(A.f)) f[n] = A.f[n].map((v, i) => L(v, B.f[n][i]));
  const tA = A.thumb, tB = B.thumb;
  return { f, splay: L(A.splay, B.splay), thumb: { tip: tA.tip.map((v, i) => L(v, tB.tip[i])), pole: (tA.pole || [0.6, 0, 0.8]).map((v, i) => L(v, (tB.pole || [0.6, 0, 0.8])[i])), adduct: L(tA.adduct ?? 0, tB.adduct ?? 0) } };
}

// 正向运动学：返回各手指的关节点（手坐标）和"手背方向"
export function solve(pose, scale = 1) {
  const S = (p) => p.map((v) => v * scale);
  const out = {};
  const names = ['index', 'middle', 'ring', 'little'];
  names.forEach((n, i) => {
    const F = FINGERS[n], fl = pose.f[n];
    const spread = pose.splay * (1.5 - i);           // 食指往拇指那边、小指往外
    let dir = rot([0, 1, 0], [0, 0, 1], spread), axis = rot([1, 0, 0], [0, 0, 1], spread);
    let p = [F.mcp[0], F.mcp[1], 0];
    const pts = [[p[0], p[1] - 1.6, 0], p];             // 往手掌里多一个点，手指"长"在手掌里
    let up = [0, 0, 1];
    for (let k = 0; k < 3; k++) {
      dir = rot(dir, axis, -fl[k]); up = rot(up, axis, -fl[k]);
      p = V.add(p, V.mul(dir, F.len[k])); pts.push(p);
    }
    out[n] = { pts: pts.map(S), w: [F.w[0] * 1.08, F.w[0], F.w[1], F.w[2], F.w[2] * 0.95].map((v) => v * scale * 1.08), up, dir };
  });
  // 拇指：给指尖的目标位置（手坐标，厘米）。掌骨从腕掌关节指向目标的方向（按 adduct 往掌面收一点），
  // 后两节用两节反向运动学够到目标，指节往手背、拇指外侧鼓（弯向手心）
  const T = pose.thumb;
  const cmc = THUMB.cmc;
  const tgt = T.tip;
  let toT = V.sub(tgt, cmc), dT = Math.hypot(...toT);
  let mdir = V.norm(V.add(V.norm(toT), [0.25, -0.1, 0.35 * (T.adduct ?? 0)]));
  const mcp = V.add(cmc, V.mul(mdir, THUMB.len[0]));
  const l1 = THUMB.len[1], l2 = THUMB.len[2];
  let v = V.sub(tgt, mcp), d = Math.min(Math.hypot(...v), l1 + l2 - 1e-3);
  const vn = V.norm(v);
  const pole = V.norm(T.pole || [0.6, 0.0, 0.8]);                         // 指间关节往哪边鼓
  const side = V.norm(V.sub(pole, V.mul(vn, V.dot(pole, vn))));
  const c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), sn = Math.sqrt(Math.max(0, 1 - c * c));
  const ip = V.add(mcp, V.add(V.mul(vn, l1 * c), V.mul(side, l1 * sn)));
  const tip = V.add(ip, V.mul(V.norm(V.sub(V.add(mcp, V.mul(vn, d)), ip)), l2));
  const tp = [V.add(cmc, [-1.6, -1.2, 0.3]), cmc, mcp, ip, tip];
  const dirT = V.norm(V.sub(tip, ip));
  const up = V.norm(V.sub(side, V.mul(dirT, V.dot(side, dirT))));         // 指甲朝鼓的那一侧
  out.thumb = { pts: tp.map(S), w: [THUMB.w[0] * 1.45, THUMB.w[0], THUMB.w[1], THUMB.w[2], THUMB.w[2] * 0.95].map((v) => v * scale * 1.05), up, dir: dirT };
  return out;
}

// ---------------------------------------------------------------- 画
const LINE = '#4a2e1f';
const lerp = (a, b, k) => a + (b - a) * k;
// 过一串二维点的平滑曲线（Catmull-Rom）+ 宽度，返回封闭轮廓（指尖圆头）和不封口的描边轮廓
function tube(pts, widths, openStart = true) {
  const n = pts.length - 1, C = (i) => pts[Math.max(0, Math.min(n, i))];
  const P = (u) => {
    const f = Math.min(n - 1e-6, Math.max(0, u * n)), i = Math.floor(f), s = f - i;
    const p0 = C(i - 1), p1 = C(i), p2 = C(i + 1), p3 = C(i + 2);
    const q = (k) => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * s + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * s * s + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * s * s * s);
    return [q(0), q(1)];
  };
  const Wd = (u) => { const f = Math.min(n - 1e-6, Math.max(0, u * n)), i = Math.floor(f); return lerp(widths[i], widths[i + 1], f - i); };
  const N = 36, L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, p = P(u), q = P(Math.min(1, u + 0.004)), r = P(Math.max(0, u - 0.004));
    const tx = q[0] - r[0], ty = q[1] - r[1], tl = Math.hypot(tx, ty) || 1, w = Wd(u) / 2;
    L.push([p[0] - ty / tl * w, p[1] + tx / tl * w]); R.push([p[0] + ty / tl * w, p[1] - tx / tl * w]);
  }
  const end = P(1), pre = P(0.985), dir = Math.atan2(end[1] - pre[1], end[0] - pre[0]), we = widths[n] / 2;
  const build = (close) => {
    const path = new Path2D(); path.moveTo(...L[0]);
    for (const p of L) path.lineTo(...p);
    path.arc(end[0], end[1], we, dir + Math.PI / 2, dir - Math.PI / 2, true);
    for (let i = R.length - 1; i >= 0; i--) path.lineTo(...R[i]);
    if (close || !openStart) path.closePath();
    return path;
  };
  return { path: build(true), outline: build(false), P, Wd, dir, end, L, R };
}
function hull(points) {
  const p = points.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
function smoothClosed(pts) {
  const path = new Path2D(), n = pts.length;
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  path.moveTo(...mid(pts[n - 1], pts[0]));
  for (let i = 0; i < n; i++) { const m = mid(pts[i], pts[(i + 1) % n]); path.quadraticCurveTo(pts[i][0], pts[i][1], m[0], m[1]); }
  path.closePath(); return path;
}

// 颜色按光照压暗（sRGB → 线性 → 乘 → sRGB）
const hex2 = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
export function shade(hex, k) { return `rgb(${hex2(hex).map((v, i) => Math.round(255 * Math.pow(Math.min(1, Math.pow(v / 255, 2.2) * k[i]), 1 / 2.2))).join(',')})`; }

// 画一只手。opt = { side: 1 右手 / -1 左手, pose, scale（小孩 0.78）, R（orient() 的结果）, at:[x,y]（手腕在画面上的位置，像素）,
//   px（每厘米多少像素）, skin, light:[r,g,b], shadeK（暗面系数）, rim（亮边颜色 rgba 字符串，可选）, forearm（前臂长，厘米）, sleeve（袖口颜色，可选）, sleeveAt（袖口离手腕多远） }
export function drawHand(ctx, opt) {
  const side = opt.side ?? 1, sc = opt.scale ?? 1, R = opt.R || orient(), px = opt.px ?? 20;
  const L = opt.light || [1, 1, 1], skin = opt.skin || '#f3c4a0', shadeCol = opt.skinShade || '#d99a78';
  const J = solve(opt.pose || POSES.relaxed, sc);
  const W = (p) => R([p[0] * side, p[1], p[2]]);                              // 手坐标 → 世界（左手镜像 x）
  const S = (w) => [opt.at[0] + w[0] * px, opt.at[1] - w[1] * px, w[2]];     // 世界 → 画面（带深度）
  const P2 = (p) => { const s = S(W(p)); return [s[0], s[1]]; };
  const depth = (p) => W(p)[2];
  // 手掌：手背、手心两面的轮廓点 + 指根一排 + 手腕，投影后取凸包
  const palmPts = [];
  for (const z of [-1.3 * sc, 0.9 * sc]) {
    for (const [x, y] of [[2.7, 0.2], [3.3, 2.5], [3.5, 5.5], [3.3, 8.0], [2.0, 8.7], [0, 8.9], [-2.0, 8.5], [-3.3, 7.3], [-3.6, 5], [-3.1, 2], [-2.4, 0.1]]) palmPts.push(P2([x * sc, y * sc, z]));
  }
  // 大鱼际（拇指根的肉）
  for (const [x, y, z] of [[3.6, 2.4, -1.8], [3.2, 4.4, -1.9], [2.2, 1.0, -1.7]]) palmPts.push(P2([x * sc, y * sc, z * sc]));
  const palmPath = smoothClosed(hull(palmPts));
  const palmN = V.norm(W([0, 0, 1]));                                          // 手背朝向（世界）
  // 前臂：从手腕往回
  const fa = opt.forearm ?? 22;
  const arm = tube([P2([0, 1.0 * sc, -0.2]), P2([0, -fa * 0.5, -0.2]), P2([0, -fa, -0.2])], [5.6 * sc * px, 6.4 * sc * px, 7.0 * sc * px]);
  // 手指（按深度排序：比手掌远的先画）
  const parts = [];
  for (const n of ['index', 'middle', 'ring', 'little', 'thumb']) {
    const f = J[n];
    const pts2 = f.pts.map(P2), ws = f.w.map((v) => v * px);
    const dAvg = f.pts.slice(2).reduce((a, p) => a + depth(p), 0) / (f.pts.length - 2);
    parts.push({ n, t: tube(pts2, ws), depth: dAvg, f });
  }
  const palmDepth = depth([0, 5 * sc, 0]);
  const tipOf = (n) => P2(J[n].pts[J[n].pts.length - 1]);
  const info = { thumbTip: tipOf('thumb'), indexTip: tipOf('index'), middleTip: tipOf('middle'), palm: P2([0, 5 * sc, -1.5 * sc]), grip: P2([0.4 * sc, 6.5 * sc, -2.6 * sc]), toScreen: P2, world: W };
  if (opt.dry) return info;                              // 只算位置不画（给道具对齐用）
  const fill = shade(skin, L), fillSh = shade(shadeCol, L.map((v) => v * (opt.shadeK ?? 0.85)));
  const lw = opt.lineW ?? Math.max(2, px * 0.14);
  ctx.save(); ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  // 先画：前臂 + 手掌的合并外轮廓（粗描边再填色，内部的线就没了）；袖口盖在前臂上
  const drawBody = () => {
    ctx.strokeStyle = LINE; ctx.lineWidth = lw * 2; ctx.stroke(arm.path); ctx.stroke(palmPath);
    ctx.fillStyle = fill; ctx.fill(arm.path); ctx.fill(palmPath);
    // 暗面：手掌靠小指一侧、前臂下侧
    ctx.save(); ctx.clip(palmPath);
    const a = P2([-3.6 * sc, 5 * sc, 0]), b = P2([-3.6 * sc, 0, 0]);
    ctx.strokeStyle = fillSh; ctx.globalAlpha = 0.55; ctx.lineWidth = 1.8 * sc * px; ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke();
    ctx.restore();
    if (opt.sleeve) {
      const s0 = opt.sleeveAt ?? 6;
      const sl = tube([P2([0, -s0 * sc, -0.2]), P2([0, -fa, -0.2])], [6.9 * sc * px, 7.6 * sc * px]);
      ctx.strokeStyle = LINE; ctx.lineWidth = lw; ctx.fillStyle = opt.sleeve; ctx.fill(sl.path); ctx.stroke(sl.path);
    }
  };
  const drawFinger = (pt) => {
    const t = pt.t;
    ctx.fillStyle = fill; ctx.fill(t.path);
    // 暗面：沿手指一侧（离光远的那边）压一条
    ctx.save(); ctx.clip(t.path); ctx.strokeStyle = fillSh; ctx.globalAlpha = opt.shadeA ?? 0.5; ctx.lineWidth = t.Wd(0.5) * 0.55; ctx.beginPath();
    for (let i = 0; i <= 24; i++) { const u = i / 24, p = t.P(u), q = t.P(Math.min(1, u + 0.01)), an = Math.atan2(q[1] - p[1], q[0] - p[0]) + Math.PI / 2, o = t.Wd(u) * 0.42; const pp = [p[0] + Math.cos(an) * o, p[1] + Math.sin(an) * o]; i ? ctx.lineTo(...pp) : ctx.moveTo(...pp); }
    ctx.stroke(); ctx.restore();
    if (opt.rim) { ctx.save(); ctx.clip(t.path); ctx.strokeStyle = opt.rim; ctx.lineWidth = t.Wd(0.5) * 0.35; ctx.filter = 'blur(2px)'; ctx.stroke(t.outline); ctx.restore(); }
    ctx.strokeStyle = LINE; ctx.lineWidth = lw; ctx.stroke(t.outline);
    // 指甲：远节的手背朝镜头时才看得见（越朝镜头越完整）
    const f = pt.f, n = f.pts.length;
    const tip = f.pts[n - 1], dip = f.pts[n - 2];
    const upW = V.norm(R([f.up[0] * side, f.up[1], f.up[2]]));
    const vis = upW[2];
    if (vis > 0.15) {
      const c = P2(V.add(V.mul(tip, 0.62), V.mul(dip, 0.38)).map((v, i) => v + f.up[i] * 0.0));
      const a2 = P2(tip), b2 = P2(dip);
      const ang = Math.atan2(a2[1] - b2[1], a2[0] - b2[0]), segL = Math.hypot(a2[0] - b2[0], a2[1] - b2[1]);
      ctx.save(); ctx.translate(...c); ctx.rotate(ang);
      const nw = t.Wd(0.95) * 0.62 * Math.min(1, vis * 1.3), nl = Math.max(segL * 0.55, t.Wd(0.95) * 0.35);
      ctx.fillStyle = shade('#f8dccf', L); ctx.beginPath(); ctx.ellipse(nl * 0.1, 0, nl * 0.5, nw / 2, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = LINE; ctx.lineWidth = lw * 0.55; ctx.stroke();
      ctx.restore();
    }
    // 近节和中节之间的褶（手背朝镜头时）
    if (vis > 0.3 && pt.n !== 'thumb') {
      const pj = P2(f.pts[3]), pj2 = P2(f.pts[4]), an = Math.atan2(pj2[1] - pj[1], pj2[0] - pj[0]) + Math.PI / 2, w = t.Wd(0.55) * 0.28;
      ctx.strokeStyle = LINE; ctx.globalAlpha = 0.5; ctx.lineWidth = lw * 0.5; ctx.beginPath();
      ctx.moveTo(pj[0] + Math.cos(an) * w, pj[1] + Math.sin(an) * w); ctx.lineTo(pj[0] - Math.cos(an) * w, pj[1] - Math.sin(an) * w); ctx.stroke(); ctx.globalAlpha = 1;
    }
  };
  const web = (pt) => {                                  // 手指骨架 + 手掌里的点围成的多边形，填肉色（握拳时不留空洞）
    const pts = pt.f.pts.map(P2); if (pts.length < 4) return;
    ctx.fillStyle = fill; ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(...p) : ctx.moveTo(...p)));
    const base = P2([pt.f.pts[1][0] * 0.6, pt.f.pts[1][1] * 0.75, -1.2 * sc]); ctx.lineTo(...base); ctx.closePath(); ctx.fill();
  };
  const back = parts.filter((p) => p.depth < palmDepth - 0.3).sort((a, b) => a.depth - b.depth);
  const front = parts.filter((p) => p.depth >= palmDepth - 0.3).sort((a, b) => a.depth - b.depth);
  back.forEach(drawFinger);
  drawBody();
  front.forEach((p) => { if (p.n !== 'thumb') web(p); });
  front.forEach(drawFinger);
  ctx.restore();
  return info;
}
