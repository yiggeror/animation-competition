"""墙上的东西：中堂画（松鹤）、对联、挂历、奖状、老照片相框。全部程序绘制，内容原创。"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .vecdraw import catmull

ROOT = Path(__file__).resolve().parents[3]
CALLI = str(ROOT / "assets/fonts/MaShanZheng-Regular.ttf")
SANS = str(ROOT / "assets/fonts/NotoSansSC-VF.ttf")


def _lin(img):
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    out = np.ones(a.shape[:2] + (4,), np.float32)
    out[..., :3] = a
    return out


def _paper(w, h, base=(226, 214, 184), seed=1, grain=10):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, grain, (h // 4 + 1, w // 4 + 1))
    n = np.asarray(Image.fromarray(n.astype(np.float32)).resize((w, h), Image.BICUBIC))
    a = np.clip(np.array(base, np.float32)[None, None] + n[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a)


def painting(w=360, h=620):
    """中堂画：松鹤图（水墨淡彩）。"""
    im = _paper(w, h, (214, 200, 166), 3)
    d = ImageDraw.Draw(im)
    # 装裱：上下天地杆、绫边
    d.rectangle([0, 0, w, 34], fill=(120, 96, 70))
    d.rectangle([0, h - 40, w, h], fill=(120, 96, 70))
    d.rectangle([14, 34, w - 14, h - 40], outline=(150, 128, 98), width=6)
    ink = (52, 44, 40)
    # 远山
    for k, (y0, col) in enumerate(((330, (170, 170, 150)), (360, (140, 145, 125)))):
        pts = [(24, h - 60)] + [(24 + i * (w - 48) / 12, y0 + 40 * math.sin(i * 0.9 + k) - 30 * (i % 3 == 1)) for i in range(13)] + [(w - 24, h - 60)]
        d.polygon(pts, fill=col)
    # 松树：弯曲的树干 + 几簇针叶
    trunk = catmull([(70, h - 70), (95, 420), (80, 330), (120, 250), (190, 210)], False, 10)
    for i in range(len(trunk) - 1):
        wdt = int(18 - i * 0.3)
        d.line([tuple(trunk[i]), tuple(trunk[i + 1])], fill=ink, width=max(4, wdt))
    for (cx, cy, r) in ((180, 200, 48), (240, 230, 40), (120, 260, 36), (95, 330, 30), (200, 160, 30)):
        for a in np.linspace(0, 2 * math.pi, 26):
            x1, y1 = cx + r * math.cos(a), cy + r * 0.5 * math.sin(a)
            d.line([(cx, cy), (x1, y1)], fill=(48, 78, 52), width=2)
    # 鹤：站在松下，红顶
    body = [(200, 470), (238, 452), (262, 466), (240, 488), (205, 490)]
    d.polygon(body, fill=(240, 236, 226), outline=ink)
    d.line([(238, 456), (250, 400), (262, 372)], fill=ink, width=5)
    d.ellipse([256, 362, 272, 376], fill=(240, 236, 226), outline=ink)
    d.ellipse([260, 360, 268, 366], fill=(190, 40, 30))
    d.line([(270, 370), (300, 378)], fill=(90, 80, 50), width=3)
    d.polygon([(200, 470), (180, 486), (206, 488)], fill=ink)
    d.line([(222, 488), (220, 545)], fill=ink, width=3)
    d.line([(232, 488), (240, 545)], fill=ink, width=3)
    # 题款与印章
    try:
        f = ImageFont.truetype(CALLI, 34)
        for i, ch in enumerate("松鹤延年"):
            d.text((w - 70, 70 + i * 40), ch, fill=ink, font=f)
    except Exception:
        pass
    d.rectangle([w - 66, 240, w - 40, 266], fill=(180, 40, 30))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    return _lin(im)


def couplet(text, w=110, h=560, seed=4):
    im = _paper(w, h, (176, 44, 34), seed, 8)
    d = ImageDraw.Draw(im)
    d.rectangle([5, 5, w - 6, h - 6], outline=(150, 34, 26), width=3)
    f = ImageFont.truetype(CALLI, 72)
    n = len(text)
    for i, ch in enumerate(text):
        d.text((w / 2, 40 + i * (h - 70) / n + 26), ch, fill=(24, 20, 18), font=f, anchor="mm")
    # 年久褪色
    a = np.asarray(im, np.float32)
    fade = np.linspace(1.0, 0.82, h)[:, None, None]
    im = Image.fromarray(np.clip(a * fade + 18, 0, 255).astype(np.uint8))
    return _lin(im)


def calendar(w=320, h=360):
    im = _paper(w, h, (240, 236, 226), 6, 4)
    d = ImageDraw.Draw(im)
    # 上半张：风景图（原创：山水、湖、帆）
    d.rectangle([12, 12, w - 12, 180], fill=(150, 186, 205))
    d.polygon([(12, 150), (90, 70), (150, 120), (210, 60), (w - 12, 140), (w - 12, 180), (12, 180)], fill=(80, 120, 96))
    d.rectangle([12, 150, w - 12, 180], fill=(100, 150, 180))
    d.polygon([(200, 160), (214, 128), (214, 160)], fill=(240, 240, 240))
    f = ImageFont.truetype(SANS, 46)
    d.text((24, 188), "8", fill=(190, 40, 30), font=f)
    d.text((70, 204), "月", fill=(60, 50, 45), font=ImageFont.truetype(SANS, 26))
    fs = ImageFont.truetype(SANS, 15)
    for r in range(5):
        for c in range(7):
            n = r * 7 + c - 2
            if 1 <= n <= 31:
                col = (190, 40, 30) if c in (0, 6) else (60, 50, 45)
                d.text((24 + c * 40, 256 + r * 20), str(n), fill=col, font=fs)
    return _lin(im)


def certificate(w=420, h=300):
    im = _paper(w, h, (236, 226, 200), 7, 6)
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, w - 10, h - 10], outline=(180, 40, 30), width=10)
    d.rectangle([24, 24, w - 24, h - 24], outline=(200, 160, 60), width=3)
    f = ImageFont.truetype(SANS, 56)
    d.text((w / 2, 82), "奖  状", fill=(190, 36, 28), font=f, anchor="mm")
    for k in range(4):
        d.line([(60, 140 + k * 26), (w - 60, 140 + k * 26)], fill=(150, 140, 120), width=2)
    d.ellipse([w - 120, h - 110, w - 50, h - 40], outline=(190, 40, 30), width=3)
    # 褪色、发黄
    a = np.asarray(im, np.float32)
    a = a * np.array([1.0, 0.96, 0.86]) + 6
    return _lin(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))


def photos(w=240, h=440):
    """大相框里的老照片拼贴。其中一张：年轻的奶奶站在戏台幕布后面，手里举着皮影（剪影）。"""
    im = Image.new("RGB", (w, h), (64, 50, 40))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(9)
    slots = [(12, 12, 108, 140), (120, 12, 228, 120), (12, 152, 140, 260), (152, 132, 228, 250), (12, 272, 228, 428)]
    for k, (x0, y0, x1, y1) in enumerate(slots):
        tone = 180 + rng.integers(-20, 20)
        ph = _paper(x1 - x0, y1 - y0, (tone, tone - 8, tone - 22), 20 + k, 14)
        pd = ImageDraw.Draw(ph)
        pw, phh = ph.size
        if k == 4:
            # 戏台幕布后面：亮的幕布，前面是年轻奶奶的侧影和一个举起的皮影
            pd.rectangle([8, 8, pw - 8, phh - 30], fill=(232, 224, 200))
            pd.ellipse([pw * 0.22, phh * 0.20, pw * 0.34, phh * 0.36], fill=(40, 34, 30))
            pd.polygon([(pw * 0.18, phh * 0.36), (pw * 0.38, phh * 0.36), (pw * 0.42, phh), (pw * 0.14, phh)], fill=(40, 34, 30))
            pd.line([(pw * 0.36, phh * 0.42), (pw * 0.60, phh * 0.30)], fill=(40, 34, 30), width=3)
            pd.polygon([(pw * 0.58, phh * 0.18), (pw * 0.70, phh * 0.14), (pw * 0.74, phh * 0.30), (pw * 0.62, phh * 0.36)], fill=(70, 60, 52))
            pd.text((pw * 0.70, phh - 22), "1972", fill=(120, 100, 80), font=ImageFont.truetype(SANS, 14))
        else:
            # 合影：几个人的剪影
            n = 1 + k % 3
            for i in range(n):
                cx = pw * (i + 1) / (n + 1)
                pd.ellipse([cx - 9, phh * 0.30, cx + 9, phh * 0.30 + 18], fill=(70, 60, 54))
                pd.rectangle([cx - 13, phh * 0.30 + 18, cx + 13, phh], fill=(80, 70, 62))
        ph = ph.filter(ImageFilter.GaussianBlur(0.8))
        im.paste(ph, (x0, y0))
    return _lin(im)


def build_textures(atlas):
    """把墙上的贴图加进图集，返回 RoomState.textures 用的字典。"""
    tex = {}
    tex["painting"] = atlas.add(painting())
    atlas.add(painting())       # 占位：保持"透射 + 反射"成对的约定
    tex["couplet_l"] = atlas.add(couplet("天增岁月人增寿"))
    atlas.add(couplet("天增岁月人增寿"))
    tex["couplet_r"] = atlas.add(couplet("春满乾坤福满门", seed=5))
    atlas.add(couplet("春满乾坤福满门", seed=5))
    tex["calendar"] = atlas.add(calendar())
    atlas.add(calendar())
    tex["certificate"] = atlas.add(certificate())
    atlas.add(certificate())
    tex["photos"] = atlas.add(photos())
    atlas.add(photos())
    return tex
