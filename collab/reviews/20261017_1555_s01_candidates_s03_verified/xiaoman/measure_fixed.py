from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.signal import fftconvolve
from scipy.ndimage import gaussian_filter1d
from scipy.stats import theilslopes
ROOT=Path(__file__).resolve().parent
MASTER=ROOT/'master.png'
POINTS=[[1410,528],[1379,614]]
CAMERA=(1453,539);CAMERA_BOX=(-14,-11,14,10)
CHECKS=[('near_elbow',[1119,854],[-40,-32,40,12]),('far_elbow',[1343,796],[-40,-32,40,12]),('hem',[681,814],[-40,-32,40,12])]
def composite(p):
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(128,128,128,255));bg.alpha_composite(im);return np.asarray(bg.convert('RGB'))
M=composite(MASTER)
def match(C,p,box):
 x,y=p;a,b,c,d=box;x0,y0,x1,y1=x+a,y+b,x+c,y+d
 t=np.asarray(Image.fromarray(M).convert('L'),float)[y0:y1,x0:x1];cg=np.asarray(Image.fromarray(C).convert('L'),float)
 search=20;sx0,sy0=x0-search,y0-search
 win=cg[sy0:y1+search,sx0:x1+search];t=t-t.mean();n=t.size
 num=fftconvolve(win,t[::-1,::-1],mode='valid');ones=np.ones(t.shape)
 s1=fftconvolve(win,ones,mode='valid');s2=fftconvolve(win*win,ones,mode='valid')
 den=np.sqrt(np.maximum(s2-s1*s1/n,1e-9))*math.sqrt((t*t).sum());ncc=num/den
 iy,ix=np.unravel_index(np.argmax(ncc),ncc.shape)
 def sub(a,i):
  if 0<i<len(a)-1:
   d=a[i-1]-2*a[i]+a[i+1];return i+(0.5*(a[i-1]-a[i+1])/d if d else 0)
  return float(i)
 fx,fy=sub(ncc[iy,:],ix),sub(ncc[:,ix],iy)
 return np.array([x-x0+sx0+fx,y-y0+sy0+fy]),float(ncc[iy,ix])
def edge(rgb):
 a=np.asarray(Image.fromarray(rgb.astype('uint8')).convert('L'),float);xs=np.arange(1392,1464);ys=[]
 for x in xs:
  ey=523-.15625*(x-1410);y0=round(ey)-3;v=a[y0-2:y0+9,x];g=gaussian_filter1d(v,.65,order=1)
  i=2+np.argmin(g[2:-2]);l=i+.5*(g[i-1]-g[i+1])/(g[i-1]-2*g[i]+g[i+1]);ys.append(l+y0-2)
 med=theilslopes(ys,xs-1418);err=np.array(ys)-(med[0]*(xs-1418)+med[1]);keep=abs(err)<.5
 slope,intercept=np.polyfit((xs-1418)[keep],np.array(ys)[keep],1)
 return {'slope':slope,'center_y_at_x1418':intercept,'deg':math.degrees(math.atan(slope)),'inliers':int(keep.sum()),'samples':[[int(x),float(y),bool(ok)]for x,y,ok in zip(xs,ys,keep)]}
me=edge(M);rows=[]
for path in sorted((ROOT/'raw').glob('*.png')):
 C=composite(path);e=edge(C);hit,score=match(C,CAMERA,CAMERA_BOX);deg=e['deg']-me['deg'];ang=math.radians(deg);c,s=math.cos(ang),math.sin(ang);R=np.array([[c,-s],[s,c]])
 forward=lambda p:(np.asarray(p)-CAMERA)@R.T+hit
 inverse=lambda p:(np.asarray(p)-hit)@R+CAMERA
 checks=[]
 for label,ref,box in CHECKS:
  pos,q=match(C,ref,box);reg=inverse(pos);checks.append({'label':label,'reference':ref,'window':box,'measured':pos.tolist(),'ncc_score':q,'registered':reg.tolist(),'residual_px':float(np.linalg.norm(reg-ref))})
 rows.append({'file':path.stem,'anchors':forward(POINTS).tolist(),'phone_edge':e,'camera_center':hit.tolist(),'camera_ncc_score':score,'fit_source_from_master':{'deg':deg,'scale':1},'checks':checks,'all_checks_under_3px':all(x['residual_px']<=3 for x in checks)})
 print(path.stem,'camera %.3f'%score,'angle %.4f'%deg,'checks',[round(x['residual_px'],3)for x in checks])
result={'method':'Same frozen phone hard-edge orientation plus camera NCC translation as first batch. Same two phone anchors and all three check-point coordinates. Original auxiliary NCC module was not in the repository; this self-contained reconstruction declares fixed check windows and evaluates old/new frames with the same windows. No check is used in fit. Scale remains 1.','target':{'width':1536,'height':1024,'anchors':POINTS},'camera_reference':CAMERA,'camera_window':CAMERA_BOX,'checks_definition':CHECKS,'master_edge':me,'frames':rows}
(ROOT/'anchors_fixed.json').write_text(json.dumps(result,indent=2)+'\n')
