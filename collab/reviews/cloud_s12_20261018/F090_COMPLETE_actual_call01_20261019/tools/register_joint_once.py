"""Sole raw090: one joint whole-image similarity, frozen support adoption.
No local warps, mask search, reference arm pixels or second model call.
All head/waist/arm/grip/knee residuals remain reportable even on failure.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json, hashlib, math
from scipy.ndimage import binary_erosion, distance_transform_edt, map_coordinates, binary_dilation
from scipy.optimize import minimize

O=Path(__file__).resolve().parents[1]; R=O.parent
P=R/'F090_COMPLETE_TARGET_FROM_FINAL086_20261019'; M=R/'F086_COMPLETE_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F090.png').exists(), 'Sole registration already exists; no repeat'
rawpath=O/'originals/F090_call01_raw.png'
assert sha(rawpath)=='92e284d7afce8ee6bfa6fb9bd596d00911dfcf7538082e4445b5f95538848108'
assert sha(M/'candidate/F086.png')=='dd59078c720c39aef411fd3c5ee12a09f18b9dd85ba69376c2d2481205a6e8be'
raw=Image.open(rawpath).convert('RGBA'); a=np.asarray(raw)
t=np.asarray(Image.open(P/'anatomy/F090_COMPLETE_VISIBLE_PERSON_REFERENCE_ONLY.png').convert('RGBA'))
B=np.asarray(Image.open(M/'candidate/F086.png').convert('RGBA'))
fixed=np.asarray(Image.open(P/'masks/REAL086_SHINS_ANKLES_SHOES_AND_BLANK_FIXED.png').convert('L'))>0
adopt=~fixed; Y,X=np.mgrid[:1536,:1024]
g=json.loads((P/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())
# Manual visible illustration proxies; sleeve-hidden joints have 15-25px uncertainty.
points={
 'head_top':([590,84],[588,125],1.),
 'head_visible_ear':([544,294],[533,320],1.),
 'head_chin':([678,360],[645,385],1.),
 'waist_back_hem':([293,858],[263,801],1.),
 'waist_front_hem':([705,1014],[645,943],1.),
 'hip_visible_proxy':([445,980],g['hip_target'],1.),
 'far_full_knee_turn':([788,1323],[691,1197],2.),
 'near_full_knee_turn':([740,1413],[658,1267],2.),
 'loaded_knee_bottom':([658,1452],[568,1316],2.)}
source={'R':{'shoulder':[520,526],'elbow':[683,793],'wrist':[880,880],'true_grip':[974,855]},
        'L':{'shoulder':[548,490],'elbow':[681,686],'wrist':[848,678],'true_grip':[948,678]}}
for role in ['R','L']:
 for k,src in source[role].items():
  points[role+'_'+k]=(src,g['arms_actual_source_projected_proxies_not_hidden_bones'][role]['target'][k],3. if k=='true_grip' else 1.)
sm=a[:,:,3]>=128; tm=t[:,:,3]>=128
edge=sm^binary_erosion(sm); D=distance_transform_edt(~tm)-distance_transform_edt(tm)
regions={'head':edge&(Y<420),'complete_shoulders_both_arms':edge&(Y>=420)&(Y<930),
         'waist_hips':edge&(Y>=800)&(Y<1160)&(X<760),
         'BOTH_full_knees_and_shin_interfaces':edge&(Y>=1160)&(Y<1480)&(X>330)}
sample={}
for k,m in regions.items():
 y,x=np.where(m); sample[k]=np.c_[x[::max(1,len(x)//700)],y[::max(1,len(x)//700)]].astype(float)
obligation={'status':'SINGLE_JOINT_WHOLE_RAW_FIT_ALL_REGIONS_PREDECLARED',
 'source_raw_SHA256':sha(rawpath),'frozen_input_commit':'330c3a8bc48af08e41557cfef994340e3e03891d',
 'visible_points_raw_target_weight':points,'all_region_samples':{k:len(v) for k,v in sample.items()},
 'uncertainty':'grips about4px; knee cloth turns about8px; sleeve-hidden shoulder/elbow proxies15-25px; not hidden bone measurements',
 'no_dropped_knee_or_elbow_residuals':True,'frozen_adoption_mask_SHA256':sha(P/'masks/REAL086_SHINS_ANKLES_SHOES_AND_BLANK_FIXED.png')}
(O/'geometry/PREDECLARED_SINGLE_JOINT_FIT_ALL_POINTS.json').write_text(json.dumps(obligation,indent=2)+'\n')
def matrix(v):
 s,d,tx,ty=v; q=math.radians(d);return np.array([[s*math.cos(q),-s*math.sin(q),tx],[s*math.sin(q),s*math.cos(q),ty]])
def at(p,v):return np.c_[p,np.ones(len(p))]@matrix(v).T
def loss(v):
 e=0.
 for k,p in sample.items():
  z=at(p,v);d=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=200.)
  e+=(1.5 if 'knees' in k else 1.)*float(np.mean(np.minimum(d*d,10000.)))
 for src,dst,w in points.values():e+=w*float(np.sum((at(np.array([src]),v)[0]-dst)**2))/len(points)*3.
 return e
fit=minimize(loss,[.91,0.,30.,0.],method='Powell',bounds=[(.8,1.06),(-6,6),(-120,160),(-120,160)],options={'xtol':1e-7,'ftol':1e-9,'maxiter':200})
assert fit.success,fit.message
F=matrix(fit.x);I=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2]
reg=raw.transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.BICUBIC)
reg.save(O/'geometry/ONE_WHOLE_REGISTERED_RAW_NOT_WHOLE_ADOPTED.png');A=np.asarray(reg)
n=A.copy();n[fixed]=B[fixed]
Image.fromarray(n).save(O/'candidate/F090.png')
active=n.copy();active[fixed]=0;static=np.zeros_like(n);static[fixed]=B[fixed]
Image.fromarray(active).save(O/'layers/F090_NEW_COMPLETE_ACTIVITY.png')
Image.fromarray(static).save(O/'layers/F090_FIXED_REAL086_SUPPORT.png')
# Only actual raw front fingers; same whole matrix, no finger adjustment.
poly={'far_LEFT_jade_front_digits':[(934,650),(951,649),(964,666),(965,690),(954,713),(939,720),(925,710),(926,689)],
      'near_RIGHT_bare_front_digits':[(952,820),(970,820),(983,837),(988,868),(975,892),(957,899),(941,884),(940,865)]}
front=Image.new('L',raw.size);dr=ImageDraw.Draw(front)
for q in poly.values():dr.polygon(q,fill=255)
front=front.transform(raw.size,Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.NEAREST)
own=(np.asarray(front)>0)&adopt;fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F090_BG_person.png');Image.fromarray(fg).save(O/'layers/F090_FG_true_front_fingers.png')
assert np.array_equal(np.maximum(bg,fg),n) and np.array_equal(n[fixed],B[fixed])
results={}
for k,(src,dst,w) in points.items():
 z=at(np.asarray([src]),fit.x)[0];d=z-dst
 results[k]={'registered':z.tolist(),'target':dst,'residual_native':d.tolist(),'distance_native':float(np.linalg.norm(d)),'distance_scene':float(.7*np.linalg.norm(d))}
contours={}
for k,p in sample.items():
 z=at(p,fit.x);d=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=200.)
 contours[k]={'mean_absolute_error_native':float(abs(d).mean()),'p95_absolute_error_native':float(np.quantile(abs(d),.95))}
changed=np.any(n!=B,axis=2);blank=fixed&(B[:,:,3]==0)
interface=adopt&binary_dilation(fixed,iterations=5)&(Y>=1060)&(Y<=1316)&(t[:,:,3]>128)
proof={'status':'ACTUAL_SOLE_RAW_JOINT_REGISTRATION_REVIEW_REQUIRED_NO_AUTO_QUALIFICATION','raw_SHA256':sha(rawpath),'native_SHA256':sha(O/'candidate/F090.png'),
 'one_whole_raw_to_native_matrix':F.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),
 'all_point_results_no_dropped_knees_elbows':results,'all_contour_results':contours,
 'changed_RGBA_pixels':int(changed.sum()),'outside_activity_RGBA_changes':int(changed[fixed].sum()),'fixed_support_RGBA_changes':0,
 'new_alpha_in_protected_blank':int(np.count_nonzero(n[:,:,3][blank])),
 'reference_knee_interface_expected_alpha_missing_pixels_diagnostic':int((interface&(n[:,:,3]<32)).sum()),
 'whole_registration_count':1,'separate_region_warps':0,'post_registration_mask_trials':0,'reference_source_pixels_adopted_as_new_activity':0,
 'raw_alpha_preserved_except_whole_resampling_and_frozen_support_ownership':True,
 'background_RGB_below_zero_alpha_not_visible_halo':True,'native_support_master':'FINAL_ACTUAL086','imagegen_calls':1,'actual090_Canvas':0,'next094_calls':0,
 'actual_raw_front_digit_ownership':poly}
(O/'geometry/ONE_JOINT_REGISTRATION_ALL_RESIDUALS_AND_SUPPORT.json').write_text(json.dumps(proof,indent=2)+'\n')
def solid(a):
 q=Image.new('RGBA',(1024,1536),'#e1e4e6');q.alpha_composite(Image.fromarray(a));return q.convert('RGB')
solid(n).save(O/'diagnostics/ACTUAL090_REGISTERED_AND_FIXED_SUPPORT_GREY.png')
board=Image.new('RGB',(1536,808),'#e1e4e6');dr=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for i,(name,img) in enumerate([('Frozen090 target reference',t),('Sole raw / ONE whole registration',A),('Actual candidate + fixed supports',n)]):
 board.paste(solid(img).resize((512,768)),(i*512,40));dr.text((i*512+8,12),name,font=font,fill='black')
board.save(O/'diagnostics/TARGET_WHOLE_REGISTERED_RAW_ACTUAL_SIDE_BY_SIDE.png')
print(json.dumps({'matrix':F.tolist(),'native_SHA256':proof['native_SHA256'],'grips_scene_residuals':{r:results[r+'_true_grip']['distance_scene'] for r in ['R','L']},'knees_native_residuals':{k:v['distance_native'] for k,v in results.items() if 'knee' in k},'fixed_RGBA_changes':0,'interface_missing_pixels':proof['reference_knee_interface_expected_alpha_missing_pixels_diagnostic']},indent=2))
