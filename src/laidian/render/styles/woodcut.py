"""画风 B「刻光」：黑底木刻，光是用刻刀刻出来的。

- 底子是墨黑；有光的地方刻出排线，排线的粗细 = 算出来的照度。全亮处排线连成一片。
- 排线方向跟着表面走：墙上是横线，地面是透视里的斜线，人物身上是环绕形体的等高线。
- 刻线的颜色就是光的颜色：马灯刻出暖橙，月光刻出冷蓝，日光灯刻出一片均匀的灰白（"平"）。
- 底下垫一层套色色块（略微错版），让器物有固有色。
- 床单上的戏不刻线：它是彩色玻璃一样的光——人的世界是刻出来的，戏的世界是亮出来的。
"""
import math

import numpy as np
from scipy import ndimage

from .. import textures as TX
from ..materials import M
from .common import (downsample, edges, face_layers, filmic, flame_shape, glow, linear_to_srgb, luminance,
                     per_light, project, total_light, world_noise)

INK = np.array([0.010, 0.009, 0.010])
PAPER = np.array([0.93, 0.89, 0.80])


def stroke_coord(buf, chars):
    """每个像素的排线坐标（世界单位，米）和该处一个像素对应的米数。"""
    P, N = buf.P, buf.N
    vert = np.abs(N[..., 2]) < 0.6
    # 竖直面：横线（等高线）；水平面：沿 x+0.45y 的斜线
    c = np.where(vert, P[..., 2], P[..., 0] * 0.9 + P[..., 1] * 0.43)
    isch = buf.CP >= 0
    # 人物：环绕形体的等高线，再随法线扭一点，显出体积
    c = np.where(isch, P[..., 2] + 0.012 * N[..., 2], c)
    return c


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    rad = A * E / math.pi
    x = rad * ctx.get("exposure", 1.0)
    Y = luminance(x)
    Yt = filmic(Y * 1.4)
    # 光的颜色（不含物体固有色）：决定刻线的颜色
    Ec = E / np.maximum(luminance(E), 1e-6)[..., None]
    Ec = Ec / np.maximum(Ec.max(-1, keepdims=True), 1e-6)
    # 排线
    px_m = buf.T * 2 * cam.tan_half / W       # 一个像素多少米
    spacing_px = np.where(buf.CP >= 0, 5.0, 7.0) * ss
    s = spacing_px * px_m
    c = stroke_coord(buf, ctx.get("chars"))
    wob = (world_noise(buf.P, 9.0, 3, 2) - 0.5) * 0.35 + (world_noise(buf.P, 40.0, 5, 1) - 0.5) * 0.12
    phase = c / np.maximum(s, 1e-6) + wob
    f = np.abs((phase % 1.0) - 0.5) * 2           # 0 = 刻线中心
    width = np.clip(Yt * 1.25, 0, 1.0)
    aa = 1.6 / spacing_px
    carved = np.clip((width - f) / aa + 0.5, 0, 1)
    carved = np.where(Yt > 0.80, 1.0, carved)
    # 刻线的颜色 = 光色 × 一点点固有色
    tint = A / np.maximum(A.max(-1, keepdims=True), 1e-6)
    linecol = PAPER * Ec * (0.55 + 0.45 * tint) * (0.65 + 0.45 * np.clip(Yt, 0, 1))[..., None]
    out = INK * (1 - carved[..., None]) + linecol * carved[..., None]
    # 套色块：固有色平涂在中间调，错版 2px
    block = np.roll(np.roll(A, 2 * ss // 2, 0), 1, 1)
    mid = np.clip((Yt - 0.08) / 0.25, 0, 1) * np.clip((0.9 - Yt) / 0.4, 0, 1)
    out = out * (1 - 0.38 * mid[..., None]) + block * Ec * 0.55 * 0.38 * mid[..., None]
    # 墨底的木纹（没刻到的地方，墨不是死黑）
    grain = TX.vnoise(buf.P * np.array([3.0, 3.0, 40.0]), 17)
    out = out + INK * 2.5 * ((grain > 0.75) * (1 - carved))[..., None]
    # 床单：不刻，直接是光
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.1)
    gray = xs.mean(-1, keepdims=True)
    xs = gray + (xs - gray) * 1.25
    out[sheet] = np.clip(xs, 0, 1)
    # 五官：亮处的脸留白（干净），五官用墨
    chars = ctx.get("chars")
    fl = face_layers(buf, ctx.get("faces", []), chars, ss)
    skin = np.isin(buf.MAT, [M("skin_xm"), M("skin_nn")])
    face_clean = skin & (Yt > 0.18)
    out[face_clean] = out[face_clean] * 0.3 + (PAPER * Ec[face_clean] * (0.55 + 0.45 * tint[face_clean]) * (0.6 + 0.5 * Yt[face_clean, None])) * 0.7
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.25, 0.05, 0.04]) * fl["mouth"][..., None]
    for k, a in (("line", 0.7), ("ink", 1.0), ("glass", 1.0)):
        out = out * (1 - a * fl[k][..., None]) + INK * a * fl[k][..., None]
    out = out * (1 - fl["white"][..., None]) + PAPER * fl["white"][..., None]
    # 轮廓：亮处留墨线（没刻掉的边），暗处本来就是墨
    outline, inner = edges(buf, scene, chars, mr_w=0.004 / ss)
    ol = ndimage.maximum_filter(outline, size=int(round(1.5 * ss)))
    out = out * (1 - ol[..., None]) + INK * ol[..., None]
    out = out * (1 - 0.6 * inner[..., None]) + INK * 0.6 * inner[..., None]
    # 发光体：灯芯刻成实心，周围刻出放射线
    for src in ctx.get("sources", []):
        q = project(cam, src["pos"], W, H)
        if q[2] <= 0 or src["kind"] != "lamp":
            continue
        ppm = W / (2 * cam.tan_half * q[2])
        ys, xs_ = np.mgrid[0:H, 0:W].astype(float)
        dx, dy = xs_ - q[0], ys - q[1]
        r = np.sqrt(dx * dx + dy * dy) + 1e-6
        ang = np.arctan2(dy, dx)
        rays = (np.abs(((ang / (2 * math.pi)) * 72) % 1.0 - 0.5) < 0.10 + 0.25 * np.exp(-r / (0.15 * ppm)))
        g = np.exp(-r / (0.22 * ppm))
        rr = rays * g * (r > 0.035 * ppm)
        out = out * (1 - rr[..., None]) + np.array([1.0, 0.72, 0.35]) * rr[..., None]
        xi, yi = int(q[0]), int(q[1])
        if 0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q[2] - 0.05:
            core, outer = flame_shape((H, W), (q[0], q[1] + 0.006 * ppm), 0.030 * ppm, 0.009 * ppm, ctx.get("t", 0.0))
            out = out * (1 - outer[..., None]) + np.array([1.0, 0.75, 0.35]) * outer[..., None]
            out = out * (1 - core[..., None]) + np.array([1.0, 0.97, 0.88]) * core[..., None]
    out[~buf.hit] = INK
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)
