"""人物身上的线和花纹：发丝、领口、纽扣、T 恤图案、碎花。都贴在身体局部坐标上，跟着人动。"""
import math

import numpy as np

from .materials import M
from .textures import vnoise


def _cov(d, aa):
    return np.clip(0.5 - d / aa, 0, 1)


def layers(buf, chars, faces, aa_scale=1.0):
    """返回 dict：hair（发丝线）、cloth_line（领口等）、button（纽扣）、print_light（浅色印花）。"""
    H, W = buf.MAT.shape
    out = {k: np.zeros((H, W)) for k in ("hair", "cloth_line", "button", "print_light")}
    if chars is None or chars.shape[0] == 0:
        return out
    CP = buf.CP
    has = CP >= 0
    grp = np.where(has, chars[np.maximum(CP, 0), 2], -1)
    layer = np.where(has, chars[np.maximum(CP, 0), 23], -1)
    for who, info, expr, g_head in faces:
        m_hair = has & (layer == 2) & (grp == g_head)
        depth = np.median(buf.T[has]) if has.any() else 1.0
        aa = depth * 0.9 / W * aa_scale
        if m_hair.any():
            q = (buf.P[m_hair] - info["head_c"]) @ info["head_R"]
            if who == "xiaoman":
                c0 = np.array([0.01, -0.012, 0.118])
                v = q - c0
                phi = np.arctan2(v[:, 0], v[:, 1])
                r = np.sqrt((v ** 2).sum(-1))
                nz = vnoise(q * 60.0, 3) * 0.9
                f = np.abs(np.sin(phi * 17 + nz))
                lines = (f < 0.10 + 0.04 * np.sin(phi * 5)) * np.clip((r - 0.03) / 0.03, 0, 1)
                # 刘海：竖向的几道
                bang = (q[:, 1] > 0.05) & (q[:, 2] > 0.02)
                fb = np.abs(np.sin(q[:, 0] * 160 + nz))
                lines = np.where(bang, (fb < 0.12) * 1.0, lines)
            else:
                psi = np.arctan2(q[:, 0], q[:, 2] + 0.02)
                nz = vnoise(q * 50.0, 5) * 0.8
                f = np.abs(np.sin(psi * 20 + nz + q[:, 1] * 8))
                lines = (f < 0.13) * 1.0
            out["hair"][m_hair] = lines * 0.85
        cloth_mat = M("tshirt_xm") if who == "xiaoman" else M("blouse_nn")
        m_cl = has & (buf.MAT == cloth_mat)
        if not m_cl.any():
            continue
        q = (buf.P[m_cl] - info["chest_c"]) @ info["chest_R"]
        nq = (info["neck_c"] - info["chest_c"]) @ info["chest_R"]
        rel = q - nq
        rad = np.sqrt(rel[:, 0] ** 2 + rel[:, 1] ** 2)
        if who == "xiaoman":
            ring = np.abs(rad - 0.050) - 0.0035
            band = (rel[:, 2] > -0.05) & (rel[:, 2] < 0.02)
            out["cloth_line"][m_cl] = _cov(ring, aa) * band
            # T 恤胸前：一颗白色的五角星（原创图案）
            front = q[:, 1] > 0
            x, z = q[:, 0] + 0.02, q[:, 2] - 0.0
            ang = np.arctan2(z, x)
            rr = np.sqrt(x * x + z * z)
            star_r = 0.026 * (0.55 + 0.45 * np.cos(5 * (ang - math.pi / 2)) ** 1) ** 1.0
            k = (0.5 + 0.5 * np.cos(5 * (ang - math.pi / 2)))
            star_r = 0.012 + 0.016 * k ** 2
            out["print_light"][m_cl] = _cov(rr - star_r, aa) * front
        else:
            front = q[:, 1] > 0
            # 翻领：从两侧颈根到胸口的 V
            x, z = q[:, 0], q[:, 2] - nq[2]
            v_line = np.abs(np.abs(x) - (0.055 + z * 0.6)) - 0.003
            in_v = (z < -0.0) & (z > -0.085)
            collar = _cov(v_line, aa) * in_v * front
            ring = (np.abs(rad - 0.056) - 0.003)
            collar = np.maximum(collar, _cov(ring, aa) * (rel[:, 2] > -0.03) * (rel[:, 2] < 0.02))
            out["cloth_line"][m_cl] = collar
            # 纽扣：前襟一排
            bt = np.full(len(x), 1e9)
            for bz in (-0.095, -0.145, -0.195, -0.245):
                bt = np.minimum(bt, np.sqrt((x - 0.004) ** 2 + (z - bz) ** 2) - 0.0055)
            out["button"][m_cl] = _cov(bt, aa) * front
            # 前襟线
            out["cloth_line"][m_cl] = np.maximum(out["cloth_line"][m_cl], _cov(np.abs(x + 0.004) - 0.0012, aa) * front * (z < -0.08))
    return out
