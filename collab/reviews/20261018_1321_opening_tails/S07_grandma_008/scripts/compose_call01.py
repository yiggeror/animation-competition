from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw,ImageFont
from scipy import ndimage,optimize
import numpy as np,json,math,hashlib
D=Path('astra_s07_f008_prepare_20261018_1249');W,H=1024,1536
raw=Image.open(D/'originals/F008_call01_raw.png').convert('RGBA');baseim=Image.open(D/'preposition/F008_preposition_NOT_FINAL.png').convert('RGBA')
def onwhite(im):return Image.alpha_composite(Image.new('RGBA',im.size,'white'),im)
s=np.array(onwhite(raw).convert('L'))/255.;d=np.array(onwhite(baseim).convert('L'))/255.
def ed(a):return np.hypot(ndimage.sobel(a,0),ndimage.sobel(a,1))
se=ed(s)>.25;de=ed(d)>.25;yy,xx=np.indices(d.shape);stable=((yy>400)&(yy<805)&(xx>300)&(xx<760))|((yy>1190)&(yy<1490)&(xx>225)&(xx<590));ys,xs=np.nonzero(de&stable);xs=xs[::3];ys=ys[::3];target=np.array([xs,ys],float);dist=ndimage.distance_transform_edt(~se)
def residual(p):
 a,b,tx,ty=p;den=a*a+b*b;q=target-np.array([[tx],[ty]]);sx=(a*q[0]+b*q[1])/den;sy=(-b*q[0]+a*q[1])/den
 return ndimage.map_coordinates(dist,[sy,sx],order=1,mode='constant',cval=30)
res=optimize.least_squares(residual,[1,0,0,0],bounds=([.985,-.012,-12,-15],[1.015,.012,12,15]),loss='soft_l1',f_scale=1.5,max_nfev=200,diff_step=1e-4)
a,b,tx,ty=res.x;M=np.array([[a,-b],[b,a]]);iv=np.linalg.inv(M);q=-iv@np.array([tx,ty]);reg=raw.transform(raw.size,Image.Transform.AFFINE,(iv[0,0],iv[0,1],q[0],iv[1,0],iv[1,1],q[1]),Image.Resampling.BICUBIC);reg.save(D/'candidates/F008_call01_registered_source.png');onwhite(reg).convert('RGB').save(D/'review/F008_call01_registered_white.jpg',quality=96)
meta={'method':'One whole-output similarity fitted only to unchanged visible head and lower-leg lines; never hidden joints or nonuniform deformation. Only local masked patch is used.','parameters':dict(zip(['a','b','tx','ty'],res.x.tolist())),'scale':math.hypot(a,b),'rotation_degrees':math.degrees(math.atan2(b,a)),'sample_count':len(xs),'median_nearest_edge_distance_asset':float(np.median(res.fun)),'p90_nearest_edge_distance_asset':float(np.percentile(res.fun,90)),'caveat':'Nearest line registration diagnostic, not anatomical error.'};(D/'geometry/F008_call01_registration.json').write_text(json.dumps(meta,indent=2))
base=np.array(baseim);new=np.array(reg);mask=np.array(Image.open(D/'masks/local_connection_edit_mask_PROPOSAL.png'))
# Take only approved local repairs. Exact opaque held cluster is protected by approved mask.
w=mask.astype(float)[:,:,None]/255;out=np.rint(base*(1-w)+new*w).astype('uint8');candidate=Image.fromarray(out);candidate.save(D/'candidates/F008_local_v1.png')
for name,c in [('white','white'),('gray',(160,160,160,255))]:Image.alpha_composite(Image.new('RGBA',candidate.size,c),candidate).convert('RGB').save(D/f'review/F008_local_v1_{name}.jpg',quality=96)
onwhite(candidate).crop((360,810,920,1180)).resize((1120,740)).convert('RGB').save(D/'review/F008_local_v1_join_detail.jpg',quality=97)
prev=Image.open(D/'sources/F000_LOCKED_rgba.png').convert('RGBA');Image.blend(onwhite(prev),onwhite(candidate),.5).convert('RGB').save(D/'review/F000_F008_candidate_onion.jpg',quality=96)
check={'outside_approved_mask_rgba_changed_pixels':int(np.any(out!=base,axis=2)[mask==0].sum()),'lower_legs_y_over_1160_changed_pixels':int(np.any(out!=np.array(prev),axis=2)[yy>1160].sum()),'actual_changed_pixels':int(np.any(out!=base,axis=2).sum()),'sha256':hashlib.sha256((D/'candidates/F008_local_v1.png').read_bytes()).hexdigest(),'status':'AUTHOR_REVIEW_PENDING'};(D/'geometry/F008_local_v1_check.json').write_text(json.dumps(check,indent=2));print(json.dumps(meta,indent=2));print(check)
