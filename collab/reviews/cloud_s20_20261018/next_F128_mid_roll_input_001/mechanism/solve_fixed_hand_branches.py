"""Diagnostic alternative roots only; not selected128 character inputs."""
from pathlib import Path
import runpy,json
import numpy as np
from scipy.optimize import root
F=Path(__file__).resolve().parent;c=runpy.run_path(str(F/'solve_constraints.py'))
M=json.loads((F/'constraint_preflight.json').read_text());raw=c['raw1'];card=c['cardpoint'];ray=c['rayplane'];master=c['master'];pins=c['pins'];hand=c['handworld'];ids=c['ids'];lengths=[r['rigid_rod_length_m'] for r in M['rows']];hands=[hand(p) for p in pins]
def error(rt):return [np.linalg.norm(ray(card(rt,raw['points'][id]))-b)-length for id,b,length in zip(ids,hands,lengths)]
solutions=[]
for dx in [-.4,0,.4]:
 for dz in [-.4,0,.4]:
  s=root(error,np.array(M['root120_registered_from_passed_axes'])+[dx,dz])
  if not(s.success and np.linalg.norm(error(s.x))<1e-7):continue
  if any(np.linalg.norm(s.x-np.array(q['root']))<=.001 for q in solutions):continue
  a=[master(card(s.x,raw['points'][id])) for id in ids];v=pins[0]-a[0];w=pins[1]-a[1];t,u=np.linalg.solve(np.column_stack([v,-w]),a[1]-a[0]);x=a[0]+t*v
  solutions.append({'root':s.x.tolist(),'A':[q.tolist() for q in a],'X':x.tolist(),'params':[float(t),float(u)],'R_X':float(np.linalg.norm(x-pins[0])),'L_X':float(np.linalg.norm(x-pins[1])),'error':error(s.x)})
result={'status':'F128_PUPPET_ROOT_IK_BRANCHES_WITH_EXACT_FIXED_A_B_LENGTHS_AND_UNCHANGED_120_GRIPS','solutions':solutions}
(F/'fixed_hand_inverse_branches.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'diagnostic_roots':len(solutions),'adopted':False}))
