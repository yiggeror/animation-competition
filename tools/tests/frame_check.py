"""构图检查：把关键点投影到画面上（像素坐标）。"""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian import layout as L
from laidian.render.camera import Camera
W, H = 1920, 1080
def check(cam, pts):
    for name, p in pts.items():
        q = cam.project(np.array(p, float)[None], W, H)[0]
        inside = 0 <= q[0] < W and 0 <= q[1] < H and q[2] > 0
        print(f"  {name:16s} x={q[0]:7.0f} y={q[1]:7.0f} d={q[2]:.2f} {'ok' if inside else 'OUT'}")
xa = L.MARKS["xiaoman_audience"]
for pos, tgt, fov in [((1.70, 2.05, 0.80), (1.12, 4.0, 1.26), 54), ((1.72, 1.95, 0.86), (1.10, 4.0, 1.30), 52)]:
    print("B", pos, tgt, fov)
    check(Camera(pos, tgt, fov), {"xm_head": (xa.x, xa.y + 0.02, 0.92), "xm_shoulder": (xa.x + 0.12, xa.y, 0.74),
                                  "crane_head": (1.25, 4.0, 1.68), "crane_feet": (1.0, 4.0, 1.02), "sheet_tl": (0.25, 4.0, 2.08), "sheet_br": (2.35, 4.0, 0.86)})
for pos, tgt, fov in [((2.62, 4.42, 1.22), (0.9, 4.42, 1.12), 52), ((2.66, 4.30, 1.20), (0.95, 4.55, 1.12), 50)]:
    print("D", pos, tgt, fov)
    check(Camera(pos, tgt, fov), {"nn_head": (0.88, 4.82, 1.42), "xm_head": (1.76, 4.78, 1.15), "lamp": (1.30, 4.70, 1.45),
                                  "sheet_e_top": (2.35, 4.0, 2.08), "sheet_e_bot": (2.35, 4.0, 0.86), "nn_feet": (0.88, 4.84, 0.0)})
