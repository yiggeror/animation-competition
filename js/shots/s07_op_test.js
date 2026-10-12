// 动作测试：后台，奶奶操纵鹤（4 秒）。机位在后台西侧、略靠后，斜看床单。
// 奶奶侧身（面朝床单），两手各握一根签子：身签让鹤往前走两步，头签让鹤低头啄、再抬头。
// 马灯挂在她和床单之间，照亮她的脸和手；床单上贴着鹤的背面（从后台看到的是染色的皮面）。
// 检查：手始终握在签子末端；胳膊跟着签子动、肘只往正确方向弯；身体随动作轻轻前后晃。
import * as N from '../chars/nainai.js';
import { loadPuppet, drawPuppet, solve, pointOn } from '../puppet.js';
import { LightMap, glow, radial } from '../lib/light.js';
import { setBoil, shape, line, fillPoly, rrectPts, ellipsePts } from '../lib/draw.js';
import { key, clamp, lerp, EASE, kick, noise1, blink } from '../lib/core.js';

export const DURATION = 4.0;

// 斜着看的平行投影（所有东西用同一套）：世界坐标 (x 沿床单, 深度 = 离床单往后台的距离, z 高度) → 画面
//   沿床单 1 米 → (+300, -40) 像素（往右往里退）；往后台 1 米 → (-520, +30)；往上 1 米 → (0, -620)
// 奶奶站在 x 0.88、离床单 0.84 米；马灯 x 1.30、离床单 0.70 米、高 1.55 米；签子长 0.55 米。
const SH = { x0: 0.25, x1: 2.35, z0: 0.86, z1: 2.08 };
const O = [848, 1090];
const P3 = (x, dep, z) => [O[0] + 300 * (x - SH.x0) - 520 * dep, O[1] - 40 * (x - SH.x0) + 30 * dep - 620 * z];
const sp = (x, z) => P3(x, 0, z);
const NN_AT = P3(0.88, 0.84, 0);
const LAMP = P3(1.30, 0.70, 1.55);

const NECK_HIGH = [1.10, 0.12, 0.10, 0.07, 0.02, -0.04, -0.10, -0.14, -0.16, -0.15, -0.12, -0.08, -0.40];
const NECK_PECK = [0.35, -0.05, -0.10, -0.14, -0.16, -0.16, -0.12, -0.08, -0.04, 0.0, 0.02, 0.04, -0.78];

function crane(t) {
  // 往前走两步：身子一顿一顿地往前（每步先蓄一下），腿交替
  const stepK = key(t, [[0, 0], [0.5, 0], [1.0, 0.5, EASE.outBack], [1.3, 0.5], [1.8, 1, EASE.outBack], [4, 1]]);
  const peck = key(t, [[0, 0], [2.2, 0], [2.5, 1, 'io'], [2.65, 0.7, 'io'], [2.8, 1, 'io'], [3.4, 0, 'io3'], [4, 0]]);
  const rootX = 0.95 + 0.16 * stepK, rootZ = 1.18 + 0.012 * Math.sin(stepK * Math.PI * 2);
  const n = NECK_HIGH.map((a, i) => lerp(a, NECK_PECK[i], peck));
  const angles = {};
  for (let i = 0; i < 12; i++) angles['neck' + i] = n[i];
  angles.head = n[12];
  const ph = stepK * Math.PI * 2;
  Object.assign(angles, {
    tibia_near: 0.25 + 0.45 * Math.sin(ph), tarsus_near: -0.5 - 0.5 * Math.max(0, Math.sin(ph)), foot_near: 0.3,
    tibia_far: -0.05 - 0.4 * Math.sin(ph), tarsus_far: 0.02 - 0.45 * Math.max(0, -Math.sin(ph)), foot_far: 0.05,
  });
  return { pose: { angles, rootAngle: -0.05 - 0.14 * peck + 0.04 * Math.sin(ph), facing: 1 }, root: [rootX, rootZ], peck, stepK };
}

let pup = null;
export async function renderFrame(ctx, t, W, H) {
  pup ||= await loadPuppet('crane');
  setBoil(t);
  const S = W / 1920;
  ctx.save(); ctx.scale(S, S);
  const flick = 1 + 0.04 * noise1(t * 7.3, 3) + 0.02 * noise1(t * 17.1, 5);
  const C = crane(t);

  // ================= 背景：后台的墙、床单（斜着看）、马灯
  ctx.fillStyle = '#b9ad98'; ctx.fillRect(0, 0, 1920, 1080);
  ctx.fillStyle = '#566e5c'; ctx.fillRect(0, 700, 1920, 380);
  shape(ctx, [[0, 700], [1920, 700]], { closed: false, lw: 2, stroke: '#3c5143', seed: 3 });
  // 床单（背面）：被马灯照亮的白布
  const quad = [sp(SH.x0, SH.z1), sp(SH.x1, SH.z1), sp(SH.x1, SH.z0), sp(SH.x0, SH.z0)];
  shape(ctx, quad, { fill: '#efe6d3', lw: 2.2, seed: 5, smooth: false });
  line(ctx, [P3(-0.2, 0, 2.09), P3(2.6, 0, 2.09)], { lw: 2, stroke: '#4a4038', seed: 7 });
  // 鹤：贴在床单背面，画在床单平面的斜变换里（看到的是皮面颜色）
  ctx.save();
  const o = sp(C.root[0], C.root[1]);
  ctx.transform(0.300, -0.040, 0, -0.620, o[0], o[1]);   // 皮影毫米（y 向上）→ 画面，和 P3 一致
  drawPuppet(ctx, pup, C.pose, 'r');
  ctx.restore();
  // 签子的两个连接点（床单平面 → 画面），签子往奶奶手里伸：离开床单往后台（画面左、下）
  const sol = solve(pup, C.pose);
  const att = (part, at) => { const p = pointOn(pup, sol, part, at); return sp(C.root[0] + p[0] / 1000, C.root[1] + p[1] / 1000); };
  const aBody = att('body', [8, 6]), aHead = att('head', [16, 2]);
  // 手的位置：签子是硬的、长约 0.55 米，从皮影往后台、斜着往下伸到奶奶胸前（艺人的手低于灯，手影才不上幕）
  const rodOff = (dep, dz) => { const a = P3(SH.x0, 0, 0), b = P3(SH.x0 - 0.03, dep, dz); return [b[0] - a[0], b[1] - a[1]]; };
  const ob = rodOff(0.46, -0.26), oh = rodOff(0.38, -0.40);
  const hBody = [aBody[0] + ob[0], aBody[1] + ob[1]];
  const hHead = [aHead[0] + oh[0], aHead[1] + oh[1]];
  // 马灯
  const L = [LAMP[0], LAMP[1] + 40];
  line(ctx, [[L[0], -10], [L[0], L[1] - 70]], { lw: 1.8, stroke: '#5a4a3a', seed: 11 });
  shape(ctx, rrectPts(L[0] - 34, L[1] - 70, 68, 14, 4), { fill: '#3b3b3b', lw: 2, seed: 12, smooth: false });
  shape(ctx, ellipsePts(L[0], L[1] - 16, 30, 46, 30), { fill: 'rgba(255,214,150,0.9)', lw: 2, seed: 13 });
  shape(ctx, rrectPts(L[0] - 40, L[1] + 26, 80, 34, 8), { fill: '#4a4744', lw: 2, seed: 14, smooth: false });

  // ================= 奶奶（侧面，面朝床单）
  const sway = 0.02 * Math.sin(t * 2.1) + 0.035 * (C.stepK - 0.5) + 0.03 * C.peck;
  const look = key(t, [[0, 0], [2.0, 0], [2.4, 1], [3.6, 1], [4, 0.6]]);
  const smile = key(t, [[0, 0.25], [3.3, 0.25], [3.7, 0.9, 'out'], [4, 0.85]]);
  const nn = {
    x: NN_AT[0], y: NN_AT[1], s: 6.2,
    lean: 0.05 + sway, stoop: 1.0,
    head: { nod: 0.4 + 0.5 * look, tilt: 0.04 * Math.sin(t * 1.7) },
    face: { look: [0.6, 0.6], smile, happyEyes: smile > 0.7 ? 1 : 0, blink: blink(t, [1.2, 3.1]), open: 0.95 },
    // 手的目标：画面坐标换回奶奶的身体坐标（厘米）
    armN: { hand: [(hBody[0] - NN_AT[0]) / 6.2, (hBody[1] - NN_AT[1]) / 6.2], hp: 'grip', bend: -1, rot: -0.35 },
    armF: { hand: [(hHead[0] - NN_AT[0]) / 6.2, (hHead[1] - NN_AT[1]) / 6.2], hp: 'grip', bend: -1, rot: -0.35 },
  };
  // 签子（画在奶奶后面一层：远侧的手握头签）
  line(ctx, [aHead, hHead], { lw: 3, stroke: '#7a5a3a', seed: 21 });
  const r = N.draw(ctx, 'side', nn, { defer: true });
  line(ctx, [aBody, hBody], { lw: 3.4, stroke: '#7a5a3a', seed: 22 });

  // ================= 光：马灯是唯一的暖光；其余是很暗的冷色
  const lm = new LightMap(ctx, '46,48,70');
  lm.point(L[0], L[1], 900, '255,190,115', 1.0 * flick, 1.15, 1);
  lm.point(1500, 420, 700, '255,200,140', 0.35 * flick, 0.8, 1.2);    // 床单反射回来的光
  lm.apply();
  // 灯本身和光晕（叠底之后，比白纸还亮）
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  shape(ctx, ellipsePts(L[0], L[1] - 12, 8, 14, 16), { fill: 'rgba(255,240,200,1)', lw: 0 });
  ctx.restore();
  glow(ctx, L[0], L[1] - 12, 160, '255,200,130', 0.55 * flick);
  glow(ctx, L[0], L[1] - 12, 420, '255,180,110', 0.18 * flick);
  // 奶奶面向灯的一侧的亮边
  ctx.save(); ctx.translate(nn.x, nn.y); ctx.scale(nn.s, nn.s);
  r.fig.rim({ dirs: [[1, -0.2]], w: 6, rgb: '255,200,130', a: 0.8 * flick, blur: 1.2 });
  r.fig.drawLights();
  ctx.restore();
  const vg = ctx.createRadialGradient(960, 500, 450, 960, 500, 1200);
  vg.addColorStop(0, 'rgba(20,14,10,0)'); vg.addColorStop(1, 'rgba(20,14,10,0.5)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, 1920, 1080);
  ctx.restore();
}
