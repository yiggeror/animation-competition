"""Prepare opaque reference inputs only. Finished drawings must be actual model output."""
from pathlib import Path
import json,hashlib,sys,ast,math,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
P=Path(__file__).resolve().parent; PACK=P.parent; OLD=PACK/'handoff_008_020_032_generation_002'
f=int(sys.argv[1]);assert f in [12,15,18]
F=P/f'F{f:03}';I=F/'inputs';ART=F/'art';Q=F/'qa'
for x in [F,I,ART,Q]:x.mkdir(exist_ok=True)
shift={12:(-10,2),15:(-5,1),18:(-1,0)}[f];dx,dy=shift
base=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][1]['state']
def ik(S,W,a,b,upper):
 S=np.array(S,float);W=np.array(W,float);v=W-S;d=np.linalg.norm(v);assert abs(a-b)<d<a+b
 t=(a*a-b*b+d*d)/(2*d);h=math.sqrt(a*a-t*t);u=v/d;n=np.array([-u[1],u[0]])
 candidates=[S+t*u+h*n,S+t*u-h*n];return min(candidates,key=lambda p:p[1]) if upper else max(candidates,key=lambda p:p[1])
g=dict(base)
for side,a,b in [('R',90,105),('L',75,95)]:
 S=np.array(base[side+'_chain'][0],float);W=np.array(base[side+'_chain'][2],float)-shift
 palm=np.array(base[side+'_palm'],float)-shift
 if f==12 and side=='L':W=np.array([814,467],float)-shift;palm=np.array([837,455],float)-shift
 E=ik(S,W,a,b,side=='R');g[side+'_chain']=[S.tolist(),E.tolist(),W.tolist()];g[side+'_palm']=palm.tolist()
# Reuse a proven local target authoring procedure in an isolated namespace. It
# reads only locked source; all products below go to this new Fxxx directory.
src=(OLD/'prepare_F020.py').read_text()
src=src.replace("P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F020';I=F/'inputs';ART=F/'art'","P=OLD;F=NEWF;I=F/'inputs';ART=F/'art'")
src=src.replace("g=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][1]['state']","g=NEWG")
# Import only pure hand function definitions from the earlier input authoring tool.
tree=ast.parse((PACK/'F008_corrected_input_001/prepare_target.py').read_text())
pure='\n'.join(ast.get_source_segment((PACK/'F008_corrected_input_001/prepare_target.py').read_text(),n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['finger','hand'])
if f==12:
 marker="header=f'<svg"
 src=src.replace(marker,pure+'\n'+marker)
 src=src.replace("closed_hand(g['L_chain'][2],g['L_palm'])","hand(g['L_chain'][2],g['L_palm'],True)")
if f==15:
 # First opposition: thumb not yet fully wrapped; four fingers visibly begin curling.
 src=src.replace("def closed_hand(wrist,palm):","def closed_hand(wrist,palm,partial=False):")
 src=src.replace("z+=path('M8 -7 C12 -24 30 -23 34 -13 Q38 -9 34 -3 L24 4 Q16 12 10 5 Z',SKIN,sw=1.25)","z+=path(('M8 -7 C10 -23 20 -30 28 -26 Q33 -23 28 -18 L21 -10 Q16 -1 10 5 Z' if partial else 'M8 -7 C12 -24 30 -23 34 -13 Q38 -9 34 -3 L24 4 Q16 12 10 5 Z'),SKIN,sw=1.25)")
 src=src.replace("closed_hand(g['L_chain'][2],g['L_palm'])","closed_hand(g['L_chain'][2],g['L_palm'],True)")
ns={'__file__':str(OLD/'prepare_F020.py'),'OLD':OLD,'PACK':PACK,'NEWF':F,'NEWG':g}
exec(compile(src,'isolated_reference_builder','exec'),ns)
# Whole head/neck/chest/pelvis advances together in the input, never a face warp.
for name in ['child_F020_complete_pose.svg','closed_hand_coverage.svg']:
 p=ART/name;s=p.read_text();end=s.index('>')+1;s=s[:end]+f'<g transform="translate({dx} {dy})">'+s[end:];s=s.replace('</svg>','</g></svg>');p.write_text(s)
(F/'geometry.json').write_text(json.dumps({'frame':f,'body_translation_from020_target':list(shift),'world_chains':{k:(np.array(v)+shift).tolist() for k,v in g.items() if k.endswith('_chain')},'source_locked008_sha256':hashlib.sha256((OLD/'F008/S20_F008_accepted.png').read_bytes()).hexdigest(),'input_only_not_drawing':True},indent=2)+'\n')
print('Input SVG only prepared for',f)
