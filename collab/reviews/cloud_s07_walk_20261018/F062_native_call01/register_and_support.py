#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
P=R/'candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png'
s=.36410361842105265;tx=627.0254537171638;ty=402.7604324894813
inv=(1/s,0,-tx/s,0,1/s,-ty/s);size=(1672,941)
paths=[B/'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png',P]
worlds=[]
for n,p in zip([57,62],paths):
 z=Image.open(p).convert('RGBA').transform(size,Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));worlds.append(z)
 if n==62:z.save(R/'candidate/F062_world_registered_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
sheet=Image.new('RGB',(1100,820),(235,241,246));d=ImageDraw.Draw(sheet)
for i,(n,z) in enumerate(zip([57,62],worlds)):
 bg=Image.new('RGBA',size,(213,223,231,255));bg.alpha_composite(z);dr=ImageDraw.Draw(bg);dr.line((800,775,1090,775),fill='#53808b',width=1)
 panel=bg.crop((800,390,1080,790)).resize((532,760),Image.Resampling.LANCZOS);sheet.paste(panel.convert('RGB'),(i*550,45));d.text((i*550+8,10),f'F{n:03d} 同一注册／近鞋底774.874world',font=font,fill='#243640')
sheet.save(R/'qa/F057_F062_registered_actual_support_comparison.png')
report={'source_candidate_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'registration_unchanged':{'scale':s,'translation_xy':[tx,ty],'world_canvas':size,'inverse_pillow_affine':inv},'near_actual_shoe_alpha128_bottom_native':1022,'near_actual_shoe_alpha128_bottom_world':1022*s+ty,'whole_near_shoe_layer_no_rotation_translation_scale_or_recolor':True,'F062_native_original_count':1,'scope':'Actual single062 drawing and two-state registration/support comparison only; no scene render, movement tween, sound or entire-shot readiness.'}
(R/'qa/world_registration_and_support_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
