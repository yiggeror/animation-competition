// S32 · 第 13 场：屋外，夜。镜头从这扇窗慢慢往后退：村子里家家户户亮着日光灯的白光，电线杆和电线横过夜空（"来电"了）；
// 只有这一扇窗是暖黄的——窗里挂着床单，床单上鹤和乌龟的影子还在动。退到全景（片名已移到片头；音乐的"呛"在 S32 结尾）。
// 代码画的版本（等合作方的 bg_34_village_night 到了再换成底图 + 程序打光）。世界坐标 3840×2160，镜头从窗口拉到全景。
import { makeCrane } from '../lamp/crane.js';
import { makeTurtle, turtlePose } from '../lamp/turtle.js';
import { drawPuppet, pointOn } from '../puppet.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, cranePoseOf, mixNeck } from '../lamp/choreo.js';
export const DURATION = 15;
export const SHOW_TITLE = false;
const WW = 3840, WH = 2160, LINE = '#120d0a';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const WIN = { x: 1920, y: 1330, w: 300, h: 230 };       // 那扇窗（世界坐标中心、宽高）
let SKY = null, CRANE = null, TURTLE = null;

// 一次连续的安静对戏，不取模、不让两只偶同步往复。
// 每次行进都以零速度起停；腿的相位只在行进中累积，停下便落脚。
export function windowPerformance(t) {
  const ramp = (a, b) => sstep(a, b, t);
  const pulse = (a, b, c, d) => ramp(a, b) - ramp(c, d);
  const first = ramp(0.45, 1.85), second = ramp(6.10, 7.65);
  const velocity = (a, b) => {
    const u = Math.max(0, Math.min(1, (t - a) / (b - a)));
    return 4 * u * (1 - u);
  };
  return {
    travel: 23 * first + 17 * second,
    stepTime: 1.25 * first + 1.25 * second,
    walk: 0.95 * Math.max(velocity(0.45, 1.85), velocity(6.10, 7.65)),
    // 龟先走近停住，鹤看它；龟伸颈回答后，鹤才抬起。
    bow: 0.06 + 0.83 * pulse(1.65, 2.65, 3.65, 4.65)
      + 0.69 * pulse(7.55, 8.70, 9.50, 10.65)
      + 0.40 * pulse(12.05, 13.25, 14.00, 15.40),
    neckOut: 0.38 + 0.45 * pulse(2.75, 3.35, 4.25, 5.10)
      + 0.38 * pulse(8.70, 9.30, 10.25, 11.15)
      + 0.30 * ramp(13.35, 14.50),
    headTilt: 0.14 * pulse(2.90, 3.45, 4.10, 4.80)
      + 0.12 * pulse(8.85, 9.40, 10.20, 10.90),
  };
}

function rnd(seed) { let s = seed; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }

// 远景、中景的房子和树、电线杆：画一次缓存（窗户另画，好让它们有的亮有的暗）
function village() {
  if (SKY) return SKY;
  const c = new OffscreenCanvas(WW, WH), x = c.getContext('2d');
  // 天：深蓝到地平线略亮；星星；月亮
  const g = x.createLinearGradient(0, 0, 0, WH * 0.62);
  g.addColorStop(0, '#060a1a'); g.addColorStop(0.7, '#14213e'); g.addColorStop(1, '#25365a');
  x.fillStyle = g; x.fillRect(0, 0, WW, WH);
  const r = rnd(5);
  for (let i = 0; i < 260; i++) { x.fillStyle = `rgba(230,235,255,${0.25 + 0.6 * r()})`; x.beginPath(); x.arc(r() * WW, r() * WH * 0.5, 1 + 2 * r(), 0, 7); x.fill(); }
  x.fillStyle = '#f2ecd2'; x.beginPath(); x.arc(3120, 330, 70, 0, 7); x.fill();
  const mg = x.createRadialGradient(3120, 330, 60, 3120, 330, 380); mg.addColorStop(0, 'rgba(220,225,255,0.25)'); mg.addColorStop(1, 'rgba(220,225,255,0)'); x.fillStyle = mg; x.fillRect(2700, 0, 900, 800);
  // 远山
  x.fillStyle = '#1a2440'; x.beginPath(); x.moveTo(0, 1180);
  for (let xx = 0; xx <= WW; xx += 40) x.lineTo(xx, 1120 - 90 * Math.sin(xx * 0.0016) - 50 * Math.sin(xx * 0.005 + 1));
  x.lineTo(WW, WH); x.lineTo(0, WH); x.fill();
  return (SKY = c);
}
// 一排房子：返回窗户位置（之后按亮/暗画）
function houses(x, seed, y0, scale, n, color, roofColor, skipCenter) {
  const r = rnd(seed), wins = [];
  let xx = -100;
  for (let i = 0; i < n && xx < WW + 100; i++) {
    const w = (260 + 180 * r()) * scale, h = (190 + 90 * r()) * scale, rh = (90 + 50 * r()) * scale;
    if (skipCenter && Math.abs(xx + w / 2 - WW / 2) < 520) { xx += w + 40 * scale; continue; }
    x.fillStyle = color; x.fillRect(xx, y0 - h, w, h + 400);
    x.fillStyle = roofColor; x.beginPath(); x.moveTo(xx - 20 * scale, y0 - h); x.lineTo(xx + w * 0.5, y0 - h - rh); x.lineTo(xx + w + 20 * scale, y0 - h); x.closePath(); x.fill();
    const nw = 1 + Math.floor(r() * 2.5);
    for (let k = 0; k < nw; k++) wins.push({ x: xx + w * (0.22 + 0.56 * (nw === 1 ? 0.5 : k / (nw - 1))) - 28 * scale, y: y0 - h * 0.62, w: 56 * scale, h: 46 * scale, on: r() < 0.85, f: r() * 6 });
    xx += w + (30 + 80 * r()) * scale;
    if (r() < 0.35) { // 树（竹子 / 樟树）的剪影
      x.fillStyle = '#0b1120'; const tx = xx - 10 * scale, th = (240 + 160 * r()) * scale;
      x.beginPath(); x.ellipse(tx, y0 - th * 0.7, 90 * scale, th * 0.45, 0, 0, 7); x.fill(); x.fillRect(tx - 8 * scale, y0 - th * 0.4, 16 * scale, th * 0.4);
    }
  }
  return wins;
}
function drawWins(x, wins, t, warm = false) {
  for (const w of wins) {
    if (!w.on) { x.fillStyle = '#0d1424'; x.fillRect(w.x, w.y, w.w, w.h); continue; }
    const c = warm ? [255, 196, 110] : [222, 236, 255];
    x.fillStyle = `rgb(${c.join(',')})`; x.fillRect(w.x, w.y, w.w, w.h);
    x.strokeStyle = '#0d1424'; x.lineWidth = Math.max(2, w.w * 0.06); x.beginPath(); x.moveTo(w.x + w.w / 2, w.y); x.lineTo(w.x + w.w / 2, w.y + w.h); x.stroke();
    const g = x.createRadialGradient(w.x + w.w / 2, w.y + w.h / 2, 2, w.x + w.w / 2, w.y + w.h / 2, w.w * 1.6);
    g.addColorStop(0, `rgba(${c.join(',')},0.28)`); g.addColorStop(1, `rgba(${c.join(',')},0)`);
    x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = g; x.fillRect(w.x - w.w * 1.6, w.y - w.w * 1.6, w.w * 4.2, w.w * 4.2); x.restore();
  }
}
let FAR = null, MID = null;
function layers() {
  if (FAR) return;
  FAR = { c: new OffscreenCanvas(WW, WH) }; MID = { c: new OffscreenCanvas(WW, WH) };
  FAR.wins = houses(FAR.c.getContext('2d'), 11, 1240, 0.45, 40, '#1c2742', '#141c33', false);
  MID.wins = houses(MID.c.getContext('2d'), 23, 1440, 0.8, 24, '#222c45', '#161d30', true);
}

// 这家人的房子（正中）：白墙、瓦顶、木门、一扇暖黄的窗，窗里是床单和皮影的影子
function mainHouse(x, t) {
  const cx = WW / 2, y0 = 1620;
  x.fillStyle = '#262c3e'; x.fillRect(cx - 520, y0 - 470, 1040, 900);                 // 墙（夜里的白墙，偏蓝灰）
  x.fillStyle = '#1b2033'; x.beginPath(); x.moveTo(cx - 600, y0 - 470); x.lineTo(cx, y0 - 760); x.lineTo(cx + 600, y0 - 470); x.closePath(); x.fill();   // 瓦顶
  x.strokeStyle = '#11162a'; x.lineWidth = 6; for (let k = 1; k < 9; k++) { x.beginPath(); x.moveTo(cx - 600 + k * 66, y0 - 470 - k * 32); x.lineTo(cx + 600 - k * 66, y0 - 470 - k * 32); x.stroke(); }
  x.fillStyle = '#26201c'; x.fillRect(cx + 200, y0 - 300, 170, 300);                  // 木门
  // 窗：暖黄的床单，鹤和乌龟的影子
  const { x: wx, y: wy, w, h } = WIN;
  const win = new OffscreenCanvas(w * 2, h * 2), wc = win.getContext('2d');
  const g = wc.createRadialGradient(w * 1.0, h * 0.7, 20, w, h, w * 1.3); g.addColorStop(0, '#ffd99a'); g.addColorStop(1, '#e09a4c');
  wc.fillStyle = g; wc.fillRect(0, 0, w * 2, h * 2);
  CRANE ||= makeCrane(1.35, 'plain'); TURTLE ||= makeTurtle();
  // 皮影在床单上的影子：先画到单独的画布，再整块涂成暗色（只要轮廓）
  const sh = new OffscreenCanvas(w * 2, h * 2), sx = sh.getContext('2d');
  const a = windowPerformance(t);
  const neck = mixNeck(NECK_UP, mixNeck(NECK_LOW, NECK_DOWN, 0.34), a.bow);
  const cp = cranePoseOf(neck, { mode: 'stand', swing: a.bow * 0.08 }, 0.04, 1);
  const tp = turtlePose(a.stepTime, {
    facing: -1, walk: a.walk, speed: 0.8, neckOut: a.neckOut,
    headTilt: a.headTilt,
  });
  // 固定投影尺度与朝向。头颈有转动，不用镜像翻转冒充转身。
  // 签子端点从同一次正向运动学求解得到，不能漂在皮影旁边。
  const drawHeld = (pup, pose, px, py, scale, rods) => {
    sx.save(); sx.translate(px, py); sx.scale(scale, -scale);
    const sol = drawPuppet(sx, pup, pose, 'r');
    sx.restore();
    sx.save(); sx.strokeStyle = '#462612'; sx.lineWidth = 2.8; sx.lineCap = 'round';
    for (const rod of rods) {
      const pt = pointOn(pup, sol, rod.part, rod.at);
      const ax = px + scale * pose.facing * pt[0], ay = py - scale * pt[1];
      sx.beginPath(); sx.moveTo(ax, ay);
      sx.lineTo(rod.handX, h * 2 + 24); sx.stroke();
    }
    sx.restore();
  };
  drawHeld(CRANE, cp, w * 0.72, h * 1.30, 0.62, [
    { part: 'body', at: [24, 12], handX: w * 0.62 },
    { part: 'head', at: [0, 0], handX: w * 1.10 + 10 * a.bow },
  ]);
  drawHeld(TURTLE, tp, w * 1.53 - a.travel, h * 1.70, 0.6, [
    { part: 'shell', at: [0, 35], handX: w * 1.55 - a.travel },
    { part: 'head', at: [20, 0], handX: w * 1.28 - a.travel * 0.7 },
  ]);
  sx.globalCompositeOperation = 'source-in'; sx.fillStyle = 'rgba(70,38,18,0.82)'; sx.fillRect(0, 0, w * 2, h * 2);
  wc.filter = 'blur(2px)'; wc.drawImage(sh, 0, 0); wc.filter = 'none';
  x.drawImage(win, wx - w / 2, wy - h / 2, w, h);
  // 窗棂（木格子）
  x.strokeStyle = '#2a1d14'; x.lineWidth = 12; x.strokeRect(wx - w / 2, wy - h / 2, w, h);
  x.lineWidth = 7; for (const k of [1, 2]) { x.beginPath(); x.moveTo(wx - w / 2 + k * w / 3, wy - h / 2); x.lineTo(wx - w / 2 + k * w / 3, wy + h / 2); x.stroke(); }
  x.beginPath(); x.moveTo(wx - w / 2, wy); x.lineTo(wx + w / 2, wy); x.stroke();
  // 暖光溢到窗外的墙上、地上
  x.save(); x.globalCompositeOperation = 'lighter';
  const gl = x.createRadialGradient(wx, wy, w * 0.4, wx, wy + 40, w * 2.6); gl.addColorStop(0, 'rgba(255,190,110,0.22)'); gl.addColorStop(1, 'rgba(255,170,90,0)');
  x.fillStyle = gl; x.fillRect(wx - w * 3, wy - h * 3, w * 6, h * 6.5); x.restore();
  // 屋前的地、一棵树的剪影、电线杆
  x.fillStyle = '#0c1220'; x.fillRect(0, y0, WW, WH - y0);
}
function poles(x) {
  x.strokeStyle = '#05080f'; x.lineCap = 'round';
  const P = [[520, 1650, 980], [1500, 1660, 1010], [2650, 1650, 990], [3560, 1660, 1000]];
  for (const [px, py, top] of P) { x.lineWidth = 22; x.beginPath(); x.moveTo(px, py); x.lineTo(px, top); x.stroke(); x.lineWidth = 12; x.beginPath(); x.moveTo(px - 90, top + 40); x.lineTo(px + 90, top + 40); x.stroke(); }
  x.lineWidth = 4;
  for (const dy of [40, 34, 46]) for (let i = 0; i < P.length - 1; i++) {
    const a = P[i], b = P[i + 1], o = dy - 40;
    x.beginPath(); x.moveTo(a[0] - 80 + o * 3, a[2] + dy); x.quadraticCurveTo((a[0] + b[0]) / 2, a[2] + dy + 120, b[0] - 80 + o * 3, b[2] + dy); x.stroke();
  }
  // 电线连到这家的屋檐
  x.beginPath(); x.moveTo(1500, 1050); x.quadraticCurveTo(1700, 1000, 1920 + 380, 900); x.stroke();
}

export async function renderFrame(ctx, t, W, H) {
  layers();
  const world = new OffscreenCanvas(WW, WH), x = world.getContext('2d');
  x.drawImage(village(), 0, 0);
  x.drawImage(FAR.c, 0, 0); drawWins(x, FAR.wins, t);
  x.drawImage(MID.c, 0, 0); drawWins(x, MID.wins, t);
  poles(x);
  mainHouse(x, t);
  // 萤火虫几点
  const r = rnd(9);
  x.save(); x.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 18; i++) { const fx = 1300 + r() * 1300 + 40 * Math.sin(t * 0.7 + i), fy = 1550 + r() * 300 + 25 * Math.sin(t * 0.9 + i * 2), a = 0.5 + 0.5 * Math.sin(t * 2 + i * 1.7);
    const g = x.createRadialGradient(fx, fy, 0, fx, fy, 16); g.addColorStop(0, `rgba(210,255,150,${0.8 * a})`); g.addColorStop(1, 'rgba(210,255,150,0)'); x.fillStyle = g; x.fillRect(fx - 16, fy - 16, 32, 32); }
  x.restore();
  // 镜头：从窗口慢慢往后退到全景
  const k = sstep(0, 12.5, t), zoom = 2.6 * Math.pow(1 / 2.6, k);
  const cx = WIN.x + (WW / 2 - WIN.x) * k, cy = WIN.y + (WH / 2 - 40 - WIN.y) * k;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const s = (W / 1920) * (1920 / WW) * 2 * zoom / 2 * 1;   // 全景时 3840 宽铺满画面
  const sc = (W / WW) * zoom;
  ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-cx, -cy);
  ctx.drawImage(world, 0, 0);
  ctx.restore();
  // 片名（10-21 起片名移到片头 js/code/title.js；这里留着开关，成片不显示）
  const ta = SHOW_TITLE ? sstep(11.6, 13.0, t) : 0;
  if (ta > 0) {
    ctx.save(); ctx.globalAlpha = ta; ctx.fillStyle = '#f6e7c8'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = `${Math.round(H * 0.16)}px "Ma Shan Zheng"`; ctx.shadowColor = 'rgba(255,200,120,0.6)'; ctx.shadowBlur = H * 0.03;
    ctx.fillText('来电', W / 2, H * 0.26); ctx.restore();
  }
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }

