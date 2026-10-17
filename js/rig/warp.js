// 骨架变形（"生图形象做皮，代码骨架做动作"）：一张人物图绑一副 2D 骨架，图切成细三角网格，
// 每个顶点按到各骨头的距离分权重（线性混合蒙皮），骨头转动时图跟着连续变形——类似 Live2D / Spine 的网格变形。
// 绑骨数据：assets/rigs/<图名>.rig.json（格式见 collab/claude.md 2026-10-17 08:55）：
//   bones: [{ name, parent, head:[x,y], tail:[x,y] }]（原图像素；head 是关节）
//   layers: [{ name, bones:[...], poly:[[x,y]...], z }]（叠在身体前、要单独动的部分，切成单独一层，只受这些骨头影响）
//   regions: [{ bones:[...], poly:[[x,y]...] }]（这块范围里的顶点只受这几根骨头影响，例如盆、凳子、贴地的腿）
//   pins: [[x,y]... 或 { at:[x,y], bone?, r? }]（钉点：半径 r 里的网格顶点整个绑在 bone（默认 root）上，不随别的骨头动，例如贴地的膝盖、手肘）
//   刚体：手机、盆这类不能弯的东西用 regions 只绑一根骨头（手机绑在 phone 骨上，握手机的手指也绑这根），整块一起转
// 姿势：{ 骨名: { rot（弧度，相对绑定姿势）, sx?, sy?（沿骨头方向/垂直方向的伸缩，呼吸用）, dx?, dy?（只对 root） } }
// 表情：pose.__face = loadFace(...) 的结果（和原图逐像素对齐的表情头，只取脸的范围）—— 贴在同一网格上，跟着头动。
// 眨眼：pose.__blink = 0..1（rig.eyes 给眼睛的位置和大小，程序画眼皮）。
// 输出：和原图同尺寸的画布（透明底），可以直接当 paintshot 的图层或 cards 的固有色用。
const VS = `#version 300 es
in vec2 aRest; in vec4 aW; in vec4 aI; out vec2 vUV;
uniform mat3 uB[32]; uniform vec2 uSize;
void main() {
  vec3 p = vec3(aRest, 1.0), q = vec3(0.0);
  for (int k = 0; k < 4; k++) q += aW[k] * (uB[int(aI[k])] * p);
  vUV = aRest / uSize;
  gl_Position = vec4(q.x / uSize.x * 2.0 - 1.0, 1.0 - q.y / uSize.y * 2.0, 0.0, 1.0);
}`;
const FS = `#version 300 es
precision highp float; in vec2 vUV; uniform sampler2D uTex; out vec4 o;
void main() { o = texture(uTex, vUV); }`;

const segDist = (p, a, b) => {
  const vx = b[0] - a[0], vy = b[1] - a[1], wx = p[0] - a[0], wy = p[1] - a[1];
  const L = vx * vx + vy * vy, u = L > 0 ? Math.max(0, Math.min(1, (wx * vx + wy * vy) / L)) : 0;
  return Math.hypot(wx - u * vx, wy - u * vy);
};
const inPoly = (p, poly) => {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > p[1]) !== (yj > p[1]) && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
};
// 3×3 仿射（列主序给 GLSL）：[a c e; b d f; 0 0 1]
const mul = (A, B) => [A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3], A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5]];
const rotAbout = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [c, s, -s, c, p[0] - c * p[0] + s * p[1], p[1] - s * p[0] - c * p[1]]; };
const transl = (dx, dy) => [1, 0, 0, 1, dx, dy];
// 沿骨头方向 sx、垂直方向 sy 的伸缩（以关节为中心）
function stretch(head, tail, sx, sy) {
  const ang = Math.atan2(tail[1] - head[1], tail[0] - head[0]);
  return mul(rotAbout(head, ang), mul([sx, 0, 0, sy, head[0] - sx * head[0], head[1] - sy * head[1]], rotAbout(head, -ang)));
}
const apply = (M, p) => [M[0] * p[0] + M[2] * p[1] + M[4], M[1] * p[0] + M[3] * p[1] + M[5]];

// 绑骨：算网格和权重（每张图只算一次）
export function bind(img, rig, o = {}) {
  const W = img.width, H = img.height, step = o.step ?? 10, falloff = o.falloff ?? 3;
  const bones = rig.bones, idx = Object.fromEntries(bones.map((b, i) => [b.name, i]));
  // 透明度：只在人物上（含一圈余量）铺网格
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d'); x.drawImage(img, 0, 0);
  const A = x.getImageData(0, 0, W, H).data, alphaAt = (px, py) => A[(Math.min(H - 1, Math.max(0, py | 0)) * W + Math.min(W - 1, Math.max(0, px | 0))) * 4 + 3];
  const layerDefs = [{ name: 'body', bones: null, poly: null, z: 0 }, ...(rig.layers || [])];
  const layers = [];
  for (const L of layerDefs) {
    const allowed = L.bones ? L.bones.map((n) => idx[n]) : bones.map((_, i) => i).filter((i) => !(rig.layers || []).some((l) => l.exclusive && l.bones.includes(bones[i].name)));
    const nx = Math.ceil(W / step) + 1, ny = Math.ceil(H / step) + 1, vid = new Int32Array(nx * ny).fill(-1);
    const nb = bones.length, rest = [], full = [], fixed = [], grid = [];
    const inLayer = (p) => (L.poly ? inPoly(p, L.poly) : !(rig.layers || []).some((l) => inPoly(p, l.poly)));
    const used = (gx, gy) => {   // 这个格子里有不透明像素、并且属于这一层
      for (let yy = gy * step; yy <= (gy + 1) * step; yy += step / 2) for (let xx = gx * step; xx <= (gx + 1) * step; xx += step / 2) if (alphaAt(xx, yy) > 8 && inLayer([xx, yy])) return true;
      return false;
    };
    const tris = [];
    for (let gy = 0; gy < ny - 1; gy++) for (let gx = 0; gx < nx - 1; gx++) {
      if (!used(gx, gy)) continue;
      const corner = [[gx, gy], [gx + 1, gy], [gx + 1, gy + 1], [gx, gy + 1]].map(([u, v]) => {
        const k = v * nx + u;
        if (vid[k] < 0) {
          vid[k] = rest.length / 2; const p = [u * step, v * step]; rest.push(p[0], p[1]); grid.push(k);
          // 权重：到每根允许的骨头线段的距离，w = 1 / (d + 6)^falloff。
          // regions：落在某个多边形里的顶点只受那几根骨头影响（盆、凳子、贴地的腿不被胳膊和身子带着变形），这些顶点的权重固定不平滑
          // pins：钉点附近（半径 r，默认 24 像素）的顶点整个绑在一根骨头上（默认 root），例如贴在竹席上的手肘、膝盖
          const pin = (rig.pins || []).map((q) => (Array.isArray(q) ? { at: q } : q)).find((q) => Math.hypot(p[0] - q.at[0], p[1] - q.at[1]) < (q.r ?? 24));
          const reg = pin ? { bones: [pin.bone || 'root'] } : (rig.regions || []).find((r) => inPoly(p, r.poly));
          const cand = reg ? reg.bones.map((n) => idx[n]).filter((bi) => allowed.includes(bi)) : allowed;
          const wv = new Float32Array(nb);
          for (const bi of cand.length ? cand : allowed) wv[bi] = 1 / Math.pow(segDist(p, bones[bi].head, bones[bi].tail) + 6, falloff);
          const sum = wv.reduce((a, b) => a + b, 0); for (let q = 0; q < nb; q++) wv[q] /= sum;
          full.push(wv); fixed.push(!!reg);
        }
        return vid[k];
      });
      tris.push(corner[0], corner[1], corner[2], corner[0], corner[2], corner[3]);
    }
    // 权重平滑：不在 regions 里的顶点和上下左右邻居取平均，几轮下来分界处是渐变的，骨头转动时三角形不会被撕开
    const nv = full.length;
    for (let it = 0; it < (o.smooth ?? 8); it++) {
      const nxt = full.map((w) => w.slice());
      for (let v = 0; v < nv; v++) {
        if (fixed[v]) continue;
        const k = grid[v], acc = full[v].slice(); let n = 1;
        for (const kk of [k - 1, k + 1, k - nx, k + nx]) { const u = kk >= 0 ? vid[kk] : -1; if (u >= 0) { for (let q = 0; q < nb; q++) acc[q] += full[u][q]; n++; } }
        for (let q = 0; q < nb; q++) nxt[v][q] = acc[q] / n;
      }
      for (let v = 0; v < nv; v++) full[v] = nxt[v];
    }
    const wts = new Float32Array(nv * 4), ids = new Float32Array(nv * 4);
    for (let v = 0; v < nv; v++) {   // 每个顶点留最大的 4 根骨头
      const top = Array.from(full[v], (w, q) => [q, w]).sort((m, n) => n[1] - m[1]).slice(0, 4), sum = top.reduce((a, t) => a + t[1], 0) || 1;
      top.forEach(([q, w], j) => { wts[v * 4 + j] = w / sum; ids[v * 4 + j] = q; });
    }
    // 这一层的贴图：只保留这一层范围里的像素（身体层挖掉单独一层的部分）
    const tex = new OffscreenCanvas(W, H), tx = tex.getContext('2d');
    tx.drawImage(img, 0, 0);
    if (L.poly) { tx.globalCompositeOperation = 'destination-in'; tx.beginPath(); L.poly.forEach(([px, py], i) => (i ? tx.lineTo(px, py) : tx.moveTo(px, py))); tx.closePath(); tx.fill(); }
    else if (rig.layers?.length && !o.keepUnder) { tx.globalCompositeOperation = 'destination-out'; for (const l of rig.layers) { if (l.keepUnder) continue; tx.beginPath(); l.poly.forEach(([px, py], i) => (i ? tx.lineTo(px, py) : tx.moveTo(px, py))); tx.closePath(); tx.fill(); } }
    layers.push({ name: L.name, z: L.z ?? 0, rest: new Float32Array(rest), w: wts, i: ids, tris: new Uint32Array(tris), tex });
  }
  layers.sort((p, q) => p.z - q.z);
  return { W, H, rig, idx, layers, img };
}

// 由姿势算每根骨头的变换（正向运动学：子骨跟着父骨走，再绕自己的关节转）
export function boneMatrices(B, pose) {
  const bones = B.rig.bones, M = new Array(bones.length);
  for (let i = 0; i < bones.length; i++) {
    const b = bones[i], p = pose[b.name] || {}, parent = b.parent ? M[B.idx[b.parent]] : [1, 0, 0, 1, 0, 0];
    let local = rotAbout(b.head, p.rot || 0);
    if (p.sx || p.sy) local = mul(local, stretch(b.head, b.tail, p.sx ?? 1, p.sy ?? 1));
    if (!b.parent && (p.dx || p.dy)) local = mul(transl(p.dx || 0, p.dy || 0), local);
    M[i] = mul(parent, local);
  }
  return M;
}
// 某根骨头上一点（原图坐标）摆完姿势以后的位置——用来让签子、手机、火柴跟着手走
export function posePoint(B, pose, bone, p) { return apply(boneMatrices(B, pose)[B.idx[bone]], p); }

let GLC = null;
function glCtx(W, H) {
  if (GLC && GLC.W === W && GLC.H === H) return GLC;
  const cv = new OffscreenCanvas(W, H), gl = cv.getContext('webgl2', { premultipliedAlpha: true, alpha: true });
  const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
  const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
  GLC = { cv, gl, pr, W, H, tex: new Map() };
  return GLC;
}
// 渲染：返回原图尺寸的画布
export function render(B, pose) {
  const G = glCtx(B.W, B.H), gl = G.gl;
  gl.viewport(0, 0, B.W, B.H); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
  gl.useProgram(G.pr); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
  const M = boneMatrices(B, pose), mats = new Float32Array(32 * 9);
  M.forEach((m, k) => mats.set([m[0], m[1], 0, m[2], m[3], 0, m[4], m[5], 1], k * 9));
  gl.uniformMatrix3fv(gl.getUniformLocation(G.pr, 'uB'), false, mats);
  gl.uniform2f(gl.getUniformLocation(G.pr, 'uSize'), B.W, B.H);
  const face = pose.__face, lid = pose.__blink ? lids(B, pose.__blink) : null;
  for (const L of B.layers) {
    drawLayer(G, L, L.tex);
    if (face && L.name === (face.layer || 'body')) drawLayer(G, L, face.tex);   // 表情头：同一层网格、换一张贴图（只在脸的范围里有像素）
    if (lid && L.name === 'body') drawLayer(G, L, lid);                          // 眨眼的眼皮，跟着头走
  }
  const out = new OffscreenCanvas(B.W, B.H); out.getContext('2d').drawImage(G.cv, 0, 0);
  return out;
}
function drawLayer(G, L, texCanvas) {
  const gl = G.gl;
  let t = G.tex.get(texCanvas);
  if (!t) {
    t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, texCanvas);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    G.tex.set(texCanvas, t);
  }
  gl.bindTexture(gl.TEXTURE_2D, t);
  L.vao ||= (() => {
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    const buf = (data, loc, n) => { const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, n, gl.FLOAT, false, 0, 0); };
    buf(L.rest, gl.getAttribLocation(G.pr, 'aRest'), 2); buf(L.w, gl.getAttribLocation(G.pr, 'aW'), 4); buf(L.i, gl.getAttribLocation(G.pr, 'aI'), 4);
    const e = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, e); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, L.tris, gl.STATIC_DRAW);
    return vao;
  })();
  gl.bindVertexArray(L.vao);
  gl.drawElements(gl.TRIANGLES, L.tris.length, gl.UNSIGNED_INT, 0);
}
// 眨眼：rig.eyes = [{ c:[x,y], rx, ry, rot?, skin, line? }]（原图像素）。k 0..1：半闭（上半个眼睛盖上皮肤色，中间一道眼皮线）→ 全闭（整个眼睛盖上，
// 下沿一道向下弯的闭眼线）。按两档缓存，眨眼只有两三帧
function lids(B, k) {
  const q = k >= 0.75 ? 1 : 0.5, key = `__lid${q}`;
  if (B[key]) return B[key];
  const c = new OffscreenCanvas(B.W, B.H), x = c.getContext('2d');
  for (const e of B.rig.eyes || []) {
    x.save(); x.translate(...e.c); x.rotate(e.rot || 0);
    x.beginPath(); x.ellipse(0, 0, e.rx + 2, e.ry + 2, 0, 0, Math.PI * 2); x.clip();
    x.fillStyle = e.skin; x.fillRect(-e.rx - 4, -e.ry - 4, 2 * e.rx + 8, q >= 1 ? 2 * e.ry + 8 : e.ry + 4);
    x.restore();
    x.save(); x.translate(...e.c); x.rotate(e.rot || 0); x.strokeStyle = e.line || '#3a2418'; x.lineWidth = e.lw || 3; x.lineCap = 'round';
    x.beginPath();
    if (q >= 1) { x.moveTo(-e.rx, e.ry * 0.15); x.quadraticCurveTo(0, e.ry * 0.75, e.rx, e.ry * 0.15); }   // 闭着：下沿一道弯
    else { x.moveTo(-e.rx, 0); x.quadraticCurveTo(0, e.ry * 0.25, e.rx, 0); }                           // 半闭：中间一道
    x.stroke(); x.restore();
  }
  return (B[key] = c);
}
// 眨眼曲线：times 里每个时刻眨一次（0.05 秒闭上、停 0.04、0.08 秒睁开）
export function blinkAt(t, times) {
  let k = 0;
  for (const b of times) { const u = t - b; if (u > -0.05 && u < 0.12) k = Math.max(k, u < 0 ? 1 + u / 0.05 : u < 0.04 ? 1 : 1 - (u - 0.04) / 0.08); }
  return k;
}
// 读绑骨数据 + 图，绑好
const CACHE = new Map();
export async function loadRig(name) {
  if (CACHE.has(name)) return CACHE.get(name);
  const rig = await (await fetch(`/assets/rigs/${name}.rig.json`)).json();
  const img = await createImageBitmap(await (await fetch(`/${rig.image}`)).blob());
  const B = bind(img, rig);
  CACHE.set(name, B);
  return B;
}
// 表情头：和原图对齐的整张图，只取脸的范围（poly），贴在指定层的网格上
export async function loadFace(file, poly) {
  const img = await createImageBitmap(await (await fetch(`/${file}`)).blob());
  const c = new OffscreenCanvas(img.width, img.height), x = c.getContext('2d');
  x.drawImage(img, 0, 0);
  if (poly) { x.globalCompositeOperation = 'destination-in'; x.filter = 'blur(3px)'; x.beginPath(); poly.forEach(([px, py], i) => (i ? x.lineTo(px, py) : x.moveTo(px, py))); x.closePath(); x.fill(); }
  return { tex: c };
}
