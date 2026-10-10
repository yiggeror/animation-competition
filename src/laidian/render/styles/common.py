"""各画风共用：光照汇总、床单、边线、五官、发光体、缩小输出。"""
import math

import numpy as np
from scipy import ndimage

from .. import face as FACE
from ..frame import SHEET_R, SHEET_T, diffuser_table
from ..materials import M, MATS
from ..textures import fbm, vnoise


def linear_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def filmic(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def luminance(c):
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722


def total_light(buf):
    """总辐照度（RGB）。床单：同侧光乘反射率、背侧光乘透射率（返回的是"等效反射"后的辐照度）。"""
    dif = diffuser_table()[buf.MAT] > 0
    w = np.where(buf.SIDE > 0, 1.0, SHEET_T / SHEET_R)[..., None]
    w = np.where(dif[..., None, None], w, 1.0)
    E = (buf.E * w).sum(axis=2)
    return E + buf.EB * buf.AO[..., None], dif


def per_light(buf):
    dif = diffuser_table()[buf.MAT] > 0
    w = np.where(buf.SIDE > 0, 1.0, SHEET_T / SHEET_R)[..., None]
    w = np.where(dif[..., None, None], w, 1.0)
    return buf.E * w


def object_ids(buf):
    return np.where(buf.CP >= 0, 100000 + buf.CP, buf.ID).astype(np.int64)


def char_group_ids(buf, chars):
    g = np.full(buf.CP.shape, -1, np.int64)
    m = buf.CP >= 0
    g[m] = chars[buf.CP[m], 2].astype(np.int64)
    return g


def edges(buf, scene, chars=None, depth_rel=0.04, crease=0.55, mr_w=None):
    """返回 (outline, inner)：轮廓线（物体之间、前后遮挡）和内部线（折痕）。值 0–1。"""
    H, W = buf.MAT.shape
    obj = object_ids(buf)
    # 同一个人物的不同图元算同一个物体，只有组（头/手/躯干…）不同时才算边
    if chars is not None and chars.shape[0]:
        g = char_group_ids(buf, chars)
        layer = np.full((H, W), -1)
        m = buf.CP >= 0
        layer[m] = chars[buf.CP[m], 23]
        obj = np.where(buf.CP >= 0, 100000 + g * 10 + layer, obj)
    # 静态物体：同一个"名字"的拼接件（墙体分块等）算一个物体
    if hasattr(scene, "names"):
        name_id = {}
        lut = np.array([name_id.setdefault(n.split(":")[0] if not n.startswith(("wall", "purlin", "rafter")) else n[:4], len(name_id))
                        for n in scene.names] + [-1])
        sid = np.where(buf.ID >= 0, lut[np.maximum(buf.ID, 0)], -1)
        obj = np.where(buf.CP >= 0, obj, sid)
    T = buf.T
    out = np.zeros((H, W))
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        o2 = np.roll(np.roll(obj, -dy, 0), -dx, 1)
        t2 = np.roll(np.roll(T, -dy, 0), -dx, 1)
        diff = (o2 != obj)
        dep = np.abs(t2 - T) / np.maximum(np.minimum(t2, T), 1e-3) > depth_rel
        e = (diff | dep).astype(float)
        # 线画在近的那一侧
        near_self = T <= t2
        out = np.maximum(out, e * near_self)
        out = np.maximum(out, np.roll(np.roll(e * ~near_self, dy, 0), dx, 1))
    # 人物轮廓：用球面追踪里的最小距离（光滑、不锯齿）
    if mr_w is not None:
        sil = np.clip(1 - buf.MR / mr_w, 0, 1) * (buf.CP < 0)
        out = np.maximum(out, sil)
    # 折痕：法线突变
    N = buf.N
    inner = np.zeros((H, W))
    for dy, dx in ((0, 1), (1, 0)):
        n2 = np.roll(np.roll(N, -dy, 0), -dx, 1)
        o2 = np.roll(np.roll(obj, -dy, 0), -dx, 1)
        same = o2 == obj
        dn = (N * n2).sum(-1)
        inner = np.maximum(inner, ((dn < crease) & same).astype(float))
    out[~buf.hit & (np.roll(buf.hit, 1, 0) | np.roll(buf.hit, 1, 1))] = 1
    return out, inner


def face_layers(buf, cams_info, chars, ss=1):
    """对每个人物的头部像素画五官。cams_info: [(who, info, expr), ...]，按人物在 chars 里的顺序。"""
    H, W = buf.MAT.shape
    layers = {k: np.zeros((H, W)) for k in ("ink", "white", "mouth", "blush", "glass", "line")}
    if chars is None or chars.shape[0] == 0:
        return layers
    for who, info, expr, g_head in cams_info:
        m = (buf.CP >= 0)
        m = m & (chars[np.maximum(buf.CP, 0), 2] == g_head) & (chars[np.maximum(buf.CP, 0), 23] == 0)
        if not m.any():
            continue
        # 一个像素在头部大约多少米（抗锯齿宽度）
        depth = np.median(buf.T[m])
        aa = depth * 2 * math.tan(math.radians(25)) / W * 1.2
        d = FACE.decals(buf.P, m, info["head_c"], info["head_R"], who, expr, aa)
        for k in layers:
            layers[k][m] = np.maximum(layers[k][m], d[k])
    return layers


def downsample(img, ss):
    if ss == 1:
        return img
    H, W, C = img.shape
    return img.reshape(H // ss, ss, W // ss, ss, C).mean(axis=(1, 3))


def project(cam, p, W, H):
    q = cam.project(np.asarray(p, float)[None], W, H)[0]
    return q


def glow(img_shape, center, radius, falloff=2.0):
    H, W = img_shape
    ys, xs = np.mgrid[0:H, 0:W]
    d = np.sqrt((xs - center[0]) ** 2 + (ys - center[1]) ** 2) / radius
    return 1.0 / (1.0 + d ** falloff)


def flame_shape(img_shape, center, h, w, t=0.0):
    """煤油灯火苗：下圆上尖的水滴形，带一点摆动。返回 (核心, 外焰) 覆盖率。"""
    H, W = img_shape
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    sway = math.sin(t * 7.3) * 0.08 + math.sin(t * 13.1) * 0.04
    yy = (ys - center[1]) / h        # 向下为正
    xx = (xs - center[0]) / w - sway * np.clip(-yy, 0, 1)
    # 水滴：y∈[-1, 0.35]
    rad = np.where(yy > 0, np.sqrt(np.clip(1 - (yy / 0.35) ** 2, 0, 1)), np.clip(1 + yy, 0, 1) ** 0.7)
    inside = np.clip((rad - np.abs(xx)) * 6, 0, 1) * (yy > -1) * (yy < 0.35)
    core = np.clip((rad * 0.55 - np.abs(xx)) * 8, 0, 1) * (yy > -0.6) * (yy < 0.3)
    return core, inside


def world_noise(P, scale, seed=0, octaves=3):
    return fbm(P * scale, octaves, seed)
