#!/usr/bin/env python3
"""Limited homologous dark-side colour repair; all source geometry is immutable."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
EXPECTED={'F084':'cd5d4d79d00b9cdaab4e261cfe71d9ace543533d5b6d32bc93721608a25f4de0','F090':'751693d6cbfd6ad5e7182dc2309639ebbbb5c144c25cafa9424877a759636dfa'}
for sub in ['candidate','masks','qa','provenance']:(HERE/sub).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pixel_sha=lambda a:hashlib.sha256(a.tobytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def smooth(lo,hi,z):
 t=np.clip((z-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def profiles(a):
 p=np.zeros((520,4),float);h=a.shape[0]
 for x in range(520):
  labels,n=nd.label(a[:,x,3]>=128);runs=[np.where(labels==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15];assert len(runs)==2
  p[x]=[runs[0][0],runs[0][-1],runs[1][0],runs[1][-1]]
 # The lower arm is cropped at the bottom-left. Infer its hidden continuation
 # only to locate the semantic colour field, never to alter a silhouette.
 clipped=p[:,3]>=h-2
 visible=np.where((~clipped)&(np.arange(520)<320))[0]
 fitx=visible[:120];coef=np.polyfit(fitx,p[fitx,3],1)
 p[clipped,3]=np.maximum(h-1,np.polyval(coef,np.where(clipped)[0]))
 # A colour field follows continuous form, not one-pixel raster quantization
 # or the old bottom-crop transition. Smooth only the normalization profiles.
 p=nd.gaussian_filter1d(p,sigma=3,axis=0)
 return p,dict(clipped_columns=np.where(clipped)[0].tolist(),fit_visible_columns=[int(fitx[0]),int(fitx[-1])],hidden_boundary_linear_fit=coef.tolist(),profile_smoothing_sigma_columns=3,purpose='Mask semantic depth only; no drawing or alpha changed.')
def composite(a,c=(115,115,115)):
 im=Image.new('RGBA',(a.shape[1],a.shape[0]),(*c,255));im.alpha_composite(Image.fromarray(a));return im.convert('RGB')
refpath=ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png'
assert sha(refpath)=='97560237598d024a725ab63ee62809d1f5ded5f6fc5aadc1d8a4f158ca85da4a'
reference=np.array(Image.open(refpath).convert('RGBA'));rp,rclip=profiles(reference)
images={'F024':reference,'F066':np.array(Image.open(ROOT/'second_push_colour_060_066/candidate/F066_colour_fixed.png').convert('RGBA'))}
all_checks={}
for name in ['F084','F090']:
 src=ROOT/'third_push_084_090'/name/'candidate'/f'{name}_final.png';assert sha(src)==EXPECTED[name]
 a=np.array(Image.open(src).convert('RGBA'));h,w=a.shape[:2];p,clip=profiles(a)
 semantic=np.zeros((h,w),np.uint8);depth=np.full((h,w),-1.,float);deficit=np.zeros((h,w,3),float)
 yy=np.arange(h)
 for x in range(520):
  for i in range(2):
   top,bottom=p[x,2*i:2*i+2];t=(yy-top)/(bottom-top)
   m=(t>=0)&(t<=1)&(a[:,x,3]>=128);semantic[m,x]=i+1;depth[m,x]=t[m]
   rt,rb=rp[x,2*i:2*i+2];ry=rt+t*(rb-rt)
   for k in range(3):
    target=np.interp(ry,yy,reference[:,x,k]);deficit[m,x,k]=target[m]-a[m,x,k].astype(float)
 # Wide, soft field: core .70-.88, soft shoulders .60-.70/.88-.98.
 # Middle/light planes through depth .60 remain byte-exact.
 across=smooth(.60,.70,depth)*(1-smooth(.88,.98,depth))
 along=1-smooth(400,520,np.arange(w)[None,:])
 rgb=a[:,:,:3].astype(float)
 ink=(a[:,:,3]>0)&((rgb[:,:,0]<=210)|(rgb[:,:,1]<=135)|(rgb[:,:,2]<=100));ink=nd.binary_dilation(ink,iterations=2)
 contour=nd.binary_dilation(a[:,:,3]<128,iterations=3)&(a[:,:,3]>0)
 protected=ink|contour|(a[:,:,3]<240)
 edge=smooth(2,9,nd.distance_transform_edt((semantic>0)&~protected))
 field=across*along*edge;addition=np.zeros_like(rgb)
 for arm in [1,2]:
  # Smooth mother-relative deficits before creating bounded local doses.
  region=semantic==arm
  dg=nd.gaussian_filter(deficit[:,:,1]*region,sigma=(3,7))
  db=nd.gaussian_filter(deficit[:,:,2]*region,sigma=(3,7))
  if name=='F084':
   g=(1+2*smooth(3,8,dg))*smooth(.5,3,dg)
   b=2*smooth(2,8,db)
  elif arm==1:
   g=(4+smooth(5,10,dg))*smooth(1,4,dg)
   b=(6+2*smooth(7,12,db))*smooth(1,5,db)
  else:
   g=(2+3*smooth(3,8,dg))*smooth(1,3,dg)
   b=(3+5*smooth(4,10,db))*smooth(1,4,db)
  addition[:,:,1]+=g*field*region;addition[:,:,2]+=b*field*region
 delta=np.rint(addition).astype(np.int16);out=a.copy();out[:,:,:3]=np.clip(a[:,:,:3].astype(np.int16)+delta,0,255).astype(np.uint8)
 changed=np.any(out!=a,axis=2)
 assert np.array_equal(a[:,:,3],out[:,:,3]);assert np.array_equal(a[:,520:],out[:,520:]);assert np.array_equal(a[protected],out[protected])
 mid=(semantic>0)&(depth<=.60);assert np.array_equal(a[mid],out[mid]);assert not np.any(delta[:,:,0])
 assert delta[:,:,1].max()<=(3 if name=='F084' else 5);assert delta[:,:,2].max()<=(2 if name=='F084' else 8)
 dest=HERE/'candidate'/f'{name}_shadow_fixed.png';Image.fromarray(out).save(dest)
 for arm,label in [(1,'adult'),(2,'child')]:
  Image.fromarray(np.rint(field*(semantic==arm)*65535).astype(np.uint16)).save(HERE/'masks'/f'{name}_{label}_dark_field16.png')
 Image.fromarray(protected.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_protected.png')
 Image.fromarray(mid.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_middle_light_protected.png')
 Image.fromarray(changed.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_actual_changed.png')
 Image.fromarray(np.clip(delta*30,0,255).astype(np.uint8)).save(HERE/'masks'/f'{name}_actual_addition_RGB_x30.png')
 np.savez_compressed(HERE/'provenance'/f'{name}_shadow_fields.npz',profiles=p,semantic=semantic,depth=depth.astype(np.float32),mother_relative_RGB_deficit=deficit.astype(np.float32),soft_dark_field=field.astype(np.float32),signed_RGB_delta=delta)
 for kind,c in [('gray',(115,115,115)),('dark',(32,32,32))]:
  composite(out,c).save(HERE/'qa'/f'{name}_after_on_{kind}.png')
  board=Image.new('RGB',(1200,773),(25,25,25));d=ImageDraw.Draw(board)
  for i,(title,b) in enumerate([(name+' / frozen before',a),(name+' / shadow after',out)]):
   board.paste(composite(b,c).crop((0,200,600,941)),(600*i,32));d.text((600*i+8,5),title,font=font,fill='white')
  board.save(HERE/'qa'/f'{name}_before_after_{kind}_native.png')
 overlay=np.array(composite(a)).astype(float);z=field[:,:,None]*.5;color=np.zeros_like(rgb);color[semantic==1]=[255,140,40];color[semantic==2]=[30,210,255]
 overlay=overlay*(1-z)+color*z;Image.fromarray(np.rint(overlay).clip(0,255).astype(np.uint8)).save(HERE/'qa'/f'{name}_dark_field_overlay.png')
 images[name+'_before']=a;images[name+'_after']=out
 checks=dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),candidate_sha256=sha(dest),alpha_exact=True,alpha_sha256=pixel_sha(a[:,:,3]),contact_x_ge_520_exact=True,contact_RGBA_sha256=pixel_sha(a[:,520:]),ink_and_contour_guards_exact=True,middle_light_through_depth_060_exact=True,RGB_max_addition=delta.max(axis=(0,1)).tolist(),changed_pixels=int(changed.sum()),clip_normalization=clip,field='Core .70-.88; soft shoulders .60-.70/.88-.98; x0-400 main,400-520 smooth to zero; mother-relative adaptive local dose; ink/alpha guards.',new_image_calls=0)
 all_checks[name]=checks;print(name,json.dumps(checks))

# Homologous strips are QA resampling of the actual paintings, never character art.
names=['F024','F066','F084_before','F084_after','F090_before','F090_after']
board=Image.new('RGB',(1800,510),(25,25,25));d=ImageDraw.Draw(board);measure={}
for i,name in enumerate(names):
 a=images[name];p,_=profiles(a);measure[name]={}
 for arm,label in [(0,'adult'),(1,'child')]:
  strip=np.zeros((200,101,4),np.uint8)
  for j,x in enumerate(range(250,351)):
   t=np.linspace(0,1,200);top,bottom=p[x,arm*2:arm*2+2];ys=top+t*(bottom-top)
   for k in range(4):strip[:,j,k]=np.rint(np.interp(ys,np.arange(a.shape[0]),a[:,x,k])).clip(0,255).astype(np.uint8)
  tile=composite(strip).resize((260,200));y=35+arm*240;board.paste(tile,(i*300+30,y));d.text((i*300+8,y-25),name+' / '+label,font=font,fill='white')
  for f in [.50,.65,.80,.90]:
   liney=y+round(f*199);d.line((i*300+30,liney,i*300+289,liney),fill=(80,200,220));d.text((i*300+1,liney-8),str(int(f*100)),font=font,fill='white')
  for f in [.2,.5,.65,.7,.75,.8,.85,.9]:
   vals=[]
   for x in range(250,351):
    ls,n=nd.label(a[:,x,3]>=128);runs=[np.where(ls==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15]
    top,bottom=runs[arm][0],runs[arm][-1];yy=round(top+f*(bottom-top));vals.append(a[yy-2:yy+3,x,:3])
   measure[name].setdefault(str(f),{})[label]=np.median(np.concatenate(vals),axis=0).tolist()
board.save(HERE/'qa/homologous_forearm_024_066_084_090_before_after.png')
(HERE/'provenance/correction_checks.json').write_text(json.dumps(all_checks,indent=2)+'\n')
(HERE/'provenance/homologous_dark_samples.json').write_text(json.dumps(dict(method='Actual source columns250-350; five-pixel samples at homologous depth from unsmoothed real alpha bounds. These columns are fully visible. Profile smoothing and hidden-boundary extension apply only to the soft colour field/QA strip normalization, not the sample coordinates.',samples=measure),indent=2)+'\n')
print(json.dumps({k:v['0.8'] for k,v in measure.items()},indent=2))
