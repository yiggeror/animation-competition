// S12 · 第 4 场：木箱。樟木箱的盖子"吱——"地开到底，里面叠着蓝印花布，布上平放着那只鹤。
// 奶奶的两只手从下面伸进来，握住两根竹签，把鹤立起来、举高——马灯在画外左前方，鹤透出来的彩色光斑落在竖着的箱盖内侧上，
// 随着她轻轻转动，光斑跟着晃（扬琴"叮—咚"在 4.6、5.0 秒）。这就是后面整场皮影戏的原理，先在这里露一下。
// 鹤用和床单戏同一只（js/lamp/crane.js）：正面受光看到的是皮面（'r'），投到箱盖上的是透光色（'t'）。
import { makeCrane } from '../lamp/crane.js';
import { drawPuppet, solve, pointOn } from '../puppet.js';
import { NECK_UP, NECK_LOW, cranePoseOf, mixNeck } from '../lamp/choreo.js';
import { drawHand, POSES, orient, shade } from './hand3d.js';
export const DURATION = 8;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;
let CRANE = null;
const RIM = 700;                          // 箱沿（画面 y）

// ---------------------------------------------------------------- 箱子：前板、箱沿、里面的布；箱盖（open 0..1，1 = 竖直靠住）
function box(x, open) {
  // 箱盖：开的过程中从斜着到竖直（透视里高度从短变长）
  const lidH = lerp(140, 470, open), lidTop = RIM - 30 - lidH;
  x.fillStyle = '#7a3f22'; x.strokeStyle = LINE; x.lineWidth = 5;
  x.beginPath(); x.moveTo(250, RIM - 30); x.lineTo(1670, RIM - 30); x.lineTo(1640, lidTop); x.lineTo(280, lidTop); x.closePath(); x.fill(); x.stroke();
  // 箱盖内侧的浅色木板（光斑落在这里）
  x.fillStyle = '#c99a6a'; x.beginPath(); x.moveTo(300, RIM - 50); x.lineTo(1620, RIM - 50); x.lineTo(1600, lidTop + 24); x.lineTo(320, lidTop + 24); x.closePath(); x.fill();
  x.strokeStyle = 'rgba(90,50,25,0.25)'; x.lineWidth = 2;
  for (let i = 1; i < 9; i++) { const yy = lerp(RIM - 50, lidTop + 24, i / 9); x.beginPath(); x.moveTo(305, yy); x.lineTo(1615, yy + Math.sin(i) * 3); x.stroke(); }
  // 箱子里：叠好的蓝印花布
  x.fillStyle = '#2f4a78'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(230, RIM + 10); x.lineTo(1690, RIM + 10); x.lineTo(1660, RIM - 26); x.lineTo(260, RIM - 26); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = 'rgba(235,235,225,0.75)';
  for (let i = 0; i < 26; i++) { const cx = 300 + i * 54, cy = RIM - 8 + (i % 2) * 6; x.beginPath(); x.arc(cx, cy, 5, 0, 7); x.fill(); x.beginPath(); x.arc(cx + 27, cy - 10, 3, 0, 7); x.fill(); }
  // 前板：樟木，铜包角，铜搭扣
  const g = x.createLinearGradient(0, RIM, 0, RH); g.addColorStop(0, '#9a5530'); g.addColorStop(1, '#6e3a1e');
  x.fillStyle = g; x.strokeStyle = LINE; x.lineWidth = 5;
  x.beginPath(); x.rect(200, RIM + 10, 1520, RH - RIM); x.fill(); x.stroke();
  x.fillStyle = '#3d2014'; x.fillRect(200, RIM + 10, 1520, 14);
  x.strokeStyle = 'rgba(60,30,15,0.35)'; x.lineWidth = 2;
  for (let i = 0; i < 14; i++) { const yy = RIM + 40 + i * 26; x.beginPath(); x.moveTo(205, yy); for (let xx = 205; xx < 1715; xx += 60) x.lineTo(xx, yy + Math.sin(xx * 0.01 + i) * 5); x.stroke(); }
  x.fillStyle = '#c9a046'; x.strokeStyle = LINE; x.lineWidth = 3;
  for (const cx of [200, 1720]) { x.beginPath(); x.moveTo(cx - 40 * Math.sign(cx - 960), RIM + 10); x.lineTo(cx, RIM + 10); x.lineTo(cx, RIM + 80); x.closePath(); x.fill(); x.stroke(); }
  x.beginPath(); x.roundRect(920, RIM + 18, 80, 90, 8); x.fill(); x.stroke();
  x.fillStyle = '#7a5a1e'; x.beginPath(); x.arc(960, RIM + 70, 9, 0, 7); x.fill();
  return { lid: [[300, RIM - 50], [1620, RIM - 50], [1600, lidTop + 24], [320, lidTop + 24]] };
}

function action(t) {
  const open = sstep(-0.2, 0.9, t);
  const reach = sstep(1.3, 2.2, t);                 // 手伸进来
  const rise = sstep(2.4, 4.1, t);                  // 把鹤立起来、举高
  const sway = sstep(4.0, 5.0, t) * (0.06 * Math.sin((t - 4) * 1.1) + 0.03 * Math.sin((t - 4) * 2.3));
  return { open, reach, rise, sway };
}

export async function renderFrame(ctx, t, W, H) {
  CRANE ||= makeCrane(1.35, 'plain');
  const A = action(t);
  const neck = mixNeck(NECK_LOW, NECK_UP, sstep(3.4, 4.6, t));
  const pose = cranePoseOf(neck, { mode: 'stand' }, 0.04 + A.sway, 1);
  const sol = solve(CRANE, pose);
  // 鹤的位置：平躺在布上（压扁）→ 立起来、举到画面中间。k 像素/毫米
  const k = 0.8;
  const lie = 1 - A.rise;
  const root = [lerp(860, 900, A.rise) + A.sway * 300, lerp(RIM - 4, 590, A.rise)];
  const squash = lerp(0.28, 1, A.rise);
  // 前景层：鹤（皮面）+ 签子 + 手
  const fg = new OffscreenCanvas(RW, RH), fx = fg.getContext('2d');
  fx.save(); fx.translate(root[0], root[1]); fx.scale(k, -k * squash); drawPuppet(fx, CRANE, pose, 'r'); fx.restore();
  // 签子：从鹤身上的两个接点往下伸到手里
  const rodTop = [pointOn(CRANE, sol, 'body', [-75, 6]), pointOn(CRANE, sol, 'neck3', [10, 0])].map((p) => [root[0] + p[0] * k, root[1] - p[1] * k * squash]);
  const handAt = [[lerp(470, 580, A.rise), lerp(1320, 1045, A.reach) + 30 * lie], [lerp(1420, 1310, A.rise), lerp(1340, 1055, A.reach) + 30 * lie]];
  fx.lineCap = 'round';
  if (A.reach > 0.3) for (let i = 0; i < 2; i++) {
    const a = rodTop[i], b = [handAt[i][0], handAt[i][1] + 40];
    fx.strokeStyle = LINE; fx.lineWidth = 9; fx.beginPath(); fx.moveTo(...a); fx.lineTo(...b); fx.stroke();
    fx.strokeStyle = '#d8b878'; fx.lineWidth = 5; fx.beginPath(); fx.moveTo(...a); fx.lineTo(...b); fx.stroke();
  }
  const HAND = { skin: '#efc19c', skinShade: '#cf9672', light: [1, 1, 1], sleeve: '#4b5872', sleeveAt: 4.5, forearm: 34, lineW: 3, shadeA: 0.35 };
  for (let i = 0; i < 2; i++) {
    if (A.reach < 0.02) break;
    const side = i === 0 ? -1 : 1;
    // 拳头竖着握住签子：手背朝镜头，四指横着绕过签子，前臂往下伸出画面
    const R = orient(side * 0.35, -0.35, side * 0.45);               // 拳头握住签子，前臂往外下方伸出画面
    const pr = drawHand(fx, { dry: true, side, pose: POSES.grip, R, at: [0, 0], px: 26 });
    drawHand(fx, { side, pose: POSES.grip, R, at: [handAt[i][0] - pr.grip[0], handAt[i][1] - pr.grip[1]], px: 26, ...HAND });
  }
  // ---- 背景层（固有色）
  const bgc = new OffscreenCanvas(RW, RH), bx = bgc.getContext('2d');
  bx.fillStyle = '#5a4634'; bx.fillRect(0, 0, RW, RH);                 // 远处的墙（很暗）
  const B = box(bx, A.open);
  // ---- 光：马灯在画外左前方（暖），其余很暗
  const light = new OffscreenCanvas(RW, RH), lx = light.getContext('2d');
  lx.fillStyle = 'rgb(30,24,22)'; lx.fillRect(0, 0, RW, RH);
  lx.globalCompositeOperation = 'lighter';
  const fl = 1 + 0.04 * Math.sin(t * 11) + 0.03 * Math.sin(t * 23);
  const g = lx.createRadialGradient(-200, 1100, 100, -200, 1100, 2300 * fl); g.addColorStop(0, 'rgba(255,200,130,1)'); g.addColorStop(0.5, 'rgba(230,150,80,0.75)'); g.addColorStop(1, 'rgba(120,70,40,0)');
  lx.fillStyle = g; lx.fillRect(0, 0, RW, RH);
  // 箱盖上的光：同样的灯光 × 鹤的透光色（放大、往右上偏，带一点模糊）
  const proj = new OffscreenCanvas(RW, RH), px2 = proj.getContext('2d');
  px2.fillStyle = '#fff'; px2.fillRect(0, 0, RW, RH);
  if (A.rise > 0.5) {
    const m = 1.45, off = [260 + A.sway * 500, -120];
    px2.save(); px2.filter = `blur(${7 + 4 * (1 - A.rise)}px)`; px2.globalAlpha = sstep(0.5, 1.0, A.rise);
    px2.translate(root[0] + off[0], root[1] + off[1]); px2.scale(k * m, -k * m * squash); px2.globalCompositeOperation = 'multiply';
    drawPuppet(px2, CRANE, pose, 't'); px2.restore();
    // 签子的影子
    px2.strokeStyle = 'rgba(60,40,30,0.6)'; px2.lineWidth = 10; px2.filter = 'blur(6px)';
    for (const a of rodTop) { const pa = [root[0] + off[0] + (a[0] - root[0]) * m, root[1] + off[1] + (a[1] - root[1]) * m]; px2.beginPath(); px2.moveTo(...pa); px2.lineTo(pa[0] + 120, pa[1] + 700); px2.stroke(); }
  }
  const lidLight = new OffscreenCanvas(RW, RH), ll = lidLight.getContext('2d');
  ll.drawImage(light, 0, 0);
  ll.save(); ll.beginPath(); B.lid.forEach((p, i) => (i ? ll.lineTo(...p) : ll.moveTo(...p))); ll.closePath(); ll.clip();
  ll.globalCompositeOperation = 'lighter'; const gl2 = ll.createRadialGradient(1100, 420, 50, 1100, 420, 900); gl2.addColorStop(0, `rgba(255,210,150,${0.55 * fl})`); gl2.addColorStop(1, 'rgba(255,180,110,0.1)');
  ll.fillStyle = gl2; ll.fillRect(0, 0, RW, RH); ll.restore();
  ll.save(); ll.beginPath(); B.lid.forEach((p, i) => (i ? ll.lineTo(...p) : ll.moveTo(...p))); ll.closePath(); ll.clip();
  ll.globalCompositeOperation = 'multiply'; ll.drawImage(proj, 0, 0); ll.restore();
  // 合成：背景 × （带光斑的）光；前景 × 光（只在前景有东西的地方）
  bx.globalCompositeOperation = 'multiply'; bx.drawImage(lidLight, 0, 0);
  const fl2 = new OffscreenCanvas(RW, RH), f2 = fl2.getContext('2d');
  f2.drawImage(fg, 0, 0); f2.globalCompositeOperation = 'multiply'; f2.drawImage(light, 0, 0); f2.globalCompositeOperation = 'destination-in'; f2.drawImage(fg, 0, 0);
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  ctx.drawImage(bgc, 0, 0); ctx.drawImage(fl2, 0, 0);
  const v = ctx.createRadialGradient(RW * 0.45, RH * 0.5, RH * 0.3, RW * 0.5, RH * 0.5, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 12;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 7; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
