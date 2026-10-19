"""Authorized same-raw full distal-arm rotation; no new drawing or imagegen."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,binary_dilation,distance_transform_edt
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent
raw=P/'originals/F018_raw_call01.png';a=np.array(Image.open(raw));assert hashlib.sha256(raw.read_bytes()).hexdigest()=='fbc502639b90de00eb0b664a41af7898df15e92bf5d58ac9e172579121b486a3'
H,W=a.shape[:2];yy,xx=np.indices((H,W));X=np.stack([xx+.5,yy+.5],2);E=np.array([770.,836.]);axis=np.array([.878,.479]);axis/=np.linalg.norm(axis)
# Observed visible elbow-body cross-section midpoint, not the older construction skeleton.
# Source forearm + bangle + entire palm/all digits. Polygon only isolates the actual native silhouette.
pts=[(713,751),(742,778),(778,800),(829,834),(854,842),(876,855),(900,869),(950,874),(980,886),(1012,907),(1015,936),(1003,947),(999,964),(978,970),(954,965),(931,950),(908,938),(879,927),(849,925),(815,899),(776,883),(738,868),(712,853),(687,834),(674,805)]
im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(pts,fill=255);poly=binary_dilation(np.array(im)>0,iterations=8)
# Preserve AA attached to the real silhouette, omit transparent RGB and remote alpha noise.
core=poly&(a[:,:,3]>=8);physical=poly&binary_dilation(core,iterations=2)&(a[:,:,3]>0)
source=a.astype(float)/255;source[~physical]=0;prem=source[:,:,:3]*source[:,:,3,None];u=(X-E)@axis
A=json.loads((S/'geometry/three_key_pose_proposal.json').read_text())['states'][0]['points_scene']
def gaps(mask):
 ys,xs=np.nonzero(mask);p=np.stack([xs+.5,ys+.5],1)*.7+[275,112];res={}
 for key,endpoint in [('L','P_neck'),('R','P_body')]:
  start=np.array(A['free_grip'+key]);end=np.array(A[endpoint]);v=end-start;t=np.clip(((p-start)@v)/(v@v),0,1);d=np.linalg.norm(p-(start+t[:,None]*v),axis=1)-3.5-.7*np.sqrt(2)/2;i=np.argmin(d);res[key]={'min_gap_to_nominal_7px_scene':float(d[i]),'nearest_native_pixel':[int(xs[i]),int(ys[i])],'actual_outer_AA_pixels':len(xs)}
 return res
trials=[]
for degrees in [3.5,3.75,4.0,4.25,4.5,4.75,5.0,5.25]:
 theta=np.deg2rad(degrees);p=X.copy()
 # Invert q = E + R(-theta*smoothstep(u))* (p-E) to retain a single continuous elbow contour.
 for _ in range(16):
  su=(p-E)@axis;v=np.clip((su+18.)/36.,0,1);ang=theta*v*v*(3-2*v);c=np.cos(ang);s=np.sin(ang);dx=X[:,:,0]-E[0];dy=X[:,:,1]-E[1];p=np.stack([E[0]+c*dx-s*dy,E[1]+s*dx+c*dy],2)
 coords=[p[:,:,1]-.5,p[:,:,0]-.5];wa=map_coordinates(source[:,:,3],coords,order=1,mode='constant',cval=0);wr=np.stack([map_coordinates(prem[:,:,i],coords,order=1,mode='constant',cval=0) for i in range(3)],2)
 result=np.zeros_like(a);result[:,:,3]=np.rint(np.clip(wa,0,1)*255).astype(np.uint8);result[:,:,:3]=np.clip(np.rint(np.divide(wr,wa[:,:,None],out=np.zeros_like(wr),where=wa[:,:,None]>1e-9)*255),0,255).astype(np.uint8)
 # Only replace the old/new actual distal silhouette and a 2px AA guard; everything else stays raw.
 active_old=physical&(u>-18.);active_new=(result[:,:,3]>0)&(((p-E)@axis)>-18.);clear_old=poly&(a[:,:,3]>0)&(u>-18.);domain=binary_dilation(active_old|active_new|clear_old,iterations=2)&(u>-20.)
 out=a.copy();out[domain]=result[domain]
 # At unmoved proximal boundary, exact source reinstatement avoids any extraction edge change.
 out[(u<=-18.)&physical]=a[(u<=-18.)&physical]
 changed=np.any(out!=a,2);phys_out=(physical&~domain)|((out[:,:,3]>0)&domain)
 gap=gaps(phys_out);trials.append({'angle_deg':degrees,'outer_AA_nominal_7px_gap':gap,'criterion':'native prescreen only; actual Canvas raster gate follows'})
 if gap['L']['min_gap_to_nominal_7px_scene']>=3.8:break
assert gap['L']['min_gap_to_nominal_7px_scene']>=3.8,trials
assert not np.any(changed&~domain)
Image.fromarray(out).save(O/'candidate/F018_geometry_only.png')
for name,m in [('source_far_arm_physical_alpha_support',physical),('geometry_edit_domain',domain),('geometry_actual_RGBA_changed',changed),('corrected_far_arm_physical_alpha_support',phys_out)]:Image.fromarray(m.astype(np.uint8)*255).save(O/f'masks/{name}.png')
y,x=np.nonzero(domain);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];np.savez_compressed(O/'provenance/inverse_geometry_map.npz',destination_bbox_xyxy=np.array(bbox),source_xy_pixel_centres=p[bbox[1]:bbox[3],bbox[0]:bbox[2]],elbow_pivot=E,distal_axis=axis,angle_deg=degrees,blend_u_bounds=np.array([-18.,18.]))
metadata={'source_raw_SHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'visible_elbow_pivot_native':E.tolist(),'pivot_basis':'Manual midpoint of actual visible arm body around native x770, y836 in actual elbow grid; hidden shoulder/construction E not substituted. Estimate, not an X-ray joint measurement.','distal_axis_native':axis.tolist(),'chosen_raise_counterclockwise_deg':degrees,'joint_blend_native_u_bounds':[-18,18],'full_distal_rigid_from_u':18,'whole_forearm_bangle_palm_all_digits_one_mapping':True,'finger_or_wrist_separate_transforms':0,'source_polygon_native':pts,'source_polygon_guard_dilation_native_px':8,'cleared_vacated_source_alpha1to7_pixels':int(np.count_nonzero((a[:,:,3]>0)&(a[:,:,3]<8)&(out[:,:,3]==0)&domain)),'source_AA_rule':'Actual alpha>0 attached within2px to alpha>=8 in isolated real forearm silhouette. Remote alpha/RGB are not transformed.','inverse_iterations':16,'resampling':'single inverse premultiplied RGBA bilinear sampling; elbow short smoothstep angle transition only','spatial_identity_outside_domain':True,'geometry_RGBA_changed_pixels':int(changed.sum()),'edit_domain_bbox':bbox,'native_outer_AA_gap_prescreen':gap,'trials':trials,'rendered_scene_frames':0,'imagegen_calls':0,'rigid_length_scale':1.0,'rotation_determinant':1.0,'note':'Native mask/analytic rod prescreen is not final actual Canvas acceptance.'}
(O/'qa/native_geometry_repair.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps({k:metadata[k] for k in ['visible_elbow_pivot_native','chosen_raise_counterclockwise_deg','geometry_RGBA_changed_pixels','native_outer_AA_gap_prescreen','trials']},indent=2))
