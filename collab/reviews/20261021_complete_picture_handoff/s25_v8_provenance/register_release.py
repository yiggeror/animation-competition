from PIL import Image
from pathlib import Path
P=Path(__file__).parent;O=P/'candidate/assets/chars/s25_smooth_20261021'
for f in [38,41,44,48]:
 p=P/f'release{f}.png'
 if not p.exists():continue
 im=Image.open(p).convert('RGBA').resize((1920,1080),Image.Resampling.LANCZOS);im.save(O/f'F{f:03}.png')
 r=im.copy();r.paste((0,0,0,0),(0,0,1000,1080));r.save(O/f'R{f:03}.png')
 l=im.copy();l.paste((0,0,0,0),(1000,0,1920,1080));l.save(O/'Lrelease.png')
