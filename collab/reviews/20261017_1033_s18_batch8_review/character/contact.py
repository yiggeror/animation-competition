from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
out=Path('/tmp/laidian-s18-pilot-audit/batch8_character');src=Path('/tmp/laidian-s18-batch8/originals');repo=Path('/workspace/animation-competition');font=ImageFont.truetype(str(repo/'assets/fonts/NotoSansSC-VF.ttf'),19)
files={}
def flat(path):
 im=Image.open(path).convert('RGBA'); bg=Image.new('RGBA',im.size,(190,190,190,255));bg.alpha_composite(im);files[str(path)]={'size':list(im.size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};return bg.convert('RGB').resize((635,1175),Image.Resampling.LANCZOS)
ims={k:flat(src/f'x18_{k}.png') for k in ['k02','k03','k04','k05','k08','k09','k10','k11']}
for group,base,keys in [('A','x16_arms_loose',['k02','k03','k04','k05']),('B','x18_laugh',['k08','k09','k10','k11'])]:
 images=[flat(repo/'assets/chars'/f'{base}.png')]+[ims[k] for k in keys];labels=[base]+keys
 # upper detail no registration, only nominal whole-image scaling for comparison.
 box=(35,5,465,660);w,h=430,655;strip=Image.new('RGB',(5*w,h+32),'white');d=ImageDraw.Draw(strip)
 for i,(lab,im) in enumerate(zip(labels,images)):
  strip.paste(im.crop(box),(i*w,32));d.text((i*w+5,5),lab+' 灰底合成 / 未配准',font=font,fill='black')
 strip.save(out/'evidence'/f'{group}_upper.png')
 contact=Image.new('RGB',(5*318,620),'white');d=ImageDraw.Draw(contact)
 for i,(lab,im) in enumerate(zip(labels,images)):
  contact.paste(im.resize((318,588)),(i*318,32));d.text((i*318+5,5),lab,font=font,fill='black')
 contact.save(out/'evidence'/f'{group}_full.png')
(out/'source_manifest.json').write_text(json.dumps(files,ensure_ascii=False,indent=2))
print('created four alpha-composited sheets; no source modifications')
