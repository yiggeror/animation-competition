from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, scipy.ndimage as ndi
from scipy.spatial.distance import cdist
import json,math
P=Path(__file__).parent
mother=Image.open(P/'F116_lift_call01/S31_F116_CHARACTER.png').convert('RGBA')
def dots(im):
 a=np.asarray(im);y,x=np.ogrid[:a.shape[0],:a.shape[1]];mask=(a[:,:,0]>230)&(a[:,:,1]>215)&(a[:,:,2]>170)&(a[:,:,3]>220)&(x>440)&(x<850)&(y>445)&(y<1040)
 lab,n=ndi.label(mask);out=[]
 for i in range(1,n+1):
  yy,xx=np.where(lab==i)
  if len(xx)>45 and len(xx)<550 and np.ptp(xx)<34 and np.ptp(yy)<40:out.append([xx.mean(),yy.mean()])
 return np.array(out)
B=dots(mother)
for f in [120,129]:
 D=P/f'F{f}_wrist_call01';raw=Image.open(D/f'S31_F{f}_wrist_call01_RAW.png').convert('RGBA');A=dots(raw)
 # Fit one global similarity, robust matching of native unchanged white-dot centres.
 pred=A-np.array([18,0]);ids=np.argmin(cdist(pred,B),axis=1);dist=np.min(cdist(pred,B),axis=1);q=dist<18;aa=A[q];bb=B[ids[q]]
 for _ in range(5):
  T=np.zeros((2*len(aa),4));v=bb.reshape(-1)
  T[0::2,0]=aa[:,0];T[0::2,1]=-aa[:,1];T[0::2,2]=1;T[1::2,0]=aa[:,1];T[1::2,1]=aa[:,0];T[1::2,3]=1
  z=np.linalg.lstsq(T,v,rcond=None)[0];fit=(T@z).reshape(-1,2);err=np.linalg.norm(fit-bb,axis=1);keep=err<max(2.5,np.median(err)*2);aa=aa[keep];bb=bb[keep]
 a,b,tx,ty=z;scale=math.hypot(a,b);theta=math.atan2(b,a);den=a*a+b*b;aff=(a/den,b/den,(-a*tx-b*ty)/den,-b/den,a/den,(b*tx-a*ty)/den)
 reg=raw.transform(mother.size,Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC);reg.save(D/'REGISTERED_RAW.png')
 j={'method':'One global similarity fitted to matched original unchanged white-dot centres, no local hand warp','params_scale_rotation_tx_ty':[scale,theta,tx,ty],'pointPairs':[{'raw':p.tolist(),'locked':q.tolist()}for p,q in zip(aa,bb)],'rmsPx':float(np.sqrt(np.mean(err[keep]**2)))};(D/'REGISTRATION.json').write_text(json.dumps(j,indent=2)+'\n');print(f,len(aa),j['params_scale_rotation_tx_ty'],j['rmsPx'])
 c=Image.new('RGBA',mother.size,'#c1c4bc');c.alpha_composite(reg);d=ImageDraw.Draw(c)
 for x in range(240,431,10):d.line([(x,170),(x,485)],fill=(20,115,150,100),width=1);d.text((x+1,172),str(x),fill='#183f52')
 for y in range(180,481,10):d.line([(230,y),(440,y)],fill=(20,115,150,100),width=1);d.text((231,y+1),str(y),fill='#183f52')
 c.crop((230,170,445,485)).resize((645,945)).convert('RGB').save(D/'REGISTERED_FOREARM_GRID.jpg',quality=95)
