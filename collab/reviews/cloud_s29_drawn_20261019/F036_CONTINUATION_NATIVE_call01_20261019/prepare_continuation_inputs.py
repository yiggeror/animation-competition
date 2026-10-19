"""Same approved four-input rule for F036, no imagegen calls in this script."""
from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/tmp/s29-image-tools')
import cv2

R=Path(__file__).resolve().parent;B=R.parent
T=B/'FIRST3_024_030_036_TARGETS_zero_call_20261019'
P=B/'REGISTER_REAL_PROPS_zero_call_v1_20261019'
PREP=B/'F030_REPAIR_FOUR_INPUTS_ZERO_CALL_v1_20261019'
GOOD=B/'F030_REPAIR_NATIVE_call01_20261019'
assert json.loads((GOOD/'CALL_STATE.json').read_text())['status']=='LOCAL_NATIVE_ANATOMY_INWARD_LIFT_PASS_PROP_CAMERA_PENDING'
for d in ('frozen_inputs','requests','qa','originals'):(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
native=T/'native_probes/F036_WHOLE_TARGET_REAL_PIXEL_PROBE_NOT_NEW_DRAWING.png'
source1=T/'targets/F036_COMPLETE_NEW_VOLUME_TARGET_TECHNICAL.png'
one=R/'frozen_inputs/01_F036_ONLY_COMPLETE_NEW_TARGET_TECHNICAL.png';shutil.copyfile(source1,one)
source2=PREP/'inputs/02_F024_HEAD_IDENTITY_AND_INTERIOR_MATERIAL_CROPS_ONLY.png'
two=R/'frozen_inputs/02_F024_HEAD_IDENTITY_AND_INTERIOR_MATERIAL_CROPS_ONLY.png';shutil.copyfile(source2,two)
im=Image.open(native).convert('RGBA');box=(465,410,1015,1080);crop=im.crop(box)
bg=Image.new('RGBA',crop.size,(237,240,242,255));bg.alpha_composite(crop)
detail=Image.new('RGB',(1020,1310),'#edf0f2');d=ImageDraw.Draw(detail)
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((15,12),'F036 SAME TARGET: FIRST SMALL OUTER TAIL COVER',font=font(24),fill='#22364c')
d.text((15,47),'Complete far arm + one opaque sheet; redraw technical seams',font=font(20),fill='#ad481e')
detail.paste(bg.convert('RGB').resize((990,1206),Image.Resampling.LANCZOS),(15,85))
three=R/'frozen_inputs/03_SAME_F036_COMPLETE_ARM_FIRST_TAIL_COVER_ENLARGED.png';detail.save(three)

g=json.loads((T/'geometry/THREE_ACTUAL_TARGETS.json').read_text())['targets'][2];assert g['frame']==36
semantic=np.array(Image.open(PREP/'inputs/04_COMPLETE_MOVEMENT_SEMANTIC_WHITE_PROTECT_BLACK.png'))>0
full_arm=[]
for name,mat in [('SOURCE_FAR_UPPER_SHOULDER_SLEEVE','upper'),('SOURCE_FAR_FOREARM','forearm'),('SOURCE_FAR_HAND_BANGLE_TOGETHER','hand_and_bangle_together')]:
 m=np.array(Image.open(T/f'masks/{name}.png'))
 a=cv2.warpAffine(m,np.array(g['human_matrices_reference_only'][mat],dtype='float32'),(1024,1536),flags=cv2.INTER_NEAREST)>0
 full_arm.append((name,a));semantic|=a
front=np.array(Image.open(T/'masks/F036_ACTUAL_MOVING_CLOTH_SURFACE.png'))>0
rear=np.array(Image.open(T/'masks/F036_FULL_CONTINUOUS_REAR_CLOTH_FACE.png'))>0
semantic|=front|rear
near=np.array(Image.open(PREP/'masks/FULL_NEAR_BARE_RIGHT_ARM_PROTECTED.png'))>0
lower=np.array(Image.open(PREP/'masks/LOWER_BODY_PROTECTED.png'))>0
props=np.array(Image.open(P/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png').getchannel('A'))>0
# This approved state first turns a small leading lip in FRONT. Permit only
# the real target's 544 foreground-occlusion pixels, including 36 core pixels.
# All other true leather/straight-shaft pixels remain black protection.
cover_allowed=props&front
protected_props=props&~cover_allowed
yy,xx=np.indices(semantic.shape);protect=near|lower|protected_props|(yy<395)
semantic&=~protect
four=R/'frozen_inputs/04_COMPLETE_MOVEMENT_WHITE_WITH_FIRST_TAIL_COVER_ONLY.png'
Image.fromarray(semantic.astype('uint8')*255).save(four)
Image.fromarray(cover_allowed.astype('uint8')*255).save(R/'qa/APPROVED_FIRST_PROP_OCCLUSION_DOMAIN_ONLY_NOT_INPUT.png')
neutral=Image.new('RGBA',im.size,(237,240,242,255));neutral.alpha_composite(im)
over=np.zeros((1536,1024,4),dtype='uint8');over[semantic]=[245,135,35,90]
Image.alpha_composite(neutral,Image.fromarray(over)).save(R/'qa/SEMANTIC_DOMAIN_ON_SAME_TARGET_AUDIT_ONLY_NOT_INPUT.png')
coverage={}
for name,arm in full_arm:
 visible=arm&~protect;missing=int((visible&~semantic).sum());assert missing==0
 coverage[name]={'visible_nonprotected_pixels':int(visible.sum()),'covered_white':int((visible&semantic).sum()),'missing_white':missing}
core=np.array(Image.open(T/'masks/CONSERVATIVE_ORIGINAL_BLACK_TAIL_CORE.png'))>0
checks={'same_four_input_rule':True,'only_complete_pose_is_approved_new_F036':True,'first_target_exact_source_bytes':one.read_bytes()==source1.read_bytes(),'second_exact_approved_024_identity_material_crop_bytes':two.read_bytes()==source2.read_bytes(),'no_old_complete_mother_pose':True,'no_old_complete_024_or_030_pose':True,'no_failed_030_image_in_request':True,'source_front_fold_actual_original_prop_overlap_pixels':int(cover_allowed.sum()),'approved_original_black_tail_core_new_cover_pixels':int((front&core).sum()),'near_bare_arm_white_overlap':int((semantic&near).sum()),'lower_body_white_overlap':int((semantic&lower).sum()),'remaining_true_prop_white_overlap':int((semantic&protected_props).sum()),'semantic_values':np.unique(np.array(Image.open(four))).tolist(),'far_visible_arm_coverage':coverage,'mask_is_semantic_reference_not_executed_inpaint':True,'new_imagegen_calls_in_preparation':0,'real_native_continuation_source':str(GOOD/'originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png'),'real_native_continuation_source_sha256':'0c182aa0d62acf8647daa316e06cdb4bfdd9ebd6c2e6c02f1b0e2f8065ffd4e5','source_030_complete_pose_is_provenance_only_not_sent':True}
assert checks['approved_original_black_tail_core_new_cover_pixels']==36
for k in ('near_bare_arm_white_overlap','lower_body_white_overlap','remaining_true_prop_white_overlap'):assert checks[k]==0
(R/'qa/ACTUAL_CONTINUATION_INPUT_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
(R/'qa/TARGET_SOFT_GEOMETRY_AND_SOURCE.json').write_text(json.dumps({'approved_target_source':str(source1),'approved_native_probe_source':str(native),'detail_native_crop':box,'detail_scale':1.8,'soft_geometry':g,'limits':'Technical contact target, not newly drawn native art. Prop mask counts prove target construction only, not raw output contact/collision.'},indent=2)+'\n')
inputs=[one,two,three,four]
(R/'requests/ACTUAL_INPUTS_SHA256.json').write_text(json.dumps([{'order':i+1,'actual_frozen_path':str(p),'sha256':sha(p),'size':list(Image.open(p).size),'source_role':['approved_new_F036_target','approved_024_head_and_interior_material_only','enlarged_same_F036_target','complete_movement_semantics_first_small_tail_occlusion'][i]} for i,p in enumerate(inputs)],indent=2)+'\n')
print(json.dumps(checks,indent=2))
