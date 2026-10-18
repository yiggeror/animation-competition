"""Register actual drawn head/neck uniformly; preserve fixed garment pixel attachment."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi,optimize
P=Path(__file__).resolve().parent
state,raw_name,mother_name=sys.argv[1:4]
mother_path=P/mother_name
mother=np.array(Image.open(mother_path).convert('RGBA'))
raw=np.array(Image.open(P/'originals'/raw_name).convert('RGBA'))
sf=mother.astype(float);rf=raw.astype(float)
g=ndi.gaussian_gradient_magnitude(sf[:,:,:3].mean(2),.7)
Y,X=np.indices(sf.shape[:2]);valid=(Y>=945)&(Y<=1070)&(X>520)&(X<1390)&(sf[:,:,3]>240)&(g>6)
y,x=np.where(valid);rng=np.random.default_rng(12);ix=rng.choice(len(x),min(1600,len(x)),replace=False);x=x[ix];y=y[ix];c=sf[y,x,:3]
expected=raw.shape[1]/1920
def loss(z):
 s,tx,ty=z;coords=np.array([s*y+ty,s*x+tx]);v=np.column_stack([ndi.map_coordinates(rf[:,:,i],coords,order=1,mode='constant',cval=0) for i in range(3)]);return np.minimum(np.abs(v-c).mean(1),70).mean()
r=optimize.differential_evolution(loss,[(expected*.96,expected*1.04),(-30,30),(-30,30)],seed=16,popsize=11,maxiter=70,tol=.0003,polish=True)
s,tx,ty=r.x
a=raw[:,:,3];ch=np.ptp(raw[:,:,:3].astype(int),axis=2);yy,xx=np.indices(a.shape)
gray_hair=(yy<raw.shape[0]*.71)&(ch<=45)
red_bead=(xx<raw.shape[1]*.45)&(yy>raw.shape[0]*.32)&(yy<raw.shape[0]*.56)&(raw[:,:,0].astype(int)>raw[:,:,1].astype(int)+25)
protected=gray_hair|red_bead
lab,n=ndi.label(a>0);areas=np.bincount(lab.ravel());areas[0]=0;main=areas.argmax();mx=ndi.maximum(a,lab,index=np.arange(n+1));isolated=(lab>0)&(lab!=main)&(mx[lab]<=8)&~protected
dist=ndi.distance_transform_edt(a<128);cleanup=isolated|((a>0)&(a<=24)&(ch>=60)&(dist>1.5)&~protected)
clean=raw.copy();clean[:,:,3][cleanup]=0
assert np.array_equal(clean[:,:,:3],raw[:,:,:3]) and np.array_equal(clean[a>24],raw[a>24])
reg=Image.fromarray(clean).transform((1920,1080),Image.Transform.AFFINE,(s,0,tx,0,s,ty),resample=Image.Resampling.BICUBIC)
v=np.array(reg);reg.save(P/'inputs'/f'{state}_registered_whole.png')
def skin(z):
 c=z[:,:,:3].astype(int)
 return (z[:,:,3]>100)&(c[:,:,0]-c[:,:,1]>10)&(c[:,:,1]-c[:,:,2]>10)
def gray(z):
 c=z[:,:,:3].astype(int)
 return (z[:,:,3]>24)&(np.ptp(c,axis=2)<45)&(c[:,:,0]>60)&(c[:,:,0]<230)
skin_union=(skin(mother)|skin(v))&(Y>=680)&(Y<933)
hair_union=(gray(mother)|gray(v))&(Y>=680)&(Y<755)&(X>600)&(X<1350)
region=(Y<690)|ndi.binary_dilation(skin_union,iterations=8)|ndi.binary_dilation(hair_union,iterations=5)
region[Y>=948]=False
w=np.minimum(ndi.distance_transform_edt(region)/3,1.)
# Preserve the attached fixed blue garment wherever a transparent donor hair
# margin would erase it; this safeguard already passed the reviewed F030.
mother_blue=mother[:,:,2].astype(int)-mother[:,:,0].astype(int)>35
w[(Y>=690)&mother_blue&(v[:,:,3]<200)]=0
out=(v.astype(float)*w[:,:,None]+mother.astype(float)*(1-w[:,:,None])).round().clip(0,255).astype('uint8')
locked=np.array(Image.open(P.parent/'F000_repair/candidate/F000_repaired.png'))
assert np.array_equal(out[948:],locked[948:])
Image.fromarray(out).save(P/'candidate'/f'{state}.png')
Image.fromarray((w*255).round().astype('uint8')).save(P/'masks'/f'{state}_whole_head_neck_adoption.png')
Image.fromarray((cleanup*255).astype('uint8')).save(P/'masks'/f'{state}_source_alpha_cleanup.png')
Image.fromarray(out[100:950,560:1340]).save(P/'qa'/f'{state}_head_neck_native.png')
for name,bg in [('gray',(110,110,110,255)),('white',(255,255,255,255)),('black',(0,0,0,255))]:
 im=Image.new('RGBA',(1920,1080),bg);im.alpha_composite(Image.fromarray(out));im.convert('RGB').save(P/'qa'/f'{state}_{name}.jpg',quality=93)
info={'raw':raw_name,'raw_sha256':hashlib.sha256((P/'originals'/raw_name).read_bytes()).hexdigest(),'mother':mother_name,'mother_sha256':hashlib.sha256(mother_path.read_bytes()).hexdigest(),'registration':'uniform full donor by fixed chest texture only; no face/skull nonrigid warp','donor_per_canvas':[float(s),float(tx),float(ty)],'chest_feature_error':float(r.fun),'all_RGBA_y948_1079_identical_to_locked_F000':True,'all_new_head_hair_ears_neck_from_actual_generated_output':True,'cleanup_pixels':int(cleanup.sum()),'cleanup_max_alpha':int(a[cleanup].max()) if cleanup.any() else 0,'cleanup_RGB_changed':False,'cleanup_alpha_above24_changed':False,'candidate_sha256':hashlib.sha256((P/'candidate'/f'{state}.png').read_bytes()).hexdigest()}
(P/'provenance'/f'{state}_preparation.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
