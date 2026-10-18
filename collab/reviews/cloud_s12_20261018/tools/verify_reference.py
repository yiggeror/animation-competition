from pathlib import Path
import json,csv,hashlib,subprocess,numpy as np
from scipy.spatial import ConvexHull
from PIL import Image
H=Path('collab/reviews/cloud_s12_20261018');G=json.loads((H/'geometry/three_key_pose_proposal.json').read_text());S=G['states'];L=G['bone_lengths_H'];SC=G['head_unit_scene_pixels']
rows=[(0,12,'首态：低跪俯身，两手张开靠近双签，未握','A'),(12,6,'远左手向neck3上签推进',''),(18,4,'远肘在躯干外，腕与掌跟进',''),(22,4,'左拇指接近上签',''),(26,4,'左食指包拢，不先抬鹤',''),(30,4,'左掌闭合，仍由布托鹤',''),(34,6,'上签已握，先抬高杆柄分上下手；鹤仍在布上',''),(40,8,'上签柄到位；近手启动，下签仍由箱沿托住',''),(48,4,'近右前臂前送向body下签',''),(52,4,'右拇指到杆侧',''),(56,4,'右食指包拢，腕不落躯干',''),(60,4,'下签完整闭合，不额外抬肘',''),(64,6,'双签轻预紧；鹤仍受箱内布托','B'),(70,6,'髋向膝上推进，胸廓随起',''),(76,6,'脊柱回正，双肩同走',''),(82,6,'整躯干起，双掌跟握点，不拉臂',''),(88,6,'跪姿回直；膝胫不离地',''),(94,4,'鹤根抬离箱沿遮挡区',''),(98,4,'鹤颈与腿按真实铆点展开',''),(102,4,'领颈/头随胸回正，双杆不伸缩',''),(106,4,'鹤片转向灯，真实平面转立',''),(110,4,'透光彩影初读；约4.583秒',''),(114,6,'举鹤关键：躯干回直，双签/鹤同稳','C'),(120,6,'约5秒轻提/轻晃；握点随整臂微调',''),(126,6,'小幅回落到持稳位',''),(132,12,'控制动作落定，不循环晃',''),(144,24,'柔和得意，看向画右画外小满',''),(168,24,'末停；新画微小整体落定，不代码呼吸','')]
assert len(rows)==28 and sum(r[1] for r in rows)==192
out=[]
for i,(start,hold,beat,key) in enumerate(rows):assert start==sum(r[1] for r in rows[:i]);out.append({'id':f'd{i+1:02d}','start':start,'hold':hold,'end_inclusive':start+hold-1,'beat':beat,'key_reference':key,'status':'TIMING_PROPOSAL_NOT_DRAWN'})
with (H/'exposure_192f_PROPOSAL.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
(H/'geometry/exposure_plan.json').write_text(json.dumps({'status':'PENDING_ASTRA_REFERENCE_AND_TIMING_FREEZE_NO_IMAGEGEN','fps':24,'frames':192,'duration':8,'proposed_drawing_states':28,'constructed_key_references_only':['A/F000','B/F064','C/F114'],'no_other25_pose_references_claimed':True,'rows':out},ensure_ascii=False,indent=2)+'\n')
def p(s,k):return np.array(s['points_H'][k])
def v(s,k):return np.array(s['points_scene'][k])
qa=[]
for s in S:
 errors=[]
 for role in ['R','L']:
  for a,b,k in [('shoulder','elbow','upper_arm'),('elbow','wrist','forearm'),('hip','knee','femur'),('knee','ankle','tibia')]:errors.append(abs(np.linalg.norm(p(s,a+role)-p(s,b+role))-L[k]))
  if s['id']!='A':errors.append(abs(np.linalg.norm(p(s,'grip'+role)-p(s,'wrist'+role))-L['wrist_to_grip']))
 assert max(errors)<1e-10
 # Projected forearm surfaces: conservative subtract both largest radii.
 aa=v(s,'elbowR')[None,:]+np.linspace(0,1,501)[:,None]*(v(s,'wristR')-v(s,'elbowR'))
 bb=v(s,'elbowL')[None,:]+np.linspace(0,1,501)[:,None]*(v(s,'wristL')-v(s,'elbowL'))
 centre=float(np.min(np.linalg.norm(aa[:,None,:]-bb[None,:,:],axis=-1)));gap=centre-(.095+.09)*SC;assert gap>15,(s['id'],gap)
 elbows=float(np.linalg.norm(v(s,'elbowR')-v(s,'elbowL')));assert elbows>80
 rrs=[];col=[]
 if s['id']!='A':
  for role,endpoint in [('R','P_body'),('L','P_neck')]:
   rrs.append(abs(np.linalg.norm(p(s,endpoint)-p(s,'grip'+role))-s['rod_lengths_H'][role]));g=v(s,'grip'+role);P=v(s,endpoint);W=v(s,'wrist'+role);col.append(float(abs((P-g)[0]*(W-g)[1]-(P-g)[1]*(W-g)[0])/np.linalg.norm(P-g)))
  assert max(rrs)<1e-10 and max(col)<1e-10
 # Explicit approximate mass proxy, not a dynamics certificate.
 torso=(p(s,'hip')+p(s,'shoulder_mid'))/2;armcentre=np.mean([p(s,x+r) for r in ['R','L'] for x in ['shoulder','elbow','wrist']],axis=0);legcentre=np.mean([p(s,x+r) for r in ['R','L'] for x in ['hip','knee','ankle']],axis=0)
 com=.14*p(s,'hip')+.42*torso+.10*p(s,'head_center')+.10*armcentre+.24*legcentre
 support=np.array([[-.75,-.5],[.74,-.5],[.74,.5],[-.75,.5]]);inside=bool(-.75<com[0]<.74 and -.5<com[2]<.5);assert inside
 qa.append({'state':s['id'],'bone_max_abs_error_H':max(errors),'projected_forearm_conservative_surface_gap_scene_px':gap,'projected_elbow_distance_scene_px':elbows,'rod_length_abs_error_H':rrs,'projected_rod_wrist_grip_collinearity_residual_px':col,'mass_proxy_H':com.tolist(),'mass_proxy_inside_approx_support_region':inside,'mass_model_note':'illustrative14/42/10/10/24 percent hip/torso/head/arms/legs,not physical human dynamics validation','knees_Y_H':[p(s,'kneeR')[1],p(s,'kneeL')[1]],'kneepads_radius_H':.12,'shin_axis_Y_H':.12,'shin_radius_H':.12,'shoe_bottom_Y_H':0})
# Frozen no-contact A hands; same free rods asB; grasp starts in actual later exposure.
G['states'][0]['free_rod_grip_points_H']={r:S[0]['points_H']['free_grip'+r] for r in ['R','L']};G['states'][0]['rod_lengths_H']=S[1]['rod_lengths_H'];G['geometry_notes']=['Head units and bone lengths derive from actual03manual measurements,not humanrealworldcentimetres','A hands open;both free rods rest on proposed left rim contacts,not suspended;Rnear/无镯 vsLfar/玉镯 fixed','B/C hand grasp centersfixedlocal.23Hfromwrist along rod;no wrist-as-grasp shortcut','body local[-75,6] and neck3local[10,0] derived with actualmakeCrane(1.35) +solve/pointOn','Initial crane foldedneck+legs slants55deg overcloth;proposal deliberately replaces oldpixel-squash;literalflatlying needs Astra disposition','All colored people volumesareconstruction,never productionart.Only puppet PNGs areactualexistingcodeprop renders.']
(H/'geometry/three_key_pose_proposal.json').write_text(json.dumps(G,ensure_ascii=False,indent=2)+'\n')
(H/'qa/geometry_and_exposure_validation.json').write_text(json.dumps({'status':'REFERENCE_CONSTRUCTION_NUMERIC_GATES_PASS_PENDING_ASTRA_VISUAL_FREEZE','states':qa,'duration_frames':192,'fps':24,'exposure_sum':sum(r['hold'] for r in out),'exposure_rows':28,'key_references':3,'new_character_images_generated':0,'image_tool_calls':0,'code_prop_extraction_calls':1,'actual_scene_render_frames':0,'unvalidated':'No actualhandanatomy/nativecharacteracceptance;no final scene or light/shadowrender;no entire28poseconstruction or bone tests for unbuiltstates.'},ensure_ascii=False,indent=2)+'\n')
files=['collab/README.md','collab/claude.md','collab/partner.md','docs/keyframes/scenes03_12_drawing_plan.md','docs/preproduction/script-v3.md','docs/preproduction/floorplan.md','js/film/edl.js','js/paint/shots/s12.js','js/lamp/crane.js','js/lamp/choreo.js','js/puppet.js','assets/chars/g12_box_crane.png','collab/refs/anim_12_grandma_box_crane.png','collab/refs/grandma_turnaround_current03_draft.png','collab/refs/grandma_turnaround_current04_draft.png','collab/refs/grandma_expressions_current02.png']
manifest=[]
for n in files:
 pp=Path(n)
 if not pp.exists():continue
 b=pp.read_bytes();assert b==subprocess.check_output(['git','show','aa397e44887e47d395b699fdba92cbd7795a9001:'+n]);r={'path':n,'sha256':hashlib.sha256(b).hexdigest(),'fixed_commit':'aa397e44887e47d395b699fdba92cbd7795a9001','git_blob':subprocess.check_output(['git','rev-parse','aa397e44887e47d395b699fdba92cbd7795a9001:'+n],text=True).strip()}
 if n.endswith('.png'):
  with Image.open(pp) as im:r.update(size=list(im.size),mode=im.mode)
 manifest.append(r)
(H/'provenance/source_manifest.json').write_text(json.dumps({'identity_working_basis':'03,not latest04;per partner.md2732review and later2865/2878notes','sources':manifest,'scope':'S12reference only;no production/sharedfileedits'},ensure_ascii=False,indent=2)+'\n')
for pp in list((H/'reference').glob('*.png'))+list((H/'reference').glob('*.jpg')):
 with Image.open(pp) as im:im.verify()
print('PASS3keys fixedbones/rods,gaps',[(r['state'],round(r['projected_forearm_conservative_surface_gap_scene_px'],2)) for r in qa],'exposure28sum192;source manifest',len(manifest))
