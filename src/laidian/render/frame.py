"""一帧的渲染流程：主光线 → 人物 → 直接光 → 间接光 → 遮蔽，输出 G-buffer。

画风（风格化合成）只读这里输出的缓冲，不再自己"发明"光影——
所以每种画风的明暗、阴影、颜色都来自同一套光照计算。
"""
import time
from dataclasses import dataclass, field

import numpy as np

from . import light as LT
from . import rt, sdf
from .camera import Camera
from .materials import MATS, albedo_table


def diffuser_table():
    return np.array([1.0 if m.transmit > 0 and m.name == "sheet" else 0.0 for m in MATS])


SHEET_R = 0.55   # 棉床单：反射
SHEET_T = 0.42   # 棉床单：漫透射


@dataclass
class Buffers:
    W: int
    H: int
    T: np.ndarray          # 深度（沿视线）
    ID: np.ndarray         # 静态图元编号（人物处为 -1）
    CP: np.ndarray         # 人物图元编号（无为 -1）
    MAT: np.ndarray        # 材质编号
    N: np.ndarray
    P: np.ndarray
    UV: np.ndarray
    D: np.ndarray          # 视线方向
    E: np.ndarray          # 每个光源的直接辐照度 (H,W,nl,3)
    EB: np.ndarray         # 间接光 (H,W,3)
    AO: np.ndarray
    MR: np.ndarray         # 人物轮廓指标
    hit: np.ndarray
    light_names: list = field(default_factory=list)
    timings: dict = field(default_factory=dict)


def render(scene, cam: Camera, lights, light_names, W, H, chars=None, groups=None,
           jitter=(0.5, 0.5), vpl_n=40, ao=True, ao_radius=0.35, bounce_lights=None):
    tm = {}
    if chars is None:
        chars, groups = sdf.empty()
    o, f, r, u = cam.basis()
    t0 = time.time()
    T, ID, N, UV, P, D = rt.primary(scene.prims, scene.nodes, scene.order, o, f, r, u, cam.tan_half, W, H,
                                    scene.atlas, scene.rects, jitter[0], jitter[1])
    tm["primary"] = time.time() - t0
    MAT = np.where(ID >= 0, scene.prims[np.maximum(ID, 0), 1], 0).astype(np.int32)
    CP = np.full((H, W), -1, np.int32)
    MR = np.full((H, W), 1e9, np.float32)
    if chars.shape[0] > 0:
        t0 = time.time()
        TC, PC, NC, MR = sdf.primary(chars, groups, o, f, r, u, cam.tan_half, W, H, T, jitter[0], jitter[1])
        m = PC >= 0
        T = np.where(m, TC, T)
        N = np.where(m[..., None], NC, N)
        P = np.where(m[..., None], o + D * TC[..., None], P)
        CP = PC
        MAT = np.where(m, chars[np.maximum(PC, 0), 1].astype(np.int32), MAT)
        ID = np.where(m, -1, ID)
        tm["chars"] = time.time() - t0
    hit = (ID >= 0) | (CP >= 0)
    lights = np.asarray(lights, float).reshape(-1, LT.NL)
    bn = LT.blue_noise(H, W)
    t0 = time.time()
    E, SIDE = LT.direct(P, N, ID, MAT, diffuser_table(), scene.prims, scene.nodes, scene.order, scene.atlas, scene.rects,
                        lights, chars, groups, bn, hit)
    tm["direct"] = time.time() - t0
    t0 = time.time()
    EB = np.zeros((H, W, 3), np.float32)
    bl = lights if bounce_lights is None else bounce_lights
    for k in range(bl.shape[0]):
        v = LT.make_vpls(bl[k], scene, n=vpl_n, seed=11 + k)
        if v.shape[0]:
            EB += LT.bounce(P, N, v, hit, 0.15)
    tm["bounce"] = time.time() - t0
    t0 = time.time()
    if ao:
        AO = LT.ambient_occlusion(P, N, ID, scene.prims, scene.nodes, scene.order, scene.atlas, scene.rects,
                                  chars, groups, hit, ao_radius, 8, bn)
    else:
        AO = np.ones((H, W), np.float32)
    tm["ao"] = time.time() - t0
    b = Buffers(W, H, T, ID, CP, MAT, N, P, UV, D, E, EB, AO, MR, hit, list(light_names), tm)
    b.SIDE = SIDE
    return b


def physical_preview(buf: Buffers, exposure=1.0, albedo=None, emissive=None):
    """不加画风的物理预览：反照率 × 总光照，再做色调映射。用来检查光照本身对不对。"""
    if albedo is None:
        albedo = albedo_table()[buf.MAT]
    # 床单：同侧光反射，背侧光透射
    dif = diffuser_table()[buf.MAT] > 0
    w = np.where(buf.SIDE > 0, 1.0, SHEET_T / SHEET_R)[..., None]
    w = np.where(dif[..., None, None], w, 1.0)
    E = (buf.E * w).sum(axis=2) + buf.EB * buf.AO[..., None]
    rad = albedo * E / np.pi
    if emissive is not None:
        rad = rad + emissive
    rad = np.where(buf.hit[..., None], rad, 0)
    x = rad * exposure
    # 简单的胶片曲线
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    return (np.where(y <= 0.0031308, 12.92 * y, 1.055 * np.power(y, 1 / 2.4) - 0.055) * 255).astype(np.uint8)


def upsample_guided(X, ID_lo, ID_hi, ss):
    """把低分辨率的光照放大到高分辨率：优先取同一物体的邻近样本，避免光照渗到别的物体上。"""
    H, W = ID_hi.shape
    h, w = ID_lo.shape
    ys = np.minimum(np.arange(H) // ss, h - 1)
    xs = np.minimum(np.arange(W) // ss, w - 1)
    out = X[ys][:, xs].copy()
    base_id = ID_lo[ys][:, xs]
    bad = base_id != ID_hi
    if bad.any():
        jj, ii = np.nonzero(bad)
        y0, x0 = ys[jj], xs[ii]
        done = np.zeros(len(jj), bool)
        for dy in (0, -1, 1, -2, 2):
            for dx in (0, -1, 1, -2, 2):
                yy = np.clip(y0 + dy, 0, h - 1)
                xx = np.clip(x0 + dx, 0, w - 1)
                ok = (~done) & (ID_lo[yy, xx] == ID_hi[jj, ii])
                out[jj[ok], ii[ok]] = X[yy[ok], xx[ok]]
                done |= ok
    return out


def render_ss(scene, cam, lights, light_names, W, H, ss=2, chars=None, groups=None, denoise=True, keep_mats=(), **kw):
    """高分辨率几何（画线、贴花用）+ 低分辨率光照（放大后合成），最后由画风合成再缩小。"""
    from .denoise import denoise_buffers
    lo = render(scene, cam, lights, light_names, W, H, chars, groups, **kw)
    if denoise:
        lo = denoise_buffers(lo, keep_mats=keep_mats)
    if chars is None:
        chars, groups = sdf.empty()
    o, f, r, u = cam.basis()
    Wh, Hh = W * ss, H * ss
    T, ID, N, UV, P, D = rt.primary(scene.prims, scene.nodes, scene.order, o, f, r, u, cam.tan_half, Wh, Hh,
                                    scene.atlas, scene.rects, 0.5, 0.5)
    MAT = np.where(ID >= 0, scene.prims[np.maximum(ID, 0), 1], 0).astype(np.int32)
    CP = np.full((Hh, Wh), -1, np.int32)
    MR = np.full((Hh, Wh), 1e9, np.float32)
    if chars.shape[0] > 0:
        TC, PC, NC, MR = sdf.primary(chars, groups, o, f, r, u, cam.tan_half, Wh, Hh, T, 0.5, 0.5)
        m = PC >= 0
        T = np.where(m, TC, T)
        N = np.where(m[..., None], NC, N)
        P = np.where(m[..., None], o + D * TC[..., None], P)
        CP = PC
        MAT = np.where(m, chars[np.maximum(PC, 0), 1].astype(np.int32), MAT)
        ID = np.where(m, -1, ID)
    hit = (ID >= 0) | (CP >= 0)
    obj_lo = np.where(lo.CP >= 0, 100000 + lo.CP, lo.ID)
    obj_hi = np.where(CP >= 0, 100000 + CP, ID)
    nl = lo.E.shape[2]
    E = upsample_guided(lo.E.reshape(H, W, nl * 3), obj_lo, obj_hi, ss).reshape(Hh, Wh, nl, 3)
    EB = upsample_guided(lo.EB, obj_lo, obj_hi, ss)
    AO = upsample_guided(lo.AO, obj_lo, obj_hi, ss)
    SIDE = upsample_guided(lo.SIDE, obj_lo, obj_hi, ss)
    b = Buffers(Wh, Hh, T, ID, CP, MAT, N, P, UV, D, E, EB, AO, MR, hit, list(light_names), lo.timings)
    b.SIDE = SIDE
    b.lo = lo
    b.ss = ss
    return b
