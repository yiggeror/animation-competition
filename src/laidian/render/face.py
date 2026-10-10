"""五官贴花：眼睛、眉毛、嘴、皱纹、眼镜，画在头部曲面上（跟着头转、自然透视缩短）。

表情参数（expr）：
  eye_open 0–1.2  blink 0–1  eye_smile 0–1（眯成月牙）  look (左右, 上下)
  brow 抬眉 -1–1  brow_tilt 皱眉/发愁 -1–1（正 = 眉头上扬发愁）
  mouth_smile -1–1  mouth_open 0–1  mouth_w 0.6–1.4  puff 鼓腮 0–1  squint 0–1
"""
import math

import numpy as np

R_FACE = 0.088   # 把方位角换成弧长用的半径


def _seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    t = np.clip((wx * vx + wy * vy) / (vx * vx + vy * vy + 1e-12), 0, 1)
    dx, dy = wx - t * vx, wy - t * vy
    return np.sqrt(dx * dx + dy * dy)


def _poly(px, py, pts):
    d = np.full(px.shape, 1e9)
    for (a, b) in zip(pts[:-1], pts[1:]):
        d = np.minimum(d, _seg(px, py, a[0], a[1], b[0], b[1]))
    return d


def _ell(px, py, cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    x = (px - cx) * c + (py - cy) * s
    y = -(px - cx) * s + (py - cy) * c
    k = np.sqrt((x / rx) ** 2 + (y / ry) ** 2)
    return (k - 1) * min(rx, ry)


def _quad(a, b, c, n=12):
    t = np.linspace(0, 1, n)[:, None]
    a, b, c = (np.asarray(v, float) for v in (a, b, c))
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c


def _cov(d, aa):
    """距离 → 覆盖率（抗锯齿）。aa = 一个像素对应的米数。"""
    return np.clip(0.5 - d / aa, 0, 1)


def decals(P, mask, head_c, head_R, who, expr, aa, brows_only=False):
    """返回 dict(ink, white, mouth, blush, glass)：每个是 (n,) 覆盖率，只对 mask 内的像素。"""
    p = P[mask] - head_c
    q = p @ head_R           # 头部局部坐标
    front = q[:, 1] > 0
    u = np.arctan2(q[:, 0], q[:, 1]) * R_FACE
    v = q[:, 2]
    n = len(u)
    out = {k: np.zeros(n) for k in ("ink", "white", "mouth", "blush", "glass", "line")}
    e = dict(eye_open=1.0, blink=0.0, eye_smile=0.0, look=(0.0, 0.0), brow=0.0, brow_tilt=0.0,
             mouth_smile=0.2, mouth_open=0.0, mouth_w=1.0, puff=0.0, squint=0.0)
    e.update(expr or {})
    lw = aa * 1.0
    xm = who == "xiaoman"
    ex, ey = (0.033, 0.004) if xm else (0.031, 0.010)
    open_ = max(0.0, e["eye_open"] * (1 - e["blink"]) * (1 - 0.6 * e["squint"]))
    smile = e["eye_smile"]
    lx, ly = e["look"]
    for sg in (1, -1):
        cx = sg * ex
        cy = ey
        if brows_only:
            pass
        elif xm:
            # 孩子的眼睛：大而黑的眼珠 + 高光 + 上眼睑粗线
            rx, ry = 0.0122, 0.0158 * max(open_, 0.0)
            if open_ > 0.08 and smile < 0.6:
                d_iris = _ell(u, v, cx + lx * 0.004, cy + ly * 0.003, rx * 0.88, max(ry * 0.92, 1e-4))
                # 被上眼睑盖住的部分
                lid = v - (cy + ry * 0.75)
                d_iris = np.maximum(d_iris, lid)
                out["ink"] = np.maximum(out["ink"], _cov(d_iris, aa))
                hl = _ell(u, v, cx + lx * 0.004 - 0.0035, cy + ly * 0.003 + 0.0045 * open_, 0.0031, 0.0036)
                out["white"] = np.maximum(out["white"], _cov(hl, aa) * (u * sg > -1))
            # 上眼睑：一道弧线（眯眼/笑时变成向上弯的月牙）
            k = smile
            top = cy + (0.012 * open_) * (1 - k) + 0.004 * k
            arc = _quad((cx - sg * 0.014, cy + 0.003 - 0.004 * k), (cx, top + 0.007 * (1 - k) + 0.006 * k), (cx + sg * 0.014, cy + 0.006 - 0.002 * k))
            out["ink"] = np.maximum(out["ink"], _cov(_poly(u, v, arc) - 0.0019, aa))
        else:
            # 奶奶：眼睛细长，笑起来是月牙；眼尾的笑纹；眼袋一道细线
            k = max(smile, 0.35)
            arc = _quad((cx - sg * 0.012, cy - 0.001), (cx, cy + 0.006 * open_ * (1 - k) + 0.005 * k), (cx + sg * 0.012, cy + 0.001))
            out["ink"] = np.maximum(out["ink"], _cov(_poly(u, v, arc) - 0.0014, aa))
            if open_ > 0.3 and smile < 0.7:
                d_iris = _ell(u, v, cx + lx * 0.003, cy - 0.0005 + ly * 0.002, 0.0055, 0.0050 * open_)
                d_iris = np.maximum(d_iris, v - (cy + 0.004))
                out["ink"] = np.maximum(out["ink"], _cov(d_iris, aa))
                hl = _ell(u, v, cx + lx * 0.003 - 0.0018, cy + 0.0015, 0.0013, 0.0013)
                out["white"] = np.maximum(out["white"], _cov(hl, aa))
            for t in range(3):
                a = (-0.5 + t * 0.5)
                p0 = (cx + sg * 0.015, cy + 0.001 + a * 0.004)
                p1 = (cx + sg * 0.022, cy + 0.002 + a * 0.008)
                out["line"] = np.maximum(out["line"], _cov(_seg(u, v, *p0, *p1) - 0.0005, aa) * 0.8)
            bag = _quad((cx - sg * 0.009, cy - 0.007), (cx, cy - 0.010), (cx + sg * 0.010, cy - 0.006))
            out["line"] = np.maximum(out["line"], _cov(_poly(u, v, bag) - 0.0004, aa) * 0.6)
            # 老花镜：细圆框
            gl = np.abs(_ell(u, v, cx, cy - 0.001, 0.0175, 0.0145)) - 0.0008
            out["glass"] = np.maximum(out["glass"], _cov(gl, aa))
        # 眉毛
        b_raise = e["brow"] * 0.006
        tilt = e["brow_tilt"] * 0.004
        by = cy + (0.026 if xm else 0.028) + b_raise
        inner = (cx - sg * 0.010, by + tilt - (0.0 if xm else 0.001))
        outer = (cx + sg * 0.013, by - tilt * 0.5 - 0.002)
        midp = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 + 0.002)
        brow = _quad(inner, midp, outer)
        w0 = 0.0028 if xm else 0.0016
        db = _poly(u, v, brow) - w0
        out["ink"] = np.maximum(out["ink"], _cov(db, aa) * (1.0 if xm else 0.75))
        if brows_only:
            continue
        # 腮红
        out["blush"] = np.maximum(out["blush"], np.clip(1 - ((u - sg * 0.042) ** 2 / 0.00022 + (v + 0.022) ** 2 / 0.00008), 0, 1))
    if brows_only:
        for k_ in out:
            out[k_] = out[k_] * front
        return out
    if not xm:
        # 眼镜鼻梁、法令纹、额头纹
        out["glass"] = np.maximum(out["glass"], _cov(_poly(u, v, _quad((-0.0135, 0.010), (0, 0.013), (0.0135, 0.010))) - 0.0007, aa))
        for sg in (1, -1):
            nl = _quad((sg * 0.016, -0.022), (sg * 0.024, -0.040), (sg * 0.022, -0.058))
            out["line"] = np.maximum(out["line"], _cov(_poly(u, v, nl) - 0.0006, aa) * 0.7)
        for k in range(2):
            fh = _quad((-0.022, 0.052 + k * 0.009), (0, 0.055 + k * 0.009), (0.022, 0.052 + k * 0.009))
            out["line"] = np.maximum(out["line"], _cov(_poly(u, v, fh) - 0.0004, aa) * 0.4)
    # 嘴
    mw = (0.019 if xm else 0.014) * e["mouth_w"] * (0.55 if e["puff"] > 0.3 else 1.0)
    my = -0.046 if xm else -0.050
    sm = e["mouth_smile"] * (0.008 if xm else 0.006)
    op = e["mouth_open"]
    if op > 0.05:
        top = _quad((-mw, my + sm), (0, my + 0.002), (mw, my + sm))
        bot_c = (0, my - 0.004 - (0.020 if xm else 0.014) * op)
        bot = _quad((mw, my + sm), bot_c, (-mw, my + sm))
        pts = np.concatenate([top, bot])
        d = _poly(u, v, np.concatenate([pts, pts[:1]]))
        inside = (v < my + 0.002) & (v > bot_c[1]) & (np.abs(u) < mw)
        dd = np.where(inside, -d, d)
        out["mouth"] = np.maximum(out["mouth"], _cov(dd, aa))
        out["ink"] = np.maximum(out["ink"], _cov(np.abs(dd) - 0.0009, aa))
    else:
        curve = _quad((-mw, my + sm), (0, my - sm * 0.8), (mw, my + sm))
        out["ink"] = np.maximum(out["ink"], _cov(_poly(u, v, curve) - (0.0013 if xm else 0.0011), aa))
    for k_ in out:
        out[k_] = out[k_] * front
    return out
