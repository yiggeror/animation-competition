from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
import numpy as np,json,hashlib
D=Path('astra_s07_f025_prepare_20261018_1420');W,H=1024,1536;yy,xx=np.indices((H,W));a=np.array(Image.open(D/'preposition/F025_preposition_v4_NOT_FINAL.png').convert('RGBA'));b=np.array(Image.open(D/'candidates/F025_call01_registered_source.png').convert('RGBA'));ma=np.array(Image.open(D/'masks/F025_connection_mask_v5_PROPOSAL.png'));m=Image.new('L',(W,H));d=ImageDraw.Draw(m)
# Clear the full old hand silhouette outside the original guide polygon. Only source-transparent pixels are returned here.
d.polygon([(270,970),(348,970),(348,1027),(270,1027)],fill=255)
# Same-raw tiny neck join and new waist slit/hem join, not a new body draw.
d.polygon([(346,793),(382,799),(389,840),(351,840)],fill=255)
d.polygon([(724,1068),(786,1088),(794,1202),(723,1200)],fill=255)
# Continuous pant-front contour through the disclosed old-arm region.
d.polygon([(313,1080),(338,1080),(343,1350),(313,1350)],fill=255)
ma=np.maximum(ma,np.array(m))
# Restore the inherited blue material in the one generated patch. Do not warm white flowers, skin, jade, navy pants or ink.
r,g,bl=b[:,:,0].astype(float),b[:,:,1].astype(float),b[:,:,2].astype(float);pig=np.minimum.reduce([(bl-r-15)/15,(g-r-5)/15,(g-70)/30,(225-r)/35]);pig=np.clip(pig,0,1);pig[(yy>1205)|(b[:,:,3]<200)]=0;b[:,:,:3]=np.rint(np.clip(b[:,:,:3].astype(float)+pig[:,:,None]*[13,9,2],0,255)).astype('uint8');Image.fromarray(np.rint(pig*255).astype('uint8')).save(D/'masks/F025_blue_material_match_v2.png')
# A narrow interior-only seam blend avoids an artificial take-polygon stripe; silhouette repairs remain full strength.
soft=np.array(Image.fromarray(ma).filter(ImageFilter.GaussianBlur(2))).astype(float);interior=(a[:,:,3]>245)&(b[:,:,3]>245)&(xx>500)&(yy<1200);mask=ma.copy();mask[interior]=np.maximum(ma[interior]*.0,soft[interior]).astype('uint8')
Image.fromarray(mask).save(D/'masks/F025_local_take_v2.png');w=mask[:,:,None].astype(float)/255;out=np.rint(a*(1-w)+b*w).astype('uint8');im=Image.fromarray(out);im.save(D/'candidates/F025_local_v2.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB').save(D/f'review/F025_local_v2_{n}.jpg',quality=98)
wh=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),im);wh.crop((280,725,895,1210)).resize((1045,824)).convert('RGB').save(D/'review/F025_local_v2_connections.jpg',quality=98)
check={'sha256':hashlib.sha256((D/'candidates/F025_local_v2.png').read_bytes()).hexdigest(),'changed_pixels_from_preposition':int(np.any(out!=a,axis=2).sum()),'outside_take_mask_changed':int(np.any(out!=a,axis=2)[mask==0].sum()),'blue_material_delta_RGB':[13,9,2],'status':'AUTHOR_REVIEW_PENDING'};(D/'geometry/F025_local_v2_checks.json').write_text(json.dumps(check,indent=2));print(check)
