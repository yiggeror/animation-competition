from pathlib import Path
import json, math, hashlib, subprocess
import numpy as np
from PIL import Image,ImageDraw
from scipy.signal import fftconvolve
P=Path(__file__).resolve().parent
TOOLS=P/'tools_snapshot'
POINTS=[(165,1084),(843,1147),(594,1111)]
PATCHES=[(-35,-25,35,25),(-30,-25,30,25),(-35,-35,35,35)]
SEARCH=40
def gray(im):
 b=Image.new('RGBA',im.size,(128,128,128,255));b.alpha_composite(im.convert('RGBA'));return b.convert('L')
def match(m,c,p,patch,s):
 x0,y0,x1,y1=[p[i%2]+patch[i] for i in range(4)]
 t=np.asarray(m.crop((x0,y0,x1,y1)).resize((round((x1-x0)*s),round((y1-y0)*s)),Image.Resampling.LANCZOS),float)
 sx0,sy0=int(x0*s)-SEARCH,int(y0*s)-SEARCH
 pad=SEARCH+2;big=np.pad(np.asarray(c,float),pad,constant_values=128)
 win=big[sy0+pad:sy0+pad+t.shape[0]+2*SEARCH,sx0+pad:sx0+pad+t.shape[1]+2*SEARCH]
 t-=t.mean();n=t.size;ones=np.ones(t.shape)
 num=fftconvolve(win,t[::-1,::-1],mode='valid');s1=fftconvolve(win,ones,mode='valid');s2=fftconvolve(win*win,ones,mode='valid')
 ncc=num/(np.sqrt(np.maximum(s2-s1*s1/n,1e-9))*math.sqrt((t*t).sum()))
 iy,ix=np.unravel_index(np.argmax(ncc),ncc.shape)
 def sub(a,i):
  if 0<i<len(a)-1:
   d=a[i-1]-2*a[i]+a[i+1];return i+(0.5*(a[i-1]-a[i+1])/d if d else 0)
  return i
 return np.array([(p[0]-x0)*s+sx0+sub(ncc[iy,:],ix),(p[1]-y0)*s+sy0+sub(ncc[:,ix],iy)]),float(ncc[iy,ix])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
master=Image.open(P/'originals/g03_watermelon_k01.png').convert('RGBA');mg=gray(master);out=[]
(P/'diagnostics/registered_rgba').mkdir(exist_ok=True)
marked=gray(master).convert('RGB');d=ImageDraw.Draw(marked)
for i,(p,r) in enumerate(zip(POINTS,PATCHES)):
 col=['red','blue','green'][i];d.rectangle([p[0]+r[0],p[1]+r[1],p[0]+r[2],p[1]+r[3]],outline=col,width=3);d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=col);d.text((p[0]+8,p[1]),['A','B','H'][i]+str(p),fill=col)
marked.save(P/'diagnostics/master_anchor_patches.png')
for src in sorted((P/'originals').glob('g03_watermelon_k*.png')):
 im=Image.open(src).convert('RGBA');nom=math.sqrt(im.width*im.height/(master.width*master.height));cg=gray(im)
 if src.stem.endswith('k01'):matches=[(np.array(p,float),1.) for p in POINTS]
 else:matches=[match(mg,cg,p,r,nom) for p,r in zip(POINTS,PATCHES)]
 a,b,h=[x[0] for x in matches];target=np.array(POINTS,float);u=b-a;v=target[1]-target[0];sc=np.linalg.norm(v)/np.linalg.norm(u);ang=math.atan2(v[1],v[0])-math.atan2(u[1],u[0]);mat=sc*np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]]);trans=target[0]-mat@a;mapped=mat@h+trans;res=float(np.linalg.norm(mapped-target[2]))
 inv=np.linalg.inv(mat);off=-inv@trans
 reg=im.transform(master.size,Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),Image.Resampling.BICUBIC)
 regpath=P/'diagnostics/registered_rgba'/src.name;reg.save(regpath)
 rec={'file':src.stem,'source':str(src),'sha256':sha(src),'size':list(im.size),'anchors':[a.tolist(),b.tolist()],'holdout_native':h.tolist(),'target_holdout':list(POINTS[2]),'holdout_mapped':mapped.tolist(),'score':[x[1] for x in matches],'check_residual_px':res,'passes_3px':res<=3,'matrix':mat.tolist(),'translation':trans.tolist(),'registered_path':str(regpath),'registered_sha256':sha(regpath)};out.append(rec)
 print(src.stem,'NCC',*[round(x[1],4) for x in matches],'holdout',round(res,4),'PASS' if res<=3 else 'REJECT',flush=True)
 dst=P/'assets/chars'/src.name
 if dst.exists() and dst.with_name(dst.stem+'_n.png').exists() and dst.with_name(dst.stem+'_m.png').exists(): continue
 aimg=np.asarray(im.getchannel('A'),np.float32);im.putalpha(Image.fromarray(np.round(np.clip((aimg-6)/241,0,1)*255).astype('uint8')));im.save(dst)
 for script,args in [('card_maps.py',[dst,dst.with_name(dst.stem+'_n.png'),dst.with_name(dst.stem+'_m.png')]),('card_soft.py',[dst,dst.with_name(dst.stem+'_n.png')])]:
  subprocess.run(['python3','-I',str(TOOLS/script)]+list(map(str,args)),check=True,stdout=subprocess.DEVNULL)
(P/'registration_measurements.json').write_text(json.dumps({'method':'Two fixed lower-garment NCC patch centers, global similarity only; third independently matched clothing holdout. These are not rigid world/stool anchors. No manual target fitting or local deformation.','target_size':list(master.size),'target_anchors':POINTS[:2],'holdout':POINTS[2],'patches':PATCHES,'search_native_px':SEARCH,'frames':out},ensure_ascii=False,indent=2)+'\n')
