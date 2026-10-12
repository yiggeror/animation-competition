// 小满（9 岁）：坐在小板凳上抱着膝盖，抬头看床单上的鹤。侧面（脸朝右）。
// 局部坐标：厘米，x 朝她面朝的方向，y 朝上，原点在板凳面的中心；地面 y = -22。
// 每个部件是一块平滑的形状；颜色是固有色，明暗全部交给场景里的光去算（cards.js 由轮廓算法线）。
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
  const lean = pose.lean ?? 0.36, headUp = pose.headUp ?? 0.34;
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

  // ---------------- 骨架
  const hip = [0, 8];
  const ankle = [25, -16.0], ankleF = [28.0, -16.1];
  const leg = ik(hip, ankle, 27, 24.5, 1);          // 膝盖往上拱
  const knee = leg.joint;
  const legF = ik(add(hip, [1.0, 0.5]), ankleF, 27, 24.5, 1), kneeF = legF.joint;
  const up = rot([0, 1], -lean);                  // 身体轴（往前倾 = 往 +x 歪）
  const along = (d, side = 0) => add(add(hip, [up[0] * d, up[1] * d]), [up[1] * side, -up[0] * side]);
  const neck0 = along(33, 1.0), shoulder = along(28.5, -0.8);
  const head = add(neck0, rot([2.0, 6.3], -lean * 0.3));
  const hr = headUp - lean * 0.15;               // 头相对竖直方向的转角（抬头为正）
  const HS = 1.1;
  const H = (p) => add(head, rot([p[0] * HS, p[1] * HS], hr));        // 头的局部坐标 → 身体坐标
  // 两只手在下巴底下握在一起（看得入迷、有点激动）
  const handT = pose.hands === 'knee' ? add(knee, [-6.5, 2.2]) : H([2.6, -12.8]);
  const arm = ik(shoulder, handT, 15.5, 13.5, -1);
  const elbow = arm.joint, wrist = arm.end;

  // ---------------- 后面的辫子（远侧，大部分被头挡住）
  const tieF = H([-6.6, -2.2]);
  part('pigFar', tubeL([tieF, add(tieF, [-3.4, -5.5]), add(tieF, [-3.0, -11.5]), add(tieF, [-1.6, -15.5])], [2.0, 2.1, 1.5, 0.2]),
    { fill: C.hair, R: 1.6, mat: 2, extra: 0.8 });
  // ---------------- 板凳
  part('stoolLegB', [[-11, -2], [-8.5, -2], [-10.2, -22], [-12.8, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolLegF', [[8.5, -2], [11, -2], [12.8, -22], [10.2, -22]], { fill: C.stoolDark, R: 1.0, smooth: false });
  part('stoolRung', [[-11.2, -13], [11.4, -13], [11.6, -15], [-11.4, -15]], { fill: C.stoolDark, R: 0.8, smooth: false });
  part('stoolSeat', [[-14, 0.5], [14, 0.5], [14, -3], [-14, -3]], { fill: C.stool, R: 1.4, smooth: false,
    detail: (c) => { strokeL(c, [[-13, -1.2], [13, -1.0]], 0.12, 'rgba(60,35,20,0.5)'); } });
  // ---------------- 远侧的腿（稍微露出一点脚）
  part('shinF', tubeL([kneeF, lerp(kneeF, ankleF, 0.3), lerp(kneeF, ankleF, 0.65), ankleF], [3.8, 4.0, 3.0, 2.2]), { fill: C.skinDeep, R: 1.6, flat: 0.5, mat: 1 });
  part('footF', footPts(ankleF), { fill: C.skinDeep, R: 1.6, mat: 1 });
  part('sandalF', sandalPts(ankleF), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankleF).forEach((q, i) => part('strapF' + i, q, { fill: '#9e2522', R: 0.8, smooth: false }));
  // ---------------- 身体 + 裙子
  const waistB = along(11.5, -6.2), waistF = along(11.5, 5.2), chest = along(21.5, 6.4), backU = along(24.5, -5.8);
  const collarF = along(31.2, 3.6), collarB = along(31.6, -3.9);
  // 大腿（在裙子底下，决定膝盖的形）
  part('thigh', tubeL([add(hip, [-2, 0]), lerp(hip, knee, 0.5), knee], [6.0, 5.4, 4.6]), { fill: C.skin, R: 3.5, mat: 1 });
  const thighDir = [(knee[0] - hip[0]) / 27, (knee[1] - hip[1]) / 27], thN = [-thighDir[1], thighDir[0]];
  const onThigh = (t, o) => add(lerp(hip, knee, t), [thN[0] * o, thN[1] * o]);
  const dress = [
    collarB, backU, waistB, add(hip, [-7.8, -2.5]), add(hip, [-6.5, -7.6]),             // 后背 → 坐着的臀部（裙子搭在凳面上）
    [3, -0.4], onThigh(0.5, -5.6), onThigh(0.9, -5.2),                                    // 大腿底下
    add(knee, [2.8, -4.2]), add(knee, [4.8, -2.6]), add(knee, [5.0, 0.6]),                // 裙摆盖过膝盖
    onThigh(0.9, 5.4), onThigh(0.55, 6.2), onThigh(0.2, 6.8), waistF,                     // 大腿上面（腿面）
    chest, collarF,
  ];
  part('dress', dress, { fill: C.dress, R: 3.2, flat: 0.4, mat: 3, extra: 0.3, shadow: [-0.3, -0.4, 0.7, 0.35],
    detail: (c) => {
      for (let i = -8; i < 12; i++) for (let j = -3; j < 12; j++) {
        const q = add(add(hip, [i * 3.3 + (j % 2) * 1.65, j * 3.3]), [0, 0]);
        const m = map(q); c.fillStyle = 'rgba(251,230,162,0.6)'; c.beginPath(); c.arc(m[0], m[1], 0.4 * s, 0, 6.283); c.fill();
      }
      // 腰线、腿面上的褶
      strokeL(c, [along(12, -6.0), along(12.7, 0), along(12, 5.4)], 0.22, 'rgba(160,96,20,0.45)');
      strokeL(c, [onThigh(0.35, 3), onThigh(0.75, 1.5), add(knee, [3.0, -2.5])], 0.16, 'rgba(160,96,20,0.3)');
      strokeL(c, [add(hip, [-5, -6]), onThigh(0.45, -4.5)], 0.14, 'rgba(160,96,20,0.3)');
    } });
  // 白色小圆领
  part('collar', [collarB, along(34.4, -2.0), along(34.6, 2.4), add(collarF, [1.3, 0.4]), add(along(29.2, 4.2), [0.6, 0]), along(29.7, 0.6), along(30.2, -2.9)],
    { fill: C.collar, R: 1.4, mat: 3, extra: 0.4, shadow: [-0.3, -0.4, 0.5, 0.35] });
  // ---------------- 近侧的腿：小腿、脚、红凉鞋
  part('shin', tubeL([add(knee, [-0.3, 0.6]), lerp(knee, ankle, 0.3), lerp(knee, ankle, 0.65), ankle], [[4.0, 4.0], [3.4, 4.9], [2.9, 3.4], [2.2, 2.4]]), { fill: C.skin, R: 1.8, flat: 0.5, mat: 1, shadow: [-0.4, -0.5, 0.6, 0.3] });
  part('foot', footPts(ankle), { fill: C.skin, R: 1.8, mat: 1 });
  part('sandal', sandalPts(ankle), { fill: C.sole, R: 0.8, smooth: false });
  strapPts(ankle).forEach((q, i) => part('strap' + i, q, { fill: C.sandal, R: 0.8, smooth: false, shadow: [-0.1, -0.2, 0.3, 0.35] }));
  // ---------------- 脖子、头
  part('neck', tubeL([H([0.8, -5.0]), lerp(H([0.8, -5.0]), neck0, 0.5), add(neck0, [0, -2.0])], [3.0, 2.9, 3.3]), { fill: C.skinDeep, R: 2.6, mat: 1 });
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
      strokeL(c, [H([7.2, 1.85]), H([7.85, 2.5]), H([8.25, 2.6])], 0.16, '#2a1612');
      strokeL(c, [H([6.7, 2.1]), H([7.15, 2.85]), H([7.5, 3.05])], 0.15, '#2a1612');
      strokeL(c, [H([6.1, 2.1]), H([6.4, 2.75])], 0.13, '#2a1612');
      strokeL(c, [H([5.7, -0.2]), H([6.9, -0.05])], 0.08, 'rgba(120,60,50,0.4)');          // 下眼皮
      strokeL(c, [H([5.0, 3.55]), H([6.2, 3.95]), H([7.4, 3.85])], 0.28, '#3a2419');          // 眉毛
    } });
  // 眼睛里的高光：映着床单（单独一块，材质 4）
  if (1 - blink > 0.4) {
    part('glint', ellipse(...H([6.95, 1.45]), 0.36, 0.42, hr, 12), { fill: '#ffffff', R: 0.4, mat: 4 });
    part('glint2', ellipse(...H([6.25, 0.45]), 0.16, 0.16, 0, 8), { fill: '#ffffff', R: 0.2, mat: 4 });
  }
  // 耳朵
  const ear = [[0.5, 1.6], [-0.9, 2.4], [-2.4, 1.4], [-2.7, -1.2], [-1.9, -3.4], [-0.6, -4.2], [0.3, -3.6], [0.0, -2.2], [0.5, -0.2]].map(([x, y]) => [x * 0.66 - 0.6, y * 0.66 + 0.1]);
  part('ear', ear.map(H), { fill: '#eab597', R: 0.9, flat: 0.4, mat: 1, extra: 0.3,
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
  const tie = H([-7.6, -3.6]), sw = pose.pig ?? 0;
  const pig = [tie, add(tie, rot([-3.0, -5.0], sw * 0.5)), add(tie, rot([-3.8, -10.5], sw)), add(tie, rot([-2.8, -16.0], sw * 1.2))];
  part('pig', tubeL(pig, [2.4, 2.6, 1.9, 0.3]), { fill: C.hair, R: 1.8, mat: 2, extra: 0.9, shadow: [0.3, -0.4, 0.6, 0.45],
    detail: (c) => { for (let i = -1; i <= 1; i++) strokeL(c, pig.map((p, k) => add(p, [i * 0.6 * (1 - k / 4), 0])), 0.1, 'rgba(90,62,50,0.55)'); } });
  part('tie1', ellipse(...add(tie, [0.3, 0.7]), 1.25, 1.2), { fill: C.tie, R: 1.1, mat: 3, extra: 0.6, shadow: [-0.2, -0.3, 0.4, 0.4] });
  part('tie2', ellipse(...add(tie, [-0.8, -0.6]), 1.2, 1.15), { fill: C.tie, R: 1.1, mat: 3, extra: 0.6 });
  // ---------------- 近侧的胳膊：泡泡袖、上臂、前臂抱着小腿、手
  part('arm', tubeL([shoulder, lerp(shoulder, elbow, 0.5), elbow, lerp(elbow, wrist, 0.5), wrist], [2.9, 2.7, 2.3, 2.2, 1.9]), { fill: C.skin, R: 1.4, flat: 0.6, mat: 1, shadow: [-0.3, -0.4, 0.6, 0.25] });
  const ha = Math.atan2(wrist[1] - elbow[1], wrist[0] - elbow[0]);
  // 握在一起的两只手：近处的手背和弯着的四根手指，远处那只手的指尖从下面露出来
  const HW = (p) => add(wrist, rot(p, ha));
  part('handFar', [[1.6, -2.0], [5.2, -2.8], [7.8, -1.6], [7.6, 0.4], [4.4, 0.2], [1.6, 0.0]].map(HW), { fill: C.skinDeep, R: 1.0, flat: 0.4, mat: 1 });
  part('hand', [[-0.4, 1.7], [3.4, 2.5], [6.0, 2.1], [7.4, 1.0], [7.5, -0.6], [6.8, -1.9], [4.6, -2.4], [2.0, -2.1], [-0.2, -1.6]].map(HW), { fill: C.skin, R: 1.4, flat: 0.4, mat: 1, shadow: [-0.3, -0.4, 0.5, 0.35],
    detail: (c) => { strokeL(c, [HW([5.6, 2.0]), HW([6.6, 0.6]), HW([6.9, -1.0])], 0.12, 'rgba(170,100,80,0.55)'); for (let i = 0; i < 3; i++) strokeL(c, [HW([6.9 - i * 0.2, 0.9 - i * 0.9]), HW([7.45, 0.7 - i * 0.9])], 0.09, 'rgba(170,100,80,0.5)'); } });
  part('thumb', tubeL([HW([3.0, 2.0]), HW([4.8, 2.9]), HW([6.6, 3.1])], [0.95, 0.85, 0.7]), { fill: C.skin, R: 0.8, flat: 0.4, mat: 1, shadow: [-0.2, -0.3, 0.3, 0.3],
    detail: (c) => { strokeL(c, [HW([6.0, 3.3]), HW([6.6, 3.0])], 0.12, 'rgba(230,170,150,0.9)'); } });
  // 泡泡袖：肩头鼓起来的灯笼形，袖口收一道边
  const ua = Math.atan2(elbow[1] - shoulder[1], elbow[0] - shoulder[0]);
  const A = (u, v) => add(shoulder, rot([u, v], ua));
  const sl = [A(-3.2, -2.6), A(-1.0, -4.0), A(3.0, -4.5), A(6.4, -4.0), A(7.6, -2.8), A(7.8, 0), A(7.6, 2.8), A(6.4, 3.9), A(3.0, 4.4), A(-0.6, 3.9), A(-3.0, 2.8), A(-4.0, 0)];
  part('sleeve', sl, { fill: C.dress, R: 2.4, flat: 0.3, mat: 3, extra: 0.3, shadow: [-0.4, -0.5, 0.6, 0.4],
    detail: (c) => {
      strokeL(c, [A(6.6, -3.8), A(7.0, 0), A(6.6, 3.8)], 0.5, 'rgba(160,96,20,0.35)');
      for (let i = 0; i < 3; i++) strokeL(c, [A(0.5 + i * 1.6, -3.6), A(1.5 + i * 1.6, 0), A(1.0 + i * 1.6, 3.5)], 0.12, 'rgba(160,96,20,0.25)');
    } });
  P.joints = { hip, knee, ankle, kneeF, ankleF, neck0, head, shoulder, elbow, wrist, chest: along(20, 1), belly: along(10, 0) };
  return P;
}

function footPts(a) {
  // 脚：脚跟圆、脚背往前斜下去、脚趾圆头，长约 16 厘米
  return [[a[0] - 2.6, a[1] + 2.6], [a[0] + 1.6, a[1] + 2.2], [a[0] + 5.0, a[1] - 1.2], [a[0] + 9.5, a[1] - 3.4], [a[0] + 12.4, a[1] - 4.3],
    [a[0] + 13.4, a[1] - 5.2], [a[0] + 13.0, a[1] - 5.9], [a[0] - 2.4, a[1] - 5.9], [a[0] - 3.6, a[1] - 4.6], [a[0] - 3.5, a[1] - 1.0]];
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
