#!/usr/bin/env python3
"""Limited new-forearm colour finishing against mother and approved dark planes."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;name=sys.argv[1];p=HERE/name
TAG='_edge_aligned' if len(sys.argv)>2 and sys.argv[2]=='edge_aligned' else ''
policy=json.loads((HERE/'provenance/colour_policy.json').read_text())[name]
def smooth(lo,hi,z):
 t=np.clip((z-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def profile(a):
 h=a.shape[0];pr=np.zeros((520,4),float)
 for x in range(520):
  ls,n=nd.label(a[:,x,3]>=128);runs=[np.where(ls==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15];assert len(runs)==2
  pr[x]=[runs[0][0],runs[0][-1],runs[1][0],runs[1][-1]]
 clip=pr[:,3]>=h-2;xs=np.where((~clip)&(np.arange(520)<320))[0][:120];fit=np.polyfit(xs,pr[xs,3],1);pr[clip,3]=np.maximum(h-1,np.polyval(fit,np.where(clip)[0]))
 return nd.gaussian_filter1d(pr,sigma=3,axis=0)
def read(path):return np.array(Image.open(path).convert('RGBA'))
def compose(a,c=(115,115,115)):
 im=Image.new('RGBA',(a.shape[1],a.shape[0]),(*c,255));im.alpha_composite(Image.fromarray(a));return im.convert('RGB')
motherpath=ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png'
darkpath=ROOT/'third_push_shadow_084_090/candidate/F090_shadow_fixed.png'
mother,dark=read(motherpath),read(darkpath)
assert hashlib.sha256(darkpath.read_bytes()).hexdigest()=='cabe79438fa626ff0ce7a36e6447a4b8dbac4755528479fce125323a3a68d805'
src=p/'candidate'/f'{name}_mapped{TAG}.png';a=read(src);h,w=a.shape[:2];pr=profile(a);mp=profile(mother);dp=profile(dark)
semantic=np.zeros((h,w),np.uint8);depth=np.full((h,w),-1.);md=np.zeros((h,w,3));dd=np.zeros_like(md);yy=np.arange(h)
for x in range(520):
 for arm in range(2):
  top,bottom=pr[x,arm*2:arm*2+2];t=(yy-top)/(bottom-top);m=(t>=0)&(t<=1)&(a[:,x,3]>=128);semantic[m,x]=arm+1;depth[m,x]=t[m]
  for reference,rp,out in [(mother,mp,md),(dark,dp,dd)]:
   rt,rb=rp[x,arm*2:arm*2+2];ry=rt+t*(rb-rt)
   for k in range(3):out[m,x,k]=np.interp(ry,yy,reference[:,x,k])[m]-a[m,x,k].astype(float)
rgb=a[:,:,:3].astype(float)
ink=(a[:,:,3]>0)&((rgb[:,:,0]<=210)|(rgb[:,:,1]<=135)|(rgb[:,:,2]<=100));ink=nd.binary_dilation(ink,iterations=2)
contour=nd.binary_dilation(a[:,:,3]<128,iterations=3)&(a[:,:,3]>0);protected=ink|contour|(a[:,:,3]<240)
edge=smooth(2,9,nd.distance_transform_edt((semantic>0)&~protected));along=1-smooth(400,520,np.arange(w)[None,:])
darkfield=smooth(.60,.70,depth)*(1-smooth(.88,.98,depth))*edge*along
light=rgb@np.array([.2126,.7152,.0722]);midfield=(1-smooth(.56,.74,depth))*smooth(198,212,light)*edge*along*(semantic>0)
addition=np.zeros_like(rgb);weights={}
for area in ['middle','dark']:
 for label,strength in policy.get(area,{}).items():
  arm,channel=label.split('_');region=semantic=={'adult':1,'child':2}[arm];k='RGB'.index(channel);strength=float(strength)
  # Calibrate only where the chosen mother/approved reference supports the sign.
  deficit=md[:,:,k] if area=='middle' else dd[:,:,k]
  signed=nd.gaussian_filter(deficit*region,sigma=(3,7))*np.sign(strength)
  gate=smooth(.25,1.25,signed);weight=(midfield if area=='middle' else darkfield)*region*gate
  addition[:,:,k]+=strength*weight;weights[area+'_'+label]=weight
delta=np.rint(addition).astype(np.int16);out=a.copy();out[:,:,:3]=np.clip(a[:,:,:3].astype(np.int16)+delta,0,255).astype(np.uint8)
assert np.array_equal(a[:,:,3],out[:,:,3]) and np.array_equal(a[:,520:],out[:,520:]) and np.array_equal(a[protected],out[protected])
assert not np.any(delta[:,:,0])
if not policy.get('middle'):assert np.array_equal(a[(semantic>0)&(depth<=.60)],out[(semantic>0)&(depth<=.60)])
(p/'masks').mkdir(exist_ok=True)
for label,weight in weights.items():Image.fromarray(np.rint(weight*65535).astype(np.uint16)).save(p/'masks'/(label+TAG+'_weight16.png'))
Image.fromarray(protected.astype(np.uint8)*255).save(p/('masks/colour_protected'+TAG+'.png'))
Image.fromarray(np.any(delta,axis=2).astype(np.uint8)*255).save(p/('masks/colour_actual_changed'+TAG+'.png'))
Image.fromarray(np.clip(128+delta*24,0,255).astype(np.uint8)).save(p/('masks/colour_signed_RGB_bias128_x24'+TAG+'.png'))
np.savez_compressed(p/('provenance/colour_fields'+TAG+'.npz'),semantic=semantic,depth=depth.astype(np.float32),mother_RGB_deficit=md.astype(np.float32),approved_dark_RGB_deficit=dd.astype(np.float32),signed_RGB_delta=delta,**{k:v.astype(np.float32) for k,v in weights.items()})
dest=p/'candidate'/f'{name}_final{TAG}.png';Image.fromarray(out).save(dest)
for kind,c in [('gray',(115,115,115)),('dark',(32,32,32))]:compose(out,c).save(p/'qa'/f'{name}_final{TAG}_on_{kind}.png')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);board=Image.new('RGB',(1800,773),(25,25,25));d=ImageDraw.Draw(board)
for i,(title,b) in enumerate([('Approved090 / calibrated dark',dark),(name+' / mapped before',a),(name+' / final',out)]):
 board.paste(compose(b).crop((0,200,600,941)),(600*i,32));d.text((600*i+8,5),title,font=font,fill='white')
board.save(p/'qa'/f'{name}_090_before_after{TAG}_native.png');compose(out).crop((470,260,1120,750)).resize((1300,980)).save(p/'qa'/f'{name}_final{TAG}_contact_2x.png')
def samples(b):
 result={}
 for f in [.2,.5,.65,.8,.9]:
  v=[[],[]]
  for x in range(250,351):
   ls,n=nd.label(b[:,x,3]>=128);runs=[np.where(ls==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15]
   for i,r in enumerate(runs):
    y=round(r[0]+f*(r[-1]-r[0]));v[i].append(b[y-2:y+3,x,:3])
  result[str(f)]={label:np.median(np.concatenate(v[i]),axis=0).tolist() for i,label in enumerate(['adult','child'])}
 return result
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
record=dict(source_sha256=sha(src),final_sha256=sha(dest),mother_sha256=sha(motherpath),approved_dark_sha256=sha(darkpath),policy=policy,alpha_ink_and_contact_exact=True,RGB_min_delta=delta.min(axis=(0,1)).tolist(),RGB_max_delta=delta.max(axis=(0,1)).tolist(),samples=dict(F024=samples(mother),approved_F090=samples(dark),before=samples(a),after=samples(out)),new_image_calls=0)
(p/('provenance/colour_checks'+TAG+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
