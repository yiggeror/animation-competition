#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys,json,hashlib
P=Path(__file__).resolve().parents[1];f=int(sys.argv[1]);previous=Path(sys.argv[2]);current=P/f'candidates/F{f:03}_rgba.png'
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im):
 bg=Image.new('RGBA',im.size,(209,215,215,255));bg.alpha_composite(im);return bg.convert('RGB')
out=Image.new('RGB',(1600,1120),'#f3f0e8');draw=ImageDraw.Draw(out)
for i,(path,label)in enumerate([(previous,'前一合格态'),(current,f'F{f:03}候选')]):
 im=Image.open(path).convert('RGBA');panel=comp(im);panel.thumbnail((700,1050));out.paste(panel,(i*800+25,55));draw.text((i*800+15,15),label,font=font(27),fill='#25333d')
out.save(P/f'qa/F{f:03}_previous_current_full.jpg',quality=97)
out=Image.new('RGB',(1600,760),'#f3f0e8');draw=ImageDraw.Draw(out)
for i,(path,label)in enumerate([(previous,'前一合格态 · 颏颈/耳根'),(current,f'F{f:03} · 颏颈/耳根')]):
 panel=comp(Image.open(path).convert('RGBA')).crop((150,510,940,1190));out.paste(panel,(i*800+5,55));draw.text((i*800+10,15),label,font=font(26),fill='#25333d')
out.save(P/f'qa/F{f:03}_previous_current_neck_ears.jpg',quality=97)
im=Image.open(current);bb=im.getchannel('A').point(lambda v:255 if v>=248 else 0).getbbox()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'frame':f,'previous_path':str(previous),'previous_sha256':sha(previous),'candidate_sha256':sha(current),'B_registration':[.7,590,20],'opaque_alpha_threshold':248,'opaque_bbox':list(bb),'opaque_top_margin_scene_px':round(20+.7*bb[1],2),'status':'DIAGNOSTIC_ONLY_ACTUAL_VISUAL_REVIEW_REQUIRED','not_Canvas_scene':True}
(P/f'qa/F{f:03}_continuity_diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
