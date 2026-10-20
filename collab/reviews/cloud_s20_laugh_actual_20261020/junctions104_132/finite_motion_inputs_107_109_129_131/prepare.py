"""Unique prop/hand inputs, original paper motion only; never paints people."""
from pathlib import Path
import ast,json,math,numpy as np
from scipy.optimize import minimize
P=Path(__file__).resolve().parent;R=P.parents[1];helper=R/'continuation036057/prepare.py'
tree=ast.parse(helper.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='old_c' for t in node.targets):break
 prefix.append(node)
ns={'__file__':str(helper),'__name__':'finite_input_helpers'};exec(compile(ast.Module(body=prefix,type_ignores=[]),str(helper),'exec'),ns)
card,on_sheet,master,project=[ns[k] for k in ['card','on_sheet','master','project']]
Q=json.load(open(R/'junctions104_132/model_probe.json'))['states'];g120=json.load(open('assets/chars/g20/F120_geometry.json'));late=json.load(open('assets/chars/g20/child132_CONSUMER_MAPPING.json'));g128=json.load(open('assets/chars/g20/F128_geometry.json'));frozen=json.load(open('assets/chars/g20/frozen_stage.json'));crane=json.load(open('assets/chars/g20/closure_CHARACTER_AND_RODS.json'))['rods'];native={s['key']:s for s in json.load(open(R/'front058131/native_contact_measurements.json'))};offset=np.array(g120['turtle']['root'])-Q['120']['root'];lengths=[r['rod_length_m'] for r in late['finite_T_rods']]
basis=ns['b'];C,right,up,fwd=[np.array(basis[k]) for k in ['C','right','up','fwd']];focal=basis['focal'];pm=ns['pm']
def rayFor(p):
 pix=np.array([pm[0]*p[0]+pm[2]*p[1]+pm[4],pm[1]*p[0]+pm[3]*p[1]+pm[5]])
 return fwd+right*((pix[0]-960)/focal)+up*((540-pix[1])/focal)
def lineDistance(a,p):
 ray=rayFor(p);v=C-a;return math.sqrt(max(0,v@v-(v@ray)**2/(ray@ray)))
def candidates(a,p,length):
 ray=rayFor(p);v=C-a;aa=ray@ray;bb=2*(ray@v);cc=v@v-length*length;disc=bb*bb-4*aa*cc;assert disc>=-1e-10
 return [C+ray*((-bb+s*math.sqrt(max(0,disc)))/(2*aa)) for s in [-1,1]]
def fixedEnd(a,goal,length):return a+length*(goal-a)/np.linalg.norm(goal-a)
ends={};correction={};boundaries={}
for f in [104,112]:
 st=Q[str(f)];ref=np.array(st['root'])+offset;grips=[r['observedClamp'] for r in native[f]['axes']]
 def constraints(rt):return np.array([length-.003-lineDistance(on_sheet(card(rt,st['points'][role])),grip) for role,grip,length in zip(['T_H','T_S'],grips,lengths)])
 fit=minimize(lambda rt:np.sum((rt-ref)**2),ref,method='SLSQP',constraints={'type':'ineq','fun':constraints},bounds=[(ref[0]-.2,ref[0]+.2),(ref[1]-.2,ref[1]+.2)],options={'ftol':1e-13,'maxiter':200});assert fit.success
 rt=fit.x;correction[f]=rt-ref;arr=[]
 for role,grip,length,old in zip(['T_H','T_S'],grips,lengths,g120['rods']):
  a=on_sheet(card(rt,st['points'][role]));can=[b for b in candidates(a,grip,length) if b[1]>.004];assert can;arr.append(min(can,key=lambda b:abs(b[1]-old['end_world'][1])))
 ends[f]=arr;boundaries[str(f)]={'root':rt.tolist(),'originalRootOffset':offset.tolist(),'additionalMinimalRootCorrection':correction[f].tolist(),'unchangedNativeGripMaster':grips,'B_world':[b.tolist() for b in arr]}
cn=crane[1];cnA=np.array(cn['A_world']);cnL=cn['fixedLengthMetres'];oldCN=next(r['grip_master_px'] for r in frozen['geometry']['rod_endpoints'] if r['id']=='C_N');cnStart=min([b for b in candidates(cnA,oldCN,cnL) if b[1]>.004],key=lambda b:np.linalg.norm(b-np.array(cn['end_world'])));states=[]
for f in list(range(104,113))+list(range(128,133)):
 st=Q[str(f)]
 if f<=112:
  u=(f-104)/8;u=u*u*(3-2*u);rt=np.array(st['root'])+offset+(1-u)*correction[104]+u*correction[112];goals=[(1-u)*a+u*b for a,b in zip(ends[104],ends[112])];cnB=cnStart
 else:
  u=(f-128)/4;u=u*u*(3-2*u);rt=np.array(st['root'])+offset;goals=[(1-u)*np.array(a['end_world'])+u*np.array(b['B_world']) for a,b in zip(g128['rods'],late['finite_T_rods'])];cnB=fixedEnd(cnA,(1-u)*cnStart+u*np.array(cn['end_world']),cnL)
 rods=[]
 for role,goal,length in zip(['T_H','T_S'],goals,lengths):
  a=on_sheet(card(rt,st['points'][role]));b=fixedEnd(a,goal,length);rods.append({'id':role,'holder':'X.R' if role=='T_H' else 'X.L','part':'head' if role=='T_H' else 'shell','at':[20,0] if role=='T_H' else [0,40],'A_world':a.tolist(),'B_world':b.tolist(),'A_master':master(project(a)).tolist(),'B_master':master(project(b)).tolist(),'A_CAM20':project(a).tolist(),'B_CAM20':project(b).tolist(),'length_m':length,'length_error_m':abs(float(np.linalg.norm(b-a))-length),'diameter_m':.007})
 for r,b in [(crane[0],np.array(crane[0]['end_world'])),(cn,cnB)]:
  a=np.array(r['A_world']);rods.append({'id':r['id'],'holder':'G.R' if r['id']=='C_B' else 'G.L','A_world':a.tolist(),'B_world':b.tolist(),'A_master':master(project(a)).tolist(),'B_master':master(project(b)).tolist(),'A_CAM20':project(a).tolist(),'B_CAM20':project(b).tolist(),'length_m':r['fixedLengthMetres'],'length_error_m':abs(float(np.linalg.norm(b-a))-r['fixedLengthMetres']),'diameter_m':.007})
 state={'frame':f,'time_seconds':f/24,'turtle':{'root':rt.tolist(),'pose':st['pose'],'scale':1.3},'crane':{'root':frozen['geometry']['crane_root_m'],'pose':frozen['geometry']['puppet_poses']['crane'],'scale':1.35},'rods':rods};states.append(state)
 if f in [107,109,129,131]:(P/f'F{f:03}_CAM20_FINITE_INPUT.json').write_text(json.dumps(state,indent=2)+'\n')
# Existing native screen palms stay fixed. Existing128/132 finite endpoints
# remain exact; only the four previously undrawn poses receive new grips.
for f in [104,112]:
 state=next(s for s in states if s['frame']==f)
 for r,grip in zip(state['rods'][:2],boundaries[str(f)]['unchangedNativeGripMaster']):assert np.linalg.norm(np.array(r['B_master'])-grip)<1e-8
for f,sources in [(128,g128['rods']),(132,late['finite_T_rods'])]:
 for r,src in zip(next(s for s in states if s['frame']==f)['rods'][:2],sources):assert np.linalg.norm(np.array(r['B_world'])-src.get('end_world',src.get('B_world')))<1e-8
assert max(r['length_error_m'] for s in states for r in s['rods'])<1e-8
manifest={'status':'UNIQUE_AUTHOR_INPUT_FINITE_GEOMETRY_NOT_SCENE_ACCEPTANCE','camera':late['camera'],'canvas':[1920,1080],'masterCanvas':[1672,941],'peopleRegistration':late['people_billboard_registration'],'masterToCAM20':late['master_to_original_CAM20'],'requestedFrames':[107,109,129,131],'source':'Original turtleState motion only, no old poseX/poseG people rig. Constant root offset is the adopted120/128/132 registration, not arbitrary AH.','104_112':'Both existing native palm projections preserved to1e-8px. Earlier billboard B depths were not frozen. Solve actual behind-sheet endpoints on their unchanged rays with the same .218644/.255042m physical rods;112 paper root gets the least movement needed for reach with3mm clearance. The current arbitrary-AH104/112 prop registrations are superseded as reference, native people remain unchanged.','intermediatePath':'Use original paper angles/internal motion. Interpolate boundary root-registration correction with smoothstep. Interpolate B world goals, then constrain each new B to its fixed-radius sphere about the true same-card A. This creates new hand targets only for not-yet-drawn poses; it never moves an existing source palm or changes rod length.','128_132':'Exact original approved flip angles/positions plus adopted constant root offset.128 and132 world endpoints/lengths remain exact. C_B stays atR; C_N follows a fixed-length direction arc from oldL screen grip to adopted enteringL. No early secure doublehold orLrelease.','depthContract':'Actual B depth is explicit in each input. Native front thumb/fingers must occlude the rod within the grip; the earlier flat whole-people depth approximation cannot override these physical hand depths. Actual scene occlusion remains integration work.','exposure':'Four requested drawing instants; this is not a frozen new whole-shot exposure table. No new180, audio orEDL changes.','boundaries104112':boundaries,'states':states};(P/'FINITE_MOTION_INPUTS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('PASS:14 physical samples,4 requested inputs; fixed lengths, unchanged104/112 palms, exact128/132 endpoints.')
