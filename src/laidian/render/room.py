"""根据 layout 搭出堂屋的三维几何。

所有尺寸都来自 laidian.layout；这里只负责把它们变成几何体，并补上细节
（门框、窗棂、屋架、家具的腿和抽屉……）。
"""
import math
from dataclasses import dataclass, field

import numpy as np

from .. import layout as L
from .materials import M
from .rt import F_ALPHA, F_NOVIS, F_SHADOW, F_TRANSMIT, PrimList

RIDGE_Z = 4.30
RIDGE_Y = L.ROOM_D / 2
EAVE_Z = L.ROOM_H


@dataclass
class RoomState:
    """随剧情变化的布景状态。"""
    sheet_hung: bool = False
    clothes_on_wire: bool = True
    lamp_at: str = "cabinet"        # cabinet / chest / stage / none
    fan_angle: float = 0.0          # 吊扇叶片角度（弧度）
    tv_on: bool = True
    back_door_open: bool = True
    main_door_open: float = 0.0     # 0 关 → 1 开
    textures: dict = field(default_factory=dict)  # 名称 -> 图集编号


def roof_z(y):
    """屋面下沿高度（两坡顶）。"""
    return EAVE_Z + (RIDGE_Z - EAVE_Z) * (1 - abs(y - RIDGE_Y) / RIDGE_Y)


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def _wall(pl, wall, lo, hi, z_top, openings, mat):
    """沿墙方向 [lo, hi] 生成墙体，挖掉洞口。"""
    T = L.WALL_T
    ops = sorted([(a0, a1, z0, z1) for (w, a0, a1, z0, z1, _) in openings if w == wall])
    cuts = sorted({lo, hi, *[a for o in ops for a in o[:2]]})

    def emit(a0, a1, z0, z1):
        if a1 - a0 < 1e-6 or z1 - z0 < 1e-6:
            return
        if wall == "S":
            pl.box(mat, a0, a1, -T, 0.0, z0, z1, name=f"wall_S")
        elif wall == "N":
            pl.box(mat, a0, a1, L.ROOM_D, L.ROOM_D + T, z0, z1, name=f"wall_N")
        elif wall == "W":
            pl.box(mat, -T, 0.0, a0, a1, z0, z1, name=f"wall_W")
        else:
            pl.box(mat, L.ROOM_W, L.ROOM_W + T, a0, a1, z0, z1, name=f"wall_E")

    for a0, a1 in zip(cuts, cuts[1:]):
        mid = (a0 + a1) / 2
        hit = [o for o in ops if o[0] <= mid <= o[1]]
        if hit:
            o = hit[0]
            emit(a0, a1, 0.0, o[2])
            emit(a0, a1, o[3], z_top)
        else:
            emit(a0, a1, 0.0, z_top)


def build(state: RoomState) -> PrimList:
    pl = PrimList()
    T = L.WALL_T
    W, D = L.ROOM_W, L.ROOM_D
    tex = state.textures

    # ---------------- 地面（向外延伸成屋外的禾场）
    pl.box(M("concrete"), -12, W + 12, -30, D + 4, -0.3, 0.0, name="floor")

    # ---------------- 墙
    ops = list(L.OPENINGS.values())
    _wall(pl, "S", -T, W + T, EAVE_Z, ops, M("plaster"))
    _wall(pl, "N", -T, W + T, EAVE_Z, ops, M("plaster"))
    # 山墙到屋脊（室内看不到超出屋面的部分）
    _wall(pl, "W", 0.0, D, RIDGE_Z + 0.2, ops, M("plaster"))
    _wall(pl, "E", 0.0, D, RIDGE_Z + 0.2, ops, M("plaster"))

    # ---------------- 屋架：檩条（沿 x 的圆木）、椽子（沿坡）、瓦
    for y in (0.30, 0.85, 1.40, 1.95, RIDGE_Y, 3.05, 3.60, 4.15, 4.70):
        z = roof_z(y) - 0.075
        pl.cyl(M("beam"), (-T, y, z), (W + T, y, z), 0.075 if y != RIDGE_Y else 0.10, name="purlin")
    slope = math.atan2(RIDGE_Z - EAVE_Z, RIDGE_Y)
    run = math.hypot(RIDGE_Y, RIDGE_Z - EAVE_Z)
    nraf = 24
    for side in (0, 1):
        ang = slope if side == 0 else -slope
        yc = RIDGE_Y / 2 if side == 0 else RIDGE_Y * 1.5
        zc = (EAVE_Z + RIDGE_Z) / 2 + 0.015
        for k in range(nraf):
            x = 0.12 + k * (W - 0.24) / (nraf - 1)
            pl.obox(M("beam"), (x, yc, zc), (0.035, run / 2, 0.018), R=rot_x(ang), name="rafter")
        # 瓦面
        pl.obox(M("roof_tile"), (W / 2, yc, zc + 0.05), (W / 2 + T, run / 2 + 0.05, 0.03), R=rot_x(ang), name="tiles")
    # 穿梁：横跨堂屋，挂日光灯
    tie_y = 2.0
    pl.box(M("beam"), -T, W + T, tie_y - 0.08, tie_y + 0.08, 3.17, 3.33, name="tie_beam")

    # ---------------- 后屋（简单的盒子，暗）
    BD = 2.3
    pl.box(M("plaster"), -T, W + T, D + T + BD, D + 2 * T + BD, 0.0, 3.0, name="backroom_wall")
    pl.box(M("plaster"), -T - 0.0, 0.0 - 0.0, D + T, D + T + BD, 0.0, 3.0, name="backroom_wall_w")
    pl.box(M("plaster"), W, W + T, D + T, D + T + BD, 0.0, 3.0, name="backroom_wall_e")
    pl.box(M("beam"), -T, W + T, D + T, D + 2 * T + BD, 2.75, 2.85, name="backroom_ceiling")
    # 后屋里的杂物：米袋、箩筐、锄头
    pl.box(M("paper"), 0.3, 0.8, D + T + 1.4, D + T + 1.9, 0.0, 0.55, name="rice_bag")
    pl.cyl(M("broom"), (1.2, D + T + 1.8, 0.0), (1.2, D + T + 1.8, 0.45), 0.25, name="basket")
    pl.cyl(M("wood_raw"), (2.2, D + T + 2.2, 0.0), (2.4, D + T + 2.1, 1.5), 0.018, name="hoe_handle")

    # ---------------- 门窗
    # 南窗：窗框、窗棂、玻璃、纱窗
    wx0, wx1, wz0, wz1 = L.OPENINGS["window_s"][1:5]
    fr = 0.05
    pl.box(M("door_wood"), wx0, wx1, -T, 0.0, wz0, wz0 + fr, name="win_frame")
    pl.box(M("door_wood"), wx0, wx1, -T, 0.0, wz1 - fr, wz1, name="win_frame")
    pl.box(M("door_wood"), wx0, wx0 + fr, -T, 0.0, wz0, wz1, name="win_frame")
    pl.box(M("door_wood"), wx1 - fr, wx1, -T, 0.0, wz0, wz1, name="win_frame")
    pl.box(M("door_wood"), (wx0 + wx1) / 2 - 0.02, (wx0 + wx1) / 2 + 0.02, -T, 0.0, wz0, wz1, name="win_mullion")
    pl.box(M("door_wood"), wx0, wx1, -T, 0.0, (wz0 + wz1) / 2 - 0.015, (wz0 + wz1) / 2 + 0.015, name="win_transom")
    g = pl.quad(M("glass"), (wx0, -0.10, wz0), (wx1 - wx0, 0, 0), (0, 0, wz1 - wz0), flags=F_SHADOW | F_TRANSMIT, name="win_glass")
    pl.rows[g][20] = 0.85
    sc = pl.quad(M("screen"), (wx0, -0.03, wz0), (wx1 - wx0, 0, 0), (0, 0, wz1 - wz0), flags=F_SHADOW | F_TRANSMIT, name="win_screen")
    pl.rows[sc][20] = 0.6
    # 窗台
    pl.box(M("concrete"), wx0 - 0.05, wx1 + 0.05, -T - 0.02, 0.04, wz0 - 0.04, wz0, name="win_sill")

    # 大门：两扇关着的木门
    dx0, dx1, dz0, dz1 = L.OPENINGS["door_main"][1:5]
    half = (dx1 - dx0) / 2
    for k in range(2):
        a0 = dx0 + k * half
        pl.box(M("door_wood"), a0 + 0.005, a0 + half - 0.005, -0.12, -0.07, 0.0, dz1, name="main_door")
    pl.box(M("wood_raw"), dx0 + 0.2, dx1 - 0.2, -0.07, -0.03, 1.15, 1.20, name="door_bar")  # 门闩
    for x in (dx0, dx1):
        pl.box(M("door_wood"), x - 0.06, x + 0.06, -T - 0.01, 0.01, 0.0, dz1 + 0.08, name="door_frame")
    pl.box(M("door_wood"), dx0 - 0.06, dx1 + 0.06, -T - 0.01, 0.01, dz1, dz1 + 0.10, name="door_lintel")

    # 后屋门：门框 + 打开的门扇（推向后屋）
    bx0, bx1, bz0, bz1 = L.OPENINGS["door_back"][1:5]
    for x in (bx0, bx1):
        pl.box(M("door_wood"), x - 0.05, x + 0.05, D - 0.01, D + T + 0.01, 0.0, bz1 + 0.06, name="back_frame")
    pl.box(M("door_wood"), bx0 - 0.05, bx1 + 0.05, D - 0.01, D + T + 0.01, bz1, bz1 + 0.09, name="back_lintel")
    if state.back_door_open:
        w = bx1 - bx0 - 0.02
        pl.obox(M("door_wood"), (bx0 + 0.03, D + T + w / 2, bz1 / 2), (0.022, w / 2, bz1 / 2 - 0.01), ang=0.0, name="back_door_leaf")

    # 东屋门（关着）
    ey0, ey1, ez0, ez1 = L.OPENINGS["door_east"][1:5]
    pl.box(M("door_wood"), W + 0.06, W + 0.11, ey0, ey1, 0.0, ez1, name="east_door")
    for y in (ey0, ey1):
        pl.box(M("door_wood"), W - 0.01, W + T + 0.01, y - 0.05, y + 0.05, 0.0, ez1 + 0.06, name="east_frame")
    pl.box(M("door_wood"), W - 0.01, W + T + 0.01, ey0 - 0.05, ey1 + 0.05, ez1, ez1 + 0.09, name="east_lintel")

    # ---------------- 木柱 + 石础，晾衣铁丝
    c = L.COLUMN
    pl.cyl(M("column"), (c.x, c.y, 0.18), (c.x, c.y, roof_z(c.y)), L.COLUMN_R, name="column")
    pl.cyl(M("stone"), (c.x, c.y, 0.0), (c.x, c.y, 0.18), L.COLUMN_R + 0.06, name="column_base")
    pl.cyl(M("wire"), (0.0, L.WIRE_Y, L.WIRE_Z), (c.x - L.COLUMN_R, L.WIRE_Y, L.WIRE_Z), 0.0025, name="wire")

    # ---------------- 电器
    t = L.TUBE
    pl.box(M("plastic_white"), t.x0 - 0.04, t.x1 + 0.04, t.y0 - 0.03, t.y1 + 0.03, 3.155, 3.17, name="tube_fixture")
    pl.cyl(M("tube_glass"), (t.x0, (t.y0 + t.y1) / 2, 3.14), (t.x1, (t.y0 + t.y1) / 2, 3.14), 0.016, flags=0, name="tube")
    # 吊扇：吊杆、电机、三片叶子
    f = L.FAN
    pl.cyl(M("metal"), (f.x, f.y, f.z + 0.08), (f.x, f.y, roof_z(f.y) - 0.05), 0.012, name="fan_rod")
    pl.ell(M("metal"), (f.x, f.y, f.z + 0.03), (0.11, 0.11, 0.07), name="fan_motor")
    for k in range(3):
        a = state.fan_angle + k * 2 * math.pi / 3
        R = rot_z(a)
        cx = f.x + math.cos(a) * (0.14 + L.FAN_R / 2 - 0.07)
        cy = f.y + math.sin(a) * (0.14 + L.FAN_R / 2 - 0.07)
        tilt = rot_x(0.12)
        pl.obox(M("metal"), (cx, cy, f.z), (L.FAN_R / 2 - 0.07, 0.055, 0.004), R=R @ tilt, name="fan_blade")
    # 拉线开关 + 灯绳
    s = L.PULL_SWITCH
    pl.cyl(M("plastic_white"), (s.x, 0.0, s.z), (s.x, 0.035, s.z), 0.03, name="pull_switch")
    pl.cyl(M("wire"), (s.x, 0.04, s.z - 0.01), (s.x, 0.05, L.PULL_CORD_END_Z + 0.03), 0.0015, name="pull_cord")
    pl.ell(M("plastic_white"), (s.x, 0.05, L.PULL_CORD_END_Z), (0.008, 0.008, 0.025), name="pull_bead")
    r = L.FAN_REGULATOR
    pl.box(M("plastic_white"), r.x - 0.045, r.x + 0.045, 0.0, 0.025, r.z - 0.06, r.z + 0.06, name="fan_regulator")
    so = L.SOCKET
    pl.box(M("plastic_white"), 0.0, 0.015, so.y - 0.043, so.y + 0.043, so.z - 0.043, so.z + 0.043, name="socket")

    # ---------------- 家具
    fur = {b.name: b for b in L.FURNITURE}
    b = fur["mat"]
    pl.box(M("bamboo"), b.x0, b.x1, b.y0, b.y1, 0.0, 0.006, name="mat")

    b = fur["tv_cabinet"]
    pl.box(M("wood_dark"), b.x0, b.x1, b.y0, b.y1, 0.10, b.z1, name="tv_cabinet")
    for (yy, xx) in ((b.y0 + 0.03, b.x1 - 0.03), (b.y1 - 0.03, b.x1 - 0.03), (b.y0 + 0.03, b.x0 + 0.03), (b.y1 - 0.03, b.x0 + 0.03)):
        pl.box(M("wood_dark"), xx - 0.025, xx + 0.025, yy - 0.025, yy + 0.025, 0.0, 0.10, name="tv_cab_leg")
    for k in range(2):  # 两个抽屉
        y0 = b.y0 + 0.05 + k * (b.y1 - b.y0 - 0.1) / 2
        y1 = y0 + (b.y1 - b.y0 - 0.1) / 2 - 0.02
        pl.box(M("wood_dark"), b.x1, b.x1 + 0.012, y0, y1, 0.50, 0.66, name="drawer")
        pl.box(M("brass"), b.x1 + 0.012, b.x1 + 0.025, (y0 + y1) / 2 - 0.04, (y0 + y1) / 2 + 0.04, 0.575, 0.59, name="drawer_handle")
    tv = fur["tv"]
    pl.box(M("tv_body"), tv.x0 + 0.08, tv.x1 - 0.02, tv.y0 + 0.05, tv.y1 - 0.05, tv.z0, tv.z1 - 0.02, name="tv_back")
    pl.box(M("tv_body"), tv.x1 - 0.10, tv.x1, tv.y0, tv.y1, tv.z0, tv.z1, name="tv_front")
    # 显像管屏幕：微微凸出的椭球面
    pl.ell(M("tv_screen"), (tv.x1 - 0.06, (tv.y0 + tv.y1) / 2 - 0.05, (tv.z0 + tv.z1) / 2 + 0.02), (0.065, 0.21, 0.165), name="tv_screen")
    pl.cyl(M("tv_body"), (tv.x1, tv.y1 - 0.07, tv.z0 + 0.30), (tv.x1 + 0.015, tv.y1 - 0.07, tv.z0 + 0.30), 0.012, name="tv_knob")
    pl.cyl(M("tv_body"), (tv.x1, tv.y1 - 0.07, tv.z0 + 0.20), (tv.x1 + 0.015, tv.y1 - 0.07, tv.z0 + 0.20), 0.012, name="tv_knob")
    # 天线（兔耳朵）
    for a in (-0.5, 0.45):
        top = (tv.x0 + 0.25 + 0.25 * math.sin(a), (tv.y0 + tv.y1) / 2 + 0.35 * math.sin(a), tv.z1 + 0.42)
        pl.cyl(M("metal"), (tv.x0 + 0.25, (tv.y0 + tv.y1) / 2, tv.z1), top, 0.003, name="tv_antenna")

    b = fur["table"]
    top_t = 0.045
    pl.box(M("wood_dark"), b.x0, b.x1, b.y0, b.y1, b.z1 - top_t, b.z1, name="table_top")
    for (xx, yy) in ((b.x0 + 0.04, b.y0 + 0.04), (b.x1 - 0.04, b.y0 + 0.04), (b.x0 + 0.04, b.y1 - 0.04), (b.x1 - 0.04, b.y1 - 0.04)):
        pl.box(M("wood_dark"), xx - 0.035, xx + 0.035, yy - 0.035, yy + 0.035, 0.0, b.z1 - top_t, name="table_leg")
    pl.box(M("wood_dark"), b.x0 + 0.04, b.x1 - 0.04, b.y0 + 0.02, b.y0 + 0.05, b.z1 - 0.14, b.z1 - top_t, name="table_apron")
    pl.box(M("wood_dark"), b.x0 + 0.04, b.x1 - 0.04, b.y1 - 0.05, b.y1 - 0.02, b.z1 - 0.14, b.z1 - top_t, name="table_apron")
    pl.box(M("wood_dark"), b.x0 + 0.02, b.x0 + 0.05, b.y0 + 0.04, b.y1 - 0.04, b.z1 - 0.14, b.z1 - top_t, name="table_apron")
    pl.box(M("wood_dark"), b.x1 - 0.05, b.x1 - 0.02, b.y0 + 0.04, b.y1 - 0.04, b.z1 - 0.14, b.z1 - top_t, name="table_apron")
    # 桌上：西瓜（盘子里的一块）、暖水瓶、搪瓷杯
    tz = b.z1
    pl.disc(M("enamel"), (3.40, 2.05, tz + 0.012), (0, 0, 1), 0.11, name="plate")
    pl.cyl(M("enamel"), (3.40, 2.05, tz), (3.40, 2.05, tz + 0.012), 0.10, name="plate_base")
    pl.obox(M("watermelon_red"), (3.40, 2.05, tz + 0.06), (0.07, 0.012, 0.045), ang=0.6, name="melon_slice")
    pl.cyl(M("thermos"), (3.85, 2.45, tz), (3.85, 2.45, tz + 0.30), 0.055, name="thermos")
    pl.cyl(M("wood_raw"), (3.85, 2.45, tz + 0.30), (3.85, 2.45, tz + 0.34), 0.03, name="thermos_cork")
    for (xx, yy) in ((3.62, 2.48), (3.70, 2.30)):
        pl.cyl(M("enamel"), (xx, yy, tz), (xx, yy, tz + 0.09), 0.04, name="enamel_cup")

    for nm in ("bench_n", "bench_e"):
        b = fur[nm]
        pl.box(M("wood_raw"), b.x0, b.x1, b.y0, b.y1, b.z1 - 0.04, b.z1, name=nm)
        lx = (b.x1 - b.x0) > (b.y1 - b.y0)
        for e in (0, 1):
            if lx:
                xx = b.x0 + 0.08 if e == 0 else b.x1 - 0.08
                pl.box(M("wood_raw"), xx - 0.02, xx + 0.02, b.y0 + 0.03, b.y1 - 0.03, 0.0, b.z1 - 0.04, name="bench_leg")
            else:
                yy = b.y0 + 0.08 if e == 0 else b.y1 - 0.08
                pl.box(M("wood_raw"), b.x0 + 0.03, b.x1 - 0.03, yy - 0.02, yy + 0.02, 0.0, b.z1 - 0.04, name="bench_leg")

    for nm in ("stool_nainai", "stool_xiaoman"):
        b = fur[nm]
        if nm == "stool_xiaoman" and not state.sheet_hung:
            continue
        pl.box(M("wood_raw"), b.x0, b.x1, b.y0, b.y1, b.z1 - 0.03, b.z1, name=nm)
        for (xx, yy) in ((b.x0 + 0.03, b.y0 + 0.03), (b.x1 - 0.03, b.y0 + 0.03), (b.x0 + 0.03, b.y1 - 0.03), (b.x1 - 0.03, b.y1 - 0.03)):
            pl.box(M("wood_raw"), xx - 0.015, xx + 0.015, yy - 0.015, yy + 0.015, 0.0, b.z1 - 0.03, name="stool_leg")

    b = fur["basin"]
    cxy = ((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2)
    pl.cyl(M("enamel"), (cxy[0], cxy[1], 0.0), (cxy[0], cxy[1], 0.09), 0.15, name="basin")
    pl.disc(M("soybean"), (cxy[0], cxy[1], 0.07), (0, 0, 1), 0.135, name="beans")

    b = fur["chest"]
    pl.box(M("chest"), b.x0, b.x1, b.y0, b.y1, 0.0, b.z1, name="chest")
    pl.box(M("brass"), (b.x0 + b.x1) / 2 - 0.03, (b.x0 + b.x1) / 2 + 0.03, b.y0 - 0.008, b.y0, b.z1 - 0.10, b.z1 - 0.03, name="chest_lock")

    b = fur["altar_table"]
    pl.box(M("wood_dark"), b.x0, b.x1, b.y0, b.y1, b.z1 - 0.05, b.z1, name="altar_top")
    for xx in (b.x0 + 0.05, b.x1 - 0.05):
        pl.box(M("wood_dark"), xx - 0.04, xx + 0.04, b.y0 + 0.03, b.y1 - 0.03, 0.0, b.z1 - 0.05, name="altar_leg")
    pl.box(M("wood_dark"), b.x0 + 0.05, b.x1 - 0.05, b.y0 + 0.01, b.y0 + 0.03, b.z1 - 0.20, b.z1 - 0.05, name="altar_apron")
    # 条台上：座钟、暖水瓶、收音机、塑料花瓶
    az = b.z1
    pl.box(M("wood_dark"), 3.15, 3.38, 4.72, 4.88, az, az + 0.36, name="clock")
    pl.disc(M("enamel"), (3.265, 4.715, az + 0.24), (0, -1, 0), 0.085, name="clock_face")
    pl.cyl(M("thermos"), (4.45, 4.80, az), (4.45, 4.80, az + 0.32), 0.055, name="thermos2")
    pl.box(M("tv_body"), 4.00, 4.32, 4.74, 4.88, az, az + 0.18, name="radio")
    pl.cyl(M("enamel"), (2.98, 4.80, az), (2.98, 4.80, az + 0.20), 0.05, name="vase")

    b = fur["cabinet"]
    pl.box(M("wood_dark"), b.x0, b.x1, b.y0, b.y1, 0.0, b.z1, name="cabinet")
    pl.box(M("wood_dark"), b.x0 - 0.012, b.x0, b.y0 + 0.04, (b.y0 + b.y1) / 2 - 0.01, 0.15, b.z1 - 0.06, name="cabinet_door")
    pl.box(M("wood_dark"), b.x0 - 0.012, b.x0, (b.y0 + b.y1) / 2 + 0.01, b.y1 - 0.04, 0.15, b.z1 - 0.06, name="cabinet_door")

    b = fur["coil"]
    pl.disc(M("metal"), ((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, 0.01), (0, 0, 1), 0.07, name="coil_tray")
    b = fur["broom"]
    pl.cyl(M("broom"), (4.68, 0.12, 0.0), (4.70, 0.10, 0.35), 0.07, name="broom_head")
    pl.cyl(M("wood_raw"), (4.70, 0.10, 0.35), (4.72, 0.08, 1.20), 0.012, name="broom_handle")

    # ---------------- 墙上的东西（贴图四边形，离墙 5 毫米）
    def wall_quad(wall, a0, a1, z0, z1, mat, name, texname=None, off=0.005):
        tid = tex.get(texname, -1) if texname else -1
        if wall == "N":
            o, u, v = (a0, D - off, z0), (a1 - a0, 0, 0), (0, 0, z1 - z0)
        elif wall == "S":
            o, u, v = (a1, off, z0), (a0 - a1, 0, 0), (0, 0, z1 - z0)
        elif wall == "W":
            o, u, v = (off, a1, z0), (0, a0 - a1, 0), (0, 0, z1 - z0)
        else:
            o, u, v = (W - off, a0, z0), (0, a1 - a0, 0), (0, 0, z1 - z0)
        return pl._add(4, mat, [*o, *u, *v], F_SHADOW, tid, name)

    for (wall, a0, a1, z0, z1, label) in L.WALL_ITEMS:
        if "中堂" in label:
            wall_quad(wall, a0, a1, z0, z1, M("image") if "painting" in tex else M("paper"), "painting", "painting")
        elif "对联" in label:
            wall_quad(wall, a0, a1, z0, z1, M("image") if "couplet_l" in tex else M("paper_red"), "couplet",
                      "couplet_l" if a0 < 3.5 else "couplet_r")
        elif "相框" in label:
            pl.box(M("wood_dark"), a0 - 0.02, a1 + 0.02, D - 0.03, D, z0 - 0.02, z1 + 0.02, name="photo_frame")
            wall_quad(wall, a0, a1, z0, z1, M("image") if "photos" in tex else M("paper"), "photos", "photos", off=0.032)
        elif "挂历" in label:
            wall_quad(wall, a0, a1, z0, z1, M("image") if "calendar" in tex else M("paper"), "calendar", "calendar")
        elif "奖状" in label:
            wall_quad(wall, a0, a1, z0, z1, M("image") if "certificate" in tex else M("paper"), "certificate", "certificate")
        elif "衣服" in label:
            pl.cyl(M("metal"), (W, (a0 + a1) / 2, z1), (W - 0.04, (a0 + a1) / 2, z1), 0.004, name="cloth_nail")
            wall_quad(wall, a0, a1, z0, z1 - 0.05, M("cloth_blouse"), "hanging_cloth", off=0.03)

    # ---------------- 床单（第 5 场起）：搭在铁丝上，顶上一截折过去是两层
    if state.sheet_hung:
        sh = L.SHEET
        pl.quad(M("sheet"), (sh.x0, L.WIRE_Y, sh.z0), (sh.x1 - sh.x0, 0, 0), (0, 0, sh.z1 - sh.z0), name="sheet")
        k = pl.quad(M("sheet"), (sh.x0, L.WIRE_Y + 0.004, sh.z1 - 0.16), (sh.x1 - sh.x0, 0, 0), (0, 0, 0.16),
                    flags=F_SHADOW | F_TRANSMIT, name="sheet_fold")
        pl.rows[k][20] = 0.45
        for k in range(6):
            x = sh.x0 + 0.06 + k * (sh.x1 - sh.x0 - 0.12) / 5
            pl.box(M("wood_raw"), x - 0.006, x + 0.006, L.WIRE_Y - 0.008, L.WIRE_Y + 0.008, L.WIRE_Z - 0.06, L.WIRE_Z + 0.012, name="clothespin")

    # ---------------- 晾衣铁丝上的东西
    if state.clothes_on_wire and not state.sheet_hung:
        pl.quad(M("cloth_towel"), (0.45, L.WIRE_Y, L.WIRE_Z - 0.62), (0.38, 0, 0), (0, 0, 0.62), name="towel")
        pl.quad(M("cloth_tshirt"), (1.05, L.WIRE_Y + 0.002, L.WIRE_Z - 0.55), (0.50, 0, 0), (0, 0, 0.55), name="tshirt")
        pl.quad(M("cloth_blouse"), (1.75, L.WIRE_Y - 0.002, L.WIRE_Z - 0.60), (0.48, 0, 0), (0, 0, 0.60), name="blouse")
    elif state.sheet_hung:
        # 衣服被推到铁丝东头，挤成一堆
        x0 = L.SHEET.x1 + 0.06
        pl.quad(M("cloth_towel"), (x0, L.WIRE_Y - 0.004, L.WIRE_Z - 0.58), (0.14, 0, 0), (0, 0, 0.58), name="towel")
        pl.quad(M("cloth_tshirt"), (x0 + 0.08, L.WIRE_Y, L.WIRE_Z - 0.52), (0.16, 0, 0), (0, 0, 0.52), name="tshirt")
        pl.quad(M("cloth_blouse"), (x0 + 0.18, L.WIRE_Y + 0.004, L.WIRE_Z - 0.57), (0.18, 0, 0), (0, 0, 0.57), name="blouse")

    return pl
