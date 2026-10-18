// 2-7 中景（6 秒）：黑屋里，奶奶坐在八仙桌边点马灯。人物用代码小人（侧面、面朝右），马灯、桌子、火柴、火苗、烟都是代码画的。
// 节拍（音效对齐 audio/build.py 的 S08：0.2 划火柴、1.8 灯芯着、2.2 甩灭、3.4 灯罩落下"叮"）：
//   0.12～0.2 右手（近手）拿火柴在左手的火柴盒上一擦——0.2 着了，火光一跳，照亮她的脸，她眯一下眼；
//   0.45～0.75 左手把火柴盒放到桌上；0.75～1.12 左手去够灯罩旁边的拨杆，往上一抬，灯罩升起来；
//   1.1～1.7 身子往前探、眼睛盯着灯芯，火柴伸到灯罩下面；1.8 灯芯着了，她眉毛一扬；
//   1.85～2.3 收回火柴、手腕甩两下，2.2 灭了，冒一缕烟；2.4～2.8 把灭了的火柴放到桌上；
//   3.15～3.4 左手松开拨杆，灯罩落下（"叮"），暖光铺开；3.5～4.2 往后坐回去；4.3 看着灯笑开；5.0 眼睛往画面左边（小满那边）一瞟。
import { renderPaint, loadImg } from '../paint/paintshot.js';
import { lamp as drawLamp, flameShape, LX, LB } from '../code/s08.js';
import { key, charLayer, stool, armSide, blink, EASE } from './kit.js';
export const DURATION = 6;
const W = 1920, H = 1080, K = 14, AT = [596, 1793];          // 每厘米 14 像素；奶奶原点（地面、两脚中间）在画面外下方
const TOP = -58, EDGE = 12, LAMP_X = 56, LS = 1 / 18.5;      // 桌面高 58 厘米、桌沿在 x = 12；马灯放在 x = 56，设计坐标 18.5 单位 = 1 厘米（连提梁约 40 厘米）
const SEAT_Y = 27;                                          // 坐着：髋往下挪 27 厘米（凳面 45）
const WICK = [LAMP_X, TOP - 228 * LS];
const S = (p) => [AT[0] + p[0] * K, AT[1] + p[1] * K];       // 地面坐标（厘米）→ 画面像素
const cl = (v) => Math.min(1, Math.max(0, v));
const seg = (t, a, b, e = 'io') => EASE[e](cl((t - a) / (b - a)));
const fl = (t) => 1 + 0.06 * Math.sin(t * 9.3) + 0.04 * Math.sin(t * 17.7) + 0.03 * Math.sin(t * 31);

// 灯罩高低：0.95～1.12 抬起，3.28～3.4 落下（越落越快）
const lift = (t) => seg(t, 0.95, 1.12) * (1 - seg(t, 3.28, 3.4, 'in'));
// 拨杆头（马灯左右镜像过，拨杆朝向奶奶这边）
function leverTip(lf) { const la = 0.55 - lf * 0.9; return [LAMP_X - (150 + 95 * Math.cos(la)) * LS, TOP + (-230 + 95 * Math.sin(la)) * LS]; }
// 火柴火苗大小：0.2 划着先蹿一下，2.2 甩灭；灯芯火苗：1.8 点着，灯罩落下后长大稳住
const matchFlame = (t) => (t < 0.2 || t >= 2.2 ? 0 : t < 0.4 ? 1.6 - (t - 0.2) * 3.75 : 0.85 + 0.06 * Math.sin(t * 19));
const wickFlame = (t) => (t < 1.8 ? 0 : 0.55 * seg(t, 1.8, 2.15, 'out') + 0.45 * seg(t, 3.4, 4.2));

function pose(t) {
  const lean = key(t, [[0, 0.22], [1.1, 0.25], [1.65, 0.5, 'io'], [2.0, 0.42], [3.3, 0.42], [4.2, 0.2, 'io'], [6, 0.2]]);
  const P = { y: SEAT_Y, lean, head: { nod: key(t, [[0, 0.25], [1.1, 0.3], [1.65, 0.45], [3.5, 0.4], [4.2, 0.15], [5.0, 0.15], [5.3, 0.05, 'out'], [6, 0.05]]), tilt: 0 } };
  // 脚：坐着，脚踩在桌子底下的地上
  P.legN = { foot: [30, -4.6 - SEAT_Y] }; P.legF = { foot: [26, -4.6 - SEAT_Y] };
  const toBody = (p) => [p[0], p[1] - SEAT_Y];
  // ---- 右手（近手）：擦火柴 → 举着 → 伸到灯芯 → 收回甩 → 放下
  const tip = (t < 1.1) ? null : key(t, [[1.1, [35, -75]], [1.7, [WICK[0] - 0.6, WICK[1] - 1.0], 'io'], [1.85, [WICK[0] - 0.6, WICK[1] - 1.0]], [2.05, [36, -72], 'out'], [2.4, [36, -72]], [2.8, [30, TOP - 1.2], 'io'], [6, [30, TOP - 1.2]]]);
  let hN = key(t, [[0, [18, -64]], [0.12, [18, -64]], [0.2, [27, -66.5], 'out'], [0.45, [27, -67], 'out'], [1.1, [28, -67]]]);   // 胸口高度擦火柴、举着
  const shake = t > 2.05 && t < 2.35 ? Math.sin((t - 2.05) * 52) * (1 - (t - 2.05) / 0.3) : 0;
  let rotN = -0.9 + 0.5 * shake;                                       // 火柴头朝上（手掌往上翻）
  if (tip) {                                                           // 让火柴头落在目标点上：反推手腕位置（迭代两三次）
    let w = [tip[0] - 7, tip[1] + 1.5];
    for (let i = 0; i < 4; i++) { const a = armSide('n', P, 'N', toBody(w)), d = a.dir + rotN, m = matchTip(a.W, d); w = [w[0] + tip[0] - m[0], w[1] + tip[1] - (m[1] + SEAT_Y)]; }
    hN = w;
    if (t > 2.4) rotN = -0.9 + 0.9 * seg(t, 2.4, 2.8);               // 放下火柴时手放平
  }
  P.armN = { hand: toBody(hN), hp: t > 2.75 ? 'relax' : 'pinch', rot: rotN };
  // ---- 左手（远手）：托火柴盒 → 放到桌上 → 抬拨杆 → 松开 → 收回
  const lv = leverTip(lift(t));
  const hF = t < 0.75 ? key(t, [[0, [22, -63]], [0.12, [22, -63]], [0.2, [21.5, -62.5]], [0.45, [22, -63]], [0.72, [25, TOP - 1.5], 'io']])
    : t < 3.4 ? key(t, [[0.75, [25, TOP - 1.5]], [0.95, [lv[0] - 1.2, lv[1] + 1.2], 'io'], [3.28, [lv[0] - 1.2, lv[1] + 1.2]]]).map((v, i) => (t > 0.95 ? [lv[0] - 1.2, lv[1] + 1.2][i] : v))
    : key(t, [[3.4, [lv[0] - 1.2, lv[1] + 1.2]], [3.9, [19, TOP - 1.5], 'io']]);
  P.armF = { hand: toBody(hF), hp: t < 0.72 ? 'grip' : 'relax', rot: t < 0.72 ? -0.3 : 0 };
  // ---- 脸
  const squint = key(t, [[0.2, 0], [0.24, 1, 'out'], [0.5, 0, 'io']]);
  const focus = key(t, [[1.1, 0], [1.4, 1], [1.8, 1], [2.0, 0.3], [3.3, 0.4], [3.6, 0]]);
  const up = key(t, [[1.8, 0], [1.9, 1, 'out'], [2.3, 0.2]]);
  const smile = key(t, [[0, 0.1], [4.3, 0.12], [4.8, 0.6, 'out'], [6, 0.55]]);
  const look = key(t, [[0, [0.4, 0.5]], [0.5, [0.6, 0.3]], [1.1, [0.8, 0.5]], [1.6, [0.9, 0.7]], [2.05, [0.6, 0.2], 'out'], [2.4, [0.8, 0.5]], [3.5, [0.8, 0.3]], [4.2, [0.7, 0.1]], [5.0, [0.7, 0.1]], [5.2, [-0.7, 0.15], 'out'], [6, [-0.7, 0.15]]]);
  P.face = { look, smile, open: 0.9 - 0.45 * squint - 0.12 * focus + 0.15 * up - 0.25 * seg(t, 4.3, 4.8), brow: 0.25 * up + 0.1 * focus, worry: 0.15 * focus, mouth: 0, blush: 0.3, blink: blink(t, [0.9, 3.0, 5.6]) };
  return { P, hN, hF };
}
// 火柴：手指尖（手腕往前 4.6 厘米）捏着，往前再伸 4.5 厘米是火柴头（人物坐标）
function matchTip(Wr, d) { const b = [Wr[0] + Math.cos(d) * 4.6, Wr[1] + Math.sin(d) * 4.6]; return [b[0] + Math.cos(d - 0.15) * 4.5, b[1] + Math.sin(d - 0.15) * 4.5]; }
function matchGeom(P) {
  const a = armSide('n', P, 'N', P.armN.hand), d = a.dir + (P.armN.rot || 0);
  const b = [a.W[0] + Math.cos(d) * 4.6, a.W[1] + Math.sin(d) * 4.6 + SEAT_Y], h = matchTip(a.W, d);
  return { base: b, head: [h[0], h[1] + SEAT_Y] };                  // 地面坐标
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
  x.save(); x.translate(LAMP_X, TOP - 1.1); x.scale(-LS, LS); x.translate(-LX, -LB); drawLamp(x, lift(t), false); x.restore();
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
    const { P } = pose(t), M = matchGeom(P), mf = matchFlame(t);
    return [
      lampLayer(t),
      charLayer('n', 'side', P, { box: [0, 0, W, H], k: K, at: AT, ss: 1,
        before: (x) => stool(x, -3, 45),
        after: (x) => {
          // 火柴盒：0.72 以前在左手里，之后放在桌上
          const hb = t < 0.72 ? null : [25, TOP - 2.2];
          if (hb) { x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.2; x.beginPath(); x.rect(hb[0] - 2.6, hb[1] - 1.5, 5.2, 1.5); x.fill(); x.stroke(); x.fillStyle = '#9b3a26'; x.fillRect(hb[0] - 2.5, hb[1] - 1.0, 5, 0.5); }
          else { const a = armSide('n', P, 'F', P.armF.hand); x.save(); x.translate(a.W[0], a.W[1] + SEAT_Y); x.rotate(a.dir - 0.3); x.translate(4, -1.2); x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.2; x.beginPath(); x.rect(-2.6, -1.6, 5.2, 3.2); x.fill(); x.stroke(); x.fillStyle = '#9b3a26'; x.fillRect(-2.5, 1.1, 5, 0.5); x.restore(); }
          // 火柴：着之前是红褐的药头，灭了以后是黑头；2.8 以后放在桌上
          const put = t >= 2.8;
          const b = put ? [27, TOP - 2.3] : M.base, h = put ? [31.4, TOP - 2.5] : M.head;
          x.strokeStyle = '#d8c39a'; x.lineWidth = 0.35; x.lineCap = 'round'; x.beginPath(); x.moveTo(...b); x.lineTo(...h); x.stroke();
          x.fillStyle = t < 0.2 ? '#8a2f1e' : t < 2.2 ? '#5a2a18' : '#241712'; x.beginPath(); x.arc(h[0], h[1], 0.4, 0, 7); x.fill();
        } }),
      tableFront(),
    ];
  },
  light: (t) => {
    const { P } = pose(t), M = matchGeom(P), m = matchFlame(t), w = wickFlame(t), lights = [];
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
    const { P } = pose(t), M = matchGeom(P), m = matchFlame(t), w = wickFlame(t);
    if (m > 0) { const q = S(M.head); flameShape(x, [q[0], q[1] + 2], 0.42 * m, t); }
    if (w > 0) { const q = S(WICK); flameShape(x, [q[0], q[1] + 2], 0.62 * w * fl(t), t, true); }
    // 灭了的火柴冒的一缕烟（2.2 起，2.5 秒散掉）
    const age = t - 2.2;
    if (age > 0 && age < 2.5) {
      const q = S(t < 2.8 ? M.head : [31.4, TOP - 2.5]);
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
