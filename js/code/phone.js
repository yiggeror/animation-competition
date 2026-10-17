// 手机特写（S02、S05）：俯拍小满横握的手机，屏幕里是原创的跑酷小游戏，右上角电量。
// 设计坐标 1920×1080，渲染时按画布宽度缩放。画法和人物图一致：深棕轮廓线 + 平涂，暗处按光照压色。
// 光照：S02 日光灯从头顶照下来（竹席亮、手机和手在竹席上有一块软影子）；S05 停了电，只有屏幕自己发光，手指成了暗剪影、边上一圈屏幕的冷光。
export const RW = 1920, RH = 1080;
export const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;
const LINE = '#4a2e1f';

// ---------------------------------------------------------------- 颜色：sRGB ↔ 线性，按光照压色
const hex2rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const s2l = (v) => Math.pow(v / 255, 2.2), l2s = (v) => Math.round(255 * Math.pow(Math.max(0, Math.min(1, v)), 1 / 2.2));
export function lit(hex, k) { const c = hex2rgb(hex); return `rgb(${c.map((v, i) => l2s(s2l(v) * k[i])).join(',')})`; }

// ---------------------------------------------------------------- 竹席：一条条竹篾，每隔一段一道编线，竹节
let MAT = null;
export function mat() {
  if (MAT) return MAT;
  const W = 2600, H = 1700, c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  x.fillStyle = '#b8955a'; x.fillRect(0, 0, W, H);
  const sw = 34;
  for (let y = -sw, i = 0; y < H + sw; y += sw, i++) {
    const v = 0.9 + 0.2 * rnd();
    const base = [208 * v, 172 * v, 108 * v].map(Math.round);
    const g = x.createLinearGradient(0, y, 0, y + sw);
    g.addColorStop(0, `rgb(${base.map((b) => Math.min(255, b + 18)).join(',')})`);
    g.addColorStop(0.55, `rgb(${base.join(',')})`);
    g.addColorStop(1, `rgb(${base.map((b) => b - 30).join(',')})`);
    x.fillStyle = g; x.fillRect(0, y + 2, W, sw - 4);
    // 竹节：一道浅横纹 + 一点暗
    for (let k = 0; k < 6; k++) {
      const nx = rnd() * W;
      x.fillStyle = `rgba(120,85,40,0.35)`; x.fillRect(nx, y + 3, 5, sw - 6);
      x.fillStyle = `rgba(255,235,190,0.25)`; x.fillRect(nx + 5, y + 3, 3, sw - 6);
    }
    // 篾面细纹
    x.strokeStyle = 'rgba(110,80,40,0.12)'; x.lineWidth = 1;
    for (let k = 0; k < 3; k++) { const yy = y + 6 + rnd() * (sw - 12); x.beginPath(); x.moveTo(0, yy); x.lineTo(W, yy + rnd() * 4 - 2); x.stroke(); }
  }
  // 编线：竖着的细麻线，每隔 150 像素一道，在篾条上一上一下
  for (let xx = 60; xx < W; xx += 150) {
    for (let y = 0, i = 0; y < H; y += sw, i++) {
      if (i % 2) continue;
      x.fillStyle = 'rgba(90,64,34,0.55)'; x.fillRect(xx - 4, y + 1, 8, sw - 2);
      x.fillStyle = 'rgba(230,205,160,0.5)'; x.fillRect(xx - 3, y + 2, 2, sw - 4);
    }
  }
  return (MAT = c);
}

// ---------------------------------------------------------------- 手机
export const PW = 1180, PH = 580, PR = 78, BZ = 20;
export const SX0 = -PW / 2 + BZ, SY0 = -PH / 2 + BZ;
export let SW = PW - 2 * BZ, SH = PH - 2 * BZ;
export let DPAD = [150, SH - 140], JUMP = [SW - 150, SH - 140];   // 屏幕坐标（左上角为原点）
// 换成合作方画的手机图时，屏幕尺寸和两个按键的位置按图来（按键在两个拇指下面）
export function setScreen(w, h, dpad, jump) { SW = w; SH = h; DPAD = dpad; JUMP = jump; }
export { drawGame, drawStatus };

// 跑酷小游戏：小人跑、跳过木箱、吃金币。g = { t, jumps:[按下的时刻], mash（狂按程度 0..1） }
const V = 430, RX = 380;
function jumpY(t, jumps) {
  let y = 0;
  for (const j of jumps) { const u = (t - j) / 0.55; if (u > 0 && u < 1) y = Math.max(y, 4 * u * (1 - u)); }
  return y * 150;
}
function drawGame(x, g) {
  const t = g.t, gy = SH * 0.76;
  // 天
  const sky = x.createLinearGradient(0, 0, 0, gy); sky.addColorStop(0, '#5cc4ff'); sky.addColorStop(1, '#d6f2ff');
  x.fillStyle = sky; x.fillRect(0, 0, SW, SH);
  x.fillStyle = '#fff2a8'; x.beginPath(); x.arc(SW * 0.8, 110, 46, 0, 7); x.fill();
  // 云（慢）
  x.fillStyle = 'rgba(255,255,255,0.92)';
  for (let k = 0; k < 4; k++) {
    const cx = ((k * 380 - t * V * 0.15) % 1520 + 1520) % 1520 - 200, cy = 90 + (k % 2) * 60;
    for (const [dx, dy, r] of [[0, 0, 34], [36, -14, 40], [76, 0, 30]]) { x.beginPath(); x.arc(cx + dx, cy + dy, r, 0, 7); x.fill(); }
  }
  // 远山（中速）
  x.fillStyle = '#8fd48a'; x.beginPath(); x.moveTo(0, gy);
  for (let sx = 0; sx <= SW; sx += 20) { const w = sx + t * V * 0.4; x.lineTo(sx, gy - 70 - 40 * Math.sin(w * 0.006) - 25 * Math.sin(w * 0.017)); }
  x.lineTo(SW, gy); x.fill();
  // 地面
  x.fillStyle = '#c98a4e'; x.fillRect(0, gy, SW, SH - gy);
  x.fillStyle = '#5db64e'; x.fillRect(0, gy, SW, 22);
  x.fillStyle = 'rgba(120,70,30,0.35)';
  for (let k = 0; k < 14; k++) { const sx = ((k * 90 - t * V) % 1260 + 1260) % 1260 - 60; x.fillRect(sx, gy + 46, 40, 8); x.fillRect(sx + 45, gy + 86, 30, 8); }
  // 障碍和金币：每次起跳时正好有一只木箱到小人脚下
  for (const j of g.jumps) {
    const bx = RX + V * (j + 0.27 - t);
    if (bx < -100 || bx > SW + 100) continue;
    x.fillStyle = '#b8743a'; x.strokeStyle = '#5a3417'; x.lineWidth = 5;
    x.beginPath(); x.roundRect(bx - 38, gy - 76, 76, 76, 6); x.fill(); x.stroke();
    x.beginPath(); x.moveTo(bx - 38, gy - 76); x.lineTo(bx + 38, gy); x.moveTo(bx + 38, gy - 76); x.lineTo(bx - 38, gy); x.stroke();
    for (let k = -1; k <= 1; k++) {
      const cx = bx + k * 52, cy = gy - 150 - (k ? 0 : 40);
      const got = cx < RX + 10;
      if (got) { if (cx > RX - 70) { x.strokeStyle = `rgba(255,240,120,${(cx - RX + 70) / 80})`; x.lineWidth = 4; for (let a = 0; a < 6; a++) { const an = a * 1.05; x.beginPath(); x.moveTo(RX + 20 + Math.cos(an) * 20, gy - 160 + Math.sin(an) * 20); x.lineTo(RX + 20 + Math.cos(an) * 34, gy - 160 + Math.sin(an) * 34); x.stroke(); } } continue; }
      x.fillStyle = '#ffd23a'; x.strokeStyle = '#b07a00'; x.lineWidth = 4;
      x.beginPath(); x.ellipse(cx, cy, 20 * Math.abs(Math.cos(t * 5 + k)) + 4, 22, 0, 0, 7); x.fill(); x.stroke();
    }
  }
  // 小人：圆身子、红围巾、两条小腿交替
  const jy = jumpY(t, g.jumps), ph = t * 14, air = jy > 2;
  const px = RX, py = gy - 52 - jy;
  x.save(); x.translate(px, py);
  x.strokeStyle = '#3a2410'; x.lineWidth = 9; x.lineCap = 'round';
  const l1 = air ? 0.6 : Math.sin(ph) * 0.7, l2 = air ? -0.4 : -Math.sin(ph) * 0.7;
  for (const a of [l1, l2]) { x.beginPath(); x.moveTo(0, 30); x.lineTo(Math.sin(a) * 30, 30 + Math.cos(a) * 26); x.stroke(); }
  x.fillStyle = '#ff8a3d'; x.strokeStyle = '#7a3a10'; x.lineWidth = 5;
  x.beginPath(); x.arc(0, 0, 42, 0, 7); x.fill(); x.stroke();
  x.fillStyle = '#e8322e'; x.beginPath(); x.moveTo(-30, 18); x.quadraticCurveTo(-70, 10 + Math.sin(ph) * 8, -96, 24 + Math.sin(ph * 1.3) * 10); x.lineTo(-90, 36); x.quadraticCurveTo(-60, 30, -26, 30); x.fill();
  x.fillStyle = '#fff'; x.beginPath(); x.arc(16, -8, 13, 0, 7); x.fill();
  x.fillStyle = '#222'; x.beginPath(); x.arc(20, -8, 6, 0, 7); x.fill();
  x.restore();
  // 分数（左上），暂停键（右上，避开状态栏）
  const score = 1280 + 30 * g.jumps.filter((j) => t > j + 0.3).length;
  x.fillStyle = '#ffd23a'; x.strokeStyle = '#b07a00'; x.lineWidth = 4; x.beginPath(); x.arc(56, 96, 18, 0, 7); x.fill(); x.stroke();
  x.font = 'bold 40px "Noto Sans SC"'; x.textBaseline = 'middle'; x.lineWidth = 7; x.strokeStyle = 'rgba(0,0,0,0.35)'; x.fillStyle = '#fff';
  x.strokeText(String(score), 86, 98); x.fillText(String(score), 86, 98);
  // 虚拟按键：左边方向键，右边起跳键（被按下时变亮、缩一点）
  const btn = (c, r, pressed, icon) => {
    x.save(); x.translate(c[0], c[1]); const s = pressed ? 0.92 : 1; x.scale(s, s);
    x.fillStyle = pressed ? 'rgba(255,255,255,0.55)' : 'rgba(255,255,255,0.28)'; x.strokeStyle = 'rgba(255,255,255,0.8)'; x.lineWidth = 5;
    x.beginPath(); x.arc(0, 0, r, 0, 7); x.fill(); x.stroke(); icon(); x.restore();
  };
  btn(DPAD, 92, g.dpadPressed, () => {
    x.fillStyle = 'rgba(255,255,255,0.9)';
    for (const d of [-1, 1]) { x.beginPath(); x.moveTo(d * 62, 0); x.lineTo(d * 30, -24); x.lineTo(d * 30, 24); x.fill(); }
  });
  btn(JUMP, 92, g.jumpPressed, () => {
    x.fillStyle = 'rgba(255,255,255,0.9)'; x.beginPath(); x.moveTo(0, -42); x.lineTo(34, 4); x.lineTo(12, 4); x.lineTo(12, 36); x.lineTo(-12, 36); x.lineTo(-12, 4); x.lineTo(-34, 4); x.fill();
  });
}

// 状态栏：时间、信号、电量（百分比 + 电池图标 + 充电闪电）。字放大了，镜头推近时一眼能读
function drawStatus(x, st) {
  x.fillStyle = 'rgba(0,0,0,0.22)'; x.fillRect(0, 0, SW, 62);
  x.font = '600 36px "Noto Sans SC"'; x.textBaseline = 'middle'; x.fillStyle = '#fff';
  x.fillText('21:47', 110, 32);
  // 信号
  for (let k = 0; k < 4; k++) { x.fillStyle = k < 3 ? '#fff' : 'rgba(255,255,255,0.4)'; x.fillRect(SW - 330 + k * 14, 44 - k * 8 - 8, 9, 8 + k * 8); }
  // 电池
  const bx = SW - 132, by = 15, bw = 76, bh = 36;
  const red = st.level <= 2, blinkOn = !st.blink || Math.floor(st.t * 3) % 2 === 0;
  x.strokeStyle = red && st.level <= 1 && blinkOn ? '#ff4b3e' : '#fff'; x.lineWidth = 4;
  x.beginPath(); x.roundRect(bx, by, bw, bh, 8); x.stroke();
  x.fillStyle = x.strokeStyle; x.fillRect(bx + bw + 3, by + 11, 6, 14);
  x.fillStyle = '#ff4b3e'; x.fillRect(bx + 5, by + 5, Math.max(4, (bw - 10) * st.level / 100), bh - 10);
  if (st.bolt > 0) {
    x.save(); x.translate(bx + bw / 2, by + bh / 2); x.scale(st.bolt, st.bolt);
    x.fillStyle = '#fff'; x.strokeStyle = '#2a2a2a'; x.lineWidth = 3;
    x.beginPath(); x.moveTo(4, -17); x.lineTo(-10, 3); x.lineTo(-1, 3); x.lineTo(-5, 17); x.lineTo(10, -4); x.lineTo(1, -4); x.closePath(); x.stroke(); x.fill();
    x.restore();
  }
  x.font = '700 40px "Noto Sans SC"'; x.textAlign = 'right';
  x.fillStyle = st.level <= 1 ? (blinkOn ? '#ff5a4a' : '#fff') : '#fff';
  x.fillText(`${st.level}%`, bx - 14, 34); x.textAlign = 'left';
}

// ---------------------------------------------------------------- 手
// 横握手机，从上往下看：手掌和四指在手机背后（托着），只有露出机身外的那一截看得见；拇指从机身下角越过边框，压在屏幕的按键上。
// 拇指：掌根 R0 → 掌指关节 M → 指间关节 J（两节反向运动学）→ 指尖 T，沿骨架做平滑曲线，往两边偏出轮廓，指尖圆头，指甲朝上。
function ik2(M, T, l1, l2, bendSign) {
  const dx = T[0] - M[0], dy = T[1] - M[1], d = Math.min(Math.hypot(dx, dy), l1 + l2 - 1e-3);
  const a = Math.atan2(dy, dx), c = Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))));
  return [M[0] + Math.cos(a + bendSign * c) * l1, M[1] + Math.sin(a + bendSign * c) * l1];
}
// 过一串点的平滑曲线（Catmull-Rom），宽度在点之间线性变；返回轮廓和取样函数
function limbPath(pts, widths) {
  const n = pts.length - 1;
  const C = (i) => pts[Math.max(0, Math.min(n, i))];
  const P = (u) => {
    const f = Math.min(n - 1e-6, Math.max(0, u * n)), i = Math.floor(f), s = f - i;
    const p0 = C(i - 1), p1 = C(i), p2 = C(i + 1), p3 = C(i + 2);
    const q = (k) => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * s + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * s * s + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * s * s * s);
    return [q(0), q(1)];
  };
  const Wd = (u) => { const f = Math.min(n - 1e-6, Math.max(0, u * n)), i = Math.floor(f); return lerp(widths[i], widths[i + 1], f - i); };
  const N = 40, L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, p = P(u), q = P(Math.min(1, u + 0.005)), r = P(Math.max(0, u - 0.005));
    const tx = q[0] - r[0], ty = q[1] - r[1], tl = Math.hypot(tx, ty) || 1, w = Wd(u) / 2;
    L.push([p[0] - ty / tl * w, p[1] + tx / tl * w]); R.push([p[0] + ty / tl * w, p[1] - tx / tl * w]);
  }
  const end = P(1), pre = P(0.98), dir = Math.atan2(end[1] - pre[1], end[0] - pre[0]), we = widths[n] / 2;
  // path 是封闭的（填色、裁剪用）；outline 不封口（描边用：根部接在手掌上，不画那道横线）
  const build = (close) => {
    const path = new Path2D(); path.moveTo(...L[0]);
    for (const p of L) path.lineTo(...p);
    path.arc(end[0], end[1], we, dir + Math.PI / 2, dir - Math.PI / 2, true);
    for (let i = R.length - 1; i >= 0; i--) path.lineTo(...R[i]);
    if (close) path.closePath();
    return path;
  };
  return { path: build(true), outline: build(false), P, Wd, dir, end };
}

const SKIN = '#f7c6a3', SKIN_SH = '#e3a37e', NAIL = '#f9ddd2';
// 手机背后的部分：手掌、手腕（伸出画面），沿着机身两头露出来的食指和中指
function drawHandBack(x, side, Lt) {
  const fill = (h) => lit(h, Lt.skin), ex = side * PW / 2, sx = (v) => ex + side * v;
  x.save(); x.lineJoin = 'round'; x.lineCap = 'round';
  // 食指、中指：从手掌往上，贴着机身的这一头，指头在机身中段（大半被机身挡住）
  for (const [y0, y1, w, out] of [[PH / 2 - 10, -PH / 2 + 95, 74, 34], [PH / 2 + 20, -PH / 2 + 230, 70, 22]]) {
    const f = limbPath([[sx(out + 30), y0], [sx(out + 8), (y0 + y1) / 2], [sx(out - 2), y1]], [w + 6, w, w - 6]);
    x.fillStyle = fill(SKIN); x.fill(f.path);
    x.save(); x.clip(f.path); x.fillStyle = fill(SKIN_SH); x.globalAlpha = 0.6;
    x.fillRect(sx(out + 18) - (side > 0 ? 0 : 60), y1 - 60, 60, y0 - y1 + 120); x.restore();
    x.strokeStyle = LINE; x.lineWidth = 5; x.stroke(f.outline);
  }
  // 手掌 + 手腕：在机身下角的外面，往外下方伸出画面
  const palm = new Path2D();
  palm.moveTo(sx(-150), PH / 2 - 20);
  palm.bezierCurveTo(sx(-60), PH / 2 - 120, sx(90), PH / 2 - 120, sx(130), PH / 2 - 20);
  palm.bezierCurveTo(sx(170), PH / 2 + 110, sx(250), PH / 2 + 300, sx(330), PH / 2 + 560);
  palm.lineTo(sx(-110), PH / 2 + 600);
  palm.bezierCurveTo(sx(-120), PH / 2 + 380, sx(-190), PH / 2 + 160, sx(-150), PH / 2 - 20);
  palm.closePath();
  x.fillStyle = fill(SKIN); x.fill(palm);
  x.save(); x.clip(palm); x.fillStyle = fill(SKIN_SH); x.globalAlpha = 0.55;
  x.beginPath(); x.ellipse(sx(210), PH / 2 + 220, 90, 420, side * -0.4, 0, 7); x.fill(); x.restore();
  x.strokeStyle = LINE; x.lineWidth = 5; x.stroke(palm);
  x.restore();
}
// 机身前面的拇指（连着掌根的大鱼际），tip 是指肚压的位置；lift 0..1 抬起（离镜头近，稍大，影子错开）
function drawThumb(x, side, tip, lift, Lt) {
  const k = Lt.skin, fill = (h) => lit(h, k), ex = side * PW / 2;
  x.save(); x.lineJoin = 'round'; x.lineCap = 'round';
  const s = 1 + 0.04 * lift;
  const R0 = [ex + side * 70, PH / 2 + 250], M = [ex + side * 40, PH / 2 + 60];
  // 指肚在指尖往回 50 像素；抬起时往外、往下一点
  const tgt = [tip[0] + side * 10 * lift, tip[1] + 18 * lift];
  const d0 = Math.atan2(tgt[1] - M[1], tgt[0] - M[0]);
  const T = [M[0] + (tgt[0] + Math.cos(d0) * 50 - M[0]) * s, M[1] + (tgt[1] + Math.sin(d0) * 50 - M[1]) * s];
  const J = ik2(M, T, 205 * s, 165 * s, side > 0 ? -1 : 1);
  const th = limbPath([R0, M, J, T], [210 * s, 128 * s, 108 * s, 94 * s]);
  if (Lt.thumbShadow > 0 && lift > 0.05) {
    x.save(); x.translate(12 + 22 * lift, 24 + 40 * lift); x.filter = `blur(${10 + 16 * lift}px)`;
    x.fillStyle = `rgba(0,0,0,${0.22 + 0.18 * lift})`; x.fill(th.path); x.restore();
  }
  x.fillStyle = fill(SKIN); x.fill(th.path);
  // 体积：靠外（远离手机中心）的一侧压暗
  x.save(); x.clip(th.path); x.strokeStyle = fill(SKIN_SH); x.globalAlpha = 0.6; x.lineWidth = 46; x.beginPath();
  for (let i = 0; i <= 30; i++) {
    const u = i / 30, p = th.P(u), q = th.P(Math.min(1, u + 0.01)), a = Math.atan2(q[1] - p[1], q[0] - p[0]) + (side > 0 ? Math.PI / 2 : -Math.PI / 2);
    const o = th.Wd(u) / 2; const pt = [p[0] + Math.cos(a) * o, p[1] + Math.sin(a) * o]; i ? x.lineTo(...pt) : x.moveTo(...pt);
  }
  x.stroke(); x.restore();
  if (Lt.rim > 0) { x.save(); x.clip(th.path); x.strokeStyle = `rgba(170,210,255,${Lt.rim})`; x.lineWidth = 18; x.filter = 'blur(5px)'; x.stroke(th.outline); x.restore(); }
  x.strokeStyle = LINE; x.lineWidth = 5; x.stroke(th.outline);
  // 指间关节的两道褶（在 J 附近，横着拇指）
  const uj = 2 / 3, pj = th.P(uj), pj2 = th.P(uj + 0.01), aj = Math.atan2(pj2[1] - pj[1], pj2[0] - pj[0]);
  x.lineWidth = 3;
  for (const [o, len] of [[-12, 26], [4, 20]]) {
    const cx = pj[0] + Math.cos(aj) * o, cy = pj[1] + Math.sin(aj) * o, nx = Math.cos(aj + Math.PI / 2), ny = Math.sin(aj + Math.PI / 2);
    x.beginPath(); x.moveTo(cx + nx * len, cy + ny * len); x.quadraticCurveTo(cx + Math.cos(aj) * 7, cy + Math.sin(aj) * 7, cx - nx * len, cy - ny * len); x.stroke();
  }
  // 掌指关节处的一道浅纹（拇指根和大鱼际的分界）
  const pm = th.P(1 / 3), pm2 = th.P(1 / 3 + 0.01), am = Math.atan2(pm2[1] - pm[1], pm2[0] - pm[0]);
  x.globalAlpha = 0.6; x.beginPath(); x.moveTo(pm[0] + Math.cos(am + 1.9) * 50, pm[1] + Math.sin(am + 1.9) * 50);
  x.quadraticCurveTo(pm[0] + Math.cos(am) * 14, pm[1] + Math.sin(am) * 14, pm[0] + Math.cos(am - 1.9) * 30, pm[1] + Math.sin(am - 1.9) * 30); x.stroke(); x.globalAlpha = 1;
  // 指甲
  const nc = th.P(0.93), nd = th.dir;
  x.save(); x.translate(nc[0], nc[1]); x.rotate(nd);
  x.fillStyle = fill(NAIL); x.beginPath(); x.roundRect(-30, -28, 62, 56, [8, 26, 26, 8]); x.fill();
  x.strokeStyle = LINE; x.lineWidth = 3; x.stroke();
  x.globalAlpha = 0.5 * Math.min(1, k[0]); x.fillStyle = '#fff'; x.beginPath(); x.ellipse(6, -11, 15, 5, 0, 0, 7); x.fill();
  x.restore();
  x.restore();
}

// ---------------------------------------------------------------- 一帧
// st = { t, cam:{x,y,zoom}, phone:{x,y,rot}, game:{...}, status:{level,bolt,blink}, screenOn（0..1）, light:'fluor'|'dark',
//        hands:{ L:{tip,lift}, R:{tip,lift} } }
export function renderPhone(ctx, W, H, st) {
  const dark = st.light === 'dark';
  const scr = st.screenOn;
  // 环境光：日光灯（偏冷的白）/ 停电（很暗的蓝，月光）
  const amb = dark ? [0.05, 0.06, 0.095] : [0.92, 0.95, 1.0];
  const Lt = {
    skin: dark ? [0.1 + 0.16 * scr, 0.11 + 0.2 * scr, 0.16 + 0.3 * scr] : [0.98, 0.99, 1.0],
    rim: dark ? 0.75 * scr : 0,
    thumbShadow: dark ? 0 : 1,
  };
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const k = W / RW;
  ctx.scale(k, k);
  const cam = st.cam;
  ctx.translate(RW / 2, RH / 2); ctx.scale(cam.zoom, cam.zoom); ctx.translate(-cam.x, -cam.y);
  // 竹席（离手机近，略虚一点）
  ctx.save(); ctx.filter = 'blur(2px)'; ctx.drawImage(mat(), -340, -310); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = `rgb(${amb.map((v) => l2s(v)).join(',')})`; ctx.fillRect(-400, -400, 2800, 1900); ctx.restore();
  const P = st.phone;
  ctx.save(); ctx.translate(P.x, P.y); ctx.rotate(P.rot);
  // 竹席上的影子（日光灯在头顶）/ 屏幕往外溢的冷光（停电）
  if (!dark) {
    ctx.save(); ctx.translate(26, 40); ctx.filter = 'blur(38px)'; ctx.fillStyle = 'rgba(40,25,10,0.45)';
    ctx.beginPath(); ctx.roundRect(-PW / 2 - 30, -PH / 2 - 20, PW + 60, PH + 40, PR); ctx.fill();
    ctx.beginPath(); ctx.ellipse(-PW / 2 - 40, PH / 2 + 200, 230, 420, 0.4, 0, 7); ctx.ellipse(PW / 2 + 40, PH / 2 + 200, 230, 420, -0.4, 0, 7); ctx.fill();
    ctx.restore();
  } else if (scr > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createRadialGradient(0, 0, PH * 0.3, 0, 0, PW * 0.95);
    g.addColorStop(0, `rgba(70,110,160,${0.55 * scr})`); g.addColorStop(0.5, `rgba(35,60,95,${0.3 * scr})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(-PW * 1.2, -PW * 1.2, PW * 2.4, PW * 2.4); ctx.restore();
  }
  // 充电线：从左头插进去，弯一下伸出画面
  ctx.save(); ctx.lineCap = 'round';
  const cab = new Path2D(); cab.moveTo(-PW / 2 - 40, 0); cab.bezierCurveTo(-PW / 2 - 220, 10, -PW / 2 - 200, 300, -PW / 2 - 420, 520);
  ctx.strokeStyle = LINE; ctx.lineWidth = 26; ctx.stroke(cab);
  ctx.strokeStyle = lit('#f2f2ee', amb.map((v, i) => v + (dark ? [0.1, 0.16, 0.26][i] * scr : 0))); ctx.lineWidth = 18; ctx.stroke(cab);
  ctx.fillStyle = lit('#e8e8e4', amb.map((v, i) => v + (dark ? 0.2 * scr : 0))); ctx.strokeStyle = LINE; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.roundRect(-PW / 2 - 70, -20, 64, 40, 8); ctx.fill(); ctx.stroke();
  ctx.restore();
  // 手机背后的手掌、手指
  drawHandBack(ctx, -1, Lt); drawHandBack(ctx, 1, Lt);
  // 机身
  ctx.fillStyle = lit('#2b2d33', dark ? [0.25 + 0.4 * scr, 0.3 + 0.45 * scr, 0.4 + 0.6 * scr] : amb);
  ctx.beginPath(); ctx.roundRect(-PW / 2, -PH / 2, PW, PH, PR); ctx.fill();
  ctx.strokeStyle = LINE; ctx.lineWidth = 6; ctx.stroke();
  // 边框高光
  ctx.strokeStyle = dark ? `rgba(150,190,240,${0.35 * scr})` : 'rgba(255,255,255,0.35)'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.roundRect(-PW / 2 + 5, -PH / 2 + 5, PW - 10, PH - 10, PR - 5); ctx.stroke();
  // 屏幕
  ctx.save(); ctx.beginPath(); ctx.roundRect(SX0, SY0, SW, SH, PR - BZ); ctx.clip();
  ctx.translate(SX0, SY0);
  if (scr > 0.001) {
    ctx.save(); ctx.globalAlpha = 1; drawGame(ctx, st.game); drawStatus(ctx, { ...st.status, t: st.t }); ctx.restore();
    if (scr < 1) { ctx.fillStyle = `rgba(0,0,0,${1 - scr})`; ctx.fillRect(0, 0, SW, SH); }
  } else {
    ctx.fillStyle = '#050608'; ctx.fillRect(0, 0, SW, SH);
  }
  // 前摄像头的挖孔（横屏在左边）
  ctx.fillStyle = '#0a0a0c'; ctx.beginPath(); ctx.arc(34, SH / 2, 13, 0, 7); ctx.fill();
  // 玻璃反光：一道斜的淡白（屏幕黑了以后更显眼，反出一点月光）
  const gl = ctx.createLinearGradient(SW * 0.25, 0, SW * 0.55, SH);
  const ga = scr > 0.001 ? (dark ? 0.03 : 0.07) : 0.07;
  gl.addColorStop(0, 'rgba(255,255,255,0)'); gl.addColorStop(0.45, `rgba(220,235,255,${ga})`); gl.addColorStop(0.55, `rgba(220,235,255,${ga * 1.3})`); gl.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gl; ctx.fillRect(0, 0, SW, SH);
  ctx.restore();
  // 手（屏幕坐标 → 手机坐标）
  const toP = (p) => [SX0 + p[0], SY0 + p[1]];
  drawThumb(ctx, -1, toP(st.hands.L.tip), st.hands.L.lift, Lt);
  drawThumb(ctx, 1, toP(st.hands.R.tip), st.hands.R.lift, Lt);
  ctx.restore();
  ctx.restore();
  // 暗角、颗粒
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 0.95);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${dark ? 0.6 : 0.3})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let seed = Math.floor(st.t * 24) * 7919 + 17;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (rnd() - 0.5) * 6; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}

// 拇指按键的动作：presses 是按下的时刻；按下 0.12 秒，抬起后悬着
export function thumbAt(t, presses, base, o = {}) {
  let lift = 1, dx = 0, dy = 0;
  for (const p of presses) {
    const u = t - p;
    if (u > -0.12 && u < 0.22) { const d = u < 0 ? (u + 0.12) / 0.12 : u < 0.1 ? 1 : 1 - (u - 0.1) / 0.12; lift = Math.min(lift, 1 - d); }
  }
  lift = 0.25 + 0.75 * lift * (o.hover ?? 1);
  if (o.wiggle) { dx = o.wiggle * Math.sin(t * (o.wf ?? 3)); }
  return { tip: [base[0] + dx + (o.ox ?? 0), base[1] + dy + (o.oy ?? 0)], lift: Math.max(0, Math.min(1, lift)), pressed: lift < 0.5 };
}
