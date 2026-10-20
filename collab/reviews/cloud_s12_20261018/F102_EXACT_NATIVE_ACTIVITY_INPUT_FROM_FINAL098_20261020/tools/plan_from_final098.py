"""Rebind102 to the locked actual098; never reuse the old102 human preview.
Only true prop/C110 fields are inherited. This file creates no character art.
"""
from pathlib import Path
import numpy as np,json,math,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F098_EXACT_NATIVE_ACTIVITY_actual_call01_20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=M/'candidate/F098.png';canvas=M/'actual_scene/F098_canvas.png'
assert sha(native)=='9de7e1957a1bce44df2a0f7bf785981ea14cda008ba52613f86c9924e65da6e8'
assert sha(canvas)=='9039571a4dc56680204d34f34b90aabe73b4b9dff78a5e7f002178241f47e648'
lock={'commit':'e3c93f032172826f683799d1496a1151b00c6dc3','native_path':str(native),'native_SHA256':sha(native),'actual_Canvas_path':str(canvas),'actual_Canvas_SHA256':sha(canvas),'locked098_unchanged':True,'accepted_prior_coordinate_correction':'one whole-original affine, not uniform similarity; axis ratio difference about2.74%'}
(O/'provenance/SOLE_FINAL098_MOTHER.json').write_text(json.dumps(lock,indent=2)+'\n')
old=json.loads((R/'F098_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL094_20261020/geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text())['prop_plan']
C=json.loads((R/'geometry/three_key_pose_proposal.json').read_text())['states'][-1]
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def rigid(p,t,d):
 rr=rot(d);return np.c_[rr,np.asarray(t)-rr@np.asarray(p)]
def at(m,p):return np.asarray(m)@np.r_[p,1.]
# New visible proxies read on FINAL098, not the old nominal102 construction.
# Hidden shoulder/hip estimates remain visibly labelled estimates, not bone data.
hip=np.array([520.,860.]);knee=np.array([610.,1200.])
source={'R':{'shoulder':[548.,452.],'elbow':[615.,678.],'wrist':[841.,779.]},'L':{'shoulder':[585.,415.],'elbow':[670.,625.],'wrist':[790.,531.]}}
for r in source:source[r]['true_grip']=((np.array(old['rods'][r]['grip_scene'])-[275.,112.])/.7).tolist()
def make(frame):
 t=(frame-98)/12;turns=(frame-98)/4
 root=(1-t)*np.array(old['root_scene'])+t*np.array([1240.,550.]);plane=70+15*t;roll=(1-t)*old['projected_roll_degrees']
 pose={'angles':{k:(1-t)*v+t*C['code_pose']['angles'][k] for k,v in old['code_pose']['angles'].items()},'rootAngle':0,'facing':1}
 beta,alpha,theta=map(math.radians,[15,12,plane]);cam=np.array([[math.cos(beta),0,-math.sin(beta)],[-math.sin(alpha)*math.sin(beta),-math.cos(alpha),-math.sin(alpha)*math.cos(beta)],[math.cos(alpha)*math.sin(beta),-math.sin(alpha),math.cos(alpha)*math.cos(beta)]])
 basis=cam@np.array([[1.,0.],[0.,math.sin(theta)],[0.,math.cos(theta)]]);basis[:2]=rot(roll)@basis[:2];assert np.allclose(basis.T@basis,np.eye(2))
 ob=np.array(old['paper_3D_camera_basis']);Q=np.c_[basis,np.cross(basis[:,0],basis[:,1])]@np.c_[ob,np.cross(ob[:,0],ob[:,1])].T
 neck=np.array([152.55,58.05]);angle=0.
 for i in range(3):angle+=pose['angles']['neck'+str(i)];neck+=rot(math.degrees(angle))@np.array([28.35,0.])
 angle+=pose['angles']['neck3'];neck+=rot(math.degrees(angle))@np.array([10.,0.]);local={'R':[-75.,6.],'L':neck}
 ht=knee+rot(6*turns)@(hip-knee);UT=rigid(hip,ht,-6*turns);TH=rigid(knee,knee,6*turns);props={};arms={}
 for r in ['R','L']:
  prev=old['rods'][r];mu=prev['grip_fraction_from_hinge_unchanged'];h3=np.r_[root,0.]+.72*basis@np.array(local[r]);vec=Q@(np.array(prev['free_camera3D_scene_units'])-prev['hinge_camera3D_scene_units']);f3=h3+vec;g3=h3+mu*vec
  ov=np.array(prev['hinge_scene'])-prev['free_scene'];nv=-vec[:2];da=math.degrees(math.atan2(nv[1],nv[0])-math.atan2(ov[1],ov[0]));assert abs(np.linalg.norm(vec)-prev['physical_length_scene_units'])<1e-8
  props[r]={'part':prev['part'],'joint_local_mm':list(local[r]),'hinge_scene':h3[:2].tolist(),'hinge_camera3D_scene_units':h3.tolist(),'grip_scene':g3[:2].tolist(),'grip_camera3D_scene_units':g3.tolist(),'free_scene':f3[:2].tolist(),'free_camera3D_scene_units':f3.tolist(),'grip_fraction_from_hinge_unchanged':mu,'physical_length_H':prev['physical_length_H'],'physical_length_scene_units':prev['physical_length_scene_units'],'physical_length_camera3D_check':float(np.linalg.norm(vec)),'projected_length_new_scene':float(np.linalg.norm(vec[:2])),'projected_angle_delta_degrees':da}
  s,e,w,c=[np.array(source[r][k]) for k in ['shoulder','elbow','wrist','true_grip']];gt=(g3[:2]-[275.,112.])/.7;H=rigid(c,gt,da);wt=at(H,w);st=at(UT,s);u=float(np.linalg.norm(e-s));f=float(np.linalg.norm(w-e));v=wt-st;d=float(np.linalg.norm(v));assert abs(u-f)<d<u+f
  al=(u*u-f*f+d*d)/(2*d);he=math.sqrt(u*u-al*al);v0=w-s;v1=e-s;sg=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1;et=st+al*v/d+sg*he*np.array([-v[1],v[0]])/d
  ad=lambda a,b:math.degrees(math.atan2(b[1],b[0])-math.atan2(a[1],a[0]));du=ad(e-s,et-st);dv=ad(w-e,wt-et)
  arms[r]={'source_final098':source[r],'target':{'shoulder':st.tolist(),'elbow':et.tolist(),'wrist':wt.tolist(),'true_grip':gt.tolist()},'upper_rigid_matrix':rigid(s,st,du).tolist(),'forearm_rigid_matrix':rigid(e,et,dv).tolist(),'whole_hand_bangle_same_rod_angle_matrix':H.tolist(),'upper_projected_proxy_length_source':u,'upper_projected_proxy_length_target':float(np.linalg.norm(et-st)),'forearm_projected_proxy_length_source':f,'forearm_projected_proxy_length_target':float(np.linalg.norm(wt-et)),'straight_reach_spare_native':u+f-d,'elbow_delta_native':(et-e).tolist(),'hand_scale':1,'wrist_articulation_delta_degrees':da-dv,'independent_finger_moves':0}
 return {'status':'F102_INPUT_ONLY_NO_GENERATION_PENDING_ACTUAL_GATE','frame':frame,'sole_locked098':lock,'new_visible_proxy_uncertainty':'15-25px sleeve-hidden shoulder/elbow/hip; wrists approx5px; not measured anatomical bone lengths','old102_human_preplan_reused':False,'hip_source_final098_proxy':hip.tolist(),'hip_target':ht.tolist(),'hip_delta_native':(ht-hip).tolist(),'knee_support_visible_proxy':knee.tolist(),'whole_torso_head_rise_degrees':-6*turns,'whole_torso_head_rigid_matrix':UT.tolist(),'thigh_rigid_matrix':TH.tolist(),'pose_choice':'Whole torso/collar/neck/head stand up together from accepted098. Far elbow remains at outer chest edge; both complete chains require actual visual gate, not reach-only approval.','arms':arms,'prop_plan':{'root_scene':root.tolist(),'paper_plane_inclination_degrees':plane,'projected_roll_degrees':roll,'code_pose':pose,'actual_makeCrane_scale':1.35,'paper_3D_camera_basis':basis.tolist(),'mm_to_scene_scale':.72,'rods':props,'C110_terminal':{'root_scene':[1240,550],'paper_plane_inclination_degrees':85},'legacy_frame114_not_used':True,'code_human_points_used':False,'true_physical_rod_3D_rotation':Q.tolist(),'camera_depth_feasible_model_not_measured':True},'new102_imagegen_calls':0,'new106_imagegen_calls':0,'actual102_person_Canvas':0}
g=make(102);light=make(106)
(O/'geometry/F102_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
(O/'qa/F106_LIGHTWEIGHT_ONLY_REBIND_AFTER102.json').write_text(json.dumps({'status':'SCALAR_REACH_ONLY_NOT_A_106_INPUT_TARGET','actual106_must_rebind_after102_lock':True,'paper_degrees':80,'arms':{r:{'reachable':True,'straight_reach_spare_native':a['straight_reach_spare_native'],'upper_proxy_length':a['upper_projected_proxy_length_source'],'forearm_proxy_length':a['forearm_projected_proxy_length_source']} for r,a in light['arms'].items()},'imagegen_calls':0},indent=2)+'\n')
print(json.dumps({'hip_delta':g['hip_delta_native'],'paper':75,'root':g['prop_plan']['root_scene'],'arms':{r:{'elbow':a['target']['elbow'],'wrist':a['target']['wrist'],'wrist_articulation_delta':a['wrist_articulation_delta_degrees']} for r,a in g['arms'].items()}},indent=2))
