# 逐帧动画的清单：每个输出帧用的是哪张关键帧、每张图的哈希和尺寸、对齐要转多少度和缩放多少（和 js/rig/flipbook.js 同样的算法和校验）。
# 交审查用，确认成片里实际放的是哪几张图、一拍三有没有落实。只是静态计算，不代替实际渲染：flipbook 拒收的输入这里同样报错退出（退出码 1）。
# 用法：python3 -I tools/flip_manifest.py x18_laugh [总帧数，默认 72]   → 打印 JSON
import hashlib
import json
import math
import sys
from PIL import Image

name = sys.argv[1]
total = int(sys.argv[2]) if len(sys.argv) > 2 else 72
spec = json.load(open(f'assets/flips/{name}.flip.json', encoding='utf-8'))
MAX_DEG, SCALE = 6, (0.8, 1.25)   # 和 flipbook.js 一致


def bad(m):
    sys.exit(f'{name}.flip.json：{m}')


def span(a):
    ok = isinstance(a, list) and len(a) == 2 and all(isinstance(p, list) and len(p) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in p) for p in a)
    return math.dist(*a) if ok else 0


T = spec['target']
if span(T.get('anchors')) < 40: bad('target 要有两个相距 40 像素以上的定位点')
(r1, r2) = T['anchors']
out = {'mode': 'flipbook', 'flip': f'assets/flips/{name}.flip.json', 'fps': spec.get('fps', 24), 'frames': [], 'perFrame': []}
for f in spec['frames']:
    if span(f.get('anchors')) < 40: bad(f'{f["file"]} 的两个定位点要相距 40 像素以上')
    (a1, a2) = f['anchors']
    s = math.dist(r1, r2) / math.dist(a1, a2)
    deg = math.degrees(math.atan2(r2[1] - r1[1], r2[0] - r1[0]) - math.atan2(a2[1] - a1[1], a2[0] - a1[0]))
    deg = (deg + 180) % 360 - 180
    files = {}
    for suf in ('', '_n', '_m'):
        p = f'assets/chars/{f["file"]}{suf}.png'
        try:
            files[p] = {'sha256': hashlib.sha256(open(p, 'rb').read()).hexdigest(), 'size': Image.open(p).size}
        except FileNotFoundError:
            if not suf: bad(f'缺 {p}')
            files[p] = None
    w, h = files[f'assets/chars/{f["file"]}.png']['size']
    if any(v and v['size'] != (w, h) for v in files.values()): bad(f'{f["file"]} 的法线 / 材质图和固有色尺寸不一样')
    nom = math.sqrt(T['width'] * T['height'] / (w * h))
    if abs(deg) > MAX_DEG or not SCALE[0] <= s / nom <= SCALE[1]: bad(f'{f["file"]} 对齐要转 {deg:.1f}°、缩放 {s / nom:.2f}（已扣掉分辨率比 {nom:.3f}），超出范围')
    out['frames'].append({'file': f['file'], 'deg': round(deg, 2), 'scale': round(s, 4), 'scaleAfterResolution': round(s / nom, 4), 'files': files})
tl = spec['timelineFrames']
if not tl or tl[0][0] != 0: bad('timelineFrames 要从第 0 帧开始')
for k, (n, i) in enumerate(tl):
    if not isinstance(n, int) or (k and n <= tl[k - 1][0]): bad('timelineFrames 的帧号要是递增的整数')
    if not (isinstance(i, int) and 0 <= i < len(spec['frames'])): bad(f'timelineFrames 里的帧序号 {i} 不是整数或越界')
for n in range(total):
    out['perFrame'].append([i for n0, i in tl if n >= n0][-1])
print(json.dumps(out, ensure_ascii=False, indent=1))
