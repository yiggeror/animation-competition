#!/usr/bin/env python3
"""Small same-drawing material correction, referenced to024 rather than the chain."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
name=sys.argv[1];p=HERE/name
policy=json.loads((HERE/'provenance/colour_policy.json').read_text())[name]
src=p/'candidate'/f'{name}_mapped.png';a=np.array(Image.open(src).convert('RGBA'));h,w=a.shape[:2]
semantic=np.zeros((h,w),np.uint8)
for x in range(520):
 labels,n=nd.label(a[:,x,3]>=128);runs=[np.where(labels==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15];assert len(runs)==2
 for i,r in enumerate(runs):semantic[r[0]:r[-1]+1,x]=i+1
def smooth(lo,hi,z):
 t=np.clip((z-lo)/(hi-lo),0,1);return t*t*(3-2*t)
rgb=a[:,:,:3].astype(float);light=rgb@np.array([.2126,.7152,.0722])
tone=smooth(198,212,light)*(1-.35*smooth(238,250,light))
ink=(a[:,:,3]>0)&((rgb[:,:,0]<=210)|(rgb[:,:,1]<=135)|(rgb[:,:,2]<=100));ink=nd.binary_dilation(ink,iterations=2)
contour=nd.binary_dilation(a[:,:,3]<128,iterations=3)&(a[:,:,3]>0)
protected=ink|contour|(a[:,:,3]<240)
edge=smooth(2,9,nd.distance_transform_edt((semantic>0)&~protected))
along=1-smooth(400,520,np.arange(w)[None,:]);dose=np.zeros_like(rgb);weights={}
for key,strength in policy['doses'].items():
 arm,channel=key.split('_');region={'adult':1,'child':2}[arm];k='RGB'.index(channel)
 weight=(semantic==region)*tone*edge*along;weights[key]=weight
 dose[:,:,k]+=float(strength)*weight
delta=-np.rint(dose).astype(np.int16);out=a.copy();out[:,:,:3]=np.clip(a[:,:,:3].astype(np.int16)+delta,0,255).astype(np.uint8)
assert np.array_equal(out[:,:,3],a[:,:,3]);assert np.array_equal(out[:,520:],a[:,520:]);assert np.array_equal(out[protected],a[protected])
assert not np.any(delta[:,:,0]);changed=np.any(out!=a,axis=2)
(p/'masks').mkdir(exist_ok=True)
for key,weight in weights.items():Image.fromarray(np.rint(weight*65535).astype(np.uint16)).save(p/'masks'/f'{key}_colour_weight16.png')
Image.fromarray(protected.astype(np.uint8)*255).save(p/'masks/colour_protected.png');Image.fromarray(changed.astype(np.uint8)*255).save(p/'masks/colour_actual_changed.png')
Image.fromarray(np.clip(-delta*60,0,255).astype(np.uint8)).save(p/'masks/colour_actual_subtraction_RGB_x60.png')
Image.fromarray(np.clip(delta*50,0,255).astype(np.uint8)).save(p/'masks/colour_actual_addition_RGB_x50.png')
Image.fromarray(np.clip(128+delta*24,0,255).astype(np.uint8)).save(p/'masks/colour_actual_signed_RGB_bias128_x24.png')
np.savez_compressed(p/'provenance/colour_masks.npz',semantic=semantic,tone=tone.astype(np.float32),edge=edge.astype(np.float32),along=along.astype(np.float32),signed_RGB_delta=delta,**{k:v.astype(np.float32) for k,v in weights.items()})
dest=p/'candidate'/f'{name}_final.png';Image.fromarray(out).save(dest)
def composite(b,c=(115,115,115)):
 im=Image.new('RGBA',(w,h),(*c,255));im.alpha_composite(Image.fromarray(b));return im.convert('RGB')
for kind,c in [('gray',(115,115,115)),('white',(255,255,255)),('black',(0,0,0))]:composite(out,c).save(p/'qa'/f'{name}_final_on_{kind}.png')
composite(out).crop((470,300,1050,755)).resize((1160,910)).save(p/'qa'/f'{name}_final_contact_2x.png')
reference=np.array(Image.open(ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png').convert('RGBA'))
board=Image.new('RGB',(1800,773),(25,25,25));d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
for i,(label,im) in enumerate([('Locked024 / colour source',composite(reference)),(name+' / mapped before',composite(a)),(name+' / final',composite(out))]):
 board.paste(im.crop((0,200,600,941)),(i*600,32));d.text((i*600+8,5),label,font=font,fill='white')
board.save(p/'qa'/f'{name}_024_before_after_native.png')
def samples(b):
 result={}
 for fraction in [.2,.5,.8]:
  values=[[],[]]
  for x in range(250,351):
   ls,n=nd.label(b[:,x,3]>=128);runs=[np.where(ls==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>20]
   for i,r in enumerate([runs[0],runs[-1]]):
    y=round(r[0]+fraction*(r[-1]-r[0]));values[i].append(b[y-2:y+3,x,:3])
  result[str(fraction)]={k:np.median(np.concatenate(values[i]),axis=0).tolist() for i,k in enumerate(['adult','child'])}
 return result
sha=lambda z:hashlib.sha256(z).hexdigest()
record=dict(source_sha256=sha(src.read_bytes()),final_sha256=sha(dest.read_bytes()),policy=policy,alpha_exact=True,ink_and_contour_guards_exact=True,contact_x_ge_520_exact=True,source_contact_RGBA_sha256=sha(a[:,520:].tobytes()),final_contact_RGBA_sha256=sha(out[:,520:].tobytes()),changed_pixels=int(changed.sum()),RGB_min_delta=delta.min(axis=(0,1)).tolist(),RGB_max_delta=delta.max(axis=(0,1)).tolist(),samples=dict(F024=samples(reference),before=samples(a),after=samples(out)),additional_image_calls=0)
(p/'provenance/colour_checks.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
