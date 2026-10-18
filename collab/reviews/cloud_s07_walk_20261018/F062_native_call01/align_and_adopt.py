#!/usr/bin/env python3
"""One global canonical scale, then exact approved mask adoption of native art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;V=B/'next3_preflight_61sol/hip_calibrated_062_v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawpath=R/'originals/F062_call01_raw.png';assert sha(rawpath)=='efa81720135228ccec5c7af65b05d75a8ec2db39b28c2dd1d6ba740ad89722b0'
raw=Image.open(rawpath).convert('RGBA');assert raw.size==(1024,1536)
aligned=raw.resize((520,780),Image.Resampling.LANCZOS)
aligned.save(R/'qa/call01_whole_crop_uniform_alignment.png')
donor=np.zeros((1080,1672,4),dtype=np.uint8);donor[280:1060,650:1120]=np.array(aligned.crop((25,0,495,780)))
srcpath=V/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png';source=Image.open(srcpath).convert('RGBA');a=np.array(source)
maskpath=V/'masks/F062_full_pants_and_sleeves_WHITE_EDIT_PENDING.png';assert sha(maskpath)=='dd82a555bf31f12d8b1a3ff5b8cf85dd743da9347004b7c5210a9378c4160634'
edit=np.array(Image.open(maskpath))>0
c=a.copy();c[edit]=donor[edit]
out=R/'candidate/F062_native_art_exact_approved_mask_PENDING.png';candidate=Image.fromarray(c);candidate.save(out)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
def bg(z,color):
 p=Image.new('RGBA',z.size,color);p.alpha_composite(z);return p.convert('RGB')
for nm,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 full=bg(candidate,color);full.save(R/f'qa/F062_full_{nm}.png')
 crop=full.crop((650,280,1120,1060));crop.save(R/f'qa/F062_adopted_crop_{nm}.png')
 sheet=Image.new('RGB',(1520,860),(236,241,245));d=ImageDraw.Draw(sheet)
 for i,(label,z) in enumerate([('已批像素预摆／非画稿',source.crop((650,280,1120,1060))),('唯一原生输出整体等比对齐',aligned.crop((25,0,495,780))),('按原白域采用／待实审',candidate.crop((650,280,1120,1060)))]):
  sheet.paste(bg(z,color),(i*505+10,45));d.text((i*505+10,10),label,font=font,fill='#253740')
 sheet.save(R/f'qa/preposition_native_adopted_{nm}.png')
guards={}
for name in ['HARD_complete_head_blouse_except_sleeve','HARD_visible_complete_arms_except_sleeve','HARD_visible_complete_shoes_ankles']:
 z=np.array(Image.open(V/'masks'/f'{name}.png'))>0;guards[name]=int(np.any(c[z]!=a[z],axis=1).sum());assert guards[name]==0
outside=int(np.any(c[~edit]!=a[~edit],axis=1).sum());assert outside==0
ra=np.array(raw)
report={'status':'SINGLE_NATIVE_ART_ADOPTED_WITH_EXACT_APPROVED_MASK_PENDING_ACTUAL_REVIEW','source_sha256':sha(srcpath),'raw_sha256':sha(rawpath),'candidate_sha256':sha(out),'raw_size':raw.size,'canonical_size':aligned.size,'whole_crop_uniform_scale':520/1024,'extra_translation':[0,0],'removed_transparent_padding_left_right':[25,25],'paste_xy':[650,280],'nonuniform_or_segment_warp':False,'approved_mask_sha256':sha(maskpath),'adoption_pixels':int(edit.sum()),'outside_approved_mask_RGBA_changes':outside,'protected_RGBA_changes':guards,'raw_alpha_corners':[int(ra[y,x,3]) for x,y in [(0,0),(1023,0),(0,1535),(1023,1535)]],'raw_alpha_nonzero':int((ra[:,:,3]>0).sum()),'new_image_requests':1,'actual_originals':1,'no_new_call_for_alignment':True,'not_yet_art_or_ground_contact_pass':True}
(R/'qa/exact_mask_adoption_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
