"""把检查点的渲染整理成可提交的预览：压成 JPEG、拼一张画风对比总览。

用法：python tools/make_boards.py BUILD_DIR renders/checkpoint1
"""
import subprocess
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
    # 动态小样：仓库里放压缩过的版本（CRF 24），外加三个画风并排的对比
    mv = sorted((src / "motion").glob("motion_*.mp4"))
    if mv:
        (dst / "motion").mkdir(exist_ok=True)
        for p in mv:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p), "-c:v", "libx264", "-crf", "24",
                            "-preset", "slow", "-pix_fmt", "yuv420p", str(dst / "motion" / p.name)], check=True)
        order = [src / "motion" / f"motion_{s}.mp4" for s in ("lantern", "woodcut", "silk")]
        if all(p.exists() for p in order):
            names = ["A 灯影", "B 刻光", "C 绢灯"]
            fl = []
            for i, nm in enumerate(names):
                fl.append(f"[{i}:v]scale=640:360,drawtext=fontfile={FONT}:text='{nm}':x=14:y=12:fontsize=22:"
                          f"fontcolor=white:box=1:boxcolor=black@0.45:boxborderw=6[v{i}]")
            fl.append("[v0][v1][v2]hstack=inputs=3[out]")
            cmd = ["ffmpeg", "-y", "-loglevel", "error"]
            for p in order:
                cmd += ["-i", str(p)]
            cmd += ["-filter_complex", ";".join(fl), "-map", "[out]", "-c:v", "libx264", "-crf", "23", "-preset", "slow",
                    "-pix_fmt", "yuv420p", str(dst / "motion" / "motion_compare.mp4")]
            subprocess.run(cmd, check=True)
    # 动态小样的关键帧接触表：行 = 画风，列 = 时间
    frames_dirs = [(s_, nm) for s_, nm in (("lantern", "A 灯影"), ("woodcut", "B 刻光"), ("silk", "C 绢灯"))
                   if (src / "motion" / s_).is_dir()]
    if frames_dirs:
        allf = sorted((src / "motion" / frames_dirs[0][0]).glob("*.png"))
        if allf:
            n = len(allf)
            picks = [round(i * (n - 1) / 5) for i in range(6)]
            fw, fh, pad, head, left = 400, 225, 10, 70, 130
            CW = left + 6 * (fw + pad) + pad
            CH = head + len(frames_dirs) * (fh + pad) + pad
            Cb = Image.new("RGB", (CW, CH), (236, 231, 220))
            dc = ImageDraw.Draw(Cb)
            dc.text((pad, 14), "动态小样关键帧（第 6 场鹤亮相，24 帧/秒）", fill=(40, 34, 30), font=font(28, 700))
            for j, f in enumerate(picks):
                dc.text((left + j * (fw + pad) + 4, 48), f"{f / 24:.1f} 秒", fill=(60, 52, 46), font=font(16, 600))
            for i, (s_, nm) in enumerate(frames_dirs):
                y = head + i * (fh + pad)
                dc.text((pad, y + fh / 2 - 14), nm, fill=(40, 34, 30), font=font(24, 700))
                for j, f in enumerate(picks):
                    fp = src / "motion" / s_ / f"{f:04d}.png"
                    if fp.exists():
                        Cb.paste(Image.open(fp).convert("RGB").resize((fw, fh), Image.LANCZOS), (left + j * (fw + pad), y))
            (dst / "motion").mkdir(exist_ok=True)
            Cb.save(dst / "motion" / "motion_frames.jpg", quality=88)
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
