"""One joint whole-raw094 similarity, all required regions retained in review.
Native fixed090 support only. No local elbow/hand/knee rescues or new request.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,math
from scipy.ndimage import binary_erosion,distance_transform_edt,map_coordinates
from scipy.optimize import minimize
O=Path(__file__).resolve().parents[1];R=O.parent;P=R/'F094_COMPLETE_TARGET_FROM_LOCKED090_20261019';M=R/'F090_SAME_RAW_SEMANTIC_OWNERSHIP_FIXED_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F094.png').exists(),'One094 whole registration exists; no repeat'
rawpath=O/'originals/F094_call01_raw.png';assert sha(rawpath)=='c02b78a2d69977c0ea1776f3645a341c03ddb22a4fd2698c303e557f72342d04'
raw=Image.open(rawpath).convert('RGBA');A0=np.asarray(raw);B=np.asarray(Image.open(M/'candidate/F090.png').convert('RGBA'));T=np.asarray(Image.open(P/'anatomy/F094_COMPLETE_VISIBLE_REFERENCE_ONLY.png').convert('RGBA'));Y,X=np.mgrid[:1536,:1024]
fixed=np.asarray(Image.open(P/'masks/LOCKED090_REAL_SHINS_ANKLES_SHOES_BLANK_FIXED.png').convert('L'))>0;g=json.loads((P/'geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())
points={'head_top':([620.,55.],[620.,77.],1.),'head_visible_ear':([596.,265.],[557.,282.],1.),'chin':([716.,320.],[675.,328.],1.),
 'hip_visible_proxy':([555.,945.],g['hip_target'],2.),'waist_back_hem':([399.,829.],[341.,771.],1.),'waist_front_hem':([783.,979.],[691.,910.],1.),
 'far_complete_knee_turn':([852.,1320.],[721.,1218.],2.),'near_complete_knee_turn':([825.,1410.],[685.,1295.],2.),'knee_loaded_bottom':([700.,1454.],[616.,1316.],2.)}
source={'R':{'shoulder':[588.,480.],'elbow':[657.,730.],'wrist':[866.,839.],'true_grip':[941.,840.]},
        'L':{'shoulder':[628.,456.],'elbow':[771.,671.],'wrist':[891.,642.],'true_grip':[980.,666.]}}
for r in ['R','L']:
 for k,v in source[r].items():points[r+'_'+k]=(v,g['arms'][r]['target'][k],4. if k=='true_grip' else 1.)
sm=A0[:,:,3]>=128;tm=T[:,:,3]>=128;edge=sm^binary_erosion(sm);D=distance_transform_edt(~tm)-distance_transform_edt(tm)
regions={'head':edge&(Y<410),'complete_shoulders_both_arm_chains':edge&(Y>=410)&(Y<900),
 'waist_hips':edge&(Y>=800)&(Y<1150)&(X>350)&(X<900),'BOTH_complete_round_knees_upper_shin_returns':edge&(Y>=1150)&(Y<1470)&(X>360)}
samples={}
for k,q in regions.items():
 y,x=np.where(q);stride=max(1,len(x)//800);samples[k]=np.c_[x[::stride],y[::stride]].astype(float)
pre={'status':'ONE_JOINT_WHOLE094_HEAD_SHOULDERS_HIP_BOTH_GRIPS_BOTH_KNEES','raw_SHA256':sha(rawpath),'raw_visible_points_target_weights':points,
 'all_regions_required':{k:len(v) for k,v in samples.items()},'uncertainty_native':'grasp approx4px; visible knee turns approx8px; hidden sleeve/hip proxy15-25px, not bone measurement',
 'fixed_domain_SHA256':sha(P/'masks/LOCKED090_REAL_SHINS_ANKLES_SHOES_BLANK_FIXED.png'),'knees_never_dropped_because_generated_shins_not_adopted':True}
(O/'geometry/PREDECLARED_ONE_JOINT_ALL_REGIONS.json').write_text(json.dumps(pre,indent=2)+'\n')
def mat(v):
 s,a,tx,ty=v;a=math.radians(a);return np.array([[s*math.cos(a),-s*math.sin(a),tx],[s*math.sin(a),s*math.cos(a),ty]])
def at(p,v):return np.c_[p,np.ones(len(p))]@mat(v).T
def loss(v):
 total=0.
 for k,p in samples.items():
  q=at(p,v);dd=map_coordinates(D,[q[:,1],q[:,0]],order=1,mode='constant',cval=200.);total+=(1.5 if 'knees' in k else 1.)*float(np.mean(np.minimum(dd*dd,14400.)))
 total+=3*sum(w*float(np.sum((at(np.asarray([s]),v)[0]-t)**2)) for s,t,w in points.values())/len(points)
 return total
fit=minimize(loss,[.91,0.,0.,5.],method='Powell',bounds=[(.8,1.06),(-6,6),(-120,160),(-120,160)],options={'xtol':1e-7,'ftol':1e-9,'maxiter':200});assert fit.success,fit.message
F=mat(fit.x);inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2];reg=raw.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);reg.save(O/'geometry/ONE_WHOLE_REGISTERED_RAW_NOT_WHOLE_ADOPTED.png');A=np.asarray(reg)
n=A.copy();n[fixed]=B[fixed];Image.fromarray(n).save(O/'candidate/F094.png');assert np.array_equal(n[fixed],B[fixed])
frontpolys={'L':[(957,638),(983,637),(998,657),(999,684),(983,710),(958,712),(947,693),(953,674)],
 'R':[(924,798),(949,796),(967,817),(969,845),(955,865),(935,872),(915,859),(916,838)]}
front=Image.new('L',raw.size);d=ImageDraw.Draw(front)
for p in frontpolys.values():d.polygon(p,fill=255)
front=front.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST);own=(np.asarray(front)>0)&~fixed;fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F094_BG_person.png');Image.fromarray(fg).save(O/'layers/F094_FG_true_front_fingers.png');assert np.array_equal(np.maximum(bg,fg),n)
res={}
for k,(s,t,w) in points.items():
 z=at(np.asarray([s]),fit.x)[0];dd=z-t;res[k]={'registered':z.tolist(),'target':t,'residual_native':dd.tolist(),'distance_native':float(np.linalg.norm(dd)),'distance_scene':float(.7*np.linalg.norm(dd))}
contours={}
for k,p in samples.items():
 z=at(p,fit.x);dd=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=200.);contours[k]={'mean_absolute_native':float(np.abs(dd).mean()),'p95_absolute_native':float(np.quantile(np.abs(dd),.95))}
changed=np.any(n!=B,axis=2);blank=fixed&(B[:,:,3]==0)
proof={'status':'ONE_WHOLE_JOINT094_REGISTERED_ALL_RESIDUALS_REVIEW_REQUIRED','raw_SHA256':sha(rawpath),'native_SHA256':sha(O/'candidate/F094.png'),
 'one_whole_raw_to_native_matrix':F.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'all_joint_residuals_no_dropped_knees':res,'all_contour_regions':contours,
 'fixed_native_support_RGBA_changes':0,'outside_activity_RGBA_changes':int(changed[fixed].sum()),'protected_blank_new_alpha':int(np.count_nonzero(n[:,:,3][blank])),
 'joint_whole_output_registrations':1,'independent_local_warps':0,'technical_reference_pixels_adopted':0,'model_calls':1,'actual094_Canvas':0,'next098_calls':0,'front_digit_polygons_raw':frontpolys}
(O/'geometry/ONE_JOINT_REGISTRATION_ALL_REGIONS_AND_SUPPORT.json').write_text(json.dumps(proof,indent=2)+'\n')
def solid(im):
 q=Image.new('RGBA',im.size,'#e1e4e6');q.alpha_composite(im);return q.convert('RGB')
solid(Image.fromarray(n)).save(O/'diagnostics/ACTUAL094_REGISTERED_REAL_SUPPORT_NATIVE.png')
board=Image.new('RGB',(1536,800),'#e1e4e6');d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for i,(txt,im) in enumerate([('Reviewed094 reference',Image.fromarray(T)),('Sole raw / one joint whole fit',reg),('Actual new activity + fixed090 support',Image.fromarray(n))]):board.paste(solid(im).resize((512,768)),(i*512,32));d.text((i*512+5,6),txt,font=font,fill='#25313b')
board.save(O/'diagnostics/SAME_SCALE_TARGET_REGISTERED_RAW_ACTUAL.png')
print(json.dumps({'matrix':F.tolist(),'grips_scene':{r:res[r+'_true_grip']['distance_scene'] for r in ['R','L']},'knee_residuals_native':{k:v['distance_native'] for k,v in res.items() if 'knee' in k},'native_SHA256':proof['native_SHA256'],'fixed_support_RGBA_changes':0},indent=2))
