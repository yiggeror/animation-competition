// 手：卡通的四指手，每种手型是一条设计好的整体轮廓（像动画师画手的几个关键形），手指之间的分隔用内线。
// 局部坐标：手腕在原点，+x 指向指尖，-y 是拇指一侧（手指朝右时拇指在上）；手掌长 = 1。
//   侧面手型（看到拇指一侧）：relax 放松、fist 拳、grip 握签子、point 指、pinch 捏
//   正面手型（手掌/手背）：open 张开、wave 挥手、rest 微曲；open 系列可以给每根手指单独的弯曲 curl[4]
import { M } from '../lib/figure.js';
import { ellipsePts, catmull } from '../lib/draw.js';

export const HAND_POSES = {
  relax: { kind: 'relax' }, fist: { kind: 'fist' }, grip: { kind: 'grip' }, point: { kind: 'point' }, pinch: { kind: 'pinch' },
  open: { kind: 'open', curl: [0, 0, 0, 0.05], spread: 1, thumb: 0 },
  wave: { kind: 'open', curl: [0.05, 0, 0.05, 0.12], spread: 0.6, thumb: 0.15 },
  rest: { kind: 'open', curl: [0.3, 0.25, 0.32, 0.4], spread: 0.25, thumb: 0.35 },
};

// 侧面手型：拇指是整体轮廓上的一个鼓包，只补画拇指下沿那一道线（不画成封闭的圈）
const RELAX = [[0, -0.26], [0.3, -0.34], [0.62, -0.41], [0.9, -0.43], [1.05, -0.37], [1.1, -0.28], [1.38, -0.24], [1.66, -0.1], [1.82, 0.08], [1.8, 0.26], [1.62, 0.3], [1.38, 0.22], [1.1, 0.26], [0.6, 0.33], [0, 0.27]];
const RELAX_LINES = [[[0.42, -0.25], [0.76, -0.29], [1.05, -0.34]], [[1.12, 0.04], [1.4, 0.02], [1.62, 0.12]]];
const FIST = [[0, -0.27], [0.45, -0.37], [0.85, -0.41], [1.08, -0.34], [1.22, -0.18], [1.25, 0.04], [1.17, 0.26], [0.97, 0.38], [0.55, 0.38], [0, 0.28]];
const FIST_LINES = [[[0.36, -0.26], [0.7, -0.21], [0.98, -0.13], [1.1, -0.05]], [[0.98, 0.0], [1.12, 0.06], [1.1, 0.14]], [[0.94, 0.17], [1.06, 0.23], [1.0, 0.31]]];
const POINT = [[0, -0.27], [0.45, -0.37], [0.95, -0.37], [1.5, -0.36], [1.88, -0.32], [1.97, -0.23], [1.9, -0.14], [1.5, -0.13], [1.2, -0.09], [1.25, 0.06], [1.17, 0.26], [0.97, 0.38], [0.55, 0.38], [0, 0.28]];
const POINT_LINES = [[[0.36, -0.22], [0.7, -0.15], [1.02, -0.07]], [[1.0, 0.08], [1.12, 0.13], [1.08, 0.21]]];
const PINCH = [[0, -0.27], [0.4, -0.36], [0.8, -0.42], [1.2, -0.41], [1.45, -0.31], [1.51, -0.19], [1.41, -0.1], [1.2, -0.03], [1.2, 0.18], [1.08, 0.34], [0.6, 0.38], [0, 0.28]];
const PINCH_LINES = [[[0.55, -0.24], [0.98, -0.25], [1.42, -0.19]], [[1.02, 0.1], [1.12, 0.16], [1.06, 0.24]]];

// 张开的手（手背朝外，拇指在 -y 一侧）：按每根手指的弯曲和张开程度拼出整条轮廓
function openOutline(P) {
  const sp = P.spread ?? 0.6;
  const fingers = [ // 根部 y、长度、宽度
    { y: -0.27, len: 0.88, w: 0.12 }, { y: -0.08, len: 0.98, w: 0.125 }, { y: 0.11, len: 0.9, w: 0.12 }, { y: 0.29, len: 0.7, w: 0.11 },
  ];
  const pts = [[0, 0.3], [0.55, 0.4]];
  for (let i = 3; i >= 0; i--) {
    const f = fingers[i], c = P.curl?.[i] ?? 0;
    const ang = f.y * 0.75 * sp;
    const len = f.len * (1 - 0.6 * c);
    const bx = 0.92 + (i === 0 || i === 3 ? -0.05 : 0), by = f.y;
    const ca = Math.cos(ang), sa = Math.sin(ang);
    const nx = -sa, ny = ca; // 手指的横向
    const tip = [bx + ca * len, by + sa * len];
    pts.push([bx + nx * f.w, by + ny * f.w]);
    pts.push([bx + ca * len * 0.55 + nx * f.w * 0.95, by + sa * len * 0.55 + ny * f.w * 0.95]);
    pts.push([tip[0] + nx * f.w * 0.7, tip[1] + ny * f.w * 0.7]);
    pts.push([tip[0] + ca * f.w * 0.8, tip[1] + sa * f.w * 0.8]);
    pts.push([tip[0] - nx * f.w * 0.7, tip[1] - ny * f.w * 0.7]);
    pts.push([bx + ca * len * 0.55 - nx * f.w * 0.95, by + sa * len * 0.55 - ny * f.w * 0.95]);
    pts.push([bx - nx * f.w * 0.9 + 0.02, by - ny * f.w * 0.9]);
  }
  // 拇指
  const th = P.thumb ?? 0;
  const ta = -1.0 + th * 0.9;
  const tb = [0.42, -0.38];
  const tl = 0.62 * (1 - 0.25 * th);
  const ttip = [tb[0] + Math.cos(ta) * tl + 0.08, tb[1] + Math.sin(ta) * tl];
  pts.push([0.78, -0.38]);
  pts.push([ttip[0] + 0.1, ttip[1] + 0.05]);
  pts.push([ttip[0], ttip[1] - 0.08]);
  pts.push([ttip[0] - 0.12, ttip[1] + 0.04]);
  pts.push([0.3, -0.36]);
  pts.push([0, -0.3]);
  return pts;
}

// pose: 名字或对象；o.size: 手掌长（厘米）；o.mirror: 拇指换到另一侧
export function hand(fig, Mw, pose, o) {
  const P = typeof pose === 'string' ? HAND_POSES[pose] : { ...HAND_POSES[pose.base || 'open'], ...pose };
  const s = o.size, mir = o.mirror ? -1 : 1;
  const T = M.chain(Mw, M.s(s, s * mir));
  const ap = (pts) => M.apAll(T, pts);
  const fill = o.skin, z = o.z, name = o.name, lw = o.lw;
  const line = o.line;
  const crease = (pts, w = 0.5, extra = {}) => fig.detail(ap(pts), { z: z + 0.3, lw: lw * w, color: o.ink, clip: [name], profile: 'taper', ...extra });
  const k = P.kind;
  const side = { relax: [RELAX, RELAX_LINES, [0.95, 0.05], [1.82, 0.1]], fist: [FIST, FIST_LINES, [0.82, 0.02], [1.24, 0]],
    grip: [FIST, FIST_LINES, [0.82, 0.02], [1.24, 0]], point: [POINT, POINT_LINES, [0.82, 0.02], [1.97, -0.23]], pinch: [PINCH, PINCH_LINES, [1.46, -0.2], [1.5, -0.2]] }[k];
  if (side) {
    fig.part(name, ap(side[0]), { fill, z, per: 4 });
    side[1].forEach((l, i) => crease(l, i === 0 ? 0.62 : 0.45));
    return { grip: M.ap(T, side[2]), tip: M.ap(T, side[3]) };
  }
  // 张开的手
  fig.part(name, ap(openOutline(P)), { fill, z, per: 3 });
  // 手指根部的分隔线已经在轮廓里；补两道掌纹般的浅线让手不像手套
  if (o.palmLine !== false) crease([[0.35, -0.12], [0.6, 0.0], [0.72, 0.18]], 0.35, { color: line });
  return { grip: M.ap(T, [0.6, 0]), tip: M.ap(T, [1.9, -0.08]) };
}

// 玉镯（奶奶左腕）
export function bracelet(fig, Mw, size, o) {
  const T = M.chain(Mw, M.s(size));
  fig.part(o.name, M.apAll(T, ellipsePts(-0.12, 0, 0.13, 0.38, 18)), { fill: '#8fc4a0', z: o.z, inner: true, innerLw: 0.6 });
}
export { catmull };
