"""画风 A「灯影」：用皮影的镂空纹样做明暗。

- 亮处：平涂的"染色牛皮"颜色（固有色 × 光色，饱和、两级色阶）。
- 暗处：整片沉成深棕的剪影，不画细节——像没被灯照到的皮影。
- 亮暗之间：用皮影刀法的纹样（圆点、鱼鳞、卷草、方胜）刻出过渡——光越强，刻掉的越多。
  纹样贴在物体表面（墙、木头、地面），人物身上用画面坐标的细点（避免关节处出现纹样接缝）。
- 轮廓：亮处有深棕的刀刻边；暗处与剪影融成一片。
- 床单上的戏保留物理计算的透光颜色——画面里最亮、最纯的东西。
- 日光灯一亮，所有地方都落在"亮"的那一档：纹样和剪影全部消失，画面变平——这就是"惨白、平"。
"""
import math

import numpy as np
from scipy import ndimage

from .. import chardecals as CD
from .. import textures as TX
from ..materials import M
from .common import (screens, downsample, edges, face_layers, filmic, flame_shape, glow, linear_to_srgb, luminance,
                     project, total_light, world_noise)

DARK = np.array([0.030, 0.016, 0.010])
INK = np.array([0.028, 0.015, 0.010])


def plane_uv(P, N):
    """按主法线方向取平面坐标（墙、地、家具都能贴上纹样）。"""
    ax = np.argmax(np.abs(N), axis=-1)
    u = np.where(ax == 0, P[..., 1], P[..., 0])
    v = np.where(ax == 2, P[..., 1], P[..., 2])
    return u, v


def motif(name, u, v, cell):
    """返回阈值场 M ∈ [0,1]：光的强度（归一化）超过 M 的地方被"刻亮"。"""
    x = u / cell
    y = v / cell
    if name == "dots":
        fx = x - np.floor(x) - 0.5
        fy = y - np.floor(y) - 0.5
        return np.clip(np.sqrt(fx * fx + fy * fy) / 0.7071, 0, 1)
    if name == "diamond":
        fx = np.abs(x - np.floor(x) - 0.5)
        fy = np.abs(y - np.floor(y) - 0.5)
        return np.clip((fx + fy), 0, 1)
    if name == "scale":
        row = np.floor(y)
        xx = x + 0.5 * (row % 2)
        fx = xx - np.floor(xx) - 0.5
        fy = y - row
        d = np.sqrt(fx * fx + (fy * 1.3) ** 2)
        return np.clip(d / 0.75, 0, 1)
    if name == "wave":
        w = np.sin(x * 2 * math.pi) * 0.18
        f = np.abs(((y + w) % 1.0) - 0.5) * 2
        return np.clip(f, 0, 1)
    if name == "lines":
        return np.clip(np.abs((y % 1.0) - 0.5) * 2, 0, 1)
    if name == "crescent":
        row = np.floor(y)
        xx = x + 0.5 * (row % 2)
        fx = xx - np.floor(xx) - 0.5
        fy = y - row - 0.5
        d1 = np.sqrt(fx * fx + fy * fy)
        d2 = np.sqrt((fx - 0.12) ** 2 + (fy + 0.10) ** 2)
        return np.clip(np.maximum(d1 / 0.62, 1 - d2 / 0.40), 0, 1)
    return np.full_like(x, 0.5)


MOTIF = {
    "plaster": ("crescent", 0.024), "concrete": ("diamond", 0.045), "wood_dark": ("wave", 0.016), "wood_raw": ("wave", 0.014),
    "beam": ("wave", 0.02), "column": ("wave", 0.016), "door_wood": ("lines", 0.012), "chest": ("wave", 0.016),
    "bamboo": ("lines", 0.010), "roof_tile": ("scale", 0.05), "tv_body": ("dots", 0.010), "enamel": ("dots", 0.008),
    "cloth_towel": ("scale", 0.012), "cloth_blouse": ("scale", 0.012), "cloth_tshirt": ("scale", 0.012),
    "paper": ("dots", 0.008), "paper_red": ("dots", 0.008), "stone": ("diamond", 0.02), "metal": ("dots", 0.006),
}


def compose(buf, scene, ctx):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    x = A * E / math.pi * ctx.get("exposure", 1.0)
    Y = luminance(x)
    # 光的强弱（归一化 0–1）和光色
    Lv = np.clip(filmic(Y * 1.6) / 0.85, 0, 1)
    Ec = E / np.maximum(luminance(E), 1e-6)[..., None]
    Ec = Ec / np.maximum(Ec.max(-1, keepdims=True), 1e-6)
    # 纹样阈值场
    u, v = plane_uv(buf.P, buf.N)
    Mf = np.full((H, W), 0.5)
    for name, (mo, cell) in MOTIF.items():
        m = buf.MAT == M(name)
        if m.any():
            Mf[m] = motif(mo, u[m], v[m], cell)
    # 墙裙用方胜
    wain = (buf.MAT == M("plaster")) & (buf.P[..., 2] < 1.05)
    Mf[wain] = motif("scale", u[wain], v[wain], 0.028)
    # 人物：画面坐标的细点（不随肢体游动，也不会在关节处出现接缝）
    isch = buf.CP >= 0
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    cellpx = 5.0 * ss
    rot = 0.42
    su = (xx * math.cos(rot) - yy * math.sin(rot)) / cellpx
    sv = (xx * math.sin(rot) + yy * math.cos(rot)) / cellpx
    Mf[isch] = motif("dots", su[isch] * 0.02, sv[isch] * 0.02, 0.02)[...]
    # 过渡带
    t0, t1 = 0.10, 0.40
    level = np.clip((Lv - t0) / (t1 - t0), 0, 1)
    aa = 0.10
    lit = np.clip((level - Mf) / aa + 0.5, 0, 1)
    lit = np.where(level >= 0.999, 1.0, lit)
    lit = np.where(level <= 0.001, 0.0, lit)
    # 亮处的颜色：固有色 × 光色，两级色阶
    sat_a = A / np.maximum(A.max(-1, keepdims=True), 1e-6)
    gray = A.mean(-1, keepdims=True)
    dyed = np.clip(gray + (A - gray) * 1.35, 0, 1)
    tone = np.where(Lv > 0.72, 1.0, 0.78)[..., None]
    c_lit = dyed * (0.45 + 0.55 * Ec) * tone * 1.15
    # 暗处：深棕，带一点光色
    c_dark = DARK + 0.035 * Ec * level[..., None]
    out = c_dark * (1 - lit[..., None]) + c_lit * lit[..., None]
    # 皮面纹理：亮处一点点斑驳
    hide = TX.fbm(buf.P * 7.0, 3, 77)
    out = out * (0.92 + 0.14 * hide[..., None] * lit[..., None])
    # 床单：物理透光
    sheet = dif & buf.hit
    xs = filmic(x[sheet] * 1.05)
    out[sheet] = xs * 1.10
    # 人物的线与五官
    chars = ctx.get("chars")
    faces = ctx.get("faces", [])
    fl = face_layers(buf, faces, chars, ss)
    cd = CD.layers(buf, chars, faces)
    litc = np.clip(lit, 0.25, 1)[..., None]
    out = out * (1 - cd["print_light"][..., None]) + np.array([0.95, 0.92, 0.82]) * litc * cd["print_light"][..., None]
    out = out * (1 - fl["blush"][..., None] * 0.35) + np.array([0.75, 0.25, 0.20]) * 0.35 * fl["blush"][..., None] * litc
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.30, 0.06, 0.04]) * fl["mouth"][..., None] * litc
    for key, a in (("line", 0.6), ("ink", 1.0), ("glass", 0.9)):
        out = out * (1 - a * fl[key][..., None]) + INK * a * fl[key][..., None]
    for key, a in (("hair", 0.55), ("cloth_line", 0.85)):
        out = out * (1 - a * cd[key][..., None] * lit[..., None]) + INK * a * cd[key][..., None] * lit[..., None]
    out = out * (1 - cd["button"][..., None]) + np.array([0.92, 0.9, 0.85]) * litc * cd["button"][..., None]
    out = out * (1 - fl["white"][..., None]) + np.array([1.0, 0.96, 0.88]) * litc * fl["white"][..., None]
    out = out + screens(buf, ctx)
    # 刀刻轮廓：亮处清楚，暗处融进剪影
    outline, inner = edges(buf, scene, chars, mr_w=0.0050 / ss)
    k = max(1, int(round(2.2 * ss)))
    ol = ndimage.maximum_filter(outline, size=k)
    ol = ndimage.gaussian_filter(ol, 0.35 * ss)
    il = ndimage.gaussian_filter(inner, 0.35 * ss) * 0.6
    out = out * (1 - ol[..., None]) + INK * ol[..., None]
    out = out * (1 - (il * lit)[..., None]) + INK * (il * lit)[..., None]
    out = add_sources(out, buf, ctx)
    out[~buf.hit] = ctx.get("sky", DARK)
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)


def add_sources(out, buf, ctx):
    H, W = buf.MAT.shape
    cam = ctx["cam"]
    t = ctx.get("t", 0.0)
    for src in ctx.get("sources", []):
        if src["kind"] != "lamp":
            continue
        q = project(cam, src["pos"], W, H)
        if q[2] <= 0:
            continue
        xi, yi = int(q[0]), int(q[1])
        visible = 0 <= xi < W and 0 <= yi < H and buf.T[yi, xi] > q[2] - 0.05
        if not visible:
            continue
        ppm = W / (2 * cam.tan_half * q[2])
        g = glow((H, W), q[:2], 0.06 * ppm, 1.8) * src.get("intensity", 1.0)
        rings = np.floor(np.clip(g, 0, 0.999) * 6) / 6
        out = out + np.array([1.0, 0.55, 0.18]) * (rings * 0.30)[..., None]
        core, outer = flame_shape((H, W), (q[0], q[1] + 0.006 * ppm), 0.030 * ppm, 0.009 * ppm, t)
        out = out * (1 - outer[..., None]) + np.array([1.0, 0.62, 0.22]) * 1.5 * outer[..., None]
        out = out * (1 - core[..., None]) + np.array([1.0, 0.94, 0.75]) * 1.7 * core[..., None]
    return out
