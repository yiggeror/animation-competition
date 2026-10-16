// 小满（9 岁，约 1.32 米）：坐在小板凳上，身子前倾、手肘撑在膝盖上、两只拳头托着下巴，抬头看床单上的鹤。侧面（脸朝右）。
// 局部坐标：厘米，x 朝她面朝的方向，y 朝上，原点在板凳面的中心；地面 y = -22。
// 比例按 9 岁女孩的人体尺寸（头略放大一点）：上臂 20、前臂 16.5、拳头 7、大腿 30、小腿 28、脚 18 厘米。
// 姿势是解出来的：手肘落在膝盖上 → 上臂长度定出身体前倾多少；拳头顶着下巴、脖子保持 6～7 厘米 → 定出前臂角度和头的位置。
// 同一块皮肉（上臂-前臂-拳头、大腿-小腿-脚）是一个"组"，法线合起来算，手肘、手腕、膝盖、脚踝不出接缝。
// 颜色是固有色，明暗全部交给场景里的光去算（cards.js 由轮廓算法线）。
import { catmull } from '../lib/draw.js';
import { tube } from '../lib/figure.js';
import { bboxOf } from './cards.js';

const C = {
  skin: '#f0c4a2', skinDeep: '#e2a988', blush: 'rgba(236,112,100,0.55)', lip: '#d9786c',
  hair: '#2a1c19', hairHi: '#4a3128', tie: '#d42a2f', tieHi: '#f05a50',
  dress: '#f4b336', dot: '#fbe6a2', collar: '#f6f0e2', sandal: '#c82f2b', sole: '#6e1d1b',
  stool: '#8a5a36', stoolDark: '#5e3b22', eyeW: '#f3ece6', iris: '#3a2418', pupil: '#120a08',
};

const rot = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
function ik(root, target, l1, l2, bend) {
  const d = Math.min(Math.hypot(target[0] - root[0], target[1] - root[1]), l1 + l2 - 1e-3);
  const a = Math.atan2(target[1] - root[1], target[0] - root[0]);
  const c = Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))));
  const j = [root[0] + Math.cos(a + bend * c) * l1, root[1] + Math.sin(a + bend * c) * l1];
  return { joint: j, end: [root[0] + Math.cos(a) * d, root[1] + Math.sin(a) * d] };
}
function ellipse(cx, cy, rx, ry, rotA = 0, n = 28) {
  const out = [];
  for (let i = 0; i < n; i++) { const t = (i / n) * Math.PI * 2; const p = rot([Math.cos(t) * rx, Math.sin(t) * ry], rotA); out.push([cx + p[0], cy + p[1]]); }
  return out;
}


// 一笔画出整条四肢的外轮廓（A 根 → B 关节 → C 末端），像画师画人体那样：
//   弯曲的外侧绕着关节画一段圆弧（膝盖骨、肘尖），内侧两条轮廓线在关节处相交、挤出一道褶（膝窝、肘窝）；
//   末端接上脚或手腕。这样整条腿/胳膊是一块连续的肉，不会像拼起来的管子那样在关节处鼓出"球关节"。
// w1p/w1m：第一段在 +n / −n 两侧的半宽 [[t, w], ...]；w2p/w2m：第二段。extremity(pEnd, mEnd) 返回从 + 侧末端绕到 − 侧末端的点。
function limbOutline(A, B, C, w1p, w1m, w2p, w2m, extremity = null, step = 0.6) {
  const sub2 = (a, b) => [a[0] - b[0], a[1] - b[1]], add2 = (a, b) => [a[0] + b[0], a[1] + b[1]], mul2 = (a, k) => [a[0] * k, a[1] * k];
  const prof = (w, t) => { if (t <= w[0][0]) return w[0][1]; for (let i = 1; i < w.length; i++) if (t <= w[i][0]) { const k = (t - w[i - 1][0]) / (w[i][0] - w[i - 1][0]), e = k * k * (3 - 2 * k); return w[i - 1][1] + (w[i][1] - w[i - 1][1]) * e; } return w[w.length - 1][1]; };
  const L1 = Math.hypot(...sub2(B, A)), L2 = Math.hypot(...sub2(C, B));
  const d1 = mul2(sub2(B, A), 1 / L1), d2 = mul2(sub2(C, B), 1 / L2), n1 = [-d1[1], d1[0]], n2 = [-d2[1], d2[0]];
  const outer = d1[0] * d2[1] - d1[1] * d2[0] > 0 ? -1 : 1;     // 往左拐时 +n 侧在里面
  const side = (sg, wa, wb) => {
    const pts = [];
    const o1 = (t) => add2(add2(A, mul2(d1, L1 * t)), mul2(n1, sg * prof(wa, t)));
    const o2 = (t) => add2(add2(B, mul2(d2, L2 * t)), mul2(n2, sg * prof(wb, t)));
    const N1 = Math.max(4, Math.ceil(L1 / step)), N2 = Math.max(4, Math.ceil(L2 / step));
    if (sg === outer) {
      for (let i = 0; i <= N1; i++) pts.push(o1(i / N1));
      // 绕关节的圆弧，半径从第一段末端的半宽过渡到第二段起点的半宽
      const a0 = Math.atan2(sg * n1[1], sg * n1[0]); let a1 = Math.atan2(sg * n2[1], sg * n2[0]);
      let da = a1 - a0; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI;
      const r0 = prof(wa, 1), r1 = prof(wb, 0), K = Math.max(3, Math.ceil(Math.abs(da) * 8));
      for (let k = 1; k < K; k++) { const u = k / K, a = a0 + da * u, r = r0 + (r1 - r0) * u; pts.push(add2(B, [Math.cos(a) * r, Math.sin(a) * r])); }
      for (let i = 0; i <= N2; i++) pts.push(o2(i / N2));
    } else {
      // 里侧：两条轮廓线的交点就是褶
      const p = add2(B, mul2(n1, sg * prof(wa, 1))), q = add2(B, mul2(n2, sg * prof(wb, 0)));
      const den = d1[0] * d2[1] - d1[1] * d2[0];
      let u = 0, v = 0;
      if (Math.abs(den) > 1e-4) { const w = sub2(q, p); u = (w[0] * d2[1] - w[1] * d2[0]) / den; v = (w[0] * d1[1] - w[1] * d1[0]) / den; }
      u = Math.max(-L1 * 0.6, Math.min(0, u)); v = Math.max(0, Math.min(L2 * 0.6, v));
      for (let i = 0; i <= N1; i++) { const t = i / N1; if (L1 * t - L1 > u) break; pts.push(o1(t)); }
      pts.push(add2(p, mul2(d1, u)));
      for (let i = 0; i <= N2; i++) { const t = i / N2; if (L2 * t < v) continue; pts.push(o2(t)); }
    }
    return pts;
  };
  const P = side(1, w1p, w2p), M = side(-1, w1m, w2m);
  const ext = extremity ? extremity(P[P.length - 1], M[M.length - 1]) : [];
  return [...P, ...ext, ...M.reverse()];
}

// pose：{ lean 身体前倾（弧度）, headUp 抬头（弧度）, mouth 0..1, blink 0..1, pig 辫子摆动（弧度）, breathe 0..1 }
// map(p)：局部厘米 → 画面像素
export function parts(map, pose = {}, s = 7) {
  const P = [];
  const toPath = (pts, smooth = true, per = 6) => {
    const q = (smooth ? catmull(pts, true, per) : pts).map(map);
    const p = new Path2D(); q.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y))); p.closePath();
    return { path: p, bbox: bboxOf(q) };
  };
  const strokeL = (ctx, pts, w, color, smooth = true) => {
    const q = (smooth && pts.length > 2 ? catmull(pts, false, 6) : pts).map(map);
    ctx.strokeStyle = color; ctx.lineWidth = w * s; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); q.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke();
  };
  const fillL = (ctx, pts, color, smooth = true) => {
    const q = (smooth ? catmull(pts, true, 6) : pts).map(map);
    ctx.fillStyle = color; ctx.beginPath(); q.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill();
  };
  const radial = (ctx, c, r, color, sy = 1) => {
    const m = map(c); ctx.save(); ctx.translate(m[0], m[1]); ctx.scale(1, sy);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, r * s); g.addColorStop(0, color); g.addColorStop(1, color.replace(/[\d.]+\)$/, '0)'));
    ctx.fillStyle = g; ctx.fillRect(-r * s, -r * s, 2 * r * s, 2 * r * s); ctx.restore();
  };
  const part = (name, pts, o) => P.push({ name, ...toPath(pts, o.smooth ?? pts.length < 60), ...o, R: (o.R ?? 3) * s, shadow: o.shadow ? [o.shadow[0] * s, -o.shadow[1] * s, (o.shadow[2] ?? 0.8) * s, o.shadow[3] ?? 0.4] : null });
  const tubeL = (spine, widths, o = {}) => tube(spine, widths.map((w, i) => [i / (widths.length - 1), w]), { step: 0.4, ...o }).outline;

  // ---------------- 骨架（解出来的姿势）
  const HS = 1.1;
  const norm = (v) => { const l = Math.hypot(v[0], v[1]) || 1; return [v[0] / l, v[1] / l]; };
  const mul = (v, k) => [v[0] * k, v[1] * k];
  const dir = (a) => [Math.cos(a), Math.sin(a)];
  const hip = [0, 8];
  const ankle = [22.5, -15.5], ankleF = [25.0, -15.6];
  const knee = ik(hip, ankle, 30, 28, 1).joint, kneeF = ik(add(hip, [0.8, 0.4]), ankleF, 30, 28, 1).joint;
  const td = norm(sub(knee, hip)), tn = [-td[1], td[0]];               // 大腿方向、大腿"上面"的法向
  const onThigh = (t, o) => add(lerp(hip, knee, t), mul(tn, o));
  const elbow = add(add(knee, mul(td, -3.2)), mul(tn, 6.4));           // 手肘（尺骨鹰嘴）落在膝盖上方
  const breathe = pose.breathe ?? 0;
  const spine = (lam) => { const up = rot([0, 1], -lam); return (d, side = 0) => add(add(hip, mul(up, d)), [up[1] * side, -up[0] * side]); };
  // 上臂 20 厘米：二分求身体前倾角
  let lo = 0.05, hi = 1.3;
  for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; const S = spine(m)(31, -0.6); (Math.hypot(S[0] - elbow[0], S[1] - elbow[1]) > 20 ? (lo = m) : (hi = m)); }
  const lean = (lo + hi) / 2, along = spine(lean);
  const shoulder = add(along(31, -0.6), [0, 0.3 * breathe]), neck0 = add(along(34.2, 1.4), [0, 0.3 * breathe]);
  // 抬头角 hr；手腕在下巴前下方（头的局部坐标 WRIST_L），前臂 16.5 厘米 → 前臂角 phi 由"脖子露出 6.5 厘米"定。
  // 这个条件一般有两个解（前臂竖一点 / 斜一点）。只取前臂竖的那支，并且用二分求精确的根——
  // 之前逐帧取"误差最小"的格点，两个解来回跳，人在画面里一伸一缩。
  const hr = pose.headUp ?? 0.30;
  const WRIST_L = [4.9, -10.2];
  const at = (phi) => {
    const w = add(elbow, mul(dir(phi), 16.5));
    const hc = sub(w, rot(mul(WRIST_L, HS), hr));
    const nb = add(hc, rot(mul([0.6, -5.2], HS), hr));
    return { w, hc, f: Math.hypot(nb[0] - neck0[0], nb[1] - neck0[1]) - 6.5 };
  };
  let phi = 1.35;
  {
    const roots = [];
    let prev = at(0.8);
    for (let x = 0.8 + 0.01; x <= 2.3; x += 0.01) {
      const cur = at(x);
      if (Math.sign(cur.f) !== Math.sign(prev.f)) {
        let a = x - 0.01, b = x;
        for (let i = 0; i < 30; i++) { const m = (a + b) / 2; (Math.sign(at(m).f) === Math.sign(at(a).f) ? (a = m) : (b = m)); }
        roots.push((a + b) / 2);
      }
      prev = cur;
    }
    if (roots.length) phi = roots[0];                 // 前臂更竖的那一支
    else { let bestE = Infinity; for (let x = 0.8; x <= 2.3; x += 0.005) { const e = Math.abs(at(x).f); if (e < bestE) { bestE = e; phi = x; } } }
  }
  const sol = at(phi), wrist = sol.w, head = sol.hc;
  const H = (p) => add(head, rot([p[0] * HS, p[1] * HS], hr));        // 头的局部坐标 → 身体坐标
  const sw = pose.pig ?? 0;

  // ---------------- 后面的辫子（远侧，大部分被头挡住）
  const tieF = H([-7.4, -2.6]);
  part('pigFar', tubeL([tieF, add(tieF, rot([-3.2, -5.0], sw * 0.4)), add(tieF, rot([-3.6, -10.5], sw * 0.8)), add(tieF, rot([-2.4, -15.0], sw))], [2.0, 2.2, 1.6, 0.25]),
    { fill: C.hair, R: 1.6, mat: 2, extra: 0.8 });
  // ---------------- 板凳
  part('stoolLegB', [[-11, -2], [-8.5, -2], [-10.2, -22], [-12.8, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolLegF', [[8.5, -2], [11, -2], [12.8, -22], [10.2, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolRung', [[-11.2, -13], [11.4, -13], [11.6, -15], [-11.4, -15]], { fill: C.stoolDark, R: 0.8, smooth: false });
  part('stoolSeat', [[-14, 0.5], [14, 0.5], [14, -3], [-14, -3]], { fill: C.stool, R: 1.4, smooth: false,
    detail: (c) => { strokeL(c, [[-13, -1.2], [13, -1.0]], 0.12, 'rgba(60,35,20,0.5)'); } });
  // ---------------- 腿：一笔外轮廓（大腿面 → 膝盖骨 → 胫骨 → 脚背 → 脚趾 → 脚底 → 脚跟 → 跟腱 → 小腿肚 → 膝窝的褶 → 大腿底面）
  const legShape = (k, a, grp, fill, near) => {
    const foot = (pEnd, mEnd) => [
      [a[0] + 2.7, a[1] - 0.9], [a[0] + 5.0, a[1] - 2.5], [a[0] + 8.8, a[1] - 4.1], [a[0] + 11.8, a[1] - 5.0], [a[0] + 13.2, a[1] - 5.6],
      [a[0] + 13.3, a[1] - 6.2], [a[0] + 12.2, a[1] - 6.5], [a[0] + 8.0, a[1] - 6.45], [a[0] + 4.6, a[1] - 6.0], [a[0] + 1.2, a[1] - 6.3],
      [a[0] - 2.0, a[1] - 6.5], [a[0] - 3.3, a[1] - 5.8], [a[0] - 3.6, a[1] - 4.0], [a[0] - 3.0, a[1] - 2.0]];
    const out = limbOutline(add(hip, [-1.5, 0.5]), k, a,
      [[0, 6.0], [0.5, 5.6], [0.85, 4.8], [1, 4.4]],            // 大腿面
      [[0, 6.0], [0.5, 5.5], [0.85, 4.6], [1, 4.3]],            // 大腿底面
      [[0, 4.3], [0.15, 3.7], [0.5, 3.3], [0.85, 2.6], [1, 2.3]],   // 小腿前面（胫骨，几乎是直的）
      [[0, 4.1], [0.25, 4.8], [0.5, 4.2], [0.8, 2.8], [1, 2.4]],   // 小腿肚
      foot);
    part(grp, out, { fill, R: 2.6, flat: 0.35, mat: 1, smooth: false,
    });
  };
  // 远侧的腿（在暗处，颜色深一点，大半被近侧挡住）
  legShape(kneeF, ankleF, 'legF', C.skinDeep, false);
  part('sandalF', sandalPts(ankleF), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankleF).forEach((q, i) => part('strapF' + i, q, { fill: '#9e2522', R: 0.8, smooth: false }));
  // 远侧的前臂：在近侧胳膊后面，手托在远侧脸颊上（被头挡住）
  const fd = dir(phi);
  const wristF = add(wrist, [1.2, 0.6]);
  part('armF', tubeL([add(elbow, [1.6, 0.2]), lerp(add(elbow, [1.6, 0.2]), wristF, 0.3), wristF], [2.5, 2.4, 1.9]), { fill: C.skinDeep, R: 1.9, flat: 0.4, mat: 1, smooth: false });
  // ---------------- 近侧的腿
  legShape(knee, ankle, 'legN', C.skin, true);
  part('sandal', sandalPts(ankle), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankle).forEach((q, i) => part('strap' + i, q, { fill: C.sandal, R: 0.8, smooth: false, shadow: [-0.1, -0.2, 0.3, 0.3] }));
  // ---------------- 身体 + 裙子：后背微微拱起（身子前倾）；裙子盖住大腿到膝盖上面一点
  // 裙子顺着大腿面盖下来（裙子上沿 = 大腿面 + 布的厚度），裙摆斜着包住大腿：上面盖到膝盖前一点，下面短一点，
  // 在大腿底下垂一点。膝盖和小腿从裙摆底下自然伸出来，裙摆在腿上投一点影子（不是"安"在裙子外面的一截腿）。
  const hemTop = 0.84, hemBot = 0.72;
  const dress = [
    along(33.6, -3.4), along(29.5, -6.0), along(22, -7.0), along(14, -6.8), along(6, -6.6),       // 后背
    [-7.6, 3.0], [-7.4, -0.6], [-2, -0.9],                                                            // 坐在凳面上的臀部
    onThigh(0.4, -6.6), onThigh(0.62, -6.9), onThigh(hemBot, -6.5),                                    // 大腿底下垂着的裙子
    onThigh((hemBot * 2 + hemTop) / 3, -3.0), onThigh((hemBot + hemTop * 2) / 3, 1.5), onThigh(hemTop, 5.0),   // 斜着的裙摆，包住大腿
    onThigh(hemTop - 0.04, 5.9), onThigh(0.6, 6.2), onThigh(0.3, 6.6), onThigh(0.1, 7.0),               // 腿面（贴着大腿面）
    along(10, 6.2), along(18, 6.6), along(25, 5.8), along(30.8, 3.4),                                  // 肚子、胸口
  ];
  part('dress', dress, { fill: C.dress, R: 3.0, flat: 0.4, mat: 3, extra: 0.3, shadow: [0.3, -0.6, 0.8, 0.45],
    detail: (c) => {
      for (let i = -8; i < 14; i++) for (let j = -3; j < 14; j++) {
        const q = add(hip, [i * 3.3 + (j % 2) * 1.65, j * 3.3]);
        const m = map(q); c.fillStyle = 'rgba(251,230,162,0.6)'; c.beginPath(); c.arc(m[0], m[1], 0.4 * s, 0, 6.283); c.fill();
      }
      // 腰线（前倾时腰在肚子那里折一下）、腿面上布料被拉出的褶、裙摆的一道边
      strokeL(c, [along(12, -6.6), along(12.4, 0), along(11.5, 6.0)], 0.22, 'rgba(160,96,20,0.45)');
      strokeL(c, [onThigh(0.25, 4.5), onThigh(0.55, 3.6), onThigh(hemTop - 0.06, 2.0)], 0.15, 'rgba(160,96,20,0.3)');
      strokeL(c, [onThigh(hemTop - 0.01, 5.0), onThigh((hemBot + hemTop * 2) / 3 - 0.01, 1.5), onThigh((hemBot * 2 + hemTop) / 3 - 0.01, -3.0), onThigh(hemBot - 0.01, -6.3)], 0.32, 'rgba(160,96,20,0.4)');   // 裙摆的折边
    } });
  // 白色小圆领
  part('collar', [along(33.8, -3.2), along(35.2, -1.4), along(35.4, 2.2), along(32.6, 4.2), along(30.0, 3.8), along(30.6, 0.4), along(31.2, -2.6)],
    { fill: C.collar, R: 1.3, flat: 0.3, mat: 3, extra: 0.4, shadow: [-0.2, -0.3, 0.4, 0.3] });
  // ---------------- 脖子、头
  part('neck', tubeL([H([0.6, -4.6]), lerp(H([0.6, -4.6]), neck0, 0.5), add(neck0, [-0.2, -1.6])], [3.2, 3.0, 3.4]), { fill: C.skinDeep, R: 2.4, flat: 0.3, mat: 1 });
  const face = [[2.0, 9.6], [5.6, 7.9], [7.5, 5.2], [8.3, 3.0], [8.0, 1.5], [8.4, 0.3], [9.5, -1.4], [9.6, -2.1], [9.1, -2.5], [8.5, -2.7],
    [8.7, -3.2], [8.95, -3.75], [8.45, -4.2], [8.55, -4.65], [8.2, -5.2], [8.3, -5.9], [7.6, -6.9], [5.8, -7.6], [3.0, -7.2], [0.6, -5.9],
    [-2.2, -3.2], [-4.2, 2.0], [-2.2, 8.2]];
  const eyeC = [5.9, 0.7], blink = pose.blink ?? 0;
  part('face', face.map(H), { fill: C.skin, R: 4.0, flat: 0.2, mat: 1, tilt: [0.75, 0.15],
    detail: (c) => {
      radial(c, H([5.0, -2.6]), 2.3, C.blush, 0.65);                                       // 脸蛋
      strokeL(c, [H([8.75, -2.1]), H([8.45, -2.35])], 0.22, 'rgba(150,80,60,0.55)');        // 鼻孔
      // 嘴：微微张开（看得入迷）
      const mo = pose.mouth ?? 0.6;
      fillL(c, [H([8.95, -3.85]), H([8.0, -4.0]), H([7.7, -4.2]), H([8.2, -4.25 - 0.25 * mo]), H([8.65, -4.15 - 0.35 * mo])], '#5a2420');
      strokeL(c, [H([8.95, -3.8]), H([8.1, -3.95])], 0.14, C.lip);
      // 眼睛（侧面：杏仁形、前面有一点眼珠的弧）
      const op = 1 - blink;
      const eyeShape = [[4.55, 0.85], [5.3, 1.75 * op + 0.8 * (1 - op)], [6.55, 2.05 * op + 0.85 * (1 - op)], [7.45, 1.35], [6.95, 0.05 * op + 0.7 * (1 - op)], [5.6, -0.15 * op + 0.75 * (1 - op)]].map((p) => H(p));
      if (op > 0.15) {
        fillL(c, eyeShape, C.eyeW);
        c.save(); const ep = new Path2D(); catmull(eyeShape, true, 6).map(map).forEach(([x, y], i) => (i ? ep.lineTo(x, y) : ep.moveTo(x, y))); ep.closePath(); c.clip(ep);
        fillL(c, ellipse(...H([6.55, 0.95]), 0.95, 1.25, hr), C.iris);
        fillL(c, ellipse(...H([6.75, 1.0]), 0.5, 0.75, hr), C.pupil);
        c.restore();
      }
      // 上眼皮的线和睫毛
      strokeL(c, [H([4.35, 0.95]), H([5.3, 1.85 * op + 0.85 * (1 - op)]), H([6.6, 2.15 * op + 0.9 * (1 - op)]), H([7.55, 1.5])], 0.36, '#2a1612');
      if (op > 0.45) {   // 睁着：睫毛往上翘
        strokeL(c, [H([7.2, 1.85]), H([7.85, 2.5]), H([8.25, 2.6])], 0.16, '#2a1612');
        strokeL(c, [H([6.7, 2.1]), H([7.15, 2.85]), H([7.5, 3.05])], 0.15, '#2a1612');
        strokeL(c, [H([6.1, 2.1]), H([6.4, 2.75])], 0.13, '#2a1612');
      } else {           // 闭着：眼皮合成一道往下弯的线，睫毛顺着往下
        strokeL(c, [H([7.3, 1.0]), H([7.9, 0.6]), H([8.2, 0.55])], 0.15, '#2a1612');
        strokeL(c, [H([6.7, 0.85]), H([7.1, 0.35]), H([7.4, 0.25])], 0.14, '#2a1612');
      }
      strokeL(c, [H([5.7, -0.2]), H([6.9, -0.05])], 0.08, 'rgba(120,60,50,0.4)');          // 下眼皮
      strokeL(c, [H([5.0, 3.55]), H([6.2, 3.95]), H([7.4, 3.85])], 0.28, '#3a2419');          // 眉毛
    } });
  // 眼睛里的高光：映着床单（单独一块，材质 4）
  if (1 - blink > 0.4) {
    part('glint', ellipse(...H([6.95, 1.45]), 0.36, 0.42, hr, 12), { fill: '#ffffff', R: 0.4, mat: 4, keepNormal: true });
    part('glint2', ellipse(...H([6.25, 0.45]), 0.16, 0.16, 0, 8), { fill: '#ffffff', R: 0.2, mat: 4, keepNormal: true });
  }
  // 耳朵
  const ear = [[0.5, 1.6], [-0.9, 2.4], [-2.4, 1.4], [-2.7, -1.2], [-1.9, -3.4], [-0.6, -4.2], [0.3, -3.6], [0.0, -2.2], [0.5, -0.2]].map(([x, y]) => [x * 0.66 - 0.6, y * 0.66 + 0.1]);
  part('ear', ear.map(H), { fill: '#eab597', R: 0.7, flat: 0.6, mat: 1, extra: 0.3,
    detail: (c) => { fillL(c, [H([-1.0, 0.8]), H([-1.8, 0.5]), H([-1.9, -0.8]), H([-1.4, -1.5]), H([-1.1, -0.7])], 'rgba(196,120,96,0.45)'); } });
  // 头发
  const hairPts = [[6.2, 7.7], [3.5, 10.7], [0, 11.5], [-4.6, 10.5], [-8.7, 7.0], [-10.3, 2.3], [-9.7, -2.5], [-7.5, -5.6], [-4.8, -5.2], [-3.2, -3.4],
    [-3.4, 0.0], [-2.0, 2.9], [0.6, 3.6], [2.7, 3.2], [3.6, 4.8], [4.8, 6.6]];
  part('hair', hairPts.map(H), { fill: C.hair, R: 5.0, mat: 2, extra: 0.6, shadow: [-0.2, -0.3, 0.6, 0.5],
    detail: (c) => {
      // 往后梳的发丝
      // 头顶一圈淡淡的光泽（发丝的反光），再加一绺绺往后梳到辫子根的发丝
      strokeL(c, [H([4.6, 9.4]), H([0.5, 10.6]), H([-4.0, 9.6]), H([-7.4, 6.6])], 1.3, 'rgba(120,84,66,0.35)');
      strokeL(c, [H([4.4, 9.2]), H([0.5, 10.3]), H([-4.0, 9.3])], 0.45, 'rgba(160,118,92,0.35)');
      for (let i = 0; i < 12; i++) {
        const t = i / 11;
        strokeL(c, [H([6.0 - t * 2.5, 7.8 + t * 2.6]), H([0 - t * 2.2, 9.8 + t * 1.0 - t * t * 3]), H([-5 - t * 1.8, 6.5 - t * 3.2]), H([-7.2, -3.4])], 0.1 + (i % 3) * 0.04, i % 2 ? 'rgba(96,66,52,0.6)' : 'rgba(8,5,4,0.55)');
      }
    } });
  // 刘海：齐刘海，下沿三四绺
  const bangs = [[2.4, 9.9], [6.2, 8.7], [7.9, 6.8], [8.45, 5.3], [8.25, 4.55], [7.7, 4.1], [7.25, 4.6], [6.65, 3.95], [6.05, 4.65], [5.4, 4.2], [4.75, 5.05], [4.0, 5.9], [3.4, 7.0], [2.9, 8.2]];
  part('bangs', bangs.map(H), { fill: C.hair, R: 2.0, mat: 2, extra: 0.8, shadow: [-0.1, -0.5, 0.4, 0.45],
    detail: (c) => { for (let i = 0; i < 5; i++) strokeL(c, [H([3.4 + i * 1.1, 8.8 - i * 0.2]), H([4.1 + i * 1.1, 5.0 + (i % 2) * 0.3])], 0.1, 'rgba(90,62,50,0.5)'); } });
  // 呆毛
  part('cowlick', tubeL([H([0.2, 11.0]), H([1.3, 12.9]), H([2.9, 13.6]), H([3.3, 12.6])], [0.55, 0.45, 0.3, 0.05]), { fill: C.hair, R: 0.5, mat: 2, extra: 1.0 });
  // 近侧的辫子：扎在耳朵后面，垂下来（重力方向是竖直的，不跟头转）
  const tie = H([-7.6, -3.6]);
  const pig = [tie, add(tie, rot([-3.0, -5.0], sw * 0.5)), add(tie, rot([-3.8, -10.5], sw)), add(tie, rot([-2.8, -16.0], sw * 1.2))];
  part('pig', tubeL(pig, [2.4, 2.6, 1.9, 0.3]), { fill: C.hair, R: 1.8, mat: 2, extra: 0.9, shadow: [0.3, -0.4, 0.6, 0.45],
    detail: (c) => { for (let i = -1; i <= 1; i++) strokeL(c, pig.map((p, k) => add(p, [i * 0.6 * (1 - k / 4), 0])), 0.1, 'rgba(90,62,50,0.55)'); } });
  part('tie1', ellipse(...add(tie, [0.3, 0.7]), 1.25, 1.2), { fill: C.tie, R: 1.1, mat: 3, extra: 0.6, shadow: [-0.2, -0.3, 0.4, 0.4] });
  part('tie2', ellipse(...add(tie, [-0.8, -0.6]), 1.2, 1.15), { fill: C.tie, R: 1.1, mat: 3, extra: 0.6 });
  // ---------------- 近侧的胳膊：一笔外轮廓（后面：三角肌 → 肱三头肌 → 肘尖 → 前臂背面；前面：前臂掌面 → 肘窝的褶 → 肱二头肌）
  const ud = norm(sub(elbow, shoulder)), un = [-ud[1], ud[0]];
  const armOut = limbOutline(add(shoulder, mul(ud, -1.2)), elbow, wrist,
    [[0, 3.1], [0.4, 2.9], [0.85, 2.4], [1, 2.3]],                // 上臂前面（肱二头肌）
    [[0, 3.2], [0.35, 3.0], [0.8, 2.5], [1, 2.2]],                // 上臂后面（肱三头肌）
    [[0, 2.4], [0.2, 2.75], [0.6, 2.2], [1, 1.75]],               // 前臂靠身体一侧（肌肉在靠肘处鼓）
    [[0, 2.2], [0.25, 2.5], [0.6, 2.05], [1, 1.75]], null);       // 前臂外侧（尺骨，比较直）
  part('arm', armOut, { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN', groupR: 1.9 * s, smooth: false, shadow: [-0.3, -0.4, 0.6, 0.25] });
  // ---------------- 手：张开托着脸颊。手背朝外，四根手指分开搭在脸颊上，大拇指顺着下颌往前
  // 手的局部坐标：u 从手腕指向中指指尖，v 往脸的前面（大拇指那边）为正
  const tipL = [2.4, -1.4];                                         // 中指指尖落在脸颊上（头的局部坐标）
  const hd = norm(sub(H(tipL), wrist)), hv0 = [-hd[1], hd[0]];
  const hv = hv0[0] > 0 ? hv0 : mul(hv0, -1);                       // 让 v 朝前
  const HW = (u, v) => add(wrist, add(mul(hd, u), mul(hv, v)));
  const handLen = Math.hypot(...sub(H(tipL), wrist));
  const palmL = handLen * 0.53;                                     // 手掌约占手长一半
  part('palm', [[-0.8, 1.75], [1.5, 2.15], [palmL * 0.6, 2.45], [palmL, 2.35], [palmL + 0.3, 1.2], [palmL + 0.3, -1.0], [palmL, -2.1], [palmL * 0.6, -2.35], [1.5, -2.0], [-0.8, -1.75]].map(([u, v]) => HW(u, v)),
    { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN' });
  // 四根手指：食指在前，小指在后，微微张开；每根是圆头的细长条，带两道指节纹和指甲
  const fingers = [[1.85, 0.07, 0.86, 0.56], [0.62, 0.0, 1.0, 0.58], [-0.62, -0.07, 0.92, 0.55], [-1.8, -0.15, 0.72, 0.48]];
  fingers.forEach(([v0, ang, lenK, w], i) => {
    const len = (handLen - palmL) * lenK + 0.3;
    const fdir = rot(hd, ang * (hv === hv0 ? 1 : -1));
    const base = HW(palmL - 0.3, v0), tip = add(base, mul(fdir, len));
    const pts = tubeL([base, lerp(base, tip, 0.5), tip], [w, w * 0.95, w * 0.85]);
    part('finger' + i, pts, { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN', smooth: false, shadow: [-0.12, -0.18, 0.25, 0.3],
      detail: (c) => {
        const fn = [-fdir[1], fdir[0]];
        for (const k of [0.38, 0.7]) { const q = lerp(base, tip, k); strokeL(c, [add(q, mul(fn, -w * 0.7)), add(q, mul(fn, w * 0.7))], 0.07, 'rgba(170,100,84,0.45)'); }
        const nb = lerp(base, tip, 0.82);
        fillL(c, ellipse(...add(nb, mul(fdir, 0.15)), w * 0.55, w * 0.42, Math.atan2(fdir[1], fdir[0]) + Math.PI / 2, 12), 'rgba(248,214,200,0.85)');   // 指甲
      } });
  });
  // 大拇指：从手掌靠手腕的地方伸出来，顺着下颌往前（两节）
  const tb = HW(1.6, 1.9), tdir = norm(add(mul(hd, 0.45), mul(hv, 0.9)));
  const tm = add(tb, mul(tdir, 2.2)), tt = add(tm, mul(norm(add(tdir, mul(hd, 0.25))), 1.9));
  part('thumb', tubeL([tb, tm, tt], [0.72, 0.62, 0.55]), { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN', smooth: false, shadow: [-0.1, -0.15, 0.2, 0.25],
    detail: (c) => { strokeL(c, [add(tm, mul(hd, -0.5)), add(tm, mul(hd, 0.5))], 0.07, 'rgba(170,100,84,0.45)'); fillL(c, ellipse(...lerp(tm, tt, 0.72), 0.36, 0.28, Math.atan2(tdir[1], tdir[0]) + Math.PI / 2, 12), 'rgba(248,214,200,0.85)'); } });
  // 泡泡袖：肩头鼓起来的灯笼形，袖口收一道边（盖住上臂上面一小半）
  const A = (u, v) => add(shoulder, add(mul(ud, u), mul(un, v)));
  const sl = [A(-3.2, 2.4), A(-1.0, 3.8), A(2.2, 4.1), A(4.4, 3.8), A(5.6, 3.35), A(6.2, 3.3), A(6.5, 0), A(6.2, -3.35), A(5.6, -3.4), A(4.2, -3.9), A(1.6, -4.1), A(-1.2, -3.6), A(-3.2, -2.5), A(-3.9, 0)];
  part('sleeve', sl, { fill: C.dress, R: 2.4, flat: 0.3, mat: 3, extra: 0.3, shadow: [-0.3, -0.4, 0.5, 0.35],
    detail: (c) => {
      strokeL(c, [A(5.6, -3.3), A(5.9, 0), A(5.6, 3.3)], 0.5, 'rgba(160,96,20,0.4)');   // 袖口收的那道边，箍在胳膊上
      for (let i = 0; i < 3; i++) strokeL(c, [A(0.4 + i * 1.4, -3.0), A(1.2 + i * 1.4, 0), A(0.9 + i * 1.4, 3.0)], 0.12, 'rgba(160,96,20,0.25)');
    } });
  P.joints = { hip, knee, ankle, kneeF, ankleF, neck0, head, shoulder, elbow, wrist, chest: along(20, 1), belly: along(10, 0), lean, phi, tip: H(tipL) };
  return P;
}

function footPts(a) {
  // 脚：脚跟圆、脚背从脚踝斜着下去、足弓、脚趾圆头；长约 17 厘米，脚踝处高约 6.5 厘米
  return [[a[0] - 2.2, a[1] + 2.0], [a[0] + 1.4, a[1] + 1.8], [a[0] + 4.6, a[1] - 1.6], [a[0] + 8.8, a[1] - 3.6], [a[0] + 12.0, a[1] - 4.6],
    [a[0] + 13.2, a[1] - 5.4], [a[0] + 12.9, a[1] - 6.1], [a[0] + 6.0, a[1] - 6.2], [a[0] + 2.0, a[1] - 5.8], [a[0] - 2.6, a[1] - 6.1], [a[0] - 3.7, a[1] - 5.0], [a[0] - 3.3, a[1] - 1.6]];
}
function sandalPts(a) {
  // 红凉鞋：鞋底 + 脚背上一道宽带子 + 脚踝一道细带子（连成一块）
  return [[a[0] - 3.8, a[1] - 5.4], [a[0] + 13.8, a[1] - 5.4], [a[0] + 13.8, a[1] - 6.7], [a[0] - 3.9, a[1] - 6.7], [a[0] - 3.9, a[1] - 5.4]];
}
export function strapPts(a) {
  return [[[a[0] + 4.2, a[1] - 0.4], [a[0] + 6.0, a[1] - 1.5], [a[0] + 7.6, a[1] - 5.6], [a[0] + 5.4, a[1] - 5.6]],
    [[a[0] - 2.8, a[1] + 1.6], [a[0] + 1.4, a[1] + 1.4], [a[0] + 1.6, a[1] + 0.2], [a[0] - 3.2, a[1] + 0.3]]];
}
export const COLORS = C;
