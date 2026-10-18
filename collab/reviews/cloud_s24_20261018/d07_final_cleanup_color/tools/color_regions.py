#!/usr/bin/env python3
"""Fixed-mother local material colour, preserving alpha/anatomy/features, no image generation."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
import numpy as np,json,hashlib
H=Path(__file__).resolve().parents[1];P=H.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'candidates/F024_cleanup_before_color.png';master=P/'d01_hair_color_fix/candidates/F000_hair_corrected_rgba.png';assert sha(master)=='0485c6fe2ee6ec05d762a6b1c531ed9764e7e77223b6cce455b54f50f99eff22'
a=np.array(Image.open(source).convert('RGBA'));m=np.array(Image.open(master).convert('RGBA'));out=a.copy();yy,xx=np.indices(a.shape[:2]);r,g,b,al=np.moveaxis(a.astype('int16'),2,0)
def poly(pts):
 q=Image.new('L',(1024,1536));ImageDraw.Draw(q).polygon(pts,fill=255);return np.array(q)>0
def oval(x,y,rx,ry):return ((xx-x)/rx)**2+((yy-y)/ry)**2<=1
def rect(box):
 x,y,X,Y=box;return (xx>=x)&(xx<X)&(yy>=y)&(yy<Y)
def arrstat(im,mask):
 v=im[:,:,:3][mask].astype(float);assert len(v)>100,len(v)
 return {'pixels':len(v),'median_RGB':np.median(v,0).round(5).tolist(),'mean_RGB':v.mean(0).round(5).tolist()}
def sample_roi(im,roi,kind):
 rr,gg,bb,aa=np.moveaxis(im.astype('int16'),2,0)
 if kind=='hair':mat=(aa>=248)&(rr>35)&(rr<125)&(rr>gg+7)&(gg>bb+2)&(gg<95)&(bb<85)
 else:raise ValueError(kind)
 return rect(roi)&mat
garment_guard=np.array(Image.open(P/'d07_F024_zero_call_repair/masks/protected_whole_collar_with_stroke_AA.png'))>0
# Three independent brown hair components, with their own reference ROIs and line/highlight guards.
brown=(al>=248)&(r>30)&(r<125)&(r>g+7)&(g>b+2)&(g<95)&(b<85)&(yy<1060);labels,_=ndi.label(brown)
hair_specs={
 'crown':{'seed':[450,300],'roi':[330,280,610,450],'master_roi':[360,280,730,500],'line_floor':48,'highlight_floor':70},
 'near_tail':{'seed':[200,910],'roi':[175,870,280,970],'master_roi':[760,850,875,960],'line_floor':46,'highlight_floor':68},
 'far_tail':{'seed':[820,910],'roi':[780,865,860,940],'master_roi':[265,910,355,965],'line_floor':46,'highlight_floor':68},
}
material_union=np.zeros_like(brown);hairlock=np.zeros_like(brown);hair_domains={};rows=[]
for name,c in hair_specs.items():
 x,y=c['seed'];idx=labels[y,x];assert idx>0;domain=labels==idx;hair_domains[name]=domain
 ridge=(ndi.grey_closing(r,size=(7,7))-r)>=4
 line=ndi.binary_dilation(((r<=c['line_floor'])|ridge)&domain,iterations=1)&domain
 highlight=((r>=c['highlight_floor'])|((r>=64)&(r-g>=23)))&domain;lock=line|highlight|(garment_guard&domain)
 weight=np.minimum(1,ndi.distance_transform_edt(domain&~lock)/2)*np.clip((r-c['line_floor'])/10,0,1)*np.clip((c['highlight_floor']+1-r)/4,0,1)
 weight[~domain|lock]=0;sample=sample_roi(a,c['roi'],'hair');msample=sample_roi(m,c['master_roi'],'hair');before=arrstat(a,sample);ref=arrstat(m,msample);delta=np.subtract(before['median_RGB'],ref['median_RGB']).astype(float)
 # Smallest component-wise offset satisfying both mean/median±4 under fixed interior samples.
 for _ in range(20):
  proposed=np.rint(a[:,:,:3].astype(float)-weight[:,:,None]*delta).clip(0,255).astype('uint8');test=np.dstack((proposed,a[:,:,3]));st=arrstat(test,sample);dm=np.subtract(st['mean_RGB'],ref['mean_RGB']);dd=np.subtract(st['median_RGB'],ref['median_RGB'])
  if max(abs(dm).max(),abs(dd).max())<=3.9:break
  for ch in range(3):
   if dm[ch]>3.9 or dd[ch]>3.9:delta[ch]+=.5
   elif dm[ch]<-3.9 or dd[ch]<-3.9:delta[ch]-=.5
 else:raise AssertionError((name,delta,dm,dd))
 out[:,:,:3][domain]=proposed[domain];material_union|=domain;hairlock|=lock
 for label,mat in [('domain',domain),('line_highlight_protected',lock),('weight',weight),('sample',sample)]:Image.fromarray(np.rint(np.clip(mat,0,1)*255).astype('uint8')).save(H/f'masks/{name}_{label}.png')
 Image.fromarray((msample*255).astype('uint8')).save(H/f'masks/master_{name}_sample.png')
 rows.append({'region':name,'before':before,'master':ref,'subtract_RGB':delta.tolist(),'after':st,'mean_delta':dm.round(5).tolist(),'median_delta':dd.round(5).tolist(),'line_floor':c['line_floor'],'highlight_floor':c['highlight_floor']})
all_hair=np.logical_or.reduce(list(hair_domains.values()))
# Actual facial feature pixels, not rectangular blocks of adjacent skin. Hair domain is excluded.
features=np.zeros_like(brown)
for box in [(550,555,685,710),(772,530,860,662),(538,489,674,550),(763,462,854,514),(766,660,813,712),(714,725,803,774),(355,695,451,782)]:
 actual=rect(box)&(((r<180)|(g<110)|(b<85))|((r>220)&(g>220)&(b>205)))&~all_hair
 features|=ndi.binary_dilation(actual,iterations=1)&~all_hair
blush=oval(606,747,62,35)|oval(850,690,23,29)
protected_features=features|blush|garment_guard
# Matching current/master face, ear, neck areas, each split into lit and shadow core samples.
def skin_parts(im,is_master=False):
 rr,gg,bb,aa=np.moveaxis(im.astype('int16'),2,0)
 sk=(aa>=248)&(rr>180)&(gg>110)&(bb>85)&(rr>gg+15)&(gg>bb+10)&(rr-gg<100)&(gg-bb<80)&(yy<1100)
 lab,_=ndi.label(sk);sk=lab==lab[1000,600]
 if not is_master:
  f=poly([(450,310),(880,310),(900,780),(850,825),(781,857),(690,866),(620,859),(553,840),(476,808),(450,740)])
  e=poly([(335,660),(473,660),(475,815),(335,825)])
 else:
  f=poly([(165,370),(576,370),(596,789),(557,846),(504,879),(451,906),(351,918),(273,886),(219,846),(200,778)])
  e=poly([(585,625),(715,625),(715,808),(585,808)])
 e&=sk;f&=sk&~e;n=sk&~f&~e
 return {'face':f,'ear':e,'neck':n}
parts=skin_parts(a);mparts=skin_parts(m,True);mr,mg,mb,mal=np.moveaxis(m.astype('int16'),2,0)
mblush=oval(430,796,63,30)|oval(240,774,23,30)
# Blush stays byte-exact, with a soft colour-only surround. Alpha/shape never changes here.
feature_weight=np.minimum(1,ndi.distance_transform_edt(~features)/3)*np.minimum(1,ndi.distance_transform_edt(~blush)/10)*np.minimum(1,ndi.distance_transform_edt(~garment_guard)/3)
lit_mix=np.clip((g-196)/10,0,1);lit_mix=lit_mix*lit_mix*(3-2*lit_mix)
skin_correction=np.zeros((*g.shape,3),float)
for name,domain in parts.items():
 # Natural black outlines/AA are outside or at the edge of the skin material domain.
 edge_weight=np.minimum(1,ndi.distance_transform_edt(domain)/3)*feature_weight
 deltas={};samps={};refs={}
 for mode in ['lit','shadow']:
  sample=domain&~protected_features&(edge_weight>.95)&(r>=235)&((g>=206)if mode=='lit'else(g<=196))
  # Symmetric eroded pigment core excludes line/AA mixtures on both images.
  msample=mparts[name]&(ndi.distance_transform_edt(mparts[name])>=3)&~mblush&(mr>=235)&((mg>=201)if mode=='lit'else(mg<=191))
  before=arrstat(a,sample);ref=arrstat(m,msample);delta=np.subtract(before['median_RGB'],ref['median_RGB']).astype(float)
  Image.fromarray((msample*255).astype('uint8')).save(H/f'masks/master_skin_{name}_{mode}_sample.png')
  deltas[mode]=delta;samps[mode]=(sample,before);refs[mode]=ref
  Image.fromarray((sample*255).astype('uint8')).save(H/f'masks/skin_{name}_{mode}_core_sample.png')
 correction=(lit_mix[:,:,None]*deltas['lit']+(1-lit_mix[:,:,None])*deltas['shadow'])*edge_weight[:,:,None]
 skin_correction[domain]=correction[domain];material_union|=domain
 Image.fromarray((domain*255).astype('uint8')).save(H/f'masks/skin_{name}_domain.png');Image.fromarray(np.rint(edge_weight*255).astype('uint8')).save(H/f'masks/skin_{name}_weight.png')
 for mode in ['lit','shadow']:
  sample,before=samps[mode];rows.append({'region':'skin_'+name+'_'+mode,'before':before,'master':refs[mode],'subtract_RGB':deltas[mode].tolist(),'sample_mask':f'masks/skin_{name}_{mode}_core_sample.png','lighting_assignment':'frozen from pre-correction RGB; not reclassified after colour change'})
skin_union=np.logical_or.reduce(list(parts.values()));rgb=np.rint(a[:,:,:3].astype(float)-skin_correction).clip(0,255).astype('uint8');out[:,:,:3][skin_union]=rgb[skin_union]
for row in rows:
 if not row['region'].startswith('skin_'):continue
 mask=np.array(Image.open(H/row['sample_mask']))>0;after=arrstat(out,mask);dm=np.subtract(after['mean_RGB'],row['master']['mean_RGB']);dd=np.subtract(after['median_RGB'],row['master']['median_RGB']);row.update({'after':after,'mean_delta':dm.round(5).tolist(),'median_delta':dd.round(5).tolist()})
 assert max(abs(dm).max(),abs(dd).max())<=4,(row['region'],dm,dd)
changed=np.any(out!=a,2);assert not np.any(changed&~material_union);assert not np.any(changed&hairlock);assert not np.any(changed&protected_features);assert np.array_equal(out[:,:,3],a[:,:,3]);assert np.array_equal(out[1100:],a[1100:])
# Entire yellow/white garment is unchanged, including its collar and antialias outline by protected source identity.
# The independent frozen collar matte guards warm edge pixels. Neck highlight colours must not be mistaken for white cloth.
yellow_geom=(yy>=1080)|((yy>=950)&((xx<410)|(xx>760)))
clothing=garment_guard|(yellow_geom&(r>170)&(g>110)&(b<135)&(g>b+55))|((yy>=1100)&(r>215)&(g>215)&(b>195))
assert not np.any(changed&clothing)
for name,mask in [('color_actual_changes',changed),('all_color_domains',material_union),('protected_hair_lines_highlights',hairlock),('protected_features_blush_and_frozen_collar',protected_features),('protected_clothing_yellow_white',clothing)]:Image.fromarray((mask*255).astype('uint8')).save(H/f'masks/{name}.png')
Image.fromarray(out).save(H/'candidates/F024_final_rgba.png')
for name,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 bg=Image.new('RGBA',(1024,1536),(*col,255));bg.alpha_composite(Image.fromarray(out));bg.convert('RGB').save(H/f'qa/F024_final_{name}_full.jpg',quality=98)
 bg.convert('RGB').crop((330,455,890,1090)).save(H/f'qa/F024_final_{name}_face_ear_neck.jpg',quality=98)
 bg.convert('RGB').crop((775,1405,970,1480)).resize((1560,600)).save(H/f'qa/F024_final_{name}_cuff8x.jpg',quality=98)
report={'source_cleanup_sha256':sha(source),'locked_mother_sha256':sha(master),'final_sha256':sha(H/'candidates/F024_final_rgba.png'),'skin_sample_definition':{'both_images':'alpha>=248,pigment_R>=235,own_domain_interior>=3px,blush excluded;source feature/collar guards excluded','current_lit_G_min':206,'current_shadow_G_max':196,'master_lit_G_min':201,'master_shadow_G_max':191,'assignment':'frozen before correction; lit/shadow is not recomputed from corrected output'},'method':'3 independent hair components + face/ear/neck each lit/shadow; local channel offsets on fixed semantic domains; gradients retained; no whole-image mean mapping','regions':rows,'alpha_changes_color_step':int(np.count_nonzero(out[:,:,3]!=a[:,:,3])),'outside_color_domains_changes':int((changed&~material_union).sum()),'hair_line_highlight_changes':int((changed&hairlock).sum()),'facial_feature_blush_changes':int((changed&(features|blush)).sum()),'frozen_collar_RGBA_changes':int((changed&garment_guard).sum()),'clothing_yellow_white_changes':int((changed&clothing).sum()),'lower_body_y1100_on_changes':int(changed[1100:].sum()),'color_changed_pixels':int(changed.sum()),'image_calls':0,'status':'LOCAL_COLOR_GATES_PASS;ACTUAL_VISUAL_REVIEW_REQUIRED'}
(H/'qa/color_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'final_sha256':report['final_sha256'],'region_deltas':{r['region']:r['mean_delta']for r in rows},'alpha_features_lines_clothing_outside_changes':0},ensure_ascii=False,indent=2))
