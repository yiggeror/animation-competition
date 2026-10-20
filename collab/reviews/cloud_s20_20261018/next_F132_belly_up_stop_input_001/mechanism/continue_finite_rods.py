"""F132 continuation of the accepted finite mechanism; no person motion guess."""
from pathlib import Path
import json,math,hashlib
import numpy as np
F=Path(__file__).resolve().parent; P=F.parents[1]
D=json.loads((F/'source_model_probe.json').read_text())
G=json.loads((P/'F128_two_domains_close_zero_call_001/scene_config.json').read_text())
v=D['camera_basis'];C=np.array(v['C']);fw=np.array(v['fwd']);right=np.array(v['right']);up=np.array(v['up']);focal=v['focal']
reg=G['reg'];base=np.array(reg['base_world_m']);pm=np.array(D['people_to_CAM20_matrix'])
project=lambda p:np.array([960+np.dot(np.array(p)-C,right)/np.dot(np.array(p)-C,fw)*focal,540-np.dot(np.array(p)-C,up)/np.dot(np.array(p)-C,fw)*focal])
master=lambda p:np.linalg.solve(np.array([[pm[0],pm[2]],[pm[1],pm[3]]]),np.array(p)-pm[4:])
root=np.array(G['frames']['128']['root'])+np.array(D['states']['132']['source_root_m'])-np.array(D['states']['128']['source_root_m'])
def endpoint(rootxz,pt):
    q=project([rootxz[0],.004,rootxz[1]]);qx=project([rootxz[0]+.1,.004,rootxz[1]]);qy=project([rootxz[0],.004,rootxz[1]+.1])
    return q+(qx-q)*(-pt[0]/100)+(qy-q)*(pt[1]/100)
def sheetworld(p):
    ray=fw+right*((p[0]-960)/focal)+up*((540-p[1])/focal)
    return C+ray*((.004-C[1])/ray[1])
rows=[];circles=[];gripcircles={}
for old in G['frames']['128']['rods']:
    id=old['id'];a_screen=endpoint(root,D['states']['132']['points'][id]);aw=sheetworld(a_screen)
    # Verify the continuation calculator exactly reproduces the adopted128
    # skin endpoint before using the same rule at132.
    a128=master(endpoint(np.array(G['frames']['128']['root']),D['states']['128']['points'][id]))
    assert np.linalg.norm(a128-np.array(old['A_master']))<1e-8
    bw=np.array(old['B_world']);length=old['candidate_A_B_length_m']
    h=np.dot(aw-base,fw);center=aw-h*fw;rho2=length*length-h*h
    row={'id':id,'holder':old['holder'],'part':old['part'],'at':old['at'],
         'A_master':master(a_screen).tolist(),'A_screen':a_screen.tolist(),
         'A_world_effective':aw.tolist(),'candidate_A_B_length_m':length,
         'sphere_hand_plane_radius_squared_m2':float(rho2)}
    if rho2>=0:
        radius=math.sqrt(rho2);direction=bw-center;direction-=fw*np.dot(direction,fw)
        closest=center+radius*direction/np.linalg.norm(direction);bp=master(project(closest))
        row.update({'B_world':closest.tolist(),'B_master':bp.tolist(),
                    'delta_from128_grip_master':(bp-old['B_master']).tolist(),
                    'length_error_m':float(np.linalg.norm(closest-aw)-length),
                    'meaning':'Closest unchanged-length solution to adopted128 grip on the SAME whole-person card plane; not adopted132 contact.'})
        angles=np.linspace(0,2*math.pi,721)
        world=center+radius*(np.cos(angles)[:,None]*right+np.sin(angles)[:,None]*up)
        pixels=np.array([master(project(q)) for q in world]);gripcircles[id]=pixels.tolist()
        shoulder=np.array([552.,428.]) if id=='T_H' else np.array([671.,468.])
        circles.append({'id':id,'all_B132_master_bbox':[pixels.min(0).tolist(),pixels.max(0).tolist()],
                        'all_B132_world_y_range_m':[float(world[:,1].min()),float(world[:,1].max())],
                        'minimum_observed128_shoulder_to_any132_grip_px':float(np.linalg.norm(pixels-shoulder,axis=1).min()),
                        'observed128_shoulder':shoulder.tolist()})
    rows.append(row)
# Read actual native128 bones as 2D references only. They are NOT certified
# physical 3D limb lengths, so this does not prove all staging is impossible.
chains=[{'side':'R','shoulder':[552.,428.],'elbow':[518.,462.],'wrist':[442.,434.],
         'grip':G['frames']['128']['rods'][0]['B_master']},
        {'side':'L','shoulder':[671.,468.],'elbow':[650.,526.],'wrist':[514.,535.],
         'grip':G['frames']['128']['rods'][1]['B_master']}]
for chain,circle,row in zip(chains,circles,rows):
    q=np.array([chain[k] for k in ['shoulder','elbow','wrist','grip']]);lengths=np.linalg.norm(np.diff(q,axis=0),axis=1)
    chain['observed_projected_segment_lengths']=lengths.tolist();chain['sum_projected_arm_hand_reference_px']=float(lengths.sum())
    chain['minimum_distance_to_whole132_grip_circle_px']=circle['minimum_observed128_shoulder_to_any132_grip_px']
    chain['shortfall_with128_shoulder_and_projected_lengths_px']=float(chain['minimum_distance_to_whole132_grip_circle_px']-lengths.sum())
    chain['tolerance_for_visual_landmarks_px']=4
    chain['not_a_3D_bone_certification']=True
out={'status':'F132_CONTACT_REACH_GATE_BLOCKED_UNDER_CURRENT128_CARD_REFERENCE',
     'new_image_calls':0,'source128_commit':'34781f2253181eb5feee39a23099b15dd721370c',
     'root132_same_registration_plus_original128_to132_delta':root.tolist(),
     'original_pose132':D['states']['132']['pose'],'flip_fraction132':D['states']['132']['flip_fraction'],
     'rows':rows,'complete_grip_circle_audit':circles,'actual128_2D_chain_references':chains,
     'no_finite_intersection_extension_used':True,'no_new_pose_or_shoulder_shift_authorized_or_assumed':True,
     'specific_missing_gate':'Need an explicit F132 T_H-to-R contact/reach continuation within accepted staging. Current same-card circle is remote from128 arm and has world y<0 throughout. Do not choose a new torso action, card-depth rule, rod length, root or registration automatically.',
     'not_universal_impossibility_claim':'2D projected-chain check constrains current continuous construction only; changing body staging/depth or foreshortening needs an explicit gate, not a false claim of3D bone impossibility.'}
(F/'finite_F132_preflight.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(F/'all_possible_F132_B_circles.json').write_text(json.dumps(gripcircles,ensure_ascii=False)+'\n')
print(json.dumps({'status':out['status'],'rows':rows,'chains':chains},ensure_ascii=False,indent=2))
