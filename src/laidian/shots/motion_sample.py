"""动态小样（4 秒）：第 6 场鹤亮相，床单正面（B 机位，镜头慢慢推近）。

奶奶在床单后面把鹤从灯前送到床单上：皮影离床单远时影子大而虚，贴上后小而清楚（光线追踪算出来的，不是模糊滤镜）；
头签带着脖子抬起来；没装签子的鹤腿靠惯性摆动。小满坐在左下角，一开始抱着胳膊，影子变清楚时身子往前探、胳膊松开。
同时检查画风合成在镜头运动时是否稳定（不闪、不游）。

用法：python -m laidian.shots.motion_sample OUT_DIR [--w 1280 --h 720 --ss 2 --fps 24 --styles lantern,woodcut,silk]
"""
import argparse
import math
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image

from .. import anim, layout as L
from ..render import character as C
from ..render import frame, puppets as PP, rt, room, sheetglow
from ..render import lighting_states as LS
from ..render.camera import Camera
from ..render.materials import M
from .style_samples import STYLES, PuppetAssets, merge_chars, place_grip, rod_point

ROD = 0.55
DUR = 4.0


def crane_tracks():
    """鹤：身体在床单平面上的位置（米）、离床单的距离、身体角度；头相对身体的位置（毫米，皮影局部坐标）。"""
    # 一开始鹤在灯前 0.40 米（离灯 0.30 米）：影子放大约 2.3 倍，火苗和玻璃罩把边缘晕开；
    # 放大中心是马灯，所以鹤要靠近灯的高度举着，影子才落在床单中间。
    root = anim.Track([(0.0, (1.22, 1.40)), (0.8, (1.20, 1.37), "inout"), (2.1, (1.03, 1.31), "out"),
                       (2.5, (1.03, 1.30), "inout"), (4.0, (1.04, 1.31), "inout")])
    dist = anim.Track([(0.0, 0.40), (0.8, 0.38, "inout"), (2.1, 0.004, "out"), (4.0, 0.004)])
    body_ang = anim.Track([(0.0, -0.10), (0.8, -0.14, "inout"), (2.1, 0.08, "out"), (2.6, 0.03, "inout"), (4.0, 0.05)])
    head = anim.Track([(0.0, (150, 110)), (0.8, (140, 92), "inout"), (2.2, (168, 196), "inout"),
                       (2.9, (182, 238), "out"), (3.4, (178, 228), "inout"), (4.0, (180, 232), "inout")])
    head_ang = anim.Track([(0.0, -0.9), (2.2, -0.6), (2.9, -0.30, "out"), (4.0, -0.38)])
    return root, dist, body_ang, head, head_ang


def build_frame(assets, t, state):
    root_t, dist_t, bang_t, head_t, hang_t = state["tracks"]
    dt = 1.0 / state["fps"]
    rx, rz = root_t(t)
    dist = float(dist_t(t))
    bang = float(bang_t(t))
    pose = PP.Pose(root_xz=(rx, rz), facing=1, dist=dist, root_angle=bang, angles={})
    # 脖子：从身体铆点到头的位置，FABRIK
    base = np.array([84.0, 32.0])
    ca, sa = math.cos(bang), math.sin(bang)
    base_w = np.array([ca * base[0] - sa * base[1], sa * base[0] + ca * base[1]])
    hp = np.asarray(head_t(t), float)
    hp_w = np.array([ca * hp[0] - sa * hp[1], sa * hp[0] + ca * hp[1]])
    angs, pts = PP_neck(base_w, bang + 1.0, hp_w, state)
    # 链的角度是相对的：第一节相对身体（基准方向 bang+1.0），之后每节相对上一节
    pose.angles["neck0"] = 1.0 + angs[0]
    for k in range(1, PP.N_NECK):
        pose.angles[f"neck{k}"] = angs[k]
    total = bang + pose.angles["neck0"] + sum(angs[1:])
    pose.angles["head"] = (bang + float(hang_t(t))) - total
    # 腿：摆
    hip = np.array([rx, rz])
    prev = state.get("hip_prev")
    vel = (hip - prev) / dt if prev is not None else np.zeros(2)
    acc = (vel - state.get("hip_vel", np.zeros(2))) / dt if prev is not None else np.zeros(2)
    state["hip_prev"] = hip
    state["hip_vel"] = vel
    for side, pend_name in (("near", "pend_near"), ("far", "pend_far")):
        p = state[pend_name]
        th = p.step(bang, acc, dt)
        pose.angles[f"tibia_{side}"] = th
        pose.angles[f"tarsus_{side}"] = -th * 0.4 + (0.05 if side == "near" else -0.03)
        pose.angles[f"foot_{side}"] = -th * 0.3
    return pose


def PP_neck(base_w, base_ang, head_w, state):
    angs, pts = anim.neck_chain(base_w, base_ang, head_w, PP.N_NECK, PP.NECK_LEN, prev=state.get("neck_pts"))
    state["neck_pts"] = pts
    return angs, pts


def nainai_pose(t, hand_body, hand_head, body_pt, head_pt, state):
    Pn = C.NAINAI
    nb = L.MARKS["nainai_backstage"]
    lift = float(anim.Track([(0.0, 0.0), (0.8, -0.2), (2.1, 1.0, "out"), (4.0, 1.0)])(t))
    lean = 3.0 + 5.0 * lift
    breath = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.6)
    pose = C.CharPose(root=(nb.x, nb.y + 0.03 - 0.03 * lift, Pn.hip_h - 0.012 * (1 - lift)), yaw=180.0, lean=(lean, 0.0),
                      spine2=(2 + 2 * lift, 0, -6), neck=(4 - 3 * lift, 0, 2), head=(6 - 10 * lift, -4, 10 - 4 * lift),
                      breath=breath)
    wR, hR = place_grip(Pn, hand_head, head_pt, "R", (-0.2, 0.3, -1.0))
    wL, hL = place_grip(Pn, hand_body, body_pt, "L", (0.2, 0.3, -1.0))
    pose.wrist = {"R": wR, "L": wL}
    pose.hands = {"R": hR, "L": hL}
    pose.elbow_pole = {"R": np.array([nb.x - 0.5, nb.y + 0.4, 0.5]), "L": np.array([nb.x + 0.5, nb.y + 0.4, 0.5])}
    pose.ankle = {"R": (nb.x - 0.09, nb.y + 0.05, 0.08), "L": (nb.x + 0.10, nb.y - 0.03, 0.08)}
    pose.knee_pole = {"R": (nb.x - 0.1, nb.y - 1.0, 0.5), "L": (nb.x + 0.1, nb.y - 1.0, 0.5)}
    pose.foot_dir = {"R": (0.1, -1, 0), "L": (-0.15, -1, 0)}
    smile = float(anim.Track([(0.0, 0.1), (2.3, 0.2), (3.0, 0.8, "out"), (4.0, 0.75)])(t))
    blink = 1.0 if 1.45 < t < 1.55 or 3.55 < t < 3.63 else 0.0
    pose.expr = dict(eye_smile=smile, mouth_smile=0.2 + 0.5 * smile, blink=blink, look=(0.2, 0.3))
    return pose


def xiaoman_pose(t):
    """小满：坐板凳，背对镜头。先抱着胳膊缩着、低着头；影子变清楚时坐直、伸脖子往上看，胳膊松开。
    背影里能读出来的是头和肩膀的高度变化，所以动作主要放在坐直上。"""
    P = C.XIAOMAN
    st_x = L.MARKS["xiaoman_audience"]
    root = np.array([st_x.x, st_x.y, 0.30 + 0.075])
    lean_in = float(anim.Track([(0.0, 0.0), (1.3, 0.0), (2.5, 1.08, "out"), (3.0, 0.95, "inout"), (4.0, 1.0, "inout")])(t))
    unfold = float(anim.Track([(0.0, 0.0), (1.7, 0.0), (2.8, 1.0, "inout"), (4.0, 1.0)])(t))
    breath = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.0)
    pose = C.CharPose(root=tuple(root), yaw=0.0, lean=(-4.0 + 9.0 * lean_in, 0.0), spine2=(12 - 15 * lean_in, 0, 3),
                      neck=(10 - 16 * lean_in, 0, 0), head=(8 - 18 * lean_in, 4 * lean_in, 2), breath=breath,
                      cowlick=(0.004 * math.sin(t * 3.1), 0.0))
    fr = C.body_frames(P, pose)
    R2 = fr["R2"]
    chest = fr["s2"] + R2 @ np.array([0, 0.11, -0.02])
    # 抱胳膊：两只手腕都压在胸前；松开：右手落到右膝上，左手落到左腿上
    wR0 = chest + R2 @ np.array([-0.07, 0.03, -0.05])
    wL0 = chest + R2 @ np.array([0.07, 0.04, -0.03])
    wR1 = root + np.array([0.11, 0.24, 0.07])
    wL1 = root + np.array([-0.10, 0.20, 0.03])
    pose.wrist = {"R": wR0 + (wR1 - wR0) * unfold, "L": wL0 + (wL1 - wL0) * unfold}
    pose.elbow_pole = {"R": chest + R2 @ np.array([0.40, 0.0, -0.4]), "L": chest + R2 @ np.array([-0.40, 0.0, -0.4])}
    pose.ankle = {"R": (root[0] + 0.10, root[1] + 0.30, 0.075), "L": (root[0] - 0.09, root[1] + 0.26, 0.075)}
    pose.knee_pole = {"R": (root[0] + 0.15, root[1] + 1.0, 0.5), "L": (root[0] - 0.15, root[1] + 1.0, 0.5)}
    blink = 1.0 if 0.9 < t < 1.0 else 0.0
    pose.expr = dict(eye_open=0.85 + 0.35 * lean_in, mouth_open=0.4 * lean_in, brow=-0.3 + 0.9 * lean_in,
                     look=(0.0, 0.5), blink=blink)
    return pose


def camera(t):
    """B 机位，4 秒里沿视线推近 0.15 米。"""
    cs = L.CAMERAS[1]
    pos0 = np.array(cs.pos, float)
    tgt = np.array(cs.target, float)
    d = (tgt - pos0) / np.linalg.norm(tgt - pos0)
    push = float(anim.Track([(0.0, 0.0), (4.0, 0.15, "inout")])(t))
    return Camera(tuple(pos0 + d * push), tuple(tgt), cs.hfov_deg)


def setup(assets, t, state):
    st = room.RoomState(sheet_hung=True, tv_on=False, textures=assets.room_tex)
    pl = room.build(st)
    lp = L.LAMP_STAGE
    LS.lamp_geometry(pl, (lp.x, lp.y, lp.z), hang_z=L.LAMP_PURLIN_Z)
    cpose = build_frame(assets, t, state)
    body_pt = rod_point(cpose, PP.CRANE_RIG, "body", (8, 6))
    head_pt = rod_point(cpose, PP.CRANE_RIG, "head", (16, 2))
    # 签子：刚性，长 0.55 米；方向朝奶奶手的方向（往后、往下一点）
    d_body = np.array([-0.06, 0.92, -0.38])
    d_head = np.array([0.02, 0.90, -0.42])
    hand_body = body_pt + d_body / np.linalg.norm(d_body) * ROD
    hand_head = head_pt + d_head / np.linalg.norm(d_head) * ROD
    PP.add_puppet(pl, PP.CRANE_RIG, assets.cp, assets.ids("c"), cpose, L.WIRE_Y, M("wood_raw"), "crane",
                  rods=[("body", (8, 6), hand_body), ("head", (16, 2), hand_head)], rod_mat=M("wood_raw"))
    scene = rt.Scene(pl, assets.A, assets.R)
    xpose = xiaoman_pose(t)
    c1, g1, info1 = C.build(C.XIAOMAN, xpose, "xiaoman")
    npose = nainai_pose(t, hand_body, hand_head, body_pt, head_pt, state)
    c2, g2, info2 = C.build(C.NAINAI, npose, "nainai")
    chars, groups, faces = merge_chars([(c1, g1), (c2, g2)],
                                       [("xiaoman", info1, xpose.expr, 0), ("nainai", info2, npose.expr, None)])
    lights = LS.lamp_lights((lp.x, lp.y, lp.z), t) + [LS.moon_light(0.6)]
    names = ["lamp_core", "lamp_globe", "moon"]
    glow = sheetglow.glow_lights(scene, lights, chars, groups)
    lights = lights + glow
    names += [f"sheet{k}" for k in range(len(glow))]
    cam = camera(t)
    ctx = dict(exposure=2.4, chars=chars, faces=faces, t=t, cam=cam,
               sources=[dict(kind="lamp", pos=(lp.x, lp.y, lp.z), intensity=0.6)])
    return scene, cam, lights, names, chars, groups, ctx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--styles", default="lantern,woodcut,silk")
    ap.add_argument("--frames", default="", help="只渲染这些帧（逗号分隔），用于检查")
    a = ap.parse_args()
    out = Path(a.out)
    styles = a.styles.split(",")
    for s in styles:
        (out / s).mkdir(parents=True, exist_ok=True)
    assets = PuppetAssets()
    state = dict(fps=a.fps, tracks=crane_tracks(), pend_near=anim.Pendulum(0.19, 0.0), pend_far=anim.Pendulum(0.19, 0.0))
    n = int(DUR * a.fps)
    only = {int(x) for x in a.frames.split(",")} if a.frames else None
    for f in range(n):
        t = f / a.fps
        scene, cam, lights, names, chars, groups, ctx = setup(assets, t, state)
        if only is not None and f not in only:
            continue
        t0 = time.time()
        pm = np.array([nm.startswith(("crane:", "turtle:")) and not nm.endswith(":rod") for nm in scene.names])
        buf = frame.render_ss(scene, cam, lights, names, a.w, a.h, ss=a.ss, chars=chars, groups=groups,
                              keep_mats=(M("sheet"),), vpl_n=24)
        ctx["extra"] = {"puppet_mask": np.where(buf.ID >= 0, pm[np.maximum(buf.ID, 0)], False)}
        for s in styles:
            img = STYLES[s](buf, scene, ctx)
            Image.fromarray(img).save(out / s / f"{f:04d}.png")
        print(f"frame {f}/{n} {time.time() - t0:.1f}s", flush=True)
    if only is None:
        for s in styles:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", str(out / s / "%04d.png"),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out / f"motion_{s}.mp4")], check=True)


if __name__ == "__main__":
    main()
