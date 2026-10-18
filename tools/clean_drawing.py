# 画稿接景前的处理：奶奶头发最外一圈画成了一层平的深灰（外面一条、里面隔一道黑线），推成近景像单独盖上去的一层。
# 只调颜色：在头部高度、贴近外轮廓 40 像素以内、低饱和的中暗灰上，用羽化过的软遮罩往头发中间调提亮（越接近黑线动得越少）。
# 原图的透明度一点不改（10-18 第一版收紧了透明度、换了半透明边的颜色，头顶出现黑块、断口，胳膊起锯齿——Astra 实片指出，已撤）。
# 用法：python3 -I tools/clean_drawing.py 输出目录 输入1.png 输入2.png …（文件名不变）
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for f in [x for x in sys.argv[2:] if not x.startswith('--')]:
    src = Image.open(f).convert('RGBA'); im = np.array(src).astype(np.float32)
    rgb, a = im[..., :3], im[..., 3] / 255.0
    solid = a > 0.5
    ys, _ = np.where(solid); top = ys.min()
    head = np.zeros_like(solid); head[top: top + int((ys.max() - top) * 0.30)] = True
    edge = ndimage.distance_transform_edt(solid) < 40
    lum = rgb.mean(-1); sat = rgb.max(-1) - rgb.min(-1)
    shell = (head & edge & solid & (sat < 30) & (lum > 55) & (lum < 140)).astype(np.float32)
    soft = ndimage.gaussian_filter(shell, 2.0) * (lum > 55)              # 软遮罩：边界不出台阶；黑线本身不动
    k = np.clip((lum - 55) / 85, 0, 1)
    rgb = rgb + (soft * (150 - lum) * (0.35 + 0.5 * k)).clip(min=0)[..., None]
    res = np.dstack([rgb.clip(0, 255), im[..., 3]]).round().astype(np.uint8)   # 透明度用原图的
    Image.fromarray(res, 'RGBA').save(out / Path(f).name)
    print(Path(f).name, '提亮像素', int((soft > 0.05).sum()))
