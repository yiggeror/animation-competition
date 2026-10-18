// 动态分镜（代码动画）公用：用代码人物（js/chars）按关键帧表演，先把节奏、动作、表情定准，之后再按这些姿势配画。
// 人物画到一张透明图上，当作 paint 镜头的图层，跟场景吃同一套光。
import * as X from '../chars/xiaoman.js';
import * as N from '../chars/nainai.js';
import { ik2 } from '../lib/draw.js';
export { key, EASE, blink, kick, spring, clamp, lerp, noise1 } from '../lib/core.js';

// 人物图层。who 'x' 小满 / 'n' 奶奶；view 'side' | 'front' | 'back'；pose 见 js/chars/*.js 的 POSE0。
// k = 每厘米多少背景像素；at = 人物原点（站立时两脚中点，坐/趴时用 pose.y 往下挪）在背景里的位置；box = 图层范围（背景像素）；
// flip = 左右镜像（侧面默认面朝右）。props(ctx) 在人物坐标里画道具（厘米），before 画在人物后面、after 画在前面。
// 躺着的姿势用整个人转：rot = 画面上顺时针转多少（弧度），pivot = 绕人物身上哪一点（人物坐标），to = 这一点落在哪（地面坐标，跟道具同一套）。
// 这样腿跟身体一起转，不会出现"上身躺下、腿还按站着的坐标画"的情况。
export function charLayer(who, view, pose, { box, k, at, flip = false, ss = 2, before, after, light, rot = 0, pivot = [0, 0], to = null }) {
  const [x0, y0, x1, y1] = box, w = Math.ceil((x1 - x0) * ss), h = Math.ceil((y1 - y0) * ss);
  const c = new OffscreenCanvas(w, h), x = c.getContext('2d');
  x.scale(ss, ss); x.translate(at[0] - x0, at[1] - y0); x.scale(flip ? -k : k, k);
  if (before) { x.save(); before(x); x.restore(); }
  x.save();
  if (rot || to) { const q = to || pivot; x.translate(q[0], q[1]); x.rotate(flip ? -rot : rot); x.translate(-pivot[0], -pivot[1]); }
  (who === 'x' ? X : N).draw(x, view, pose, light ? { light } : {});
  x.restore();
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
  const r = 2.6 * bite;
  if (bite > 0) { x.beginPath(); x.rect(-20, -20, 40, 40); x.arc(0, -5.2, r, 0, 7, true); x.clip('evenodd'); }   // 咬掉的一口：这块不画，后面的脸/背景透出来（不能用擦除，会把人物也擦掉）
  x.lineWidth = 0.6; x.strokeStyle = '#3b2c25';
  x.beginPath(); x.moveTo(-6, 2.5); x.quadraticCurveTo(0, 5.2, 6, 2.5); x.lineTo(0, -5); x.closePath();
  x.fillStyle = '#e8584b'; x.fill(); x.stroke();
  x.beginPath(); x.moveTo(-6, 2.5); x.quadraticCurveTo(0, 5.2, 6, 2.5); x.quadraticCurveTo(0, 6.6, -6, 2.5); x.fillStyle = '#3f8a45'; x.fill(); x.stroke();
  x.fillStyle = '#2b1d18'; for (const [px, py] of [[-2, 0.5], [1.5, 0], [0, -2.2], [-0.5, 2]]) { x.beginPath(); x.ellipse(px, py, 0.35, 0.55, 0.3, 0, 7); x.fill(); }
  if (bite > 0) {   // 咬口的边：一道浅色的果肉弧，只画在瓜里面
    x.beginPath(); x.moveTo(-6, 2.5); x.quadraticCurveTo(0, 5.2, 6, 2.5); x.lineTo(0, -5); x.closePath(); x.clip();
    x.strokeStyle = '#f6b3a6'; x.lineWidth = 1.1; x.beginPath(); x.arc(0, -5.2, r + 0.5, 0, 7); x.stroke();
    x.strokeStyle = '#3b2c25'; x.lineWidth = 0.5; x.beginPath(); x.arc(0, -5.2, r, 0, 7); x.stroke();
  }
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

// ---- 关节：按角度推算（骨头长度固定，不会被拉长）。角度是弧度，0 = 朝 +x，+π/2 = 朝下（画布 y 向下）
export const XM_LEG = { thigh: 20.2, shin: 19.6, hipN: [0.1, -43.5], hipF: [-1.9, -43.5] };   // 小满侧面：髋（身体坐标）、大腿、小腿长（厘米）
export function legFK(hip, aThigh, aShin, l1, l2) {
  const knee = [hip[0] + Math.cos(aThigh) * l1, hip[1] + Math.sin(aThigh) * l1];
  return { knee, foot: [knee[0] + Math.cos(aShin) * l2, knee[1] + Math.sin(aShin) * l2] };
}
// 两节 IK（脚踩在固定的地面点上时用），bend 选膝盖/肘朝哪边
export function limbIK(root, target, l1, l2, bend = 1) { const r = ik2(root, target, l1, l2, bend); return { joint: r.joint, end: r.end }; }

// 肩膀在人物坐标里的位置（跟 js/chars 里侧面胳膊的算法一样），用来提前算手能不能够到、手里的东西在哪
const rotP = (p, a, c) => { const cs = Math.cos(a), sn = Math.sin(a), dx = p[0] - c[0], dy = p[1] - c[1]; return [c[0] + dx * cs - dy * sn, c[1] + dx * sn + dy * cs]; };
export function shoulderSide(who, P, side) {
  const bob = P.bob || 0, lean = P.lean || 0, sh = P.shrug || 0;
  if (who === 'n') { const st = P.stoop ?? 1; return rotP([side === 'N' ? 1.4 + st * 1.2 : -0.4 + st, -103.5 + sh * 2.4 + st * 1.2 + bob], lean, [-1, -75 + bob]); }
  return rotP([side === 'N' ? 0.4 : -0.6, -77.6 + sh * 2.0 + bob], lean, [-1, -43.5 + bob]);
}
export const ARM = { x: [12.4, 11.2, 4.4], n: [21.5, 19.5, 5.4] };   // 上臂、小臂、手掌长（厘米）
// 侧面胳膊：给肩、手腕目标，返回肘、腕（够不着就停在最远处）和手的朝向
export function armSide(who, P, side, hand, bend = -1) {
  const S = shoulderSide(who, P, side), [l1, l2] = ARM[who];
  const r = ik2(S, hand, l1, l2, bend);
  return { S, E: r.joint, W: r.end, dir: Math.atan2(r.end[1] - r.joint[1], r.end[0] - r.joint[0]), reach: Math.hypot(hand[0] - S[0], hand[1] - S[1]) / (l1 + l2) };
}
