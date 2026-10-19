from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent
roles=[('01_F008_unique_opaque_pose_target.png','唯一完整新姿态：不透明新孩子体量；奶奶/四签/鞋踝原像素'),
       ('02_same_view_approach_3x.png','仅第一图指定裁片的同视角直接3倍放大'),
       ('03_head_identity_internal_materials.png','仅头部身份与内部布/肤/发裁片，不含旧全身或完整旧臂'),
       ('04_edit_white.png','唯一白可完稿/黑保护域；沿既批孩子域，另扣真实四签')]
prompt='''把第一张已经完整摆成S20 F008的新姿态自然完稿。第一张是唯一完整动作底：孩子旧低臂和旧躯干已全部清掉，现有不透明袖肩、完整上臂/肘/前臂、真实五指张掌，以及头颈胸骨盆和腿部支撑，就是本态必须保持的动作，不另起姿态。只将人工target的简化线条/布纹/肤肉接合整理成自然二维手绘，保持这张的新动作和原角色尺度。
第二张仅是第一张接近区的同视角直接3倍放大，没有另一套动作。第三张只有孩子头部身份与衣布/肤肉/头发的内部裁片，只参考造型与固有色；没有旧全身或完整旧手臂可照搬。第四张是唯一编辑白域，白可自然完稿、黑必须保持原RGBA，不反转语义。
孩子自身R为近臂，从新肩(611,417)沿肘(683.585,363.789)到腕(783,330)，空掌中心(806,318)，在龟头签T_H上侧接近；L为远臂，从肩(656,428)沿肘(719.015,468.671)到腕(814,467)，空掌中心(837,455)，从龟壳签T_S下侧接近。沿第一张完整新轮廓画自然袖根、上臂厚度、肘弯和连续腕掌，不拉长骨段、不只搬掌。每掌保真实拇指加四指的完整张开外轮廓；两掌及指尖与任一龟签都留可见空气隙，接触数0。不得改回母态双低掌、提前握签、用圆圈/骨线代替手或长出第三只手。头颈、胸廓、骨盆与下肢按第一张共同前倾，不独立缩放头或孩子。
奶奶整个人、高位带唯一玉镯的近L臂/掌和两鹤签、低位裸腕G.R持两龟签的掌、孩子原鞋踝全部保持第一张真实原像素，不重画奶奶，不为高鹤接景改灯或相机。四根竹签沿第一张真实原轴线与原握点保持；龟两签仍由奶奶R支持，孩子尚未碰到；不得折杆、合杆、改轴或改掌去迁就杆。
输出严格1672×941透明人物层，完整两人及四杆，原构图不裁切、不补边、不缩放。只完成本态白域，保持中性固有色和自然体积，不烘焙场景灯光，不画偶、场景、影子、文字、施工标记、骨架、剖面圈、旧姿态灰影或其他帧。'''
(P/'prompt_zh.txt').write_text(prompt+'\n')
rows=[]
for i,(name,role) in enumerate(roles,1):
 p=P/'inputs'/name;assert p.exists()
 rows.append({'order':i,'path':str(p.resolve()),'relative_path':'inputs/'+name,'role':role,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(Image.open(p).size)})
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]}
(P/'input_manifest.json').write_text(json.dumps({'status':'CORRECTED_FOUR_INPUTS_PREPARED_NOT_SUBMITTED',
 'image_model_calls_this_round':0,'new_raws':0,'in_flight':0,'old_full_mother_in_model_references':False,
 'old_gray_child_body_or_low_arms_in_target':False,'inputs':rows},ensure_ascii=False,indent=2)+'\n')
(P/'request_prepared.json').write_text(json.dumps({'tool':'image_gen.imagegen',
 'status':'PENDING_ASTRA_CORRECTED_INPUT_SHORT_GATE','submitted':False,'tool_args':args},ensure_ascii=False,indent=2)+'\n')
print('Four actual input PNGs and exact complete unsubmitted request prepared. 0 image calls.')
