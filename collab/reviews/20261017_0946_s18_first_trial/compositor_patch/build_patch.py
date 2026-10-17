from pathlib import Path
import difflib

base = Path('/tmp/laidian-s18-pilot-audit/compositor')
changes = {}
p = 'js/rig/flipbook.js'
s = (base/'source'/p).read_text()
s = s.replace("  const spec = await (await fetch(`/assets/flips/${name}.flip.json`)).json();", """  const response = await fetch(`/assets/flips/${name}.flip.json`);
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
  });""")
s=s.replace("    return { ...f, alb, nrm, mat };", """    for (const [ch, img] of [['nrm', nrm], ['mat', mat]]) if (img && (img.width !== alb.width || img.height !== alb.height)) fail(`${f.file}: ${ch} dimensions differ from albedo`);
    return { ...f, alb, nrm, mat };""")
s=s.replace("  const ref = frames[spec.ref ?? 0];\n  // 每张对齐到参考帧：两点确定的相似变换", "  // 每张（包括第一张）对齐到母版坐标；canvas/referenceAnchors 必须显式给出。")
s=s.replace("const [a1, a2] = f.anchors, [r1, r2] = ref.anchors;", "const [a1, a2] = f.anchors, [r1, r2] = referenceAnchors;")
s=s.replace("W: ref.alb.width, H: ref.alb.height", "W: spec.canvas[0], H: spec.canvas[1]")
s=s.replace('//   { "frames":', '//   { "canvas": [635,1175], "referenceAnchors": [[x,y],[x,y]], "frames":')
s=s.replace(', "ref": 0,', ',')
changes[p]=s

p='js/lamp/shots/s18.js';s=(base/'patch_base'/p).read_text()
old="""let FLIP;
async function flip() { if (FLIP === undefined) { try { FLIP = await loadFlip('x18_laugh'); } catch { FLIP = null; } } return FLIP; }"""
new="""let FLIP, FLIP_ERROR;
// 试片入口：页面 ?flipReview=1，或导入本模块后调用 setFlipReviewRequired()。
let FLIP_REQUIRED = new URLSearchParams(globalThis.location?.search ?? '').get('flipReview') === '1';
export function setFlipReviewRequired(required = true) { FLIP_REQUIRED = required; }
async function flip() {
  if (FLIP === undefined) {
    try { FLIP = await loadFlip('x18_laugh'); }
    catch (error) { FLIP_ERROR = error; FLIP = null; }
  }
  if (FLIP_REQUIRED && FLIP === null) throw new Error('S18 flip review requires valid keyframes; legacy fallback disabled', { cause: FLIP_ERROR });
  return FLIP;
}"""
assert old in s;s=s.replace(old,new);changes[p]=s
patch=''
for p,new in changes.items():
    original = base/'patch_base'/p if (base/'patch_base'/p).exists() else base/'source'/p
    old=original.read_text(); dest=base/'patch_candidate'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(new)
    patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+p,tofile='b/'+p))
(base/'s18_minimal.patch').write_text(patch)
print(base/'s18_minimal.patch')
