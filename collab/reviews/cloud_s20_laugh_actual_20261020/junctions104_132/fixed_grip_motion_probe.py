from pathlib import Path
import ast,json,math,numpy as np
from scipy.optimize import root
P=Path('collab/reviews/cloud_s20_laugh_actual_20261020');helper=P/'continuation036057/prepare.py';tree=ast.parse(helper.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='old_c' for t in node.targets):break
 prefix.append(node)
ns={'__file__':str(helper.resolve()),'__name__':'junction_geometry_helpers'};exec(compile(ast.Module(body=prefix,type_ignores=[]),str(helper),'exec'),ns)
Q=json.loads((P/'junctions104_132/model_probe.json').read_text())['states'];card,on_sheet,master=map(ns.get,['card','on_sheet','master'])
g128=json.load(open('assets/chars/g20/F128_geometry.json'));mapping=json.load(open('assets/chars/g20/child132_CONSUMER_MAPPING.json'));B=np.array([r['end_world'] for r in g128['rods']]);L=np.array([r['length_m'] for r in g128['rods']]);rows=[];prior=np.array(g128['turtle']['root'])
for f in range(128,133):
 st=Q[str(f)]
 def residual(v):return [np.linalg.norm(on_sheet(card(v,st['points'][role]))-b)-length for role,b,length in zip(['T_H','T_S'],B,L)]
 fits=[]
 for x in [prior,[1.8,.75],[2,.8],[1.7,.8],[2,1],[1.8,1]]:
  fit=root(residual,x)
  if fit.success and np.linalg.norm(residual(fit.x))<1e-7 and np.linalg.norm(fit.x-prior)<.6:fits.append(fit)
 if fits:
  fit=min(fits,key=lambda r:np.linalg.norm(r.x-prior));prior=fit.x
  rows.append({'frame':f,'fixed128GripPhysicalLengthsFeasible':True,'root':fit.x.tolist(),'rootAngle':st['pose']['rootAngle'],'residual_m':residual(fit.x),'A_master':[master(card(fit.x,st['points'][role])).tolist() for role in ['T_H','T_S']]})
 else:rows.append({'frame':f,'fixed128GripPhysicalLengthsFeasible':False,'bestResidual_m':min(np.linalg.norm(root(residual,x).fun) for x in [[1.8,.75],[2,.8],[1.7,.8],[2,1],[1.8,1]])})
(P/'junctions104_132/fixed_grip_motion_feasibility.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
