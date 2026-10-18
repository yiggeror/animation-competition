// 五官：眼睛、眉毛、鼻子、嘴、腮红、眼镜。两个人物共用，造型参数不同。
// 表情用语义参数：open 睁眼程度、look 视线、smile 嘴角、mouth 张嘴、brow 眉毛高低、worry 眉毛内角上扬、
// squint 眯眼、blush 腮红、puff 鼓腮、tongue 吐舌头。
import { brush, ellipsePts, arcPts, lerpP } from '../lib/draw.js';
import { clamp, lerp } from '../lib/core.js';

export const FACE0 = { open: 1, look: [0, 0], smile: 0.2, mouth: 0, brow: 0, worry: 0, squint: 0, blush: 0.5, puff: 0, tongue: 0, blink: 0, happyEyes: 0, frown: 0, side: 0 };
export function faceOf(f = {}) { return { ...FACE0, ...f }; }

// 一只眼睛。c = 中心，r = [rx, ry]，sgn = -1 左眼 / +1 右眼（画面左右）
// 闭眼和笑眼画成弧线；睁眼是深色椭圆 + 高光，上眼皮按 open/squint 压下来
export function eye(fig, c, r, f, sgn, o) {
  const z = o.z ?? 6, clip = o.clip;
  const open = clamp(f.open * (1 - f.blink) * (1 - 0.55 * f.squint), 0, 1.3);
  const happy = clamp(f.happyEyes, 0, 1);
  const ink = o.ink;
  if (open < 0.12 || happy > 0.5) {
    // 闭眼：开心时是向上弯的弧（^），平时是向下弯的弧
    const up = happy > 0.5 ? 1 : -0.35;
    const w = r[0] * 1.15;
    fig.detail([[c[0] - w, c[1] + r[1] * 0.1 * up], [c[0], c[1] - r[1] * 0.55 * up], [c[0] + w, c[1] + r[1] * 0.1 * up]], { z, lw: o.lw * 1.05, color: ink, profile: 'soft', clip });
    if (o.lash && happy <= 0.5) fig.detail([[c[0] + sgn * w * 0.85, c[1] - r[1] * 0.05], [c[0] + sgn * w * 1.25, c[1] - r[1] * 0.35]], { z, lw: o.lw * 0.6, color: ink, profile: 'out', clip });
    return;
  }
  const ry = r[1] * Math.min(1, open);
  const look = f.look;
  const cx = c[0] + look[0] * r[0] * 0.25, cy = c[1] + look[1] * r[1] * 0.2 + (r[1] - ry) * 0.35;
  // 眼白（大眼睛才有）
  if (o.white) fig.detail(ellipsePts(c[0], cy, r[0] * 1.35, ry * 1.2, 28), { z, fill: o.white, lw: 0, clip });
  fig.detail(ellipsePts(cx, cy, r[0], ry, 28), { z: z + 0.01, fill: o.iris, lw: 0, clip, smooth: false });
  // 高光
  if (ry > r[1] * 0.35) {
    fig.detail(ellipsePts(cx - r[0] * 0.3, cy - ry * 0.35, r[0] * 0.32, r[0] * 0.32, 12), { z: z + 0.02, fill: '#fffaf0', lw: 0, clip, smooth: false });
    if (o.hi2) fig.detail(ellipsePts(cx + r[0] * 0.35, cy + ry * 0.35, r[0] * 0.14, r[0] * 0.14, 10), { z: z + 0.02, fill: '#fffaf0', lw: 0, clip, smooth: false });
  }
  // 上眼皮：眯眼、睡眼时压下来的一条粗线
  const lid = c[1] - r[1] * (1.05 - 0.9 * (1 - open)) - r[1] * 0.1;
  if (open < 0.95 || f.squint > 0.05) fig.detail([[c[0] - r[0] * 1.35, lid + r[1] * 0.25], [c[0], lid], [c[0] + r[0] * 1.35, lid + r[1] * 0.25]], { z: z + 0.03, lw: o.lw * 0.95, color: ink, profile: 'soft', clip });
  // 睫毛（小满：外眼角一笔）
  if (o.lash) fig.detail([[c[0] + sgn * r[0] * 0.9, cy - ry * 0.75], [c[0] + sgn * r[0] * 1.45, cy - ry * 1.1]], { z: z + 0.03, lw: o.lw * 0.7, color: ink, profile: 'out', clip });
}

// 眉毛：短粗一笔。brow 抬高、worry 内角上扬、frown 内角下压（生气/嘴硬）
export function brow(fig, c, w, f, sgn, o) {
  const inner = [c[0] - sgn * w * 0.5, c[1] - f.brow * 1.2 - f.worry * 1.4 + f.frown * 1.1];
  const outer = [c[0] + sgn * w * 0.5, c[1] - f.brow * 1.0 + f.worry * 0.5 - f.frown * 0.4];
  const mid = [(inner[0] + outer[0]) / 2, Math.min(inner[1], outer[1]) - w * 0.12];
  fig.detail([inner, mid, outer], { z: o.z ?? 9, lw: o.lw, color: o.color, profile: sgn < 0 ? 'out' : 'in', clip: o.clip });
}

// 嘴。c = 中心，w = 宽。smile -1…1，mouth 0…1 张嘴，puff 鼓腮时嘴缩成一个小圆
export function mouth(fig, c, w, f, o) {
  const z = o.z ?? 6, clip = o.clip, ink = o.ink;
  if (f.puff > 0.4) {
    fig.detail(ellipsePts(c[0], c[1], w * 0.16, w * 0.2, 14), { z, fill: o.inside, lw: o.lw * 0.6, color: ink, clip });
    return;
  }
  const s = f.smile;
  const open = clamp(f.mouth, 0, 1);
  const hw = w * (0.5 + 0.12 * s - 0.15 * open * (s < 0 ? 1 : 0));
  const lift = s * w * 0.28;
  if (open < 0.08) {
    fig.detail([[c[0] - hw, c[1] - lift], [c[0], c[1] + lift * 0.5], [c[0] + hw, c[1] - lift]], { z, lw: o.lw * 0.85, color: ink, profile: 'soft', clip });
    return;
  }
  // 嘴角往下又张着嘴（吃惊、发愣、"不是吧"）：竖着的小椭圆，不画成笑口
  if (s < -0.2) {
    fig.detail(ellipsePts(c[0], c[1] + w * 0.08, w * (0.14 + 0.1 * open), w * (0.16 + 0.32 * open), 16), { z, fill: o.inside, lw: o.lw * 0.75, color: ink, clip });
    return;
  }
  // 张开：上唇线 + 下唇的弧，里面填深色，笑的时候露一点舌头
  const top = c[1] - lift * 0.6;
  const depth = w * (0.25 + 0.65 * open);
  const pts = [];
  for (const p of arcPts(c[0], top, hw, depth, 0, Math.PI, 12)) pts.push(p);
  pts.push([c[0] - hw, top - lift * 0.4]);
  pts.push([c[0], top + lift * 0.15]);
  pts.push([c[0] + hw, top - lift * 0.4]);
  fig.detail(pts, { z, fill: o.inside, lw: o.lw * 0.75, color: ink, clip, smooth: true });
  if (f.tongue > 0 || s > 0.3) {
    fig.paint((ctx) => {
      ctx.fillStyle = o.tongue;
      ctx.beginPath(); ctx.ellipse(c[0], top + depth * 0.82, hw * 0.55, depth * 0.38, 0, 0, Math.PI * 2); ctx.fill();
    }, { z: z + 0.01, clip });
  }
}

// 圆框眼镜（奶奶）
export function glasses(fig, cl, cr, r, o) {
  const z = o.z ?? 8;
  for (const c of [cl, cr]) fig.detail(ellipsePts(c[0], c[1], r, r * 0.92, 30), { z, fill: 'rgba(255,255,255,0.10)', lw: o.lw, color: o.color });
  fig.detail([[cl[0] + r * 0.95, cl[1] - r * 0.2], [(cl[0] + cr[0]) / 2, cl[1] - r * 0.42], [cr[0] - r * 0.95, cr[1] - r * 0.2]], { z, lw: o.lw * 0.9, color: o.color, profile: 'flat' });
  if (o.temple !== false) {
    fig.detail([[cl[0] - r, cl[1] - r * 0.1], [cl[0] - r * 1.7, cl[1] - r * 0.25]], { z: z - 0.5, lw: o.lw * 0.8, color: o.color, profile: 'flat' });
    fig.detail([[cr[0] + r, cr[1] - r * 0.1], [cr[0] + r * 1.7, cr[1] - r * 0.25]], { z: z - 0.5, lw: o.lw * 0.8, color: o.color, profile: 'flat' });
  }
}

export function blush(fig, c, r, a, o) {
  if (a <= 0.02) return;
  fig.paint((ctx) => {
    const g = ctx.createRadialGradient(c[0], c[1], 0, c[0], c[1], r);
    g.addColorStop(0, `rgba(${o.rgb},${0.55 * a})`);
    g.addColorStop(1, `rgba(${o.rgb},0)`);
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.ellipse(c[0], c[1], r, r * 0.7, 0, 0, Math.PI * 2); ctx.fill();
  }, { z: o.z ?? 5.6, clip: o.clip });
}

export { lerpP, lerp };
