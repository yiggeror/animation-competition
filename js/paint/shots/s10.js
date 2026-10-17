// S10 · 第 3 场：手电的光柱扫过屋子，照到奶奶，奶奶眯起眼。
// 0～3 秒：屋子全景（合作方画的 bg_01 底图，白天平光），停电的夜里压成蓝黑，只有八仙桌上的马灯一团暖光；
//   小满跪在电视柜前举着推亮的手电（S09 刚推亮），光柱从后墙扫过门、墙上的鹤画，停在坐在凳子上剥豆的奶奶身上（anim_01_grandma_beans）。
// 3～5 秒：切到奶奶脸部特写（anim_10_grandma_squint），手电的冷白光从左边打在脸上，她眯着眼往后一缩。
import { renderPaint, loadImg } from '../paintshot.js';
import { lamp as drawLamp, LX, LB } from '../../code/s08.js';
export const DURATION = 5;
const T_CUT = 3.0;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const BW = 1672, BH = 941;
// 小满跪在电视柜前（同 S09 的图 x09_flashlight，缩小放进全景），手电头在她手里；光柱从这里扫出去
const XM = { x: 127, y: 472, sc: 0.19 };
const SRC = [XM.x + 1096 * XM.sc, XM.y + 488 * XM.sc];
const GM = { x: 905, y: 772, sc: 0.235 };          // 奶奶脚底中点（底图像素）、缩放
const LAMP = { x: 1365, y: 628, s: 0.17 };        // 桌上的马灯（底图像素，底座中点）、缩放
let LAMPIMG = null;
function lampImg() {
  if (LAMPIMG) return LAMPIMG;
  const c = new OffscreenCanvas(700, 1000), x = c.getContext('2d');
  x.translate(350 - LX, 980 - LB); drawLamp(x, 0, true);
  return (LAMPIMG = c);
}
// 光柱的角度：先照后墙，扫过门和鹤画（在画上停一下），最后落在奶奶身上
function beamAng(t) {
  // 图里手电是平着朝右的，光柱只在水平上下三十度里扫：先照门左边的墙，再停在鹤画上，最后落到奶奶脸上
  const a0 = -0.55, a1 = -0.34, a2 = Math.atan2(GM.y - 230 - SRC[1], GM.x - SRC[0]);
  return a0 + (a1 - a0) * sstep(0.35, 1.3, t) + (a2 - a1) * sstep(1.75, 2.6, t);
}
const fl = (t) => 1 + 0.05 * Math.sin(t * 9.3) + 0.03 * Math.sin(t * 17.7);

const wide = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const lit = sstep(0.15, 0.25, t);
    return [
      { img: '/assets/chars/g01_beans.png', x: GM.x, y: GM.y, sc: GM.sc, ox: 304, oy: 1348, flip: false },
      { img: '/assets/chars/x09_flashlight.png', x: XM.x, y: XM.y, sc: XM.sc },
      { img: lampImg(), x: LAMP.x, y: LAMP.y, sc: LAMP.s, ox: 350, oy: 980 },
    ].map((L) => ({ ...L, alpha: 1 + 0 * lit }));
  },
  light: (t) => {
    const on = 1;                                  // 手电在上一镜（S09）已经推亮
    return {
      ambient: [0.028, 0.032, 0.05],
      lights: [{ x: LAMP.x, y: LAMP.y - 95, r: 760 * fl(t), color: [1.0, 0.62, 0.30], i: 0.95, falloff: 2.4 }],
      cone: on > 0 ? { x: SRC[0], y: SRC[1], ang: beamAng(t), spread: 0.1, len: 1900, color: [0.95, 0.96, 1.0], i: 0.95 * on, soft: 60 } : null,
      exposure: 1.0, vignette: 0.5, grain: 7,
    };
  },
  glow: (t) => [{ x: LAMP.x, y: LAMP.y - 95, r: 70 * fl(t), color: [255, 200, 120], a: 0.85, core: 0.2 }],
  cam: () => ({ x: BW / 2, y: BH / 2 + 10, fit: 1.06 }),
};

// 特写：奶奶的脸，背后是虚掉的屋子（暗）
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
    const u = t - T_CUT;
    const flinch = Math.sin(Math.PI * Math.min(1, u / 0.35)) * (u < 0.35 ? 1 : 0);
    const away = sstep(0.1, 0.7, u);
    return [{ img: '/assets/chars/g10_squint.png', x: 540 + 22 * away + 8 * flinch, y: 60 + 6 * flinch, sc: 0.72, rot: 0.02 * away }];
  },
  light: (t) => ({
    ambient: [0.03, 0.03, 0.045],
    lights: [{ x: 1950, y: 820, r: 1300, color: [1.0, 0.62, 0.30], i: 0.45 * fl(t) }, { x: 700, y: 400, r: 1100, color: [0.95, 0.96, 1.0], i: 1.25, falloff: 1.4 }],
    exposure: 1.0, vignette: 0.45, grain: 6,
  }),
  glow: () => [],
  cam: () => ({ x: 960, y: 540, fit: 1 }),
};

export async function renderFrame(ctx, t, W, H) {
  if (t < T_CUT) {
    await renderPaint(ctx, t, W, H, wide);
    // 看得见的光柱（空气里的灰被照亮）：在画面坐标里补一道半透明的锥
    {
      const k = (W / BW) * 1.06, on = 1;   // 和 wide.cam 的 fit 一致
      const S = [(SRC[0] - BW / 2) * k + W / 2, (SRC[1] - BH / 2 - 10) * k + H / 2], a = beamAng(t), L = 1500 * k;
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.filter = `blur(${Math.round(8 * k)}px)`;
      const g = ctx.createRadialGradient(S[0], S[1], 0, S[0], S[1], L);
      g.addColorStop(0, `rgba(235,242,255,${0.16 * on})`); g.addColorStop(1, 'rgba(255,248,230,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(S[0], S[1]); ctx.arc(S[0], S[1], L, a - 0.09, a + 0.09); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  } else {
    close.bg = await closeBg();
    await renderPaint(ctx, t, W, H, close);
  }
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
