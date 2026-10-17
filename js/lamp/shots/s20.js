// S20 · 第 8 场：后台（机位 C）。小满第一次上手：她攥着乌龟的两根签子（合作方画的 anim_20_xiaoman_puppeteer），手忙脚乱——
// 乌龟在床单背面乱晃、打转，两根签子绞到一起（2.4～4.6，对上竹签相碰声），乌龟一下子翻了肚皮（5.5，对上"噔"和小锣）；
// 奶奶本来稳稳地拿着鹤，这下笑弯了腰（6.0 切到奶奶中近景，换成 anim_20_grandma_laugh_bent：一只手捂着肚子，另一只手把两根鹤签并在一起握着）。
// 签子都由程序从图里的拳头握点画到皮影身上的接点；图上露在拳头外的短签擦掉。
import { renderShot, billboardM, S, CRANE_ROOT, RODS, DEBUG } from '../s06_key.js';
import { solve, pointOn, drawPuppet } from '../../puppet.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck, sstep } from '../choreo.js';
import { GRANDMA, GR, CAM_C, loadMaps, flatMaps, makeLamp, craneCard } from '../s08_back.js';
export const DURATION = 9;
const T_LAUGH = 6.0;
// 小满：站在奶奶右边、离床单近一点；图里脚底中点、每厘米像素（身高约 1.32 米）、两个拳头的握点（上手、下手）、要擦掉的短签
const XM = { file: 'x20_puppeteer', pos: [1.98, 0.78], ox: 193, oy: 1425, sc: 10.75, grips: [[568, 330], [510, 495]],
  erase: [[[590, 300], [646, 256], [662, 276], [600, 320]], [[538, 466], [588, 428], [602, 446], [548, 484]]] };
// 奶奶笑弯腰：脚底、比例、握点（两根鹤签并在一只手里）、要擦掉的短签
const GL = { file: 'g20_laugh', ox: 175, oy: 1284, sc: 9.0, grip: [585, 538], erase: [[[606, 522], [664, 522], [664, 550], [606, 550]]] };
let MAPS = null, LAMPM = null, TURTLE = null;
// 机位：后台东北角往西南看——小满和乌龟离镜头近，奶奶、马灯、鹤在后面。人物都面朝床单（画面左边），图要水平翻转
const CAM20 = { pos: [3.05, 1.5, 1.18], target: [1.5, 0.42, 0.95], hfov: 58 };
// 6 秒乌龟翻肚之后切到奶奶的中近景（她笑弯了腰，两根鹤签并到一只手里——换姿势正好藏在剪辑点上），镜头慢慢推一点
const CAMG = (t) => { const k = sstep(T_LAUGH, DURATION, t); return { pos: [2.55, 1.7, 1.2], target: [1.2, 1.15, 1.0 + 0.02 * k], hfov: 42 - 4 * k }; };   // 机位不动只收视角（往前挪会钻进后台的木箱）
const GPOS = (t) => [GRANDMA.pos[0] - 0.12, GRANDMA.pos[1] - 0.05 + (t >= T_LAUGH ? 0.16 * sstep(T_LAUGH, T_LAUGH + 0.25, t) : 0), 0];   // 笑的时候往后退一步
const flipP = (card, p) => [2 * card.ox - p[0], p[1]];
const mulM = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
const flipM = (card) => [-1, 0, 0, 1, 2 * card.ox, 0];

function imgWorld(cam, base, card, p) {
  const x = (p[0] - card.ox) / card.sc / 100, y = (card.oy - p[1]) / card.sc / 100;
  return [base[0] + cam.right[0] * x + cam.up[0] * y, base[1] + cam.right[1] * x + cam.up[1] * y, base[2] + cam.right[2] * x + cam.up[2] * y];
}
const toHand = (w) => [w[0], w[2], w[1]];           // 世界 [x, y(离床单), z] → 签子手端 [x, z, 离床单]

// 乌龟的位置和姿势（床单背面）
function turtleState(t) {
  const flip = sstep(5.2, 5.5, t);
  const spin = sstep(2.4, 3.0, t) * (1 - sstep(4.4, 4.8, t));
  const x = 1.95 + 0.07 * Math.sin(t * 3.1) + 0.04 * Math.sin(t * 7.3) * (1 - flip);
  const z = 0.80 + 0.05 * Math.sin(t * 4.3) - 0.04 * flip + 0.02 * Math.abs(Math.sin(t * 9)) * flip;
  const ang = 0.22 * Math.sin(t * 2.7) + spin * 0.7 * Math.sin(t * 6.2) + Math.PI * flip;
  const pose = turtlePose(t * (1 + flip), { facing: -1, walk: 1, speed: 1.6 + 1.2 * flip, neckOut: 0.6 - 0.3 * spin, rootAngle: ang });
  return { root: [x, z], pose, cross: spin > 0.5 || flip > 0.5 };
}
function craneState(t) {
  const laugh = sstep(T_LAUGH - 0.1, T_LAUGH + 0.3, t);
  const bob = laugh * Math.sin((t - T_LAUGH) * 9);
  const neck = mixNeck(NECK_UP, NECK_LOW, 0.25 + 0.5 * laugh + 0.2 * bob);
  return { root: [CRANE_ROOT[0] - 0.08, CRANE_ROOT[1] + 0.005 * Math.sin(t * 1.7) - 0.03 * laugh + 0.01 * bob], pose: cranePoseOf(neck, { mode: 'two' }, 0.04 + 0.1 * bob, 1) };
}

// 小满的拳头在世界里的位置（人轻轻发抖）
function xmBase(t) {
  const j = 0.006 * Math.sin(t * 9.3) + 0.004 * Math.sin(t * 15.1) + (t > 5.4 && t < 5.7 ? 0.01 : 0);
  return [XM.pos[0] + j, XM.pos[1], 0];
}
function grips(t, cam) {
  const xm = XM.grips.map((g) => imgWorld(cam, xmBase(t), XM, flipP(XM, g)));
  const gm = t < T_LAUGH ? GR.grips.map((g) => imgWorld(cam, GPOS(t), GR, flipP(GR, g)))
    : [0, 1].map(() => imgWorld(cam, GPOS(t), GL, flipP(GL, GL.grip)));
  return { xm, gm };
}

const shot = {
  cam: (t) => (t < T_LAUGH ? CAM20 : CAMG(t)),
  exp: 0.26,
  fog: 0.5,                                            // 后台的雾减半：人离镜头近，雾太浓会发灰发闷
  sheet: (t, env) => {
    TURTLE ||= makeTurtle();
    const T = turtleState(t), C = craneState(t);
    const G = grips(t, env.cam);
    // 乌龟的两根签子：平时上手→头、下手→壳；绞到一起时交叉
    const tr = [{ part: 'shell', at: [0, 40] }, { part: 'head', at: [20, 0] }];
    const turtle = { pup: TURTLE, pose: T.pose, root: T.root, dist: 0.004, rods: tr.map((r, i) => ({ ...r, hand: toHand(G.xm[T.cross ? i : 1 - i]) })) };
    const crane = { pup: env.crane, pose: C.pose, root: C.root, dist: 0.004, rods: RODS.map((r, i) => ({ ...r, hand: toHand(G.gm[i]) })) };
    return [turtle, crane];
  },
  hands: (root, t, cam) => grips(t, cam).gm.map(toHand),
  cranePose: (t) => craneState(t).pose,
  cards: async (CARDS, cam, t, ctx) => {
    MAPS ||= { gr: await loadMaps(GR.file), gl: await loadMaps(GL.file), xm: await loadMaps(XM.file) };
    LAMPM ||= makeLamp();
    const T = turtleState(t), C = craneState(t), G = grips(t, cam), dist = 0.004;
    const sheetM = (root, facing, cardPx, ox, oy) => {
      const W = (mm) => cam.project([root[0] + facing * mm[0] / 1000, dist, root[1] + mm[1] / 1000]);
      const q0 = W([0, 0]), q1 = W([100, 0]), q2 = W([0, 100]);
      const a = [(q1[0] - q0[0]) / 100, (q1[1] - q0[1]) / 100, (q2[0] - q0[0]) / 100, (q2[1] - q0[1]) / 100];
      return { m: [a[0] / cardPx, a[1] / cardPx, -a[2] / cardPx, -a[3] / cardPx, q0[0] - a[0] * ox / cardPx + a[2] * oy / cardPx, q0[1] - a[1] * ox / cardPx + a[3] * oy / cardPx], d: q0[2], W };
    };
    // 1. 鹤（皮面，贴床单背面）
    const cc = craneCard(ctx.crane, C.pose), cm = sheetM(C.root, C.pose.facing ?? 1, 2, 900, 1000);
    CARDS.addImage([{ maps: cc.maps, m: cm.m }], cm.d);
    // 2. 乌龟（皮面）：2 像素/毫米，原点 (600, 500)
    const tcv = new OffscreenCanvas(1200, 1000), tx = tcv.getContext('2d');
    tx.translate(600, 500); tx.scale(2, -2); drawPuppet(tx, TURTLE, { ...T.pose, rootAngle: T.pose.rootAngle }, 'r');
    const tm = sheetM(T.root, 1, 2, 600, 500);
    CARDS.addImage([{ maps: flatMaps(tcv, 0), m: tm.m }], tm.d);
    // 3. 马灯
    const L = S.lamp, lampBase = [L.x, L.y, L.z];
    const mL = billboardM(cam, lampBase, LAMPM.ox, LAMPM.oy, LAMPM.K), dL = cam.project(lampBase)[2];
    CARDS.addImage([{ maps: LAMPM.metal, m: mL }, { maps: LAMPM.glass, m: mL }, { maps: LAMPM.flame, m: mL }], dL);
    // 4. 签子：鹤（奶奶）、乌龟（小满）
    const rod = (pmWorld, grip) => { const A = cam.project(pmWorld), B = cam.project(grip); CARDS.addStroke([[A[0], A[1]], [B[0], B[1]]], Math.max(1.5, 0.007 * B[3]), '#9a7848', (A[2] + B[2]) / 2); };
    const csol = solve(ctx.crane, C.pose);
    RODS.forEach((r, i) => { const pm = pointOn(ctx.crane, csol, r.part, r.at); rod([C.root[0] + (C.pose.facing ?? 1) * pm[0] / 1000, dist, C.root[1] + pm[1] / 1000], G.gm[i]); });
    const tsol = solve(TURTLE, T.pose);
    [{ part: 'shell', at: [0, 40] }, { part: 'head', at: [20, 0] }].forEach((r, i) => {
      const pm = pointOn(TURTLE, tsol, r.part, r.at);
      rod([T.root[0] + (T.pose.facing ?? 1) * pm[0] / 1000, dist, T.root[1] + pm[1] / 1000], G.xm[T.cross ? i : 1 - i]);   // 皮面按 facing 镜像画，杆端也要乘
    });
    // 5. 小满（比奶奶离镜头远，先画；奶奶的中近景里她在画外，不画）
    const xb = xmBase(t), dX = cam.project(xb)[2];
    if (t < T_LAUGH) CARDS.addImage([{ maps: MAPS.xm, m: mulM(billboardM(cam, xb, XM.ox, XM.oy, XM.sc), flipM(XM)), clip: { pts: XM.erase, invert: true } }], dX);
    // 6. 奶奶：拿着鹤 → 笑弯了腰
    const gb = GPOS(t), dG = cam.project(gb)[2];
    if (t < T_LAUGH) CARDS.addImage([{ maps: MAPS.gr, m: mulM(billboardM(cam, gb, GR.ox, GR.oy, GR.sc), flipM(GR)), clip: { pts: GR.erase, invert: true } }], dG);
    else {
      // 笑：一颤一颤（以脚底为基准竖直方向轻轻伸缩）
      const u = t - T_LAUGH, sy = 1 + 0.008 * Math.sin(u * 9) * Math.exp(-u * 0.25);
      const m0 = billboardM(cam, gb, GL.ox, GL.oy, GL.sc);
      const mul = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
      CARDS.addImage([{ maps: MAPS.gl, m: mul(mul(m0, [1, 0, 0, sy, 0, GL.oy * (1 - sy)]), flipM(GL)), clip: { pts: GL.erase, invert: true } }], dG);
    }
  },
};

export async function render(ctx, arg, W, H) {
  let t = +arg || 0;
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); t = o.t ?? 0; }
  return renderShot(ctx, t, W, H, shot);
}
export async function renderFrame(ctx, t, W, H) { return renderShot(ctx, t, W, H, shot); }
