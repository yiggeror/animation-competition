"""ONE whole raw similarity; fixed074 support ownership includes empty pixels.
No limb/finger/shoe warps; only actual new raw activity pixels are adopted.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
from scipy.ndimage import distance_transform_edt,map_coordinates,binary_erosion
from scipy.optimize import minimize

O=Path(__file__).resolve().parents[1];R=O.parent
REF=R/'F082_ACTIVE_TARGET_FIXED074_SUPPORTS_20261019'
M=R/'F078_NARROW_JOIN_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F082.png').exists(),'Single registered adoption already exists; no second trial.'
rawpath=O/'originals/F082_call01_raw.png'
assert sha(rawpath)=='1e2a0674f404054874c3b0ebef3370662d8dedc708fc73d7353ab492f8175afc'
raw=Image.open(rawpath).convert('RGBA');a=np.asarray(raw)
t=np.asarray(Image.open(REF/'anatomy/F082_COMPLETE_VISIBLE_REFERENCE_ONLY.png').convert('RGBA'))
B=np.asarray(Image.open(M/'candidate/F078.png').convert('RGBA'))
maskpath=REF/'masks/F082_ACTIVE_UPPER_BOTH_THIGHS_AND_MOVING_KNEE_CONNECTOR.png'
assert sha(maskpath)=='416356ffa3248330be4d334e9366ec5beb3d062a1369d0b15347683cd5f3ca8b'
adopt=np.asarray(Image.open(maskpath).convert('L'))>0
fixed=~adopt
sm=a[:,:,3]>=128;tm=t[:,:,3]>=128
edge=sm^binary_erosion(sm)
# Fit the activity silhouette only. Generated lower legs/shoes cannot pull
# the registration or change the permanent original074 support placement.
edge[1030:]=False
y,x=np.where(edge);stride=max(1,len(x)//1800)
pts=np.c_[x[::stride],y[::stride]].astype(float)
D=distance_transform_edt(~tm)-distance_transform_edt(tm)
g=json.loads((REF/'geometry/F082_COMPLETE_ACTIVE_RISE_TRUE_CONTACTS_AND_SUPPORT_DOMAIN.json').read_text())
U=np.asarray(g['one_upper_rigid_native_matrix'])
accepted=json.loads((R/'F078_COMPLETE_actual_call01_20261019/geometry/WHOLE_RAW_REGISTRATION.json').read_text())['registered_soft_contact_estimates']
handTarget=np.c_[np.asarray(accepted),np.ones(2)]@U.T
# Raw soft palm/shaft-facing points read from the sole raw coordinate crop.
# They preserve the preceding PASSED relative soft-contact placement; not
# invented hidden joints or a new requirement for contact on an axis dot.
handRaw=np.array([[979.,702.],[987.,824.]])
def matrix(q):
    s,ang,tx,ty=q;r=math.radians(ang)
    return np.array([[s*math.cos(r),-s*math.sin(r),tx],[s*math.sin(r),s*math.cos(r),ty]])
def apply(p,q):return np.c_[p,np.ones(len(p))]@matrix(q).T
def loss(q):
    z=apply(pts,q)
    v=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100.)
    e=apply(handRaw,q)-handTarget
    return float(np.mean(np.minimum(v*v,400))+3*np.sum(e*e))
fit=minimize(loss,[1.,0.,0.,0.],method='Powell',bounds=[(.98,1.02),(-1,1),(-15,15),(-15,15)],options={'xtol':1e-8,'ftol':1e-10,'maxiter':220})
assert fit.success,fit.message
Mraw=matrix(fit.x);inv=np.linalg.inv(np.vstack([Mraw,[0,0,1]]))[:2]
registered=raw.transform((1024,1536),Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC)
registered.save(O/'geometry/WHOLE_RAW_REGISTERED_CONTEXT_NOT_WHOLE_ADOPTED.png')
reg=np.asarray(registered)
# Predeclared semantic activity ownership is applied to EVERY RGBA pixel,
# including background. A new shoe cannot leak into fixed transparent space.
n=reg.copy();n[fixed]=B[fixed]
# A 2-native-pixel fabric join transition ONLY inside the approved active
# domain and where both actual source fabrics are visible. No mask expansion,
# new pants patch, shape repair, alpha growth, or movement of fixed supports.
distance=distance_transform_edt(adopt)
Y,X=np.mgrid[:1536,:1024]
join=adopt&(distance<2.01)&(Y>1030)&(reg[:,:,3]>16)&(B[:,:,3]>16)
weight=np.clip(distance/2,0,1)
for i in range(4):
    v=n[:,:,i].copy()
    v[join]=np.uint8(np.rint(weight[join]*reg[:,:,i][join]+(1-weight[join])*B[:,:,i][join]))
    n[:,:,i]=v
assert np.array_equal(n[fixed],B[fixed])
Image.fromarray(n).save(O/'candidate/F082.png')
active=n.copy();active[fixed]=0
static=np.zeros_like(n);static[fixed]=B[fixed]
Image.fromarray(active).save(O/'layers/F082_ACTIVE_NEW_UPPER_HIPS_BOTH_THIGHS_TRUE_JOIN.png')
Image.fromarray(static).save(O/'layers/F082_FIXED074_STATIC_SUPPORTS_INCLUDING_EMPTY.png')
Image.fromarray(np.uint8(adopt)*255).save(O/'geometry/FROZEN_ACTIVE_ADOPTION_DOMAIN.png')
Image.fromarray(np.uint8(join)*255).save(O/'geometry/TWO_NATIVE_EDGE_TRANSITION_INSIDE_ACTIVE_ONLY.png')

# Actual raw curled front digits: ownership partition only, same whole matrix.
fgMask=Image.new('L',raw.size);dr=ImageDraw.Draw(fgMask)
polygons={
 'far_LEFT_jade_front_curled_digits':[(939,693),(955,687),(976,693),(985,705),(984,720),(971,728),(950,725),(935,715)],
 'near_RIGHT_bare_front_curled_digits':[(985,778),(1003,782),(1015,798),(1015,826),(1004,844),(985,850),(974,839),(978,824),(985,817),(981,804)]}
for p in polygons.values():dr.polygon(p,fill=255)
fgMask=fgMask.transform((1024,1536),Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST)
own=(np.asarray(fgMask)>0)&adopt
fg=np.zeros_like(n);fg[own]=n[own]
bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F082_BG_person.png')
Image.fromarray(fg).save(O/'layers/F082_FG_true_front_fingers.png')
fgMask.save(O/'geometry/RAW_FRONT_DIGIT_OWNERSHIP_SAME_WHOLE_MATRIX.png')
assert np.array_equal(np.maximum(bg,fg),n)
visible=(n[:,:,3]>0)
union=np.maximum(active,static)
assert np.array_equal(union,n)
assert not np.any((active[:,:,3]>0)&(static[:,:,3]>0))
fixedblank=fixed&(B[:,:,3]==0)
changed=np.any(n!=B,axis=2)
proof={'status':'ONE_WHOLE_REGISTERED_ACTIVITY_ADOPTION_ONE_REAL_CANVAS_PENDING_NOT_POSE_PASS',
 'raw_SHA256':sha(rawpath),'native_SHA256':sha(O/'candidate/F082.png'),
 'one_whole_raw_to_native_matrix':Mraw.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'translation_native':fit.x[2:].tolist(),
 'fit_activity_only':'actual alpha128 contour y<1030 plus actual raw soft palms targeting preceding qualified078 palms under approved082 rigid upper transform; no generated lower support coordinates in fit',
 'raw_soft_contact_far_then_near':handRaw.tolist(),'preceding_qualified_actual078_soft_contacts':accepted,'target_soft_contacts_from_qualified078_same_rigid_transform':handTarget.tolist(),'registered_soft_contacts':apply(handRaw,fit.x).tolist(),'soft_contact_residual_native':(apply(handRaw,fit.x)-handTarget).tolist(),'soft_contact_estimate_uncertainty_native':3,
 'frozen_adoption_mask_SHA256':sha(maskpath),'frozen_adoption_pixels':int(adopt.sum()),'mask_expanded_or_changed':False,'new_activity_RGBA_changed_pixels':int(changed[adopt].sum()),'outside_active_RGBA_changed_pixels':int(changed[fixed].sum()),
 'fixed_support_coordinate_scale_identity':True,'fixed_static_region_ALL_RGBA_exact_including_empty':True,'fixed_transparent_blank_pixels':int(fixedblank.sum()),'new_alpha_leaks_in_fixed_blank_pixels':int(np.count_nonzero(n[:,:,3][fixedblank])),
 'edge_transition_width_native':2,'edge_transition_pixels_inside_active_only':int(join.sum()),'edge_transition_outside_active':int((join&fixed).sum()),
 'new_generated_shins_shoes_adopted_in_fixed_domain':0,'reference_person_pixels_adopted_as_new_art':0,'raw_RGBA_edits':0,'separate_body_finger_knee_shin_shoe_warps':0,
 'active_static_exclusive_RGBA_reconstruction_differences':0,'BG_FG_exclusive_RGBA_reconstruction_differences':0,'front_digit_partition_raw_polygons_only':polygons,
 'imagegen_calls':1,'actual082_Canvas':0,'next_posture_imagegen_calls':0}
(O/'geometry/ONE_WHOLE_REGISTRATION_FROZEN_OWNERSHIP_AND_PROTECTION.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:v for k,v in proof.items() if k!='front_digit_partition_raw_polygons_only'},indent=2))
