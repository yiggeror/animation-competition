from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent
a=Image.open(B/'inputs/k06_rightpad_1672x941.png').getchannel('A')
for f in [65,74,75,76]:
    p=B/f'F{f:03d}_candidate.png'
    im=Image.open(p).convert('RGBA')
    im.putalpha(a)
    im.save(p)
