# 透明底的人物图 → 光照卡片要的法线图和材质图（编码和 js/lamp/cards.js 一致）。
# 法线：深色的轮廓线、衣褶线当作分界，每块区域按到分界的距离"鼓"起来（圆弧截面），再模糊一点；
#       线本身取旁边区域的法线。外轮廓边上法线是横的，被侧光、逆光勾出亮边。
# 材质：按颜色分——皮肤 1、头发 2、布 3（裙子、领子、绒球、凉鞋），其他（凳子）0；线取旁边区域的材质。
# 用法：python3 -I tools/card_maps.py 透明底.png 法线.png 材质.png [圆鼓半径像素]
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

src, out_n, out_m = sys.argv[1:4]
R = float(sys.argv[4]) if len(sys.argv) > 4 else 18.0
im = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
rgb, a = im[..., :3], im[..., 3] / 255.0
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
L = rgb @ np.array([0.299, 0.587, 0.114])
solid = a > 0.5
line = (L < ndi.uniform_filter(L, 7) - 18) & solid           # 比周围暗一截的细线
inside = solid & ~line
# 每个像素最近的"区域内"像素（线和边缘用它的值）
near = ndi.distance_transform_edt(~inside, return_distances=False, return_indices=True)

d = ndi.distance_transform_edt(inside)
u = np.minimum(d + 0.5, R) / R
h = np.where(inside, R * np.sqrt(np.maximum(0.0, 1 - (1 - u) ** 2)), 0.0)
h = ndi.gaussian_filter(h, max(1.0, R * 0.15))
h = np.where(inside, h, h[near[0], near[1]])
gy, gx = np.gradient(h)
# 外轮廓边上：用到透明区域的距离梯度，保证法线是横的
de = ndi.distance_transform_edt(solid)
ey, ex = np.gradient(de)
el = np.hypot(ex, ey) + 1e-6
edge = solid & (de < 2.0)
gx = np.where(edge, ex / el * 6, gx); gy = np.where(edge, ey / el * 6, gy)
flat = 0.4
nx, ny, nz = -gx, gy, np.full_like(gx, 1 + flat)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
N = np.dstack([(nx / ln * 0.5 + 0.5) * 255, (ny / ln * 0.5 + 0.5) * 255, (nz / ln * 0.5 + 0.5) * 255, a * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(N, 'RGBA').save(out_n)

mat = np.zeros(L.shape, np.uint8); extra = np.zeros(L.shape, np.float32)
skin = (r > 195) & (g > 140) & (g < 228) & (b > 105) & (b < 205) & (r - g > 12) & (r - g < 75) & (r - b > 28)
hair = (L < 95) & (np.abs(r - b) < 45)
yellow = (r > 190) & (g > 140) & (b < 130) & (r - b > 90)
white = (L > 225) & (b > 180)
red = (r > 150) & (g < 95) & (b < 95)
skin &= ~(ndi.uniform_filter(yellow.astype(np.float32), 15) > 0.3)   # 黄裙上的米色波点不是皮肤
mat[skin] = 1
mat[hair] = 2; extra[hair] = 0.6
for m in (yellow, white, red): mat[m] = 3; extra[m] = 0.3
mat = np.where(inside, mat, mat[near[0], near[1]]); extra = np.where(inside, extra, extra[near[0], near[1]])
M = np.dstack([np.zeros_like(mat), mat * 30, (extra * 255).astype(np.uint8), (a * 255).astype(np.uint8)]).astype(np.uint8)
Image.fromarray(M, 'RGBA').save(out_m)
print(out_n, out_m, 'skin %.2f hair %.2f cloth %.2f' % (skin[solid].mean(), hair[solid].mean(), (mat[solid] == 3).mean()))
