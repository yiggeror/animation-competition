"""被照亮的床单本身也是光源：算出床单两面的亮度，再把它变成面光源去照亮人和屋子。"""
import numpy as np

from .. import layout as L
from . import light as LT
from . import sdf
from .frame import SHEET_R, SHEET_T
from .lighting_states import sheet_glow_lights


def sheet_radiance(scene, lights, chars=None, groups=None, nx=24, nz=14):
    if chars is None:
        chars, groups = sdf.empty()
    s = L.SHEET
    xs = np.linspace(s.x0 + 0.02, s.x1 - 0.02, nx)
    zs = np.linspace(s.z1 - 0.02, s.z0 + 0.02, nz)
    X, Z = np.meshgrid(xs, zs)
    sid = [k for k, n in enumerate(scene.names) if n == "sheet"]
    if not sid:
        return None
    sid = sid[0]
    out = {}
    for side, ny, yoff in (("back", 1.0, 0.002), ("front", -1.0, -0.002)):
        P = np.stack([X, np.full_like(X, L.WIRE_Y + yoff), Z], -1)
        N = np.zeros_like(P)
        N[..., 1] = ny
        ID = np.full(X.shape, sid, np.int32)
        MAT = np.zeros(X.shape, np.int32)
        hit = np.ones(X.shape, bool)
        bn = LT.blue_noise(nz, nx, 5)
        E, _ = LT.direct(P, N, ID, MAT, np.zeros(64), scene.prims, scene.nodes, scene.order, scene.atlas, scene.rects,
                         np.asarray(lights, float).reshape(-1, LT.NL), chars, groups, bn, hit)
        out[side] = E.sum(axis=2)
    Eb, Ef = out["back"], out["front"]
    rad_back_side = (SHEET_R * Eb + SHEET_T * Ef) / np.pi
    rad_front_side = (SHEET_R * Ef + SHEET_T * Eb) / np.pi
    return rad_back_side, rad_front_side


def glow_lights(scene, lights, chars=None, groups=None, nx=2, nz=1):
    r = sheet_radiance(scene, lights, chars, groups)
    if r is None:
        return []
    return sheet_glow_lights(r[0], r[1], nx=nx, nz=nz)
