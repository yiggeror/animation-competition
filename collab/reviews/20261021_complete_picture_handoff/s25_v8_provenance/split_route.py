from PIL import Image
import numpy as np
from scipy.ndimage import label
from pathlib import Path
P=Path(__file__).parent;O=P/'candidate/assets/chars/s25_smooth_20261021'
for f in [52,56,60]:
 im=Image.open(O/f'F{f:03}.png').convert('RGBA');a=np.array(im);lab,n=label(a[:,:,3]>100);siz=np.bincount(lab.ravel());ids=np.argsort(siz[1:])[-2:]+1;ids=sorted(ids,key=lambda i:np.where(lab==i)[1].mean())
 for side,i in zip(['L','R'],ids):
  b=a.copy();b[:,:,3]=np.where(lab==i,b[:,:,3],0);Image.fromarray(b).save(O/f'{side}{f:03}.png')
im=Image.open(P/'release36.png').convert('RGBA');a=np.array(im);lab,n=label(a[:,:,3]>100);sizes=np.bincount(lab.ravel());ids=np.argsort(sizes[1:])[-2:]+1;i=max(ids,key=lambda i:np.where(lab==i)[1].mean());a[:,:,3]=np.where(lab==i,a[:,:,3],0);im=Image.fromarray(a);sc=.52;tx=1030-1000*sc;ty=955-635*sc;im=im.transform((1920,1080),Image.Transform.AFFINE,(1/sc,0,-tx/sc,0,1/sc,-ty/sc),Image.Resampling.BICUBIC);im.save(O/'R036.png')
