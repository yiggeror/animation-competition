from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import label
from pathlib import Path
P=Path(__file__).parent;out=P/'candidate/assets/chars/s25_smooth_20261021';out.mkdir(parents=True,exist_ok=True)
# Only rigid similarity placement of each complete generated arm, never limb warping.
settings={52:[(1.14,(780,804),(875,940)),(1.14,(910,775),(1062,904))],60:[(1.0,(814,730),(905,875)),(1.0,(922,741),(1034,860))],68:[(1.0,(817,703),(938,803))],78:[(1.14,(831,660),(948,752))]}
for f,ss in settings.items():
 im=Image.open(P/('generated52_armroute.png' if f==52 else f'generated{f}_v2.png' if f==68 else f'generated{f}.png')).convert('RGBA');ar=np.array(im);canvas=Image.new('RGBA',(1920,1080))
 if len(ss)==2:
  labels,n=label(ar[:,:,3]>127);sizes=np.bincount(labels.ravel());idx=np.argsort(sizes[1:])[-2:]+1;idx=sorted(idx,key=lambda i:np.where(labels==i)[1].mean())
  layers=[]
  for i in idx:
   z=ar.copy();z[:,:,3]=np.where(labels==i,z[:,:,3],0);layers.append(Image.fromarray(z))
 else:layers=[im]
 for layer,(sc,src,dst) in zip(layers,ss):
  # Continue only the already cut, joint-free forearm below its source edge.
  z=np.array(layer); ys,xs=np.where(z[:,:,3]>127); bottom=int(ys.max()); spans=[]
  def runs(row):
   ids=np.where(row>127)[0];return np.split(ids,np.where(np.diff(ids)>1)[0]+1) if len(ids) else []
  pad=Image.new('RGBA',(layer.width,layer.height+600));d=ImageDraw.Draw(pad)
  for rr in runs(z[bottom,:,3]):
   if len(rr)<12:continue
   a,b=int(rr[0]),int(rr[-1]);prev=runs(z[max(0,bottom-20),:,3]);prev=min(prev,key=lambda q:abs(q.mean()-(a+b)/2))
   drift=((a+b)/2-prev.mean())/20*600
   strip=layer.crop((a,bottom,b+1,bottom+1)).resize((b-a+1,600))
   wide=Image.new('RGBA',pad.size);wide.alpha_composite(strip,(a,bottom))
   sheared=wide.transform(pad.size,Image.Transform.AFFINE,(1,-drift/600,drift/600*bottom,0,1,0),Image.Resampling.BICUBIC)
   pad.alpha_composite(sheared)
  pad.alpha_composite(layer);layer=pad
  tx=dst[0]-src[0]*sc;ty=dst[1]-src[1]*sc
  transformed=layer.transform((1920,1080),Image.Transform.AFFINE,(1/sc,0,-tx/sc,0,1/sc,-ty/sc),Image.Resampling.BICUBIC)
  canvas.alpha_composite(transformed)
 canvas.save(out/f'F{f:03}.png')
