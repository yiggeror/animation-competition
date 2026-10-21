from PIL import Image
from pathlib import Path
P=Path(__file__).parent;O=P/'candidate/assets/chars/s25_smooth_20261021'
for n,sc,src in [('mid',.9,(875,700)),('late',1.14,(875,810))]:
 im=Image.open(P/f'grip_{n}.png').convert('RGBA');im.paste((0,0,0,0),(0,0,810 if n=='mid' else 840,im.height));tx=1010-src[0]*sc;ty=950-src[1]*sc;im=im.transform((1920,1080),Image.Transform.AFFINE,(1/sc,0,-tx/sc,0,1/sc,-ty/sc),Image.Resampling.BICUBIC);im.save(O/f'Rgrip_{n}.png')
