"""Actual original-model / original-camera F120 -> F128 geometry preflight."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image
from scipy.optimize import root
F=Path(__file__).resolve().parent;P=F.parents[1]
D=json.loads((F/'source_model_probe.json').read_text());BASIS=D['camera_basis'];C=np.array(BASIS['C']);fwd=np.array(BASIS['fwd']);right=np.array(BASIS['right']);up=np.array(BASIS['up']);focal=BASIS['focal'];reg=D['approved_people_registration'];base=np.array(reg['base_world_m']);pm=np.array(D['people_to_CAM20_matrix']);ids=['T_H','T_S']
project=lambda p:np.array([960+np.dot(np.array(p)-C,right)/np.dot(np.array(p)-C,fwd)*focal,540-np.dot(np.array(p)-C,up)/np.dot(np.array(p)-C,fwd)*focal])
screen=lambda p:np.array([pm[0]*p[0]+pm[2]*p[1]+pm[4],pm[1]*p[0]+pm[3]*p[1]+pm[5]])
def master(p):return np.linalg.solve(np.array([[pm[0],pm[2]],[pm[1],pm[3]]]),np.array(p)-pm[4:])
def handworld(p):return base+right*((p[0]-reg['ox'])/reg['pixels_per_cm']/100)+up*((reg['oy']-p[1])/reg['pixels_per_cm']/100)
def cardpoint(rootxz,pointmm):
 q0=project([rootxz[0],.004,rootxz[1]]);qx=project([rootxz[0]+.1,.004,rootxz[1]]);qy=project([rootxz[0],.004,rootxz[1]+.1]);return q0+(qx-q0)*(-pointmm[0]/100)+(qy-q0)*(pointmm[1]/100)
def rayplane(p):
 ray=fwd+right*((p[0]-960)/focal)+up*((540-p[1])/focal);return C+ray*((.004-C[1])/ray[1])
source=P/'next_F120_passive_decay_input_001/generation_001/F120_uniform_registered_upper_fixed_full_lower_candidate.png';A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];r,g,b=A[:,:,:3].astype(float).transpose(2,0,1);wood=(A[:,:,3]>160)&(r>140)&(g>70)&(r>g+15)&(b<g*.8)
axes=[]
for xs,guess in [(range(251,329),lambda x:580-.475*x),(range(280,333),lambda x:1.05*x+42)]:
 pts=[]
 for xcol in xs:
  ys=np.flatnonzero(wood[:,xcol]&(abs(np.arange(H)-guess(xcol))<9))
  if len(ys)>=3:pts.append([xcol,float(np.median(ys))])
 assert len(pts)>35
 m,b0=np.polyfit(np.array(pts)[:,0],np.array(pts)[:,1],1);axes.append([float(m),float(b0)])
def onaxis(p,mb):
 m,b0=mb;q=np.array([p[0],m*p[0]+b0]);v=np.array([1.,m]);return q+v*np.dot(np.array(p)-q,v)/np.dot(v,v)
pins=[onaxis([395.5969615931523,391.9163010277811],axes[0]),onaxis([433.82592856936486,497.25733241893283],axes[1])]
states=D['states'];raw0=states['120'];raw1=states['128']
def ends(rootxz,raw):return [master(cardpoint(rootxz,raw['points'][id])) for id in ids]
def error(rt):return [(q[1]-m*q[0]-b0)/math.hypot(1,m) for q,(m,b0) in zip(ends(rt,raw0),axes)]
sol=root(error,raw0['source_root_m']);assert sol.success and np.linalg.norm(error(sol.x))<1e-6
root0=sol.x;root1=root0+np.array(raw1['source_root_m'])-np.array(raw0['source_root_m'])
rows=[]
for i,id in enumerate(ids):
 p0=cardpoint(root0,raw0['points'][id]);p1=cardpoint(root1,raw1['points'][id]);a0=rayplane(p0);a1=rayplane(p1);b0=handworld(pins[i]);length=np.linalg.norm(b0-a0);h=np.dot(a1-base,fwd);center=a1-h*fwd;rho2=length*length-h*h;row={'id':id,'part':D['bindings'][id]['part'],'at':D['bindings'][id]['at'],'source_grip_master':pins[i].tolist(),'source_axis':axes[i],'A120_master':master(p0).tolist(),'A128_master':master(p1).tolist(),'A120_world_effective':a0.tolist(),'A128_world_effective':a1.tolist(),'B120_world':b0.tolist(),'rigid_rod_length_m':float(length),'hand_plane_sphere_radius_squared':float(rho2)}
 if rho2>=0:
  v=b0-center;v-=fwd*np.dot(v,fwd);b1=center+math.sqrt(rho2)*v/np.linalg.norm(v);newpin=master(project(b1));row.update({'B128_world':b1.tolist(),'grip128_master':newpin.tolist(),'grip_delta_master':(newpin-pins[i]).tolist(),'length_error_m':float(np.linalg.norm(b1-a1)-length)})
 rows.append(row)
out={'status':'PRELIMINARY_GEOMETRY_NOT_PRODUCTION_RENDER','new_image_calls':0,'scene_renders':0,'camera':D['camera'],'original_turtle_scale':D['turtle_scale'],'source120_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'axis120':axes,'root120_registered_from_passed_axes':root0.tolist(),'root128_same_registration_plus_original_puppet_delta':root1.tolist(),'root_solver_residual_master':error(root0),'original_pose_roll_angle120':raw0['pose']['rootAngle'],'original_pose_roll_angle128':raw1['pose']['rootAngle'],'flip_fraction128':raw1['flip_fraction'],'rows':rows,'old_cross_remap_used':False,'card_endpoint_rule':'Original sheetM affine projection; effective sheet-world point from that actual skin-point ray. Raw millimetre FK and camera preserved.'}
a,b=[np.array(r['A128_master']) for r in rows];ra,rb=[np.array(r['grip128_master']) for r in rows];v=ra-a;w=rb-b;tv,uv=np.linalg.solve(np.column_stack([v,-w]),b-a);cross=a+tv*v
out['minimal_grip_solution_audit']={'axis_intersection_master':cross.tolist(),'distance_to_R_grip_px':float(np.linalg.norm(cross-ra)),'distance_to_L_grip_px':float(np.linalg.norm(cross-rb)),'head_attachment_to_R_intersection_parameter':float(tv),'shell_attachment_to_L_intersection_parameter':float(uv),'intersection_is_on_A_to_B_of_both_original_renderer_rods':bool(0<=tv<=1 and 0<=uv<=1),'single_grip_crossing_gate_passed':False,'note':'This closest-hand candidate is a preflight failure, not proof that all registrations/hand branches are impossible.'}
(F/'constraint_preflight.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'flip_fraction128':out['flip_fraction128'],'audit':out['minimal_grip_solution_audit']},ensure_ascii=False))
