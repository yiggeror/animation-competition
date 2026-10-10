"""动画工具：关键帧轨道、弹簧（跟随与惯性）、皮影的摆动和脖子链。"""
import math

import numpy as np

from .render.rig import ease


class Track:
    """关键帧轨道。keys: [(t, value, easing)]，easing 作用在"到达这一帧"的那一段。"""

    def __init__(self, keys):
        self.keys = sorted(keys, key=lambda k: k[0])

    def __call__(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return np.asarray(ks[0][1], float)
        if t >= ks[-1][0]:
            return np.asarray(ks[-1][1], float)
        for (t0, v0, *_), (t1, v1, *e) in zip(ks, ks[1:]):
            if t0 <= t <= t1:
                kind = e[0] if e else "inout"
                u = ease((t - t0) / max(t1 - t0, 1e-9), kind)
                return np.asarray(v0, float) + (np.asarray(v1, float) - np.asarray(v0, float)) * u
        return np.asarray(ks[-1][1], float)


class Spring:
    """阻尼弹簧：x 追 target，用来做头发、马尾、衣服的跟随和惯性。"""

    def __init__(self, x0, freq=3.0, damp=0.35):
        self.x = np.asarray(x0, float).copy()
        self.v = np.zeros_like(self.x)
        self.w = 2 * math.pi * freq
        self.z = damp

    def step(self, target, dt, sub=4):
        target = np.asarray(target, float)
        h = dt / sub
        for _ in range(sub):
            a = self.w * self.w * (target - self.x) - 2 * self.z * self.w * self.v
            self.v += a * h
            self.x += self.v * h
        return self.x


class Pendulum:
    """皮影上没装签子的部件（鹤腿、龟腿）：挂在铆点上，被身体带着摆。角度相对父部件。"""

    def __init__(self, length_m, rest=0.0, damp=1.6, stiff=6.0):
        self.L = length_m
        self.th = rest
        self.om = 0.0
        self.rest = rest
        self.damp = damp
        self.k = stiff      # 皮子铆点的摩擦和一点点弹性，让它回到自然垂下的角度

    def step(self, parent_angle, pivot_acc, dt, sub=8):
        """pivot_acc：铆点的加速度（世界二维，米/秒²）；重力向下。"""
        g = 9.81
        h = dt / sub
        for _ in range(sub):
            a_world = parent_angle + self.th - math.pi / 2   # 部件朝向（向下为 -π/2）
            # 绕铆点的角加速度：重力 + 惯性（铆点加速度的反向）
            ax, ay = pivot_acc
            torque = (-(g + ay) * math.cos(a_world) + ax * math.sin(a_world)) / self.L
            alpha = torque - self.damp * self.om - self.k * (self.th - self.rest)
            self.om += alpha * h
            self.th += self.om * h
        return self.th


def neck_chain(base, base_angle, head_pos, n, seg, prev=None, iters=20, max_bend=0.45):
    """鹤脖子：从身体上的铆点到头的铆点，一串 n 节，每节长 seg（毫米）。
    用 FABRIK 求各节位置，再换成相对角度（每节弯曲不超过 max_bend）。"""
    base = np.asarray(base, float)
    head_pos = np.asarray(head_pos, float)
    if prev is None:
        d = head_pos - base
        pts = np.array([base + d * (k / n) for k in range(n + 1)])
    else:
        pts = prev.copy()
    total = seg * n
    if np.linalg.norm(head_pos - base) > total:
        d = (head_pos - base) / np.linalg.norm(head_pos - base)
        head_pos = base + d * total * 0.999
    for _ in range(iters):
        pts[-1] = head_pos
        for k in range(n - 1, -1, -1):
            d = pts[k] - pts[k + 1]
            pts[k] = pts[k + 1] + d / (np.linalg.norm(d) + 1e-9) * seg
        pts[0] = base
        for k in range(n):
            d = pts[k + 1] - pts[k]
            pts[k + 1] = pts[k] + d / (np.linalg.norm(d) + 1e-9) * seg
    angs = []
    prev_a = base_angle
    for k in range(n):
        d = pts[k + 1] - pts[k]
        a = math.atan2(d[1], d[0])
        rel = (a - prev_a + math.pi) % (2 * math.pi) - math.pi
        rel = max(-max_bend, min(max_bend, rel))
        angs.append(rel)
        prev_a = prev_a + rel
    return angs, pts
