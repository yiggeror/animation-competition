"""画堂屋平面图和戏台剖面图（数据全部来自 laidian.layout）。

用法：python tools/draw_floorplan.py
输出：docs/preproduction/floorplan.png, docs/preproduction/stage-section.png
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from laidian import layout as L  # noqa: E402

FONT = str(ROOT / "assets/fonts/NotoSansSC-VF.ttf")
OUT = ROOT / "docs/preproduction"

S = 150          # 像素/米
M = 170          # 边距
INK = (40, 36, 32)
WALL = (88, 80, 72)
PAPER = (247, 243, 234)
WARM = (214, 128, 40)
COLD = (70, 120, 190)
GREEN = (60, 130, 90)


def rect(d, xy, **kw):
    (x0, y0), (x1, y1) = (xy[0], xy[1]) if len(xy) == 2 else ((xy[0], xy[1]), (xy[2], xy[3]))
    d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], **kw)


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def plan():
    W = int(L.ROOM_W * S + 2 * M + 520)
    H = int(L.ROOM_D * S + 2 * M + 60)
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    def P(x, y):  # 平面坐标 -> 像素（北在上）
        return (M + x * S, M + (L.ROOM_D - y) * S)

    t = L.WALL_T
    # 墙
    for (x0, y0, x1, y1) in [(-t, -t, L.ROOM_W + t, 0), (-t, L.ROOM_D, L.ROOM_W + t, L.ROOM_D + t),
                             (-t, 0, 0, L.ROOM_D), (L.ROOM_W, 0, L.ROOM_W + t, L.ROOM_D)]:
        a, b = P(x0, y1), P(x1, y0)
        rect(d, [a, b], fill=WALL)
    # 洞口
    for key, (wall, a0, a1, z0, z1, label) in L.OPENINGS.items():
        if wall == "S":
            box = (a0, -t, a1, 0)
        elif wall == "N":
            box = (a0, L.ROOM_D, a1, L.ROOM_D + t)
        elif wall == "E":
            box = (L.ROOM_W, a0, L.ROOM_W + t, a1)
        else:
            box = (-t, a0, 0, a1)
        p0, p1 = P(box[0], box[3]), P(box[2], box[1])
        fill = (190, 215, 235) if "window" in key else PAPER
        rect(d, [p0, p1], fill=fill, outline=INK)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        off = {"S": (0, 28), "N": (0, -30), "E": (-150, 0), "W": (-60, 0)}[wall]
        d.text((cx + off[0], cy + off[1]), label, fill=INK, font=font(19), anchor="mm")
    # 后屋（示意）
    d.text(P(1.45, L.ROOM_D + 0.75), "后屋（杂物，暗）", fill=WALL, font=font(20), anchor="mm")
    d.text(P(L.ROOM_W / 2, -0.85), "南  ·  屋外：禾场、村子", fill=WALL, font=font(20), anchor="mm")

    # 家具
    for b in L.FURNITURE:
        p0, p1 = P(b.x0, b.y1), P(b.x1, b.y0)
        col = (226, 214, 190) if b.name != "mat" else (222, 214, 160)
        if b.name in ("stool_xiaoman",):
            col = (235, 222, 200)
        rect(d, [p0, p1], fill=col, outline=INK, width=2)
        if b.name == "mat":
            for i in range(1, 12):
                xx = b.x0 + (b.x1 - b.x0) * i / 12
                d.line([P(xx, b.y0), P(xx, b.y1)], fill=(190, 178, 120), width=1)
    labels = {
        "mat": (1.10, 1.25, "竹席"), "tv_cabinet": (0.95, 3.45, "电视柜\n显像管电视"),
        "stool_nainai": (2.30, 1.25, "奶奶的小板凳"), "basin": (2.10, 2.15, "毛豆盆"),
        "table": (3.58, 2.22, "八仙桌\n(西瓜·搪瓷杯·暖水瓶)"), "bench_n": (3.58, 3.18, "长凳"),
        "bench_e": (4.62, 2.22, "长凳"), "chest": (0.48, 4.72, "旧木箱"),
        "altar_table": (3.85, 4.78, "条台"), "cabinet": (5.09, 4.25, "立柜"),
        "stool_xiaoman": (1.75, 3.30, "小满看戏的板凳(5场起)"), "coil": (2.02, 0.80, "蚊香"),
        "broom": (4.68, 0.45, "扫帚"),
    }
    for name, (x, y, text) in labels.items():
        d.multiline_text(P(x, y), text, fill=INK, font=font(17), anchor="mm", align="center")

    # 墙上物件
    for wall, a0, a1, z0, z1, label in L.WALL_ITEMS:
        if wall == "N":
            p0, p1 = P(a0, L.ROOM_D - 0.06), P(a1, L.ROOM_D)
            tp = P((a0 + a1) / 2, L.ROOM_D - 0.32)
        elif wall == "W":
            p0, p1 = P(0, a1), P(0.06, a0)
            tp = P(0.62, (a0 + a1) / 2)
        else:
            p0, p1 = P(L.ROOM_W - 0.06, a1), P(L.ROOM_W, a0)
            tp = P(L.ROOM_W - 0.62, (a0 + a1) / 2)
        rect(d, [p0, p1], fill=(170, 60, 50))
    d.text(P(3.85, 4.40), "中堂画·对联·大相框（北墙）", fill=(150, 50, 40), font=font(16), anchor="mm")
    d.text(P(0.55, 1.85), "挂历", fill=(150, 50, 40), font=font(16), anchor="mm")
    d.text(P(0.55, 3.75), "奖状", fill=(150, 50, 40), font=font(16), anchor="mm")

    # 立柱和铁丝、床单
    cx, cy = P(L.COLUMN.x, L.COLUMN.y)
    r = L.COLUMN_R * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 80, 50), outline=INK)
    d.text((cx + 30, cy - 22), "木柱", fill=INK, font=font(17), anchor="lm")
    d.line([P(0, L.WIRE_Y), P(L.COLUMN.x, L.WIRE_Y)], fill=(120, 120, 120), width=2)
    d.line([P(L.SHEET.x0, L.WIRE_Y), P(L.SHEET.x1, L.WIRE_Y)], fill=(255, 255, 255), width=9)
    d.line([P(L.SHEET.x0, L.WIRE_Y), P(L.SHEET.x1, L.WIRE_Y)], fill=INK, width=1)
    d.text(P(1.30, L.WIRE_Y - 0.17), "白床单（搭在晾衣铁丝上，5 场起）", fill=INK, font=font(18, 600), anchor="mm")
    d.text(P(1.30, L.WIRE_Y + 0.20), "后台", fill=WARM, font=font(18, 600), anchor="mm")

    # 光源
    def star(x, y, col, rr=13):
        px, py = P(x, y)
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = rr if i % 2 == 0 else rr * 0.45
            pts.append((px + rad * math.cos(ang), py + rad * math.sin(ang)))
        d.polygon(pts, fill=col, outline=INK)

    star(L.LAMP_STAGE.x, L.LAMP_STAGE.y, WARM)
    d.text(P(L.LAMP_STAGE.x + 0.12, L.LAMP_STAGE.y - 0.12), "马灯(5场起)", fill=WARM, font=font(16, 600), anchor="lm")
    star(L.LAMP_CABINET.x, L.LAMP_CABINET.y, WARM, 10)
    d.text(P(L.LAMP_CABINET.x - 0.1, L.LAMP_CABINET.y - 0.2), "马灯原位", fill=WARM, font=font(15), anchor="rm")
    star(L.FLASHLIGHT_PROP.x, L.FLASHLIGHT_PROP.y, COLD, 10)
    d.text(P(L.FLASHLIGHT_PROP.x + 0.1, L.FLASHLIGHT_PROP.y - 0.22), "手电(9场)", fill=COLD, font=font(15, 600), anchor="lm")
    t0, t1 = P(L.TUBE.x0, L.TUBE.y1), P(L.TUBE.x1, L.TUBE.y0)
    rect(d, [t0[0], t0[1] - 4, t1[0], t1[1] + 4], fill=(225, 240, 255), outline=COLD, width=2)
    d.text(P((L.TUBE.x0 + L.TUBE.x1) / 2 - 0.3, L.TUBE.y0 - 0.2), "日光灯管（房梁上）", fill=COLD, font=font(17, 600), anchor="mm")
    fx, fy = P(L.FAN.x, L.FAN.y)
    rr = L.FAN_R * S
    d.ellipse([fx - rr, fy - rr, fx + rr, fy + rr], outline=(150, 150, 150), width=2)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3
        d.line([(fx, fy), (fx + rr * math.cos(a), fy + rr * math.sin(a))], fill=(150, 150, 150), width=5)
    d.text((fx - rr - 8, fy - rr + 10), "吊扇", fill=INK, font=font(17), anchor="mm")
    sx, sy = P(L.PULL_SWITCH.x, 0.12)
    d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=GREEN)
    d.text((sx - 10, sy + 18), "拉线开关", fill=GREEN, font=font(16, 600), anchor="rm")
    ox, oy = P(0.08, L.SOCKET.y)
    rect(d, [ox - 6, oy - 8, ox + 6, oy + 8], fill=GREEN)
    d.text((ox + 14, oy), "插座", fill=GREEN, font=font(16, 600), anchor="lm")

    # 月光
    mx, my, mz = L.MOON_DIR
    for (wx, wz) in [(0.75, 0.95), (1.95, 0.95), (1.95, 2.10), (0.75, 2.10)]:
        tt = wz / mz
        gx, gy = wx - mx * tt, 0 - my * tt
        d.line([P(wx, 0), P(gx, gy)], fill=(150, 175, 215), width=1)
    corners = []
    for (wx, wz) in [(0.75, 0.95), (1.95, 0.95), (1.95, 2.10), (0.75, 2.10)]:
        tt = wz / mz
        corners.append(P(wx - mx * tt, -my * tt))
    d.polygon(corners, outline=(120, 150, 205))
    d.text(P(0.95, 2.25), "月光落地（停电后）", fill=(100, 130, 190), font=font(15), anchor="mm")

    # 人物站位
    for key, p in L.MARKS.items():
        px, py = P(p.x, p.y)
        col = (200, 70, 70) if "xiaoman" in key else (90, 90, 160)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col, outline=INK)

    # 机位
    for cam in L.CAMERAS:
        if cam.name == "E":
            continue
        px, py = P(cam.pos[0], cam.pos[1])
        dx, dy = cam.target[0] - cam.pos[0], cam.target[1] - cam.pos[1]
        ang = math.atan2(dy, dx)
        h = math.radians(cam.hfov_deg) / 2
        ln = 1.1 * S
        a = (px + ln * math.cos(ang + h), py - ln * math.sin(ang + h))
        b = (px + ln * math.cos(ang - h), py - ln * math.sin(ang - h))
        d.polygon([(px, py), a, b], outline=(60, 60, 60))
        d.ellipse([px - 15, py - 15, px + 15, py + 15], fill=(30, 30, 30))
        d.text((px, py), cam.name, fill=(255, 255, 255), font=font(18, 700), anchor="mm")

    # 图例
    lx = M + L.ROOM_W * S + 120
    ly = M
    d.text((lx, ly), "《来电》堂屋平面图", fill=INK, font=font(34, 700))
    ly += 60
    rows = [
        ("单位：米；北在上；网格 1 米", INK),
        ("● 红点：小满站位", (200, 70, 70)),
        ("● 蓝点：奶奶站位", (90, 90, 160)),
        ("★ 橙：马灯（暖、跳动、阴影深）", WARM),
        ("★ 蓝：手电（冷、硬、有方向）", COLD),
        ("▭ 日光灯：平、白、惨白", COLD),
        ("A–D：主要机位（E 在屋外，正对南窗）", INK),
    ]
    for text, col in rows:
        d.text((lx, ly), text, fill=col, font=font(20))
        ly += 34
    ly += 20
    notes = [
        "因果要点",
        "1. 日光灯在床单【前面】：来电时从正面压",
        "   淡影子；影子剩淡淡残影。",
        "2. 马灯吊在床单后 0.7 米、略高于台口中部；",
        "   艺人站在灯两侧稍后，签子从灯旁伸出：",
        "   身体和手都不在灯与床单之间。",
        "3. 南窗正对床单：尾声从屋外能看见影子。",
        "4. 床单搭在铁丝上（离北墙 1 米），",
        "   D 机位能同时看到床单两边。",
        "5. 拉线开关在大门左边，线垂到 1.35 米。",
        "6. 插座在西墙，紧挨竹席；手机线够得着。",
        "7. 木箱本来就在西北角（床单后面），",
        "   不用拖；第 9 场手电架在它上面。",
    ]
    for i, text in enumerate(notes):
        d.text((lx, ly), text, fill=INK, font=font(19, 700 if i == 0 else 400))
        ly += 31

    # 网格刻度
    for i in range(int(L.ROOM_W) + 1):
        d.text(P(i, -0.45), f"{i}", fill=WALL, font=font(15), anchor="mm")
    for j in range(int(L.ROOM_D) + 1):
        d.text(P(-0.5, j), f"{j}", fill=WALL, font=font(15), anchor="mm")
    im.save(OUT / "floorplan.png")


def section():
    """沿 x≈1.3 的南北剖面：光源、床单、操纵者、日光灯的几何关系。"""
    S2 = 180
    y_min, y_max = -0.3, 5.6
    W = int((y_max - y_min) * S2 + 2 * M)
    H = int(3.6 * S2 + 2 * M)
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    def P(y, z):
        return (M + (y - y_min) * S2, M + (3.5 - z) * S2)

    d.line([P(y_min, 0), P(y_max, 0)], fill=INK, width=3)
    rect(d, [P(-L.WALL_T, L.ROOM_H), P(0, 0)], fill=WALL)
    rect(d, [P(L.ROOM_D, L.ROOM_H), P(L.ROOM_D + L.WALL_T, 2.0)], fill=WALL)
    rect(d, [P(-L.WALL_T, 2.10), P(0, 0.95)], fill=(190, 215, 235))
    d.line([P(0, L.ROOM_H), P(L.ROOM_D, L.ROOM_H)], fill=WALL, width=4)
    d.text(P(-0.12, 2.3), "南窗", fill=INK, font=font(18), anchor="mm")
    d.text(P(L.ROOM_D + 0.35, 1.0), "后屋门", fill=INK, font=font(18), anchor="mm")
    # 床单
    d.line([P(L.WIRE_Y, L.SHEET.z1), P(L.WIRE_Y, L.SHEET.z0)], fill=(255, 255, 255), width=7)
    d.line([P(L.WIRE_Y, L.SHEET.z1), P(L.WIRE_Y, L.SHEET.z0)], fill=INK, width=1)
    d.text(P(L.WIRE_Y - 0.05, L.SHEET.z1 + 0.15), "床单", fill=INK, font=font(18, 600), anchor="mm")
    # 马灯
    ly, lz = L.LAMP_STAGE.y, L.LAMP_STAGE.z
    for z_hit in (L.SHEET.z1, 1.30, L.SHEET.z0):
        d.line([P(ly, lz), P(L.WIRE_Y, z_hit)], fill=WARM, width=2)
    lx, lz2 = P(ly, lz)
    d.ellipse([lx - 12, lz2 - 12, lx + 12, lz2 + 12], fill=WARM, outline=INK)
    d.text((lx + 16, lz2 - 26), f"马灯 {lz:.2f}m", fill=WARM, font=font(18, 600), anchor="lm")
    # 艺人站在灯后，签子越过灯
    oy = L.MARKS["nainai_backstage"].y
    hy, hz = L.LAMP_STAGE.y - 0.02, 1.32
    py_, pz_ = L.WIRE_Y + 0.02, 1.38
    d.line([P(py_, pz_), P(hy, hz)], fill=(130, 90, 40), width=4)
    hx, hz2 = P(hy, hz)
    d.ellipse([hx - 9, hz2 - 9, hx + 9, hz2 + 9], fill=(230, 190, 160), outline=INK)
    d.text(P(hy - 0.05, hz - 0.12), "平端签子", fill=INK, font=font(16), anchor="rm")
    d.line([P(L.WIRE_Y + 0.02, 1.15), P(L.WIRE_Y + 0.02, 1.55)], fill=(180, 50, 40), width=5)
    d.text(P(L.WIRE_Y + 0.06, 1.66), "皮影贴紧床单", fill=(180, 50, 40), font=font(16), anchor="lm")
    # 人（站立）
    d.ellipse([P(oy - 0.1, 1.52), P(oy + 0.1, 1.30)], outline=(90, 90, 160), width=3)
    d.line([P(oy, 1.30), P(oy, 0.0)], fill=(90, 90, 160), width=3)
    d.line([P(oy, 1.18), P(hy, hz)], fill=(90, 90, 160), width=3)
    d.text(P(oy + 0.12, 0.7), "奶奶（站在灯后）", fill=(90, 90, 160), font=font(16), anchor="lm")
    # 头的"影子线"：从灯经过头顶，落到哪里
    for zz in (1.30, 1.52):
        t = (L.WIRE_Y - ly) / (oy - ly)
        d.line([P(ly, lz), P(oy, zz)], fill=(150, 110, 60), width=1)
    d.text(P(L.WIRE_Y + 0.1, 0.55), "人在灯后：头和手的影子都落不到床单上", fill=(150, 110, 60), font=font(16), anchor="lm")
    # 吊灯的麻绳
    d.line([P(ly, L.LAMP_PURLIN_Z), P(ly, lz + 0.2)], fill=(120, 100, 70), width=2)
    # 日光灯
    ty, tz = (L.TUBE.y0 + L.TUBE.y1) / 2, L.TUBE.z0
    tx, tz2 = P(ty, tz)
    rect(d, [tx - 16, tz2 - 5, tx + 16, tz2 + 5], fill=(225, 240, 255), outline=COLD, width=2)
    for z_hit in (L.SHEET.z1, L.SHEET.z0):
        d.line([P(ty, tz), P(L.WIRE_Y, z_hit)], fill=COLD, width=2)
    d.text((tx, tz2 - 22), "日光灯（床单前方）", fill=COLD, font=font(18, 600), anchor="mm")
    # 观众
    sy = L.MARKS["xiaoman_audience"].y
    rect(d, [P(sy - 0.11, 0.3), P(sy + 0.11, 0)], fill=(235, 222, 200))
    d.ellipse([P(sy - 0.09, 1.02), P(sy + 0.09, 0.84)], outline=(200, 70, 70), width=3)
    d.line([P(sy, 0.84), P(sy, 0.3)], fill=(200, 70, 70), width=3)
    d.text(P(sy, 1.18), "小满看戏（5–7场）", fill=(200, 70, 70), font=font(16), anchor="mm")
    # 吊扇
    fy = L.FAN.y
    d.line([P(fy, L.ROOM_H), P(fy, L.FAN.z)], fill=(120, 120, 120), width=3)
    d.line([P(fy - L.FAN_R, L.FAN.z), P(fy + L.FAN_R, L.FAN.z)], fill=(120, 120, 120), width=5)
    d.text(P(fy, L.FAN.z - 0.15), "吊扇", fill=INK, font=font(16), anchor="mm")
    # 月光
    mx, my, mz = L.MOON_DIR
    for wz in (0.95, 2.10):
        t = wz / mz
        d.line([P(0, wz), P(-my * t, 0)], fill=(150, 175, 215), width=1)
    d.text((M, M - 80), "戏台剖面（沿 x≈1.3m，南 ← → 北）", fill=INK, font=font(30, 700))
    d.text((M, M - 38), "马灯吊在床单后 0.7 米，艺人站在灯后；日光灯在床单前面：来电时从正面把影子压淡。",
           fill=INK, font=font(19))
    for i in range(0, 6):
        d.text(P(i, -0.12), f"y={i}", fill=WALL, font=font(14), anchor="mm")
    for j in range(0, 4):
        d.text(P(y_min - 0.12, j), f"{j}m", fill=WALL, font=font(14), anchor="mm")
    im.save(OUT / "stage-section.png")


if __name__ == "__main__":
    plan()
    section()
    print("ok")
