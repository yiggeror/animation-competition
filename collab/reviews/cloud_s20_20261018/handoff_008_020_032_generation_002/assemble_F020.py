from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F020';I=F/'inputs';Q=F/'qa'
info=json.loads((F/'source_and_geometry.json').read_text());source=Path(info['source_actual_F008'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==info['source_actual_sha256']
A=np.array(Image.open(source).convert('RGBA'));C=np.array(Image.open(F/'art/child_F020_complete_pose.png').convert('RGBA'))
hand=np.array(Image.open(F/'art/closed_hand_coverage.png').convert('RGBA'))[:,:,3]>0
rod=np.array(Image.open(PACK/'F008_corrected_input_001/local_masks/protect_four_real_rods.png'))>0
old=np.array(Image.open(PACK/'handoff_008_020_032_reference_001/F020/04_edit_white.png'))>0
M=old&(~rod|binary_dilation(hand,iterations=1))
out=A.copy();out[M]=C[M];out[805:,525:662]=A[805:,525:662]
assert not np.any(out[~M]!=A[~M]) and not np.any(out[:,885:]!=A[:,885:])
Image.fromarray(out).save(I/'01_F020_unique_opaque_target_from_accepted008.png')
Image.fromarray((M*255).astype('uint8')).save(I/'04_edit_white.png')
Image.fromarray((hand*255).astype('uint8')).save(F/'art/actual_target_hand_coverage.png')
box=(565,280,1005,505);im=Image.fromarray(out)
im.crop(box).resize((1320,675),Image.Resampling.NEAREST).save(I/'02_same_view_grips_3x.png')
bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg.convert('RGB').save(Q/'opaque_target_full_gray.png')
bg.crop(box).resize((1760,900),Image.Resampling.NEAREST).convert('RGB').save(Q/'grips_target_4x.png')
g=info['frozen_F020_geometry']
for side in ['R','L']:
 for s,e in zip(g[side+'_chain'],g[side+'_chain'][1:]):
  for t in np.linspace(.05,.95,31):
   x,y=np.rint(np.array(s)+(np.array(e)-s)*t).astype(int);assert C[y,x,3]>=250,(side,x,y)
prompt='''将第一张完整的新F020共同承重姿态自然完稿为与第三张已通过008实物一致的二维手绘风格。第一张是本态唯一完整动作底：它从已通过008实物的头部身份、固有色、奶奶/四签/鞋踝原像素派生，孩子完整肩袖—上臂—肘—前臂—腕和两只真实屈指握掌已按已批020骨点摆好；没有旧双低掌或旧灰体。不得改回008空手或母态。第二张只把第一张接握区直接3倍放大，第三张只含已过008的头部和内部材质裁片，不含完整旧臂/旧全身。第四张白可完稿、黑须原RGBA保留；黑白语义不反转。
本态F020共同承重：孩子自身近R肩(631,409)→肘(696.374,347.143)→腕(797,377.132)，掌中心(820,365.132)，拇指对屈曲食/中指真实夹住龟头签T_H；远L肩(676,429)→肘(740.326,467.564)→腕(827,428.673)，掌中心(850,416.673)，拇指对屈曲四指真实握住龟壳签T_S。两根各有独立掌内接触段，指腹形成对握，竹签从掌两侧沿同一直轴接出；不能只把闭拳贴杆、用圆圈夹杆或让裸杆穿掌面。五指体积与关节真实，近远臂各完整接回自己的肩，禁止多臂、断腕或拉长骨段。头颈、胸廓、骨盆按第一张共同靠近，鞋踝固定，角色尺度不变。
奶奶低位裸腕G.R仍闭合支持两龟签后端，绝不提前松手。孩子R只接T_H，L只接T_S；T_H=龟head[20,0]，T_S=龟shell[0,40]，不换轴/偶端或合成一根。奶奶整个人、高位带唯一玉镯近L掌和两鹤签、低位供应掌、原鞋踝及黑域竹签原像素保持，不重画奶奶，不为高鹤远端接景改高握臂、灯或相机。
保持第一张已具备的自然完整体量，把简化施工线条和色面转成自然衣褶、肤肉和真实指掌；不改姿态、不照搬技术几何。输出严格1672×941透明人物层，只这一时刻、两人四杆；无文字、骨架、圆掌/剖面、灰影、偶、场景、灯光、影子或额外帧；不裁切、补边、缩放。'''
roles=[('01_F020_unique_opaque_target_from_accepted008.png','unique new opaque F020 pose, derived from actual accepted008'),('02_same_view_grips_3x.png','exact same-view direct crop3x'),('03_accepted008_head_materials_only.png','accepted008 cropped identity and internal materials only'),('04_edit_white.png','single editable white, black source protection')]
rows=[]
for n,(name,role) in enumerate(roles,1):
 f=I/name;rows.append({'order':n,'path':str(f.resolve()),'sha256':sha(f),'size':list(Image.open(f).size),'role':role})
args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]}
(F/'prompt_prepared_zh.txt').write_text(prompt+'\n');(F/'tool_args_prepared.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(F/'input_manifest.json').write_text(json.dumps({'inputs':rows,'source_accepted_F008_sha256':sha(source),'frozen_geometry_commit':'c1b1833b7dfe806ae2daa1b84ddacfb804070f3d','authority':'Astra: after actual corrected008 passes, derive020 then032 from accepted actual; no extra states','submitted':False},ensure_ascii=False,indent=2)+'\n')
print('F020 four actual inputs complete. Shared-load target opaque, source-protected, actual008-derived; no model call yet.')
