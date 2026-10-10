"""小型矢量绘图：样条曲线、闭合轮廓、描边，画成高分辨率蒙版（抗锯齿）。

皮影的雕花、人物脸部的五官贴花、道具贴图都用它画。
坐标用毫米（或任意单位），由 Canvas 负责换算成像素。
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def catmull(points, closed=True, n=16):
    """Catmull-Rom 样条：过所有控制点的平滑曲线。"""
    P = np.asarray(points, float)
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed or i > 0 else P[0]
        p1 = P[i]
        p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed or i + 2 < m else P[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append(q)
    if not closed:
        out.append(P[-1])
    return np.array(out)


def bezier(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def offset_polyline(pts, width_fn):
    """把折线按宽度函数扩成一个闭合多边形（变宽笔触）。width_fn(t∈[0,1]) -> 半宽。"""
    P = np.asarray(pts, float)
    n = len(P)
    seg = np.diff(P, axis=0)
    tang = np.zeros_like(P)
    tang[1:-1] = seg[1:] + seg[:-1]
    tang[0] = seg[0]
    tang[-1] = seg[-1]
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-12
    nor = np.stack([-tang[:, 1], tang[:, 0]], 1)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(seg, axis=1))])
    t = L / max(L[-1], 1e-9)
    w = np.array([width_fn(x) for x in t])[:, None]
    left = P + nor * w
    right = P - nor * w
    return np.concatenate([left, right[::-1]])


class Canvas:
    """单通道蒙版画布。坐标 (x 向右, y 向上)，单位 mm；ppmm = 每毫米像素数；ss = 超采样倍数。"""

    def __init__(self, x0, y0, x1, y1, ppmm=6.0, ss=2):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.ppmm = ppmm
        self.ss = ss
        self.W = int(math.ceil((x1 - x0) * ppmm))
        self.H = int(math.ceil((y1 - y0) * ppmm))
        self.img = Image.new("L", (self.W * ss, self.H * ss), 0)
        self.d = ImageDraw.Draw(self.img)

    def px(self, pts):
        P = np.asarray(pts, float)
        s = self.ppmm * self.ss
        return [((x - self.x0) * s, (self.y1 - y) * s) for x, y in P]

    def poly(self, pts, v=255):
        self.d.polygon(self.px(pts), fill=v)
        return self

    def line(self, pts, w, v=255):
        """折线描边（w 为毫米线宽），端点圆头。"""
        P = self.px(pts)
        wp = max(1, int(round(w * self.ppmm * self.ss)))
        self.d.line(P, fill=v, width=wp, joint="curve")
        r = wp / 2
        for (x, y) in (P[0], P[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=v)
        return self

    def circle(self, c, r, v=255):
        s = self.ppmm * self.ss
        x, y = (c[0] - self.x0) * s, (self.y1 - c[1]) * s
        rr = r * s
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=v)
        return self

    def ellipse(self, c, rx, ry, rot=0.0, v=255, n=48):
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        ca, sa = math.cos(rot), math.sin(rot)
        x = rx * np.cos(a)
        y = ry * np.sin(a)
        pts = np.stack([c[0] + ca * x - sa * y, c[1] + sa * x + ca * y], 1)
        return self.poly(pts, v)

    def array(self, blur=0.0):
        im = self.img
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur * self.ss))
        im = im.resize((self.W, self.H), Image.LANCZOS)
        return np.asarray(im, np.float32) / 255.0

    def blank(self):
        return Canvas(self.x0, self.y0, self.x1, self.y1, self.ppmm, self.ss)
