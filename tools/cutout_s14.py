"""S14 approved v2 source cutout. Preserve original canvas and contact cloth.
Usage: python tools/cutout_s14.py collab/refs/anim_14_grandma_hang_sheet.png --out assets/chars --report-dir /tmp/s14-proof
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
from scipy import ndimage as ndi
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',nargs='?',default='collab/refs/anim_14_grandma_hang_sheet.png');p.add_argument('--out',default='assets/chars');p.add_argument('--report-dir');args=p.parse_args()
source_hash=hashlib.sha256(Path(args.source).read_bytes()).hexdigest()
if source_hash!='8f63518a0d0b8de74dadfcb13158ce6194ea2e9732961d390e032a35d1c0a0ef':raise ValueError('S14 requires the approved v2 source; refusing a different image')
a=np.array(Image.open(args.source).convert('RGB'));r,g,b=[a[...,i].astype(float) for i in range(3)];lum=a.mean(-1);sat=a.max(-1).astype(float)-a.min(-1)
bg=np.median(np.concatenate([a[:8].reshape(-1,3),a[-8:].reshape(-1,3),a[:,:8].reshape(-1,3)]),axis=0);dist=np.linalg.norm(a.astype(float)-bg,axis=-1)
# Cool neutral background differs from warmer grey hair and warm white cloth.
near=(dist<70)&(b>=r)&(sat<22)&(lum>135)&(lum<238)
seed=np.zeros(lum.shape,bool);seed[0]=1;seed[-1]=1;seed[:,0]=1;seed[:,-1]=1;seed[300,720]=1
cleared=ndi.binary_propagation(seed&near,mask=near)
# Enclosed neutral gaps between thin hair loops; protect white eyes/cloth.
cleared|=(dist<33)&(b>=r+1)&(sat<18)&(lum<232)
edge=ndi.distance_transform_edt(~cleared)
cleared|=(edge<2)&(dist<52)&(b>=r)&(lum>165)&(lum<234)
hair=np.zeros(lum.shape,bool);hair[45:365,260:575]=True
edge=ndi.distance_transform_edt(~cleared)
cleared|=hair&(edge<4)&(lum>192)&(sat<20)
labels,_=ndi.label(~cleared);sizes=np.bincount(labels.ravel());solid=(sizes[labels]>100)&~cleared
alpha=Image.fromarray(np.uint8(solid)*255).filter(ImageFilter.GaussianBlur(.30));im=Image.fromarray(a).convert('RGBA');im.putalpha(alpha)
out=Path(args.out);out.mkdir(parents=True,exist_ok=True);dst=out/'g14_hang_sheet.png';im.save(dst)
# Partition only approved source pixels. Upper arm includes 18px of original
# sleeve underlap so its small rigid rotation cannot expose a skin-coloured hole.
def polygon(points):
 m=Image.new('L',im.size);ImageDraw.Draw(m).polygon(points,fill=255);return np.asarray(m)/255.
arm=polygon([(596,277),(650,250),(700,181),(719,128),(760,73),(790,44),(845,42),(876,76),(878,160),(835,163),(829,137),(805,143),(775,177),(754,225),(719,291),(681,337),(627,361),(615,320),(605,280)])
cloth=polygon([(853,134),(1024,120),(1024,360),(858,338),(852,241),(849,161)])
yy,xx=np.indices(lum.shape)
# All original cloth disappears from the body; the overlapping cloth insert is
# softly joined to the unchanged full sheet. Protect the small gripped fold.
contact=np.maximum(np.clip((1008-xx)/110,0,1)*np.clip((325-yy)/110,0,1),np.exp(-((xx-858)/16)**2-((yy-176)/43)**2))
contact*=np.where(yy<210,1,np.clip((xx-855)/22,0,1))
sleeve=polygon([(550,300),(616,274),(627,310),(630,356),(624,399),(551,416)])
for name,mask in [('g14_body',np.maximum(1-arm,sleeve)*(1-cloth)),('g14_press_arm',arm),('g14_contact_cloth',cloth*contact)]:
 layer=im.copy();layer.putalpha(Image.fromarray(np.uint8(np.asarray(alpha).astype(float)*mask)));layer.save(out/(name+'.png'))
if args.report_dir:
 d=Path(args.report_dir);d.mkdir(parents=True,exist_ok=True);c=Image.new('RGBA',im.size,(42,61,54,255));c.alpha_composite(im);c.convert('RGB').save(d/'cutout_check.jpg')
 (d/'asset_manifest.json').write_text(json.dumps({'source':args.source,'source_sha256':hashlib.sha256(Path(args.source).read_bytes()).hexdigest(),'output':str(dst),'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'canvas':[1024,1536],'method':'cool neutral background removal; preserve warm grey hair/white contact cloth and original pixels'},indent=2)+'\n')
