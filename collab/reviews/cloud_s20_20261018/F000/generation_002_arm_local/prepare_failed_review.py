"""Preserve a failed single edit and make QA evidence. Never composite or retry."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
import base64, hashlib, json, struct

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'S20_F000_call002_arm_raw.png'
data=RAW.read_bytes()
assert data[:8]==b'\x89PNG\r\n\x1a\n'
png_size=list(struct.unpack('>II',data[16:24]))
assert png_size==list(Image.open(RAW).size)==[1671,941]
returned=json.loads((ROOT/'tool_return_original.json').read_text())
assert base64.b64decode(returned['image_url'].split(',',1)[1])==data
sha=hashlib.sha256(data).hexdigest()
assert sha=='9f8edf0f17d5aac7ec425bb74258e168a80f0aad096c56a3efd4f307b6ce98bf'

def gray(path):
    im=Image.open(path).convert('RGBA')
    bg=Image.new('RGBA',im.size,(140,140,140,255));bg.alpha_composite(im)
    return bg.convert('RGB')

old=ROOT.parent/'generation_001/S20_F000_call001_raw.png'
gate=ROOT.parent/'arm_correction_001'
target=gate/'S20_F000_arms_target.png'
board=Image.new('RGB',(2140,690),'#f3f4f5');d=ImageDraw.Draw(board)
font_path=ROOT.parents[4]/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(font_path),26)
small=ImageFont.truetype(str(font_path),22)
box=(875,235,1220,485)
for i,(title,path) in enumerate([
    ('call001：原错误臂链',old),
    ('已审target：近L高掌／远R低掌',target),
    ('call002：仍为原错误臂链，未通过',RAW),
]):
    x=20+i*705
    d.text((x,20),title,font=small,fill='#9f3133' if i==2 else '#263743')
    # Same nominal coordinate crop; enlargement is QA only, no registration
    # or size correction is applied to the raw / any character output.
    board.paste(gray(path).crop(box).resize((690,500),Image.Resampling.NEAREST),(x,75))
d.text((22,592),'尺寸门失败：实际PNG 1671×941，冻结画布1672×941。未缩放、未补列、未按白域回贴。',font=font,fill='#9f3133')
d.text((22,638),'原件保留；仅此一次局修，无重试。颈色、孤立alpha与后态均未开放。',font=small,fill='#263743')
board.save(ROOT/'qa/approved_target_vs_failed_raw.png')

def write(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

review={
    'reviewed_utc':datetime.now(timezone.utc).isoformat(),
    'raw_sha256':sha,'source_gate_commit':'5ce9da50b92eac9062e808a335c4f0b2f5b08995',
    'outcome':'FAIL_NEAR_FAR_ARM_OWNERSHIP_AND_CANVAS_WIDTH_NO_COMPOSITE',
    'actual_views_inspected':['qa/raw_shoulders_to_palms_3x_QA.png',
        'qa/raw_high_wrist_to_far_sleeve_3x_QA.png',
        'qa/raw_low_wrist_to_near_sleeve_3x_QA.png',
        'qa/approved_target_vs_failed_raw.png'],
    'acceptance_checks':{
        'near_L_from_near_shoulder_to_high_bracelet_palm':False,
        'far_R_from_far_shoulder_to_low_bare_wrist':False,
        'canvas_exactly_1672x941':False,
    },
    'observations':[
        '高位带镯掌仍通过前臂接到躯干远侧；近侧短袖/上臂/肘仍接低位裸腕掌。',
        '原错误整条臂链仍保留，没有实现target的近L高掌、远R低掌替代连接；不把它登记为仅有少量旧臂残影。',
        'PNG IHDR和Pillow独立读数均为1671×941；宽度少1列，不能假定缺列位置或自动补列/缩放注册。',
        '模型raw未注册且未合成，不称孩子/两掌/玉镯/四前杆与源逐像素保真。所有冻结源和输入原字节均保留。',
    ],
    'white_mask_composite_executed':False,'composite_output_exists':False,
    'raw_resized_padded_cropped_or_edited':False,
    'neck_or_alpha_cleanup_applied':False,'new_model_calls':1,'new_raws':1,
    'cumulative_model_calls':2,'cumulative_raws':2,'in_flight':0,'retries':0,
    'later_pose_calls':0,'production_ready':False,
    'cause_limits':'Only observed failure is recorded; model internals and the reason for the one-column width discrepancy are unknown.',
}
write('author_visual_review.json',review)
write('dimension_inspection.json',{
    'expected':[1672,941],'PNG_IHDR':png_size,'Pillow':list(Image.open(RAW).size),
    'match':False,'width_difference':-1,'auto_resize':False,'pad':False,
    'crop':False,'registration_assumed':False,
})
status=json.loads((ROOT/'status.json').read_text())
status.update(state='REJECTED_LOCAL_ARM_EDIT_NO_COMPOSITE',in_flight=0,new_raws=1,
    author_review=review['outcome'],acceptance_passed=False,production_ready=False,
    white_mask_composite_executed=False,composite_output_exists=False,
    retries=0,later_pose_calls=0,neck_or_alpha_cleanup_applied=False)
write('status.json',status)
print(json.dumps({'raw_sha256':sha,'image_acceptance':'FAIL',
    'PNG_IHDR':png_size,'white_mask_composite_executed':False,
    'local_edit_calls':1,'cumulative_calls':2,'in_flight':0,'retries':0},ensure_ascii=False))
