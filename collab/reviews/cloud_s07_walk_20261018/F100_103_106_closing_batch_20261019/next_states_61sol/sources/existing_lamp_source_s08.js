// S08 · 第 2 场：马灯特写。黑暗里，奶奶左手托着火柴盒，右手捏一根火柴"嚓"地划着（0.35 秒），火光照亮两只手；
// 火柴伸到抬起的灯罩下面，灯芯着了（1.8），甩灭火柴（2.2）；顺手按下灯罩右边的拨杆，灯罩落下（3.4，"叮"）——暖光一下子铺开。
// 时间和 audio/build.py 的 S08 音效对齐。马灯照片式的结构：油壶、灯头（灯芯、调芯旋钮）、玻璃灯罩、护丝、两根侧管、顶盖和提梁。
import { drawHand, POSES, mixPose, orient, shade } from './hand3d.js';
export const DURATION = 6;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;
export const LX = 1120, LB = 950;          // 马灯中心 x、底 y（设计坐标）

// ---------------------------------------------------------------- 桌面和背景（固有色，之后乘光照）
let BG = null;
function bg() {
  if (BG) return BG;
  const c = new OffscreenCanvas(RW, RH), x = c.getContext('2d');
  let seed = 3; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  // 远处的墙（虚）
  x.fillStyle = '#b9ab92'; x.fillRect(0, 0, RW, RH);
  x.filter = 'blur(18px)';
  x.fillStyle = '#8c7a60'; x.fillRect(1500, 120, 260, 520);                     // 立柜（虚）
  x.fillStyle = '#d8ccb2'; x.fillRect(180, 160, 300, 220);                      // 墙上的老照片框（虚）
  x.fillStyle = '#6f5c44'; x.fillRect(200, 180, 260, 180);
  x.filter = 'none';
  // 八仙桌面：木纹
  const top = RH * 0.78;
  x.fillStyle = '#8a5a34'; x.fillRect(0, top, RW, RH - top);
  for (let i = 0; i < 40; i++) {
    x.strokeStyle = `rgba(${rnd() < 0.5 ? '60,35,18' : '170,120,75'},${0.15 + 0.15 * rnd()})`; x.lineWidth = 1 + rnd() * 3;
    const y = top + rnd() * (RH - top); x.beginPath(); x.moveTo(0, y); for (let xx = 0; xx <= RW; xx += 80) x.lineTo(xx, y + Math.sin(xx * 0.004 + i) * 6 + (rnd() - 0.5) * 3); x.stroke();
  }
  x.strokeStyle = LINE; x.lineWidth = 4; x.beginPath(); x.moveTo(0, top); x.lineTo(RW, top); x.stroke();
  x.fillStyle = 'rgba(255,230,190,0.18)'; x.fillRect(0, top + 2, RW, 6);
  return (BG = c);
}

// ---------------------------------------------------------------- 马灯
export function lamp(x, lift, flameOn) {
  x.save(); x.translate(LX, LB); x.lineJoin = 'round'; x.lineCap = 'round';
  const L = (w) => { x.strokeStyle = LINE; x.lineWidth = w; };
  // 桌上的影子
  x.fillStyle = 'rgba(30,15,5,0.35)'; x.beginPath(); x.ellipse(0, 4, 230, 26, 0, 0, 7); x.fill();
  // 两根侧管（冷风式马灯）：从油壶两边升到顶盖
  for (const sd of [-1, 1]) {
    x.fillStyle = '#a3302a'; L(4);
    x.beginPath(); x.moveTo(sd * 168, -120); x.lineTo(sd * 168, -560); x.quadraticCurveTo(sd * 168, -610, sd * 120, -612); x.lineTo(sd * 100, -612); x.lineTo(sd * 100, -590); x.lineTo(sd * 122, -590); x.quadraticCurveTo(sd * 146, -590, sd * 146, -560); x.lineTo(sd * 146, -120); x.closePath(); x.fill(); x.stroke();
    x.fillStyle = 'rgba(255,220,180,0.25)'; x.fillRect(sd * 157 - 3, -540, 6, 400);
  }
  // 油壶：扁圆柱，红漆，边上一圈压线
  x.fillStyle = '#a3302a'; L(5);
  x.beginPath(); x.moveTo(-190, -20); x.quadraticCurveTo(-200, -120, -150, -140); x.lineTo(150, -140); x.quadraticCurveTo(200, -120, 190, -20); x.quadraticCurveTo(0, 12, -190, -20); x.closePath(); x.fill(); x.stroke();
  x.strokeStyle = 'rgba(60,20,12,0.6)'; x.lineWidth = 3; x.beginPath(); x.moveTo(-185, -70); x.quadraticCurveTo(0, -48, 185, -70); x.stroke();
  x.fillStyle = 'rgba(255,200,170,0.22)'; x.beginPath(); x.ellipse(-90, -110, 60, 12, -0.1, 0, 7); x.fill();
  x.fillStyle = '#c9a046'; L(3); x.beginPath(); x.ellipse(110, -132, 22, 8, 0, 0, 7); x.fill(); x.stroke();   // 加油口
  // 灯头：铜座 + 调芯旋钮
  x.fillStyle = '#c49a45'; L(4);
  x.beginPath(); x.moveTo(-70, -140); x.lineTo(-58, -200); x.lineTo(58, -200); x.lineTo(70, -140); x.closePath(); x.fill(); x.stroke();
  x.beginPath(); x.ellipse(84, -170, 16, 22, 0, 0, 7); x.fill(); x.stroke();
  x.strokeStyle = 'rgba(80,50,15,0.6)'; x.lineWidth = 2; for (let k = -2; k <= 2; k++) { x.beginPath(); x.moveTo(84 + k * 5, -190); x.lineTo(84 + k * 5, -150); x.stroke(); }
  // 灯芯（扁的棉芯，烧过的头发黑）
  x.fillStyle = '#e8dcc0'; L(2.5); x.beginPath(); x.rect(-22, -222, 44, 22); x.fill(); x.stroke();
  x.fillStyle = '#2b2018'; x.fillRect(-21, -226, 42, 6);
  // 灯罩托（灯罩坐在上面）
  const gy = -200 - lift * 110;                                // 灯罩底边
  x.fillStyle = '#7d2622'; L(4); x.beginPath(); x.ellipse(0, gy - 4, 128, 16, 0, 0, 7); x.fill(); x.stroke();
  // 玻璃灯罩：鼓肚，半透明；火苗在里面
  const glob = new Path2D();
  glob.moveTo(-96, gy - 6); glob.bezierCurveTo(-190, gy - 120, -170, gy - 300, -70, gy - 340); glob.lineTo(70, gy - 340); glob.bezierCurveTo(170, gy - 300, 190, gy - 120, 96, gy - 6); glob.closePath();
  x.fillStyle = 'rgba(225,235,230,0.18)'; x.fill(glob);
  x.strokeStyle = 'rgba(74,46,31,0.85)'; x.lineWidth = 3; x.stroke(glob);
  x.strokeStyle = 'rgba(255,255,255,0.35)'; x.lineWidth = 7; x.beginPath(); x.moveTo(-120, gy - 70); x.bezierCurveTo(-150, gy - 160, -130, gy - 260, -80, gy - 300); x.stroke();   // 玻璃上的高光
  // 护丝：几道弯的铁丝 + 一道横箍
  x.strokeStyle = '#3a2a22'; x.lineWidth = 4;
  for (const k of [-1, -0.35, 0.35, 1]) { x.beginPath(); x.moveTo(k * 110, gy - 10); x.bezierCurveTo(k * 205, gy - 130, k * 190, gy - 280, k * 80, gy - 345); x.stroke(); }
  x.beginPath(); x.ellipse(0, gy - 170, 182, 18, 0, 0, Math.PI); x.stroke();
  // 顶盖：一个带孔的圆帽，连着两根侧管
  const ty = -598;
  x.fillStyle = '#8f2a25'; L(4);
  x.beginPath(); x.moveTo(-110, ty + 20); x.quadraticCurveTo(-100, ty - 40, 0, ty - 52); x.quadraticCurveTo(100, ty - 40, 110, ty + 20); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = '#2b1a14'; for (let k = -2; k <= 2; k++) { x.beginPath(); x.ellipse(k * 34, ty - 8, 8, 5, 0, 0, 7); x.fill(); }
  // 提梁
  x.strokeStyle = '#3a2a22'; x.lineWidth = 5; x.beginPath(); x.moveTo(-168, -480); x.bezierCurveTo(-170, -760, 170, -760, 168, -480); x.stroke();
  // 拨杆：灯罩托旁边伸出来的一根小杆（左边），抬灯罩时往下按
  const la = 0.55 - lift * 0.9;                                 // 右边：抬起时杆头朝上，按下去杆头朝下
  x.save(); x.translate(150, -230); x.rotate(la); x.strokeStyle = '#3a2a22'; x.lineWidth = 7; x.beginPath(); x.moveTo(0, 0); x.lineTo(95, 0); x.stroke();
  x.fillStyle = '#3a2a22'; x.beginPath(); x.arc(95, 0, 9, 0, 7); x.fill(); x.restore();
  x.restore();
  return { lever: [LX + 150 + Math.cos(la) * 95, LB - 230 + Math.sin(la) * 95], wick: [LX, LB - 228], globeTop: [LX, LB + gy - 340] };
}

// 火苗（加在最后，自发光）
export function flameShape(x, at, size, t, cool = false) {
  if (size <= 0.01) return;
  const fl = 1 + 0.08 * Math.sin(t * 23) + 0.05 * Math.sin(t * 37 + 1);
  const h = 70 * size * fl, w = 20 * size;
  x.save(); x.translate(at[0], at[1]); x.globalCompositeOperation = 'lighter';
  const g = x.createRadialGradient(0, -h * 0.35, 1, 0, -h * 0.35, h * 0.9);
  g.addColorStop(0, `rgba(255,240,200,${0.95})`); g.addColorStop(0.35, 'rgba(255,170,70,0.75)'); g.addColorStop(1, 'rgba(255,90,20,0)');
  x.fillStyle = g;
  x.beginPath(); x.moveTo(0, -h); x.bezierCurveTo(w * 1.1, -h * 0.55, w * 1.0, -h * 0.05, 0, 0); x.bezierCurveTo(-w * 1.0, -h * 0.05, -w * 1.1, -h * 0.55, 0, -h); x.fill();
  if (cool) { x.fillStyle = 'rgba(90,140,255,0.35)'; x.beginPath(); x.ellipse(0, -h * 0.08, w * 0.6, h * 0.1, 0, 0, 7); x.fill(); }
  x.restore();
}

// ---------------------------------------------------------------- 动作
function action(t) {
  // 右手（火柴）：0～0.2 靠过来，0.2～0.4 一划，1.1～1.7 伸到灯芯，1.95～2.35 收回来甩，2.4 往右出画
  const strikeK = sstep(0.18, 0.38, t);
  const toWick = sstep(1.05, 1.65, t) * (1 - sstep(1.95, 2.4, t));
  const out = sstep(3.6, 4.3, t);
  const shake = t > 2.05 && t < 2.45 ? Math.sin((t - 2.05) * 60) * (1 - (t - 2.05) / 0.4) : 0;
  const matchLit = t > 0.33 && t < 2.2;
  const mFlame = !matchLit ? 0 : t < 0.5 ? 1.6 - (t - 0.33) * 3.5 : 0.85 + 0.1 * Math.sin(t * 19);
  // 左手（火柴盒 → 拨杆）：0～0.9 托着盒子，0.9～1.4 放下去出画；2.5 从左边回来按拨杆，3.0～3.4 往下按，3.9 收走
  const toLever = sstep(2.45, 2.95, t), press = sstep(2.95, 3.4, t);
  const lift = 1 - press;
  // 灯芯：1.8 点着，慢慢长大；灯罩落下以后稳住
  const wick = t < 1.75 ? 0 : sstep(1.75, 2.2, t) * 0.55 + sstep(3.3, 4.2, t) * 0.45;
  return { strikeK, toWick, out, shake, mFlame, toLever, press, lift, wick };
}

export async function renderFrame(ctx, t, W, H) {
  const A = action(t);
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  ctx.drawImage(bg(), 0, 0);
  const lp = lamp(ctx, A.lift, A.wick > 0);
  // ---- 右手：捏着火柴从右下伸进来（划火柴在画外，只听见"嚓"、看见暖光从右边涌进来）
  const px = 25, warm = [1, 1, 1];
  const HAND = { skin: '#efc19c', skinShade: '#cf9672', light: warm, sleeve: '#4b5872', sleeveAt: 4.5, forearm: 22, lineW: 3, shadeA: 0.35 };
  let matchHead = null;
  const offR = [1500, 860];                                  // 画外划火柴的位置（右边）
  if (A.out < 0.99 && t > 0.6) {
    const enter = sstep(0.6, 1.1, t);
    const wickAt = [lp.wick[0] + 14, lp.wick[1] - 22];
    const near = [lp.wick[0] + 170, lp.wick[1] - 40];
    let head = [lerp(lerp(2000, near[0], enter), wickAt[0], A.toWick), lerp(lerp(900, near[1], enter), wickAt[1], A.toWick)];
    // 按拨杆：火柴头（指尖）挪到杆头上面，往下压（杆头跟着下去）
    const lv = lp.lever, onLever = [lv[0] + 6, lv[1] - 16];
    head = [lerp(head[0], onLever[0], A.toLever), lerp(head[1], onLever[1], A.toLever)];
    head = [head[0] + A.out * 900 + A.shake * 16, head[1] + A.out * 260 + A.shake * 5];
    const R = orient(0.15, 0.35, 0.95);
    const probe = drawHand(ctx, { dry: true, side: 1, pose: POSES.pinch, R, at: [0, 0], px });
    const pinch = [(probe.thumbTip[0] + probe.indexTip[0]) / 2, (probe.thumbTip[1] + probe.indexTip[1]) / 2];
    // 火柴棍：从指尖往左上伸出 4.5 厘米
    const ang = Math.PI * 1.08 + A.shake * 0.25, L = 4.5 * px;
    const hold = [head[0] - Math.cos(ang) * L, head[1] - Math.sin(ang) * L];
    ctx.save(); ctx.lineCap = 'round'; ctx.strokeStyle = LINE; ctx.lineWidth = 9; ctx.beginPath(); ctx.moveTo(...hold); ctx.lineTo(...head); ctx.stroke();
    ctx.strokeStyle = '#e8cf98'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(...hold); ctx.lineTo(...head); ctx.stroke();
    ctx.fillStyle = '#2a1a12'; ctx.beginPath(); ctx.ellipse(head[0], head[1], 9, 7, ang, 0, 7); ctx.fill();
    ctx.restore();
    drawHand(ctx, { side: 1, pose: POSES.pinch, R, at: [hold[0] - pinch[0], hold[1] - pinch[1]], px, ...HAND });
    matchHead = head;
  } else if (t <= 0.6) matchHead = offR;
  // ---- 光照：月光的蓝黑底 + 火柴的暖光 + 灯芯的暖光（越来越大），乘到画面上
  const lm = new OffscreenCanvas(RW, RH), lx = lm.getContext('2d');
  lx.fillStyle = 'rgb(22,26,40)'; lx.fillRect(0, 0, RW, RH);
  lx.globalCompositeOperation = 'lighter';
  const glowAt = (p, r, rgb, a) => { const g = lx.createRadialGradient(p[0], p[1], 0, p[0], p[1], r); g.addColorStop(0, `rgba(${rgb},${a})`); g.addColorStop(0.4, `rgba(${rgb},${a * 0.45})`); g.addColorStop(1, `rgba(${rgb},0)`); lx.fillStyle = g; lx.fillRect(p[0] - r, p[1] - r, 2 * r, 2 * r); };
  if (matchHead && A.mFlame > 0) glowAt([matchHead[0], matchHead[1] - 20], (t < 0.6 ? 900 : 560) * Math.min(1.3, A.mFlame), '255,170,90', 0.85 * Math.min(1, A.mFlame));
  if (A.wick > 0) {
    const fl = 1 + 0.06 * Math.sin(t * 13) + 0.04 * Math.sin(t * 29);
    glowAt([lp.wick[0], lp.wick[1] - 60], (500 + 1300 * A.wick) * fl, '255,180,100', 0.55 + 0.45 * A.wick);
  }
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(lm, 0, 0); ctx.restore();
  // ---- 自发光：火苗、灯罩里的光晕
  if (matchHead && t > 0.6) flameShape(ctx, [matchHead[0] - 4, matchHead[1] - 4], A.mFlame, t, true);
  if (A.wick > 0) {
    flameShape(ctx, [lp.wick[0], lp.wick[1] - 4], 0.6 + 0.9 * A.wick, t, true);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createRadialGradient(lp.wick[0], lp.wick[1] - 120, 10, lp.wick[0], lp.wick[1] - 120, 260);
    g.addColorStop(0, `rgba(255,190,110,${0.35 * A.wick})`); g.addColorStop(1, 'rgba(255,150,60,0)');
    ctx.fillStyle = g; ctx.fillRect(lp.wick[0] - 300, lp.wick[1] - 420, 600, 600); ctx.restore();
  }
  // 火柴灭了以后的一缕烟
  if (t > 2.2 && t < 3.6 && matchHead && t > 0.6) {
    ctx.save(); ctx.strokeStyle = `rgba(200,200,210,${0.25 * (1 - (t - 2.2) / 1.4)})`; ctx.lineWidth = 6; ctx.filter = 'blur(3px)';
    ctx.beginPath(); ctx.moveTo(matchHead[0], matchHead[1]); for (let k = 1; k < 8; k++) ctx.lineTo(matchHead[0] + 14 * Math.sin(k * 0.9 + t * 3), matchHead[1] - k * 22); ctx.stroke(); ctx.restore();
  }
  // 暗角
  const v = ctx.createRadialGradient(RW * 0.55, RH * 0.55, RH * 0.3, RW * 0.55, RH * 0.55, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 5;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 7; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
