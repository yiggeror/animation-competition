"""One next-state construction input, not production art; no image call."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
OLD=P/'next_036_058_inputs_001/F058';NEW=P/'adopt047_hold054_zero_call_001'
source=NEW/'F054_inherited047_candidate.png';childpath=P/'continuation_042_054_generation_001/F054/native_complete_child.png'
actual=Image.open(source).convert('RGBA'); child=np.array(Image.open(childpath).convert('RGBA'))
guide=np.array(Image.open(OLD/'inputs/01_unique_opaque_complete_target.png').convert('RGBA'))
A=np.array(actual);H,W=A.shape[:2];yy,xx=np.indices((H,W));assert guide.shape==A.shape
# Approved manual F058 construction, NOT scene-code motion and NOT final art.
# Its old technical grandmother is entirely replaced by the actual locked layer.
guide[:,835:]=A[:,835:];target=Image.fromarray(guide);target.save(I/'01_unique_F058_construction_locked_G.png')
box=(275,380,705,555);target.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).save(I/'02_same_view_first_X_3x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20)
card=Image.new('RGB',(1080,620),'#e7ebee');d=ImageDraw.Draw(card)
d.text((16,12),'054已锁实物：仅头颈身份、衣料与鞋样；不提供旧整身／旧掌姿势',font=font,fill='#263743')
for crop,xy,size in [((525,175,730,393),(20,60),(310,330)),((555,355,700,443),(360,65),(290,176)),((565,550,715,665),(690,65),(300,230)),((490,835,735,925),(360,350),(490,180))]:
    q=actual.crop(crop);bg=Image.new('RGBA',q.size,'#bdc1c4');bg.alpha_composite(q);card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,570),'白圆领／密集乳白圆点／红搭带露趾凉鞋；施工图圆肩与封闭鞋为示意，必须自然新绘',font=font,fill='#263743')
card.save(I/'03_054_identity_and_material_patches_only.png')
edit=((guide[:,:,3]>0)|(child[:,:,3]>0))&(xx<810)
edit&=~((xx>705)&(yy<335))
edit=binary_dilation(edit,iterations=10)&(xx<810)
edit|=(xx>215)&(xx<550)&(yy>350)&(yy<530)
Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'04_child_and_T_rods_only_white.png')
bg=Image.new('RGBA',target.size,'#bdc1c4');bg.alpha_composite(target);bg.convert('RGB').save(F/'target_full_gray_REVIEW_ONLY.jpg',quality=96)
contract=json.loads((OLD/'contact_contract.json').read_text())
contract['hand_chain_construction']={k:v for k,v in contract['hand_chain_construction'].items() if k.startswith('X.')}
contract['crane_axis_gate']='Use final lower-only+2 CAM20 packet ff5f2618; this input retains locked047 people/grip axes, no further prop/camera adjustment.'
contract.update({'status':'ONE_F058_ACTUAL_INPUT_PREPARED_ONLY_ASTRA_INPUT_GATE_PENDING','generation_authorized':False,'image_model_calls':0,'frozen_grandma_source_commit':'7f8857523dd15f255ad1f42a815da5a65fbb3994','frozen_grandma_RGBA_x835_plus_equal_locked':True,'predecessor':'054 complete native anticipation child; approved047 grandma inherited','old_F058_technical_grandma_removed':True,'whole_child_must_be_new_native_drawing':True,'technical_ball_joints_closed_shoes_sparse_dots_must_not_be_copied':True,'not_new_exposure_schedule':True})
(F/'contact_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
prompt='''只制作F058第一次绞签这一张。第一图是已批准动作协议的完整新施工target，小满体块仅说明新姿态；右侧奶奶是已锁真实原层。第二图为第一图同机位接触放大，第三图仅054实物头颈身份和衣鞋材质，第四图白域可新绘、黑域严格保护。不要把施工圆肩、球肘、简略掌、封闭鞋或稀疏点纹照抄为成品。
小满双脚支撑，骨盆/胸廓/整头颈延续054蓄势，肩—肘—完整前臂—腕一起内收；手前的两根硬直龟签第一次形成X，T_S近、T_H远，前臂彼此分开不互绕。角色自身R始终夹T_H turtle.head[20,0]，L始终夹T_S turtle.shell[0,40]，不因杆交叉交换偶端或手别。施工夹点R约(450,448)、L约(487,489)，杆前端T_H约(300,465)、T_S约(300,425)。两掌均一拇四指，拇指与食指真正相向夹住同一硬杆，其余三指自然卷曲，掌厚和完整腕臂连续；必须新绘完整小满原生双臂/双掌，不能把旧拳头贴回新臂。
完整小满从头到脚自然手绘，保持054实际儿童比例、原骨长、支持点与左侧面身份，不拉长骨头、不只扭脸。白色彼得潘圆领、黄泡袖连衣裙、密集乳白圆点、红搭带露趾凉鞋必须按第三图实物，深棕发红花双马尾与中性肤色一致。原场景灯光之后接入，不烘焙光条。奶奶蓝花宽短袖、整头、双臂及五指、玉镯、真C_N/C_B杆全部原样保持黑域，特别是已过047上杆对夹及下杆尾端净空不可改变。不要重生奶奶、047掌腕或045。
输出单张1672×941透明人物层，同画布同站位，不裁切缩放，不加骨架、圆圈、文字、背景、地影、额外杆或额外帧。第一图施工体块仅作新姿态输入，不能作为最终绘图交付。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
paths=[I/n for n in ['01_unique_F058_construction_locked_G.png','02_same_view_first_X_3x.png','03_054_identity_and_material_patches_only.png','04_child_and_T_rods_only_white.png']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[{'order':i+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(paths)]
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]}
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
assert np.array_equal(guide[:,835:],A[:,835:]); assert not np.any(edit[:,810:])
manifest={'status':'PREPARATION_ONLY_NO_REQUEST_NO_NEW_RAW','frame':58,'new_image_calls':0,'submitted':False,'generation_authorized':False,'inputs':rows,'predecessor054_file':str(source),'predecessor054_sha256':sha(source),'frozen054_child_sha256':sha(childpath),'construction_source':str(OLD/'inputs/01_unique_opaque_complete_target.png'),'construction_source_sha256':sha(OLD/'inputs/01_unique_opaque_complete_target.png'),'old_scene_code_motion_used':False,'new_frozen_G_exact':True,'requires_explicit_new_generation_gate':True,'further_frames_prepared':False}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('F058 only: four real prepared input PNGs, unique target + same-view crop + material-only + mask; no request, no image call')
