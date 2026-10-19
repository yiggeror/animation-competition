"""One whole-raw joint fit: head/shoulders, waist, both grips, BOTH full knees.
No region is discarded after fitting; natural fixed-shin interfaces are checked
on the adopted pixels and actual Canvas. No local rescue or second mask trial.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,math
from scipy.ndimage import binary_erosion,binary_dilation,distance_transform_edt,map_coordinates
from scipy.optimize import minimize

O=Path(__file__).resolve().parents[1];R=O.parent;P=R/'F086_COMPLETE_TARGET_FROM_FINAL082_20261019';M=R/'F082_COMPLETE_PANTS_JOIN_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F086.png').exists(),'One joint registration already exists; no second attempt.'
rawpath=O/'originals/F086_call01_raw.png';assert sha(rawpath)=='ae2a835773684b21ff6b64ff4ce40b285338cc9a2c0544916670f2b941ec8bae'
raw=Image.open(rawpath).convert('RGBA');a=np.asarray(raw)
t=np.asarray(Image.open(P/'anatomy/F086_COMPLETE_VISIBLE_SOURCE_PIXEL_REFERENCE_ONLY.png').convert('RGBA'))
B=np.asarray(Image.open(M/'candidate/F082.png').convert('RGBA'))
fixed=np.asarray(Image.open(P/'masks/FINAL082_REAL_SHINS_ANKLES_SHOES_AND_EMPTY_FIXED.png').convert('L'))>0
adopt=~fixed;Y,X=np.mgrid[:1536,:1024]
sm=a[:,:,3]>=128;tm=t[:,:,3]>=128
edge=sm^binary_erosion(sm)
D=distance_transform_edt(~tm)-distance_transform_edt(tm)
groups={
 'head':edge&(Y<500),
 'shoulders_complete_arms':edge&(Y>=500)&(Y<780),
 'waist_hips':edge&(Y>=780)&(Y<1050)&(X<750),
 'BOTH_complete_knee_alpha_turns_and_fold_edges':edge&(Y>=1050)&(Y<=1340)&(X>330)}
sample={}
for key,mask in groups.items():
 y,x=np.where(mask);stride=max(1,len(x)//900);sample[key]=np.c_[x[::stride],y[::stride]].astype(float)
assert all(len(v)>30 for v in sample.values())
g=json.loads((P/'geometry/F086_FULL_RISE_BOTH_ARM_TRUE_PROP_AND_FIXED_SUPPORT_GEOMETRY.json').read_text());UA=np.asarray(g['whole_both_arms_closed_grips_native_matrix'])
oldsoft=json.loads((R/'F082_ACTIVE_actual_call01_20261019/geometry/ONE_WHOLE_REGISTRATION_FROZEN_OWNERSHIP_AND_PROTECTION.json').read_text())['registered_soft_contacts']
gripTarget=np.c_[np.asarray(oldsoft),np.ones(2)]@UA.T
# Actual visually read soft contact estimates, not hidden joints. Preserve the
# qualified palm-to-axis relationship rather than inventing a new pole dot.
gripRaw=np.array([[976.,643.],[992.,767.]])
waistRaw=np.array([[278.,831.],[617.,943.]])
waistTarget=np.array([[276.,839.],[614.,953.]])
def knee_points(mask):
 out=[]
 for lo,hi in [(1140,1240),(1250,1325)]:
  y,x=np.where(mask&(Y>=lo)&(Y<hi)&(X>450));mx=x.max();out.append([float(mx),float(y[x==mx].mean())])
 y,x=np.where(mask&(X>=450)&(X<=650));my=y.max();out.append([float(x[y==my].mean()),float(my)])
 return np.asarray(out)
kneeRaw=knee_points(sm);kneeTarget=knee_points(tm)
obligation={'status':'PREDECLARED_SINGLE_JOINT_GLOBAL_FIT_ALL_REGIONS_MANDATORY','regions':{k:len(v) for k,v in sample.items()},'raw_soft_grips_far_near':gripRaw.tolist(),'target_qualified_soft_grips_far_near':gripTarget.tolist(),'raw_visible_waist_hem_endpoints':waistRaw.tolist(),'target_visible_waist_hem_endpoints':waistTarget.tolist(),'raw_complete_far_near_knee_turn_and_ground_points':kneeRaw.tolist(),'target_complete_far_near_knee_turn_and_ground_points':kneeTarget.tolist(),'knee_error_never_ignored_because_generated_shins_not_adopted':True,'estimated_point_uncertainty_native':'soft grips about3px; waist/cloth turns about4to8px, not hidden bone measurements'}
(O/'geometry/PREDECLARED_JOINT_HEAD_WAIST_GRIPS_BOTH_KNEES_OBLIGATION.json').write_text(json.dumps(obligation,indent=2)+'\n')
def matrix(v):
 s,deg,tx,ty=v;r=math.radians(deg);return np.array([[s*math.cos(r),-s*math.sin(r),tx],[s*math.sin(r),s*math.cos(r),ty]])
def apply(p,v):return np.c_[p,np.ones(len(p))]@matrix(v).T
weights={'head':1.,'shoulders_complete_arms':1.,'waist_hips':1.,'BOTH_complete_knee_alpha_turns_and_fold_edges':2.}
def loss(v):
 e=0.
 for key,p in sample.items():
  z=apply(p,v);dist=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100.)
  e+=weights[key]*np.mean(np.minimum(dist*dist,2500.))
 e+=1.5*np.mean(np.sum((apply(gripRaw,v)-gripTarget)**2,axis=1))
 e+=.8*np.mean(np.sum((apply(waistRaw,v)-waistTarget)**2,axis=1))
 e+=1.2*np.mean(np.sum((apply(kneeRaw,v)-kneeTarget)**2,axis=1))
 return float(e)
fit=minimize(loss,[1.,0.,0.,0.],method='Powell',bounds=[(.94,1.03),(-2,2),(-25,40),(-25,40)],options={'xtol':1e-8,'ftol':1e-10,'maxiter':250})
assert fit.success,fit.message
F=matrix(fit.x);I=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2]
reg=raw.transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.BICUBIC);reg.save(O/'geometry/ONE_WHOLE_REGISTERED_RAW_NOT_WHOLE_ADOPTED.png');A=np.asarray(reg)
n=A.copy();n[fixed]=B[fixed]
# At most2native real fabric edge integration inside the reviewed activity,
# never copy/paste old bottom ink arc into the full newly drawn knee.
dist=distance_transform_edt(adopt);ground=np.asarray(Image.open(P/'masks/GROUND_GEOMETRY_ONLY_ALLOW_REAL_NEW_PEN_WITHIN_3PX.png').convert('L'))>0
join=adopt&(dist<2.01)&(Y>1030)&(A[:,:,3]>32)&(B[:,:,3]>32)&~binary_dilation(ground,iterations=3)
w=np.clip(dist/2,0,1)
for c in range(4):n[:,:,c][join]=np.uint8(np.rint(w[join]*A[:,:,c][join]+(1-w[join])*B[:,:,c][join]))
assert np.array_equal(n[fixed],B[fixed]);Image.fromarray(n).save(O/'candidate/F086.png')
Image.fromarray(np.uint8(adopt)*255).save(O/'geometry/REVIEWED_COMPLETE_KNEE_ACTIVITY_ADOPTION_DOMAIN.png');Image.fromarray(np.uint8(join)*255).save(O/'geometry/ONLY_2PX_FABRIC_EDGE_INSIDE_ACTIVITY.png')
active=n.copy();active[fixed]=0;static=np.zeros_like(n);static[fixed]=B[fixed]
Image.fromarray(active).save(O/'layers/F086_NEW_HEAD_BODY_ARMS_HIPS_THIGHS_FULL_KNEES_FOLDS.png');Image.fromarray(static).save(O/'layers/F086_FIXED_REAL082_SHINS_ANKLES_SHOES_AND_BLANK.png')
assert np.array_equal(np.maximum(active,static),n)

# Actual raw front curled digits only: one identical matrix for partition.
front=Image.new('L',raw.size);dr=ImageDraw.Draw(front)
poly={'far_LEFT_jade_front_curled_digits':[(941,631),(963,628),(981,635),(990,650),(986,670),(974,679),(954,676),(938,666),(933,652)],'near_RIGHT_bare_front_curled_digits':[(981,731),(1000,733),(1015,750),(1022,778),(1009,799),(992,805),(977,795),(978,779),(987,768),(984,749)]}
for p in poly.values():dr.polygon(p,fill=255)
front=front.transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.NEAREST);own=(np.asarray(front)>0)&adopt
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F086_BG_person.png');Image.fromarray(fg).save(O/'layers/F086_FG_true_front_fingers.png');front.save(O/'geometry/ACTUAL_RAW_FRONT_DIGITS_SAME_WHOLE_MATRIX.png');assert np.array_equal(np.maximum(bg,fg),n)

regionQA={}
for key,p in sample.items():
 z=apply(p,fit.x);d=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100.)
 regionQA[key]={'point_count':len(p),'mean_absolute_contour_error_native':float(abs(d).mean()),'p95_absolute_contour_error_native':float(np.quantile(abs(d),.95))}
interface=adopt&binary_dilation(fixed,iterations=5)&(Y>=1060)&(Y<=1316)&(t[:,:,3]>128)
missing=interface&(n[:,:,3]<32)
blank=fixed&(B[:,:,3]==0);changed=np.any(n!=B,axis=2)
proof={'status':'ONE_JOINT_GLOBAL_RAW_REGISTRATION_ALL_REGIONS_REPORTED_ACTUAL_CANVAS_PENDING','raw_SHA256':sha(rawpath),'native_SHA256':sha(O/'candidate/F086.png'),'one_whole_raw_to_native_matrix':F.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'translation_native':fit.x[2:].tolist(),'joint_fit_objective':obligation,'ALL_region_contour_results_no_dropped_knees':regionQA,
 'registered_soft_grips_far_near':apply(gripRaw,fit.x).tolist(),'soft_grip_residuals_native':(apply(gripRaw,fit.x)-gripTarget).tolist(),'registered_waist_endpoints':apply(waistRaw,fit.x).tolist(),'waist_residuals_native':(apply(waistRaw,fit.x)-waistTarget).tolist(),'registered_complete_knee_turn_and_ground_points':apply(kneeRaw,fit.x).tolist(),'complete_knee_turn_and_ground_residuals_native':(apply(kneeRaw,fit.x)-kneeTarget).tolist(),
 'natural_knee_shin_interface_expected_reference_alpha_missing_pixels_diagnostic_not_bone_proof':int(missing.sum()),'knees_or_interface_errors_dropped':False,
 'reviewed_adoption_domain_SHA256':sha(P/'masks/F086_COMPLETE_ACTIVITY_THROUGH_BOTH_ROUND_KNEES_AND_FOLDS.png'),'domain_pixels':int(adopt.sum()),'changed_RGBA_pixels':int(changed.sum()),'outside_activity_RGBA_changes':int(changed[fixed].sum()),'fixed_native_shins_shoes_blank_RGBA_changes':0,'protected_blank_pixels':int(blank.sum()),'new_alpha_leaks_in_protected_blank':int(np.count_nonzero(n[:,:,3][blank])),
 'edge_transition_pixels_inside_activity':int(join.sum()),'ground_ink_arc_copied_back':False,'separate_head_arm_knee_shin_foot_warps':0,'reference_body_pixels_adopted_as_new_art':0,'post_registration_mask_trials':0,'imagegen_calls':1,'actual086_Canvas':0,'next090_calls':0,'raw_front_digit_ownership_polygons':poly}
(O/'geometry/ONE_JOINT_WHOLE_REGISTRATION_COMPLETE_KNEES_AND_STATIC_PROTECTION.json').write_text(json.dumps(proof,indent=2)+'\n')
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
def solid(a):
 z=Image.new('RGBA',(1024,1536),'#e1e4e6');z.alpha_composite(Image.fromarray(a));return z.convert('RGB')
solid(n).crop((150,780,760,1360)).save(O/'diagnostics/ACTUAL_NATIVE_WAIST_FULL_BOTH_KNEES_FIXED_SHINS_1to1.png')
board=Image.new('RGB',(1830,620),'#e1e4e6');d=ImageDraw.Draw(board)
for i,(name,a) in enumerate([('APPROVED086 source-pixel target',t),('JOINT REGISTERED sole true raw',A),('ADOPTED full knees + fixed shins',n)]):board.paste(solid(a).crop((150,780,760,1360)),(610*i,40));d.text((610*i+8,10),name,font=font(18),fill='#25313b')
board.save(O/'diagnostics/SAME_NATIVE_TARGET_REGISTERED_RAW_ADOPTED_COMPLETE_KNEES.png')
print(json.dumps({k:v for k,v in proof.items() if k not in ['joint_fit_objective','raw_front_digit_ownership_polygons']},indent=2))
