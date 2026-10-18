from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage,optimize
import numpy as np,json,math,hashlib
D=Path('astra_s07_f022_prepare_20261018_1357');W,H=1024,1536
raw=Image.open(D/'originals/F022_call01_raw.png').convert('RGBA');baseim=Image.open(D/'preposition/F022_preposition_v5_NOT_FINAL.png').convert('RGBA')
def onwhite(im):return Image.alpha_composite(Image.new('RGBA',im.size,'white'),im)
s=np.array(onwhite(raw).convert('L'))/255.;d=np.array(onwhite(baseim).convert('L'))/255.
def ed(a):return np.hypot(ndimage.sobel(a,0),ndimage.sobel(a,1))
se=ed(s)>.25;de=ed(d)>.25;yy,xx=np.indices(d.shape);stable=((yy>605)&(yy<790)&(xx>90)&(xx<455))|((yy>1350)&(yy<1470)&(xx>435)&(xx<590));ys,xs=np.nonzero(de&stable);xs=xs[::3];ys=ys[::3];target=np.array([xs,ys],float);dist=ndimage.distance_transform_edt(~se)
def residual(p):
 a,b,tx,ty=p;den=a*a+b*b;q=target-np.array([[tx],[ty]]);sx=(a*q[0]+b*q[1])/den;sy=(-b*q[0]+a*q[1])/den
 return ndimage.map_coordinates(dist,[sy,sx],order=1,mode='constant',cval=30)
res=optimize.least_squares(residual,[1,0,0,0],bounds=([.985,-.012,-12,-15],[1.015,.012,12,15]),loss='soft_l1',f_scale=1.5,max_nfev=200,diff_step=1e-4)
a,b,tx,ty=res.x;M=np.array([[a,-b],[b,a]]);iv=np.linalg.inv(M);q=-iv@np.array([tx,ty]);reg=raw.transform(raw.size,Image.Transform.AFFINE,(iv[0,0],iv[0,1],q[0],iv[1,0],iv[1,1],q[1]),Image.Resampling.BICUBIC);reg.save(D/'candidates/F022_call01_registered_source.png');onwhite(reg).convert('RGB').save(D/'review/F022_call01_registered_white.jpg',quality=97)
meta={'method':'One whole-output similarity fitted only to unchanged visible head and lower-leg lines; no hidden joint fitting or nonuniform scaling. Only local masked patch is used.','parameters':dict(zip(['a','b','tx','ty'],res.x.tolist())),'scale':math.hypot(a,b),'rotation_degrees':math.degrees(math.atan2(b,a)),'sample_count':len(xs),'median_nearest_edge_distance_asset':float(np.median(res.fun)),'p90_nearest_edge_distance_asset':float(np.percentile(res.fun,90)),'caveat':'Nearest-line registration diagnostic, not anatomical measurement.'};(D/'geometry/F022_call01_registration.json').write_text(json.dumps(meta,indent=2))
base=np.array(baseim);new=np.array(reg);mask=np.array(Image.open(D/'masks/F022_connection_mask_v6_APPROVED.png'))
# Natural whole near arm including the model's coherent single jade bangle accepted by coordinator and independent reviewer. Expanded explicit take domain; no old bangle overlay.
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([(365,965),(520,974),(566,1130),(524,1330),(200,1330),(202,1165),(325,1090)],fill=255);mask=np.maximum(mask,np.array(m))
# Restore fixed continuous back cloth and seat original pixels. These exclusions do not clip either hand.
pro=np.array(Image.open(D/'masks/F022_hard_protect_v6.png'))>0;pro[(xx<520)&(yy>1120)]=False;mask[pro]=0
mask[(yy>=1340)]=0
Image.fromarray(mask).save(D/'masks/F022_expanded_arm_take_v1.png')
w=mask[:,:,None].astype(float)/255;out=np.rint(base*(1-w)+new*w).astype('uint8');im=Image.fromarray(out);im.save(D/'candidates/F022_local_v1.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB').save(D/f'review/F022_local_v1_{n}.jpg',quality=98)
onwhite(im).crop((200,775,920,1345)).resize((1080,855)).convert('RGB').save(D/'review/F022_local_v1_connections.jpg',quality=98)
check={'actual_changed_pixels_from_preposition':int(np.any(out!=base,axis=2).sum()),'outside_take_mask_changed':int(np.any(out!=base,axis=2)[mask==0].sum()),'sha256':hashlib.sha256((D/'candidates/F022_local_v1.png').read_bytes()).hexdigest(),'status':'AUTHOR_REVIEW_PENDING'};(D/'geometry/F022_local_v1_check.json').write_text(json.dumps(check,indent=2));print(meta);print(check)
