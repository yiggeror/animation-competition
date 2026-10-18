#!/usr/bin/env python3
"""One complete native arm rigid fit; genuine source sleeves/rigid grip remain."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_dilation,binary_fill_holes
import numpy as np,json,hashlib,math
R=Path(__file__).resolve().parent;T=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
motherpath=T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png';mother=Image.open(motherpath).convert('RGBA');a=np.array(mother);size=mother.size;yy,xx=np.indices(a.shape[:2])
native=np.zeros_like(a);native[240:860,620:1240]=np.array(Image.open(R/'qa/call01_whole_crop_uniform_alignment.png').convert('RGBA'))
rgb=native[:,:,:3].astype(int)
def mask(name):return np.array(Image.open(R/'masks'/f'{name}.png'))>0
def polygon(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
roi=polygon([(650,610),(750,580),(900,610),(1040,480),(1090,560),(960,700),(910,790),(760,800),(650,720)])
skin=(rgb[:,:,0]>165)&(rgb[:,:,0]-rgb[:,:,1]>12)&(rgb[:,:,1]-rgb[:,:,2]>10)&(native[:,:,3]>=128)
seed=skin&roi&((yy-xx)>=-479)
lab,_=label(seed);ct=np.bincount(lab.ravel());ct[0]=0;core=binary_fill_holes(lab==int(ct.argmax()))
armmask=binary_dilation(core,iterations=2)&(native[:,:,3]>0)&roi&((yy-xx)>=-482)
yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>130)&(rgb[:,:,2]<130)
white=(rgb.min(axis=2)>220)
armmask&=~yellow&~white
arm=native.copy();arm[~armmask]=0;Image.fromarray(arm).save(R/'production_layers/native_complete_near_arm_unfitted.png')
angle=-2.8;theta=math.radians(angle);rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);pivot=np.array([1030.,554.]);trans=pivot-rot@pivot;inv=rot.T;off=-inv@trans
fitted=Image.fromarray(arm).transform(size,Image.Transform.AFFINE,(*inv[0],off[0],*inv[1],off[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));f=np.array(fitted);fitted.save(R/'production_layers/native_complete_near_arm_rigid_fit_trial.png')
# Clear only actual previous near-arm/ink, not the wide potential edit box.
oldskin=mask('old_near_arm_actual_material');oldarm=binary_dilation(oldskin,iterations=3)&(a[:,:,3]>0)
ruffle=mask('near_ruffle_actual_material');receiver=mask('fixed_receiver_palm_material');head=mask('head_neck_collar_actual');waist=mask('waist_and_skirt_actual_material')
oldarm&=~ruffle&~receiver&~head&~waist
pure31=Image.open(R/'sources/F031_rigid_whole_torch_and_grip.png').convert('RGBA');oldprop=Image.new('RGBA',size);oldprop.paste(pure31,(0,59));oldprop=np.array(oldprop)
oldunit=np.array(Image.open(R/'reference/F042_true_grip_torch_detached_SOURCE.png'))[:,:,3]>0
removeprop=(oldprop[:,:,3]>0)|oldunit
base=a.copy();base[oldarm|removeprop]=0
purepalm=np.array(Image.open(T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png').convert('RGBA'));base[receiver]=purepalm[receiver]
# Fill newly exposed original-arm territory with actual native yellow cloth /
# white dots and immediate real ink; no source waist/puff shape replacement.
clothseed=(yellow|white)&(native[:,:,3]>0)&oldarm
cloth=binary_dilation(clothseed,iterations=1)&oldarm&(native[:,:,3]>0)&~skin
background=np.zeros_like(a);background[cloth]=native[cloth]
canvas=Image.alpha_composite(Image.fromarray(base),Image.fromarray(background));canvas.alpha_composite(fitted)
# Original ruffle foreground and rigid handtorch are their actual source RGBA.
rr=np.zeros_like(a);rr[ruffle]=a[ruffle];canvas.alpha_composite(Image.fromarray(rr))
unit=Image.open(R/'reference/F044_rigid_hand_torch_up48_SOURCE.png').convert('RGBA');canvas.alpha_composite(unit)
# Receiver exact source layer at fixed position.
pm=np.zeros_like(a);pm[receiver]=purepalm[receiver];canvas.alpha_composite(Image.fromarray(pm))
out=R/'candidate/F044_complete_native_arm_rigid_fit_TRIAL.png';canvas.save(out);c=np.array(canvas)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
for n,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 b=Image.new('RGBA',size,col);b.alpha_composite(canvas);b.convert('RGB').save(R/f'qa/F044_semantic_arm_trial_full_{n}.png')
 b.crop((620,240,1240,860)).convert('RGB').save(R/f'qa/F044_semantic_arm_trial_crop_{n}.png')
report={'status':'WHOLE_NATIVE_ARM_RIGID_FIT_TRIAL_PENDING_ACTUAL_REVIEW_NOT_PASS','mother_sha256':sha(motherpath),'native_raw_sha256':'3d0561f41e8dadd5f318ae51b9b732f8ddc6d3835217ee009d4cc45482fc25a4','candidate_sha256':sha(out),'native_arm_pixels':int(armmask.sum()),'whole_arm_rigid_rotation_deg':angle,'whole_arm_pivot_native':pivot.tolist(),'whole_arm_translation_native':trans.tolist(),'whole_arm_scale':1,'no_per_segment_warp_or_stretch':True,'old_actual_skin_ink_removed':int(oldarm.sum()),'same_native_cloth_background_pixels':int(cloth.sum()),'native_cuff_and_waist_NOT_adopted':True,'fixed_palm_core_RGB_changes':int(np.any(c[receiver&(purepalm[:,:,3]==255),:3]!=purepalm[receiver&(purepalm[:,:,3]==255),:3],axis=1).sum()),'F044_calls':1,'S09_requests':18,'S09_originals':17,'F048_unopened':True}
(R/'qa/semantic_arm_trial_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
