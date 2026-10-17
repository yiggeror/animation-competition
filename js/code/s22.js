// S22 · 第 8 场：后台特写——手把手。用合作方画的 anim_22_hands_together（奶奶的手从后面包住小满握签子的手，两双手各握一根签子）。
// 开头小满的手还在抖，被奶奶稳住（0～1.3 秒）——慢一点；然后两双手一起，一秒一步，稳稳地往上送（1.4、2.4、3.4、4.4，对上低音拨弦），
// 背景里床单背面的乌龟（虚）跟着一步步爬起来。签子按图里原来的方向延长出画面（图里杆轴 y = 403 − 0.115x、y = 846 − 0.115x），不拐弯。
import { makeTurtle, turtlePose } from '../lamp/turtle.js';
import { drawPuppet } from '../puppet.js';
export const DURATION = 5;
const RW = 1920, RH = 1080, LINE = '#4a2e1f';
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
let IMG = null, TURTLE = null;
async function img() { if (IMG) return IMG; const r = await fetch('/assets/chars/h22_together.png'); return (IMG = await createImageBitmap(await r.blob())); }
const AXES = [[403, -0.115], [846, -0.115]];          // 图里两根签子的轴：y = a + b·x（原图像素，抠图没有裁边）

function action(t) {
  const shake = (1 - sstep(0.3, 1.3, t)) * (Math.sin(t * 29) * 0.6 + Math.sin(t * 43) * 0.4);
  let step = 0;
  for (let k = 0; k < 4; k++) step += sstep(1.4 + k, 1.72 + k, t);
  return { shake, step };
}

export async function renderFrame(ctx, t, W, H) {
  const im = await img(); TURTLE ||= makeTurtle();
  const A = action(t);
  const scene = new OffscreenCanvas(RW, RH), x = scene.getContext('2d');
  // ---- 背景：床单背面（马灯从后面照，暖、亮），褶子，乌龟的皮影贴在床单上（虚）
  const g = x.createRadialGradient(1250, 180, 80, 1150, 320, 1500);
  g.addColorStop(0, '#f6d7a2'); g.addColorStop(0.5, '#cf9152'); g.addColorStop(1, '#3e2615');
  x.fillStyle = g; x.fillRect(0, 0, RW, RH);
  x.save(); x.filter = 'blur(5px)'; x.strokeStyle = 'rgba(120,80,45,0.28)'; x.lineWidth = 3;
  for (let i = 0; i < 10; i++) { const x0 = 120 + i * 190 + 30 * Math.sin(i); x.beginPath(); x.moveTo(x0, 0); x.quadraticCurveTo(x0 + 20, 540, x0 - 10, RH); x.stroke(); }
  x.restore();
  // 乌龟：在床单背面的右上方，一步步往上爬（皮面朝后台）
  x.save(); x.filter = 'blur(4px)'; x.globalAlpha = 0.9;
  const tp = turtlePose(t, { facing: 1, walk: A.step % 1 > 0.02 && A.step % 1 < 0.98 ? 1 : 0.15, neckOut: 0.7 });
  x.translate(1380 + A.step * 26, 330 - A.step * 22); x.scale(1.2, -1.2); x.rotate(0.08);
  drawPuppet(x, TURTLE, tp, 'r');
  x.restore();
  // ---- 两双手（图）+ 程序接长的签子：整张图转 -28°，签子朝右上伸出画面
  const sc = 0.92, rot = -0.42 + A.shake * 0.006;
  const base = [-170 + A.step * 34 + A.shake * 5, 820 - A.step * 30 + A.shake * 4];   // 图的左边缘（袖口切口）落在画面外
  x.save(); x.translate(base[0], base[1]); x.rotate(rot); x.scale(sc, sc); x.translate(0, -560);
  // 签子：从图里签子的末端（x≈1460）沿同一条轴往外接 2600 像素
  x.lineCap = 'round';
  for (const [a, b] of AXES) {
    const p0 = [1440, a + b * 1440], p1 = [4200, a + b * 4200];
    x.strokeStyle = LINE; x.lineWidth = 18; x.beginPath(); x.moveTo(...p0); x.lineTo(...p1); x.stroke();
    x.strokeStyle = '#c99a52'; x.lineWidth = 11; x.beginPath(); x.moveTo(...p0); x.lineTo(...p1); x.stroke();
  }
  x.drawImage(im, 0, 0);
  x.restore();
  // ---- 光：马灯在后台左上方（暖），手被照亮；画面下角暗
  const lm = new OffscreenCanvas(RW, RH), lx = lm.getContext('2d');
  const lg = lx.createRadialGradient(500, -100, 100, 700, 200, 1800);
  const fl = 1 + 0.03 * Math.sin(t * 11) + 0.02 * Math.sin(t * 23);
  lg.addColorStop(0, `rgb(255,${Math.round(236 * Math.min(1, fl))},${Math.round(200 * Math.min(1, fl))})`); lg.addColorStop(0.6, 'rgb(230,190,150)'); lg.addColorStop(1, 'rgb(90,62,48)');
  lx.fillStyle = lg; lx.fillRect(0, 0, RW, RH);
  x.globalCompositeOperation = 'multiply'; x.drawImage(lm, 0, 0); x.globalCompositeOperation = 'source-over';
  // ---- 镜头慢慢推近
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  const z = 1 + 0.05 * sstep(0, 5, t);
  ctx.translate(RW / 2, RH / 2); ctx.scale(z, z); ctx.translate(-RW / 2, -RH / 2);
  ctx.drawImage(scene, 0, 0);
  ctx.restore();
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  const v = ctx.createRadialGradient(RW * 0.5, RH * 0.45, RH * 0.35, RW * 0.5, RH * 0.5, RH * 1.0);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let sd = Math.floor(t * 24) * 7919 + 22;
  const r2 = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (r2() - 0.5) * 6; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
