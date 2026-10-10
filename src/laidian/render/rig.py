"""骨架数学：旋转、正向运动学、两段式反向运动学、手指。

人物局部坐标：x = 人物的右边，y = 前方，z = 上。
"""
import math

import numpy as np


def rx(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler(x=0.0, y=0.0, z=0.0):
    """x = 前屈/低头（正数向前），y = 向右侧倾，z = 向左转身。先 x、再 y、再 z。"""
    return rz(z) @ ry(y) @ rx(-x)


def axis_angle(axis, deg):
    a = np.asarray(axis, float)
    a = a / (np.linalg.norm(a) + 1e-12)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def frame_from(y_axis, z_hint):
    """以 y_axis 为主轴、z_hint 为次轴构造正交旋转矩阵（列 = x, y, z）。"""
    y = np.asarray(y_axis, float)
    y = y / (np.linalg.norm(y) + 1e-12)
    z = np.asarray(z_hint, float)
    z = z - y * (z @ y)
    nz = np.linalg.norm(z)
    if nz < 1e-6:
        z = np.array([0, 0, 1.0]) if abs(y[2]) < 0.9 else np.array([1.0, 0, 0])
        z = z - y * (z @ y)
        nz = np.linalg.norm(z)
    z = z / nz
    x = np.cross(y, z)
    return np.stack([x, y, z], axis=1)


def two_bone_ik(a, target, l1, l2, pole):
    """肩 a、目标 target、上下段长度、肘/膝指向 pole（世界坐标里的一个点）。返回中间关节位置和实际末端。
    关节永远朝 pole 那一侧弯——手肘、膝盖不会反折。"""
    a = np.asarray(a, float)
    t = np.asarray(target, float)
    d = t - a
    dist = np.linalg.norm(d)
    dist_c = min(max(dist, abs(l1 - l2) + 1e-4), l1 + l2 - 1e-4)
    dirv = d / (dist + 1e-12)
    end = a + dirv * dist_c
    cos_a = (l1 * l1 + dist_c * dist_c - l2 * l2) / (2 * l1 * dist_c)
    cos_a = min(max(cos_a, -1.0), 1.0)
    sin_a = math.sqrt(1 - cos_a * cos_a)
    p = np.asarray(pole, float) - a
    p = p - dirv * (p @ dirv)
    pn = np.linalg.norm(p)
    if pn < 1e-6:
        p = np.cross(dirv, [0, 0, 1.0])
        pn = np.linalg.norm(p)
    p /= pn
    mid = a + dirv * (l1 * cos_a) + p * (l1 * sin_a)
    return mid, end


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t, kind="inout"):
    t = min(max(t, 0.0), 1.0)
    if kind == "in":
        return t * t * t
    if kind == "out":
        return 1 - (1 - t) ** 3
    if kind == "linear":
        return t
    return t * t * (3 - 2 * t) if kind == "smooth" else (4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2)
