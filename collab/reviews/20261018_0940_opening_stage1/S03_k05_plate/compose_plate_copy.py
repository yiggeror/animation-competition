from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
ROOT=Path(__file__).resolve().parent
S=ROOT.parent/'astra_s03b_painted_pilot_20261018/refs/painted'
p5=next(S.glob('*_k05_*'));p6=next(S.glob('*_k06_*'))
a=Image.open(p5).convert('RGBA'); b=Image.open(p6).convert('RGBA'); W,H=a.size
# Hand-traced native-pixel masks. No source image is overwritten or resampled.
erase_pts=[(295,894),(307,886),(320,881),(332,879),(338,888),(347,895),(359,902),(367,903),(374,912),(383,914),(421,913),(462,911),(474,896),(485,879),(489,875),(507,878),(523,885),(530,894),(530,906),(522,919),(504,932),(477,941),(346,941),(321,930),(305,916),(296,905)]
plate_pts=[(336,916),(340,908),(351,902),(369,897),(395,892),(424,889),(460,888),(491,890),(521,894),(545,898),(561,903),(570,909),(569,918),(559,927),(543,935),(522,941),(342,941),(336,932),(334,924)]
# Keep hand+melon core, silhouette, and original shared contact edge unchanged.
protect_pts=[(300,770),(530,770),(530,820),(490,864),(488,870),(484,880),(478,890),(470,900),(463,908),(444,910),(418,912),(383,913),(375,912),(368,904),(360,902),(348,897),(337,888),(328,875),(316,860),(300,850)]
def mask(pts):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(pts,fill=255);return m
em=mask(erase_pts);pm=mask(plate_pts);fm=mask(protect_pts)
# Empty k06 plate supplies pixels hidden by the original k05 fruit; translate y+6, no scale or warp.
bpad=Image.new('RGBA',(W,H));bpad.paste(b,(0,0));ba=np.array(bpad);mp=np.array(pm);ba[:,:,3]=np.minimum(ba[:,:,3],mp)
layer=Image.new('RGBA',(W,H));layer.paste(Image.fromarray(ba),(0,6))
aa=np.array(a);ea=np.array(em);fa=np.array(fm)
roi=np.zeros((H,W),bool);roi[875:,295:531]=True
white=(aa[:,:,:3].min(axis=2)>140)&(np.ptp(aa[:,:,:3].astype(int),axis=2)<32)&roi
fa[white]=0
effective=((ea>0)|(white))&(fa==0);out=aa.copy();out[effective]=0
com=Image.alpha_composite(Image.fromarray(out),layer)
fg=aa.copy();fg[:,:,3]=np.minimum(fg[:,:,3],fa)
com=Image.alpha_composite(com,Image.fromarray(fg))
c=np.array(com)
allowed=effective|(np.array(layer)[:,:,3]>0)
c[~allowed]=aa[~allowed]
core=(fa>0)&(aa[:,:,3]>=250);c[core]=aa[core] # preserve opaque original foreground without punching transparent holes
outim=Image.fromarray(c);outim.save(ROOT/'S03_k05_fixed_plate_candidate_v3.png')
em.save(ROOT/'old_plate_erase_mask.png');pm.save(ROOT/'k06_empty_plate_source_mask.png');Image.fromarray(fa).save(ROOT/'hand_melon_protect_mask.png');Image.fromarray((allowed*255).astype('uint8')).save(ROOT/'plate_change_allowed_mask.png');layer.save(ROOT/'plate_layer_at_453_918.png')
diff=np.any(c!=aa,axis=2);ys,xs=np.where(diff)
meta={'status':'CANDIDATE_PENDING_ACTUAL_CONTACT_REVIEW','canvas':[W,H],'source_k05':{'file':p5.name,'sha256':hashlib.sha256(p5.read_bytes()).hexdigest()},'plate_source_k06':{'file':p6.name,'sha256':hashlib.sha256(p6.read_bytes()).hexdigest()},'plate_transform':{'translate':[0,6],'scale':1,'source_center_estimate':[453,912],'target_center_estimate':[453,918]},'method':'Reuse the already-painted empty k06 plate to fill the occlusion under k05 hand/fruit. Do not translate hand, fruit, arm or body. Explicit visible-old-plate erase, new plate layer, and protected hand/fruit restoration. Source drawings unchanged.','changed_pixels':int(diff.sum()),'changed_bbox_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'protected_opaque_foreground_changed_pixels':int(np.any(c[core]!=aa[core],axis=1).sum()),'outside_plate_roi_changed_pixels':int(diff[:875].sum()),'generation_calls':0,'erase_polygon':erase_pts,'source_plate_polygon':plate_pts,'protect_polygon':protect_pts,'candidate_sha256':hashlib.sha256((ROOT/'S03_k05_fixed_plate_candidate_v3.png').read_bytes()).hexdigest()}
(ROOT/'plate_fix_v3.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
# Read-only inspection contact sheet on a visible neutral background.
row=Image.new('RGB',(1500,450),'#cccccc')
for i,(im,label) in enumerate([(a,'k05 original'),(outim,'k05 plate-copy candidate'),(bpad,'k06 plate source')]):
 crop=im.crop((280,775,580,941));bg=Image.new('RGBA',crop.size,(205,205,205,255));bg.alpha_composite(crop);pic=bg.convert('RGB').resize((500,277));row.paste(pic,(i*500,45));ImageDraw.Draw(row).text((i*500+10,12),label,fill='black')
row.save(ROOT/'plate_fix_v3_contact.jpg');print(json.dumps(meta,ensure_ascii=False))
