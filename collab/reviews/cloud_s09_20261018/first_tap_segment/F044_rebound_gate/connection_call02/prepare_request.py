#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;T=P.parent
for n in ['reference','masks','requests','originals','candidate','qa']:(R/n).mkdir(exist_ok=True)
assert not (R/'requests/execution_state.json').exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=P/'candidate/F044_complete_native_arm_rigid_fit_TRIAL.png';im=Image.open(source).convert('RGBA');a=np.array(im);size=im.size;yy,xx=np.indices(a.shape[:2])
mother=T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png';m=np.array(Image.open(mother).convert('RGBA'))
oldedit=np.array(Image.open(P/'masks/F044_complete_near_arm_vacated_WHITE_EDIT_PENDING.png'))>0
def mask(n):return np.array(Image.open(P/'masks'/f'{n}.png'))>0
def poly(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
holes=(a[:,:,3]<180)&(m[:,:,3]>=128)&oldedit&(yy>=600)&(yy<=790)&(xx>=650)&(xx<=1065)
edit=binary_dilation(holes,iterations=5)
root=poly([(678,639),(731,632),(765,681),(740,716),(681,704)])
wrist=poly([(1005,518),(1048,518),(1080,577),(1042,605),(996,579)])
edit|=root|wrist
unit=np.array(Image.open(P/'reference/F044_rigid_hand_torch_up48_SOURCE.png').convert('RGBA'))
actualunit=unit[:,:,3]>0
proximal_cut_release=wrist&(abs((yy-xx)+474)<=7)&actualunit
guards=mask('head_neck_collar_actual')|mask('near_ruffle_actual_material')|mask('fixed_receiver_palm_material')|mask('waist_and_skirt_actual_material')|(actualunit&~proximal_cut_release)
edit&=~guards
crop=(620,500,1160,860);inside=(xx>=620)&(xx<1160)&(yy>=500)&(yy<860);edit&=inside
im.crop(crop).save(R/'reference/F044_existing_arm_local_crop.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F044_connection_crop_WHITE_EDIT.png')
Image.fromarray(edit.astype('uint8')*255).save(R/'masks/F044_explicit_connection_domain.png')
Image.fromarray(proximal_cut_release.astype('uint8')*255).save(R/'masks/proximal_wrist_extraction_edge_release.png')
for name,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,color);z.alpha_composite(im);w=Image.new('RGBA',size,(220,35,120,0));w.putalpha(Image.fromarray(edit.astype('uint8')*100));z.alpha_composite(w);z.crop(crop).convert('RGB').save(R/f'qa/actual_connection_domain_{name}.png')
prompt='''Repair ONLY the WHITE local connection areas of image2 in image1. Image1 is the actual540x360 RGBA local crop of F044 after the FIRST flashlight tap has rebounded. Keep this exact540x360 framing and transparent background. Image3 is locked motherF042 for the original sleeve design, dress, colors and back-arm depth only; do not copy its lower flashlight or old near-arm pose.

The full raised near RIGHT arm in image1 is already real native artwork, rigidly connected to the fixed original hand and torch. Keep its current elbow location, whole upper-arm/forearm proportions and raised-wrist position. The complete flashlight and genuine grasping fingers remain fixed and rigid, switchOFF, light dark. The open LEFT receiving palm and original far lower arm remain fixed. This is a small connection/occlusion repair, not another pose or a new arm.

The narrow transparent strip BELOW the raised near arm is an extraction vacancy, not a sleeve, gap through the body, white scar or exposed bone. Reconstruct the real material BEHIND the foreground near arm: original yellow torso cloth with small white dots where it is chest, and the genuine far upper arm/sleeve continuation where that back arm is newly revealed. The far yellow puff sleeve is one rounded original sleeve behind the near forearm. Let its contour disappear naturally behind the foreground skin; no pointed fork, second sleeve ring or cuff ink over the near arm. Keep the far forearm attached naturally to its existing lower arm and unchanged palm. Do not paint the entire strip skin or the entire strip yellow without respecting the original back-arm/body layout.

At the LEFT near yellow ruffle opening, join original real sleeve cloth to one continuous upper-arm skin volume. Preserve the original black-locked ruffle and white dots; remove the source-cut vacancy and any old ink/white outline at its inside. Do not add another cuff arc or move the sleeve. The whole near arm is foreground over the dress and far sleeve.

At the RIGHT wrist, connect the existing forearm into the original hand naturally. Only the proximal extraction edge is released; all actual grasping fingers, thumb, palm, flashlight and its original shape are black-locked. One continuous wrist silhouette, no narrow bridge, extra skin sliver, parallel old outline, overlapping V or detached wrist. Preserve the accepted natural arm thickness.

The original yellow torso waist/belt and skirt line in image1 are already correct and black-locked: do not raise or draw a second waistline. Match the original skin flat color and soft warm cel shadow separately; do not brighten, wash out or relight. Keep blue-gray empty space truly transparent. No scene, light beam, extra hands, objects, dots floating in space, labels, masks, guide lines or motion blur. Return the repaired local crop only, preserving all black source material and current drawing positions.'''
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F044_existing_arm_local_crop.png'),str(R/'masks/F044_connection_crop_WHITE_EDIT.png'),str(mother)],'transparent_background':True}
(R/'requests/prompt.txt').write_text(prompt+'\n');(R/'requests/arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
meta={'status':'ACTUAL_F044_CONNECTION_REPAIR_INPUT_READY_NOT_CALLED','source_trial_sha256':sha(source),'first_native_raw_sha256':'3d0561f41e8dadd5f318ae51b9b732f8ddc6d3835217ee009d4cc45482fc25a4','crop_xyxy':crop,'crop_size':[540,360],'white_pixels':int(edit.sum()),'actual_input_hole_pixels':int(holes.sum()),'proximal_wrist_cut_material_released':int(proximal_cut_release.sum()),'original_real_grip_except_cut_white_overlap':int((edit&actualunit&~proximal_cut_release).sum()),'fixed_palm_white_overlap':int((edit&mask('fixed_receiver_palm_material')).sum()),'native_F044_requests_before_this':1,'new_requests':0,'inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']]}
(R/'requests/input_freeze.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False,indent=2))
