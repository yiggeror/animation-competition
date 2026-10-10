"""人物检查：三视图（正、侧、背）+ 手的特写，简单打光。"""
import sys, time, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian.render import rt, frame, sdf, character as C
from laidian.render import light as LT
from laidian.render.camera import Camera
from laidian.render.materials import M
from laidian.render.rt import PrimList

def stage():
    pl = PrimList()
    pl.box(M("concrete"), -5, 5, -5, 5, -0.2, 0.0)
    return rt.Scene(pl)

def shot(sc, chars, groups, cam, W=360, H=480):
    key = LT.make_light(LT.SPHERE, (1, 0.95, 0.9), 6.0, pos=(1.5, -2.0, 2.5), radius=0.1, samples=8)
    fill = LT.make_light(LT.SPHERE, (0.6, 0.7, 1.0), 2.0, pos=(-2.0, -1.5, 1.5), radius=0.3, samples=4)
    b = frame.render(sc, cam, [key, fill], ["key", "fill"], W, H, chars, groups, vpl_n=8, ao=False)
    im = frame.physical_preview(b, exposure=1.2)
    # 轮廓线：人物边缘
    edge = (b.MR < 0.004) & (b.CP < 0)
    im[edge] = (im[edge] * 0.2).astype(np.uint8)
    return im, b

sc = stage()
out = []
for P, outfit in ((C.XIAOMAN, "xiaoman"), (C.NAINAI, "nainai")):
    pose = C.CharPose(root=(0, 0, P.hip_h), breath=0.5)
    chars, groups, info = C.build(P, pose, outfit)
    print(P.name, chars.shape, groups.shape)
    h = P.hip_h + 0.85 if outfit == "xiaoman" else P.hip_h + 0.95
    cy = h * 0.5
    row = []
    for ang in (0, 45, 90, 180):
        a = math.radians(ang)
        pos = (math.sin(a) * 4.0, math.cos(a) * 4.0, cy)
        cam = Camera(pos, (0, 0, cy), 26)
        t0 = time.time()
        im, b = shot(sc, chars, groups, cam)
        print(" view", ang, f"{time.time()-t0:.1f}s", b.timings.get("chars"))
        row.append(im)
    out.append(np.concatenate(row, 1))
grid = np.concatenate(out, 0)
Image.fromarray(grid).save(sys.argv[1])
print("ok")
