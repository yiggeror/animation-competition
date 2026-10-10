"""小满和奶奶：比例、骨架、身体与衣服的 SDF 形体。

身体是一个连续的形体（平滑并集），衣服是另一层，头发再一层。
手臂和腿用两段式 IK 摆放，关节只会朝正确的方向弯；手指逐节弯曲，拇指可以对握。
"""
import math
from dataclasses import dataclass, field

import numpy as np

from . import sdf as S
from .materials import M
from .rig import axis_angle, euler, frame_from, rx, ry, rz, two_bone_ik

FINGERS = ("index", "middle", "ring", "pinky")


@dataclass
class Proportions:
    name: str
    hip_h: float            # 站立时髋关节离地高度（参考）
    spine1: float
    spine2: float
    neck: float
    head_pivot: float
    head_r: tuple           # 颅骨椭球半径 (宽, 深, 高)
    face_r: tuple
    shoulder_w: float       # 肩关节离中线
    shoulder_up: float
    upper_arm: float
    forearm: float
    arm_r: tuple            # (肩, 肘, 腕)
    hip_w: float
    thigh: float
    shin: float
    leg_r: tuple            # (髋, 膝, 踝)
    foot_len: float
    palm: tuple             # (长, 宽, 厚)
    finger_len: dict        # 每根手指三节长度
    finger_r: tuple         # (根, 尖)
    thumb_len: tuple
    thumb_r: tuple
    knuckle: float = 0.0    # 指关节额外的骨感
    stoop: float = 0.0      # 驼背（度）
    skin: str = "skin_xm"
    torso_r: tuple = (0.13, 0.09, 0.13)


XIAOMAN = Proportions(
    name="xiaoman", hip_h=0.648, spine1=0.10, spine2=0.12, neck=0.12, head_pivot=0.062,
    head_r=(0.096, 0.101, 0.106), face_r=(0.080, 0.077, 0.075),
    shoulder_w=0.128, shoulder_up=0.095, upper_arm=0.21, forearm=0.18, arm_r=(0.034, 0.028, 0.022),
    hip_w=0.068, thigh=0.285, shin=0.272, leg_r=(0.056, 0.040, 0.030), foot_len=0.175,
    palm=(0.066, 0.060, 0.024),
    finger_len={"index": (0.029, 0.018, 0.015), "middle": (0.032, 0.020, 0.016), "ring": (0.030, 0.019, 0.015),
                "pinky": (0.023, 0.014, 0.013)},
    finger_r=(0.0074, 0.0060), thumb_len=(0.028, 0.023, 0.019), thumb_r=(0.0092, 0.0072),
    skin="skin_xm", torso_r=(0.125, 0.085, 0.125))

NAINAI = Proportions(
    name="nainai", hip_h=0.826, spine1=0.11, spine2=0.14, neck=0.13, head_pivot=0.065,
    head_r=(0.088, 0.098, 0.104), face_r=(0.073, 0.073, 0.077),
    shoulder_w=0.145, shoulder_up=0.10, upper_arm=0.26, forearm=0.225, arm_r=(0.036, 0.027, 0.021),
    hip_w=0.085, thigh=0.38, shin=0.362, leg_r=(0.068, 0.044, 0.032), foot_len=0.215,
    palm=(0.076, 0.066, 0.022),
    finger_len={"index": (0.037, 0.023, 0.019), "middle": (0.041, 0.026, 0.020), "ring": (0.038, 0.024, 0.019),
                "pinky": (0.030, 0.018, 0.016)},
    finger_r=(0.0068, 0.0054), thumb_len=(0.033, 0.027, 0.022), thumb_r=(0.0086, 0.0066),
    knuckle=0.0012, stoop=9.0, skin="skin_nn", torso_r=(0.15, 0.11, 0.14))


@dataclass
class Hand:
    """手的姿势。frame：世界坐标的 3x3（列 x=拇指侧(右手)/小指侧(左手)，y=手指方向，z=掌心朝向）。"""
    frame: np.ndarray = None
    curl: dict = field(default_factory=lambda: {f: (15.0, 20.0, 10.0) for f in FINGERS})
    spread: float = 4.0
    thumb: tuple = (20.0, 10.0, 10.0, 10.0)   # (对掌, 掌指, 近节, 远节)
    thumb_along: bool = False                  # 拇指顺着签子贴上去（握细棍、拿筷子的握法）


@dataclass
class CharPose:
    root: tuple = (0, 0, 0.62)       # 骨盆中心（世界）
    yaw: float = 0.0                  # 朝向：0 = 面朝世界 +y
    lean: tuple = (0.0, 0.0)          # 整体前倾、侧倾（度）
    spine1: tuple = (0.0, 0.0, 0.0)
    spine2: tuple = (0.0, 0.0, 0.0)
    neck: tuple = (0.0, 0.0, 0.0)
    head: tuple = (0.0, 0.0, 0.0)
    shrug: tuple = (0.0, 0.0)         # (右, 左) 耸肩，米
    wrist: dict = field(default_factory=dict)     # 'R'/'L' -> 世界坐标
    elbow_pole: dict = field(default_factory=dict)
    hands: dict = field(default_factory=dict)     # 'R'/'L' -> Hand
    ankle: dict = field(default_factory=dict)
    knee_pole: dict = field(default_factory=dict)
    foot_dir: dict = field(default_factory=dict)  # 脚尖方向（世界）
    expr: dict = field(default_factory=dict)
    hair_offset: tuple = (0.0, 0.0, 0.0)          # 头发的惯性偏移（弹簧算出）
    cowlick: tuple = (0.0, 0.0)                   # 呆毛的摆动
    ponytail: tuple = (0.0, 0.0, 0.0)             # 马尾的惯性偏移（弹簧算出，头部局部坐标）
    breath: float = 0.0                           # 呼吸 0..1


class Builder:
    def __init__(self):
        self.rows = []
        self.groups = []
        self._g = []

    def begin(self):
        self._g = []

    def end(self, pad=0.0):
        if not self._g:
            return
        lo = np.min([g[0] for g in self._g], axis=0) - pad
        hi = np.max([g[1] for g in self._g], axis=0) + pad
        c = (lo + hi) / 2
        r = np.linalg.norm(hi - lo) / 2
        start = len(self.rows) - len(self._g)
        self.groups.append([c[0], c[1], c[2], r, start, len(self._g), 0, 0])
        self._g = []

    def _row(self, typ, mat, k, layer):
        row = np.zeros(S.NC)
        row[0] = typ
        row[1] = M(mat)
        row[2] = len(self.groups)
        row[3] = k
        row[23] = layer
        return row

    def cone(self, a, b, ra, rb, mat, k=0.02, layer=0):
        row = self._row(S.ROUNDCONE, mat, k, layer)
        row[4:7] = a
        row[7:10] = b
        row[10] = ra
        row[11] = rb
        self.rows.append(row)
        r = max(ra, rb) + k
        self._g.append((np.minimum(a, b) - r, np.maximum(a, b) + r))

    def capcone(self, a, b, ra, rb, mat, rnd=0.004, k=0.02, layer=1):
        row = self._row(S.CAPCONE, mat, k, layer)
        row[4:7] = a
        row[7:10] = b
        row[10] = ra
        row[11] = rb
        row[12] = rnd
        self.rows.append(row)
        r = max(ra, rb) + k
        self._g.append((np.minimum(a, b) - r, np.maximum(a, b) + r))

    def ell(self, c, r, R, mat, k=0.02, layer=0):
        row = self._row(S.ELLIPSOID, mat, k, layer)
        row[4:7] = c
        row[7:10] = r
        row[10:19] = np.asarray(R).reshape(-1)
        self.rows.append(row)
        e = max(r) + k
        self._g.append((np.asarray(c) - e, np.asarray(c) + e))

    def rbox(self, c, h, R, rnd, mat, k=0.01, layer=0):
        row = self._row(S.ROUNDBOX, mat, k, layer)
        row[4:7] = c
        row[7:10] = h
        row[10:19] = np.asarray(R).reshape(-1)
        row[19] = rnd
        self.rows.append(row)
        e = np.linalg.norm(h) + k
        self._g.append((np.asarray(c) - e, np.asarray(c) + e))

    def arrays(self):
        if not self.rows:
            return S.empty()
        return np.array(self.rows), np.array(self.groups, float)


# ------------------------------------------------------------------ 手
def grip_frame(stick_dir, palm_toward, side="R"):
    """握一根棍子：掌心朝 palm_toward，手指绕着棍子（与棍垂直），拇指侧沿着棍子。"""
    a = np.asarray(stick_dir, float)
    a /= np.linalg.norm(a)
    z = np.asarray(palm_toward, float)
    z = z - a * (z @ a)
    z /= np.linalg.norm(z)
    x = a if side == "R" else -a
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def hand_prims(B: Builder, P: Proportions, wrist, F, hand: Hand, side, skin):
    """手掌 + 拇指根的肌肉 + 五根手指（逐节）。返回指尖位置（用来检查接触）。"""
    sgn = 1.0 if side == "R" else -1.0
    X, Y, Z = F[:, 0], F[:, 1], F[:, 2]
    pl, pw, pt = P.palm
    B.begin()
    # 手掌：稍微拱起（掌心凹），用圆角盒 + 掌根椭球
    c = wrist + Y * (pl * 0.5) - Z * (pt * 0.05)
    B.rbox(c, (pw * 0.5, pl * 0.5, pt * 0.5), F, pt * 0.45, skin, k=0.010)
    B.ell(wrist + Y * (pl * 0.18) + Z * (pt * 0.15), (pw * 0.46, pl * 0.25, pt * 0.48), F, skin, k=0.012)
    # 拇指根（大鱼际）
    B.ell(wrist + Y * (pl * 0.32) + X * (sgn * pw * 0.28) + Z * (pt * 0.35), (pw * 0.22, pl * 0.30, pt * 0.42), F, skin, k=0.010)
    tips = {}
    offs = {"index": 0.36, "middle": 0.12, "ring": -0.12, "pinky": -0.36}
    yoff = {"index": -0.02, "middle": 0.02, "ring": 0.0, "pinky": -0.10}
    for f in FINGERS:
        base = wrist + Y * (pl * (1.0 + yoff[f])) + X * (sgn * pw * offs[f])
        d = Y.copy()
        spread = hand.spread * (offs[f] / 0.36) * sgn
        d = axis_angle(Z, spread) @ d
        c0, c1, c2 = hand.curl.get(f, (10, 10, 10))
        lens = P.finger_len[f]
        r0, r1 = P.finger_r
        if f == "pinky":
            r0, r1 = r0 * 0.88, r1 * 0.9
        p = base
        rads = np.linspace(r0, r1, 4)
        axis = np.cross(d, Z)  # 绕这根轴弯向掌心
        for k, (ang, ln) in enumerate(zip((c0, c1, c2), lens)):
            axis = np.cross(d, Z if k == 0 else axis_z)
            axis /= np.linalg.norm(axis) + 1e-12
            d = axis_angle(axis, ang) @ d
            axis_z = np.cross(axis, d)
            q = p + d * ln
            B.cone(p, q, rads[k], rads[k + 1], skin, k=0.006 if k else 0.009)
            if P.knuckle and k < 2:
                B.cone(q, q, rads[k + 1] + P.knuckle, rads[k + 1] + P.knuckle, skin, k=0.004)
            p = q
        tips[f] = p
    # 拇指：从掌根拇指侧伸出；对掌角度让它转向掌心
    opp, a0, a1, a2 = hand.thumb
    base = wrist + Y * (pl * 0.20) + X * (sgn * pw * 0.42) + Z * (pt * 0.25)
    if hand.thumb_along:
        # 拇指沿着手的 x 轴（握棍时 = 棍子方向），稍微压向掌心一侧
        d = X * sgn * 0.80 + Y * 0.45 + Z * 0.40
    else:
        d = (Y * 0.75 + X * sgn * 0.55 + Z * 0.35)
    d /= np.linalg.norm(d)
    d = axis_angle(Y, -sgn * opp) @ d
    p = base
    lens = P.thumb_len
    rads = np.linspace(P.thumb_r[0], P.thumb_r[1], 4)
    for k, (ang, ln) in enumerate(zip((a0, a1, a2), lens)):
        axis = np.cross(d, Z)
        axis /= np.linalg.norm(axis) + 1e-12
        d = axis_angle(axis, ang * 0.8) @ d
        q = p + d * ln
        B.cone(p, q, rads[k] * (1.25 if k == 0 else 1.0), rads[k + 1], skin, k=0.010 if k == 0 else 0.006)
        p = q
    tips["thumb"] = p
    B.end(0.01)
    return tips


# ------------------------------------------------------------------ 整个人
def body_frames(P: Proportions, pose: CharPose):
    """躯干、头的世界变换。"""
    R0 = rz(pose.yaw) @ rx(-pose.lean[0]) @ ry(pose.lean[1])
    root = np.asarray(pose.root, float)
    R1 = R0 @ euler(*pose.spine1)
    s1 = root + R0 @ np.array([0, 0, P.spine1])
    R2 = R1 @ euler(*pose.spine2) @ rx(-P.stoop)
    s2 = s1 + R1 @ np.array([0, 0, P.spine2])
    breath = 1.0 + 0.012 * pose.breath
    Rn = R2 @ euler(*pose.neck) @ rx(-P.stoop * 0.9)
    neck = s2 + R2 @ np.array([0, 0.0, P.neck])
    Rh = Rn @ euler(*pose.head) @ rx(P.stoop * 1.6)
    hp = neck + Rn @ np.array([0, 0.004, P.head_pivot])
    hc = hp + Rh @ np.array([0, 0.012, 0.088])
    return dict(R0=R0, R1=R1, R2=R2, Rn=Rn, Rh=Rh, root=root, s1=s1, s2=s2, neck=neck, hp=hp, hc=hc, breath=breath)


def default_limbs(P: Proportions, pose: CharPose, fr):
    """没给 IK 目标时：手臂自然下垂，腿直立。"""
    R0, R2 = fr["R0"], fr["R2"]
    out = {}
    for side, sg in (("R", 1), ("L", -1)):
        sh = fr["s2"] + R2 @ np.array([sg * P.shoulder_w, 0.0, P.shoulder_up])
        out[f"wrist_{side}"] = sh + R0 @ np.array([sg * 0.05, 0.03, -(P.upper_arm + P.forearm) * 0.97])
        out[f"pole_{side}"] = sh + R0 @ np.array([sg * 0.25, -0.35, -0.15])
        hip = fr["root"] + R0 @ np.array([sg * P.hip_w, 0, -0.04])
        out[f"ankle_{side}"] = hip + R0 @ np.array([0, 0.0, -(P.thigh + P.shin) * 0.99])
        out[f"kpole_{side}"] = hip + R0 @ np.array([0, 0.5, -0.2])
    return out


def build(P: Proportions, pose: CharPose, outfit: str):
    """返回 (chars, groups, info)。info 里有头部变换（画五官用）、关键点（检查接触用）。"""
    B = Builder()
    fr = body_frames(P, pose)
    R0, R1, R2, Rn, Rh = fr["R0"], fr["R1"], fr["R2"], fr["Rn"], fr["Rh"]
    skin = P.skin
    info = {"head_c": fr["hc"], "head_R": Rh, "frames": fr, "who": P.name,
            "chest_c": fr["s2"], "chest_R": R2, "neck_c": fr["neck"]}
    dl = default_limbs(P, pose, fr)

    # ---------------- 头
    B.begin()
    hc = fr["hc"]
    hr = P.head_r
    B.ell(hc + Rh @ np.array([0, -0.006, 0.022]), hr, Rh, skin, k=0.03)
    fc = hc + Rh @ np.array([0, 0.024, -0.032])
    puff = pose.expr.get("puff", 0.0)
    B.ell(fc, (P.face_r[0] * (1 + 0.10 * puff), P.face_r[1], P.face_r[2]), Rh, skin, k=0.035)
    # 脸颊（鼓腮时变大）
    for sg in (1, -1):
        B.ell(hc + Rh @ np.array([sg * 0.046, 0.058, -0.040]), (0.026 + 0.016 * puff, 0.022 + 0.012 * puff, 0.024 + 0.008 * puff),
              Rh, skin, k=0.02)
    B.ell(hc + Rh @ np.array([0, 0.052, -0.083]), (0.028, 0.026, 0.022), Rh, skin, k=0.03)          # 下巴
    if P.name == "xiaoman":
        B.ell(hc + Rh @ np.array([0, 0.084, -0.018]), (0.010, 0.010, 0.012), Rh, skin, k=0.014)   # 小鼻头
    else:
        B.ell(hc + Rh @ np.array([0, 0.086, -0.016]), (0.0135, 0.014, 0.018), Rh, skin, k=0.014)  # 奶奶：圆一点的鼻子
    for sg in (1, -1):
        B.ell(hc + Rh @ np.array([sg * 0.086, -0.006, -0.008]), (0.011, 0.020, 0.029), Rh @ rz(sg * 12), skin, k=0.01)  # 耳朵
    # 脖子
    B.cone(fr["neck"] - R2 @ np.array([0, 0.0, 0.03]), fr["hp"] + Rh @ np.array([0, 0.0, 0.01]),
           0.038 if P.name == "nainai" else 0.035, 0.033, skin, k=0.03)
    hair_prims(B, P, pose, hc, Rh)
    B.end(0.02)

    # ---------------- 衣服（躯干）
    B.begin()
    tr = P.torso_r
    br = fr["breath"]
    # 斜方肌：从脖子根斜下到肩头，让肩膀有坡度（不是平的托盘）
    for sg in (1, -1):
        shp = fr["s2"] + R2 @ np.array([sg * P.shoulder_w, 0.0, P.shoulder_up + (pose.shrug[0] if sg > 0 else pose.shrug[1])])
        nb = fr["neck"] + R2 @ np.array([sg * 0.022, -0.004, -0.028])
        B.cone(nb, shp, 0.040, P.arm_r[0] + 0.013, "tshirt_xm" if outfit == "xiaoman" else "blouse_nn", k=0.04, layer=1)
    if outfit == "xiaoman":
        top = "tshirt_xm"
        B.ell(fr["s2"] + R2 @ np.array([0, 0.004, -0.004]), (tr[0] * 0.96 * br, tr[1] * br, tr[2] * 0.92), R2, top, k=0.05, layer=1)
        B.ell(fr["s1"] + R1 @ np.array([0, 0.006, 0.0]), (tr[0] * 0.98, tr[1] * 1.02, tr[2] * 0.9), R1, top, k=0.05, layer=1)
        B.ell(fr["root"] + R0 @ np.array([0, 0.004, 0.0]), (tr[0] * 1.02, tr[1] * 1.05, 0.075), R0, top, k=0.04, layer=1)
        # 短裤
        B.ell(fr["root"] + R0 @ np.array([0, 0.0, -0.045]), (tr[0] * 0.95, tr[1] * 1.0, 0.085), R0, "shorts_xm", k=0.03, layer=1)
    else:
        top = "blouse_nn"
        B.ell(fr["s2"] + R2 @ np.array([0, 0.012, -0.004]), (tr[0] * 0.95 * br, tr[1] * br, tr[2] * 0.92), R2, top, k=0.05, layer=1)
        B.ell(fr["s1"] + R1 @ np.array([0, 0.022, -0.01]), (tr[0] * 1.0, tr[1] * 1.08, tr[2] * 0.9), R1, top, k=0.05, layer=1)   # 有点肚子
        B.ell(fr["root"] + R0 @ np.array([0, 0.01, 0.01]), (tr[0] * 1.04, tr[1] * 1.08, 0.08), R0, top, k=0.04, layer=1)
        B.ell(fr["root"] + R0 @ np.array([0, 0.0, -0.05]), (tr[0] * 0.98, tr[1] * 1.0, 0.09), R0, "trousers_nn", k=0.03, layer=1)
    B.end(0.03)

    # ---------------- 手臂 + 手
    for side, sg in (("R", 1), ("L", -1)):
        shrug = pose.shrug[0] if side == "R" else pose.shrug[1]
        sh = fr["s2"] + R2 @ np.array([sg * P.shoulder_w, 0.0, P.shoulder_up + shrug])
        wt = pose.wrist.get(side, dl[f"wrist_{side}"])
        pole = pose.elbow_pole.get(side, dl[f"pole_{side}"])
        el, wr = two_bone_ik(sh, wt, P.upper_arm, P.forearm, pole)
        info[f"shoulder_{side}"], info[f"elbow_{side}"], info[f"wrist_{side}"] = sh, el, wr
        B.begin()
        ra, re, rw = P.arm_r
        # 上臂：肩部更粗（三角肌），肘部收窄
        B.cone(sh, el, ra, re, skin, k=0.02)
        mid = sh + (el - sh) * 0.3
        B.ell(mid, (ra * 1.05, ra * 1.05, np.linalg.norm(el - sh) * 0.32), _axis_frame(el - sh), skin, k=0.02)
        B.cone(el, wr, re * 0.98, rw, skin, k=0.018)
        # 前臂靠肘一段更厚（肌肉）
        B.ell(el + (wr - el) * 0.28, (re * 1.12, re * 1.0, np.linalg.norm(wr - el) * 0.30), _axis_frame(wr - el), skin, k=0.018)
        # 袖子
        dirv = (el - sh) / (np.linalg.norm(el - sh) + 1e-9)
        if outfit == "xiaoman":
            B.capcone(sh - dirv * 0.012, sh + dirv * 0.105, ra + 0.013, ra + 0.017, top, rnd=0.005, k=0.035)
        else:
            B.capcone(sh - dirv * 0.012, sh + dirv * 0.13, ra + 0.012, ra + 0.015, top, rnd=0.005, k=0.035)
            if side == "L":
                # 玉镯：腕上一圈
                wdir = (wr - el) / (np.linalg.norm(wr - el) + 1e-9)
                ring_c = wr - wdir * 0.025
                for k_ in range(10):
                    a = 2 * math.pi * k_ / 10
                    fx = _axis_frame(wdir)
                    off = fx[:, 0] * math.cos(a) * (rw + 0.007) + fx[:, 1] * math.sin(a) * (rw + 0.007)
                    B.cone(ring_c + off, ring_c + off, 0.0045, 0.0045, "jade", k=0.004)
        B.end(0.02)
        hand = pose.hands.get(side, Hand())
        if hand.frame is None:
            fdir = (wr - el) / (np.linalg.norm(wr - el) + 1e-9)
            palm = R0 @ np.array([-sg, 0.15, 0.0])
            hand.frame = _relaxed_hand(fdir, palm, side)
        tips = hand_prims(B, P, wr, hand.frame, hand, side, skin)
        info[f"tips_{side}"] = tips

    # ---------------- 腿
    for side, sg in (("R", 1), ("L", -1)):
        hip = fr["root"] + R0 @ np.array([sg * P.hip_w, 0, -0.04])
        at = pose.ankle.get(side, dl[f"ankle_{side}"])
        kp = pose.knee_pole.get(side, dl[f"kpole_{side}"])
        kn, an = two_bone_ik(hip, at, P.thigh, P.shin, kp)
        info[f"hip_{side}"], info[f"knee_{side}"], info[f"ankle_{side}"] = hip, kn, an
        B.begin()
        rh, rk, ra_ = P.leg_r
        B.cone(hip, kn, rh, rk, skin, k=0.03)
        B.ell(hip + (kn - hip) * 0.35, (rh * 1.02, rh * 1.0, np.linalg.norm(kn - hip) * 0.36), _axis_frame(kn - hip), skin, k=0.03)
        B.cone(kn, an, rk, ra_, skin, k=0.02)
        B.ell(kn + (an - kn) * 0.3, (rk * 1.1, rk * 1.18, np.linalg.norm(an - kn) * 0.28), _axis_frame(an - kn), skin, k=0.02)  # 小腿肚
        tdir = (kn - hip) / (np.linalg.norm(kn - hip) + 1e-9)
        sdir = (an - kn) / (np.linalg.norm(an - kn) + 1e-9)
        if outfit == "xiaoman":
            B.capcone(hip - tdir * 0.04, hip + tdir * 0.15, rh + 0.014, rh + 0.013, "shorts_xm", rnd=0.006, k=0.03)
        else:
            B.capcone(hip - tdir * 0.04, kn, rh + 0.03, rk + 0.032, "trousers_nn", rnd=0.006, k=0.03)
            B.capcone(kn - tdir * 0.01, an - sdir * 0.02, rk + 0.032, ra_ + 0.028, "trousers_nn", rnd=0.006, k=0.035)
        # 脚
        fd = np.asarray(pose.foot_dir.get(side, R0 @ np.array([sg * 0.12, 1.0, 0.0])), float)
        fd = fd - np.array([0, 0, fd[2]])
        fd /= np.linalg.norm(fd) + 1e-9
        F = frame_from(fd, [0, 0, 1])
        heel = an + np.array([0, 0, -0.035]) - fd * 0.03
        toe = heel + fd * P.foot_len
        info[f"toe_{side}"] = toe
        if outfit == "xiaoman":
            B.cone(an, heel + fd * 0.01 + np.array([0, 0, 0.012]), ra_ * 1.05, 0.025, skin, k=0.02)
            B.rbox((heel + toe) / 2 + np.array([0, 0, 0.004]), (0.035, P.foot_len * 0.5, 0.017), F, 0.016, skin, k=0.02)
            for k_ in range(5):
                tp = toe + F[:, 0] * (0.024 - k_ * 0.012) - fd * (0.004 * abs(k_ - 1)) + np.array([0, 0, 0.0])
                B.cone(tp - fd * 0.01, tp, 0.0068 if k_ else 0.0085, 0.006 if k_ else 0.0075, skin, k=0.006)
        else:
            B.rbox((heel + toe) / 2 + np.array([0, 0, 0.012]), (0.042, P.foot_len * 0.5, 0.026), F, 0.024, "shoes_nn", k=0.02, layer=1)
            B.rbox((heel + toe) / 2 + np.array([0, 0, -0.012]), (0.043, P.foot_len * 0.51, 0.008), F, 0.007, "sole", k=0.0, layer=1)
        B.end(0.02)
    chars, groups = B.arrays()
    return chars, groups, info


def _axis_frame(axis):
    """以 axis 为 z 轴的旋转矩阵（列 = x, y, z）。"""
    z = np.asarray(axis, float)
    z /= np.linalg.norm(z) + 1e-12
    h = np.array([0, 0, 1.0]) if abs(z[2]) < 0.9 else np.array([1.0, 0, 0])
    x = np.cross(h, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def _relaxed_hand(fdir, palm, side):
    y = np.asarray(fdir, float)
    y /= np.linalg.norm(y)
    z = np.asarray(palm, float)
    z = z - y * (z @ y)
    z /= np.linalg.norm(z)
    x = np.cross(y, z)
    return np.stack([x, y, z], axis=1)


def hair_prims(B, P, pose, hc, Rh):
    off = np.asarray(pose.hair_offset, float)
    hr_ = P.head_r
    if P.name == "xiaoman":
        m = "hair_xm"
        # 头发往后扎成一个高马尾：整头发盖 − 脸的区域（剪出发际线），刘海几绺，马尾（三节，会甩）
        B.ell(hc + Rh @ np.array([0, -0.008, 0.026]) + off * 0.2, (hr_[0] + 0.005, hr_[1] + 0.008, hr_[2] + 0.007), Rh, m, k=0.02, layer=2)
        B.ell(hc + Rh @ np.array([0, 0.074, -0.050]), (0.090, 0.074, 0.090), Rh, m, k=0.012, layer=3)
        for (x, dx, ln) in ((-0.046, -0.006, 0.040), (-0.020, -0.002, 0.044), (0.008, 0.003, 0.046), (0.034, 0.006, 0.042), (0.054, 0.006, 0.030)):
            top_ = hc + Rh @ np.array([x, 0.086 - abs(x) * 0.35, 0.072])
            tip = hc + Rh @ np.array([x + dx, 0.100 - abs(x) * 0.45, 0.072 - ln])
            B.cone(top_, tip, 0.012, 0.003, m, k=0.008, layer=5)
        tie = hc + Rh @ np.array([0, -0.088, 0.070])
        B.ell(tie, (0.020, 0.018, 0.018), Rh, m, k=0.015, layer=2)
        B.cone(tie, tie, 0.0135, 0.0135, "paper_red", k=0.0, layer=2)   # 红色发圈
        # 马尾：根部跟着头，越往梢越受重力往下垂（世界坐标的"下"），再加上弹簧算出的甩动
        pt = np.asarray(pose.ponytail, float)
        down = np.array([0, 0, -1.0])
        back = Rh @ np.array([0, -1.0, 0.25])
        back /= np.linalg.norm(back)

        def seg_dir(w_g):
            d = back * (1 - w_g) + down * w_g
            return d / np.linalg.norm(d)
        p1 = tie + seg_dir(0.15) * 0.036 + pt * 0.35
        p2 = p1 + seg_dir(0.65) * 0.048 + pt * 0.65
        p3 = p2 + seg_dir(0.92) * 0.050 + pt * 1.0
        B.cone(tie, p1, 0.016, 0.022, m, k=0.012, layer=2)
        B.cone(p1, p2, 0.022, 0.017, m, k=0.012, layer=2)
        B.cone(p2, p3, 0.017, 0.004, m, k=0.010, layer=2)
        # 呆毛：从头顶翘起的一小撮，会摆
        base = hc + Rh @ np.array([0.012, 0.0, 0.124])
        cx, cy = pose.cowlick
        p1 = base + Rh @ np.array([0.004 + cx * 0.5, 0.012 + cy * 0.5, 0.022])
        p2 = p1 + Rh @ np.array([0.010 + cx, 0.026 + cy, 0.012])
        B.cone(base, p1, 0.0080, 0.0050, m, k=0.008, layer=2)
        B.cone(p1, p2, 0.0050, 0.0020, m, k=0.004, layer=2)
    else:
        m = "hair_nn"
        # 灰白短发，往后梳，别在耳后；发际线在额头上方
        hr_ = P.head_r
        B.ell(hc + Rh @ np.array([0, -0.010, 0.040]) + off * 0.2, (hr_[0] + 0.004, hr_[1] + 0.006, hr_[2] - 0.008), Rh, m, k=0.02, layer=2)
        B.ell(hc + Rh @ np.array([0, 0.052, 0.064]) + off * 0.2, (0.078, 0.036, 0.022), Rh @ rx(30), m, k=0.03, layer=2)
        B.ell(hc + Rh @ np.array([0, -0.062, -0.018]) + off * 0.4, (0.076, 0.046, 0.060), Rh, m, k=0.03, layer=2)
        for sg in (1, -1):
            B.ell(hc + Rh @ np.array([sg * 0.074, -0.030, -0.006]) + off * 0.5, (0.024, 0.052, 0.050), Rh, m, k=0.02, layer=2)
        # 发卡（黑色细条）
        B.cone(hc + Rh @ np.array([0.082, 0.004, 0.044]), hc + Rh @ np.array([0.080, -0.040, 0.050]), 0.0032, 0.0032,
               "hair_xm", k=0.0, layer=2)
