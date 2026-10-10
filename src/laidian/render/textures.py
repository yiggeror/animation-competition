"""程序纹理：按材质给每个像素算反照率细节（墙上的水渍、墙裙掉漆、水泥地的裂缝、木纹、竹席……）。

纹理只决定"东西本来是什么颜色"，明暗全部来自光照计算。
"""
import math

import numpy as np

from .materials import MATS, M, albedo_table


# ---------------------------------------------------------------- 噪声（向量化）
def _hash3(ix, iy, iz, seed=0):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 1274126177) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF).astype(np.float64) / float(0xFFFFFF)


def vnoise(p, seed=0):
    """三维值噪声，p: (...,3)，返回 [0,1]。"""
    f = np.floor(p)
    t = p - f
    t = t * t * (3 - 2 * t)
    i = f.astype(np.int64)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[..., 0] if dx else 1 - t[..., 0]) * (t[..., 1] if dy else 1 - t[..., 1]) * (t[..., 2] if dz else 1 - t[..., 2])
                out = out + w * _hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out


def fbm(p, octaves=4, seed=0, lac=2.0, gain=0.5):
    a = 0.5
    s = 0.0
    n = 0.0
    q = p
    for o in range(octaves):
        s = s + a * vnoise(q, seed + o * 17)
        n += a
        a *= gain
        q = q * lac
    return s / n


def ridged(p, octaves=4, seed=0):
    s = 0.0
    a = 0.5
    n = 0.0
    q = p
    for o in range(octaves):
        v = 1 - abs(vnoise(q, seed + o * 31) * 2 - 1)
        s = s + a * v ** 4
        n += a
        a *= 0.5
        q = q * 2.03
    return s / n


# ---------------------------------------------------------------- 各材质
def albedo(buf, scene, chars=None, extra=None):
    """返回 (H,W,3) 线性反照率。"""
    H, W = buf.MAT.shape
    base = albedo_table()
    A = base[buf.MAT].copy()
    P = buf.P
    N = buf.N
    mat = buf.MAT

    def sel(name):
        return (mat == M(name)) & buf.hit

    # 墙：上半截刷白（泛黄、水渍、霉点），下半截绿漆墙裙（掉漆露出底下的白）
    m = sel("plaster")
    if m.any():
        p = P[m]
        z = p[:, 2]
        st = fbm(p * np.array([2.0, 2.0, 1.2]), 5, 3)
        col = base[M("plaster")] * (0.92 + 0.14 * (st - 0.5))[:, None]
        # 水渍：靠近屋顶的大片淡黄褐色晕
        wet = np.clip((fbm(p * 0.9, 3, 9) - 0.60) * 3, 0, 1) * np.clip((z - 2.4) / 0.8, 0, 1)
        col = col * (1 - 0.18 * wet[:, None]) + np.array([0.42, 0.33, 0.20]) * 0.18 * wet[:, None]
        # 墙根的脏
        grime = np.clip(1 - z / 0.25, 0, 1) * (0.5 + 0.5 * fbm(p * 6, 3, 4))
        col = col * (1 - 0.35 * grime[:, None])
        # 墙裙
        wain = z < 1.05
        chips = (fbm(p * 14, 4, 21) > 0.79) & (np.abs(z - 0.55) > 0.25)
        wc = base[M("wainscot")] * (0.9 + 0.2 * (fbm(p * 3, 3, 5) - 0.5))[:, None]
        col = np.where((wain & ~chips)[:, None], wc, col)
        band = (z > 1.035) & (z < 1.06)
        col = np.where(band[:, None], base[M("wainscot")] * 0.45, col)
        A[m] = col
    m = sel("concrete")
    if m.any():
        p = P[m]
        st = fbm(p * 1.5, 5, 7)
        col = base[M("concrete")] * (0.80 + 0.35 * (st - 0.5))[:, None]
        crack = ridged(p * np.array([1.3, 1.3, 1.0]), 4, 11)
        col = col * (1 - 0.45 * np.clip((crack - 0.55) * 4, 0, 1))[:, None]
        # 常走的路线磨得发亮
        worn = np.exp(-((p[:, 0] - 2.6) ** 2) / 1.2 - ((p[:, 1] - 1.8) ** 2) / 3.0)
        col = col * (1 + 0.10 * worn)[:, None]
        A[m] = col
    for nm, scale in (("wood_dark", 1.0), ("wood_raw", 1.0), ("beam", 0.8), ("door_wood", 1.0), ("column", 0.9), ("chest", 1.0)):
        m = sel(nm)
        if not m.any():
            continue
        p = P[m]
        n = N[m]
        # 木纹方向：水平面沿 x，竖直面沿 z（门板、柱子），檩条沿 x
        if nm in ("door_wood", "column"):
            q = p * np.array([12.0, 12.0, 0.8])
        elif nm == "beam":
            q = p * np.array([0.8, 14.0, 14.0])
        else:
            vert = np.abs(n[:, 2]) < 0.5
            q = np.where(vert[:, None], p * np.array([10.0, 10.0, 0.9]), p * np.array([0.9, 10.0, 10.0]))
        g = fbm(q, 3, 13)
        rings = 0.5 + 0.5 * np.sin(g * 28.0)
        col = base[M(nm)] * (0.82 + 0.22 * rings + 0.12 * (fbm(p * 4, 2, 2) - 0.5))[:, None] * scale
        if nm == "door_wood":
            plank = (np.abs(((p[:, 0] + p[:, 1]) * 6.5) % 1.0 - 0.5) > 0.47)
            col = np.where(plank[:, None], col * 0.4, col)
        A[m] = col
    m = sel("bamboo")
    if m.any():
        p = P[m]
        slat = (p[:, 0] * 66.0) % 1.0
        edge = np.minimum(slat, 1 - slat) < 0.08
        node = np.abs(((p[:, 1] + 0.37 * np.floor(p[:, 0] * 66.0)) * 3.0) % 1.0 - 0.5) > 0.47
        weave = np.abs((p[:, 1] * 12.5) % 1.0 - 0.5) > 0.46
        tone = 0.85 + 0.2 * fbm(p * np.array([60.0, 3.0, 1.0]), 2, 41)
        col = base[M("bamboo")] * tone[:, None]
        col = np.where((edge | node)[:, None], col * 0.6, col)
        col = np.where(weave[:, None], col * 0.7, col)
        # 被人躺得发亮、发深
        A[m] = col
    m = sel("sheet")
    if m.any():
        p = P[m]
        weave = 0.96 + 0.04 * np.sin(p[:, 0] * 2400) * np.sin(p[:, 2] * 2400)
        fold = np.minimum(np.abs(((p[:, 0] - 0.25) / 0.525) % 1.0 - 0.5), 1.0)
        crease = np.exp(-((((p[:, 0] - 0.25) / 0.525) % 1.0) - 0.0) ** 2 / 0.0004)
        crease2 = np.exp(-((((p[:, 2] - 0.86) / 0.405) % 1.0)) ** 2 / 0.0006)
        yel = 0.04 * fbm(p * 3, 3, 51)
        col = base[M("sheet")] * weave[:, None] * (1 - 0.05 * (crease + crease2))[:, None]
        col = col - np.array([0.0, 0.01, 0.04]) * yel[:, None] * 10
        A[m] = np.clip(col, 0, 1)
    m = sel("roof_tile")
    if m.any():
        p = P[m]
        row = np.abs((p[:, 1] * 6.0) % 1.0 - 0.5) > 0.42
        col = base[M("roof_tile")] * (0.8 + 0.3 * fbm(p * 5, 3, 61))[:, None]
        A[m] = np.where(row[:, None], col * 0.5, col)
    m = sel("blouse_nn")
    if m.any():
        # 碎花：浅蓝底上散着小白花和粉花（世界坐标里只用于静止镜头的预览；人物身上会改用身体坐标）
        p = P[m] * 95.0
        cell = np.floor(p)
        f = p - cell - 0.5
        h = _hash3(cell[:, 0].astype(np.int64), cell[:, 1].astype(np.int64), cell[:, 2].astype(np.int64), 3)
        r = np.sqrt((f ** 2).sum(-1))
        flower = (r < 0.24) & (h > 0.45)
        col = np.tile(base[M("blouse_nn")], (m.sum(), 1))
        col = np.where((flower & (h > 0.75))[:, None], np.array([0.85, 0.55, 0.6]), col)
        col = np.where((flower & (h <= 0.75))[:, None], np.array([0.88, 0.88, 0.84]), col)
        A[m] = col
    m = sel("enamel")
    if m.any():
        p = P[m]
        A[m] = base[M("enamel")] * (0.95 + 0.05 * fbm(p * 30, 2, 71))[:, None]
    # 贴图材质（画、对联、日历、照片……）
    m = sel("image")
    if m.any() and scene.atlas.shape[0] > 1:
        ids = buf.ID[m]
        texid = scene.prims[ids, 3].astype(int)
        uv = buf.UV[m]
        out = np.ones((m.sum(), 3))
        for t in np.unique(texid):
            if t < 0:
                continue
            k = texid == t
            x0, y0, w, h = scene.rects[t]
            xs = np.clip((uv[k, 0] * (w - 1)).round().astype(int), 0, int(w) - 1) + int(x0)
            ys = np.clip(((1 - uv[k, 1]) * (h - 1)).round().astype(int), 0, int(h) - 1) + int(y0)
            out[k] = scene.atlas[ys, xs, :3]
        A[m] = out
    # 皮影（从正面/背面直接看到的皮子颜色：反射贴图 = 透射贴图编号 + 1）
    if extra is not None and "puppet_mask" in extra:
        pm = extra["puppet_mask"] & buf.hit & (buf.ID >= 0)
        if pm.any():
            ids = buf.ID[pm]
            texid = scene.prims[ids, 3].astype(int) + 1
            uv = buf.UV[pm]
            out = np.ones((pm.sum(), 3))
            for t in np.unique(texid):
                k = texid == t
                x0, y0, w, h = scene.rects[t]
                xs = np.clip((uv[k, 0] * (w - 1)).round().astype(int), 0, int(w) - 1) + int(x0)
                ys = np.clip(((1 - uv[k, 1]) * (h - 1)).round().astype(int), 0, int(h) - 1) + int(y0)
                out[k] = scene.atlas[ys, xs, :3]
            A[pm] = out
    return A
