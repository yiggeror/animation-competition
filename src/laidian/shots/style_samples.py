"""画风样张：第 6 场鹤第一次亮相、第 10 场来电的一瞬间。

用法：python -m laidian.shots.style_samples OUT_DIR [--w 1920 --h 1080 --ss 2] [--styles lantern,woodcut,silk]
"""
import argparse
import math
import time
from pathlib import Path

import numpy as np
from PIL import Image

from .. import layout as L
from ..render import character as C
from ..render import frame, puppets as PP, rt, room, sheetglow
from ..render import lighting_states as LS
from ..render.camera import Camera
from ..render.materials import M
from ..render.rig import euler, rz
from .. import poses as PO
from ..render.styles import lantern, silk, woodcut

STYLES = {"lantern": lantern.compose, "woodcut": woodcut.compose, "silk": silk.compose}


# ---------------------------------------------------------------- 皮影资产
class PuppetAssets:
    def __init__(self, ppmm=5.0):
        self.cp = PP.crane_parts(ppmm)
        self.tp = PP.turtle_parts(ppmm)
        self.atlas = PP.Atlas()
        self.tex = {}
        for pre, parts in (("c", self.cp), ("t", self.tp)):
            for k, v in parts.items():
                self.tex[f"{pre}:{k}"] = self.atlas.add(v.trans)
                self.atlas.add(v.refl)
        from ..render import setdressing
        self.room_tex = setdressing.build_textures(self.atlas)
        self.A, self.R = self.atlas.build()

    def ids(self, pre):
        return {k[2:]: v for k, v in self.tex.items() if k.startswith(pre + ":")}


def crane_pose_debut(root=(1.02, 1.30), dist=0.004):
    return PP.Pose(root_xz=root, facing=1, dist=dist,
                   angles={"body": 0.05, "neck0": 1.10, "neck1": 0.12, "neck2": 0.10, "neck3": 0.07, "neck4": 0.02,
                           "neck5": -0.04, "neck6": -0.10, "neck7": -0.14, "neck8": -0.16, "neck9": -0.15, "neck10": -0.12,
                           "neck11": -0.08, "head": -0.40,
                           "tibia_near": 0.55, "tarsus_near": -1.25, "foot_near": 0.55,
                           "tibia_far": -0.05, "tarsus_far": 0.02, "foot_far": 0.03})


def crane_pose_peck(root=(1.10, 1.30), dist=0.004):
    """鹤低头（追逐、啄）：脖子往前下方弯。"""
    return PP.Pose(root_xz=root, facing=1, dist=dist,
                   angles={"body": -0.10, "neck0": 0.55, "neck1": 0.05, "neck2": -0.06, "neck3": -0.10, "neck4": -0.12,
                           "neck5": -0.12, "neck6": -0.10, "neck7": -0.08, "neck8": -0.05, "neck9": -0.02, "neck10": 0.0,
                           "neck11": 0.02, "head": -0.55,
                           "tibia_near": 0.35, "tarsus_near": -0.55, "foot_near": 0.25,
                           "tibia_far": -0.20, "tarsus_far": 0.15, "foot_far": 0.05})


def turtle_pose(root=(1.78, 1.00), facing=-1, dist=0.004, head_out=1.0):
    return PP.Pose(root_xz=root, facing=facing, dist=dist,
                   angles={"leg_front_near": 0.25, "leg_back_near": -0.2, "leg_front_far": -0.15, "leg_back_far": 0.12,
                           "headneck": 0.12},
                   slide={"headneck": -38.0 * (1 - head_out)})


def rod_point(pose, rig, part, local):
    sol = PP.solve(rig, pose)
    o, ang = sol[part]
    ca, sa = math.cos(ang), math.sin(ang)
    p = o + np.array([ca * local[0] - sa * local[1], sa * local[0] + ca * local[1]])
    return PP.to_world(pose, p, L.WIRE_Y, 3.0)


# ---------------------------------------------------------------- 握签子
def grip(hand_pos, rod_from, side, palm_hint, curl=(72, 88, 58), thumb=(55, 25, 30, 20)):
    """返回 (腕部目标, Hand)。rod_from = 签子另一端（皮影上的点）。"""
    a = np.asarray(rod_from, float) - np.asarray(hand_pos, float)
    a /= np.linalg.norm(a)
    F = C.grip_frame(a, palm_hint, side)
    X, Y, Z = F[:, 0], F[:, 1], F[:, 2]
    P = None
    return F, C.Hand(frame=F, curl={f: curl for f in C.FINGERS}, spread=2.0, thumb=(8, 18, 22, 14), thumb_along=True)


def place_grip(Pr, hand_pos, rod_from, side, palm_hint, curl=(72, 88, 58), thumb=(55, 25, 30, 20), along=0.0):
    F, hand = grip(hand_pos, rod_from, side, palm_hint, curl, thumb)
    X, Y, Z = F[:, 0], F[:, 1], F[:, 2]
    pl, pw, pt = Pr.palm
    wrist = np.asarray(hand_pos, float) - Y * (pl * 0.62) - Z * (pt * 0.5 + 0.007) - X * along
    return wrist, hand


# ---------------------------------------------------------------- 两个时刻
def moment6(assets, t=0.0):
    """第 6 场：床单正面（B 机位），鹤贴上床单亮相；小满坐在左下，抱着的胳膊开始松开。"""
    st = room.RoomState(sheet_hung=True, tv_on=False, textures=assets.room_tex)
    pl = room.build(st)
    lp = L.LAMP_STAGE
    LS.lamp_geometry(pl, (lp.x, lp.y, lp.z), hang_z=L.LAMP_PURLIN_Z)
    cpose = crane_pose_debut()
    body_pt = rod_point(cpose, PP.CRANE_RIG, "body", (8, 6))
    head_pt = rod_point(cpose, PP.CRANE_RIG, "head", (16, 2))
    hand_body = np.array([0.96, 4.55, 1.00])
    hand_head = np.array([1.10, 4.53, 1.08])
    PP.add_puppet(pl, PP.CRANE_RIG, assets.cp, assets.ids("c"), cpose, L.WIRE_Y, M("wood_raw"), "crane",
                  rods=[("body", (8, 6), hand_body), ("head", (16, 2), hand_head)], rod_mat=M("wood_raw"))
    scene = rt.Scene(pl, assets.A, assets.R)
    # 人物
    chars_list = []
    faces = []
    # 小满：坐在板凳上，面朝床单（世界 +y）
    st_x = L.MARKS["xiaoman_audience"]
    P = C.XIAOMAN
    root = np.array([st_x.x, st_x.y, 0.30 + 0.075])
    pose = C.CharPose(root=tuple(root), yaw=0.0, lean=(4.0, 0.0), spine2=(-4, 0, 3), neck=(-8, 0, 0), head=(-10, 4, 2),
                      breath=0.4, cowlick=(0.004, 0.0))
    # 胳膊抱在胸前、正在松开：右手搭在左小臂上，左手垂到腿上
    fr = C.body_frames(P, pose)
    R2 = fr["R2"]
    chest = fr["s2"] + R2 @ np.array([0, 0.11, -0.02])
    pose.wrist = {"R": chest + R2 @ np.array([-0.06, 0.02, -0.06]), "L": root + np.array([-0.10, 0.20, 0.02])}
    pose.elbow_pole = {"R": chest + R2 @ np.array([0.35, 0.0, -0.4]), "L": root + np.array([-0.4, -0.1, 0.1])}
    pose.ankle = {"R": (root[0] + 0.10, root[1] + 0.30, 0.075), "L": (root[0] - 0.09, root[1] + 0.26, 0.075)}
    pose.knee_pole = {"R": (root[0] + 0.15, root[1] + 1.0, 0.5), "L": (root[0] - 0.15, root[1] + 1.0, 0.5)}
    pose.expr = dict(eye_open=1.15, mouth_open=0.35, brow=0.6, look=(0.0, 0.5))
    c1, g1, info1 = C.build(P, pose, "xiaoman")
    chars_list.append((c1, g1))
    faces.append(("xiaoman", info1, pose.expr, 0))
    # 奶奶：站在马灯后面，两手握签子
    Pn = C.NAINAI
    nb = L.MARKS["nainai_backstage"]
    npose = C.CharPose(root=(nb.x, nb.y, Pn.hip_h), yaw=180.0, lean=(6.0, 0.0), spine2=(4, 0, -6), neck=(2, 0, 0), head=(4, 0, 8),
                       breath=0.5)
    wR, hR = place_grip(Pn, hand_head, head_pt, "R", (-0.3, 0, -1.0))
    wL, hL = place_grip(Pn, hand_body, body_pt, "L", (0.3, 0, -1.0))
    npose.wrist = {"R": wR, "L": wL}
    npose.hands = {"R": hR, "L": hL}
    npose.elbow_pole = {"R": np.array([nb.x - 0.4, nb.y + 0.3, 0.6]), "L": np.array([nb.x + 0.4, nb.y + 0.3, 0.6])}
    npose.ankle = {"R": (nb.x - 0.09, nb.y + 0.02, 0.08), "L": (nb.x + 0.10, nb.y - 0.06, 0.08)}
    npose.knee_pole = {"R": (nb.x - 0.1, nb.y - 1.0, 0.5), "L": (nb.x + 0.1, nb.y - 1.0, 0.5)}
    npose.foot_dir = {"R": (0.1, -1, 0), "L": (-0.15, -1, 0)}
    npose.expr = dict(eye_smile=0.6, mouth_smile=0.5, look=(0.0, 0.2))
    c2, g2, info2 = C.build(Pn, npose, "nainai")
    chars_list.append((c2, g2))
    faces.append(("nainai", info2, npose.expr, None))
    chars, groups, faces = merge_chars(chars_list, faces)
    lights = LS.lamp_lights((lp.x, lp.y, lp.z), t) + [LS.moon_light(0.6)]
    names = ["lamp_core", "lamp_globe", "moon"]
    glow = sheetglow.glow_lights(scene, lights, chars, groups)
    lights = lights + glow
    names += [f"sheet{k}" for k in range(len(glow))]
    cs = L.CAMERAS[1]
    cam = Camera(cs.pos, cs.target, cs.hfov_deg)
    ctx = dict(exposure=2.4, chars=chars, faces=faces, t=t,
               sources=[dict(kind="lamp", pos=(lp.x, lp.y, lp.z), intensity=0.6)],
               extra={"puppet_mask": None})
    return scene, cam, lights, names, chars, groups, ctx


def moment10(assets, t=0.0):
    """第 10 场：来电的一瞬间。侧面镜头沿着床单看后台：床单被日光灯照透像灯箱，祖孙被晃得眯眼。"""
    st = room.RoomState(sheet_hung=True, tv_on=True, textures=assets.room_tex)
    pl = room.build(st)
    lp = L.LAMP_STAGE
    LS.lamp_geometry(pl, (lp.x, lp.y, lp.z), hang_z=L.LAMP_PURLIN_Z)
    cpose = crane_pose_peck(root=(1.04, 1.30))
    tpose = turtle_pose(root=(1.70, 1.00), facing=-1)
    body_pt = rod_point(cpose, PP.CRANE_RIG, "body", (8, 6))
    head_pt = rod_point(cpose, PP.CRANE_RIG, "head", (16, 2))
    shell_pt = rod_point(tpose, PP.TURTLE_RIG, "shell", (0, 24))
    hand_body = np.array([0.96, 4.55, 1.00])
    hand_head = np.array([1.10, 4.53, 1.08])
    hand_turtle = np.array([1.62, 4.56, 0.88])
    PP.add_puppet(pl, PP.CRANE_RIG, assets.cp, assets.ids("c"), cpose, L.WIRE_Y, M("wood_raw"), "crane",
                  rods=[("body", (8, 6), hand_body), ("head", (16, 2), hand_head)], rod_mat=M("wood_raw"))
    PP.add_puppet(pl, PP.TURTLE_RIG, assets.tp, assets.ids("t"), tpose, L.WIRE_Y, M("wood_raw"), "turtle",
                  rods=[("shell", (0, 24), hand_turtle)], rod_mat=M("wood_raw"))
    # 手电：架在木箱上
    fp = L.FLASHLIGHT_PROP
    pl.cyl(M("metal"), (fp.x - 0.06, fp.y + 0.05, fp.z - 0.03), (fp.x, fp.y, fp.z), 0.018, name="flashlight")
    scene = rt.Scene(pl, assets.A, assets.R)
    chars_list, faces = [], []
    Pn = C.NAINAI
    nb = L.MARKS["nainai_backstage"]
    npose = C.CharPose(root=(nb.x, nb.y, Pn.hip_h - 0.01), yaw=180.0, lean=(-2.0, 0.0), spine2=(-4, 0, -6), neck=(0, 0, -4),
                       head=(2, 8, 34), breath=0.8)
    wR, hR = place_grip(Pn, hand_head, head_pt, "R", (-0.3, 0, -1.0))
    wL, hL = place_grip(Pn, hand_body, body_pt, "L", (0.3, 0, -1.0))
    npose.wrist = {"R": wR, "L": wL}
    npose.hands = {"R": hR, "L": hL}
    npose.elbow_pole = {"R": np.array([nb.x - 0.4, nb.y + 0.3, 0.6]), "L": np.array([nb.x + 0.4, nb.y + 0.3, 0.6])}
    npose.ankle = {"R": (nb.x - 0.09, nb.y + 0.02, 0.08), "L": (nb.x + 0.10, nb.y - 0.06, 0.08)}
    npose.knee_pole = {"R": (nb.x - 0.1, nb.y - 1.0, 0.5), "L": (nb.x + 0.1, nb.y - 1.0, 0.5)}
    npose.foot_dir = {"R": (0.1, -1, 0), "L": (-0.15, -1, 0)}
    npose.expr = dict(eye_open=0.2, squint=1.0, brow_tilt=0.6, brow=-0.4, mouth_open=0.25, mouth_smile=-0.2)
    c2, g2, info2 = C.build(Pn, npose, "nainai")
    chars_list.append((c2, g2))
    faces.append(("nainai", info2, npose.expr, None))
    P = C.XIAOMAN
    xb = L.MARKS["xiaoman_backstage"]
    xpose = C.CharPose(root=(xb.x, xb.y, P.hip_h), yaw=180.0, lean=(-4.0, 0.0), spine2=(-2, 0, 14), neck=(4, -4, 16),
                       head=(8, -8, 30), breath=0.9, cowlick=(0.01, 0.006), shrug=(0.016, 0.022))
    wR, hR = place_grip(P, hand_turtle, shell_pt, "R", (-0.3, 0, -1.0))
    # 左手抬到眉前挡光：手背朝自己、掌心朝床单
    fr = C.body_frames(P, xpose)
    hcx = fr["hc"]
    Rh = fr["Rh"]
    # 左手攥着衣角，缩着肩，脸往镜头这边扭开、眯眼
    xpose.wrist = {"R": wR, "L": np.array([xb.x + 0.13, xb.y - 0.06, 0.62])}
    xpose.hands = {"R": hR, "L": PO.hand("fist", PO.frame_from_dirs((0.1, -0.2, -1.0), (-1.0, 0.0, 0.1), "L"))}
    xpose.elbow_pole = {"R": np.array([xb.x - 0.4, xb.y + 0.3, 0.5]), "L": np.array([xb.x + 0.5, xb.y + 0.2, 0.7])}
    xpose.ankle = {"R": (xb.x - 0.08, xb.y - 0.04, 0.07), "L": (xb.x + 0.09, xb.y + 0.04, 0.07)}
    xpose.knee_pole = {"R": (xb.x - 0.1, xb.y - 1.0, 0.4), "L": (xb.x + 0.1, xb.y - 1.0, 0.4)}
    xpose.foot_dir = {"R": (0.1, -1, 0), "L": (-0.2, -1, 0)}
    xpose.expr = dict(eye_open=0.08, squint=1.0, brow_tilt=0.8, brow=-0.6, mouth_open=0.35, mouth_w=0.8, mouth_smile=-0.3)
    c1, g1, info1 = C.build(P, xpose, "xiaoman")
    chars_list.append((c1, g1))
    faces.append(("xiaoman", info1, xpose.expr, None))
    chars, groups, faces = merge_chars(chars_list, faces)
    lights = [LS.tube_light(1.0)] + LS.lamp_lights((lp.x, lp.y, lp.z), t) + \
        [LS.flashlight((fp.x, fp.y, fp.z), (1.35, 4.0, 1.30), 1.0), LS.moon_light(0.5), LS.tv_light(t, 1.0)]
    names = ["tube", "lamp_core", "lamp_globe", "flash", "moon", "tv"]
    glow = sheetglow.glow_lights(scene, lights, chars, groups)
    lights = lights + glow
    names += [f"sheet{k}" for k in range(len(glow))]
    cs = L.CAMERAS[3]
    cam = Camera(cs.pos, cs.target, cs.hfov_deg)
    ctx = dict(exposure=0.55, chars=chars, faces=faces, t=t, tv="static", phone="charge", scene_names=scene.names,
               sources=[dict(kind="lamp", pos=(lp.x, lp.y, lp.z), intensity=0.25)], extra={"puppet_mask": None})
    return scene, cam, lights, names, chars, groups, ctx


def moment10_wide(assets, t=0.0):
    """第 10 场：来电的一瞬间，全景。日光灯灌满屋子，电视雪花，手机亮起充电图标；
    床单上的影子被压到几乎看不见；床单下沿露出祖孙俩的腿。"""
    scene, cam, lights, names, chars, groups, ctx = moment10(assets, t)
    st = room.RoomState(sheet_hung=True, tv_on=True, shells=True, fan_angle=0.9, textures=assets.room_tex)
    # 重新搭场景（加上毛豆壳、吊扇角度），皮影和签子沿用 moment10 的
    pl = room.build(st)
    lp = L.LAMP_STAGE
    LS.lamp_geometry(pl, (lp.x, lp.y, lp.z), hang_z=L.LAMP_PURLIN_Z)
    keep = [k for k, n in enumerate(scene.names) if n.startswith(("crane:", "turtle:", "flashlight"))]
    for k in keep:
        pl.rows.append(scene.prims[k].copy())
        pl.names.append(scene.names[k])
    scene = rt.Scene(pl, assets.A, assets.R)
    cs = L.CAMERAS[0]
    cam = Camera(cs.pos, cs.target, cs.hfov_deg)
    lights = [l for l, n in zip(lights, names) if not n.startswith("sheet")]
    names = [n for n in names if not n.startswith("sheet")]
    glow = sheetglow.glow_lights(scene, lights, chars, groups)
    lights = lights + glow
    names += [f"sheet{k}" for k in range(len(glow))]
    ctx.update(exposure=0.55, scene_names=scene.names, sources=[])
    return scene, cam, lights, names, chars, groups, ctx


def merge_chars(chars_list, faces):
    """把几个人物的图元合并，组号重新编；返回五官信息里每个人头部组的编号。"""
    rows, groups = [], []
    out_faces = []
    off = 0
    goff = 0
    for (c, g), (who, info, expr, _) in zip(chars_list, faces):
        c = c.copy()
        g = g.copy()
        c[:, 2] += goff
        g[:, 4] += off
        rows.append(c)
        groups.append(g)
        out_faces.append((who, info, expr, goff))   # 每个人的第 0 组是头
        off += c.shape[0]
        goff += g.shape[0]
    return np.concatenate(rows), np.concatenate(groups), out_faces


def render_moment(fn, assets, W, H, ss, styles, out_dir, tag, t=0.0, cache=None):
    import pickle
    if cache and Path(cache).exists():
        with open(cache, "rb") as f:
            buf, scene, ctx = pickle.load(f)
        outs = {}
        for sname in styles:
            t0 = time.time()
            img = STYLES[sname](buf, scene, ctx)
            Image.fromarray(img).save(Path(out_dir) / f"{tag}_{sname}.png")
            print(" ", sname, f"{time.time() - t0:.1f}s (cache)")
            outs[sname] = img
        return outs
    scene, cam, lights, names, chars, groups, ctx = fn(assets, t)
    ctx["cam"] = cam
    pm = np.array([n.startswith(("crane:", "turtle:")) and not n.endswith(":rod") for n in scene.names])
    t0 = time.time()
    buf = frame.render_ss(scene, cam, lights, names, W, H, ss=ss, chars=chars, groups=groups,
                          keep_mats=(M("sheet"),), vpl_n=32)
    print(tag, "render", f"{time.time() - t0:.1f}s", buf.timings)
    ctx["extra"] = {"puppet_mask": np.where(buf.ID >= 0, pm[np.maximum(buf.ID, 0)], False)}
    if cache:
        with open(cache, "wb") as f:
            pickle.dump((buf, scene, ctx), f)
    outs = {}
    for sname in styles:
        t0 = time.time()
        img = STYLES[sname](buf, scene, ctx)
        Image.fromarray(img).save(Path(out_dir) / f"{tag}_{sname}.png")
        print(" ", sname, f"{time.time() - t0:.1f}s")
        outs[sname] = img
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--w", type=int, default=960)
    ap.add_argument("--h", type=int, default=540)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--styles", default="lantern,woodcut,silk")
    ap.add_argument("--moments", default="6,10")
    ap.add_argument("--cache", default="", help="缓存目录：有缓存就只重跑画风合成")
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    assets = PuppetAssets() if not a.cache or not all((Path(a.cache) / f"s{m.zfill(2)}_{a.w}.pkl").exists() for m in a.moments.split(",")) else None
    styles = a.styles.split(",")
    cdir = Path(a.cache) if a.cache else None
    if cdir:
        cdir.mkdir(parents=True, exist_ok=True)
    if "6" in a.moments.split(","):
        render_moment(moment6, assets, a.w, a.h, a.ss, styles, a.out, "s06", cache=cdir / f"s06_{a.w}.pkl" if cdir else None)
    if "10" in a.moments.split(","):
        render_moment(moment10, assets, a.w, a.h, a.ss, styles, a.out, "s10", cache=cdir / f"s10_{a.w}.pkl" if cdir else None)
    if "10w" in a.moments.split(","):
        render_moment(moment10_wide, assets, a.w, a.h, a.ss, styles, a.out, "s10w", cache=cdir / f"s10w_{a.w}.pkl" if cdir else None)


if __name__ == "__main__":
    main()
