# 去掉画稿里烘进去的偏色光（例如 S02a 最早三张下巴、领口那层淡蓝的手机光），让新旧画同一个中性底色，场景光再统一乘一次。
# 做法：在人物下半部，按上半部（额头、脸颊）皮肤的颜色比例，把偏蓝的皮肤拉回去；近白的领口拉回中性白。上半部不动，透明度不动。
# 用法：python3 -I tools/neutralize_cast.py 输出目录 [--ref 参考.png] 输入1.png …
# --ref：处理完再把下巴以下（颈根、领口）的皮肤和白领口两类颜色，分别对齐到参考图同一区域的平均色，免得新旧画之间颈领一帧暖一帧紫
import sys
from pathlib import Path
import numpy as np
from PIL import Image

args = sys.argv[2:]; ref = None
if '--ref' in args: i = args.index('--ref'); ref = args[i + 1]; args = args[:i] + args[i + 2:]
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)

def classes(im):
    r, g, b, a = (im[..., k] for k in range(4))
    ys, _ = np.where(a > 128); y0, y1 = ys.min(), ys.max()
    yy = np.arange(im.shape[0])[:, None] * np.ones((1, im.shape[1]))
    low = (a > 200) & (yy > y0 + 0.78 * (y1 - y0))                         # 下巴以下：颈根和领口
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    white = low & (mn > 175) & (mx - mn < 30) & ~((r > b + 18) & (r > g))
    skin = low & ~white & (r > 140) & (r > b + 25)
    return skin, white

REF = None
def fixlow(im):
    if REF is None: return im
    for m, mref in zip(classes(im), REF[1]):
        if m.sum() < 50: continue
        d = REF[0][mref][:, :3].mean(0) - im[m][:, :3].mean(0)
        im[..., :3][m] = im[..., :3][m] + d
    return im

def neutral(f):
    im = np.array(Image.open(f).convert('RGBA')).astype(np.float32)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    ys, xs = np.where(a > 128); y0, y1 = ys.min(), ys.max(); H = y1 - y0
    yy = np.arange(im.shape[0])[:, None] * np.ones((1, im.shape[1]))
    skin = (a > 128) & (r > 150) & (r > g) & (g > b * 0.95)
    upper = skin & (yy > y0 + 0.25 * H) & (yy < y0 + 0.45 * H)            # 额头、脸颊一带（不受手机光）
    kg, kb = np.median(g[upper] / r[upper]), np.median(b[upper] / r[upper])
    w = np.clip((yy - (y0 + 0.45 * H)) / (0.15 * H), 0, 1)                # 往下渐入，交界不出线
    low = (a > 0) & (w > 0)
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    wh = low & (mn > 175) & (mx - mn < 30) & ~((r > b + 18) & (r > g))     # 白领口：先从原像素认出来（低饱和近白），不进皮肤处理（Astra 10:31 复现：原来先被当皮肤压了 G/B）
    sk = low & ~wh & (r > 110) & (b > r * kb)                              # 偏蓝的皮肤
    for ch, k in ((g, kg), (b, kb)):
        tgt = r * k; ch[sk] = ch[sk] + (np.minimum(ch[sk], np.maximum(tgt[sk], ch[sk] - 60)) - ch[sk]) * w[sk]
    m = (r + g + b) / 3                                                    # 白领口拉成中性白
    for ch in (r, g, b): ch[wh] = ch[wh] + (m[wh] + 1.5 - ch[wh]) * w[wh]
    return np.dstack([r, g, b, a]), kg, kb, int(sk.sum() + wh.sum())

if ref:
    rim = neutral(ref)[0]; REF = (rim, classes(rim))
for f in args:
    im, kg, kb, n = neutral(f)
    im = fixlow(im)
    Image.fromarray(im.clip(0, 255).round().astype(np.uint8), 'RGBA').save(out / Path(f).name)
    print(Path(f).name, f'皮肤比例 g/r={kg:.3f} b/r={kb:.3f}', '改了', n, '像素')
