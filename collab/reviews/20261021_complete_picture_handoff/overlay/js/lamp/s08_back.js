// 第 8 场 · 后台机位 C：从床单背面的西北角看，画面从左到右是奶奶 → 挂着的马灯 → 床单背面和鹤。
// 奶奶是合作 AI 画的图（collab/refs/anim_20_grandma_puppeteer.png），抠图后算好法线和材质；
// 两根竹签由程序从她手心的握点画到鹤身上的两个接点（第四版 makeCrane 的 body / neck3），床单上的签子影子用同样的手端位置算；
// 鹤从后台看是皮面（drawPuppet 'r'），贴在床单背面前 4 毫米；马灯是程序画的，玻璃罩和火苗自己发光。
import { renderShot, billboardM, S, CRANE_ROOT, RODS, DEBUG, cranePose } from './s06_key.js';
import { solve, pointOn, drawPuppet } from '../puppet.js';

export const DURATION = 5;

// 奶奶站的地方：这个镜头里比第 6 场往后、往东挪一点，马灯才在她和床单之间露出来，不被她挡住
export const GRANDMA = { pos: [1.25, 1.15] };
// 图：脚底中点（图片像素）、每厘米像素（身高约 1.5 米）、两只手的握点（低的握主签、高的握头签）
// 图上手里那几截短签方向不一（握签的那只低手前后两截还错开了一点），裁掉露在拳头外面的部分（erase），
// 由程序从拳头里的握点画一根直的长签，拳头盖住签子的根，签子从握点自然伸出去
export const GR = { file: 'g20_puppeteer', ox: 245, oy: 1363, sc: 9.04, grips: [[578, 641], [590, 466]],
  erase: [[[608, 445], [665, 445], [665, 482], [608, 482]], [[588, 626], [618, 626], [618, 654], [588, 654]], [[460, 668], [495, 668], [495, 694], [460, 694]]] };
export const CAM_C = { pos: [-0.2, 1.5, 1.2], target: [1.1, 0.75, 0.95], hfov: 60 };

let GM = null, LAMPM = null, CRANEC = null;
const load = async (u) => createImageBitmap(await (await fetch(u)).blob());
export async function loadMaps(f) { const b = '/assets/chars/' + f; const [alb, nrm, mat] = await Promise.all([load(b + '.png'), load(b + '_n.png'), load(b + '_m.png')]); return { alb, nrm, mat }; }

// 平涂的卡片：给一张固有色画布，配上朝镜头的法线和一种材质
export function flatMaps(alb, mat = 0, extra = 0) {
  const mk = (fill) => { const c = new OffscreenCanvas(alb.width, alb.height), x = c.getContext('2d'); x.drawImage(alb, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = fill; x.fillRect(0, 0, c.width, c.height); return c; };
  return { alb, nrm: mk('rgb(128,128,255)'), mat: mk(`rgb(0,${mat * 30},${Math.round(extra * 255)})`) };
}

// 马灯（风灯）：铁皮油壶、玻璃罩、上盖、两根护罩铁丝、提梁，挂在钩子上。局部厘米，原点在火苗；画成 10 像素/厘米的图
export function makeLamp() {
  const K = 10, W = 26 * K, H = 46 * K, ox = 13 * K, oy = 24 * K;     // 火苗在 (13, 24) 厘米处
  const P = (x, y) => [ox + x * K, oy - y * K];
  const layer = () => { const c = new OffscreenCanvas(W, H); return [c, c.getContext('2d')]; };
  const [metal, mx] = layer(), [glass, gx] = layer(), [flame, fx] = layer();
  const ell = (ctx, x, y, rx, ry, fill) => { ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(...P(x, y), rx * K, ry * K, 0, 0, 6.283); ctx.fill(); };
  const rect = (ctx, x0, y0, x1, y1, fill) => { const a = P(x0, y1), b = P(x1, y0); ctx.fillStyle = fill; ctx.fillRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); };
  // 玻璃罩（被火苗照得发亮，越靠中间越亮）
  const g = gx.createRadialGradient(...P(0, 0.5), 0, ...P(0, 0.5), 6.5 * K);
  g.addColorStop(0, 'rgb(255,214,150)'); g.addColorStop(0.6, 'rgb(240,170,90)'); g.addColorStop(1, 'rgb(170,100,45)');
  gx.fillStyle = g; gx.beginPath(); gx.ellipse(...P(0, 0.5), 5.2 * K, 7.0 * K, 0, 0, 6.283); gx.fill();
  // 火苗
  fx.fillStyle = 'rgb(255,236,180)'; fx.beginPath();
  fx.moveTo(...P(0, 2.6)); fx.quadraticCurveTo(...P(1.0, 0.6), ...P(0.6, -0.6)); fx.quadraticCurveTo(...P(0, -1.1), ...P(-0.6, -0.6)); fx.quadraticCurveTo(...P(-1.0, 0.6), ...P(0, 2.6)); fx.fill();
  // 铁皮：油壶、灯座、上盖、护罩铁丝、提梁、挂钩
  const iron = 'rgb(58,48,42)', ironHi = 'rgb(92,74,60)';
  ell(mx, 0, -9.5, 7.5, 3.2, iron); rect(mx, -7.5, -12.5, 7.5, -9.5, iron); ell(mx, 0, -12.5, 7.5, 1.6, ironHi);     // 油壶
  rect(mx, -4.5, -7.6, 4.5, -6.0, ironHi);                                                                        // 灯座
  rect(mx, -4.0, 7.0, 4.0, 8.4, iron); ell(mx, 0, 9.2, 4.6, 1.6, iron); rect(mx, -1.2, 9.5, 1.2, 11.0, iron);     // 上盖、烟囱
  mx.strokeStyle = iron; mx.lineWidth = 0.45 * K; mx.lineCap = 'round';
  for (const s of [-1, 1]) { mx.beginPath(); mx.moveTo(...P(s * 7.0, -9.5)); mx.quadraticCurveTo(...P(s * 7.6, 0.5), ...P(s * 4.0, 7.5)); mx.stroke(); }   // 护罩铁丝
  mx.beginPath(); mx.moveTo(...P(-6.5, -9)); mx.bezierCurveTo(...P(-9, 10), ...P(-4, 17), ...P(0, 17)); mx.bezierCurveTo(...P(4, 17), ...P(9, 10), ...P(6.5, -9)); mx.stroke();   // 提梁
  mx.lineWidth = 0.3 * K; mx.beginPath(); mx.moveTo(...P(0, 17)); mx.lineTo(...P(0, 22)); mx.stroke();          // 挂绳
  return { K, ox, oy, metal: flatMaps(metal, 0), glass: flatMaps(glass, 8, 0.25), flame: flatMaps(flame, 8, 1.0) };
}

// 鹤从后台看：皮面贴图（drawPuppet 'r'），2 像素/毫米，原点 (900, 1000)
export function craneCard(pup, pose) {
  const c = new OffscreenCanvas(1800, 1800), x = c.getContext('2d');
  x.translate(900, 1000); x.scale(2, -2);
  drawPuppet(x, pup, pose, 'r');
  return { maps: flatMaps(c, 0), px: (mm) => [900 + mm[0] * 2, 1000 - mm[1] * 2] };
}

// 图片像素 → 世界：奶奶的卡片正对镜头，脚底中点在她站的地方
function gripWorld(cam, base, p) {
  const x = (p[0] - GR.ox) / GR.sc / 100, y = (GR.oy - p[1]) / GR.sc / 100;
  return [base[0] + cam.right[0] * x + cam.up[0] * y, base[1] + cam.right[1] * x + cam.up[1] * y, base[2] + cam.right[2] * x + cam.up[2] * y];
}

const shot = {
  cam: CAM_C,
  exp: 0.32,         // 人离马灯只有六十厘米，比看戏那边亮得多，曝光收到三分之一
  // 床单上签子影子的手端：用她手心握点的世界位置 [x, z, 离床单]
  hands: (root, t, cam) => {
    const base = [GRANDMA.pos[0], GRANDMA.pos[1], 0];
    return GR.grips.map((g) => { const w = gripWorld(cam, base, g); return [w[0], w[2], w[1]]; });
  },
  cards: async (CARDS, cam, t, ctx) => {
    GM ||= await loadMaps(GR.file);
    LAMPM ||= makeLamp();
    const pose = cranePose(t), root = ctx.root, dist = 0.004;
    // 1. 鹤（最远，贴着床单背面）：鹤的毫米 → 世界 (x, 离床单, z) → 画面
    const cc = craneCard(ctx.crane, pose);
    const W = (mm) => cam.project([root[0] + (pose.facing ?? 1) * mm[0] / 1000, dist, root[1] + mm[1] / 1000]);
    const q0 = W([0, 0]), q1 = W([100, 0]), q2 = W([0, 100]);
    // 贴图像素 → 毫米：x = (px - 900) / 2，y = (1000 - py) / 2；再接毫米 → 画面
    const a = [(q1[0] - q0[0]) / 100, (q1[1] - q0[1]) / 100, (q2[0] - q0[0]) / 100, (q2[1] - q0[1]) / 100];
    const mCrane = [a[0] / 2, a[1] / 2, -a[2] / 2, -a[3] / 2, q0[0] - a[0] * 450 + a[2] * 500, q0[1] - a[1] * 450 + a[3] * 500];
    CARDS.addImage([{ maps: cc.maps, m: mCrane }], q0[2]);
    // 2. 马灯（挂在床单和奶奶之间），火苗在 S.lamp
    const L = S.lamp, lampBase = [L.x, L.y, L.z];
    const mL = billboardM(cam, lampBase, LAMPM.ox, LAMPM.oy, LAMPM.K), dL = cam.project(lampBase)[2];
    CARDS.addImage([{ maps: LAMPM.metal, m: mL }, { maps: LAMPM.glass, m: mL }, { maps: LAMPM.flame, m: mL }], dL);
    // 3. 两根竹签：从手心握点到鹤身上的接点（同一条世界直线）
    const base = [GRANDMA.pos[0], GRANDMA.pos[1], 0];
    const sol = solve(ctx.crane, pose);
    RODS.forEach((r, i) => {
      const pm = pointOn(ctx.crane, sol, r.part, r.at);
      const A = cam.project([root[0] + (pose.facing ?? 1) * pm[0] / 1000, dist, root[1] + pm[1] / 1000]);
      const B = cam.project(gripWorld(cam, base, GR.grips[i]));
      CARDS.addStroke([[A[0], A[1]], [B[0], B[1]]], Math.max(1.5, 0.007 * B[3]), '#9a7848', (A[2] + B[2]) / 2);
    });
    // 4. 奶奶（最近）
    const dG = cam.project(base)[2];
    CARDS.addImage([{ maps: GM, m: billboardM(cam, base, GR.ox, GR.oy, GR.sc), clip: { pts: GR.erase, invert: true } }], dG);
  },
};

export async function render(ctx, arg, W, H) {
  let t = +arg || 0;
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); t = o.t ?? 0; }
  return renderShot(ctx, t, W, H, shot);
}
export async function renderFrame(ctx, t, W, H) { return renderShot(ctx, t, W, H, shot); }
