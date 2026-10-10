"""画能量（热闹程度）曲线，数据来自 laidian.beats。

用法：python tools/draw_tension.py → docs/preproduction/tension-curve.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from laidian.beats import BEATS, CREDITS_DUR, timeline  # noqa: E402

FONT = str(ROOT / "assets/fonts/NotoSansSC-VF.ttf")
SURFACE = (252, 252, 251)
TEXT1 = (11, 11, 11)
TEXT2 = (82, 81, 78)
GRID = (226, 225, 220)
BAND = (244, 243, 239)
SERIES = (42, 120, 214)
K = 2  # 超采样


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size * K)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def main():
    W, H = 1500, 640
    ml, mr, mt, mb = 90, 40, 120, 110
    im = Image.new("RGB", (W * K, H * K), SURFACE)
    d = ImageDraw.Draw(im)
    tl = timeline()
    T = tl[-1][2] + CREDITS_DUR

    def X(t):
        return (ml + (W - ml - mr) * t / T) * K

    def Y(v):
        return (mt + (H - mt - mb) * (1 - v / 10)) * K

    # 场次色带
    for i, (b, t0, t1) in enumerate(tl):
        if i % 2 == 0:
            d.rectangle([X(t0), Y(10), X(t1), Y(0)], fill=BAND)
        d.text(((X(t0) + X(t1)) / 2, Y(10) - 30 * K), f"{b.no}", fill=TEXT2, font=font(15, 600), anchor="mm")
        d.text(((X(t0) + X(t1)) / 2, Y(10) - 12 * K), b.name, fill=TEXT2, font=font(14), anchor="mm")
    t_end = tl[-1][2]
    d.text(((X(t_end) + X(T)) / 2, Y(10) - 12 * K), "字幕", fill=TEXT2, font=font(14), anchor="mm")
    # 网格
    for v in (0, 2, 4, 6, 8, 10):
        d.line([X(0), Y(v), X(T), Y(v)], fill=GRID, width=K)
        d.text((X(0) - 12 * K, Y(v)), str(v), fill=TEXT2, font=font(14), anchor="rm")
    for s in range(0, int(T) + 1, 30):
        d.text((X(s), Y(0) + 18 * K), f"{s // 60}:{s % 60:02d}", fill=TEXT2, font=font(14), anchor="mm")
    d.text((X(T / 2), Y(0) + 48 * K), "时间（分:秒）", fill=TEXT2, font=font(15), anchor="mm")

    # 曲线
    pts = []
    for b, t0, t1 in tl:
        for (u, v) in b.energy:
            pts.append((t0 + u * b.dur, v))
    pts.append((T, 4.2))
    xy = [(X(t), Y(v)) for t, v in pts]
    d.line(xy, fill=SERIES, width=3 * K, joint="curve")

    # 少量直接标注
    marks = {
        "停电笑点": (2, 0.55), "鹤亮相": (6, 0.3), "手把手": (8, 0.6),
        "第一个高潮": (9, 1.0), "来电：音乐全停": (10, 0.02), "关灯·再来": (12, 0.5),
    }
    for text, (no, u) in marks.items():
        b, t0, _ = tl[no - 1]
        t = t0 + u * b.dur
        # 在曲线上插值
        v = None
        for (ta, va), (tb, vb) in zip(pts, pts[1:]):
            if ta <= t <= tb:
                v = va + (vb - va) * ((t - ta) / (tb - ta) if tb > ta else 0)
                break
        r = 5 * K
        d.ellipse([X(t) - r, Y(v) - r, X(t) + r, Y(v) + r], fill=SERIES, outline=SURFACE, width=2 * K)
        dy = -22 if text != "手把手" else 24
        d.text((X(t), Y(v) + dy * K), text, fill=TEXT1, font=font(14, 600), anchor="mm")

    d.text((ml * K, 28 * K), "《来电》能量曲线", fill=TEXT1, font=font(24, 700))
    d.text((ml * K, 62 * K), "能量 = 画面和声音的热闹程度（0 静 – 10 闹）。来电是一次断崖，不是滑坡；关灯后不回到高潮，停在温暖的中间。",
           fill=TEXT2, font=font(15))
    im = im.resize((W, H), Image.LANCZOS)
    out = ROOT / "docs/preproduction/tension-curve.png"
    im.save(out)
    print(out)


if __name__ == "__main__":
    main()
