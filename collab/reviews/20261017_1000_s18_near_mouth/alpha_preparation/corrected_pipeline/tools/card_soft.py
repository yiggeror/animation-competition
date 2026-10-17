# 柔和的整体法线：把整个人的轮廓（透明度）大幅模糊后求梯度，只给"整个人一点点圆"，不按身体部位分块。
# 用在离马灯很近、侧光很硬的镜头（后台），避免画上已有的明暗再被法线叠一遍、一节一节地鼓起来。
# 用法：python3 -I tools/card_soft.py 透明底.png 法线.png [模糊半径像素=45] [强度=0.35]
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]
sig = float(sys.argv[3]) if len(sys.argv) > 3 else 45.0
k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.35
a = np.array(Image.open(src).convert('RGBA'))[..., 3].astype(np.float32) / 255
h = ndi.gaussian_filter(a, sig)
gy, gx = np.gradient(h)
s = k * sig
nx, ny, nz = -gx * s, gy * s, np.ones_like(h)
l = np.sqrt(nx * nx + ny * ny + nz * nz)
n = np.stack([nx / l, ny / l, nz / l], -1)
rgb = ((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
alpha = (a * 255).astype(np.uint8)
Image.fromarray(np.dstack([rgb, alpha])).save(out)
print(out, 'max tilt %.2f' % np.degrees(np.arccos(n[..., 2].min())))
