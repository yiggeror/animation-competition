// 床单上的影子：按真实几何算，不是滤镜凭感觉调。
//
// 马灯在床单后面 D 米处，皮影在床单后面 d 米处（d < D）。从床单正面看：
//   · 影子是皮影的形状，以"灯在床单上的垂足"为中心放大 m = D / (D - d) 倍；
//   · 边缘被光源的大小晕开：光源半径 r 时，半影半宽 = r · d / (D - d)。马灯有两个光源——
//     火苗（r ≈ 1.1 厘米，最亮）和被熏黄、自己发光的玻璃罩（r ≈ 5.5 厘米，暗一些），所以边缘是"一道清楚的边 + 一圈淡晕"；
//   · 彩色牛皮透光：影子里透出牛皮的颜色（染色的地方是彩色的光，没染的薄皮是暖黄的光）；
//   · 签子：一头连着皮影、一头在艺人手里，手在灯旁边，所以签子越往手那头放大越多、越虚，很快就出了床单。
// 床单本身的亮度：点光源照在平面上，照度 ∝ D / r³（r 是灯到床单上那一点的距离），所以中间亮、四周暗；
// 薄棉布还能透出灯的一团亮芯。
import { drawPuppet, solve, pointOn } from './puppet.js';

const POOL = {};
function cv(key, w, h) {
  let c = POOL[key];
  if (!c) c = POOL[key] = new OffscreenCanvas(w, h);
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  const x = c.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.filter = 'none';
  return [c, x];
}

// sheet: { x0, x1, z0, z1 }（米，世界 x 和高度 z）；lamp: { x, z, D, core, globe, coreW, globeW, rgb, I }
// actors: [{ pup, pose, root:[x,z], dist, rods:[{ part, at:[mm], hand:[x, z, dist] }] }]
// 返回一张床单正面的亮度贴图（OffscreenCanvas，k 像素/米）
export function sheetImage(sheet, lamp, actors, k = 520, o = {}) {
  const W = Math.round((sheet.x1 - sheet.x0) * k), H = Math.round((sheet.z1 - sheet.z0) * k);
  const toU = (X) => (X - sheet.x0) * k, toV = (Z) => (sheet.z1 - Z) * k;
  // ---- 1. 每个皮影一张透光图（已经按放大倍数投到床单上），再按两种光源的半影晕开
  const [mask, mx] = cv('mask', W, H);
  mx.fillStyle = '#fff'; mx.fillRect(0, 0, W, H);
  actors.forEach((A, i) => {
    const d = Math.max(0.001, A.dist), D = lamp.D;
    const m = D / (D - d);
    const [one, ox] = cv('one' + (i % 3), W, H);
    ox.fillStyle = '#fff'; ox.fillRect(0, 0, W, H);
    ox.globalCompositeOperation = 'multiply';
    ox.setTransform(1, 0, 0, 1, toU(lamp.x + (A.root[0] - lamp.x) * m), toV(lamp.z + (A.root[1] - lamp.z) * m));
    ox.scale((k * m) / 1000, -(k * m) / 1000);
    drawPuppet(ox, A.pup, A.pose, 't');
    ox.setTransform(1, 0, 0, 1, 0, 0);
    // 签子的影子
    if (A.rods) {
      const sol = solve(A.pup, A.pose);
      const f = A.pose.facing ?? 1;
      for (const R of A.rods) {
        const pm = pointOn(A.pup, sol, R.part, R.at);
        const a = [A.root[0] + (f * pm[0]) / 1000, A.root[1] + pm[1] / 1000, d];
        const b = R.hand;
        const pts = [];
        for (let s = 0; s <= 24; s++) {
          const t = s / 24;
          const P = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
          if (P[2] >= D * 0.97) break;
          const mm = D / (D - P[2]);
          pts.push([toU(lamp.x + (P[0] - lamp.x) * mm), toV(lamp.z + (P[1] - lamp.z) * mm), mm, P[2]]);
        }
        for (let s = 1; s < pts.length; s++) {
          const p0 = pts[s - 1], p1 = pts[s];
          const blur = (lamp.core * p1[3]) / (D - p1[3]) * k;
          ox.save();
          ox.globalCompositeOperation = 'multiply';
          ox.globalAlpha = Math.max(0.15, 0.85 - blur * 0.02);
          ox.filter = `blur(${Math.min(30, blur * 0.5).toFixed(1)}px)`;
          ox.strokeStyle = '#4a3a2c';
          ox.lineWidth = Math.max(1, 0.005 * p1[2] * k);
          ox.lineCap = 'round';
          ox.beginPath(); ox.moveTo(p0[0], p0[1]); ox.lineTo(p1[0], p1[1]); ox.stroke();
          ox.restore();
        }
      }
    }
    // 两种光源的半影：火苗（清楚的边）+ 玻璃罩（一圈淡晕）
    const b1 = ((lamp.core * d) / (D - d)) * k, b2 = ((lamp.globe * d) / (D - d)) * k;
    const [bl, bx] = cv('blur', W, H);
    bx.filter = `blur(${Math.max(0.3, b1 * 0.55).toFixed(2)}px)`;
    bx.drawImage(one, 0, 0);
    bx.filter = `blur(${Math.max(0.5, b2 * 0.55).toFixed(2)}px)`;
    bx.globalAlpha = lamp.globeW / (lamp.coreW + lamp.globeW);
    bx.drawImage(one, 0, 0);
    mx.globalCompositeOperation = 'multiply';
    mx.drawImage(bl, 0, 0);
  });
  // ---- 2. 床单被灯照透的亮度
  const [img, ix] = cv('sheet', W, H);
  const lu = toU(lamp.x), lv = toV(lamp.z), Dk = lamp.D * k;
  // 照度 ∝ (D/r)³：用分段的径向渐变近似
  const R = Math.max(W, H) * 1.4;
  const g = ix.createRadialGradient(lu, lv, 0, lu, lv, R);
  for (let s = 0; s <= 12; s++) {
    const rr = (s / 12) * R;
    const e = Math.pow(Dk / Math.hypot(Dk, rr), 3);
    const v = Math.min(1, lamp.I * e);
    g.addColorStop(s / 12, `rgb(${lamp.rgb.map((c) => Math.round(c * v)).join(',')})`);
  }
  ix.fillStyle = g; ix.fillRect(0, 0, W, H);
  // 灯的亮芯透过薄棉布
  const hot = ix.createRadialGradient(lu, lv, 0, lu, lv, 0.16 * k);
  hot.addColorStop(0, `rgba(255,248,225,${0.55 * (o.hot ?? 1)})`);
  hot.addColorStop(0.35, `rgba(255,236,190,${0.2 * (o.hot ?? 1)})`);
  hot.addColorStop(1, 'rgba(255,230,180,0)');
  ix.globalCompositeOperation = 'lighter';
  ix.fillStyle = hot; ix.fillRect(0, 0, W, H);
  // 折痕（叠放多年的床单）和布纹
  ix.globalCompositeOperation = 'multiply';
  ix.strokeStyle = 'rgba(150,120,90,0.06)';
  ix.lineWidth = 2;
  for (const u of [W / 3, (2 * W) / 3]) { ix.beginPath(); ix.moveTo(u + 3, 0); ix.lineTo(u - 4, H); ix.stroke(); }
  for (const v of [H / 2]) { ix.beginPath(); ix.moveTo(0, v); ix.lineTo(W, v + 5); ix.stroke(); }
  // ---- 3. 乘上影子
  ix.drawImage(mask, 0, 0);
  return { canvas: img, W, H, k };
}
