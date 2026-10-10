"""光线求交核心（numba）。

场景里的静态物体和大部分道具都用解析几何体表示，逐像素精确求交：
  BOX  轴对齐长方体      OBOX 绕 z 轴旋转的长方体
  CYL  任意轴向的圆柱    ELL  轴对齐椭球
  QUAD 平行四边形（可贴图、可按透明度镂空）  DISC 圆盘
人物（SDF）、皮影（透光片）另有模块，在这里统一参与可见性和阴影。
"""
import math

import numpy as np
from numba import njit, prange

BOX, OBOX, CYL, ELL, QUAD, DISC = 0, 1, 2, 3, 4, 5
NPARAM = 24
F_SHADOW = 1      # 投射阴影
F_ALPHA = 2       # 按贴图透明度镂空
F_TRANSMIT = 4    # 透光（床单、纱窗、皮影）：阴影光线乘透射率而不是挡住
F_NOVIS = 8       # 不出现在主光线里（只挡光）
F_NOSHADOWRECV = 16

EPS = 1e-4


class PrimList:
    """在 Python 侧拼装几何体，最后转成 numba 用的数组。"""

    def __init__(self):
        self.rows = []
        self.names = []

    def _add(self, typ, mat, params, flags=F_SHADOW, tex=-1, name=""):
        row = np.zeros(NPARAM)
        row[0] = typ
        row[1] = mat
        row[2] = flags
        row[3] = tex
        row[4:4 + len(params)] = params
        self.rows.append(row)
        self.names.append(name)
        return len(self.rows) - 1

    def box(self, mat, x0, x1, y0, y1, z0, z1, flags=F_SHADOW, name=""):
        return self._add(BOX, mat, [min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)], flags, name=name)

    def obox(self, mat, c, h, R=None, ang=0.0, flags=F_SHADOW, name=""):
        """c 中心，h 半尺寸，R 局部->世界的 3x3 旋转（默认绕 z 转 ang）。"""
        if R is None:
            ca, sa = math.cos(ang), math.sin(ang)
            R = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1.0]])
        R = np.asarray(R, float)
        return self._add(OBOX, mat, [c[0], c[1], c[2], h[0], h[1], h[2], *R.reshape(-1)], flags, name=name)

    def cyl(self, mat, a, b, r, flags=F_SHADOW, name=""):
        return self._add(CYL, mat, [a[0], a[1], a[2], b[0], b[1], b[2], r], flags, name=name)

    def ell(self, mat, c, r, flags=F_SHADOW, name=""):
        return self._add(ELL, mat, [c[0], c[1], c[2], r[0], r[1], r[2]], flags, name=name)

    def quad(self, mat, o, u, v, flags=F_SHADOW, tex=-1, name=""):
        return self._add(QUAD, mat, [o[0], o[1], o[2], u[0], u[1], u[2], v[0], v[1], v[2]], flags, tex, name=name)

    def disc(self, mat, c, n, r, flags=F_SHADOW, name=""):
        n = np.asarray(n, float)
        n = n / np.linalg.norm(n)
        return self._add(DISC, mat, [c[0], c[1], c[2], n[0], n[1], n[2], r], flags, name=name)

    def array(self):
        if not self.rows:
            return np.zeros((0, NPARAM))
        return np.array(self.rows)


# ------------------------------------------------------------------ 贴图图集
@njit(cache=True, fastmath=True)
def atlas_sample(atlas, rects, tex, s, t):
    """双线性采样图集中第 tex 张贴图，(s,t) ∈ [0,1]，t=0 在贴图底部。"""
    x0 = rects[tex, 0]
    y0 = rects[tex, 1]
    w = rects[tex, 2]
    h = rects[tex, 3]
    fx = min(max(s, 0.0), 1.0) * (w - 1)
    fy = (1.0 - min(max(t, 0.0), 1.0)) * (h - 1)
    ix = int(fx)
    iy = int(fy)
    ax = fx - ix
    ay = fy - iy
    ix1 = min(ix + 1, int(w) - 1)
    iy1 = min(iy + 1, int(h) - 1)
    X0 = int(x0) + ix
    X1 = int(x0) + ix1
    Y0 = int(y0) + iy
    Y1 = int(y0) + iy1
    out = np.empty(4, dtype=np.float32)
    for c in range(4):
        a = atlas[Y0, X0, c] * (1 - ax) + atlas[Y0, X1, c] * ax
        b = atlas[Y1, X0, c] * (1 - ax) + atlas[Y1, X1, c] * ax
        out[c] = a * (1 - ay) + b * ay
    return out


# ------------------------------------------------------------------ 单个几何体求交
@njit(cache=True, fastmath=True)
def isect(p, ox, oy, oz, dx, dy, dz, tmax, atlas, rects):
    """返回 (t, nx, ny, nz, s, u)；未命中时 t = -1。"""
    typ = int(p[0])
    if typ == BOX:
        inv = 1e30
        tn = -1e30
        tf = 1e30
        nax = 0
        nsg = 0.0
        for ax in range(3):
            o = ox if ax == 0 else (oy if ax == 1 else oz)
            d = dx if ax == 0 else (dy if ax == 1 else dz)
            lo = p[4 + 2 * ax]
            hi = p[5 + 2 * ax]
            if abs(d) < 1e-12:
                if o < lo or o > hi:
                    return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
                continue
            inv = 1.0 / d
            t1 = (lo - o) * inv
            t2 = (hi - o) * inv
            sg = -1.0
            if t1 > t2:
                t1, t2 = t2, t1
                sg = 1.0
            if t1 > tn:
                tn = t1
                nax = ax
                nsg = sg
            if t2 < tf:
                tf = t2
            if tn > tf:
                return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        if tn < EPS or tn > tmax:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        nx = nsg if nax == 0 else 0.0
        ny = nsg if nax == 1 else 0.0
        nz = nsg if nax == 2 else 0.0
        return tn, nx, ny, nz, 0.0, 0.0
    elif typ == OBOX:
        cx, cy, cz = p[4], p[5], p[6]
        hx, hy, hz = p[7], p[8], p[9]
        # R 按行存放在 p[10:19]；局部 = R^T (o - c)
        rx, ry, rz = ox - cx, oy - cy, oz - cz
        lox = p[10] * rx + p[13] * ry + p[16] * rz
        loy = p[11] * rx + p[14] * ry + p[17] * rz
        loz = p[12] * rx + p[15] * ry + p[18] * rz
        ldx = p[10] * dx + p[13] * dy + p[16] * dz
        ldy = p[11] * dx + p[14] * dy + p[17] * dz
        ldz = p[12] * dx + p[15] * dy + p[18] * dz
        tn = -1e30
        tf = 1e30
        nax = 0
        nsg = 0.0
        for ax in range(3):
            o = lox if ax == 0 else (loy if ax == 1 else loz)
            d = ldx if ax == 0 else (ldy if ax == 1 else ldz)
            hh = hx if ax == 0 else (hy if ax == 1 else hz)
            if abs(d) < 1e-12:
                if o < -hh or o > hh:
                    return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
                continue
            inv = 1.0 / d
            t1 = (-hh - o) * inv
            t2 = (hh - o) * inv
            sg = -1.0
            if t1 > t2:
                t1, t2 = t2, t1
                sg = 1.0
            if t1 > tn:
                tn = t1
                nax = ax
                nsg = sg
            if t2 < tf:
                tf = t2
            if tn > tf:
                return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        if tn < EPS or tn > tmax:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        # 世界法线 = R * 局部法线（局部法线只有一个分量）
        nx = p[10 + nax] * nsg
        ny = p[13 + nax] * nsg
        nz = p[16 + nax] * nsg
        # 局部坐标作为 uv（贴图用）
        hlx = lox + tn * ldx
        hly = loy + tn * ldy
        return tn, nx, ny, nz, hlx, hly
    elif typ == CYL:
        ax_, ay_, az_ = p[4], p[5], p[6]
        bx, by, bz = p[7], p[8], p[9]
        ra = p[10]
        bax, bay, baz = bx - ax_, by - ay_, bz - az_
        ocx, ocy, ocz = ox - ax_, oy - ay_, oz - az_
        baba = bax * bax + bay * bay + baz * baz
        bard = bax * dx + bay * dy + baz * dz
        baoc = bax * ocx + bay * ocy + baz * ocz
        k2 = baba - bard * bard
        k1 = baba * (ocx * dx + ocy * dy + ocz * dz) - baoc * bard
        k0 = baba * (ocx * ocx + ocy * ocy + ocz * ocz) - baoc * baoc - ra * ra * baba
        h = k1 * k1 - k2 * k0
        if h < 0.0 or abs(k2) < 1e-14:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        h = math.sqrt(h)
        t = (-k1 - h) / k2
        y = baoc + t * bard
        if y > 0.0 and y < baba and t > EPS and t < tmax:
            nx = (ocx + t * dx - bax * y / baba) / ra
            ny = (ocy + t * dy - bay * y / baba) / ra
            nz = (ocz + t * dz - baz * y / baba) / ra
            return t, nx, ny, nz, y / baba, 0.0
        # 端盖
        if y < 0.0:
            t = (0.0 - baoc) / bard if abs(bard) > 1e-14 else -1.0
        else:
            t = (baba - baoc) / bard if abs(bard) > 1e-14 else -1.0
        if t > EPS and t < tmax and abs(k1 + k2 * t) < h:
            sg = -1.0 if y < 0.0 else 1.0
            il = 1.0 / math.sqrt(baba)
            return t, sg * bax * il, sg * bay * il, sg * baz * il, (0.0 if y < 0.0 else 1.0), 1.0
        return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    elif typ == ELL:
        cx, cy, cz = p[4], p[5], p[6]
        rx, ry, rz = p[7], p[8], p[9]
        lox, loy, loz = (ox - cx) / rx, (oy - cy) / ry, (oz - cz) / rz
        ldx, ldy, ldz = dx / rx, dy / ry, dz / rz
        a = ldx * ldx + ldy * ldy + ldz * ldz
        b = lox * ldx + loy * ldy + loz * ldz
        c = lox * lox + loy * loy + loz * loz - 1.0
        h = b * b - a * c
        if h < 0.0:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        t = (-b - math.sqrt(h)) / a
        if t < EPS or t > tmax:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        hx = (lox + t * ldx) / rx
        hy = (loy + t * ldy) / ry
        hz = (loz + t * ldz) / rz
        ln = math.sqrt(hx * hx + hy * hy + hz * hz)
        return t, hx / ln, hy / ln, hz / ln, 0.0, 0.0
    elif typ == QUAD:
        o0, o1, o2 = p[4], p[5], p[6]
        u0, u1, u2 = p[7], p[8], p[9]
        v0, v1, v2 = p[10], p[11], p[12]
        nx = u1 * v2 - u2 * v1
        ny = u2 * v0 - u0 * v2
        nz = u0 * v1 - u1 * v0
        den = nx * dx + ny * dy + nz * dz
        if abs(den) < 1e-14:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        t = (nx * (o0 - ox) + ny * (o1 - oy) + nz * (o2 - oz)) / den
        if t < EPS or t > tmax:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        hx = ox + t * dx - o0
        hy = oy + t * dy - o1
        hz = oz + t * dz - o2
        # 解 h = s*u + v*w
        uu = u0 * u0 + u1 * u1 + u2 * u2
        vv = v0 * v0 + v1 * v1 + v2 * v2
        uv = u0 * v0 + u1 * v1 + u2 * v2
        hu = hx * u0 + hy * u1 + hz * u2
        hv = hx * v0 + hy * v1 + hz * v2
        det = uu * vv - uv * uv
        s = (hu * vv - hv * uv) / det
        w = (hv * uu - hu * uv) / det
        if s < 0.0 or s > 1.0 or w < 0.0 or w > 1.0:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        flags = int(p[2])
        if (flags & F_ALPHA) and p[3] >= 0:
            a = atlas_sample(atlas, rects, int(p[3]), s, w)[3]
            if a < 0.5:
                return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        nx /= ln
        ny /= ln
        nz /= ln
        if den > 0:  # 双面：法线朝向来光线一侧
            nx, ny, nz = -nx, -ny, -nz
        return t, nx, ny, nz, s, w
    elif typ == DISC:
        cx, cy, cz = p[4], p[5], p[6]
        nx, ny, nz = p[7], p[8], p[9]
        r = p[10]
        den = nx * dx + ny * dy + nz * dz
        if abs(den) < 1e-14:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        t = (nx * (cx - ox) + ny * (cy - oy) + nz * (cz - oz)) / den
        if t < EPS or t > tmax:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        hx = ox + t * dx - cx
        hy = oy + t * dy - cy
        hz = oz + t * dz - cz
        if hx * hx + hy * hy + hz * hz > r * r:
            return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0
        if den > 0:
            nx, ny, nz = -nx, -ny, -nz
        return t, nx, ny, nz, math.sqrt(hx * hx + hy * hy + hz * hz) / r, 0.0
    return -1.0, 0.0, 0.0, 0.0, 0.0, 0.0


# ------------------------------------------------------------------ BVH
def prim_aabb(row):
    typ = int(row[0])
    p = row
    if typ == BOX:
        return np.array([p[4], p[6], p[8]]), np.array([p[5], p[7], p[9]])
    if typ == OBOX:
        c = p[4:7]
        h = p[7:10]
        R = p[10:19].reshape(3, 3)
        ext = np.abs(R) @ h
        return c - ext, c + ext
    if typ == CYL:
        a, b, r = p[4:7], p[7:10], p[10]
        return np.minimum(a, b) - r, np.maximum(a, b) + r
    if typ == ELL:
        return p[4:7] - p[7:10], p[4:7] + p[7:10]
    if typ == QUAD:
        o, u, v = p[4:7], p[7:10], p[10:13]
        pts = np.array([o, o + u, o + v, o + u + v])
        return pts.min(0) - 1e-4, pts.max(0) + 1e-4
    if typ == DISC:
        return p[4:7] - p[10] - 1e-4, p[4:7] + p[10] + 1e-4
    raise ValueError(typ)


def build_bvh(prims, leaf=3):
    """返回 (nodes, order)。nodes: (N, 8) = [minx,miny,minz,maxx,maxy,maxz, a, b]
    内部节点 a=左孩子, b=右孩子（b>=0）；叶子 a=起始, b=-(数量)。"""
    n = prims.shape[0]
    if n == 0:
        return np.zeros((1, 8)), np.zeros(0, dtype=np.int32)
    lo = np.zeros((n, 3))
    hi = np.zeros((n, 3))
    for k in range(n):
        lo[k], hi[k] = prim_aabb(prims[k])
    cen = (lo + hi) / 2
    nodes = []
    order = []

    def rec(idx):
        me = len(nodes)
        nodes.append(None)
        bl, bh = lo[idx].min(0), hi[idx].max(0)
        if len(idx) <= leaf:
            start = len(order)
            order.extend(idx.tolist())
            nodes[me] = [*bl, *bh, start, -len(idx)]
            return me
        c = cen[idx]
        ax = int(np.argmax(c.max(0) - c.min(0)))
        srt = idx[np.argsort(c[:, ax])]
        mid = len(srt) // 2
        l = rec(srt[:mid])
        r = rec(srt[mid:])
        nodes[me] = [*bl, *bh, l, r]
        return me

    rec(np.arange(n))
    return np.array(nodes, dtype=np.float64), np.array(order, dtype=np.int32)


@njit(cache=True, fastmath=True)
def _aabb_hit(nd, ox, oy, oz, idx, idy, idz, tmax):
    t1 = (nd[0] - ox) * idx
    t2 = (nd[3] - ox) * idx
    tn = min(t1, t2)
    tf = max(t1, t2)
    t1 = (nd[1] - oy) * idy
    t2 = (nd[4] - oy) * idy
    tn = max(tn, min(t1, t2))
    tf = min(tf, max(t1, t2))
    t1 = (nd[2] - oz) * idz
    t2 = (nd[5] - oz) * idz
    tn = max(tn, min(t1, t2))
    tf = min(tf, max(t1, t2))
    return tf >= max(tn, 0.0) and tn < tmax


@njit(cache=True, fastmath=True)
def trace(prims, nodes, order, ox, oy, oz, dx, dy, dz, tmax, atlas, rects, need_vis):
    """最近交点（BVH）。返回 (t, idx, nx, ny, nz, s, u)。"""
    best = tmax
    bi = -1
    bnx = bny = bnz = 0.0
    bs = bu = 0.0
    if order.shape[0] == 0:
        return best, bi, bnx, bny, bnz, bs, bu
    idx = 1.0 / dx if abs(dx) > 1e-12 else 1e12
    idy = 1.0 / dy if abs(dy) > 1e-12 else 1e12
    idz = 1.0 / dz if abs(dz) > 1e-12 else 1e12
    stack = np.empty(64, dtype=np.int64)
    sp = 0
    stack[sp] = 0
    sp += 1
    while sp > 0:
        sp -= 1
        ni = stack[sp]
        nd = nodes[ni]
        if not _aabb_hit(nd, ox, oy, oz, idx, idy, idz, best):
            continue
        a = int(nd[6])
        b = int(nd[7])
        if b < 0:
            for q in range(a, a - b):
                k = order[q]
                fl = int(prims[k, 2])
                if need_vis and (fl & F_NOVIS):
                    continue
                t, nx, ny, nz, s, u = isect(prims[k], ox, oy, oz, dx, dy, dz, best, atlas, rects)
                if t > 0.0 and t < best:
                    best = t
                    bi = k
                    bnx, bny, bnz = nx, ny, nz
                    bs, bu = s, u
        else:
            stack[sp] = a
            sp += 1
            stack[sp] = b
            sp += 1
    return best, bi, bnx, bny, bnz, bs, bu


@njit(cache=True, fastmath=True)
def transmittance(prims, nodes, order, ox, oy, oz, dx, dy, dz, tmax, atlas, rects, skip):
    """阴影光线：返回 RGB 透射率（0 = 完全挡住）。透光物体乘贴图颜色或统一透射率 p[20]。"""
    tr = 1.0
    tg = 1.0
    tb = 1.0
    if order.shape[0] == 0:
        return tr, tg, tb
    idx = 1.0 / dx if abs(dx) > 1e-12 else 1e12
    idy = 1.0 / dy if abs(dy) > 1e-12 else 1e12
    idz = 1.0 / dz if abs(dz) > 1e-12 else 1e12
    stack = np.empty(64, dtype=np.int64)
    sp = 0
    stack[sp] = 0
    sp += 1
    while sp > 0:
        sp -= 1
        ni = stack[sp]
        nd = nodes[ni]
        if not _aabb_hit(nd, ox, oy, oz, idx, idy, idz, tmax):
            continue
        a = int(nd[6])
        b = int(nd[7])
        if b < 0:
            for q in range(a, a - b):
                k = order[q]
                if k == skip:
                    continue
                fl = int(prims[k, 2])
                if not (fl & F_SHADOW):
                    continue
                t, nx, ny, nz, s, u = isect(prims[k], ox, oy, oz, dx, dy, dz, tmax, atlas, rects)
                if t > 0.0:
                    if fl & F_TRANSMIT:
                        tex = int(prims[k, 3])
                        if tex >= 0:
                            c = atlas_sample(atlas, rects, tex, s, u)
                            tr *= c[0]
                            tg *= c[1]
                            tb *= c[2]
                        else:
                            f = prims[k, 20]
                            tr *= f
                            tg *= f
                            tb *= f
                        if tr + tg + tb < 1e-4:
                            return 0.0, 0.0, 0.0
                    else:
                        return 0.0, 0.0, 0.0
        else:
            stack[sp] = a
            sp += 1
            stack[sp] = b
            sp += 1
    return tr, tg, tb


class Scene:
    """静态几何 + BVH + 贴图图集。"""

    def __init__(self, primlist, atlas=None, rects=None):
        self.prims = primlist.array()
        self.names = list(primlist.names)
        self.nodes, self.order = build_bvh(self.prims)
        self.atlas = atlas if atlas is not None else np.zeros((1, 1, 4), np.float32)
        self.rects = rects if rects is not None else np.zeros((1, 4), np.float64)


@njit(parallel=True, cache=True, fastmath=True)
def primary(prims, nodes, order, cam_o, cam_fwd, cam_right, cam_up, tan_half, W, H, atlas, rects, jx, jy):
    """主光线（每像素一条，(jx,jy) 是像素内抖动，用于多次采样抗锯齿）。"""
    T = np.full((H, W), 1e9)
    ID = np.full((H, W), -1, dtype=np.int32)
    N = np.zeros((H, W, 3))
    UV = np.zeros((H, W, 2))
    P = np.zeros((H, W, 3))
    D = np.zeros((H, W, 3))
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
            D[j, i, 0] = dx
            D[j, i, 1] = dy
            D[j, i, 2] = dz
            t, k, nx, ny, nz, s, u = trace(prims, nodes, order, cam_o[0], cam_o[1], cam_o[2], dx, dy, dz, 1e8, atlas, rects, True)
            if k >= 0:
                T[j, i] = t
                ID[j, i] = k
                N[j, i, 0] = nx
                N[j, i, 1] = ny
                N[j, i, 2] = nz
                UV[j, i, 0] = s
                UV[j, i, 1] = u
                P[j, i, 0] = cam_o[0] + t * dx
                P[j, i, 1] = cam_o[1] + t * dy
                P[j, i, 2] = cam_o[2] + t * dz
    return T, ID, N, UV, P, D
