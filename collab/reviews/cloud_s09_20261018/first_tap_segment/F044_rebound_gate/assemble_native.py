#!/usr/bin/env python3
"""Canonical whole-crop registration and original-domain first adoption."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawpath=R/'originals/F044_call01_raw.png';assert sha(rawpath)=='3d0561f41e8dadd5f318ae51b9b732f8ddc6d3835217ee009d4cc45482fc25a4'
raw=Image.open(rawpath).convert('RGBA');assert raw.size==(1254,1254)
aligned=raw.resize((620,620),Image.Resampling.LANCZOS);aligned.save(R/'qa/call01_whole_crop_uniform_alignment.png')
srcpath=R/'reference/F044_actual_source_preposition_NOT_ART.png';source=Image.open(srcpath).convert('RGBA');a=np.array(source)
native=np.zeros_like(a);native[240:860,620:1240]=np.array(aligned)
edit=np.array(Image.open(R/'masks/F044_complete_near_arm_vacated_WHITE_EDIT_PENDING.png'))>0
c=a.copy();c[edit]=native[edit]
out=R/'candidate/F044_native_exact_domain_PENDING.png';im=Image.fromarray(c);im.save(out)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
for name,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 def bg(z):
  p=Image.new('RGBA',z.size,color);p.alpha_composite(z);return p.convert('RGB')
 bg(im).save(R/f'qa/F044_first_adoption_full_{name}.png')
 sheet=Image.new('RGB',(1860,655),(238,242,246));d=ImageDraw.Draw(sheet)
 for i,(title,z) in enumerate([('044已批真实源预摆／非画稿',source.crop((620,240,1240,860))),('044唯一原生整块等比',aligned),('原白域采用／待形体实审',im.crop((620,240,1240,860)))]):
  sheet.paste(bg(z),(i*620,35));d.text((i*620+5,8),title,font=font,fill='#253740')
 sheet.save(R/f'qa/preposition_native_adopted_{name}.png')
guards={}
for p in ['head_neck_collar_actual','near_ruffle_actual_material','far_puff_actual_visible','far_arm_actual_visible_except_new_foreground','fixed_receiver_palm_material','rigid_grip_torch_actual_material','waist_and_skirt_actual_material']:
 g=np.array(Image.open(R/'masks'/f'{p}.png'))>0;guards[p]=int(np.any(c[g]!=a[g],axis=1).sum());assert guards[p]==0
report={'status':'FIRST_ADOPTION_PENDING_ACTUAL_ART_REVIEW_NOT_F044_PASS','raw_SHA256':sha(rawpath),'raw_dimensions':raw.size,'canonical_dimensions':aligned.size,'single_uniform_whole_crop_scale':620/1254,'paste_xy':[620,240],'no_rotation_additional_translation_or_limb_warp':True,'candidate_sha256':sha(out),'source_preposition_sha256':sha(srcpath),'original_white_domain_pixels':int(edit.sum()),'outside_original_white_domain_RGBA_changes':int(np.any(c[~edit]!=a[~edit],axis=1).sum()),'protected_RGBA_changes':guards,'F044_native_requests':1,'F044_native_originals':1,'S09_requests':18,'S09_originals':17,'F048_unopened':True}
(R/'qa/first_adoption_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
