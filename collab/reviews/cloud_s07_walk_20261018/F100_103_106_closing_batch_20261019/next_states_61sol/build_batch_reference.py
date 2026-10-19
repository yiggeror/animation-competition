from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,hashlib,shutil
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'F100_next_gate_20261019';S=R/'sources';size=(1960,1080);s=.36410361842105265;off=np.array([627.0254537171638,402.7604324894813]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['sources','reference','qa','geometry','requests']:(R/d).mkdir(exist_ok=True)
needed=['F095_body_head_blouse.png','F095_far_complete_arm_jade_hand.png','F095_near_shoe_ankle_COLLECTED_LANDED.png','F095_far_shoe_ankle_SUPPORT_FIXED.png','F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png','F095_actual_preparation_metadata.json','existing_lamp_source_s08.js']
for n in needed:
 if not(S/n).exists():shutil.copyfile(OLD/'sources'/n,S/n)
# Exact existing prop function: separate its table-shadow command from object.
ss=(S/'existing_lamp_source_s08.js').read_text();fn=ss[ss.index('export function lamp('):ss.index('\n// 火苗',ss.index('export function lamp('))].replace('export function lamp(','function lamp(',1)
shadow="x.fillStyle = 'rgba(30,15,5,0.35)'; x.beginPath(); x.ellipse(0, 4, 230, 26, 0, 0, 7); x.fill();"
assert fn.count(shadow)==1
objfn=fn.replace(shadow,'/* Original table-shadow command separated; object commands unchanged. */')
for key,drawfn in [('object',objfn),('shadow','function lamp(x){x.save();x.translate(LX,LB);'+shadow+'x.restore();}')]:
 html='<!doctype html><html><style>*{margin:0}html,body{background:transparent;overflow:hidden}</style><canvas width="1960" height="1080"></canvas><script>const LX=1120,LB=950,LINE="#4a2e1f";'+drawfn+'\nconst x=document.querySelector("canvas").getContext("2d");x.setTransform(1/'+str(s)+',0,0,1/'+str(s)+',-'+str(off[0])+'/'+str(s)+',-'+str(off[1])+'/'+str(s)+');x.translate(1262,642);x.scale(-.17,.17);x.translate(-LX,-LB);lamp(x,0,false);</script></html>'
 (R/f'reference/existing_lamp_{key}_ONLY_source.html').write_text(html)
(R/'geometry/prop_source_split.json').write_text(json.dumps({'source':needed[-1],'sha256':sha(S/needed[-1]),'removed_exact_shadow_command':shadow,'object_design_changed':False,'same_scene_transform':{'world_lamp_at':[1262,642],'design_scale':[-.17,.17],'design_anchor':[1120,950],'native_world_scale':s,'native_world_offset':off.tolist()},'table_shadow_must_NOT_lift_with_object':True},indent=2)+'\n')
