"""Prepare an unsubmitted local edit request and deferred same-raw contracts."""
from pathlib import Path
from PIL import Image, ImageFilter
from collections import deque
import hashlib, json
import numpy as np

ROOT=Path(__file__).resolve().parent
rawpath=ROOT.parent/'generation_001/S20_F000_call001_raw.png'
raw=np.array(Image.open(rawpath).convert('RGBA'))
alpha=raw[:,:,3]
outside=np.ones(alpha.shape,dtype=bool)
outside[30:930,450:1245]=False
near_strong=np.array(Image.fromarray(np.where(alpha>=2,255,0).astype('uint8')).filter(ImageFilter.MaxFilter(7)))>0
candidates=(alpha==1)&outside&~near_strong
seen=np.zeros_like(candidates)
isolated=np.zeros_like(candidates)
groups=[]
for sy,sx in zip(*np.where(candidates)):
    if seen[sy,sx]:continue
    todo=deque([(int(sy),int(sx))]);seen[sy,sx]=True;points=[]
    while todo:
        y,x=todo.popleft();points.append((y,x))
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                ny,nx=y+dy,x+dx
                if 0<=ny<941 and 0<=nx<1672 and candidates[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;todo.append((ny,nx))
    if len(points)<=4:
        for y,x in points:isolated[y,x]=True
    groups.append(len(points))
Image.fromarray(np.where(isolated,255,0).astype('uint8')).save(ROOT/'masks/deferred_isolated_alpha1_only.png')
def write(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
write('postprocess_contract.json',{
    'applied_this_round':False,'core_arm_edit_mask_does_not_include_neck_or_background_cleanup':True,
    'neck':{'mode':'deferred semantic same-raw dewarming','preserve':['alpha','ink lines','face and neck structure','natural form shadows'],
            'not_permitted':'broad warm-color threshold across clothing/skin; no image regeneration for this step',
            'current_target_neck_pixels':'unchanged original'},
    'alpha1':{'outside_subject_region_xyxy':[450,30,1245,930],
              'original_alpha1_outside_count':int(((alpha==1)&outside).sum()),
              'eligible_isolated_point_pixels':int(isolated.sum()),
              'eligible_mask':'masks/deferred_isolated_alpha1_only.png',
              'rule':'Only alpha==1 outside subject region, farther than 3px from alpha>=2 and in 8-connected candidate groups of at most4 pixels.',
              'candidate_component_sizes':sorted(groups),
              'must_preserve':'hair strands, all four thin rods and their antialias; never broad alpha cutoff',
              'current_target_cleanup_applied':False},
    'canvas':[1672,941],'auto_crop':False,
    'child_size':{'keep_original_pixels':True,'scale_or_translation_applied':False,
                  'reported_child_adult_height_ratio':0.82,'construction_ratio':0.88,
                  'ratio_is_not_a_new_size_lock':True,'defer':'unified registration / actualCAM20 review'},
})

prompt='''仅对第一张《来电》S20 F000唯一原件作奶奶双臂的局部解剖纠正。输出仍为1672×941透明RGBA；不裁切、不镜像、不缩放任何角色。小满、奶奶头/脸/颈、腰部以下、两只持杆掌的中心与握指、唯一玉镯，以及四根竹签的前段位置和轴线，全部沿原件保持。

第二张是逐像素叠在原件上的连续体量target，只规定完整臂链、遮挡和接腕；其简化平色/花纹不是新的美术风格。第三张黑白图中白域可修、黑域保护。第四张的白域是保护域，和第三张互为反相。第五张是透明前衣层的双臂体量透视参考，完整露出被遮的远R上臂与肘；虚线、字母/标签、灰透视层只用于说明，禁止画进人物层，禁止多画手臂。

必须纠正的归属：奶奶解剖左臂L为近臂，从画面右侧近肩及近短袖真实接出上臂，经过近肘，再由前臂斜向左上接到原高位带绿玉镯的掌，掌仍握C_N、C_B两鹤签。奶奶解剖右臂R为远臂，从画面左侧远肩、远短袖后方接出，上臂和肘被躯干前衣层遮挡，前臂从躯干左缘伸到原低位裸腕掌，掌仍握T_H、T_S两龟签。R完整臂体必须在躯干后连续存在；不能从衣襟凭空冒腕。只画因正确遮挡而可见的部分，不把X光图的隐藏上臂/肘画透到成图上。

严格维持四手四杆关系：高掌及玉镯不移动到另一手；低掌不抬高；两掌不互换。禁止只换手镯、换色、镜像或改标签来假冒纠正。重画完整双肩袖→上臂→肘→腕的连接，使近L在躯干前、远R在躯干后，实际腕宽/掌厚与肩袖连续。两只原持杆掌的指杆接触继续成立，不另造手指或重复掌。

低位两龟签的前段原轴保持。原图掌后两根外露短尾向下偏离前段轴，必须去掉。按原前段外推，在x960时T_H约y462.53、T_S约y458.66；本target让两根正确杆端结束于原掌遮挡内，不补外露尾。绝不沿原来的y470–476错尾再画，也不把竹杆折弯接尾。高位两鹤签与原掌接触不变。

把target的平色体量转成原件二维手绘风格的自然布袖、肤肉、肘腕体积，参考原件线条和蓝白小花布纹；补回旧错臂移走后的衣服/透明空隙，不能留下旧臂双边、透明裂缝、截面圈或接片方台阶。奶奶头颈和小满完全不重画，孩子两掌仍然空起，接触数0。全图仍仅奶奶与小满各一人、四根竹签，不添加偶、场景、灯光、影子、文字或施工标识。

本轮核心只修双臂归属与错尾。颈侧减暖与主体外孤立alpha1清理留给后续同raw显式语义处理，不在本次模型请求扩大白域，不用全局阈值伤及细杆/发丝AA。孩子与成人高度比不在这里校正，保持孩子原像素，等待统一注册核验。仅输出这一张F000局修结果，禁止后态。'''
(ROOT/'prompt_local_edit_zh.txt').write_text(prompt+'\n')
paths=[rawpath,ROOT/'S20_F000_arms_target.png',ROOT/'masks/edit_white.png',
       ROOT/'masks/protect_white.png',ROOT/'full_arm_volume_xray.png']
roles=['原件，唯一身份/画布/既有手掌/四前杆像素源','连续双臂target，施工参考非完成图',
       '白可修/黑保护的局部编辑域','白保护/黑可修的保护域','完整双臂体量；远R上臂肘透衣显示，仅用于遮挡说明']
inputs=[]
for i,(p,role) in enumerate(zip(paths,roles),1):
    assert p.exists()
    inputs.append({'order':i,'actual_local_path':str(p.resolve()),
                   'relative_to_pack':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else '../generation_001/'+p.name,
                   'role':role,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                   'size':list(Image.open(p).size)})
write('input_manifest.json',{'status':'PENDING_ASTRA_LOCAL_CORRECTION_INPUT_GATE','submitted':False,
                             'new_image_generation_calls':0,'in_flight':0,'inputs':inputs})
write('request_prepared.json',{'tool':'image_gen.imagegen','submitted':False,'attempts_this_round':0,
    'requires_next_Astra_input_gate':True,'not_reserved_for_execution':True,
    'args':{'prompt':prompt+'\n','transparent_background':True,
            'referenced_image_paths':[str(p.resolve()) for p in paths]},
    'mask_api_note':'Tool exposes reference images, no separate hard-mask argument. The two masks are references; any future returned raw must be composited only through edit_white to retain protected original bytes.',
    'post_return_contract':'Do not accept full-pair resampling. Verify dimensions before local white-mask composite; outside white must be exact original RGBA; no automatic retries.'})
write('status.json',{'state':'STATIC_ARM_TARGET_READY_PENDING_ASTRA_GATE','source_commit':'300840f48aaa8fec60f2392bc16beb28e0a963e1',
                     'source_raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),
                     'new_model_calls':0,'new_generated_raws':0,'in_flight':0,'historical_model_calls':1,
                     'historical_raws':1,'later_pose_calls':0,'production_ready':False,'submitted':False,
                     'original_author_pass_superseded_by_Astra_near_far_arm_rejection':True})
print(json.dumps({'new_model_calls':0,'prepared_reference_count':len(inputs),
                  'source_alpha1_outside':int(((alpha==1)&outside).sum()),
                  'isolated_alpha1_candidates':int(isolated.sum()),'postprocess_applied':False},ensure_ascii=False))
