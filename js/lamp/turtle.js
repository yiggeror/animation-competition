// 乌龟（皮影）：和鹤同一套做法（crane.js 的 part）——每个部件是一片刮薄的牛皮，画成透光率图和皮面图。
// 龟壳拱起、刻六边形甲纹（染深绿，甲缝刻成细缝透光）；脖子三节，能伸长去咬鹤嘴；头上刻眼睛和嘴线；四条腿、尾巴各一片。
// 坐标：毫米，y 朝上，乌龟面朝 +x（上场时 facing = -1 朝左，对着鹤）。部件局部原点 = 和父部件的铆点。
import { part, path, circ } from './crane.js';

function rivet(L, x, y, r = 4) { L.fill(circ(x, y, r), 'line'); L.carve(circ(x, y, r * 0.3)); }

export function makeTurtle(S = 1.3) {
  const s = (v) => v * S;
  const P = (pts) => pts.map(([x, y]) => [x * S, y * S]);
  const parts = [];
  // ================================================================ 龟壳（身子）：拱起的壳 + 下面一道浅色的腹甲边
  parts.push(part('shell', null, [0, 0], 0, [s(-150), s(-40), s(150), s(115)], (L) => {
    const shell = path(P([[135, 8], [122, 46], [90, 82], [40, 102], [-20, 104], [-75, 90], [-115, 60], [-138, 22], [-140, 2], [-100, -6], [0, -8], [100, -6]]));
    L.fill(shell, 'dkgreen');
    // 甲纹：中间一排五块六边形的背甲，两边一圈缘甲；甲缝刻成细缝
    L.clip(shell, () => {
      const hex = (cx, cy, r) => { const p = new Path2D(); for (let k = 0; k < 6; k++) { const a = Math.PI / 6 + (k * Math.PI) / 3; const x = s(cx + Math.cos(a) * r), y = s(cy + Math.sin(a) * r * 0.82); k ? p.lineTo(x, y) : p.moveTo(x, y); } p.closePath(); return p; };
      for (const [cx, cy, r] of [[-82, 52, 24], [-38, 70, 26], [8, 74, 26], [54, 62, 24], [92, 38, 20], [-60, 22, 20], [-15, 32, 22], [32, 30, 22], [75, 14, 16]]) {
        L.fill(hex(cx, cy, r - 3), 'green');
        L.carveLine(hex(cx, cy, r), s(2.0));
        L.carve(circ(s(cx), s(cy), s(2.4)));           // 每块甲中间一个小孔，透一点光
      }
      for (let i = 0; i < 13; i++) {                     // 缘甲：沿着壳边一圈刻缝
        const u = i / 12, a = Math.PI * (0.02 + 0.96 * u);
        const x0 = Math.cos(a) * 134, y0 = Math.sin(a) * 98, x1 = Math.cos(a) * 124, y1 = Math.sin(a) * 88;
        const l = new Path2D(); l.moveTo(s(x0), s(y0)); l.lineTo(s(x1), s(y1)); L.carveLine(l, s(1.8));
      }
    });
    L.stroke(shell, s(3.0));
    // 腹甲：壳下沿一条本色皮，刻一排小方孔
    const belly = path(P([[118, 2], [100, -10], [0, -14], [-100, -10], [-132, 0], [-100, 6], [0, 4], [100, 6]]));
    L.fill(belly, 'leather');
    for (let i = 0; i < 9; i++) { const x = -90 + i * 22; L.carve(path(P([[x - 4, -2], [x + 4, -2], [x + 4, -7], [x - 4, -7]]), true, false)); }
    L.stroke(belly, s(1.8));
    rivet(L, s(110), s(14)); rivet(L, s(-112), s(4));
    for (const [x, y] of [[70, -6], [-70, -6], [60, -8], [-60, -8]]) rivet(L, s(x), s(y), s(3.2));
  }));
  // ================================================================ 脖子三节 + 头
  const NL = s(32);
  for (let k = 0; k < 3; k++) {
    const w = s(15 - k * 1.5);
    parts.push(part('neck' + k, k ? 'neck' + (k - 1) : 'shell', k ? [NL, 0] : [s(110), s(14)], k ? 0.5 + k * 0.1 : -0.5, [-w - 2, -w - 2, NL + w + 2, w + 2], (L) => {
      const seg = path([[-w * 0.9, 0], [-w * 0.6, w * 0.85], [NL * 0.5, w], [NL + w * 0.6, w * 0.85], [NL + w * 0.9, 0], [NL + w * 0.6, -w * 0.85], [NL * 0.5, -w], [-w * 0.6, -w * 0.85]]);
      L.fill(seg, 'leather');
      for (let i = 0; i < 3; i++) { const x = NL * (0.2 + i * 0.3); const l = new Path2D(); l.moveTo(x, -w * 0.7); l.lineTo(x + w * 0.2, w * 0.7); L.carveLine(l, s(1.4)); }   // 颈上的皱褶
      L.stroke(seg, s(1.8));
      rivet(L, 0, 0, s(3));
    }));
  }
  parts.push(part('head', 'neck2', [NL, 0], 1.0, [s(-18), s(-24), s(62), s(30)], (L) => {
    const head = path(P([[-12, -14], [-14, 6], [-2, 22], [20, 26], [42, 20], [56, 8], [58, -4], [48, -14], [24, -20], [4, -20]]));
    L.fill(head, 'leather');
    L.fill(path(P([[2, 16], [20, 23], [40, 18], [30, 10], [12, 9]])), 'green');                 // 头顶一块绿
    L.carve(circ(s(36), s(8), s(5)));                                                              // 眼睛
    L.fill(circ(s(37), s(8), s(2.4)), 'black');
    const mouth = new Path2D(); mouth.moveTo(s(57), s(-4)); mouth.quadraticCurveTo(s(40), s(-10), s(22), s(-6)); L.carveLine(mouth, s(1.8));   // 嘴线
    L.stroke(head, s(2.0));
    rivet(L, 0, 0, s(3));
  }));
  // ================================================================ 四条腿、尾巴
  const leg = (name, at, layer, back) => part(name, 'shell', at, layer, [s(-22), s(-58), s(30), s(10)], (L) => {
    const p = path(P(back ? [[-14, 4], [12, 6], [18, -20], [26, -44], [14, -54], [-4, -50], [-10, -26]] : [[-12, 4], [14, 4], [20, -22], [28, -46], [16, -54], [-2, -50], [-8, -24]]));
    L.fill(p, 'leather');
    for (let k = 0; k < 3; k++) L.fill(path(P([[2 + k * 8, -50], [6 + k * 8, -58], [10 + k * 8, -50]]), true, false), 'black');   // 爪
    L.fill(path(P([[-6, -10], [14, -10], [16, -22], [-4, -22]])), 'dkgreen');                       // 腿上的鳞块
    L.stroke(p, s(1.8));
    rivet(L, 0, 0, s(3));
  });
  parts.push(leg('legFF', [s(60), s(-2)], -1.2, false));
  parts.push(leg('legBF', [s(-70), s(-2)], -1.2, true));
  parts.push(leg('legFN', [s(70), s(-4)], 1.2, false));
  parts.push(leg('legBN', [s(-60), s(-4)], 1.2, true));
  parts.push(part('tail', 'shell', [s(-130), s(2)], -0.8, [s(-40), s(-12), s(4), s(10)], (L) => {
    const p = path(P([[2, 6], [-18, 6], [-36, -2], [-20, -6], [2, -6]]));
    L.fill(p, 'leather'); L.stroke(p, s(1.6)); rivet(L, 0, 0, s(2.8));
  }));
  const map = {};
  for (const p of parts) map[p.part] = p;
  return { name: 'turtle', rig: parts.map(({ part, parent, at, layer }) => ({ part, parent, at, layer })), parts: map };
}

// 乌龟爬：四条腿交替前后摆，身子轻轻起伏，头一伸一缩。t 秒，speed 步/秒；neckOut 0..1 脖子伸出去多少；bite 0..1 张嘴（头往上抬）
export function turtlePose(t, o = {}) {
  const sp = o.speed ?? 1.2, ph = t * sp * Math.PI * 2, walk = o.walk ?? 1;
  const out = o.neckOut ?? 0, angles = {};
  angles.legFN = walk * 0.35 * Math.sin(ph); angles.legBF = walk * 0.35 * Math.sin(ph);
  angles.legFF = walk * 0.35 * Math.sin(ph + Math.PI); angles.legBN = walk * 0.35 * Math.sin(ph + Math.PI);
  angles.tail = 0.15 * Math.sin(ph * 0.5);
  // 脖子：缩着时三节往回折，伸出去时拉直、略往上
  // 缩头：三节折紧，头贴在壳的前沿（第一节往后下、第二节折回来、第三节再折），伸出去时拉直、略往上
  angles.neck0 = -1.5 * (1 - out) + 0.15 * out; angles.neck1 = 2.7 * (1 - out) + 0.05 * out; angles.neck2 = -1.9 * (1 - out);
  angles.head = (o.headTilt ?? 0) + 0.05 * Math.sin(ph) * walk + 0.25 * (o.bite ?? 0);
  return { angles, rootAngle: (o.rootAngle ?? 0) + walk * 0.02 * Math.sin(ph * 2), facing: o.facing ?? -1 };
}
