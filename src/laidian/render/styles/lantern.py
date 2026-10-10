"""画风 A「灯影」：把皮影的造型语言延伸到整个画面。

- 明暗分成几层色阶，像一层层染过色的牛皮；灯光因此自然铺成一圈一圈。
- 有光的地方颜色更饱和、更暖（光透过染色的皮），暗处是深棕，不是死黑。
- 每种材质有自己的"刀纹"（墙面的刮痕、木纹、碎花），只在受光处透亮——纹理是光照的结果，不是滤镜。
- 轮廓是刀刻的深棕线，略有起伏。
- 床单上的戏保留物理计算出的透光颜色，是全画面最亮、最纯的地方。
"""
import math

import numpy as np
from scipy import ndimage

from .. import textures as TX
from ..materials import M
from .common import (downsample, edges, face_layers, filmic, flame_shape, glow, linear_to_srgb, luminance,
                     project, total_light, world_noise)

LEVELS = np.array([0.0, 0.028, 0.085, 0.20, 0.42, 0.78, 1.25])
INK = np.array([0.030, 0.016, 0.010])
SHADOW = np.array([0.020, 0.011, 0.008])


def band(Y, soft=0.10):
    """把亮度量化成色阶（边缘略软）。"""
    out = np.zeros_like(Y)
    for k in range(1, len(LEVELS)):
        lo, hi = LEVELS[k - 1], LEVELS[k]
        t = np.clip((Y - lo) / max(hi - lo, 1e-6), 0, 1)
        step = np.clip((t - 0.5) / soft + 0.5, 0, 1)
        out = np.where(Y >= lo, lo + (hi - lo) * step, out)
    return out


def patterns(buf):
    """各材质的刀纹（0–1）。用世界坐标，镜头动也不会"游"。"""
    H, W = buf.MAT.shape
    P = buf.P
    pat = np.zeros((H, W))
    mat = buf.MAT

    def sel(n):
        return mat == M(n)

    m = sel("plaster")
    if m.any():
        p = P[m]
        streak = TX.vnoise(p * np.array([60.0, 60.0, 2.5]), 5)
        dots = TX.vnoise(p * 70.0, 7) > 0.93
        pat[m] = np.clip((streak - 0.72) * 4, 0, 1) * 0.6 + dots * 0.5
    for n in ("wood_dark", "chest", "beam", "column", "door_wood", "wood_raw"):
        m = sel(n)
        if m.any():
            p = P[m]
            g = TX.fbm(p * np.array([1.0, 9.0, 9.0]) if n == "beam" else p * np.array([9.0, 9.0, 1.0]) if n in ("column", "door_wood") else p * np.array([1.0, 9.0, 9.0]), 3, 13)
            pat[m] = np.clip(1 - np.abs(np.sin(g * 40.0)) * 6, 0, 1) * 0.7
    m = sel("concrete")
    if m.any():
        p = P[m]
        pat[m] = np.clip((TX.ridged(p * 1.3, 4, 11) - 0.6) * 5, 0, 1)
    m = sel("blouse_nn")
    if m.any():
        # 碎花：一朵朵五瓣小花刻空
        p = P[m] * 110.0
        cell = np.floor(p)
        f = p - cell - 0.5
        jit = TX._hash3(cell[:, 0].astype(np.int64), cell[:, 1].astype(np.int64), cell[:, 2].astype(np.int64), 3)
        r = np.sqrt((f ** 2).sum(-1))
        ang = np.arctan2(f[:, 1], f[:, 0] + f[:, 2])
        petal = 0.22 + 0.10 * np.cos(5 * ang + jit * 6)
        pat[m] = (r < petal) * (jit > 0.35) * 0.9
    m = sel("tshirt_xm")
    if m.any():
        p = P[m]
        pat[m] = (np.abs(((p[:, 2] * 40.0) % 1.0) - 0.5) > 0.46) * 0.25   # 针织横纹
    m = sel("bamboo")
    if m.any():
        p = P[m]
        pat[m] = (np.abs(((p[:, 0] * 66.0) % 1.0) - 0.5) > 0.40) * 0.8
    return pat


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    rad = A * E / math.pi
    x = rad * ctx.get("exposure", 1.0)
    Y = luminance(x)
    chroma = x / np.maximum(Y, 1e-6)[..., None]
    Yb = band(Y)
    # 受光处更饱和、更暖
    lit = np.clip(Yb / 0.42, 0, 1)
    gray = chroma.mean(-1, keepdims=True)
    chroma = gray + (chroma - gray) * (1.0 + 0.45 * lit[..., None])
    out = chroma * Yb[..., None]
    out = out * (1 + np.array([0.06, 0.0, -0.06]) * lit[..., None])
    # 暗部：深棕而不是黑
    out = np.maximum(out, SHADOW * (1 - lit[..., None]))
    # 刀纹：只在亮处透光
    pat = patterns(buf)
    glowp = np.clip((Y - 0.12) / 0.35, 0, 1)
    out = out * (1 + 0.55 * (pat * glowp)[..., None]) - (pat * (1 - glowp) * 0.25)[..., None] * out
    # 床单：保留物理透光，不分色阶
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.05)
    out[sheet] = xs * 1.12
    # 皮影本身（背面直接看到）：透光的颜色更亮一点
    # 人物五官
    chars = ctx.get("chars")
    fl = face_layers(buf, ctx.get("faces", []), chars, ss)
    skin_light = np.clip(Yb / 0.3, 0.15, 1.0)[..., None]
    out = out * (1 - 0.35 * fl["blush"][..., None]) + np.array([0.55, 0.18, 0.15]) * 0.35 * fl["blush"][..., None] * skin_light
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.20, 0.04, 0.03]) * fl["mouth"][..., None] * skin_light
    out = out * (1 - fl["line"][..., None] * 0.6) + INK * fl["line"][..., None] * 0.6
    out = out * (1 - fl["ink"][..., None]) + INK * fl["ink"][..., None]
    out = out * (1 - fl["glass"][..., None]) + np.array([0.12, 0.08, 0.05]) * fl["glass"][..., None]
    out = out * (1 - fl["white"][..., None]) + np.array([0.95, 0.9, 0.8]) * skin_light * fl["white"][..., None]
    # 刀刻轮廓
    outline, inner = edges(buf, scene, chars, mr_w=0.0045 / ss)
    k = int(round(1.6 * ss))
    ol = ndimage.maximum_filter(outline, size=k)
    wob = world_noise(buf.P, 18.0, 4, 2)
    ol = ol * (wob > 0.32)
    il = ndimage.maximum_filter(inner, size=max(1, k - 1)) * 0.55
    line_col = INK * (0.6 + 0.4 * (1 - lit))[..., None]
    out = out * (1 - ol[..., None]) + line_col * ol[..., None]
    out = out * (1 - il[..., None] * (1 - lit[..., None] * 0.5)) + line_col * il[..., None] * (1 - lit[..., None] * 0.5)
    # 发光体
    out = add_sources(out, buf, ctx, style="lantern")
    # 没打到任何东西（窗外）
    out[~buf.hit] = ctx.get("sky", np.array([0.006, 0.008, 0.016]))
    # 皮面纹理：整个画面一层很细的纤维，亮处更明显
    yy, xx = np.mgrid[0:H, 0:W]
    fp = np.stack([xx * 0.35 / ss, yy * 0.03 / ss, np.zeros((H, W))], -1)
    fiber = TX.vnoise(fp, 9)
    out = out * (0.94 + 0.12 * fiber[..., None] * (0.3 + 0.7 * lit[..., None]))
    img = downsample(out, ss)
    return (linear_to_srgb(filmic(img * 1.0) if ctx.get("final_filmic") else np.clip(img, 0, 1)) * 255).astype(np.uint8)


def add_sources(out, buf, ctx, style="lantern"):
    """马灯火苗与玻璃罩的光晕、日光灯管、手机/电视屏幕。"""
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    t = ctx.get("t", 0.0)
    for src in ctx.get("sources", []):
        kind = src["kind"]
        q = project(cam, src["pos"], W, H)
        if q[2] <= 0:
            continue
        # 被挡住了吗（深度比较）
        xi, yi = int(q[0]), int(q[1])
        visible = 0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q[2] - 0.05
        px_per_m = W / (2 * cam.tan_half * q[2])
        if kind == "lamp":
            inten = src.get("intensity", 1.0)
            g = glow((H, W), q[:2], 0.09 * px_per_m, 1.6) * inten
            # 一圈一圈的光晕（灯影画风的标志）
            if style == "lantern":
                rings = np.floor(np.clip(g, 0, 1) * 5) / 5
                out += np.array([1.0, 0.55, 0.20])[None, None] * (rings * 0.20)[..., None]
            else:
                out += np.array([1.0, 0.6, 0.25])[None, None] * (g * 0.25)[..., None]
            if visible:
                core, outer = flame_shape((H, W), (q[0], q[1] + 0.006 * px_per_m), 0.030 * px_per_m, 0.009 * px_per_m, t)
                out = out * (1 - outer[..., None]) + np.array([1.0, 0.62, 0.22]) * 1.6 * outer[..., None]
                out = out * (1 - core[..., None]) + np.array([1.0, 0.92, 0.70]) * 1.8 * core[..., None]
        elif kind == "tube":
            pass
    return out
