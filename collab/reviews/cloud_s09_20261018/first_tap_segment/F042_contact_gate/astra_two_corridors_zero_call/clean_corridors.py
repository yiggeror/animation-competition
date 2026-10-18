#!/usr/bin/env python3
"""Astra's two explicit ghost corridors, using existing PNG source pixels only. No image call/recolor."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
R=Path(__file__).resolve().parent;P=R.parent;T=P.parent
for d in ['candidate','masks','qa','exposure']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=P/'connection_call02/candidate/F042_complete_joint_pixels_v2_PENDING.png';assert sha(source)=='c909ea491e345021299dd7deada41b2a1748b6c12fc2c743e58242195d8a0270'
im=Image.open(source).convert('RGBA');a=np.array(im);size=im.size;yy,xx=np.indices(a.shape[:2])
donorpath=P/'connection_call02/qa/native_whole_crop_uniform_alignment.png';aligned=Image.open(donorpath).convert('RGBA');b=np.zeros_like(a);b[490:810,630:1110]=np.array(aligned)
p37=T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png';assert sha(p37)=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9'
m37=Image.open(p37).convert('RGBA');moved37=Image.new('RGBA',size);moved37.paste(m37,(0,91));truth=np.array(moved37)
rigid31=Image.open(T/'reference/F031_rigid_whole_torch_and_grip.png').convert('RGBA');rigid=Image.new('RGBA',size);rigid.paste(rigid31,(0,59));rig=np.array(rigid)
# Tight true material and its actual AA only: no rectangular guard around a torch.
prop_guard=(rig[:,:,3]>0)&binary_dilation(rig[:,:,3]>=128,iterations=2)
arm=np.array(Image.open(P/'connection_call02/masks/actual_complete_registered_arm_material.png'))>0
arm_guard=binary_dilation(arm,iterations=2)&(a[:,:,3]>0)
receiver=(np.array(m37)[:,:,3]>0)&(yy>=690)&(xx>=1010)
def polygon(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
# Follow the actual slanted upper-wrist silhouette, with both endpoint AA.
# Alpha disagreement identifies the obsolete strip; no skin/color threshold is used.
wrist_corridor=polygon([(1041,518),(1057,518),(1057,526),(1009,584),(998,584),(998,574)])
wrist_seed=wrist_corridor&(a[:,:,3]>1)&(b[:,:,3]==0)
wrist_take=binary_dilation(wrist_seed,iterations=2)&wrist_corridor
# Full outside-head/body/tail side corridor, excluding actual prop/arm/palm material.
# Every adopted clear pixel has an actual same-coordinate037+91 source with alpha0.
torch_corridor=(xx>=1058)&(xx<=1226)&(yy>=290)&(yy<=748)
ghost_take=torch_corridor&(a[:,:,3]>0)&(a[:,:,3]<128)&(truth[:,:,3]==0)&~prop_guard&~arm_guard&~receiver
c=a.copy();c[wrist_take]=b[wrist_take];c[ghost_take]=truth[ghost_take]
alltake=wrist_take|ghost_take
assert np.array_equal(c[~alltake],a[~alltake]);assert (ghost_take&prop_guard).sum()==0;assert (ghost_take&arm_guard).sum()==0;assert (ghost_take&receiver).sum()==0
assert np.array_equal(c[receiver],a[receiver]);assert np.array_equal(c[prop_guard&~wrist_corridor],a[prop_guard&~wrist_corridor]);assert c[414,1196,3]==0
for name,z in [('upper_wrist_full_corridor',wrist_corridor),('upper_wrist_actual_native_adoption',wrist_take),('torch_outer_full_corridor',torch_corridor),('torch_non_material_ghost_adoption',ghost_take),('real_hand_torch_material_guard',prop_guard),('real_near_arm_AA_guard',arm_guard),('stationary_palm_material_guard',receiver)]:Image.fromarray(z.astype(np.uint8)*255).save(R/f'masks/{name}.png')
out=R/'candidate/F042_two_corridors_clean_PENDING_ASTRA.png';result=Image.fromarray(c);result.save(out)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
boxes=[('腕上缘整段旧肤条',(988,508,1075,598),4),('筒外头圈/筒侧/尾圈',(1058,300,1226,748),2)]
for nm,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1300,1450),(239,243,246));d=ImageDraw.Draw(sheet)
 for row,(title,box,factor) in enumerate(boxes):
  for j,(label,z) in enumerate([('c909修前',im),('同原片零调用清理',result)]):
   bg=Image.new('RGBA',size,col);bg.alpha_composite(z);patch=bg.crop(box).resize(((box[2]-box[0])*factor,(box[3]-box[1])*factor),Image.Resampling.NEAREST);x=j*650+15;y=40 if row==0 else 485
   sheet.paste(patch.convert('RGB'),(x,y));d.text((x,y-28),title+' · '+label,font=font,fill='#26343e')
 sheet.save(R/f'qa/two_corridors_before_after_{nm}.png')
 bg=Image.new('RGBA',size,col);bg.alpha_composite(result);bg.convert('RGB').save(R/f'qa/F042_clean_full_{nm}.png')
remaining=wrist_corridor&(c[:,:,3]>1)&(b[:,:,3]==0)
remaining_ghost=torch_corridor&(c[:,:,3]>0)&(c[:,:,3]<128)&(truth[:,:,3]==0)&~prop_guard&~arm_guard&~receiver
assert not remaining.any();assert not remaining_ghost.any()
report={'status':'TWO_ASTRA_SPECIFIED_CORRIDORS_CLEANED_PENDING_ACTUAL_REVIEW','authority':'Astra merged review: contact/whole arm/two sleeves/7f passed; only upper-wrist old skin strip and non-prop low-alpha torch outer contour, no regeneration/recolor,044/048 wait.','source_commit':'e6fa5e1f37fdf1bfbf3f9db9f4820b95950e522c','source_path':str(source),'source_sha256':sha(source),'candidate_sha256':sha(out),'wrist_existing_native_donor_path':str(donorpath),'wrist_donor_sha256':sha(donorpath),'wrist_donor_transform':'Previously frozen whole call02 crop scale0.3125 only; reused identical aligned PNG, no additional resampling.','ghost_donor_path':str(p37),'ghost_donor_sha256':sha(p37),'ghost_donor_translation':[0,91],'actual_prop_source':'Original031 rigid hand/torch translated[0,59], equivalent to037+91. Guard uses actual alpha material/AA, no coarse box.','wrist_take_pixels':int(wrist_take.sum()),'wrist_changed_pixels':int(np.any(c[wrist_take]!=a[wrist_take],axis=1).sum()),'ghost_take_pixels':int(ghost_take.sum()),'outside_two_adoption_masks_RGBA_changes':int(np.any(c[~alltake]!=a[~alltake],axis=1).sum()),'stationary_receiving_palm_RGBA_changes':0,'actual_prop_and_grip_except_authorized_proximal_wrist_corridor_RGBA_changes':0,'remaining_wrist_old_strip_pixels':int(remaining.sum()),'remaining_same_donor_non_material_ghost_pixels':int(remaining_ghost.sum()),'example1196_414_before_RGBA':a[414,1196].tolist(),'example1196_414_after_RGBA':c[414,1196].tolist(),'no_recolor':True,'new_image_calls':0,'S09_total_requests_unchanged':17,'S09_total_originals_unchanged':16,'F044_F048_unopened':True}
(R/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
