"""Replay only the actual generated eye/brow patch, with frozen registration."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
z=json.loads((P/'provenance/F024_preparation.json').read_text())
s,x0,y0=z['donor_uniform_registration']
reg=Image.open(P/'originals/F024_call01_raw.png').transform((410,235),Image.Transform.AFFINE,(s,0,x0,0,s,y0),resample=Image.Resampling.BICUBIC)
d=np.array(reg).astype(float);d[:,:,:3]=(d[:,:,:3]+z['skin_RGB_offset']).clip(0,255)
a=np.array(Image.open(P.parent/'F000_repair/candidate/F000_repaired.png'))
y,x=np.indices((1080,1920));mask=np.zeros((1080,1920),float)
for cx,cy,rx,ry in [(857,507,65,56),(1063,501,65,56)]:
    r=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)
    mask=np.maximum(mask,np.clip((1-r)*min(rx,ry)/3,0,1))
mask=np.maximum(mask,np.clip(np.minimum.reduce([x-788,1145-x,y-358,433-y])/4,0,1))
w=mask[350:585,760:1170,None]
a[350:585,760:1170]=(a[350:585,760:1170]*(1-w)+d*w).round().clip(0,255).astype('uint8')
Image.fromarray(a).save(P/'candidate/F024.png')
print('F024 actual donor patch replayed; no new image call.')
