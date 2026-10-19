"""Prepare only correct-pose generation references; never submit a model call."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hashlib, json, shutil
import numpy as np

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
OLD=ROOT.parent/'arm_correction_001'
RAW1=ROOT.parent/'generation_001/S20_F000_call001_raw.png'
RAW2=ROOT.parent/'generation_002_arm_local/S20_F000_call002_arm_raw.png'
for name in ['inputs','qa_only','masks_local']:(ROOT/name).mkdir(exist_ok=True)
# Final Astra boundary replaces the unsubmitted five-image draft. These are
# only local preparation derivatives, never model originals or frozen inputs.
for name in ['02_correct_shoulders_to_palms_large.png','03_edit_white.png',
             '04_protect_white.png','05_identity_materials_no_arms.png']:
    p=ROOT/'inputs'/name
    if p.exists():p.unlink()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'S20_F000_arms_target.png')=='a6d23f92bd8eef585881f1c674c2cbafe5c42b7a9a6696437b72430ae0cefa0a'
assert sha(RAW1)=='de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330'
assert sha(RAW2)=='9f8edf0f17d5aac7ec425bb74258e168a80f0aad096c56a3efd4f307b6ce98bf'
target=Image.open(OLD/'S20_F000_arms_target.png').convert('RGBA')
source=Image.open(RAW1).convert('RGBA')
assert target.size==source.size==(1672,941)
assert Image.open(RAW2).size==(1671,941)  # Preserve; never resize or use as input.
shutil.copyfile(OLD/'S20_F000_arms_target.png',ROOT/'inputs/01_F000_only_correct_pose.png')
shutil.copyfile(OLD/'masks/edit_white.png',ROOT/'inputs/04_edit_white.png')
shutil.copyfile(OLD/'masks/protect_white.png',ROOT/'masks_local/protect_white.png')
shutil.copyfile(OLD/'full_arm_volume_xray.png',ROOT/'inputs/03_correct_arm_xray.png')
for name in ['protect_L_palm_bracelet.png','protect_R_palm.png',
             'protect_four_front_rods.png','clear_old_limb_occupancy.png']:
    shutil.copyfile(OLD/'masks'/name,ROOT/'masks_local'/name)

fontpath=REPO/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(fontpath),29)
small=ImageFont.truetype(str(fontpath),24)

def gray(im):
    bg=Image.new('RGBA',im.size,(140,140,140,255))
    bg.alpha_composite(im.convert('RGBA'))
    return bg.convert('RGB')

crop=(875,235,1220,485)
native=target.crop(crop)
native.save(ROOT/'qa_only/correct_shoulders_to_palms_native.png')
enlarged=native.resize((1380,1000),Image.Resampling.NEAREST)
enlarged.save(ROOT/'inputs/02_target_shoulders_to_palms_4x.png')
transform={'source':'inputs/01_F000_only_correct_pose.png',
    'source_sha256':sha(ROOT/'inputs/01_F000_only_correct_pose.png'),
    'native_crop_xyxy':list(crop),'native_crop_size':list(native.size),
    'scale':4,'interpolation':'NEAREST exact pixel replication',
    'mirror':False,'rotation_degrees':0,'added_marks':False,'only_direct_enlargement':True}
(ROOT/'enlargement_transform.json').write_text(json.dumps(transform,ensure_ascii=False,indent=2)+'\n')

# QA-only evidence deliberately contains the rejected old pose. It is kept
# outside inputs/ and must never become a model reference.
clear=np.array(Image.open(OLD/'masks/clear_old_limb_occupancy.png'))==255
src=np.array(source);rgb=src[:,:,:3].astype(float)
edit_domain=np.array(Image.open(OLD/'masks/edit_white.png'))==255
# QA erasure also clears the small old upper-arm wedge immediately below the
# cuff. This is not a changed generation target or an expanded model mask.
skin_in_edit=((src[:,:,3]>0)&(rgb[:,:,0]>=175)&(rgb[:,:,0]>rgb[:,:,1]+25)
              &(rgb[:,:,1]>rgb[:,:,2]+12)&edit_domain)
skin_margin=np.array(Image.fromarray(np.where(skin_in_edit,255,0).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0
clear=(clear|skin_margin)&edit_domain
Image.fromarray(np.where(clear,255,0).astype('uint8')).save(ROOT/'masks_local/all_old_arm_clear_for_QA.png')
cleared=src.copy();cleared[clear]=0
assert not cleared[skin_in_edit,3].any()
Image.fromarray(cleared).save(ROOT/'qa_only/old_arm_occupancy_cleared_stage.png')
board=Image.new('RGB',(2140,720),'#f2f4f5');bd=ImageDraw.Draw(board)
for i,(title,im) in enumerate([
    ('仅QA：原错误臂链，不送模型',source),
    ('仅QA：清除旧臂，保原双掌/镯/前杆',Image.fromarray(cleared)),
    ('生成输入：正确完整双臂体量target',target),
]):
    x=20+i*705
    bd.text((x,20),title,font=small,fill='#263743')
    board.paste(gray(im).crop(crop).resize((690,500),Image.Resampling.NEAREST),(x,85))
bd.text((20,610),'左/中只用于清除核对；生成白名单完全排除call001/call002及所有旧臂对照图。',font=font,fill='#263743')
bd.text((20,660),'唯一姿态底是右图对应的1672×941完整target；不换掌、不换镯、不镜像、不缩放孩子。',font=small,fill='#263743')
board.save(ROOT/'qa_only/old_arm_removal_comparison.png')
gray(target).save(ROOT/'qa_only/only_correct_pose_full_gray.png')

roles=[
    ('01_F000_only_correct_pose.png','唯一完整姿态底：已清旧臂并置入正确连续双臂体量；完整两人原抓持关系'),
    ('02_target_shoulders_to_palms_4x.png','第一张同视角肩至双掌的直接4倍放大，无重画、无额外图或标记'),
    ('03_correct_arm_xray.png','正确双臂透衣体量：仅说明被躯干遮住的远R上臂和肘，成图不画透'),
    ('04_edit_white.png','单张1672×941编辑白域：白可改／黑保护'),
]
items=[]
for i,(name,role) in enumerate(roles,1):
    p=ROOT/'inputs'/name
    assert sha(p) not in [sha(RAW1),sha(RAW2)]
    items.append({'order':i,'relative_path':'inputs/'+name,'actual_local_path':str(p.resolve()),
        'role':role,'sha256':sha(p),'size':list(Image.open(p).size)})
payload={
    'status':'FINAL_FOUR_INPUTS_PREPARED_PENDING_ASTRA_INPUT_GATE',
    'submitted':False,'new_model_calls':0,'new_raws':0,'in_flight':0,
    'canvas':[1672,941],'inputs':items,
    'full_failed_raws_in_generation_references':False,
    'QA_comparison_in_generation_references':False,
    'unique_pose_input_sha256':sha(ROOT/'inputs/01_F000_only_correct_pose.png'),
    'final_four_image_boundary_applied':True,
    'extra_identity_material_reference_excluded':True,
    'inverse_protection_reference_excluded':True,
    'local_protection_source_only':{
        'path':'../generation_001/S20_F000_call001_raw.png','sha256':sha(RAW1),
        'passed_as_model_reference':False,'purpose':'post-return hard protection only'},
    'call002_preserved_unmodified':{'path':'../generation_002_arm_local/S20_F000_call002_arm_raw.png',
        'sha256':sha(RAW2),'actual_size':[1671,941],'passed_as_reference':False,'resized':False},
    'supplementary_boundary_received_and_applied':True,
}
(ROOT/'input_manifest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
delta=np.any(np.array(target)!=np.array(source),axis=2)
edit=np.array(Image.open(ROOT/'inputs/04_edit_white.png'))
assert not delta[edit==0].any()
assert not delta[:,:835].any()
print(json.dumps({'assets_prepared':len(items),'unique_pose':payload['unique_pose_input_sha256'],
    'raws_in_generation_references':False,'new_calls':0,'boundary_status':'FINAL_FOUR_APPLIED'},ensure_ascii=False))
