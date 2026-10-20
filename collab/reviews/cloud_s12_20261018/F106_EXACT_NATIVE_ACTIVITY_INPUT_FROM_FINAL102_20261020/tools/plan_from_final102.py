"""Rebind106 to the locked actual102; never reuse the old106 human preview.
Only true prop/C110 fields are inherited. This file creates no character art.
"""
from pathlib import Path
import numpy as np,json,math,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F102_EXACT_NATIVE_ACTIVITY_actual_call01_20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=M/'candidate/F102.png';canvas=M/'actual_scene/F102_canvas.png'
assert sha(native)=='5dac76001f36f1714584533b01761395ffa7c91b6035c69dbf000791eebc709e'
assert sha(canvas)=='a54885a37a089e28d42b67c6b6512b7455c0b980a13c90d51c17e27f6eeb380b'
lock={'commit':'7dc826e12ccce49f26cfa6b747ebe630588e85e4','native_path':str(native),'native_SHA256':sha(native),'actual_Canvas_path':str(canvas),'actual_Canvas_SHA256':sha(canvas),'locked102_unchanged':True,'accepted_prior_coordinate_correction':'one whole-original affine, not uniform similarity; axis ratio difference about1.63745%'}
(O/'provenance/SOLE_FINAL102_MOTHER.json').write_text(json.dumps(lock,indent=2)+'\n')
old=json.loads((R/'F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020/geometry/F102_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text())['prop_plan']
C=json.loads((R/'geometry/three_key_pose_proposal.json').read_text())['states'][-1]
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def rigid(p,t,d):
 rr=rot(d);return np.c_[rr,np.asarray(t)-rr@np.asarray(p)]
def at(m,p):return np.asarray(m)@np.r_[p,1.]
# New visible proxies read on FINAL102, not the old nominal106 construction.
# Hidden shoulder/hip estimates remain visibly labelled estimates, not bone data.
hip=np.array([552.,852.]);knee=np.array([610.,1200.])
source={'R':{'shoulder':[540.,446.],'elbow':[584.,674.],'wrist':[825.,773.]},'L':{'shoulder':[592.,414.],'elbow':[659.,606.],'wrist':[755.,513.]}}
for r in source:source[r]['true_grip']=((np.array(old['rods'][r]['grip_scene'])-[275.,112.])/.7).tolist()
def make(frame):
 t=(frame-102)/8;turns=(frame-102)/4
 root=(1-t)*np.array(old['root_scene'])+t*np.array([1240.,550.]);plane=75+10*t;roll=(1-t)*old['projected_roll_degrees']
 pose={'angles':{k:(1-t)*v+t*C['code_pose']['angles'][k] for k,v in old['code_pose']['angles'].items()},'rootAngle':0,'facing':1}
 beta,alpha,theta=map(math.radians,[15,12,plane]);cam=np.array([[math.cos(beta),0,-math.sin(beta)],[-math.sin(alpha)*math.sin(beta),-math.cos(alpha),-math.sin(alpha)*math.cos(beta)],[math.cos(alpha)*math.sin(beta),-math.sin(alpha),math.cos(alpha)*math.cos(beta)]])
 basis=cam@np.array([[1.,0.],[0.,math.sin(theta)],[0.,math.cos(theta)]]);basis[:2]=rot(roll)@basis[:2];assert np.allclose(basis.T@basis,np.eye(2))
 ob=np.array(old['paper_3D_camera_basis']);Q=np.c_[basis,np.cross(basis[:,0],basis[:,1])]@np.c_[ob,np.cross(ob[:,0],ob[:,1])].T
 neck=np.array([152.55,58.05]);angle=0.
 for i in range(3):angle+=pose['angles']['neck'+str(i)];neck+=rot(math.degrees(angle))@np.array([28.35,0.])
 angle+=pose['angles']['neck3'];neck+=rot(math.degrees(angle))@np.array([10.,0.]);local={'R':[-75.,6.],'L':neck}
 ht=knee+rot(4*turns)@(hip-knee);UT=rigid(hip,ht,-3*turns);TH=rigid(knee,knee,6*turns);props={};arms={}
 for r in ['R','L']:
  prev=old['rods'][r];mu=prev['grip_fraction_from_hinge_unchanged'];h3=np.r_[root,0.]+.72*basis@np.array(local[r]);vec=Q@(np.array(prev['free_camera3D_scene_units'])-prev['hinge_camera3D_scene_units']);f3=h3+vec;g3=h3+mu*vec
  ov=np.array(prev['hinge_scene'])-prev['free_scene'];nv=-vec[:2];da=math.degrees(math.atan2(nv[1],nv[0])-math.atan2(ov[1],ov[0]));assert abs(np.linalg.norm(vec)-prev['physical_length_scene_units'])<1e-8
  props[r]={'part':prev['part'],'joint_local_mm':list(local[r]),'hinge_scene':h3[:2].tolist(),'hinge_camera3D_scene_units':h3.tolist(),'grip_scene':g3[:2].tolist(),'grip_camera3D_scene_units':g3.tolist(),'free_scene':f3[:2].tolist(),'free_camera3D_scene_units':f3.tolist(),'grip_fraction_from_hinge_unchanged':mu,'physical_length_H':prev['physical_length_H'],'physical_length_scene_units':prev['physical_length_scene_units'],'physical_length_camera3D_check':float(np.linalg.norm(vec)),'projected_length_new_scene':float(np.linalg.norm(vec[:2])),'projected_angle_delta_degrees':da}
  s,e,w,c=[np.array(source[r][k]) for k in ['shoulder','elbow','wrist','true_grip']];gt=(g3[:2]-[275.,112.])/.7;H=rigid(c,gt,da);wt=at(H,w);st=at(UT,s);us=float(np.linalg.norm(e-s));projected_upper_scale=1.;u=us*projected_upper_scale;f=float(np.linalg.norm(w-e));v=wt-st;d=float(np.linalg.norm(v));assert abs(u-f)<d<u+f
  al=(u*u-f*f+d*d)/(2*d);he=math.sqrt(u*u-al*al);v0=w-s;v1=e-s;sg=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1;et=st+al*v/d+sg*he*np.array([-v[1],v[0]])/d
  ad=lambda a,b:math.degrees(math.atan2(b[1],b[0])-math.atan2(a[1],a[0]));du=ad(e-s,et-st);dv=ad(w-e,wt-et)
  su=(e-s)/us;sn=np.array([-su[1],su[0]]);tu=(et-st)/u;tn=np.array([-tu[1],tu[0]]);ua=projected_upper_scale*np.outer(tu,su)+np.outer(tn,sn);UM=np.c_[ua,st-ua@s]
  arms[r]={'source_final102':source[r],'target':{'shoulder':st.tolist(),'elbow':et.tolist(),'wrist':wt.tolist(),'true_grip':gt.tolist()},'upper_reference_matrix':UM.tolist(),'upper_reference_matrix_kind':'rigid; actual upper projected segment retained','upper_projected_scale':projected_upper_scale,'physical_upper_bone_length_change':False,'far_depth_note':'Actual wrist line re-read behind jade on final102; earlier palm-interior proxy discarded. No shortening needed.' if r=='L' else None,'forearm_rigid_matrix':rigid(e,et,dv).tolist(),'whole_hand_bangle_same_rod_angle_matrix':H.tolist(),'upper_projected_proxy_length_source':us,'upper_projected_proxy_length_target':float(np.linalg.norm(et-st)),'forearm_projected_proxy_length_source':f,'forearm_projected_proxy_length_target':float(np.linalg.norm(wt-et)),'straight_reach_spare_native':u+f-d,'elbow_delta_native':(et-e).tolist(),'hand_scale':1,'wrist_articulation_delta_degrees':da-dv,'independent_finger_moves':0}
 return {'status':'F106_INPUT_ONLY_NO_GENERATION_PENDING_ACTUAL_GATE','frame':frame,'sole_locked102':lock,'new_visible_proxy_uncertainty':'15-25px sleeve-hidden shoulder/elbow/hip; wrists approx5px; not measured anatomical bone lengths','old106_human_preplan_reused':False,'hip_source_final102_proxy':hip.tolist(),'hip_target':ht.tolist(),'hip_delta_native':(ht-hip).tolist(),'knee_support_visible_proxy':knee.tolist(),'whole_torso_head_rise_degrees':-3*turns,'whole_torso_head_rigid_matrix':UT.tolist(),'thigh_rigid_matrix':TH.tolist(),'pose_choice':'Whole torso/collar/neck/head stand up together from accepted102. Far elbow remains at outer chest edge; both complete chains require actual visual gate, not reach-only approval.','arms':arms,'prop_plan':{'root_scene':root.tolist(),'paper_plane_inclination_degrees':plane,'projected_roll_degrees':roll,'code_pose':pose,'actual_makeCrane_scale':1.35,'paper_3D_camera_basis':basis.tolist(),'mm_to_scene_scale':.72,'rods':props,'C110_terminal':{'root_scene':[1240,550],'paper_plane_inclination_degrees':85},'legacy_frame114_not_used':True,'code_human_points_used':False,'true_physical_rod_3D_rotation':Q.tolist(),'camera_depth_feasible_model_not_measured':True},'new106_imagegen_calls':0,'new110_imagegen_calls':0,'actual106_person_Canvas':0}
g=make(106);light=make(110)
(O/'geometry/F106_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
(O/'qa/C110_SCALAR_ONLY_REBIND_AFTER106.json').write_text(json.dumps({'status':'SCALAR_C110_ONLY_NOT_AN_INPUT_TARGET','C110_must_rebind_after106_lock':True,'paper_degrees':85,'arms':{r:{'reachable':True,'straight_reach_spare_native':a['straight_reach_spare_native'],'upper_proxy_length':a['upper_projected_proxy_length_source'],'forearm_proxy_length':a['forearm_projected_proxy_length_source']} for r,a in light['arms'].items()},'imagegen_calls':0},indent=2)+'\n')
print(json.dumps({'hip_delta':g['hip_delta_native'],'paper':80,'root':g['prop_plan']['root_scene'],'arms':{r:{'elbow':a['target']['elbow'],'wrist':a['target']['wrist'],'wrist_articulation_delta':a['wrist_articulation_delta_degrees']} for r,a in g['arms'].items()}},indent=2))
