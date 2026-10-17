// S08 · 第 2 场：奶奶点马灯。人物是合作方画的 anim_08_grandma_light_lamp（奶奶坐在八仙桌边、朝右前倾，右手捏着火柴举在前面，
// 左手掌心朝上——这里让它托着火柴盒），抠图 assets/chars/g08_light_lamp.png；马灯、桌子、火柴盒、火苗和烟由程序画。
// 三段（时间和 audio/build.py 的 S08 音效对齐：0.2 划火柴、1.8 灯芯着、2.2 甩灭、3.4 灯罩落下"叮"）：
//   A 0～1.25  中景，屋里黑着：0.2"嚓"地火柴着了，火光照亮奶奶的脸和两只手、桌上还没点的马灯（灯罩抬着）
//   B 1.25～3.9 灯头特写：奶奶的手（同一张图里的右手和小臂，放大）把火柴伸进抬起的灯罩下面碰到灯芯，灯芯着了；
//              收回来一甩，火柴灭了冒一缕烟，手出画；灯罩落下（按拨杆的手在画外右边）——暖光铺开
//   C 3.9～6   回中景，马灯亮着：奶奶还举着灭了的火柴，一缕烟往上飘
// 中景里人和灯的比例：奶奶的头约 23 厘米 ≈ 图上 320 像素（14 像素/厘米）；马灯到顶盖约 30 厘米 = 设计坐标 650 → 缩放 0.645。
// 火柴在图上的位置比灯芯高（合作方审查里算过：灯底放在托掌上、灯芯对火柴会让灯大一倍），所以真正碰灯芯的一下放在特写 B 里拍，
// 中景 C 里是点完以后把火柴拿开举着。
import { renderPaint, loadImg } from '../paintshot.js';
import { lamp as drawLamp, flameShape, LX, LB } from '../../code/s08.js';
export const DURATION = 6;
const T_B = 1.25, T_C = 3.9;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const IW = 1536, IH = 1024;
const MATCH = [1216, 404];                    // 图上火柴头
const LS = 0.645;                             // 中景里马灯的缩放（设计坐标 → 图像素）
const LAMP_AT = [1392, 786];                  // 中景里马灯底的中点（桌面上）
const TABLE = { x0: 1010, top: 762, edge: 800 };
const wickM = [LAMP_AT[0], LAMP_AT[1] - 228 * LS];
const fl = (t) => 1 + 0.06 * Math.sin(t * 9.3) + 0.04 * Math.sin(t * 17.7) + 0.03 * Math.sin(t * 31);
// 灯芯火苗大小：1.8 点着，罩子落下以后长大稳住
const wickSize = (t) => (t < 1.78 ? 0 : 0.5 * sstep(1.78, 2.05, t) + 0.5 * sstep(3.35, 4.0, t));
// 火柴火苗：0.2 划着（先蹿一下），2.2 甩灭
const matchSize = (t) => (t < 0.2 || t > 2.2 ? 0 : t < 0.36 ? 1.7 - (t - 0.2) * 5 : 0.8 + 0.08 * Math.sin(t * 19));
const lift = (t) => 1 - sstep(3.15, 3.4, t);

// 马灯画成一张图（700×1000，灯底中点在 (350, 980)）；按灯罩高低缓存
const LAMPS = {};
function lampImg(lf) {
  const k = Math.round(lf * 20) / 20;
  if (LAMPS[k]) return LAMPS[k];
  const c = new OffscreenCanvas(700, 1000), x = c.getContext('2d');
  x.translate(350 - LX, 980 - LB); drawLamp(x, k, true);
  return (LAMPS[k] = c);
}
// 火柴盒（侧面看，躺在左手心里）和图上火柴头的遮盖（没划着时是红褐色的药头，灭了以后是黑的）
function matchbox(x) {
  x.save(); x.translate(1160, 683); x.rotate(-0.04);
  x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 3;
  x.beginPath(); x.roundRect(-38, -12, 76, 24, 3); x.fill(); x.stroke();
  x.fillStyle = '#9b3a26'; x.fillRect(-36, -3, 72, 7);            // 侧面的擦皮
  x.fillStyle = 'rgba(255,240,200,0.35)'; x.fillRect(-34, -10, 68, 3);
  x.restore();
}
function matchHead(x, burnt) { x.fillStyle = burnt ? '#241712' : '#8a2f1e'; x.beginPath(); x.ellipse(MATCH[0] - 1, MATCH[1], 8, 6, -0.15, 0, 7); x.fill(); }
// 一缕烟：从 (x0, y0) 往上飘、往右偏，age 秒以后散掉
function smoke(x, p, age, t) {
  if (age < 0 || age > 2.5) return;
  x.save(); x.lineCap = 'round';
  for (let k = 0; k < 3; k++) {
    const a = Math.max(0, 0.22 * (1 - age / 2.5) - k * 0.05);
    x.strokeStyle = `rgba(200,200,205,${a})`; x.lineWidth = 3 + k * 4 + age * 6;
    x.beginPath(); x.moveTo(p[0], p[1]);
    const h = 60 + age * 140;
    for (let s = 1; s <= 8; s++) { const u = s / 8; x.lineTo(p[0] + 18 * Math.sin(u * 5 + t * 1.7 + k) * u + 30 * u * age, p[1] - h * u); }
    x.stroke();
  }
  x.restore();
}

// ---------------------------------------------------------------- 中景（A、C）
let MID_BG = null;
async function midBg() {
  if (MID_BG) return MID_BG;
  const room = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(IW, IH), x = c.getContext('2d');
  x.filter = 'blur(20px)'; x.drawImage(room, 760, 220, 700, 420, -60, -40, IW + 120, IH * 0.9);   // 屋子后墙一带，虚掉
  x.filter = 'none';
  // 八仙桌：桌面（略俯视看到一条）+ 桌边
  x.fillStyle = '#8a5a34'; x.fillRect(TABLE.x0, TABLE.top, IW - TABLE.x0, TABLE.edge - TABLE.top);
  x.fillStyle = '#6a4226'; x.fillRect(TABLE.x0, TABLE.edge, IW - TABLE.x0, IH - TABLE.edge);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 4;
  x.beginPath(); x.moveTo(TABLE.x0, TABLE.top); x.lineTo(IW, TABLE.top); x.moveTo(TABLE.x0, TABLE.edge); x.lineTo(IW, TABLE.edge); x.moveTo(TABLE.x0, TABLE.top); x.lineTo(TABLE.x0, IH); x.stroke();
  x.strokeStyle = 'rgba(60,35,18,0.35)'; x.lineWidth = 2; for (let k = 0; k < 5; k++) { const y = TABLE.edge + 30 + k * 40; x.beginPath(); x.moveTo(TABLE.x0 + 10, y); x.lineTo(IW, y + 4); x.stroke(); }
  return (MID_BG = c);
}
const mid = {
  size: [IW, IH],
  layers: async (t) => {
    const lit = t >= T_C;
    const g = { img: '/assets/chars/g08_light_lamp.png', x: 0, y: 0, sc: 1 };
    const over = new OffscreenCanvas(IW, IH), ox = over.getContext('2d');
    matchbox(ox); matchHead(ox, lit);
    return [
      { img: lampImg(lift(t)), x: LAMP_AT[0], y: LAMP_AT[1], sc: LS, ox: 350, oy: 980 },
      g, { img: over, x: 0, y: 0, sc: 1 },
    ];
  },
  light: (t) => {
    const lights = [];
    const m = matchSize(t);
    if (t < T_C && m > 0) lights.push({ x: MATCH[0], y: MATCH[1] - 10, r: 720 * (0.8 + 0.25 * m), color: [1.0, 0.64, 0.32], i: 0.75 + 0.35 * m * fl(t), falloff: 1.9 });
    if (t >= T_C) lights.push({ x: wickM[0], y: wickM[1] - 30, r: 1500 * fl(t), color: [1.0, 0.62, 0.30], i: 1.15, falloff: 2.0 });
    return { ambient: t < T_C ? [0.018, 0.022, 0.036] : [0.03, 0.03, 0.045], lights, exposure: 1.0, vignette: 0.5, grain: 7 };
  },
  glow: (t) => {
    const out = [];
    const m = matchSize(t);
    if (t < T_C && m > 0) out.push({ x: MATCH[0] + 4, y: MATCH[1] - 8, r: 60 * (0.7 + 0.4 * m), color: [255, 190, 110], a: 0.7, core: 0.2 });
    if (t >= T_C) out.push({ x: wickM[0], y: wickM[1] - 25, r: 120 * fl(t), color: [255, 200, 120], a: 0.8, core: 0.2 }, { x: wickM[0], y: wickM[1] - 60, r: 210, color: [255, 210, 150], a: 0.18, core: 0.4 });
    return out;
  },
  emit: (x, t) => {
    const m = matchSize(t);
    if (t < T_C && m > 0) flameShape(x, [MATCH[0] + 6, MATCH[1] + 2], 0.42 * m, t);
    if (t >= T_C) { flameShape(x, [wickM[0], wickM[1] - 4], 0.62 * wickSize(t) * fl(t), t, true); smoke(x, [MATCH[0], MATCH[1] - 6], t - 2.2, t); }
  },
  cam: (t) => (t < T_C ? { x: IW / 2, y: 455, fit: 1.0 } : { x: IW / 2 + 30 * sstep(T_C, DURATION, t), y: 455 - 10 * sstep(T_C, DURATION, t), fit: 1.0 + 0.05 * sstep(T_C, DURATION, t) }),
};

// ---------------------------------------------------------------- 灯头特写（B）
// 画面坐标 1920×1080：灯芯在 WICK_B，马灯放大 SB 倍（设计坐标 → 画面像素）；奶奶的右手按同样的比例放大（SB / LS 倍）
const SB = 2.2, WICK_B = [1430, 600], HS = SB / LS;
const ARM = [[760, 560], [1030, 365], [1245, 365], [1245, 445], [1120, 515], [1000, 522], [900, 582], [810, 642], [760, 665]];   // 图上右小臂 + 右手 + 火柴
// 火柴头相对灯芯的位置（画面像素）：从左上方伸进来、碰到灯芯，收回来甩，出画
function matchB(t) {
  const touch = [-20, -14], near = [-330, -110], back = [-360, -150], gone = [-1500, -260];
  const kIn = sstep(1.25, 1.75, t), kBack = sstep(1.98, 2.3, t), kOut = sstep(2.55, 3.0, t);
  let p = [near[0] + (touch[0] - near[0]) * kIn, near[1] + (touch[1] - near[1]) * kIn];
  p = [p[0] + (back[0] - p[0]) * kBack, p[1] + (back[1] - p[1]) * kBack];
  p = [p[0] + (gone[0] - p[0]) * kOut, p[1] + (gone[1] - p[1]) * kOut];
  const shake = t > 2.05 && t < 2.4 ? Math.sin((t - 2.05) * 55) * (1 - (t - 2.05) / 0.35) : 0;
  return { head: [WICK_B[0] + p[0], WICK_B[1] + p[1] + 10 * shake], rot: 0.12 * shake + 0.03 * Math.sin(t * 3) * (1 - kOut) };
}
let CLOSE_BG = null;
async function closeBg() {
  if (CLOSE_BG) return CLOSE_BG;
  const room = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(1920, 1080), x = c.getContext('2d');
  x.filter = 'blur(26px)'; x.drawImage(room, 1000, 300, 420, 236, -80, -60, 2080, 1200); x.filter = 'none';
  x.fillStyle = '#8a5a34'; x.fillRect(0, 1010, 1920, 70);                       // 桌面（灯底下面一条）
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 4; x.beginPath(); x.moveTo(0, 1010); x.lineTo(1920, 1010); x.stroke();
  return (CLOSE_BG = c);
}
const close = {
  size: [1920, 1080],
  layers: async (t) => {
    const M = matchB(t);
    const L = [{ img: lampImg(lift(t)), x: WICK_B[0], y: WICK_B[1] + 228 * SB, sc: SB, ox: 350, oy: 980 }];
    if (t < 3.05) {
      const over = new OffscreenCanvas(IW, IH), ox = over.getContext('2d'); matchHead(ox, t > 2.2);
      const arm = { img: '/assets/chars/g08_light_lamp.png', x: M.head[0], y: M.head[1], sc: HS, ox: MATCH[0], oy: MATCH[1], rot: M.rot, clip: ARM.map(([px, py]) => [px - MATCH[0], py - MATCH[1]]) };   // paintshot 的 clip 在以 (ox, oy) 为原点的坐标里
      L.push(arm, { ...arm, img: over });
    }
    return L;
  },
  light: (t) => {
    const M = matchB(t), m = matchSize(t), w = wickSize(t), lights = [];
    if (m > 0) lights.push({ x: M.head[0], y: M.head[1] - 20, r: 900, color: [1.0, 0.64, 0.32], i: 0.6 + 0.3 * m * fl(t), falloff: 1.8 });
    if (w > 0) lights.push({ x: WICK_B[0], y: WICK_B[1] - 60, r: 1500 + 900 * w, color: [1.0, 0.62, 0.30], i: 0.5 + 0.9 * w * fl(t), falloff: 1.8 });
    return { ambient: [0.02, 0.022, 0.035], lights, exposure: 1.0, vignette: 0.5, grain: 7 };
  },
  glow: (t) => {
    const w = wickSize(t), out = [];
    if (w > 0) out.push({ x: WICK_B[0], y: WICK_B[1] - 60 * w, r: 260 * w * fl(t), color: [255, 200, 120], a: 0.7, core: 0.2 });
    return out;
  },
  emit: (x, t) => {
    const M = matchB(t), m = matchSize(t), w = wickSize(t);
    if (m > 0) { x.save(); x.translate(M.head[0], M.head[1]); x.rotate(M.rot); flameShape(x, [8, 4], 1.3 * m, t); x.restore(); }
    if (w > 0) flameShape(x, [WICK_B[0], WICK_B[1] - 6], 2.4 * w * fl(t), t, true);
    if (t > 2.2) smoke(x, [M.head[0], M.head[1] - 8], t - 2.2, t);
  },
  cam: () => ({ x: 960, y: 540, fit: 1 }),
};

export async function renderFrame(ctx, t, W, H) {
  if (t < T_B || t >= T_C) { mid.bg = await midBg(); return renderPaint(ctx, t, W, H, mid); }
  close.bg = await closeBg(); return renderPaint(ctx, t, W, H, close);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
