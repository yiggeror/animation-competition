// S28 · 第 10 场：来电以后。日光灯惨白地亮着，吊扇转起来（0.2），电视"嘶"地亮了（1.4）。
// 0～3.2 秒：奶奶的近景（合作方画的 anim_10_grandma_squint），被突然的白光晃得眯起眼、往后一缩；吊扇叶子的影子一下下扫过。
// 3.2～8 秒：俯拍竹席，一地毛豆壳中间躺着小满的手机，插着充电线；5.5 秒屏幕亮起充电图标（"叮"，audio/build.py）。
// 两个人一起眯眼的全景等合作方的图（anim_28_both_squint）到了再换。
import { renderPaint, loadImg } from '../paintshot.js';
import { mat } from '../../code/phone.js';
export const DURATION = 8;
const T_CUT = 3.2, T_CHG = 5.5;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// 吊扇：0.2 秒通电，慢慢转快；叶子的影子扫过（三片叶子，每转一圈扫三下）
const fanPhase = (t) => { const u = Math.max(0, t - 0.2); return 3 * (0.35 * u * u / (1 + 0.4 * u)); };
const fanShade = (t) => (t < 0.2 ? 0 : 0.06 * Math.max(0, Math.sin(2 * Math.PI * fanPhase(t))) ** 3 * Math.min(1, (t - 0.2) * 2));

// ---------------------------------------------------------------- 奶奶近景
let CLOSE_BG = null;
async function closeBg() {
  if (CLOSE_BG) return CLOSE_BG;
  const bg = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.filter = 'blur(22px)'; x.drawImage(bg, 980, 200, 520, 292, -60, -40, 2040, 1160);
  return (CLOSE_BG = c);
}
const close = {
  size: [1920, 1080],
  layers: async (t) => {
    const flinch = sstep(0.0, 0.35, t) * (1 - 0.5 * sstep(0.6, 1.6, t));
    return [{ img: '/assets/chars/g10_squint.png', x: 540 + 26 * flinch, y: 60 + 4 * flinch, sc: 0.72, rot: 0.018 * flinch }];
  },
  light: (t) => ({
    ambient: [0.62 - fanShade(t), 0.66 - fanShade(t), 0.72 - fanShade(t)],
    lights: [
      { x: 1000, y: -400, r: 2300, color: [0.94, 0.97, 1.0], i: 0.6, falloff: 1.2 },                        // 头顶的日光灯
      { x: -200, y: 600, r: 1300, color: [0.55, 0.7, 1.0], i: t > 1.4 ? 0.3 + 0.1 * Math.sin(t * 7.1) : 0, falloff: 1.5 },   // 电视亮了
    ],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  glow: () => [],
  cam: () => ({ x: 960, y: 540, fit: 1 }),
};

// ---------------------------------------------------------------- 竹席上的手机（俯拍）
const PH = { x: 960, y: 560, w: 1000, h: 480, r: 66, rot: -0.12 };
let FLOOR = null;
function floor() {
  if (FLOOR) return FLOOR;
  const c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.drawImage(mat(), -340, -310);
  // 一地毛豆壳：剥开的豆荚，两瓣，绿里带黄
  let seed = 31; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 26; i++) {
    const px = rnd() * 1920, py = rnd() * 1080;
    if (Math.abs(px - PH.x) < 560 && Math.abs(py - PH.y) < 300) continue;
    x.save(); x.translate(px, py); x.rotate(rnd() * 6.3);
    // 豆荚壳的两瓣：鼓鼓的外壳（绿，带细毛的哑光）+ 翻开露出的浅色内面，几个鼓包是豆子撑出来的
    for (const s of [-1, 1]) {
      x.save(); x.rotate(s * (0.25 + rnd() * 0.35)); x.translate(0, s * 6);
      const L = 80 + rnd() * 25, Wd = 20;
      x.fillStyle = rnd() < 0.3 ? '#a3b154' : '#78a043'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 2.5;
      x.beginPath(); x.moveTo(0, 0);
      for (let k = 0; k <= 3; k++) { const u = (k + 0.5) / 3.5; x.quadraticCurveTo(L * (u - 0.07), -s * (Wd + 3), L * (u + 0.07), -s * Wd * 0.85); }
      x.quadraticCurveTo(L * 1.02, -s * Wd * 0.3, L, 0); x.quadraticCurveTo(L * 0.5, s * 5, 0, 0); x.closePath(); x.fill(); x.stroke();
      x.fillStyle = 'rgba(214,226,160,0.9)'; x.beginPath(); x.ellipse(L * 0.5, -s * Wd * 0.38, L * 0.38, Wd * 0.28, 0, 0, 7); x.fill();
      x.restore();
    }
    x.restore();
  }
  return (FLOOR = c);
}
// 手机：深灰机身、黑屏；插着白色充电线（从手机底边伸出去出画）
function phone(scrOn, t) {
  const c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.translate(PH.x, PH.y); x.rotate(PH.rot);
  // 充电线
  x.lineCap = 'round'; const cab = new Path2D(); cab.moveTo(-PH.w / 2 - 4, 40); cab.bezierCurveTo(-PH.w / 2 - 200, 60, -PH.w / 2 - 260, 360, -PH.w / 2 - 700, 520);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 26; x.stroke(cab); x.strokeStyle = '#f1f1ec'; x.lineWidth = 18; x.stroke(cab);
  x.fillStyle = '#e9e9e4'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 3; x.beginPath(); x.roundRect(-PH.w / 2 - 60, 22, 64, 36, 6); x.fill(); x.stroke();
  // 机身
  x.fillStyle = '#26282c'; x.strokeStyle = '#141516'; x.lineWidth = 5; x.beginPath(); x.roundRect(-PH.w / 2, -PH.h / 2, PH.w, PH.h, PH.r); x.fill(); x.stroke();
  const sw = PH.w - 44, sh = PH.h - 40;
  x.fillStyle = '#07080a'; x.beginPath(); x.roundRect(-sw / 2, -sh / 2, sw, sh, PH.r - 18); x.fill();
  x.fillStyle = '#0d0e10'; x.beginPath(); x.arc(-sw / 2 + 28, 0, 10, 0, 7); x.fill();
  if (scrOn > 0) {
    // 充电界面：黑底，中间一节电池，红色的一小格，闪电；下面"1%"
    x.save(); x.globalAlpha = scrOn;
    const bw = 230, bh = 110, pulse = 0.6 + 0.4 * Math.sin((t - T_CHG) * 3);
    x.strokeStyle = '#e8e8e8'; x.lineWidth = 8; x.beginPath(); x.roundRect(-bw / 2, -bh / 2 - 20, bw, bh, 18); x.stroke();
    x.fillStyle = '#e8e8e8'; x.fillRect(bw / 2 + 6, -20 - 20, 14, 40);
    x.fillStyle = `rgba(255,75,62,${pulse})`; x.fillRect(-bw / 2 + 12, -bh / 2 - 8, 16, bh - 24);
    x.fillStyle = '#58d36a'; x.strokeStyle = '#1b1b1b'; x.lineWidth = 4;
    x.beginPath(); x.moveTo(10, -78); x.lineTo(-30, -14); x.lineTo(-4, -14); x.lineTo(-16, 38); x.lineTo(30, -28); x.lineTo(4, -28); x.closePath(); x.stroke(); x.fill();
    x.fillStyle = '#e8e8e8'; x.font = '600 52px "Noto Sans SC"'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('1%', 0, 110);
    x.restore();
  }
  // 玻璃的一道斜反光
  const g = x.createLinearGradient(-sw * 0.3, -sh / 2, sw * 0.1, sh / 2); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(230,240,255,0.10)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.beginPath(); x.roundRect(-sw / 2, -sh / 2, sw, sh, PH.r - 18); x.fill();
  return c;
}
const scrOn = (t) => sstep(T_CHG, T_CHG + 0.15, t);
const top = {
  size: [1920, 1080],
  layers: async (t) => [{ img: phone(scrOn(t), t), x: 0, y: 0, sc: 1 }],
  light: (t) => ({
    ambient: [0.66 - fanShade(t), 0.7 - fanShade(t), 0.76 - fanShade(t)],
    lights: [{ x: 700, y: -300, r: 2400, color: [0.94, 0.97, 1.0], i: 0.5, falloff: 1.2 }],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  // 屏幕自己发光：亮起来以后把屏幕区域提亮（发光的东西不该被环境光压暗）
  glow: (t) => (scrOn(t) > 0 ? [{ x: PH.x, y: PH.y - 10, r: 260, color: [120, 230, 140], a: 0.12 * scrOn(t), core: 0.3 }] : []),
  emit: (x, t) => {
    const s = scrOn(t); if (s <= 0) return;
    // 屏幕上的图标直接再画一遍在光照之后（自发光，不受日光灯明暗影响）
    x.globalAlpha = 0.85 * s; x.drawImage(phone(1, t), 0, 0); x.globalAlpha = 1;
  },
  cam: (t) => { const k = sstep(T_CUT, 8, t); return { x: 960 + 20 * k, y: 540, fit: 1 + 0.12 * k }; },
};

export async function renderFrame(ctx, t, W, H) {
  if (t < T_CUT) { close.bg = await closeBg(); return renderPaint(ctx, t, W, H, close); }
  top.bg = floor(); return renderPaint(ctx, t, W, H, top);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
