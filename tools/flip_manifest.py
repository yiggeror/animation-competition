# 逐帧动画的清单：每个输出帧用的是哪张关键帧、每张图的哈希和尺寸、对齐要转多少度和缩放多少（和 js/rig/flipbook.js 同样的算法）。
# 交审查用，确认成片里实际放的是哪几张图、一拍三有没有落实。
# 用法：python3 -I tools/flip_manifest.py x18_laugh [总帧数，默认 72]   → 打印 JSON
import hashlib
import json
import math
import sys
from PIL import Image

name = sys.argv[1]
total = int(sys.argv[2]) if len(sys.argv) > 2 else 72
spec = json.load(open(f'assets/flips/{name}.flip.json', encoding='utf-8'))
(r1, r2) = spec['target']['anchors']
out = {'mode': 'flipbook', 'flip': f'assets/flips/{name}.flip.json', 'fps': spec.get('fps', 24), 'frames': [], 'perFrame': []}
for f in spec['frames']:
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
            files[p] = None
    out['frames'].append({'file': f['file'], 'deg': round(deg, 2), 'scale': round(s, 4), 'files': files})
tl = spec['timelineFrames']
for n in range(total):
    k = [i for n0, i in tl if n >= n0][-1]
    out['perFrame'].append(k)
print(json.dumps(out, ensure_ascii=False, indent=1))
