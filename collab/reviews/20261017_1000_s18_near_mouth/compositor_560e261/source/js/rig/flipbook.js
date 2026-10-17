// 逐帧动画（用户 2026-10-17 选定："Astra 逐帧出关键帧，代码只做合成、光照和镜头"）。
// 一个动作 = 一串关键帧图（合作方生图），每张标两个不动的定位点；这里按定位点把每张（包括第一张）对齐到母版画幅
// （平移 + 旋转 + 等比缩放），按整数帧曝光表换帧（一拍三，停顿处停更久），不叠化。
// 床单戏图卡要三张图（固有色、法线、材质：tools/prep_flip.py 生成 _n、_m），屋内镜头只用固有色。
// 描述文件 assets/flips/<名字>.flip.json：
//   { "target": { "width": 635, "height": 1175, "anchors": [[x, y], [x, y]] },   母版画幅、母版上的两个不动点
//     "fps": 24,
//     "frames": [{ "file": "x18_f01", "anchors": [[x, y], [x, y]] }, ...],      每张图上同样两个点的实测坐标
//     "timelineFrames": [[0, 0], [6, 1], ...] }                                [开始帧号, 帧序号]，到下一项开始为止一直停在这一帧
// 校验不过（定位点太近、三张图尺寸不一、对齐要转太多、曝光表乱序或越界）直接报错，不悄悄出一张歪图。
const load = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(`${u} ${r.status}`); return createImageBitmap(await r.blob()); };
const MAX_DEG = 6, SCALE = [0.8, 1.25];   // 法线图只跟着挪位置、没转法线方向，所以只允许小角度校正

export async function loadFlip(name, o = {}) {
  const r = await fetch(`/assets/flips/${name}.flip.json`);
  if (r.status === 404 && o.optional) return null;   // 没有描述文件：调用方可以退回旧画法；有描述文件但读坏了一律报错
  if (!r.ok) throw new Error(`${name}.flip.json ${r.status}`);
  const spec = await r.json(), T = spec.target, bad = (m) => { throw new Error(`${name}.flip.json：${m}`); };
  const span = (a) => (a?.length === 2 && a.flat().every(Number.isFinite) ? Math.hypot(a[1][0] - a[0][0], a[1][1] - a[0][1]) : 0);
  if (!(T?.width > 0 && T?.height > 0) || span(T.anchors) < 40) bad('target 要有画幅和两个相距 40 像素以上的定位点');
  const frames = await Promise.all(spec.frames.map(async (f) => {
    const b = `/assets/chars/${f.file}`;
    const alb = await load(`${b}.png`);
    const [nrm, mat] = o.maps === false ? [null, null] : await Promise.all([load(`${b}_n.png`).catch(() => null), load(`${b}_m.png`).catch(() => null)]);
    for (const m of [nrm, mat]) if (m && (m.width !== alb.width || m.height !== alb.height)) bad(`${f.file} 的法线 / 材质图和固有色尺寸不一样`);
    if (span(f.anchors) < 40) bad(`${f.file} 的两个定位点要相距 40 像素以上`);
    return { ...f, alb, nrm, mat };
  }));
  // 每张对齐到母版：两点确定的相似变换
  const [r1, r2] = T.anchors, vr = [r2[0] - r1[0], r2[1] - r1[1]];
  for (const f of frames) {
    const [a1, a2] = f.anchors, va = [a2[0] - a1[0], a2[1] - a1[1]];
    const s = Math.hypot(...vr) / Math.hypot(...va), ang = Math.atan2(vr[1], vr[0]) - Math.atan2(va[1], va[0]);
    const deg = Math.atan2(Math.sin(ang), Math.cos(ang)) * 180 / Math.PI;
    if (Math.abs(deg) > MAX_DEG || s < SCALE[0] || s > SCALE[1]) bad(`${f.file} 对齐要转 ${deg.toFixed(1)}°、缩放 ${s.toFixed(2)}，超出范围，图和母版差太多`);
    const c = s * Math.cos(ang), d = s * Math.sin(ang);
    f.M = [c, d, -d, c, r1[0] - (c * a1[0] - d * a1[1]), r1[1] - (d * a1[0] + c * a1[1])];
    f.reg = { deg, scale: s };
  }
  const tl = spec.timelineFrames;
  if (!tl?.length || tl[0][0] !== 0) bad('timelineFrames 要从第 0 帧开始');
  tl.forEach(([n, i], k) => {
    if (!Number.isInteger(n) || (k && n <= tl[k - 1][0])) bad('timelineFrames 的帧号要是递增的整数');
    if (!(i >= 0 && i < frames.length)) bad(`timelineFrames 里的帧序号 ${i} 越界`);
  });
  return { spec, frames, fps: spec.fps || 24, W: T.width, H: T.height, cache: new Map() };
}
// t 秒时该放哪一张（按整数帧取，t = n / fps）
export function frameAt(F, t) {
  const n = Math.floor(t * F.fps + 1e-6);
  let k = F.spec.timelineFrames[0][1];
  for (const [n0, i] of F.spec.timelineFrames) { if (n >= n0) k = i; else break; }
  return k;
}
// 对齐后的图（固有色；有法线、材质时一并给），按帧缓存
export function flipMaps(F, i) {
  if (F.cache.has(i)) return F.cache.get(i);
  const f = F.frames[i];
  const reg = (img, fill) => {
    const c = new OffscreenCanvas(F.W, F.H), x = c.getContext('2d');
    if (!img) {   // 没有法线 / 材质图：朝镜头的平法线、普通材质，形状跟着固有色
      x.setTransform(...f.M); x.drawImage(f.alb, 0, 0); x.setTransform(1, 0, 0, 1, 0, 0);
      x.globalCompositeOperation = 'source-in'; x.fillStyle = fill; x.fillRect(0, 0, F.W, F.H);
      return c;
    }
    x.setTransform(...f.M); x.drawImage(img, 0, 0);
    return c;
  };
  const m = { alb: reg(f.alb), nrm: reg(f.nrm, 'rgb(128,128,255)'), mat: reg(f.mat, 'rgb(0,0,0)') };
  F.cache.set(i, m);
  return m;
}
