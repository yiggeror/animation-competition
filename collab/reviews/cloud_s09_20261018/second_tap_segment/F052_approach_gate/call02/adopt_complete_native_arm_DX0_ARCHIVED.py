#!/usr/bin/env python3
"""Extract coherent actual native arm; composite true source units with natural AA."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
Q=Path(__file__).resolve().parent;R=Q.parent
(Q/'masks').mkdir(exist_ok=True)
for d in ['candidate','production_layers','qa','masks']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pre=Image.open(R/'reference/F052_actual_source_preposition_NOT_ART.png').convert('RGBA');a=np.array(pre);h,w=a.shape[:2];yy,xx=np.indices((h,w))
n=np.zeros_like(a);n[500:860,620:1160]=np.array(Image.open(Q/'qa/native_whole_crop_uniform_540x360.png').convert('RGBA'));rgb=n[:,:,:3].astype(int)
def loadmask(p):return np.array(Image.open(p).convert('L'))>0
def poly(points):
 z=Image.new('L',(w,h));ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
roi=poly([(665,625),(755,598),(843,631),(1045,500),(1090,500),(1075,581),(976,691),(900,749),(811,752),(668,700)])
skin=(rgb[:,:,0]>165)&(rgb[:,:,2]>105)&(rgb[:,:,0]-rgb[:,:,1]>12)&(rgb[:,:,1]-rgb[:,:,2]>10)&(n[:,:,3]>128)&roi
lab,_=label(skin);cc=lab[680,850];assert cc>0
core=binary_fill_holes(lab==cc)
arm=binary_dilation(core,iterations=2)&(n[:,:,3]>0)&roi
yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>130)&(rgb[:,:,2]<110)
white=rgb.min(axis=2)>220
arm&=~yellow&~white
unit=np.array(Image.open(R/'reference/F052_pure031_unit_plus22_SOURCE.png').convert('RGBA'));um=unit[:,:,3]>0
release=loadmask(R/'masks/wrist_technical_extraction90_RELEASE.png');assert release.sum()==90
old=loadmask(R/'masks/old048_actual_near_arm_material.png')
domain=loadmask(R/'masks/F052_complete_near_arm_and_vacated_WHITE_EDIT_PENDING.png')|arm|old
hard_names=['head_neck_collar_actual','near_ruffle_ACTUAL048_material','fixed_receiver_palm_actual_material','waist_skirt_actual_material']
hard=np.zeros((h,w),bool)
for name in hard_names:hard|=loadmask(R/'masks'/f'{name}.png')
back=loadmask(R/'masks/far_arm_actual_visible_except_new_foreground.png')|loadmask(R/'masks/far_puff_actual_visible_except_new_foreground.png')
hard|=back&~arm
domain&=~hard&~(um&~release)
out=a.copy();out[domain]=n[domain]
# The local crop covers the full new arm. Obsolete old048 arm remnants above
# the crop are cleared using its actual source material mask, never drawn over.
cleared=domain&(yy<500)&old
assert not (cleared&hard).any()
# Recompose genuine whole original unit as foreground. Opaque material keeps
# exact RGBA; natural AA sees real native forearm behind the proximal cut.
behind=(arm|release)&um
out[um]=0;out[behind]=n[behind]
uf=unit.copy();uf[release]=0
base=Image.fromarray(out);base.alpha_composite(Image.fromarray(uf));out=np.array(base)
candidate=R/'candidate/F052_complete_native_arm_TRIAL_NOT_ACCEPTED.png';base.save(candidate)
nl=np.zeros_like(n);nl[arm]=n[arm];Image.fromarray(nl).save(R/'production_layers/call02_actual_complete_near_arm_TRIAL.png')
Image.fromarray(domain.astype('uint8')*255).save(Q/'masks/complete_native_arm_adoption_TRIAL.png')
Image.fromarray(arm.astype('uint8')*255).save(Q/'masks/native_actual_whole_near_arm_material.png')
Image.fromarray(cleared.astype('uint8')*255).save(Q/'masks/obsolete_old048_arm_above_local_crop_CLEAR.png')
for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 b=Image.new('RGBA',(w,h),col);b.alpha_composite(base);b.convert('RGB').save(R/f'qa/F052_complete_native_arm_full_{tag}_TRIAL.png');b.crop((620,420,1240,860)).convert('RGB').save(R/f'qa/F052_complete_native_arm_crop_{tag}_TRIAL.png')
for title,box in [('wrist',(970,470,1090,620)),('cuff',(640,590,810,740))]:
 b=Image.new('RGBA',(w,h),(35,43,52,255));b.alpha_composite(base);b.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(R/f'qa/F052_{title}_3x_TRIAL.png')
protected=um&~release
report={'status':'COHERENT_NATIVE_ARM_TRIAL_REVIEW_REQUIRED','candidate_sha256':sha(candidate),'native_call02_sha256':sha(Q/'original/F052_call02_RAW.png'),'actual_native_arm_pixels':int(arm.sum()),'whole_semantic_adoption_pixels':int(domain.sum()),'old_arm_above_local_crop_cleared':int(cleared.sum()),'source_unit_opaque_RGBA_changes':int(np.any(out[(unit[:,:,3]==255)&protected]!=unit[(unit[:,:,3]==255)&protected],axis=1).sum()),'source_unit_alpha240_RGBA_changes':int(np.any(out[(unit[:,:,3]>=240)&protected]!=unit[(unit[:,:,3]>=240)&protected],axis=1).sum()),'hard_source_RGBA_changes':int(np.any(out[hard]!=a[hard],axis=1).sum()),'code_articulation_or_limb_scaling':False,'source_unit_transform':'pure031+22 integerY; scale1 rotation0','new_requests':2,'F056_unopened':True}
(R/'qa/call02_native_arm_trial_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
