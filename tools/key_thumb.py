# 从合作方的手机图 B（anim_02_hands_phone_b，拇指按下去的那一帧）里抠出右拇指和它压在屏幕上的接触影，
# 给 js/code/phone_img.js 按键时换上（底图仍用 A，只换右手这一块）。
# A、B 两张图的右手在线条上有细小差别（一直到手掌外缘），只换屏幕里的拇指会在边框处错开一截，
# 所以换的是"屏幕里的拇指 + 屏幕右边整只右手"这一块（上下边缘羽化，那里两张图几乎一样）；区域另存一张遮罩，按下时底图挖掉这一块。
# 绿幕：屏幕底色约 (6,248,40)；接触影是更暗的绿 (4,218,15)，按"比屏幕暗多少"算成黑色半透明影子。
# 用法：python3 tools/key_thumb.py collab/refs/anim_02_hands_phone_b.png assets/chars/h02_thumb_b.png assets/chars/h02_thumb_b_shadow.png assets/chars/h02_thumb_b_region.png
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, out_skin, out_shadow, out_region = sys.argv[1:5]
im = np.array(Image.open(src).convert('RGB')).astype(np.float32)
H, W = im.shape[:2]
# 拇指在屏幕上的部分（比 A 的多边形往下放 30 像素：按下去的拇指更低），右边到屏幕边缘再多 4 像素
POLY = [(1176, 330), (1346, 330), (1346, 566), (1294, 566), (1176, 462)]
m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); d.polygon(POLY, fill=255); d.rectangle((1340, 150, W, 750), fill=255)
m = np.array(m.filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255
Image.fromarray((255 * m).astype(np.uint8), 'L').convert('RGBA').save(out_region)   # 只用它的亮度当遮罩

r, g, b = im[..., 0], im[..., 1], im[..., 2]
green = g - np.maximum(r, b)                       # 屏幕 ≈ 208，皮肤和墨线 < 0
a_skin = 1 - np.clip((green - 25) / 150, 0, 1)
# 屏幕外的灰底 (211,210,210) 也抠掉
gray = np.sqrt(((im - np.array([211, 210, 210], np.float32)) ** 2).sum(-1))
a_skin = a_skin * np.clip((gray - 10) / 30, 0, 1)
# 去溢色：半透明边上的绿压到不超过红蓝
g2 = np.minimum(g, np.maximum(r, b) + 12)
rgb = np.stack([r, np.where(a_skin < 0.98, g2, g), b], -1)
skin = np.dstack([rgb, 255 * a_skin * m]).clip(0, 255).astype(np.uint8)
Image.fromarray(skin, 'RGBA').save(out_skin)

# 接触影：纯绿处按亮度差算（248 → 0，218 → 约 0.36），皮肤处不算
G0 = 248.0
dark = np.clip((G0 - g) / G0, 0, 1) * (1 - a_skin)
sh = np.clip(dark * 3.0, 0, 0.6)
shadow = np.zeros((H, W, 4), np.uint8); shadow[..., 3] = (255 * sh * m).astype(np.uint8)
Image.fromarray(shadow, 'RGBA').save(out_shadow)
print('skin px', int((a_skin * m > 0.5).sum()), 'shadow max', float(sh[m > 0.5].max()))
