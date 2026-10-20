"""Blocked F132 preflight evidence. Fixed128 is NEVER relabelled as132 art."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
F=Path(__file__).resolve().parent; P=F.parent
S=P/'F128_two_domains_close_zero_call_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((F/'mechanism/finite_F132_preflight.json').read_text())
probe=json.loads((F/'mechanism/source_model_probe.json').read_text())
cfg=json.loads((F/'scene_config_DIAGNOSTIC.json').read_text())
actual=json.loads((F/'actual_CAM20_132_geometry_DIAGNOSTIC.json').read_text())
previous=json.loads((S/'actual_CAM20_128_geometry.json').read_text())
assert actual['camera']==previous['camera'] and actual['people_to_CAM20']==previous['people_to_CAM20']
assert actual['pose']==probe['states']['132']['pose']
assert actual['root_input_baseline_established_this_gate']==d['root132_same_registration_plus_original128_to132_delta']
for row,base,calc in zip(actual['rods'],previous['rods'],d['rows']):
    for k in ['candidate_A_B_length_m','part','at','holder']:assert row[k]==base[k]
    assert abs(row['width_screen']-base['width_screen'])<1e-10
    for k in ['A_master','B_master','B_world']:assert row[k]==calc[k]
assert actual['finite_A_B_only'] and actual['external_handle_tail_m']==0
assert sha(F/'people_CAM20_132_RGBA.png')==sha(S/'people_CAM20_128_RGBA.png')
assert 'ERROR ' not in (F/'browser_console.log').read_text()
source=S/'F128_two_domains_closed_CANDIDATE.png'
assert sha(source)=='46294a1f899c2b80780ef26da2f632b7446a04636213ce28e56f2859cfaf5bcc'
im=Image.open(F/'CAM20_F132_mechanism_DIAGNOSTIC_fixed128_albedo.png').convert('RGB')
assert im.size==(1920,1080)
pm=np.array(actual['people_to_CAM20'])
screen=lambda p:(pm[:4].reshape(2,2).T@np.array(p)+pm[4:]).tolist()
# Above pm reshape is correct for original [a,b,c,d,tx,ty] canvas ordering.
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),22)
small=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),18)
diag=im.copy();draw=ImageDraw.Draw(diag)
draw.rectangle((0,0,1920,82),fill='#e4e8ec')
draw.text((20,10),'诊断：人物为锁定128原像素，只有龟偶/真有限杆取132；不是132人物目标',font=font,fill='#273644')
draw.text((20,43),'红圈＝132 T_H 所有同卡平面握点；青圈＝128投影肩肘腕掌长度和（非3D骨长认证）',font=small,fill='#273644')
circles=json.loads((F/'mechanism/all_possible_F132_B_circles.json').read_text())
draw.line([tuple(screen(q)) for q in circles['T_H']],fill='#d61f38',width=4)
chain=d['actual128_2D_chain_references'][0];sx,sy=screen(chain['shoulder']);radius=chain['sum_projected_arm_hand_reference_px']*pm[0]
draw.ellipse((sx-radius,sy-radius,sx+radius,sy+radius),outline='#0088b4',width=3)
points=[tuple(screen(chain[k])) for k in ['shoulder','elbow','wrist','grip']]
draw.line(points,fill='#0088b4',width=2)
for x,y in points:draw.ellipse((x-4,y-4,x+4,y+4),fill='#0088b4')
bp=np.array([screen(q) for q in circles['T_H']]).mean(0)
draw.text((int(bp[0])-85,int(bp[1])+24),'132 T_H B 全圈',font=small,fill='#b1132a')
draw.text((int(sx)+8,int(sy)-30),'128 R肩',font=small,fill='#006784')
diag.save(F/'DIAGNOSTIC_132_true_mechanism_fixed128_person_reach_1x.png')
diag.crop((250,500,1100,940)).save(F/'DIAGNOSTIC_R_reach_gap_normal_1x.png')
im.crop((230,550,1100,940)).save(F/'DIAGNOSTIC_132_finite_rods_fixed128_palms_normal_1x.png')
Image.open(F/'CAM20_F132_mechanism_DIAGNOSTIC_fixed128_actual.png').crop((230,550,1100,940)).save(F/'DIAGNOSTIC_actual_132_finite_rods_fixed128_palms_normal_1x.png')
shutil.copyfile(S/'actual_support_1x.png',F/'locked128_fixed_full_support_REFERENCE_1x.png')
# The sole reusable prospective image is identity only, no competing old arm
# pose. There is intentionally NO false132 target, contact or mask input.
I=F/'prepared_identity_only';I.mkdir(exist_ok=True)
A=Image.open(source).convert('RGBA');head=Image.open(S/'own128_complete_head_all_hair_one_scale_continuous_neck.png').convert('RGBA')
card=Image.new('RGB',(1080,640),'#e7ebee');cd=ImageDraw.Draw(card)
cd.text((16,12),'锁定128身份局部：供132待机构门后使用；无旧整臂/杆姿',font=small,fill='#263743')
parts=[(head,(560,140,845,450),(20,65),(285,310)),
       (A,(605,360,700,415),(370,90),(285,165)),
       (A,(650,570,850,650),(710,85),(300,120)),
       (A,(490,835,755,935),(350,380),(530,200))]
for src,box,xy,size in parts:
    patch=src.crop(box);bg=Image.new('RGBA',patch.size,'#bdc1c4');bg.alpha_composite(patch)
    card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
card.save(I/'03_locked128_identity_head_collar_cloth_shoes_ONLY.png')
prompt='''F132/5.5秒完成原龟偶翻肚，小满沿已锁128的惊讶抬视与后收收住双签，不续主动绞签、不换手端或偶端。R只握T_H、L只握T_S，完整肩肘腕掌连续，有真实固定下肢支持。保留已锁128整头颈身份体量与本次原生表情，不把头缩回旧小头，不分挪五官。完整新上身双臂双掌整裙自然重绘，固定完整裸腿鞋、奶奶/C不动；近腿既有横接痕保留，不扩成全人物修复。原龟和真长杆不生成，人物只含各自短接触段，灯光由场景接入。透明1672×941。
本草稿尚缺已通过的T_H→R可达接触方案和唯一完整132姿态；不得凭此草稿让模型猜动作。只有人物目标、同姿真实接触与完整mask通过下一门后，才能形成实际四输入参数。'''
(F/'prompt_DRAFT_BLOCKED_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
status={'status':d['status'],'submitted':False,'generation_authorized':False,'new_image_calls':0,
        'actual_callable_tool_args_prepared':False,'actual_args':None,
        'known_parameters':{'transparent_background':True,'output_canvas_requested':[1672,941]},
        'required_inputs':{'01_unique_complete132_target':None,'02_same_pose_actual132_contacts':None,
                           '03_identity_only':str((I/'03_locked128_identity_head_collar_cloth_shoes_ONLY.png').resolve()),
                           '04_complete_actual132_mask':None},
        'missing_requirement':d['specific_missing_gate'],
        'why_not_complete_args':'No valid132 contact/pose or complete mask exists. Do not submit an incomplete payload or feed fixed128 diagnostic as132 target.',
        '132_exposure_frozen':False,'later_states_opened':False}
(F/'REQUEST_PREPARATION_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
verification={'status':'F132_PREFLIGHT_EVIDENCE_SAVED_CONTACT_GATE_REQUIRED',
    'new_image_calls':0,'new132_character_poses_generated_or_faked':0,
    'actual_scene_diagnostic_frame':132,'diagnostic_person_pixels_exact_locked128':True,
    'original132_turtle_pose_and_original_root_delta_used':True,
    'original_turtle_scale_facing_and_card_registration_unchanged':True,
    'true_rods_A_B_length_width_camera_registration_preserved':True,
    'source128_endpoint_reproduction_error_less_than_px':1e-8,
    'complete_grip_circle_checked_not_only_nearest_branch':True,
    'R_2D_reference_reach_shortfall_px':chain['shortfall_with128_shoulder_and_projected_lengths_px'],
    'reference_bones_are_2D_not_universal3D_impossibility':True,
    'locked128_sha256':sha(source),'actual_scene_diagnostic_sha256':sha(F/'CAM20_F132_mechanism_DIAGNOSTIC_fixed128_actual.png'),
    'full_four_input_payload_ready':False,'submitted':False,'adopted':False,'exposure_frozen':False,'later_states_opened':False}
(F/'VERIFICATION.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(verification,ensure_ascii=False,indent=2))
