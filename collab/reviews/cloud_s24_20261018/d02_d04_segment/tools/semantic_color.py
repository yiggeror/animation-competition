#!/usr/bin/env python3
"""Per-state local material correction of actual native outputs; no geometry synthesis."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import sys,json,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1]
cfg=json.loads(Path(sys.argv[1]).read_text());f=cfg['frame'];tag=f'F{f:03}'
raw=P/cfg['raw'];master=P/cfg['master'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(master)==cfg['master_sha256']
a=np.array(Image.open(raw).convert('RGBA'));m=np.array(Image.open(master).convert('RGBA'));assert a.shape==m.shape==(1536,1024,4)
r,g,b,al=np.moveaxis(a.astype(np.int16),2,0)
def material_mask(im,kind):
 rr,gg,bb,aa=np.moveaxis(im.astype(np.int16),2,0);opaque=aa>=248
 if kind=='hair':return opaque&(rr>35)&(rr<125)&(rr>gg+7)&(gg>bb+2)&(gg<95)&(bb<85)
 if kind=='skin':return opaque&(rr>150)&(gg>90)&(bb>65)&(rr>gg+10)&(gg>bb+10)&(gg-bb<70)&(rr-gg<100)
 return opaque&(rr>180)&(gg>120)&(bb<130)&(rr>gg+10)&(gg>bb+60)
def stats(im,roi,kind):
 x,y,X,Y=roi;crop=im[y:Y,x:X];vals=crop[:,:,:3][material_mask(crop,kind)].astype(float);assert len(vals)>100
 return {'roi':roi,'pixels':len(vals),'median_RGB':np.median(vals,axis=0).tolist(),'mean_RGB':vals.mean(0).round(5).tolist()}
brown=(al>=248)&(r>30)&(r<125)&(r>g+7)&(g>b+2)&(g<95)&(b<85);brown[1060:]=False
labels,_=ndi.label(brown);out=a.copy();union=np.zeros(a.shape[:2],bool);protected=np.zeros_like(union);rows=[]
for name,c in cfg['regions'].items():
 kind=c['type'];before=stats(a,c['roi'],kind);ref=stats(m,c['master_roi'],kind);delta=np.subtract(before['median_RGB'],ref['median_RGB'])
 if kind=='hair':
  x,y=c['seed'];n=labels[y,x];assert n>0,(tag,name,c['seed']);domain=labels==n
  ridge=(ndi.grey_closing(r,size=(7,7))-r)>=4
  floor=c.get('line_floor',48);high=c.get('highlight_floor',67)
  line=ndi.binary_dilation(((r<=floor)|ridge)&domain,iterations=1)&domain
  highlight=((r>=high)|((r>=c.get('highlight_warm_red_floor',62))&(r-g>=c.get('highlight_chroma_delta',19))))&domain;lock=line|highlight
  weight=np.minimum(1,ndi.distance_transform_edt(domain&~lock)/2)*np.clip((r-floor)/10,0,1)*np.clip((high+1-r)/4,0,1)
 else:
  domain=material_mask(a,kind)
  if kind=='skin':domain[:540]=False
  else:domain[:990]=False
  lock=np.zeros_like(domain);weight=np.minimum(1,ndi.distance_transform_edt(domain)/2)
 weight[~domain|lock]=0
 out[:,:,:3]=np.where(domain[:,:,None],np.rint(a[:,:,:3].astype(float)-weight[:,:,None]*delta).clip(0,255),out[:,:,:3]).astype('uint8')
 union|=domain;protected|=lock
 (P/f'qa/{tag}_masks').mkdir(exist_ok=True)
 Image.fromarray((domain*255).astype('uint8')).save(P/f'qa/{tag}_masks/{name}_semantic.png')
 Image.fromarray(np.rint(weight*255).astype('uint8')).save(P/f'qa/{tag}_masks/{name}_weight.png')
 rows.append({'region':name,'type':kind,'before':before,'master':ref,'subtract_RGB':delta.tolist()})
changed=np.any(a!=out,axis=2)
assert np.array_equal(a[:,:,3],out[:,:,3]) and not np.any(changed&~union) and not np.any(changed&protected)
for row in rows:
 c=cfg['regions'][row['region']];row['after']=stats(out,c['roi'],row['type']);row['mean_delta_vs_master']=np.subtract(row['after']['mean_RGB'],row['master']['mean_RGB']).round(5).tolist();row['median_delta_vs_master']=np.subtract(row['after']['median_RGB'],row['master']['median_RGB']).tolist()
 assert max(abs(x)for x in row['mean_delta_vs_master'])<=4,(tag,row)
 assert max(abs(x)for x in row['median_delta_vs_master'])<=4,(tag,row)
candidate=P/f'candidates/{tag}_rgba.png';Image.fromarray(out).save(candidate)
for name,mask in [('material_union',union),('hair_line_highlight_protected',protected),('actual_changed',changed)]:Image.fromarray((mask*255).astype('uint8')).save(P/f'qa/{tag}_masks/{name}.png')
def comp(im,col=(209,215,215,255)):
 bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);return bg.convert('RGB')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
sheet=Image.new('RGB',(1800,1030),'#f3f0e8');d=ImageDraw.Draw(sheet)
for i,(im,title)in enumerate([(Image.fromarray(m),'锁定新修母'),(Image.fromarray(a),tag+'原生raw'),(Image.fromarray(out),tag+'区域色门后')]):
 im=comp(im);im.thumbnail((580,930));sheet.paste(im,(i*600+10,50));d.text((i*600+12,12),title,font=font(25),fill='#25333d')
sheet.save(P/f'qa/{tag}_master_raw_candidate.jpg',quality=97)
native=Image.fromarray(out);placed=native.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);comp(placed).save(P/f'qa/{tag}_B_neutral_NOT_SCENE.jpg',quality=97)
result={'frame':f,'raw':cfg['raw'],'raw_sha256':sha(raw),'candidate':str(candidate.relative_to(P)),'candidate_sha256':sha(candidate),'candidate_RGBA_sha256':hashlib.sha256(out.tobytes()).hexdigest(),'locked_corrected_mother_sha256':cfg['master_sha256'],'native_canvas':[1024,1536],'method':'Each actual native state gets separate explicit hair/skin/dress material domains; same approved mother for every color target. Local channel offsets preserve gradients. Hair deep/ridge lines and highlights, alpha and outside domains exact. No warp/reposition/anatomy code.','regions':rows,'changed_pixels':int(changed.sum()),'alpha_changes':0,'protected_hair_line_highlight_changes':0,'outside_material_changes':0,'geometry_changes_from_this_color_step':0,'image_generation_calls_this_color_step':0,'status':'COLOR_GATE_PASS;ACTUAL_STRUCTURE_GAZE_AND_FRAMING_REVIEW_REQUIRED'}
(P/f'qa/{tag}_color_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frame':f,'candidate_sha256':sha(candidate),'region_mean_deltas':{row['region']:row['mean_delta_vs_master']for row in rows},'alpha_line_highlight_outside_changes':0},ensure_ascii=False,indent=2))
