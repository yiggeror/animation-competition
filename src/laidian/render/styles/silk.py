"""画风 C「绢灯」：一幅会动的绢本工笔画，灯光是真实的。

- 底子是旧绢：细密经纬、微微泛黄、边上有年久的晕。
- 铁线描：轮廓用均匀的细墨线；人物的线比背景的线略重。
- 设色：固有色像矿物颜料（石青、石绿、朱砂、赭石）一样平涂，不画立体渐变。
- 光：受光处颜料"透出来"、偏暖金；背光处一层层罩淡墨，墨色里带花青——夜是蓝黑的，不是灰的。
- 床单：画面里唯一"发光"的东西，像绢的背后点了灯。
"""
import math

import numpy as np
from scipy import ndimage

from .. import chardecals as CD
from .. import textures as TX
from ..materials import M
from .common import (screens, downsample, edges, face_layers, filmic, flame_shape, glow, linear_to_srgb, luminance,
                     project, total_light, world_noise)

SILK = np.array([0.78, 0.68, 0.50])
INK = np.array([0.040, 0.034, 0.032])
NIGHT = np.array([0.030, 0.045, 0.085])     # 花青 + 墨
GOLD = np.array([1.00, 0.74, 0.36])


def mineral(A):
    g = A.mean(-1, keepdims=True)
    B = g + (A - g) * 1.05
    return np.clip(B * 0.9 + 0.04, 0, 1)


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    x = A * E / math.pi * ctx.get("exposure", 1.0)
    Y = luminance(x)
    Lv = np.clip(filmic(Y * 1.5) / 0.85, 0, 1)
    Ec = E / np.maximum(luminance(E), 1e-6)[..., None]
    Ec = Ec / np.maximum(Ec.max(-1, keepdims=True), 1e-6)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # 绢底
    warp = 0.5 + 0.5 * np.sin(xx / ss * 2.4)
    weft = 0.5 + 0.5 * np.sin(yy / ss * 2.1 + 0.3 * np.sin(xx / (40 * ss)))
    silk = SILK * (0.94 + 0.06 * warp * weft)[..., None]
    stain = TX.fbm(np.stack([xx / (260.0 * ss), yy / (260.0 * ss), np.zeros((H, W))], -1), 4, 33)
    silk = silk * (0.88 + 0.16 * stain[..., None])
    # 设色：平涂矿物色，亮度只分"受光 / 背光"两层，中间用墨晕柔和过渡
    pig = mineral(A) * (0.55 + 0.45 * Ec)
    lit = np.clip((Lv - 0.18) / 0.30, 0, 1)
    lit = lit * lit * (3 - 2 * lit)
    body = pig * (silk / SILK.mean()) * (0.62 + 0.38 * np.where(Lv > 0.65, 1.0, 0.8))[..., None]
    # 背光：墨 + 花青，墨色深浅随光的强弱，边缘带一点水迹
    inkwash = NIGHT * (0.55 + 0.9 * Lv[..., None]) + pig * 0.12 * Lv[..., None]
    out = inkwash * (1 - lit[..., None]) + body * lit[..., None]
    edge_w = np.abs(ndimage.sobel(lit, 0)) + np.abs(ndimage.sobel(lit, 1))
    edge_w = np.clip(ndimage.gaussian_filter(edge_w, 1.2 * ss) * 0.5, 0, 0.3)
    out = out * (1 - edge_w[..., None] * 0.6)
    # 暖光：受光处罩一层金
    warm = lit * np.clip(Ec[..., 0] - Ec[..., 2], 0, 1)
    out = out * (1 - 0.22 * warm[..., None]) + GOLD * (silk / SILK.mean()) * 0.22 * warm[..., None] * Lv[..., None]
    # 床单
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.1)
    out[sheet] = xs * (silk[sheet] / SILK.mean()) * 1.06
    # 人物细节
    chars = ctx.get("chars")
    faces = ctx.get("faces", [])
    fl = face_layers(buf, faces, chars, ss)
    cd = CD.layers(buf, chars, faces)
    litc = (0.35 + 0.65 * lit)[..., None]
    out = out * (1 - 0.3 * fl["blush"][..., None]) + np.array([0.78, 0.36, 0.30]) * 0.3 * fl["blush"][..., None] * litc
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.50, 0.12, 0.09]) * fl["mouth"][..., None] * litc
    for key, a in (("line", 0.55), ("ink", 1.0), ("glass", 0.9)):
        out = out * (1 - a * fl[key][..., None]) + INK * a * fl[key][..., None]
    out = out * (1 - fl["white"][..., None]) + silk * 1.2 * fl["white"][..., None] * litc
    for key, a in (("hair", 0.45), ("cloth_line", 0.8)):
        out = out * (1 - a * cd[key][..., None]) + INK * a * cd[key][..., None]
    out = out * (1 - cd["print_light"][..., None]) + silk * 1.15 * cd["print_light"][..., None] * litc
    out = out * (1 - cd["button"][..., None]) + silk * 1.2 * cd["button"][..., None] * litc
    out = out + screens(buf, ctx)
    # 铁线描
    outline, inner = edges(buf, scene, chars, mr_w=0.0038 / ss)
    ol = np.clip(ndimage.gaussian_filter(outline, 0.45 * ss) * 2.0, 0, 1)
    isch = buf.CP >= 0
    near_ch = ndimage.maximum_filter(isch.astype(float), size=3 * ss)
    weight = np.where(near_ch > 0, 1.0, 0.75)
    out = out * (1 - (ol * weight)[..., None]) + INK * (ol * weight)[..., None]
    il = np.clip(ndimage.gaussian_filter(inner, 0.45 * ss), 0, 1) * 0.45
    out = out * (1 - il[..., None]) + INK * il[..., None]
    # 灯
    for src in ctx.get("sources", []):
        q_ = project(cam, src["pos"], W, H)
        if q_[2] <= 0 or src["kind"] != "lamp":
            continue
        xi, yi = int(q_[0]), int(q_[1])
        if not (0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q_[2] - 0.05):
            continue
        ppm = W / (2 * cam.tan_half * q_[2])
        g = glow((H, W), q_[:2], 0.08 * ppm, 2.0)
        out = out + GOLD * (g * 0.30)[..., None]
        core, outer = flame_shape((H, W), (q_[0], q_[1] + 0.006 * ppm), 0.030 * ppm, 0.009 * ppm, ctx.get("t", 0.0))
        out = out * (1 - outer[..., None]) + GOLD * 1.15 * outer[..., None]
        out = out * (1 - core[..., None]) + np.array([1.0, 0.96, 0.82]) * core[..., None]
    out[~buf.hit] = NIGHT
    # 画边年久的暗晕
    vig = ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2)
    out = out * (1 - 0.35 * np.clip(vig * 1.6, 0, 1))[..., None]
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)
