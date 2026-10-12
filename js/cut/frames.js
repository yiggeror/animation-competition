// 画风样张：同一个镜头、同一组纸片，三种画法。arg = '<画法>:<镜头>'，画法 paper | silhouette | gongbi，镜头 s06 | close
//   s06   第 6 场鹤亮相：正对床单。机位高 1 米、离床单 2.5 米；奶奶在床单后 0.84 米（按透视缩小，床单挡住上半身，只露出裤腿和布鞋）；
//         小满在床单前 1 米坐着看（侧面），脸被床单的光照亮。
//   close 后台，奶奶在马灯旁操纵鹤：灯在她脸前面，墙上投着她大大的影子；床单在右边，贴着鹤的背面。
import * as XC from './xiaoman.js';
import * as NC from './nainai.js';
import { drawPieces, silk } from './render.js';
import { circle, plum, pattern, petal4 } from './rig.js';
import { loadPuppet, drawPuppet, solve, pointOn } from '../puppet.js';
import { sheetImage } from '../shadowplay.js';
import { LightMap, radial, glow } from '../lib/light.js';

const SHEET = { x0: 0.25, x1: 2.35, z0: 0.86, z1: 2.08 };
const LAMP = { x: 1.30, z: 1.55, D: 0.70, core: 0.011, globe: 0.055, coreW: 1.0, globeW: 0.55, rgb: [255, 200, 128], I: 1.32 };
const NECK_HIGH = [1.10, 0.12, 0.10, 0.07, 0.02, -0.04, -0.10, -0.14, -0.16, -0.15, -0.12, -0.08, -0.40];
function cranePose() {
  const angles = {};
  NECK_HIGH.slice(0, 12).forEach((a, i) => (angles['neck' + i] = a));
  Object.assign(angles, { head: NECK_HIGH[12], tibia_near: 0.55, tarsus_near: -1.25, foot_near: 0.55, tibia_far: -0.05, tarsus_far: 0.02, foot_far: 0.03 });
  return { angles, rootAngle: 0.05, facing: 1 };
}

// 透视：机位高 1 米、离床单 2.5 米；δ = 离床单的深度（往后为正）
const CAM = { h: 1.0, d: 2.5, k: 470, cx: 1253, X: 1.3, hy: 560 };
const kAt = (dl) => (CAM.k * CAM.d) / (CAM.d + dl);
const P3 = (X, Z, dl = 0) => [CAM.cx + (X - CAM.X) * kAt(dl), CAM.hy + (CAM.h - Z) * kAt(dl)];
const rect = (x0, y0, x1, y1) => [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];

let crane = null;
export async function render(ctx, arg = 'paper:s06', W, H) {
  crane ||= await loadPuppet('crane');
  const [style, shot] = arg.split(':');
  ctx.save(); ctx.scale(W / 1920, H / 1080);
  if (shot === 'close') closeup(ctx, style);
  else s06(ctx, style);
  ctx.restore();
}

// ================================================================== 第 6 场
function s06(ctx, style) {
  const pieces = [];
  const wallY0 = P3(0, 1.05, 1.0)[1], floorBack = P3(0, 0, 1.0)[1];
  // 后墙（床单后 1 米）、墙裙、地面
  pieces.push({ name: 'wall', pts: rect(-20, -20, 1940, wallY0 + 2), z: 0, fill: '#d8cbb2', flat: true, noShadow: true, fiber: 0.45, group: 'set' });
  const wave = []; for (let x = -20; x <= 1940; x += 24) wave.push([x, wallY0 + (Math.floor((x + 20) / 24) % 2 ? 7 : -2)]);
  pieces.push({ name: 'wains', pts: [...wave, [1940, floorBack + 2], [-20, floorBack + 2]], z: 0.1, fill: '#4f7562', flat: true, group: 'set', lift: 0.25 });
  pieces.push({ name: 'floor', pts: rect(-20, floorBack, 1940, 1100), z: 0.2, fill: '#8c7a63', flat: true, noShadow: true, fiber: 0.5, group: 'set' });
  // 左边：通往里屋的门，挂着蓝底的门帘（镂空团花）
  const dl = 1.0, L = P3(-1.15, 2.05, dl), R = P3(-0.35, 0, dl);
  pieces.push({ name: 'doorframe', pts: rect(L[0] - 14, L[1] - 14, R[0] + 14, R[1]), z: 0.5, fill: '#6a4632', flat: true, group: 'set' });
  pieces.push({ name: 'doorway', pts: rect(L[0], L[1], R[0], R[1]), z: 0.55, fill: '#2a2220', flat: true, noShadow: true, group: 'set' });
  const curtain = [[L[0] + 6, L[1] + 4], [R[0] - 6, L[1] + 4], [R[0] - 4, L[1] + 420]];
  for (let i = 0; i <= 6; i++) { const x = R[0] - 4 - (i / 6) * (R[0] - L[0] - 8); curtain.push([x, L[1] + 420 + (i % 2 ? 26 : 4)]); }
  curtain.push([L[0] + 4, L[1] + 420]);
  pieces.push({ name: 'curtain', pts: curtain, z: 0.6, fill: '#3d5f8f', under: '#e8e0cc', group: 'set', flat: true,
    holes: pattern(curtain, 54, 13, (x, y, r, row) => plum(x, y, r, row * 0.5), 18), lift: 1.2 });
  // 墙上一张红色团花窗花（剪纸里的剪纸）
  const cc = P3(-1.75, 1.92, 1.0);
  const flower = circle(cc[0], cc[1] - 30, 46, 40);
  pieces.push({ name: 'chuanghua', pts: flower, z: 0.7, fill: '#c8392b', group: 'set', holes: [...pattern(flower, 17, 4.5, (x, y, r, row) => plum(x, y, r, row)), ...[0, 1, 2, 3, 4, 5].map((i) => circle(cc[0] + Math.cos(i * 1.047) * 30, cc[1] - 30 + Math.sin(i * 1.047) * 30, 3.5, 8))].slice(0, 22), lift: 0.6 });
  // 奶奶：在床单后面 0.84 米，侧身朝着马灯（按透视缩小；床单挡住上半身）
  const kN = kAt(0.84) / 100;
  const nnFoot = P3(0.82, 0, 0.84);
  const nn = NC.pieces({ x: nnFoot[0], y: nnFoot[1] - 59 * kN, s: kN, legN: { angles: [-0.12, 0.08, 0.04] }, legF: { angles: [0.1, -0.02, 0] },
    armN: { hand: [nnFoot[0] + 26 * kN, nnFoot[1] - 98 * kN], hp: 'grip' }, armF: { hand: [nnFoot[0] + 30 * kN, nnFoot[1] - 104 * kN], hp: 'grip' } });
  pieces.push(...nn.pieces.map((p) => ({ ...p, z: 1 + p.z * 0.01, group: 'nn' })));
  // 后台的木箱
  const b0 = P3(1.85, 0.42, 0.95), b1 = P3(2.45, 0, 0.95);
  pieces.push({ name: 'chest', pts: rect(b0[0], b0[1], b1[0], b1[1]), z: 0.9, fill: '#8a4f2c', flat: true, group: 'set', slits: [{ pts: [[b0[0] + 6, b0[1] + 26], [b1[0] - 6, b0[1] + 26]], w: 3, color: 'rgba(40,24,14,0.7)' }] });
  for (const [cx, cy] of [[b0[0], b0[1]], [b1[0], b0[1]], [b0[0], b1[1]], [b1[0], b1[1]]]) pieces.push({ name: 'corner', pts: circle(cx, cy, 13, 12), z: 0.95, fill: '#c99a45', group: 'set', lift: 0.3 });
  pieces.push({ name: 'lock', pts: rect((b0[0] + b1[0]) / 2 - 10, b0[1] + 18, (b0[0] + b1[0]) / 2 + 10, b0[1] + 44), z: 0.96, fill: '#c99a45', flat: true, group: 'set', lift: 0.3 });
  // 晾衣铁丝右头推过去的衣服：一条红条纹毛巾、一件小满的蓝衬衫
  const wy = P3(2.5, 2.09)[1];
  const towel = [[1770, wy], [1850, wy - 2], [1856, wy + 160], [1774, wy + 166]];
  pieces.push({ name: 'towel', pts: towel, z: 21, fill: '#f3ead6', group: 'laundry', flat: true, slits: [0, 1, 2].map((i) => ({ pts: [[1772, wy + 120 + i * 12], [1854, wy + 118 + i * 12]], w: 5, color: '#c8392b' })) });
  const shirt = [[1858, wy], [1945, wy - 3], [1950, wy + 40], [1935, wy + 150], [1868, wy + 152], [1860, wy + 40]];
  pieces.push({ name: 'shirt', pts: shirt, z: 21.1, fill: '#7fa3c9', under: '#eef2f4', group: 'laundry', holes: pattern(shirt, 22, 4, (x, y, r, row) => petal4(x, y, r, row)), flat: true });
  // 门边：一篮毛豆、一个红暖水瓶
  const bk = P3(-0.15, 0.0, 0.6);
  pieces.push({ name: 'basket', pts: [[bk[0] - 70, bk[1] - 60], [bk[0] + 70, bk[1] - 60], [bk[0] + 56, bk[1]], [bk[0] - 56, bk[1]]], z: 1.5, fill: '#b98a4e', group: 'set', slits: [0, 1, 2].map((i) => ({ pts: [[bk[0] - 64 + i * 4, bk[1] - 42 + i * 16], [bk[0] + 64 - i * 4, bk[1] - 42 + i * 16]], w: 2.5, color: 'rgba(90,60,30,0.7)' })) });
  for (let i = 0; i < 7; i++) pieces.push({ name: 'pea', pts: circle(bk[0] - 48 + i * 16, bk[1] - 64 - (i % 2) * 8, 12, 10).map(([x, y]) => [x, y + (x - bk[0]) * 0.05]), z: 1.45, fill: '#7fae4f', group: 'set', lift: 0.3 });
  const th = P3(-0.55, 0.0, 0.7);
  pieces.push({ name: 'thermos', pts: [[th[0] - 22, th[1] - 150], [th[0] + 22, th[1] - 150], [th[0] + 26, th[1] - 120], [th[0] + 26, th[1]], [th[0] - 26, th[1]], [th[0] - 26, th[1] - 120]], z: 1.4, fill: '#c8392b', group: 'set', flat: true, slits: [{ pts: [[th[0] - 24, th[1] - 70], [th[0] + 24, th[1] - 70]], w: 6, color: '#e7c35a' }] });
  // 前景：画面左边挂着一串干红辣椒（离镜头最近的一层）
  const fore = [];
  fore.push({ name: 'rope', pts: [[96, -20], [104, -20], [104, 520], [96, 520]], z: 30, fill: '#a0784c', flat: true, group: 'fore', lift: 2.2 });
  for (let i = 0; i < 9; i++) {
    const y = 40 + i * 52, sg = i % 2 ? 1 : -1;
    fore.push({ name: 'chili', pts: [[100, y], [100 + sg * 30, y + 8], [100 + sg * 58, y + 38], [100 + sg * 64, y + 62], [100 + sg * 40, y + 40], [100 + sg * 14, y + 22]], z: 30.1 + i * 0.01, fill: i % 3 === 1 ? '#a8261c' : '#c8392b', group: 'fore', lift: 2.2,
      slits: [{ pts: [[100 + sg * 14, y + 12], [100 + sg * 40, y + 30]], w: 2, color: 'rgba(255,200,170,0.35)' }] });
  }
  // 小满：床单前 1 米，坐着看（侧面），脸被床单照亮
  const kX = kAt(-0.85) / 100;
  const xmHip = P3(0.1, 0.34, -0.85);
  const xm = XC.pieces({ x: xmHip[0], y: xmHip[1], s: kX, seated: true, lean: 0.12, face: { eye: 'wide', mouth: 'open' }, head: { tilt: -0.14 }, pig: [0.05, 0.1],
    armN: { hand: [xmHip[0] + 15 * kX, xmHip[1] - 4 * kX] }, armF: { hand: [xmHip[0] + 13 * kX, xmHip[1] - 5 * kX] } });
  // 小板凳
  const stool = [{ name: 'seat', pts: rect(xmHip[0] - 13 * kX, xmHip[1] + 2 * kX, xmHip[0] + 11 * kX, xmHip[1] + 5.5 * kX), z: 9.5, fill: '#8d5e3a', flat: true, group: 'stool' },
    ...[-10, 8].map((dx) => ({ name: 'sleg', pts: [[xmHip[0] + dx * kX, xmHip[1] + 5 * kX], [xmHip[0] + (dx + 3) * kX, xmHip[1] + 5 * kX], [xmHip[0] + (dx + 4.5) * kX, xmHip[1] + 40 * kX], [xmHip[0] + (dx + 1.5) * kX, xmHip[1] + 40 * kX]], z: 9.4, fill: '#7a4f30', flat: true, group: 'stool' }))];
  const xmPieces = [...stool, ...xm.pieces.map((p) => ({ ...p, z: 10 + p.z * 0.01 }))];

  // ---- 床单（自己发光，物理影子）
  const root = [1.03, 1.30], dist = 0.004, pose = cranePose();
  const sh = sheetImage(SHEET, LAMP, [{ pup: crane, pose, root, dist, rods: [{ part: 'body', at: [8, 6], hand: [root[0] - 0.033, root[1] - 0.24, 0.47] }, { part: 'head', at: [16, 2], hand: [root[0] - 0.033, root[1] - 0.10, 0.40] }] }], 520);
  const s0 = P3(SHEET.x0, SHEET.z1), s1 = P3(SHEET.x1, SHEET.z0);
  const drawSheet = (alpha = 1) => {
    ctx.save(); ctx.globalAlpha = alpha;
    const pins = [0.32, 0.68, 1.05, 1.42, 1.80, 2.17].map((x) => P3(x, SHEET.z1));
    const path = new Path2D();
    path.moveTo(s0[0], s0[1] + 3);
    for (let i = 0; i < pins.length; i++) { path.lineTo(pins[i][0], pins[i][1] - 1); if (i < pins.length - 1) path.quadraticCurveTo((pins[i][0] + pins[i + 1][0]) / 2, pins[i][1] + 7, pins[i + 1][0], pins[i + 1][1] - 1); }
    path.lineTo(s1[0], s0[1] + 3); path.lineTo(s1[0] - 2, s1[1]); path.quadraticCurveTo((s0[0] + s1[0]) / 2, s1[1] + 8, s0[0] + 2, s1[1] - 2); path.closePath();
    ctx.clip(path);
    ctx.drawImage(sh.canvas, s0[0], s0[1], s1[0] - s0[0], s1[1] - s0[1]);
    ctx.restore();
    return pins;
  };
  const wire = (c) => { c.strokeStyle = '#3b3029'; c.lineWidth = 2.2; c.beginPath(); c.moveTo(-20, s0[1] - 6); c.quadraticCurveTo(960, s0[1] + 4, 1940, s0[1] - 8); c.stroke(); };
  const pinsPieces = [0.32, 0.68, 1.05, 1.42, 1.80, 2.17].map((x) => { const p = P3(x, SHEET.z1); return { name: 'pin', pts: rect(p[0] - 5, p[1] - 18, p[0] + 5, p[1] + 10), z: 20, fill: '#9a7652', flat: true, group: 'pins', lift: 0.3 }; });

  if (style === 'silhouette') {
    // 背景本身就是光：上面靛蓝的夜，床单周围和床单下沿被马灯照成暖金
    const g = ctx.createLinearGradient(0, 0, 0, 1080);
    g.addColorStop(0, '#1d2747'); g.addColorStop(0.55, '#4a4258'); g.addColorStop(1, '#2a2233');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080);
    radial(ctx, P3(1.3, 1.55, 0.7)[0], 380, 1100, '255,186,110', 0.75, 1.2, 1);
    radial(ctx, P3(1.3, 0.3, 0.8)[0], P3(1.3, 0.3, 0.8)[1], 560, '255,190,120', 0.9, 1.6, 0.6);
    drawPieces(ctx, [...pieces.filter((p) => !['wall', 'wains', 'floor'].includes(p.name))], 'silhouette', { s: 4.7, silhouette: '#140f18' });
    drawSheet();
    wire(ctx);
    drawPieces(ctx, pinsPieces, 'silhouette', { s: 4.7, silhouette: '#140f18' });
    glow(ctx, P3(1.3, 1.45)[0], P3(1.3, 1.45)[1], 950, '255,190,120', 0.14, 1.25, 1);
    drawPieces(ctx, xmPieces, 'silhouette', { s: 4.7, silhouette: '#120d16', rim: { dir: [1, -0.25], rgb: '255,206,140', a: 0.95, w: 7, blur: 1.2 } });
    drawPieces(ctx, fore, 'silhouette', { s: 4.7, silhouette: '#0d0a10' });
    vignette(ctx, 0.45);
    return;
  }
  // 剪纸片 / 工笔：先画纸片，再乘光照图，再画发光的床单，最后小满（她有自己的光）
  drawPieces(ctx, pieces, style, { s: 4.7, shadow: [-4, 6] });
  const lm = new LightMap(ctx, style === 'gongbi' ? '138,140,168' : '48,60,112');
  const lampP = P3(1.3, 1.55, 0.7);
  lm.point(lampP[0], lampP[1], 980, '255,176,96', 1.15, 1.35, 1);                 // 马灯从床单上下沿漏出来的光
  lm.point(P3(1.3, 1.4)[0], P3(1.3, 1.4)[1] + 300, 1300, '255,196,130', 0.38, 1.2, 0.8);   // 床单发的光照到屋里
  lm.point(P3(1.3, 0.3, 0.8)[0], P3(1.3, 0.3, 0.8)[1], 640, '255,184,108', 0.9, 1.6, 0.6);   // 床单下沿的缝：后台被直接照亮
  lm.apply();
  drawSheet();
  wire(ctx);
  drawPieces(ctx, pinsPieces, style, { s: 4.7, shadow: [-2, 3] });
  glow(ctx, P3(1.3, 1.45)[0], P3(1.3, 1.45)[1], 950, '255,190,120', 0.12, 1.25, 1);
  // 小满单独一层：画好、乘她自己的光（右边床单的暖光 + 冷色环境），再加脸上的亮边
  const [lay, lc] = layer('xm', ctx.canvas.width, ctx.canvas.height);
  lc.setTransform(ctx.getTransform());
  drawPieces(lc, xmPieces, style, { s: 4.7, shadow: [-5, 6] });
  multiplyLight(lc, (c) => {
    c.setTransform(ctx.getTransform());
    c.fillStyle = style === 'gongbi' ? 'rgb(160,160,186)' : 'rgb(76,86,138)'; c.fillRect(0, 0, 1920, 1080);
    c.globalCompositeOperation = 'lighter';
    radial(c, 820, 420, 1500, '255,196,130', 1.0, 1.1, 1);   // 床单的暖光照在她朝着床单的脸上
  });
  rimOn(lc, xmPieces, { dir: [1, -0.25], rgb: '255,210,150', a: 0.75, w: 6, blur: 1.5 }, ctx.getTransform());
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(lay, 0, 0); ctx.restore();
  const [fl, fc] = layer('fore', ctx.canvas.width, ctx.canvas.height);
  fc.setTransform(ctx.getTransform());
  drawPieces(fc, fore, style, { s: 4.7, shadow: [-14, 18], shadowBlur: 12 });
  multiplyLight(fc, (c) => { c.setTransform(ctx.getTransform()); c.fillStyle = style === 'gongbi' ? 'rgb(170,160,180)' : 'rgb(110,90,120)'; c.fillRect(0, 0, 1920, 1080); });
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(fl, 0, 0); ctx.restore();
  if (style === 'gongbi') silk(ctx, 1920, 1080, 0.18);
  vignette(ctx, 0.35);
}

// ================================================================== 后台近景
function closeup(ctx, style) {
  const s = 12.0;
  const base = [600, 1080 + 2 * s];           // 奶奶的髋（在画面下边上）
  const lampP = [1000, 330];                   // 马灯：在她脸前面一点、略高
  // 签子的两端：奶奶胸前的手 → 床单上的鹤（右边）
  const hN = [base[0] + 22 * s, base[1] - 22 * s], hF = [base[0] + 27 * s, base[1] - 27 * s];
  const nn = NC.pieces({ x: base[0], y: base[1], s, stoop: 1, head: { nod: 0.3 }, face: { eye: 'open', mouth: 'smile' },
    armN: { hand: hN, hp: 'grip' }, armF: { hand: hF, hp: 'grip' } });
  const pieces = [];
  pieces.push({ name: 'wall', pts: rect(-20, -20, 1940, 1100), z: 0, fill: '#cdbfa6', flat: true, noShadow: true, fiber: 0.45, group: 'set' });
  pieces.push({ name: 'wains', pts: rect(-20, 760, 1940, 1100), z: 0.1, fill: '#5a7761', flat: true, noShadow: true, group: 'set' });
  // 床单（侧着看，一条亮带）
  const sheetQ = [[1600, 60], [1960, 20], [1960, 1100], [1600, 1010]];
  // 马灯：铁提梁、玻璃罩（发光）、油壶
  const lampPieces = [
    { name: 'string', pts: [[lampP[0] - 2, -20], [lampP[0] + 2, -20], [lampP[0] + 2, lampP[1] - 110], [lampP[0] - 2, lampP[1] - 110]], z: 29, fill: '#8a6d4d', flat: true, group: 'lamp' },
    { name: 'bail', pts: [[lampP[0] - 34, lampP[1] - 112], [lampP[0] + 34, lampP[1] - 112], [lampP[0] + 30, lampP[1] - 96], [lampP[0] - 30, lampP[1] - 96]], z: 30, fill: '#3a3632', flat: true, group: 'lamp' },
    { name: 'tank', pts: [[lampP[0] - 52, lampP[1] + 58], [lampP[0] + 52, lampP[1] + 58], [lampP[0] + 46, lampP[1] + 110], [lampP[0] - 46, lampP[1] + 110]], z: 30, fill: '#4b4743', group: 'lamp', slits: [{ pts: [[lampP[0] - 40, lampP[1] + 78], [lampP[0] + 40, lampP[1] + 78]], w: 3, color: 'rgba(20,18,16,0.6)' }] },
    { name: 'cap', pts: [[lampP[0] - 40, lampP[1] - 98], [lampP[0] + 40, lampP[1] - 98], [lampP[0] + 44, lampP[1] - 80], [lampP[0] - 44, lampP[1] - 80]], z: 30.2, fill: '#3e3a36', flat: true, group: 'lamp' },
  ];
  const chimney = circle(lampP[0], lampP[1] - 12, 44, 30).map(([x, y]) => [x, lampP[1] - 12 + (y - lampP[1] + 12) * 1.55]);
  // 墙上奶奶的大影子：马灯在她前面，影子投在身后的墙上（以灯为中心放大）
  const shadowPieces = nn.pieces.filter((p) => !['glasses', 'temple'].includes(p.name)).map((p) => ({
    ...p, pts: p.pts.map(([x, y]) => [lampP[0] + (x - lampP[0]) * 1.7, lampP[1] + (y - lampP[1]) * 1.7]), holes: undefined, slits: undefined, dots: undefined,
  }));
  const rodPts = [[hN, [1660, 560]], [hF, [1700, 380]]];
  const drawRods = (c) => { c.strokeStyle = '#7a5838'; c.lineWidth = 6; c.lineCap = 'round'; for (const [a, b] of rodPts) { c.beginPath(); c.moveTo(a[0] - 18, a[1] + 14); c.lineTo(b[0], b[1]); c.stroke(); } };
  const drawCraneBack = (c) => { // 鹤贴在床单背面：斜着看（压扁）
    c.save(); c.translate(1665, 565); c.transform(0.42, -0.08, 0, -0.95, 0, 0);
    drawPuppet(c, crane, cranePose(), 'r'); c.restore();
  };
  const nnPieces = nn.pieces.map((p) => ({ ...p, z: 10 + p.z * 0.01 }));
  if (style === 'silhouette') {
    const g = ctx.createLinearGradient(0, 0, 1920, 0);
    g.addColorStop(0, '#1b2242'); g.addColorStop(0.55, '#7a5a4a'); g.addColorStop(1, '#f4c27a');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080);
    radial(ctx, lampP[0], lampP[1], 900, '255,190,115', 0.9, 1, 1.1);
    ctx.save(); ctx.fillStyle = 'rgba(255,236,200,0.9)'; ctx.beginPath(); sheetQ.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill(); ctx.restore();
    drawCraneBack(ctx);
    ctx.save(); ctx.globalCompositeOperation = 'source-atop'; ctx.restore();
    drawRods(ctx);
    drawPieces(ctx, nnPieces, 'silhouette', { s, silhouette: '#120d16', rim: { dir: [1, -0.3], rgb: '255,206,140', a: 0.95, w: 9, blur: 1.5 } });
    drawPieces(ctx, lampPieces, 'silhouette', { s, silhouette: '#120d16' });
    ctx.fillStyle = 'rgba(255,224,170,0.95)'; ctx.fill(new Path2D(polyD(chimney)));
    glow(ctx, lampP[0], lampP[1] - 10, 260, '255,200,130', 0.7); glow(ctx, lampP[0], lampP[1] - 10, 60, '255,245,215', 1);
    vignette(ctx, 0.4);
    return;
  }
  drawPieces(ctx, pieces, style, { s: 6 });
  // 墙上的影子（柔和、暖暗）
  ctx.save(); ctx.filter = 'blur(10px)'; ctx.fillStyle = 'rgba(60,36,24,0.42)';
  for (const p of shadowPieces) ctx.fill(new Path2D(polyD(p.pts)));
  ctx.restore();
  // 床单（侧着看）、鹤的背面、签子
  ctx.save(); const sg = ctx.createLinearGradient(1600, 0, 1920, 0); sg.addColorStop(0, '#fff2d6'); sg.addColorStop(1, '#e8cf9e'); ctx.fillStyle = sg; ctx.beginPath(); sheetQ.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill(); ctx.restore();
  drawCraneBack(ctx);
  drawRods(ctx);
  drawPieces(ctx, nnPieces, style, { s, shadow: [-8, 10] });
  drawPieces(ctx, lampPieces, style, { s });
  const lm = new LightMap(ctx, style === 'gongbi' ? '138,140,168' : '44,54,104');
  lm.point(lampP[0], lampP[1], 1200, '255,190,115', 1.05, 1, 1.05);
  lm.point(1780, 500, 700, '255,214,160', 0.5, 0.6, 1.4);
  lm.apply();
  // 玻璃罩和火苗（发光）
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = 'rgba(255,200,120,0.55)'; ctx.fill(new Path2D(polyD(chimney))); ctx.restore();
  ctx.save(); ctx.fillStyle = 'rgba(255,246,220,1)'; ctx.beginPath(); ctx.ellipse(lampP[0], lampP[1] - 8, 9, 22, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  glow(ctx, lampP[0], lampP[1] - 10, 260, '255,200,130', 0.6); glow(ctx, lampP[0], lampP[1] - 10, 700, '255,180,110', 0.14);
  // 奶奶面向灯的一侧亮边、眼镜上的一点反光
  rimOn(ctx, nnPieces, { dir: [1, -0.3], rgb: '255,206,140', a: 0.7, w: 8, blur: 1.5 }, ctx.getTransform(), true);
  if (style === 'gongbi') silk(ctx, 1920, 1080, 0.18);
  vignette(ctx, 0.35);
}

// ---------------------------------------------------------------- 小工具
function polyD(pts) { return pts.map(([x, y], i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1)).join(' ') + 'Z'; }
const LAY = {};
function layer(name, W, H) {
  let c = LAY[name];
  if (!c) c = LAY[name] = new OffscreenCanvas(W, H);
  if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
  const x = c.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none'; x.clearRect(0, 0, W, H);
  return [c, x];
}
function multiplyLight(lc, light) {
  const W = lc.canvas.width, H = lc.canvas.height;
  const [m, mx] = layer('lm', W, H);
  light(mx);
  mx.setTransform(1, 0, 0, 1, 0, 0);
  mx.globalCompositeOperation = 'destination-in'; mx.drawImage(lc.canvas, 0, 0);
  lc.save(); lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'multiply'; lc.drawImage(m, 0, 0); lc.restore();
}
// 亮边：这组纸片的整体轮廓往背光方向平移、相减
function rimOn(c, pcs, rim, T, direct = false) {
  const W = c.canvas.width, H = c.canvas.height;
  const [m, mx] = layer('rimA', W, H);
  mx.setTransform(T);
  mx.fillStyle = '#fff';
  for (const p of pcs) { if (!p._p) continue; mx.fill(p._p); }
  const [r, rx] = layer('rimB', W, H);
  rx.drawImage(m, 0, 0);
  rx.globalCompositeOperation = 'destination-out';
  const k = W / 1920, len = Math.hypot(rim.dir[0], rim.dir[1]);
  rx.drawImage(m, (-rim.dir[0] / len) * rim.w * k, (-rim.dir[1] / len) * rim.w * k);
  rx.globalCompositeOperation = 'source-in'; rx.fillStyle = `rgb(${rim.rgb})`; rx.fillRect(0, 0, W, H);
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalCompositeOperation = 'screen'; c.globalAlpha = rim.a; c.filter = `blur(${(rim.blur ?? 1) * k}px)`;
  c.drawImage(r, 0, 0);
  c.restore();
}
function vignette(ctx, a) {
  const g = ctx.createRadialGradient(1000, 500, 420, 1000, 500, 1250);
  g.addColorStop(0, 'rgba(18,12,10,0)'); g.addColorStop(1, `rgba(18,12,10,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080);
}
