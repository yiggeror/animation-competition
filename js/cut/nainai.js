// 奶奶（剪纸片造型，侧面，面朝 +x）：
// 笑成一道弯的眼睛 + 眼角两道刻出来的笑纹、圆框眼镜是一圈细纸环、圆圆的鼻头、灰白头发刻着波纹往后梳成发髻插一根红珠发簪、
// 淡蓝衬衫镂空小碎花透出白底、深蓝宽裤、黑布鞋白鞋底、左腕一只绿玉镯；背有一点驼，头往前探。
import { fk, limbIK, ap, ap1, capsule, circle, petal4, pattern } from './rig.js';

export const NN = {
  skin: '#efcdae', skinFar: '#dcb595', cheek: '#e58a73', hair: '#cfc8bc', hairLine: '#8e877c', bun: '#c4bdb1',
  blouse: '#8fb0cf', blouseUnder: '#eef2f4', blouseFar: '#7698ba', pants: '#2f3a52', pantsFar: '#252e42',
  shoe: '#211c1a', sole: '#f1ebe0', frame: '#5b4636', pin: '#9c2f24', bead: '#d8402d', jade: '#7fbf9a',
  eye: '#2a1f1a', mouth: '#7a3028',
  upper: 16, fore: 15, thigh: 27, shin: 26,
};

const PARTS = [
  { name: 'hip', parent: null, at: [0, 0] },
  { name: 'torso', parent: 'hip', at: [0, -6] },
  { name: 'head', parent: 'torso', at: [4.0, -29.4] },
  { name: 'upF', parent: 'torso', at: [-1.6, -25.6] },
  { name: 'foreF', parent: 'upF', at: [0, 16] },
  { name: 'handF', parent: 'foreF', at: [0, 15] },
  { name: 'thighF', parent: 'hip', at: [-1.4, 0] },
  { name: 'shinF', parent: 'thighF', at: [0, 27] },
  { name: 'footF', parent: 'shinF', at: [0, 26] },
  { name: 'thighN', parent: 'hip', at: [1.2, 0] },
  { name: 'shinN', parent: 'thighN', at: [0, 27] },
  { name: 'footN', parent: 'shinN', at: [0, 26] },
  { name: 'upN', parent: 'torso', at: [1.0, -25.2] },
  { name: 'foreN', parent: 'upN', at: [0, 16] },
  { name: 'handN', parent: 'foreN', at: [0, 15] },
];

// 上身（腰为原点）：背上有一点驼，衬衫下摆盖过腰
const TORSO = [[-11.63, 7.0], [-11.86, -2.0], [-12.54, -11.0], [-13.91, -19.0], [-12.77, -25.4], [-8.89, -29.6], [-1.82, -31.0], [4.1, -30.2], [8.89, -25.4], [11.17, -17.0], [12.77, -8.0], [13.0, 0.0], [12.31, 7.4], [0.0, 8.4]];
const COLLAR = [[-2.6, -31.0], [4.2, -30.6], [8.6, -26.6], [6.2, -24.2], [1.8, -27.6]];
const NECK = [[-4.09, 3.58], [4.1, 3.58], [4.34, -5.84], [-3.84, -6.58]];
// 头（脖子根为原点）
const FACE = [[-12.02, -6.34], [-6.07, -0.38], [3.85, 0.36], [10.79, -0.63], [14.02, -3.11], [14.88, -5.34], [13.77, -6.83], [14.51, -8.32], [14.02, -9.81], [16.74, -11.79], [15.63, -14.4], [14.51, -16.26], [14.88, -18.98], [13.89, -22.95], [10.67, -27.17], [2.61, -29.9], [-7.06, -28.16], [-13.02, -21.22], [-14.26, -12.54]];
const HAIR = [[13.27, -22.7], [11.78, -27.17], [5.09, -31.14], [-4.58, -30.89], [-12.77, -25.68], [-15.5, -16.5], [-14.26, -7.33], [-9.54, -4.1], [-6.07, -8.07], [-3.84, -17.99], [3.1, -20.72], [8.56, -20.22], [11.29, -21.84]];
const HAIR_SLITS = [[[11.04, -25.18], [3.6, -28.16], [-5.08, -27.66], [-11.53, -22.46]], [[6.82, -22.21], [-1.36, -24.19], [-9.54, -20.22], [-12.77, -12.78]], [[-5.82, -18.74], [-10.54, -11.3], [-10.78, -7.08]]];
const EAR = [[-2.35, -18.49], [0.62, -18.98], [1.99, -14.52], [1.24, -9.56], [-0.12, -7.58], [-1.73, -8.69], [-2.6, -13.28]];
const BUN = circle(-15.3, -10.2, 5.6, 18);
const SHORT_SLEEVE = [[-4.2, -2.6], [0, -4.0], [4.4, -2.6], [4.6, 5.6], [3.6, 9.4], [-3.6, 9.4], [-4.6, 5.4]];
const HAND = [[-1.8, -0.3], [-2.2, 3.0], [-1.7, 6.2], [0, 7.8], [1.6, 6.9], [2.0, 4.2], [3.2, 3.0], [2.9, 1.1], [1.8, -0.3]];
const FIST = [[-1.9, -0.3], [-2.5, 2.4], [-2.1, 5.4], [0.2, 6.4], [2.5, 5.4], [2.9, 2.6], [1.8, -0.3]];
const SHOE = [[-4.6, -0.8], [2.0, -0.9], [8.0, 1.0], [9.4, 3.2], [8.2, 4.4], [-4.8, 4.4], [-5.4, 1.6]];
const SOLE = [[-5.4, 3.6], [9.4, 3.6], [9.8, 5.0], [-5.4, 5.0]];
// 宽裤腿
const THIGH = (len) => [[-6.0, -1.6], [-6.2, len * 0.5], [-5.4, len + 1], [5.2, len + 1], [5.8, len * 0.5], [5.8, -1.6]];
const SHIN = (len) => [[-5.2, -0.6], [-5.0, len * 0.6], [-5.6, len + 0.6], [5.4, len + 0.6], [4.8, len * 0.6], [5.0, -0.6]];

export function pieces(P) {
  const D = NN;
  const st = P.stoop ?? 1;
  const ang = {
    torso: (P.lean ?? 0) + 0.04 * st, head: 0.12 * st + (P.head?.tilt ?? 0) + (P.head?.nod ?? 0) * 0.15,
    thighN: 0.02, shinN: -0.02, footN: 0, thighF: -0.04, shinF: 0.03, footF: 0,
    upN: 0.18, foreN: -0.22, upF: 0.24, foreF: -0.26,
  };
  for (const side of ['N', 'F']) {
    const L = P['leg' + side];
    if (L?.angles) [ang['thigh' + side], ang['shin' + side], ang['foot' + side]] = L.angles;
    const A = P['arm' + side];
    if (A?.angles) [ang['up' + side], ang['fore' + side]] = A.angles;
  }
  const root = { x: P.x, y: P.y, s: P.s, flip: P.flip ?? 1 };
  let T = fk(PARTS, ang, root);
  let again = false;
  for (const side of ['N', 'F']) {
    const A = P['arm' + side];
    if (A?.hand) {
      // 握签子：签子从拳心穿过，所以要让"拳心"落在签子末端——先粗算一次，再按手的朝向把手腕往回挪
      let target = A.hand;
      for (let k = 0; k < 2; k++) {
        const S = ap1(T['up' + side].M, [0, 0]);
        const r = limbIK(S, target, D.upper * P.s, D.fore * P.s, A.bend ?? -1, T.torso.abs, root.flip);
        ang['up' + side] = r.upper; ang['fore' + side] = r.fore;
        T = fk(PARTS, ang, root);
        if (A.hp === 'grip') {
          const g = ap1(T['hand' + side].M, [0.2, 3.0]), w = ap1(T['hand' + side].M, [0, 0]);
          target = [A.hand[0] - (g[0] - w[0]), A.hand[1] - (g[1] - w[1])];
        }
      }
      again = true;
    }
  }
  if (again) T = fk(PARTS, ang, root);
  const F = { eye: 'smile', mouth: 'smile', ...(P.face || {}) };
  const out = [];
  const add = (name, part, pts, o = {}) => out.push({ name, pts: ap(T[part].M, pts), group: 'nn', ...o, holes: o.holes ? o.holes.map((h) => ap(T[part].M, h)) : undefined });
  const H = (pts) => ap(T.head.M, pts), tr = (part, p) => ap1(T[part].M, p);
  // ---- 远侧
  add('thighF', 'thighF', THIGH(D.thigh), { fill: D.pantsFar, z: 1, fiber: 0.35 });
  add('shinF', 'shinF', SHIN(D.shin), { fill: D.pantsFar, z: 1.1, fiber: 0.35 });
  add('footF', 'footF', SHOE, { fill: D.shoe, z: 1.2 });
  add('soleF', 'footF', SOLE, { fill: '#d9d2c6', z: 1.3, flat: true });
  add('upF', 'upF', capsule(D.upper, 5.4, 4.6), { fill: D.skinFar, z: 1.5, fiber: 0.25 });
  add('foreF', 'foreF', capsule(D.fore, 4.6, 3.9), { fill: D.skinFar, z: 1.6, fiber: 0.25 });
  add('handF', 'handF', P.armF?.hp === 'grip' ? FIST : HAND, { fill: D.skinFar, z: 1.7, fiber: 0.25 });
  add('sleeveF', 'upF', SHORT_SLEEVE, { fill: D.blouseFar, z: 1.8 });
  // ---- 身体
  add('thighN', 'thighN', THIGH(D.thigh), { fill: D.pants, z: 3, fiber: 0.35, slits: [{ pts: ap(T.thighN.M, [[1.6, 4], [2.0, D.thigh * 0.6], [1.4, D.thigh]]), w: 0.4, color: 'rgba(20,26,40,0.7)', sil: false }] });
  add('shinN', 'shinN', SHIN(D.shin), { fill: D.pants, z: 3.1, fiber: 0.35 });
  add('footN', 'footN', SHOE, { fill: D.shoe, z: 3.2, slits: [{ pts: ap(T.footN.M, [[4, 0.2], [6.6, 1.4]]), w: 0.35, color: 'rgba(90,80,70,0.8)', sil: false }] });
  add('soleN', 'footN', SOLE, { fill: D.sole, z: 3.3, flat: true });
  add('torso', 'torso', TORSO, {
    fill: D.blouse, under: D.blouseUnder, z: 4,
    holes: pattern(TORSO, 4.6, 0.95, (x, y, r, row) => petal4(x, y, r, 0.4 + row * 0.3), 1.6),
    slits: [{ pts: ap(T.torso.M, [[9.6, -24], [10.6, -12], [10.8, 6.6]]), w: 0.35, color: 'rgba(50,70,100,0.6)', sil: false }],
    dots: [-20, -12, -4, 4].map((y) => ({ c: ap1(T.torso.M, [9.2 + y * -0.02, y]), r: 0.75, fill: '#f6f3ee' })),
  });
  add('neck', 'head', NECK, { fill: D.skin, z: 3.9, fiber: 0.22 });
  add('collar', 'torso', COLLAR, { fill: D.blouse, z: 4.3, flat: false, lift: 0.5 });
  // ---- 头
  const slits = [], dots = [];
  if (F.eye === 'open' || F.eye === 'wide') {
    dots.push({ c: tr('head', [10.3, -13.53]), r: F.eye === 'wide' ? 1.25 : 1.0, sx: 0.85, sy: 1.0, fill: D.eye, sil: true, shadow: false });
    dots.push({ c: tr('head', [9.92, -14.02]), r: 0.3, fill: '#fffaf0', shadow: false });
  } else if (F.eye === 'squint') slits.push({ pts: H([[8.56, -13.28], [10.3, -13.78], [12.03, -13.28]]), w: 0.5, sil: true });
  else slits.push({ pts: H([[8.44, -12.78], [10.3, -14.4], [12.16, -12.91]]), w: 0.55, sil: true });   // 笑眼
  // 笑纹、法令纹、抬头纹
  slits.push({ pts: H([[6.82, -13.53], [5.34, -14.77]]), w: 0.32, color: 'rgba(150,100,80,0.75)', sil: false });
  slits.push({ pts: H([[6.82, -12.29], [5.34, -11.54]]), w: 0.32, color: 'rgba(150,100,80,0.75)', sil: false });
  slits.push({ pts: H([[12.28, -10.06], [11.41, -8.07], [11.78, -6.34]]), w: 0.32, color: 'rgba(150,100,80,0.75)', sil: false });
  slits.push({ pts: H([[10.54, -24.44], [12.78, -23.45]]), w: 0.28, color: 'rgba(150,100,80,0.6)', sil: false });
  // 眉毛（灰白）
  slits.push({ pts: H([[6.8, -15.8 - (F.brow ?? 0) * 0.6], [8.6, -16.5 - (F.brow ?? 0) * 0.8], [12.53, -18.24]]), w: 0.55, color: '#a49c90', sil: false });
  if (F.mouth === 'open') dots.push({ c: tr('head', [13.4, -6.34]), r: 0.95, sx: 0.8, sy: 1.1, fill: D.mouth, sil: true, shadow: false });
  else if (F.mouth === 'puff') dots.push({ c: tr('head', [14.26, -6.58]), r: 0.6, fill: D.mouth, sil: true, shadow: false });
  else slits.push({ pts: H([[13.77, -6.96], [12.78, -6.21], [11.78, -6.58]]), w: 0.45, sil: false });
  dots.push({ c: tr('head', [9.55, -7.82]), r: 2.1, fill: D.cheek, shadow: false });
  add('face', 'head', F.mouth === 'puff' ? FACE.map(([x, y]) => (x > 9 && y > -11 && y < -4 ? [x + 1.7, y] : [x, y])) : FACE, { fill: D.skin, z: 5, slits, dots, fiber: 0.22 });
  add('bun', 'head', BUN, { fill: D.bun, z: 5.3, slits: [{ pts: H([[-18.22, -13.78], [-15.74, -14.77], [-13.51, -12.29], [-15.5, -9.56], [-17.48, -11.3]]), w: 0.4, color: 'rgba(120,112,100,0.85)', sil: false }], lift: 0.6 });
  add('hair', 'head', HAIR, { fill: D.hair, z: 5.4, slits: HAIR_SLITS.map((s) => ({ pts: H(s), w: 0.42, color: 'rgba(130,122,110,0.9)', sil: false })), lift: 0.6 });
  add('pin', 'head', [[-22.94, -16.01], [-9.05, -8.82], [-8.8, -7.82], [-22.69, -15.02]], { fill: D.pin, z: 5.5, flat: true, dots: [{ c: tr('head', [-23.18, -15.76]), r: 0.9, fill: D.bead }] });
  add('ear', 'head', EAR, { fill: D.skin, z: 5.6, fiber: 0.22, slits: [{ pts: H([[-0.86, -16.26], [0.38, -13.53], [-0.37, -10.8]]), w: 0.3, color: 'rgba(170,110,90,0.8)', sil: false }] });
  // 眼镜：一圈细纸环（镜片是空的）+ 镜腿
  const ring = circle(11.0, -13.9, 4.0, 26).map(([x, y]) => [11.0 + (x - 11.0) * 0.62, y]);
  const ringIn = circle(11.0, -13.9, 3.45, 26).map(([x, y]) => [11.0 + (x - 11.0) * 0.55, y]);
  add('glasses', 'head', ring, { fill: D.frame, z: 5.8, holes: [ringIn], noShadow: false, lift: 0.3, noSilHoles: false });
  add('temple', 'head', [[9.0, -15.2], [1.2, -15.6], [1.2, -14.9], [9.0, -14.5]], { fill: D.frame, z: 5.75, flat: true, lift: 0.3 });
  // ---- 近侧胳膊
  add('upN', 'upN', capsule(D.upper, 5.4, 4.6), { fill: D.skin, z: 6, fiber: 0.25 });
  add('foreN', 'foreN', capsule(D.fore, 4.6, 3.9), { fill: D.skin, z: 6.1, fiber: 0.25 });
  add('handN', 'handN', P.armN?.hp === 'grip' ? FIST : HAND, { fill: D.skin, z: 6.2, fiber: 0.25 });
  add('jade', 'foreN', [[-2.6, D.fore - 1.8], [2.6, D.fore - 1.8], [2.8, D.fore - 0.4], [-2.8, D.fore - 0.4]], { fill: D.jade, z: 6.25, lift: 0.3 });
  add('sleeveN', 'upN', SHORT_SLEEVE, { fill: D.blouse, under: D.blouseUnder, z: 6.3, holes: [petal4(0, 3, 0.95, 0.5)] });
  for (const pc of out) {
    if (pc.slits) pc.slits = pc.slits.map((sl) => ({ ...sl, w: sl.w * P.s }));
    if (pc.dots) pc.dots = pc.dots.map((d) => ({ ...d, r: d.r * P.s }));
  }
  return { pieces: out, T };
}
