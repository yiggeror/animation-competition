// 皮影：读入导出的部件贴图（tools/export_puppets.py），正向运动学摆姿势，画透光图或皮面。
// 皮影局部坐标：毫米，y 向上（和导出时一致）；画的时候由调用方给一个"毫米 → 画布"的变换。

const cache = {};
function loadImage(url) {
  return new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = url; });
}
export async function loadPuppet(name, base = '../assets/puppets/') {
  if (cache[name]) return cache[name];
  const rig = await (await fetch(`${base}${name}/rig.json`)).json();
  const parts = {};
  await Promise.all(rig.parts.map(async (p) => {
    parts[p.part] = { ...p, t: await loadImage(`${base}${name}/${p.part}_t.png`), r: await loadImage(`${base}${name}/${p.part}_r.png`) };
  }));
  return (cache[name] = { name, rig: rig.parts, parts });
}

// pose: { angles: {部件: 弧度}, slide: {部件: mm}, rootAngle, facing: ±1 }
export function solve(pup, pose) {
  const out = {};
  for (const j of pup.rig) {
    const a = pose.angles?.[j.part] ?? 0;
    if (!j.parent) { out[j.part] = { o: [0, 0], a: (pose.rootAngle ?? 0) + a }; continue; }
    const P = out[j.parent];
    const c = Math.cos(P.a), s = Math.sin(P.a);
    let o = [P.o[0] + c * j.at[0] - s * j.at[1], P.o[1] + s * j.at[0] + c * j.at[1]];
    const ang = P.a + a;
    const sl = pose.slide?.[j.part] ?? 0;
    if (sl) o = [o[0] + Math.cos(ang) * sl, o[1] + Math.sin(ang) * sl];
    out[j.part] = { o, a: ang };
  }
  return out;
}
// 皮影局部点（某部件上的 mm 坐标）→ 皮影整体坐标（mm, y 向上）
export function pointOn(pup, sol, part, p) {
  const S = sol[part], c = Math.cos(S.a), s = Math.sin(S.a);
  return [S.o[0] + c * p[0] - s * p[1], S.o[1] + s * p[0] + c * p[1]];
}

// 在 ctx 当前变换下画（当前变换 = 皮影 mm 坐标，y 向上已经由调用方翻转好）。
// mode: 't' 透光（正片叠底到白底上） | 'r' 皮面颜色（后台看到的样子）
export function drawPuppet(ctx, pup, pose, mode = 't') {
  const sol = solve(pup, pose);
  const order = pup.rig.slice().sort((a, b) => a.layer - b.layer);
  const f = pose.facing ?? 1;
  for (const j of order) {
    const pt = pup.parts[j.part], S = sol[j.part];
    const [x0, y0, x1, y1] = pt.bounds;
    ctx.save();
    ctx.scale(f, 1);
    ctx.translate(S.o[0], S.o[1]);
    ctx.rotate(S.a);
    // 贴图第 0 行是 y1（上边），所以翻一下 y
    ctx.translate(x0, y1);
    ctx.scale((x1 - x0) / pt.t.width, -(y1 - y0) / pt.t.height);
    ctx.drawImage(mode === 't' ? pt.t : pt.r, 0, 0);
    ctx.restore();
  }
  return sol;
}
