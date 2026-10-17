from pathlib import Path
import json,math,sys,hashlib
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
ROOT=Path(__file__).parent
SOURCE=ROOT.parent.parent/'batch2_scope/refs/x31_flashlight_face.png'
POINTS={'A':(272,1187,32),'B':(630,1176,32),'H':(530,873,32),'right_fist':(477,642,40),'left_palm':(850,607,32),'rod_tip':(938,476,20),'collar':(570,597,32),'jaw':(473,510,24)}
def rgb(im):
 im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,(48,52,59,255));bg.alpha_composite(im);return np.asarray(bg.convert('RGB'),dtype=float)
def gray(a):return a@np.array([.299,.587,.114])
def match(master,cand,key,radius=64):
 x,y,h=POINTS[key];T=gray(master[y-h:y+h+1,x-h:x+h+1]);ox=x-h-radius;oy=y-h-radius;S=gray(cand[oy:y+h+radius+1,ox:x+h+radius+1]);ones=np.ones(T.shape);n=T.size;z=T-T.mean();num=fftconvolve(S,z[::-1,::-1],mode='valid');su=fftconvolve(S,ones,mode='valid');ss=fftconvolve(S*S,ones,mode='valid');den=np.sqrt(np.maximum(ss-su*su/n,0)*np.sum(z*z));score=num/np.maximum(den,1e-8);iy,ix=np.unravel_index(np.argmax(score),score.shape);p=np.array([ox+ix+h,oy+iy+h],float)
 # Rival maxima outside +/-5px protect against repetitive dot ambiguity.
 rivals=score.copy();rivals[max(0,iy-5):iy+6,max(0,ix-5):ix+6]=-2
 return {'point_normalized':p.tolist(),'ncc':float(score[iy,ix]),'rival_ncc':float(rivals.max())}
def fit(src,dst):
 va=src[1]-src[0];vr=dst[1]-dst[0];c=np.dot(va,vr)/np.dot(va,va);d=np.cross(va,vr)/np.dot(va,va);R=np.array([[c,-d],[d,c]]);t=dst[0]-R@src[0];return R,t
def measure(master,cand):
 matches={k:match(master,cand,k) for k in POINTS};a=np.array([matches[k]['point_normalized'] for k in ['A','B']]);r=np.array([POINTS[k][:2] for k in ['A','B']]);R,t=fit(a,r)
 for k,m in matches.items():m['registered_normalized']=(R@np.array(m['point_normalized'])+t).tolist();m['residual_px']=float(np.linalg.norm(np.array(m['registered_normalized'])-np.array(POINTS[k][:2])))
 return {'matches':matches,'M_normalized':[R[0,0],R[1,0],R[0,1],R[1,1],t[0],t[1]],'H_pass':matches['H']['residual_px']<=3,'note':'H never enters fit. Diagnostic anatomy points are secondary checks, not fit anchors. NCC only establishes local texture alignment, not anatomical validity.'}
def selftest():
 im=rgb(Image.open(SOURCE));I=measure(im,im);T=measure(im,np.roll(np.roll(im,7,axis=1),-5,axis=0));bad=im.copy();x,y,h=POINTS['H'];bad[y-48:y+49,x-48:x+49]=np.roll(im[y-48:y+49,x-48:x+49],8,axis=1);B=measure(im,bad)
 assert all(m['residual_px']<1e-8 for m in I['matches'].values());assert max(m['residual_px'] for m in T['matches'].values())<1e-8;assert B['matches']['H']['residual_px']>=7.9 and not B['H_pass']
 return {'identity':I,'translation_7_minus5':T,'held_out_H_only_shift8':B,'passed':True,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
if __name__=='__main__':
 if len(sys.argv)==1:result=selftest();out=ROOT/'measurement_selftest.json'
 else:
  path=Path(sys.argv[1]);im=Image.open(path).convert('RGBA');w,h=im.size;master=rgb(Image.open(SOURCE));cand=rgb(im.resize((1024,1536),Image.Resampling.LANCZOS));result=measure(master,cand);result['candidate_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();result['candidate_size']=[w,h]
  for m in result['matches'].values():m['point_raw']=[m['point_normalized'][0]*w/1024,m['point_normalized'][1]*h/1536]
  M=result['M_normalized'];result['M_raw']=[M[0]*1024/w,M[1]*1024/w,M[2]*1536/h,M[3]*1536/h,M[4],M[5]];out=ROOT/'candidate_measurement.json'
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'output':str(out),'passed':result.get('passed'),'H_pass':result.get('H_pass'),'H_residual':result.get('matches',{}).get('H',{}).get('residual_px')}))
