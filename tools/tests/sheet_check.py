"""床单检查：马灯从背后照，鹤贴紧床单 / 离开床单时的影子（物理预览）。"""
import sys, time, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian import layout as L
from laidian.render import rt, room, frame, puppets as PP
from laidian.render import lighting_states as LS
from laidian.render.camera import Camera
from laidian.render.materials import M

W, H = 960, 540
cp = PP.crane_parts(5.0)
tp = PP.turtle_parts(5.0)
atlas = PP.Atlas()
tex = {}
for nm, pt in {**{f"c:{k}": v for k, v in cp.items()}, **{f"t:{k}": v for k, v in tp.items()}}.items():
    tex[nm] = atlas.add(pt.trans)
    atlas.add(pt.refl)
A, R = atlas.build()
print("atlas", A.shape)
crane_pose = PP.Pose(root_xz=(1.05, 1.30), facing=1, dist=0.004,
                     angles={"neck0": 0.9, **{f"neck{k}": (0.10 if k < 5 else -0.12) for k in range(1, 11)}, "head": -0.55,
                             "tibia_near": -0.15, "tarsus_near": 0.25, "foot_near": -0.1,
                             "tibia_far": 0.12, "tarsus_far": -0.05, "foot_far": 0.0})
turtle_pose = PP.Pose(root_xz=(1.75, 0.98), facing=-1, dist=0.12,
                      angles={"leg_front_near": 0.2, "leg_back_near": -0.15, "headneck": 0.05})
lp = L.LAMP_STAGE
def build(cpose, tpose):
    st = room.RoomState(sheet_hung=True)
    pl = room.build(st)
    LS.lamp_geometry(pl, (lp.x, lp.y, lp.z))
    PP.add_puppet(pl, PP.CRANE_RIG, cp, {k[2:]: v for k, v in tex.items() if k.startswith("c:")}, cpose, L.WIRE_Y, M("wood_raw"),
                  "crane", rods=[("body", (10, 5), (1.0, 4.45, 1.25)), ("head", (20, 0), (1.3, 4.45, 1.55))], rod_mat=M("wood_raw"))
    PP.add_puppet(pl, PP.TURTLE_RIG, tp, {k[2:]: v for k, v in tex.items() if k.startswith("t:")}, tpose, L.WIRE_Y, M("wood_raw"),
                  "turtle", rods=[("shell", (0, 20), (1.8, 4.5, 1.0))], rod_mat=M("wood_raw"))
    return rt.Scene(pl, A, R)
sc = build(crane_pose, turtle_pose)
cam = Camera.from_setup(L.CAMERAS[1])
ls = LS.lamp_lights((lp.x, lp.y, lp.z), 0.0) + [LS.moon_light()]
t0 = time.time()
b = frame.render(sc, cam, ls, ["core", "globe", "moon"], W, H, vpl_n=24)
print(time.time() - t0, b.timings)
im = frame.physical_preview(b, exposure=3.0)
Image.fromarray(im).save(sys.argv[1] + "_front.png")
# 背面
camC = Camera.from_setup(L.CAMERAS[2])
b = frame.render(sc, camC, ls, ["core", "globe", "moon"], W, H, vpl_n=24)
Image.fromarray(frame.physical_preview(b, exposure=3.0)).save(sys.argv[1] + "_back.png")
print("ok")
