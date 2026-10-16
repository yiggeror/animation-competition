// 皮影动作编排：鹤和乌龟的几个基本动作，组合成床单戏的各个镜头。
// 鹤的骨架见 crane.js（12 节脖子、头、两条腿），乌龟见 turtle.js。角度是弧度，各部件相对父部件转。
export const NECK_UP = [1.25, 0.10, 0.08, 0.06, 0.03, 0.0, -0.04, -0.07, -0.09, -0.10, -0.09, -0.07, -0.55];
export const NECK_LOW = [0.80, 0.16, 0.14, 0.12, 0.08, 0.02, -0.06, -0.14, -0.22, -0.28, -0.30, -0.26, -0.15];
// 低头啄水：脖子往前伸、往下弯，喙朝下
export const NECK_DOWN = [0.25, -0.02, -0.06, -0.10, -0.14, -0.17, -0.19, -0.2, -0.19, -0.16, -0.12, -0.08, -0.55];
// 梳毛：脖子往回弯，头埋到背上
export const NECK_PREEN = [1.45, 0.30, 0.30, 0.28, 0.26, 0.24, 0.22, 0.2, 0.18, 0.12, 0.05, 0.0, 1.2];

export const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
export const lerp = (a, b, k) => a + (b - a) * k;
export const mixNeck = (A, B, k) => A.map((v, i) => lerp(v, B[i], k));
export const backOut = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); const c = 1.4; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };

// 鹤的姿势：neck（13 个数：12 节脖子 + 头）、腿（站立 / 收起一条 / 走路的相位）、身子的倾角
// legs：{ mode: 'stand' 单腿站（另一条收起）| 'two' 两腿站 | 'walk', ph: 走路相位（弧度）, swing: 收起那条腿的惯性摆动 }
export function cranePoseOf(neck, legs = { mode: 'stand' }, rootAngle = 0.04, facing = 1) {
  const angles = {};
  for (let i = 0; i < 12; i++) angles['neck' + i] = neck[i];
  angles.head = neck[12];
  const sw = legs.swing ?? 0;
  if (legs.mode === 'walk') {
    // 两条腿交替：迈出去的那条大腿往前抬、小腿往后折，落地的那条伸直往后蹬
    const p = legs.ph, a = Math.sin(p), b = Math.sin(p + Math.PI);
    const lift = (s) => Math.max(0, s);
    angles.tibia_near = 0.35 * a + 0.5 * lift(a); angles.tarsus_near = -0.9 * lift(a); angles.foot_near = 0.4 * lift(a);
    angles.tibia_far = 0.35 * b + 0.5 * lift(b); angles.tarsus_far = -0.9 * lift(b); angles.foot_far = 0.4 * lift(b);
  } else if (legs.mode === 'two') {
    Object.assign(angles, { tibia_near: 0.08, tarsus_near: -0.02, foot_near: 0.03, tibia_far: -0.05, tarsus_far: 0.02, foot_far: 0.03 });
  } else {
    Object.assign(angles, { tibia_near: 1.15 + sw, tarsus_near: -2.5 - sw * 0.6, foot_near: 1.15 + sw * 0.4, tibia_far: -0.05, tarsus_far: 0.02, foot_far: 0.03 });
  }
  return { angles, rootAngle, facing };
}

// 鹤的签子手端：跟着鹤的根点走（和第 6 场一样的相对位置）
export const craneRods = (RODS, root) => RODS.map((r) => ({ ...r, hand: r.hand(root) }));
// 乌龟的两根签子：壳上一根、头上一根，手在后下方
export const turtleRods = (root, facing = -1) => [
  { part: 'shell', at: [0, 40], hand: [root[0] - facing * 0.10, root[1] - 0.14, 0.42] },
  { part: 'head', at: [20, 0], hand: [root[0] + facing * 0.18, root[1] - 0.06, 0.42] },
];
