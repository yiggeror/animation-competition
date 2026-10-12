// 小满（剪纸片造型，侧面，面朝 +x）。造型语言取自民间剪纸和年画娃娃：
// 圆圆的红脸蛋（一个正圆）、剪出来的杏仁眼、扇贝边的齐刘海、刻着发丝的双马尾和红绒球、
// 镂空梅花的黄裙子透出底下浅一层的黄、白色扇贝领、红色小凉鞋。
// 身体由一片片纸铆在一起：髋 → 上身 → 头；肩 → 上臂 → 前臂 → 手；髋 → 大腿 → 小腿 → 脚。单位：厘米，原点在髋关节。
import { fk, limbIK, ap, ap1, capsule, circle, plum, pattern } from './rig.js';

export const XM = {
  skin: '#f6d6b9', skinFar: '#e6bfa0', cheek: '#e0503b', hair: '#2b1e19', hairLine: '#5a463c',
  dress: '#efbf2e', dressUnder: '#fbe6a2', dressFar: '#d9a521', collar: '#fdf8ec', bobble: '#d8402d',
  sandal: '#d8402d', eye: '#1e1512', white: '#fffaf0', mouth: '#8a2f26',
  upper: 10, fore: 9, thigh: 14, shin: 12.5,
};

// 骨架（铆点位置都在父片的局部坐标里）
const PARTS = [
  { name: 'hip', parent: null, at: [0, 0] },
  { name: 'torso', parent: 'hip', at: [0, -8] },
  { name: 'head', parent: 'torso', at: [1.2, -22.6] },
  { name: 'pigF', parent: 'head', at: [-7.2, -24.6] },
  { name: 'pigN', parent: 'head', at: [-9.6, -20.6] },
  { name: 'upF', parent: 'torso', at: [-0.8, -19.6] },
  { name: 'foreF', parent: 'upF', at: [0, 10] },
  { name: 'handF', parent: 'foreF', at: [0, 9] },
  { name: 'thighF', parent: 'hip', at: [-0.8, 0] },
  { name: 'shinF', parent: 'thighF', at: [0, 14] },
  { name: 'footF', parent: 'shinF', at: [0, 12.5] },
  { name: 'thighN', parent: 'hip', at: [0.8, 0] },
  { name: 'shinN', parent: 'thighN', at: [0, 14] },
  { name: 'footN', parent: 'shinN', at: [0, 12.5] },
  { name: 'upN', parent: 'torso', at: [0.6, -19.4] },
  { name: 'foreN', parent: 'upN', at: [0, 10] },
  { name: 'handN', parent: 'foreN', at: [0, 9] },
];

// ---- 各片的形状（局部坐标）
const TORSO = [[-6.0, 0.6], [-6.4, -8], [-6.0, -15], [-4.6, -19.6], [-2.6, -21.9], [2.6, -22.3], [4.7, -20], [6.0, -16], [6.3, -9], [5.9, 0.6]];
const SKIRT_STAND = [[-6.0, -0.6], [-8.4, 7], [-11.6, 17.6], [-5, 19.2], [2.6, 19.6], [9.6, 19.0], [12.8, 17.4], [9.0, 7], [6.0, -0.6]];
const SKIRT_SIT = [[-6.0, -0.6], [-8.6, 5.6], [-9.0, 9.6], [-3, 11.0], [6, 11.0], [12.8, 10.6], [15.0, 7.6], [14.0, 4.4], [8.6, 4.0], [6.0, -0.6]];
const SASH = [[-6.3, -1.6], [6.3, -1.4], [6.4, 1.3], [-6.4, 1.1]];
const BOW = [[-6.0, 0], [-10.4, -2.2], [-11.2, 1.2], [-9.6, 4.8], [-6.8, 1.6]];
const COLLAR = [[-1.6, -22.5], [2.9, -22.8], [5.3, -21.1], [5.1, -18.4], [2.5, -17.9], [0.2, -19.5]];
const SLEEVE = [[-3.3, -2.0], [0, -3.4], [3.5, -2.0], [3.9, 2.5], [2.7, 5.6], [-2.7, 5.6], [-3.9, 2.4]];
const NECK = [[-2.3, 1.2], [2.7, 1.2], [3.1, -5], [-2.5, -5.5]];
const FACE = [[-10.47, -8.83], [-7.05, -3.13], [3.78, -1.53], [9.48, -1.08], [14.84, -3.13], [16.43, -5.87], [15.98, -6.78], [16.78, -7.92], [16.21, -9.51], [17.8, -10.43], [16.09, -12.25], [15.64, -14.53], [15.75, -16.81], [14.84, -20.23], [11.76, -25.36], [4.35, -29.92], [-4.77, -29.35], [-11.61, -23.65], [-13.32, -15.67]];
// 头发：扇贝边的齐刘海停在眉毛上面，后面一直包到后颈，在耳朵前面留出鬓角
const HAIR = [[15.64, -19.55], [14.5, -18.63], [13.58, -20.12], [12.22, -18.75], [10.96, -20.34], [9.48, -19.2], [8.23, -20.69], [6.4, -19.77], [3.44, -20.91], [0.47, -19.09], [-2.72, -17.49], [-4.31, -12.25], [-5.45, -8.37], [-7.96, -4.5], [-12.29, -5.18], [-15.26, -11.11], [-15.71, -19.09], [-11.84, -27.75], [-3.63, -32.31], [5.49, -32.54], [13.01, -28.67], [15.75, -23.65]];
const HAIR_SLITS = [
  [[11.87, -27.75], [4.35, -30.26], [-4.2, -29.35], [-10.24, -25.25]], [[7.31, -24.11], [-0.21, -25.93], [-7.73, -23.65], [-12.52, -17.49]],
  [[-7.96, -19.77], [-12.29, -12.93], [-12.29, -7.92]],
];
const EAR = circle(0.9, -13.0, 3.0, 14);
const PIG = [[-2.6, 0], [-4.4, 5], [-4.2, 10.2], [-2.5, 14.4], [0, 15.6], [2.5, 14.0], [3.9, 9.8], [3.9, 5], [2.7, 0]];
const PIG_SLITS = [[[0.2, 3.2], [-0.2, 8.4], [0.6, 12.8]], [[-2.2, 6], [-2.0, 10.4]]];
const HAND_RELAX = [[-1.35, -0.2], [-1.7, 2.5], [-1.3, 5.0], [0, 6.3], [1.25, 5.5], [1.6, 3.4], [2.5, 2.4], [2.3, 0.9], [1.35, -0.2]];
const HAND_FIST = [[-1.4, -0.2], [-1.9, 1.8], [-1.6, 4.2], [0.2, 5.0], [1.9, 4.2], [2.2, 2.0], [1.4, -0.2]];
const HAND_OPEN = [[-1.4, -0.2], [-1.8, 2.6], [-2.4, 5.4], [-1.9, 7.6], [-0.9, 6.0], [-0.6, 8.2], [0.3, 6.2], [0.6, 8.0], [1.2, 5.6], [1.7, 7.0], [2.1, 4.8], [3.6, 3.6], [2.6, 2.2], [1.4, -0.2]];
const FOOT = [[-2.2, -0.8], [1.5, -0.3], [6.2, 1.4], [7.4, 2.8], [6.6, 3.6], [-2.4, 3.6], [-2.8, 1.5]];
const SOLE = [[-3.0, 3.0], [7.6, 3.0], [7.8, 4.5], [-3.0, 4.5]];

const FACE0 = { eye: 'open', mouth: 'smile', look: 0, cheek: 1 };

// pose: { x, y, s, flip, lean, seated, head:{tilt}, armN/armF:{hand:[x,y] 世界坐标 | angles:[u,f]}, legN/legF:{angles:[t,s,f]}, pig:[f,n], face:{} }
export function pieces(P) {
  const D = XM;
  const seated = !!P.seated;
  const ang = {
    torso: P.lean ?? 0,
    head: (P.head?.tilt ?? 0),
    pigN: 1.05 + (P.pig?.[1] ?? 0), pigF: 1.25 + (P.pig?.[0] ?? 0),
    thighN: seated ? -1.5 : 0.03, shinN: seated ? 1.45 : -0.03, footN: seated ? 0.05 : 0,
    thighF: seated ? -1.52 : -0.05, shinF: seated ? 1.5 : 0.04, footF: seated ? 0.02 : 0,
    upN: 0.12, foreN: -0.15, upF: 0.18, foreF: -0.2,
  };
  for (const side of ['N', 'F']) {
    const L = P['leg' + side];
    if (L?.angles) [ang['thigh' + side], ang['shin' + side], ang['foot' + side]] = L.angles;
    const A = P['arm' + side];
    if (A?.angles) [ang['up' + side], ang['fore' + side]] = A.angles;
  }
  const root = { x: P.x, y: P.y, s: P.s, flip: P.flip ?? 1 };
  let T = fk(PARTS, ang, root);
  // 手的目标（世界坐标）→ 用 IK 算上臂、前臂的角度，再重新解一次
  let again = false;
  for (const side of ['N', 'F']) {
    const A = P['arm' + side];
    if (A?.hand) {
      const S = ap1(T['up' + side].M, [0, 0]);
      const r = limbIK(S, A.hand, D.upper * P.s, D.fore * P.s, A.bend ?? -1, T.torso.abs, root.flip);
      ang['up' + side] = r.upper; ang['fore' + side] = r.fore; again = true;
    }
  }
  if (again) T = fk(PARTS, ang, root);
  const F = { ...FACE0, ...(P.face || {}) };
  const out = [];
  const add = (name, part, pts, o) => out.push({ name, pts: ap(T[part].M, pts), group: 'xm', ...o, holes: o.holes ? o.holes.map((h) => ap(T[part].M, h)) : undefined });
  const tr = (part, p) => ap1(T[part].M, p);
  // ---- 远侧（颜色稍暗，在后面）
  add('pigF', 'pigF', PIG, { fill: D.hair, z: 1, slits: PIG_SLITS.map((s) => ({ pts: ap(T.pigF.M, s), w: 0.45, color: 'rgba(90,70,60,0.8)', sil: false })) });
  add('thighF', 'thighF', capsule(D.thigh, 7.2, 5.8), { fill: D.skinFar, z: 2, fiber: 0.25 });
  add('shinF', 'shinF', shin(D.shin), { fill: D.skinFar, z: 2.1, fiber: 0.25 });
  add('footF', 'footF', FOOT, { fill: D.skinFar, z: 2.2 });
  add('soleF', 'footF', SOLE, { fill: '#b8341f', z: 2.3, flat: true });
  add('upF', 'upF', capsule(D.upper, 4.2, 3.6), { fill: D.skinFar, z: 2.5, fiber: 0.25 });
  add('foreF', 'foreF', capsule(D.fore, 3.6, 3.0), { fill: D.skinFar, z: 2.6, fiber: 0.25 });
  add('handF', 'handF', handShape(P.armF?.hp), { fill: D.skinFar, z: 2.7, fiber: 0.25 });
  add('sleeveF', 'upF', SLEEVE, { fill: D.dressFar, z: 2.8 });
  // ---- 身体
  const skirt = seated ? SKIRT_SIT : SKIRT_STAND;
  add('skirt', 'torso', skirt, { fill: D.dress, under: D.dressUnder, z: 4, holes: pattern(skirt, 4.6, 0.85, (x, y, r, row) => plum(x, y, r, row * 0.6)).map((h) => h), lift: 1 });
  add('torso', 'torso', TORSO, { fill: D.dress, under: D.dressUnder, z: 4.5, holes: pattern(TORSO, 4.4, 0.8, (x, y, r, row) => plum(x, y, r, row)) });
  add('sash', 'torso', SASH, { fill: D.bobble, z: 4.7, lift: 0.5 });
  add('bow', 'torso', BOW, { fill: D.bobble, z: 4.75, lift: 0.6, slits: [{ pts: ap(T.torso.M, [[-7, 0.4], [-9.6, 0.2]]), w: 0.3, color: 'rgba(120,30,20,0.7)', sil: false }] });
  add('neck', 'head', NECK, { fill: D.skin, z: 4.4 });
  add('collar', 'torso', COLLAR, { fill: D.collar, z: 4.8, slits: [{ pts: ap(T.torso.M, [[1.6, -19.0], [3.4, -18.6], [4.6, -19.6]]), w: 0.25, color: 'rgba(160,140,110,0.7)' }] });
  // ---- 头
  const H = (pts) => ap(T.head.M, pts);
  const faceSlits = [], dots = [];
  const eyeC = [11.6 + (F.look ?? 0) * 0.3, -14.0];
  if (F.eye === 'happy') faceSlits.push({ pts: H([[9.94, -13.39], [11.65, -14.99], [13.36, -13.62]]), w: 0.55 });
  else if (F.eye === 'closed') faceSlits.push({ pts: H([[9.94, -14.07], [11.65, -13.16], [13.36, -13.96]]), w: 0.5 });
  else {
    const big = F.eye === 'wide' ? 1.25 : F.eye === 'squint' ? 0.55 : 1;
    dots.push({ c: tr('head', eyeC), r: 2.35, sx: 0.9, sy: 0.8 * big, rot: (P.flip ?? 1) * -0.2, fill: D.eye, sil: true, shadow: false });
    if (big > 0.6) dots.push({ c: tr('head', [eyeC[0] - 0.6, eyeC[1] - 0.6 * big]), r: 0.6, fill: D.white, shadow: false });
    faceSlits.push({ pts: H([[9.59, -14.42], [8.23, -15.9]]), w: 0.45, sil: false });
    faceSlits.push({ pts: H([[10.28, -15.44], [9.59, -17.04]]), w: 0.4, sil: false });
  }
  const bl = F.brow ?? 0;
  faceSlits.push({ pts: H([[9.0, -15.9 - bl * 0.6], [10.6, -16.6 - bl * 0.8], [12.2, -16.1 - bl * 0.5 + (F.frown ?? 0) * 0.8]]), w: 0.6, sil: false });
  if (F.mouth === 'open') dots.push({ c: tr('head', [15.07, -6.89]), r: 0.95, sx: 0.8, sy: 1.1, fill: D.mouth, sil: true, shadow: false });
  else if (F.mouth === 'pout') faceSlits.push({ pts: H([[15.52, -6.55], [14.5, -7.12]]), w: 0.45 });
  else faceSlits.push({ pts: H([[15.64, -7.58], [14.72, -6.78], [13.7, -7.23]]), w: 0.5, sil: false });
  if (F.cheek) dots.push({ c: tr('head', [10.51, -8.15]), r: 2.7, fill: D.cheek, shadow: false });
  add('face', 'head', FACE, { fill: D.skin, z: 5, slits: faceSlits, dots, fiber: 0.22 });
  add('hair', 'head', HAIR, { fill: D.hair, z: 5.5, slits: HAIR_SLITS.map((s) => ({ pts: H(s), w: 0.5, color: 'rgba(120,98,86,0.9)', sil: false })), lift: 0.6 });
  add('ear', 'head', EAR, { fill: D.skin, z: 5.6, slits: [{ pts: H([[1.27, -14.53], [-0.1, -13.62], [0.59, -11.79], [1.5, -12.71]]), w: 0.3, color: 'rgba(170,110,90,0.8)' }], lift: 0.4 });
  add('pigN', 'pigN', PIG, { fill: D.hair, z: 5.8, slits: PIG_SLITS.map((s) => ({ pts: ap(T.pigN.M, s), w: 0.45, color: 'rgba(120,98,86,0.9)', sil: false })) });
  add('bobN', 'pigN', circle(0, 0.6, 2.5, 16), { fill: D.bobble, z: 5.9, lift: 0.5, dots: [{ c: ap1(T.pigN.M, [-0.8, -0.2]), r: 0.6, fill: 'rgba(255,240,220,0.9)', shadow: false }] });
  add('bobF', 'pigF', circle(0, 0.6, 2.2, 14), { fill: '#b8341f', z: 1.1 });
  // 呆毛
  add('cowlick', 'head', [[3.89, -32.09], [5.03, -35.51], [7.54, -36.87], [9.59, -35.73], [8.45, -34.82], [6.86, -35.28], [5.95, -33.23], [5.95, -31.86]], { fill: D.hair, z: 5.45 });
  // ---- 近侧四肢
  add('thighN', 'thighN', capsule(D.thigh, 7.2, 5.8), { fill: D.skin, z: 3.6, fiber: 0.25 });
  add('shinN', 'shinN', shin(D.shin), { fill: D.skin, z: seated ? 4.2 : 3.7, fiber: 0.25 });
  add('footN', 'footN', FOOT, { fill: D.skin, z: 4.25, slits: [{ pts: ap(T.footN.M, [[0.6, -0.4], [1.8, 1.2], [2.6, 3.0]]), w: 0.55, color: D.sandal }] });
  add('soleN', 'footN', SOLE, { fill: D.sandal, z: 4.3, flat: true });
  add('upN', 'upN', capsule(D.upper, 4.2, 3.6), { fill: D.skin, z: 6, fiber: 0.25 });
  add('foreN', 'foreN', capsule(D.fore, 3.6, 3.0), { fill: D.skin, z: 6.1, fiber: 0.25 });
  add('handN', 'handN', handShape(P.armN?.hp), { fill: D.skin, z: 6.2, fiber: 0.25 });
  add('sleeveN', 'upN', SLEEVE, { fill: D.dress, under: D.dressUnder, z: 6.3, holes: [plum(0, 1.2, 0.8, 0.3)] });
  // 刻缝宽度、小圆片半径是厘米 → 换成画面像素
  for (const pc of out) {
    if (pc.slits) pc.slits = pc.slits.map((sl) => ({ ...sl, w: sl.w * P.s }));
    if (pc.dots) pc.dots = pc.dots.map((d) => ({ ...d, r: d.r * P.s }));
  }
  return { pieces: out, T };
}
// 小腿：膝盖下面鼓一点（腿肚），往脚踝收
function shin(len) { return [[-2.6, -0.6], [-2.9, len * 0.3], [-2.2, len * 0.75], [-1.7, len + 0.4], [1.7, len + 0.6], [2.0, len * 0.7], [2.5, len * 0.25], [2.4, -0.8]]; }
function handShape(hp) { const h = hp === 'fist' || hp === 'grip' ? HAND_FIST : hp === 'open' ? HAND_OPEN : HAND_RELAX; return h.map(([x, y]) => [x * 1.2, y * 1.2]); }
