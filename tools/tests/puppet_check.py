"""皮影设计检查：在亮床单上的样子（透光）+ 从后台看到的皮面（反射）。"""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian.render import puppets as PP
from laidian.shots.style_samples import crane_pose_debut, turtle_pose

def to8(x):
    x = np.clip(x, 0, 1)
    return (np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1/2.4) - 0.055) * 255).astype(np.uint8)

def assemble(rig, parts, pose, W, H, origin, scale, mode="trans"):
    img = np.ones((H, W, 3), np.float32)
    acc = np.zeros((H, W, 3), np.float32); cov_all = np.zeros((H, W), np.float32)
    sol = PP.solve(rig, pose)
    ys, xs = np.mgrid[0:H, 0:W]
    order = sorted(rig, key=lambda j: j.layer)
    for j in order:
        pt = parts[j.part]
        o, ang = sol[j.part]
        x0, y0, x1, y1 = pt.bounds
        tex = pt.trans if mode == "trans" else pt.refl
        th, tw = tex.shape[:2]
        mx = (xs - origin[0]) / scale * pose.facing - o[0]
        my = (origin[1] - ys) / scale - o[1]
        ca, sa = math.cos(-ang), math.sin(-ang)
        lx = ca * mx - sa * my; ly = sa * mx + ca * my
        u = ((lx - x0) / (x1 - x0) * (tw - 1)).round().astype(int)
        v = ((y1 - ly) / (y1 - y0) * (th - 1)).round().astype(int)
        ok = (u >= 0) & (u < tw) & (v >= 0) & (v < th)
        if mode == "trans":
            t = np.ones((H, W, 3), np.float32); t[ok] = tex[v[ok], u[ok], :3]; img *= t
        else:
            a = np.zeros((H, W), np.float32); a[ok] = tex[v[ok], u[ok], 3]
            c = np.zeros((H, W, 3), np.float32); c[ok] = tex[v[ok], u[ok], :3]
            acc = acc * (1 - a[..., None]) + c * a[..., None]; cov_all = np.maximum(cov_all, a)
    if mode == "trans":
        return img
    return acc, cov_all

ppmm = 3.0
cp = PP.crane_parts(ppmm); tp = PP.turtle_parts(ppmm)
lamp = np.array([1.0, 0.70, 0.40])
cpose = crane_pose_debut(); cpose.facing = 1
W, H = 1400, 1000
a = assemble(PP.CRANE_RIG, cp, cpose, W, H, (620, 600), 2.0)
tpose = turtle_pose(facing=1)
b = assemble(PP.TURTLE_RIG, tp, tpose, W, 420, (700, 230), 2.4)
sheet = np.concatenate([a, b], 0) * lamp
Image.fromarray(to8(sheet)).save(sys.argv[1] + "_sheet.png")
ra, ca = assemble(PP.CRANE_RIG, cp, cpose, W, H, (620, 600), 2.0, "refl")
rb, cb = assemble(PP.TURTLE_RIG, tp, tpose, W, 420, (700, 230), 2.4, "refl")
bg = np.array([0.05, 0.04, 0.035])
r = np.concatenate([ra * ca[..., None] + bg * (1 - ca[..., None]), rb * cb[..., None] + bg * (1 - cb[..., None])], 0) * 2.2
Image.fromarray(to8(r)).save(sys.argv[1] + "_refl.png")
print("ok")
