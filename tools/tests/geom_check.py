"""几何检查：从 A–D 机位渲染简单着色，确认空间关系。"""
import sys, time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian import layout as L
from laidian.render import rt, room
from laidian.render.camera import Camera
from laidian.render.materials import albedo_table

def render(cam, scene, W=640, H=360):
    o, f, r, u = cam.basis()
    T, ID, N, UV, P, D = rt.primary(scene.prims, scene.nodes, scene.order, o, f, r, u, cam.tan_half, W, H, scene.atlas, scene.rects, 0.5, 0.5)
    alb = albedo_table()
    mat = np.where(ID >= 0, scene.prims[np.maximum(ID, 0), 1].astype(int), 0)
    a = alb[mat]
    ldir = np.array([0.4, -0.6, 0.7]); ldir /= np.linalg.norm(ldir)
    sh = 0.35 + 0.65 * np.clip((N * ldir).sum(-1), 0, 1)
    img = a * sh[..., None]
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    return (img * 255).astype(np.uint8)

st = room.RoomState(sheet_hung=True)
pl = room.build(st)
scene = rt.Scene(pl)
print("prims", scene.prims.shape[0], "nodes", scene.nodes.shape[0])
tiles = []
for cs in L.CAMERAS[:4]:
    t0 = time.time()
    im = render(Camera.from_setup(cs), scene)
    print(cs.name, f"{time.time()-t0:.2f}s")
    tiles.append(im)
grid = np.concatenate([np.concatenate(tiles[:2], 1), np.concatenate(tiles[2:], 1)], 0)
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build/geom_check.png"
out.parent.mkdir(parents=True, exist_ok=True)
Image.fromarray(grid).save(out)
print(out)
