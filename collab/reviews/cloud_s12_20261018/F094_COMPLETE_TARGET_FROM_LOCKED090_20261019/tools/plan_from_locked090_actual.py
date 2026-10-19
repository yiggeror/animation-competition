"""094 planning: final actual090 only; no old construction human geometry.
True code-puppet fields/physical rod lengths only are read from frozen C.
"""
from pathlib import Path
import numpy as np,json,math,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent
old=json.loads((R/'F090_COMPLETE_TARGET_FROM_FINAL086_20261019/geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())['prop_plan']
C=json.loads((R/'geometry/three_key_pose_proposal.json').read_text())['states'][-1]
actual=json.loads((R/'F090_TWO_ARMS_LOCAL_actual_call01_20261019/geometry/ONE_COMPLETE_LOCAL_PATCH_REGISTRATION_AND_ALL_RESIDUALS.json').read_text())
locked=json.loads((O/'provenance/SOLE_LOCKED090_MOTHER.json').read_text());assert hashlib.sha256(Path(locked['native_path']).read_bytes()).hexdigest()==locked['native_SHA256']
shifts={'R':[14.086744,.620598],'L':[-14.038403,2.519830]}
source={r:{k:(np.asarray(actual['all_shoulder_elbow_wrist_true_grip_residuals'][r+'_'+k]['registered'])+shifts[r]).tolist() for k in ['shoulder','elbow','wrist','true_grip']} for r in ['R','L']}
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def rigid(p,t,d):
 rr=rot(d);return np.c_[rr,np.asarray(t)-rr@np.asarray(p)]
def at(m,p):return np.asarray(m)@np.r_[p,1.]
hip=np.array([429.1659790128363,890.0949751477058]);knee=np.array([610.,1200.]);hipt=knee+rot(6)@(hip-knee)
torso=rigid(hip,hipt,-3);thigh=rigid(knee,knee,6)
t=.2;root=(1-t)*np.asarray(old['root_scene'])+t*np.array([1240.,550.]);plane=65.;roll=(1-t)*old['projected_roll_degrees']
pose={'angles':{k:(1-t)*v+t*C['code_pose']['angles'][k] for k,v in old['code_pose']['angles'].items()},'rootAngle':0,'facing':1}
beta=math.radians(15);alpha=math.radians(12);theta=math.radians(plane)
cam=np.array([[math.cos(beta),0,-math.sin(beta)],[-math.sin(alpha)*math.sin(beta),-math.cos(alpha),-math.sin(alpha)*math.cos(beta)],[math.cos(alpha)*math.sin(beta),-math.sin(alpha),math.cos(alpha)*math.cos(beta)]])
basis=cam@np.array([[1.,0.],[0.,math.sin(theta)],[0.,math.cos(theta)]]);basis[:2]=rot(roll)@basis[:2];assert np.allclose(basis.T@basis,np.eye(2))
neck=np.array([152.55,58.05]);a=0.
for i in range(3):a+=pose['angles']['neck'+str(i)];neck+=rot(math.degrees(a))@np.array([28.35,0.])
a+=pose['angles']['neck3'];neck+=rot(math.degrees(a))@np.array([10.,0.])
local={'R':np.array([-75.,6.]),'L':neck};K=.72
# Whole physical rod vectors follow the actual paper 3D orientation change.
# No old code-person C hand/elbow coordinates are used.
oldbasis=np.asarray(old['paper_3D_camera_basis'])
oldframe=np.c_[oldbasis,np.cross(oldbasis[:,0],oldbasis[:,1])]
newframe=np.c_[basis,np.cross(basis[:,0],basis[:,1])]
Q=newframe@oldframe.T;assert np.allclose(Q.T@Q,np.eye(3))
props={};arms={};origin=np.array([275.,112.])
for r in ['R','L']:
 prev=old['rods'][r];mu=prev['grip_fraction_from_hinge_unchanged'];h3=np.r_[root,0.]+K*basis@local[r];h=h3[:2]
 vec=Q@(np.asarray(prev['free_camera3D_scene_units'])-np.asarray(prev['hinge_camera3D_scene_units']))
 f3=h3+vec;g3=h3+mu*vec;f=f3[:2];g=g3[:2];length=prev['physical_length_scene_units'];projected=float(np.linalg.norm(f-h))
 assert abs(np.linalg.norm(f3-h3)-length)<1e-8
 oldv=np.asarray(prev['hinge_scene'])-np.asarray(prev['free_scene']);newv=h-f
 da=math.degrees(math.atan2(newv[1],newv[0])-math.atan2(oldv[1],oldv[0]))
 props[r]={'part':prev['part'],'joint_local_mm':local[r].tolist(),'hinge_scene':h.tolist(),'hinge_camera3D_scene_units':h3.tolist(),'grip_scene':g.tolist(),'grip_camera3D_scene_units':g3.tolist(),'free_scene':f.tolist(),'free_camera3D_scene_units':f3.tolist(),'grip_fraction_from_hinge_unchanged':mu,'physical_length_H':prev['physical_length_H'],'physical_length_scene_units':length,'physical_length_camera3D_check':float(np.linalg.norm(f3-h3)),'projected_length_previous_scene':prev['projected_length_new_scene'],'projected_length_new_scene':projected,'projected_angle_delta_degrees':da,'camera_depth_solution_is_feasible_not_measured':True}
 s,e,w,c=[np.asarray(source[r][k]) for k in ['shoulder','elbow','wrist','true_grip']];gn=(g-origin)/.7;hand=rigid(c,gn,da);wt=at(hand,w);st=at(torso,s)
 u=float(np.linalg.norm(e-s));ff=float(np.linalg.norm(w-e));v=wt-st;d=float(np.linalg.norm(v));assert abs(u-ff)<d<u+ff,(r,'no natural reach',d,u,ff)
 along=(u*u-ff*ff+d*d)/(2*d);height=math.sqrt(u*u-along*along);v0=w-s;v1=e-s;branch=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1
 et=st+along*v/d+branch*height*np.array([-v[1],v[0]])/d
 angle=lambda a,b:math.degrees(math.atan2(b[1],b[0])-math.atan2(a[1],a[0]))
 U=rigid(s,st,angle(e-s,et-st));V=rigid(e,et,angle(w-e,wt-et))
 assert et[0]<e[0],(r,'not elbow retraction',et,e)
 arms[r]={'source_actual090':source[r],'target':{'shoulder':st.tolist(),'elbow':et.tolist(),'wrist':wt.tolist(),'true_grip':gn.tolist()},'upper_rigid_matrix':U.tolist(),'forearm_rigid_matrix':V.tolist(),'whole_hand_bangle_same_rod_angle_matrix':hand.tolist(),'upper_projected_proxy_length_source':u,'upper_projected_proxy_length_target':float(np.linalg.norm(et-st)),'forearm_projected_proxy_length_source':ff,'forearm_projected_proxy_length_target':float(np.linalg.norm(wt-et)),'elbow_delta_native':(et-e).tolist(),'hand_scale':1,'no_independent_finger_moves':True}
plan={'status':'UNIQUE094_INPUT_TARGET_ONLY_NO_GENERATION','frame':94,'sole_locked090':locked,'source_actual090_visible_arm_proxies':source,'proxy_uncertainty_native':'15-25px for sleeve-hidden shoulder/elbow/hip; not hidden anatomical measurements','hip_source_actual090_visual_proxy':hip.tolist(),'hip_target':hipt.tolist(),'hip_delta_native':(hipt-hip).tolist(),'knee_support_actual090_visual_proxy':knee.tolist(),'thigh_proxy_rise_degrees':6,'whole_torso_head_rise_degrees':-3,'torso_head_rigid_matrix':torso.tolist(),'thigh_rigid_matrix':thigh.tolist(),'arms':arms,'prop_plan':{'root_scene':root.tolist(),'root_source_locked090':old['root_scene'],'paper_plane_inclination_degrees':plane,'projected_roll_degrees':roll,'code_pose':pose,'actual_makeCrane_scale':1.35,'paper_3D_camera_basis':basis.tolist(),'mm_to_scene_scale':K,'rods':props,'C110_terminal':{'root':[1240,550],'paper_plane_inclination':85},'legacy_C_table_frame114_is_not_used_user_frozen_terminal_is110':True,'human_points_from_old_code_table_used':False,'whole_physical_hand_rod_group_3D_rotation_from_locked090':Q.tolist(),'no_old_code_human_grip_coordinates':True,'camera_depth_is_feasible_model_not_measured':True},'new094_imagegen_calls':0,'actual094_full_Canvas':0}
(O/'geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'hip_delta':plan['hip_delta_native'],'root':root.tolist(),'paper':plane,'elbow_deltas':{r:a['elbow_delta_native'] for r,a in arms.items()},'grips_scene':{r:p['grip_scene'] for r,p in props.items()}},indent=2))
