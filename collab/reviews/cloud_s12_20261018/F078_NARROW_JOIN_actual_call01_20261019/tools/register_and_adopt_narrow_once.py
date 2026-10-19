"""One whole true new patch similarity; frozen18457domain NEVER altered.
No joint/foot warp, no regenerated context adopted outside domain.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,math
from scipy.ndimage import gaussian_filter,distance_transform_edt,map_coordinates,binary_opening,binary_closing,binary_fill_holes,binary_dilation,label
from scipy.optimize import minimize
O=Path(__file__).resolve().parents[1];R=O.parent;I=R/'F078_NARROW_KNEE_JOIN_INPUT_GATE_20261019';D=R/'F078_FIXED074_SUPPORTS_ZERO_CALL_20261019';S74=R/'F074_PANTS_LOCAL_actual_call01_20261019';A78=R/'F078_COMPLETE_actual_call01_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F078.png').exists(),'Never repeat actual patch candidate creation.'
raw=Image.open(O/'originals/F078_NARROW_JOIN_call01_raw.png').convert('RGBA');a=np.asarray(raw);q=a.astype(int)
# Actual output includes adjacent shoe/skin context. Restrict working pixels to true navy cloth.
navy=(q[:,:,2]-q[:,:,0]>7)&(q[:,:,2]-q[:,:,1]>7)&(q[:,:,2]<180)&(q[:,:,3]>24);core=binary_opening(navy);ls,k=label(core);areas=np.bincount(ls.ravel());keep=np.flatnonzero(areas>2500);keep=keep[keep!=0];core=binary_fill_holes(binary_closing(np.isin(ls,keep),iterations=2));pants=binary_dilation(core,iterations=2)&(a[:,:,3]>0);pants&=~((q[:,:,0]-q[:,:,2]>20)|(np.max(q[:,:,:3],axis=2)>190));cut=np.zeros_like(a);cut[pants]=a[pants];Image.fromarray(cut).save(O/'layers/ACTUAL_RAW_NAVY_CLOTH_CONTEXT_ONLY.png');Image.fromarray(np.uint8(pants)*255).save(O/'geometry/ACTUAL_RAW_NAVY_CONTEXT_SEMANTIC_MASK.png')
t=np.asarray(Image.open(I/'reference/CONTINUOUS_KNEE_UPPER_JOIN_TARGET_REFERENCE_ONLY.png').convert('RGBA'));m=np.asarray(Image.open(I/'masks/PROPOSED_NARROW_KNEE_UPPER_CONNECTION_ONLY.png').convert('L'))>0;assert int(m.sum())==18457
rg=cut[:,:,:3].mean(axis=2);tg=t[:,:,:3].mean(axis=2);re=(rg-gaussian_filter(rg,1.5)<-4.5)&(cut[:,:,3]>128)&(rg<85);te=(tg-gaussian_filter(tg,1.2)<-4.0)&(t[:,:,3]>128)&(tg<85)
Y,X=np.mgrid[:1536,:1024];roi=(X>=230)&(X<=695)&(Y>=1070)&(Y<=1220);yy,xx=np.where(te&roi);tp=np.c_[xx,yy].astype(float)[::3];DR=distance_transform_edt(~re);yy,xx=np.where(m&(t[:,:,3]>128));coverage=np.c_[xx,yy].astype(float)[::9]
# Visible cap/upper-knee image anchors ONLY, not hidden bone measurements.
rawAnch=np.array([[344.,334.],[1336.,540.]]);targetAnch=np.array([[285.,1096.],[674.,1170.]])
def matrix(v):
 s,d,tx,ty=v;r=math.radians(d);return np.array([[s*math.cos(r),-s*math.sin(r),tx],[s*math.sin(r),s*math.cos(r),ty]])
def inverse(p,v):return np.c_[p,np.ones(len(p))]@np.linalg.inv(np.vstack([matrix(v),[0,0,1]]))[:2].T
def loss(v):
 z=inverse(tp,v);d=map_coordinates(DR,[z[:,1],z[:,0]],order=1,mode='constant',cval=100)*v[0]
 z=inverse(coverage,v);alpha=map_coordinates(cut[:,:,3].astype(float),[z[:,1],z[:,0]],order=1,mode='constant',cval=0)
 anchors=np.c_[rawAnch,np.ones(2)]@matrix(v).T-targetAnch
 return float(np.mean(np.minimum(d*d,144))+.09*np.sum(anchors*anchors)+25*np.mean(np.maximum(128-alpha,0)**2/128**2))
fit=minimize(loss,[.391,-.93,149,967],method='Powell',bounds=[(.34,.45),(-5,4),(85,200),(900,1025)],options={'xtol':1e-7,'ftol':1e-9,'maxiter':250});assert fit.success,fit.message
F=matrix(fit.x);inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2];registered=Image.fromarray(cut).transform((1024,1536),Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);P=np.asarray(registered);registered.save(O/'layers/ONE_WHOLE_REGISTERED_TRUE_NEW_JOIN_WITH_CONTEXT.png')
B=np.asarray(Image.open(D/'candidate/F078.png').convert('RGBA'));edge=distance_transform_edt(m);w=np.minimum(edge/2,1);w[~m]=0;bp=B.astype(float)/255;pp=P.astype(float)/255;bp[:,:,:3]*=bp[:,:,3:4];pp[:,:,:3]*=pp[:,:,3:4];n=pp*w[:,:,None]+bp*(1-w[:,:,None]);v=n[:,:,3]>0;n[v,:3]/=n[v,3:4];n=np.uint8(np.clip(n*255+.5,0,255));n[~m]=B[~m];assert np.array_equal(n[~m],B[~m]);Image.fromarray(n).save(O/'candidate/F078.png')
feet=np.asarray(Image.open(I/'masks/FINAL074_SHOES_ANKLES_HARD_PROTECT.png').convert('L'))>0;S=np.asarray(Image.open(S74/'candidate/F074.png').convert('RGBA'));A=np.asarray(Image.open(A78/'candidate/F078.png').convert('RGBA'));assert np.array_equal(n[feet],S[feet]);assert np.array_equal(n[1210:],S[1210:]);assert np.array_equal(n[:1060],A[:1060])
# Persistent static support and active+new-connector layers are EXCLUSIVE; no drifted078 feet.
oldStatic=np.asarray(Image.open(D/'masks/STATIC074_OWNERSHIP.png').convert('L'))>0;staticOwn=oldStatic&~m;support=np.zeros_like(n);active=np.zeros_like(n);support[staticOwn]=n[staticOwn];active[~staticOwn]=n[~staticOwn];assert np.array_equal(np.maximum(support,active),n);assert not np.any((support[:,:,3]>0)&(active[:,:,3]>0))
Image.fromarray(support).save(O/'layers/F078_FIXED074_STATIC_SUPPORTS.png');Image.fromarray(active).save(O/'layers/F078_ACTIVE078_UPPER_THIGHS_PLUS_TRUE_NEW_JOIN.png');Image.fromarray(np.uint8(staticOwn)*255).save(O/'geometry/FINAL_STATIC_ACTIVE_EXCLUSIVE_OWNERSHIP.png');(O/'geometry/FROZEN18457_ADOPTION_DOMAIN.png').write_bytes((I/'masks/PROPOSED_NARROW_KNEE_UPPER_CONNECTION_ONLY.png').read_bytes())
fgPath=A78/'layers/F078_FG_true_front_fingers.png';FG=np.asarray(Image.open(fgPath).convert('RGBA'));own=FG[:,:,3]>0;assert np.array_equal(n[own],A[own]);bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'layers/F078_BG_person.png');(O/'layers/F078_FG_true_front_fingers.png').write_bytes(fgPath.read_bytes())
q={'status':'SOLE_TRUE_NEW_NARROW_JOIN_ONE_WHOLE_SIMILARITY_BEFORE_REAL_CANVAS','raw_SHA256':sha(O/'originals/F078_NARROW_JOIN_call01_raw.png'),'native_SHA256':sha(O/'candidate/F078.png'),'one_whole_patch_raw_to_native_matrix':F.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'translation_native':fit.x[2:].tolist(),'source074_support_identity_unchanged':True,'source078_existing_registration_unchanged':True,'allowed_domain_pixels':18457,'outside_domain_RGBA_changes':int(np.count_nonzero(np.any(n[~m]!=B[~m],axis=1))),'fixed074_shoes_ankles_RGBA_changes':0,'fixed074_ground_support_y1210down_RGBA_changes':0,'active078_upper_y1060up_RGBA_changes':0,'new_RGBA_changed_pixels':int(np.count_nonzero(np.any(n!=B,axis=2))),'original078_FG_byte_identical':True,'support_active_alpha_overlap':0,'support_active_RGBA_channelmax_union_exact':True,'new_source_reference_pixels_adopted':0,'separate_knee_shin_foot_warps':0,'frozen_mask_changed':False,'imagegen_calls':1,'actual078_Canvas':0,'next_posture_calls':0}
(O/'geometry/ONE_PATCH_REGISTRATION_AND_FROZEN_DOMAIN_PROOF.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
