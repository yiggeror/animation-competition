# 把浅灰纯色背景的参考图抠成透明底 PNG：从图边往里漫水填充，和背景色差小于阈值的连通像素当背景。
# 轮廓线是深棕色，能把人物和背景隔开，所以人物内部和背景同色的地方（比如白领）不会被吃掉。
# 用法：python3 -I tools/cutout.py 输入.png 输出.png [阈值] [裁切框 x0,y0,x1,y1]
# 同一姿势的几张变体（比如抱着胳膊 / 胳膊松开）要用同一个裁切框，才能逐像素对齐
import sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
thr = float(sys.argv[3]) if len(sys.argv) > 3 else 14.0
fixed = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else None
rgb = np.array(Image.open(src).convert('RGB')).astype(np.float32)
H, W, _ = rgb.shape
bg = np.median(np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]), axis=0)
dist = np.sqrt(((rgb - bg) ** 2).sum(-1))
near = dist < thr
seen = np.zeros((H, W), bool)
q = deque()
for x in range(W):
    for y in (0, H - 1):
        if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
for y in range(H):
    for x in (0, W - 1):
        if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
while q:
    y, x = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < H and 0 <= xx < W and near[yy, xx] and not seen[yy, xx]:
            seen[yy, xx] = True; q.append((yy, xx))
# 被轮廓围住、和背景同色的封闭块（比如凳子腿中间露出的背景）也去掉：白领、眼白离背景色远，不会被误删
lab = np.zeros((H, W), np.int32); n = 0
for y0 in range(H):
    for x0 in range(W):
        if near[y0, x0] and not seen[y0, x0] and lab[y0, x0] == 0:
            n += 1; comp = [(y0, x0)]; lab[y0, x0] = n; i = 0
            while i < len(comp):
                y, x = comp[i]; i += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and near[yy, xx] and not seen[yy, xx] and lab[yy, xx] == 0:
                        lab[yy, xx] = n; comp.append((yy, xx))
            if len(comp) > 150:
                for y, x in comp: seen[y, x] = True
# 剥掉边上偏背景色的毛边（浅灰的细发丝和抗锯齿边），在暗场景里会显出一圈亮边
for _ in range(3):
    b = ~seen
    edge = b & (np.roll(seen, 1, 0) | np.roll(seen, -1, 0) | np.roll(seen, 1, 1) | np.roll(seen, -1, 1))
    lum = rgb @ np.array([0.299, 0.587, 0.114]); sat = rgb.max(-1) - rgb.min(-1)
    peel = edge & ((dist < 60) | ((lum > 200) & (sat < 30)))     # 偏背景色的，或者偏白偏灰的浅边（暗场景里会亮成一圈）
    seen |= peel
# 开运算：先收 2 像素再扩 2 像素，去掉头发外缘 1～3 像素宽的散发丝和它们与头发之间夹着的浅灰缝
# （暗场景里会亮成断续的白线）；呆毛、辫梢都比这粗，保留
from scipy import ndimage as ndi
# 外轮廓 6 像素以内、接近中性灰的浅色像素（散发丝和头发之间夹着的背景色）当作背景；白领子偏暖，不受影响
lum = rgb @ np.array([0.299, 0.587, 0.114]); sat = rgb.max(-1) - rgb.min(-1)
near_edge = ndi.distance_transform_edt(~seen) <= 6
seen |= near_edge & (lum > 165) & (sat < 12)
solid = ndi.binary_opening(~seen, structure=np.ones((5, 5), bool))
seen = ~solid
alpha = np.where(seen, 0, 255).astype(np.uint8)
# 边缘抗锯齿：背景一侧按色差给半透明，再轻轻收一圈去掉灰边
a = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
out = np.dstack([rgb.astype(np.uint8), np.array(a)])
ys, xs = np.where(np.array(a) > 8)
pad = 6
box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(W, xs.max() + pad + 1), min(H, ys.max() + pad + 1))
if fixed: box = fixed
Image.fromarray(out, 'RGBA').crop(box).save(dst)
print(dst, 'crop box', box, 'bg', bg.round(1))
