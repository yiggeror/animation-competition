from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_propagation
import numpy as np,json
R=Path('astra_s07_xiaoman_release_20261018_1110');F='/workspace/scratch/f060b5601755/astra_s03b_painted_pilot_20261018/refs/NotoSansSC-VF.ttf'
B=Image.open(R/'sources/bg_01_room_wide_base_v2_draft.png').convert('RGB');U=Image.open(R/'sources/anim_07_xiaoman_flop.png').convert('RGB');P=Image.open(R/'sources/anim_01_xiaoman_prone_phone.png').convert('RGB')
# Only diagnostic context extraction. Mask is explicit and saved. Originals are not modified.
def cut(im,name):
 a=np.array(im).astype(int);ok=(a.min(2)>120)&((a.max(2)-a.min(2))<30);seed=np.zeros(ok.shape,bool);seed[0,:]=ok[0,:];seed[-1,:]=ok[-1,:];seed[:,0]=ok[:,0];seed[:,-1]=ok[:,-1];bg=binary_propagation(seed,mask=ok);m=(~bg).astype('uint8')*255;Image.fromarray(m).save(R/'masks'/f'{name}_diagnostic_only_mask.png');out=im.convert('RGBA');out.putalpha(Image.fromarray(m));out.save(R/'reference'/f'{name}_diagnostic_only_cutout.png');return out
cu=cut(U,'supine_source');cp=cut(P,'prone_source')
board=Image.new('RGB',(1600,1300),'white');d=ImageDraw.Draw(board);font=lambda n:ImageFont.truetype(F,n)
def t(p,s,n=22,c='#17384a'):d.text(p,s,font=font(n),fill=c)
t((20,10),'同场接地核查：原像素副本 + 显式诊断mask；只用于配准，非生产抠图',28)
for i,(im,s,xy,lab) in enumerate([(cp,.16,(430,533),'S01沿用尺度 / F000待新画严格侧面'),(cu,.22,(350.72,526.76),'建议新躺姿体量 / F039仍须重画双臂和体积')]):
 w=B.convert('RGBA');a=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);w.alpha_composite(a,(round(xy[0]),round(xy[1])));w=w.convert('RGB');box=(300,540,780,735);a=w.crop(box).resize((1440,585),Image.Resampling.LANCZOS);board.paste(a,(80,60+i*610));t((90,70+i*610),lab,24)
board.save(R/'reference/06_context_contact_diagnostic.jpg',quality=95)
(R/'masks/README.txt').write_text('These two masks are diagnostic-only connected-background mattes used to inspect placement on the scene mat. They are not accepted production cutouts. Original source bytes are unchanged. No generated image, no body deformation, no pose alteration. White=source pixels retained; black=background hidden. Transparent cutout copies in reference/.\n')
