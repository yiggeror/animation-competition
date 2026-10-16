// 小满（画好的图）在第 6 场：坐在小板凳上看鹤。图由合作 AI 和用户提供（collab/refs/anim_16_*），抠图后算好法线和材质（tools/）。
// 两张变体逐像素对齐（同一个裁切框）：A 抱着胳膊、抿着嘴（"倒要看看"）；B 胳膊松开搭在膝盖上、嘴张开（看呆了）。
// 分三层：身体（整张图减去头）→ 头（含头发、辫子、脖子，绕颈根转）→ 领子（盖住脖子上的切口）。
// 眨眼在头那层上画眼皮；从 A 换到 B 放在一次眨眼里（眼睛闭上的几帧换图），换脸不跳。
export const RIG16 = {
  files: { A: 'x16_arms_crossed', B: 'x16_arms_loose' },
  ox: 144, oy: 856, sc: 13, floorY: 1149,      // 凳面中心（图片像素）、每厘米像素（凳高约 22.5 厘米）、地面
  head: [[0, 0], [420, 0], [420, 372], [322, 440], [205, 425], [200, 470], [0, 490]],
  pivot: [255, 405],                          // 颈根
  collar: [[195, 418], [230, 414], [275, 424], [305, 432], [326, 450], [336, 478], [318, 493], [280, 489], [240, 471], [200, 456], [188, 436]],
  lid: [[286, 222], [300, 213], [326, 213], [341, 226], [343, 252], [338, 257], [314, 265], [292, 259], [285, 248]],
  lidLine: [[288, 252], [300, 259], [316, 262], [332, 257], [342, 250]],
  skin: { A: '#fecbaa', B: '#fdc8a6' },
};

export async function loadRig(rig) {
  const load = async (u) => createImageBitmap(await (await fetch(u)).blob());
  const one = async (f) => { const b = '/assets/chars/' + f; const [alb, nrm, mat] = await Promise.all([load(b + '.png'), load(b + '_n.png'), load(b + '_m.png')]); return { alb, nrm, mat }; };
  return { A: await one(rig.files.A), B: await one(rig.files.B) };
}

const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const backOut = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); const c = 1.4; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
// 眨眼：t0 开始，0.06 秒闭上，停 0.05 秒，0.09 秒睁开；返回 0（睁）..1（闭）
const blinkAt = (t, t0) => { const u = t - t0; if (u < 0 || u > 0.2) return 0; if (u < 0.06) return u / 0.06; if (u < 0.11) return 1; return 1 - (u - 0.11) / 0.09; };

// 第 6 场的表演（秒）：
//   0～1.5：抱着胳膊、抿着嘴，下巴比图里低一点（鹤还低着头）
//   1.55：眨一下眼——闭眼的那几帧换成 B（胳膊松开、嘴张开）
//   1.3～2.8：跟着鹤扬头，下巴抬到图里的角度，略冲过头再回来
//   4.15：再眨一次眼；全程轻轻呼吸
export function pose16(t) {
  const blink = Math.max(blinkAt(t, 1.55), blinkAt(t, 4.15));
  const useB = t >= 1.61;                                    // 头（脸）在闭眼时换
  const mixB = sstep(1.50, 1.78, t);                          // 身体（胳膊）在 0.28 秒里渐变过去（等合作方补"胳膊松到一半"的中间图）
  const head = 0.045 * (1 - backOut(1.3, 2.8, t));        // 弧度；正 = 下巴低（画面里顺时针）
  const breathe = Math.sin((t / 3.4) * 6.283);
  return { blink, useB, mixB, head, breathe };
}

// 生成 cards.addImage 需要的层。m：图片像素 → 画面像素的仿射变换
export function layers16(rig, maps, m, p) {
  const V = p.useB ? maps.B : maps.A, skin = p.useB ? rig.skin.B : rig.skin.A;
  const mul = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
  // 呼吸：以凳面为基准，竖直方向轻轻伸缩 0.25%
  const sy = 1 + 0.0025 * p.breathe, breathe = [1, 0, 0, sy, 0, rig.oy * (1 - sy)];
  const mb = mul(m, breathe);
  // 头：绕颈根转
  const [px, py] = rig.pivot, c = Math.cos(p.head), s = Math.sin(p.head);
  const rotH = [c, s, -s, c, px - c * px + s * py, py - s * px - c * py];
  const mh = mul(mb, rotH);
  const eyelid = (ctx) => {
    if (p.blink < 0.35) return;
    const L = rig.lid, top = Math.min(...L.map((q) => q[1])), bot = Math.max(...L.map((q) => q[1]));
    const k = p.blink > 0.75 ? 1 : 0.55, yEdge = top + (bot - top) * k;
    ctx.save();
    ctx.beginPath(); ctx.rect(270, top - 4, 90, yEdge - top + 4); ctx.clip();
    ctx.fillStyle = skin; ctx.beginPath(); L.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill();
    ctx.restore();
    // 眼皮的边：闭上是一道往下弯的线（带两根睫毛），半闭是一道横线
    ctx.strokeStyle = '#3a1f16'; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath();
    if (k === 1) rig.lidLine.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    else { ctx.moveTo(287, yEdge); ctx.quadraticCurveTo(315, yEdge + 4, 343, yEdge - 2); }
    ctx.stroke();
    if (k === 1) { ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(292, 256); ctx.lineTo(284, 262); ctx.moveTo(298, 259); ctx.lineTo(292, 266); ctx.stroke(); }
  };
  const w = p.mixB ?? (p.useB ? 1 : 0);
  return [
    { blend: [{ maps: maps.A, w: 1 - w }, { maps: maps.B, w }], m: mb, clip: { pts: rig.head, invert: true } },
    { maps: V, m: mh, clip: { pts: rig.head }, overlay: eyelid },
    { maps: w < 0.5 ? maps.A : maps.B, m: mb, clip: { pts: rig.collar } },
  ];
}
