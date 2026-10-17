// S30 · 第 12 场：关灯（临时版，等小满拉灯绳的图 anim_32_xiaoman_pull_cord）。
// 门边墙上的拉线开关特写：日光灯惨白，吊扇的风吹得灯绳轻轻晃；画外脚步声走过来（1.5～4.0）；
// 5.5 灯绳被往下一拽（拉的手在画外下边），5.95"咔嗒"——日光灯灭了，6.6 电视也关了；
// 屋里一下子黑成蓝的，然后马灯的暖光从右边（床单那边）慢慢显出来，灯绳弹回去还在晃。
import { renderPaint, loadImg } from '../paintshot.js';
export const DURATION = 12;
const T_OFF = 6.0;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const W = 1920, H = 1080, LINE = '#3e2a1e';
const TOP = [1180, 150];                       // 开关盒（灯绳从这里垂下来）

let BG = null;
async function bg() {
  if (BG) return BG;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(10px)'; x.drawImage(im, 560, 230, 300, 169, -40, -30, W + 80, H + 60); x.filter = 'none';   // 门框上边一带的墙
  // 墙上沿着走的旧电线（从开关盒往左出画）
  x.strokeStyle = '#efeee8'; x.lineWidth = 9; x.beginPath(); x.moveTo(-20, 120); x.quadraticCurveTo(600, 150, TOP[0] - 40, TOP[1] - 10); x.stroke();
  x.strokeStyle = 'rgba(62,42,30,0.6)'; x.lineWidth = 2; x.stroke();
  return (BG = c);
}
// 灯绳：上端固定在开关盒，下端坠一个塑料坠子；pull = 往下拽的长度（像素），swing = 摆角
function cordState(t) {
  const pull = 260 * (sstep(5.5, 5.92, t) - sstep(5.98, 6.12, t));
  const kick = t > 6.05 ? Math.exp(-(t - 6.05) * 0.9) * Math.sin((t - 6.05) * 5.5) * 0.12 : 0;     // 松手后弹回来来回晃
  const fan = t < T_OFF ? 0.025 * Math.sin(t * 2.1) + 0.012 * Math.sin(t * 5.3) : 0.025 * Math.exp(-(t - T_OFF) * 0.3) * Math.sin(t * 2.1);
  const bounce = t > 6.05 ? -40 * Math.exp(-(t - 6.05) * 3) * Math.cos((t - 6.05) * 14) : 0;
  return { len: 640 + pull + bounce, ang: fan + kick };
}
function cordLayer(t) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const C = cordState(t);
  // 开关盒：拉线开关（白塑料圆盒）
  x.fillStyle = 'rgba(0,0,0,0.25)'; x.beginPath(); x.ellipse(TOP[0] + 10, TOP[1] + 14, 78, 36, 0, 0, 7); x.fill();
  x.fillStyle = '#f1efe6'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.ellipse(TOP[0], TOP[1], 74, 32, 0, 0, 7); x.fill(); x.stroke();
  x.beginPath(); x.roundRect(TOP[0] - 52, TOP[1] - 6, 104, 46, 14); x.fill(); x.stroke();
  x.fillStyle = 'rgba(160,150,120,0.3)'; x.fillRect(TOP[0] - 46, TOP[1] + 22, 92, 8);
  // 灯绳（略带弧）+ 坠子
  const end = [TOP[0] + Math.sin(C.ang) * C.len, TOP[1] + 40 + Math.cos(C.ang) * C.len];
  x.strokeStyle = '#e8e2cf'; x.lineWidth = 5; x.lineCap = 'round';
  x.beginPath(); x.moveTo(TOP[0], TOP[1] + 40); x.quadraticCurveTo(TOP[0] + Math.sin(C.ang) * C.len * 0.45 + 8, TOP[1] + 40 + C.len * 0.5, end[0], end[1]); x.stroke();
  x.strokeStyle = 'rgba(62,42,30,0.45)'; x.lineWidth = 1.5; x.stroke();
  x.save(); x.translate(end[0], end[1]); x.rotate(-C.ang);
  x.fillStyle = '#d9c9a0'; x.strokeStyle = LINE; x.lineWidth = 3; x.beginPath(); x.ellipse(0, 26, 15, 28, 0, 0, 7); x.fill(); x.stroke();
  x.fillStyle = 'rgba(255,255,240,0.5)'; x.beginPath(); x.ellipse(-5, 18, 4, 10, 0, 0, 7); x.fill();
  x.restore();
  return c;
}
const tv = (t) => (t < 6.6 ? 0.25 + 0.1 * Math.sin(t * 7.1) + 0.06 * Math.sin(t * 13) : 0);
const shot = {
  size: [W, H],
  layers: async (t) => [{ img: cordLayer(t), x: 0, y: 0, sc: 1 }],
  light: (t) => {
    const lit = t < T_OFF ? 1 : 0, warm = sstep(6.4, 9.0, t);
    const f = 1 + 0.04 * Math.sin(t * 11) + 0.03 * Math.sin(t * 23);
    return {
      ambient: lit ? [0.64, 0.67, 0.73] : [0.03, 0.035, 0.06],
      lights: [
        { x: -300, y: 700, r: 1500, color: [0.55, 0.7, 1.0], i: tv(t), falloff: 1.5 },                       // 电视
        { x: 2400, y: 900, r: 2600 * f, color: [1.0, 0.62, 0.30], i: 0.75 * warm, falloff: 1.6 },            // 马灯（床单后面）
      ],
      exposure: 1.0, vignette: lit ? 0.3 : 0.55, grain: lit ? 5 : 8,
    };
  },
  glow: () => [],
  cam: (t) => ({ x: W / 2 + 30 * sstep(0, 5.5, t), y: H / 2 + 20 * sstep(0, 5.5, t), fit: 1 + 0.06 * sstep(0, 5.5, t) }),
};
export async function renderFrame(ctx, t, w, h) { shot.bg = await bg(); return renderPaint(ctx, t, w, h, shot); }
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
