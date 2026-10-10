"""画风 B「刻光」：黑底木刻，光是用刻刀刻出来的。

- 底子是墨黑（带木纹）；有光的地方刻出排线，排线的粗细 = 算出来的照度；全亮处连成一片。
- 排线跟着表面走：墙上横刻，地面顺着透视斜刻；人物身上用 45° 的斜刻（像版画里刻人物的刀法），
  亮面整片留白，暗面只剩几道刀痕。刀痕两头尖、粗细有起伏、偶尔断开——是手刻的，不是机器线。
- 刻线的颜色就是光的颜色：马灯刻出暖橙，月光刻出冷蓝，日光灯刻出一片平平的灰白。
- 底下垫一层套色（固有色的色块，故意错开一点版）。
- 床单上的戏不刻：它是彩色玻璃一样的光。人的世界是刻出来的，戏的世界是亮出来的。
"""
import math

import numpy as np
from scipy import ndimage

from .. import chardecals as CD
from .. import textures as TX
from ..materials import M
from .common import (screens, downsample, edges, face_layers, filmic, flame_shape, linear_to_srgb, luminance,
                     project, total_light, world_noise)

INK = np.array([0.012, 0.010, 0.011])
PAPER = np.array([0.95, 0.91, 0.82])


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    x = A * E / math.pi * ctx.get("exposure", 1.0)
    Y = luminance(x)
    Yt = filmic(Y * 1.5)
    Ec = E / np.maximum(luminance(E), 1e-6)[..., None]
    Ec = Ec / np.maximum(Ec.max(-1, keepdims=True), 1e-6)
    isch = buf.CP >= 0
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # ---- 排线坐标
    px_m = buf.T * 2 * cam.tan_half / W
    P, N = buf.P, buf.N
    vert = np.abs(N[..., 2]) < 0.6
    c_world = np.where(vert, P[..., 2], P[..., 0] * 0.9 + P[..., 1] * 0.43)
    spacing_world = 7.5 * ss * px_m
    phase_w = c_world / np.maximum(spacing_world, 1e-6)
    # 人物：画面坐标里的 45° 斜刻
    sp_c = 5.5 * ss
    phase_c = (xx + yy) / (sp_c * math.sqrt(2))
    phase = np.where(isch, phase_c, phase_w)
    # 手刻的不规则：每道刀的位置、粗细都随机起伏；偶尔断刀
    strand = np.floor(phase)
    jitter = TX._hash3(strand.astype(np.int64), np.zeros_like(strand, dtype=np.int64), np.full(strand.shape, 7, np.int64), 1)
    along = np.where(isch, (xx - yy) / (sp_c * 6), (P[..., 0] + P[..., 1] * 0.3) * 9.0)
    wob = (TX.vnoise(np.stack([strand * 0.37, along, np.zeros_like(along)], -1), 3) - 0.5) * 0.35
    f = np.abs(((phase + wob) % 1.0) - 0.5) * 2
    taper = 0.75 + 0.5 * TX.vnoise(np.stack([strand * 1.7, along * 0.6, np.ones_like(along)], -1), 9)
    width = np.clip(Yt * 1.3 * taper * (0.85 + 0.3 * jitter), 0, 1.05)
    aa = 1.5 / np.where(isch, sp_c, 7.5 * ss)
    carved = np.clip((width - f) / aa + 0.5, 0, 1)
    breaks = TX.vnoise(np.stack([strand * 2.3, along * 1.8, np.full_like(along, 3.0)], -1), 13) > 0.86
    carved = np.where(breaks & (Yt < 0.6), carved * 0.0, carved)
    carved = np.where(Yt > 0.82, 1.0, carved)
    # 人物亮面整片留白
    carved = np.where(isch & (Yt > 0.55), 1.0, carved)
    # ---- 刻线颜色 = 光色 × 一点固有色
    tint = A / np.maximum(A.max(-1, keepdims=True), 1e-6)
    linecol = PAPER * Ec * (0.6 + 0.4 * tint) * (0.62 + 0.45 * np.clip(Yt, 0, 1))[..., None]
    out = INK * (1 - carved[..., None]) + linecol * carved[..., None]
    # 套色：固有色色块（错版 2px），只在中间调
    shift = max(1, ss)
    block = np.roll(np.roll(A, shift, 0), shift, 1)
    mid = np.clip((Yt - 0.10) / 0.25, 0, 1) * np.clip((0.95 - Yt) / 0.35, 0, 1)
    out = out * (1 - 0.32 * mid[..., None]) + block * (0.5 + 0.5 * Ec) * 0.42 * 0.32 * mid[..., None] * 2.0
    # 墨底的木纹
    grain = TX.vnoise(np.stack([xx / (90.0 * ss), yy / (3.0 * ss), np.zeros_like(xx)], -1), 17)
    out = out + INK * 3.0 * ((grain > 0.72) * (1 - carved))[..., None]
    # ---- 床单：不刻线，直接是光
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.1)
    gray = xs.mean(-1, keepdims=True)
    out[sheet] = np.clip(gray + (xs - gray) * 1.25, 0, 1)
    # ---- 人物细节
    chars = ctx.get("chars")
    faces = ctx.get("faces", [])
    fl = face_layers(buf, faces, chars, ss)
    cd = CD.layers(buf, chars, faces)
    skin = np.isin(buf.MAT, [M("skin_xm"), M("skin_nn")])
    face_clean = skin & (Yt > 0.16)
    fc = PAPER * Ec * (0.6 + 0.4 * tint) * (0.62 + 0.5 * Yt[..., None])
    out[face_clean] = fc[face_clean]
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.30, 0.06, 0.04]) * fl["mouth"][..., None]
    out = out * (1 - fl["brow_halo"][..., None]) + PAPER * 0.85 * fl["brow_halo"][..., None]
    for key, a in (("line", 0.7), ("ink", 1.0), ("glass", 1.0)):
        out = out * (1 - a * fl[key][..., None]) + INK * a * fl[key][..., None]
    out = out * (1 - fl["white"][..., None]) + PAPER * fl["white"][..., None]
    hairm = np.isin(buf.MAT, [M("hair_xm"), M("hair_nn")])
    # 黑发：刻出亮的发丝；白发：本来就亮，刻墨线
    hl = cd["hair"] * hairm
    is_dark_hair = buf.MAT == M("hair_xm")
    out = np.where((is_dark_hair & (hl > 0.3))[..., None], linecol * 0.9, out)
    out = np.where((~is_dark_hair & hairm & (hl > 0.3))[..., None], INK, out)
    out = out * (1 - cd["cloth_line"][..., None]) + INK * cd["cloth_line"][..., None]
    out = out * (1 - cd["print_light"][..., None]) + PAPER * Ec * cd["print_light"][..., None]
    out = out * (1 - cd["button"][..., None]) + PAPER * cd["button"][..., None]
    out = out + screens(buf, ctx)
    # ---- 轮廓：亮处留墨线
    outline, inner = edges(buf, scene, chars, mr_w=0.0045 / ss)
    ol = ndimage.maximum_filter(outline, size=max(1, int(round(1.6 * ss))))
    out = out * (1 - ol[..., None]) + INK * ol[..., None]
    out = out * (1 - 0.6 * inner[..., None]) + INK * 0.6 * inner[..., None]
    # ---- 灯：看得见灯的时候，刻出放射的光芒
    for src in ctx.get("sources", []):
        q = project(cam, src["pos"], W, H)
        if q[2] <= 0 or src["kind"] != "lamp":
            continue
        xi, yi = int(q[0]), int(q[1])
        if not (0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q[2] - 0.05):
            continue
        ppm = W / (2 * cam.tan_half * q[2])
        dx, dy = xx - q[0], yy - q[1]
        r = np.sqrt(dx * dx + dy * dy) + 1e-6
        ang = np.arctan2(dy, dx)
        k = np.floor((ang / (2 * math.pi)) * 64)
        jit = TX._hash3(k.astype(np.int64), np.zeros_like(k, dtype=np.int64), np.zeros_like(k, dtype=np.int64), 5)
        rays = (np.abs(((ang / (2 * math.pi)) * 64) % 1.0 - 0.5) < 0.12 + 0.2 * np.exp(-r / (0.08 * ppm)))
        reach = (0.12 + 0.18 * jit) * ppm
        behind = buf.T > q[2] + 0.15          # 只画在灯后面的背景上（不压在灯身、人身上）
        rr = rays * (r < reach) * (r > 0.03 * ppm) * ~(dif & buf.hit) * behind * (buf.CP < 0)
        out = out * (1 - rr[..., None]) + np.array([1.0, 0.72, 0.35]) * rr[..., None]
        core, outer = flame_shape((H, W), (q[0], q[1] + 0.006 * ppm), 0.030 * ppm, 0.009 * ppm, ctx.get("t", 0.0))
        out = out * (1 - outer[..., None]) + np.array([1.0, 0.75, 0.35]) * outer[..., None]
        out = out * (1 - core[..., None]) + np.array([1.0, 0.97, 0.88]) * core[..., None]
    out[~buf.hit] = INK
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)
