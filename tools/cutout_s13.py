"""S13: reviewed A torso, aligned B head, source-pixel mouth layers.
Usage: python tools/cutout_s13.py A.png B.png --report-dir /tmp/s13-proof
No generation or character painting. B moves (+1,+29) before head isolation.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
p=argparse.ArgumentParser();p.add_argument('a');p.add_argument('b');p.add_argument('--out',default='assets/chars');p.add_argument('--report-dir');args=p.parse_args()
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
report=Path(args.report_dir) if args.report_dir else None
if report:report.mkdir(parents=True,exist_ok=True)
SIZE=(1024,1536);DX=1;DY=29

def cutout(src,eyes,mouth_box):
    rgb=np.asarray(Image.open(src).convert('RGB')).copy();h,w=rgb.shape[:2]
    if (w,h)!=SIZE:raise ValueError('S13 originals must be 1024 x 1536')
    bg=np.median(np.concatenate([rgb[:8].reshape(-1,3),rgb[-8:].reshape(-1,3),rgb[:,:8].reshape(-1,3),rgb[:,-8:].reshape(-1,3)]),axis=0)
    dist=np.linalg.norm(rgb.astype(float)-bg,axis=-1);sat=rgb.max(-1).astype(float)-rgb.min(-1);lum=rgb.mean(-1)
    near=(dist<90)&(sat<26)&(lum>155)&(lum<235)
    seeds=np.zeros((h,w),bool);seeds[0]=seeds[-1]=True;seeds[:,0]=seeds[:,-1]=True
    cleared=ndi.binary_propagation(seeds&near,mask=near)
    safe=np.zeros((h,w),bool)
    for x0,y0,x1,y1 in [eyes,mouth_box]:safe[y0:y1,x0:x1]=True
    head_region=np.indices((h,w))[0]<1090
    cleared|=near&head_region&~safe  # enclosed empty spaces between braids/neck
    yy,xx=np.indices((h,w));hair_zone=(yy<950)|(xx<290)|(xx>750)
    cleared|=(dist<105)&(sat<28)&(lum>155)&hair_zone&head_region&~safe
    labels,_=ndi.label(~cleared);sizes=np.bincount(labels.ravel());solid=(sizes[labels]>80)&~cleared
    alpha=np.asarray(Image.fromarray((solid*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.35))).copy()
    # Feather RGB comes from the nearest opaque foreground, never the gray matte.
    core=solid&(ndi.distance_transform_edt(solid)>1.3)
    _,idx=ndi.distance_transform_edt(~core,return_indices=True)
    edge=(alpha>0)&(alpha<250);rgb[edge]=rgb[idx[0][edge],idx[1][edge]]
    return np.dstack([rgb,alpha])

A=cutout(args.a,(510,510,805,725),(680,730,780,825));B0=cutout(args.b,(200,575,590,720),(315,745,425,885))
B=np.zeros_like(B0);B[DY:,DX:]=B0[:-DY,:-DX]
# Follow the original A collar/shoulder top, including the skin opening.
body_path=[(0,1536),(0,1150),(160,1110),(240,1050),(297,1013),(311,997),(350,971),(381,955),(398,952),(411,960),(393,972),(403,989),(435,1015),(480,1042),(534,1067),(575,1080),(599,1068),(620,1045),(637,1012),(633,995),(596,970),(595,950),(627,958),(667,975),(710,1013),(760,1024),(815,1060),(865,1140),(1024,1250),(1024,1536)]
m=Image.new('L',SIZE);ImageDraw.Draw(m).polygon(body_path,fill=255);body=np.asarray(m)>0
rgb=A[:,:,:3].astype(float);Y=np.indices(A.shape[:2])[0]
yellow=(rgb[:,:,0]>160)&(rgb[:,:,1]>130)&(rgb[:,:,2]<150)&((rgb[:,:,0]-rgb[:,:,2])>60)&((rgb[:,:,1]-rgb[:,:,2])>45)&(Y>975)
body|=ndi.binary_dilation(yellow,iterations=3)
head=~body
# Neck overlap stays behind A's collar during the small rigid anticipation/settle.
neck=np.zeros_like(head);neck[940:1100,390:645]=True
head|=ndi.binary_dilation(head,iterations=12)&neck
head&=(Y<1088)  # no B shoulder outlines may survive below the two braids

def layer(rgba,mask):
    r=rgba.copy();r[:,:,3]=(r[:,:,3].astype(float)*mask).round().astype('uint8');return r

# A's lower neck is a fixed underlap with a short spatial feather, covering
# B's original collar line without moving A's collar or stretching either neck.
neck_root=np.zeros_like(Y,dtype=float);neck_root[:,390:650]=np.clip((Y[:,390:650]-1000)/40,0,1)
neck_root[Y>1100]=0
body_weight=np.maximum(body.astype(float),neck_root)
bodyA=layer(A,body_weight);headA=layer(A,head);headB=layer(B,head)
# Copy a clear neighboring B cheek patch behind the original mouth. The animated
# aperture is the original outlined mouth texture, not a newly drawn lip/teeth shape.
# Coordinates below are in B aligned to A (+1,+29 px).
mouth_roi=np.zeros_like(head);mouth_roi[780:892,320:420]=True
brgb=B[:,:,:3].astype(float)
feature=mouth_roi&((brgb.mean(-1)<145)|((brgb[:,:,0]-brgb[:,:,1])>65))
# Keep every outlined-mouth component: the upper lip is separated from the
# dark interior by the white tooth and must not remain as a floating mark.
mouth_core=ndi.binary_fill_holes(feature)
mm=Image.fromarray((ndi.binary_dilation(mouth_core,iterations=3)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.65))
mouthmask=np.asarray(mm,dtype=float)/255
mouth=layer(headB,mouthmask)
# Replacement is sampled from the same source, 90px to the right of the mouth.
clean=headB.copy();shift=np.roll(headB[:,:,:3],-90,axis=1)
fill=np.asarray(Image.fromarray((ndi.binary_dilation(mouth_core,iterations=12)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(4)),dtype=float)/255
fill[ndi.binary_dilation(mouth_core,iterations=4)]=1
clean[:,:,:3]=(headB[:,:,:3]*(1-fill[:,:,None])+shift*fill[:,:,None]).round().astype('uint8')
outputs={'x13_body_a':bodyA,'x13_head_a':headA,'x13_head_b':clean,'x13_mouth_b':mouth}
entries=[]
for name,rgba in outputs.items():
    dst=out/(name+'.png');Image.fromarray(rgba,'RGBA').save(dst)
    entries.append({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
    if report:
        check=Image.new('RGBA',SIZE,(54,65,51,255));check.alpha_composite(Image.fromarray(rgba,'RGBA'));check.convert('RGB').save(report/(name+'_check.jpg'))
if report:
    for name,rgba in [('A_cutout',A),('B_aligned_cutout',B)]:Image.fromarray(rgba,'RGBA').save(report/(name+'.png'))
    (report/'asset_manifest.json').write_text(json.dumps({'sources':[{'path':s,'sha256':hashlib.sha256(Path(s).read_bytes()).hexdigest()} for s in [args.a,args.b]],'canvas':SIZE,'b_alignment':[DX,DY],'body_path':body_path,'mouth_center':[370,827],'mouth_cheek_sample_offset':[90,0],'method':'Source-pixel layers, connected neutral background removal with eye protection; exterior RGB decontamination; A collar and shoulders fixed; B head/neck only; local mouth source cutout and same-B skin patch. No image generation.','outputs':entries},indent=2)+'\n')
