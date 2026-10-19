"""Concise input gate: source bytes, complete requests and construction feasibility only."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();g=json.loads((O/'geometry/contact_segment.json').read_text());fixed='2c265ea885f956e15915cede73288c5c4d0f33f6';source=S/'d03_F018_20261019/same_raw_fix_20261019/candidate/F018.png';assert source.read_bytes()==subprocess.check_output(['git','show',fixed+':'+source.relative_to(R).as_posix()],cwd=R);assert (O/'inputs/01_locked_F018.png').read_bytes()==source.read_bytes()
upper=[np.array(g['upper_rod_native'][x]) for x in ['start','end']];lower=[np.array(g['lower_rod_native'][x]) for x in ['start','end']]
def gap(points,radii,a,b):
 p=np.array(points);rr=np.array(radii);v=b-a;t=np.clip(((p-a)@v)/(v@v),0,1);return float(np.min(np.linalg.norm(p-(a+t[:,None]*v),axis=1)-rr-5.-1.1)*.7)
def pathgap(path,radii,rod):
 values=[]
 for p,q,r1,r2 in zip(path,path[1:],radii,radii[1:]):
  u=np.linspace(0,1,101);points=np.array(p)+(np.array(q)-p)*u[:,None];rr=r1+(r2-r1)*u;values.append(gap(points,rr,*rod))
 return min(values)
rows=[]
for st in g['stages']:
 f=st['frame'];req=json.loads((O/f'requests/F{f:03d}_NOT_EXECUTED.json').read_text());args=req['tool_arguments'];assert req['execution_enabled'] is False and req['hold']==4 and req['end_inclusive']==f+3;assert len(args['referenced_image_paths'])==3 and args['transparent_background'] is True and args['prompt']==(O/f'prompts/F{f:03d}.txt').read_text() and sha(O/f'prompts/F{f:03d}.txt')==req['prompt_SHA256'];assert set(args)=={'prompt','referenced_image_paths','transparent_background'}
 for row,pstr in zip(req['input_SHA256'],args['referenced_image_paths']):
  p=Path(pstr);Image.open(p).load();assert sha(p)==row['sha256'] and p.relative_to(R).as_posix()==row['path']
 lo=[];hi=[]
 for j,path in enumerate(st['digits']):
  radius=[6.2-j*.35,5.8-j*.35,5.-j*.3,4.6-j*.27];lo.append(pathgap(path,radius,lower))
  if f==22 or(f==26 and j>0):hi.append(pathgap(path,radius,upper))
 lo.append(pathgap(st['thumb'],[7,6.8,6.3,6],lower));assert min(lo)>=3.8
 if hi:assert min(hi)>=4.
 thumb=np.array(st['thumb'][-1]);us,ue=upper;v=ue-us;u=((thumb-us)@v)/(v@v);thumb_tangent=abs(np.linalg.norm(thumb-us-u*v)-5.-6.);assert thumb_tangent<1e-10
 palm=np.linalg.norm(np.array(st['digits'][0][0])-st['W']);assert 75<=palm<=86
 assert max(abs(st['bone_lengths_native_depth_proxy']['upper']-.86*293),abs(st['bone_lengths_native_depth_proxy']['forearm']-.64*293))<1e-9
 bound=max(pt[0]+r for j,path in enumerate(st['digits']) for pt,r in zip(path,[6.2-j*.35,5.8-j*.35,5.-j*.3,4.6-j*.27]));assert bound<1012
 rows.append({'frame':f,'hold':4,'construction_lower_rod_all_digits_min_air_scene':min(lo),'construction_noncontact_digits_upper_min_air_scene':min(hi) if hi else None,'thumb_same_G_tangent_error_native':float(thumb_tangent),'palm_W_to_indexMCP_native':float(palm),'prompt_SHA256':req['prompt_SHA256']})
paths=[x[3:] for x in subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=R).decode().splitlines()];assert all(x.startswith(O.relative_to(R).as_posix()+'/') for x in paths)
report={'status':'PASS_INPUT_REFERENCE_GATE_ONLY','mother_commit':fixed,'mother_SHA256':sha(source),'actual_tool_inputs_per_request':3,'ordered_batch':[22,26,30],'holds':[4,4,4],'all_three_execution_disabled':True,'imagegen_calls':0,'scene_renders':0,'construction_only_not_future_actual_image_acceptance':True,'rows':rows};(O/'INPUT_GATE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
