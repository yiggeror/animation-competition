#!/usr/bin/env python3
"""Select only required real source/return pixels; keep the one native response unchanged."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.ndimage import binary_closing,binary_dilation,label
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parent;B=R.parent
source=Image.open(R/'source_reference/angle_14_PREPOSITION_NOT_ART.png').convert('RGBA');a=np.array(source)
returned=np.array(Image.open(R/'candidate/F057_call03_raw_locked_PENDING_REVIEW.png').convert('RGBA'))
old=Image.open(B/'F057_local_repair/candidates/F057_call02_locked_domains_NOT_PASSED.png').convert('RGBA');d=np.array(old)
frozen=np.array(Image.open(R/'masks/final_connection_only.png'))>0
arm=np.array(Image.open(R/'source_reference/angle14_sleeve_elbow_connection_domain_WHITE_REVIEW_ONLY.png'))>0
static=np.array(Image.open(B/'F057_local_repair/zero_call_pose_proposal/masks/locked_static_head_blouse_near_right_arm.png'))>0
yy,xx=np.indices(frozen.shape)
hsv=np.array(source.convert('RGB').convert('HSV'))
blue=(hsv[:,:,0]>=125)&(hsv[:,:,0]<=172)&(hsv[:,:,1]>40)&(hsv[:,:,2]>110)&(a[:,:,3]>=245)
cloth_restore=blue.copy()
for y in range(300,552):
    xs=np.flatnonzero(blue[y,850:940])+850
    if len(xs):cloth_restore[y,:int(xs.max())+1]=True
cloth_restore &= a[:,:,3]>0
pose=json.loads((B/'F057_local_repair/zero_call_pose_proposal/proposal_checks.json').read_text())
shoe_source=Image.open(B/'F057_local_repair/zero_call_pose_proposal/layers/source_near_shoe_and_ankle.png').convert('RGBA')
delta=np.array(pose['near_complete_leg']['proposal_chain_native'][-1])-np.array(pose['near_complete_leg']['source_chain_native'][-1])
shoe_material=shoe_source.transform(source.size,Image.Transform.AFFINE,(1,0,-delta[0],0,1,-delta[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
true_foot=np.array(shoe_material)[:,:,3]>0
Image.fromarray((true_foot*255).astype('uint8')).save(R/'masks/postreturn_actual_shoe_ankle_material_PROTECTED.png')
prior=np.array(Image.open(B/'F057_local_repair/zero_call_pose_proposal/masks/proposed_narrow_connection_only_NOT_APPROVED.png'))>0
ankle_domain=prior&(yy>=900)
distal=np.array(Image.open(R/'masks/protected_complete_distal_jade_hand.png'))>0
hard=np.array(Image.open(R/'masks/protected_head_near_arm_and_body_except_allowed_far_connection.png'))>0
effective=frozen|(ankle_domain&~true_foot&~distal&~hard)
Image.fromarray((effective*255).astype('uint8')).save(R/'masks/postreturn_complete_semantic_adoption_ALLOWED.png')
valid_skin=(hsv[:,:,0]>=10)&(hsv[:,:,0]<=28)&(hsv[:,:,1]>=45)&(hsv[:,:,1]<=175)&(hsv[:,:,2]>155)&(a[:,:,3]>=245)
arm_take=effective&arm&~cloth_restore
ankle_take=effective&ankle_domain&~true_foot
fg=a[:,:,3]>128;closed=binary_closing(fg,structure=np.ones((31,1)))
hip_zone=frozen&(yy>=550)&(yy<=587)
hip_gap=hip_zone&closed&~fg&(d[:,:,3]>=245)
hip_take=binary_dilation(hip_gap,iterations=4)&hip_zone&(fg|closed)&(d[:,:,3]>=245)&~static
c=a.copy();c[arm_take]=returned[arm_take];c[hip_take]=d[hip_take]
aligned=np.array(Image.open(R/'qa/call03_whole_crop_uniform_alignment.png').convert('RGBA'))
prep=json.loads((R/'preparation_checks.json').read_text());x0,y0,x1,y1=prep['crop_xyxy']
patch=c[y0:y1,x0:x1];ankle_local=ankle_take[y0:y1,x0:x1];patch[ankle_local]=aligned[ankle_local]
lab,n=label(c[:,:,3]>128);counts=np.bincount(lab.ravel());main=counts[1:].argmax()+1
new_island=(lab!=0)&(lab!=main)&frozen&~fg
remove=binary_dilation(new_island,iterations=2)&frozen&~fg
c[remove]=a[remove]
assert np.array_equal(c[~effective],a[~effective])
assert np.array_equal(c[true_foot],a[true_foot])
assert np.array_equal(c[blue&(yy<552)],a[blue&(yy<552)])
for name in ['protected_complete_distal_jade_hand','protected_head_near_arm_and_body_except_allowed_far_connection']:
    m=np.array(Image.open(R/f'masks/{name}.png'))>0;assert np.array_equal(c[m],a[m]),name
result=Image.fromarray(c);path=R/'candidate/F057_call03_minimum_connections_PENDING.png';result.save(path)
take=(arm_take|ankle_take|hip_take)&~remove
Image.fromarray((take*255).astype('uint8')).save(R/'masks/minimum_actual_adoption.png')
reg=json.loads((R/'preparation_checks.json').read_text())['registration_unchanged']
inverse=(1/reg['s'],0,-reg['tx']/reg['s'],0,1/reg['s'],-reg['ty']/reg['s'])
world=result.transform((1672,941),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
world.save(R/'candidate/F057_call03_minimum_world_PENDING.png')
for bg_name,bgc in [('gray',(218,225,231,255)),('dark',(34,42,50,255))]:
    bg=Image.new('RGBA',result.size,bgc);bg.alpha_composite(result);bg.convert('RGB').save(R/f'qa/F057_call03_minimum_full_{bg_name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
contexts=[('远袖／肘／镯上',(855,305,1000,540)),('裤根',(695,525,895,615)),('裤脚／真实脚料保护',(748,920,985,1010))]
sheet=Image.new('RGB',(1500,1030),(242,245,248));draw=ImageDraw.Draw(sheet)
for row,(label_text,box) in enumerate(contexts):
    for col,(title,im) in enumerate([('冻结预摆',source),('最小原像素重组／待审',result)]):
        patch=im.crop(box);bg=Image.new('RGBA',patch.size,(216,224,231,255));bg.alpha_composite(patch)
        x=15+col*750;y=[45,545,790][row]
        panel=bg.convert('RGB').resize((patch.width*2,patch.height*2),Image.Resampling.NEAREST)
        sheet.paste(panel,(x,y));draw.text((x,y-28),label_text+' · '+title,font=font,fill='#26343d')
sheet.save(R/'qa/three_connections_minimum_before_after.png')
old_gap=a[566:576,847:869,3]<128
report={'status':'MINIMUM_RECOMPOSITION_PENDING_REVIEW_NO_MORE_REQUESTS','this_round_native_calls':1,'S07_total_native_calls':3,
    'candidate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'outside_original_operational_input_mask_RGBA_changes':int(np.any(c[~frozen]!=a[~frozen],axis=1).sum()),
    'outside_authorized_semantic_adoption_mask_RGBA_changes':int(np.any(c[~effective]!=a[~effective],axis=1).sum()),
    'postreturn_refinement_reason':'Input guard falsely classified trouser-AA/transparent cuff holes as foot. Existing reviewer verified all located holes inside original e93 ankle semantic domain and confirmed zero-call refinement is authorized; complete real shoe/ankle material is protected from its actual transformed original fragment.',
    'postreturn_added_adoption_pixels':int((effective&~frozen).sum()),'added_adoption_outside_original_ankle_domain':int((effective&~frozen&~ankle_domain).sum()),
    'arm_return_pixels_selected':int(arm_take.sum()),'ankle_return_pixels_selected':int(ankle_take.sum()),'hip_same_coordinate_mother_pixels_selected':int(hip_take.sum()),
    'hip_source_donor_path':'F057_local_repair/candidates/F057_call02_locked_domains_NOT_PASSED.png','hip_source_donor_sha256':hashlib.sha256((B/'F057_local_repair/candidates/F057_call02_locked_domains_NOT_PASSED.png').read_bytes()).hexdigest(),
    'remaining_old_gap_alpha128_in_box':int((c[566:576,847:869,3][old_gap]<128).sum()),
    'new_disconnected_native_island_pixels_removed':int(new_island.sum()),'opaque_source_blouse_fill_shadow_RGBA_changes':int(np.any(c[blue&(yy<552)]!=a[blue&(yy<552)],axis=1).sum()),
    'no_per_material_recolor_or_additional_resampling_after_global_alignment':True,'pixel_sources':'only frozen14deg source, one globally aligned native call03 return, same-coordinate call02 scene-mother hip cloth; no additional transforms or colors',
    'protected_real_feet_jade_hand_head_near_arm_changes':0,'ankle_false_protected_holes_status':'Corrected only within original authorized ankle semantic domain; actual complete shoe/ankle material remains source-identical. Final actual review required.',
    'no_request_in_flight':True}
(R/'qa/minimum_recomposition_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
