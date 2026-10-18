#!/usr/bin/env python3
"""Compare actual Canvas box-contact controls; only QA crops and numeric records."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
P=Path(__file__).resolve().parents[1]
out=Image.new('RGB',(1540,640),'#f3f0e8');draw=ImageDraw.Draw(out)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22);rows=[]
for i,f in enumerate([20,22]):
 a=Image.open(f'build/S08_first23/{f:05}.png').convert('RGB');b=Image.open(P/f'diagnostic/F{f:03}_without_box_contact_ACTUAL_CONTROL.png').convert('RGB')
 delta=np.array(a).astype(int)-np.array(b).astype(int);changed=np.any(delta!=0,axis=2);ys,xs=np.where(changed);assert len(xs)>0
 row={'frame':f,'changed_pixels':len(xs),'bbox_xyxy_exclusive':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'RGB_min_delta':delta.min(axis=(0,1)).tolist(),'RGB_max_delta':delta.max(axis=(0,1)).tolist(),'crosses_front_lip981':bool(ys.max()>=981)}
 assert not row['crosses_front_lip981'];assert ys.min()==ys.max()==970;rows.append(row)
 for col,(im,label)in enumerate([(a,'采用：盒影开启'),(b,'诊断：仅盒影关闭')]):
  crop=im.crop((1040,938,1165,980)).resize((750,252),Image.Resampling.NEAREST);x,y=col*770+5,i*320+40;out.paste(crop,(x,y));draw.text((x,y-30),f'F{f:03} {label} · 实际Canvas6×裁近',font=font,fill='#25333d')
out.save(P/'06_box_contact_on_off_ACTUAL_CONTROL.png')
(P/'contact_actual_difference.json').write_text(json.dumps({'status':'PASS_TINY_ACTUAL_BOX_CONTACT_ATTACHED_WITHIN_TABLE_SURFACE','method':'Same fixed browser with one contact omitted only in memory;adopted diagnostic rerenders identical main20 PNG. Pixel difference between lossless real Canvas frames,not painted shadow.','records':rows,'source_files_modified':False,'control_adopted':False},ensure_ascii=False,indent=2)+'\n')
print('PASS box contact attached at970;actual changed counts', [r['changed_pixels']for r in rows],';no frontlip981 crossing')
