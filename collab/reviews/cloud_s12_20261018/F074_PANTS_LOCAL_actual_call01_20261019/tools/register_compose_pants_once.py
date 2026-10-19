"""ONE whole actual-pants similarity + authorized2px hem/cuff transition only.
Never adopt target/reference body RGB or new generated shoes/ankle skin.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,math
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,binary_dilation,binary_erosion,label,distance_transform_edt,map_coordinates
from scipy.optimize import minimize
O=Path(__file__).resolve().parents[1];R=O.parent;REF=R/'F074_PANTS_CONTINUITY_INPUT_GATE_20261019';M=R/'F074_COMPLETE_actual_call01_20261019'
assert not (O/'candidate/F074.png').exists(),'Do not repeat actual candidate creation'
raw=Image.open(O/'originals/F074_PANTS_call01_raw.png').convert('RGBA');a=np.asarray(raw);q=a.astype(int)
navy=(q[:,:,2]-q[:,:,0]>7)&(q[:,:,2]-q[:,:,1]>7)&(q[:,:,2]<170)&(q[:,:,3]>24)
core=binary_opening(navy,iterations=1);labs,k=label(core);areas=np.bincount(labs.ravel());keep=np.flatnonzero(areas>2500);keep=keep[keep!=0];core=binary_fill_holes(binary_closing(np.isin(labs,keep),iterations=2));rawPants=binary_dilation(core,iterations=2)&(q[:,:,3]>0)
# Generated shoes/skin/white sole are explicitly NOT part of the adopted semantic pants.
shoeSkin=(q[:,:,0]-q[:,:,2]>20)|(np.max(q[:,:,:3],axis=2)>190);rawPants&=~shoeSkin
cut=np.zeros_like(a);cut[rawPants]=a[rawPants];Image.fromarray(cut).save(O/'layers/ACTUAL_RAW_PANTS_ONLY_NO_NEW_SHOES.png');Image.fromarray(np.uint8(rawPants)*255).save(O/'geometry/RAW_COMPLETE_PANTS_SEMANTIC_MASK.png')
t=np.asarray(Image.open(REF/'reference/WHOLE_PANTS_SOURCE074_TEXTURE_GEOMETRY_REFERENCE_ONLY.png').convert('RGBA'));tm=t[:,:,3]>=128;sm=cut[:,:,3]>=128
D=distance_transform_edt(~tm)-distance_transform_edt(tm);DS=distance_transform_edt(~sm)-distance_transform_edt(sm)
blue=np.asarray(Image.open(REF/'masks/CURRENT074_BLUE_HEM_HARD_PROTECT.png').convert('L'))>0;feet=np.asarray(Image.open(REF/'masks/CURRENT074_BOTH_SHOES_BARE_ANKLES_HARD_PROTECT.png').convert('L'))>0;hard=blue|feet
# Raw waist/top is hidden behind the original hard-protected blouse, so it is not an exposed contour target.
y,x=np.where(sm^binary_erosion(sm));sel=y>=280;pts=np.c_[x[sel],y[sel]].astype(float)[::3]
y,x=np.where((tm^binary_erosion(tm))&~binary_dilation(hard,iterations=4));tpts=np.c_[x,y].astype(float)[::3]
y,x=np.where(binary_erosion(tm,iterations=5));inside=np.c_[x,y].astype(float)[::35]
def mat(v):
 s,deg,tx,ty=v;r=math.radians(deg);return np.array([[s*math.cos(r),-s*math.sin(r),tx],[s*math.sin(r),s*math.cos(r),ty]])
def fwd(p,v):return np.c_[p,np.ones(len(p))]@mat(v).T
def inv(p,v):return np.c_[p,np.ones(len(p))]@np.linalg.inv(np.vstack([mat(v),[0,0,1]]))[:2].T
# Entire semantic pants is fitted as one shape; no independent knees/shins/cuffs.
def loss(v):
 z=fwd(pts,v);d=map_coordinates(D,[z[:,1],z[:,0]],order=1,mode='constant',cval=100)
 h=map_coordinates(hard.astype(float),[z[:,1],z[:,0]],order=0,mode='constant',cval=0)>.5
 valid=~h;aa=np.mean(np.minimum(d[valid]**2,1600)) if valid.any() else 1600
 u=inv(tpts,v);d2=map_coordinates(DS,[u[:,1],u[:,0]],order=1,mode='constant',cval=100)*v[0]
 u=inv(inside,v);dc=map_coordinates(DS,[u[:,1],u[:,0]],order=1,mode='constant',cval=100)*v[0]
 return float(aa+np.mean(np.minimum(d2*d2,1600))+3*np.mean(np.minimum(np.maximum(dc,0)**2,1600)))
fit=minimize(loss,[.56,0,-78,817],method='Powell',bounds=[(.50,.64),(-3,3),(-170,10),(730,900)],options={'xtol':1e-7,'ftol':1e-9,'maxiter':250});assert fit.success,fit.message
F=mat(fit.x);I=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2];patch=Image.fromarray(cut).transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.BICUBIC);patch.save(O/'layers/WHOLE_REGISTERED_TRUE_NEW_PANTS.png')
A=np.asarray(Image.open(M/'candidate/F074.png').convert('RGBA'));P=np.asarray(patch);allowed=np.asarray(Image.open(REF/'masks/PROPOSED_WHOLE_PANTS_PLUS_2PX_CONNECTION_ALLOWED.png').convert('L'))>0;assert int(allowed.sum())==134552
# Only the explicitly approved narrow hem/cuff corridor blends original074 pants RGB/alpha.
dist=distance_transform_edt(~hard);join=allowed&(dist<=2);w=np.ones(allowed.shape,float);w[join]=np.clip(dist[join]/2,0,1)
# Premultiplied interpolation only in <=2native connection corridor; all other allowed pixels are true new patch.
ap=A.astype(float)/255;pp=P.astype(float)/255;ap[:,:,:3]*=ap[:,:,3:4];pp[:,:,:3]*=pp[:,:,3:4];z=pp*w[:,:,None]+ap*(1-w[:,:,None]);good=z[:,:,3]>0;z[good,:3]/=z[good,3:4];z=np.uint8(np.clip(z*255+.5,0,255));out=A.copy();out[allowed]=z[allowed]
assert np.array_equal(out[~allowed],A[~allowed]);assert np.array_equal(out[feet],A[feet]);assert np.array_equal(out[blue],A[blue]);Image.fromarray(out).save(O/'candidate/F074.png');Image.fromarray(np.uint8(join)*255).save(O/'geometry/APPROVED_2PX_HEM_CUFF_TRANSITION_ONLY.png')
FG=Image.open(M/'layers/F074_FG_true_front_fingers.png').convert('RGBA');fg=np.asarray(FG);own=fg[:,:,3]>0;bg=out.copy();bg[own]=0;assert np.array_equal(out[own],A[own]);Image.fromarray(bg).save(O/'layers/F074_BG_person.png');(O/'layers/F074_FG_true_front_fingers.png').write_bytes((M/'layers/F074_FG_true_front_fingers.png').read_bytes())
# Patch must cover the visible complete cloth interiors; holes are reported, never auto-filled with old legs.
expected=binary_erosion(tm,iterations=3)&~join;missing=expected&(out[:,:,3]<32)
qa={'status':'TRUE_NEW_COMPLETE_PANTS_ONE_WHOLE_SIMILARITY_CANDIDATE_FOR_REAL_CANVAS','raw_SHA256':hashlib.sha256((O/'originals/F074_PANTS_call01_raw.png').read_bytes()).hexdigest(),'native_candidate_SHA256':hashlib.sha256((O/'candidate/F074.png').read_bytes()).hexdigest(),'one_whole_pants_raw_to_native_matrix':F.tolist(),'uniform_scale':float(fit.x[0]),'rotation_degrees':float(fit.x[1]),'translation_native':fit.x[2:].tolist(),'generated_shoes_ankle_skin_adopted':False,'actual_new_semantic_raw_pants_pixels':int(rawPants.sum()),'allowed_pixels':int(allowed.sum()),'outside_allowed_RGBA_changes':int(np.count_nonzero(np.any(out[~allowed]!=A[~allowed],axis=1))),'protected_blue_RGBA_changes':0,'protected_current074_shoes_bare_ankles_RGBA_changes':0,'original074_FG_file_byte_identical':True,'approved_2px_join_pixels':int(join.sum()),'RGBA_changed_pixels':int(np.count_nonzero(np.any(out!=A,axis=2))),'reference_expected_eroded_mask_alpha_not_covered_pixels':int(missing.sum()),'old070_or_reference_RGB_alpha_adopted':0,'separate_knee_shin_shoe_warps':0,'actual_Canvas_pending':True}
(O/'geometry/ONE_WHOLE_PANTS_REGISTRATION_AND_PROTECTION.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
