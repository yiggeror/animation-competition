"""光源与直接光照（numba）。

光源都有真实的位置和大小，阴影由光线追踪算出：
  SPHERE  球形光源（马灯火苗、被熏黄的玻璃罩）  —— 软阴影的半影宽度由光源大小决定
  LINE    线光源（日光灯管）
  SPOT    聚光（手电），带光斑轮廓（亮芯 + 外圈溢光）
  DIR     平行光（月光），有角直径
  RECT    矩形面光源（被照亮的床单、电视屏幕、手机屏幕）
透光物体（皮影、纱窗、玻璃）让阴影光线变色/变暗，而不是挡死。
"""
import math

import numpy as np
from numba import njit, prange

from . import rt
from . import sdf as S

SPHERE, LINE, SPOT, DIR, RECT = 0, 1, 2, 3, 4
NL = 24  # 每个光源的参数个数


def make_light(kind, color, intensity, pos=(0, 0, 0), vec=(0, 0, 0), radius=0.0,
               cos_in=1.0, cos_out=0.0, samples=8, vec2=(0, 0, 0), spill=0.0, two_sided=0.0):
    row = np.zeros(NL)
    row[0] = kind
    row[1:4] = np.asarray(color, float) * intensity
    row[4:7] = pos
    row[7:10] = vec
    row[10] = radius
    row[11] = cos_in
    row[12] = cos_out
    row[13] = samples
    row[14:17] = vec2
    row[17] = spill
    row[18] = two_sided
    return row


# --------------------------------------------------------------- 采样序列
def _r2(n):
    """R2 低差异序列。"""
    g = 1.32471795724474602596
    a1, a2 = 1.0 / g, 1.0 / (g * g)
    i = np.arange(n) + 0.5
    return np.stack([(0.5 + a1 * i) % 1.0, (0.5 + a2 * i) % 1.0], 1)


SEQ = _r2(64)


def blue_noise(H, W, seed=7):
    """每像素的随机旋转（固定种子，静止画面不闪）。"""
    rng = np.random.default_rng(seed)
    return rng.random((H, W, 2))


# --------------------------------------------------------------- 单光源采样
@njit(cache=True, fastmath=True)
def _sample_light(L, u1, u2, px, py, pz):
    """返回光源上的采样点 (x,y,z)、该点的辐射系数 w（含光源朝向/光斑轮廓）。"""
    kind = int(L[0])
    if kind == SPHERE:
        # 在朝向接收点的圆盘上均匀采样（球形光源的投影）
        cx, cy, cz = L[4], L[5], L[6]
        r = L[10]
        wx, wy, wz = px - cx, py - cy, pz - cz
        ln = math.sqrt(wx * wx + wy * wy + wz * wz) + 1e-9
        wx /= ln
        wy /= ln
        wz /= ln
        # 正交基
        if abs(wz) < 0.9:
            ax, ay, az = -wy, wx, 0.0
        else:
            ax, ay, az = 0.0, -wz, wy
        al = math.sqrt(ax * ax + ay * ay + az * az)
        ax /= al
        ay /= al
        az /= al
        bx = wy * az - wz * ay
        by = wz * ax - wx * az
        bz = wx * ay - wy * ax
        rr = r * math.sqrt(u1)
        th = 2 * math.pi * u2
        ca = rr * math.cos(th)
        sa = rr * math.sin(th)
        return cx + ca * ax + sa * bx, cy + ca * ay + sa * by, cz + ca * az + sa * bz, 1.0
    elif kind == LINE:
        ax, ay, az = L[4], L[5], L[6]
        bx, by, bz = L[7], L[8], L[9]
        return ax + (bx - ax) * u1, ay + (by - ay) * u1, az + (bz - az) * u1, 1.0
    elif kind == SPOT:
        cx, cy, cz = L[4], L[5], L[6]
        r = L[10]
        # 光源口径内的圆盘采样（垂直于光轴）
        dx, dy, dz = L[7], L[8], L[9]
        if abs(dz) < 0.9:
            ax, ay, az = -dy, dx, 0.0
        else:
            ax, ay, az = 0.0, -dz, dy
        al = math.sqrt(ax * ax + ay * ay + az * az)
        ax /= al
        ay /= al
        az /= al
        bx = dy * az - dz * ay
        by = dz * ax - dx * az
        bz = dx * ay - dy * ax
        rr = r * math.sqrt(u1)
        th = 2 * math.pi * u2
        ca = rr * math.cos(th)
        sa = rr * math.sin(th)
        return cx + ca * ax + sa * bx, cy + ca * ay + sa * by, cz + ca * az + sa * bz, 1.0
    elif kind == RECT:
        ox, oy, oz = L[4], L[5], L[6]
        return (ox + L[7] * u1 + L[14] * u2, oy + L[8] * u1 + L[15] * u2,
                oz + L[9] * u1 + L[16] * u2, 1.0)
    return 0.0, 0.0, 0.0, 0.0


@njit(cache=True, fastmath=True)
def spot_profile(L, wx, wy, wz):
    """手电光斑：亮芯 + 一圈稍暗的溢光，边缘有一道亮环（反光杯的典型样子）。
    (wx,wy,wz) 是从光源指向接收点的单位向量。"""
    c = wx * L[7] + wy * L[8] + wz * L[9]
    cin = L[11]
    cout = L[12]
    if c <= cout:
        return 0.0
    if c >= cin:
        # 亮芯内部：中心略暗、边缘一道亮环
        t = (1.0 - c) / max(1.0 - cin, 1e-6)
        return 1.0 + 0.25 * math.exp(-((t - 0.85) ** 2) / 0.01) - 0.08 * (1 - t)
    t = (c - cout) / (cin - cout)
    spill = L[17]
    return spill * t + (1 - spill) * t ** 6


# --------------------------------------------------------------- 直接光照
@njit(parallel=True, cache=True, fastmath=True)
def direct(P, N, ID, MAT, diffuser, prims, nodes, order, atlas, rects, lights, chars, groups, bn, hit_mask):
    """逐像素、逐光源的直接辐照度 E[h, w, l, rgb]（已含阴影和透光着色）。
    diffuser[材质]=1 的表面（床单）两面受光：SIDE[h,w,l] = +1 光在法线（观察者）一侧，-1 在背面。"""
    H, W = ID.shape
    nl = lights.shape[0]
    E = np.zeros((H, W, nl, 3), dtype=np.float32)
    SIDE = np.ones((H, W, nl), dtype=np.int8)
    for j in prange(H):
        for i in range(W):
            if not hit_mask[j, i]:
                continue
            px, py, pz = P[j, i, 0], P[j, i, 1], P[j, i, 2]
            nx, ny, nz = N[j, i, 0], N[j, i, 1], N[j, i, 2]
            skip = ID[j, i]
            dif = diffuser[MAT[j, i]] > 0
            for l in range(nl):
                L = lights[l]
                kind = int(L[0])
                ns = int(L[13])
                snx, sny, snz = nx, ny, nz
                if dif:
                    # 光在哪一面：用光源中心判断（月光用方向）
                    if kind == DIR:
                        side = L[7] * nx + L[8] * ny + L[9] * nz
                    elif kind == RECT:
                        side = (L[4] + 0.5 * (L[7] + L[14]) - px) * nx + (L[5] + 0.5 * (L[8] + L[15]) - py) * ny + (L[6] + 0.5 * (L[9] + L[16]) - pz) * nz
                    else:
                        side = (L[4] - px) * nx + (L[5] - py) * ny + (L[6] - pz) * nz
                    if side < 0:
                        snx, sny, snz = -nx, -ny, -nz
                        SIDE[j, i, l] = -1
                ox = px + snx * 2e-3
                oy = py + sny * 2e-3
                oz = pz + snz * 2e-3
                accr = 0.0
                accg = 0.0
                accb = 0.0
                for s in range(ns):
                    u1 = (SEQ_[s % 64, 0] + bn[j, i, 0]) % 1.0
                    u2 = (SEQ_[s % 64, 1] + bn[j, i, 1]) % 1.0
                    if kind == DIR:
                        # 月亮：在角直径内抖动方向
                        dx, dy, dz = L[7], L[8], L[9]
                        jr = L[10] * math.sqrt(u1)
                        th = 6.2831853 * u2
                        dx += jr * math.cos(th)
                        dy += jr * math.sin(th)
                        dl = math.sqrt(dx * dx + dy * dy + dz * dz)
                        dx /= dl
                        dy /= dl
                        dz /= dl
                        cosr = snx * dx + sny * dy + snz * dz
                        if cosr <= 0:
                            continue
                        tr, tg, tb = rt.transmittance(prims, nodes, order, ox, oy, oz, dx, dy, dz, 1e6, atlas, rects, skip)
                        if tr + tg + tb > 0 and chars.shape[0] > 0:
                            v = S.shadow(chars, groups, ox, oy, oz, dx, dy, dz, 30.0, 0.02)
                            tr *= v
                            tg *= v
                            tb *= v
                        accr += tr * cosr
                        accg += tg * cosr
                        accb += tb * cosr
                        continue
                    lx, ly, lz, w = _sample_light(L, u1, u2, px, py, pz)
                    dx, dy, dz = lx - ox, ly - oy, lz - oz
                    d2 = dx * dx + dy * dy + dz * dz
                    dl = math.sqrt(d2)
                    dx /= dl
                    dy /= dl
                    dz /= dl
                    cosr = snx * dx + sny * dy + snz * dz
                    if cosr <= 0:
                        continue
                    g = cosr / max(d2, 1e-4)
                    if kind == SPOT:
                        g *= spot_profile(L, -dx, -dy, -dz)
                    elif kind == RECT:
                        # 面光源朝向
                        rnx = L[8] * L[16] - L[9] * L[15]
                        rny = L[9] * L[14] - L[7] * L[16]
                        rnz = L[7] * L[15] - L[8] * L[14]
                        rl = math.sqrt(rnx * rnx + rny * rny + rnz * rnz)
                        cl = -(rnx * dx + rny * dy + rnz * dz) / rl
                        if L[18] > 0:
                            cl = abs(cl)
                        if cl <= 0:
                            continue
                        g *= cl
                    elif kind == LINE:
                        # 灯管侧面发光为主，端部暗
                        ax_, ay_, az_ = L[7] - L[4], L[8] - L[5], L[9] - L[6]
                        al = math.sqrt(ax_ * ax_ + ay_ * ay_ + az_ * az_)
                        ca = abs(ax_ * dx + ay_ * dy + az_ * dz) / al
                        g *= math.sqrt(max(1.0 - ca * ca, 0.0))
                    if g <= 0:
                        continue
                    tr, tg, tb = rt.transmittance(prims, nodes, order, ox, oy, oz, dx, dy, dz, dl - 0.01, atlas, rects, skip)
                    if tr + tg + tb > 0 and chars.shape[0] > 0:
                        v = S.shadow(chars, groups, ox, oy, oz, dx, dy, dz, dl - 0.01, 0.02)
                        tr *= v
                        tg *= v
                        tb *= v
                    accr += tr * g
                    accg += tg * g
                    accb += tb * g
                inv = 1.0 / max(ns, 1)
                E[j, i, l, 0] = accr * inv * L[1]
                E[j, i, l, 1] = accg * inv * L[2]
                E[j, i, l, 2] = accb * inv * L[3]
    return E, SIDE


SEQ_ = SEQ.copy()


# --------------------------------------------------------------- 间接光（虚拟点光源）
def make_vpls(light, scene, n=48, seed=3, room_box=None):
    """从光源向外发射 n 条光线，在第一次命中的漫反射表面放一个虚拟点光源。
    返回 (n, 9)：位置、法线、功率 RGB。"""
    from .materials import albedo_table
    alb = albedo_table()
    rng = np.random.default_rng(seed)
    kind = int(light[0])
    out = []
    power = light[1:4]
    for k in range(n):
        if kind == DIR:
            break
        if kind == LINE:
            t = rng.random()
            o = light[4:7] + (light[7:10] - light[4:7]) * t
        elif kind == RECT:
            o = light[4:7] + light[7:10] * rng.random() + light[14:17] * rng.random()
        else:
            o = light[4:7].copy()
        # 方向：均匀球面（手电只在光锥内）
        while True:
            v = rng.normal(size=3)
            v /= np.linalg.norm(v)
            if kind == SPOT:
                if v @ light[7:10] < light[12]:
                    continue
            if kind == RECT:
                rn = np.cross(light[7:10], light[14:17])
                rn /= np.linalg.norm(rn)
                if light[18] <= 0 and v @ rn > 0:
                    continue
            break
        t, idx, nx, ny, nz, s, u = rt.trace(scene.prims, scene.nodes, scene.order, o[0], o[1], o[2], v[0], v[1], v[2], 1e6,
                                            scene.atlas, scene.rects, False)
        if idx < 0:
            continue
        p = o + v * t
        mat = int(scene.prims[idx, 1])
        a = alb[mat]
        # 立体角权重：功率 = 4π I / n （球面均匀）
        if kind == SPOT:
            solid = 2 * math.pi * (1 - light[12])
        elif kind == RECT:
            solid = 2 * math.pi
        else:
            solid = 4 * math.pi
        pw = power * a * solid / n
        if kind == SPOT:
            pw = pw * spot_profile(light, v[0], v[1], v[2])
        out.append([*p, nx, ny, nz, *pw])
    if not out:
        return np.zeros((0, 9))
    return np.array(out)


@njit(parallel=True, cache=True, fastmath=True)
def bounce(P, N, vpls, hit_mask, clamp_d2):
    H, W = hit_mask.shape
    E = np.zeros((H, W, 3), dtype=np.float32)
    for j in prange(H):
        for i in range(W):
            if not hit_mask[j, i]:
                continue
            px, py, pz = P[j, i, 0], P[j, i, 1], P[j, i, 2]
            nx, ny, nz = N[j, i, 0], N[j, i, 1], N[j, i, 2]
            r = 0.0
            g = 0.0
            b = 0.0
            for k in range(vpls.shape[0]):
                dx = vpls[k, 0] - px
                dy = vpls[k, 1] - py
                dz = vpls[k, 2] - pz
                d2 = dx * dx + dy * dy + dz * dz
                dl = math.sqrt(d2) + 1e-9
                dx /= dl
                dy /= dl
                dz /= dl
                c1 = nx * dx + ny * dy + nz * dz
                c2 = -(vpls[k, 3] * dx + vpls[k, 4] * dy + vpls[k, 5] * dz)
                if c1 <= 0 or c2 <= 0:
                    continue
                f = c1 * c2 / (math.pi * max(d2, clamp_d2))
                r += vpls[k, 6] * f
                g += vpls[k, 7] * f
                b += vpls[k, 8] * f
            E[j, i, 0] = r
            E[j, i, 1] = g
            E[j, i, 2] = b
    return E


@njit(parallel=True, cache=True, fastmath=True)
def ambient_occlusion(P, N, ID, prims, nodes, order, atlas, rects, chars, groups, hit_mask, radius, nrays, bn):
    H, W = hit_mask.shape
    A = np.ones((H, W), dtype=np.float32)
    for j in prange(H):
        for i in range(W):
            if not hit_mask[j, i]:
                continue
            px, py, pz = P[j, i, 0], P[j, i, 1], P[j, i, 2]
            nx, ny, nz = N[j, i, 0], N[j, i, 1], N[j, i, 2]
            if abs(nz) < 0.9:
                ax, ay, az = -ny, nx, 0.0
            else:
                ax, ay, az = 0.0, -nz, ny
            al = math.sqrt(ax * ax + ay * ay + az * az)
            ax /= al
            ay /= al
            az /= al
            bx = ny * az - nz * ay
            by = nz * ax - nx * az
            bz = nx * ay - ny * ax
            occ = 0.0
            for s in range(nrays):
                u1 = (SEQ_[s, 0] + bn[j, i, 0]) % 1.0
                u2 = (SEQ_[s, 1] + bn[j, i, 1]) % 1.0
                r = math.sqrt(u1)
                th = 6.2831853 * u2
                lx = r * math.cos(th)
                ly = r * math.sin(th)
                lz = math.sqrt(max(0.0, 1 - u1))
                dx = lx * ax + ly * bx + lz * nx
                dy = lx * ay + ly * by + lz * ny
                dz = lx * az + ly * bz + lz * nz
                ox = px + nx * 2e-3
                oy = py + ny * 2e-3
                oz = pz + nz * 2e-3
                t, k, a1, a2, a3, a4, a5 = rt.trace(prims, nodes, order, ox, oy, oz, dx, dy, dz, radius, atlas, rects, False)
                if k >= 0:
                    occ += 1.0 - t / radius
                elif chars.shape[0] > 0:
                    v = S.shadow(chars, groups, ox, oy, oz, dx, dy, dz, radius, 0.05)
                    occ += (1.0 - v) * 0.7
            A[j, i] = 1.0 - occ / nrays
    return A
