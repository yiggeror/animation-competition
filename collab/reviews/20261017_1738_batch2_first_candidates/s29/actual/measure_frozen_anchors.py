# 在一串关键帧图里自动找两个定位点（凳腿之类整段不动的东西）：把母版上定位点周围的一块按分辨率比缩放后，
# 在每张图的预期位置附近做归一化互相关（NCC），取最匹配的位置。输出可以直接抄进 flip.json 的 frames 项。
# 同时报告匹配分数（1 = 完全一样）和第三个检查点的残差：分数低或残差大，说明凳子被生图画变形了，要人工核。
# 用法：python3 -I tools/flip_anchors.py 母版.png "x1,y1;x2,y2" "检查点x,y" 图1.png [图2.png …]
import json
import math
import sys
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

master, pts, check, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
A = [tuple(map(float, p.split(','))) for p in pts.split(';')]
C = tuple(map(float, check.split(',')))
PATCH = (-45, -110, 45, 15)   # 定位点周围取的块（母版像素，左上右下相对定位点）
SEARCH = 40                   # 在预期位置附近搜索的半径（图的像素）


def gray(path):
    im = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', im.size, (128, 128, 128, 255)); bg.alpha_composite(im)
    return bg.convert('L')


def match(Mg, Cg, p, s):
    x0, y0 = max(0, p[0] + PATCH[0]), max(0, p[1] + PATCH[1])
    x1, y1 = min(Mg.width, p[0] + PATCH[2]), min(Mg.height, p[1] + PATCH[3])
    t = np.asarray(Mg.crop((int(x0), int(y0), int(x1), int(y1))).resize((round((x1 - x0) * s), round((y1 - y0) * s)), Image.LANCZOS), np.float64)
    ex, ey = x0 * s, y0 * s                      # 块左上角的预期位置
    sx0, sy0 = int(ex) - SEARCH, int(ey) - SEARCH
    P = SEARCH + 2   # 图外补一圈灰（和合成底色一样），定位点贴着图边时也能往外搜
    big = np.pad(np.asarray(Cg, np.float64), P, constant_values=128)
    win = big[sy0 + P:sy0 + P + t.shape[0] + 2 * SEARCH, sx0 + P:sx0 + P + t.shape[1] + 2 * SEARCH]
    t = t - t.mean(); n = t.size
    num = fftconvolve(win, t[::-1, ::-1], mode='valid')
    ones = np.ones(t.shape)
    s1 = fftconvolve(win, ones, mode='valid'); s2 = fftconvolve(win * win, ones, mode='valid')
    den = np.sqrt(np.maximum(s2 - s1 * s1 / n, 1e-9)) * math.sqrt((t * t).sum())
    ncc = num / den
    iy, ix = np.unravel_index(np.argmax(ncc), ncc.shape)
    # 亚像素：峰值附近抛物线拟合
    def sub(a, i):
        if 0 < i < len(a) - 1:
            d = a[i - 1] - 2 * a[i] + a[i + 1]
            return i + (0.5 * (a[i - 1] - a[i + 1]) / d if d else 0)
        return i
    fx, fy = sub(ncc[iy, :], ix), sub(ncc[:, ix], iy)
    return ((p[0] - x0) * s + sx0 + fx, (p[1] - y0) * s + sy0 + fy), float(ncc[iy, ix])


Mg = gray(master)
out = []
for f in files:
    Cg = gray(f)
    s = math.sqrt(Cg.width * Cg.height / (Mg.width * Mg.height))
    (a1, q1), (a2, q2) = match(Mg, Cg, A[0], s), match(Mg, Cg, A[1], s)
    c, qc = match(Mg, Cg, C, s)
    # 用两点算出的相似变换把检查点映回母版，看离它应在的位置多远
    va, vr = (a2[0] - a1[0], a2[1] - a1[1]), (A[1][0] - A[0][0], A[1][1] - A[0][1])
    k = math.hypot(*vr) / math.hypot(*va); ang = math.atan2(vr[1], vr[0]) - math.atan2(va[1], va[0])
    dx, dy = c[0] - a1[0], c[1] - a1[1]
    cm = (A[0][0] + k * (math.cos(ang) * dx - math.sin(ang) * dy), A[0][1] + k * (math.sin(ang) * dx + math.cos(ang) * dy))
    out.append({'file': f.rsplit('/', 1)[-1].rsplit('.', 1)[0], 'anchors': [[round(v, 2) for v in a1], [round(v, 2) for v in a2]],
                'score': [round(q1, 3), round(q2, 3), round(qc, 3)], 'check_residual_px': round(math.dist(cm, C), 2)})
print(json.dumps(out, ensure_ascii=False, indent=1))
