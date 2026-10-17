# 把合作方交的一串关键帧原图处理成可用的帧：灰底图抠图、透明底图保留原透明度（整张画幅不裁，保持对齐）→ 材质图（card_maps）→ 柔和整体法线（card_soft）。
# 用法：python3 -I tools/prep_flip.py collab/refs/x18_f01.png [更多…]   → assets/chars/x18_f01.png、_n.png、_m.png
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image
for src in sys.argv[1:]:
    name = Path(src).stem
    w, h = Image.open(src).size
    out = f'assets/chars/{name}.png'
    im = Image.open(src)
    if 'A' in im.getbands() and im.getchannel('A').getextrema()[0] < 255:
        # 已经是透明底的图（生图工具直接给的 RGBA）：保留原来的透明度，不再重抠（重抠会把藏在透明处的颜色翻出来，Astra fff848b 实测）。
        # 只把"几乎不透明"拉满、"几乎透明"清零：生图的人物内部 alpha 是 253，不拉满会微微透出背景；外圈还有一层很淡的雾
        a = np.asarray(im.getchannel('A'), np.float32)
        a = np.clip((a - 6) / (247 - 6), 0, 1) * 255
        im = im.convert('RGBA'); im.putalpha(Image.fromarray(a.round().astype(np.uint8)))
        im.save(out)
    else:
        subprocess.run(['python3', '-I', 'tools/cutout.py', src, out, '14', f'0,0,{w},{h}'], check=True)
    subprocess.run(['python3', '-I', 'tools/card_maps.py', out, f'assets/chars/{name}_n.png', f'assets/chars/{name}_m.png'], check=True)
    subprocess.run(['python3', '-I', 'tools/card_soft.py', out, f'assets/chars/{name}_n.png'], check=True)   # 法线换成整体柔和的，避免一节一节的浮雕
    print(name, w, h)
