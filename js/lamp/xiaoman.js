// 小满（9 岁，约 1.32 米）：背挺直坐在小板凳上，双手搭在膝盖上，抬头看床单上的鹤。侧面（脸朝右）。
// 局部坐标：厘米，x 朝她面朝的方向，y 朝上，原点在板凳面的中心；地面 y = -22。
// 比例按 9 岁女孩的人体尺寸（头略放大一点）：上臂 20、前臂 16、手 12.4、大腿 29、小腿 26.5、脚 18 厘米。
// 先定外形（骨盆坐稳、胸在骨盆正上方、肩放松、脚平放），再用骨长连起来；手顺着膝盖的轮廓搭上去，手肘由手和肩的位置定。
// 同一块皮肉（上臂-前臂-手）是一个"组"，法线合起来算，手肘、手腕不出接缝。
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

// 分段宽度表 [[t, w], ...] 上平滑插值
function prof(w, t) {
  if (t <= w[0][0]) return w[0][1];
  for (let i = 1; i < w.length; i++) if (t <= w[i][0]) { const k = (t - w[i - 1][0]) / (w[i][0] - w[i - 1][0]), e = k * k * (3 - 2 * k); return w[i - 1][1] + (w[i][1] - w[i - 1][1]) * e; }
  return w[w.length - 1][1];
}

// 一笔画出整条四肢的外轮廓（A 根 → B 关节 → C 末端），像画师画人体那样：
//   弯曲的外侧绕着关节画一段圆弧（膝盖骨、肘尖），内侧两条轮廓线在关节处相交、挤出一道褶（膝窝、肘窝）；
//   末端接上脚或手腕。这样整条腿/胳膊是一块连续的肉，不会像拼起来的管子那样在关节处鼓出"球关节"。
// w1p/w1m：第一段在 +n / −n 两侧的半宽 [[t, w], ...]；w2p/w2m：第二段。extremity(pEnd, mEnd) 返回从 + 侧末端绕到 − 侧末端的点。
function limbOutline(A, B, C, w1p, w1m, w2p, w2m, extremity = null, step = 0.6) {
  const sub2 = (a, b) => [a[0] - b[0], a[1] - b[1]], add2 = (a, b) => [a[0] + b[0], a[1] + b[1]], mul2 = (a, k) => [a[0] * k, a[1] * k];
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
      pts.arcStart = pts.length - 1;
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
  const res = [...P, ...ext, ...[...M].reverse()];
  res.sideP = P; res.sideM = M;
  return res;
}

// 搭在一条轮廓（比如腿的外轮廓）上的东西：沿着轮廓从 s0 往前 len 厘米，厚度 thick(u)（u = 0..1），
// 里侧陷进去 sink 厘米（压着皮肉，不留缝）。返回外形，以及 at(u, v)：沿轮廓 u 处、离里侧 v 厘米的点。
function onCurve(curve, s0, len, thick, sink = 0.35, step = 0.25) {
  const cum = [0];
  for (let i = 1; i < curve.length; i++) cum.push(cum[i - 1] + Math.hypot(curve[i][0] - curve[i - 1][0], curve[i][1] - curve[i - 1][1]));
  const pos = (s) => {
    s = Math.max(0, Math.min(cum[cum.length - 1], s));
    let i = 1; while (i < curve.length - 1 && cum[i] < s) i++;
    const a = curve[i - 1], b = curve[i], k = (s - cum[i - 1]) / ((cum[i] - cum[i - 1]) || 1);
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
  };
  const frame = (s) => {   // 法线用前后各 0.8 厘米的弦算，轮廓顶点处不折
    const a = pos(s - 0.8), b = pos(s + 0.8), d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    return { p: pos(s), d: [(b[0] - a[0]) / d, (b[1] - a[1]) / d], n: [-(b[1] - a[1]) / d, (b[0] - a[0]) / d] };
  };
  const at = (u, v) => { const f = frame(s0 + u * len); return [f.p[0] + f.n[0] * (v - sink), f.p[1] + f.n[1] * (v - sink)]; };
  const N = Math.max(8, Math.ceil(len / step)), outer = [], inner = [];
  for (let i = 0; i <= N; i++) { const u = i / N; outer.push(at(u, thick(u))); inner.push(at(u, 0)); }
  // 末端圆头
  const f = frame(s0 + len), r = thick(1) / 2, c = at(1, r), cap = [];
  for (let k = 1; k < 8; k++) { const a = (k / 8) * Math.PI; cap.push([c[0] + f.n[0] * r * Math.cos(a) + f.d[0] * r * Math.sin(a), c[1] + f.n[1] * r * Math.cos(a) + f.d[1] * r * Math.sin(a)]); }
  return { outline: [...outer, ...cap, ...inner.reverse()], at, cum };
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

  // ---------------- 骨架：直背坐在小板凳上，双手搭在膝盖上，抬头看。
  // 先定外形上要的样子（骨盆坐稳、胸在骨盆正上方、肩放松、脚平放在地上），再用固定的骨长把它们连起来。
  const HS = 1.18;                                                   // 头略放大：站着约 5.8 头身
  const norm = (v) => { const l = Math.hypot(v[0], v[1]) || 1; return [v[0] / l, v[1] / l]; };
  const mul = (v, k) => [v[0] * k, v[1] * k];
  const hip = [0, 8];
  const lean = pose.lean ?? 0.04;                                    // 身子微微前倾（看入迷了会再往前一点）
  const breathe = pose.breathe ?? 0;
  const up = rot([0, 1], -lean);
  const along = (d, side = 0) => add(add(hip, mul(up, d)), [up[1] * side, -up[0] * side]);   // 沿脊柱 d 厘米，side > 0 往前
  // 腿：凳面高 22 厘米，脚平放，小腿差不多竖直，膝盖比髋略高（低凳子上本来就这样坐）
  const ankle = [32.5, -15.8], ankleF = [34.2, -15.9];             // 脚稍往前伸，小腿斜一点，放松
  const knee = ik(hip, ankle, 29, 26.5, 1).joint, kneeF = ik(add(hip, [0.6, 0.3]), ankleF, 29, 26.5, 1).joint;
  const td = norm(sub(knee, hip)), tn = [-td[1], td[0]];
  const onThigh = (t, o) => add(lerp(hip, knee, t), mul(tn, o));
  const bre = [0, 0.35 * breathe];
  const shoulder = add(along(31.5, -0.8), bre), neck0 = add(along(34.6, 0.9), bre);
  // 头：孩子的脖子短而粗；抬头一部分来自脖子往后仰
  const hr = pose.headUp ?? 0.25;
  const neckTop = add(neck0, mul(rot(up, hr * 0.45), 3.4));
  const head = sub(neckTop, rot(mul([0.6, -5.2], HS), hr));
  const H = (p) => add(head, rot([p[0] * HS, p[1] * HS], hr));        // 头的局部坐标 → 身体坐标
  const sw = pose.pig ?? 0;

  // 腿的宽度（半宽，厘米）：孩子的腿肉乎乎的，膝盖不尖
  const W_THIGH_TOP = [[0, 5.8], [0.5, 5.3], [0.85, 4.6], [1, 4.3]], W_THIGH_BOT = [[0, 5.8], [0.5, 5.2], [0.85, 4.5], [1, 4.2]];
  const W_SHIN = [[0, 4.2], [0.15, 3.8], [0.5, 3.4], [0.85, 2.8], [1, 2.5]], W_CALF = [[0, 4.0], [0.22, 4.9], [0.45, 4.4], [0.75, 3.0], [1, 2.6]];
  const legOutline = (k, a) => limbOutline(add(hip, [-1.5, 0.5]), k, a, W_THIGH_TOP, W_THIGH_BOT, W_SHIN, W_CALF, (pEnd, mEnd) => [
    [a[0] + 2.7, a[1] - 0.9], [a[0] + 5.0, a[1] - 2.5], [a[0] + 8.8, a[1] - 4.1], [a[0] + 11.8, a[1] - 5.0], [a[0] + 13.2, a[1] - 5.6],
    [a[0] + 13.3, a[1] - 6.2], [a[0] + 12.2, a[1] - 6.5], [a[0] + 8.0, a[1] - 6.45], [a[0] + 4.6, a[1] - 6.0], [a[0] + 1.2, a[1] - 6.3],
    [a[0] - 2.0, a[1] - 6.5], [a[0] - 3.3, a[1] - 5.8], [a[0] - 3.6, a[1] - 4.0], [a[0] - 3.0, a[1] - 2.0]]);
  const legN = legOutline(knee, ankle), legF = legOutline(kneeF, ankleF);
  // 手：顺着膝盖的外轮廓搭上去——手腕在大腿面上，手背拱过膝盖顶，手指沿膝盖前面垂下来。
  // 从外侧（小指那边）看：大拇指在膝盖里侧看不见，小指、无名指贴在膝盖侧面，中指最长、指尖在最前面。
  const HAND_LEN = 12.4, HAND_BACK = 5.2;                             // 手长；手腕在膝盖顶点之前多少厘米
  const handThick = (u) => prof([[0, 0.0], [0.13, 2.3], [0.2, 2.35], [0.42, 2.05], [0.52, 2.1], [0.6, 1.4], [0.85, 1.12], [1, 0.95]], u);
  const handOn = (leg, len = HAND_LEN, from = 0, thick = handThick, sink = 0.35) => {
    const sp = leg.sideP, h0 = onCurve(sp, 0, 1, () => 1);
    return onCurve(sp, h0.cum[sp.arcStart] - HAND_BACK + from, len, thick, sink);
  };
  const handN = handOn(legN), handF = handOn(legF);
  // 无名指、小指：离我们更近，贴在膝盖侧面，所以在侧面投影里比中指"陷"进去一点；指尖一个比一个短
  const fingerThick = (u) => prof([[0, 0.3], [0.18, 1.08], [0.8, 1.0], [1, 0.88]], u);
  const ringN = handOn(legN, 5.4, 6.2, fingerThick, 1.05), pinkyN = handOn(legN, 4.2, 6.4, (u) => fingerThick(u) * 0.9, 1.7);
  const wrist = handN.at(0.13, 1.15), wristF = handF.at(0.13, 1.15);   // 手掌根从前臂底下楔出来，不留台阶
  // 手肘朝后下方。骨长取 9 岁孩子的正常值；任何时候肩到手腕都要比两段骨头加起来短，手臂才是自然微弯，不会被拉直锁死
  const elbow = ik(shoulder, wrist, 20, 16, -1).joint;
  const elbowF = add(elbow, [1.4, 0.3]);

  // ---------------- 后面的辫子（远侧，大半被头挡住）
  const tieF = H([-6.7, -2.4]);
  part('pigFar', tubeL([tieF, add(tieF, rot([-2.4, -3.4], sw * 0.4)), add(tieF, rot([-3.0, -7.2], sw * 0.8)), add(tieF, rot([-2.3, -10.4], sw))], [2.0, 2.3, 1.8, 0.35]),
    { fill: C.hair, R: 1.6, mat: 2, extra: 0.8 });
  // ---------------- 板凳
  part('stoolLegB', [[-11, -2], [-8.5, -2], [-10.2, -22], [-12.8, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolLegF', [[8.5, -2], [11, -2], [12.8, -22], [10.2, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolRung', [[-11.2, -13], [11.4, -13], [11.6, -15], [-11.4, -15]], { fill: C.stoolDark, R: 0.8, smooth: false });
  part('stoolSeat', [[-14, 0.5], [14, 0.5], [14, -3], [-14, -3]], { fill: C.stool, R: 1.4, smooth: false,
    detail: (c) => { strokeL(c, [[-13, -1.2], [13, -1.0]], 0.12, 'rgba(60,35,20,0.5)'); } });
  // ---------------- 远侧的腿、胳膊、手（在暗处，颜色深一点，大半被近侧挡住）
  part('legF', legF, { fill: C.skinDeep, R: 2.6, flat: 0.45, mat: 1, smooth: false });
  part('sandalF', sandalPts(ankleF), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankleF).forEach((q, i) => part('strapF' + i, q, { fill: '#9e2522', R: 0.8, smooth: false }));
  part('armF', limbOutline(add(elbowF, mul(norm(sub(elbowF, wristF)), 1.0)), lerp(elbowF, wristF, 0.5), add(wristF, mul(norm(sub(wristF, elbowF)), 0.8)),
    [[0, 2.4], [1, 2.2]], [[0, 2.3], [1, 2.1]], [[0, 2.2], [1, 1.55]], [[0, 2.1], [1, 1.5]]), { fill: C.skinDeep, R: 1.9, flat: 0.5, mat: 1, group: 'armF', smooth: false });
  part('handF', handF.outline, { fill: C.skinDeep, R: 1.9, flat: 0.5, mat: 1, group: 'armF', smooth: false });
  // ---------------- 近侧的腿：一笔外轮廓（大腿面 → 膝盖 → 胫骨 → 脚背 → 脚底 → 脚跟 → 小腿肚 → 膝窝 → 大腿底面）
  part('legN', legN, { fill: C.skin, R: 2.6, flat: 0.45, mat: 1, smooth: false });
  part('sandal', sandalPts(ankle), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankle).forEach((q, i) => part('strap' + i, q, { fill: C.sandal, R: 0.8, smooth: false, shadow: [-0.1, -0.2, 0.3, 0.3] }));
  // ---------------- 身体 + 裙子：背自然地直（腰稍往里收、屁股坐在凳面上），小肚子微微鼓；
  // 裙子从腰上散开，盖住屁股和大腿，裙摆在膝盖前几厘米，大腿底下垂下一点布；膝盖和小腿从裙摆下面伸出来。
  const hemTop = 0.84, hemBot = 0.67;
  const dress = [
    along(34.0, -3.2), along(31.5, -5.9), along(27, -7.0), along(21, -6.6), along(15.5, -5.4), along(10.5, -5.9), along(6, -7.3), along(2.5, -7.9),   // 后背、腰、屁股
    [-7.2, 1.6], [-5.6, 0.6], [4, 0.5], [13.6, 0.45],                                                                               // 坐在凳面上
    [16.2, -0.5], [18.8, -0.7], onThigh(hemBot - 0.04, -7.6), onThigh(hemBot, -7.0),                                               // 过了凳子前沿，布在两腿之间往下垂一点
    onThigh(hemBot + 0.03, -6.0), onThigh(0.735, -3.3), onThigh(0.785, 0.4), onThigh(0.82, 3.5), onThigh(hemTop, 4.9), onThigh(hemTop - 0.012, 5.4),   // 裙摆斜着绕过大腿
    onThigh(0.7, 5.7), onThigh(0.5, 6.1), onThigh(0.32, 6.5),                                                                       // 盖在大腿面上
    along(10.4, 6.9), along(14.5, 7.1), along(19.5, 6.7), along(25, 6.1), along(29.5, 5.2), along(32.6, 3.5), along(34.4, 1.8),      // 小肚子、胸口
  ];
  part('dress', dress, { fill: C.dress, R: 3.4, flat: 0.5, mat: 3, extra: 0.3, shadow: [0.3, -0.6, 0.9, 0.4],
    detail: (c) => {
      for (let i = -8; i < 14; i++) for (let j = -3; j < 16; j++) {
        const q = add(hip, [i * 3.3 + (j % 2) * 1.65, j * 3.3]);
        const m = map(q); c.fillStyle = 'rgba(251,230,162,0.6)'; c.beginPath(); c.arc(m[0], m[1], 0.4 * s, 0, 6.283); c.fill();
      }
      strokeL(c, [along(15.2, -5.7), along(15.6, 0.5), along(15.0, 7.0)], 0.2, 'rgba(160,96,20,0.4)');                                 // 腰线（裙子在这里收拢）
      for (const k of [0.3, 0.5]) strokeL(c, [along(14, k * 9 - 1), onThigh(k, 3.0), onThigh(k + 0.22, -1.5)], 0.12, 'rgba(160,96,20,0.22)');   // 裙子在腿上拉出的褶
      strokeL(c, [onThigh(hemTop - 0.012, 4.8), onThigh(0.82 - 0.012, 3.4), onThigh(0.785 - 0.012, 0.4), onThigh(0.735 - 0.012, -3.3), onThigh(hemBot + 0.02, -6.0)], 0.3, 'rgba(160,96,20,0.4)');   // 裙摆的折边
    } });
  // 白色小圆领：圆圆的领片搭在胸口前，从侧面看得见
  part('collar', [along(34.7, -3.1), along(35.8, -1.0), along(35.7, 1.6), along(34.9, 3.5), along(33.4, 5.6), along(31.4, 6.5), along(29.6, 6.2), along(28.9, 4.8),
    along(29.6, 3.0), along(31.3, 1.0), along(32.4, -1.8), along(33.3, -3.2)],
    { fill: C.collar, R: 1.4, flat: 0.4, mat: 3, extra: 0.4, shadow: [-0.2, -0.3, 0.4, 0.25],
      detail: (c) => { strokeL(c, [along(34.7, 3.3), along(33.2, 5.3), along(31.4, 6.1), along(29.8, 5.8)], 0.1, 'rgba(150,140,120,0.5)'); } });
  // ---------------- 脖子、头
  part('neck', tubeL([H([0.6, -4.6]), lerp(H([0.6, -4.6]), neck0, 0.5), add(neck0, [-0.2, -1.8])], [3.7, 3.6, 4.0]), { fill: C.skinDeep, R: 2.6, flat: 0.4, mat: 1 });
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
      const op = 1 - blink, wo = (pose.wow ?? 0) * op;               // wow：看呆了，眼睛睁大、眉毛抬起
      const eyeShape = [[4.55, 0.85], [5.3, 1.75 * op + 0.8 * (1 - op) + 0.2 * wo], [6.55, 2.05 * op + 0.85 * (1 - op) + 0.25 * wo], [7.45, 1.35 + 0.1 * wo], [6.95, 0.05 * op + 0.7 * (1 - op)], [5.6, -0.15 * op + 0.75 * (1 - op)]].map((p) => H(p));
      if (op > 0.15) {
        fillL(c, eyeShape, C.eyeW);
        c.save(); const ep = new Path2D(); catmull(eyeShape, true, 6).map(map).forEach(([x, y], i) => (i ? ep.lineTo(x, y) : ep.moveTo(x, y))); ep.closePath(); c.clip(ep);
        fillL(c, ellipse(...H([6.55, 0.95]), 0.95, 1.25, hr), C.iris);
        fillL(c, ellipse(...H([6.75, 1.0]), 0.5, 0.75, hr), C.pupil);
        c.restore();
      }
      // 上眼皮的线和睫毛
      strokeL(c, [H([4.35, 0.95]), H([5.3, 1.85 * op + 0.85 * (1 - op) + 0.2 * wo]), H([6.6, 2.15 * op + 0.9 * (1 - op) + 0.25 * wo]), H([7.55, 1.5 + 0.1 * wo])], 0.34, '#2a1612');
      if (op > 0.45) {   // 睁着：眼尾两根短睫毛（孩子，不画成化了妆的长睫毛）
        strokeL(c, [H([7.25, 1.75 + 0.1 * wo]), H([7.75, 2.2 + 0.1 * wo])], 0.13, '#2a1612');
        strokeL(c, [H([6.85, 2.05 + 0.2 * wo]), H([7.2, 2.55 + 0.2 * wo])], 0.12, '#2a1612');
      } else {           // 闭着：眼皮合成一道往下弯的线，睫毛顺着往下
        strokeL(c, [H([7.3, 1.0]), H([7.9, 0.6]), H([8.2, 0.55])], 0.15, '#2a1612');
        strokeL(c, [H([6.7, 0.85]), H([7.1, 0.35]), H([7.4, 0.25])], 0.14, '#2a1612');
      }
      strokeL(c, [H([5.7, -0.2]), H([6.9, -0.05])], 0.08, 'rgba(120,60,50,0.4)');          // 下眼皮
      strokeL(c, [H([5.0, 3.55 + 0.3 * wo]), H([6.2, 3.95 + 0.45 * wo]), H([7.4, 3.85 + 0.4 * wo])], 0.28, '#3a2419');          // 眉毛
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
  // 近侧的辫子：扎在耳朵后面低处，一小把，发梢分成两三绺（重力方向是竖直的，不跟头转）
  const tie = H([-7.4, -3.6]);
  const pig = [tie, add(tie, rot([-2.6, -3.6], sw * 0.5)), add(tie, rot([-3.3, -7.8], sw)), add(tie, rot([-2.6, -11.6], sw * 1.2))];
  part('pig', tubeL(pig, [2.5, 2.9, 2.2, 0.5]), { fill: C.hair, R: 1.9, mat: 2, extra: 0.9, shadow: [0.3, -0.4, 0.6, 0.4],
    detail: (c) => { for (let i = -1; i <= 1; i++) strokeL(c, pig.map((p, k) => add(p, [i * 0.7 * (1 - k / 4), 0])), 0.1, 'rgba(90,62,50,0.55)'); } });
  part('pigTip', tubeL([pig[2], add(pig[2], rot([0.6, -2.6], sw)), add(pig[2], rot([1.4, -4.0], sw))], [1.0, 0.7, 0.15]), { fill: C.hair, R: 1.0, mat: 2, extra: 0.9 });
  part('tie1', ellipse(...add(tie, [0.3, 0.7]), 1.35, 1.3), { fill: C.tie, R: 1.2, mat: 3, extra: 0.6, shadow: [-0.2, -0.3, 0.4, 0.4] });
  part('tie2', ellipse(...add(tie, [-0.9, -0.5]), 1.3, 1.25), { fill: C.tie, R: 1.1, mat: 3, extra: 0.6 });
  // ---------------- 近侧的胳膊：一笔外轮廓；上臂差不多垂着、稍往前，前臂顺着大腿往前搭到膝盖上
  const ud = norm(sub(elbow, shoulder)), un = [-ud[1], ud[0]];
  const armOut = limbOutline(add(shoulder, mul(ud, -1.2)), elbow, add(wrist, mul(norm(sub(wrist, elbow)), 1.6)),
    [[0, 3.2], [0.4, 3.0], [0.85, 2.5], [1, 2.4]],                // 上臂前面
    [[0, 3.3], [0.35, 3.1], [0.8, 2.6], [1, 2.35]],               // 上臂后面
    [[0, 2.45], [0.25, 2.7], [0.65, 2.1], [1, 1.5]],              // 前臂上面（手背那一侧）
    [[0, 2.35], [0.3, 2.6], [0.65, 2.0], [1, 1.5]], null);        // 前臂下面
  part('arm', armOut, { fill: C.skin, R: 1.9, flat: 0.5, mat: 1, group: 'armN', groupR: 1.9 * s, smooth: false, shadow: [-0.2, -0.4, 0.7, 0.22] });
  // ---------------- 手：一整块轮廓（手背拱过膝盖顶、手指垂在膝盖前），手指只用很淡的线分开，不画成一根根圆条
  const hA = handN.at;
  part('hand', handN.outline, { fill: C.skin, R: 1.9, flat: 0.5, mat: 1, group: 'armN', smooth: false, shadow: [-0.15, -0.35, 0.6, 0.3],
    detail: (c) => {
      strokeL(c, [hA(0.5, 1.95), hA(0.53, 2.12), hA(0.56, 1.9)], 0.06, 'rgba(176,104,84,0.25)');               // 指根关节的小鼓包
      fillL(c, [hA(0.955, 0.98), hA(0.985, 0.95), hA(0.99, 0.62), hA(0.96, 0.6)], 'rgba(248,214,200,0.55)');   // 中指指甲（侧面只看见一条）
    } });
  // 无名指、小指：各自一块，边上一道很淡的线，指尖下面一点接触阴影
  const fingerLine = (f) => (c) => {
    const o = f.outline, n = (o.length - 7) / 2;
    strokeL(c, o.slice(Math.round(n * 0.42), Math.round(n) + 9), 0.07, 'rgba(170,98,80,0.45)', false);
  };
  part('ring', ringN.outline, { fill: C.skin, R: 0.7, flat: 0.9, mat: 1, smooth: false, shadow: [-0.08, -0.12, 0.35, 0.18], detail: fingerLine(ringN) });
  part('pinky', pinkyN.outline, { fill: C.skin, R: 0.6, flat: 0.9, mat: 1, smooth: false, shadow: [-0.08, -0.12, 0.35, 0.18], detail: fingerLine(pinkyN) });
  // 泡泡袖：布鼓起来包住肩和上臂上端，袖口收一圈（软的布，不是硬壳）
  const A = (u, v) => add(shoulder, add(mul(ud, u), mul(un, v)));
  const sl = [A(-3.0, 2.1), A(-0.9, 3.2), A(2.2, 3.55), A(4.5, 3.45), A(5.9, 3.25), A(6.5, 3.15), A(6.8, 1.0), A(6.9, -1.2), A(6.5, -3.25),
    A(5.8, -3.35), A(4.2, -3.75), A(1.6, -3.9), A(-1.1, -3.4), A(-3.0, -2.4), A(-3.7, 0)];
  part('sleeve', sl, { fill: C.dress, R: 2.8, flat: 0.55, mat: 3, extra: 0.3, shadow: [-0.25, -0.35, 0.5, 0.25],
    detail: (c) => {
      strokeL(c, [A(5.9, -3.2), A(6.15, 0), A(5.9, 3.1)], 0.3, 'rgba(160,96,20,0.3)');      // 袖口收的那圈
      for (let i = 0; i < 3; i++) strokeL(c, [A(0.6 + i * 1.5, -3.2), A(1.3 + i * 1.5, 0), A(1.0 + i * 1.5, 3.2)], 0.1, 'rgba(160,96,20,0.18)');
      for (let i = -3; i < 6; i++) for (let j = -2; j < 3; j++) { const m = map(A(i * 1.6 + (j % 2) * 0.8, j * 1.6)); c.fillStyle = 'rgba(251,230,162,0.6)'; c.beginPath(); c.arc(m[0], m[1], 0.4 * s, 0, 6.283); c.fill(); }
    } });
  P.joints = { hip, knee, ankle, kneeF, ankleF, neck0, head, shoulder, elbow, wrist, chest: along(22, 0.5), belly: along(11, 0.5), lean };
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
  return [[[a[0] + 3.9, a[1] - 1.3], [a[0] + 6.3, a[1] - 2.6], [a[0] + 7.4, a[1] - 5.6], [a[0] + 5.0, a[1] - 5.6]],
    [[a[0] - 2.8, a[1] + 1.6], [a[0] + 1.4, a[1] + 1.4], [a[0] + 1.6, a[1] + 0.2], [a[0] - 3.2, a[1] + 0.3]]];
}
export const COLORS = C;
