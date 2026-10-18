#!/usr/bin/env python3
"""Diagnostic semantic adoption of one whole native donor with uniform dy30."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_fill_holes,binary_closing,binary_dilation,label
R=Path(__file__).resolve().parent;B=R.parent
source=B/'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png'
mother=Image.open(source).convert('RGBA');pre=Image.open(R/'reference/F037_rigid_preposition_NOT_ART.png').convert('RGBA')
raw=Image.open(R/'originals/F037_call01_raw.png').convert('RGBA')
raw_same=Image.new('RGBA',pre.size);raw_same.paste(raw,(0,0));rs=np.array(raw_same)
donor=Image.new('RGBA',pre.size);donor.paste(raw,(0,30));a=np.array(mother);d=np.array(donor);p=np.array(pre)
yy,xx=np.indices(a.shape[:2]);roi=Image.new('L',pre.size)
ImageDraw.Draw(roi).polygon([(669,617),(740,604),(847,632),(1006,431),(1098,470),(1092,564),(897,786),(793,789),(665,711)],fill=255)
roi=np.array(roi)>0
def skin(z):
    q=z[:,:,:3].astype(int)
    return (z[:,:,3]>20)&(q[:,:,0]>170)&(q[:,:,1]>95)&(q[:,:,2]>70)&((q[:,:,0]-q[:,:,2])>25)&((q[:,:,0]-q[:,:,2])<125)&(q[:,:,0]>q[:,:,1])&(q[:,:,1]>q[:,:,2])
old=binary_fill_holes(binary_closing(skin(a)&roi,iterations=2))
new=binary_fill_holes(binary_closing(skin(d)&roi,iterations=2))
# Select the near-arm component only, using its actual visible elbow.
def arm_component(q,point):
    labs,n=label(q);key=labs[point[1],point[0]];assert key>0;return labs==key
old=arm_component(old,(830,720));new=arm_component(new,(840,715))
adopt=binary_dilation(old,iterations=14)|binary_dilation(new,iterations=3)
old_rigid=np.array(Image.open(R/'masks/rigid_whole_torch_and_grip_source.png'))>0
new_rigid=np.array(Image.open(R/'masks/F037_rigid_destination_guard.png'))>0
adopt |= old_rigid&~new_rigid

# Freeze farther sleeve material and real exterior contour. The old diagonal
# near-forearm occlusion ink is part of the moving arm, not a permanent seam on
# the sleeve: its upper two-pixel guard must not be retained as a floating line.
far_full=np.array(Image.open(R/'masks/actual_far_sleeve_cuff_guard.png'))>0
rgb=a[:,:,:3].astype(int)
yellow=(a[:,:,3]>32)&((rgb[:,:,0]-rgb[:,:,2])>110)&((rgb[:,:,1]-rgb[:,:,2])>70)
far_material=far_full.copy()
for x in range(940,1031):
    y=np.flatnonzero(yellow[590:693,x])
    if len(y):far_material[:int(y[0]+590),x]=False
    else:far_material[:,x]=False
far_material[(xx<940)|(xx>1030)]=False
headroi=Image.new('L',pre.size);ImageDraw.Draw(headroi).polygon([(665,460),(758,445),(844,457),(892,470),(912,518),(904,553),(885,573),(830,567),(805,552),(785,574),(733,564),(685,541),(662,505)],fill=255)
headraw=((yy<505)&(xx<1011))|(np.array(headroi)>0)
head=binary_dilation(headraw&(a[:,:,3]>0),iterations=2)
# Original visible cuff material, rather than the skin lying under it.
nearshape=Image.new('L',pre.size)
ImageDraw.Draw(nearshape).polygon([(638,674),(647,651),(668,628),(699,611),(733,603),(760,607),(777,619),(778,635),(763,644),(747,641),(726,650),(708,667),(692,691),(679,711),(659,717),(643,706)],fill=255)
nearroi=np.array(nearshape)>0
near_cuff=binary_dilation(binary_fill_holes(binary_closing(yellow&nearroi,iterations=2)),iterations=2)
Image.fromarray(head.astype(np.uint8)*255).save(R/'masks/F037_call01_actual_head_guard_DIAGNOSTIC.png')
Image.fromarray(near_cuff.astype(np.uint8)*255).save(R/'masks/F037_call01_near_cuff_guard_DIAGNOSTIC.png')
adopt &= ~(head|far_material|new_rigid|near_cuff)
adopt[(yy>=680)&(xx>=925)]=False
adopt[yy>=778]=False

# Complete each actual source/returned white dot intersected by the vacated
# material domain. Finish the whole material mark, never trim a dot at a mask.
for z in [a,rs]:
    whites=(z[:,:,:3].min(axis=2)>225)&(z[:,:,3]>230)&(yy>590)&(yy<778)&(xx<1030)&(xx>660)
    labs,n=label(whites)
    keys=np.unique(labs[adopt&whites]);keys=keys[keys>0]
    if len(keys):adopt|=binary_dilation(np.isin(labs,keys),iterations=2)
adopt &= ~(head|far_material|new_rigid|near_cuff)
adopt[(yy>=680)&(xx>=925)]=False
adopt[yy>=778]=False

new_domain=binary_dilation(new,iterations=3)&adopt
cloth_domain=adopt&~new_domain
out=p.copy();out[cloth_domain]=rs[cloth_domain]
# Arm donor uses real skin/ink only, not the shifted donor's yellow clothing or
# transparent padding. Alpha-over keeps the stationary cloth behind AA edges.
drgb=d[:,:,:3].astype(int)
donor_yellow=((drgb[:,:,0]-drgb[:,:,2])>110)&((drgb[:,:,1]-drgb[:,:,2])>70)
donor_white=(drgb.min(axis=2)>225)
new_layer_mask=new_domain&~donor_yellow&~donor_white&(d[:,:,3]>0)
out[new_domain&~new_layer_mask]=rs[new_domain&~new_layer_mask]
layer=np.zeros_like(d);layer[new_layer_mask]=d[new_layer_mask]
out=np.array(Image.alpha_composite(Image.fromarray(out),Image.fromarray(layer)))
outim=Image.fromarray(out);outpath=R/'candidate/F037_call01_global_dy30_semantic_DIAGNOSTIC.png';outim.save(outpath)
Image.fromarray(adopt.astype(np.uint8)*255).save(R/'masks/F037_call01_semantic_adoption_DIAGNOSTIC.png')
Image.fromarray(far_material.astype(np.uint8)*255).save(R/'masks/F037_call01_far_material_guard_DIAGNOSTIC.png')
for name,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    bg=Image.new('RGBA',pre.size,bgc);bg.alpha_composite(outim)
    bg.crop((630,350,1240,850)).resize((976,800),Image.Resampling.LANCZOS).save(R/f'qa/F037_call01_semantic_{name}.png')
changed=np.any(out!=p,axis=2);inputmask=np.array(Image.open(R/'masks/F037_near_arm_and_vacated_domain.png'))>0
checks={'status':'DIAGNOSTIC_NOT_ADOPTED_PENDING_ACTUAL_REVIEW','donor_transform':{'arm_scale':1,'complete_near_arm_translation':[0,30],'vacated_clothing_translation':[0,0],'independent_limb_fit':False,'warp':False},
 'adoption_mask_pixels':int(adopt.sum()),'changed_pixels':int(changed.sum()),'changes_outside_frozen_operational_input_mask':int((changed&~inputmask).sum()),
 'new_native_calls':0,'new_mask_scope':'same approved complete near arm, its old occlusion outline and vacated area; input mask retained immutable',
 'whole_grip_prop_guard_changes':int(changed[new_rigid].sum()),'head_guard_changes':int(changed[head].sum()),'far_material_changes':int(changed[far_material].sum()),
 'candidate_sha256':hashlib.sha256(outpath.read_bytes()).hexdigest()}
(R/'qa/F037_call01_semantic_diagnostic_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks))
