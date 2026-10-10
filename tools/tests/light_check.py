"""光照检查：空房间在几种光照状态下的物理预览。"""
import sys, time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from laidian import layout as L
from laidian.render import rt, room, frame
from laidian.render import lighting_states as LS
from laidian.render.camera import Camera

W, H = 640, 360
camA = Camera.from_setup(L.CAMERAS[0])
camB = Camera.from_setup(L.CAMERAS[1])

def scene_with(state, lamp_pos=None):
    pl = room.build(state)
    if lamp_pos is not None:
        LS.lamp_geometry(pl, lamp_pos)
    return rt.Scene(pl)

tiles = []
# 1 日光灯
st = room.RoomState(clothes_on_wire=True)
sc = scene_with(st)
ls = [LS.tube_light(), LS.moon_light(), LS.tv_light(0.0)]
t0 = time.time(); b = frame.render(sc, camA, ls, ["tube", "moon", "tv"], W, H); print("1", time.time()-t0, b.timings)
tiles.append(frame.physical_preview(b, exposure=0.9))
# 2 月光
ls = [LS.moon_light()]
b = frame.render(sc, camA, ls, ["moon"], W, H); tiles.append(frame.physical_preview(b, exposure=14))
# 3 马灯在立柜顶 + 月光
lp = L.LAMP_CABINET
sc3 = scene_with(st, (lp.x, lp.y, lp.z))
ls = LS.lamp_lights((lp.x, lp.y, lp.z), 0.0) + [LS.moon_light()]
b = frame.render(sc3, camA, ls, ["core", "globe", "moon"], W, H); tiles.append(frame.physical_preview(b, exposure=4))
# 4 马灯挂在后台 + 手电，床单位置空（还没做床单）
st4 = room.RoomState(sheet_hung=True)
lp = L.LAMP_STAGE
sc4 = scene_with(st4, (lp.x, lp.y, lp.z))
fp = L.FLASHLIGHT_PROP
ls = LS.lamp_lights((lp.x, lp.y, lp.z), 0.0) + [LS.moon_light(), LS.flashlight((fp.x, fp.y, fp.z), (1.4, 4.0, 1.35))]
t0 = time.time(); b = frame.render(sc4, camB, ls, ["core", "globe", "moon", "flash"], W, H); print("4", time.time()-t0, b.timings)
tiles.append(frame.physical_preview(b, exposure=3))
grid = np.concatenate([np.concatenate(tiles[:2], 1), np.concatenate(tiles[2:], 1)], 0)
out = Path(sys.argv[1])
Image.fromarray(grid).save(out); print(out)
