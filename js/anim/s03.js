// 1-4 奶奶中近景（4 秒）：剥着豆，眼睛先抬起来看小满，头跟着抬、嘴角带笑；拿起一块西瓜往小满那边推过去；手停在那儿等。
import { closeShot, grandmaFront } from './close.js';
import { key, blink } from './kit.js';
import { ik2, curScale, inkScale } from '../lib/draw.js';
import { draw as drawGrandma } from '../chars/nainai.js';
export const DURATION = 4;
const K = 13, AT = [1010, 1480];
const SH_L = [-14.6, -103.5];   // 奶奶右肩（画面左）
// 首尾姿势保持冻结。旧“余弦压肘”会把上臂/前臂实际缩短；这里以固定骨长的
// 肩角与肘角做 FK：放开豆荚后先下探伸展，再收肘取瓜。两个相反的二维 IK 分支
// 必须经过伸直，不能承诺“不越肩腕线”；关键是连续伸展，不能在短臂状态下翻向。
const ARM_START = 34 / 24, ARM_END = 44 / 24, UPPER = 21.5, FORE = 19.5;
function shoulder(P) {
  const a = P.lean || 0, cs = Math.cos(a), sn = Math.sin(a), p = [-14.6, -103.5 + 1.2 + 75];
  return [p[0] * cs - p[1] * sn, -75 + p[0] * sn + p[1] * cs];
}
function fixedArm(P, hand, bend) {
  const r = ik2(shoulder(P), hand, UPPER, FORE, bend);
  return { elbow: r.joint, hand: r.end };
}
function reachArm(P, hand, t) {
  if (t <= ARM_START) return fixedArm(P, hand, -1);
  if (t >= ARM_END) return fixedArm(P, hand, 1);
  const S = shoulder(P), a = fixedArm(P, [-8, -76], -1), b = fixedArm(P, [-30, -78], 1);
  const angle = (p, q) => Math.atan2(q[1] - p[1], q[0] - p[0]);
  const wrap = (x) => Math.atan2(Math.sin(x), Math.cos(x));
  const a0 = angle(S, a.elbow), a1 = angle(S, b.elbow);
  const e0 = wrap(angle(a.elbow, a.hand) - a0), e1 = wrap(angle(b.elbow, b.hand) - a1);
  const u = (t - ARM_START) / (ARM_END - ARM_START), w = u * u * (3 - 2 * u);
  const upper = a0 + wrap(a1 - a0) * w, fore = upper + e0 + (e1 - e0) * w;
  const elbow = [S[0] + UPPER * Math.cos(upper), S[1] + UPPER * Math.sin(upper)];
  return { elbow, hand: [elbow[0] + FORE * Math.cos(fore), elbow[1] + FORE * Math.sin(fore)] };
}
// 供 Opus 合并到共享 keyposes；本镜不写共享时表。
export const KEYS = [[0.2, '剥豆'], [1.4, '松荚，手开始下探'], [1.63, '手臂连续伸展，腕下探至盆前遮挡区'], [1.85, '收肘到瓜旁'], [1.9, '托瓜'], [2.4, '递出停等'], [3.3, '保持等待']];
function palm(h) { const dx = h[0] - SH_L[0], dy = h[1] - SH_L[1], d = Math.hypot(dx, dy); return [h[0] + dx / d * 5, h[1] + dy / d * 5 + 37 - 3, 0.1, 8.5]; }
export function pose(t) {
  const look = key(t, [[0, [0, 0.6]], [0.4, [0, 0.6]], [0.6, [-0.7, -0.1], 'out'], [4, [-0.7, -0.1]]]);
  const lift = key(t, [[0.55, 0], [1.05, 1, 'io']]);
  const smile = key(t, [[0.7, 0.2], [1.1, 0.5], [3.4, 0.5], [3.9, 0.3]]);
  const brow = key(t, [[2.4, 0], [2.7, 0.35, 'out'], [4, 0.3]]);
  // 右手（画面左）：剥豆 → 豆荚丢回盆 → 往下伸去拿盘里的西瓜 → 端起来往左边推
  // 递瓜：肘往下收，手心朝上托着瓜，往画面左下方送过去（不是肘抬高、瓜挂在腕边）
  const hL = key(t, [[0, [-5, -78]], [0.3, [-4, -79]], [1.0, [-4, -79]], [1.25, [-8, -76]], [1.45, [-8, -76]], [1.8, [-30, -78], 'io'], [1.9, [-30, -78]], [2.35, [-38, -80], 'out'], [4, [-38, -80]]]);
  const hR = key(t, [[0, [6, -79]], [0.3, [5, -80]], [1.0, [5, -80]], [1.4, [9, -77]], [4, [9, -77]]]);
  const melonOn = t >= 1.9;
  return {
    P: { y: 37, seated: true, head: { nod: 0.5 * (1 - lift), turn: -0.3 * lift, tilt: 0.04 * lift }, lean: 0.03 * (1 - lift),
      armL: { ...reachArm({ lean: 0.03 * (1 - lift) }, hL, t), hp: t >= 1.9 ? 'rest' : 'pinch' }, armR: { hand: hR, hp: 'pinch' },
      face: { look, smile, brow, open: 0.9, blink: blink(t, [3.1]) } },
    melonAt: melonOn ? palm(hL) : null,   // 瓜坐在掌心上：手腕沿小臂方向再往前 5 厘米、往上 3 厘米
    plate: melonOn ? null : [-30, -38],                                 // 盘子放在身边的小凳上，取瓜那一下在画面里
  };
}
// close.js 的坐姿腿面矩形会连盆左侧的前臂一起擦掉。只在空手取瓜过渡中，
// 从同帧原人物恢复“真实左臂/手轮廓 ∩ 腿面裁线下方”，随后让真实盆再次遮住它。
// 不改共享 lap，不恢复腿/躯干，不把侧盘覆盖到抓瓜手前；腕自然出画的帧不做假补画。
function reachingLayer(s, t) {
  const layer = grandmaFront(s.P, { k: K, at: AT, plate: s.plate, melonAt: s.melonAt });
  if (t <= ARM_START || t >= ARM_END) return layer;
  const raw = new OffscreenCanvas(1920, 1080), r = raw.getContext('2d');
  r.translate(AT[0], AT[1]); r.scale(K, K);
  const { fig } = drawGrandma(r, 'front', s.P);
  const mask = new OffscreenCanvas(1920, 1080), m = mask.getContext('2d');
  m.setTransform(fig.m); m.fillStyle = '#fff'; m.strokeStyle = '#fff'; m.lineJoin = 'round'; m.lineCap = 'round';
  const lw = fig.lw * inkScale() / curScale(m);
  for (const part of fig.parts) if (part.name === 'armL' || part.name === 'handL') {
    m.lineWidth = lw * 2 * (part.o.lwMul ?? 1);
    if (part.o.outline !== false) m.stroke(part.path);
    m.fill(part.path);
  }
  // mask 含真实外墨线，不只恢复填色轮廓而漏半圈描边。
  r.save(); r.setTransform(1, 0, 0, 1, 0, 0); r.globalCompositeOperation = 'destination-in'; r.drawImage(mask, 0, 0); r.restore();
  const x = layer.img.getContext('2d');
  x.save(); x.setTransform(K, 0, 0, K, AT[0], AT[1]);
  x.beginPath(); x.rect(-80, -36, 160, 60); x.clip();
  x.setTransform(1, 0, 0, 1, 0, 0); x.drawImage(raw, 0, 0); x.restore();
  x.save(); x.setTransform(K, 0, 0, K, AT[0], AT[1]);
  // 与 close.js 相同的实体盆前景，侧盘与瓜保持原绘制顺序。
  x.fillStyle = '#f3efe6'; x.strokeStyle = '#3b2c25'; x.lineWidth = 0.5;
  x.beginPath(); x.ellipse(0, -36, 19, 4.5, 0, 0, Math.PI); x.lineTo(-19, -36); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = '#7fae4f'; x.beginPath(); x.ellipse(0, -36, 17.5, 3.8, 0, Math.PI, 0); x.fill();
  x.strokeStyle = '#2f4f7a'; x.lineWidth = 0.9; x.beginPath(); x.ellipse(0, -36, 19, 4.5, 0, Math.PI, 0); x.stroke();
  x.restore();
  return layer;
}
const shot = closeShot({
  bgKey: 'room_gm', bgCrop: [900, 180, 640, 360], blur: 16,
  layers: async (t) => { const s = pose(t); return [reachingLayer(s, t)]; },
  light: () => ({ ambient: [0.62, 0.66, 0.72], lights: [{ x: 1100, y: -300, r: 2200, color: [0.92, 0.96, 1.0], i: 0.55, falloff: 1.2 }, { x: -200, y: 520, r: 1300, color: [0.55, 0.7, 1.0], i: 0.3, falloff: 1.5 }], exposure: 1.0, vignette: 0.3, grain: 5 }),
});
export async function renderFrame(ctx, t, W, H) { return shot.render(ctx, t, W, H); }
