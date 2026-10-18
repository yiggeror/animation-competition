// 2-7 中景（6 秒）：黑屋里，奶奶坐在八仙桌边点马灯。人物用代码小人（侧面、面朝右），马灯、桌子、火柴、火苗、烟都是代码画的。
// 节拍（音效对齐 audio/build.py 的 S08：0.2 划火柴、1.8 灯芯着、2.2 甩灭、3.4 灯罩落下"叮"）：
//   0.12～0.2 右手（近手）拿火柴在左手的火柴盒上一擦——0.2 着了，火光一跳，照亮她的脸，她眯一下眼；
//   0.45～0.72 左手放下火柴盒；0.90 捏住拨杆端，0.95～1.12 提罩；
//   1.1～1.7 探身送火，1.7～1.85 燃烧头贴芯；1.8 起芯火，之后才撤火柴；
//   1.85～2.35 收回火柴、单次甩腕，2.2 灭了；2.4～2.8 放到桌上，松指收手；
//   3.25～3.3 松杆撤指，3.3～3.4 杆和罩自由落回（"叮"）；3.5～4.25 髋退回凳面、双手收回；4.3 笑开，5.0 看向画面左边。
import { renderPaint, loadImg } from '../paint/paintshot.js';
import { lamp as drawLamp, flameShape, LX, LB } from '../code/s08.js';
import { key, charLayer, stool, armSide, blink, EASE } from './kit.js';
import { NN } from '../chars/nainai.js';
export const DURATION = 6;
const W = 1920, H = 1080, K = 14, AT = [596, 1793];          // 每厘米 14 像素；奶奶原点（地面、两脚中间）在画面外下方
const TOP = -58, EDGE = 12, LAMP_X = 56, LS = 1 / 18.5;      // 桌面高 58 厘米、桌沿在 x = 12；马灯放在 x = 56，设计坐标 18.5 单位 = 1 厘米（连提梁约 40 厘米）
const SEAT_Y = 27;                                          // 坐着：髋往下挪 27 厘米（凳面 45）
// 与 lampLayer 同一原点；code/s08.js 实际黑色芯帽顶是 −226（返回的 −228 是旧火苗提示点）。
const LAMP_Y = TOP - 1.1;
const WICK = [LAMP_X, LAMP_Y - 226 * LS];
const S = (p) => [AT[0] + p[0] * K, AT[1] + p[1] * K];       // 地面坐标（厘米）→ 画面像素
const cl = (v) => Math.min(1, Math.max(0, v));
const seg = (t, a, b, e = 'io') => EASE[e](cl((t - a) / (b - a)));
const fl = (t) => 1 + 0.06 * Math.sin(t * 9.3) + 0.04 * Math.sin(t * 17.7) + 0.03 * Math.sin(t * 31);

// 先捏住杆头，再提罩；撤指完成后，拨杆和罩才一起落回。
const lift = (t) => seg(t, 0.95, 1.12) * (1 - seg(t, 3.3, 3.4, 'in'));
function leverTip(lf) { const la = 0.55 - lf * 0.9; return [LAMP_X - (150 + 95 * Math.cos(la)) * LS, LAMP_Y + (-230 + 95 * Math.sin(la)) * LS]; }
const matchFlame = (t) => (t < 0.2 || t >= 2.2 ? 0 : t < 0.4 ? 1.6 - (t - 0.2) * 3.75 : 0.85 + 0.06 * Math.sin(t * 19));
const wickFlame = (t) => (t < 1.8 ? 0 : 0.55 * seg(t, 1.8, 2.15, 'out') + 0.45 * seg(t, 3.4, 4.2));

// hand.js 的 pinch 真正握点，不是腕前的任意常数。世界手角先定，再精确反求腕，避免不收敛的固定点迭代。
const PINCH = [1.46 * NN.palm, -0.2 * NN.palm], BOX_OFFSET = [4, -1.2];
const MATCH_LENGTH = 4.5, MATCH_ANGLE = -0.15;
const MATCH_HEAD = [PINCH[0] + MATCH_LENGTH * Math.cos(MATCH_ANGLE), PINCH[1] + MATCH_LENGTH * Math.sin(MATCH_ANGLE)];
const PUT_HEAD = [31.4, TOP - 2.5], PUT_ANGLE = Math.atan2(-0.2, 4.4) - MATCH_ANGLE;
const BOX_REST = [25, TOP - 2.95];
const rotate = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const origin = (P) => [P.x || 0, P.y || 0];
function targetHand(P, side, target, offset, angle, hp) {
  const wrist = sub(sub(target, rotate(offset, angle)), origin(P));
  const a = armSide('n', P, side, wrist);
  return { hand: wrist, hp, rot: angle - a.dir };
}
function handPoint(P, side, local) {
  const A = P['arm' + side], a = armSide('n', P, side, A.hand);
  return add(add(a.W, origin(P)), rotate(local, a.dir + A.rot));
}
const heldAngle = (t) => key(t, [[0, -1.35], [0.2, -1.35], [0.45, -1.15], [1.1, -1.15], [1.65, -0.55], [1.85, -0.55], [2.05, -1.15], [2.16, -0.75], [2.28, -1.25], [2.4, -1.0], [2.8, PUT_ANGLE]]);
const heldHead = (t) => key(t, [[0, [22.2, -64.9]], [0.12, [22.2, -64.9]], [0.2, [25.8, -66.6], 'out'], [0.45, [29, -76], 'out'], [1.1, [31, -76]], [1.5, [50, -73]], [1.7, WICK], [1.85, WICK], [2.05, [38, -74]], [2.2, [39.5, -71]], [2.35, [36, -72]], [2.4, [36, -72]], [2.8, PUT_HEAD]]);

function pose(t) {
  const lean = key(t, [[0, 0.22], [1.1, 0.25], [1.65, 0.5, 'io'], [2.0, 0.42], [3.3, 0.42], [4.2, 0.2, 'io'], [6, 0.2]]);
  const settle = seg(t, 3.5, 4.25);
  const P = { x: -3 * settle, y: SEAT_Y + 1.2 * settle, lean, seated: true,
    head: { nod: key(t, [[0, 0.25], [1.1, 0.3], [1.65, 0.45], [3.5, 0.4], [4.2, 0.15], [5.0, 0.15], [5.3, 0.05, 'out'], [6, 0.05]]), tilt: 0 } };
  // 髋小幅退回凳面；双脚保持世界坐标，不随坐回滑动。
  P.legN = { foot: sub([30, -4.6], origin(P)) }; P.legF = { foot: sub([26, -4.6], origin(P)) };
  // 右手：真实指掌握点 → 火柴棍 → 药头；1.7 已接芯，1.8 才起芯火。
  P.armN = targetHand(P, 'N', heldHead(t), MATCH_HEAD, heldAngle(t), 'pinch');
  if (t > 2.8) {
    const rest = sub(PUT_HEAD, rotate(MATCH_HEAD, PUT_ANGLE));
    const wrist = key(t, [[2.8, rest], [2.9, rest], [3.35, [17, TOP - 0.5]], [4.25, [9, -53]]]);
    P.armN = targetHand(P, 'N', wrist, [0, 0], key(t, [[2.8, PUT_ANGLE], [3.35, -0.1], [4.25, 0.35]]), t < 2.9 ? 'pinch' : 'relax');
  }
  // 左手先托盒；盒在0.72落桌后，指尖于0.90先锁杆头，0.95才提罩。
  if (t < 0.72) {
    const center = key(t, [[0, [24, -66]], [0.45, [24, -66]], [0.72, BOX_REST]]);
    const angle = key(t, [[0, -0.55], [0.45, -0.55], [0.72, 0]]);
    P.armF = targetHand(P, 'F', center, BOX_OFFSET, angle, 'grip');
  } else {
    const from = add(sub(BOX_REST, BOX_OFFSET), PINCH), high = leverTip(1);
    const contact = t < 0.9 ? key(t, [[0.72, from], [0.9, leverTip(0)]])
      : t <= 3.25 ? leverTip(lift(t))
      : key(t, [[3.25, high], [3.3, add(high, [-3.4, -2])], [3.4, add(high, [-5, -2.5])], [3.9, [25, -60]], [4.25, [14, -53.5]]]);
    const angle = key(t, [[0.72, 0], [0.9, -0.2], [3.4, -0.2], [4.25, 0.25]]);
    P.armF = targetHand(P, 'F', contact, PINCH, angle, t < 0.78 ? 'grip' : t < 3.3 ? 'pinch' : 'relax');
  }
  const hN = add(P.armN.hand, origin(P)), hF = add(P.armF.hand, origin(P));
  // ---- 脸
  const squint = key(t, [[0.2, 0], [0.24, 1, 'out'], [0.5, 0, 'io']]);
  const focus = key(t, [[1.1, 0], [1.4, 1], [1.8, 1], [2.0, 0.3], [3.3, 0.4], [3.6, 0]]);
  const up = key(t, [[1.8, 0], [1.9, 1, 'out'], [2.3, 0.2]]);
  const smile = key(t, [[0, 0.1], [4.3, 0.12], [4.8, 0.6, 'out'], [6, 0.55]]);
  const look = key(t, [[0, [0.4, 0.5]], [0.5, [0.6, 0.3]], [1.1, [0.8, 0.5]], [1.6, [0.9, 0.7]], [2.05, [0.6, 0.2], 'out'], [2.4, [0.8, 0.5]], [3.5, [0.8, 0.3]], [4.2, [0.7, 0.1]], [5.0, [0.7, 0.1]], [5.2, [-0.7, 0.15], 'out'], [6, [-0.7, 0.15]]]);
  P.face = { look, smile, open: 0.9 - 0.45 * squint - 0.12 * focus + 0.15 * up - 0.25 * seg(t, 4.3, 4.8), brow: 0.25 * up + 0.1 * focus, worry: 0.15 * focus, mouth: 0, blush: 0.3, blink: blink(t, [0.9, 3.0, 5.6]) };
  return { P, hN, hF };
}
// 与真实手型共用同一握点和世界变换；放下时两端连续，之后火柴固定在桌面。
function matchGeom(P) { return { base: handPoint(P, 'N', PINCH), head: handPoint(P, 'N', MATCH_HEAD) }; }
function matchAt(t, P) {
  return t < 2.8 ? matchGeom(P) : { base: sub(PUT_HEAD, rotate([MATCH_LENGTH, 0], PUT_ANGLE + MATCH_ANGLE)), head: PUT_HEAD };
}

// ---------------------------------------------------------------- 画面
let BG = null;
async function bg() {
  if (BG) return BG;
  const room = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(22px)'; x.drawImage(room, 980, 160, 640, 360, -80, -60, W + 160, H + 120); x.filter = 'none';   // 后墙（虚）
  x.save(); x.translate(AT[0], AT[1]); x.scale(K, K);
  // 桌面（从略高处看到一窄条），马灯就站在这一条上
  x.fillStyle = '#8a5a34'; x.fillRect(EDGE, TOP - 2.2, 200, 2.2);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.3; x.beginPath(); x.moveTo(EDGE, TOP - 2.2); x.lineTo(200, TOP - 2.2); x.stroke();
  x.restore();
  return (BG = c);
}
function lampLayer(t) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.translate(AT[0], AT[1]); x.scale(K, K);
  x.save(); x.translate(LAMP_X, LAMP_Y); x.scale(-LS, LS); x.translate(-LX, -LB); drawLamp(x, lift(t), false); x.restore();
  return { img: c, x: 0, y: 0, sc: 1 };
}
function tableFront() {        // 桌沿和牙板：挡住桌子底下的腿
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.translate(AT[0], AT[1]); x.scale(K, K);
  x.fillStyle = '#6a4226'; x.fillRect(EDGE, TOP, 200, 3.4); x.fillStyle = '#5a361e'; x.fillRect(EDGE + 1.5, TOP + 3.4, 200, 4.2);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.35; x.strokeRect(EDGE, TOP, 200, 3.4); x.strokeRect(EDGE + 1.5, TOP + 3.4, 200, 4.2);
  x.fillStyle = '#4a2c18'; x.fillRect(EDGE + 2, TOP + 7.6, 3.6, 60);       // 桌腿
  return { img: c, x: 0, y: 0, sc: 1 };
}
const TF = { c: null };
const shot = {
  size: [W, H],
  layers: async (t) => {
    const { P } = pose(t), M = matchAt(t, P);
    return [
      lampLayer(t),
      charLayer('n', 'side', P, { box: [0, 0, W, H], k: K, at: AT, ss: 1,
        before: (x) => stool(x, -3, 45),
        after: (x) => {
          // 盒子落桌前后使用同一尺寸、中心和朝向，避免交接跳变。
          const held = t < 0.72, a = armSide('n', P, 'F', P.armF.hand);
          const box = held ? handPoint(P, 'F', BOX_OFFSET) : BOX_REST;
          x.save(); x.translate(...box); x.rotate(held ? a.dir + P.armF.rot : 0);
          x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.2;
          x.beginPath(); x.rect(-2.6, -0.75, 5.2, 1.5); x.fill(); x.stroke();
          x.fillStyle = '#9b3a26'; x.fillRect(-2.5, 0, 5, 0.5); x.restore();
          const b = M.base, h = M.head;
          x.strokeStyle = '#d8c39a'; x.lineWidth = 0.35; x.lineCap = 'round'; x.beginPath(); x.moveTo(...b); x.lineTo(...h); x.stroke();
          x.fillStyle = t < 0.2 ? '#8a2f1e' : t < 2.2 ? '#5a2a18' : '#241712'; x.beginPath(); x.arc(h[0], h[1], 0.4, 0, 7); x.fill();
        } }),
      tableFront(),
    ];
  },
  light: (t) => {
    const { P } = pose(t), M = matchAt(t, P), m = matchFlame(t), w = wickFlame(t), lights = [];
    if (m > 0) { const p = S(M.head); lights.push({ x: p[0], y: p[1] - 14, r: 780 * (0.85 + 0.2 * m), color: [1.0, 0.64, 0.32], i: (0.55 + 0.45 * m) * fl(t), falloff: 1.9 }); }
    if (w > 0) { const p = S(WICK); lights.push({ x: p[0], y: p[1] - 30, r: 900 + 1100 * w, color: [1.0, 0.62, 0.30], i: (0.35 + 0.95 * w) * fl(t), falloff: 1.9 }); }
    return { ambient: [0.10, 0.11, 0.17], lights, exposure: 1.0, vignette: 0.5, grain: 7 };
  },
  glow: (t) => {
    const w = wickFlame(t), out = [], p = S(WICK);
    if (w > 0) out.push({ x: p[0], y: p[1] - 25, r: 150 * fl(t) * (0.5 + w), color: [255, 200, 120], a: 0.55 * w + 0.2, core: 0.2 }, { x: p[0], y: p[1] - 70, r: 260, color: [255, 210, 150], a: 0.18 * w, core: 0.4 });
    const m = matchFlame(t); if (m > 0) { const { P } = pose(t), q = S(matchGeom(P).head); out.push({ x: q[0], y: q[1] - 10, r: 90 * (0.7 + 0.4 * m), color: [255, 190, 110], a: 0.5, core: 0.25 }); }
    return out;
  },
  emit: (x, t) => {
    const { P } = pose(t), M = matchAt(t, P), m = matchFlame(t), w = wickFlame(t);
    if (m > 0) { const q = S(M.head); flameShape(x, [q[0], q[1] + 2], 0.42 * m, t); }
    if (w > 0) { const q = S(WICK); flameShape(x, [q[0], q[1] + 2], 0.62 * w * fl(t), t, true); }
    // 灭了的火柴冒的一缕烟（2.2 起，2.5 秒散掉）
    const age = t - 2.2;
    if (age > 0 && age < 2.5) {
      const q = S(M.head);
      x.save(); x.lineCap = 'round';
      for (let k = 0; k < 3; k++) {
        x.strokeStyle = `rgba(200,200,205,${Math.max(0, 0.22 * (1 - age / 2.5) - k * 0.05)})`; x.lineWidth = 3 + k * 4 + age * 6;
        x.beginPath(); x.moveTo(q[0], q[1]); const hh = 60 + age * 140;
        for (let s = 1; s <= 8; s++) { const u = s / 8; x.lineTo(q[0] + 18 * Math.sin(u * 5 + t * 1.7 + k) * u + 30 * u * age, q[1] - hh * u); }
        x.stroke();
      }
      x.restore();
    }
  },
  cam: (t) => ({ x: W / 2 + 10 * seg(t, 3.4, 6), y: H / 2, fit: 1.0 + 0.03 * seg(t, 3.4, 6) }),   // 灯亮以后镜头慢慢推一点
  async render(ctx, t, w, h) { this.bg = await bg(); return renderPaint(ctx, t, w, h, this); },
};
export async function renderFrame(ctx, t, w, h) { return shot.render(ctx, t, w, h); }
export { pose, matchGeom, WICK, leverTip, lift };
