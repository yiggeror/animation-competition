// 奶奶：七十来岁。灰白头发往后梳成低发髻、插一根发簪；圆框眼镜，眼睛常常笑成两道弯；
// 淡蓝碎花的确良短袖衬衫，深蓝宽腿裤，黑布鞋白鞋底；左手腕戴玉镯；背有一点驼。
// 身体坐标：厘米，原点在两脚中间的地面，+y 向下。视角：front 正面、side 侧面（面朝 +x）、back 背面。
import { Figure, tube, M } from '../lib/figure.js';
import { ik2, lerpP, rotP, ellipsePts, curScale } from '../lib/draw.js';
import { clamp, lerp } from '../lib/core.js';
import { eye, brow, mouth, blush, glasses, faceOf } from './face.js';
import { hand, bracelet } from './hand.js';

export const NN = {
  name: '奶奶',
  skin: '#f1cfb2', skinShade: '#dcab8c', blush: '232,140,120', wrinkle: '#c9967a',
  hair: '#bdb8b0', hairHi: '#dcd8d1', hairLo: '#9c968d', pin: '#5a3b2c',
  blouse: '#a9c6de', blouseShade: '#86a7c4', flower: '#f6f1ea', flower2: '#e9a7a0',
  pants: '#3e4454', pantsShade: '#31364300',
  shoe: '#2b2725', sole: '#efe7da',
  frame: '#6d5547', iris: '#2e211b', mouthIn: '#7e3a32', tongue: '#d98476',
  jade: '#8fc4a0',
  ink: '#3b2c25',
  faceC: [0, -124], nl: -108.5, shoulder: [14.6, -103.5], upper: 21.5, fore: 19.5, palm: 5.4,
  hipY: -75, hipX: 7.2, thigh: 35.5, shin: 35.5, hem: -70.5,
};

export const POSE0 = {
  x: 0, y: 0, s: 1,
  lean: 0, stoop: 1, bob: 0, breath: 0, shrug: 0,
  head: { tilt: 0, turn: 0, nod: 0 },
  face: {},
  armL: null, armR: null,
  legL: null, legR: null,
  seated: false,
};
export function pose(o = {}) { return { ...POSE0, ...o, head: { ...POSE0.head, ...(o.head || {}) } }; }
function inkFor(ctx) { return clamp(curScale(ctx) * 0.4, 1.5, 5.0); }

// 衬衫上的小碎花
function flowers(c, up, x0, x1, y0, y1, D) {
  for (let r = 0; r * 4.6 < y1 - y0; r++) for (let q = 0; q * 4.4 < x1 - x0; q++) {
    const p = up([x0 + q * 4.4 + (r % 2) * 2.2, y0 + r * 4.6]);
    c.fillStyle = (q + r) % 3 === 0 ? D.flower2 : D.flower;
    for (let k = 0; k < 4; k++) { const a = k * Math.PI / 2 + 0.4; c.beginPath(); c.arc(p[0] + Math.cos(a) * 0.55, p[1] + Math.sin(a) * 0.55, 0.42, 0, Math.PI * 2); c.fill(); }
  }
}

// ================================================================== 正面
export function front(ctx, P0, o = {}) {
  const P = pose(P0), D = NN;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 11, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const hipC = [0, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);
  const sh = P.shrug * 2.6 + P.stoop * 1.2, br = P.breath, nl = D.nl;
  const N = up([0, nl - 1.6 + P.stoop * 1.4]);
  const turn = clamp(P.head.turn, -1, 1), nod = P.head.nod;
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt), M.t(0, D.faceC[1] - (nl - 1.6)));
  const H = (p) => M.ap(HM, p), Hs = (pts) => pts.map(H);
  // ---- 裤子（两条宽裤腿）和布鞋
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const leg = P['leg' + side] || {};
    const foot = leg.foot || [sg * 7.4, -4.6];
    const pts = [[sg * 16.0, D.hem - 3], [sg * 0.6, D.hem - 3], [sg * 1.4, -56], [foot[0] - sg * 4.2, -24], [foot[0] - sg * 4.4, foot[1] + 0.4], [foot[0] + sg * 4.4, foot[1] + 0.4], [foot[0] + sg * 4.6, -26], [sg * 15.2, -52]];
    fig.part('pants' + side, pts, { fill: D.pants, z: -4, per: 3 });
    fig.detail([[sg * 6.6, -60], [foot[0] - sg * 0.2, -30], [foot[0], foot[1] - 2]], { z: -3.9, lw: lw * 0.5, color: '#2e3340', clip: ['pants' + side], profile: 'taper' });
    const fx = foot[0], fy = foot[1];
    fig.part('shoe' + side, [[fx - 4.4, fy + 0.4], [fx - 4.8, fy + 2.8], [fx - 3.2, fy + 4.2], [fx + 3.2, fy + 4.2], [fx + 4.8, fy + 2.8], [fx + 4.4, fy + 0.4], [fx, fy - 0.4]], { fill: D.shoe, z: -3.8, inner: true });
    fig.part('sole' + side, [[fx - 4.9, fy + 3.4], [fx - 4.6, fy + 4.8], [fx + 4.6, fy + 4.8], [fx + 4.9, fy + 3.4]], { fill: D.sole, z: -3.7, inner: true });
  }
  // ---- 耳朵、脖子
  for (const sg of [-1, 1]) {
    const ex = sg * (11.0 - (sg * turn > 0 ? turn * 1.0 : 0));
    fig.part('ear' + (sg < 0 ? 'L' : 'R'), Hs([[ex - sg * 0.4, -3.6], [ex + sg * 1.9, -3.4], [ex + sg * 2.4, 0.5], [ex + sg * 1.6, 4.6], [ex + sg * 0.4, 5.4], [ex - sg * 0.6, 3.0]]), { fill: D.skin, z: 4.2 });
    fig.detail(Hs([[ex + sg * 0.6, -2.0], [ex + sg * 1.4, 0.6], [ex + sg * 0.7, 3.2]]), { z: 4.3, lw: lw * 0.5, color: D.skinShade, clip: ['ear' + (sg < 0 ? 'L' : 'R')] });
  }
  fig.part('neck', [up([-4.0, nl - 6]), up([4.0, nl - 6]), up([4.6, nl + 2]), up([-4.6, nl + 2])], { fill: D.skin, z: 0.5 });
  // ---- 衬衫
  const bw = 1 + br * 0.02;
  const rel = [[-5.0, 0], [-10.4, 1.4 + sh], [-13.8, 3.6 + sh], [-14.2, 11], [-14.6, 22], [-15.4, 31], [-16.2, 37.4]];
  const left = rel.map(([x, y]) => up([x * bw, nl + y]));
  const right = rel.slice().reverse().map(([x, y]) => up([-x * bw, nl + y]));
  const hem = [[-8, D.hem + 0.8], [0, D.hem + 1.6], [8, D.hem + 0.8]].map(up);
  fig.part('blouse', [...left, ...hem, ...right, up([0, nl + 5])], { fill: D.blouse, z: 0 });
  fig.paint((c) => flowers(c, up, -16, 16, nl + 4, D.hem + 2, D), { z: 0.1, clip: ['blouse'] });
  // 门襟和扣子
  fig.detail([up([0.6, nl + 5]), up([0.6, nl + 20]), up([0.6, D.hem + 1.4])], { z: 0.2, lw: lw * 0.6, color: D.blouseShade, clip: ['blouse'], profile: 'flat' });
  for (let i = 0; i < 4; i++) { const b = up([1.9, nl + 9 + i * 8]); fig.detail(ellipsePts(b[0], b[1], 0.7, 0.7, 10), { z: 0.3, fill: D.flower, lw: lw * 0.4, color: D.blouseShade }); }
  // 衣领（尖领，两片）
  for (const sg of [-1, 1]) fig.part('collar' + sg, [[sg * 0.4, 5.2], [sg * 4.6, -0.6], [sg * 8.6, 0.8 + sh * 0.6], [sg * 7.6, 3.6], [sg * 3.6, 9.6]].map(([x, y]) => up([x, nl + y])), { fill: D.blouse, z: 1, inner: true, per: 3, smooth: false });
  // 衣服的几道褶（胸下、腰侧）
  for (const sg of [-1, 1]) fig.detail([up([sg * 12.5, nl + 15]), up([sg * 9.5, nl + 20]), up([sg * 6.5, nl + 22])], { z: 0.2, lw: lw * 0.5, color: D.blouseShade, clip: ['blouse'], profile: 'taper' });
  // ---- 胳膊
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const A = P['arm' + side] || {};
    const S = up([sg * D.shoulder[0], D.shoulder[1] + sh]);
    const W = A.hand || [sg * 17.6, -64.5];
    const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? sg).joint;
    const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 2.8], [0.45, 2.4], [0.55, 2.2], [1, 1.75]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    const zA = A.z ?? 2;
    fig.part('arm' + side, arm.outline, { fill: D.skin, z: zA, inner: true });
    // 短袖：盖到上臂一半
    const ua = Math.atan2(E[1] - S[1], E[0] - S[0]);
    const sv = tube([S, [S[0] + Math.cos(ua) * 9.5, S[1] + Math.sin(ua) * 9.5]], [[0, 4.0], [1, 3.6]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    fig.part('sleeve' + side, sv.outline, { fill: D.blouse, z: zA + 0.5, inner: true });
    fig.paint((c) => flowers(c, (p) => p, S[0] - 6, S[0] + 6, S[1] - 3, S[1] + 11, D), { z: zA + 0.55, clip: ['sleeve' + side] });
    const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
    const Mw = M.chain(M.t(W[0], W[1]), M.r(dir));
    hand(fig, Mw, A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? sg > 0, skin: D.skin, z: zA + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
    if (side === 'R') bracelet(fig, Mw, D.palm, { name: 'jade', z: zA + 0.4 });
  }
  // ---- 头
  headFront(fig, H, Hs, P, D, lw, turn, nod);
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
}

function headFront(fig, H, Hs, P, D, lw, turn, nod) {
  const tx = turn * 2.0;
  const face = [[-10.2, -8], [-11, -1], [-10.7, 5], [-9.3, 9.6], [-5.6, 12.7], [0, 13.5], [5.6, 12.7], [9.3, 9.6], [10.7, 5], [11, -1], [10.2, -8], [7.5, -12.5], [0, -14], [-7.5, -12.5]]
    .map(([x, y]) => [x + tx * 0.25 * (1 - Math.abs(y) / 15), y]);
  fig.part('face', Hs(face), { fill: D.skin, z: 5 });
  const F = faceOf({ smile: 0.35, blush: 0.3, ...P.face });
  const fy = nod * 1.2;
  const wr = { z: 6.2, lw: lw * 0.45, color: D.wrinkle, clip: ['face'], profile: 'taper' };
  for (const sg of [-1, 1]) {
    const k = 1 - sg * turn * 0.15;
    eye(fig, H([sg * 4.6 + tx, -0.2 + fy]), [1.15 * k, 1.45], F, sg, { z: 6, clip: ['face'], iris: D.iris, ink: D.ink, lw: lw * 0.95 });
    blush(fig, H([sg * 7.0 + tx * 0.7, 5.2 + fy]), 2.6, F.blush, { rgb: D.blush, clip: ['face'] });
    brow(fig, H([sg * 4.8 + tx, -5.6 + fy]), 3.6, F, sg, { z: 8.5, lw: lw * 0.75, color: D.hairLo });
    // 鱼尾纹、法令纹
    const cr = sg * 8.6 + tx * 0.8;
    fig.detail(Hs([[cr, -1.6 + fy], [cr + sg * 1.4, -2.4 + fy]]), wr);
    fig.detail(Hs([[cr, 0.4 + fy], [cr + sg * 1.5, 0.6 + fy]]), wr);
    fig.detail(Hs([[sg * 2.7 + tx, 4.9 + fy], [sg * 3.8 + tx, 7.0 + fy], [sg * 4.1 + tx, 9.4 + fy]]), { ...wr, lw: lw * 0.5 });
  }
  // 抬头纹
  fig.detail(Hs([[-4.5 + tx, -8.6], [0 + tx, -9.2], [4.5 + tx, -8.6]]), { ...wr, lw: lw * 0.4 });
  // 鼻子
  fig.detail(Hs([[0.6 + tx * 1.1, 0.8 + fy], [-0.4 + tx * 1.1, 4.0 + fy], [-1.6 + tx * 1.1, 4.8 + fy], [0.2 + tx * 1.1, 5.3 + fy], [1.7 + tx * 1.1, 4.6 + fy]]), { z: 6, lw: lw * 0.55, color: D.skinShade, clip: ['face'], profile: 'soft' });
  mouth(fig, H([tx * 0.9, 8.4 + fy]), 4.2, F, { z: 6, clip: ['face'], ink: D.ink, lw, inside: D.mouthIn, tongue: D.tongue });
  // 眼镜
  glasses(fig, H([-4.6 + tx, -0.2 + fy]), H([4.6 + tx, -0.2 + fy]), 3.5, { z: 8, lw: lw * 0.7, color: D.frame, temple: true });
  // 头发：往后梳，左边分缝
  const hair = [[-12.0, 1.0], [-13.3, -6], [-12.6, -12.6], [-8, -16.9], [0, -18.1], [8, -16.9], [12.6, -12.6], [13.3, -6], [12.0, 1.0], [10.6, -1.8], [10.2, -5.8], [7.6, -9.4], [2.5, -10.7], [-1.2, -10.1], [-5.2, -10.0], [-8.8, -8.2], [-10.4, -4.8], [-10.8, -1.4]];
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  for (const [a, b, c] of [[[-1.2, -10.2], [-3, -14], [-6, -16.4]], [[2, -10.6], [5, -14], [8.6, -15]], [[-5.5, -10], [-9, -11.8], [-11.6, -8]], [[6, -9.8], [10, -10.2], [12.2, -6.4]]])
    fig.detail(Hs([a, b, c]), { z: 7.1, lw: lw * 0.55, color: D.hairLo, clip: ['hair'] });
  fig.detail(Hs([[-7, -15.4], [-1, -16.8], [5.6, -16]]), { z: 7.1, lw: lw * 1.0, color: D.hairHi, clip: ['hair'], profile: 'taper' });
}

// ================================================================== 侧面（面朝 +x）：驼背、头往前探
export function side(ctx, P0, o = {}) {
  const P = pose(P0), D = NN;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 13, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const st = P.stoop;
  const hipC = [-1, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);
  const nl = D.nl, sh = P.shrug * 2.4;
  // 驼背：脖子根往前、往下
  const N = up([3.2 + st * 3.2, nl - 1.6 + st * 2.2]);
  const nod = P.head.nod;
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt + st * 0.08 + nod * 0.14), M.t(-1.5, D.faceC[1] - (nl - 1.6)));
  const H = (p) => M.ap(HM, p), Hs = (pts) => pts.map(H);
  const seated = P.seated;
  // ---- 腿
  for (const [side, dx, z, tone] of [['F', -2.0, -6, '#353a48'], ['N', 1.0, -4, D.pants]]) {
    const leg = P['leg' + side] || {};
    const hip = [dx - 1, D.hipY + P.bob];
    const foot = leg.foot || [dx + 1, -4.6];
    const knee = leg.knee || ik2(hip, foot, D.thigh, D.shin, 1).joint;
    const t = tube([hip, lerpP(hip, knee, 0.5), knee, lerpP(knee, foot, 0.5), foot], [[0, 7.2], [0.45, 5.6], [0.55, 5.2], [1, 4.6]], { capStart: 'round', capStartK: 0.4, capEnd: 'flat', step: 0.7 });
    fig.part('leg' + side, t.outline, { fill: tone, z, per: 2 });
    fig.detail([lerpP(hip, knee, 0.6), knee, lerpP(knee, foot, 0.4)].map((p) => [p[0] + 1.5, p[1]]), { z: z + 0.05, lw: lw * 0.45, color: '#2e3340', clip: ['leg' + side], profile: 'taper' });
    const fx = foot[0], fy = foot[1];
    fig.part('shoe' + side, [[fx - 4.6, fy - 0.6], [fx + 2.0, fy - 0.8], [fx + 7.6, fy + 1.0], [fx + 8.8, fy + 3.0], [fx + 7.8, fy + 4.2], [fx - 4.8, fy + 4.2], [fx - 5.2, fy + 1.6]], { fill: D.shoe, z: z + 0.1, inner: true });
    fig.part('sole' + side, [[fx - 5.4, fy + 3.4], [fx + 8.8, fy + 3.4], [fx + 9.2, fy + 4.8], [fx - 5.4, fy + 4.8]], { fill: D.sole, z: z + 0.2, inner: true, smooth: false });
  }
  // ---- 远侧胳膊
  armSide(fig, P, D, 'F', up, sh, -3, '#dcae90', lw, st);
  // ---- 脖子、发髻在后面
  fig.part('neck', [up([0 + st * 2.6, nl - 5 + st * 1.6]), up([6 + st * 2.8, nl - 4 + st * 2]), up([6.2 + st * 1.6, nl + 2.4]), up([-1.6 + st * 1.2, nl + 2.4])], { fill: D.skin, z: 0.5 });
  // ---- 衬衫（背弯成弧）
  const back = [[-3.4 + st * 1.6, -0.6 + st * 0.8], [-6.6 + st * 0.6, 2.6 + sh], [-8.4 - st * 1.0, 9], [-8.6 - st * 0.8, 18], [-8.8, 28], [-9.6, 37.6]].map(([x, y]) => up([x, nl + y]));
  const frontC = [[11.2, 38.2], [11.6, 30], [10.6, 22], [9.4, 13], [8.6 + st * 0.8, 6], [6.6 + st * 1.6, 1.6]].map(([x, y]) => up([x, nl + y]));
  const hemC = [[-4, D.hem + 1.4], [4, D.hem + 1.8]].map(up);
  fig.part('blouse', [...back, ...hemC, ...frontC], { fill: D.blouse, z: 0 });
  fig.paint((c) => flowers(c, up, -10, 12, nl + 3, D.hem + 2, D), { z: 0.1, clip: ['blouse'] });
  fig.part('collar', [[0.2 + st * 1.2, -0.4], [4.4 + st * 1.6, -1.2], [8.6 + st * 1.4, 2.4], [7.0 + st, 5.4], [2.6 + st, 3.6]].map(([x, y]) => up([x, nl + y])), { fill: D.blouse, z: 1, inner: true, per: 3 });
  for (let i = 0; i < 3; i++) { const b = up([9.0 + st * 0.4, nl + 10 + i * 9]); fig.detail(ellipsePts(b[0], b[1], 0.7, 0.7, 10), { z: 0.3, fill: D.flower, lw: lw * 0.4, color: D.blouseShade }); }
  // ---- 头：侧脸、圆眼镜、发髻
  const face = [[-4.5, -12], [5.2, -12.8], [8.8, -8.6], [10.0, -3.6], [10.2, -0.6], [12.4, 3.0], [11.6, 4.6], [10.6, 5.0], [10.9, 7.0], [10.2, 8.2], [10.4, 9.4], [9.0, 12.0], [4.6, 13.6], [0, 12.6], [-4.6, 8.6], [-6.0, 0]];
  fig.part('face', Hs(face), { fill: D.skin, z: 5 });
  const F = faceOf({ smile: 0.35, blush: 0.3, ...P.face });
  eye(fig, H([6.8, -0.4]), [0.9, 1.45], F, 1, { z: 6, clip: ['face'], iris: D.iris, ink: D.ink, lw: lw * 0.95 });
  blush(fig, H([5.2, 5.0]), 2.4, F.blush, { rgb: D.blush, clip: ['face'] });
  brow(fig, H([6.8, -5.4]), 2.8, F, 1, { z: 8.5, lw: lw * 0.75, color: D.hairLo });
  const wr = { z: 6.2, lw: lw * 0.45, color: D.wrinkle, clip: ['face'], profile: 'taper' };
  fig.detail(Hs([[3.2, -1.6], [2.0, -2.4]]), wr);
  fig.detail(Hs([[3.2, 0.6], [2.0, 0.8]]), wr);
  fig.detail(Hs([[8.6, 5.6], [8.0, 8.0], [8.6, 10.2]]), { ...wr, lw: lw * 0.5 });
  const mc = H([10.2, 8.3]);
  if (F.mouth > 0.1 || F.puff > 0.4) fig.detail(ellipsePts(mc[0] - 0.3, mc[1] + 0.4, 0.6 + F.mouth * 0.8, 0.8 + F.mouth * 1.3, 14), { z: 6, fill: D.mouthIn, lw: lw * 0.6, color: D.ink, clip: ['face'] });
  else fig.detail([H([10.8, 8.1 - F.smile * 0.2]), H([9.4, 8.3 - F.smile * 0.9])], { z: 6, lw: lw * 0.7, color: D.ink, clip: ['face'], profile: 'out' });
  // 眼镜：侧面是一个圆圈 + 镜腿到耳朵
  const gc = H([7.6, -0.4]);
  fig.detail(ellipsePts(gc[0], gc[1], 1.6, 3.3, 24, P.lean + P.head.tilt), { z: 8, fill: 'rgba(255,255,255,0.12)', lw: lw * 0.7, color: D.frame });
  fig.detail([H([6.0, -1.6]), H([2, -2.2]), H([-1.2, -1.2])], { z: 8, lw: lw * 0.7, color: D.frame, profile: 'flat' });
  // 耳朵
  fig.part('ear', Hs([[-2.4, -3.4], [-0.2, -3.6], [0.6, 0], [0.0, 4.4], [-1.4, 5.4], [-2.6, 3]]), { fill: D.skin, z: 7.6, inner: true, innerLw: 0.8 });
  fig.detail(Hs([[-1.0, -2.0], [-0.4, 0.6], [-1.1, 3.2]]), { z: 7.7, lw: lw * 0.5, color: D.skinShade, clip: ['ear'] });
  // 头发 + 低发髻 + 发簪
  const hair = [[9.2, -6.8], [9.6, -10], [7.2, -15], [1.5, -18.2], [-5.5, -18], [-11, -14.4], [-13.4, -8], [-13, -1], [-10, 5.4], [-6.2, 7.6], [-3.6, 4.4], [-3.4, -3.6], [1.5, -8.2], [6.2, -8.4]];
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  fig.part('bun', Hs(ellipsePts(-12.4, 3.6, 4.6, 4.2, 22)), { fill: D.hair, z: 7.2, inner: true });
  fig.detail(Hs([[-14.6, 1.6], [-12.4, 3.6], [-10.4, 6.0]]), { z: 7.25, lw: lw * 0.5, color: D.hairLo, clip: ['bun'] });
  fig.part('pin', Hs([[-17.8, 1.0], [-6.8, 5.6], [-6.6, 6.4], [-17.6, 1.8]]), { fill: D.pin, z: 7.3, smooth: false });
  for (const [a, b, c] of [[[8, -9], [2, -11.6], [-5, -12]], [[4, -14], [-3, -15.6], [-9.5, -12]], [[-3.6, -3], [-7.6, -4], [-11.4, -1]]])
    fig.detail(Hs([a, b, c]), { z: 7.1, lw: lw * 0.55, color: D.hairLo, clip: ['hair'] });
  fig.detail(Hs([[-6, -15.4], [0, -16.6], [5.2, -14.2]]), { z: 7.1, lw: lw * 1.0, color: D.hairHi, clip: ['hair'], profile: 'taper' });
  // ---- 近侧胳膊
  armSide(fig, P, D, 'N', up, sh, 2, D.skin, lw, st);
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
}

function armSide(fig, P, D, side, up, sh, z, tone, lw, st) {
  const A = P['arm' + side] || {};
  const S = up([side === 'N' ? 1.4 + st * 1.2 : -0.4 + st, D.shoulder[1] + sh + st * 1.2]);
  const W = A.hand || (side === 'N' ? [4.6, -67] : [0.4, -67.6]);
  const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? 1).joint;
  const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 2.8], [0.45, 2.4], [0.55, 2.2], [1, 1.75]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
  const zA = A.z ?? z;
  fig.part('arm' + side, arm.outline, { fill: tone, z: zA, inner: side === 'N' });
  const ua = Math.atan2(E[1] - S[1], E[0] - S[0]);
  if (side === 'N') {
    const sv = tube([[S[0] - Math.cos(ua) * 1.5, S[1] - Math.sin(ua) * 1.5], [S[0] + Math.cos(ua) * 9.5, S[1] + Math.sin(ua) * 9.5]], [[0, 4.2], [1, 3.6]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    fig.part('sleeve', sv.outline, { fill: D.blouse, z: zA + 0.5, inner: true });
    fig.paint((c) => flowers(c, (p) => p, S[0] - 6, S[0] + 6, S[1] - 3, S[1] + 11, D), { z: zA + 0.55, clip: ['sleeve'] });
  }
  const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
  const Mw = M.chain(M.t(W[0], W[1]), M.r(dir));
  const h = hand(fig, Mw, A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? false, skin: tone, z: zA + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
  if (side === 'N' && A.jade !== false) bracelet(fig, Mw, D.palm, { name: 'jade', z: zA + 0.4 });
  return h;
}

// ================================================================== 背面
export function back(ctx, P0, o = {}) {
  const P = pose(P0), D = NN;
  const fig = new Figure(ctx, { lw: inkFor(ctx), seed: o.seed ?? 17, ink: D.ink, defer: o.defer });
  const lw = fig.lw;
  const hipC = [0, D.hipY + P.bob];
  const up = (p) => rotP([p[0], p[1] + P.bob], P.lean, hipC);
  const sh = P.shrug * 2.6 + P.stoop * 1.2, nl = D.nl;
  const N = up([0, nl - 1.6 + P.stoop * 2.0]);
  const HM = M.chain(M.t(N[0], N[1]), M.r(P.lean + P.head.tilt), M.t(0, D.faceC[1] - (nl - 1.6)));
  const H = (p) => M.ap(HM, p), Hs = (pts) => pts.map(H);
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const foot = (P['leg' + side] || {}).foot || [sg * 7.4, -4.6];
    const pts = [[sg * 16.0, D.hem - 3], [sg * 0.6, D.hem - 3], [sg * 1.4, -56], [foot[0] - sg * 4.2, -24], [foot[0] - sg * 4.4, foot[1] + 0.4], [foot[0] + sg * 4.4, foot[1] + 0.4], [foot[0] + sg * 4.6, -26], [sg * 15.2, -52]];
    fig.part('pants' + side, pts, { fill: D.pants, z: -4, per: 3 });
    const fx = foot[0], fy = foot[1];
    fig.part('shoe' + side, [[fx - 4.2, fy + 0.4], [fx - 4.6, fy + 3.0], [fx + 4.6, fy + 3.0], [fx + 4.2, fy + 0.4]], { fill: D.shoe, z: -3.8, inner: true });
    fig.part('sole' + side, [[fx - 4.7, fy + 3.0], [fx - 4.5, fy + 4.8], [fx + 4.5, fy + 4.8], [fx + 4.7, fy + 3.0]], { fill: D.sole, z: -3.7, inner: true });
  }
  fig.part('neck', [up([-4.2, nl - 6]), up([4.2, nl - 6]), up([4.8, nl + 2]), up([-4.8, nl + 2])], { fill: D.skin, z: 0.5 });
  const rel = [[-5.4, 0.6], [-10.6, 1.4 + sh], [-13.8, 3.6 + sh], [-14.6, 11], [-14.8, 22], [-15.4, 31], [-16.2, 37.4]];
  const left = rel.map(([x, y]) => up([x, nl + y]));
  const right = rel.slice().reverse().map(([x, y]) => up([-x, nl + y]));
  const hem = [[-8, D.hem + 0.8], [0, D.hem + 1.2], [8, D.hem + 0.8]].map(up);
  fig.part('blouse', [...left, ...hem, ...right, up([0, nl + 1.4])], { fill: D.blouse, z: 0 });
  fig.paint((c) => flowers(c, up, -16, 16, nl + 2, D.hem + 2, D), { z: 0.1, clip: ['blouse'] });
  fig.detail([up([-9, nl + 2.6]), up([0, nl + 4.2]), up([9, nl + 2.6])], { z: 1, lw: lw * 0.7, color: D.ink, clip: ['blouse'], profile: 'soft' });
  fig.detail([up([-6, nl + 8]), up([0, nl + 10.6]), up([6, nl + 8])], { z: 0.2, lw: lw * 0.5, color: D.blouseShade, clip: ['blouse'], profile: 'taper' });
  for (const [side, sg] of [['L', -1], ['R', 1]]) {
    const A = P['arm' + side] || {};
    const S = up([sg * D.shoulder[0], D.shoulder[1] + sh]);
    const W = A.hand || [sg * 17.6, -64.5];
    const E = A.elbow || ik2(S, W, D.upper, D.fore, A.bend ?? sg).joint;
    const arm = tube([S, lerpP(S, E, 0.5), E, lerpP(E, W, 0.5), W], [[0, 2.8], [0.45, 2.4], [0.55, 2.2], [1, 1.75]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    const zA = A.z ?? 2;
    fig.part('arm' + side, arm.outline, { fill: D.skin, z: zA, inner: true });
    const ua = Math.atan2(E[1] - S[1], E[0] - S[0]);
    const sv = tube([S, [S[0] + Math.cos(ua) * 9.5, S[1] + Math.sin(ua) * 9.5]], [[0, 4.0], [1, 3.6]], { capStart: 'round', capEnd: 'flat', step: 0.5 });
    fig.part('sleeve' + side, sv.outline, { fill: D.blouse, z: zA + 0.5, inner: true });
    fig.paint((c) => flowers(c, (p) => p, S[0] - 6, S[0] + 6, S[1] - 3, S[1] + 11, D), { z: zA + 0.55, clip: ['sleeve' + side] });
    const dir = Math.atan2(W[1] - E[1], W[0] - E[0]) + (A.rot || 0);
    const Mw = M.chain(M.t(W[0], W[1]), M.r(dir));
    hand(fig, Mw, A.hp || 'relax', { size: D.palm, mirror: A.mirror ?? sg < 0, skin: D.skin, z: zA + 0.2, name: 'hand' + side, lw, line: D.skinShade, ink: D.ink });
    if (side === 'L') bracelet(fig, Mw, D.palm, { name: 'jade', z: zA + 0.4 });
  }
  for (const sg of [-1, 1]) fig.part('ear' + sg, Hs([[sg * 10.4, -3.4], [sg * 12.6, -2.8], [sg * 12.9, 1.0], [sg * 12.0, 4.8], [sg * 10.6, 4.4]]), { fill: D.skin, z: 4.2 });
  fig.part('nape', Hs([[-6.5, 4], [6.5, 4], [5.8, 13], [-5.8, 13]]), { fill: D.skin, z: 4.5 });
  const hair = [[-11.4, 4.6], [-13.3, -6], [-12.6, -12.6], [-8, -16.9], [0, -18.1], [8, -16.9], [12.6, -12.6], [13.3, -6], [11.4, 4.6], [7, 7.4], [0, 8.0], [-7, 7.4]];
  fig.part('hair', Hs(hair), { fill: D.hair, z: 7, per: 4 });
  for (const sg of [-1, 1]) for (const k of [0.3, 0.65]) fig.detail(Hs([[sg * 2 * k, -17.6], [sg * 9 * k + sg * 2, -10], [sg * 4.0, 1.2]]), { z: 7.1, lw: lw * 0.5, color: D.hairLo, clip: ['hair'] });
  fig.part('bun', Hs(ellipsePts(0, 3.4, 5.4, 4.6, 24)), { fill: D.hair, z: 7.2, inner: true });
  fig.detail(Hs([[-3.4, 1.6], [0, 3.6], [3.6, 2.0]]), { z: 7.25, lw: lw * 0.5, color: D.hairLo, clip: ['bun'] });
  fig.detail(Hs([[-3.0, 5.4], [0.4, 6.4], [3.4, 5.2]]), { z: 7.25, lw: lw * 0.5, color: D.hairLo, clip: ['bun'] });
  fig.part('pin', Hs([[-8.8, 0.4], [8.4, 3.6], [8.4, 4.4], [-8.8, 1.2]]), { fill: D.pin, z: 7.3, smooth: false });
  fig.detail(Hs([[-6, -15.4], [0, -16.6], [6, -15.4]]), { z: 7.1, lw: lw * 1.0, color: D.hairHi, clip: ['hair'], profile: 'taper' });
  if (o.light) { if (o.light.rim) fig.rim(o.light.rim); if (o.light.shade) fig.shadeFrom(o.light.shade); }
  fig.draw();
  return { fig, N, H };
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
