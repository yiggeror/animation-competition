// 动态分镜（代码动画）公用：用代码人物（js/chars）按关键帧表演，先把节奏、动作、表情定准，之后再按这些姿势配画。
// 人物画到一张透明图上，当作 paint 镜头的图层，跟场景吃同一套光。
import * as X from '../chars/xiaoman.js';
import * as N from '../chars/nainai.js';
export { key, EASE, blink, kick, spring, clamp, lerp, noise1 } from '../lib/core.js';

// 人物图层。who 'x' 小满 / 'n' 奶奶；view 'side' | 'front' | 'back'；pose 见 js/chars/*.js 的 POSE0。
// k = 每厘米多少背景像素；at = 人物原点（站立时两脚中点，坐/趴时用 pose.y 往下挪）在背景里的位置；box = 图层范围（背景像素）；
// flip = 左右镜像（侧面默认面朝右）。props(ctx) 在人物坐标里画道具（厘米），before 画在人物后面、after 画在前面。
export function charLayer(who, view, pose, { box, k, at, flip = false, ss = 2, before, after, light }) {
  const [x0, y0, x1, y1] = box, w = Math.ceil((x1 - x0) * ss), h = Math.ceil((y1 - y0) * ss);
  const c = new OffscreenCanvas(w, h), x = c.getContext('2d');
  x.scale(ss, ss); x.translate(at[0] - x0, at[1] - y0); x.scale(flip ? -k : k, k);
  if (before) { x.save(); before(x); x.restore(); }
  (who === 'x' ? X : N).draw(x, view, pose, light ? { light } : {});
  if (after) { x.save(); after(x); x.restore(); }
  return { img: c, x: x0, y: y0, sc: 1 / ss };
}

// ---- 道具（人物坐标，厘米，+y 向下，地面 y = 0）
export function stool(x, cx, top = 30) {
  x.fillStyle = '#8a5b3c'; x.strokeStyle = '#3b2c25'; x.lineWidth = 1.2;
  x.beginPath(); x.rect(cx - 15, -top, 30, 4); x.fill(); x.stroke();
  for (const dx of [-12, 9]) { x.beginPath(); x.rect(cx + dx, -top + 4, 3, top - 4); x.fill(); x.stroke(); }
}
export function bowl(x, cx, cy, w = 30) {
  x.fillStyle = '#f3efe6'; x.strokeStyle = '#3b2c25'; x.lineWidth = 1.2;
  x.beginPath(); x.ellipse(cx, cy, w / 2, w * 0.12, 0, 0, Math.PI); x.lineTo(cx - w / 2, cy); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = '#7fae4f'; x.beginPath(); x.ellipse(cx, cy, w / 2 - 2, w * 0.1, 0, Math.PI, 0); x.fill();
  x.strokeStyle = '#2f4f7a'; x.lineWidth = 1.6; x.beginPath(); x.ellipse(cx, cy, w / 2, w * 0.12, 0, Math.PI, 0); x.stroke();
}
// 西瓜块：中心 (cx, cy)，转角 a（弧度），大小 s（厘米），bite = 咬掉一口（0–1）
export function melon(x, cx, cy, a = 0, s = 10, bite = 0) {
  x.save(); x.translate(cx, cy); x.rotate(a); x.scale(s / 10, s / 10);
  x.lineWidth = 0.6; x.strokeStyle = '#3b2c25';
  x.beginPath(); x.moveTo(-6, 2.5); x.quadraticCurveTo(0, 5.2, 6, 2.5); x.lineTo(0, -5); x.closePath();
  x.fillStyle = '#e8584b'; x.fill(); x.stroke();
  x.beginPath(); x.moveTo(-6, 2.5); x.quadraticCurveTo(0, 5.2, 6, 2.5); x.quadraticCurveTo(0, 6.6, -6, 2.5); x.fillStyle = '#3f8a45'; x.fill(); x.stroke();
  x.fillStyle = '#2b1d18'; for (const [px, py] of [[-2, 0.5], [1.5, 0], [0, -2.2], [-0.5, 2]]) { x.beginPath(); x.ellipse(px, py, 0.35, 0.55, 0.3, 0, 7); x.fill(); }
  if (bite > 0) { x.globalCompositeOperation = 'destination-out'; x.beginPath(); x.arc(0, -5, 2.6 * bite, 0, 7); x.fill(); }
  x.restore();
}
export function phone(x, cx, cy, a = 0, lit = 1) {
  x.save(); x.translate(cx, cy); x.rotate(a);
  x.fillStyle = '#1f1f24'; x.strokeStyle = '#111'; x.lineWidth = 0.4; x.beginPath(); x.roundRect(-7, -3.6, 14, 7.2, 1); x.fill(); x.stroke();
  if (lit > 0) { x.fillStyle = `rgba(150,200,255,${0.85 * lit})`; x.beginPath(); x.roundRect(-6.2, -3, 12.4, 6, 0.6); x.fill(); }
  x.restore();
}
// 背景虚化的一块（近景用）
export function blurredBg(im, sx, sy, sw, sh, W, H, blur = 16) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = `blur(${blur}px)`; x.drawImage(im, sx, sy, sw, sh, -60, -60, W + 120, H + 120);
  return c;
}
// 帧数 → 秒（24 帧）
export const F = (n) => n / 24;
