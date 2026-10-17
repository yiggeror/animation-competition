// S06 · 第 2 场：墙脚插座特写（月光），严格侧面机位。小满的右手捏着充电器插头（合作方画的 anim_06_hand_plug，
// 抠图 assets/chars/h06_plug.png），拔下来、看看、插回去；没反应——再拔，捏着晃两下，再插；停住；最后往回一收、狠狠插回去
// （必须停在"插着"的状态，第 10 场手机才能自己充电）。
// 侧面看，插头的两片插脚正好前后重叠成一条；插座面板贴在右边的墙上，插脚沿墙的法线（画面水平方向）进出，
// 进去的那一截被面板挡住——面板画在手的上面。
// 时间和 audio/build.py 里 S06 的插头声对齐：声音在 t0 + 0.11 秒"咔"，t0 = 1.0 拔、1.8 插、3.0 拔、3.9 插、6.4 狠插；3.25～3.6 晃。
import { renderPaint } from '../paintshot.js';
export const DURATION = 8;
const W = 1920, H = 1080, LINE = '#3e2a1e';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// 手图（裁切后 1168×661）：插脚根（插头前脸）在 (1078, 171)，插脚伸出 88 像素；画面里放大 1.45 倍（约 8.7 像素/毫米）
const HAND = { img: '/assets/chars/h06_plug.png', root: [1078, 171], sc: 1.45, pin: 88 };
const FACE = 1460;                 // 面板前脸（画面 x），插到底时插头前脸贴在这里
const PIN_Y = 455;                 // 插脚的高度（画面 y）
const MM = 8.7;
// 面板：86 型，厚约 10 毫米；两孔在面板中心往上约 18 毫米
const PANEL = { x0: FACE, x1: FACE + 10 * MM, y0: PIN_Y + 18 * MM - 43 * MM, y1: PIN_Y + 18 * MM + 43 * MM };
const WALL = PANEL.x1;

// 手离插到底差多少（像素，负 = 往外拔）和一点转动
function handPose(t) {
  const OUT1 = -235, OUT2 = -260, WIND = -300;
  let dx = 0, rot = 0;
  // 第一次：拔（1.0～1.11），看一眼（举在外面轻轻转），插（1.66～1.91）
  dx += OUT1 * (sstep(0.98, 1.12, t) - sstep(1.66, 1.91, t));
  rot += (-0.03 + 0.025 * Math.sin((t - 1.12) * 7)) * (sstep(1.0, 1.2, t) - sstep(1.6, 1.85, t));
  // 第二次：拔（3.0～3.11），晃两下（3.25～3.6），插（3.78～4.01）
  dx += OUT2 * (sstep(2.98, 3.12, t) - sstep(3.78, 4.01, t));
  const sh = sstep(3.18, 3.25, t) * (1 - sstep(3.58, 3.66, t));
  rot += sh * 0.07 * Math.sin((t - 3.25) * 2 * Math.PI * 4.5);
  dx += sh * 9 * Math.sin((t - 3.25) * 2 * Math.PI * 4.5 + 1);
  // 第三次：慢慢往回收（5.75～6.15），停一下，猛地插（6.33～6.51）
  dx += WIND * (sstep(5.75, 6.15, t) - (t < 6.33 ? 0 : Math.min(1, ((t - 6.33) / 0.18) ** 2)));
  // 插着的时候手轻轻发抖、按着
  const holding = dx > -1;
  if (holding) rot += 0.004 * Math.sin(t * 11.3) + 0.003 * Math.sin(t * 17.9);
  // 最后一下插完，手泄了劲，往下垂一点
  rot += 0.012 * sstep(6.9, 7.6, t);
  return { dx: Math.min(0, dx), rot };
}
// 狠插那一下：墙和面板一震
const jolt = (t) => (t > 6.51 && t < 6.75 ? Math.exp(-(t - 6.51) * 18) * Math.sin((t - 6.51) * 70) : 0);

// 背景：黑下来的屋子（远处地面、八仙桌腿都虚在暗里）；右边的墙（下半截刷的绿漆，掉了几块，墙面和视线几乎平行）画在 panel() 里
let BG = null;
function bg() {
  if (BG) return BG;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const g = x.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#6c6a64'); g.addColorStop(0.62, '#5d5a54'); g.addColorStop(1, '#4b4842');
  x.fillStyle = g; x.fillRect(0, 0, W, H);
  // 远处：桌腿、凳腿的虚影，地面
  x.save(); x.filter = 'blur(28px)';
  x.fillStyle = '#3f3a33'; for (const [px, w] of [[260, 70], [520, 60], [880, 80]]) x.fillRect(px, 120, w, 900);
  x.fillStyle = '#56524b'; x.fillRect(-100, 860, 1700, 400);
  x.restore();
  return (BG = c);
}
// 墙 + 面板（侧面）：盖在手上面——插脚比面板厚（约 15 对 10 毫米），插到底时伸进墙里的插座盒，要被面板和墙一起挡住。
// 面板米黄塑料，前脸一条窄边，后面贴墙；在墙上投一点接触影
let PNL = null;
function panel() {
  if (PNL) return PNL;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  let seed = 9; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  // 墙：绿漆，竖着压扁的斑驳（墙面斜着看，水平方向的纹理被压缩）
  x.fillStyle = '#6f907a'; x.fillRect(WALL, 0, W - WALL, H);
  for (let i = 0; i < 160; i++) {
    const px = WALL + rnd() * (W - WALL), py = rnd() * H, h = 10 + rnd() * 90, w = 2 + rnd() * 10;
    x.fillStyle = rnd() < 0.5 ? 'rgba(60,80,66,0.18)' : 'rgba(200,215,200,0.12)'; x.fillRect(px, py, w, h);
  }
  for (let i = 0; i < 12; i++) {   // 掉漆露出的白灰
    const px = WALL + 20 + rnd() * (W - WALL - 40), py = rnd() * H;
    x.fillStyle = 'rgba(214,200,170,0.75)'; x.beginPath(); x.ellipse(px, py, 3 + rnd() * 6, 8 + rnd() * 20, 0, 0, 7); x.fill();
  }
  // 墙的边（离镜头最远处）一道暗线
  x.strokeStyle = 'rgba(40,50,42,0.6)'; x.lineWidth = 3; x.beginPath(); x.moveTo(WALL, 0); x.lineTo(WALL, H); x.stroke();
  const { x0, x1, y0, y1 } = PANEL, r = 22;
  x.fillStyle = 'rgba(30,36,30,0.35)'; x.fillRect(x1, y0 + 14, 18, y1 - y0 - 8);   // 贴墙的接触影
  x.fillStyle = '#e7dfc8'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(x1, y0); x.lineTo(x0 + r, y0); x.quadraticCurveTo(x0, y0, x0, y0 + r); x.lineTo(x0, y1 - r); x.quadraticCurveTo(x0, y1, x0 + r, y1); x.lineTo(x1, y1); x.closePath(); x.fill(); x.stroke();
  // 前脸的窄边（圆角过渡）和侧面上旧了发黄的印子
  x.fillStyle = 'rgba(150,130,95,0.22)'; x.fillRect(x0 + 3, y0 + r, 14, y1 - y0 - 2 * r);
  x.strokeStyle = 'rgba(62,42,30,0.35)'; x.lineWidth = 2; x.beginPath(); x.moveTo(x0 + 17, y0 + r); x.lineTo(x0 + 17, y1 - r); x.stroke();
  x.fillStyle = 'rgba(170,150,100,0.18)'; x.fillRect(x0 + 30, y1 - 160, 40, 120);
  return (PNL = c);
}

const shot = {
  size: [W, H],
  layers: async (t) => {
    const P = handPose(t), j = jolt(t);
    const s = HAND.sc, ox = HAND.root[0], oy = HAND.root[1];
    // 手图以插脚根为原点：插到底时插脚根在 (FACE, PIN_Y)
    return [
      { img: HAND.img, x: FACE + P.dx, y: PIN_Y, sc: s, ox, oy, rot: P.rot },
      { img: panel(), x: 2 * j, y: 0, sc: 1 },
    ];
  },
  light: (t) => ({
    ambient: [0.05, 0.06, 0.09],
    lights: [
      { x: 300, y: -500, r: 2400, color: [0.55, 0.66, 0.95], i: 1.15, falloff: 1.3 },        // 窗口进来的月光，从左上斜照
      { x: 1500, y: 300, r: 700, color: [0.5, 0.6, 0.85], i: 0.25, falloff: 1.6 },          // 墙上的反光
    ],
    exposure: 1.0, vignette: 0.45, grain: 6,
  }),
  glow: () => [],
  cam: (t) => { const j = jolt(t); return { x: W / 2 + 3 * j, y: H / 2 + 2 * j, fit: 1 }; },
};
export async function renderFrame(ctx, t, w, h) { shot.bg = bg(); return renderPaint(ctx, t, w, h, shot); }
export async function render(ctx, arg, w, h) { return renderFrame(ctx, +arg || 0, w, h); }
