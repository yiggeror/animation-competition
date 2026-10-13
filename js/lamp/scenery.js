// 皮影的布景片：《龟与鹤》的场景是"宁静的湖面……水面荷花悄悄盛开，岸边杨柳依依低垂"。
// 奶奶的家庭小戏只有几片：床单底边一条水纹、两三片荷叶和一朵荷花、上沿一枝垂柳。
// 和鹤一样是刻花、染色的牛皮，用晾衣夹、别针固定在床单上（奶奶两只手都在操纵鹤），影子由 shadowplay.js 投出来。
import { part, path, circ, feather } from './crane.js';

const one = (name, bounds, draw) => {
  const p = part('p', null, [0, 0], 0, bounds, draw);
  return { name, rig: [{ part: 'p', parent: null, at: [0, 0], layer: 0 }], parts: { p } };
};

// 荷塘：一长条水纹（比床单宽，两头藏在床单外），原点在水面中间；水面以下 300 毫米
export function makePond() {
  return one('pond', [-1300, -320, 1300, 560], (L) => {
    const wave = (x, row) => 9 * Math.sin(x / 46 + row * 1.7);
    const top = []; for (let x = 1300; x >= -1300; x -= 24) top.push([x, wave(x, 2)]);
    const water = path([[-1300, -310], [1300, -310], ...top], true, false);
    L.fill(water, 'blue');
    L.clip(water, () => {
      for (let row = 0; row < 8; row++) {
        const y0 = -22 - row * 36;
        for (let x = -1300; x < 1300; x += 30) { const p = new Path2D(); p.moveTo(x, y0 + wave(x, row)); p.lineTo(x + 30, y0 + wave(x + 30, row)); L.carveLine(p, 8 - row * 0.4); }
        for (let x = -1280 + (row % 2) * 70; x < 1300; x += 140) {
          const y = y0 + wave(x, row) + 11;
          const c = new Path2D(); for (let k = 0; k <= 20; k++) { const a = k * 0.4, r = 2.5 + k * 0.5; const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r * 0.7; k ? c.lineTo(px, py) : c.moveTo(px, py); }
          L.carveLine(c, 2.0);
        }
      }
    });
    L.stroke(path(top, false, false), 3);
    // 两根别针
    for (const x of [-640, 660]) { L.fill(circ(x, -16, 6), 'line'); const nd = new Path2D(); nd.moveTo(x, -16); nd.lineTo(x + 46, -20); L.stroke(nd, 2.2); }
    // 浮在水面上的荷叶（扁椭圆，叶脉镂空）
    const leaf = (x, y, r, sy, tilt) => {
      const pts = [];
      for (let k = 0; k < 30; k++) { const a = (k / 30) * Math.PI * 2; const rr = r * (1 + 0.05 * Math.sin(a * 5)); pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr * sy + Math.cos(a) * r * tilt]); }
      // 叶子上有一道缺口（荷叶从中心裂到边）
      const lp = path(pts, true, true);
      L.fill(lp, 'green'); L.stroke(lp, 3);
      for (let k = 0; k < 13; k++) { const a = (k / 13) * Math.PI * 2 + 0.15, v = new Path2D(); v.moveTo(x, y); v.quadraticCurveTo(x + Math.cos(a) * r * 0.5, y + Math.sin(a) * r * sy * 0.5 + 4, x + Math.cos(a) * r * 0.86, y + Math.sin(a) * r * sy * 0.86 + Math.cos(a) * r * tilt * 0.8); L.carveLine(v, 2.4); }
      L.fill(circ(x, y, 6), 'yellow');
    };
    leaf(-300, 12, 120, 0.28, -0.05);
    leaf(470, 8, 100, 0.26, 0.06);
    // 一片立起来的荷叶（侧着看，像一把半开的伞）和叶柄
    const sx = -720;
    const stem = feather([[sx + 6, -10], [sx + 2, 120], [sx - 4, 230]], 6, 5);
    L.fill(path(stem.outline, true, false), 'dkgreen');
    const up = path([[sx - 120, 236], [sx - 60, 268], [sx, 276], [sx + 70, 266], [sx + 128, 236], [sx + 60, 246], [sx, 250], [sx - 60, 246]]);
    L.fill(up, 'green'); L.stroke(up, 3);
    for (let k = -4; k <= 4; k++) { const v = new Path2D(); v.moveTo(sx, 232); v.lineTo(sx + k * 28, 262 - Math.abs(k) * 4); L.carveLine(v, 2.2); }
    // 一朵开着的荷花：粉色花瓣（刻出瓣脉），中间黄色莲蓬
    const fx = -520, fy = 290;
    const fs = feather([[fx + 18, -10], [fx + 24, 150], [fx, fy - 40]], 5, 4.5);
    L.fill(path(fs.outline, true, false), 'dkgreen');
    const petal = (ang, len, wid) => {
      const tip = [fx + Math.sin(ang) * len, fy + Math.cos(ang) * len];
      const sideA = [fx + Math.sin(ang - 0.35) * len * 0.5, fy + Math.cos(ang - 0.35) * len * 0.5];
      const sideB = [fx + Math.sin(ang + 0.35) * len * 0.5, fy + Math.cos(ang + 0.35) * len * 0.5];
      const pp = path([[fx, fy - 6], sideA, tip, sideB]);
      L.fill(pp, 'pink'); L.stroke(pp, 2.2);
      const v = new Path2D(); v.moveTo(fx + Math.sin(ang) * 14, fy + Math.cos(ang) * 14); v.lineTo(fx + Math.sin(ang) * len * 0.78, fy + Math.cos(ang) * len * 0.78); L.carveLine(v, 1.8);
    };
    for (const a of [-1.15, 1.15]) petal(a, 78, 30);
    for (const a of [-0.62, 0.62]) petal(a, 92, 34);
    L.fill(path([[fx - 26, fy + 18], [fx + 26, fy + 18], [fx + 18, fy - 2], [fx - 18, fy - 2]]), 'yellow');
    for (const dx of [-12, 0, 12]) L.carve(circ(fx + dx, fy + 10, 3));
    petal(0, 98, 34);
  });
}

// 垂柳：一枝柳条，用晾衣夹夹在床单上沿；原点在夹子下面的枝根
export function makeWillow() {
  return one('willow', [-60, -820, 860, 200], (L) => {
    const clip = path([[-14, 30], [16, 30], [14, 150], [-12, 150]], true, false);
    L.fill(clip, 'line');
    L.carve(path([[-4, 112], [5, 112], [5, 122], [-4, 122]], true, false));
    // 枝：从夹子往右上拱起，再慢慢垂下去，越往梢越细；中间分出一根小枝
    const br = feather([[0, 40], [130, 92], [280, 112], [430, 96], [580, 50], [720, -20]], 13, 3);
    L.fill(path(br.outline, true, false), 'brown'); L.stroke(path(br.outline, true, false), 2.4);
    const tw = feather([[300, 108], [380, 150], [470, 160]], 5, 1.5);
    L.fill(path(tw.outline, true, false), 'brown');
    // 柳条：从枝上一根根垂下来，长短不一，都顺着一点风往右飘；梢上的更短更密
    let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const along = (sp, t) => { const i = Math.min(sp.length - 1, Math.floor(t * (sp.length - 1))); return sp[i]; };
    for (let i = 0; i < 15; i++) {
      const t = 0.08 + (i / 14) * 0.9;
      const [x, y] = along(br.spine, t);
      const len = (0.55 + 0.45 * Math.sin(Math.PI * Math.min(1, t * 1.2))) * (520 + rnd() * 280);
      const drift = 40 + rnd() * 50, wob = (rnd() - 0.5) * 30;
      const sp = [[x, y], [x + drift * 0.15 + wob, y - len * 0.3], [x + drift * 0.55 - wob, y - len * 0.65], [x + drift, y - len]];
      const st = feather(sp, 2.6, 1.0);
      L.fill(path(st.outline, true, false), 'dkgreen');
      // 叶子：两头尖的细长条，交替长在两边，斜着往下；越往柳条下面越小
      const line = st.spine;
      for (let k = 3; k < line.length - 1; k += 2) {
        const a = line[k], b = line[k + 1];
        const dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, n = [-dy / d, dx / d], sg = (k >> 1) % 2 ? 1 : -1;
        const u = k / line.length, ll = 44 * (1 - 0.45 * u) * (0.8 + rnd() * 0.4);
        const tip = [a[0] + n[0] * sg * ll * 0.45 + (dx / d) * ll * 0.85, a[1] + n[1] * sg * ll * 0.45 + (dy / d) * ll * 0.85];
        const lf = feather([a, [(a[0] * 0.45 + tip[0] * 0.55) + n[0] * sg * 3, (a[1] * 0.45 + tip[1] * 0.55) + n[1] * sg * 3], tip], 6 * (1 - 0.3 * u), 0.6);
        L.fill(path(lf.outline, true, false), k % 4 === 1 ? 'dkgreen' : 'green');
        if (ll > 30) L.carveLine(path(lf.spine.slice(2, -2), false, false), 1.1);
      }
    }
  });
}
