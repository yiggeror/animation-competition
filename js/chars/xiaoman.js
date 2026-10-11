// 小满：9 岁的小孙女。双马尾 + 红色小绒球、齐刘海、头顶一撮呆毛、圆脸大眼，黄色 A 字连衣裙配白色圆领，红色塑料凉鞋。
// 身体坐标：厘米，原点在两脚中间的地面，+y 向下。视角：front 正面、side 侧面（面朝 +x）、back 背面。
// 姿势是一组语义控制量（前倾、耸肩、转头、歪头……）加上手、脚的目标位置；每一帧按控制量重新生成轮廓。
import { Figure, tube, M } from '../lib/figure.js';
import { ik2, lerpP, rotP, ellipsePts, curScale } from '../lib/draw.js';
import { clamp, lerp } from '../lib/core.js';
import { eye, brow, mouth, blush, faceOf } from './face.js';
import { hand } from './hand.js';

export const XM = {
  name: '小满',
  skin: '#f8dac2', skinShade: '#ecbb9e', blush: '242,132,120',
  hair: '#2d2321', hairHi: '#4b3b35',
  dress: '#f3c444', dressShade: '#dca52f', dressDot: '#fff6dc',
  collar: '#fffaf0', collarShade: '#eadfca',
  bobble: '#e2483d',
  sandal: '#e2574a',
  iris: '#2b1d18', mouthIn: '#8e3b33', tongue: '#e88b7d',
  ink: '#3b2c25',
  // 比例（厘米）。头大、腿短一点，更像小孩，也方便看清表情
  faceC: [0, -97],      // 脸的中心
  nl: -82.2,            // 领口
  shoulder: [11.2, -77.6],
  upper: 12.4, fore: 11.2, palm: 4.4,
  hipY: -43.5, hipX: 4.9, thigh: 20.2, shin: 19.6,
  hem: -38.5,
};

export const POSE0 = {
  x: 0, y: 0, s: 1,
  lean: 0, bob: 0, breath: 0, shrug: 0,
  head: { tilt: 0, turn: 0, nod: 0 },
  face: {},
  armL: null, armR: null, // { hand:[x,y] 身体坐标, hp:'relax', bend:±1, rot:手的额外转角, z }
  legL: null, legR: null, // { foot:[x,y], knee:[x,y] }
  pig: [0, 0],            // 双马尾的摆角（跟随动作，弧度）
  cowlick: 0,             // 呆毛的摆
  dress: 0,               // 裙摆摆动
};
export function pose(o = {}) { return { ...POSE0, ...o, head: { ...POSE0.head, ...(o.head || {}) } }; }

function inkFor(ctx) { return clamp(curScale(ctx) * 0.4, 1.5, 5.0); }

// 马尾：局部坐标里沿 +x 伸出的一束头发，末端分成两绺
function pigtailPts(len, w) {
  const k = len / 13;
  return [[0, -w * 0.62], [3.5 * k, -w * 0.95], [8.5 * k, -w], [11.6 * k, -w * 0.62], [13.2 * k, -w * 0.12], [11.9 * k, w * 0.08], [12.9 * k, w * 0.5], [10.8 * k, w * 0.92], [6 * k, w * 0.98], [2.4 * k, w * 0.8], [0, w * 0.6]];
}

// ================================================================== 正面
export function front(ctx, P0, o = {}) {
  const P = pose(P0), D = XM;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 3, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const hipC = [0, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);   // 上半身的点：跟着前倾转
  const sh = P.shrug * 2.2, br = P.breath;
  const nl = D.nl;
  const N = up([0, nl - 1.2 - sh * 0.3]);
  const turn = clamp(P.head.turn, -1, 1), nod = P.head.nod;
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt), M.t(0, D.faceC[1] - (nl - 1.2)));
  const H = (p) => M.ap(HM, p);
  const Hs = (pts) => pts.map(H);

  // ---- 腿（裙子下面）和凉鞋
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const leg = P['leg' + side] || {};
    const hip = [sg * D.hipX, D.hipY + P.bob];
    const foot = leg.foot || [sg * 5.4, -4.0];
    // 正面看，膝盖弯曲是朝镜头的（看起来只是腿变短），所以膝盖放在中点，只按弯曲程度往外偏一点
    const bentK = clamp(1 - Math.hypot(foot[0] - hip[0], foot[1] - hip[1]) / (D.thigh + D.shin));
    const knee = leg.knee || [lerp(hip[0], foot[0], 0.5) + sg * bentK * 9, lerp(hip[1], foot[1], D.thigh / (D.thigh + D.shin))];
    const t = tube([hip, lerpP(hip, knee, 0.5), knee, lerpP(knee, foot, 0.4), foot], [[0, 3.3], [0.45, 2.5], [0.55, 2.55], [0.72, 2.45], [1, 1.55]], { capStart: 'flat', capEnd: 'flat', step: 0.6 });
    fig.part('leg' + side, t.outline, { fill: D.skin, z: -4, per: 2 });
    const fx = foot[0] + sg * 0.5, fy = foot[1];
    fig.part('foot' + side, [[fx - 2.3, fy - 0.8], [fx - 2.7, fy + 2.2], [fx - 1.6, fy + 3.8], [fx + 1.6, fy + 3.9], [fx + 2.8, fy + 2.6], [fx + 2.4, fy - 0.6], [fx, fy - 1.5]], { fill: D.skin, z: -3.9 });
    fig.part('sole' + side, [[fx - 3.0, fy + 3.0], [fx - 2.7, fy + 4.4], [fx + 3.0, fy + 4.4], [fx + 3.2, fy + 3.0], [fx, fy + 3.5]], { fill: D.sandal, z: -3.8, inner: true });
    fig.detail([[fx - 2.6, fy + 1.0], [fx, fy + 0.5], [fx + 2.7, fy + 1.1]], { z: -3.7, lw: lw * 1.6, color: D.sandal, profile: 'flat', clip: ['foot' + side] });
  }

  // ---- 马尾、绒球、耳朵（在脸后面）
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const sw = P.pig[side === 'L' ? 0 : 1];
    const base = [sg * 13.2, -9.2];
    const ang = sg < 0 ? Math.PI - 0.72 - sw : 0.72 + sw;   // 向外、向下约 40°
    const T = M.chain(HM, M.t(base[0], base[1]), M.r(ang));
    const pts = pigtailPts(12.5, 3.6).map((p) => [p[0], p[1] * (sg < 0 ? -1 : 1)]);
    fig.part('pig' + side, M.apAll(T, pts), { fill: D.hair, z: 3.5, per: 4 });
    fig.detail(M.apAll(T, [[2.5, 0.4 * sg], [6.5, 0.9 * sg], [10.5, 0.5 * sg]]), { z: 3.6, lw: lw * 0.55, color: D.hairHi, clip: ['pig' + side] });
    fig.part('bob' + side, M.apAll(T, ellipsePts(0.6, 0, 2.15, 2.25, 16)), { fill: D.bobble, z: 7.4, inner: true });
    const ex = sg * (12.7 - (sg * turn > 0 ? turn * 1.2 : turn * 0.2 * sg));
    fig.part('ear' + side, Hs(ellipsePts(ex, 1.6, 2.0, 2.8, 18)), { fill: D.skin, z: 4.2 });
    fig.detail(Hs([[ex - sg * 0.2, 0.2], [ex + sg * 0.5, 1.6], [ex - sg * 0.1, 2.8]]), { z: 4.3, lw: lw * 0.5, color: D.skinShade, clip: ['ear' + side] });
  }

  // ---- 脖子
  fig.part('neck', [up([-3.0, nl - 4.5]), up([3.0, nl - 4.5]), up([3.3, nl + 1.2]), up([-3.3, nl + 1.2])], { fill: D.skin, z: 0.5 });

  // ---- 连衣裙（A 字，裙摆随 P.dress 摆）
  const hs = P.dress * 2.2, hem = D.hem;
  const bw = 1 + br * 0.025;
  const dressRel = [
    [-4.6, 0], [-9.3, 0.7 + sh], [-11.2, 2.8 + sh], [-10.9, 9], [-10.0, 16.5], [-11.0, 25], [-12.8, 34],
  ];
  const left = dressRel.map(([x, y]) => up([x * bw, nl + y]));
  const right = dressRel.slice().reverse().map(([x, y]) => up([-x * bw, nl + y]));
  // 下半截（腰以下）不完全跟着上身转，裙摆留在腿上
  const skirt = [[-15.0 + hs, hem - 0.8], [-7.6 + hs * 0.6, hem + 0.6], [hs * 0.4, hem + 0.9], [7.6 + hs * 0.6, hem + 0.6], [15.0 + hs, hem - 0.8]].map((p) => lerpP(up(p), [p[0], p[1] + P.bob], 0.75));
  const dress = [...left, ...skirt, ...right, up([0, nl + 0.9])];
  fig.part('dress', dress, { fill: D.dress, z: 0 });
  fig.paint((c) => { // 白色小波点
    c.fillStyle = D.dressDot;
    for (let r = 0; r < 10; r++) for (let q = -4; q <= 4; q++) {
      const p = up([q * 3.3 + (r % 2) * 1.65, nl + 6 + r * 4.3]);
      c.beginPath(); c.arc(p[0], p[1], 0.42, 0, Math.PI * 2); c.fill();
    }
  }, { z: 0.1, clip: ['dress'] });
  for (const x of [-6.2, 0.4, 6.8]) fig.detail([up([x * 0.45, nl + 17]), lerpP(up([x * 0.85, nl + 30]), [x * 0.85 + hs * 0.3, nl + 30], 0.5), [x * 1.3 + hs * 0.5, hem + 0.4]], { z: 0.2, lw: lw * 0.55, color: D.dressShade, clip: ['dress'], profile: 'in' });
  for (const sg of [-1, 1]) { // 白色圆领
    const pts = [[0, 0.3], [sg * 4.9, -1.4 + sh * 0.3], [sg * 8.6, 0.4 + sh * 0.5], [sg * 8.2, 3.6], [sg * 4.6, 5.0], [sg * 1.1, 3.4]].map(([x, y]) => up([x, nl + y]));
    fig.part('collar' + (sg < 0 ? 'L' : 'R'), pts, { fill: D.collar, z: 1, inner: true, per: 4 });
  }

  // ---- 胳膊：泡泡袖 + 手臂 + 手
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const A = P['arm' + side] || {};
    const S = up([sg * D.shoulder[0], D.shoulder[1] + sh]);
    const W = A.hand || [sg * 14.6, -53.5];
    const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? sg).joint;
    const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 1.95], [0.45, 1.7], [0.55, 1.55], [1, 1.2]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    const zA = A.z ?? 2;
    fig.part('arm' + side, arm.outline, { fill: D.skin, z: zA, inner: true });
    const sv = [[sg * 8.8, -0.2 + sh], [sg * 12.3, 0 + sh], [sg * 15.0, 2.6 + sh], [sg * 14.9, 6.6 + sh], [sg * 12.5, 8.2 + sh], [sg * 9.8, 7.6]].map(([x, y]) => up([x, nl + y]));
    fig.part('sleeve' + side, sv, { fill: D.dress, z: zA + 0.5, inner: true, per: 4 });
    fig.detail([sv[3], lerpP(sv[3], sv[4], 0.5), sv[4]].map((p) => [p[0], p[1] - 0.9]), { z: zA + 0.6, lw: lw * 0.55, color: D.dressShade, clip: ['sleeve' + side] });
    const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
    hand(fig, M.chain(M.t(W[0], W[1]), M.r(dir)), A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? sg > 0, skin: D.skin, z: zA + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
  }

  // ---- 头
  headFront(fig, H, Hs, P, D, lw, turn, nod);
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
}

function headFront(fig, H, Hs, P, D, lw, turn, nod) {
  const tx = turn * 2.4;
  const face = [[-12.6, -6], [-13.3, 0.5], [-12.4, 6.2], [-9.9, 10.6], [-5.4, 13.4], [0, 14.2], [5.4, 13.4], [9.9, 10.6], [12.4, 6.2], [13.3, 0.5], [12.6, -6], [10, -11.5], [0, -14], [-10, -11.5]]
    .map(([x, y]) => [x + tx * 0.25 * (1 - Math.abs(y) / 15), y]);
  fig.part('face', Hs(face), { fill: D.skin, z: 5 });
  const F = faceOf(P.face);
  const fy = nod * 1.4;
  for (const sg of [-1, 1]) {
    const k = 1 - sg * turn * 0.18;
    eye(fig, H([sg * 5.5 + tx, 0.8 + fy]), [1.95 * k, 2.6], F, sg, { z: 6, clip: ['face'], iris: D.iris, ink: D.ink, lw, lash: true, hi2: true });
    blush(fig, H([sg * 8.3 + tx * 0.7, 5.8 + fy]), 2.8, F.blush, { rgb: D.blush, clip: ['face'] });
    brow(fig, H([sg * 5.6 + tx, -4.4 + fy]), 3.6, F, sg, { z: 9, lw: lw * 0.9, color: D.hair });
  }
  fig.detail([H([0.35 + tx * 1.1, 4.0 + fy]), H([-0.25 + tx * 1.1, 5.0 + fy]), H([0.45 + tx * 1.1, 5.3 + fy])], { z: 6, lw: lw * 0.55, color: D.skinShade, clip: ['face'], profile: 'soft' });
  mouth(fig, H([tx * 0.9, 8.7 + fy]), 3.4, F, { z: 6, clip: ['face'], ink: D.ink, lw, inside: D.mouthIn, tongue: D.tongue });
  // 头发：圆圆的头顶 + 齐刘海 + 两侧鬓发
  const hx = tx * 0.35;
  const hair = [
    [-12.9, 5.5], [-14.9, -2.5], [-15.6, -10.5], [-13.4, -17.6], [-7.2, -21.9], [0, -23], [7.2, -21.9], [13.4, -17.6], [15.6, -10.5], [14.9, -2.5], [12.9, 5.5],
    [11.5, 2.5], [11.3, -3.6], [9.6 + hx, -6.0], [7.7 + hx, -5.0], [5.6 + hx, -6.3], [3.2 + hx, -5.1], [0.7 + hx, -6.5], [-1.8 + hx, -5.2], [-4.4 + hx, -6.4], [-6.8 + hx, -5.1], [-9.3 + hx, -6.1], [-11.3, -3.6], [-11.5, 2.5],
  ];
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  // 呆毛
  const cw = P.cowlick;
  const cl = tube([[0.8, -22.4], [1.6 + cw * 1.5, -25.2], [3.6 + cw * 2.6, -26.2], [5.0 + cw * 3, -25.0]], [[0, 0.75], [0.6, 0.5], [1, 0.12]], { capStart: 'flat', step: 0.25 });
  fig.part('cowlick', Hs(cl.outline), { fill: D.hair, z: 7.05, per: 3 });
  fig.detail(Hs([[-9.5, -16], [-3.5, -19.6], [3.2, -19.6]]), { z: 7.1, lw: lw * 1.1, color: D.hairHi, clip: ['hair'], profile: 'taper' });
  fig.detail(Hs([[-6.5, -8.2], [-5.4, -12.8]]), { z: 7.1, lw: lw * 0.55, color: D.hairHi, clip: ['hair'] });
  fig.detail(Hs([[4.5, -8.4], [5.6, -13]]), { z: 7.1, lw: lw * 0.55, color: D.hairHi, clip: ['hair'] });
}

export function draw(ctx, view, P, o = {}) {
  ctx.save();
  const p = pose(P);
  ctx.translate(p.x, p.y);
  ctx.scale(p.s, p.s);
  const r = view === 'side' ? side(ctx, p, o) : view === 'back' ? back(ctx, p, o) : front(ctx, p, o);
  ctx.restore();
  return r;
}

// ================================================================== 侧面（面朝 +x）
export function side(ctx, P0, o = {}) {
  const P = pose(P0), D = XM;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 5, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const hipC = [-1.0, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);
  const sh = P.shrug * 2.0, br = P.breath, nl = D.nl;
  const N = up([0.6, nl - 1.2 - sh * 0.3]);
  const nod = P.head.nod;
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt + nod * 0.12), M.t(-1.0, D.faceC[1] - (nl - 1.2)));
  const H = (p) => M.ap(HM, p), Hs = (pts) => pts.map(H);
  // ---- 腿：远的一条在后面，近的一条在前面
  for (const [side, dx, z, tone] of [['F', -1.4, -6, D.skinShade], ['N', 0.6, -4, D.skin]]) {
    const leg = P['leg' + side] || {};
    const hip = [dx - 0.5, D.hipY + P.bob];
    const foot = leg.foot || [dx + 0.4, -3.8];
    const knee = leg.knee || ik2(hip, foot, D.thigh, D.shin, 1).joint; // 膝盖朝前（+x）
    const t = tube([hip, lerpP(hip, knee, 0.5), knee, lerpP(knee, foot, 0.45), foot], [[0, [3.4, 3.4]], [0.45, [2.6, 2.6]], [0.55, [2.5, 2.5]], [0.7, [2.2, 2.7]], [1, [1.5, 1.5]]], { capStart: 'flat', capEnd: 'flat', step: 0.6 });
    fig.part('leg' + side, t.outline, { fill: tone, z, per: 2 });
    const fx = foot[0], fy = foot[1];
    fig.part('foot' + side, [[fx - 2.2, fy - 1.2], [fx + 1.5, fy - 0.2], [fx + 5.6, fy + 1.6], [fx + 6.4, fy + 3.2], [fx + 5.6, fy + 3.9], [fx - 2.4, fy + 3.9], [fx - 2.8, fy + 1.6]], { fill: tone, z: z + 0.1 });
    fig.part('sole' + side, [[fx - 3.0, fy + 3.1], [fx + 6.6, fy + 3.1], [fx + 6.9, fy + 4.4], [fx - 3.0, fy + 4.4]], { fill: D.sandal, z: z + 0.2, inner: true, smooth: false });
    fig.detail([[fx + 0.4, fy - 0.2], [fx + 1.6, fy + 1.4], [fx + 2.4, fy + 3.2]], { z: z + 0.3, lw: lw * 1.6, color: D.sandal, profile: 'flat', clip: ['foot' + side] });
    fig.detail([[fx + 3.8, fy + 0.9], [fx + 4.3, fy + 3.2]], { z: z + 0.3, lw: lw * 1.4, color: D.sandal, profile: 'flat', clip: ['foot' + side] });
  }
  // ---- 远侧胳膊（大部分被身体挡住）
  armSide(fig, P, D, 'F', up, sh, -3, D.skinShade, lw);
  // ---- 马尾：远的一根从后脑勺后面露出一点，近的一根挂在耳后
  for (const [side, base, ang0, z] of [['F', [-10.6, -10.8], 2.15, 3.0], ['N', [-9.4, -8.6], 1.95, 7.2]]) {
    const sw = P.pig[side === 'F' ? 0 : 1];
    const T = M.chain(HM, M.t(base[0], base[1]), M.r(ang0 + sw));
    fig.part('pig' + side, M.apAll(T, pigtailPts(12.5, 3.5)), { fill: D.hair, z, per: 4 });
    fig.detail(M.apAll(T, [[2.5, -0.4], [6.5, -0.9], [10.5, -0.5]]), { z: z + 0.1, lw: lw * 0.55, color: D.hairHi, clip: ['pig' + side] });
    fig.part('bob' + side, M.apAll(T, ellipsePts(0.6, 0, 2.15, 2.25, 16)), { fill: D.bobble, z: z + 0.2, inner: true });
  }
  // ---- 脖子、裙子
  fig.part('neck', [up([-2.4, nl - 4.5]), up([2.6, nl - 4.2]), up([3.2, nl + 1.0]), up([-3.0, nl + 1.0])], { fill: D.skin, z: 0.5 });
  const hs = P.dress * 2.2, hem = D.hem;
  const bw = 1 + br * 0.03;
  const top = [[-3.6, -0.5], [-5.0, 1.6 + sh], [-5.6, 7], [-5.4, 15], [-6.2, 24], [-7.6, 33]].map(([x, y]) => up([x * bw, nl + y]));
  const frontC = [[8.2, 33], [6.6, 24], [6.1, 16], [5.7, 7.5], [4.6, 2.4], [3.4, 0.6]].map(([x, y]) => up([x * bw, nl + y]));
  const skirt = [[-9.6 + hs, hem - 0.8], [-3 + hs * 0.6, hem + 0.6], [4 + hs * 0.6, hem + 0.7], [10.6 + hs, hem - 0.6]].map((p) => lerpP(up(p), [p[0], p[1] + P.bob], 0.75));
  fig.part('dress', [...top, ...skirt, ...frontC], { fill: D.dress, z: 0 });
  fig.paint((c) => {
    c.fillStyle = D.dressDot;
    for (let r = 0; r < 10; r++) for (let q = -3; q <= 3; q++) {
      const p = up([q * 3.3 + (r % 2) * 1.65, nl + 6 + r * 4.3]);
      c.beginPath(); c.arc(p[0], p[1], 0.42, 0, Math.PI * 2); c.fill();
    }
  }, { z: 0.1, clip: ['dress'] });
  for (const x of [-2.5, 3.5]) fig.detail([up([x * 0.5, nl + 18]), up([x * 0.9, nl + 30]), [x * 1.4 + hs * 0.5, hem + 0.3]], { z: 0.2, lw: lw * 0.55, color: D.dressShade, clip: ['dress'], profile: 'in' });
  // 圆领（侧面只看到前面一片）
  fig.part('collar', [[-1.6, -0.4], [2.2, -0.9 + sh * 0.3], [4.6, 0.7], [5.4, 3.4], [3.2, 4.6], [0.2, 3.2]].map(([x, y]) => up([x, nl + y])), { fill: D.collar, z: 1, inner: true, per: 4 });
  // ---- 头
  const face = [[-4.5, -12], [5.6, -12.6], [10.3, -7.2], [11.7, -2.2], [11.9, 1.4], [13.1, 3.6], [12.3, 5.0], [12.5, 6.8], [11.8, 7.9], [12.0, 9.0], [10.6, 11.6], [6.0, 13.4], [0.5, 12.6], [-4.8, 8.5], [-6.4, 0]];
  fig.part('face', Hs(face), { fill: D.skin, z: 5 });
  const F = faceOf(P.face);
  eye(fig, H([8.3, 0.9 + nod * 0.8]), [1.45, 2.6], F, 1, { z: 6, clip: ['face'], iris: D.iris, ink: D.ink, lw, lash: true, hi2: false });
  blush(fig, H([6.6, 5.9]), 2.6, F.blush, { rgb: D.blush, clip: ['face'] });
  brow(fig, H([8.4, -4.3 + nod * 0.6]), 3.0, F, 1, { z: 9, lw: lw * 0.9, color: D.hair });
  sideMouth(fig, H, F, D, lw);
  fig.part('ear', Hs(ellipsePts(-1.4, 1.9, 2.0, 2.7, 18)), { fill: D.skin, z: 7.6, inner: true, innerLw: 0.8 });
  fig.detail(Hs([[-0.4, 0.2], [-1.6, 1.8], [-0.6, 3.2]]), { z: 7.7, lw: lw * 0.5, color: D.skinShade, clip: ['ear'] });
  const hair = [[11.4, -6.4], [11.4, -9.8], [9.4, -15.8], [4, -20.8], [-3, -22.8], [-10.2, -19.2], [-14.8, -11], [-14.9, -2], [-12.2, 6], [-7.6, 8.4], [-4.0, 5.6], [-3.6, -3.4], [1.4, -6.6], [4.5, -5.0], [7.2, -6.4], [9.4, -5.2]];
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  const cw = P.cowlick;
  const cl = tube([[1.8, -22.4], [2.4 + cw * 1.5, -25.4], [4.4 + cw * 2.6, -26.3], [5.9 + cw * 3, -25.0]], [[0, 0.75], [0.6, 0.5], [1, 0.12]], { capStart: 'flat', step: 0.25 });
  fig.part('cowlick', Hs(cl.outline), { fill: D.hair, z: 7.05, per: 3 });
  fig.detail(Hs([[-9.5, -15], [-3.5, -19.6], [3.6, -19.4]]), { z: 7.1, lw: lw * 1.1, color: D.hairHi, clip: ['hair'], profile: 'taper' });
  fig.detail(Hs([[-11, -4], [-9.5, -11.5]]), { z: 7.1, lw: lw * 0.55, color: D.hairHi, clip: ['hair'] });
  // ---- 近侧胳膊
  armSide(fig, P, D, 'N', up, sh, 2, D.skin, lw);
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
}

function sideMouth(fig, H, F, D, lw) {
  const c = H([11.3, 8.0]);
  if (F.mouth > 0.1 || F.puff > 0.4) {
    const r = 0.6 + F.mouth * 1.2;
    fig.detail(ellipsePts(c[0] - 0.4, c[1] + r * 0.3, r * 0.55, r, 14), { z: 6, fill: D.mouthIn, lw: lw * 0.6, color: D.ink, clip: ['face'] });
  } else {
    const s = F.smile;
    fig.detail([H([11.9, 7.9 - s * 0.2]), H([10.9, 8.0 - s * 0.7])], { z: 6, lw: lw * 0.7, color: D.ink, clip: ['face'], profile: 'out' });
  }
}

function armSide(fig, P, D, side, up, sh, z, tone, lw) {
  const A = P['arm' + side] || {};
  const S = up([side === 'N' ? 0.4 : -0.6, D.shoulder[1] + sh]);
  const W = A.hand || (side === 'N' ? [2.8, -54.2] : [-1.6, -54.6]);
  const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? 1).joint;   // 肘尖朝后（-x）
  const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 1.95], [0.45, 1.7], [0.55, 1.55], [1, 1.2]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
  fig.part('arm' + side, arm.outline, { fill: tone, z: A.z ?? z, inner: side === 'N' });
  if (side === 'N') {
    const nl = D.nl;
    const sv = [[-3.6, 1.2 + sh], [0.4, 0.2 + sh], [3.8, 2.4 + sh], [4.2, 6.8 + sh], [1.4, 8.6 + sh], [-2.8, 7.6 + sh], [-4.2, 4.6 + sh]].map(([x, y]) => up([x, nl + y]));
    fig.part('sleeve', sv, { fill: D.dress, z: (A.z ?? z) + 0.5, inner: true, per: 4 });
    fig.detail([sv[3], sv[4], sv[5]].map((p) => [p[0], p[1] - 0.9]), { z: (A.z ?? z) + 0.6, lw: lw * 0.55, color: D.dressShade, clip: ['sleeve'] });
  }
  const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
  hand(fig, M.chain(M.t(W[0], W[1]), M.r(dir)), A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? false, skin: tone, z: (A.z ?? z) + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
}

// ================================================================== 背面
export function back(ctx, P0, o = {}) {
  const P = pose(P0), D = XM;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 7, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const hipC = [0, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);
  const sh = P.shrug * 2.2, br = P.breath, nl = D.nl;
  // 背面：低头时头往下沉一点、后脑勺露得更多（用整体下移近似）
  const N = up([0, nl - 1.2 - sh * 0.3 + P.head.nod * 2.4]);
  const turn = clamp(P.head.turn, -1, 1);
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt), M.t(0, D.faceC[1] - (nl - 1.2)));
  const H = (p) => M.ap(HM, p), Hs = (pts) => pts.map(H);
  const seated = !!P.seated;
  // ---- 腿（坐着时腿在身前，背后看不见，只露一点脚后跟）
  if (!seated) {
    for (const [side, sg] of [['L', -1], ['R', 1]]) {
      const leg = P['leg' + side] || {};
      const hip = [sg * D.hipX, D.hipY + P.bob];
      const foot = leg.foot || [sg * 5.4, -4.0];
      const knee = [lerp(hip[0], foot[0], 0.5), lerp(hip[1], foot[1], D.thigh / (D.thigh + D.shin))];
      const t = tube([hip, lerpP(hip, knee, 0.5), knee, lerpP(knee, foot, 0.4), foot], [[0, 3.3], [0.45, 2.5], [0.55, 2.6], [0.72, 2.6], [1, 1.55]], { capStart: 'flat', capEnd: 'flat', step: 0.6 });
      fig.part('leg' + side, t.outline, { fill: D.skin, z: -4, per: 2 });
      fig.detail([[knee[0] - 1.6, knee[1] + 0.3], [knee[0], knee[1] + 0.9], [knee[0] + 1.6, knee[1] + 0.3]], { z: -3.95, lw: lw * 0.45, color: D.skinShade, clip: ['leg' + side] });
      const fx = foot[0], fy = foot[1];
      fig.part('heel' + side, [[fx - 2.2, fy - 0.6], [fx - 2.5, fy + 2.6], [fx - 1.4, fy + 3.7], [fx + 1.4, fy + 3.7], [fx + 2.5, fy + 2.6], [fx + 2.2, fy - 0.6]], { fill: D.skin, z: -3.9 });
      fig.part('sole' + side, [[fx - 2.8, fy + 3.0], [fx - 2.6, fy + 4.4], [fx + 2.6, fy + 4.4], [fx + 2.8, fy + 3.0]], { fill: D.sandal, z: -3.8, inner: true });
      fig.detail([[fx - 2.3, fy + 1.8], [fx, fy + 2.4], [fx + 2.3, fy + 1.8]], { z: -3.7, lw: lw * 1.4, color: D.sandal, profile: 'flat', clip: ['heel' + side] });
    }
  }
  // ---- 脖子
  fig.part('neck', [up([-3.0, nl - 4.5]), up([3.0, nl - 4.5]), up([3.3, nl + 1.2]), up([-3.3, nl + 1.2])], { fill: D.skin, z: 0.5 });
  // ---- 裙子：背面有一个蝴蝶结
  const hs = P.dress * 2.2, hem = seated ? (P.hemY ?? D.hem) : D.hem;
  const bw = 1 + br * 0.025;
  const rel = [[-4.4, 0.4], [-9.3, 0.7 + sh], [-11.2, 2.8 + sh], [-10.9, 9], [-10.0, 16.5], [-11.0, 25], [-12.8, 34]];
  const left = rel.map(([x, y]) => up([x * bw, nl + y]));
  const right = rel.slice().reverse().map(([x, y]) => up([-x * bw, nl + y]));
  const spread = seated ? 1.25 : 1;
  const skirt = [[-15.0 * spread + hs, hem - 0.8], [-7.6 * spread + hs * 0.6, hem + 0.6], [hs * 0.4, hem + 0.9], [7.6 * spread + hs * 0.6, hem + 0.6], [15.0 * spread + hs, hem - 0.8]].map((p) => lerpP(up(p), [p[0], p[1] + P.bob], 0.75));
  fig.part('dress', [...left, ...skirt, ...right, up([0, nl - 0.2])], { fill: D.dress, z: 0 });
  fig.paint((c) => {
    c.fillStyle = D.dressDot;
    for (let r = 0; r < 10; r++) for (let q = -5; q <= 5; q++) {
      const p = up([q * 3.3 + (r % 2) * 1.65, nl + 6 + r * 4.3]);
      c.beginPath(); c.arc(p[0], p[1], 0.42, 0, Math.PI * 2); c.fill();
    }
  }, { z: 0.1, clip: ['dress'] });
  for (const x of [-6.2, 0.4, 6.8]) fig.detail([up([x * 0.45, nl + 20]), up([x * 0.85, nl + 30]), [x * 1.3 + hs * 0.5, hem + 0.4]], { z: 0.2, lw: lw * 0.55, color: D.dressShade, clip: ['dress'], profile: 'in' });
  // 领子后面一圈
  fig.detail([up([-8.4, nl + 1.0]), up([0, nl + 2.6]), up([8.4, nl + 1.0])], { z: 1, lw: lw * 0.8, color: D.ink, clip: ['dress'], profile: 'soft' });
  // 蝴蝶结（腰后）
  const bc = up([0, nl + 19]);
  for (const sg of [-1, 1]) fig.part('bow' + sg, [[0, 0], [sg * 3.6, -2.2], [sg * 4.6, -0.4], [sg * 4.2, 1.8], [sg * 1.0, 0.6]].map(([x, y]) => [bc[0] + x, bc[1] + y]), { fill: D.dress, z: 1.2, inner: true, per: 3 });
  for (const sg of [-1, 1]) fig.part('tail' + sg, [[sg * 0.4, 0.4], [sg * 2.4, 4.6], [sg * 1.8, 6.4], [sg * 0.6, 5.0], [sg * -0.2, 1.0]].map(([x, y]) => [bc[0] + x, bc[1] + y]), { fill: D.dress, z: 1.15, inner: true, per: 3 });
  fig.part('knot', ellipsePts(bc[0], bc[1] + 0.2, 1.3, 1.4, 12), { fill: D.dress, z: 1.3, inner: true });
  // ---- 胳膊
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const A = P['arm' + side] || {};
    const S = up([sg * D.shoulder[0], D.shoulder[1] + sh]);
    const W = A.hand || [sg * 14.6, -53.5];
    const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? sg).joint;
    const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 1.95], [0.45, 1.7], [0.55, 1.55], [1, 1.2]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    const zA = A.z ?? 2;
    fig.part('arm' + side, arm.outline, { fill: D.skin, z: zA, inner: true });
    const sv = [[sg * 8.8, -0.2 + sh], [sg * 12.3, 0 + sh], [sg * 15.0, 2.6 + sh], [sg * 14.9, 6.6 + sh], [sg * 12.5, 8.2 + sh], [sg * 9.8, 7.6]].map(([x, y]) => up([x, nl + y]));
    fig.part('sleeve' + side, sv, { fill: D.dress, z: zA + 0.5, inner: true, per: 4 });
    const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
    hand(fig, M.chain(M.t(W[0], W[1]), M.r(dir)), A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? sg < 0, skin: D.skin, z: zA + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
  }
  // ---- 头：后脑勺整块头发，耳朵从两边露出来，马尾和绒球
  const tx = -turn * 1.6;
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const ex = sg * (12.5 + (sg * turn < 0 ? 0.6 : -0.8) * Math.abs(turn));
    fig.part('ear' + side, Hs(ellipsePts(ex, 1.6, 2.0, 2.8, 18)), { fill: D.skin, z: 4.2 });
    const sw = P.pig[side === 'L' ? 0 : 1];
    const base = [sg * 12.4, -9.4];
    const ang = sg < 0 ? Math.PI - 0.72 - sw : 0.72 + sw;
    const T = M.chain(HM, M.t(base[0], base[1]), M.r(ang));
    const pts = pigtailPts(12.5, 3.6).map((p) => [p[0], p[1] * (sg < 0 ? -1 : 1)]);
    fig.part('pig' + side, M.apAll(T, pts), { fill: D.hair, z: 7.3, inner: true, innerLw: 0.7, per: 4 });
    fig.detail(M.apAll(T, [[2.5, 0.4 * sg], [6.5, 0.9 * sg], [10.5, 0.5 * sg]]), { z: 7.35, lw: lw * 0.55, color: D.hairHi, clip: ['pig' + side] });
    fig.part('bob' + side, M.apAll(T, ellipsePts(0.6, 0, 2.15, 2.25, 16)), { fill: D.bobble, z: 7.4, inner: true });
  }
  // 后颈的皮肤（头发下沿露出来）
  fig.part('nape', Hs([[-5.0, 6], [5.0, 6], [4.2, 12.2], [-4.2, 12.2]]), { fill: D.skin, z: 4.5 });
  const hair = [[-12.6, 6.5], [-14.9, -2.5], [-15.6, -10.5], [-13.4, -17.6], [-7.2, -21.9], [0, -23], [7.2, -21.9], [13.4, -17.6], [15.6, -10.5], [14.9, -2.5], [12.6, 6.5], [8.5, 9.6], [4.5, 8.6], [2, 10.4], [-0.8, 8.8], [-3.6, 10.2], [-6.5, 8.8], [-9.6, 9.4]]
    .map(([x, y]) => [x + tx * 0.15, y]);
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  // 后脑勺的分缝：从头顶到两边马尾
  fig.detail(Hs([[0 + tx, -22.5], [0.2 + tx, -12], [0 + tx, 7.5]]), { z: 7.1, lw: lw * 0.55, color: D.hairHi, clip: ['hair'] });
  for (const sg of [-1, 1]) fig.detail(Hs([[sg * 1.2 + tx, -21], [sg * 7, -15], [sg * 11.6, -9.6]]), { z: 7.1, lw: lw * 0.5, color: D.hairHi, clip: ['hair'] });
  fig.detail(Hs([[-9, -17.5], [-3.5, -20.2], [3, -20.4]]), { z: 7.1, lw: lw * 1.1, color: D.hairHi, clip: ['hair'], profile: 'taper' });
  const cw = P.cowlick;
  const cl = tube([[-0.6, -22.4], [0.4 + cw * 1.5, -25.4], [2.4 + cw * 2.6, -26.3], [3.9 + cw * 3, -25.0]], [[0, 0.75], [0.6, 0.5], [1, 0.12]], { capStart: 'flat', step: 0.25 });
  fig.part('cowlick', Hs(cl.outline), { fill: D.hair, z: 6.9, per: 3 });
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
}
