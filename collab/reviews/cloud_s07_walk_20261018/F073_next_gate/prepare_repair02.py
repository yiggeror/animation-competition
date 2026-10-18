#!/usr/bin/env python3
"""Complete trousers redraw at the unchanged real source feet; no leg warping."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P/'repair_call02'
for d in ['reference','masks','qa','requests','originals']:(R/d).mkdir(parents=True,exist_ok=True)
assert not (R/'requests/execution_state.json').exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=P/'candidate/F073_complete_native_layered_PENDING_ACTUAL_REVIEW.png';im=Image.open(src).convert('RGBA');a=np.array(im);size=im.size;yy,xx=np.indices(a.shape[:2])
def capsule(points,r):
 z=Image.new('L',size);d=ImageDraw.Draw(z);pts=[tuple(map(float,q))for q in points];d.line(pts,fill=255,width=2*r+1)
 for x,y in pts:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
g=json.loads((P/'geometry/preparation_checks.json').read_text());m=json.loads((P/'sources/F062_calibrated_preparation_metadata.json').read_text())
H=np.array(g['hidden_hip_proxy_native']);A=np.array(m['near062_chain_native'][-1])+np.array(g['near_complete_shoe_translation_native'])
chain=np.array(m['near062_chain_native']);l1=np.linalg.norm(chain[1]-chain[0]);l2=np.linalg.norm(chain[2]-chain[1]);v=A-H;dist=np.linalg.norm(v);u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=np.sqrt(l1*l1-along*along);perp=np.array([-u[1],u[0]]);ks=[H+along*u+height*perp,H+along*u-height*perp];K=max(ks,key=lambda q:q[0])
old=np.array(Image.open(P/'masks/actual_native_complete_trousers_material.png'))>0
nearfoot=np.array(Image.open(P/'layers/F073_near_shoe_ankle_SWING.png'));farfoot=np.array(Image.open(P/'layers/F073_far_shoe_ankle_SUPPORT_FIXED.png'));body=np.array(Image.open(P/'layers/F073_body_head_blouse.png'));neararm=np.array(Image.open(P/'layers/F073_near_complete_arm.png'));fararm=np.array(Image.open(P/'layers/F073_far_complete_arm_jade_hand.png'))
domain=binary_dilation(old,iterations=10)|capsule([H,K,A],64)|capsule([H+[-80,-64],H+[50,-64]],42)
# Genuine partial body AA does not freeze empty under-layer slots. Original
# independent body/arm source material will be recomposed after native output.
hard=(body[:,:,3]>=128)|(neararm[:,:,3]>0)|(fararm[:,:,3]>0)|(nearfoot[:,:,3]>0)
oldfront=(np.array(Image.open(P/'production_layers/native_complete_trousers_color_locked.png'))[:,:,3]>0)|(body[:,:,3]>0)|(neararm[:,:,3]>0)|(fararm[:,:,3]>0)|(nearfoot[:,:,3]>0)
far_visible=(farfoot[:,:,3]>0)&~oldfront
hard|=far_visible
edit=domain&~hard&(yy>=498)&(yy<=1010)&(xx>=780)&(xx<1300)
crop=(780,280,1300,1060);im.crop(crop).save(R/'reference/F073_actual_fixed_shoes_current_NOT_PASS.png');Image.fromarray(edit.astype('uint8')*255).save(R/'masks/full_trousers_actual_fixed_feet_WHITE_EDIT.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/crop_WHITE_EDIT.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
guide=Image.new('RGBA',size,(213,223,231,255));guide.alpha_composite(im);d=ImageDraw.Draw(guide)
d.line([tuple(H),tuple(K),tuple(A)],fill='#cc4c4c',width=3)
for q,label,color in [(H,'hidden hip PROXY','#bb4c4c'),(K,'bend corridor ONLY','#bb4c4c'),(A,'actual ORIGINAL ankle','#0087b5')]:
 x,y=q;d.ellipse((x-7,y-7,x+7,y+7),outline=color,width=3);d.text((x-100,y-25),label,fill=color)
d.line((970,1022,1230,1022),fill='#33858e',width=2)
guide.crop(crop).convert('RGB').save(R/'reference/actual_foot_target_and_hidden_proxy_GUIDE_NOT_ART.png')
for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(im);wash=Image.new('RGBA',size,(220,35,120,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));z.alpha_composite(wash);z.crop(crop).convert('RGB').save(R/f'qa/actual_complete_trousers_edit_{name}.png')
prompt='''Correct the COMPLETE WHITE TROUSERS in image1 using image2 as edit mask. Image1 is the actual520x780 crop with the ONLY genuine fixed original shoes already composited, but its current new near trouser leg is visibly disconnected and WRONG. Keep the exact same crop/camera and transparent background. Image3 is a guide on the same crop, not final art: red is a hidden hip PROXY and natural knee-bending corridor, blue marks the actual original near ankle. Image4 is lockedF062 PALETTE only, not a leg pose to copy.

F073: far anatomical LEFT leg supports on the LOWER original shoe. That complete genuine far shoe is already in its EXACT locked068 position and baseline. Near anatomical RIGHT leg is passing forward to the UPPER original shoe, which is already in its exact approved position. Do NOT reposition, resize, rotate, redraw or replace either shoe or true ankle. The upper near shoe is directly OVER the planted lower shoe, only63native pixels higher. It is NOT another shoe farther to the right. All real shoes, hands, arms, head and source blouse are black-locked.

The current floating near cuff is far too far RIGHT of the actual exposed near ankle: its old position is obsolete. REDRAW the ENTIRE near thigh, natural knee volume AND WHOLE CALF/cuff, bending the knee forward and then bringing the calf BACK LEFT into the actual upper shoe ankle, as in the red corridor. One continuous real leg from the hidden hip inside the body down into that blue-marked genuine ankle, with accepted unchanged limb volume and proportion. Do not bridge the empty gap with a thin skin strip, horizontal connector, long stretched calf or detached navy flap. Do not keep the old wrong knee/cuff location. The guide is a projected corridor, not measured anatomy; draw organic cloth, not the guide. Do not copy source piece cuts as joints.

The complete WHITE far trouser leg must stay weight-bearing naturally into the LOWER original shoe with original limb volume. Where the near thigh/calf passes in front, proper foreground cloth occludes the far leg. Whole trouser waist/hip/crotch/legs are one coherent native redraw, no seams between old and new trousers. Keep both true shoe endpoints exactly and remove ALL obsolete old pant contours within white. Do not paint a third foot or shoe fragment. Restore continuous real navy material directly under and slightly BEHIND the original blue blouse hem: the present thin transparent line under the shirt is an extraction vacancy, not a belt, white stripe or extra skin. No gap at the waist or cuff. Retain the actual original blouse, flowers and arms, do not lengthen the body or use the shirt hem as the hip joint.

Match lockedF062 navy flat planes and darker crease planes separately, alpha/ink crisp and original warm skin unchanged. No new lighting, background, glow, labels, red/blue guide lines, motion blur or global color change. The near leg is foreground and the genuine far supporting shoe is a back layer; do not use a hidden back outline to cut the new near leg. Return one repaired transparent local crop ONLY.'''
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F073_actual_fixed_shoes_current_NOT_PASS.png'),str(R/'masks/crop_WHITE_EDIT.png'),str(R/'reference/actual_foot_target_and_hidden_proxy_GUIDE_NOT_ART.png'),str(P/'sources/F062_palette_anchor.png')],'transparent_background':True}
(R/'requests/prompt.txt').write_text(prompt+'\n');(R/'requests/arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
checks={'status':'WHOLE_NATIVE_TROUSERS_REPAIR_INPUT_NOT_CALLED','source_notpass_sha256':sha(src),'crop_xyxy':crop,'white_pixels':int(edit.sum()),'hidden_H_proxy':H.tolist(),'near_knee_corridor_proxy':K.tolist(),'actual_near_ankle_proxy':A.tolist(),'guide_only_not_anatomical_bone_measurement':True,'source_calibrated_projected_lengths_only_for_corridor':[float(l1),float(l2)],'near_actual_shoe_white_overlap':int((edit&(nearfoot[:,:,3]>0)).sum()),'far_actual_visible_shoe_white_overlap':int((edit&far_visible).sum()),'inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'F073_requests_before':1,'F073_originals_before':1}
(R/'requests/input_freeze_PREPARED.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False,indent=2))
