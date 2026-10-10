"""各段落的光照状态：光源位置、颜色、强度、闪烁。

强度单位是相对的：马灯火苗 1 米处的照度 ≈ 1。
"""
import math

import numpy as np

from .. import layout as L
from .light import DIR, LINE, RECT, SPHERE, SPOT, make_light
from .materials import M
from .rt import F_SHADOW, F_TRANSMIT, F_NOVIS

# 色温（线性 RGB，近似）
K2000 = np.array([1.00, 0.56, 0.22])   # 煤油火苗
K1800 = np.array([1.00, 0.50, 0.17])   # 熏黄的玻璃罩
K6500 = np.array([0.90, 0.96, 1.00])   # 日光灯
K5000 = np.array([0.95, 0.98, 1.00])   # 手电（偏冷的白光 LED）
MOON = np.array([0.50, 0.62, 1.00])


def _noise1(t, seed):
    """平滑的一维噪声（几个正弦叠加，可复现）。"""
    rng = np.random.default_rng(seed)
    fr = rng.uniform(0.6, 4.5, 6)
    ph = rng.uniform(0, 2 * math.pi, 6)
    am = 1.0 / fr
    return float(np.sum(am * np.sin(2 * math.pi * fr * t + ph)) / np.sum(am))


def lamp_flicker(t):
    """火苗：亮度 ±6%，偶尔一次快速的跳动；位置水平晃 ±3 毫米，高度 ±4 毫米。"""
    k = 1.0 + 0.05 * _noise1(t, 11) + 0.02 * _noise1(t * 3.1, 12)
    jump = math.exp(-((t % 3.7) - 1.3) ** 2 / 0.004) * 0.10
    k -= jump
    dx = 0.003 * _noise1(t * 1.7, 13)
    dy = 0.002 * _noise1(t * 1.9, 14)
    dz = 0.004 * _noise1(t * 2.3, 15) - jump * 0.02
    return k, (dx, dy, dz)


def lamp_lights(pos, t, wick=1.0):
    k, (dx, dy, dz) = lamp_flicker(t)
    p = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
    core = make_light(SPHERE, K2000, 1.0 * k * wick, pos=p, radius=0.011, samples=12)
    globe = make_light(SPHERE, K1800, 0.30 * k * wick, pos=(pos[0], pos[1], pos[2] + 0.01), radius=0.055, samples=8)
    return [core, globe]


def lamp_geometry(pl, pos, hang_z=None):
    """马灯：油壶、玻璃罩（透光）、顶盖、护丝、提手。pos 是火苗中心；hang_z 给出时加一根吊绳。"""
    x, y, z = pos
    if hang_z is not None:
        pl.cyl(M("broom"), (x, y, z + 0.20), (x, y, hang_z), 0.003, name="lamp_rope")
    pl.cyl(M("metal"), (x, y, z - 0.13), (x, y, z - 0.06), 0.07, name="lamp_tank")
    g = pl.ell(M("lamp_glass"), (x, y, z + 0.01), (0.055, 0.055, 0.075), flags=F_SHADOW | F_TRANSMIT | F_NOVIS, name="lamp_globe")
    pl.rows[g][20] = 0.82
    pl.cyl(M("metal"), (x, y, z + 0.085), (x, y, z + 0.115), 0.045, name="lamp_cap")
    for a in (0.3, 2.4, 4.5):
        cx, cy = x + 0.065 * math.cos(a), y + 0.065 * math.sin(a)
        pl.cyl(M("metal"), (cx, cy, z - 0.06), (cx, cy, z + 0.09), 0.0025, name="lamp_guard")
    pl.cyl(M("metal"), (x - 0.06, y, z + 0.115), (x, y, z + 0.20), 0.002, name="lamp_handle")
    pl.cyl(M("metal"), (x, y, z + 0.20), (x + 0.06, y, z + 0.115), 0.002, name="lamp_handle")


def tube_light(on=1.0):
    t = L.TUBE
    yc = (t.y0 + t.y1) / 2
    return make_light(LINE, K6500, 26.0 * on, pos=(t.x0 + 0.03, yc, 3.13), vec=(t.x1 - 0.03, yc, 3.13), samples=12)


def moon_light(strength=1.0):
    d = np.asarray(L.MOON_DIR, float)
    d /= np.linalg.norm(d)
    return make_light(DIR, MOON, 0.10 * strength, vec=d, radius=0.006, samples=4)


def flashlight(pos, target, strength=1.0):
    d = np.asarray(target, float) - np.asarray(pos, float)
    d /= np.linalg.norm(d)
    return make_light(SPOT, K5000, 4.0 * strength, pos=pos, vec=d, radius=0.010,
                      cos_in=math.cos(math.radians(9)), cos_out=math.cos(math.radians(30)), spill=0.10, samples=6)


def tv_light(t, on=1.0):
    tv = [b for b in L.FURNITURE if b.name == "tv"][0]
    # 屏幕的颜色随节目变化（原创节目：只用来给环境染色）
    c = np.array([0.55 + 0.25 * _noise1(t * 0.7, 21), 0.6 + 0.2 * _noise1(t * 0.5, 22), 0.8 + 0.2 * _noise1(t * 0.6, 23)])
    c = np.clip(c, 0.2, 1.0)
    x = tv.x1 + 0.01
    return make_light(RECT, c, 1.1 * on, pos=(x, 3.00, 0.82), vec=(0, 0.40, 0), vec2=(0, 0, 0.30), samples=4)


def phone_light(pos, on=1.0):
    """手机屏幕：朝上的小面光源。"""
    return make_light(RECT, np.array([0.70, 0.82, 1.0]), 0.9 * on, pos=(pos[0] - 0.035, pos[1] - 0.07, pos[2]),
                      vec=(0.07, 0, 0), vec2=(0, 0.14, 0), samples=4)


def sheet_glow_lights(sheet_rad_back, sheet_rad_front, nx=4, nz=2):
    """把被照亮的床单当作面光源（分块，每块用平均亮度）。
    sheet_rad_*：(H, W, 3) 床单两面的出射亮度贴图。北面（后台）一侧和南面（观众）一侧各一组。"""
    s = L.SHEET
    out = []
    H, W, _ = sheet_rad_back.shape
    for side, rad, y in (("back", sheet_rad_back, s.y1 + 0.003), ("front", sheet_rad_front, s.y0 - 0.003)):
        for a in range(nx):
            for b in range(nz):
                tile = rad[b * H // nz:(b + 1) * H // nz, a * W // nx:(a + 1) * W // nx].reshape(-1, 3).mean(0)
                if tile.sum() < 1e-5:
                    continue
                x0 = s.x0 + (s.x1 - s.x0) * a / nx
                z1 = s.z1 - (s.z1 - s.z0) * b / nz
                du = (s.x1 - s.x0) / nx
                dz = -(s.z1 - s.z0) / nz
                # 面法线 = u × v，需要朝外：后台一侧朝 +y，观众一侧朝 -y
                if side == "back":
                    o, u, v = (x0, y, z1), (du, 0, 0), (0, 0, dz)
                else:
                    o, u, v = (x0 + du, y, z1), (-du, 0, 0), (0, 0, dz)
                area = du * abs(dz)
                # 朗伯面光源：tile 是辐射亮度；E = ∫ L cos cos / d² dA ≈ L·A·平均(cos cos / d²)
                out.append(make_light(RECT, tile, area, pos=o, vec=u, vec2=v, samples=4))
    return out
