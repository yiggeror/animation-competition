"""Consume the coordinator's15 existing drawings in the original CAM20.
No generated people, no body transform, no input-guide clamp substitution.
"""
from pathlib import Path
import ast,copy,hashlib,io,json,math,subprocess
import numpy as np
from PIL import Image
from scipy.optimize import root
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,binary_dilation,label
P=Path(__file__).resolve().parent
helper=P.parent/'continuation036057/prepare.py'
# Reuse only the pure source/camera helpers, before the six-state preparation.
tree=ast.parse(helper.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='old_c' for t in node.targets):break
 prefix.append(node)
ns={'__file__':str(helper),'__name__':'s20_prop_geometry_helpers'}
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(helper),'exec'),ns)
for name in ['get','read','write','project','master','world','card','on_sheet','rotate','probe','frozen','ASSETS']:globals()[name]=ns[name]
table=json.loads((P/'CONSUMPTION_058_131_CANDIDATE.json').read_text());measured={s['key']:s for s in json.loads((P/'native_contact_measurements.json').read_text())}
oldC=read('cam20_crane_lamp_left_001/registration_input.json')['rods'];states=[];records=[]
previous=json.loads((ASSETS/'F054_geometry.json').read_text())['turtle']
for row in table['states']:
 f=row['frame'];raw=get(row['path']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];A=np.array(Image.open(io.BytesIO(raw)).convert('RGBA'));H,W=A.shape[:2];y,x=np.indices((H,W));state=probe['states'][str(f)];mech=row['mechanism'];baseline=mech.get('finiteGateBaseline');axes=measured.get(f,{}).get('axes',[])
 if baseline:
  pose=baseline['pose'];rt=baseline['root'];points=state['points'];geometry={'turtle':{'root':rt,'pose':pose},'rods':[],'sourceFiniteGatePreserved':True}
  for original in baseline['rods']:
   role=original['id'];aa=on_sheet(card(rt,points[role]));end=np.array(original['B_world']);geometry['rods'].append({'id':role,'part':original['part'],'at':original['at'],'A_world':aa.tolist(),'end_world':end.tolist(),'A_master':master(project(aa)).tolist(),'length_m':float(np.linalg.norm(end-aa)),'adoptedLength_m':original['candidate_A_B_length_m']})
 else:
  points=state['points'];obs=measured[f];target=obs['cross'][0]-35
  if f==112:
   gate120=next(x for x in table['states'] if x['frame']==120)['mechanism']['finiteGateBaseline']
   target=gate120['rods'][0]['A_master'][0]+axes[0]['observedClamp'][0]-gate120['rods'][0]['B_master'][0]
  def residual(v):
   pp={k:rotate(p,v[2]) for k,p in points.items()};r=[]
   for role,a in zip(['T_H','T_S'],axes):
    z=master(card(v[:2],pp[role]));r.append((z[1]-a['slope']*z[0]-a['intercept'])/math.hypot(1,a['slope']))
   r.append(master(card(v[:2],pp['T_H']))[0]-target);return r
  seeds=[[previous['root'][0],previous['root'][1],previous['pose']['rootAngle']-state['pose']['rootAngle']],[state['root'][0],state['root'][1],.3-state['pose']['rootAngle']]]
  fits=[]
  for seed in seeds:
   fit=root(residual,seed)
   if fit.success and np.linalg.norm(residual(fit.x))<1e-4:fits.append(fit)
  assert fits,f'No finite actual-axis registration at{f}'
  # Keep the branch nearest the preceding whole puppet, not a new body pose.
  fit=min(fits,key=lambda z:np.linalg.norm(z.x[:2]-previous['root']))
  pose=copy.deepcopy(state['pose']);pose['rootAngle']+=float(fit.x[2]);rt=fit.x[:2].tolist();geometry={'turtle':{'root':rt,'pose':pose},'rods':[],'nativeAxisResidualMasterPx':residual(fit.x),'nativeCross':obs['cross'],'earlierWorldLengthsNotHistoricallyFrozen':True}
  for axis in axes:
   role=axis['id'];aa=on_sheet(card(rt,rotate(points[role],fit.x[2])));end=world(axis['observedClamp']);geometry['rods'].append({'id':role,'part':'head' if role=='T_H' else 'shell','at':[20,0] if role=='T_H' else [0,40],'A_world':aa.tolist(),'end_world':end.tolist(),'A_master':master(project(aa)).tolist(),'end_master':axis['observedClamp'],'length_m':float(np.linalg.norm(end-aa))})
 previous=geometry['turtle']
 geometry['craneRodOverrides']=[json.loads((ASSETS/'closure_CHARACTER_AND_RODS.json').read_text())['rods'][0]]
 geometry['craneRodReason']='After accepted047 R owns C_B; reuse its adopted finite source endpoint/unchanged length from closure package, not old L-held endpoint.'
 # Clear actual painted prop corridors only, preserving native solid silhouettes
 # and all skin components attached to them, including thumb/finger contours.
 rr,gg,bb=A[:,:,:3].astype(float).transpose(2,0,1);skin=(A[:,:,3]>0)&(rr>165)&(gg>110)&(bb>gg*.70)&(rr>gg+10)
 corridor=np.zeros((H,W),dtype=bool)
 for a in axes:
  m,b=a['slope'],a['intercept'];corridor|=(x>=180)&(x<=a['observedClamp'][0]+100)&(abs(y-m*x-b)/math.hypot(1,m)<10)
 hue=(gg-bb)/np.maximum(1,rr-bb)/6
 painted_wood=corridor&(A[:,:,3]>0)&(rr>gg+7)&(gg>bb+7)&(bb<.85*gg)&(bb>.35*gg)&(hue>.075)&((rr-gg)>.8*(gg-bb))
 ids,_=label(binary_opening((A[:,:,3]>160)&~painted_wood,iterations=4));sizes=np.bincount(ids.ravel());solid=(ids>0)&(sizes[ids]>1000);sid,_=label(skin);touch=np.unique(sid[binary_dilation(solid,iterations=5)&skin]);touch=touch[touch>0];native_skin=np.isin(sid,touch)
 yellow=(A[:,:,3]>0)&(rr>gg+8)&(gg>bb+8)&(hue>.112);yi,_=label(yellow);yt=np.unique(yi[solid&yellow]);native_yellow=np.isin(yi,yt[yt>0])
 protected=binary_dilation(binary_fill_holes(binary_closing(native_skin,iterations=2)),iterations=3)|binary_dilation(solid,iterations=4)|native_yellow
 for role in ['C_B','C_N']:
  a=oldC[role];m,b=a['slope'],a['intercept'];corridor|=(x>=670)&(x<=956)&(abs(y-m*x-b)/math.hypot(1,m)<8)
 a=oldC['C_B'];old_cb=(x>885)&(x<960)&(abs(y-a['slope']*x-a['intercept'])/math.hypot(1,a['slope'])<9);clear_old_cb=old_cb&(A[:,:,3]>0)&(rr>gg+7)&(gg>bb+7)&(bb<.68*gg)&(hue>.075)
 erase=(corridor&(A[:,:,3]>0)&~protected)|clear_old_cb;B=A.copy();B[erase]=0;assert np.array_equal(B[protected&~clear_old_cb],A[protected&~clear_old_cb]);assert np.array_equal(B[~erase],A[~erase]);Image.fromarray(erase.astype('uint8')*255).save(P/f'F{f:03}_engineering_only_mask.png')
 name=f'F{f:03}_people.png';Image.fromarray(B).save(ASSETS/name);gname=f'F{f:03}_geometry.json';geometry['originalTurtleScale']=1.3;geometry['noPersonTransform']=True;write(ASSETS/gname,geometry)
 start,end=row['candidateExposureInclusive'];states.append({'key':f,'start':start,'end':end,'people':name,'geometry':gname,'stage':'active_entangle' if start<111 else 'passive_residual' if start<125 else 'mid_roll','candidateExposure':True})
 records.append({'key':f,'source':row['path'],'sourceCommit':row['sourceFetchCommit'],'sourceSHA256':row['sha256'],'production':name,'productionSHA256':hashlib.sha256((ASSETS/name).read_bytes()).hexdigest(),'protectedNativePixelsUnchanged':True,'exteriorGuidePixelsRemoved':int(erase.sum()),'newImageCalls':0})
 print(f,'registered turtle',np.round(rt,3).tolist(),'rootAngle',round(pose['rootAngle'],3),'A/B',[(r['id'],np.round(r['A_master'],1).tolist(),round(r['length_m'],3)) for r in geometry['rods']],flush=True)
q=json.loads((ASSETS/'sequence.json').read_text());q['states']=sorted([s for s in q['states'] if s['key']<58 or s['key']>131]+states,key=lambda s:s['start']);q['availableIntervals']=[[0,143]];q['missingExposure']=None;q['status']='ALL_FRONT_DRAWINGS_AND_EXPLICIT_CANDIDATE_EXPOSURES_BOUND_ACTUAL_REVIEW_PENDING';write(ASSETS/'sequence.json',q);write(P/'source_and_cleanup.json',records)
print('15 adopted sources,74 explicit exposures, native people unchanged; original finite120/128 baselines retained.')
