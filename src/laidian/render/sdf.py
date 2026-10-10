"""人物的有向距离场（SDF）：身体是一整块连续的形体。

身体由圆锥台（两端半径不同的胶囊）、椭球、圆角盒、截锥拼成，用平滑并集连在一起——
所以关节处没有缝、没有圆点；肘部、膝部弯曲时外侧是圆的、内侧自然收拢出褶。

数组格式 chars (n, 24)：
  0 类型  1 材质  2 组号  3 平滑半径 k
  ROUNDCONE: 4-6 a, 7-9 b, 10 ra, 11 rb
  ELLIPSOID: 4-6 中心, 7-9 半径, 10-18 旋转（局部->世界，按行）
  ROUNDBOX : 4-6 中心, 7-9 半尺寸, 10-18 旋转, 19 圆角
  CAPCONE  : 4-6 a, 7-9 b, 10 ra, 11 rb, 12 圆角（截锥，端面平——袖口、裤腿）
  23 层级：0 皮肤/身体；1 衣服（与身体硬接）；2 头发
groups (g, 8)：0-2 包围球心, 3 半径, 4 起始, 5 数量
"""
import math

import numpy as np
from numba import njit, prange

ROUNDCONE, ELLIPSOID, ROUNDBOX, CAPCONE = 0, 1, 2, 3
NC = 24


@njit(cache=True, fastmath=True)
def smin(a, b, k):
    if k <= 0.0:
        return min(a, b)
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k * 0.25


@njit(cache=True, fastmath=True)
def sd_roundcone(px, py, pz, ax, ay, az, bx, by, bz, r1, r2):
    # Inigo Quilez, "round cone" between two points
    bax, bay, baz = bx - ax, by - ay, bz - az
    l2 = bax * bax + bay * bay + baz * baz
    if l2 < 1e-12:
        dx, dy, dz = px - ax, py - ay, pz - az
        return math.sqrt(dx * dx + dy * dy + dz * dz) - r1
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pax, pay, paz = px - ax, py - ay, pz - az
    y = pax * bax + pay * bay + paz * baz
    z = y - l2
    xx = pax * l2 - bax * y
    xy = pay * l2 - bay * y
    xz = paz * l2 - baz * y
    x2 = xx * xx + xy * xy + xz * xz
    y2 = y * y * l2
    z2 = z * z * l2
    k = (1.0 if rr >= 0 else -1.0) * rr * rr * x2
    if (1.0 if z >= 0 else -1.0) * a2 * z2 > k:
        return math.sqrt(x2 + z2) * il2 - r2
    if (1.0 if y >= 0 else -1.0) * a2 * y2 < k:
        return math.sqrt(x2 + y2) * il2 - r1
    return (math.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1


@njit(cache=True, fastmath=True)
def sd_capcone(px, py, pz, ax, ay, az, bx, by, bz, ra, rb, rnd):
    # Inigo Quilez, capped cone between two points, 带圆角
    ra -= rnd
    rb -= rnd
    rba = rb - ra
    bax, bay, baz = bx - ax, by - ay, bz - az
    baba = bax * bax + bay * bay + baz * baz
    pax, pay, paz = px - ax, py - ay, pz - az
    papa = pax * pax + pay * pay + paz * paz
    paba = (pax * bax + pay * bay + paz * baz) / baba
    x = math.sqrt(max(papa - paba * paba * baba, 0.0))
    cax = max(0.0, x - (ra if paba < 0.5 else rb))
    cay = abs(paba - 0.5) - 0.5
    k = rba * rba + baba
    f = min(max((rba * (x - ra) + paba * baba) / k, 0.0), 1.0)
    cbx = x - ra - f * rba
    cby = paba - f
    s = -1.0 if (cbx < 0.0 and cay < 0.0) else 1.0
    d = math.sqrt(min(cax * cax + cay * cay * baba, cbx * cbx + cby * cby * baba))
    return s * d - rnd


@njit(cache=True, fastmath=True)
def _local(c, px, py, pz):
    rx, ry, rz = px - c[4], py - c[5], pz - c[6]
    lx = c[10] * rx + c[13] * ry + c[16] * rz
    ly = c[11] * rx + c[14] * ry + c[17] * rz
    lz = c[12] * rx + c[15] * ry + c[18] * rz
    return lx, ly, lz


@njit(cache=True, fastmath=True)
def sd_prim(c, px, py, pz):
    typ = int(c[0])
    if typ == ROUNDCONE:
        return sd_roundcone(px, py, pz, c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11])
    if typ == CAPCONE:
        return sd_capcone(px, py, pz, c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12])
    if typ == ELLIPSOID:
        lx, ly, lz = _local(c, px, py, pz)
        rx, ry, rz = c[7], c[8], c[9]
        k0 = math.sqrt((lx / rx) ** 2 + (ly / ry) ** 2 + (lz / rz) ** 2)
        k1 = math.sqrt((lx / (rx * rx)) ** 2 + (ly / (ry * ry)) ** 2 + (lz / (rz * rz)) ** 2)
        if k1 < 1e-12:
            return -min(rx, min(ry, rz))
        return k0 * (k0 - 1.0) / k1
    if typ == ROUNDBOX:
        lx, ly, lz = _local(c, px, py, pz)
        r = c[19]
        qx = abs(lx) - c[7] + r
        qy = abs(ly) - c[8] + r
        qz = abs(lz) - c[9] + r
        ox = max(qx, 0.0)
        oy = max(qy, 0.0)
        oz = max(qz, 0.0)
        return math.sqrt(ox * ox + oy * oy + oz * oz) + min(max(qx, max(qy, qz)), 0.0) - r
    return 1e9


@njit(cache=True, fastmath=True)
def scene_sdf(chars, groups, px, py, pz, best_bound):
    """返回 (距离, 主导图元编号)。best_bound：超过此距离的组直接用包围球距离代替。"""
    d_body = 1e9
    d_cloth = 1e9
    d_hair = 1e9
    pb = -1
    pc = -1
    ph = -1
    db_near = 1e9
    dc_near = 1e9
    dh_near = 1e9
    dfar = 1e9
    for g in range(groups.shape[0]):
        gx = px - groups[g, 0]
        gy = py - groups[g, 1]
        gz = pz - groups[g, 2]
        dg = math.sqrt(gx * gx + gy * gy + gz * gz) - groups[g, 3]
        if dg > best_bound:
            if dg < dfar:
                dfar = dg
            continue
        st = int(groups[g, 4])
        for q in range(st, st + int(groups[g, 5])):
            c = chars[q]
            d = sd_prim(c, px, py, pz)
            layer = int(c[23])
            k = c[3]
            if layer == 0:
                if d < db_near:
                    db_near = d
                    pb = q
                d_body = smin(d_body, d, k)
            elif layer == 1:
                if d < dc_near:
                    dc_near = d
                    pc = q
                d_cloth = smin(d_cloth, d, k)
            else:
                if d < dh_near:
                    dh_near = d
                    ph = q
                d_hair = smin(d_hair, d, k)
    d = d_body
    p = pb
    if d_cloth < d:
        d = d_cloth
        p = pc
    if d_hair < d:
        d = d_hair
        p = ph
    if p < 0:
        return dfar, -1
    if dfar < d:
        return dfar, -1
    return d, p


@njit(cache=True, fastmath=True)
def _ray_groups(groups, ox, oy, oz, dx, dy, dz):
    """射线与所有组包围球的进入/离开范围。"""
    tn = 1e9
    tf = -1e9
    for g in range(groups.shape[0]):
        cx = groups[g, 0] - ox
        cy = groups[g, 1] - oy
        cz = groups[g, 2] - oz
        b = cx * dx + cy * dy + cz * dz
        c = cx * cx + cy * cy + cz * cz - groups[g, 3] * groups[g, 3]
        h = b * b - c
        if h < 0:
            continue
        h = math.sqrt(h)
        t0 = b - h
        t1 = b + h
        if t1 < 0:
            continue
        tn = min(tn, max(t0, 0.0))
        tf = max(tf, t1)
    return tn, tf


@njit(cache=True, fastmath=True)
def march(chars, groups, ox, oy, oz, dx, dy, dz, tmax):
    """球面追踪。返回 (t, 图元, 沿途最小距离/t 的比值——用于画轮廓线)。"""
    tn, tf = _ray_groups(groups, ox, oy, oz, dx, dy, dz)
    if tf < 0 or tn > tmax:
        return -1.0, -1, 1e9
    t = tn
    tf = min(tf, tmax)
    minr = 1e9
    for it in range(160):
        d, p = scene_sdf(chars, groups, ox + dx * t, oy + dy * t, oz + dz * t, 0.05)
        if p >= 0 and t > 1e-3:
            r = d / t
            if r < minr:
                minr = r
        if d < 2e-4 * max(t, 0.3):
            if p >= 0:
                return t, p, minr
        t += max(d * 0.9, 1e-4)
        if t > tf:
            break
    return -1.0, -1, minr


@njit(cache=True, fastmath=True)
def normal(chars, groups, px, py, pz):
    e = 4e-4
    d1, _ = scene_sdf(chars, groups, px + e, py - e, pz - e, 1e9)
    d2, _ = scene_sdf(chars, groups, px - e, py - e, pz + e, 1e9)
    d3, _ = scene_sdf(chars, groups, px - e, py + e, pz - e, 1e9)
    d4, _ = scene_sdf(chars, groups, px + e, py + e, pz + e, 1e9)
    nx = d1 - d2 - d3 + d4
    ny = -d1 - d2 + d3 + d4
    nz = -d1 + d2 - d3 + d4
    l = math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-12
    return nx / l, ny / l, nz / l


@njit(cache=True, fastmath=True)
def shadow(chars, groups, ox, oy, oz, dx, dy, dz, tmax, w):
    """软阴影可见度（0 挡住，1 无遮挡）。w 越大半影越宽。"""
    tn, tf = _ray_groups(groups, ox, oy, oz, dx, dy, dz)
    if tf < 0 or tn > tmax:
        return 1.0
    t = max(tn, 2e-3)
    tf = min(tf, tmax)
    res = 1.0
    for it in range(96):
        d, p = scene_sdf(chars, groups, ox + dx * t, oy + dy * t, oz + dz * t, 0.1)
        if p >= 0:
            res = min(res, d / (w * t))
            if res < -1.0:
                return 0.0
        t += min(max(abs(d), 0.003), 0.15)
        if t > tf:
            break
    res = max(res, -1.0)
    return 0.25 * (1 + res) * (1 + res) * (2 - res)


@njit(parallel=True, cache=True, fastmath=True)
def primary(chars, groups, cam_o, cam_fwd, cam_right, cam_up, tan_half, W, H, Tstatic, jx, jy):
    """人物主光线：只在静态场景更近处才算命中。返回 T, 图元, 法线, 轮廓指标。"""
    T = np.full((H, W), 1e9)
    PR = np.full((H, W), -1, dtype=np.int32)
    Nn = np.zeros((H, W, 3))
    MR = np.full((H, W), 1e9, dtype=np.float32)
    aspect = W / H
    for j in prange(H):
        for i in range(W):
            px = (2.0 * (i + jx) / W - 1.0) * tan_half
            py = (1.0 - 2.0 * (j + jy) / H) * tan_half / aspect
            dx = cam_fwd[0] + px * cam_right[0] + py * cam_up[0]
            dy = cam_fwd[1] + px * cam_right[1] + py * cam_up[1]
            dz = cam_fwd[2] + px * cam_right[2] + py * cam_up[2]
            ln = math.sqrt(dx * dx + dy * dy + dz * dz)
            dx /= ln
            dy /= ln
            dz /= ln
            t, p, mr = march(chars, groups, cam_o[0], cam_o[1], cam_o[2], dx, dy, dz, Tstatic[j, i])
            MR[j, i] = mr
            if p >= 0:
                T[j, i] = t
                PR[j, i] = p
                hx = cam_o[0] + dx * t
                hy = cam_o[1] + dy * t
                hz = cam_o[2] + dz * t
                nx, ny, nz = normal(chars, groups, hx, hy, hz)
                Nn[j, i, 0] = nx
                Nn[j, i, 1] = ny
                Nn[j, i, 2] = nz
    return T, PR, Nn, MR


def empty():
    return np.zeros((0, NC)), np.zeros((0, 8))
