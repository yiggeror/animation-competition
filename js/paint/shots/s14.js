// S14 · 第 5 场：搭台。屋子全景（底图 bg_01，马灯的夜光），北墙前那根晾衣铁丝上搭起一条白床单：
// 0.5 床单抖开搭上铁丝（铁丝一晃，1.0）；2.5、3.2、3.9 三只衣夹夹上；5.0 马灯挂到床单后面——床单一下子亮了，成了戏台；
// 6.5～7.8 小满拖板凳过来坐下，8.5 抱起胳膊（画外，只听见声音）。
// 临时版：奶奶搭床单、小满拖凳子的图（anim_14 两张）还没到，先只拍床单亮起来；时间和 audio/build.py 的 S14 音效对齐。
import { renderPaint } from '../paintshot.js';
export const DURATION = 10;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const BW = 1672, BH = 941;
const WIRE = [[328, 268], [905, 250]];                    // 铁丝两头（左墙上的钉子、木柱）
const wireY = (x) => { const u = (x - WIRE[0][0]) / (WIRE[1][0] - WIRE[0][0]); return WIRE[0][1] + (WIRE[1][1] - WIRE[0][1]) * u + 14 * Math.sin(Math.PI * u); };
const SH = { x0: 392, x1: 842, bottom: 505 };              // 床单左右边、下沿
const T_HANG = 0.5, T_LAMP = 5.0, PINS = [[2.5, 0.12], [3.2, 0.5], [3.9, 0.88]];
const LAMP = [600, 330];                                   // 挂在床单后面的马灯（透过床单看到的亮点）

function sheet(t) {
  const c = new OffscreenCanvas(BW, BH), x = c.getContext('2d');
  const drop = sstep(T_HANG, T_HANG + 0.55, t), sway = Math.exp(-Math.max(0, t - T_HANG - 0.4) * 1.6) * Math.sin((t - T_HANG) * 7) * (t > T_HANG ? 1 : 0);
  if (drop <= 0) return c;
  const wob = (t > 1.0 ? Math.exp(-(t - 1.0) * 3) * Math.sin((t - 1.0) * 30) * 3 : 0);
  // 铁丝晃一下（在底图的铁丝上补画一根）
  const top = (px) => wireY(px) + wob * Math.sin(Math.PI * (px - WIRE[0][0]) / (WIRE[1][0] - WIRE[0][0]));
  // 床单：上沿搭在铁丝上，下沿往下坠（抖开时从短到长，晃几下停住）
  const bot = (px) => { const h = SH.bottom - top(px); return top(px) + h * drop + 14 * sway * Math.sin((px - SH.x0) * 0.02); };
  const path = new Path2D(); path.moveTo(SH.x0, top(SH.x0));
  for (let px = SH.x0; px <= SH.x1; px += 10) path.lineTo(px, top(px));
  for (let px = SH.x1; px >= SH.x0; px -= 10) path.lineTo(px, bot(px));
  path.closePath();
  x.fillStyle = '#ecebe2'; x.fill(path);
  x.save(); x.clip(path);
  // 褶子：竖着的一道道明暗；搭在铁丝上的那一折是双层的（略暗）
  for (let px = SH.x0; px < SH.x1; px += 38) { const g = x.createLinearGradient(px, 0, px + 38, 0); g.addColorStop(0, 'rgba(120,110,95,0.10)'); g.addColorStop(0.5, 'rgba(255,255,250,0.06)'); g.addColorStop(1, 'rgba(120,110,95,0.10)'); x.fillStyle = g; x.fillRect(px, 0, 38, BH); }
  x.fillStyle = 'rgba(110,100,85,0.14)'; x.beginPath(); for (let px = SH.x0; px <= SH.x1; px += 10) x.lineTo(px, top(px) + 26); x.lineTo(SH.x1, 0); x.lineTo(SH.x0, 0); x.fill();
  // 褪色的印花边（下沿一圈小花）
  x.fillStyle = 'rgba(200,120,110,0.35)'; for (let px = SH.x0 + 14; px < SH.x1; px += 28) { const by = bot(px) - 14; x.beginPath(); x.arc(px, by, 4, 0, 7); x.fill(); }
  x.restore();
  x.strokeStyle = 'rgba(62,42,30,0.75)'; x.lineWidth = 2.5; x.stroke(path);
  // 衣夹：木头夹子夹在铁丝和床单上沿
  for (const [tp, u] of PINS) {
    if (t < tp) continue;
    const px = SH.x0 + (SH.x1 - SH.x0) * u, py = top(px), k = sstep(tp, tp + 0.08, t);
    x.save(); x.translate(px, py - 4 + 6 * (1 - k)); x.fillStyle = '#c99a5c'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 2;
    x.beginPath(); x.roundRect(-4, -10, 8, 26, 2); x.fill(); x.stroke(); x.restore();
  }
  return c;
}
const lit = (t) => sstep(T_LAMP, T_LAMP + 0.6, t);
const fl = (t) => 1 + 0.05 * Math.sin(t * 9.3) + 0.03 * Math.sin(t * 17.7);
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => [{ img: sheet(t), x: 0, y: 0, sc: 1 }],
  light: (t) => {
    const L = lit(t);
    return {
      ambient: [0.022, 0.026, 0.044],
      lights: [
        { x: 520, y: 520, r: 900 * fl(t), color: [1.0, 0.62, 0.30], i: 0.75 * (1 - L), falloff: 2.0 },      // 挂上去之前：马灯搁在箱子边
        { x: LAMP[0], y: LAMP[1] + 60, r: 1300 * fl(t), color: [1.0, 0.68, 0.38], i: 0.55 * L, falloff: 1.8 }, // 挂上以后：亮床单把屋里照得暖
      ],
      exposure: 1.0, vignette: 0.5, grain: 7,
    };
  },
  glow: () => [],
  // 床单被后面的马灯透亮：在床单范围里叠一层暖光（中间亮、往边上暗）
  emit: (x, t) => {
    const L = lit(t); if (L <= 0) return;
    const m = sheet(t);
    const g = new OffscreenCanvas(BW, BH), gx = g.getContext('2d');
    const rg = gx.createRadialGradient(LAMP[0], LAMP[1], 10, LAMP[0], LAMP[1] + 40, 420);
    rg.addColorStop(0, `rgba(255,236,190,${0.95 * L})`); rg.addColorStop(0.15, `rgba(255,214,150,${0.8 * L})`); rg.addColorStop(1, `rgba(220,150,80,${0.35 * L})`);
    gx.fillStyle = rg; gx.fillRect(0, 0, BW, BH);
    gx.globalCompositeOperation = 'destination-in'; gx.drawImage(m, 0, 0);
    x.globalCompositeOperation = 'source-over'; x.globalAlpha = fl(t) * 0.97; x.drawImage(g, 0, 0); x.globalAlpha = 1;
  },
  cam: (t) => { const k = sstep(0, 10, t); return { x: 640 + 20 * k, y: 430, fit: 1.45 + 0.08 * k }; },
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
