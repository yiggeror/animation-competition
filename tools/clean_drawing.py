# 画稿抠图清理：生图给的透明边常常是一圈"深色 + 半透明"（原画在浅底上看着是柔边，放到我们的场景上就像多了一层深色的头发/轮廓）。
# 做法：半透明像素的颜色换成离它最近的不透明像素的颜色（去掉深色污染），再把透明度收紧到很窄的一条抗锯齿边。
# 用法：python3 -I tools/clean_drawing.py 输出目录 [--hair] 输入1.png 输入2.png …（文件名不变；--hair 把奶奶头发外圈那层平的深灰提亮）
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

flags = [x for x in sys.argv[2:] if x.startswith('--')]
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for f in [x for x in sys.argv[2:] if not x.startswith('--')]:
    im = np.array(Image.open(f).convert('RGBA')).astype(np.float32)
    a = im[..., 3] / 255.0
    opaque = a >= 0.98
    _, (iy, ix) = ndimage.distance_transform_edt(~opaque, return_indices=True)
    rgb = im[..., :3].copy()
    semi = (a > 0) & ~opaque
    near = im[iy, ix, :3]                                          # 每个像素最近的不透明像素的颜色
    rgb[semi] = near[semi]                                         # 一般的半透明边：颜色取最近的不透明像素
    a2 = np.clip((a - 0.45) / 0.25, 0, 1)                          # 透明度收紧：0.45 以下去掉，0.7 以上算实
    # 灰白头发外圈：生图把它画成"深灰 + 半透明"，原意是在浅底上透出来的浅灰发丝。按浅底（238）合成出原来的颜色，再当成实的
    sat = near.max(-1) - near.min(-1); lum = near.mean(-1)
    hair = semi & (sat < 28) & (lum > 110) & (lum < 215)
    rgb[hair] = im[..., :3][hair] * a[hair, None] + 238 * (1 - a[hair, None])
    a2[hair] = np.clip((a[hair] - 0.08) / 0.15, 0, 1)
    # 奶奶头发最外一圈画成了一层平的深灰（外面一条、里面隔一道黑线），推成近景像单独盖上去的一层。
    # 只动头部高度、贴近外轮廓 40 像素以内、低饱和的中暗灰（不碰黑线和高光），往头发中间调提亮，留一点暗面
    if '--hair' in flags:
        ys, xs = np.where(a2 > 0.5); top = ys.min(); head = np.zeros_like(a2, bool); head[top: top + int((ys.max() - top) * 0.30)] = True
        edge = ndimage.distance_transform_edt(a2 > 0.5) < 40
        lumc = rgb.mean(-1); satc = rgb.max(-1) - rgb.min(-1)
        shell = head & edge & (satc < 30) & (lumc > 55) & (lumc < 140) & (a2 > 0.5)
        k = np.clip((lumc[shell] - 55) / 85, 0, 1)                    # 越接近黑线的越少动，免得线糊掉
        rgb[shell] += ((150 - lumc[shell]) * (0.35 + 0.5 * k))[:, None]
    res = np.dstack([rgb, a2 * 255]).round().clip(0, 255).astype(np.uint8)
    Image.fromarray(res, 'RGBA').save(out / Path(f).name)
    print(Path(f).name, '半透明像素', int(semi.sum()))
