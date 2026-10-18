"""Adopt real imagegen eye pixels; leave every other F027 RGBA pixel unchanged."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi, optimize
P=Path(__file__).resolve().parent
mother=np.array(Image.open(P/'inputs/F027_reviewed_source.png').convert('RGBA'))
crop=mother[365:610,815:1240].astype(float)
raw=np.array(Image.open(P/'originals/F027_fix_call01_raw.png').convert('RGBA')).astype(float)
y,x=np.indices(crop.shape[:2])
grad=ndi.gaussian_gradient_magnitude(crop[:,:,:3].mean(2),.7)
valid=(grad>9)&(x>35)&(x<375)&(y>65)&(y<225)
valid&=~(((x>65)&(x<184)&(y>100)&(y<175))|((x>245)&(x<344)&(y>100)&(y<175)))
yy,xx=np.where(valid)
rng=np.random.default_rng(27);ix=rng.choice(len(xx),min(1400,len(xx)),False);xx=xx[ix];yy=yy[ix];c=crop[yy,xx,:3]
def loss(z):
 s,tx,ty=z;coords=[s*yy+ty,s*xx+tx]
 v=np.column_stack([ndi.map_coordinates(raw[:,:,k],coords,order=1,mode='constant',cval=0) for k in range(3)])
 return np.minimum(abs(v-c).mean(1),70).mean()
e=raw.shape[1]/crop.shape[1]
r=optimize.differential_evolution(loss,[(e*.97,e*1.03),(-25,25),(-25,25)],seed=27,popsize=11,maxiter=90,tol=.0001,polish=True)
s,tx,ty=r.x
reg=Image.fromarray(raw.astype('uint8')).transform((425,245),Image.Transform.AFFINE,(s,0,tx,0,s,ty),Image.Resampling.BICUBIC)
d=np.array(reg).astype(float)
# Color offset is measured only on unchanged, flat skin around the lenses.
skin=(crop[:,:,0]>210)&(crop[:,:,1]>155)&(crop[:,:,1]<220)&(crop[:,:,2]<175)&(y<75)&(x>100)&(x<350)
offset=np.median(crop[skin,:3]-d[skin,:3],axis=0)
d[:,:,:3]=np.clip(d[:,:,:3]+offset,0,255)
Y,X=np.indices(mother.shape[:2]);w=np.zeros(Y.shape,float)
for cx,cy,rx,ry in [(939,502,58,34),(1123,498,49,32)]:
 radial=np.sqrt(((X-cx)/rx)**2+((Y-cy)/ry)**2)
 w=np.maximum(w,np.clip((1-radial)*min(rx,ry)/3,0,1))
out=mother.copy();patch=w[365:610,815:1240,None]
out[365:610,815:1240]=(crop*(1-patch)+d*patch).round().clip(0,255).astype('uint8')
assert np.array_equal(out[w==0],mother[w==0])
Image.fromarray(out).save(P/'candidate/F027_fixed.png')
Image.fromarray((w*255).round().astype('uint8')).save(P/'masks/F027_eyes_only.png')
Image.fromarray(d.round().astype('uint8')).save(P/'inputs/F027_fix_registered_crop.png')
Image.fromarray(out[350:610,760:1260]).save(P/'qa/F027_fixed_eyes_native.png')
diff=np.any(out!=mother,axis=2)
info={'source':'inputs/F027_reviewed_source.png','source_sha256':hashlib.sha256((P/'inputs/F027_reviewed_source.png').read_bytes()).hexdigest(),'raw':'originals/F027_fix_call01_raw.png','donor_uniform_registration':[float(s),float(tx),float(ty)],'frame_registration_error':float(r.fun),'skin_RGB_offset':offset.tolist(),'adoption':'only two feathered lens-interior eye ellipses; no eyebrows, frame, bridge, nose, head, hair, ears, neck or clothing adoption','ellipse_masks':[[939,502,58,34],[1123,498,49,32]],'changed_pixels':int(diff.sum()),'changed_bbox':[int(X[diff].min()),int(Y[diff].min()),int(X[diff].max())+1,int(Y[diff].max())+1],'outside_eye_mask_RGBA_identical':bool(np.array_equal(out[w==0],mother[w==0])),'candidate_sha256':hashlib.sha256((P/'candidate/F027_fixed.png').read_bytes()).hexdigest()}
(P/'provenance/F027_fix_preparation.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps(info,indent=2))
