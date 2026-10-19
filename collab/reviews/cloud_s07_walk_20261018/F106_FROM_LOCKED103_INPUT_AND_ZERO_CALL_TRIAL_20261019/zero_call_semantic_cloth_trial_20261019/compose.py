"""Actual source pixels only: whole locked103 arm/hand/lamp lift, actual cloth behind.
No native request, independent part fit, wrist cut, skin drawing, or RGB correction.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from scipy.ndimage import label,binary_fill_holes,binary_dilation,binary_closing
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;S=P.parent/'F103_REPAIR_NATIVE_call02_fa796ff9_20261019'
for d in ['candidate','layers','masks','qa']:(R/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
srcp=P/'sources/F103_LOCKED06443a17.png';src=Image.open(srcp).convert('RGBA');a=np.array(src);size=src.size
assert sha(srcp)=='06443a17f780d7a72a293c27686099ffaf72ba827b00e3290059c3061cd2ad90'
rawp=P/'originals/F106_NATIVE_call01_RAW.png';raw=Image.open(rawp).convert('RGBA')
assert sha(rawp)=='10bdbcc10f20f6ac472d8f70ef98a2385f6166523dec478f59b3afab004d5aee'
mapped=Image.new('RGBA',size);mapped.alpha_composite(raw.resize((720,1080),Image.Resampling.LANCZOS),(1240,0));n=np.array(mapped)
def largest(m):
 lab,count=label(m);cnt=np.bincount(lab.ravel());cnt[0]=0;return lab==cnt.argmax()
def cloth_mask(z):
 v=z.astype(int);r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];active=v[:,:,3]>0
 blue=(b>r+20)&(g>r+10)&(b>g+10)&(b>90)&(v[:,:,3]>16)
 return binary_dilation(binary_fill_holes(largest(binary_closing(blue,iterations=2))),iterations=2)&active
def warm(z):
 v=z.astype(int);r,g,b=v[:,:,0],v[:,:,1],v[:,:,2]
 return (r>150)&(r>g+16)&(g>b+8)&(b>70)&(v[:,:,3]>16)
def poly(points):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
oldnear=np.array(Image.open(P/'masks/OLD_complete_near_bare_arm_and_hand.png').convert('L'))>0
oldnear_clean=binary_dilation(oldnear,iterations=4)
wrongskin=binary_dilation(binary_fill_holes(largest(warm(n))),iterations=3)
# One actual complete106 blouse piece; no wrong106 skin/hand/lamp is available
# in this plate. Its exposure is determined only by the whole source layers.
torso_face=poly([(1430,215),(1565,215),(1648,278),(1660,345),(1665,414),(1628,491),(1574,603),(1540,632),(1430,610),(1360,545),(1360,465),(1430,390)])
cloth106=cloth_mask(n)&~wrongskin&torso_face
plate=np.zeros_like(n);plate[cloth106]=n[cloth106]
Image.fromarray(plate).save(R/'layers/RAW106_actual_whole_continuous_blue_blouse_BACKPLATE_ONLY.png')
oldlamp=np.array(Image.open(S/'layers/ORIGINAL_whole_lamp_FIXED.png').convert('RGBA'))[:,:,3]>0
body=a.copy();body[oldnear_clean|oldlamp]=0
# This complete physical chain is the already stored single dy=-12.359119141727836
# source103 group, not the failed106 arm and not a separately translated palm.
motionp=P/'layers/F106_whole_actual_bare_arm_hand_physical_lamp_LIFTED.png'
motion=Image.open(motionp).convert('RGBA')
# The original short sleeve is a foreground garment piece. This polygon follows
# its shoulder/sleeve domain; actual material alpha, not a rectangle, owns edges.
sleeve_domain=poly([(1460,235),(1534,241),(1573,266),(1607,302),(1635,347),(1626,380),(1565,393),(1516,406),(1475,385),(1440,362),(1438,315)])
sleeve=cloth_mask(a)&sleeve_domain&~warm(a)
front=np.zeros_like(a);front[sleeve]=a[sleeve]
Image.fromarray(front).save(R/'layers/LOCKED103_actual_complete_short_sleeve_FOREGROUND.png')
Image.fromarray(body).save(R/'layers/LOCKED103_fixed_body_REMOVE_old_whole_near_chain_and_lamp.png')
out=Image.fromarray(plate);out.alpha_composite(Image.fromarray(body))
out.alpha_composite(Image.open(P/'sources/ORIGINAL_table_shadow_NOT_lifted.png').convert('RGBA'))
out.alpha_composite(motion);out.alpha_composite(Image.fromarray(front))
dest=R/'candidate/F106_ZERO_CALL_LOCKED103_WHOLE_CHAIN_actual106_CLOTH_BACKPLATE_PENDING_ASTRA.png';out.save(dest)
for name,m in [('RAW106_actual_blue_blouse_only',cloth106),('LOCKED103_original_short_sleeve_foreground',sleeve),('REMOVE_old_near_complete_arm_and_hand',oldnear_clean)]:Image.fromarray((m*255).astype('uint8')).save(R/'masks'/f'{name}.png')
for tone,color in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
 bg=Image.new('RGBA',size,color);bg.alpha_composite(out);bg.save(R/f'qa/F106_complete_canvas_{tone}.png');bg.crop((1300,0,1890,1080)).save(R/f'qa/F106_complete_person_{tone}.png')
 bg.crop((1440,235,1810,480)).resize((1110,735)).save(R/f'qa/F106_shoulder_short_sleeve_elbow_wrist_same_whole_grip_{tone}_3x.png')
 bg.crop((1360,360,1690,740)).resize((660,760)).save(R/f'qa/F106_continuous_underarm_blouse_waist_{tone}_2x.png')
o=np.array(out);motiona=np.array(motion);mcore=(motiona[:,:,3]==255)&~sleeve
fixedbody=np.array(body);bodycore=(fixedbody[:,:,3]==255)&~(motiona[:,:,3]>0)&~sleeve
checks={'state':'ZERO_CALL_SEMANTIC_TRIAL_PENDING_ACTUAL_VIEW_AND_ASTRA','candidate':str(dest.relative_to(R)),'candidate_SHA256':sha(dest),'locked103_SHA256':sha(srcp),'raw106_used_for_cloth_only_SHA256':sha(rawp),'same_whole_motion_group_path':str(motionp.relative_to(P.parents[3])),'same_whole_motion_group_SHA256':sha(motionp),'only_group_transform':{'native':[0,-12.359119141727836],'world':[0,-4.5],'rotation':0,'scale':1},'motion_group_copied_without_further_transform':True,'independent_wrist_hand_finger_lamp_fit':False,'failed106_arm_hand_lamp_adopted':False,'new_RGB_drawing_blur_or_recolor':False,'shadow_in_motion_group':False,'native_requests_this_trial':0,'native106_total_requests':1,'native106_total_raw_outputs':1,'native106_total_retries':0,'source_motion_opaque_core_RGBA_changes_outside_front_sleeve':int(np.any(o[mcore]!=motiona[mcore],axis=1).sum()),'source_fixed_body_opaque_core_RGBA_changes_outside_motion':int(np.any(o[bodycore]!=fixedbody[bodycore],axis=1).sum()),'actual_cloth_plate_pixels':int(cloth106.sum())}
assert checks['source_motion_opaque_core_RGBA_changes_outside_front_sleeve']==0
assert checks['source_fixed_body_opaque_core_RGBA_changes_outside_motion']==0
(R/'qa/checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False,indent=2))
