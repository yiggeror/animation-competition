"""F090 geometry proposal from qualified REAL086 pixels and genuine code props.
No old construction human pose/bones are used. Actual visible arm endpoints
are uncertain2D proxies; true code rod physical lengths remain frozen.
"""
from pathlib import Path
import json,numpy as np,math,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F086_COMPLETE_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(M/'candidate/F086.png')=='dd59078c720c39aef411fd3c5ee12a09f18b9dd85ba69376c2d2481205a6e8be'
old=json.loads((R/'F086_COMPLETE_TARGET_FROM_FINAL082_20261019/geometry/F086_FULL_RISE_BOTH_ARM_TRUE_PROP_AND_FIXED_SUPPORT_GEOMETRY.json').read_text())['true_points_target_F086']
frozen=json.loads((R/'geometry/three_key_pose_proposal.json').read_text());A,C=frozen['states'][0],frozen['states'][2]
t=1/6
pose={'angles':{k:(1-t)*A['code_pose']['angles'][k]+t*C['code_pose']['angles'][k] for k in A['code_pose']['angles']},'rootAngle':0,'facing':1}
def R2(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
hip=np.array([415.,925.]);knee=np.array([610.,1200.]);hipt=knee+R2(6)@(hip-knee);RT=R2(-5);tt=hipt-RT@hip;UT=np.c_[RT,tt]
root=(1-t)*np.asarray(old['crane_root'])+t*np.array([1240.,550.])
tilt=60.;roll=-8*(1-t);beta=math.radians(15);alpha=math.radians(12);theta=math.radians(tilt)
camera=np.array([[math.cos(beta),0,-math.sin(beta)],[-math.sin(alpha)*math.sin(beta),-math.cos(alpha),-math.sin(alpha)*math.cos(beta)],[math.cos(alpha)*math.sin(beta),-math.sin(alpha),math.cos(alpha)*math.cos(beta)]])
plane=np.array([[1.,0.],[0.,math.sin(theta)],[0.,math.cos(theta)]])
basis=camera@plane;basis[:2]=R2(roll)@basis[:2]
assert np.allclose(basis.T@basis,np.eye(2))
neck=np.array([152.55,58.05]);angle=0.
for i in range(3):
 angle+=pose['angles']['neck'+str(i)];neck+=R2(math.degrees(angle))@np.array([28.35,0.])
angle+=pose['angles']['neck3'];neck+=R2(math.degrees(angle))@np.array([10.,0.])
locals={'R':np.array([-75.,6.]),'L':neck}
grips={'R':np.array([948.,653.]),'L':(1-t)*np.asarray(old['far_grip'])+t*np.asarray(C['points_scene']['gripL'])}
props={};K=.72;Hunit=215.
for role in ['R','L']:
 hh=np.asarray(old['body_hinge' if role=='R' else 'neck3_hinge']);ff=np.asarray(old['body_free' if role=='R' else 'neck3_free']);gg=np.asarray(old['near_grip' if role=='R' else 'far_grip'])
 mu=float(np.dot(gg-hh,ff-hh)/np.dot(ff-hh,ff-hh));assert np.linalg.norm(hh+mu*(ff-hh)-gg)<1e-8
 hinge3=np.r_[root,0.]+K*basis@locals[role];hinge=hinge3[:2];grip=grips[role];free=hinge+(grip-hinge)/mu
 length=float(A['rod_lengths_H'][role]*Hunit);projected=float(np.linalg.norm(free-hinge));assert projected<length,(role,projected,length)
 # Feasible camera-depth branch, not a claim of measured hidden depth.
 depth=-math.sqrt(length*length-projected*projected)
 free3=np.r_[free,hinge3[2]+depth];grip3=hinge3+mu*(free3-hinge3)
 assert abs(np.linalg.norm(free3-hinge3)-length)<1e-9
 oldang=math.degrees(math.atan2((hh-ff)[1],(hh-ff)[0]));newang=math.degrees(math.atan2((hinge-free)[1],(hinge-free)[0]));da=newang-oldang
 props[role]={'part':'BODY' if role=='R' else 'NECK3','joint_local_mm':locals[role].tolist(),'hinge_scene':hinge.tolist(),'hinge_camera3D_scene_units':hinge3.tolist(),'grip_scene':grip.tolist(),'grip_camera3D_scene_units':grip3.tolist(),'free_scene':free.tolist(),'free_camera3D_scene_units':free3.tolist(),'grip_fraction_from_hinge_unchanged':mu,'physical_length_H':float(A['rod_lengths_H'][role]),'physical_length_scene_units':length,'physical_length_camera3D_check':float(np.linalg.norm(free3-hinge3)),'physical_length_mm':length/K,'projected_length_previous_scene':float(np.linalg.norm(ff-hh)),'projected_length_new_scene':projected,'projected_angle_delta_degrees':da,'camera_depth_solution_is_feasible_not_measured':True}

origin=np.array([275.,112.]);arms={}
# Visible centers read on the actual086 grid; these are projected illustration
# references, not old code-human pose coordinates or hidden anatomical bones.
source={'R':{'shoulder':[505.,550.],'elbow':[729.,710.],'wrist':[935.,779.]},'L':{'shoulder':[530.,520.],'elbow':[738.,603.],'wrist':[897.,639.]}}
def rigid_map(p,q,angle):
 rot=R2(angle);return np.c_[rot,np.asarray(q)-rot@np.asarray(p)]
def at(M,p):return M@np.r_[p,1.]
for role in ['R','L']:
 s,e,w=[np.asarray(source[role][k]) for k in ['shoulder','elbow','wrist']]
 grip0=(np.asarray(old['near_grip' if role=='R' else 'far_grip'])-origin)/.7;grip1=(grips[role]-origin)/.7
 hand=rigid_map(grip0,grip1,props[role]['projected_angle_delta_degrees']);wt=at(hand,w);st=at(UT,s)
 u=float(np.linalg.norm(e-s));f=float(np.linalg.norm(w-e));v=wt-st;d=float(np.linalg.norm(v));assert abs(u-f)<d<u+f
 direction=v/d;perp=np.array([-direction[1],direction[0]]);a=(u*u-f*f+d*d)/(2*d);h=math.sqrt(max(0,u*u-a*a));v0=w-s;v1=e-s;branch=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1
 et=st+a*direction+branch*h*perp
 au=math.degrees(math.atan2((et-st)[1],(et-st)[0])-math.atan2((e-s)[1],(e-s)[0]));af=math.degrees(math.atan2((wt-et)[1],(wt-et)[0])-math.atan2((w-e)[1],(w-e)[0]))
 upper=rigid_map(s,st,au);fore=rigid_map(e,et,af)
 assert np.allclose(at(upper,e),et) and np.allclose(at(fore,w),wt)
 assert et[0]<e[0],'Target must visibly begin elbow retraction.'
 arms[role]={'role':'nearRIGHTbare_BODY' if role=='R' else 'farLEFTjade_NECK3','source':source[role],'target':{'shoulder':st.tolist(),'elbow':et.tolist(),'wrist':wt.tolist(),'true_grip':grip1.tolist()},'source_true_grip':grip0.tolist(),'upper_arm_projected_proxy_length_source':u,'upper_arm_projected_proxy_length_target':float(np.linalg.norm(et-st)),'forearm_projected_proxy_length_source':f,'forearm_projected_proxy_length_target':float(np.linalg.norm(wt-et)),'upper_matrix':upper.tolist(),'forearm_matrix':fore.tolist(),'whole_closed_hand_matrix_same_rod_angle':hand.tolist(),'elbow_delta_native':(et-e).tolist(),'no_independent_finger_warp':True}
elbowsep=float(np.linalg.norm(np.asarray(arms['R']['target']['elbow'])-arms['L']['target']['elbow']))
g={'status':'F090_VISIBLE_GEOMETRY_PROPOSAL_ONLY_NO_NEW_DRAWING','sole_final086':{'commit':'7eba0f67b074a5508b15531611f493b620ae3767','path':str(M/'candidate/F086.png'),'SHA256':sha(M/'candidate/F086.png'),'actual_Canvas_SHA256':sha(M/'actual_scene/F086_canvas.png')},'hip_source_visual_proxy':hip.tolist(),'knee_support_visual_proxy':knee.tolist(),'hip_target':hipt.tolist(),'hip_delta_native':(hipt-hip).tolist(),'thigh_proxy_rotation_degrees':6,'whole_torso_head_rise_degrees':-5,'torso_head_native_matrix':UT.tolist(),'arms_actual_source_projected_proxies_not_hidden_bones':arms,'target_elbow_centers_separation_native':elbowsep,'person_proxy_uncertainty_native':'about15to25px; visible source-pixel articulation, not3D bone certification',
 'prop_plan':{'root_scene':root.tolist(),'root_source_final086':old['crane_root'],'root_remaining_to_C110':[1240-root[0],550-root[1]],'paper_plane_inclination_degrees':tilt,'projected_roll_degrees':roll,'code_pose':pose,'code_pose_progress_to_C':t,'actual_makeCrane_scale':1.35,'paper_3D_camera_basis':basis.tolist(),'mm_to_scene_scale':K,'rods':props,'physical_lengths_frozen_not_arbitrary_projected_scaling':True,'camera_depth_branch_note':'one feasible exact-length solution; depth is not measured from art','C110_terminal':{'root':[1240,550],'paper_plane_inclination':85}},'source_model_calls':0,'actual090_full_Canvas':0,'new094_model_calls':0}
(O/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps({'hip_target':hipt.tolist(),'hip_delta':(hipt-hip).tolist(),'root':root.tolist(),'elbows':{r:arms[r]['target']['elbow'] for r in arms},'elbow_deltas':{r:arms[r]['elbow_delta_native'] for r in arms},'elbow_separation_native':elbowsep,'grips':{r:props[r]['grip_scene'] for r in props},'physical_vs_projected_rods':{r:[props[r]['physical_length_scene_units'],props[r]['projected_length_new_scene']] for r in props}},indent=2))
