# 去掉画稿里烘进去的偏色光（例如 S02a 最早三张下巴、领口那层淡蓝的手机光），让新旧画同一个中性底色，场景光再统一乘一次。
# 做法：在人物下半部，按上半部（额头、脸颊）皮肤的颜色比例，把偏蓝的皮肤拉回去；近白的领口拉回中性白。上半部不动，透明度不动。
# 用法：python3 -I tools/neutralize_cast.py 输出目录 输入1.png …
import sys
from pathlib import Path
import numpy as np
from PIL import Image

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for f in sys.argv[2:]:
    im = np.array(Image.open(f).convert('RGBA')).astype(np.float32)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    ys, xs = np.where(a > 128); y0, y1 = ys.min(), ys.max(); H = y1 - y0
    yy = np.arange(im.shape[0])[:, None] * np.ones((1, im.shape[1]))
    skin = (a > 128) & (r > 150) & (r > g) & (g > b * 0.95)
    upper = skin & (yy > y0 + 0.25 * H) & (yy < y0 + 0.45 * H)            # 额头、脸颊一带（不受手机光）
    kg, kb = np.median(g[upper] / r[upper]), np.median(b[upper] / r[upper])
    w = np.clip((yy - (y0 + 0.45 * H)) / (0.15 * H), 0, 1)                # 往下渐入，交界不出线
    low = (a > 0) & (w > 0)
    sk = low & (r > 110) & (b > r * kb)                                    # 偏蓝的皮肤
    for ch, k in ((g, kg), (b, kb)):
        tgt = r * k; ch[sk] = ch[sk] + (np.minimum(ch[sk], np.maximum(tgt[sk], ch[sk] - 60)) - ch[sk]) * w[sk]
    wh = low & (r > 170) & (g > 170) & (b > 170) & (b > r)                 # 偏蓝的白领口
    m = (r + g + b) / 3; b[wh] = b[wh] + (np.minimum(b[wh], m[wh] + 2) - b[wh]) * w[wh]
    res = np.dstack([r, g, b, a]).clip(0, 255).round().astype(np.uint8)
    Image.fromarray(res, 'RGBA').save(out / Path(f).name)
    print(Path(f).name, f'皮肤比例 g/r={kg:.3f} b/r={kb:.3f}', '改了', int(sk.sum() + wh.sum()), '像素')
