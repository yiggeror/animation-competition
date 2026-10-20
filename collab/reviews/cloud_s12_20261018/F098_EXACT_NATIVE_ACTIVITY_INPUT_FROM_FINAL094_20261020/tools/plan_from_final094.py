"""Native activity references, not production drawing. Sole mother: locked final094.
Only genuine code prop geometry is taken from the previous plan / C110.
"""
from pathlib import Path
import numpy as np,json,math,hashlib
O=Path(__file__).resolve().parents[1]; R=O.parent
M=R/'F094_LOCAL_ARMS_KNEES_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=M/'candidate/F094.png'; canvas=M/'actual_scene/F094_canvas.png'
assert sha(native)=='63fb22a00e9a3521d5e1d6b2f3c116ad1f0e78baa7993f7fa39626daea7bc417'
assert sha(canvas)=='12bf5d70b7d38785132f41bba5e0996da6737a446e98d45d69f6900fdd77f26d'
lock={'commit':'5e65b2213351166bd2143f6e4e56e907c7519cd9','native_path':str(native),'native_SHA256':sha(native),'actual_Canvas_path':str(canvas),'actual_Canvas_SHA256':sha(canvas),'locked094_is_not_changed':True}
(O/'provenance/SOLE_FINAL094_MOTHER.json').write_text(json.dumps(lock,indent=2)+'\n')
old=json.loads((R/'F094_COMPLETE_TARGET_FROM_LOCKED090_20261019/geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())['prop_plan']
C=json.loads((R/'geometry/three_key_pose_proposal.json').read_text())['states'][-1]
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def rigid(p,t,d):
 rr=rot(d);return np.c_[rr,np.asarray(t)-rr@np.asarray(p)]
def at(m,p):return np.asarray(m)@np.r_[p,1.]
F=np.array([[.8808256253463345,-.05865897274477678,53.10534221159776],[.05865897274477680,.8808256253463345,4.105390538904658]])
hip=F@np.array([555,945,1]);knee=np.array([610.,1200.])
source={'R':{'shoulder':[543.,461.],'elbow':[642.,684.],'wrist':[865.,789.]},'L':{'shoulder':[579.5153433574776,442.599710580553],'elbow':[679.,643.],'wrist':[823.5364834028757,578.3632026173367]}}
for r in source:source[r]['true_grip']=((np.asarray(old['rods'][r]['grip_scene'])-[275.,112.])/.7).tolist()
def make(frame):
 t=(frame-94)/16;turns=(frame-94)/4
 root=(1-t)*np.asarray(old['root_scene'])+t*np.array([1240.,550.]);plane=65+20*t;roll=(1-t)*old['projected_roll_degrees']
 pose={'angles':{k:(1-t)*v+t*C['code_pose']['angles'][k] for k,v in old['code_pose']['angles'].items()},'rootAngle':0,'facing':1}
 beta,alpha,theta=map(math.radians,[15,12,plane])
 cam=np.array([[math.cos(beta),0,-math.sin(beta)],[-math.sin(alpha)*math.sin(beta),-math.cos(alpha),-math.sin(alpha)*math.cos(beta)],[math.cos(alpha)*math.sin(beta),-math.sin(alpha),math.cos(alpha)*math.cos(beta)]])
 basis=cam@np.array([[1.,0.],[0.,math.sin(theta)],[0.,math.cos(theta)]]);basis[:2]=rot(roll)@basis[:2]
 assert np.allclose(basis.T@basis,np.eye(2))
 ob=np.asarray(old['paper_3D_camera_basis']);Q=np.c_[basis,np.cross(basis[:,0],basis[:,1])]@np.c_[ob,np.cross(ob[:,0],ob[:,1])].T
 neck=np.array([152.55,58.05]);angle=0.
 for i in range(3):angle+=pose['angles']['neck'+str(i)];neck+=rot(math.degrees(angle))@np.array([28.35,0.])
 angle+=pose['angles']['neck3'];neck+=rot(math.degrees(angle))@np.array([10.,0.])
 local={'R':np.array([-75.,6.]),'L':neck};ht=knee+rot(6*turns)@(hip-knee);UT=rigid(hip,ht,-2.5*turns);TH=rigid(knee,knee,6*turns)
 props={};arms={}
 for r in ['R','L']:
  prev=old['rods'][r];mu=prev['grip_fraction_from_hinge_unchanged'];h3=np.r_[root,0.]+.72*basis@local[r]
  vec=Q@(np.asarray(prev['free_camera3D_scene_units'])-np.asarray(prev['hinge_camera3D_scene_units']));f3=h3+vec;g3=h3+mu*vec
  ov=np.asarray(prev['hinge_scene'])-np.asarray(prev['free_scene']);nv=-vec[:2];da=math.degrees(math.atan2(nv[1],nv[0])-math.atan2(ov[1],ov[0]))
  norm=float(np.linalg.norm(vec));assert abs(norm-prev['physical_length_scene_units'])<1e-8
  props[r]={'part':prev['part'],'joint_local_mm':local[r].tolist(),'hinge_scene':h3[:2].tolist(),'hinge_camera3D_scene_units':h3.tolist(),'grip_scene':g3[:2].tolist(),'grip_camera3D_scene_units':g3.tolist(),'free_scene':f3[:2].tolist(),'free_camera3D_scene_units':f3.tolist(),'grip_fraction_from_hinge_unchanged':mu,'physical_length_H':prev['physical_length_H'],'physical_length_scene_units':prev['physical_length_scene_units'],'physical_length_camera3D_check':norm,'projected_length_new_scene':float(np.linalg.norm(vec[:2])),'projected_angle_delta_degrees':da}
  s,e,w,c=[np.asarray(source[r][k]) for k in ['shoulder','elbow','wrist','true_grip']];gt=(g3[:2]-[275.,112.])/.7;H=rigid(c,gt,da);wt=at(H,w);st=at(UT,s)
  u=float(np.linalg.norm(e-s));f=float(np.linalg.norm(w-e));v=wt-st;d=float(np.linalg.norm(v));assert abs(u-f)<d<u+f
  along=(u*u-f*f+d*d)/(2*d);height=math.sqrt(u*u-along*along);v0=w-s;v1=e-s;branch=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1
  et=st+along*v/d+branch*height*np.array([-v[1],v[0]])/d
  angleof=lambda a,b:math.degrees(math.atan2(b[1],b[0])-math.atan2(a[1],a[0]))
  arms[r]={'source_final094':source[r],'target':{'shoulder':st.tolist(),'elbow':et.tolist(),'wrist':wt.tolist(),'true_grip':gt.tolist()},'upper_rigid_matrix':rigid(s,st,angleof(e-s,et-st)).tolist(),'forearm_rigid_matrix':rigid(e,et,angleof(w-e,wt-et)).tolist(),'whole_hand_bangle_same_rod_angle_matrix':H.tolist(),'upper_projected_proxy_length':u,'forearm_projected_proxy_length':f,'straight_reach_spare_native':u+f-d,'elbow_delta_native':(et-e).tolist(),'hand_scale':1,'independent_finger_moves':0}
 return {'status':'INPUT_ONLY_AWAITING_GATE_NEW_IMAGEGEN0','frame':frame,'source_final094':lock,'proxy_uncertainty_native':'15-25px sleeve-hidden shoulder/elbow/hip; projected visible proxies, not anatomical measurements','hip_source_actual094_visible_proxy':hip.tolist(),'hip_target':ht.tolist(),'hip_delta_native':(ht-hip).tolist(),'knee_support_visible_proxy':knee.tolist(),'whole_torso_head_rigid_matrix':UT.tolist(),'thigh_rigid_matrix':TH.tolist(),'arms':arms,'prop_plan':{'root_scene':root.tolist(),'paper_plane_inclination_degrees':plane,'projected_roll_degrees':roll,'code_pose':pose,'actual_makeCrane_scale':1.35,'paper_3D_camera_basis':basis.tolist(),'mm_to_scene_scale':.72,'rods':props,'C110_terminal':{'root_scene':[1240,550],'paper_plane_inclination_degrees':85},'legacy_frame114_not_used':True,'old_code_human_points_used':False,'rod_3D_rotation':Q.tolist(),'camera_depth_model_feasible_not_measured':True},'new098_imagegen_calls':0,'new102_imagegen_calls':0,'actual098_full_Canvas':0}
g=make(98);g102=make(102)
(O/'geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
# 102 is a scalar reach check only, to be rebased to the eventual locked098.
light={'status':'LIGHTWEIGHT_ONLY_NO_102_POSE_IMAGE_NO_GENERATION','must_rebase_after098_lock':True,'paper_degrees':75,'arms':{r:{'reach_spare_native':a['straight_reach_spare_native'],'lengths':[a['upper_projected_proxy_length'],a['forearm_projected_proxy_length']],'elbow':a['target']['elbow'],'reachable':True} for r,a in g102['arms'].items()},'imagegen_calls':0}
(O/'qa/F102_LIGHTWEIGHT_REACH_ONLY.json').write_text(json.dumps(light,indent=2)+'\n')
print(json.dumps({'frame98':{'hip_delta':g['hip_delta_native'],'root':g['prop_plan']['root_scene'],'paper':70,'elbow_deltas':{r:a['elbow_delta_native'] for r,a in g['arms'].items()}},'frame102':light},indent=2))
