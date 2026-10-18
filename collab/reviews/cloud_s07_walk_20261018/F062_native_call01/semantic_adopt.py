#!/usr/bin/env python3
"""Extract complete native trousers; erase cleanup islands without importing shifted hands/shoes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
from scipy.ndimage import binary_dilation,binary_fill_holes,binary_closing,label
R=Path(__file__).resolve().parent;V=R.parent/'next3_preflight_61sol/hip_calibrated_062_v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=Image.open(V/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png').convert('RGBA');a=np.array(src);size=src.size
q=Image.open(R/'qa/call01_whole_crop_uniform_alignment.png').convert('RGBA').crop((25,0,495,780));donor=np.zeros_like(a);donor[280:1060,650:1120]=np.array(q)
old=np.array(Image.open(V/'masks/F062_full_pants_and_sleeves_WHITE_EDIT_PENDING.png'))>0
yy,xx=np.indices(a.shape[:2]);rgb=donor[:,:,:3].astype(int)
# The returned native artwork's navy cloth, including its true black outer ink
# and AA. Color identifies material; no RGB values are modified or repainted.
seed=(donor[:,:,3]>=128)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)&(yy>=530)&(yy<=980)
labs,_=label(seed);counts=np.bincount(labs.ravel());counts[0]=0;navy=labs==int(counts.argmax())
navy=binary_fill_holes(binary_closing(navy,iterations=2))
pants=binary_dilation(navy,iterations=2)&(donor[:,:,3]>0)&(yy>=530)&(yy<=980)
def load(n):return np.array(Image.open(V/'masks'/f'{n}.png'))>0
body=np.array(Image.open(V/'layers/F062_body_head_blouse.png'))[:,:,3]>0
feet=load('HARD_visible_complete_shoes_ankles')
arms=np.zeros_like(old)
for name in ['near_complete_arm','far_complete_arm_jade_hand']:
 la=np.array(Image.open(V/'layers'/f'F062_{name}.png'))
 lab,_=label(la[:,:,3]>=20);ct=np.bincount(lab.ravel());ct[0]=0;material=(la[:,:,3]>0)&binary_dilation(lab==int(ct.argmax()),iterations=3)
 arms|=material
# Retain the actual source layer visibility; do not reintroduce hidden arms.
arms&=(a[:,:,3]>0);arms&=~body
locked=body|arms|feet
release=load('sleeve_release')
root_join=release&binary_dilation(body,iterations=4)&binary_dilation(arms,iterations=4)&~locked&(donor[:,:,3]>=128)
pants&=~locked
new_pants_outside_old=pants&~old
cleanup=old&~locked&~pants&~root_join
c=a.copy();c[cleanup]=0;c[pants]=donor[pants];c[root_join]=donor[root_join]
changed=np.any(c!=a,axis=2)
allowed=old|new_pants_outside_old
assert not (changed&~allowed).any();assert np.array_equal(c[locked],a[locked])
for name,z in [('native_complete_trousers_adoption',pants),('new_native_pants_AA_beyond_preflight_mask',new_pants_outside_old),('actual_source_body_arm_feet_fully_protected',locked),('cleanup_islands_not_new_objects',cleanup),('only_real_sleeve_void_join',root_join)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
out=R/'candidate/F062_complete_native_trousers_semantic_PENDING.png';z=Image.fromarray(c);z.save(out)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for nm,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 def bg(p):
  b=Image.new('RGBA',size,col);b.alpha_composite(p);return b.convert('RGB')
 full=bg(z);full.save(R/f'qa/F062_semantic_full_{nm}.png');full.crop((650,280,1120,1060)).save(R/f'qa/F062_semantic_crop_{nm}.png')
 sheet=Image.new('RGB',(1050,860),(235,241,246));d=ImageDraw.Draw(sheet)
 for i,(label,p) in enumerate([('唯一原生完整裤体',Image.fromarray(donor)),('完整裤体采用／真手鞋头衣保留',z)]):
  sheet.paste(bg(p).crop((650,280,1120,1060)),(i*525+15,45));d.text((i*525+15,12),label,font=font,fill='#253740')
 sheet.save(R/f'qa/native_and_semantic_{nm}.png')
report={'status':'COMPLETE_NATIVE_TROUSERS_SEMANTIC_ADOPTION_PENDING_ACTUAL_REVIEW','raw_sha256':'efa81720135228ccec5c7af65b05d75a8ec2db39b28c2dd1d6ba740ad89722b0','candidate_sha256':sha(out),'native_pants_adopted_pixels':int(pants.sum()),'native_whole_pants_silhouette_AA_beyond_old_mask_pixels':int(new_pants_outside_old.sum()),'scope_note':'Honest post-return whole-trousers semantic refinement: native outer contour extends beyond technical old-piece mask; no protected material changed. New mask saved explicitly.','cleanup_pixels':int(cleanup.sum()),'sleeve_true_void_join_pixels':int(root_join.sum()),'actual_body_arm_feet_RGBA_changes':int(np.any(c[locked]!=a[locked],axis=1).sum()),'outside_old_mask_and_native_whole_pants_changes':int((changed&~allowed).sum()),'new_image_calls_this_refinement':0,'F062_requests':1,'F062_originals':1,'raw_art_uniform_scale_unchanged':0.5078125,'no_segment_warp_recolor_or_code_drawn_body':True,'existing_exact_mask_trial_not_approved':True}
(R/'qa/semantic_adoption_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
