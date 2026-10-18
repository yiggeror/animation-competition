#!/usr/bin/env python3
"""Original-pixel-only F037 proposal. No drawing, resampling, or image calls."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_closing,binary_dilation,label

OUT=Path(__file__).resolve().parent
R=OUT.parent; B=R.parent
mother_path=B/'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png'
raw_path=R/'originals/F037_call01_raw.png'
pre_path=R/'reference/F037_rigid_preposition_NOT_ART.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(mother_path)=='4b59c62485cf382c3e2d411de3c8ca9fb4edee622dad31b41946362889d44da7'
assert sha(raw_path)=='d913073cf1fb4feaa9b0fcc89c68c4112b1acefe2279b4fd6ddc1022b8a61a9b'
mi=Image.open(mother_path).convert('RGBA'); a=np.array(mi)
pi=Image.open(pre_path).convert('RGBA'); p=np.array(pi)
ri=Image.open(raw_path).convert('RGBA')
same=Image.new('RGBA',mi.size);same.paste(ri,(0,0));rs=np.array(same)
shift=Image.new('RGBA',mi.size);shift.paste(ri,(0,30));d=np.array(shift)
yy,xx=np.indices(a.shape[:2])
def polygon(points):
    im=Image.new('L',mi.size);ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def component(q,point):
    labs,n=label(q);key=labs[point[1],point[0]];assert key;return labs==key
def skin(z):
    q=z[:,:,:3].astype(int)
    return (z[:,:,3]>20)&(q[:,:,0]>170)&(q[:,:,1]>95)&(q[:,:,2]>70)&((q[:,:,0]-q[:,:,2])>25)&((q[:,:,0]-q[:,:,2])<125)&(q[:,:,0]>q[:,:,1])&(q[:,:,1]>q[:,:,2])
roi=polygon([(669,617),(740,604),(847,632),(1006,431),(1098,470),(1092,564),(897,786),(793,789),(665,711)])
old=component(binary_fill_holes(binary_closing(skin(a)&roi,iterations=2)),(830,720))
new=component(binary_fill_holes(binary_closing(skin(d)&roi,iterations=2)),(840,715))
unshifted_arm=component(binary_fill_holes(binary_closing(skin(rs)&roi,iterations=2)),(830,680))
def readmask(name):return np.array(Image.open(R/'masks'/name))>0
rigid=readmask('F037_rigid_destination_guard.png')
oldrigid=readmask('rigid_whole_torch_and_grip_source.png')
head=readmask('F037_call01_actual_head_guard_DIAGNOSTIC.png')
near=readmask('F037_call01_near_cuff_guard_DIAGNOSTIC.png')
# This mask excludes the obsolete near-arm occlusion line. It preserves all
# previously visible far sleeve material, white marks and actual fold ink.
far=readmask('F037_call01_far_material_guard_DIAGNOSTIC.png')
# Record exactly which inherited guard was used, independently of later edits.
protected=head|near|far|rigid|((yy>=680)&(xx>=925))|(yy>=778)

# Complete old-arm outline and its newly exposed garment, rather than a
# narrow skin threshold strip. Extend through the exposed far-puff material;
# existing visible far material remains protected.
cloth=binary_dilation(old,iterations=20)|(oldrigid&~rigid)
cloth|=(xx>=940)&(xx<=1030)&(yy>=585)&(yy<=650)
# Include complete actual white marks touched by the old-arm reveal, from
# either legal garment source, plus yellow context around their boundary.
for z in (a,rs):
    whites=(z[:,:,:3].min(2)>225)&(z[:,:,3]>230)&(yy>590)&(yy<778)&(xx>660)&(xx<1030)
    labs,n=label(whites);keys=np.unique(labs[cloth&whites]);keys=keys[keys>0]
    if len(keys):cloth|=binary_dilation(np.isin(labs,keys),iterations=3)

# Extract the ONE complete returned arm and its ink contour. Select actual
# source pixels, including edge AA; do not alpha-composite, blend, paint,
# interpolate, or independently transform any portion of the arm.
rgb=d[:,:,:3].astype(int)
yellow=((rgb[:,:,0]-rgb[:,:,2])>110)&((rgb[:,:,1]-rgb[:,:,2])>70)
white=rgb.min(2)>225
arm_window=binary_dilation(new,iterations=3)
arm=component(arm_window&~yellow&~white&(d[:,:,3]>16),(840,715))
arm|=binary_dilation(arm,iterations=1)&arm_window&~yellow&~white&(d[:,:,3]>1)
cloth&=~protected;arm&=~protected
cloth&=~arm
# Raw at its original coordinates also contains its original near arm above
# the adopted arm. Those are not garment pixels: never import that second
# arm as revealed clothing. Retain existing garment there where available.
cloth&=~binary_dilation(unshifted_arm,iterations=3)
out=p.copy();out[cloth]=rs[cloth];out[arm]=d[arm]
adopt=cloth|arm
candidate=OUT/'F037_independent_original_pixels_PENDING.png';Image.fromarray(out).save(candidate)
for name,z in [('adoption_mask',adopt),('arm_raw_dy30_mask',arm),('cloth_raw_dy0_mask',cloth),('hard_protection_mask',protected),('far_visible_material_guard',far)]:Image.fromarray(z.astype(np.uint8)*255).save(OUT/(name+'.png'))
# Provenance: 0 locked preposition, 1 same raw at original coordinates,
# 2 same raw at y+30. Each output pixel is exactly one of these full RGBA.
provenance=np.zeros(a.shape[:2],dtype=np.uint8);provenance[cloth]=1;provenance[arm]=2
Image.fromarray(provenance).save(OUT/'pixel_source_ids.png')
for name,bg in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    canvas=Image.new('RGBA',mi.size,bg);canvas.alpha_composite(Image.fromarray(out))
    canvas.save(OUT/('F037_full_'+name+'.png'))
    canvas.crop((630,350,1240,850)).resize((976,800),Image.Resampling.NEAREST).save(OUT/('F037_closeup_'+name+'.png'))
changed=np.any(out!=p,axis=2);input_mask=readmask('F037_near_arm_and_vacated_domain.png')
checks={'status':'DIAGNOSTIC_BLOCKED_FAR_SLEEVE_SOURCE_CONFLICT_NOT_LOCKED','candidate_sha256':sha(candidate),
 'sources':{'F031':str(mother_path),'F031_sha256':sha(mother_path),'native_raw':str(raw_path),'native_raw_sha256':sha(raw_path),'locked_preposition':str(pre_path),'locked_preposition_sha256':sha(pre_path)},
 'transforms':{'one_complete_near_arm_native_translation':[0,30],'garment_native_translation':[0,0],'raw_missing_right_column':'transparent padding only','scale':1,'rotation':0,'warp':False,'alpha_composite_used_in_candidate':False},
 'adopt_pixels':int(adopt.sum()),'arm_source_pixels':int(arm.sum()),'cloth_source_pixels':int(cloth.sum()),'changed_pixels':int(changed.sum()),'outside_adoption_changes':int((changed&~adopt).sum()),'changes_outside_original_input_mask':int((changed&~input_mask).sum()),
 'locked_preposition_pixel_mismatches':int(np.any(out[~adopt]!=p[~adopt],axis=1).sum()),'arm_source_RGBA_mismatches':int(np.any(out[arm]!=d[arm],axis=1).sum()),'cloth_source_RGBA_mismatches':int(np.any(out[cloth]!=rs[cloth],axis=1).sum()),
 'head_changes':int((changed&head).sum()),'near_cuff_changes':int((changed&near).sum()),'far_visible_material_changes':int((changed&far).sum()),'whole_grip_prop_changes':int((changed&rigid).sum()),'far_arm_palm_changes':int((changed&((xx>=925)&(yy>=680))).sum()),'below_778_changes':int((changed&(yy>=778)).sum()),
 'floating_old_skin_1019_591_RGBA':out[591,1019].tolist(),'new_image_calls':0,'scope_note':'Adoption refines the previously authorized entire near arm, obsolete arm occlusion contour and garment revealed by that arm. Original invocation mask and all parent files remain unchanged.',
 'actual_review_blocker':'Preserved original far-sleeve tip and native-coordinate returned rounded sleeve do not form one smooth contour. Fixed-coordinate native garment source is transparent at the notch; original pixels there are old-arm skin/occlusion ink, not a usable new yellow contour. Do not adopt or expand F042.',
 'source_gap_samples':[{'xy':[x,y],'original_RGBA':a[y,x].tolist(),'native_dy0_RGBA':rs[y,x].tolist(),'native_dy30_RGBA':d[y,x].tolist(),'candidate_RGBA':out[y,x].tolist()} for x,y in [(1004,610),(1005,611),(1005,612),(1008,608)]]}
(OUT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
