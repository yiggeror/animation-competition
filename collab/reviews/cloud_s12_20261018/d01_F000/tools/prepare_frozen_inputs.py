from pathlib import Path
import ast,json,hashlib,subprocess,shutil,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path.cwd();P=R/'collab/reviews/cloud_s12_20261018';O=P/'d01_F000';I=O/'inputs';I.mkdir(parents=True);(O/'provenance').mkdir();(O/'qa').mkdir();(O/'tools').mkdir();(O/'originals').mkdir();(O/'candidate').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[R/'collab/refs/grandma_turnaround_current03_draft.png',P/'reference/S12_A_F000_volume_contact.jpg']
assert sha(refs[0])=='ab88b69f5303229af379303a37b6e9e3c8cdb35cd05b3902b604871efb2b1671'
G=json.loads((P/'geometry/three_key_pose_proposal.json').read_text());A=G['states'][0]
# Only reuse approved construction drawing functions; do not execute reference module's file writes.
src=(P/'tools/build_reference.py').read_text();tree=ast.parse(src);names=['proj','pnt','uv','surface','ell','basis','limb','draw_person','hand'];fns=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
ca,sa,cb,sb=np.cos(np.deg2rad(12)),np.sin(np.deg2rad(12)),np.cos(np.deg2rad(15)),np.sin(np.deg2rad(15))
from scipy.spatial import ConvexHull
ns={'np':np,'Image':Image,'ImageDraw':ImageDraw,'ConvexHull':ConvexHull,'SC':215.,'ca':ca,'sa':sa,'cb':cb,'sb':sb,'colors':{'R':(233,151,86,255),'L':(100,176,199,255)}}
exec(compile(ast.Module(body=fns,type_ignores=[]),'approved-construction-functions-only','exec'),ns)
scene=Image.new('RGBA',(1920,1080),(0,0,0,0));ns['draw_person'](scene,A);d=ImageDraw.Draw(scene)
for role in ['L','R']:ns['hand'](d,A,role)
# Reference only: inverse of approved proposed placement, never a character deliverable.
layout=scene.transform((1024,1536),Image.Transform.AFFINE,(.75,0,300,0,.75,100),Image.Resampling.BICUBIC)
d=ImageDraw.Draw(layout);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25);d.text((45,70),'CONSTRUCTION ONLY - NOT CHARACTER ART',font=font,fill='#354353');d.text((45,108),'S12 F000 / open empty hands / full kneel',font=font,fill='#354353');layout.save(I/'A_F000_native_layout_CONSTRUCTION_NOT_ART.png')
refs.insert(1,I/'A_F000_native_layout_CONSTRUCTION_NOT_ART.png')
# Source-only midtone swatches; masks intentionally exclude ink and white floral motifs.
im=np.array(Image.open(refs[0]).convert('RGB'));regions={
 'hair':((455,25,613,101),lambda a:(np.max(a,2)-np.min(a,2)<28)&(np.min(a,2)>120)&(np.max(a,2)<225)),
 'blouse_blue':((445,225,628,430),lambda a:(a[:,:,2]>a[:,:,0]+15)&(a[:,:,0]>70)&(a[:,:,1]>110)&(a[:,:,2]<240)),
 'skin':((400,335,430,445),lambda a:(a[:,:,0]>220)&(a[:,:,0]>a[:,:,1]+20)&(a[:,:,1]>a[:,:,2]+10)),
 'trousers':((443,470,625,690),lambda a:(np.max(a,2)<110)&(np.min(a,2)>25)&(a[:,:,2]>a[:,:,0]))}
col={}
for name,(box,fn) in regions.items():
 a=im[box[1]:box[3],box[0]:box[2]].astype(np.int16);mask=fn(a);v=a[mask];col[name]={'source_crop':box,'pixels':int(mask.sum()),'mean_RGB':v.mean(0).tolist(),'median_RGB':np.median(v,axis=0).tolist(),'note':'material midtone subset,not whole semantic region and not a generated-frame colour gate'}
(I/'03_midtone_reference.json').write_text(json.dumps(col,ensure_ascii=False,indent=2)+'\n')
rows=[{'path':str(p.relative_to(R)),'sha256':sha(p),'role':'identity03' if i==0 else 'construction_only_pose' if i==1 else 'approved_A_scene_context_not_art'} for i,p in enumerate(refs)]
for p in [P/'geometry/three_key_pose_proposal.json',P/'geometry/contact_shadow_anchor_proposal.json',P/'geometry/scene_integration_interface_PROPOSAL.json']:
 rows.append({'path':str(p.relative_to(R)),'sha256':sha(p),'role':'frozen09c6reference'})
(I/'frozen_inputs.json').write_text(json.dumps({'reference_commit':'09c6a981b83a4300021ad053713d5cb846326edf','identity_source_commit':'aa397e44887e47d395b699fdba92cbd7795a9001','rows':rows,'native_canvas':[1024,1536],'scene_registration':{'scale':.75,'x':300,'y':100},'only_pose_to_generate':'F000','no_batch':True,'A_native_points':{k:[(v[0]-300)/.75,(v[1]-100)/.75] for k,v in A['points_scene'].items() if k not in ['P_body','P_neck','crane_root','free_gripR','free_gripL','rim_contactR','rim_contactL']}},ensure_ascii=False,indent=2)+'\n')
(O/'provenance/astra_F000_authorization.md').write_text('''Astra source thread: 01a0fbb9-4718-7063-bf5b-9bf34d41700f

“S12三关键已实际看：A低跪未握、B双掌分杆、C整身回直举鹤，近远臂/膝胫支撑可进入首母。55°初鹤斜靠布我同意作本镜技术构造：重读script-v3，第4场的‘平放’是在说明旧稿透光错误，现要求是‘拿起鹤的身子对着马灯举起来’，没有强制初始绝对0°。条件：初态由布真实承托、两签箱沿支托，未举向灯前不出透色；不缩扁鹤、不改箱/相机，B握住后才举；末微推脚16px余量仅数值，首图必须全膝胫鞋和真实影接景验。请先S24修后60f，随后S12仅F000一张首母，按03身份/既定色基和A体量、双手未握；不提前批28图。”

本轮按09c6a981参考冻结首母输入，仅F000；不批量后态，不改共享文档/生产/EDL/音轨。
''')
print(json.dumps({'frozen_references':rows[:3],'source_midtone_samples':col},ensure_ascii=False,indent=2))
