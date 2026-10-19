"""Write the final four-image preparation only. Never invoke image generation."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'input_manifest.json').read_text())
assert len(manifest['inputs'])==4
prompt='''把第一张已有正确臂链自然完稿。仅将奶奶双臂及肩袖处的平色施工体量转成与第一张其余部位一致的二维手绘线条、蓝白花布、肤肉与自然体积，保持这张已有的正确姿态、人物身份和抓持关系。

第一张是唯一完整姿态底，画布1672×941。第二张只是第一张肩到双掌的同视角直接4倍放大，没有新增姿态。第三张是正确双臂透衣体量，只说明被遮挡的远臂如何连续接到肩和肘；成图按第一张的正常遮挡画，不画透衣、隐藏臂、虚线或施工标记。第四张是唯一白域mask：白色可完稿，黑色必须保持；没有另一套相反黑白语义。

近L从画面右侧近肩与近短袖接上臂，经近肘，前臂斜向左上接已有高位带绿色玉镯的掌，仍握两鹤签。远R从画面左侧远肩后方接出，上臂和肘藏在躯干前衣层后，前臂伸到已有低位裸腕掌，仍握两龟签。沿第一张的完整臂链完成肩袖切入、上臂厚度、肘弯与腕掌过渡，衣肉相接自然，去掉平块和接片台阶。

两只持杆掌、握指、唯一玉镯、四根前杆的原位置和接触完全保持；两根低位龟签的正确末端藏在掌内，不另添外露尾，不折杆或分叉。全图只有奶奶与小满各一人、现有四杆。小满两掌空起且零接触，整个人和原尺寸不改；奶奶头脸颈、腰腿脚不改，不换掌、不换镯、不镜像。原头身及相对站位保持，不作新的比例或机位注册。

输出严格为1672×941透明人物层，不裁切、不补边、不缩放任何角色，不改构图或镜头。只完成白域内已有正确双臂，保持中性固有色；不画场景、灯光、影子、偶、文字、重复手臂或后续姿态。颈侧色彩和主体外孤立alpha清理留待后续同raw检查，本次不处理。'''
(ROOT/'prompt_zh.txt').write_text(prompt+'\n')
paths=[x['actual_local_path'] for x in manifest['inputs']]
for item,path in zip(manifest['inputs'],paths):
    assert Path(path).parent==ROOT.resolve()/'inputs'
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==item['sha256']
request={
    'tool':'image_gen.imagegen','submitted':False,'attempts_this_round':0,
    'reserved_for_execution':False,'requires_Astra_final_four_input_gate':True,
    'args':{'prompt':prompt+'\n','transparent_background':True,'referenced_image_paths':paths},
    'input_count':4,'no_last_conversation_images':True,
    'excluded_reference_categories':['call001 full raw','call002 full raw','old-arm comparison images',
        'inverse protection image','identity/material crops'],
    'single_mask_reference_semantics':'fourth image: white editable, black protected',
    'service_mask_limit':'Tool exposes reference images, not a hard-mask parameter; local protection still required after any authorized return.',
}
(ROOT/'request_prepared.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
contract={
    'source_for_protected_pixels':'../generation_001/S20_F000_call001_raw.png',
    'source_sha256':'de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330',
    'passed_to_model':False,
    'editable_mask':'inputs/04_edit_white.png',
    'local_inverse_protection_mask':'masks_local/protect_white.png',
    'inverse_mask_passed_to_model':False,
    'preserve_exactly':['two original holding palms/fingers','single jade bracelet','four front rod segments',
        'complete Xiaoman pixels and size','grandma head/face/neck/waist/legs/feet','camera and object-holder mapping'],
    'before_any_local_composite':['require exact1672x941; no scaling, padding or cropping',
        'inspect nearL/high bracelet palm and farR/low bare palm complete shoulder-to-wrist chains',
        'inspect old arm traces, duplicate edges, wrist joins and natural form',
        'only use editable white; outside white exact originalRGBA'],
    'do_not_use_call002_as_registration_source':True,'call002_size':[1671,941],
    'neck_or_alpha_cleanup_this_round':False,'later_poses_opened':False,
}
(ROOT/'local_protection_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
directives={
    'source_thread_id':'01a0fbb9-4718-7063-bf5b-9bf34d41700f',
    'initial_new_scheme':'从输入里彻底移除带旧双臂的call001/call002；唯一姿态底为已清旧臂、保原双掌/镯/四前杆及完整正确双臂体量的target；原raw只在本地作最终保护像素源；0新调用先输入门。',
    'final_supplement_supersedes_identity_crops':'新输入精简为4图：①唯一正确全图target，②该target同视角肩到双掌直接放大，③正确双臂透衣体量，④单张白域mask。反相保护图留本地验收不送。prompt首句改为把第一张已有正确臂链自然完稿；第二只是放大、第三隐藏臂不画透。不要任何带旧完整臂链的原件；保两掌镯四杆仍取call001原像素。先输入门，不立刻重试。',
    'canvas':[1672,941],'new_calls_authorized':0,
}
(ROOT/'review_directives.json').write_text(json.dumps(directives,ensure_ascii=False,indent=2)+'\n')
status={'state':'FINAL_FOUR_CORRECT_ONLY_INPUTS_PENDING_ASTRA_GATE','new_model_calls':0,
    'new_raw_outputs':0,'in_flight':0,'historical_model_calls':2,'historical_raws':2,
    'submitted':False,'reserved_for_execution':False,'input_count':4,
    'final_supplement_applied':True,'old_full_arm_raws_excluded':True,
    'inverse_mask_and_identity_crops_excluded':True,'later_pose_calls':0,
    'production_ready':False,'target_is_construction_reference_only':True}
(ROOT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'prepared_refs':4,'prompt_first_sentence':prompt.split('。')[0]+'。',
    'submitted':False,'new_calls':0,'old_raws_or_inverse_in_references':False},ensure_ascii=False))
