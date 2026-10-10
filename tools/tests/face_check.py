"""五官检查：两个人物的头部特写（物理预览 + 贴花）。"""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian.render import rt, frame, character as C, light as LT
from laidian.render.camera import Camera
from laidian.render.materials import M
from laidian.render.rt import PrimList
from laidian.render.styles.common import face_layers
from laidian.shots.style_samples import merge_chars
pl = PrimList(); pl.box(M("concrete"), -5, 5, -5, 5, -0.2, 0.0); sc = rt.Scene(pl)
rows = []
for P, outfit, expr in ((C.XIAOMAN, "xiaoman", dict(mouth_open=0.3, brow=0.5)), (C.NAINAI, "nainai", dict(eye_smile=0.7, mouth_smile=0.6))):
    pose = C.CharPose(root=(0, 0, P.hip_h), expr=expr)
    c, g, info = C.build(P, pose, outfit)
    chars, groups, faces = merge_chars([(c, g)], [(outfit, info, expr, None)])
    hc = info["head_c"]
    row = []
    for ang in (0, 35, 80):
        a = math.radians(ang)
        cam = Camera((hc[0] + math.sin(a) * 0.9, hc[1] + math.cos(a) * 0.9, hc[2] + 0.05), tuple(hc), 26)
        key = LT.make_light(LT.SPHERE, (1, 0.95, 0.9), 2.0, pos=(hc[0] + 0.6, hc[1] + 1.0, hc[2] + 0.6), radius=0.1, samples=8)
        b = frame.render(sc, cam, [key], ["key"], 400, 400, chars, groups, vpl_n=4, ao=False)
        im = frame.physical_preview(b, exposure=2.0).astype(float) / 255
        fl = face_layers(b, faces, chars)
        print(outfit, ang, {k: float(v.max()) for k, v in fl.items()})
        im = im * (1 - fl["ink"][..., None]) + 0.02 * fl["ink"][..., None]
        im = im * (1 - fl["line"][..., None] * 0.6)
        im = im * (1 - fl["glass"][..., None]) + 0.1 * fl["glass"][..., None]
        im = im * (1 - fl["white"][..., None]) + fl["white"][..., None]
        im = im * (1 - fl["mouth"][..., None]) + np.array([0.4, 0.05, 0.05]) * fl["mouth"][..., None]
        row.append((np.clip(im, 0, 1) * 255).astype(np.uint8))
    rows.append(np.concatenate(row, 1))
Image.fromarray(np.concatenate(rows, 0)).save(sys.argv[1])
