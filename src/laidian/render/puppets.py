"""皮影：鹤与乌龟（湖南皮影风格，造型原创）。

每个部件是一片刮薄的牛皮：
  - 透射贴图 RGBA：RGB = 光穿过这片皮之后剩下的颜色比例（镂空处 = 1），A = 有皮的地方
  - 反射贴图 RGBA：从正面打光看到的皮面颜色
部件之间用枢钉连接（铆点画在贴图上），签子垂直于皮影平面（湖南"平端"）。
影子不是画出来的：渲染时从床单上每个点向马灯/手电发射光线，穿过这些贴图算出来。
"""
import math
from dataclasses import dataclass, field

import numpy as np

from .vecdraw import Canvas, catmull, offset_polyline, bezier

# ---------------------------------------------------------------- 颜色（透射比例，线性）
LEATHER_T = np.array([0.90, 0.66, 0.40]) * 0.62   # 刮薄的牛皮本色：透出暖琥珀色
LEATHER_R = np.array([0.52, 0.36, 0.19])          # 正面看牛皮
DYE = {
    "none": np.array([1.0, 1.0, 1.0]),
    "red": np.array([0.95, 0.14, 0.07]),
    "vermilion": np.array([1.0, 0.30, 0.08]),
    "green": np.array([0.22, 0.78, 0.32]),
    "olive": np.array([0.62, 0.76, 0.26]),
    "yellow": np.array([1.00, 0.86, 0.30]),
    "black": np.array([0.055, 0.045, 0.04]),
    "grey": np.array([0.30, 0.28, 0.26]),
    "teal": np.array([0.15, 0.62, 0.58]),
}


@dataclass
class PartTex:
    name: str
    bounds: tuple            # (x0, y0, x1, y1) 毫米，部件局部坐标（原点 = 与父部件的铆点）
    trans: np.ndarray        # (H, W, 4)
    refl: np.ndarray         # (H, W, 4)


class Leather:
    """在一块画布上分层画：先有皮的区域，再一块块上色，再镂刻。"""

    def __init__(self, x0, y0, x1, y1, ppmm=6.0):
        self.cv = Canvas(x0, y0, x1, y1, ppmm)
        self.bounds = (x0, y0, x1, y1)
        H, W = self.cv.H, self.cv.W
        self.cov = np.zeros((H, W), np.float32)
        self.dye = np.ones((H, W, 3), np.float32)
        self.dark = np.zeros((H, W), np.float32)    # 描线（皮面上较深的线，不透光少）

    def canvas(self):
        return self.cv.blank()

    def add(self, c: Canvas):
        self.cov = np.maximum(self.cov, c.array())

    def color(self, c: Canvas, dye):
        m = c.array()[..., None]
        col = DYE[dye] if isinstance(dye, str) else np.asarray(dye)
        self.dye = self.dye * (1 - m) + col * m

    def carve(self, c: Canvas):
        self.cov = self.cov * (1 - c.array())

    def line(self, c: Canvas, strength=0.85):
        self.dark = np.maximum(self.dark, c.array() * strength)

    def rivet(self, at, r=3.2):
        """枢钉：一个小皮疙瘩（颜色深、透光少）+ 中间一点亮（钉孔边缘）。"""
        c = self.canvas().circle(at, r)
        self.line(c, 0.9)
        c2 = self.canvas().circle(at, r * 0.35)
        m = c2.array()
        self.dark = self.dark * (1 - m * 0.6)

    def finish(self, name):
        cov = self.cov
        # 皮子边缘略厚、颜色深一点
        from scipy.ndimage import binary_erosion
        inner = binary_erosion(cov > 0.5, iterations=2).astype(np.float32)
        edge = np.clip(cov - inner, 0, 1) * 0.35
        dark = np.clip(np.maximum(self.dark, edge), 0, 1)[..., None]
        t = LEATHER_T * self.dye
        t = t * (1 - dark) + np.array([0.035, 0.03, 0.025]) * dark
        trans = np.ones(cov.shape + (4,), np.float32)
        trans[..., :3] = 1 - cov[..., None] + cov[..., None] * t
        trans[..., 3] = cov
        r = LEATHER_R * (0.35 + 0.65 * self.dye)
        r = r * (1 - dark) + np.array([0.03, 0.025, 0.02]) * dark
        refl = np.zeros_like(trans)
        refl[..., :3] = r
        refl[..., 3] = cov
        return PartTex(name, self.bounds, trans.astype(np.float32), refl.astype(np.float32))


# ---------------------------------------------------------------- 图案
def scale_feathers(lt: Leather, region_pts, origin, rows, cols, w, h, slant=0.0, crescent=True):
    """一排排鳞片状羽毛：每片羽毛描边，靠尖端刻一个月牙。"""
    region = lt.canvas().poly(region_pts).array() > 0.5
    lines = lt.canvas()
    holes = lt.canvas()
    for r in range(rows):
        for c in range(cols):
            cx = origin[0] - c * w + (r % 2) * w * 0.5 - r * slant
            cy = origin[1] - r * h * 0.78
            # 羽毛：朝后的圆弧
            ang = np.linspace(-1.25, 1.25, 14)
            arc = np.stack([cx - np.cos(ang) * w * 0.55, cy + np.sin(ang) * h * 0.55], 1)
            lines.line(arc, 0.55)
            if crescent:
                ang2 = np.linspace(-0.9, 0.9, 10)
                outer = np.stack([cx - np.cos(ang2) * w * 0.40, cy + np.sin(ang2) * h * 0.40], 1)
                inner = np.stack([cx - np.cos(ang2[::-1]) * w * 0.26 + w * 0.05, cy + np.sin(ang2[::-1]) * h * 0.30], 1)
                holes.poly(np.concatenate([outer, inner]))
    lm = lines.array() * region
    hm = holes.array() * region
    lt.dark = np.maximum(lt.dark, lm * 0.8)
    lt.cov = lt.cov * (1 - hm)


def hex_pattern(lt: Leather, region_pts, cell, wall=1.2, dot=True):
    """龟背纹：六角格，格子中间镂空成小六角，留下皮条格子。"""
    region = lt.canvas().poly(region_pts).array() > 0.5
    holes = lt.canvas()
    x0, y0, x1, y1 = lt.bounds
    dx = cell * 1.5
    dy = cell * math.sqrt(3)
    for i in range(int((x1 - x0) / dx) + 3):
        for k in range(int((y1 - y0) / dy) + 3):
            cx = x0 + i * dx
            cy = y0 + k * dy + (i % 2) * dy / 2
            rr = cell - wall
            pts = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
            holes.poly(pts)
            if dot:
                pass
    hm = holes.array() * region
    return hm


# ---------------------------------------------------------------- 鹤
N_NECK = 12
NECK_LEN = 21.0


def _feather(c, base, tip, w, holes=None, shaft=True):
    """一根长羽：圆头的叶形，中间一道羽轴；holes 画布上刻出羽轴两侧的细缝。"""
    base = np.asarray(base, float)
    tip = np.asarray(tip, float)
    d = tip - base
    L_ = np.linalg.norm(d)
    t = d / L_
    n = np.array([-t[1], t[0]])
    pts = []
    for u in np.linspace(0, 1, 14):
        ww = w * (0.55 + 0.45 * math.sin(math.pi * min(u * 0.95 + 0.05, 1.0)) ** 0.6) * (1 - 0.15 * u)
        pts.append(base + d * u + n * ww)
    for u in np.linspace(1, 0, 14):
        ww = w * (0.55 + 0.45 * math.sin(math.pi * min(u * 0.95 + 0.05, 1.0)) ** 0.6) * (1 - 0.15 * u)
        pts.append(base + d * u - n * ww)
    tipc = [base + d * 1.0 + t * w * 0.6]
    c.poly(catmull(np.array(pts[:14] + tipc + pts[14:]), True, 4))
    if holes is not None and shaft:
        holes.line([base + d * 0.08, base + d * 0.92], 0.55)
        for u in np.linspace(0.2, 0.85, 6):
            p = base + d * u
            for sg in (1, -1):
                holes.line([p + n * sg * 1.2, p + n * sg * w * 0.62 + t * w * 0.5], 0.45)


def _cloud(c, center, r, turns=1.6, w=1.2, flip=1):
    """云纹：一个往里卷的涡。"""
    th = np.linspace(0, turns * 2 * math.pi, 60)
    rr = r * (1 - th / (turns * 2 * math.pi) * 0.85)
    pts = np.stack([center[0] + flip * rr * np.cos(th), center[1] + rr * np.sin(th)], 1)
    c.line(pts, w)


def crane_parts(ppmm=6.0):
    parts = {}

    # ------ 身子（原点 = 身体中心；+x 朝前）
    lt = Leather(-205, -70, 112, 72, ppmm)
    body = [(99, 6), (97, 24), (86, 36), (62, 47), (22, 55), (-28, 54), (-74, 45), (-104, 29), (-118, 9),
            (-110, -12), (-82, -28), (-40, -38), (0, -42), (40, -38), (72, -26), (92, -11)]
    bp = catmull(body, True, 12)
    lt.add(lt.canvas().poly(bp))
    # 白羽：整个身子刻成鳞状羽片的网格——只留下一道道弧形的皮条，其余全部挖空，光大片透过来，鹤才是白的
    region = lt.canvas().poly(catmull([(96, 20), (84, 34), (62, 45), (22, 53), (-28, 52), (-74, 43), (-102, 27),
                                       (-114, 8), (-106, -11), (-80, -26), (-40, -36), (0, -40), (40, -36), (72, -24), (90, -10)],
                                      True, 10)).array()
    scal = lt.canvas()
    for r in range(9):
        yc = 50 - r * 10.5
        for c_ in range(13):
            xc = 100 - c_ * 16.0 + (r % 2) * 8.0 - r * 1.5
            ang = np.linspace(-1.25, 1.25, 14)
            arc = np.stack([xc - np.cos(ang) * 9.0, yc + np.sin(ang) * 7.4], 1)
            scal.line(arc, 1.45)
    sm = scal.array()
    breast = lt.canvas().poly(catmull([(99, 6), (96, 22), (84, 32), (68, 22), (62, -2), (70, -22), (92, -11)], True, 10)).array()
    open_ = region * (1 - breast)
    lt.cov = lt.cov * (1 - open_) + open_ * sm * lt.cov
    cl = lt.canvas()
    _cloud(cl, (80, 4), 11, 1.5, 1.2)
    _cloud(cl, (73, -14), 6.5, 1.3, 0.9, flip=-1)
    lt.carve(cl)
    # 翅膀（收拢）：粗轮廓 + 飞羽的长线——这些是留下来的皮条（挖空之后再补回来）
    wing = [(76, 36), (44, 50), (2, 54), (-40, 48), (-60, 34), (-56, 14), (-28, 4), (14, 6), (52, 16)]
    wpoly = catmull(wing, True, 10)
    wl = lt.canvas().line(wpoly, 2.4)
    lt.add(wl)
    lt.line(wl, 0.55)
    sec_l = lt.canvas()
    for k in range(5):
        b0 = (8 - k * 10, 36 - k * 5.5)
        tp = (-60 - k * 5, 30 - k * 6.5)
        sec_l.line(catmull([b0, ((b0[0] + tp[0]) / 2, (b0[1] + tp[1]) / 2 + 2.0), tp], False, 8), 1.9)
    lt.add(sec_l)
    lt.line(sec_l, 0.45)
    # 蓑羽：五根黑色长羽从背上垂下来，盖住尾部（往下弯）
    plumes = lt.canvas()
    slits = lt.canvas()
    specs = [((-20, 44), (-120, 58), (-190, 18), 10.0), ((-26, 34), (-118, 40), (-196, -4), 10.5),
             ((-32, 24), (-112, 22), (-186, -26), 10.0), ((-40, 14), (-104, 4), (-168, -46), 9.0),
             ((-48, 4), (-96, -12), (-142, -60), 8.0)]
    for (b0, mid, tp, w) in specs:
        curve = bezier(b0, mid, mid, tp, 40)
        shape = offset_polyline(curve, lambda t, w=w: w * (0.6 + 0.55 * math.sin(math.pi * min(t * 1.1, 1.0))) * (1 - 0.65 * t ** 2.5) + 0.8)
        plumes.poly(shape)
        slits.line(curve[3:-2], 0.6)
        for k in range(5, 36, 3):
            p = curve[k]
            tg = curve[k + 1] - curve[k - 1]
            tg = tg / np.linalg.norm(tg)
            nrm = np.array([-tg[1], tg[0]])
            ww = w * 0.62 * (1 - k / 46)
            for sg in (1, -1):
                slits.line([p + nrm * sg * 1.3, p + nrm * sg * ww - tg * ww * 0.85], 0.5)
    lt.add(plumes)
    lt.color(plumes, "black")
    lt.carve(slits)
    # 大腿的白羽"裤腿"
    lt.line(lt.canvas().line(catmull([(14, -40), (6, -54), (-8, -56), (-14, -44)], False, 6), 1.0), 0.75)
    ol = lt.canvas().line(bp, 2.2)
    lt.add(ol)
    lt.line(ol, 0.6)
    lt.rivet((84, 32), 2.4)
    lt.rivet((-2, -40), 2.2)
    lt.rivet((10, -38), 2.0)
    parts["body"] = lt.finish("body")

    # ------ 脖子：12 节
    for k in range(N_NECK):
        L_ = NECK_LEN
        w0 = 10.0 - 0.36 * k
        w1 = w0 - 0.36
        lt = Leather(-w0 - 3, -w0 - 3, L_ + w1 + 3, w0 + 3, ppmm)
        seg = [(0, -w0), (L_ * 0.5, -(w0 + w1) / 2), (L_, -w1), (L_ + w1 * 0.92, 0), (L_, w1),
               (L_ * 0.5, (w0 + w1) / 2), (0, w0), (-w0 * 0.92, 0)]
        poly = catmull(seg, True, 10)
        lt.add(lt.canvas().poly(poly))
        if k >= 2:
            lt.color(lt.canvas().poly(poly), "black")
            # 颈背一道白（刻空的细条），颈侧两道短斜线
            sl = lt.canvas()
            sl.line([(L_ * 0.05, w0 * 0.70), (L_ * 0.95, w1 * 0.70)], 1.1)
            sl.line([(L_ * 0.30, -w0 * 0.35), (L_ * 0.50, w0 * 0.20)], 0.6)
            sl.line([(L_ * 0.62, -w0 * 0.35), (L_ * 0.82, w0 * 0.20)], 0.6)
            lt.carve(sl)
        else:
            fl = lt.canvas()
            for j in range(2):
                fl.line(catmull([(L_ * (0.15 + 0.4 * j), -w0 * 0.6), (L_ * (0.32 + 0.4 * j), 0), (L_ * (0.15 + 0.4 * j), w0 * 0.6)], False, 6), 0.6)
            lt.line(fl, 0.75)
        lt.line(lt.canvas().line(poly, 0.7), 0.6)
        lt.rivet((0, 0), 1.9)
        parts[f"neck{k}"] = lt.finish(f"neck{k}")

    # ------ 头
    lt = Leather(-13, -16, 100, 22, ppmm)
    head = [(-9, -7), (-9, 7), (-2, 15), (11, 19.5), (23, 17), (31, 9), (35, 4), (98, 1.0), (98, -0.6), (35, -4.5),
            (27, -10), (12, -13.5), (0, -12.5)]
    hp = catmull(head, True, 10)
    lt.add(lt.canvas().poly(hp))
    face = lt.canvas().poly(catmull([(-9, -7), (-9, 7), (-2, 15), (11, 19.5), (23, 17), (31, 9), (35, 4), (35, -4.5),
                                     (27, -10), (12, -13.5), (0, -12.5)], True, 10))
    lt.color(face, "black")
    cheek = lt.canvas().poly(catmull([(-8, -4), (-5, 6), (4, 7), (12, 1), (9, -9), (0, -11)], True, 8))
    lt.color(cheek, "none")
    crown = lt.canvas().poly(catmull([(3, 14), (13, 19), (24, 16), (21, 10), (11, 9)], True, 8))
    lt.color(crown, "vermilion")
    dots = lt.canvas()
    for (x, y) in ((10, 15), (15, 16.5), (19, 14)):
        dots.circle((x, y), 0.9)
    lt.carve(dots)
    beak = lt.canvas().poly([(33, 4), (98, 1.0), (98, -0.6), (33, -4.5)])
    lt.color(beak, "olive")
    lt.line(lt.canvas().line([(35, -0.5), (92, 0.2)], 0.5), 0.8)
    lt.line(lt.canvas().line(catmull([(26, 6), (31, 3), (34, -1)], False, 6), 0.6), 0.6)
    eye = lt.canvas().circle((21, 6), 3.4)
    lt.carve(eye)
    pupil = lt.canvas().circle((21.5, 6), 1.6)
    lt.add(pupil)
    lt.color(pupil, "black")
    lt.line(lt.canvas().line(hp, 0.7), 0.6)
    lt.rivet((0, 0), 1.9)
    parts["head"] = lt.finish("head")

    # ------ 腿
    for side in ("near", "far"):
        dye = "black" if side == "far" else "grey"
        lt = Leather(-8, -98, 8, 8, ppmm)
        tib = [(-5.0, 0), (-3.6, -45), (-2.8, -90), (2.8, -90), (3.6, -45), (5.0, 0)]
        lt.add(lt.canvas().poly(catmull(tib, True, 6)))
        lt.color(lt.canvas().poly([(-6, -26), (-4, -98), (4, -98), (6, -26)]), dye)
        fe = lt.canvas()
        for k in range(3):
            fe.line([(-3.5, -4 - k * 7), (0, -1 - k * 7), (3.5, -4 - k * 7)], 0.55)
        lt.line(fe, 0.8)
        sc = lt.canvas()
        for k in range(6):
            sc.line([(-1.6, -34 - k * 9), (1.6, -36 - k * 9)], 0.5)
        lt.carve(sc)
        lt.rivet((0, 0), 1.8)
        parts[f"tibia_{side}"] = lt.finish(f"tibia_{side}")
        lt = Leather(-6, -108, 6, 6, ppmm)
        tar = [(-3.0, 0), (-2.4, -52), (-2.6, -102), (2.6, -102), (2.4, -52), (3.0, 0)]
        lt.add(lt.canvas().poly(catmull(tar, True, 6)))
        lt.color(lt.canvas().poly(catmull(tar, True, 6)), dye)
        sc = lt.canvas()
        for k in range(10):
            sc.line([(-1.5, -10 - k * 9), (1.5, -12 - k * 9)], 0.45)
        lt.carve(sc)
        lt.rivet((0, 0), 1.7)
        parts[f"tarsus_{side}"] = lt.finish(f"tarsus_{side}")
        lt = Leather(-22, -10, 46, 8, ppmm)
        foot = lt.canvas()
        foot.line([(0, 0), (40, -4)], 2.6)
        foot.line([(0, 0), (33, 3)], 2.2)
        foot.line([(0, 0), (30, -9)], 2.2)
        foot.line([(0, 0), (-16, -3)], 2.0)
        foot.circle((0, 0), 3.6)
        lt.add(foot)
        lt.color(foot, dye)
        lt.rivet((0, 0), 1.6)
        parts[f"foot_{side}"] = lt.finish(f"foot_{side}")
    return parts


# ---------------------------------------------------------------- 乌龟
def _scute(lt, poly, rings=2, dye=None):
    """一块盾片：边缘留皮（深色线），里面刻同心的生长纹，中心一个小孔。"""
    P = np.asarray(poly, float)
    c = P.mean(0)
    lines = lt.canvas()
    lines.line(np.concatenate([P, P[:1]]), 1.6)
    lt.line(lines, 0.85)
    holes = lt.canvas()
    for k in range(rings):
        s = 0.72 - k * 0.24
        Q = c + (P - c) * s
        holes.line(np.concatenate([Q, Q[:1]]), 0.7)
    holes.circle(c, 1.6)
    lt.carve(holes)


def turtle_parts(ppmm=6.0):
    parts = {}
    lt = Leather(-125, -24, 116, 80, ppmm)
    shell = [(-104, 0), (-99, 24), (-78, 48), (-40, 66), (4, 71), (46, 62), (78, 42), (98, 16), (103, 0),
             (95, -9), (60, -15), (0, -17), (-60, -15), (-96, -9)]
    tail = [(-100, -4), (-121, -11), (-103, -13)]
    sp = catmull(shell, True, 10)
    lt.add(lt.canvas().poly(sp))
    lt.add(lt.canvas().poly(tail))
    carap = catmull([(-98, 3), (-93, 25), (-73, 46), (-37, 63), (4, 67), (44, 59), (74, 40), (93, 14), (97, 3)], True, 10)
    lt.color(lt.canvas().poly(carap), "olive")
    # 盾片：脊盾（顶上一排）、肋盾（两侧）、缘盾（边上一圈）
    # 用参数网格直接构造：外圈缘盾 12 块，中圈肋盾 4 块，内圈脊盾 4 块
    def ring_pt(t, s):
        ang = math.pi * (1 - t)
        return (98 * s * math.cos(ang), 3 + 64 * s * math.sin(ang))
    tt = np.linspace(0.02, 0.98, 13)
    for k in range(12):
        q = [ring_pt(tt[k], 0.99), ring_pt(tt[k + 1], 0.99), ring_pt(tt[k + 1], 0.83), ring_pt(tt[k], 0.83)]
        _scute(lt, q, rings=1)
    tc = np.linspace(0.06, 0.94, 5)
    for k in range(4):
        q = [ring_pt(tc[k], 0.83), ring_pt(tc[k + 1], 0.83), ring_pt(tc[k + 1] - 0.02, 0.52), ring_pt(tc[k] + 0.02, 0.52)]
        _scute(lt, q, rings=2)
    tv = np.linspace(0.16, 0.84, 5)
    for k in range(4):
        q = [ring_pt(tv[k], 0.52), ring_pt(tv[k + 1], 0.52), ring_pt(tv[k + 1], 0.20), ring_pt(tv[k], 0.20)]
        _scute(lt, q, rings=2)
    plast = catmull([(-96, -2), (-60, -12), (0, -14), (60, -12), (97, -2), (60, -6), (0, -7), (-60, -6)], True, 8)
    lt.color(lt.canvas().poly(plast), "yellow")
    band = lt.canvas()
    for k in range(9):
        x = -80 + k * 20
        band.line([(x, -11.5), (x + 4, -5)], 0.7)
    lt.line(band, 0.8)
    lt.line(lt.canvas().line(sp, 1.0), 0.7)
    lt.rivet((88, 6), 2.2)
    lt.rivet((58, -8), 2.0)
    lt.rivet((-62, -8), 2.0)
    lt.rivet((64, -6), 1.8)
    lt.rivet((-56, -6), 1.8)
    parts["shell"] = lt.finish("shell")

    # ------ 头颈
    lt = Leather(-42, -16, 94, 22, ppmm)
    hn = [(-38, -8), (-38, 8), (18, 9.5), (44, 12), (60, 15.5), (76, 14), (87, 7.5), (90, 1), (86, -5.5), (70, -9.5), (48, -8.5), (18, -8)]
    hp = catmull(hn, True, 10)
    lt.add(lt.canvas().poly(hp))
    lt.color(lt.canvas().poly(hp), "olive")
    lt.color(lt.canvas().poly([(-38, -8), (-38, 8), (36, 10), (36, -8)]), "yellow")
    sc = lt.canvas()
    for k in range(8):
        for j in range(2):
            sc.ellipse((-30 + k * 8 + j * 4, -3 + j * 5), 1.8, 1.2)
    lt.carve(sc)
    hs = lt.canvas()
    _cloud(hs, (58, 3), 6.5, 1.3, 0.8)
    lt.carve(hs)
    eye = lt.canvas().circle((72, 7), 3.2)
    lt.carve(eye)
    pupil = lt.canvas().circle((72.8, 7.2), 1.5)
    lt.add(pupil)
    lt.color(pupil, "black")
    mouth = lt.canvas().line(catmull([(89, -1.5), (81, -2.4), (70, -1.0), (66, 0.8)], False, 6), 0.8)
    lt.line(mouth, 0.85)
    lt.line(lt.canvas().line(hp, 0.8), 0.6)
    parts["headneck"] = lt.finish("headneck")

    for nm, length, cd in (("front", 30, 1), ("back", 27, -1)):
        for side in ("near", "far"):
            lt = Leather(-20, -length - 12, 22, 10, ppmm)
            leg = [(-9, 4), (9, 4), (11, -length * 0.55), (12 * cd if cd > 0 else 8, -length), (-8 if cd > 0 else -12, -length), (-10, -length * 0.55)]
            lp = catmull(leg, True, 8)
            lt.add(lt.canvas().poly(lp))
            lt.color(lt.canvas().poly(lp), "olive" if side == "near" else "green")
            cl = lt.canvas()
            for k in range(4):
                x = -6 + k * 4.5 + cd * 2
                cl.poly([(x - 1.5, -length + 1), (x + 1.5, -length + 1), (x + cd * 2.4, -length - 7)])
            lt.add(cl)
            lt.color(cl, "black")
            sc = lt.canvas()
            for k in range(3):
                for j in range(2):
                    sc.ellipse((-4 + j * 8, -6 - k * 7 - j * 3), 2.2, 1.3)
            lt.carve(sc)
            lt.line(lt.canvas().line(lp, 0.8), 0.6)
            lt.rivet((0, 0), 1.9)
            parts[f"leg_{nm}_{side}"] = lt.finish(f"leg_{nm}_{side}")
    return parts


# ---------------------------------------------------------------- 图集
class Atlas:
    """把多张 RGBA 贴图装进一张大图（货架式排列）。"""

    def __init__(self, width=4096):
        self.width = width
        self.items = []

    def add(self, img):
        self.items.append(np.asarray(img, np.float32))
        return len(self.items) - 1

    def build(self):
        x = y = 0
        shelf = 0
        rects = []
        for im in self.items:
            h, w = im.shape[:2]
            if x + w > self.width:
                x = 0
                y += shelf + 2
                shelf = 0
            rects.append((x, y, w, h))
            x += w + 2
            shelf = max(shelf, h)
        H = y + shelf + 2
        atlas = np.zeros((H, self.width, 4), np.float32)
        for im, (x, y, w, h) in zip(self.items, rects):
            atlas[y:y + h, x:x + w] = im
        return atlas, np.array(rects, np.float64)


# ---------------------------------------------------------------- 骨架与姿势
@dataclass
class Joint:
    part: str
    parent: str            # 父部件名（根为 None）
    at: tuple              # 在父部件局部坐标里的铆点位置（mm）
    layer: float           # 前后层次（mm，正数更靠近床单）


CRANE_RIG = [Joint("body", None, (0, 0), 0.0)] + \
    [Joint("neck0", "body", (84, 32), 0.6)] + \
    [Joint(f"neck{k}", f"neck{k - 1}", (NECK_LEN, 0), 0.6 + 0.12 * k) for k in range(1, N_NECK)] + \
    [Joint("head", f"neck{N_NECK - 1}", (NECK_LEN, 0), 2.4),
     Joint("tibia_far", "body", (10, -38), -1.2), Joint("tarsus_far", "tibia_far", (0, -86), -1.3), Joint("foot_far", "tarsus_far", (0, -100), -1.4),
     Joint("tibia_near", "body", (-2, -40), 1.0), Joint("tarsus_near", "tibia_near", (0, -86), 1.1), Joint("foot_near", "tarsus_near", (0, -100), 1.2)]

TURTLE_RIG = [Joint("shell", None, (0, 0), 0.0),
              Joint("headneck", "shell", (88, 6), -0.8),
              Joint("leg_front_far", "shell", (64, -6), -1.0), Joint("leg_back_far", "shell", (-56, -6), -1.0),
              Joint("leg_front_near", "shell", (58, -8), 0.8), Joint("leg_back_near", "shell", (-62, -8), 0.8)]


@dataclass
class Pose:
    """部件角度（弧度，相对父部件）与少量额外自由度。"""
    root_xz: tuple = (1.2, 1.3)     # 根部铆点在床单平面上的位置（米：x, z）
    root_angle: float = 0.0
    facing: int = 1                 # 1 朝东（观众看是朝右）；-1 朝西
    dist: float = 0.004             # 离床单的距离（米），贴紧≈4mm
    tilt: float = 0.0               # 皮影平面绕竖直轴的偏转（弧度）
    angles: dict = field(default_factory=dict)
    slide: dict = field(default_factory=dict)   # 滑动关节（乌龟头颈）沿 x 的位移 mm


def solve(rig, pose: Pose):
    """正向运动学：返回每个部件的 (原点mm, 角度)。"""
    out = {}
    for j in rig:
        a = pose.angles.get(j.part, 0.0)
        if j.parent is None:
            out[j.part] = (np.array([0.0, 0.0]), pose.root_angle + a)
        else:
            po, pa = out[j.parent]
            ca, sa = math.cos(pa), math.sin(pa)
            at = np.array(j.at, float)
            o = po + np.array([ca * at[0] - sa * at[1], sa * at[0] + ca * at[1]])
            ang = pa + a
            s = pose.slide.get(j.part, 0.0)
            if s:
                o = o + np.array([math.cos(ang), math.sin(ang)]) * s
            out[j.part] = (o, ang)
    return out


def to_world(pose: Pose, p_mm, sheet_y, layer_mm=0.0):
    """皮影平面局部坐标（mm）→ 世界坐标（米）。"""
    x = pose.root_xz[0] + pose.facing * p_mm[0] / 1000.0 * math.cos(pose.tilt)
    y = sheet_y + pose.dist + layer_mm / 1000.0 + pose.facing * p_mm[0] / 1000.0 * math.sin(pose.tilt)
    z = pose.root_xz[1] + p_mm[1] / 1000.0
    return np.array([x, y, z])


def add_puppet(pl, rig, parts, tex_ids, pose: Pose, sheet_y, mat_id, name="puppet", rods=(), rod_mat=None):
    """把皮影的每个部件加成透光四边形（参与可见和阴影）；签子加成细圆柱。
    rods: [(部件名, 局部点mm, 手的世界位置)]"""
    from .rt import F_ALPHA, F_SHADOW, F_TRANSMIT
    sol = solve(rig, pose)
    for j in rig:
        pt = parts[j.part]
        o, ang = sol[j.part]
        x0, y0, x1, y1 = pt.bounds
        ca, sa = math.cos(ang), math.sin(ang)

        def L2(px, py):
            return o + np.array([ca * px - sa * py, sa * px + ca * py])

        c00 = to_world(pose, L2(x0, y0), sheet_y, j.layer)
        c10 = to_world(pose, L2(x1, y0), sheet_y, j.layer)
        c01 = to_world(pose, L2(x0, y1), sheet_y, j.layer)
        k = pl.quad(mat_id, c00, c10 - c00, c01 - c00, flags=F_SHADOW | F_TRANSMIT | F_ALPHA, tex=tex_ids[j.part],
                    name=f"{name}:{j.part}")
    world_rods = []
    for (part, local, hand) in rods:
        o, ang = sol[part]
        ca, sa = math.cos(ang), math.sin(ang)
        p = o + np.array([ca * local[0] - sa * local[1], sa * local[0] + ca * local[1]])
        a = to_world(pose, p, sheet_y, 3.0)
        pl.cyl(rod_mat, a, hand, 0.0026, name=f"{name}:rod")
        world_rods.append((a, np.asarray(hand, float)))
    return sol, world_rods
