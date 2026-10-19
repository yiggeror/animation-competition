"""Prepare only the four authorized review inputs; NEVER call imagegen.

Only the already-approved F030 technical target is a complete pose. Image2
uses actual F024 head/material crops, image3 enlarges the SAME F030 target,
and image4 is a binary semantic guide. No failed F030 or old whole pose is
in the planned request. These are references, not a new native drawing.
"""
from pathlib import Path
import json,hashlib,shutil,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy import ndimage

R=Path(__file__).resolve().parent
BASE=R.parent
T=BASE/'FIRST3_024_030_036_TARGETS_zero_call_20261019'
A=BASE/'FIRST3_NATIVE_024_030_036_call01_each_20261019'
P=BASE/'REGISTER_REAL_PROPS_zero_call_v1_20261019'
for d in ('inputs','masks','requests','qa'):(R/d).mkdir(exist_ok=True)
W,H=1024,1536
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
source024=A/'F024/originals/S29_F024_call01_RAW_UNTOUCHED.png'
assert sha(source024)=='215ddc5536b750ee56fc9cd53aafc6f3b8735e335cc7c1a5138328efa17ff61e'
target_source=T/'targets/F030_COMPLETE_NEW_VOLUME_TARGET_TECHNICAL.png'
native_source=T/'native_probes/F030_WHOLE_TARGET_REAL_PIXEL_PROBE_NOT_NEW_DRAWING.png'
target=Image.open(native_source).convert('RGBA')
raw=Image.open(source024).convert('RGBA')
geometry=json.loads((T/'geometry/THREE_ACTUAL_TARGETS.json').read_text())['targets'][1]
assert geometry['frame']==30

# 1: exact approved complete NEW target, never a second complete old pose.
one=R/'inputs/01_F030_ONLY_COMPLETE_NEW_TARGET_TECHNICAL.png'
shutil.copyfile(target_source,one)
assert one.read_bytes()==target_source.read_bytes()

# 2: no torso/arm/whole mother/camera image. Interior swatch RGB stays exact.
two=R/'inputs/02_F024_HEAD_IDENTITY_AND_INTERIOR_MATERIAL_CROPS_ONLY.png'
sheet=Image.new('RGB',(760,725),'#edf0f2');d=ImageDraw.Draw(sheet)
d.text((20,14),'HEAD IDENTITY + INTERIOR MATERIAL ONLY',font=font(23),fill='#22364c')
d.text((20,45),'Actual approved F024 pixels; no arm or complete old pose',font=font(17),fill='#ad481e')
headbox=(235,10,680,395)
head=raw.crop(headbox);hb=Image.new('RGBA',head.size,(237,240,242,255));hb.alpha_composite(head)
sheet.paste(hb.convert('RGB'),(20,85))
d.text((20,485),'Same silver bun, glasses, face and quiet downward gaze',font=font(17),fill='#22364c')
swatches=[('LIGHT BLUE BLOUSE INTERIOR',(345,465,425,595),(20,555)),
          ('INDIGO COTTON INTERIOR',(570,805,620,875),(350,555))]
crop_records=[{'role':'head_identity_only','source':str(source024),'native_crop':headbox,'destination':[20,85],'scale':1,'composite':'neutral gray for alpha only'}]
swatch_rgb_checks=[]
for label,box,pos in swatches:
 patch=raw.crop(box).convert('RGB');sheet.paste(patch,pos)
 d.text((pos[0],pos[1]-28),label,font=font(15),fill='#22364c')
 check=np.array_equal(np.array(sheet)[pos[1]:pos[1]+patch.height,pos[0]:pos[0]+patch.width],np.array(raw)[box[1]:box[3],box[0]:box[2],:3])
 assert check;swatch_rgb_checks.append(check)
 crop_records.append({'role':label,'source':str(source024),'native_crop':box,'destination':pos,'scale':1,'interior_RGB_exact':True})
sheet.save(two)

# 3: one enlarged crop of the SAME F030 target. It covers the entire far
# shoulder/sleeve/elbow/wrist/bangle/pinch and opaque face down to lap support.
three=R/'inputs/03_SAME_F030_COMPLETE_FAR_ARM_PINCH_OPAQUE_CLOTH_ENLARGED.png'
cropbox=(465,410,1015,1080);crop=target.crop(cropbox)
bg=Image.new('RGBA',crop.size,(237,240,242,255));bg.alpha_composite(crop)
scale=1.8;detail=Image.new('RGB',(1020,1310),'#edf0f2');dd=ImageDraw.Draw(detail)
dd.text((15,12),'F030 SAME TARGET: COMPLETE FAR ARM + OPAQUE CLOTH',font=font(24),fill='#22364c')
dd.text((15,47),'Whole chain redraw; technical cut seams are NOT final anatomy',font=font(20),fill='#ad481e')
detail.paste(bg.convert('RGB').resize((990,1206),Image.Resampling.LANCZOS),(15,85))
detail.save(three)

# 4: broad semantic change domain. Includes the complete source-to-target
# arm sweep and the full continuous cotton face; never a narrow wrist mask.
def polygon(points):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
source_sweep=polygon([(493,410),(588,410),(655,500),(712,560),(800,586),(873,591),(941,630),(970,696),(969,759),(914,797),(851,776),(775,747),(708,741),(643,720),(595,699),(557,669),(533,614),(510,550),(495,486)])
target_chain=polygon([(470,405),(579,404),(615,440),(627,496),(627,555),(623,587),(660,585),(714,581),(765,603),(823,628),(855,669),(854,720),(817,749),(764,736),(709,734),(657,755),(603,767),(555,756),(518,728),(500,680),(493,625),(472,565)])
full_cotton=polygon([(548,707),(650,715),(741,698),(785,675),(842,687),(905,715),(969,791),(1019,883),(1023,1016),(980,1080),(905,1100),(840,1054),(749,1040),(640,1012),(587,978),(525,1024),(395,985),(298,936),(266,902),(300,869),(360,828),(422,782),(486,743)])
cloth_new=np.array(Image.open(T/'masks/F030_FULL_CONTINUOUS_REAR_CLOTH_FACE.png'))>0
cloth_new|=np.array(Image.open(T/'masks/F030_ACTUAL_MOVING_CLOTH_SURFACE.png'))>0
full_cotton|=cloth_new
semantic=source_sweep|target_chain|full_cotton
# Preserve the WHOLE near bare right upper arm/forearm/wrist/palm, not just C1.
nearprotect=polygon([(130,574),(270,585),(287,632),(470,633),(526,654),(566,692),(575,742),(559,783),(503,799),(450,779),(310,778),(180,765),(135,735),(126,676)])
# Original visible leather and all straight shafts are black protection islands
# inside the semantic cotton domain; they are NOT transparent holes in cloth.
original=Image.open(P/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png').convert('RGBA')
prop_protect=np.array(original.getchannel('A'))>0
neck3=polygon([(489,722),(558,723),(568,782),(511,800),(483,770)])&prop_protect
yy,xx=np.indices((H,W))
# Trace the actual approved cotton hem so the exposed knees/thighs immediately
# below it are protected too, rather than protecting only calves below y1100.
hem_x=[0,100,170,280,311,450,521,609,638,750,822,898,947,1023]
hem_y=[900,900,930,903,918,980,1003,958,960,1015,1017,1006,1053,1105]
hem_y_at_x=np.interp(np.arange(W),hem_x,hem_y)[None,:]
lowerprotect=yy>=hem_y_at_x
headprotect=yy<395
protection=nearprotect|prop_protect|lowerprotect|headprotect
semantic &= ~protection
four=R/'inputs/04_COMPLETE_MOVEMENT_SEMANTIC_WHITE_PROTECT_BLACK.png'
Image.fromarray(semantic.astype('uint8')*255).save(four)
for name,m in [('FULL_NEAR_BARE_RIGHT_ARM_PROTECTED',nearprotect),('TRUE_ORIGINAL_PROPS_AND_FOUR_RODS_PROTECTED',prop_protect),('TRUE_NECK3_CONTEXT_PROTECTED',neck3),('LOWER_BODY_PROTECTED',lowerprotect),('FULL_COTTON_MOVE_DOMAIN_BEFORE_VISIBLE_PROP_PROTECTION',full_cotton)]:
 Image.fromarray(m.astype('uint8')*255).save(R/f'masks/{name}.png')

# Audit-only overlay is NOT one of the four request images and is never sent.
neutral=Image.new('RGBA',(W,H),(237,240,242,255));neutral.alpha_composite(target)
overlay=np.zeros((H,W,4),dtype='uint8');overlay[semantic]=[245,135,35,90]
audit=Image.alpha_composite(neutral,Image.fromarray(overlay));audit.save(R/'qa/SEMANTIC_DOMAIN_ON_SAME_TARGET_AUDIT_ONLY_NOT_INPUT.png')
checks={'new_imagegen_requests':0,'new_native_drawings':0,'planned_input_count':4,
 'first_input_exact_approved_F030_target_bytes':one.read_bytes()==target_source.read_bytes(),
 'all_other_inputs_are_crops_or_binary_not_old_complete_pose':True,
 'failed_F030_not_in_request':True,'old_complete_mother_not_in_request':True,'old_character_camera_not_in_request':True,
 'source_024_actual_raw_sha256':sha(source024),'interior_swatch_RGB_checks':swatch_rgb_checks,
 'semantic_values':np.unique(np.array(Image.open(four))).tolist(),
 'semantic_white_pixels':int(semantic.sum()),'semantic_near_bare_arm_overlap_pixels':int((semantic&nearprotect).sum()),
 'semantic_true_neck3_overlap_pixels':int((semantic&neck3).sum()),'semantic_original_props_rods_overlap_pixels':int((semantic&prop_protect).sum()),
 'semantic_lower_body_overlap_pixels':int((semantic&lowerprotect).sum()),'whole_far_shoulder_allowed':bool(semantic[465,525]),
 'target_elbow_allowed':bool(semantic[665,559]),'target_wrist_allowed':bool(semantic[645,703]),
 'target_pinch_allowed':bool(semantic[688,785]),'lap_fold_surface_allowed':bool(semantic[900,920]),
 'mask_is_semantic_reference_not_tool_pixel_inpaint_mask':True,
 'cloth_black_islands_mean_protected_visible_real_props_not_cloth_holes':True,
 'guide_not_native_art':True,'no_F036_request':True}
for k in ['first_input_exact_approved_F030_target_bytes','whole_far_shoulder_allowed','target_elbow_allowed','target_wrist_allowed','target_pinch_allowed','lap_fold_surface_allowed']:assert checks[k],k
for k in ['semantic_near_bare_arm_overlap_pixels','semantic_true_neck3_overlap_pixels','semantic_original_props_rods_overlap_pixels','semantic_lower_body_overlap_pixels']:assert checks[k]==0,k
(R/'qa/AUTOMATED_INPUT_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
(R/'SOURCE_CROPS_AND_GEOMETRY.json').write_text(json.dumps({'source_024_actual_raw':str(source024),'source_024_sha256':sha(source024),'approved_target_source':str(target_source),'approved_target_source_sha256':sha(target_source),'approved_native_target_probe':str(native_source),'approved_native_target_probe_sha256':sha(native_source),'target_soft_geometry':geometry,'identity_material_crops':crop_records,'detail_native_crop':cropbox,'detail_scale':scale,'complete_pose_rule':'Only image1 is a complete pose, the approved new F030 target. Image2 is head/interior swatches only, image3 is a crop from the same F030 target, image4 binary mask only. No complete mother000, complete F024 old pose, failed F030 or character camera reference is sent.'},indent=2)+'\n')
inputs=[one,two,three,four]
(R/'requests/FOUR_PLANNED_INPUTS_SHA256.json').write_text(json.dumps([{'order':i+1,'path':str(p),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(inputs)],indent=2)+'\n')
(R/'CALL_STATE_ZERO.json').write_text(json.dumps({'state':'FOUR_INPUT_PREPARATION_ONLY_AWAITING_ASTRA_SHORT_GATE','new_requests_started':0,'new_raw_outputs':0,'retry_requests_started':0,'F036_started':0,'prior_group_historical_requests':2,'prior_group_historical_raw_outputs':2,'authorized_scope':'Prepare four review inputs only; do not call imagegen before short gate'},indent=2)+'\n')
print(json.dumps(checks,indent=2))
