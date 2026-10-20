"""Zero-call current-branch person construction; originals remain untouched."""
from pathlib import Path
import json,hashlib,math,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_opening,binary_dilation,binary_fill_holes,map_coordinates,label
from scipy.interpolate import RBFInterpolator
F=Path(__file__).resolve().parent;P=F.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=P/'next_F120_passive_decay_input_001/generation_001/F120_uniform_registered_upper_fixed_full_lower_candidate.png';assert sha(source)=='40d73e42505d5e7c83dc22d33511e5a2e4862dc35b5a4ff210e50eca8ef2bf5c'
D=json.loads((F.parent/'mechanism/source_model_probe.json').read_text());M=json.loads((F.parent/'mechanism/constraint_preflight.json').read_text());A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
skin=(A[:,:,3]>40)&(r>165)&(g>90)&(b>90)&(b>g*.65)&(r>g+12)
skin=binary_fill_holes(binary_opening(skin,iterations=1));skin_edge=binary_dilation(skin,iterations=3)&(A[:,:,3]>0)
cc,_=label(binary_dilation(skin,iterations=2));ids=[int(cc[425,480]),int(cc[510,570])];assert ids[0]>0 and ids[1]>0 and ids[0]!=ids[1]
arms=[binary_dilation(binary_fill_holes(cc==idx),iterations=1)&(A[:,:,3]>0) for idx in ids]
palms=[arms[0]&poly([(378,355),(437,355),(456,392),(456,450),(378,450)]),arms[1]&poly([(408,475),(464,475),(507,500),(507,566),(408,566)])]
for i in range(2):
 Image.fromarray(np.uint8(palms[i])*255).save(F/f'complete_palm120_{"R" if i==0 else "L"}_mask.png');Image.fromarray(np.uint8(arms[i])*255).save(F/f'complete_arm120_{"R" if i==0 else "L"}_mask.png')
# Old exterior drawn axes are reference only. Erase their full ink/AA corridor
# outside real skin, preserving the source original and all hand/arm skin.
corr=np.zeros((H,W),bool)
for m,b0 in M['axis120']:corr|=(abs(yy-m*xx-b0)/math.hypot(1,m)<13)
erase=corr&(xx>205)&(xx<515)&(yy>300)&(yy<570)&(A[:,:,3]>0)&~(arms[0]|arms[1])
clean=A.copy();clean[erase]=0;Image.fromarray(np.uint8(erase)*255).save(F/'old_exterior_T_erase_mask.png');Image.fromarray(clean).save(F/'F120_people_old_exterior_T_cleared_CANDIDATE.png')
diag=np.dstack([np.full((H,W),255,np.uint8),np.full((H,W),60,np.uint8),np.full((H,W),165,np.uint8),np.uint8(erase)*220]);Image.fromarray(diag).save(F/'old_exterior_T_magenta_diagnostic_layer.png')
def elbow(s,w,l1,l2,near):
 v=w-s;d=np.linalg.norm(v);assert abs(l1-l2)<d<l1+l2;u=v/d;c=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(l1*l1-c*c);n=np.array([-u[1],u[0]]);a=s+c*u
 return min([a+h*n,a-h*n],key=lambda p:np.linalg.norm(p-near))
out=clean.copy();newmasks=[];bones=[]
for i,(side,sp,ep,wp) in enumerate([('R',[546,420],[501,446],[442.4791910880613,419.5984911398264]),('L',[675,455],[646,502],[495.61637530049626,519.9053017137846])]):
 s,e,w=map(lambda p:np.array(p,float),[sp,ep,wp]);dp=np.array(M['rows'][i]['grip_delta_master']);nw=w+dp;l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow(s,nw,l1,l2,e)
 controls=[(s,np.zeros(2)),(e,ne-e),(w,dp)]
 for y in range(360,565,6):
  for x in range(375,510,6):
   if palms[i][y,x]:controls.append((np.array([x,y],float),dp))
 # Keep each original sleeve/root continuous; distal arm follows its own palm.
 for y in range(370,480,8):
  for x in range(520 if i==0 else 640,565 if i==0 else 710,8):
   if arms[i][y,x] and (i==0 or y<468):controls.append((np.array([x,y],float),np.zeros(2)))
 for p in [[360,340],[730,340],[360,590],[730,590]]:controls.append((np.array(p,float),np.zeros(2)))
 controls=list({tuple(p):(p,d) for p,d in controls}.values());field=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
 x0,y0,x1,y1=360,340,730,590;h,wc=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:2,0:wc:2];v=field(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,wc));sx=dx.astype(float);sy=dy.astype(float)
 for _ in range(10):
  vx=map_coordinates(v[:,:,0],[sy/2,sx/2],order=3,mode='nearest');vy=map_coordinates(v[:,:,1],[sy/2,sx/2],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
 layer=np.zeros_like(clean);layer[arms[i]]=clean[arms[i]];patch=layer[y0:y1,x0:x1];a=patch[:,:,3].astype(float)/255;pm=patch[:,:,:3].astype(float)*a[:,:,None];wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1);rgb=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2);q=np.zeros_like(patch);q[:,:,3]=np.rint(wa*255).astype('uint8');q[:,:,:3]=np.rint(np.divide(rgb,wa0[:,:,None],out=np.zeros_like(rgb),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');q[q[:,:,3]<3]=0
 transformed=np.zeros_like(clean);transformed[y0:y1,x0:x1]=q;out[arms[i]]=0;out=np.array(Image.alpha_composite(Image.fromarray(out),Image.fromarray(transformed)))
 pmap=map_coordinates(palms[i][y0:y1,x0:x1].astype(float),[sy,sx],order=1,mode='constant',cval=0)>0.1;wholep=np.zeros((H,W),bool);wholep[y0:y1,x0:x1]=pmap;newmasks.append(wholep);Image.fromarray(np.uint8(wholep)*255).save(F/f'complete_palm128_{side}_mask.png');Image.fromarray(np.uint8(transformed[:,:,3]>0)*255).save(F/f'complete_arm128_{side}_mask.png')
 bones.append({'side':side,'source_SH_E_WR':[s.tolist(),e.tolist(),w.tolist()],'target_SH_E_WR':[s.tolist(),ne.tolist(),nw.tolist()],'projected_upper_length_source_target':[float(l1),float(np.linalg.norm(ne-s))],'projected_fore_length_source_target':[float(l2),float(np.linalg.norm(nw-ne))],'palm_translation':dp.tolist(),'whole_palm_scale':1,'whole_palm_rotation_deg':0,'note':'2D construction reference, not 3D bone certification or new native drawing.'})
Image.fromarray(out).save(F/'F128_people_proposed_arms_CONSTRUCTION_ONLY.png')
for frame,data in [(120,clean),(128,out)]:
 bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(data));bg.convert('RGB').save(F/f'people_{frame}_gray_CONSTRUCTION_ONLY.jpg',quality=95)
# Unchanged complete body/head/legs and grandma/C: edits are confined to arm/oldT.
changed=np.any(out!=A,axis=2);assert not np.any(changed&(xx>=810));assert not np.any(changed&~erase&(yy<360));assert not np.any(changed&(yy>=590));Image.fromarray(np.uint8(changed)*255).save(F/'actual_F128_changed_people_mask.png')
face=(A[:,:,3]>20)&(xx>490)&(xx<820)&(yy<360);Image.fromarray(np.uint8(face)*255).save(F/'complete_face_head_neck_protected_mask.png')
frames={}
for frame in [120,128]:
 rows=[]
 for row in M['rows']:
  rows.append({'id':row['id'],'holder':'X.R' if row['id']=='T_H' else 'X.L','part':row['part'],'at':row['at'],'A_master':row[f'A{frame}_master'],'B_master':row['source_grip_master' if frame==120 else 'grip128_master'],'B_world':row['B120_world' if frame==120 else 'B128_world'],'candidate_A_B_length_m':row['rigid_rod_length_m']})
 frames[str(frame)]={'root':M['root120_registered_from_passed_axes' if frame==120 else 'root128_same_registration_plus_original_puppet_delta'],'pose':D['states'][str(frame)]['pose'],'rods':rows,'people_png':'F120_people_old_exterior_T_cleared_CANDIDATE.png' if frame==120 else 'F128_people_proposed_arms_CONSTRUCTION_ONLY.png'}
config={'status':'CURRENT_MINIMUM_DISPLACEMENT_BRANCH_ONLY_NOT_ADOPTED','camera':D['camera'],'reg':D['approved_people_registration'],'canvas':[1920,1080],'frames':frames,'new_image_calls':0,'old_infinite_line_gate_withdrawn':True,'rod_rule':'Only finite A-to-B, no rendered free tail. Original paint outside palms erased on copies.','external_handle_tail_length_m':0,'root120_and_candidate_lengths_not_previously_frozen':True,'source120_file':str(source),'source120_sha256':sha(source),'bones':bones,'head_torso_skirt_full_legs_grandma_C_unchanged':True,'people128_is_construction_not_new_native_art':True}
(F/'candidate_geometry.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'source120_unchanged_sha':sha(source),'clean120_sha':sha(F/'F120_people_old_exterior_T_cleared_CANDIDATE.png'),'proposed128_sha':sha(F/'F128_people_proposed_arms_CONSTRUCTION_ONLY.png'),'bones':bones},ensure_ascii=False))
