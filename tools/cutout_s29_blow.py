"""Reproduce reviewed S29 preparation card and S30 head-shadow mask.

Usage: python tools/cutout_s29_blow.py collab/refs/anim_29_grandma_prepare_blow.png --out assets/chars --report-dir /tmp/s29-blow-proof
Only extracts source pixels, derives alpha/normals/material; does not repaint anatomy.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source');p.add_argument('--out',default='assets/chars');p.add_argument('--report-dir')
a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
rgb=np.asarray(Image.open(a.source).convert('RGB'));lum=rgb.mean(-1);sat=rgb.max(-1).astype(float)-rgb.min(-1)
# This source has neutral grey background, while grey hair is slightly warm.
# Flood the exterior, then remove the same neutral background enclosed by
# thin hair loops / the far spectacle rim. Keep dark frame and white glints.
near=(sat<=5)&(lum>85)&(lum<203)
seed=np.zeros(lum.shape,bool);seed[0]=True;seed[-1]=True;seed[:,0]=True;seed[:,-1]=True
cleared=ndi.binary_propagation(seed&near,mask=near)
cleared|=(sat<=4)&(lum>140)&(lum<181)
labels,n=ndi.label(~cleared);sizes=np.bincount(labels.ravel());solid=(sizes[labels]>65)&~cleared
alpha=Image.fromarray(np.uint8(solid)*255).filter(ImageFilter.GaussianBlur(.3))
card=Image.fromarray(rgb).convert('RGBA');card.putalpha(alpha)
alb=out/'g29_prepare_blow.png';card.save(alb)
# The shadow is head, hair, bun, beads and necessary neck ONLY. Source right
# shoulder is cropped at x1023/y890 and must never enter the projection.
# The lower neck ends below the final S30 frame; it is not a floating cutout.
keep=Image.new('L',card.size)
ImageDraw.Draw(keep).polygon([(0,0),(1024,0),(1024,750),(702,750),(677,843),(642,952),(570,1058),(531,978),(493,917),(459,881),(431,851),(410,841),(0,900)],fill=255)
shadow=Image.new('RGBA',card.size,(0,0,0,0));shadow.putalpha(Image.fromarray(np.minimum(np.asarray(alpha),np.asarray(keep))))
sh=out/'g29_prepare_blow_shadow.png';shadow.save(sh)
nrm=out/'g29_prepare_blow_n.png';mat=out/'g29_prepare_blow_m.png'
subprocess.run([sys.executable,'-I',str(Path(__file__).with_name('card_maps.py')),str(alb),str(nrm),str(mat),'35','.55'],check=True)
if a.report_dir:
 d=Path(a.report_dir);d.mkdir(parents=True,exist_ok=True)
 b=Image.new('RGBA',card.size,(42,61,54,255));b.alpha_composite(card);b.convert('RGB').save(d/'cutout_check.jpg')
 manifest={'source':str(Path(a.source)),'source_sha256':hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),'outputs':[{ 'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in[alb,nrm,mat,sh]],'method':'neutral-background extraction, separate original head/neck alpha; existing card_maps.py normal/material derivation, radius35 greyTop0.55','canvas':[1024,1536]}
 (d/'asset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
