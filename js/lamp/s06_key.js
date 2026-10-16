// 第 6 场 · 鹤亮相（"一盏灯照亮的世界"关键镜头）
// 停电的夜里，屋子全黑。奶奶在晾衣铁丝上挂了一条床单，两边挂着被子和毯子挡光，自己提着马灯在后面演皮影。
// 镜头在小满右后方、和她坐着的眼睛差不多高：她在左前景，侧脸朝右，抬头看床单上的鹤。
// 能看见的东西几乎都只被三种光照亮：床单（面光源）、从布帘上下沿和缝里漏出来的马灯光、右墙窗户斜进来的月光。
import { GL } from './gl.js';
import * as SH from './shaders.js';
import { sheetImage } from '../shadowplay.js';
import { makeCrane } from './crane.js';
import { makePond, makeWillow } from './scenery.js';
import * as XMC from './xiaoman.js';
import { Cards } from './cards.js';
import { RIG16, loadRig, pose16, layers16 } from './xm_rig.js';

export const DURATION = 5;

// ---------------------------------------------------------------- 场景（米）
export const S = {
  room: [[-1.6, -4.4, 0], [4.4, 1.6, 2.55]],
  sheet: { x0: 0.25, x1: 2.35, z0: 0.12, z1: 1.94 },
  quiltL: [-1.7, 0.232, 0.10, 1.95],
  quiltR: [2.368, 4.5, 0.14, 1.95],
  wireZ: 1.99, pin0: 0.30, pinDx: 0.35,
  lamp: { x: 1.52, y: 0.70, z: 1.30, core: 0.011, globe: 0.055, rgb: [1.0, 0.58, 0.24] },
  moon: { dir: [-0.88, 0.18, 0.44], rgb: [0.30, 0.42, 0.78] },
  window: [-2.3, -1.0, 0.9, 1.9],
  beams: [-1.7, 0.75, 1.45], beamZ0: 2.44,
  occ: [], occBack: [],
  cardSheetGain: '1.8', sheetTau: '0.16', sheetHot: '0.46', bounce: '0.10',
};
// 奶奶在床单后面、马灯左边（只看得见腰以下）：挡住马灯照后墙和地面的光
export const NN = [1.05, 0.88];
S.occBack = [[NN[0] - 0.06, NN[1], 0.12, 0.065], [NN[0] - 0.06, NN[1], 0.35, 0.07], [NN[0] - 0.06, NN[1], 0.6, 0.08],
  [NN[0] + 0.07, NN[1] + 0.02, 0.12, 0.065], [NN[0] + 0.07, NN[1] + 0.02, 0.35, 0.07], [NN[0] + 0.07, NN[1] + 0.02, 0.6, 0.08],
  [NN[0], NN[1], 0.85, 0.16], [NN[0] + 0.03, NN[1] - 0.02, 1.1, 0.17], [NN[0] + 0.06, NN[1] - 0.05, 1.35, 0.16], [NN[0] + 0.1, NN[1] - 0.06, 1.6, 0.12]];
// 小满坐在小板凳上，朝着床单上的鹤（右前方）。她是一张竖着的"卡片"：局部坐标（厘米，x 朝前、y 朝上，原点在凳面中心）→ 世界坐标
export const XM = { p: [0.50, -1.45], gaze: [0.62, 1.0], seat: 0.22 };
const XF = (() => { const g = Math.hypot(...XM.gaze); return [XM.gaze[0] / g, XM.gaze[1] / g]; })();
export const xmWorld = ([x, y], side = 0) => [XM.p[0] + (XF[0] * x) / 100 + XF[1] * side, XM.p[1] + (XF[1] * x) / 100 - XF[0] * side, XM.seat + y / 100];
// 挡光用的球：从她的骨架生成（床单光、月光在地上的软影子）
function xmProxy() {
  const J = XMC.parts(() => [0, 0]).joints;
  const L = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const sp = (p, r, side = 0) => [...xmWorld(p, side), r];
  return [sp(J.head, 0.115), sp(L(J.head, J.neck0, 0.6), 0.06), sp(J.chest, 0.11), sp(J.belly, 0.115), sp(J.hip, 0.12),
    sp(L(J.hip, J.knee, 0.5), 0.065, 0.06), sp(L(J.hip, J.knee, 0.5), 0.065, -0.06), sp(J.knee, 0.055, 0.06), sp(J.knee, 0.055, -0.06),
    sp(L(J.knee, J.ankle, 0.5), 0.045, 0.06), sp(L(J.knee, J.ankle, 0.5), 0.045, -0.06), sp([0, -11], 0.12)];
}
S.occ = xmProxy();
export const CRANE_ROOT = [1.36, 0.66];
// 两根签子：接在鹤身子后部（翅膀底下）和第 4 节脖子上；hand(root) 是第 6 场默认的手端 [x, z, 离床单的距离]
export const RODS = [
  { part: 'body', at: [-75, 6], hand: (root) => [root[0] - 0.13, root[1] - 0.10, 0.42] },
  { part: 'neck3', at: [10, 0], hand: (root) => [root[0] + 0.20, root[1] + 0.10, 0.42] },
];

// ---------------------------------------------------------------- 镜头
export function camera(W, H, o = {}) {
  const C = o.pos || [1.48, -3.013, 0.34], T = o.target || [0.75, 0.0, 1.0], hfov = o.hfov || 60;
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const fwd = nrm(sub(T, C)), right = nrm(cross(fwd, [0, 0, 1])), up = cross(right, fwd);
  const focal = (W / 2) / Math.tan((hfov * Math.PI) / 360);
  const project = (P) => {
    const d = sub(P, C);
    const z = d[0] * fwd[0] + d[1] * fwd[1] + d[2] * fwd[2];
    const x = d[0] * right[0] + d[1] * right[1] + d[2] * right[2];
    const y = d[0] * up[0] + d[1] * up[1] + d[2] * up[2];
    return [W / 2 + (x / z) * focal, H / 2 - (y / z) * focal, Math.hypot(...d), focal / z];
  };
  return { C, fwd, right, up, focal, project };
}

// ---------------------------------------------------------------- 鹤的姿势
const NECK_UP = [1.25, 0.10, 0.08, 0.06, 0.03, 0.0, -0.04, -0.07, -0.09, -0.10, -0.09, -0.07, -0.55];
const NECK_LOW = [0.80, 0.16, 0.14, 0.12, 0.08, 0.02, -0.06, -0.14, -0.22, -0.28, -0.30, -0.26, -0.15];
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const backOut = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); const c = 1.4; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
// 鹤亮相：先低着头（像在水里找东西），1.0 秒起慢慢把脖子扬起来（略冲过头再回来），然后左右看看
export const raiseAt = (t) => backOut(1.0, 2.5, t);
export function cranePose(t) {
  // 预备：扬起之前脖子先往下沉一点（0.55～1.05 秒），再扬起、略冲过头、收住
  const prep = t > 0.55 && t < 1.15 ? Math.sin(Math.PI * Math.min(1, (t - 0.55) / 0.6)) ** 2 : 0;
  const r = raiseAt(t) - 0.14 * prep, angles = {};
  for (let i = 0; i < 12; i++) angles['neck' + i] = NECK_LOW[i] + (NECK_UP[i] - NECK_LOW[i]) * r;
  const look = t > 2.5 ? 0.07 * Math.sin((t - 2.5) * 2.2) * Math.exp(-(t - 2.5) * 0.25) : 0;
  // 抬起的那条腿没装签子，身子一动它就跟着晃（惯性），慢慢停下来——皮影动作的"韵味"
  const swing = 0.10 * Math.sin((t - 1.0) * 5.2) * Math.exp(-Math.max(0, t - 1.0) * 0.9) * (t > 1.0 ? 1 : 0);
  Object.assign(angles, { head: NECK_LOW[12] + (NECK_UP[12] - NECK_LOW[12]) * r + look,
    tibia_near: 1.15 + swing, tarsus_near: -2.5 - swing * 0.6, foot_near: 1.15 + swing * 0.4, tibia_far: -0.05, tarsus_far: 0.02, foot_far: 0.03 });
  return { angles, rootAngle: 0.04 + 0.05 * (1 - Math.min(1, r)), facing: 1 };
}
// ---------------------------------------------------------------- 被子、毯子的花色（2D 画）
function quiltTex(kind) {
  const W = 512, H = 768, c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  let s = kind === 'L' ? 11 : 23;
  const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  if (kind === 'L') {
    // 大红牡丹花被面
    x.fillStyle = '#b3202a'; x.fillRect(0, 0, W, H);
    for (let i = 0; i < 26; i++) {
      const cx = rnd() * W, cy = rnd() * H, r = 34 + rnd() * 40;
      x.fillStyle = '#2f7a4a';
      for (let k = 0; k < 4; k++) { const a = rnd() * 6.28; x.beginPath(); x.ellipse(cx + Math.cos(a) * r * 1.1, cy + Math.sin(a) * r * 1.1, r * 0.7, r * 0.28, a, 0, 6.28); x.fill(); }
      const cols = rnd() < 0.5 ? ['#f2a1b5', '#e8607f', '#fbe3e8'] : ['#f6d26b', '#e79a3a', '#fff1c8'];
      for (let ring = 0; ring < 3; ring++) {
        x.fillStyle = cols[ring];
        const rr = r * (1 - ring * 0.3), n = 7 - ring;
        for (let k = 0; k < n; k++) { const a = (k / n) * 6.28 + ring * 0.4; x.beginPath(); x.ellipse(cx + Math.cos(a) * rr * 0.45, cy + Math.sin(a) * rr * 0.45, rr * 0.5, rr * 0.36, a, 0, 6.28); x.fill(); }
      }
      x.fillStyle = '#f3d36a'; x.beginPath(); x.arc(cx, cy, r * 0.12, 0, 6.28); x.fill();
    }
  } else {
    // 毛毯：蓝绿格子
    x.fillStyle = '#2f5d6e'; x.fillRect(0, 0, W, H);
    for (let i = 0; i < W; i += 96) { x.fillStyle = 'rgba(160,60,50,0.75)'; x.fillRect(i + 20, 0, 18, H); x.fillStyle = 'rgba(230,200,120,0.5)'; x.fillRect(i + 60, 0, 5, H); }
    for (let j = 0; j < H; j += 96) { x.fillStyle = 'rgba(160,60,50,0.6)'; x.fillRect(0, j + 20, W, 18); x.fillStyle = 'rgba(230,200,120,0.4)'; x.fillRect(0, j + 60, W, 5); }
  }
  // 布纹
  for (let i = 0; i < 6000; i++) { x.fillStyle = `rgba(0,0,0,${rnd() * 0.08})`; x.fillRect(rnd() * W, rnd() * H, 2, 1); }
  return c;
}

// ---------------------------------------------------------------- 渲染
let G = null, crane = null, cranePal = null, QUILTS = null, CARDS = null, POND = null, WILLOW = null, XMI = null;
// 小满：呼吸；跟着鹤抬头（慢半拍）；鹤扬起头那一下看呆了——眼睛睁大、眉毛抬起、嘴张开，身子不自觉往前探一点
// （手还搭在膝盖上，肩往前，手肘跟着弯）；后面慢慢缓下来；4 秒多眨一次眼
function xmPose(t) {
  const r = Math.min(1.05, raiseAt(t - 0.3));
  const bl = Math.max(0, 1 - Math.abs(t - 4.15) / 0.09);
  const wow = sstep(1.5, 2.1, t) * (1 - 0.45 * sstep(3.4, 4.6, t));
  return { headUp: 0.20 + 0.10 * r, lean: 0.03 + 0.045 * sstep(1.5, 2.8, t) - 0.015 * sstep(3.6, 4.8, t), wow,
    breathe: Math.sin((t / 3.4) * 6.283), mouth: 0.4 + 0.45 * sstep(2.0, 2.6, t) * (1 - 0.5 * sstep(3.6, 4.6, t)),
    blink: Math.min(1, bl * 1.6), pig: 0.03 * Math.sin(t * 1.3) - 0.05 * sstep(1.3, 2.6, t) };
}

export async function render(ctx, arg, W, H) {
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); arg = o.t ?? 0; }
  return renderFrame(ctx, +arg || 0, W, H);
}

// 一张画好的图正对镜头放在世界里（卡片垂直于视线）：图片像素 (ox, oy) 落在世界点 base，sc = 每厘米多少像素。
// 二维画的侧面不会被斜着看压窄，也没有仰视的上下透视，投影就是缩放加平移。返回图片像素 → 画面像素的仿射变换
export function billboardM(cam, base, ox, oy, sc) {
  const P = (px, py) => {
    const x = (px - ox) / sc / 100, y = (oy - py) / sc / 100;
    const r = cam.project([base[0] + cam.right[0] * x + cam.up[0] * y, base[1] + cam.right[1] * x + cam.up[1] * y, base[2] + cam.right[2] * x + cam.up[2] * y]);
    return [r[0], r[1]];
  };
  const p0 = P(0, 0), p1 = P(100, 0), p2 = P(0, 100);
  return [(p1[0] - p0[0]) / 100, (p1[1] - p0[1]) / 100, (p2[0] - p0[0]) / 100, (p2[1] - p0[1]) / 100, p0[0], p0[1]];
}

// 第 6 场的人物卡片：小满坐在小板凳上看鹤
async function cards06(CARDS, cam, t) {
  const c0 = cam.project(xmWorld([0, 0])), depth = c0[2], sc = c0[3] / 100;
  if (DEBUG.xm === 'image') {
    // 小满用画好的图（xm_rig.js）；位置是她坐的地方（凳面中心）。镜头只仰 11°，脚底因此离地面差几厘米，看不出来
    XMI ||= await loadRig(RIG16);
    const R = RIG16, base = xmWorld([0, 0]); base[2] = (R.floorY - R.oy) / R.sc / 100;
    CARDS.addImage(layers16(R, XMI, billboardM(cam, base, R.ox, R.oy, R.sc), pose16(t)), depth);
  } else {
    const map = (p) => { const r = cam.project(xmWorld(p)); return [r[0], r[1]]; };
    CARDS.addAll(XMC.parts(map, xmPose(t), sc), depth);
  }
}

export async function renderFrame(ctx, t, W, H) { return renderShot(ctx, t, W, H, {}); }

// 床单戏的通用渲染：shot = { cam, cards(CARDS, cam, t), hands(root, t) → 两根签子的手端 [x, z, 离床单], cranePose(t), afterCards(CARDS, cam, t) }
export async function renderShot(ctx, t, W, H, shot) {
  const pal = DEBUG.palette || 'plain';
  if (cranePal !== pal) { crane = makeCrane(1.35, pal); cranePal = pal; }
  POND ||= makePond(); WILLOW ||= makeWillow();
  if (!G || G.W !== W || G.H !== H) G = new GL(W, H);
  QUILTS ||= { L: quiltTex('L'), R: quiltTex('R') };
  const cam = camera(W, H, DEBUG.cam || shot.cam || {});
  const flick = 1 + 0.035 * Math.sin(t * 13.1) + 0.025 * Math.sin(t * 7.3 + 1.1) + 0.02 * Math.sin(t * 23.7);

  // 1. 床单：物理影子图
  const L = S.lamp, sh = S.sheet;
  const root = [CRANE_ROOT[0], CRANE_ROOT[1] + 0.005 * Math.sin(t * 1.7) - 0.012 * (1 - Math.min(1, raiseAt(t)))], dist = 0.004;
  const lampSP = { x: L.x, z: L.z, D: L.y, core: L.core, globe: L.globe, coreW: 1.0, globeW: 0.55, rgb: [255, 200, 128], I: 1.32 };
  const still = { angles: {}, rootAngle: 0, facing: 1 };
  // 床单上的皮影：布景（荷塘、柳枝）+ 这个镜头的角色。shot.sheet(t, env) 返回角色列表（鹤、乌龟、手影……），没有就用第 6 场的鹤
  const scenery = [
    { pup: POND, pose: still, root: [1.30, 0.34], dist: 0.003 },
    { pup: WILLOW, pose: { ...still, rootAngle: -0.03 }, root: [sh.x0 + 0.05, sh.z1 - 0.13], dist: 0.003 },
  ];
  const actors = shot.sheet ? shot.sheet(t, { crane, cam, RODS }) : [{ pup: crane, pose: (shot.cranePose || cranePose)(t), root, dist,
    rods: RODS.map((r, i) => ({ ...r, hand: shot.hands ? shot.hands(root, t, cam)[i] : r.hand(root) })) }];
  const img = sheetImage(sh, lampSP, [...scenery, ...actors], 900, { split: true, rodMin: 0.06, rodA: 0.8, rodFade: 0.05, rodBlur: 1.0, rodBlurMax: 46 });
  const patches = patchRadiance(img.mask, sh, L, flick);

  // 2. 卡片（人物、道具）
  CARDS = CARDS && CARDS.W === W ? CARDS : new Cards(W, H);
  CARDS.clear();
  if (shot.cards !== null) await (shot.cards || cards06)(CARDS, cam, t, { root, crane, flick, actors });
  const cards = { alb: CARDS.alb, nrm: CARDS.nrm, mat: CARDS.mat };

  // 3. 上传、逐遍渲染
  const gl = G;
  gl.texture('sheet', img.mask);
  gl.texture('qL', QUILTS.L); gl.texture('qR', QUILTS.R);
  gl.texture('alb', cards.alb); gl.texture('nrm', cards.nrm); gl.texture('mat', cards.mat);
  gl.texture('dust', dustLayer(cam, W, H, t, L, sh, flick));
  gl.program('scene', SH.sceneFS(S)); gl.program('fog', SH.fogFS(S)); gl.program('combine', SH.combineFS);
  gl.program('down', SH.downFS); gl.program('blur', SH.blurFS); gl.program('final', SH.finalFS);
  const U = { uRes: [W, H], uCam: cam.C, uFwd: cam.fwd, uRight: cam.right, uUp: cam.up, uFocal: cam.focal,
    uLamp: [L.x, L.y, L.z], uLampI: 1.0 * flick, uCardDbg: DEBUG.card || 0, uPatch: patches.map((p) => p * flick), uTime: t };
  const tScene = gl.target('scene', W, H);
  gl.draw('scene', tScene, U, { uSheet: gl.texs.sheet, uQuiltL: gl.texs.qL, uQuiltR: gl.texs.qR, uAlb: gl.texs.alb, uNrm: gl.texs.nrm, uMat: gl.texs.mat });
  const fw = Math.round(W / 4), fh = Math.round(H / 4);
  const tFog = gl.target('fog', fw, fh);
  gl.draw('fog', tFog, { ...U, uSigma: 0.16 * (DEBUG.fog ?? 1) }, { uScene: tScene });
  const tComb = gl.target('comb', W, H);
  gl.draw('combine', tComb, { uFogRes: [fw, fh], uExt: 0.03 }, { uScene: tScene, uFog: tFog, uDust: gl.texs.dust });
  // 泛光
  const d2 = gl.target('d2', W >> 1, H >> 1), d4 = gl.target('d4', W >> 2, H >> 2), d8 = gl.target('d8', W >> 3, H >> 3), d16 = gl.target('d16', W >> 4, H >> 4);
  gl.draw('down', d2, { uTexel: [0.5 / W, 0.5 / H] }, { uSrc: tComb });
  gl.draw('down', d4, { uTexel: [0.5 / d2.w, 0.5 / d2.h] }, { uSrc: d2 });
  gl.draw('down', d8, { uTexel: [0.5 / d4.w, 0.5 / d4.h] }, { uSrc: d4 });
  gl.draw('down', d16, { uTexel: [0.5 / d8.w, 0.5 / d8.h] }, { uSrc: d8 });
  const blur = (src, name) => {
    const a = gl.target(name + 'a', src.w, src.h), b = gl.target(name + 'b', src.w, src.h);
    gl.draw('blur', a, { uDir: [1.5 / src.w, 0] }, { uSrc: src });
    gl.draw('blur', b, { uDir: [0, 1.5 / src.h] }, { uSrc: a });
    return b;
  };
  const b4 = blur(d4, 'b4'), b8 = blur(d8, 'b8'), b16 = blur(d16, 'b16');
  gl.draw('final', null, { uRes: [W, H], uExp: 4.0 * (DEBUG.exp ?? shot.exp ?? 1), uTime: t, uBloom: 0.10 * (DEBUG.bloom ?? 1) }, { uSrc: tComb, uB1: b4, uB2: b8, uB3: b16 });
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.drawImage(gl.cv, 0, 0);
  if (DEBUG.proxy) {   // 调试：把人物的遮挡球投到画面上，看构图
    ctx.fillStyle = 'rgba(20,10,30,0.85)';
    for (const o of [...S.occ, ...S.occBack]) { const p = cam.project([o[0], o[1], o[2]]); ctx.beginPath(); ctx.arc(p[0], p[1], o[3] * p[3], 0, 6.283); ctx.fill(); }
  }
  ctx.restore();
}
export const DEBUG = { proxy: false, cam: null, xm: 'image' };   // xm：'image' 用画好的图，'code' 用代码画的小满

// 浮尘：床单前面空气里慢慢飘的灰尘。挡在发光的床单前面时被逆光照亮（前向散射），离床单越近越亮；
// 落在小满身后（她的轮廓里、比她远）的看不见。
let DUST = null, XMMASK = null;
function dustLayer(cam, W, H, t, L, sh, I) {
  if (!DUST || DUST.width !== W) DUST = new OffscreenCanvas(W, H);
  const x = DUST.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, W, H);
  x.globalCompositeOperation = 'lighter';
  const mask = CARDS.a.getImageData(0, 0, W, H).data;
  const xmDepth = cam.project(xmWorld([0, 30]))[2];
  let seed = 12345;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 150; i++) {
    // 每颗灰尘的随机数一次取齐（后面有 continue，边用边取会让别的灰尘逐帧变样）
    const b = [0.1 + rnd() * 2.4, -1.5 + rnd() * 1.45, 0.15 + rnd() * 1.9], ph = [rnd() * 6.28, rnd() * 6.28, rnd() * 6.28], sp = 0.6 + rnd() * 0.8;
    const twSp = 2 + rnd() * 3, big = rnd(), rr = rnd();
    const P = [b[0] + 0.03 * Math.sin(t * 0.31 * sp + ph[0]), b[1] + 0.02 * Math.sin(t * 0.23 * sp + ph[1]), b[2] + 0.025 * Math.sin(t * 0.19 * sp + ph[2]) + 0.006 * t];
    const pr = cam.project(P);
    if (pr[3] <= 0 || pr[0] < -10 || pr[0] > W + 10 || pr[1] < -10 || pr[1] > H + 10) continue;
    // 镜头 → 灰尘这条线延长到床单上：灰尘背后是不是床单、那里多亮
    const C = cam.C, k = -C[1] / (P[1] - C[1]); if (k < 1) continue;
    const Q = [C[0] + (P[0] - C[0]) * k, C[2] + (P[2] - C[2]) * k];
    if (Q[0] < sh.x0 || Q[0] > sh.x1 || Q[1] < sh.z0 || Q[1] > sh.z1) continue;
    const rad = sheetRadiance((Q[0] - sh.x0) / (sh.x1 - sh.x0), (sh.z1 - Q[1]) / (sh.z1 - sh.z0), sh, L, I)[0];
    const near = Math.exp(P[1] * 1.6);
    const tw = 0.6 + 0.4 * Math.sin(t * twSp + ph[0] * 3);      // 灰尘在转，忽明忽暗
    let a = Math.min(1, rad * (big > 0.85 ? 7 : 2.2) * near * tw);
    const ix = Math.round(pr[0]), iy = Math.round(pr[1]);
    if (ix >= 0 && iy >= 0 && ix < W && iy < H && mask[(iy * W + ix) * 4 + 3] > 40 && pr[2] > xmDepth) continue;
    const r = 0.9 + rr * 1.4 + Math.max(0, 1.6 - pr[2]) * 3;          // 离镜头近的虚一点、大一点
    if (r > 2.5) a *= 2.5 / r;
    const g = x.createRadialGradient(pr[0], pr[1], 0, pr[0], pr[1], r * 2);
    g.addColorStop(0, `rgba(255,226,180,${a})`); g.addColorStop(0.35, `rgba(255,214,160,${a * 0.5})`); g.addColorStop(1, 'rgba(255,200,140,0)');
    x.fillStyle = g; x.fillRect(pr[0] - r * 2, pr[1] - r * 2, r * 4, r * 4);
  }
  return DUST;
}

// 床单透过来的亮度（线性，浮点）：点光源照在平面上 E = I·D / r³，薄棉布再透出一团火苗的亮芯。着色器里用同一个公式。
export function sheetRadiance(u, v, sh, L, I = 1) {
  const X = sh.x0 + u * (sh.x1 - sh.x0), Z = sh.z1 - v * (sh.z1 - sh.z0);
  const dx = X - L.x, dz = Z - L.z, r2 = dx * dx + dz * dz + L.y * L.y, r = Math.sqrt(r2);
  const diff = SHEET_TAU * I * L.y / (r2 * r);
  const hot = I * (SHEET_HOT * Math.exp(-(dx * dx + dz * dz) / (0.12 * 0.12)) + 0.10 * Math.exp(-(dx * dx + dz * dz) / (0.34 * 0.34)));
  return [diff + hot, (diff + hot * 0.92) * 0.58 / 0.58, diff + hot * 0.8];
}
export const SHEET_TAU = +S.sheetTau, SHEET_HOT = +S.sheetHot;   // 和着色器里用同一组数
// 床单 8×6 块的平均亮度（线性），给面光源用：每块里取 6×6 个点，解析亮度 × 影子图
function patchRadiance(mask, sh, L, I) {
  const w = mask.width, h = mask.height;
  const d = mask.getContext('2d').getImageData(0, 0, w, h).data;
  const lut = new Float32Array(256); for (let i = 0; i < 256; i++) lut[i] = Math.pow(i / 255, 2.2);
  const out = [];
  for (let j = 0; j < 6; j++) for (let i = 0; i < 8; i++) {
    let r = 0, g = 0, b = 0;
    for (let sy = 0; sy < 6; sy++) for (let sx = 0; sx < 6; sx++) {
      const u = (i + (sx + 0.5) / 6) / 8, v = (j + (sy + 0.5) / 6) / 6;
      const rad = sheetRadiance(u, v, sh, L, I);
      const k = (Math.min(h - 1, Math.floor(v * h)) * w + Math.min(w - 1, Math.floor(u * w))) * 4;
      r += rad[0] * lut[d[k]] * L.rgb[0]; g += rad[1] * lut[d[k + 1]] * L.rgb[1]; b += rad[2] * lut[d[k + 2]] * L.rgb[2];
    }
    out.push(r / 36, g / 36, b / 36);
  }
  return out;
}
