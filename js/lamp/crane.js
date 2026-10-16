// 鹤（皮影）：每个部件是一片刮薄的牛皮，画成"透光率图"——
//   没染色的薄牛皮透出琥珀色的暖光；染色的地方透出颜色（朱红、青绿、黄、橄榄）；染黑的地方几乎不透光；
//   镂空（刻掉）的地方光直接穿过去，最亮。床单上的影子由 shadowplay.js 按真实几何投出来，颜色就是这些透光率。
// 骨架和原来的鹤一致（身子、12 节脖子、头、两条腿），所以动作代码不用改；整只放大到约 1.35 倍。
// 坐标：毫米，y 朝上，鹤面朝 +x。部件局部原点 = 和父部件的铆点。

const PPMM = 4;   // 贴图每毫米像素
// 透光率（sRGB）
export const T = {
  leather: 'rgb(236,196,138)', leatherEdge: 'rgb(196,140,80)',
  red: 'rgb(238,58,36)', black: 'rgb(26,20,16)', olive: 'rgb(200,196,74)', teal: 'rgb(96,196,172)',
  green: 'rgb(110,190,80)', yellow: 'rgb(252,214,90)', line: 'rgb(48,30,18)',
  blue: 'rgb(110,170,220)', pink: 'rgb(250,150,170)', dkgreen: 'rgb(50,110,60)', brown: 'rgb(120,70,40)',
};
// 从后台看的皮面颜色（反射）
const R = {
  leather: 'rgb(150,104,58)', red: 'rgb(170,40,28)', black: 'rgb(24,18,14)', olive: 'rgb(128,120,44)', teal: 'rgb(44,110,96)',
  green: 'rgb(60,110,40)', yellow: 'rgb(186,146,50)', line: 'rgb(30,20,12)',
  blue: 'rgb(50,90,130)', pink: 'rgb(170,80,100)', dkgreen: 'rgb(30,64,36)', brown: 'rgb(80,46,26)',
};

export function spline(pts, closed = true, per = 8) {
  const n = pts.length, out = [], last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const a = closed || i > 0 ? p0 : p1, d = closed || i < n - 2 ? p3 : p2;
    for (let j = 0; j < per; j++) {
      const t = j / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((k) => 0.5 * (2 * p1[k] + (p2[k] - a[k]) * t + (2 * a[k] - 5 * p1[k] + 4 * p2[k] - d[k]) * t2 + (3 * p1[k] - a[k] - 3 * p2[k] + d[k]) * t3)));
    }
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
}
export function path(pts, closed = true, smooth = true) {
  const q = smooth ? spline(pts, closed) : pts;
  const p = new Path2D(); q.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y)));
  if (closed) p.closePath();
  return p;
}
export const circ = (cx, cy, r) => { const p = new Path2D(); p.arc(cx, cy, r, 0, Math.PI * 2); return p; };
// 一根长羽：沿脊线两侧加宽度（leaf）
export function feather(spine, w0, w1 = 0) {
  const sp = spline(spine, false, 10), L = [], Rr = [];
  sp.forEach((p, i) => {
    const a = sp[Math.max(0, i - 1)], b = sp[Math.min(sp.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1]; const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
    const u = i / (sp.length - 1), w = (w0 + (w1 - w0) * u) * Math.sin(Math.PI * Math.min(1, 0.15 + u * 0.95)) ** 0.6;
    L.push([p[0] - dy * w, p[1] + dx * w]); Rr.push([p[0] + dy * w, p[1] - dx * w]);
  });
  return { outline: [...L, ...Rr.reverse()], spine: sp };
}

// 一个部件：draw(L) 里用 L.fill / L.carve / L.stroke / L.dot 画，同时生成透光图和皮面图
export function part(name, parent, at, layer, bounds, draw) {
  const [x0, y0, x1, y1] = bounds;
  const W = Math.ceil((x1 - x0) * PPMM), H = Math.ceil((y1 - y0) * PPMM);
  const mk = () => { const c = new OffscreenCanvas(W, H); const x = c.getContext('2d'); x.setTransform(PPMM, 0, 0, -PPMM, -x0 * PPMM, y1 * PPMM); return [c, x]; };
  const [tc, tx] = mk(), [rc, rx] = mk();
  const L = {
    fill(p, key) { tx.fillStyle = T[key] || key; tx.fill(p); rx.fillStyle = R[key] || key; rx.fill(p); },
    carve(p) { for (const x of [tx, rx]) { x.save(); x.globalCompositeOperation = 'destination-out'; x.fill(p); x.restore(); } },
    carveLine(p, w) { for (const x of [tx, rx]) { x.save(); x.globalCompositeOperation = 'destination-out'; x.lineWidth = w; x.lineCap = 'round'; x.lineJoin = 'round'; x.stroke(p); x.restore(); } },
    stroke(p, w, key = 'line') { tx.strokeStyle = T[key] || key; rx.strokeStyle = R[key] || key; for (const x of [tx, rx]) { x.lineWidth = w; x.lineCap = 'round'; x.lineJoin = 'round'; x.stroke(p); } },
    clip(p, fn) { tx.save(); rx.save(); tx.clip(p); rx.clip(p); fn(); tx.restore(); rx.restore(); },
  };
  draw(L);
  return { part: name, parent, at, layer, bounds, t: tc, r: rc };
}
// 枢钉：深色小疙瘩，中间钉孔透一点光
function rivet(L, x, y, r = 4.5) { L.fill(circ(x, y, r), 'line'); L.carve(circ(x, y, r * 0.3)); }
// 鱼鳞纹：一排排小弧线刻成细缝
function scales(L, region, x0, x1, y0, y1, r, w) {
  L.clip(region, () => {
    for (let row = 0, y = y1; y > y0; y -= r * 0.9, row++) {
      for (let x = x0 + (row % 2) * r; x < x1; x += r * 2) {
        const p = new Path2D(); p.arc(x, y, r, Math.PI * 1.08, Math.PI * 1.92); L.carveLine(p, w);
      }
    }
  });
}

// palette：'plain' 素（只有本色、黑、丹顶的红，像真的丹顶鹤）| 'rich' 艳（覆羽染青绿、云纹染黄）
export function makeCrane(S = 1.35, palette = 'plain') {
  const rich = palette === 'rich';
  const s = (v) => v * S;
  const P = (pts) => pts.map(([x, y]) => [x * S, y * S]);
  const parts = [];

  // ================================================================ 身子（含翅膀、尾部垂下来的黑色长羽）
  parts.push(part('body', null, [0, 0], 0.0, [s(-345), s(-175), s(160), s(100)], (L) => {
    const body = path(P([[148, 22], [132, 48], [100, 64], [50, 72], [-20, 66], [-90, 50], [-150, 28], [-195, 8], [-185, -8], [-140, -24], [-70, -44], [0, -56], [60, -58], [112, -46], [146, -22], [156, 0]]));
    L.fill(body, 'leather');
    // 胸前、肚子：鱼鳞纹镂空
    scales(L, body, s(-200), s(160), s(-80), s(90), s(11.5), s(1.6));   // 鱼鳞比翅膀上的羽纹大一号，远看两块分得开
    // 外沿一道深色描边（皮子边上刷的墨线）
    L.stroke(body, s(3.2));
    // 翅膀（收拢贴在身上）：叶形外框
    const wing = path(P([[104, 46], [66, 60], [0, 60], [-90, 44], [-165, 20], [-198, 2], [-150, -8], [-60, -20], [30, -18], [90, 4], [112, 28]]));
    L.fill(wing, 'leather');
    // 覆羽：三排青绿色的扇贝羽
    L.clip(wing, () => {
      for (let row = 0; row < 4; row++) {
        for (let i = 0; i < 13; i++) {
          const cx = 88 - i * 19 - row * 9.5, cy = 42 - row * 13 - i * 1.0;
          if (cx < -150 || cx > 96) continue;
          const sc = path(P([[cx + 9.5, cy + 4], [cx, cy + 8], [cx - 9.5, cy + 4], [cx - 11, cy - 4], [cx, cy - 11], [cx + 11, cy - 4]]));
          L.fill(sc, rich ? (row % 2 ? 'green' : 'teal') : 'leather');
          L.stroke(sc, s(1.3));
          const v = new Path2D(); v.moveTo(s(cx), s(cy + 5)); v.lineTo(s(cx), s(cy - 7)); L.carveLine(v, s(1.2));
        }
      }
      // 飞羽：下沿一排长条，本色皮、刻出羽轴
      for (let i = 0; i < 10; i++) {
        const x = 50 - i * 22;
        const f = feather(P([[x + 18, -2], [x - 10, -9], [x - 40, -12]]), s(6.5), s(2.5));
        L.fill(path(f.outline, true, false), 'leather');
        L.stroke(path(f.outline, true, false), s(1.4));
        L.carveLine(path(f.spine, false, false), s(1.3));
      }
    });
    L.stroke(wing, s(3.6));   // 主翼的外框比里面的花纹粗，远看先读出翅膀
    // 翅膀上沿一排小菱形镂空
    for (let i = 0; i < 11; i++) { const x = 70 - i * 18, y = 50 - (i > 5 ? (i - 5) * 4.5 : 0) + (i < 2 ? -3 : 0); const d = path(P([[x, y + 3], [x + 3, y], [x, y - 3], [x - 3, y]]), true, false); L.carve(d); }
    // 肩上的云纹（如意头）：黄色，镂空的旋涡
    const cloud = path(P([[96, 44], [82, 60], [60, 62], [44, 50], [48, 34], [64, 28], [80, 32], [92, 28]]));
    L.fill(cloud, rich ? 'yellow' : 'leather');
    L.stroke(cloud, s(2));
    const sw = new Path2D(); for (let k = 0; k <= 40; k++) { const a = k * 0.32, r = 3 + k * 0.42; const x = 66 + Math.cos(a) * r, y = 46 + Math.sin(a) * r * 0.8; k ? sw.lineTo(s(x), s(y)) : sw.moveTo(s(x), s(y)); }
    L.carveLine(sw, s(2.2));
    L.fill(circ(s(80), s(40), s(4)), 'red');
    // 背上一排小梅花孔
    for (let i = 0; i < 6; i++) { const x = 20 - i * 30, y = 74 - i * 5 - (i > 3 ? (i - 3) * 8 : 0); for (let k = 0; k < 5; k++) { const a = (k / 5) * Math.PI * 2; L.carve(circ(s(x + Math.cos(a) * 3.2), s(y + Math.sin(a) * 3.2), s(1.9))); } }
    // 尾部垂下来的黑色长羽（丹顶鹤的三级飞羽）：9 根，先拱起再垂下，刻出羽轴和羽枝
    for (let i = 0; i < 9; i++) {
      const bx = -30 - i * 15, by = 38 - i * 2.5;
      const tip = [-250 - i * 9 + (i % 2) * 10, -60 - i * 11];
      const f = feather(P([[bx, by], [bx - 46, by + 22 - i * 1.5], [bx - 110 + i * 3, by + 4 - i * 3], tip]), s(14 - i * 0.6), s(2));
      const fp = path(f.outline, true, false);
      L.fill(fp, 'black');
      L.carveLine(path(f.spine.slice(5, -3), false, false), s(1.5));
      for (let k = 7; k < f.spine.length - 5; k += 3) {
        const a = f.spine[k], b = f.spine[k + 1], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1;
        const n = [-dy / d, dx / d], len = s(9 - i * 0.4) * (1 - k / f.spine.length);
        for (const sg of [1, -1]) { const l = new Path2D(); l.moveTo(a[0] + n[0] * sg * 2, a[1] + n[1] * sg * 2); l.lineTo(a[0] + n[0] * sg * len - (dx / d) * len * 0.9, a[1] + n[1] * sg * len - (dy / d) * len * 0.9); L.carveLine(l, s(1.0)); }
      }
    }
    rivet(L, s(113), s(43));
    rivet(L, s(-3), s(-54));
    rivet(L, s(13), s(-51));
  }));

  // ================================================================ 脖子：12 节，下面 4 节白（本色）、上面黑，背后留一道白
  const NL = 21 * S, N = 12;
  for (let k = 0; k < N; k++) {
    const w = s(13 - k * 0.36);
    parts.push(part('neck' + k, k ? 'neck' + (k - 1) : 'body', k ? [NL, 0] : [s(113), s(43)], 0.6 + 0.12 * k, [-w - 2, -w - 2, NL + w + 2, w + 2], (L) => {
      const seg = path([[-w * 0.9, 0], [-w * 0.6, w * 0.85], [NL * 0.5, w], [NL + w * 0.6, w * 0.85], [NL + w * 0.9, 0], [NL + w * 0.6, -w * 0.85], [NL * 0.5, -w], [-w * 0.6, -w * 0.85]]);
      L.fill(seg, k < 4 ? 'leather' : 'black');
      if (k >= 4) { const back = path([[-w * 0.5, w * 0.35], [NL * 0.5, w * 0.55], [NL + w * 0.5, w * 0.35], [NL + w * 0.5, w * 0.8], [NL * 0.5, w * 0.95], [-w * 0.5, w * 0.8]]); L.fill(back, 'leather'); }
      else { for (let i = 0; i < 3; i++) L.carve(circ(NL * (0.2 + i * 0.3), (i % 2 ? -1 : 1) * w * 0.35, w * 0.16)); }
      L.stroke(seg, s(1.6));
      rivet(L, 0, 0, s(3.2));
    }));
  }
  // ================================================================ 头：朱红的丹顶、黑脸、眼睛后面一道白、长喙
  parts.push(part('head', 'neck' + (N - 1), [NL, 0], 2.4, [s(-22), s(-26), s(140), s(34)], (L) => {
    const head = path(P([[-14, -10], [-16, 6], [-8, 20], [8, 26], [26, 22], [38, 12], [44, 4], [40, -8], [24, -16], [4, -18]]));
    L.fill(head, 'black');
    const white = path(P([[-14, -6], [-12, 8], [-4, 16], [4, 12], [0, 0], [-4, -10]]));
    L.fill(white, 'leather');
    const crown = path(P([[-4, 18], [8, 26], [26, 23], [36, 14], [24, 12], [8, 13]]));
    L.fill(crown, 'red');
    for (const [x, y] of [[10, 20], [18, 21], [26, 18]]) L.carve(circ(s(x), s(y), s(1.6)));
    // 喙：上下两片，中间一道刻缝
    const beak = path(P([[38, 10], [80, 6], [136, 1], [80, -2], [40, -8], [44, 2]]), true, false);
    L.fill(beak, 'olive');
    L.stroke(beak, s(1.6));
    const bl = new Path2D(); bl.moveTo(s(44), s(1)); bl.lineTo(s(126), s(1)); L.carveLine(bl, s(1.0));
    // 眼睛：刻一圈，中间留一点
    L.carve(circ(s(24), s(5), s(5.2)));
    L.fill(circ(s(24), s(5), s(2.4)), 'black');
    L.stroke(head, s(1.8));
    rivet(L, 0, 0, s(3.2));
  }));
  // ================================================================ 腿：黑色细长，膝盖一个疙瘩，三个脚趾
  const legPart = (name, parent, at, layer, len, w, tone) => part(name, parent, at, layer, [-w - 4, -len - 6, w + 4, w + 4], (L) => {
    const p = path([[-w, 0], [-w * 0.7, -len * 0.5], [-w * 0.9, -len], [w * 0.9, -len], [w * 0.7, -len * 0.5], [w, 0]]);
    L.fill(p, tone); L.fill(circ(0, -len, w * 1.15), tone); rivet(L, 0, 0, w * 0.6);
  });
  for (const side of ['far', 'near']) {
    const far = side === 'far', base = far ? -1.2 : 1.0;
    parts.push(legPart('tibia_' + side, 'body', far ? [s(13), s(-51)] : [s(-3), s(-54)], base, s(86), s(7), 'black'));
    parts.push(legPart('tarsus_' + side, 'tibia_' + side, [0, s(-86)], base - 0.1 * (far ? 1 : -1), s(100), s(5), 'black'));
    parts.push(part('foot_' + side, 'tarsus_' + side, [0, s(-100)], base - 0.2 * (far ? 1 : -1), [s(-30), s(-14), s(62), s(10)], (L) => {
      for (const tip of [[56, -8], [40, -10], [-24, -6]]) { const f = feather(P([[0, 0], [tip[0] * 0.5, tip[1] * 0.7], tip]), s(3.6), s(1.2)); L.fill(path(f.outline, true, false), 'black'); }
      rivet(L, 0, 0, s(3));
    }));
  }
  const map = {};
  for (const p of parts) map[p.part] = p;
  return { name: 'crane2', rig: parts.map(({ part, parent, at, layer }) => ({ part, parent, at, layer })), parts: map };
}
