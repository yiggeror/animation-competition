"""设计稿：人物三视图、比例、表情、姿势、手、不同光下；皮影设计；堂屋光照状态。

用法：python -m laidian.shots.design_sheets OUT_DIR [--only characters,expressions,poses,hands,lights,puppets,room]
"""
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .. import layout as L, poses as PO
from ..render import character as C
from ..render import frame, light as LT, puppets as PP, rt, room
from ..render import lighting_states as LS
from ..render.camera import Camera
from ..render.materials import M
from ..render.rt import PrimList
from ..render.styles import lantern, model, silk, woodcut
from .style_samples import PuppetAssets, merge_chars

ROOT = Path(__file__).resolve().parents[3]
FONT = str(ROOT / "assets/fonts/NotoSansSC-VF.ttf")
PAPER = (238, 233, 222)
INKC = (40, 34, 30)


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def stage_scene():
    pl = PrimList()
    pl.box(M("concrete"), -6, 6, -6, 6, -0.2, 0.0, name="floor")
    return rt.Scene(pl)


def studio_lights(center, key=(1.0, 0.95, 0.88)):
    c = np.asarray(center, float)
    k = LT.make_light(LT.SPHERE, key, 6.0, pos=tuple(c + np.array([1.2, 2.2, 1.6])), radius=0.25, samples=8)
    f = LT.make_light(LT.SPHERE, (0.85, 0.9, 1.0), 2.0, pos=tuple(c + np.array([-1.8, 1.2, 0.8])), radius=0.4, samples=4)
    return [k, f], ["key", "fill"]


def render_chars(sc, chars_list, faces, cam, W, H, lights=None, names=None, style="model", ss=2, exposure=1.0, chars_only=True):
    chars, groups, faces2 = merge_chars(chars_list, faces)
    if lights is None:
        c = np.mean([np.asarray(f[1]["head_c"]) for f in faces], axis=0)
        lights, names = studio_lights(c - np.array([0, 0, 0.6]))
    buf = frame.render_ss(sc, cam, lights, names, W, H, ss=ss, chars=chars, groups=groups, vpl_n=8, ao=False, denoise=False)
    ctx = dict(cam=cam, chars=chars, faces=faces2, exposure=exposure, chars_only=chars_only, extra=None, sources=[])
    fn = {"model": model.compose, "lantern": lantern.compose, "woodcut": woodcut.compose, "silk": silk.compose}[style]
    return fn(buf, sc, ctx)


def label(img, text, size=26, pos=(14, 10), color=INKC):
    im = Image.fromarray(img) if isinstance(img, np.ndarray) else img
    d = ImageDraw.Draw(im)
    d.text(pos, text, fill=color, font=font(size, 600))
    return im


def sheet(panels, cols, title, subtitle="", pad=16, head=110):
    w = max(p.width for p in panels)
    h = max(p.height for p in panels)
    rows = math.ceil(len(panels) / cols)
    S = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + pad) + pad + head), PAPER)
    d = ImageDraw.Draw(S)
    d.text((pad, 18), title, fill=INKC, font=font(40, 700))
    if subtitle:
        d.text((pad, 68), subtitle, fill=(90, 80, 70), font=font(22))
    for i, p in enumerate(panels):
        r, c = divmod(i, cols)
        S.paste(p, (pad + c * (w + pad), head + pad + r * (h + pad)))
    return S


# ---------------------------------------------------------------- 人物
CHARS = [(C.XIAOMAN, "xiaoman", "小满"), (C.NAINAI, "nainai", "奶奶")]


def turnaround(out):
    sc = stage_scene()
    panels = []
    for P, outfit, cn in CHARS:
        pose = PO.standing(P, 0, 0, 0, dict(mouth_smile=0.2 if outfit == "xiaoman" else 0.5,
                                           eye_smile=0.0 if outfit == "xiaoman" else 0.4))
        if outfit == "xiaoman":
            pose.cowlick = (0.004, 0.0)
        c, g, info = C.build(P, pose, outfit)
        top = info["head_c"][2] + 0.16
        for ang, nm in ((0, "正面"), (40, "四分之三"), (90, "侧面"), (180, "背面")):
            a = math.radians(ang)
            d = 4.2
            ch = top / 2
            tv = top * 0.56 / d
            cam = Camera((math.sin(a) * d, math.cos(a) * d, ch), (0, 0, ch), 2 * math.degrees(math.atan(tv * 420 / 760)))
            img = render_chars(sc, [(c, g)], [(outfit, info, pose.expr, None)], cam, 420, 760)
            panels.append(label(img, f"{cn} · {nm}"))
    S = sheet(panels, 4, "人物三视图", "小满（9 岁，约 1.30 米）· 奶奶（七十来岁，约 1.52 米）。中性画法，仅示形体、比例、服装与配色。")
    S.save(out / "char_turnaround.png")


def scale(out):
    sc = stage_scene()
    lst, faces = [], []
    pa = PO.standing(C.XIAOMAN, -0.32, 0, 15, dict(mouth_smile=0.3))
    c1, g1, i1 = C.build(C.XIAOMAN, pa, "xiaoman")
    pb = PO.standing(C.NAINAI, 0.32, 0, -15, dict(eye_smile=0.5, mouth_smile=0.5))
    c2, g2, i2 = C.build(C.NAINAI, pb, "nainai")
    cam = Camera((0, 5.5, 0.85), (0, 0, 0.82), 21)
    img = render_chars(sc, [(c1, g1), (c2, g2)], [("xiaoman", i1, pa.expr, None), ("nainai", i2, pb.expr, None)], cam, 1000, 900)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    # 高度刻度（按相机投影换算）
    for hgt in (0.0, 0.5, 1.0, 1.30, 1.52):
        q = cam.project(np.array([[0, 0, hgt]]), 1000, 900)[0]
        d.line([(30, q[1]), (970, q[1])], fill=(170, 160, 150), width=1)
        d.text((36, q[1] - 26), f"{hgt:.2f} 米", fill=(120, 110, 100), font=font(20))
    S = sheet([im], 1, "比例图", "小满约 5.5 个头高（头稍大，便于远景读表情）；奶奶约 6.5 个头高，略驼背。")
    S.save(out / "char_scale.png")


EXPR_XM = [("平常", dict()), ("无聊（打游戏）", dict(eye_open=0.55, mouth_smile=-0.3, brow=-0.3, look=(0.3, -0.6))),
           ("着急（电量 1%）", dict(eye_open=1.2, brow_tilt=0.9, brow=0.4, mouth_open=0.35, mouth_w=0.8)),
           ("绝望（瘫倒）", dict(eye_open=0.35, brow_tilt=0.8, mouth_open=0.6, mouth_w=1.2)),
           ("嘴硬（装不在乎）", dict(eye_open=0.6, brow=-0.5, mouth_smile=-0.5, mouth_w=0.7, look=(-0.6, 0.2))),
           ("看呆了（鹤亮相）", dict(eye_open=1.2, brow=0.7, mouth_open=0.4, mouth_w=0.7, look=(0.0, 0.5))),
           ("噗嗤笑", dict(eye_smile=1.0, mouth_open=0.5, mouth_smile=0.8, mouth_w=1.2)),
           ("被晃得眯眼", dict(eye_open=0.12, squint=1.0, brow_tilt=0.7, brow=-0.5, mouth_open=0.45, mouth_w=0.9)),
           ("鬼脸", dict(eye_open=1.25, brow=1.0, mouth_open=0.9, mouth_w=1.4))]
EXPR_NN = [("平常", dict(eye_smile=0.35, mouth_smile=0.3)), ("看孙女（剥豆）", dict(eye_smile=0.5, mouth_smile=0.4, look=(-0.5, -0.2))),
           ("狡黠（有主意了）", dict(eye_smile=0.7, mouth_smile=0.7, brow=0.4, look=(0.5, 0.0))),
           ("笑弯了腰", dict(eye_smile=1.0, mouth_open=0.7, mouth_smile=1.0, mouth_w=1.3)),
           ("专注（操纵皮影）", dict(eye_open=0.8, eye_smile=0.2, mouth_smile=0.0, brow=-0.2)),
           ("被晃得眯眼", dict(eye_open=0.2, squint=1.0, brow_tilt=0.6, brow=-0.4, mouth_open=0.25)),
           ("不好意思地笑", dict(eye_smile=0.8, mouth_smile=0.5, brow_tilt=0.4, look=(0.3, -0.6))),
           ("鼓腮吹灯", dict(eye_open=0.6, puff=1.0, mouth_w=0.6, brow=0.2)),
           ("愣了一下", dict(eye_open=1.1, eye_smile=0.0, brow=0.8, mouth_open=0.2, mouth_w=0.7))]


def expressions(out):
    sc = stage_scene()
    for P, outfit, cn, table in ((C.XIAOMAN, "xiaoman", "小满", EXPR_XM), (C.NAINAI, "nainai", "奶奶", EXPR_NN)):
        panels = []
        for nm, e in table:
            pose = PO.standing(P, 0, 0, 0, e)
            pose.head = (0, 0, 18)
            c, g, info = C.build(P, pose, outfit)
            hc = info["head_c"]
            a = math.radians(22)
            cam = Camera((hc[0] + math.sin(a) * 0.95, hc[1] + math.cos(a) * 0.95, hc[2] + 0.03), tuple(hc - np.array([0, 0, 0.01])), 21)
            lights, names = studio_lights(hc - np.array([0, 0, 0.5]))
            img = render_chars(sc, [(c, g)], [(outfit, info, e, None)], cam, 380, 400, lights, names)
            panels.append(label(img, nm, 22))
        S = sheet(panels, 5 if len(panels) > 8 else 4, f"{cn} · 表情表", "每个情绪都同时落在眼睛、眉毛、嘴上；动起来时再加上姿态和小动作。")
        S.save(out / f"char_expressions_{outfit}.png")


def poses(out):
    sc = stage_scene()
    panels = []
    P = C.XIAOMAN
    lp, phone = PO.lying_phone(P, 0, 0, 0, dict(eye_open=0.6, mouth_smile=-0.2, look=(0, -0.8)))
    items = [("小满 · 趴着打游戏", P, "xiaoman", lp, (1.1, 1.2, 0.6), (0, 0.1, 0.18)),
             ("小满 · 抱着胳膊坐板凳", P, "xiaoman", PO.sitting_stool(P, 0, 0, 0.30, 0, "crossed", dict(eye_open=0.6, brow=-0.5, mouth_smile=-0.4, look=(-0.5, 0.2))), (1.3, 1.6, 0.8), (0, 0, 0.55)),
             ("小满 · 瘫倒", P, "xiaoman", PO.flop(P, 0, 0, 90, dict(eye_open=0.3, brow_tilt=0.8, mouth_open=0.6)), (1.3, 0.8, 1.0), (0, 0, 0.12)),
             ("小满 · 比手影小狗", P, "xiaoman", PO.dog_shadow(P, 0, 0, 0, (0.08, 0.38, 1.0), True, dict(eye_smile=0.6, mouth_open=0.4, mouth_smile=0.8)), (1.4, 1.4, 1.0), (0, 0.15, 0.75)),
             ("奶奶 · 坐小板凳剥毛豆", C.NAINAI, "nainai", PO.sitting_stool(C.NAINAI, 0, 0, 0.22, 0, "beans", dict(eye_smile=0.5, mouth_smile=0.4, look=(0, -0.7)), lean=12), (1.3, 1.6, 0.8), (0, 0.1, 0.5)),
             ("奶奶 · 踮脚够马灯", C.NAINAI, "nainai", PO.reaching_up(C.NAINAI, 0, 0, 0, 1.95, dict(eye_open=0.9, mouth_smile=0.1, look=(0, 0.8))), (1.6, 2.0, 1.1), (0, 0.1, 1.0))]
    for nm, P, outfit, pose, campos, look in items:
        c, g, info = C.build(P, pose, outfit)
        lst = [(c, g)]
        fc = [(outfit, info, pose.expr, None)]
        prop = props_for(nm, pose)
        if prop is not None:
            lst.append(prop)
            fc.append(("prop", info, {}, -99))
        cam = Camera(campos, look, 50)
        img = render_chars(sc, lst, fc, cam, 520, 520)
        panels.append(label(img, nm, 22))
    S = sheet(panels, 3, "典型姿势", "小满快、急、动作大、坐不住；奶奶慢、稳、准。所有姿势都由 IK 摆放，肘、膝只朝正确方向弯。")
    S.save(out / "char_poses.png")


def props_for(nm, pose):
    """设计稿里给姿势配上道具（板凳、竹席），用 SDF 圆角盒画，和人物一起渲染。"""
    from ..render.rig import rz
    B = C.Builder()
    R = rz(pose.yaw)
    root = np.asarray(pose.root, float)
    if "板凳" in nm:
        h = 0.30 if "小满" in nm else 0.22
        B.begin()
        c = np.array([root[0], root[1], h - 0.015])
        B.rbox(c, (0.15, 0.11, 0.015), R, 0.004, "wood_raw", k=0.0, layer=1)
        for sx in (-1, 1):
            for sy in (-1, 1):
                lc = np.array([root[0], root[1], (h - 0.03) / 2]) + R @ np.array([sx * 0.12, sy * 0.08, 0])
                B.rbox(lc, (0.015, 0.015, (h - 0.03) / 2), R, 0.003, "wood_raw", k=0.0, layer=1)
        B.end(0.02)
    elif "趴着" in nm or "瘫倒" in nm:
        B.begin()
        B.rbox(np.array([root[0], root[1], 0.003]), (0.75, 0.9, 0.003), R, 0.001, "bamboo", k=0.0, layer=1)
        B.end(0.02)
    else:
        return None
    return B.arrays()


def hands(out):
    sc = stage_scene()
    panels = []
    names = [("relaxed", "放松"), ("grip", "握签子"), ("pinch", "捏（剥豆、拉灯绳）"), ("point", "指"),
             ("dog_bad", "歪歪扭扭的狗"), ("dog", "小狗（闭嘴）"), ("dog_open", "小狗（张嘴）"), ("open", "张开")]
    for who, P, outfit in (("小满", C.XIAOMAN, "xiaoman"), ("奶奶", C.NAINAI, "nainai")):
        for key, cn in names:
            if outfit == "nainai" and key.startswith("dog"):
                continue
            pose = PO.standing(P, 0, 0, 0)
            fr = C.body_frames(P, pose)
            w = fr["s2"] + np.array([0.0, 0.42, 0.0])
            pose.wrist = {"R": w}
            pose.elbow_pole = {"R": fr["s2"] + np.array([0.6, -0.2, -0.4])}
            hd = PO.hand(key, PO.frame_from_dirs((0.15, 1.0, 0.25), (-1.0, 0.0, -0.25), "R"))
            pose.hands = {"R": hd}
            c, g, info = C.build(P, pose, outfit)
            wr = info["wrist_R"]
            ctr = wr + np.array([-0.01, 0.06, 0.0])
            cam = Camera(tuple(ctr + np.array([0.30, 0.18, 0.12])), tuple(ctr), 30)
            lights, ln = studio_lights(ctr)
            img = render_chars(sc, [(c, g)], [(outfit, info, {}, None)], cam, 340, 300, lights, ln)
            panels.append(label(img, f"{who} · {cn}", 20))
    S = sheet(panels, 7, "手部设计", "小满的手肉、短、指尖圆；奶奶的手长、瘦、指节突出，左腕戴玉镯。拇指能对握，握东西时四指包住、拇指压上。")
    S.save(out / "char_hands.png")


def lights(out):
    """人物在马灯、手电、日光灯下。"""
    sc = stage_scene()
    panels = []
    for P, outfit, cn in CHARS:
        pose = PO.standing(P, 0, 0, 0, dict(eye_smile=0.3 if outfit == "nainai" else 0.0, mouth_smile=0.3))
        c, g, info = C.build(P, pose, outfit)
        hc = info["head_c"]
        cam = Camera((0.55, 1.6, hc[2] - 0.15), (0, 0, hc[2] - 0.30), 34)
        for kind, cnl in (("lamp", "马灯"), ("flash", "手电"), ("tube", "日光灯")):
            if kind == "lamp":
                ls = LS.lamp_lights((0.45, 0.45, hc[2] - 0.05), 0.3)
                nm = ["core", "globe"]
                exp = 2.2
            elif kind == "flash":
                ls = [LS.flashlight((0.25, 0.9, hc[2] - 0.35), tuple(hc - np.array([0, 0, 0.2])), 1.0)]
                nm = ["flash"]
                exp = 0.9
            else:
                ls = [LS.tube_light(1.0)]
                ls[0][4:10] = [-0.6, 0.8, 3.1, 0.6, 0.8, 3.1]
                # 堂屋里日光灯照亮四面白墙，墙再把光反回来，所以日光灯下的脸是平的、白的；
                # 设计稿的空场景没有墙，用一块面光源代替被照亮的墙，否则顶光会把下半张脸压黑
                ls.append(LT.make_light(LT.RECT, (0.96, 0.96, 0.92), 14.0, pos=(-1.0, 2.2, 0.2), vec=(2.0, 0, 0),
                                        vec2=(0, 0, 2.2), samples=6))
                nm = ["tube", "walls"]
                exp = 0.5
            for style in ("lantern", "woodcut", "silk"):
                img = render_chars(sc, [(c, g)], [(outfit, info, pose.expr, None)], cam, 300, 380, ls, nm, style=style,
                                   exposure=exp, chars_only=False)
                panels.append(label(img, f"{cn}·{cnl}·{ {'lantern': 'A', 'woodcut': 'B', 'silk': 'C'}[style]}", 18,
                                    color=(240, 230, 210)))
    S = sheet(panels, 9, "人物在三种光下 × 三个画风", "马灯：暖、跳动、阴影深；手电：冷、硬、有方向；日光灯：平、白、惨白。光的计算相同，画法不同。")
    S.save(out / "char_lights.png")


# ---------------------------------------------------------------- 皮影
def puppets(out):
    import sys
    sys.path.insert(0, str(ROOT / "tools/tests"))
    from puppet_check import assemble
    from .style_samples import crane_pose_debut, turtle_pose
    ppmm = 4.0
    cp = PP.crane_parts(ppmm)
    tp = PP.turtle_parts(ppmm)
    lamp = np.array([1.0, 0.70, 0.40])
    panels = []

    def to_img(x):
        x = np.clip(x, 0, 1)
        return Image.fromarray((np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055) * 255).astype(np.uint8))
    cpose = crane_pose_debut()
    a = assemble(PP.CRANE_RIG, cp, cpose, 900, 900, (470, 545), 1.45) * lamp
    panels.append(label(to_img(a), "鹤 · 床单上的样子（透光）", 22))
    ra, ca = assemble(PP.CRANE_RIG, cp, cpose, 900, 900, (470, 545), 1.45, "refl")
    bg = np.array([0.05, 0.04, 0.035])
    panels.append(label(to_img((ra * ca[..., None] + bg * (1 - ca[..., None])) * 2.3), "鹤 · 从后台看到的皮面", 22, color=(230, 220, 200)))
    # 拆开的部件
    ex = np.ones((900, 900, 3), np.float32)
    exp_pose = PP.Pose(angles={"neck0": 1.2, **{f"neck{k}": 0.0 for k in range(1, PP.N_NECK)}, "head": -1.1})
    ex = assemble(PP.CRANE_RIG, cp, exp_pose, 900, 900, (450, 520), 1.6) * lamp
    panels.append(label(to_img(ex), "鹤 · 部件与铆点（颈 12 节）", 22))
    tpose = turtle_pose(facing=1)
    b = assemble(PP.TURTLE_RIG, tp, tpose, 900, 900, (375, 560), 2.7) * lamp
    panels.append(label(to_img(b), "乌龟 · 床单上的样子（透光）", 22))
    rb, cb = assemble(PP.TURTLE_RIG, tp, tpose, 900, 900, (375, 560), 2.7, "refl")
    panels.append(label(to_img((rb * cb[..., None] + bg * (1 - cb[..., None])) * 2.3), "乌龟 · 从后台看到的皮面", 22, color=(230, 220, 200)))
    t2 = turtle_pose(facing=1, head_out=0.0)
    c2 = assemble(PP.TURTLE_RIG, tp, t2, 900, 900, (375, 560), 2.7) * lamp
    panels.append(label(to_img(c2), "乌龟 · 缩头（头颈片滑进壳下）", 22))
    S = sheet(panels, 3, "皮影设计：鹤与乌龟（湖南皮影风格，造型原创）",
              "刮薄的牛皮，阳刻为主；鹤身刻成鳞羽网格（透光才是白鹤），黑蓑羽刻亮线；乌龟背甲按脊盾、肋盾、缘盾刻生长纹。签子平端，鹤两根（身、头），龟一根（壳）+ 头签。")
    S.save(out / "puppets.png")


# ---------------------------------------------------------------- 堂屋光照状态
def room_states(out):
    from .style_samples import STYLES
    cs = L.CAMERAS[0]
    cam = Camera(cs.pos, cs.target, cs.hfov_deg)
    lp_h = L.LAMP_HELD
    lp_s = L.LAMP_STAGE
    fp = L.FLASHLIGHT_PROP
    states = [
        ("1 日光灯（开场）", room.RoomState(clothes_on_wire=True), [LS.tube_light(), LS.tv_light(0.3), LS.moon_light(0.4)], None, 0.9),
        ("2 停电：只剩月光", room.RoomState(clothes_on_wire=True, tv_on=False), [LS.moon_light(1.6), LS.window_sky(8.0)], None, 26.0),
        ("3 马灯点亮（立柜旁）", room.RoomState(clothes_on_wire=True, tv_on=False),
         LS.lamp_lights((lp_h.x, lp_h.y, lp_h.z), 0.4) + [LS.moon_light(1.0), LS.window_sky(2.5)], (lp_h.x, lp_h.y, lp_h.z), 9.0),
        ("4 搭台后：马灯在床单后", room.RoomState(sheet_hung=True, tv_on=False),
         LS.lamp_lights((lp_s.x, lp_s.y, lp_s.z), 0.4) + [LS.moon_light(1.0), LS.window_sky(2.5)], (lp_s.x, lp_s.y, lp_s.z), 4.0),
        ("5 来电：日光灯 + 马灯 + 手电", room.RoomState(sheet_hung=True, tv_on=True),
         [LS.tube_light()] + LS.lamp_lights((lp_s.x, lp_s.y, lp_s.z), 0.4) + [LS.flashlight((fp.x, fp.y, fp.z), (1.35, 4.0, 1.3)), LS.tv_light(0.3), LS.moon_light(0.4)],
         (lp_s.x, lp_s.y, lp_s.z), 0.9),
        ("6 关灯后：马灯重新显出来", room.RoomState(sheet_hung=True, tv_on=False, fan_angle=0.5),
         LS.lamp_lights((lp_s.x, lp_s.y, lp_s.z), 0.4) + [LS.flashlight((fp.x, fp.y, fp.z), (1.35, 4.0, 1.3)), LS.moon_light(1.0), LS.window_sky(2.5)],
         (lp_s.x, lp_s.y, lp_s.z), 4.0),
    ]
    rows = {s: [] for s in ("lantern", "woodcut", "silk")}
    assets = PuppetAssets()
    for nm, st, ls, lamp_pos, exp in states:
        st.textures = assets.room_tex
        pl = room.build(st)
        if lamp_pos is not None:
            LS.lamp_geometry(pl, lamp_pos, hang_z=L.LAMP_PURLIN_Z if lamp_pos[1] > 4.5 else None)
        sc = rt.Scene(pl, assets.A, assets.R)
        names = [f"l{k}" for k in range(len(ls))]
        buf = frame.render_ss(sc, cam, ls, names, 640, 360, ss=2, keep_mats=(M("sheet"),), vpl_n=32)
        ctx = dict(cam=cam, exposure=exp, chars=None, faces=[], extra=None, scene_names=sc.names,
                   tv="on" if st.tv_on else "off", phone="charge" if "来电" in nm else ("game" if "日光灯" in nm else "off"),
                   sources=[dict(kind="lamp", pos=lamp_pos, intensity=0.6)] if lamp_pos is not None else [])
        for s in rows:
            img = STYLES[s](buf, sc, ctx)
            rows[s].append(label(img, nm, 20, color=(245, 235, 215)))
        print("room state", nm, flush=True)
    panels = rows["lantern"] + rows["woodcut"] + rows["silk"]
    S = sheet(panels, 6, "堂屋的六种光照状态（上：A 灯影；中：B 刻光；下：C 绢灯）",
              "全景机位 A。每种光都有清楚的光源和方向，影子跟着光源走。")
    S.save(out / "room_lighting.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--only", default="characters,scale,expressions,poses,hands,lights,puppets,room")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    todo = a.only.split(",")
    fns = {"characters": turnaround, "scale": scale, "expressions": expressions, "poses": poses, "hands": hands,
           "lights": lights, "puppets": puppets, "room": room_states}
    for k in todo:
        print("==", k, flush=True)
        fns[k](out)


if __name__ == "__main__":
    main()
