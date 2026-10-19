"""ONE whole-image similarity only. No anatomy/finger/shoe/source-pixel repair.
The target body remains reference only. Only actual call01 RGBA is adopted.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,math
from scipy.ndimage import distance_transform_edt,map_coordinates,binary_erosion
from scipy.optimize import minimize
O=Path(__file__).resolve().parents[1];R=O.parent;REF=R/'F074_COMPLETE_TARGET_from_LOCKED070_20261019'
assert not (O/'candidate/F074.png').exists(),'Do not repeat registered candidate creation'
raw=Image.open(O/'originals/F074_call01_raw.png').convert('RGBA');a=np.asarray(raw)
t=np.asarray(Image.open(REF/'anatomy/F074_COMPLETE_KNEELING_BODY_TARGET_REFERENCE_ONLY.png').convert('RGBA'))
sm=a[:,:,3]>=128;tm=t[:,:,3]>=128
edge=sm^binary_erosion(sm);y,x=np.where(edge);stride=max(1,len(x)//1500);p=np.c_[x[::stride],y[::stride]].astype(float)
D=distance_transform_edt(~tm)-distance_transform_edt(tm)
# These actual raw soft contact points are visual estimates (+/-3 native), NOT hidden joint measurements.
g=json.loads((REF/'geometry/F074_COMPLETE_BODY_AND_TRUE_CONTACTS.json').read_text())
far=np.array([964.4904490686764,842.8636454832905])+np.array([-3,-18])/.7
near=np.array([972.9918103860974,954.471411376163])+np.array([-3,-18])/.7
handRaw=np.array([[971.,808.],[981.,934.]]);handTarget=np.array([far,near]);weight=np.where(p[:,1]>1100,3.,1.)
def matrix(q):
 s,ang,tx,ty=q;r=math.radians(ang);return np.array([[s*math.cos(r),-s*math.sin(r),tx],[s*math.sin(r),s*math.cos(r),ty]])
def apply(pts,q):return np.c_[pts,np.ones(len(pts))]@matrix(q).T
def loss(q):
 z=apply(p,q);v=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100.)
 e=apply(handRaw,q)-handTarget
 return float(np.mean(weight*np.minimum(v*v,900))+2*np.sum(e*e))
fit=minimize(loss,[.96,0,15,25],method='Powell',bounds=[(.94,1.02),(-2,2),(-30,50),(-40,50)],options={'xtol':1e-7,'ftol':1e-9,'maxiter':250})
assert fit.success,fit.message
M=matrix(fit.x);inv=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2];im=raw.transform((1024,1536),Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);im.save(O/'candidate/F074.png')
# Foreground ownership from ACTUAL raw contours. These masks only partition, never move or repaint.
mask=Image.new('L',raw.size);dr=ImageDraw.Draw(mask)
polygons={'far_actual_curled_front_digits':[(944,795),(968,793),(985,801),(982,824),(969,836),(949,833),(930,824),(935,807)],'near_actual_curled_front_digits':[(980,891),(999,895),(1015,910),(1018,946),(1002,959),(981,952),(975,943),(978,931),(986,924),(984,907)]}
for poly in polygons.values():dr.polygon(poly,fill=255)
# Apply exactly the SAME whole-image matrix to ownership; nearest prevents duplicate alpha.
mask=mask.transform((1024,1536),Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST);own=np.asarray(mask)>0;n=np.asarray(im);fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
assert np.array_equal(np.maximum(bg,fg),n)
Image.fromarray(bg).save(O/'layers/F074_BG_person.png');Image.fromarray(fg).save(O/'layers/F074_FG_true_front_fingers.png');mask.save(O/'geometry/ACTUAL_RAW_FOREGROUND_OWNERSHIP_same_global_matrix.png')
z=apply(p,fit.x);dist=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100)
qa={'status':'ONE_WHOLE_SIMILARITY_CANDIDATE_FOR_REAL_CANVAS_NOT_POSE_PASS','raw_SHA256':hashlib.sha256((O/'originals/F074_call01_raw.png').read_bytes()).hexdigest(),'native_candidate_SHA256':hashlib.sha256((O/'candidate/F074.png').read_bytes()).hexdigest(),'one_whole_raw_to_native_matrix':M.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'translation_native':fit.x[2:].tolist(),'fit_objective':'Whole actual alpha128 silhouette weighted floor3 + PASSED actual070 grip soft-contact estimates translated with true props. Four global parameters only. Reference body pixels NEVER adopted. Actual070 grips already passed despite small soft-point-to-axis estimate residual; preserve actual relationship rather than inventing new palm points.','raw_soft_contacts_far_then_near':handRaw.tolist(),'target_passed070_soft_contacts_plus_rigid_delta':handTarget.tolist(),'registered_soft_contact_estimates':apply(handRaw,fit.x).tolist(),'contact_residual_native':(apply(handRaw,fit.x)-handTarget).tolist(),'contact_estimate_uncertainty_native':3,'lower_support_contour_absolute_distance_p95_native':float(np.quantile(abs(dist[p[:,1]>1100]),.95)),'old_support_RGBA_pixels_identical':False,'foreground_partition_only_polygons_raw':polygons,'exclusive_BG_FG_union_exact':True,'local_body_finger_shoe_warps':0,'source_reference_pixels_adopted':0,'raw_RGBA_material_edits':0,'actual_Canvas_pending':True}
(O/'geometry/WHOLE_RAW_REGISTRATION.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps({k:v for k,v in qa.items() if k not in ['foreground_partition_only_polygons_raw']},indent=2))
