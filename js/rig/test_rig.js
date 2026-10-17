// 骨架变形的检查页：node tools/js/snap.cjs js/rig/test_rig.js out.png 宽 高 '{"rig":"g01_beans","t":1.2}'
import { loadRig, render as warp } from './warp.js';
export async function render(ctx, arg, W, H) {
  const o = JSON.parse(arg || '{}'), B = await loadRig(o.rig || 'g01_beans'), t = o.t ?? 0;
  const s = (f, a) => a * Math.sin(t * f * 2 * Math.PI);
  const pose = o.pose || {
    spine: { rot: s(0.25, 0.015), sy: 1 + s(0.25, 0.006) }, neck: { rot: s(0.5, 0.03) }, head: { rot: s(0.33, 0.06) },
    upperarm_near: { rot: s(1, 0.03) }, forearm_near: { rot: s(1, 0.08) }, hand_near: { rot: s(2, 0.1) },
    upperarm_far: { rot: s(1, -0.03) }, forearm_far: { rot: s(1, -0.06) }, hand_far: { rot: s(2, 0.12) },
  };
  const c = warp(B, pose);
  ctx.fillStyle = '#ddd'; ctx.fillRect(0, 0, W, H);
  const k = Math.min(W / c.width, H / c.height); ctx.drawImage(c, (W - c.width * k) / 2, (H - c.height * k) / 2, c.width * k, c.height * k);
  if (o.bones) { ctx.save(); ctx.translate((W - c.width * k) / 2, (H - c.height * k) / 2); ctx.scale(k, k); ctx.strokeStyle = 'red'; ctx.lineWidth = 3; for (const b of B.rig.bones) { ctx.beginPath(); ctx.moveTo(...b.head); ctx.lineTo(...b.tail); ctx.stroke(); } ctx.restore(); }
}
