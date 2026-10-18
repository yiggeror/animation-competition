#!/usr/bin/env python3
"""One uniform whole-crop registration and actual native mask adoption; no geometry invented."""
from pathlib import Path
import json,hashlib,base64
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;P=R.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((R/'requests/input_freeze.json').read_text())
for q in freeze['inputs']:assert sha(q['path'])==q['sha256']
ret=json.loads((R/'requests/raw_return.json').read_text());rawpath=R/'originals/F042_call02_raw.png';assert rawpath.read_bytes()==base64.b64decode(ret['image_url'].split(',',1)[1])
p=json.loads((R/'preparation.json').read_text());source=Image.open(R/'reference/F042_complete_native_arm_registered_UNPASSED.png').convert('RGBA');a=np.array(source);m=np.array(Image.open(R/'masks/three_connection_domains_WHITE_EDIT.png'))>0
raw=Image.open(rawpath).convert('RGBA');x0,y0,x1,y1=p['crop_xyxy'];q=raw.width/(x1-x0);aligned=raw.transform((x1-x0,y1-y0),Image.Transform.AFFINE,(q,0,0,0,q,0),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));aligned.save(R/'qa/native_whole_crop_uniform_alignment.png')
c=a.copy();local=c[y0:y1,x0:x1];lm=m[y0:y1,x0:x1];local[lm]=np.array(aligned)[lm]
assert np.array_equal(c[~m],a[~m]);guards={}
for name in ['original_whole_grip_torch_PROTECTED','original_near_ruffle_material_PROTECTED']:
 g=np.array(Image.open(R/f'masks/{name}.png'))>0;guards[name]=int(np.any(c[g]!=a[g],axis=1).sum());assert guards[name]==0
candidate=Image.fromarray(c);out=R/'candidate/F042_native_connections_PENDING.png';candidate.save(out)
for nm,col in [('gray',(214,223,231,255)),('dark',(36,44,53,255))]:
 bg=Image.new('RGBA',source.size,col);bg.alpha_composite(candidate);bg.convert('RGB').save(R/f'qa/F042_full_{nm}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
regions=[('近袖单弧',(672,623,741,702)),('腕截口',(1010,565,1078,638)),('旧臂残线/短划',(710,620,803,738))]
sheet=Image.new('RGB',(1500,780),(239,243,246));d=ImageDraw.Draw(sheet)
for i,(label,box) in enumerate(regions):
 for j,(title,im) in enumerate([('输入/未通过',source),('真实局部修绘/待审',candidate)]):
  bg=Image.new('RGBA',im.size,(213,223,231,255));bg.alpha_composite(im);qim=bg.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST);x=i*500+j*245;y=50;sheet.paste(qim.convert('RGB'),(x,y));d.text((x+3,8),label,font=font,fill='#26343e');d.text((x+3,30),title,font=font,fill='#26343e')
 full=Image.new('RGBA',im.size,(213,223,231,255));full.alpha_composite(im);sheet.paste(full.crop((650,560,1110,785)).resize((690,337)).convert('RGB'),(j*750,425))
sheet.save(R/'qa/actual_three_connections_before_after.png')
report={'status':'ONE_NATIVE_MINIMUM_CONNECTION_RETURN_RECOMPOSED_PENDING_AUTHOR_AND_61SOL_ACTUAL_REVIEW','raw_sha256':sha(rawpath),'raw_size':list(raw.size),'raw_return_bytes_equal':True,'one_uniform_raw_to_crop_scale':1/q,'one_uniform_translation':[0,0],'output_height_after_uniform_scale':raw.height/q,'target_height':y1-y0,'no_per_segment_scale':True,'adoption_mask_pixels':int(m.sum()),'outside_adoption_RGBA_changes':int(np.any(c[~m]!=a[~m],axis=1).sum()),'guard_changes':guards,'candidate_sha256':sha(out),'S09_total_requests':17,'S09_total_originals':16,'F042_requests':2,'F042_originals':2,'actual_static_and_exposure_pending':True,'F044_F048_unopened':True};(R/'qa/recomposition_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
