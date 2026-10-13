// 皮影的布景片：荷塘（水波、荷叶、荷花苞、芦苇）和一枝松。和鹤一样是刻花、染色的牛皮，贴着床单，
// 影子由 shadowplay.js 投出来。每片只有一个部件（不动的布景），用 crane.js 里同一套画法。
import { part, path, circ, feather, spline } from './crane.js';

const one = (name, bounds, draw) => {
  const p = part('p', null, [0, 0], 0, bounds, draw);
  return { name, rig: [{ part: 'p', parent: null, at: [0, 0], layer: 0 }], parts: { p } };
};

// 荷塘：宽约 1.5 米、高约 0.5 米，原点在下沿中间
export function makePond() {
  return one('pond', [-1300, -340, 1300, 520], (L) => {
    // 水：一长条，比床单还宽（两头藏在床单外面）；青蓝色，大半刻成一道道镂空的水纹，光能透过来
    const wave = (x, row) => 14 * Math.sin(x / 48 + row * 1.7);
    const top = []; for (let x = 1300; x >= -1300; x -= 24) top.push([x, 120 + wave(x, 2)]);
    const water = path([[-1300, -330], [1300, -330], ...top], true, false);
    L.fill(water, 'blue');
    L.clip(water, () => {
      for (let row = 0; row < 9; row++) {
        const y0 = 100 - row * 34;
        for (let x = -1300; x < 1300; x += 30) {
          const p = new Path2D(); p.moveTo(x, y0 + wave(x, row)); p.lineTo(x + 30, y0 + wave(x + 30, row));
          L.carveLine(p, 9 - row * 0.4);
        }
        for (let x = -1280 + (row % 2) * 60; x < 1300; x += 120) {
          const y = y0 + wave(x, row) + 12;
          const c = new Path2D(); for (let k = 0; k <= 22; k++) { const a = k * 0.4, r = 2.5 + k * 0.5; const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r * 0.7; k ? c.lineTo(px, py) : c.moveTo(px, py); }
          L.carveLine(c, 2.2);
        }
      }
    });
    L.stroke(path(top, false, false), 3);
    // 两根别针把水纹条别在床单上
    for (const x of [-560, 600]) {
      L.fill(circ(x, 92, 6), 'line');
      const nd = new Path2D(); nd.moveTo(x, 92); nd.lineTo(x + 46, 88); L.stroke(nd, 2.2);
    }
    // 芦苇：细长的秆、两三片叶子、顶上一穗
    for (const [x, h, lean] of [[-640, 400, -0.15], [-600, 470, -0.05], [-560, 360, 0.08], [520, 430, 0.12], [580, 360, 0.2], [640, 480, 0.02]]) {
      const top = [x + lean * h, 150 + h];
      const st = feather([[x, 120], [x + lean * h * 0.4, 120 + h * 0.5], top], 4, 2.4);
      L.fill(path(st.outline, true, false), 'brown');
      for (const k of [0.3, 0.5, 0.7]) {
        const b = [x + lean * h * k, 120 + h * k], sg = k === 0.5 ? -1 : 1;
        const lf = feather([b, [b[0] + sg * 50, b[1] + 70], [b[0] + sg * 110, b[1] + 60]], 9, 1);
        L.fill(path(lf.outline, true, false), 'dkgreen');
        L.carveLine(path(lf.spine.slice(2, -2), false, false), 1.5);
      }
      const plume = feather([top, [top[0] + lean * 40, top[1] + 50], [top[0] + lean * 60 + 4, top[1] + 96]], 13, 3);
      L.fill(path(plume.outline, true, false), 'brown');
      for (let k = 2; k < plume.spine.length - 2; k += 2) L.carve(circ(plume.spine[k][0], plume.spine[k][1], 2.0));
    }
    // 荷叶：圆的大叶子，叶脉镂空（放射状），叶柄
    for (const [x, y, r, tilt] of [[-420, 190, 120, -0.25], [-250, 150, 84, 0.3], [330, 175, 110, 0.2], [180, 140, 70, -0.3]]) {
      const stem = feather([[x + 10, 60], [x + 4, (60 + y) / 2], [x, y - r * 0.2]], 6, 5);
      L.fill(path(stem.outline, true, false), 'dkgreen');
      const leaf = [];
      for (let k = 0; k < 28; k++) { const a = (k / 28) * Math.PI * 2; const rr = r * (1 + 0.06 * Math.sin(a * 5)); leaf.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr * 0.46 + Math.cos(a) * r * tilt * 0.4]); }
      const lp = path(leaf, true, true);
      L.fill(lp, 'green');
      L.stroke(lp, 3);
      for (let k = 0; k < 11; k++) {
        const a = (k / 11) * Math.PI * 2 + 0.2, v = new Path2D();
        v.moveTo(x, y); v.quadraticCurveTo(x + Math.cos(a) * r * 0.5, y + Math.sin(a) * r * 0.2 + 6, x + Math.cos(a) * r * 0.86, y + Math.sin(a) * r * 0.4 + Math.cos(a) * r * tilt * 0.35);
        L.carveLine(v, 2.6);
      }
      L.fill(circ(x, y, 7), 'yellow');
    }
    // 荷花苞：粉色，花瓣上刻纹
    const bx = -80, by = 300;
    const st = feather([[bx + 20, 30], [bx + 30, 180], [bx, by - 30]], 5, 4.5);
    L.fill(path(st.outline, true, false), 'dkgreen');
    for (const [dx, sc] of [[-26, 0.8], [26, 0.8], [0, 1]]) {
      const pet = path([[bx + dx * 0.4, by - 34], [bx + dx * 1.6 - 22 * sc, by + 10], [bx + dx * 0.8, by + 80 * sc], [bx + dx * 1.6 + 22 * sc, by + 10]]);
      L.fill(pet, 'pink'); L.stroke(pet, 2.4);
      const v = new Path2D(); v.moveTo(bx + dx * 0.5, by - 20); v.lineTo(bx + dx * 0.85, by + 56 * sc); L.carveLine(v, 2);
    }
  });
}

// 松枝：从左上角伸进来，原点在枝根
export function makePine() {
  return one('pine', [-40, -360, 760, 160], (L) => {
    // 用一个晾衣夹夹在床单上沿（奶奶两只手都要操纵鹤，布景得自己挂住）
    const clip = path([[-14, 30], [16, 30], [14, 150], [-12, 150]], true, false);
    L.fill(clip, 'line');
    L.carve(path([[-4, 112], [5, 112], [5, 122], [-4, 122]], true, false));
    const br = feather([[0, 60], [200, 30], [380, -40], [560, -60], [720, -120]], 22, 7);
    L.fill(path(br.outline, true, false), 'brown');
    L.stroke(path(br.outline, true, false), 3);
    for (let k = 4; k < br.spine.length - 4; k += 9) L.carveLine(path([br.spine[k], [br.spine[k][0] + 10, br.spine[k][1] - 4]], false, false), 2);
    // 松针：一簇簇扇形，深绿，刻出针
    for (const [x, y, r, a0] of [[120, 40, 90, -0.3], [260, -10, 110, 0.1], [420, -70, 100, -0.2], [560, -90, 95, 0.25], [690, -140, 80, -0.1], [330, -120, 80, 0.6], [500, -190, 85, 0.3]]) {
      const fan = [[x, y]];
      for (let k = 0; k <= 16; k++) { const a = a0 - 1.25 + (k / 16) * 2.5; fan.push([x + Math.cos(a - Math.PI / 2) * r, y + Math.sin(a - Math.PI / 2) * r]); }
      const fp = path(fan, true, false);
      L.fill(fp, 'green');
      for (let k = 1; k < 24; k++) { const a = a0 - 1.25 + (k / 24) * 2.5, v = new Path2D(); v.moveTo(x + Math.cos(a - Math.PI / 2) * r * 0.18, y + Math.sin(a - Math.PI / 2) * r * 0.18); v.lineTo(x + Math.cos(a - Math.PI / 2) * r * 0.95, y + Math.sin(a - Math.PI / 2) * r * 0.95); L.carveLine(v, 2.2); }
      L.stroke(fp, 2.4);
    }
  });
}
