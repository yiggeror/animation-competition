from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
S=Path('collab/reviews/cloud_s12_20261018');prop=json.loads((S/'geometry/code_crane_points.json').read_text())['states']
a,b=np.deg2rad(12),np.deg2rad(15);SC=215.;ORG=np.array([480.,1012.]);ca,sa,cb,sb=np.cos(a),np.sin(a),np.cos(b),np.sin(b)
L={'upper_arm':.86,'forearm':.64,'wrist_to_grip':.23,'femur':.90,'tibia':.89,'spine':1.43}
def project(p):
 x,y,z=np.array(p).T;return np.array([ORG[0]+SC*(cb*x-sb*z),ORG[1]-SC*(ca*y+sa*(sb*x+cb*z))]).T
def inv(u,v,z):
 x=((u-ORG[0])/SC+sb*z)/cb;y=((ORG[1]-v)/SC-sa*(sb*x+cb*z))/ca;return np.array([x,y,z])
def anatomy(hipY,lean):
 dy=hipY-.12;dx=np.sqrt(L['femur']**2-dy*dy);hip=np.array([.62-dx,hipY,0.]);sp=np.array([np.sin(np.deg2rad(lean)),np.cos(np.deg2rad(lean)),0.])*L['spine'];sh=hip+sp
 d={'hip':hip,'shoulder_mid':sh}
 for role,z,kx in [('R',-.34,.60),('L',.34,.64)]:
  d['hip'+role]=np.array([kx-dx,hipY,z]);d['knee'+role]=np.array([kx,.12,z]);d['ankle'+role]=np.array([kx-L['tibia'],.12,z]);d['shoulder'+role]=sh+np.array([0,0,-.57 if role=='R' else .57])
 return d
def endpoint(root,pt,tilt):
 q=.72/SC*np.array(pt);t=np.deg2rad(tilt);return root+np.array([q[0],q[1]*np.sin(t),q[1]*np.cos(t)])
def elbow(s,w,role):
 vec=w-s;dist=np.linalg.norm(vec);n=vec/dist;u,f=L['upper_arm'],L['forearm'];assert abs(u-f)<dist<u+f,(role,dist)
 t=(u*u-f*f+dist*dist)/(2*dist);r=np.sqrt(u*u-t*t);pole=np.array([0,-1,-.4]) if role=='R' else np.array([.35,-.55,1.0]);pole-=n*np.dot(pole,n);pole/=np.linalg.norm(pole);return s+t*n+r*pole
states=[]
for id,hipY,lean,rootUV,tilt in [('A',.76,45,(1335,775),55),('B',.86,28,(1335,775),55),('C',.96,8,(1240,550),85)]:
 d=anatomy(hipY,lean);root=inv(*rootUV,-.38 if id!='C' else -.25);p=next(r for r in prop if r['id']==id);d['P_body']=endpoint(root,p['body'],tilt);d['P_neck']=endpoint(root,p['neck'],tilt);d['crane_root']=root
 if id=='B':
  GR=inv(930,765,-.58);GL=inv(930,630,.26);rodlen={'R':np.linalg.norm(d['P_body']-GR),'L':np.linalg.norm(d['P_neck']-GL)}
 if id=='A':
  d['gripR']=inv(850,795,-.58);d['wristR']=d['gripR']-np.array([.23,.0,0.]);d['gripL']=inv(905,705,.26);d['wristL']=d['gripL']-np.array([.23,0,0.]);d['rodR_contact']=False;d['rodL_contact']=False
 else:
  for role,pp,uv,z in [('R',d['P_body'],(930,765) if id=='B' else (860,690),-.58),('L',d['P_neck'],(930,630) if id=='B' else (790,540),.26)]:
   def fun(g):
    direction=(pp-g)/np.linalg.norm(pp-g);w=g-L['wrist_to_grip']*direction;reach=np.linalg.norm(w-d['shoulder'+role]);return [100*(np.linalg.norm(pp-g)-rodlen[role]),.02*(project(g)[0]-uv[0]),.02*(project(g)[1]-uv[1]),.2*(g[2]-z),50*max(0,reach-1.44)]
   sol=least_squares(fun,inv(*uv,z),bounds=([-20,-20,-.9 if role=='R' else .15],[20,20,-.35 if role=='R' else .75]),max_nfev=1000,xtol=1e-13,ftol=1e-13,gtol=1e-13);g=pp+(sol.x-pp)/np.linalg.norm(sol.x-pp)*rodlen[role];direction=(pp-g)/np.linalg.norm(pp-g);d['grip'+role]=g;d['wrist'+role]=g-L['wrist_to_grip']*direction;d['rod'+role+'_contact']=True
 for role in ['R','L']:d['elbow'+role]=elbow(d['shoulder'+role],d['wrist'+role],role)
 pitch=np.deg2rad(20 if id=='A' else 12 if id=='B' else 5);axis=np.array([np.sin(pitch),np.cos(pitch),0.]);d['neck_base']=d['shoulder_mid']+axis*.18;d['head_center']=d['neck_base']+axis*.50;d['head_axis']=axis
 record={'id':id,'frame':{'A':0,'B':64,'C':114}[id],'hipY':hipY,'lean_design_degrees':lean,'prop_plane_tilt_degrees':tilt,'code_pose':p['pose'],'points_H':{k:v.tolist() for k,v in d.items() if isinstance(v,np.ndarray)},'points_scene':{k:project(v).tolist() for k,v in d.items() if isinstance(v,np.ndarray) and k!='head_axis'},'contacts':{'R':id!='A','L':id!='A'},'rod_lengths_H':rodlen if id!='A' else None}
 states.append(record)
 print(id,'head',project(d['head_center']),'shoulders',[project(d['shoulder'+r]).round(1).tolist() for r in ['R','L']],'grips',[project(d['grip'+r]).round(1).tolist() for r in ['R','L']],'elbows',[project(d['elbow'+r]).round(1).tolist() for r in ['R','L']])
 if id!='A':print('rods',rodlen,'residual',[np.linalg.norm(d['P_body' if r=='R' else 'P_neck']-d['grip'+r])-rodlen[r] for r in ['R','L']])
for role,ppkey,suv,z in [('R','P_body',(1003.0555556,795),-.75),('L','P_neck',(1015.2777778,775),-.10)]:
 aa=states[0];pp=np.array(aa['points_H'][ppkey]);rim=inv(*suv,z);target=pp+(rim-pp)/np.linalg.norm(rim-pp)*states[1]['rod_lengths_H'][role]
 for key,point in [('free_grip'+role,target),('rim_contact'+role,rim)]:aa['points_H'][key]=point.tolist();aa['points_scene'][key]=project(point).tolist()
 aa['rod_lengths_H']=states[1]['rod_lengths_H']
(S/'geometry/three_key_pose_proposal.json').write_text(json.dumps({'status':'CONSTRUCTION_REFERENCE_ONLY_PENDING_ASTRA_NOT_CHARACTER_ART','head_unit_scene_pixels':SC,'projection':{'origin':ORG.tolist(),'yaw_degrees':15,'pitch_degrees':12},'bone_lengths_H':L,'proposed_native_registration':{'canvas':[1024,1536],'scale':.75,'translation':[300,100]},'states':states},ensure_ascii=False,indent=2)+'\n')
