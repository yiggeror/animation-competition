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
  // 抬头角 hr；前臂角 phi 取使脖子长度最接近 6.5 厘米的那个
  const hr = pose.headUp ?? 0.30;
  const chinL = [6.3, -7.7];
  let best = null;
  for (let phi = 0.9; phi <= 2.1; phi += 0.004) {
    const w = add(elbow, mul(dir(phi), 16.5)), top = add(w, mul(dir(phi), 6.6));
    const hc = sub(top, rot(mul(chinL, HS), hr));
    const nb = add(hc, rot(mul([0.6, -5.2], HS), hr));
    const e = Math.abs(Math.hypot(nb[0] - neck0[0], nb[1] - neck0[1]) - 6.5);
    if (!best || e < best.e) best = { e, phi, w, hc };
  }
  const phi = best.phi, wrist = best.w, head = best.hc;
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
  // ---------------- 远侧的腿和胳膊（在暗处，颜色深一点；大半被近侧挡住）
  const legShape = (k, a, grp, fill, extraShadow) => {
    const kd = norm(sub(k, hip));
    part(grp + 'Thigh', tubeL([add(hip, mul(kd, -2)), lerp(hip, k, 0.5), add(k, mul(kd, 0.6))], [[5.6, 5.8], [5.0, 5.4], [4.3, 4.4]]), { fill, R: 2.2, flat: 0.4, mat: 1, group: grp, groupR: 2.2 * s });
    // 小腿：前面（胫骨）直，后面（小腿肚）鼓
    part(grp + 'Shin', tubeL([add(k, [0, 0.4]), lerp(k, a, 0.32), lerp(k, a, 0.7), a], [[4.0, 4.2], [3.3, 4.9], [2.7, 3.2], [2.1, 2.3]]), { fill, R: 2.2, flat: 0.4, mat: 1, group: grp });
    part(grp + 'Foot', footPts(a), { fill, R: 2.2, flat: 0.4, mat: 1, group: grp });
  };
  legShape(kneeF, ankleF, 'legF', C.skinDeep);
  part('sandalF', sandalPts(ankleF), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankleF).forEach((q, i) => part('strapF' + i, q, { fill: '#9e2522', R: 0.8, smooth: false }));
  // 远侧的拳头：在近侧拳头后面、略靠前，只露出指节
  const fd = dir(phi), fp = [-fd[1], fd[0]];
  const FW = (base, u, v) => add(base, add(mul(fd, u), mul(fp, v)));
  const wristF = add(wrist, add(mul(fd, 0.6), mul(fp, -1.6)));
  part('armF', tubeL([add(elbow, [1.4, 0.4]), lerp(add(elbow, [1.4, 0.4]), wristF, 0.5), wristF], [2.2, 2.0, 1.6]), { fill: C.skinDeep, R: 1.8, flat: 0.4, mat: 1, group: 'armF', groupR: 1.8 * s });
  part('fistF', fistPts().map(([u, v]) => FW(wristF, u, v)), { fill: C.skinDeep, R: 1.8, flat: 0.4, mat: 1, group: 'armF' });
  // ---------------- 近侧的腿：大腿（大半在裙子里）、膝盖、小腿、脚——一个组，膝盖和脚踝是连着的肉
  legShape(knee, ankle, 'legN', C.skin);
  part('sandal', sandalPts(ankle), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankle).forEach((q, i) => part('strap' + i, q, { fill: C.sandal, R: 0.8, smooth: false, shadow: [-0.1, -0.2, 0.3, 0.3] }));
  // ---------------- 身体 + 裙子：后背微微拱起（身子前倾）；裙子盖住大腿到膝盖上面一点
  const hemT = 0.8;
  const dress = [
    along(33.6, -3.4), along(29.5, -6.0), along(22, -7.0), along(14, -6.8), along(6, -6.6),       // 后背
    [-7.6, 3.0], [-7.4, -0.6], [-2, -0.9],                                                            // 坐在凳面上的臀部
    onThigh(0.45, -5.9), onThigh(hemT, -5.4), onThigh(hemT + 0.03, -2.0),                             // 大腿底下 → 裙摆
    onThigh(hemT + 0.04, 3.0), onThigh(hemT, 6.0), onThigh(0.5, 6.6), onThigh(0.2, 7.2),               // 裙摆 → 腿面
    along(10, 6.2), along(18, 6.6), along(25, 5.8), along(30.8, 3.4),                                  // 肚子、胸口
  ];
  part('dress', dress, { fill: C.dress, R: 3.0, flat: 0.4, mat: 3, extra: 0.3, shadow: [-0.2, -0.3, 0.5, 0.3],
    detail: (c) => {
      for (let i = -8; i < 14; i++) for (let j = -3; j < 14; j++) {
        const q = add(hip, [i * 3.3 + (j % 2) * 1.65, j * 3.3]);
        const m = map(q); c.fillStyle = 'rgba(251,230,162,0.6)'; c.beginPath(); c.arc(m[0], m[1], 0.4 * s, 0, 6.283); c.fill();
      }
      // 腰线（前倾时腰在肚子那里折一下）、腿面上布料被拉出的褶、裙摆的一道边
      strokeL(c, [along(12, -6.6), along(12.4, 0), along(11.5, 6.0)], 0.22, 'rgba(160,96,20,0.45)');
      strokeL(c, [onThigh(0.25, 4.5), onThigh(0.55, 3.6), onThigh(hemT - 0.02, 2.0)], 0.15, 'rgba(160,96,20,0.3)');
      strokeL(c, [onThigh(0.3, 2.2), onThigh(0.62, 0.8)], 0.12, 'rgba(160,96,20,0.25)');
      strokeL(c, [onThigh(hemT - 0.01, 5.6), onThigh(hemT + 0.02, 1), onThigh(hemT - 0.01, -5.0)], 0.3, 'rgba(160,96,20,0.35)');
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
  // ---------------- 近侧的胳膊：上臂（三角肌那里厚、往肘收）→ 肘尖 → 前臂（靠肘处肌肉鼓、往手腕收细）→ 拳头托着下巴
  // 一个组：手肘、手腕连着，不出接缝
  const ud = norm(sub(elbow, shoulder)), un = [-ud[1], ud[0]];
  part('upperArm', tubeL([add(shoulder, mul(ud, -1.0)), lerp(shoulder, elbow, 0.35), lerp(shoulder, elbow, 0.75), add(elbow, mul(ud, 0.6))], [[3.3, 3.2], [3.1, 3.1], [2.7, 2.7], [2.4, 2.4]]),
    { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN', groupR: 1.9 * s, shadow: [-0.3, -0.4, 0.6, 0.25] });
  part('elbowPt', ellipse(...add(elbow, add(mul(ud, 0.3), mul(un, -0.6))), 2.3, 2.1, Math.atan2(ud[1], ud[0])), { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN' });
  part('forearm', tubeL([add(elbow, mul(fd, -0.8)), add(elbow, mul(fd, 3.5)), lerp(elbow, wrist, 0.6), wrist], [[2.5, 2.5], [2.8, 2.7], [2.25, 2.25], [1.95, 1.95]]),
    { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN' });
  const NW = (u, v) => FW(wrist, u, v);
  part('fist', fistPts().map(([u, v]) => NW(u, v)), { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN',
    detail: (c) => {
      // 弯着的四根手指：指节之间的缝，第二节指节的小窝
      for (let i = 0; i < 3; i++) strokeL(c, [NW(5.0 + i * 0.75, -0.6), NW(5.6 + i * 0.75, -2.1)], 0.09, 'rgba(176,104,84,0.5)');
      strokeL(c, [NW(6.9, 1.6), NW(7.5, 0.2), NW(7.2, -1.6)], 0.1, 'rgba(176,104,84,0.45)');
      strokeL(c, [NW(1.2, 1.8), NW(3.2, 2.2)], 0.08, 'rgba(176,104,84,0.3)');
    } });
  // 大拇指：压在食指外侧，指甲朝外
  // 大拇指压在食指外侧：和拳头是一块肉（同一组），只用一道浅浅的折痕和指甲把它勾出来
  part('thumb', tubeL([NW(2.6, -2.0), NW(4.4, -2.5), NW(5.8, -2.3)], [0.95, 0.85, 0.7]), { fill: C.skin, R: 1.9, flat: 0.4, mat: 1, group: 'armN',
    detail: (c) => { strokeL(c, [NW(2.8, -1.2), NW(4.4, -1.6), NW(5.6, -1.5)], 0.1, 'rgba(176,104,84,0.45)'); fillL(c, [NW(5.0, -2.55), NW(5.8, -2.6), NW(5.85, -2.05), NW(5.05, -1.95)], 'rgba(244,206,192,0.9)'); } });
  // 泡泡袖：肩头鼓起来的灯笼形，袖口收一道边（盖住上臂上面一小半）
  const A = (u, v) => add(shoulder, add(mul(ud, u), mul(un, v)));
  const sl = [A(-3.0, 2.3), A(-1.0, 3.5), A(2.4, 3.9), A(5.2, 3.5), A(6.3, 2.5), A(6.5, 0), A(6.3, -2.5), A(5.2, -3.4), A(2.4, -3.8), A(-0.7, -3.4), A(-2.8, -2.5), A(-3.7, 0)];
  part('sleeve', sl, { fill: C.dress, R: 2.4, flat: 0.3, mat: 3, extra: 0.3, shadow: [-0.3, -0.4, 0.5, 0.35],
    detail: (c) => {
      strokeL(c, [A(5.5, -3.2), A(5.9, 0), A(5.5, 3.2)], 0.45, 'rgba(160,96,20,0.35)');
      for (let i = 0; i < 3; i++) strokeL(c, [A(0.4 + i * 1.4, -3.0), A(1.2 + i * 1.4, 0), A(0.9 + i * 1.4, 3.0)], 0.12, 'rgba(160,96,20,0.25)');
    } });
  P.joints = { hip, knee, ankle, kneeF, ankleF, neck0, head, shoulder, elbow, wrist, chest: along(20, 1), belly: along(10, 0), lean, phi };
  return P;
}

// 拳头（手腕局部坐标：u 沿前臂往上，v 往她身后为正）：手背、弯着的四指、指节顶着下巴
function fistPts() {
  return [[-1.2, 1.95], [1.0, 2.15], [3.2, 2.55], [5.0, 2.7], [6.7, 2.3], [7.6, 1.0], [7.7, -0.6], [7.0, -2.0], [5.4, -2.7], [3.2, -2.55], [1.0, -2.1], [-1.2, -1.95]];
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
