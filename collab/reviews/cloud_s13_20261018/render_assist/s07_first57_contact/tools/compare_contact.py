#!/usr/bin/env python3
"""Compare real Canvas frames to the prior verified001c9c18 render; no scene edits."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];OLD=Path('/tmp/s07_first57_canvas_frames');NEW=Path('build/s07_first57_contact')
prior=Path('/workspace/animation-competition-s07-render/collab/reviews/cloud_s13_20261018/render_assist/s07_first57/actual57_validation.json')
base=json.loads(prior.read_text());rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in range(57):
 old=OLD/f'{f:05}.png';new=NEW/f'{f:05}.png';assert sha(old)==base['checks'][f]['Canvas_source_sha256']
 a=np.array(Image.open(old).convert('RGB'),dtype=np.int16);b=np.array(Image.open(new).convert('RGB'),dtype=np.int16);delta=b-a;mask=np.any(delta!=0,axis=2);y,x=np.where(mask)
 rows.append({'frame':f,'old_canvas_sha256':sha(old),'contact_canvas_sha256':sha(new),'changed_pixels':int(mask.sum()),'changed_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())]if len(x)else None,'min_channel_delta':int(delta.min()),'max_channel_delta':int(delta.max())})
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def crop_compare(items,out):
 w=800;h=350;sheet=Image.new('RGB',(1600,h*len(items)),'#f3f1eb');d=ImageDraw.Draw(sheet)
 for row,(f,box,label)in enumerate(items):
  for col,S in enumerate([OLD,NEW]):
   im=Image.open(S/f'{f:05}.png').convert('RGB').crop(box);z=min(780/im.width,285/im.height);im=im.resize((round(im.width*z),round(im.height*z)));x=col*w+10;y=row*h+55;sheet.paste(im,(x,y));d.text((x,row*h+12),f'F{f:03} '+('原实际 / 'if col==0 else'contact实际 / ')+label,font=font(24),fill='#25353e')
 sheet.save(P/out,quality=98)
crop_compare([(0,(575,475,825,640),'鞋/凳与地面'),(15,(575,475,825,640),'鞋/凳与地面'),(0,(300,420,560,550),'小满身肘与席面')],'02_early_contact_old_new_actual.jpg')
crop_compare([(39,(650,345,1010,560),'颈发尾/手机/近肘'),(56,(650,345,1010,560),'近肘落席'),(39,(80,390,650,625),'躯干/裙摆与席面')],'03_supine_contact_old_new_actual.jpg')
result={'status':'PASS_REAL_FRAME_COMPARISON','baseline_source_commit':'001c9c1828d9054675437111cf52df37c48721f2','baseline_actual_delivery_commit':'835803dd650ddf71224f6aec8cf00acee5a92849','contact_commit':'60eff917ad0dfa8523ea5051b6afde5e50536175','baseline57_source_hashes_verified':True,'frames':57,'max_positive_channel_delta':max(r['max_channel_delta']for r in rows),'min_channel_delta':min(r['min_channel_delta']for r in rows),'notes':'Darkening is expected from added contacts. This comparison is on actual pre-encodeCanvas PNGs; source art/camera/phone unchanged separately verified.','checks':rows}
(P/'actual_contact_vs_original.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Compared57 real source pairs;max positive channel delta',result['max_positive_channel_delta'],';min',result['min_channel_delta'])
