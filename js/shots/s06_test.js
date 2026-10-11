// 动作测试：第 6 场 鹤亮相（5 秒）。机位在小满身后，正对床单。
// 床单上：奶奶把鹤从马灯跟前（离床单 0.4 米）送到床单上——影子按真实几何由大而虚变得小而清楚。
// 前景：小满坐在小板凳上，一开始抱着胳膊缩着；影子变清楚时坐直、仰头，胳膊松开，双马尾跟着一甩。
// 床单下沿的缝里能看到后台被马灯照亮的墙裙和奶奶的裤腿。
import * as X from '../chars/xiaoman.js';
import { loadPuppet } from '../puppet.js';
import { sheetImage } from '../shadowplay.js';
import { LightMap, glow, radial } from '../lib/light.js';
import { setBoil, shape, line, brush, fillPoly, rrectPts } from '../lib/draw.js';
import { key, clamp, lerp, EASE, kick, noise1, blink } from '../lib/core.js';

export const DURATION = 5.0;

// 堂屋尺寸（米，和 layout.py 一致）：床单 x 0.25–2.35、z 0.86–2.08；马灯在床单后 0.70 米、x 1.30、z 1.55
const SHEET = { x0: 0.25, x1: 2.35, z0: 0.86, z1: 2.08 };
const LAMP = { x: 1.30, z: 1.55, D: 0.70, core: 0.011, globe: 0.055, coreW: 1.0, globeW: 0.55, rgb: [255, 200, 128], I: 1.32 };
// 床单平面 → 画面
const K = 600, U0 = 560, V0 = 70;
const u = (x) => U0 + (x - SHEET.x0) * K;
const v = (z) => V0 + (SHEET.z1 - z) * K;

// ---- 鹤的动作
const NECK = {
  low: [0.55, 0.05, -0.02, -0.06, -0.08, -0.08, -0.06, -0.04, -0.02, 0.0, 0.02, 0.03, -0.62],
  high: [1.10, 0.12, 0.10, 0.07, 0.02, -0.04, -0.10, -0.14, -0.16, -0.15, -0.12, -0.08, -0.40],
  peck: [0.35, -0.05, -0.10, -0.14, -0.16, -0.16, -0.12, -0.08, -0.04, 0.0, 0.02, 0.04, -0.78],
};
function neckAt(t) {
  // 低 → 抬头亮相（冲过头再落定）→ 停一下 → 低头啄两下 → 再抬起来
  const lift = key(t, [[0, 0], [1.5, 0], [2.7, 1, EASE.outBack], [5, 1]]);
  const peck = key(t, [[0, 0], [3.5, 0], [3.8, 0.85, 'io'], [3.95, 0.6, 'io'], [4.1, 0.95, 'io'], [4.6, 0, 'io3'], [5, 0]]);
  const a = NECK.low.map((x, i) => lerp(x, NECK.high[i], lift));
  return a.map((x, i) => lerp(x, NECK.peck[i], peck));
}
const ROOT = [[0, [1.22, 1.40]], [0.8, [1.20, 1.37]], [2.1, [1.03, 1.31], 'out'], [2.5, [1.03, 1.30]], [5, [1.04, 1.31]]];
const DIST = [[0, 0.40], [0.8, 0.38], [2.1, 0.004, 'out3'], [5, 0.004]];
const BODY = [[0, -0.10], [0.8, -0.14], [2.1, 0.08, 'out'], [2.6, 0.03], [3.7, 0.0], [4.1, -0.12], [4.6, 0.04], [5, 0.05]];
// 没装签子的腿：按身体的加速度做钟摆（从 0 积分到 t，结果只取决于 t）
function legSwing(t) {
  let th = 0, w = 0, prev = null, pv = [0, 0];
  const dt = 1 / 120;
  for (let s = 0; s <= t; s += dt) {
    const r = key(s, ROOT);
    const vel = prev ? [(r[0] - prev[0]) / dt, (r[1] - prev[1]) / dt] : [0, 0];
    const acc = [(vel[0] - pv[0]) / dt, (vel[1] - pv[1]) / dt];
    prev = r; pv = vel;
    const g = 9.8, L = 0.19;
    const aa = (-(g + acc[1]) * Math.sin(th) - acc[0] * Math.cos(th)) / L - 1.6 * w;
    w += aa * dt; th += w * dt;
  }
  return th;
}
function cranePose(t) {
  const n = neckAt(t);
  const angles = {};
  for (let i = 0; i < 12; i++) angles['neck' + i] = n[i];
  angles.head = n[12];
  const sw = legSwing(t);
  Object.assign(angles, {
    tibia_near: 0.55 + sw, tarsus_near: -1.25 - sw * 0.4, foot_near: 0.55 - sw * 0.3,
    tibia_far: -0.05 + sw * 0.8, tarsus_far: 0.02 - sw * 0.3, foot_far: 0.03 - sw * 0.2,
  });
  return { angles, rootAngle: key(t, BODY), facing: 1 };
}

// ---- 小满的动作（背面，坐在小板凳上）
function xmPose(t) {
  const up = key(t, [[0, 0], [1.55, 0], [2.35, 1.08, 'out'], [2.8, 0.96], [3.3, 1]]);  // 坐直
  const open = key(t, [[0, 0], [1.9, 0], [2.9, 1, 'io']]);                             // 胳膊松开
  const peek = key(t, [[0, 0], [3.4, 0], [3.9, 1], [4.6, 1], [5, 0.6]]);                // 鹤啄的时候歪头
  const breath = 0.5 + 0.5 * Math.sin((t * Math.PI * 2) / 3.2);
  // 双马尾：坐直时被甩起来，再弹回
  const pig = kick(t, 1.75, 0.32, 2.2, 0.22) + kick(t, 2.35, -0.12, 2.6, 0.3);
  const crossed = (sg) => [-sg * 4.5, -60.5];
  const knees = (sg) => [sg * 9.5, -47.5];
  return {
    seated: true, hemY: -37.5,
    lean: 0.03 * (1 - up) - 0.05 * peek,
    shrug: 0.9 * (1 - up) - 0.15 * up,
    breath,
    head: { nod: 1.1 * (1 - up) - 0.5 * up, tilt: -0.10 * peek + 0.04 * (1 - up), turn: 0.2 * peek },
    pig: [pig, -pig * 0.9],
    cowlick: kick(t, 1.8, 0.8, 3.2, 0.2) + kick(t, 3.95, 0.3, 3.2, 0.2),
    armL: { hand: [lerp(crossed(-1)[0], knees(-1)[0], open), lerp(crossed(-1)[1], knees(-1)[1], open)], z: -1, bend: -1 },
    armR: { hand: [lerp(crossed(1)[0], knees(1)[0], open), lerp(crossed(1)[1], knees(1)[1], open)], z: -1, bend: 1 },
  };
}

// ---- 分层：先画在一个图层上、乘上自己的光、再贴到主画面
const LAYERS = {};
function layer(name, W, H) {
  let c = LAYERS[name];
  if (!c) c = LAYERS[name] = new OffscreenCanvas(W, H);
  if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
  const x = c.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none';
  x.clearRect(0, 0, W, H);
  return [c, x];
}
// 把 light(ctx) 画出的光照图只乘在图层已有的像素上
function multiplyLight(lc, light) {
  const W = lc.canvas.width, H = lc.canvas.height;
  const [m, mx] = layer('lightmask', W, H);
  light(mx);
  mx.globalCompositeOperation = 'destination-in';
  mx.drawImage(lc.canvas, 0, 0);
  lc.save(); lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'multiply'; lc.drawImage(m, 0, 0); lc.restore();
}

let crane = null;
export async function renderFrame(ctx, t, W, H) {
  crane ||= await loadPuppet('crane');
  setBoil(t);
  const S = W / 1920;
  ctx.save();
  ctx.scale(S, S);
  const flick = 1 + 0.035 * noise1(t * 7.3, 3) + 0.02 * noise1(t * 17.1, 5);
  const lamp = { ...LAMP, I: LAMP.I * flick };

  // ================= 1. 房间（后墙、床单下的后台、左边的门）
  const [room, rc] = layer('room', 1920, 1080);
  rc.fillStyle = '#cbbfa9'; rc.fillRect(0, 0, 1920, 1080);                 // 粉墙
  rc.fillStyle = '#5f7a66'; rc.fillRect(0, v(1.05), 1920, 1080);            // 墙裙（绿漆）
  shape(rc, [[0, v(1.05)], [1920, v(1.05)]], { closed: false, lw: 2.2, stroke: '#3f5546', seed: 2 });
  // 左边：通往里屋的门洞和门框
  fillPoly(rc, [[150, 60], [400, 60], [400, 1080], [150, 1080]], '#2c2420');
  for (const r of [[128, 40, 24, 1060], [396, 40, 24, 1060], [128, 40, 292, 22]]) shape(rc, rrectPts(r[0], r[1], r[2], r[3], 2), { fill: '#6b4a35', lw: 2.2, seed: r[0] + r[1], smooth: false });
  // 墙上几块旧水渍
  for (const [x, y, rx, ry, a] of [[700, 30, 260, 60, 0.07], [1500, 20, 300, 50, 0.06], [80, 400, 120, 260, 0.05]]) { rc.save(); rc.globalAlpha = a; radial(rc, x, y, rx, '120,96,70', 1, 1, ry / rx); rc.restore(); }
  // 床单下的后台：奶奶的裤腿（她站在灯左后方，换着脚）
  // （她在床单后面 0.84 米，透视上比床单平面小一点；灯在她身前，裤腿正面被照亮）
  const shift = 0.012 * Math.sin(t * 1.3);
  for (const [dx, k] of [[-0.075, 0], [0.075, 1]]) {
    const x0 = u(0.9 + dx + shift * (k ? 1 : -0.4));
    // 宽裤腿：上宽下略窄，膝盖处一道横褶
    const leg = [[x0 - 40, v(0.9)], [x0 + 40, v(0.9)], [x0 + 36, 960], [x0 + 33, 1090], [x0 - 32, 1090], [x0 - 36, 960]];
    shape(rc, leg, { fill: '#3e4454', lw: 2.2, seed: 40 + k, smooth: false });
    rc.save(); rc.clip(new Path2D(leg.map(([x, y], i) => (i ? 'L' : 'M') + x + ' ' + y).join(' ') + 'Z'));
    const g = rc.createLinearGradient(x0 - 40, 0, x0 + 40, 0);
    g.addColorStop(0, 'rgba(255,190,120,0)'); g.addColorStop(1, 'rgba(255,190,120,0.35)');
    rc.fillStyle = g; rc.fillRect(x0 - 45, v(0.9), 90, 400); rc.restore();
    shape(rc, [[x0 - 26, 938], [x0, 946], [x0 + 24, 936]], { closed: false, lw: 1.4, stroke: '#2c303b', seed: 46 + k });
    shape(rc, [[x0 + 6, v(0.88)], [x0 + 9, 1000], [x0 + 7, 1090]], { closed: false, lw: 1.2, stroke: '#2c303b', seed: 44 + k });
  }
  // 晾衣铁丝
  line(rc, [[-20, 58], [960, 63], [1940, 57]], { lw: 2.2, stroke: '#4a4038', seed: 6 });
  // ---- 房间的光：夜里的冷色环境光 + 马灯从床单上沿、下沿漏出来的暖光 + 床单本身把屋里照亮
  const lm = new LightMap(rc, '40,44,68');
  const lu = u(lamp.x), lv = v(lamp.z);
  lm.light((c) => { // 马灯：只从床单上面和下面漏出来（床单本身挡住了直射）
    radial(c, lu, lv, 1100, '255,186,110', 0.95 * flick, 1.3, 1);
  }, (c) => { c.fillRect(u(SHEET.x0) - 4, v(SHEET.z1) - 2, (SHEET.x1 - SHEET.x0) * K + 8, (SHEET.z1 - SHEET.z0) * K + 4); }, 18);
  lm.point(u(1.3), v(1.45), 1500, '255,196,130', 0.38 * flick, 1.25, 1);    // 床单发的光
  lm.point(u(1.3), v(0.62), 620, '255,182,104', 0.75 * flick, 1.5, 0.7);    // 床单下的缝：后台被马灯直接照亮
  lm.apply();
  ctx.drawImage(room, 0, 0);

  // ================= 2. 床单（自己发光：灯透过来的光 + 影子）
  const pose = cranePose(t);
  const root = key(t, ROOT), dist = key(t, DIST);
  const attach = { body: [8, 6], head: [16, 2] };
  const rods = Object.entries(attach).map(([part, at]) => ({ part, at, hand: null }));
  const actors = [{ pup: crane, pose, root, dist, rods: [] }];
  // 签子：从皮影往奶奶手那边（往后、往下）伸 0.55 米
  for (const R of rods) {
    actors[0].rods.push({ part: R.part, at: R.at, hand: [root[0] - 0.033, root[1] - 0.21 + (R.part === 'head' ? 0.06 : 0), dist + 0.506] });
  }
  const sh = sheetImage(SHEET, lamp, actors, 520);
  // 床单的轮廓：上沿夹在铁丝上（夹子之间微微下垂），下沿有点波浪
  const pins = [0.32, 0.68, 1.05, 1.42, 1.80, 2.17].map((x) => [u(x), v(SHEET.z1) - 2]);
  const top = [];
  for (let i = 0; i < pins.length - 1; i++) {
    top.push(pins[i]);
    top.push([(pins[i][0] + pins[i + 1][0]) / 2, pins[i][1] + 5]);
  }
  top.push(pins[pins.length - 1]);
  const outline = [[u(SHEET.x0), v(SHEET.z1) + 3], ...top, [u(SHEET.x1), v(SHEET.z1) + 3], [u(SHEET.x1) - 3, v(SHEET.z0) - 2],
    [u(1.9), v(SHEET.z0) + 4], [u(1.3), v(SHEET.z0) - 3], [u(0.8), v(SHEET.z0) + 5], [u(SHEET.x0) + 2, v(SHEET.z0)]];
  ctx.save();
  const sp = new Path2D();
  outline.forEach(([x, y], i) => (i ? sp.lineTo(x, y) : sp.moveTo(x, y)));
  sp.closePath();
  ctx.clip(sp);
  ctx.drawImage(sh.canvas, u(SHEET.x0), v(SHEET.z1), (SHEET.x1 - SHEET.x0) * K, (SHEET.z1 - SHEET.z0) * K);
  ctx.restore();
  // 床单边缘一道细墨线（手绘感）、夹子
  shape(ctx, outline, { lw: 2.0, stroke: 'rgba(70,52,38,0.55)', seed: 9, smooth: false, amp: 0.5 });
  for (const p of pins) {
    fillPoly(ctx, rrectPts(p[0] - 4, p[1] - 16, 8, 26, 3), '#8a6a4a');
    shape(ctx, rrectPts(p[0] - 4, p[1] - 16, 8, 26, 3), { lw: 1.6, stroke: '#3b2c25', seed: p[0] | 0, smooth: false });
  }
  // 床单周围的光晕
  glow(ctx, u(1.3), v(1.45), 900, '255,190,120', 0.10 * flick, 1.25, 1);

  // ================= 3. 小满（前景，背光：床单在她前面，所以她是一个被暖光勾出轮廓的背影）
  const [xl, xc] = layer('xm', 1920, 1080);
  const xs = 10.5;
  const XP = { x: 410, y: 1080 + 36 * xs, s: xs, ...xmPose(t) };
  // 小板凳
  xc.save(); xc.translate(XP.x, XP.y); xc.scale(xs, xs);
  for (const sg of [-1, 1]) shape(xc, [[sg * 9, -39], [sg * 11.5, -10], [sg * 9.6, -10], [sg * 7.2, -39]], { fill: '#7a5638', lw: 2.4, seed: 30 + sg });
  shape(xc, rrectPts(-14, -42.5, 28, 4.5, 1.2), { fill: '#8d6542', lw: 2.4, seed: 33 });
  xc.restore();
  const fx = X.draw(xc, 'back', XP, { defer: true });
  multiplyLight(xc, (c) => {
    c.fillStyle = 'rgb(96,86,100)'; c.fillRect(0, 0, 1920, 1080);
    c.globalCompositeOperation = 'lighter';
    radial(c, 1150, 300, 1250, '255,190,120', 0.62 * flick, 1.1, 1);       // 床单的光从右上方照过来
  });
  xc.save(); xc.translate(XP.x, XP.y); xc.scale(xs, xs);
  fx.fig.rim({ dirs: [[0.75, -0.66], [0.25, -1]], w: 7, rgb: '255,206,140', a: 0.85 * flick, blur: 1.5 });
  fx.fig.drawLights();
  xc.restore();
  ctx.drawImage(xl, 0, 0);

  // ================= 4. 整体：一点暗角
  const vg = ctx.createRadialGradient(1000, 480, 500, 1000, 480, 1250);
  vg.addColorStop(0, 'rgba(20,14,10,0)'); vg.addColorStop(1, 'rgba(20,14,10,0.42)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, 1920, 1080);
  ctx.restore();
}
