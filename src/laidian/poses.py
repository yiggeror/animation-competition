"""姿势库：手型和全身姿势（设计稿、动作测试、正片共用）。

所有姿势都用"目标点 + IK"表达：给出手腕、脚踝的位置和肘、膝的朝向，关节只会朝正确方向弯。
"""
import math

import numpy as np

from .render import character as C
from .render.rig import rz

F = C.FINGERS


# ---------------------------------------------------------------- 手型
def hand_preset(name):
    """返回 (curl dict, spread, thumb)。curl = 每根手指三节的弯曲角（度）。"""
    if name == "relaxed":
        return {f: (18 + 4 * i, 24 + 4 * i, 12) for i, f in enumerate(F)}, 5.0, (25, 12, 10, 8)
    if name == "fist":
        return {f: (82, 95, 62) for f in F}, 0.0, (40, 30, 40, 30)
    if name == "grip":            # 握签子：四指包住，拇指压在食指上
        return {f: (70, 88, 56) for f in F}, 2.0, (55, 25, 30, 20)
    if name == "pinch":           # 拇指和食指捏住（剥毛豆、捏签子尖、拉灯绳）
        c = {"index": (38, 58, 30), "middle": (52, 72, 40), "ring": (62, 80, 46), "pinky": (70, 86, 50)}
        return c, 3.0, (62, 18, 22, 16)
    if name == "point":
        c = {"index": (4, 6, 4), "middle": (78, 92, 58), "ring": (82, 94, 60), "pinky": (84, 96, 62)}
        return c, 2.0, (40, 30, 40, 25)
    if name == "open":
        return {f: (2, 4, 2) for f in F}, 12.0, (5, 2, 2, 2)
    if name == "dog":             # 一只手比狗：食指中指无名指并拢（狗嘴上颚），小指下垂（下颚），拇指翘起（耳朵）
        c = {"index": (6, 10, 8), "middle": (6, 10, 8), "ring": (10, 14, 10), "pinky": (55, 20, 10)}
        return c, -6.0, (-25, -10, 0, 0)
    if name == "dog_open":        # 狗张嘴：小指再往下
        c = {"index": (4, 8, 6), "middle": (4, 8, 6), "ring": (8, 12, 8), "pinky": (78, 24, 10)}
        return c, -6.0, (-30, -12, 0, 0)
    if name == "dog_bad":         # 第一次比得歪歪扭扭：手指散开、耳朵耷拉
        c = {"index": (14, 22, 16), "middle": (4, 6, 4), "ring": (24, 30, 20), "pinky": (35, 15, 8)}
        return c, 10.0, (10, 15, 20, 10)
    if name == "cupped":          # 拢着（护着火柴、捧东西）
        return {f: (30, 40, 25) for f in F}, 2.0, (40, 15, 15, 10)
    raise KeyError(name)


def hand(name, frame=None):
    c, s, t = hand_preset(name)
    return C.Hand(frame=frame, curl=c, spread=s, thumb=t)


def frame_from_dirs(fingers, palm, side="R"):
    """手的朝向：fingers = 手指方向，palm = 掌心朝向（世界坐标）。"""
    return C._relaxed_hand(np.asarray(fingers, float), np.asarray(palm, float), side)


# ---------------------------------------------------------------- 全身姿势
def _place(P, pose, local_pts):
    """把人物局部坐标（相对骨盆、按朝向旋转）的点换成世界坐标。"""
    R = rz(pose.yaw)
    root = np.asarray(pose.root, float)
    return {k: root + R @ np.asarray(v, float) for k, v in local_pts.items()}


def standing(P, x=0.0, y=0.0, yaw=0.0, expr=None):
    pose = C.CharPose(root=(x, y, P.hip_h), yaw=yaw, breath=0.5, expr=expr or {})
    pts = _place(P, pose, {"aR": (P.hip_w + 0.01, 0.02, -P.hip_h + 0.075), "aL": (-P.hip_w - 0.01, -0.02, -P.hip_h + 0.075),
                           "kR": (0.1, 0.8, -0.2), "kL": (-0.1, 0.8, -0.2)})
    pose.ankle = {"R": pts["aR"], "L": pts["aL"]}
    pose.knee_pole = {"R": pts["kR"], "L": pts["kL"]}
    R = rz(yaw)
    pose.foot_dir = {"R": R @ np.array([0.15, 1, 0]), "L": R @ np.array([-0.15, 1, 0])}
    return pose


def sitting_stool(P, x, y, seat_h, yaw=0.0, arms="crossed", expr=None, lean=4.0):
    """坐在矮凳上。arms: crossed（抱胳膊）/ knees（手放膝上）/ beans（剥毛豆）"""
    root_h = seat_h + 0.075
    pose = C.CharPose(root=(x, y, root_h), yaw=yaw, lean=(lean, 0.0), breath=0.4, expr=expr or {})
    R = rz(yaw)
    root = np.asarray(pose.root, float)
    knee_fwd = (P.thigh * 0.92)
    shin_down = root_h - 0.075
    pose.ankle = {"R": root + R @ np.array([0.10, knee_fwd + 0.03, -shin_down]),
                  "L": root + R @ np.array([-0.10, knee_fwd - 0.01, -shin_down])}
    pose.knee_pole = {"R": root + R @ np.array([0.2, 1.0, 0.4]), "L": root + R @ np.array([-0.2, 1.0, 0.4])}
    pose.foot_dir = {"R": R @ np.array([0.2, 1, 0]), "L": R @ np.array([-0.2, 1, 0])}
    fr = C.body_frames(P, pose)
    R2 = fr["R2"]
    chest = fr["s2"] + R2 @ np.array([0, 0.10, -0.02])
    if arms == "crossed":
        pose.wrist = {"R": chest + R2 @ np.array([-0.075, 0.02, -0.05]), "L": chest + R2 @ np.array([0.07, 0.035, -0.035])}
        pose.elbow_pole = {"R": chest + R2 @ np.array([0.4, 0.0, -0.4]), "L": chest + R2 @ np.array([-0.4, 0.0, -0.4])}
        pose.hands = {"R": hand("relaxed", frame_from_dirs(R2 @ np.array([-1, 0.1, 0.2]), R2 @ np.array([0, -1, 0]), "R")),
                      "L": hand("relaxed", frame_from_dirs(R2 @ np.array([1, 0.1, 0.1]), R2 @ np.array([0, -1, 0.2]), "L"))}
    elif arms == "knees":
        pose.wrist = {"R": root + R @ np.array([0.12, knee_fwd - 0.06, 0.06]), "L": root + R @ np.array([-0.12, knee_fwd - 0.08, 0.06])}
        pose.elbow_pole = {"R": root + R @ np.array([0.4, -0.3, 0.3]), "L": root + R @ np.array([-0.4, -0.3, 0.3])}
    elif arms == "beans":
        lap = root + R @ np.array([0.0, knee_fwd * 0.75, 0.05])
        pose.wrist = {"R": lap + R @ np.array([0.03, -0.02, 0.08]), "L": lap + R @ np.array([-0.04, 0.0, 0.07])}
        pose.elbow_pole = {"R": root + R @ np.array([0.4, -0.2, 0.2]), "L": root + R @ np.array([-0.4, -0.2, 0.2])}
        pose.hands = {"R": hand("pinch", frame_from_dirs(R @ np.array([-0.8, 0.3, 0.5]), R @ np.array([-0.3, 0, -1]), "R")),
                      "L": hand("cupped", frame_from_dirs(R @ np.array([0.7, 0.4, 0.4]), R @ np.array([0.2, 0, 1.0]), "L"))}
    return pose


def lying_phone(P, x, y, yaw=0.0, expr=None):
    """趴在竹席上玩手机：胸口撑在胳膊肘上，两手在面前举着手机。"""
    pose = C.CharPose(root=(x, y, 0.09), yaw=yaw, lean=(78.0, 0.0), spine1=(-10, 0, 0), spine2=(-14, 0, 0),
                      neck=(-24, 0, 0), head=(-6, 0, 0), breath=0.3, expr=expr or {})
    R = rz(yaw)
    root = np.asarray(pose.root, float)
    fr = C.body_frames(P, pose)
    phone = fr["s2"] + R @ np.array([0.0, 0.30, 0.02])
    phone[2] = 0.14
    pose.wrist = {"R": phone + R @ np.array([0.05, -0.03, 0.0]), "L": phone + R @ np.array([-0.05, -0.03, 0.0])}
    pose.elbow_pole = {"R": fr["s2"] + R @ np.array([0.3, 0.2, -0.6]), "L": fr["s2"] + R @ np.array([-0.3, 0.2, -0.6])}
    pose.hands = {"R": hand("relaxed", frame_from_dirs(R @ np.array([-0.3, 0.6, 0.3]), R @ np.array([-0.7, 0.2, 0.6]), "R")),
                  "L": hand("relaxed", frame_from_dirs(R @ np.array([0.3, 0.6, 0.3]), R @ np.array([0.7, 0.2, 0.6]), "L"))}
    # 腿：小腿翘起来晃
    pose.ankle = {"R": root + R @ np.array([0.10, -0.42, 0.22]), "L": root + R @ np.array([-0.08, -0.50, 0.05])}
    pose.knee_pole = {"R": root + R @ np.array([0.1, -0.3, -0.8]), "L": root + R @ np.array([-0.1, -0.3, -0.8])}
    pose.foot_dir = {"R": R @ np.array([0.0, -1, 0]), "L": R @ np.array([0.0, -1, 0])}
    return pose, phone


def flop(P, x, y, yaw=0.0, expr=None):
    """瘫在竹席上：仰面躺倒，一只手搭在额头上，一只手扇风。"""
    pose = C.CharPose(root=(x, y, 0.085), yaw=yaw, lean=(-86.0, 0.0), spine2=(-4, 0, 0), neck=(-6, 0, 0), head=(4, 10, 8),
                      breath=0.9, expr=expr or {})
    R = rz(yaw)
    fr = C.body_frames(P, pose)
    root = np.asarray(pose.root, float)
    # 仰面躺着：头朝人物局部的 -y，脚朝 +y；右手搭在额头上，左手摊开，右膝支起
    pose.wrist = {"R": fr["hc"] + R @ np.array([0.03, 0.04, 0.11]), "L": fr["s2"] + R @ np.array([-0.38, -0.02, 0.03])}
    pose.elbow_pole = {"R": fr["s2"] + R @ np.array([0.7, -0.1, 0.2]), "L": fr["s2"] + R @ np.array([-0.5, 0.4, 0.3])}
    pose.ankle = {"R": root + R @ np.array([0.13, 0.36, -0.03]), "L": root + R @ np.array([-0.13, 0.55, -0.03])}
    pose.knee_pole = {"R": root + R @ np.array([0.2, 0.2, 1.0]), "L": root + R @ np.array([-0.2, 0.3, 1.0])}
    pose.foot_dir = {"R": R @ np.array([0.2, 1, 0]), "L": R @ np.array([-0.3, 1, 0])}
    return pose


def reaching_up(P, x, y, yaw=0.0, target_h=1.95, expr=None):
    """踮脚够立柜顶（奶奶拿马灯）。"""
    pose = standing(P, x, y, yaw, expr)
    R = rz(yaw)
    root = np.array([x, y, P.hip_h + 0.04])
    pose.root = tuple(root)
    pose.lean = (-4.0, 0.0)
    pose.neck = (-12, 0, 0)
    pose.head = (-18, 0, 0)
    pose.wrist = {"R": root + R @ np.array([0.06, 0.28, target_h - root[2] - 0.03]),
                  "L": root + R @ np.array([-0.14, 0.18, 0.12])}
    pose.elbow_pole = {"R": root + R @ np.array([0.5, -0.2, 0.3]), "L": root + R @ np.array([-0.5, -0.2, 0.0])}
    pose.hands = {"R": hand("cupped", frame_from_dirs(R @ np.array([0, 0.4, 1]), R @ np.array([0, 1, 0]), "R"))}
    pose.ankle = {"R": root + R @ np.array([0.08, 0.02, -P.hip_h + 0.05 + 0.04]), "L": root + R @ np.array([-0.08, -0.04, -P.hip_h + 0.05 + 0.04])}
    return pose


def dog_shadow(P, x, y, yaw, hand_pos, open_=False, expr=None):
    """比手影小狗：右手比狗，左手托着手电（第 3 场）或空着。"""
    pose = standing(P, x, y, yaw, expr)
    R = rz(yaw)
    pose.lean = (6.0, 0.0)
    pose.wrist = {"R": np.asarray(hand_pos, float)}
    pose.elbow_pole = {"R": np.asarray(pose.root) + R @ np.array([0.5, -0.4, -0.2])}
    pose.hands = {"R": hand("dog_open" if open_ else "dog", frame_from_dirs(R @ np.array([0.2, 1, 0.1]), R @ np.array([-1, 0, -0.3]), "R"))}
    return pose
