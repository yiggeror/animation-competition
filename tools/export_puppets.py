"""把皮影（鹤、乌龟）的部件贴图和骨架导出给 2D 绘制程序用。

每个部件两张图：
  <部件>_t.png  透光率（RGB = 每个通道透过的比例；没有牛皮的地方是白色 = 全透）
  <部件>_r.png  皮面颜色（从后台看到的样子），alpha = 牛皮覆盖
rig.json：部件的范围（毫米，y 向上）、父部件、铆点位置、前后层次。

用法：PYTHONPATH=src python tools/export_puppets.py assets/puppets
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from laidian.render import puppets as PP


def save(arr, path, alpha=None):
    a = np.clip(arr, 0, 1)
    if alpha is not None:
        a = np.concatenate([a[..., :3], np.clip(alpha, 0, 1)[..., None]], -1)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(path, optimize=True)


def export(name, rig, parts, out):
    d = out / name
    d.mkdir(parents=True, exist_ok=True)
    meta = {"parts": [], "units": "mm, y up"}
    for j in rig:
        pt = parts[j.part]
        save(pt.trans[..., :3], d / f"{j.part}_t.png")
        save(pt.refl[..., :3], d / f"{j.part}_r.png", alpha=pt.refl[..., 3])
        meta["parts"].append({"part": j.part, "parent": j.parent, "at": list(j.at), "layer": j.layer,
                              "bounds": [float(v) for v in pt.bounds]})
    (d / "rig.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(name, len(rig), "parts")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/puppets")
    ppmm = 5.0
    export("crane", PP.CRANE_RIG, PP.crane_parts(ppmm), out)
    export("turtle", PP.TURTLE_RIG, PP.turtle_parts(ppmm), out)
