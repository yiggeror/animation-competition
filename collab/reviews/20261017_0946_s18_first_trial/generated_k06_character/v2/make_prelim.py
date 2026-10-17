from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,numpy as np
out=Path('/tmp/laidian-s18-pilot-audit/generated_k06_character/v2');root=Path('/workspace/animation-competition')
master=Image.open(root/'assets/chars/x18_laugh.png').convert('RGBA'); raw=Image.open('/tmp/laidian-s18-pilot-candidate/generated_k06_v2/x18_k06_candidate.png').convert('RGBA')
# Near-uniform nominal downscale for visual landmark measurement; final similarity is fitted separately.
s=(raw.width/master.width+raw.height/master.height)/2
nominal=raw.transform(master.size,Image.Transform.AFFINE,(s,0,0,0,s,0),Image.Resampling.BICUBIC)
gray=Image.new('RGBA',master.size,(220,220,220,255));gray.alpha_composite(nominal);gray=gray.convert('RGB');gray.save(out/'evidence/candidate_nominal_gray.png')
font=ImageFont.truetype(str(root/'assets/fonts/NotoSansSC-VF.ttf'),19)
for name,box in [('full',(0,0,635,1175)),('head',(30,60,470,480)),('stool_shoes',(0,820,635,1175)),('dress',(80,450,550,960))]:
    a=master.convert('RGB').crop(box);b=gray.crop(box);w,h=a.size
    im=Image.new('RGB',(w*2,h+35),'white');d=ImageDraw.Draw(im);im.paste(a,(0,35));im.paste(b,(w,35));d.text((7,6),'母版',font=font,fill='black');d.text((w+7,6),'新 k06（尺寸初归一，未配准）',font=font,fill='black');im.save(out/'evidence'/f'{name}_nominal_pair.png')
# Fine grid of only relevant stationary areas, in master-sized diagnostic coordinates.
im=gray.copy();d=ImageDraw.Draw(im)
for x in range(0,635,20):d.line((x,820,x,1175),fill=(20,180,180),width=1);d.text((x+1,820),str(x),fill=(0,80,100),font=font)
for y in range(840,1175,20):d.line((0,y,635,y),fill=(20,180,180),width=1);d.text((2,y+1),str(y),fill=(0,80,100),font=font)
im.crop((0,815,635,1175)).resize((1270,720)).save(out/'evidence/candidate_stool_grid.png')
print(json.dumps({'nominal_native_scale':s,'master':master.size,'candidate':raw.size,'alpha_bbox':raw.getchannel('A').getbbox()},indent=2))
