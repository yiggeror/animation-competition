"""把检查点的渲染整理成可提交的预览：压成 JPEG、拼一张画风对比总览。

用法：python tools/make_boards.py BUILD_DIR renders/checkpoint1
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = str(ROOT / "assets/fonts/NotoSansSC-VF.ttf")


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def main(src, dst):
    src, dst = Path(src), Path(dst)
    (dst / "samples").mkdir(parents=True, exist_ok=True)
    (dst / "design").mkdir(parents=True, exist_ok=True)
    for p in sorted((src / "samples").glob("*.png")):
        Image.open(p).convert("RGB").save(dst / "samples" / (p.stem + ".jpg"), quality=90)
    for p in sorted((src / "design").glob("*.png")):
        im = Image.open(p).convert("RGB")
        if im.width > 3000:
            im = im.resize((3000, int(im.height * 3000 / im.width)), Image.LANCZOS)
        im.save(dst / "design" / (p.stem + ".jpg"), quality=88)
    for p in sorted((src / "motion").glob("*.mp4")):
        (dst / "motion").mkdir(exist_ok=True)
        (dst / "motion" / p.name).write_bytes(p.read_bytes())
    # 总览：行 = 画风，列 = 样张
    styles = [("lantern", "A 灯影"), ("woodcut", "B 刻光"), ("silk", "C 绢灯")]
    shots = [("s06", "第 6 场 · 鹤亮相"), ("s10", "第 10 场 · 来电（侧面）"), ("s10w", "第 10 场 · 来电（全景）")]
    tw, th = 640, 360
    pad, head, left = 14, 90, 150
    W = left + len(shots) * (tw + pad) + pad
    H = head + len(styles) * (th + pad) + pad
    B = Image.new("RGB", (W, H), (236, 231, 220))
    d = ImageDraw.Draw(B)
    d.text((pad, 16), "《来电》画风方向对比", fill=(40, 34, 30), font=font(36, 700))
    for j, (k, nm) in enumerate(shots):
        d.text((left + j * (tw + pad) + 8, 62), nm, fill=(60, 52, 46), font=font(20, 600))
    for i, (s, nm) in enumerate(styles):
        y = head + i * (th + pad)
        d.text((pad, y + th / 2 - 16), nm, fill=(40, 34, 30), font=font(28, 700))
        for j, (k, _) in enumerate(shots):
            p = src / "samples" / f"{k}_{s}.png"
            if p.exists():
                B.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (left + j * (tw + pad), y))
    B.save(dst / "style_board.jpg", quality=90)
    print("ok", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
