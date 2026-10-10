"""针孔相机。"""
import math
from dataclasses import dataclass

import numpy as np


@dataclass
class Camera:
    pos: tuple
    target: tuple
    hfov_deg: float = 50.0
    roll_deg: float = 0.0

    def basis(self):
        o = np.asarray(self.pos, float)
        f = np.asarray(self.target, float) - o
        f /= np.linalg.norm(f)
        up = np.array([0.0, 0.0, 1.0])
        r = np.cross(f, up)
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if self.roll_deg:
            a = math.radians(self.roll_deg)
            r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
        return o, f, r, u

    @property
    def tan_half(self):
        return math.tan(math.radians(self.hfov_deg) / 2)

    def project(self, pts, W, H):
        """世界坐标 -> 像素坐标 (x, y, depth)。pts: (...,3)"""
        o, f, r, u = self.basis()
        p = np.asarray(pts, float) - o
        z = p @ f
        x = (p @ r) / z / self.tan_half
        y = (p @ u) / z / self.tan_half * (W / H)
        return np.stack([(x + 1) * 0.5 * W, (1 - y) * 0.5 * H, z], axis=-1)

    @staticmethod
    def from_setup(setup):
        return Camera(setup.pos, setup.target, setup.hfov_deg)
