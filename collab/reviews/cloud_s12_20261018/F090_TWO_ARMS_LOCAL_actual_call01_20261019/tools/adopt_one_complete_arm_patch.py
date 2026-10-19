"""One complete local arm-patch registration; no new whole-body fit.
Entire old/new arm footprints and exposed underarm shirt in one frozen domain.
All joint residuals reported; no hand move, technical pixels, second mask trial.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,math
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F090_COMPLETE_actual_call01_20261019';P=R/'F090_TWO_RIGID_ARM_ZERO_CALL_DIAGNOSTIC_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F090.png').exists(),'One local patch registration already exists'
rawpath=O/'originals/F090_two_arms_call01_raw.png';assert sha(rawpath)=='b664008d0481f15df4a55c39ba26aa8ba666f8ba449903ad5c7ce1f5aa00d5e8'
assert sha(M/'candidate/F090.png')=='0f1caa9edf588cdf525b728770a9079ac97b01c81ff09a398ec468add59ee209'
raw=Image.open(rawpath).convert('RGBA');body=Image.open(M/'candidate/F090.png').convert('RGBA');B=np.asarray(body)
g=json.loads((P/'geometry/ONE_SCHEME_RIGID_ARM_REACH_AND_PIXEL_OWNERSHIP.json').read_text())
source={'R':{'shoulder':[465.,520.],'elbow':[660.,731.],'wrist':[889.,866.],'true_grip':[977.,847.]},
        'L':{'shoulder':[500.,480.],'elbow':[714.,636.],'wrist':[889.,674.],'true_grip':[981.,703.]}}
target={r:dict(zip(['shoulder','elbow','wrist','true_grip'],g['arms'][r]['target_shoulder_elbow_wrist_grip'])) for r in ['R','L']}
weights={'shoulder':3.,'elbow':1.,'wrist':1.,'true_grip':5.}
keys=[(r,k) for r in ['R','L'] for k in ['shoulder','elbow','wrist','true_grip']]
S=np.asarray([source[r][k] for r,k in keys]);T=np.asarray([target[r][k] for r,k in keys]);w=np.asarray([weights[k] for r,k in keys]);w/=w.sum()
# One semantic region, declared once before fitting/adoption. No detached old
# fingers/sleeves can be retained by a smaller hand-only rescue mask.
polygon=[(448,405),(572,405),(655,438),(724,524),(1023,575),(1023,874),(826,874),(648,869),(552,813),(470,760),(443,610)]
mask=Image.new('L',raw.size);ImageDraw.Draw(mask).polygon(polygon,fill=255);domain=np.asarray(mask)>0
Y,X=np.mgrid[:1536,:1024];domain&=(Y>=405)&(Y<875)&~((X<480)&(Y>750))
Image.fromarray(np.uint8(domain)*255).save(O/'geometry/PREDECLARED_ONE_COMPLETE_TWO_ARM_SEMANTIC_DOMAIN.png')
pre={'status':'ONE_LOCAL_PATCH_ONLY_NOT_WHOLE_PERSON_REGISTRATION','raw_visible_joint_proxies':source,'target_corrected_joint_proxies':target,'weights':weights,
 'uncertainty_native':'closed grasp about4px, sleeve-hidden shoulder/elbow about15-25px; no hidden bone measurements',
 'one_semantic_domain_polygon':polygon,'hard_protection':'y<405 head/neck; y>=875 real waist/hips/pants/support; x<480,y>750 back waist; all pixels outside complete semantic arm region',
 'domain_SHA256':sha(O/'geometry/PREDECLARED_ONE_COMPLETE_TWO_ARM_SEMANTIC_DOMAIN.png'),'domain_trials':1,'new_whole_body_fit':False}
(O/'geometry/PREDECLARED_LOCAL_PATCH_POINTS_AND_PROTECTION.json').write_text(json.dumps(pre,indent=2)+'\n')
cs=(S*w[:,None]).sum(0);ct=(T*w[:,None]).sum(0);xs=S-cs;xt=T-ct
u,s,vh=np.linalg.svd(xs.T@(w[:,None]*xt));rr=vh.T@u.T
if np.linalg.det(rr)<0:vh[-1]*=-1;rr=vh.T@u.T
scale=float(np.sum(w*np.sum(xt*(xs@rr.T),axis=1))/np.sum(w*np.sum(xs*xs,axis=1)))
F=np.c_[scale*rr,ct-scale*rr@cs];inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2]
reg=raw.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC)
reg.save(O/'geometry/ONE_LOCAL_PATCH_REGISTERED_RAW_NOT_WHOLE_BODY_ADOPTED.png');A=np.asarray(reg)
n=B.copy();n[domain]=A[domain];Image.fromarray(n).save(O/'candidate/F090.png');assert np.array_equal(n[~domain],B[~domain])
frontpolys={'L':[(956,678),(978,680),(995,699),(999,720),(984,743),(962,744),(949,730),(953,711)],
            'R':[(953,818),(976,816),(992,834),(995,862),(979,889),(959,899),(943,883),(944,863)]}
front=Image.new('L',raw.size);d=ImageDraw.Draw(front)
for p in frontpolys.values():d.polygon(p,fill=255)
front=front.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST);own=(np.asarray(front)>0)&domain
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F090_BG_person.png');Image.fromarray(fg).save(O/'layers/F090_FG_true_front_fingers.png');assert np.array_equal(np.maximum(bg,fg),n)
Z=np.c_[S,np.ones(len(S))]@F.T;res={r+'_'+k:{'registered':z.tolist(),'target':t.tolist(),'residual_native':(z-t).tolist(),'distance_native':float(np.linalg.norm(z-t)),'distance_scene':float(.7*np.linalg.norm(z-t))} for (r,k),z,t in zip(keys,Z,T)}
changed=np.any(n!=B,axis=2);proof={'status':'SOLE_COMPLETE_LOCAL_ARM_PATCH_RESIDUALS_FOR_ACTUAL_CANVAS_REVIEW','raw_SHA256':sha(rawpath),'native_SHA256':sha(O/'candidate/F090.png'),
 'local_patch_only_similarity_matrix':F.tolist(),'uniform_local_patch_scale':scale,'local_rotation_degrees':math.degrees(math.atan2(rr[1,0],rr[0,0])),
 'all_shoulder_elbow_wrist_true_grip_residuals':res,'local_patch_registration_count':1,'new_whole_body_registration_count':0,'domain_trials':1,
 'changed_RGBA_pixels':int(changed.sum()),'outside_semantic_patch_RGBA_changes':int(changed[~domain].sum()),'protected_head_neck_RGBA_changes':int(changed[Y<405].sum()),
 'protected_waist_hips_pants_support_RGBA_changes':int(changed[Y>=875].sum()),'independent_arm_wrist_palm_finger_warps':0,'technical_reference_pixels_adopted':0,'new_model_calls':1,'actual090_Canvas':0,'next094_calls':0,
 'front_digit_polygons_raw_same_patch_matrix':frontpolys}
(O/'geometry/ONE_COMPLETE_LOCAL_PATCH_REGISTRATION_AND_ALL_RESIDUALS.json').write_text(json.dumps(proof,indent=2)+'\n')
def solid(im):
 z=Image.new('RGBA',im.size,'#e1e4e6');z.alpha_composite(im);return z.convert('RGB')
solid(Image.fromarray(n)).save(O/'diagnostics/ACTUAL_LOCAL_ARMS_ON_REAL_BODY_NATIVE.png')
board=Image.new('RGB',(1536,770),'#e1e4e6');d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for i,(name,im) in enumerate([('Old real090 / fixed body context',body),('Sole local raw / one patch matrix',reg),('Actual adopted complete arm domain',Image.fromarray(n))]):board.paste(solid(im).resize((512,738)),(512*i,32));d.text((512*i+5,6),name,font=font,fill='#25313b')
board.save(O/'diagnostics/REAL_BODY_LOCAL_REGISTERED_RAW_AND_PATCH.png')
print(json.dumps({'matrix':F.tolist(),'scale_local_patch_only':scale,'true_grip_scene_residuals':{r:res[r+'_true_grip']['distance_scene'] for r in ['R','L']},'shoulder_native_residuals':{r:res[r+'_shoulder']['distance_native'] for r in ['R','L']},'outside_arm_patch_diff':0,'native_SHA256':proof['native_SHA256']},indent=2))
