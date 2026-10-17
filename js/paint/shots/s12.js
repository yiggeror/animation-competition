// S12 · 第 4 场：樟木箱。箱盖已经开着靠在后面，箱里叠着蓝印花布，布上平放着那只鹤。
// 奶奶（合作方画的 anim_12_grandma_box_crane：朝右跪着，两只手各攥一根竹签的下端；抠图 assets/chars/g12_box_crane.png）
// 先俯身探进箱子握住签子，然后直起身把鹤立起来——马灯在画外左前方，鹤透出来的彩色光斑落在竖着的箱盖内侧，
// 她轻轻晃，光斑跟着晃（扬琴"叮—咚"在 4.6、5.0 秒）。这就是后面整场皮影戏的原理，先在这里露一下。
// 图里拳头前面露出的短签擦掉，签子由程序从拳心沿原来的签子方向接长到鹤身上的接点（下签→鹤身，上签→脖子）；
// 奶奶俯身/直起用整张图绕膝盖转来做，签子和鹤跟着手一起转，所以签子在拳头里不会折。
// 鹤用和床单戏同一只（js/lamp/crane.js）：正面受光看到的是皮面（'r'），投到箱盖上的是透光色（'t'）。
import { renderPaint, loadImg } from '../paintshot.js';
import { makeCrane } from '../../lamp/crane.js';
import { drawPuppet, solve, pointOn } from '../../puppet.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck } from '../../lamp/choreo.js';
export const DURATION = 8;
const W = 1920, H = 1080, LINE = '#3e2a1e';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// 奶奶图（1536×1024）→ 画面：缩放 0.8，平移 (-40, 260)；绕膝盖转
const G = { img: '/assets/chars/g12_box_crane.png', sc: 0.8, x0: -40, y0: 260, knee: [860, 905],
  grips: [[1050, 412], [965, 630]], tips: [[1172, 380], [1080, 602]],
  erase: [[[1102, 391], [1177, 370], [1181, 388], [1104, 409]], [[1030, 600], [1082, 592], [1084, 608], [1032, 617]]] };
const K = 0.95;                         // 鹤：图像素/毫米（奶奶的图约 9.5 像素/厘米）
const BOX = { x0: 1000, x1: 1860, rim: 800, back: 760, floor: 1040, lidH: 310 };
let CRANE = null;

function action(t) {
  const rise = sstep(2.4, 4.1, t);
  const sway = sstep(4.0, 5.0, t) * (0.025 * Math.sin((t - 4) * 1.3) + 0.012 * Math.sin((t - 4) * 2.7));
  const breath = 0.004 * Math.sin(t * 1.6);
  return { rise, theta: 0.25 * (1 - rise) + sway + breath, squash: 0.3 + 0.7 * rise, neck: sstep(3.4, 4.6, t), sway };
}
// 图像素 → 画面（含绕膝盖的转动）
function groupM(theta) {
  const kf = [G.knee[0] * G.sc + G.x0, G.knee[1] * G.sc + G.y0];
  return new DOMMatrix().translate(kf[0], kf[1]).rotate(theta * 180 / Math.PI).translate(-kf[0], -kf[1]).translate(G.x0, G.y0).scale(G.sc);
}
// 鹤和两根签子（图坐标）
function rig(A) {
  CRANE ||= makeCrane(1.35, 'plain');
  const pose = cranePoseOf(mixNeck(NECK_LOW, NECK_UP, A.neck), { mode: 'stand' }, 0.03 + 2 * A.sway, 1);
  const sol = solve(CRANE, pose);
  const g2 = G.grips[1], t2 = G.tips[1], u2 = [t2[0] - g2[0], t2[1] - g2[1]], l2 = Math.hypot(...u2);
  const body = [g2[0] + u2[0] / l2 * 420, g2[1] + u2[1] / l2 * 420];              // 下签 → 鹤身的接点
  const pb = pointOn(CRANE, sol, 'body', [-75, 6]), pn = pointOn(CRANE, sol, 'neck3', [10, 0]);
  const root = [body[0] - pb[0] * K, body[1] + pb[1] * K * A.squash];
  const neck = [root[0] + pn[0] * K, root[1] - pn[1] * K * A.squash];
  return { pose, root, rods: [[G.grips[0], neck], [g2, body]] };
}
function drawCrane(x, R, A, mode) { x.save(); x.translate(R.root[0], R.root[1]); x.scale(K, -K * A.squash); drawPuppet(x, CRANE, R.pose, mode); x.restore(); }

// 背景（每帧画：箱盖上有鹤的光斑）：暗墙、地、箱子里面的布、竖着的箱盖
let ROOM = null;
async function room() {
  if (ROOM) return ROOM;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(24px)'; x.drawImage(im, 300, 330, 900, 506, -80, -60, W + 160, H + 120); x.filter = 'none';
  const g = x.createLinearGradient(0, 860, 0, H); g.addColorStop(0, '#77736c'); g.addColorStop(1, '#8a857b');
  x.fillStyle = g; x.fillRect(0, 860, W, H - 860);
  return (ROOM = c);
}
const lidPoly = (h) => [[BOX.x0 + 20, BOX.back], [BOX.x1 - 20, BOX.back], [BOX.x1 - 35, BOX.back - h], [BOX.x0 + 35, BOX.back - h]];
async function bg(t, A, R, M) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.drawImage(await room(), 0, 0);
  // 箱盖内侧（浅色樟木板）+ 鹤的透光斑
  const lp = lidPoly(BOX.lidH), path = new Path2D(); lp.forEach((p, i) => (i ? path.lineTo(...p) : path.moveTo(...p))); path.closePath();
  x.fillStyle = '#7a3f22'; x.strokeStyle = LINE; x.lineWidth = 5; x.fill(path); x.stroke(path);
  x.save(); x.clip(path);
  x.fillStyle = '#d2a676'; x.fillRect(BOX.x0 + 40, BOX.back - BOX.lidH + 22, BOX.x1 - BOX.x0 - 80, BOX.lidH - 30);
  x.strokeStyle = 'rgba(90,50,25,0.22)'; x.lineWidth = 2;
  for (let i = 1; i < 8; i++) { const yy = BOX.back - BOX.lidH * i / 8; x.beginPath(); x.moveTo(BOX.x0 + 40, yy); x.lineTo(BOX.x1 - 40, yy + Math.sin(i) * 3); x.stroke(); }
  const show = sstep(0.55, 1.0, A.rise);
  if (show > 0) {
    // 马灯在左前方：影子往右上偏、放大，边缘有点虚；鹤透出来的颜色乘到木板上
    const proj = new OffscreenCanvas(W, H), px = proj.getContext('2d');
    px.fillStyle = '#fff'; px.fillRect(0, 0, W, H);
    const cen = M.transformPoint(new DOMPoint(R.root[0], R.root[1]));
    px.save(); px.filter = 'blur(6px)'; px.globalAlpha = show; px.globalCompositeOperation = 'multiply';
    px.setTransform(new DOMMatrix().translate(cen.x + 240 + 300 * A.sway, cen.y - 70).scale(1.4).translate(-cen.x, -cen.y).multiply(M));
    drawCrane(px, R, A, 't');
    px.strokeStyle = 'rgba(70,45,30,0.7)'; px.lineWidth = 9;
    for (const [a, b] of R.rods) { px.beginPath(); px.moveTo(...a); px.lineTo(...b); px.stroke(); }
    px.restore();
    x.globalCompositeOperation = 'multiply'; x.drawImage(proj, 0, 0); x.globalCompositeOperation = 'source-over';
  }
  x.restore();
  // 箱子里：叠好的蓝印花布（箱沿到后沿一条）
  x.fillStyle = '#2f4a78'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(BOX.x0 + 10, BOX.rim); x.lineTo(BOX.x1 - 10, BOX.rim); x.lineTo(BOX.x1 - 22, BOX.back + 4); x.lineTo(BOX.x0 + 22, BOX.back + 4); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = 'rgba(235,235,225,0.7)';
  for (let i = 0; i < 16; i++) { const cx = BOX.x0 + 50 + i * 52, cy = BOX.rim - 16 + (i % 2) * 6; x.beginPath(); x.arc(cx, cy, 4, 0, 7); x.fill(); x.beginPath(); x.arc(cx + 26, cy - 9, 2.5, 0, 7); x.fill(); }
  return c;
}
// 箱子前板（盖在鹤的腿上面：鹤是立在箱子里的）
let FRONT = null;
function front() {
  if (FRONT) return FRONT;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const g = x.createLinearGradient(0, BOX.rim, 0, BOX.floor); g.addColorStop(0, '#9a5530'); g.addColorStop(1, '#6e3a1e');
  x.fillStyle = 'rgba(20,10,5,0.35)'; x.beginPath(); x.ellipse((BOX.x0 + BOX.x1) / 2, BOX.floor, (BOX.x1 - BOX.x0) / 2 + 30, 18, 0, 0, 7); x.fill();
  x.fillStyle = g; x.strokeStyle = LINE; x.lineWidth = 5; x.beginPath(); x.rect(BOX.x0, BOX.rim, BOX.x1 - BOX.x0, BOX.floor - BOX.rim); x.fill(); x.stroke();
  x.fillStyle = '#3d2014'; x.fillRect(BOX.x0, BOX.rim, BOX.x1 - BOX.x0, 12);
  x.strokeStyle = 'rgba(60,30,15,0.35)'; x.lineWidth = 2;
  for (let i = 0; i < 8; i++) { const yy = BOX.rim + 34 + i * 26; x.beginPath(); x.moveTo(BOX.x0 + 5, yy); for (let xx = BOX.x0 + 5; xx < BOX.x1; xx += 60) x.lineTo(xx, yy + Math.sin(xx * 0.01 + i) * 4); x.stroke(); }
  x.fillStyle = '#c9a046'; x.strokeStyle = LINE; x.lineWidth = 3;
  for (const [cx, s] of [[BOX.x0, 1], [BOX.x1, -1]]) { x.beginPath(); x.moveTo(cx + 36 * s, BOX.rim); x.lineTo(cx, BOX.rim); x.lineTo(cx, BOX.rim + 60); x.closePath(); x.fill(); x.stroke(); }
  const mx = (BOX.x0 + BOX.x1) / 2; x.beginPath(); x.roundRect(mx - 34, BOX.rim + 14, 68, 74, 8); x.fill(); x.stroke();
  x.fillStyle = '#7a5a1e'; x.beginPath(); x.arc(mx, BOX.rim + 58, 8, 0, 7); x.fill();
  return (FRONT = c);
}

const shot = {
  size: [W, H],
  layers: async (t) => {
    const A = action(t), R = rig(A), M = groupM(A.theta);
    const gc = new OffscreenCanvas(W, H), gx = gc.getContext('2d');
    gx.setTransform(M);
    // 签子（在拳头下面，拳头盖住签子穿过的那一截）
    gx.lineCap = 'round';
    for (const [a, b] of R.rods) {
      gx.strokeStyle = LINE; gx.lineWidth = 11; gx.beginPath(); gx.moveTo(...a); gx.lineTo(...b); gx.stroke();
      gx.strokeStyle = '#c99a52'; gx.lineWidth = 7; gx.beginPath(); gx.moveTo(...a); gx.lineTo(...b); gx.stroke();
    }
    const im = await loadImg(G.img);
    gx.save(); gx.beginPath(); gx.rect(-10, -10, im.width + 20, im.height + 20);
    for (const p of G.erase) { p.forEach(([px, py], i) => (i ? gx.lineTo(px, py) : gx.moveTo(px, py))); gx.closePath(); }
    gx.clip('evenodd'); gx.drawImage(im, 0, 0); gx.restore();
    drawCrane(gx, R, A, 'r');
    return [{ img: gc, x: 0, y: 0, sc: 1 }, { img: front(), x: 0, y: 0, sc: 1 }];
  },
  light: (t) => {
    const f = 1 + 0.04 * Math.sin(t * 11) + 0.03 * Math.sin(t * 23);
    return {
      ambient: [0.03, 0.026, 0.03],
      lights: [
        { x: -350, y: 760, r: 2700 * f, color: [1.0, 0.64, 0.32], i: 1.25, falloff: 1.5 },          // 马灯（画外左前方）
        { x: 1350, y: 560, r: 760, color: [1.0, 0.7, 0.42], i: 0.35 * f, falloff: 1.6 },             // 箱盖上的一片光
      ],
      exposure: 1.0, vignette: 0.5, grain: 7,
    };
  },
  glow: () => [],
  cam: (t) => ({ x: W / 2 + 20 * sstep(2, 8, t), y: H / 2 - 10 * sstep(2, 8, t), fit: 1 + 0.04 * sstep(2, 8, t) }),
};
export async function renderFrame(ctx, t, w, h) {
  const A = action(t); shot.bg = await bg(t, A, rig(A), groupM(A.theta));
  return renderPaint(ctx, t, w, h, shot);
}
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
