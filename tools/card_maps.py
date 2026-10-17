# 透明底的人物图 → 光照卡片要的法线图和材质图（编码和 js/lamp/cards.js 一致）。
# 法线：按材质区域（皮肤、头发、布）和很深的轮廓线分块，每块按到分界的距离"鼓"起来（圆弧截面），再模糊一点；
#       细节线（印花、发丝、衣褶）只进颜色。外轮廓边上法线是横的，被侧光、逆光勾出亮边。
# 材质：按颜色分——皮肤 1、头发 2、布 3（裙子、领子、绒球、凉鞋），其他（凳子）0；线取旁边区域的材质。
# 用法：python3 -I tools/card_maps.py 透明底.png 法线.png 材质.png [圆鼓半径像素] [灰白头发：图片顶部多少比例以内]
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

src, out_n, out_m = sys.argv[1:4]
R = float(sys.argv[4]) if len(sys.argv) > 4 else 18.0
greyTop = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
im = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
rgb, a = im[..., :3], im[..., 3] / 255.0
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
L = rgb @ np.array([0.299, 0.587, 0.114])
solid = a > 0.5
# 分区域：材质分类（皮肤 / 头发 / 布 / 其他）的交界，加上很深、很明显的轮廓线。
# 印花、发丝、衣褶这些细节线只进颜色，不参与造型——不然每朵小花、每绺头发都会鼓成一个包，受侧光时斑斑驳驳
tophat = ndi.grey_closing(L, size=(5, 5)) - L
line = (tophat > 28) & solid                                       # 所有细线（材质归属时让给旁边的区域）
inside = solid & ~line
# 每个像素最近的"区域内"像素（线和边缘用它的值）
near = ndi.distance_transform_edt(~inside, return_distances=False, return_indices=True)
mat = np.zeros(L.shape, np.uint8); extra = np.zeros(L.shape, np.float32)
skin = (r > 195) & (g > 140) & (g < 228) & (b > 105) & (b < 205) & (r - g > 12) & (r - g < 75) & (r - b > 28)
hair = (L < 95) & (np.abs(r - b) < 45) & (b - r < 20)          # 黑头发（深蓝的裤子不算）
if greyTop > 0:                                                  # 奶奶的灰白头发：只在图片顶部那一截找
    rows = np.arange(L.shape[0])[:, None] < greyTop * L.shape[0]
    hair |= rows & (L > 120) & (L < 235) & ((rgb.max(-1) - rgb.min(-1)) < 22)
yellow = (r > 190) & (g > 140) & (b < 130) & (r - b > 90)
white = (L > 225) & (b > 180)
red = (r > 150) & (g < 95) & (b < 95)
blue = (b > r + 20) & (b > 60)                                   # 蓝底碎花衬衫、藏青裤子
black = (L < 60) & ~hair                                         # 黑布鞋
skin &= ~(ndi.uniform_filter(yellow.astype(np.float32), 15) > 0.3)   # 黄裙上的米色波点不是皮肤
mat[skin] = 1
mat[hair] = 2; extra[hair] = 0.6
for m in (yellow, white, red, blue, black): mat[m] = 3; extra[m] = 0.3
mat = np.where(inside, mat, mat[near[0], near[1]]); extra = np.where(inside, extra, extra[near[0], near[1]])
# 小碎块（比如个别像素被分错）并进周围的大类
mat = ndi.median_filter(mat, size=5)
# 被别的材质包住的小块"其他"（比如生图里偏红、带排线的腮红）改成周围最多的材质：不然打光时被当成凳子木头，脸上一块黑斑
lab, n = ndi.label((mat == 0) & solid)
for i, sl in enumerate(ndi.find_objects(lab), 1):
    if sl is None: continue
    sl = tuple(slice(max(0, s.start - 4), s.stop + 4) for s in sl)
    blob = lab[sl] == i
    if blob.sum() > 0.004 * solid.sum(): continue            # 凳子这种大块不动
    ring = ndi.binary_dilation(blob, iterations=3) & ~blob & solid[sl]
    vals = mat[sl][ring]; vals = vals[vals != 0]
    if vals.size: mat[sl][blob] = np.bincount(vals).argmax()
edgeMat = np.zeros_like(solid)
for dy, dx in ((0, 1), (1, 0)):
    edgeMat |= np.roll(mat, (dy, dx), axis=(0, 1)) != mat
strong = (tophat > 45) & (L < 70) & (mat != 2)                     # 很深的轮廓线（四肢的外轮廓）；头发里的发丝线不算
inside = solid & ~edgeMat & ~strong
near = ndi.distance_transform_edt(~inside, return_distances=False, return_indices=True)

d = ndi.distance_transform_edt(inside)
u = np.minimum(d + 0.5, R) / R
h = np.where(inside, R * np.sqrt(np.maximum(0.0, 1 - (1 - u) ** 2)), 0.0)
h = ndi.gaussian_filter(h, max(1.0, R * 0.3))                    # 平滑一些：剩下的分界只是平缓的凹，不是一道棱
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

M = np.dstack([np.zeros_like(mat), mat * 30, (extra * 255).astype(np.uint8), (a * 255).astype(np.uint8)]).astype(np.uint8)
Image.fromarray(M, 'RGBA').save(out_m)
print(out_n, out_m, 'skin %.2f hair %.2f cloth %.2f' % (skin[solid].mean(), hair[solid].mean(), (mat[solid] == 3).mean()))
