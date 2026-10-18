from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
import numpy as np,json,hashlib
D=Path('astra_s07_f022_prepare_20261018_1357');W,H=1024,1536;yy,xx=np.indices((H,W))
a=np.array(Image.open(D/'preposition/F022_preposition_v5_NOT_FINAL.png').convert('RGBA'));b=np.array(Image.open(D/'candidates/F022_call01_registered_source.png').convert('RGBA'));m=np.array(Image.open(D/'masks/F022_expanded_arm_take_v1.png')).astype(float)/255
# Same-raw edge repair: neck/sleeve outlet, former upper-pants angled edge.
z=Image.new('L',(W,H));d=ImageDraw.Draw(z);d.polygon([(343,791),(380,795),(371,834),(342,883),(330,949),(289,949),(298,880),(320,836)],fill=255);d.polygon([(300,1025),(367,1020),(365,1135),(300,1135)],fill=255);d.polygon([(481,938),(522,948),(533,1052),(488,1040)],fill=255);m=np.maximum(m,np.array(z)/255)
# Retain original back/seat without cutting a new line at a rectangular take boundary. Blend only in matte, opaque cloth interior, not limb silhouette.
back=np.array(Image.open(D/'masks/F022_hard_protect_v6.png'))>0;back[(xx<520)&(yy>1120)]=False;back[(xx<523)&(yy>935)&(yy<1055)]=False
# Preserve full original continuous right back, hem, and sitting pants beyond the local join.
back|=(xx>565)&(yy>1135);back|=(xx>560)&(yy<1050)&(yy>815);back|=(xx>700)&(yy>1000)
# Feather interior seam 4px, while protected interior retains original bytes.
blend=ndimage.distance_transform_edt(~back);m*=np.clip(blend/5,0,1)
# Below all released fingertips, ease raw pants back into the unchanged lower pants. No ground/foot/basin pixel is taken.
m*=np.where(yy>1320,np.clip((1350-yy)/30,0,1),1)
# Clear all redundant old thin edges via raw in their explicit local regions.
mask=np.rint(m*255).astype('uint8');Image.fromarray(mask).save(D/'masks/F022_local_take_v3.png')
w=mask[:,:,None].astype(float)/255;out=np.rint(a*(1-w)+b*w).astype('uint8');im=Image.fromarray(out);im.save(D/'candidates/F022_local_v3.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB').save(D/f'review/F022_local_v3_{n}.jpg',quality=98)
wh=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),im);wh.crop((285,775,920,1350)).resize((1016,920)).convert('RGB').save(D/'review/F022_local_v3_connections.jpg',quality=98)
check={'actual_changed_pixels_from_preposition':int(np.any(out!=a,axis=2).sum()),'outside_take_mask_changed':int(np.any(out!=a,axis=2)[mask==0].sum()),'sha256':hashlib.sha256((D/'candidates/F022_local_v3.png').read_bytes()).hexdigest(),'status':'AUTHOR_REVIEW_PENDING'};(D/'geometry/F022_local_v3_check.json').write_text(json.dumps(check,indent=2));print(check)
