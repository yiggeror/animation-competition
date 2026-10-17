# Reproduce S07 mattes from accepted native sources. No pixels are repainted.
# Run: python3 -I tools/cutout_s07.py
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as ndi
from pathlib import Path
root=Path(__file__).resolve().parents[1]
# Same source-pixel/matte pipeline as tools/cutout.py. Use a closed silhouette
# before filling the enclosed collar/eyes/hair: global grey removal eats those.
for name,source,lum_limit in [('x07_flop','anim_07_xiaoman_flop.png',183),('g07_tiptoe','anim_07_grandma_tiptoe_v2_draft.png',192)]:
 im=Image.open(root/'collab/refs'/source).convert('RGB');rgb=np.asarray(im).astype(float)
 sat=rgb.max(2)-rgb.min(2);lum=rgb@np.array([.299,.587,.114])
 seed=(sat>30)|(lum<lum_limit)
 seed=ndi.binary_closing(seed,structure=np.ones((3,3)))
 lab,n=ndi.label(seed);sizes=np.bincount(lab.ravel());sizes[0]=0
 mask=lab==sizes.argmax();mask=ndi.binary_fill_holes(mask)
 mask=ndi.binary_opening(mask,structure=np.ones((2,2)))
 edge=ndi.distance_transform_edt(mask)<7
 mask &= ~(edge & (lum>165) & (sat<15))
 mask=ndi.binary_opening(mask,structure=np.ones((2,2)))
 alpha=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.45))
 out=im.convert('RGBA');out.putalpha(alpha);out.save(root/'assets/chars'/f'{name}.png')
 print(name,mask.sum())
