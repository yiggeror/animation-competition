export function camera(W, H, o = {}) {
  const C = o.pos || [1.48, -3.013, 0.34], T = o.target || [0.75, 0.0, 1.0], hfov = o.hfov || 60;
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const fwd = nrm(sub(T, C)), right = nrm(cross(fwd, [0, 0, 1])), up = cross(right, fwd);
  const focal = (W / 2) / Math.tan((hfov * Math.PI) / 360);
  const project = (P) => {
    const d = sub(P, C);
    const z = d[0] * fwd[0] + d[1] * fwd[1] + d[2] * fwd[2];
    const x = d[0] * right[0] + d[1] * right[1] + d[2] * right[2];
    const y = d[0] * up[0] + d[1] * up[1] + d[2] * up[2];
    return [W / 2 + (x / z) * focal, H / 2 - (y / z) * focal, Math.hypot(...d), focal / z];
  };
  return { C, fwd, right, up, focal, project };
}

