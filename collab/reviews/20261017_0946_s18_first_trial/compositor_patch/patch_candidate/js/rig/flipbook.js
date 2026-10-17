// 逐帧动画（用户 2026-10-17 选定："Astra 逐帧出关键帧，代码只做合成、光照和镜头"）。
// 一个动作 = 一串和母版同画幅的关键帧图（合作方生图），每张标两个不动的定位点；这里按定位点把每张对齐到参考帧
// （平移 + 旋转 + 等比缩放），按时间表换帧（一拍三，停顿处停更久），不叠化。
// 床单戏图卡要三张图（固有色、法线、材质：tools/prep_flip.py 生成 _n、_m），屋内镜头只用固有色。
// 描述文件 assets/flips/<名字>.flip.json：
//   { "canvas": [635,1175], "referenceAnchors": [[x,y],[x,y]], "frames": [{ "file": "x18_f01", "anchors": [[x, y], [x, y]] }, ...],
//     "timeline": [[0.00, 0], [0.25, 1], ...]（[开始时间（秒）, 帧序号]，到下一项开始为止一直停在这一帧） }
const load = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(`${u} ${r.status}`); return createImageBitmap(await r.blob()); };

export async function loadFlip(name, o = {}) {
  const response = await fetch(`/assets/flips/${name}.flip.json`);
  if (!response.ok) throw new Error(`flip ${name}: manifest HTTP ${response.status}`);
  const spec = await response.json();
  const fail = (why) => { throw new Error(`flip ${name}: ${why}`); };
  const anchors = (p, label) => {
    if (!Array.isArray(p) || p.length !== 2 || p.some(q => !Array.isArray(q) || q.length !== 2 || q.some(v => !Number.isFinite(v)))) fail(`${label}: need two finite points`);
    if (Math.hypot(p[1][0] - p[0][0], p[1][1] - p[0][1]) < 1) fail(`${label}: anchors must be at least 1px apart`);
    return p;
  };
  if (!Array.isArray(spec.canvas) || spec.canvas.length !== 2 || spec.canvas.some(v => !Number.isInteger(v) || v <= 0)) fail('explicit canvas [width,height] required');
  const referenceAnchors = anchors(spec.referenceAnchors, 'referenceAnchors');
  if (!Array.isArray(spec.frames) || !spec.frames.length) fail('frames must not be empty');
  spec.frames.forEach((f, i) => {
    if (!f || typeof f.file !== 'string' || !f.file) fail(`frame ${i}: missing file`);
    anchors(f.anchors, `frame ${i}`);
  });
  if (!Array.isArray(spec.timeline) || !spec.timeline.length) fail('timeline must not be empty');
  spec.timeline.forEach((entry, i) => {
    if (!Array.isArray(entry) || entry.length !== 2) fail(`timeline ${i}: expected [seconds,frameIndex]`);
    const [t, k] = entry;
    if (!Number.isFinite(t) || t < 0 || (i === 0 ? t !== 0 : t <= spec.timeline[i - 1][0])) fail(`timeline ${i}: starts at zero and must strictly increase`);
    if (!Number.isInteger(k) || k < 0 || k >= spec.frames.length) fail(`timeline ${i}: frame index out of range`);
  });
  const frames = await Promise.all(spec.frames.map(async (f) => {
    const b = `/assets/chars/${f.file}`;
    const alb = await load(`${b}.png`);
    const [nrm, mat] = o.maps === false ? [null, null] : await Promise.all([load(`${b}_n.png`).catch(() => null), load(`${b}_m.png`).catch(() => null)]);
    for (const [ch, img] of [['nrm', nrm], ['mat', mat]]) if (img && (img.width !== alb.width || img.height !== alb.height)) fail(`${f.file}: ${ch} dimensions differ from albedo`);
    return { ...f, alb, nrm, mat };
  }));
  // 每张（包括第一张）对齐到母版坐标；canvas/referenceAnchors 必须显式给出。
  for (const f of frames) {
    const [a1, a2] = f.anchors, [r1, r2] = referenceAnchors;
    const va = [a2[0] - a1[0], a2[1] - a1[1]], vr = [r2[0] - r1[0], r2[1] - r1[1]];
    const s = Math.hypot(...vr) / Math.hypot(...va), ang = Math.atan2(vr[1], vr[0]) - Math.atan2(va[1], va[0]);
    const c = s * Math.cos(ang), d = s * Math.sin(ang);
    f.M = [c, d, -d, c, r1[0] - (c * a1[0] - d * a1[1]), r1[1] - (d * a1[0] + c * a1[1])];
  }
  return { spec, frames, W: spec.canvas[0], H: spec.canvas[1], cache: new Map() };
}
// t 时刻该放哪一帧
export function frameAt(F, t, timeline = F.spec.timeline) {
  let k = timeline[0][1];
  for (const [t0, i] of timeline) { if (t >= t0) k = i; else break; }
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
