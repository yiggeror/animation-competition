"""联合双边滤波：按法线、深度、物体编号引导，去掉面光源采样的颗粒，保住物体边缘。"""
import math

import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True, fastmath=True)
def joint_bilateral(X, N, T, OBJ, keep, radius, sigma_s, sigma_n, sigma_t):
    """X: (H,W,C)；keep[h,w]=True 的像素不滤（比如床单，影子边缘要锐利）。"""
    H, W, C = X.shape
    out = np.empty_like(X)
    inv2s = 1.0 / (2 * sigma_s * sigma_s)
    for j in prange(H):
        for i in range(W):
            if keep[j, i]:
                for c in range(C):
                    out[j, i, c] = X[j, i, c]
                continue
            n0x, n0y, n0z = N[j, i, 0], N[j, i, 1], N[j, i, 2]
            t0 = T[j, i]
            o0 = OBJ[j, i]
            acc = np.zeros(C)
            wsum = 0.0
            for dj in range(-radius, radius + 1):
                jj = j + dj
                if jj < 0 or jj >= H:
                    continue
                for di in range(-radius, radius + 1):
                    ii = i + di
                    if ii < 0 or ii >= W:
                        continue
                    if OBJ[jj, ii] != o0 or keep[jj, ii]:
                        continue
                    w = math.exp(-(di * di + dj * dj) * inv2s)
                    dn = n0x * N[jj, ii, 0] + n0y * N[jj, ii, 1] + n0z * N[jj, ii, 2]
                    if dn < 0.8:
                        continue
                    w *= math.exp(-(1 - dn) / sigma_n)
                    dt = abs(T[jj, ii] - t0) / max(t0, 1e-3)
                    w *= math.exp(-dt * dt / (sigma_t * sigma_t))
                    for c in range(C):
                        acc[c] += X[jj, ii, c] * w
                    wsum += w
            for c in range(C):
                out[j, i, c] = acc[c] / wsum if wsum > 0 else X[j, i, c]
    return out


def denoise_buffers(buf, keep_mats=(), radius=4):
    """对每个光源的直接光、间接光、遮蔽做滤波。"""
    H, W = buf.ID.shape
    obj = np.where(buf.CP >= 0, 100000 + buf.CP, buf.ID).astype(np.int64)
    keep = np.isin(buf.MAT, np.array(keep_mats, dtype=np.int64)) if keep_mats else np.zeros((H, W), bool)
    nl = buf.E.shape[2]
    E = buf.E.reshape(H, W, nl * 3).astype(np.float64)
    E = joint_bilateral(E, buf.N, buf.T, obj, keep, radius, radius * 0.6, 0.08, 0.02)
    buf.E = E.reshape(H, W, nl, 3).astype(np.float32)
    X = np.concatenate([buf.EB.astype(np.float64), buf.AO[..., None].astype(np.float64)], axis=2)
    X = joint_bilateral(X, buf.N, buf.T, obj, np.zeros((H, W), bool), radius + 2, (radius + 2) * 0.6, 0.15, 0.03)
    buf.EB = X[..., :3].astype(np.float32)
    buf.AO = X[..., 3].astype(np.float32)
    return buf
