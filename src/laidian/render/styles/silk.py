"""画风 C「绢灯」：绢本工笔 + 真实的灯光。

- 底子是旧绢（细密的经纬纹，微微泛黄）。
- 铁线描：所有轮廓用均匀的细墨线勾出，折痕用更淡的线。
- 固有色像矿物颜料一样平涂（石青、石绿、朱砂、赭石），再按光照"分染"：亮处颜色透出绢底，暗处一层层罩淡墨。
- 灯光是一层暖金色的罩染；夜色是花青。
- 床单上的戏仍是物理透光，像绢背后点了灯。
"""
import math

import numpy as np
from scipy import ndimage

from .. import textures as TX
from ..materials import M
from .common import (downsample, edges, face_layers, filmic, flame_shape, glow, linear_to_srgb, luminance,
                     project, total_light, world_noise)

SILK = np.array([0.80, 0.70, 0.52])
INK = np.array([0.045, 0.035, 0.030])
INDIGO = np.array([0.055, 0.085, 0.16])
GOLD = np.array([1.00, 0.70, 0.32])


def mineral(A):
    """把反照率推向矿物颜料的色域：略降饱和、偏暖、提亮暗色。"""
    g = A.mean(-1, keepdims=True)
    B = g + (A - g) * 0.85
    B = B * np.array([1.03, 1.0, 0.92])
    return np.clip(B * 0.85 + 0.06, 0, 1)


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    rad = A * E / math.pi
    x = rad * ctx.get("exposure", 1.0)
    Y = luminance(x)
    Yt = filmic(Y * 1.3)
    Ec = E / np.maximum(luminance(E), 1e-6)[..., None]
    Ec = Ec / np.maximum(Ec.max(-1, keepdims=True), 1e-6)
    # 绢底
    yy, xx = np.mgrid[0:H, 0:W]
    warp = np.sin(xx / ss * 2.1) * 0.5 + 0.5
    weft = np.sin(yy / ss * 2.3) * 0.5 + 0.5
    silk = SILK * (0.93 + 0.05 * warp * weft)[..., None]
    stain = TX.fbm(np.stack([xx / (180.0 * ss), yy / (180.0 * ss), np.zeros((H, W))], -1), 4, 33)
    silk = silk * (0.92 + 0.12 * stain[..., None])
    # 颜料：固有色 × 光色（暖灯下更金、月下更青）
    pig = mineral(A)
    lightcol = 0.55 + 0.45 * Ec
    color = pig * lightcol
    # 分染：按亮度分几层淡墨，层与层之间有水迹边
    shade = 1 - np.clip(Yt / 0.75, 0, 1)
    q = np.floor(shade * 4 + (world_noise(buf.P, 6.0, 7, 2) - 0.5) * 0.6) / 4
    q = np.clip(q, 0, 1)
    edge_dark = np.abs(np.gradient(q, axis=0)) + np.abs(np.gradient(q, axis=1))
    edge_dark = ndimage.gaussian_filter(edge_dark, 0.8 * ss) * 0.8
    wash = INK * 0.0 + 1.0
    out = color * (1 - 0.72 * q[..., None]) * silk / SILK.mean()
    out = out * (1 - np.clip(edge_dark, 0, 0.25)[..., None])
    # 夜色：花青罩在暗处
    night = np.clip(1 - Yt / 0.35, 0, 1) ** 1.5
    out = out * (1 - 0.65 * night[..., None]) + INDIGO * 0.65 * night[..., None] * (silk / SILK.mean())
    # 灯光：暖金罩染
    warm = np.clip((Yt - 0.25) / 0.6, 0, 1) * np.clip(Ec[..., 0] - Ec[..., 2], 0, 1)
    out = out * (1 - 0.25 * warm[..., None]) + GOLD * 0.25 * warm[..., None]
    # 床单
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.1)
    out[sheet] = xs * (silk[sheet] / SILK.mean()) * 1.05
    # 五官
    chars = ctx.get("chars")
    fl = face_layers(buf, ctx.get("faces", []), chars, ss)
    out = out * (1 - 0.3 * fl["blush"][..., None]) + np.array([0.75, 0.32, 0.28]) * 0.3 * fl["blush"][..., None]
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.45, 0.10, 0.08]) * fl["mouth"][..., None]
    for k, a in (("line", 0.55), ("ink", 1.0), ("glass", 0.9)):
        out = out * (1 - a * fl[k][..., None]) + INK * a * fl[k][..., None]
    out = out * (1 - fl["white"][..., None]) + silk * 1.15 * fl["white"][..., None]
    # 铁线描
    outline, inner = edges(buf, scene, chars, mr_w=0.0035 / ss)
    ol = ndimage.gaussian_filter(outline, 0.5 * ss)
    ol = np.clip(ol * 2.2, 0, 1)
    dry = world_noise(buf.P, 25.0, 9, 2) > 0.28
    out = out * (1 - ol[..., None] * 0.92 * dry[..., None]) + INK * ol[..., None] * 0.92 * dry[..., None]
    il = ndimage.gaussian_filter(inner, 0.5 * ss) * 0.5
    out = out * (1 - il[..., None]) + INK * il[..., None]
    # 发光体：金色晕
    for src in ctx.get("sources", []):
        q_ = project(cam, src["pos"], W, H)
        if q_[2] <= 0 or src["kind"] != "lamp":
            continue
        ppm = W / (2 * cam.tan_half * q_[2])
        g = glow((H, W), q_[:2], 0.12 * ppm, 1.8)
        out = out + GOLD * (g * 0.22)[..., None]
        xi, yi = int(q_[0]), int(q_[1])
        if 0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q_[2] - 0.05:
            core, outer = flame_shape((H, W), (q_[0], q_[1] + 0.006 * ppm), 0.030 * ppm, 0.009 * ppm, ctx.get("t", 0.0))
            out = out * (1 - outer[..., None]) + GOLD * 1.1 * outer[..., None]
            out = out * (1 - core[..., None]) + np.array([1.0, 0.95, 0.80]) * core[..., None]
    out[~buf.hit] = INDIGO * 0.6
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)
