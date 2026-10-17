# S29 source-pixel cutouts. No character repaint or pose generation.
# Usage: python tools/cutout_s29.py grandma.png xiaoman_a.png xiaoman_b.png --report-dir /tmp/s29-proof
# Requires numpy, Pillow and scipy, as does the existing generic tools/cutout.py.
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
from scipy import ndimage as ndi
import argparse
parser=argparse.ArgumentParser(description='S29 reviewed-source cutouts: preserve the original canvas and isolate B head/neck only.')
parser.add_argument('grandma')
parser.add_argument('xiaoman_a')
parser.add_argument('xiaoman_b')
parser.add_argument('--out',default='assets/chars')
parser.add_argument('--report-dir')
args=parser.parse_args()
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
report=Path(args.report_dir) if args.report_dir else None
if report:report.mkdir(parents=True,exist_ok=True)
HEAD=[(180,65),(860,65),(860,665),(600,665),(592,617),(573,601),(552,584),(543,607),(536,640),(518,643),(490,631),(464,613),(439,585),(424,559),(412,558),(388,575),(367,599),(351,627),(180,627)]
JOBS=[('g29_wrap',args.grandma,[(265,1060),(450,1040),(450,1150),(300,1165),(580,670)]),('x29_look_a',args.xiaoman_a,[]),('x29_head_b',args.xiaoman_b,[])]
entries=[]
for name,src,holes in JOBS:
 a=np.asarray(Image.open(src).convert('RGB'));h,w=a.shape[:2]
 bg=np.median(np.concatenate([a[:8].reshape(-1,3),a[-8:].reshape(-1,3),a[:,:8].reshape(-1,3),a[:,-8:].reshape(-1,3)]),axis=0)
 dist=np.linalg.norm(a.astype(float)-bg,axis=-1);sat=a.max(-1).astype(float)-a.min(-1);lum=a.mean(-1)
 near=(dist<72)&(sat<24)&(lum<235)
 seeds=np.zeros((h,w),bool);seeds[0]=True;seeds[-1]=True;seeds[:,0]=True;seeds[:,-1]=True
 for x,y in holes:seeds[y,x]=True
 cleared=ndi.binary_propagation(seeds&near,mask=near)
 head=Image.new('L',(w,h));ImageDraw.Draw(head).polygon(HEAD,fill=255);head=np.asarray(head)>0
 if name.startswith('x29'):
  # Head exterior + enclosed spaces between hair/neck; white collar/eyes and
  # skin are outside this neutral-background range. No clothing/body re-paint.
  eyes=np.zeros((h,w),bool); eyes[380:555,540:733]=True
  cleared|=(dist<90)&(sat<25)&head&(lum>155)&~eyes
 if name=='g29_wrap':
  hair=np.zeros((h,w),bool);hair[60:345,260:685]=True
  edge=ndi.distance_transform_edt(~cleared)
  cleared|=hair&(edge<7)&(lum>205)&(sat<18)
 # Trim only original-background-colored pixels in a 2px EXTERIOR edge band.
 # Glasses, black outlines, white collar and internal hair/cloth texture remain.
 inside=~cleared;ed=ndi.distance_transform_edt(inside)
 cleared|=(ed<=2.2)&inside&(dist<53)&(sat<24)&(lum<235)&(lum>155)
 labels,n=ndi.label(~cleared);sizes=np.bincount(labels.ravel());solid=(sizes[labels]>75)&~cleared
 alpha=Image.fromarray((solid*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.3))
 if name=='x29_head_b':alpha=Image.fromarray(np.where(head,np.asarray(alpha),0).astype('uint8'))
 rgba=Image.fromarray(a).convert('RGBA');rgba.putalpha(alpha);dst=out/f'{name}.png';rgba.save(dst)
 bgim=Image.new('RGBA',rgba.size,(65,85,75,255));bgim.alpha_composite(rgba);
 if report:bgim.convert('RGB').save(report/(name+'_cutout_check.jpg'))
 entries.append(dict(source=src,source_sha256=hashlib.sha256(Path(src).read_bytes()).hexdigest(),derived=str(dst),derived_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),fixed_canvas=[1024,1536],method='Connected neutral-background mask; explicit empty-space seeds; 2px exterior neutral defringe; B limited to head/neck; no character paint or pose redraw'))
if report:(report/'asset_manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
