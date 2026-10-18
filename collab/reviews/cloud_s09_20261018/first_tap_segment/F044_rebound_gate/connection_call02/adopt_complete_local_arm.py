#!/usr/bin/env python3
"""Use actual repaired whole local arm rather than slicing native contours."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;T=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
trial=P/'candidate/F044_complete_native_arm_rigid_fit_TRIAL.png';a=np.array(Image.open(trial).convert('RGBA'));h,w=a.shape[:2];yy,xx=np.indices((h,w))
n=np.zeros_like(a);n[500:860,620:1160]=np.array(Image.open(R/'qa/native_whole_crop_uniform_alignment.png').convert('RGBA'))
rgb=n[:,:,:3].astype(int)
def poly(points):
 z=Image.new('L',(w,h));ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
roi=poly([(655,630),(748,600),(850,616),(1025,500),(1095,500),(1075,580),(973,691),(900,740),(815,750),(670,699)])
skin=(rgb[:,:,0]>165)&(rgb[:,:,0]-rgb[:,:,1]>12)&(rgb[:,:,1]-rgb[:,:,2]>10)&(n[:,:,3]>128)&roi
lab,_=label(skin);cc=lab[680,850];assert cc>0
core=binary_fill_holes(lab==cc)
arm=binary_dilation(core,iterations=2)&(n[:,:,3]>0)&roi
yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>130)&(rgb[:,:,2]<130)
white=rgb.min(axis=2)>220
arm&=~yellow&~white
old=np.array(Image.open(P/'production_layers/native_complete_near_arm_rigid_fit_trial.png'))[:,:,3]>0
old&=(yy>=500)&(yy<860)&(xx>=620)&(xx<1160)
explicit=np.array(Image.open(R/'masks/F044_explicit_connection_domain.png'))>0
pm=np.array(Image.open(P/'masks/fixed_receiver_palm_material.png'))>0
rr=np.array(Image.open(P/'masks/near_ruffle_actual_material.png'))>0
unit=np.array(Image.open(P/'reference/F044_rigid_hand_torch_up48_SOURCE.png').convert('RGBA'));um=unit[:,:,3]>0
release=np.array(Image.open(R/'masks/proximal_wrist_extraction_edge_release.png'))>0
domain=explicit|arm|old
domain&=~pm&~rr&~(um&~release)
out=a.copy();out[domain]=n[domain]
palm=np.array(Image.open(T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png').convert('RGBA'))
mother=np.array(Image.open(T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png').convert('RGBA'))
out[pm]=palm[pm];out[rr]=mother[rr]
outpath=P/'candidate/F044_complete_local_native_arm_TRIAL.png';Image.fromarray(out).save(outpath)
Image.fromarray(domain.astype('uint8')*255).save(R/'masks/complete_local_native_arm_adoption.png')
Image.fromarray(arm.astype('uint8')*255).save(R/'masks/native_actual_near_arm_material.png')
for name,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 b=Image.new('RGBA',(w,h),color);b.alpha_composite(Image.fromarray(out));b.convert('RGB').save(P/f'qa/F044_complete_local_native_arm_full_{name}.png');b.crop((620,420,1240,860)).convert('RGB').save(P/f'qa/F044_complete_local_native_arm_crop_{name}.png')
report={'status':'WHOLE_LOCAL_NATIVE_ARM_TRIAL_ACTUAL_REVIEW_PENDING','candidate_sha256':sha(outpath),'actual_native_arm_pixels':int(arm.sum()),'adoption_domain_pixels':int(domain.sum()),'replaced_old_whole_arm_material':int((old&domain).sum()),'source_unchanged_except90_wrist_extraction_edge':int((um&domain&~release).sum()),'new_request_count':0,'native_original_count':2,'note':'Same actual call02 uniform whole crop. Complete visible local arm silhouette/interior adopted as coherent native material; input strict-mask mechanical candidate withdrawn.'}
(P/'qa/complete_local_native_arm_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
