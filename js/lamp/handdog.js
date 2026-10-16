// 手影小狗：小满两只手在手电光里比出来的狗（只有影子，所以画成不透光的剪影，和皮影用同一套 part / drawPuppet）。
// 上半是狗头：食指翘起来是耳朵，并拢的四指是嘴筒子，指缝留一个小孔当眼睛；下半是下巴（小指那一侧），一张一合像在叫。
// 头后面接着手腕和前臂，一直伸出光斑外。坐标：毫米，y 朝上，狗面朝 +x。
import { part, path, circ } from './crane.js';

export function makeDog(S = 1.0) {
  const s = (v) => v * S;
  const P = (pts) => pts.map(([x, y]) => [x * S, y * S]);
  const parts = [];
  parts.push(part('head', null, [0, 0], 0, [s(-330), s(-380), s(125), s(135)], (L) => {
    // 狗头 + 耳朵 + 后面的手腕、前臂（一直往左下伸出去）
    const head = path(P([[0, 0], [40, 7], [96, 11], [110, 17], [106, 28], [80, 40], [46, 56], [12, 70], [-12, 76], [-26, 122], [-36, 118], [-44, 72],
      [-58, 58], [-70, 28], [-74, 0], [-110, -60], [-200, -190], [-320, -370], [-250, -380], [-140, -230], [-70, -120], [-30, -40]]));
    L.fill(head, 'black');
    L.carve(circ(s(42), s(44), s(5)));                                         // 眼睛：指缝里透的一点光
    const brow = new Path2D(); brow.moveTo(s(-10), s(62)); brow.quadraticCurveTo(s(10), s(58), s(26), s(64)); L.carveLine(brow, s(1.6));   // 指缝
  }));
  parts.push(part('jaw', 'head', [0, -2], -0.5, [s(-40), s(-40), s(108), s(8)], (L) => {
    const jaw = path(P([[4, 4], [44, 0], [96, -2], [102, -10], [88, -20], [44, -27], [0, -32], [-34, -22], [-36, 0]]));
    L.fill(jaw, 'black');
  }));
  const map = {};
  for (const p of parts) map[p.part] = p;
  return { name: 'dog', rig: parts.map(({ part, parent, at, layer }) => ({ part, parent, at, layer })), parts: map };
}

// 叫：下巴张开的角度（弧度）随时间一张一合；pant 喘气时小幅快速开合
export function dogPose(t, o = {}) {
  const bark = o.bark ?? 0, pant = o.pant ?? 0;
  const jaw = -(bark * 0.5 * Math.max(0, Math.sin(t * 14)) + pant * 0.12 * (0.5 + 0.5 * Math.sin(t * 22)));
  return { angles: { jaw }, rootAngle: o.rootAngle ?? 0, facing: o.facing ?? -1 };
}

// 想让影子落在床单上 (sx, sz)：手要放在哪里（手电在 F = [x, 离床单, z]，手离床单 d）——影子以手电在床单上的垂足为中心放大 m = D / (D - d) 倍
export function rootForShadow(F, d, sx, sz) {
  const m = F[1] / (F[1] - d);
  return [F[0] + (sx - F[0]) / m, F[2] + (sz - F[2]) / m];
}
