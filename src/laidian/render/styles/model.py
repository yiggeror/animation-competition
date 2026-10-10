"""设计稿用的中性画法：浅底、固有色两级明暗、轮廓线、五官和衣服的线。不代表最终画风。"""
import math

import numpy as np
from scipy import ndimage

from .. import chardecals as CD
from .. import textures as TX
from .common import downsample, edges, face_layers, linear_to_srgb, luminance, total_light

BG = np.array([0.93, 0.91, 0.86])
INK = np.array([0.06, 0.05, 0.05])


def compose(buf, scene, ctx, bg=BG, two_tone=True):
    ss = getattr(buf, "ss", 1)
    H, W = buf.MAT.shape
    E, dif = total_light(buf)
    A = TX.albedo(buf, scene, extra=ctx.get("extra"))
    Y = luminance(E) * ctx.get("exposure", 1.0)
    if two_tone:
        shade = np.where(Y > 0.35, 1.0, 0.72)
    else:
        shade = np.clip(0.55 + 0.6 * Y, 0.55, 1.1)
    out = A * shade[..., None] * 1.05
    chars = ctx.get("chars")
    faces = ctx.get("faces", [])
    fl = face_layers(buf, faces, chars, ss)
    cd = CD.layers(buf, chars, faces)
    out = out * (1 - 0.3 * fl["blush"][..., None]) + np.array([0.85, 0.40, 0.38]) * 0.3 * fl["blush"][..., None]
    out = out * (1 - fl["mouth"][..., None]) + np.array([0.45, 0.10, 0.08]) * fl["mouth"][..., None]
    for key, a in (("line", 0.6), ("ink", 1.0), ("glass", 0.9)):
        out = out * (1 - a * fl[key][..., None]) + INK * a * fl[key][..., None]
    out = out * (1 - fl["white"][..., None]) + np.array([1, 1, 1.0]) * fl["white"][..., None]
    for key, a in (("hair", 0.45), ("cloth_line", 0.8)):
        out = out * (1 - a * cd[key][..., None]) + INK * a * cd[key][..., None]
    out = out * (1 - cd["print_light"][..., None]) + np.array([0.96, 0.95, 0.9]) * cd["print_light"][..., None]
    out = out * (1 - cd["button"][..., None]) + np.array([0.96, 0.95, 0.9]) * cd["button"][..., None]
    outline, inner = edges(buf, scene, chars, mr_w=0.004 / ss)
    if ctx.get("chars_only", True):
        near = ndimage.maximum_filter((buf.CP >= 0).astype(float), size=max(3, 4 * ss))
        outline = outline * near
    ol = np.clip(ndimage.gaussian_filter(ndimage.maximum_filter(outline, size=max(1, int(1.6 * ss))), 0.4 * ss) * 1.6, 0, 1)
    out = out * (1 - ol[..., None]) + INK * ol[..., None]
    il = np.clip(ndimage.gaussian_filter(inner, 0.4 * ss), 0, 1) * 0.5
    out = out * (1 - il[..., None]) + INK * il[..., None]
    is_bg = ~(buf.CP >= 0)
    if ctx.get("chars_only", True):
        out[is_bg & (ol < 0.5)] = bg
    img = downsample(out, ss)
    return (linear_to_srgb(np.clip(img, 0, 1)) * 255).astype(np.uint8)
