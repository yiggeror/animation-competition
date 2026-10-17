// S09 · 第 3 场：小满跪在电视柜前，两只手捧着刚从抽屉里翻出来的旧手电（合作方画的 anim_09_xiaoman_flashlight，
// 抠图 assets/chars/x09_flashlight.png），一脸疑惑。马灯在她前面（画面右边、桌上），暖光从右边照在脸上。
// 1.6 推开关——不亮（"咔"）；2.1、2.5 往手心上磕两下（整个人跟着一顿，2.5 那下灯泡闪了一下又灭）；2.9 再推——亮了，
// 一道冷白的光柱往右边打出去，空气里的灰被照亮，手和脸被手电头反上来的光照亮。时间对上 audio/build.py 的 S09。
// "拍"：合作方另画了抬手的 B（anim_09_xiaoman_flashlight_slap，右手举在手电上方）。脸、腿、托着手电的左手都用 A，
// 只把"右胳膊 + 两只手 + 手电"这一块（REG，边缘羽化）换成 B——每下拍之前抬手 4 帧（B），拍下去回到 A、整个人一顿。
// 推开关的拇指动作看不见。
import { renderPaint, loadImg } from '../paintshot.js';
export const DURATION = 4;
const W = 1920, H = 1080;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// 图（1536×1024）→ 画面：缩放 1.0，左上角放在 (OX, OY)；手电头（灯头玻璃的中心）在图上 (1088, 488)
const OX = 120, OY = 60, HEAD = [1088, 488];
const REG = [[540, 450], [630, 390], [870, 365], [1075, 360], [1080, 425], [970, 465], [970, 580], [880, 595], [830, 660], [660, 670], [540, 590]];
const UP = [[1.92, 2.08], [2.33, 2.48]];          // 抬手（B）的时间段，各约 4 帧；拍下去在 2.1、2.5
const up = (t) => UP.some(([a, b]) => t >= a && t < b);
let AB = null;
async function abLayers() {
  if (AB) return AB;
  const A = await loadImg('/assets/chars/x09_flashlight.png'), B = await loadImg('/assets/chars/x09_flashlight_slap.png');
  const mask = new OffscreenCanvas(A.width, A.height), mx = mask.getContext('2d');
  mx.filter = 'blur(7px)'; mx.fillStyle = '#000'; mx.beginPath(); REG.forEach(([x, y], i) => (i ? mx.lineTo(x, y) : mx.moveTo(x, y))); mx.closePath(); mx.fill();
  const aCut = new OffscreenCanvas(A.width, A.height), ax = aCut.getContext('2d');
  ax.drawImage(A, 0, 0); ax.globalCompositeOperation = 'destination-out'; ax.drawImage(mask, 0, 0);
  const bReg = new OffscreenCanvas(A.width, A.height), bx = bReg.getContext('2d');
  bx.drawImage(B, 0, 0); bx.globalCompositeOperation = 'destination-in'; bx.drawImage(mask, 0, 0);
  const both = new OffscreenCanvas(A.width, A.height), cx = both.getContext('2d'); cx.drawImage(aCut, 0, 0); cx.drawImage(bReg, 0, 0);
  return (AB = { A, slap: both });
}
const T_ON = 2.9, SLAPS = [2.1, 2.5];
const jolt = (t) => SLAPS.reduce((a, p) => a + (t > p && t < p + 0.3 ? Math.exp(-(t - p) * 16) * Math.sin((t - p) * 38) : 0), 0);
const on = (t) => (t >= T_ON ? sstep(T_ON, T_ON + 0.05, t) : t > 2.52 && t < 2.58 ? 0.35 : 0);
const headF = (t) => [HEAD[0] + OX, HEAD[1] + OY + 14 * jolt(t)];
const BEAM = -0.04;                          // 光柱方向（弧度，略往上）

let BG = null;
async function bg() {
  if (BG) return BG;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(18px)'; x.drawImage(im, 0, 330, 820, 461, -60, -40, W + 120, H + 80); x.filter = 'none';   // 电视柜一带
  const g = x.createLinearGradient(0, 900, 0, H); g.addColorStop(0, 'rgba(120,115,105,0)'); g.addColorStop(1, 'rgba(120,115,105,0.6)');
  x.fillStyle = g; x.fillRect(0, 900, W, H - 900);
  return (BG = c);
}
const shot = {
  size: [W, H],
  layers: async (t) => {
    const j = jolt(t), L = await abLayers();
    return [{ img: up(t) ? L.slap : L.A, x: OX, y: OY + 14 * j + 1.6 * Math.sin(t * 1.8), sc: 1, rot: 0.006 * j }];
  },
  light: (t) => {
    const f = 1 + 0.04 * Math.sin(t * 11) + 0.03 * Math.sin(t * 23), o = on(t), h = headF(t);
    const lights = [{ x: 2350, y: 260, r: 2500 * f, color: [1.0, 0.63, 0.31], i: 1.1, falloff: 1.5 }];   // 马灯（右前方）
    if (o > 0) lights.push({ x: h[0] - 40, y: h[1] - 30, r: 520, color: [0.85, 0.9, 1.0], i: 0.55 * o, falloff: 1.6 });   // 手电头反上来的光
    return {
      ambient: [0.03, 0.03, 0.045], lights,
      cone: o > 0 ? { x: h[0] + 30, y: h[1], ang: BEAM, spread: 0.11, len: 2000, color: [0.95, 0.96, 1.0], i: 0.9 * o, soft: 50 } : null,
      exposure: 1.0, vignette: 0.45, grain: 7,
    };
  },
  glow: (t) => { const o = on(t), h = headF(t); return o > 0 ? [{ x: h[0] + 22, y: h[1], r: 90, color: [235, 242, 255], a: 0.9 * o, core: 0.15 }] : []; },
  // 看得见的光柱（空气里的灰被照亮）
  emit: (x, t) => {
    const o = on(t); if (o <= 0) return;
    const h = headF(t), S = [h[0] + 30, h[1]], L = 1900;
    x.globalCompositeOperation = 'lighter'; x.filter = 'blur(10px)';
    const g = x.createRadialGradient(S[0], S[1], 0, S[0], S[1], L);
    g.addColorStop(0, `rgba(235,242,255,${0.2 * o})`); g.addColorStop(1, 'rgba(255,248,230,0)');
    x.fillStyle = g; x.beginPath(); x.moveTo(S[0], S[1] - 26); x.arc(S[0], S[1], L, BEAM - 0.1, BEAM + 0.1); x.lineTo(S[0], S[1] + 26); x.closePath(); x.fill();
    x.filter = 'none';
    // 灰尘：光柱里几粒亮点慢慢飘
    let seed = 5; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 40; i++) {
      const d = 120 + rnd() * 1500, off = (rnd() - 0.5) * 2 * Math.tan(0.09) * d + 10 * Math.sin(t * 0.7 + i);
      const px = S[0] + d * Math.cos(BEAM) - off * Math.sin(BEAM), py = S[1] + d * Math.sin(BEAM) + off * Math.cos(BEAM) + 8 * Math.sin(t * 0.5 + i * 1.3);
      x.fillStyle = `rgba(255,250,235,${0.35 * o * (1 - d / 1700)})`; x.beginPath(); x.arc(px, py, 1.5 + rnd() * 1.5, 0, 7); x.fill();
    }
  },
  cam: (t) => ({ x: W / 2 + 15 * sstep(0, 4, t), y: H / 2, fit: 1.02 + 0.03 * sstep(0, 4, t) }),
};
export async function renderFrame(ctx, t, w, h) { shot.bg = await bg(); return renderPaint(ctx, t, w, h, shot); }
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
