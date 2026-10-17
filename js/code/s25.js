// S25 · 第 9 场：后台，顺着手电的光看向床单背面（手用合作方画的 anim_25_xiaoman_dog_hands）。小满把手电架在木箱上，"咔"地推开（0.8）——暖黄的床单上多了一块冷白的光斑；
// 她的右手伸进光里，从松松的手慢慢摆成小狗：四指并拢是嘴筒子，拇指竖起来是耳朵，小指往下张开是下巴（2.0～3.4）；
// 床单上跟着长出一只大狗影。狗头歪一歪，张嘴"汪"两下（4.6、5.35，8-bit 的"汪"在 audio/build.py）。
// 镜头在手电后面一点，所以手和影子轮廓一样，影子更大、往外偏一点（视差）。手被手电从镜头这边照亮（冷白），床单被马灯从后台照得暖。
let DOG = null;
async function dogImg() { if (DOG) return DOG; const r = await fetch('/assets/chars/h25_dog.png'); return (DOG = await createImageBitmap(await r.blob())); }
export const DURATION = 6;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const lerp = (a, b, k) => a + (b - a) * k;
const LENS = [960, 1010], SPOT = [1000, 470];

function action(t) {
  const on = t >= 0.8 ? (t < 0.86 ? 0.4 : 1) : 0;                       // 推开关，闪一下亮
  const enter = sstep(1.0, 2.2, t);
  const form = sstep(2.0, 3.4, t);                                      // 摆成小狗
  const bark = (t0) => { const u = (t - t0) / 0.28; return u > 0 && u < 1 ? Math.sin(Math.PI * u) : 0; };
  const jaw = 0.15 + 0.32 * Math.max(bark(4.55), bark(5.3));
  const tilt = sstep(3.6, 4.2, t) * 0.12 * Math.sin((t - 3.6) * 2.2);
  return { on, enter, form, jaw, tilt };
}

export async function renderFrame(ctx, t, W, H) {
  const A = action(t);
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  // ---- 床单背面：马灯从后台照的暖光（上亮下暗），几道褶；左边露一点鹤的牛皮（奶奶拿着）
  const g = ctx.createRadialGradient(700, 150, 80, 800, 300, 1500);
  g.addColorStop(0, '#f4d29a'); g.addColorStop(0.5, '#c8874a'); g.addColorStop(1, '#3a2312');
  ctx.fillStyle = g; ctx.fillRect(0, 0, RW, RH);
  ctx.strokeStyle = 'rgba(120,80,45,0.3)'; ctx.lineWidth = 3;
  for (let i = 0; i < 10; i++) { const x0 = 80 + i * 190 + 25 * Math.sin(i * 2); ctx.beginPath(); ctx.moveTo(x0, 0); ctx.quadraticCurveTo(x0 + 18, 520, x0 - 8, RH); ctx.stroke(); }
  // 冷白的光斑（手电），边缘软
  if (A.on > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const sg = ctx.createRadialGradient(SPOT[0], SPOT[1], 40, SPOT[0], SPOT[1], 560);
    sg.addColorStop(0, `rgba(200,225,255,${0.75 * A.on})`); sg.addColorStop(0.75, `rgba(170,200,240,${0.45 * A.on})`); sg.addColorStop(1, 'rgba(150,180,230,0)');
    ctx.fillStyle = sg; ctx.fillRect(0, 0, RW, RH); ctx.restore();
  }
  // ---- 手（先画在一张单独的画布上，影子用同一个轮廓）
  const hand = new OffscreenCanvas(RW, RH), hx = hand.getContext('2d');
  if (A.enter > 0.01) {
    // 合作方画的狗手势（anim_25）：从左下伸进光里，到位后轻轻点头、汪的时候往前一顶
    const im = await dogImg();
    const nod = 0.05 * Math.max(0, Math.sin((t - 4.55) / 0.28 * Math.PI)) * (t > 4.55 && t < 4.83 ? 1 : 0) + 0.05 * Math.max(0, Math.sin((t - 5.3) / 0.28 * Math.PI)) * (t > 5.3 && t < 5.58 ? 1 : 0);
    const sc = 1.05;
    const at = [lerp(-700, -120, A.enter) + 18 * Math.sin(t * 1.3) * A.enter, lerp(1200, 230, A.enter) + 10 * Math.sin(t * 1.7)];
    hx.save(); hx.translate(at[0] + 1000 * sc, at[1] + 330 * sc); hx.rotate(-0.06 + A.tilt * 0.5 - nod); hx.translate(-1000 * sc, -330 * sc);
    hx.scale(sc, sc); hx.drawImage(im, 0, 0); hx.restore();
    // 手被手电从镜头这边照亮（冷白）；手电没开时只有马灯的暖暗光
    hx.globalCompositeOperation = 'source-atop'; hx.fillStyle = A.on ? 'rgba(200,220,255,0.10)' : 'rgba(40,25,15,0.55)'; hx.fillRect(0, 0, RW, RH); hx.globalCompositeOperation = 'source-over';
  }
  // ---- 狗影：手的轮廓，按手电的位置放大、往外偏，涂成暗色，边缘稍虚；只在光斑里看得见
  if (A.on > 0 && A.enter > 0.01) {
    const sh = new OffscreenCanvas(RW, RH), sx = sh.getContext('2d');
    sx.drawImage(hand, 0, 0); sx.globalCompositeOperation = 'source-in'; sx.fillStyle = 'rgb(40,46,70)'; sx.fillRect(0, 0, RW, RH);
    ctx.save();
    const m = 1.12;
    ctx.translate(LENS[0], LENS[1]); ctx.scale(m, m); ctx.translate(-LENS[0], -LENS[1]); ctx.translate(190, -70);
    ctx.filter = 'blur(5px)'; ctx.globalAlpha = 0.85 * A.on;
    // 影子只落在光斑里：先画影子，再用光斑形状裁一下
    const clip = new OffscreenCanvas(RW, RH), cx = clip.getContext('2d');
    cx.drawImage(sh, 0, 0);
    ctx.drawImage(clip, 0, 0);
    ctx.restore();
    // 光斑外面的影子很淡（马灯的暖光把它冲掉了）：用暖色在光斑外面补回来一点
    ctx.save(); ctx.globalCompositeOperation = 'soft-light';
    const fade = ctx.createRadialGradient(SPOT[0], SPOT[1], 420, SPOT[0], SPOT[1], 700); fade.addColorStop(0, 'rgba(0,0,0,0)'); fade.addColorStop(1, 'rgba(230,160,90,0.9)');
    ctx.fillStyle = fade; ctx.fillRect(0, 0, RW, RH); ctx.restore();
  }
  ctx.drawImage(hand, 0, 0);
  // ---- 前景：木箱的一角和手电的尾巴（镜头就在它后面）
  ctx.fillStyle = '#5e3a20'; ctx.strokeStyle = LINE; ctx.lineWidth = 5;
  ctx.beginPath(); ctx.moveTo(560, RH); ctx.lineTo(700, 960); ctx.lineTo(1260, 960); ctx.lineTo(1400, RH); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#7a4c2a'; ctx.beginPath(); ctx.moveTo(700, 960); ctx.lineTo(1260, 960); ctx.lineTo(1230, 940); ctx.lineTo(730, 940); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#b23a2a'; ctx.beginPath(); ctx.ellipse(LENS[0], LENS[1] + 10, 70, 60, 0, 0, 7); ctx.fill(); ctx.stroke();      // 手电的尾巴
  ctx.fillStyle = '#b7b7b0'; ctx.beginPath(); ctx.ellipse(LENS[0], LENS[1] + 10, 46, 40, 0, 0, 7); ctx.fill(); ctx.stroke();
  // 光束里的灰尘
  if (A.on > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    let sd = 4; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 70; i++) {
      const u = rnd(), a = (rnd() - 0.5) * 0.9, d = 120 + u * 620;
      const x0 = LENS[0] + Math.sin(a) * d * 0.9 + 12 * Math.sin(t * 0.6 + i), y0 = LENS[1] - Math.cos(a) * d * 0.85 + 8 * Math.sin(t * 0.4 + i * 2);
      ctx.fillStyle = `rgba(220,235,255,${(0.12 + 0.2 * rnd()) * A.on})`; ctx.beginPath(); ctx.arc(x0, y0, 1.5 + 2.2 * rnd(), 0, 7); ctx.fill();
    }
    ctx.restore();
  }
  const v = ctx.createRadialGradient(RW * 0.5, RH * 0.45, RH * 0.3, RW * 0.5, RH * 0.5, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 25;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 7; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
