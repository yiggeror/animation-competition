from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
R=Path(__file__).resolve().parent;B=R.parent
S=B/'F036_LOCAL_SOFT_LIP_ZERO_CALL_v1_20261019'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
one=R/'frozen_inputs/01_ONLY_APPROVED_LOCAL_TARGET.png'
shutil.copyfile(S/'01_LOCAL_TARGET_ARM_AND_CONTINUOUS_SOFT_LIP.png',one)
assert sha(one)=='ed1f10ce0d4f14f83efce3f2d4bf2fc77eac89d7154ae8a09aadb2f61c8d2cfc'
im=Image.open(one).convert('RGB');W,H=1024,1536
def cubic(p0,p1,p2,p3,n=180):
 t=np.linspace(0,1,n)[:,None]
 return (1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)
N=np.array([711.,670.])
edge=np.vstack([cubic(N+[0,5],[772,691],[810,768],[824,786]),cubic([824,786],[842,805],[875,805],[902,841])[1:]])
tangent=np.gradient(edge,axis=0);normal=np.c_[-tangent[:,1],tangent[:,0]]
normal/=np.linalg.norm(normal,axis=1)[:,None]
u=np.linspace(0,1,len(edge));width=2+22*np.sin(np.pi*u)**.75
outer=edge+normal*width[:,None]
mi=Image.new('L',(W,H));ImageDraw.Draw(mi).polygon([tuple(p) for p in np.vstack([edge,outer[::-1]])],fill=255)
lip=np.array(mi)>0
yy,xx=np.indices((H,W));roi=(xx>=812)&(xx<=885)&(yy>=783)&(yy<=839)
# Open the actual finite cloth cover surface AND a one-native-pixel AA border,
# not just previously indexed black feather samples. No protected pinholes.
opening=ndimage.binary_dilation(lip&roi,iterations=1)
box=(440,350,960,900)
old=np.array(Image.open(S/'03_ONE_LOCAL_DOMAIN_PROTECT_NEAR_CONTACT.png').convert('L').resize((520,550),Image.Resampling.NEAREST))>0
patch_open=opening[350:900,440:960]
new=old|patch_open
props=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))
core=np.array(Image.open(P/'masks/TRUE_TAIL_CORE_COMMON030.png'))>0
prop_open=opening&(props[:,:,3]>0)
assert np.max(props[prop_open,:3])<100,'no gold body or shaft may be unlocked'
covered_core=int((core&opening).sum());assert covered_core<int(core.sum())*.15
assert not np.any(~new&patch_open)
assert np.array_equal(new[~patch_open],old[~patch_open])
four=R/'frozen_inputs/04_FIXED_WHITE_DOMAIN_WITH_SOFT_LIP_TAIL_AA_OPEN.png'
Image.fromarray(new.astype('uint8')*255).resize(im.size,Image.Resampling.NEAREST).save(four)
two=R/'frozen_inputs/02_SAME_LOCAL_TARGET_PINCH_AND_THICK_SOFT_LIP_CLOSEUP.png'
panel=Image.new('RGB',(1500,900),'#edf0f2');d=ImageDraw.Draw(panel)
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((20,14),'DETAILS OF THE SAME LOCAL TARGET ONLY',font=font(26),fill='#23364d')
d.text((20,52),'Whole bangle/wrist/pinch and continuous cotton front edge',font=font(19),fill='#23364d')
panel.paste(im.crop((230,390,940,1000)),(20,105))
d.text((790,112),'OPAQUE THICKNESS + DARK INSIDE',font=font(21),fill='#23364d')
panel.paste(im.crop((665,790,925,1000)).resize((650,525),Image.Resampling.LANCZOS),(790,165))
d.text((790,740),'Feather lines end at the soft cloth front.',font=font(19),fill='#23364d')
d.text((790,780),'This technical surface must be redrawn as cotton.',font=font(17),fill='#23364d')
panel.save(two)
three=R/'frozen_inputs/03_HEAD_IDENTITY_AND_INTERIOR_MATERIAL_CROPS_ONLY.png'
shutil.copyfile(P/'inputs/02_024_HEAD_AND_INTERNAL_MATERIAL_CROPS_ONLY.png',three)

oldimg=np.array(Image.open(S/'03_ONE_LOCAL_DOMAIN_PROTECT_NEAR_CONTACT.png').convert('L'))>0
newimg=np.array(Image.open(four).convert('L'))>0
add=newimg&~oldimg
overlay=np.array(im).copy();overlay[add]=(np.array([240,75,120])*.65+overlay[add]*.35).round().astype('uint8')
audit=Image.new('RGB',(1350,450),'#edf0f2');d=ImageDraw.Draw(audit)
crop=(700,820,890,980)
for ox,title,part in [(10,'SAME TARGET / NEWLY OPENED AA',Image.fromarray(overlay)),(460,'OLD WHITE DOMAIN',Image.open(S/'03_ONE_LOCAL_DOMAIN_PROTECT_NEAR_CONTACT.png').convert('RGB')),(910,'FIXED WHITE DOMAIN',Image.open(four).convert('RGB'))]:
 d.text((ox,10),title,font=font(18),fill='#23364d');audit.paste(part.crop(crop).resize((420,354),Image.Resampling.NEAREST),(ox,60))
audit.save(R/'qa/ACTUAL_SOFT_LIP_TAIL_AA_WHITE_OPENING_NO_BLACK_PINHOLES.png')
inputs=[one,two,three,four]
(R/'requests/ACTUAL_INPUTS_SHA256.json').write_text(json.dumps([{'order':i+1,'path':str(p),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(inputs)],indent=2)+'\n')
checks={'approved_local_target_commit':'53b83004e5b2a38fdb4346d117e3a390a8cc470b','first_target_exact_approved_bytes':True,'target_geometry_and_pose_unchanged':True,'source030_common_pixel_pinch':[711,670],'only_mask_change':'white foreground cloth-cover surface +1 native pixel AA border over the small tail tips','newly_white_display_pixels':int(add.sum()),'black_pixels_inside_planned_cover_plus_AA':int((~new&patch_open).sum()),'unchanged_outside_planned_opening':True,'unlocked_true_pixels_are_dark_tail_only':True,'tail_core_opened_for_occlusion':covered_core,'tail_core_total':int(core.sum()),'tail_core_remaining_locked':int(core.sum())-covered_core,'original_body_and_four_rods_not_unlocked':True,'old_failed_outward_whole_poses_in_request':False,'one_local_repair_domain':True,'no_generation_executed_by_this_preparation':True}
(R/'qa/FROZEN_INPUT_AND_FIXED_MASK_CHECKS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False))
