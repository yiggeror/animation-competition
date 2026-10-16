// S09 · 第 3 场：手电特写（马灯从左边照过来的侧光）。小满从拉开的抽屉里拿出一只旧铁皮手电，大拇指推开关——不亮（2.6）；
// 右手"啪、啪"拍两下（3.1、3.5），再推——亮了（3.9），一道光柱往右边打出去，空气里的灰尘被照亮。时间对上 audio/build.py 的 S09。
import { drawHand, POSES, mixPose, orient, shade } from './hand3d.js';
export const DURATION = 5;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;

// 抽屉（从斜上方看）：木头抽屉盒，里面一堆杂物
let DR = null;
function drawer() {
  if (DR) return DR;
  const c = new OffscreenCanvas(RW, RH), x = c.getContext('2d');
  let seed = 9; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  x.fillStyle = '#5b4632'; x.fillRect(0, 0, RW, RH);                          // 柜子正面（暗）
  x.fillStyle = '#6c533a'; x.fillRect(0, 0, RW, 300);
  // 抽屉：里面的底板（梯形）、两侧板、前板
  const inner = [[260, 620], [1660, 620], [1800, 1000], [120, 1000]];
  x.fillStyle = '#9b7a52'; x.beginPath(); inner.forEach((p, i) => (i ? x.lineTo(...p) : x.moveTo(...p))); x.closePath(); x.fill();
  // 杂物：一卷线、几节电池、剪刀、钥匙、旧火柴盒、皮筋
  const things = [
    (cx, cy) => { x.fillStyle = '#c94f3d'; x.beginPath(); x.ellipse(cx, cy, 60, 34, 0, 0, 7); x.fill(); x.stroke(); x.fillStyle = '#7a2d22'; x.beginPath(); x.ellipse(cx, cy, 16, 9, 0, 0, 7); x.fill(); },
    (cx, cy) => { for (let k = 0; k < 3; k++) { x.fillStyle = '#2f5b8a'; x.beginPath(); x.roundRect(cx + k * 34, cy, 28, 80, 6); x.fill(); x.stroke(); x.fillStyle = '#d8d0b8'; x.fillRect(cx + k * 34 + 8, cy - 6, 12, 8); } },
    (cx, cy) => { x.strokeStyle = '#8a8a8a'; x.lineWidth = 8; x.beginPath(); x.moveTo(cx, cy); x.lineTo(cx + 120, cy - 30); x.moveTo(cx, cy - 30); x.lineTo(cx + 120, cy); x.stroke(); x.strokeStyle = LINE; x.lineWidth = 3; x.beginPath(); x.arc(cx - 14, cy - 34, 18, 0, 7); x.arc(cx - 14, cy + 4, 18, 0, 7); x.stroke(); },
    (cx, cy) => { x.fillStyle = '#c9a046'; x.beginPath(); x.arc(cx, cy, 20, 0, 7); x.fill(); x.stroke(); x.fillRect(cx + 16, cy - 5, 60, 10); },
    (cx, cy) => { x.fillStyle = '#d9c38c'; x.beginPath(); x.rect(cx, cy, 110, 70); x.fill(); x.stroke(); x.fillStyle = '#b23a2a'; x.fillRect(cx + 20, cy + 15, 70, 40); },
  ];
  x.strokeStyle = LINE; x.lineWidth = 3;
  const spots = [[420, 820], [1320, 720], [700, 900], [1500, 880], [980, 700]];
  things.forEach((f, i) => { x.save(); x.strokeStyle = LINE; x.lineWidth = 3; f(...spots[i]); x.restore(); });
  // 两侧板、前板（前板压在最前面）
  x.fillStyle = '#7d5f3e'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(260, 620); x.lineTo(200, 560); x.lineTo(60, 1000); x.lineTo(120, 1000); x.closePath(); x.fill(); x.stroke();
  x.beginPath(); x.moveTo(1660, 620); x.lineTo(1720, 560); x.lineTo(1860, 1000); x.lineTo(1800, 1000); x.closePath(); x.fill(); x.stroke();
  x.beginPath(); x.moveTo(200, 560); x.lineTo(1720, 560); x.lineTo(1660, 620); x.lineTo(260, 620); x.closePath(); x.fillStyle = '#8a6a46'; x.fill(); x.stroke();
  x.fillStyle = '#8a6a46'; x.fillRect(0, 1000, RW, 80); x.beginPath(); x.moveTo(0, 1000); x.lineTo(RW, 1000); x.stroke();
  x.fillStyle = '#c9a046'; x.beginPath(); x.ellipse(960, 1040, 50, 14, 0, 0, 7); x.fill(); x.stroke();    // 铜拉手
  for (let i = 0; i < 30; i++) { x.strokeStyle = `rgba(50,30,15,${0.1 + 0.1 * rnd()})`; x.lineWidth = 2; const y = 1005 + rnd() * 70; x.beginPath(); x.moveTo(0, y); x.lineTo(RW, y + rnd() * 4); x.stroke(); }
  return (DR = c);
}

// 手电：铁皮筒身（红漆）、大一点的灯头（镀铬、玻璃灯面）、筒身上一个推钮开关。c 是筒身中心，ang 方向（灯头朝 +x），s 每厘米多少像素
function torch(x, c, ang, s, on, sw) {
  x.save(); x.translate(c[0], c[1]); x.rotate(ang); x.lineJoin = 'round';
  const bodyL = 13 * s, bodyR = 1.8 * s, headL = 5 * s, headR = 2.8 * s;
  // 尾盖
  x.fillStyle = '#b7b7b0'; x.strokeStyle = LINE; x.lineWidth = 3.5;
  x.beginPath(); x.roundRect(-bodyL / 2 - 1.4 * s, -bodyR * 0.95, 1.6 * s, bodyR * 1.9, 4); x.fill(); x.stroke();
  // 筒身
  const g = x.createLinearGradient(0, -bodyR, 0, bodyR); g.addColorStop(0, '#d65a45'); g.addColorStop(0.35, '#b23a2a'); g.addColorStop(1, '#6e2219');
  x.fillStyle = g; x.beginPath(); x.rect(-bodyL / 2, -bodyR, bodyL, bodyR * 2); x.fill(); x.stroke();
  x.strokeStyle = 'rgba(255,230,210,0.5)'; x.lineWidth = 3; x.beginPath(); x.moveTo(-bodyL / 2 + 6, -bodyR * 0.55); x.lineTo(bodyL / 2 - 6, -bodyR * 0.55); x.stroke();
  // 推钮开关（往前推 = 开）
  x.fillStyle = '#d8d8d0'; x.strokeStyle = LINE; x.lineWidth = 3; x.beginPath(); x.roundRect(-1.2 * s, -bodyR - 0.5 * s, 3.4 * s, 0.7 * s, 3); x.fill(); x.stroke();
  x.fillStyle = '#3a3a3a'; x.beginPath(); x.roundRect(-0.9 * s + sw * 1.4 * s, -bodyR - 0.9 * s, 1.2 * s, 0.7 * s, 3); x.fill(); x.stroke();
  // 灯头：喇叭口，镀铬
  const hx = bodyL / 2;
  const g2 = x.createLinearGradient(0, -headR, 0, headR); g2.addColorStop(0, '#f2f2ee'); g2.addColorStop(0.4, '#b8b8b2'); g2.addColorStop(1, '#6a6a66');
  x.fillStyle = g2; x.strokeStyle = LINE; x.lineWidth = 3.5;
  x.beginPath(); x.moveTo(hx, -bodyR); x.lineTo(hx + headL * 0.55, -headR); x.lineTo(hx + headL, -headR); x.lineTo(hx + headL, headR); x.lineTo(hx + headL * 0.55, headR); x.lineTo(hx, bodyR); x.closePath(); x.fill(); x.stroke();
  // 灯面（侧面看是一条，亮的时候发光）
  x.fillStyle = on ? '#fff6dc' : '#c9d2d6'; x.beginPath(); x.ellipse(hx + headL, 0, 0.5 * s, headR * 0.92, 0, 0, 7); x.fill(); x.stroke();
  x.restore();
  return { lens: [c[0] + Math.cos(ang) * (bodyL / 2 + headL), c[1] + Math.sin(ang) * (bodyL / 2 + headL)], tail: [c[0] - Math.cos(ang) * bodyL / 2, c[1] - Math.sin(ang) * bodyL / 2], sw: [c[0] + Math.cos(ang) * 0.6 * s - Math.sin(ang) * (-bodyR - 0.6 * s), c[1] + Math.sin(ang) * 0.6 * s + Math.cos(ang) * (-bodyR - 0.6 * s)] };
}

function action(t) {
  const up = sstep(0.4, 1.5, t);                         // 从抽屉里拿起来
  const push1 = sstep(2.45, 2.6, t) * (1 - sstep(2.75, 2.9, t));   // 第一次推开关（没亮，又推回去）
  const slap = (t0) => { const u = (t - t0) / 0.18; return u > -1 && u < 1 ? Math.max(0, 1 - Math.abs(u)) : 0; };
  const s1 = slap(3.1), s2 = slap(3.5);
  const handR = sstep(2.85, 3.0, t) * (1 - sstep(3.65, 3.9, t)); // 右手进来拍、拍完收回
  const push2 = sstep(3.8, 3.92, t);
  const on = t >= 3.92;
  const jolt = (t > 3.1 ? Math.exp(-(t - 3.1) * 14) * Math.sin((t - 3.1) * 70) : 0) + (t > 3.5 ? Math.exp(-(t - 3.5) * 14) * Math.sin((t - 3.5) * 70) : 0);
  return { up, sw: Math.max(push1, push2), s1, s2, handR, on, jolt };
}

export async function renderFrame(ctx, t, W, H) {
  const A = action(t);
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  ctx.drawImage(drawer(), 0, 0);
  const s = 34;                                          // 每厘米像素
  const c0 = [900, 860], c1 = [930, 470];
  const c = [lerp(c0[0], c1[0], A.up), lerp(c0[1], c1[1], A.up) + A.jolt * 10];
  const ang = lerp(0.25, -0.08, A.up) + A.jolt * 0.04;
  const HAND = { skin: '#fdc9a7', skinShade: '#e3a283', light: [1, 1, 1], lineW: 3, shadeA: 0.35, forearm: 26, scale: 0.8 };
  // 左手握住筒身（手背朝镜头、拇指压在开关上），从左下伸进来
  const R = orient(0.1, -0.35, -ang * 0.6);                           // 拳头握住横着的手电，手背朝镜头，前臂往下伸出画面
  const pose = POSES.grip;
  const probe = drawHand(ctx, { dry: true, side: -1, pose, R, at: [0, 0], px: s, scale: 0.8 });
  const grip = [c[0] - Math.cos(ang) * 1.0 * s, c[1] - Math.sin(ang) * 1.0 * s];
  const lp = torch(ctx, c, ang, s, A.on, A.sw);
  drawHand(ctx, { side: -1, pose, R, at: [grip[0] - probe.grip[0], grip[1] - probe.grip[1]], px: s, ...HAND });
  // 右手：手掌朝下拍在灯头上
  if (A.handR > 0.01) {
    const hit = Math.max(A.s1, A.s2);
    const Rr = orient(0.05, 0.9, 2.5);                                  // 手掌朝下，从右上方拍下来
    const pr = drawHand(ctx, { dry: true, side: 1, pose: POSES.flat, R: Rr, at: [0, 0], px: s, scale: 0.8 });
    const target = [lp.lens[0] - 3.2 * s, lp.lens[1] - 2.4 * s];
    const raise = (1 - hit) * 110 + (1 - A.handR) * 500;
    drawHand(ctx, { side: 1, pose: POSES.flat, R: Rr, at: [target[0] - pr.palm[0] + (1 - A.handR) * 260, target[1] - pr.palm[1] - raise], px: s, ...HAND });
  }
  // ---- 光：马灯从左边来的暖侧光（左亮右暗），手电亮了以后加一道冷白的光柱
  const lm = new OffscreenCanvas(RW, RH), lx = lm.getContext('2d');
  const g = lx.createLinearGradient(0, 0, RW, 0); g.addColorStop(0, 'rgb(255,190,120)'); g.addColorStop(0.55, 'rgb(150,95,55)'); g.addColorStop(1, 'rgb(40,32,36)');
  lx.fillStyle = g; lx.fillRect(0, 0, RW, RH);
  const fl = 1 + 0.04 * Math.sin(t * 9) + 0.03 * Math.sin(t * 17);
  lx.globalCompositeOperation = 'multiply'; lx.fillStyle = `rgb(${Math.round(255 * Math.min(1, 0.92 * fl))},${Math.round(255 * Math.min(1, 0.92 * fl))},${Math.round(255 * Math.min(1, 0.92 * fl))})`; lx.fillRect(0, 0, RW, RH);
  lx.globalCompositeOperation = 'lighter';
  if (A.on) {
    const k = Math.min(1, (t - 3.92) / 0.08);
    const L = lp.lens, a = ang;
    lx.save(); lx.translate(L[0], L[1]); lx.rotate(a);
    const gb = lx.createLinearGradient(0, 0, 1400, 0); gb.addColorStop(0, `rgba(255,250,230,${0.9 * k})`); gb.addColorStop(1, 'rgba(255,250,230,0)');
    lx.fillStyle = gb; lx.filter = 'blur(10px)'; lx.beginPath(); lx.moveTo(0, -80); lx.lineTo(1400, -380); lx.lineTo(1400, 380); lx.lineTo(0, 80); lx.closePath(); lx.fill();
    lx.restore();
  }
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(lm, 0, 0); ctx.restore();
  if (A.on) {
    const k = Math.min(1, (t - 3.92) / 0.08), L = lp.lens;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    // 光柱里的空气（看得见的光束）和灰尘
    ctx.translate(L[0], L[1]); ctx.rotate(ang);
    const gb = ctx.createLinearGradient(0, 0, 1300, 0); gb.addColorStop(0, `rgba(255,245,220,${0.32 * k})`); gb.addColorStop(1, 'rgba(255,245,220,0)');
    ctx.fillStyle = gb; ctx.filter = 'blur(14px)'; ctx.beginPath(); ctx.moveTo(0, -70); ctx.lineTo(1300, -340); ctx.lineTo(1300, 340); ctx.lineTo(0, 70); ctx.closePath(); ctx.fill();
    ctx.filter = 'none';
    let sd = 7; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 90; i++) { const d = rnd() * 1200, w = 70 + d * 0.22; const yy = (rnd() * 2 - 1) * w, ph = rnd() * 6; ctx.fillStyle = `rgba(255,250,235,${(0.15 + 0.3 * rnd()) * k * (1 - d / 1300)})`; ctx.beginPath(); ctx.arc(d + 14 * Math.sin(t * 0.7 + ph), yy + 10 * Math.sin(t * 0.5 + ph), 1.6 + 2 * rnd(), 0, 7); ctx.fill(); }
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; const gg = ctx.createRadialGradient(L[0], L[1], 2, L[0], L[1], 120); gg.addColorStop(0, `rgba(255,250,235,${0.9 * k})`); gg.addColorStop(1, 'rgba(255,240,210,0)'); ctx.fillStyle = gg; ctx.fillRect(L[0] - 130, L[1] - 130, 260, 260); ctx.restore();
  }
  const v = ctx.createRadialGradient(RW * 0.45, RH * 0.5, RH * 0.3, RW * 0.5, RH * 0.5, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 9;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 7; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
