#!/usr/bin/env python3
"""Authorized same-raw semantic hair-base correction. No synthesis or geometry edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import hashlib, json
import numpy as np

P=Path(__file__).resolve().parents[1]
R=P.parent
ROOT=R.parents[2]
RAW=R/'d01_first_candidate/originals/S24_F000_call_001_raw.png'
MASTER=ROOT/'assets/chars/x13/F000.png'
RAW_SHA='35bb55ead65abf20e3862b4d66dde2f0ed25023f31fb634fa2f03bcda0c72281'
MASTER_SHA='91715601ae814bd84a3dc8d6ce43f1cc809a7bdd74e7390fefffe579f6882050'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(RAW.read_bytes())==RAW_SHA and sha(MASTER.read_bytes())==MASTER_SHA
for d in ['candidates','masks','qa']:(P/d).mkdir(exist_ok=True,parents=True)
a=np.array(Image.open(RAW).convert('RGBA')); master=np.array(Image.open(MASTER).convert('RGBA'))
assert a.shape==(1536,1024,4)
r,g,b,alpha=np.moveaxis(a.astype(np.int16),2,0)
brown=(alpha>=248)&(r>g+7)&(g>b+2)&(r>30)&(r<125)&(g<95)&(b<85)
brown[1030:]=False
labels,_=ndi.label(brown)
regions={
 'crown':{'seed':[500,300],'master_roi':[260,260,520,500],'raw_roi':[360,280,730,500],'relation':'whole crown; original same-ROI baseline'},
 'near_tail':{'seed':[800,900],'master_roi':[185,840,320,950],'raw_roi':[760,850,875,960],'relation':'master screen-left near tail -> S24 screen-right near tail'},
 'far_tail':{'seed':[300,940],'master_roi':[735,855,815,940],'raw_roi':[265,910,355,965],'relation':'master screen-right far tail -> S24 screen-left far tail'},
}
def stats(im,roi):
 x,y,X,Y=roi;cut=im[y:Y,x:X];rr,gg,bb,aa=np.moveaxis(cut.astype(np.int16),2,0)
 mask=(aa>=248)&(rr>gg+7)&(gg>bb+2)&(rr>35)&(rr<125)&(gg<95)&(bb<85)
 v=cut[:,:,:3][mask].astype(float);assert len(v)>100
 return {'roi':roi,'pixels':len(v),'mean_RGB':np.mean(v,axis=0).round(5).tolist(),'median_RGB':np.median(v,axis=0).tolist(),'p10_RGB':np.percentile(v,10,axis=0).tolist(),'p90_RGB':np.percentile(v,90,axis=0).tolist()}

domain=np.zeros(a.shape[:2],bool)
for name,v in regions.items():
 x,y=v['seed'];label=int(labels[y,x]);assert label>0
 m=labels==label;domain|=m
 v['component_label']=label;v['component_pixels']=int(m.sum())
 v['master']=stats(master,v['master_roi']);v['before']=stats(a,v['raw_roi'])
 v['subtract_RGB']=np.subtract(v['before']['median_RGB'],v['master']['median_RGB']).tolist()
 Image.fromarray((m*255).astype('uint8')).save(P/f'masks/{name}_semantic_component.png')

# Conservative protected sets. Closing finds narrow dark stroke valleys; a one-pixel
# dilation also protects their antialiasing. Bright/warm streaks are kept byte-exact.
dark_ridge=(ndi.grey_closing(r,size=(7,7))-r)>=4
line=((r<=48)|dark_ridge)&domain
line=ndi.binary_dilation(line,iterations=1)&domain
highlight=((r>=67)|((r>=62)&(r-g>=19)))&domain
protected=line|highlight
distance=ndi.distance_transform_edt(domain&~protected)
weight=np.minimum(1,distance/2)*np.clip((r-48)/10,0,1)*np.clip((68-r)/4,0,1)
weight[~domain|protected]=0
# Explicitly retain skin, eyes, ears, mouth, neck and the complete garment outside
# the three seeded connected brown-hair components. No threshold is applied globally.
out=a.copy()
for name,v in regions.items():
 m=labels==v['component_label'];w=weight*m
 shift=np.array(v['subtract_RGB'])
 out[:,:,:3]=np.where(m[:,:,None],np.rint(a[:,:,:3].astype(float)-w[:,:,None]*shift).clip(0,255),out[:,:,:3]).astype('uint8')

changed=np.any(a!=out,axis=2)
checks={'alpha_changed':int(np.count_nonzero(a[:,:,3]!=out[:,:,3])),
 'outside_three_semantic_components_changed':int(np.count_nonzero(changed&~domain)),
 'protected_line_changed':int(np.count_nonzero(changed&line)),
 'protected_highlight_changed':int(np.count_nonzero(changed&highlight)),
 'skin_neck_eyes_mouth_garment_outside_domain_changed':int(np.count_nonzero(changed&~domain)),
 'changed_pixels':int(changed.sum()),'RGB_min_delta':(out[:,:,:3].astype(int)-a[:,:,:3]).min(axis=(0,1)).tolist(),
 'RGB_max_delta':(out[:,:,:3].astype(int)-a[:,:,:3]).max(axis=(0,1)).tolist()}
assert all(checks[k]==0 for k in ['alpha_changed','outside_three_semantic_components_changed','protected_line_changed','protected_highlight_changed','skin_neck_eyes_mouth_garment_outside_domain_changed'])
for name,v in regions.items():
 v['after']=stats(out,v['raw_roi'])
 v['after_mean_delta_vs_master']=np.subtract(v['after']['mean_RGB'],v['master']['mean_RGB']).round(5).tolist()
 v['after_median_delta_vs_master']=np.subtract(v['after']['median_RGB'],v['master']['median_RGB']).tolist()
 assert max(abs(x)for x in v['after_mean_delta_vs_master'])<=4,(name,v)
 assert max(abs(x)for x in v['after_median_delta_vs_master'])<=4,(name,v)

candidate=P/'candidates/F000_hair_corrected_rgba.png'
Image.fromarray(out).save(candidate)
for name,m in [('hair_union',domain),('protected_line',line),('protected_highlight',highlight),('actual_changed',changed),('outside_hair_protected',~domain)]:
 Image.fromarray((m*255).astype('uint8')).save(P/f'masks/{name}.png')
Image.fromarray(np.rint(weight*255).astype('uint8')).save(P/'masks/correction_weight.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,color=(207,214,214,255)):
 bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);return bg.convert('RGB')
native=Image.fromarray(out)
sheet=Image.new('RGB',(1800,1030),'#f3f0e8');draw=ImageDraw.Draw(sheet)
for i,(im,title)in enumerate([(Image.fromarray(master),'固定F000色母'),(Image.fromarray(a),'S24同raw · 修前'),(native,'S24同raw · 仅棕发修后')]):
 im=comp(im);im.thumbnail((580,930));sheet.paste(im,(i*600+10,50));draw.text((i*600+12,12),title,font=font(25),fill='#25333d')
draw.text((15,985),'原生1024×1536；不搬脸、不改形、不动alpha/脸颈/服装；冠发与两尾分别对应取样。',font=font(23),fill='#25333d')
sheet.save(P/'qa/00_master_before_after.jpg',quality=97)
sheet=Image.new('RGB',(1800,1050),'#f3f0e8');draw=ImageDraw.Draw(sheet)
for row,(name,v)in enumerate(regions.items()):
 for col,(im,key)in enumerate([(Image.fromarray(master),'master_roi'),(Image.fromarray(a),'raw_roi'),(native,'raw_roi')]):
  crop=comp(im).crop(v[key]);crop=crop.resize((520,230));x=col*600+10;y=row*340+48;sheet.paste(crop,(x,y));draw.text((x,y-35),name+' '+['固定母色','修前','修后'][col],font=font(24),fill='#25333d')
 draw.text((12,row*340+292),'Δ中位RGB '+str(v['subtract_RGB'])+' → '+str(v['after_median_delta_vs_master']),font=font(24),fill='#25333d')
sheet.save(P/'qa/01_three_hair_regions_before_after.jpg',quality=97)
overlay=comp(Image.fromarray(a));ov=np.array(overlay);ov[changed]=(ov[changed]*.35+np.array([70,210,200])*.65).astype('uint8');ov[line]=[110,80,205];ov[highlight]=[245,150,60]
Image.fromarray(ov).save(P/'qa/02_changed_teal_line_purple_highlight_orange.png')
sheet=Image.new('RGB',(1536,818),'#f3f0e8');draw=ImageDraw.Draw(sheet)
for i,color in enumerate([(245,245,245,255),(33,39,48,255),(112,140,126,255)]):
 im=comp(native,color);im.thumbnail((500,750));sheet.paste(im,(i*512+5,45));draw.text((i*512+10,10),['浅底','深底','彩底'][i],font=font(25),fill='#25333d')
sheet.save(P/'qa/03_corrected_three_backgrounds.jpg',quality=97)
scale=.70;tx,ty=590,20
placed=native.transform((1920,1080),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC)
comp(placed).save(P/'qa/04_B_registration_neutral_NOT_SCENE.jpg',quality=97)
opaque_bbox=Image.fromarray(a[:,:,3]).point(lambda p:255 if p>=248 else 0).getbbox()
margin=ty+scale*opaque_bbox[1]
registration={'status':'B_whole_layer_registration_accepted_by_Astra;corrected_mother_color_pending_lock','scene_canvas':[1920,1080],'native_canvas':[1024,1536],'scale':scale,'translation':[tx,ty],'opaque_alpha_threshold':248,'opaque_native_bbox':list(opaque_bbox),'opaque_top_margin_scene_px':round(margin,2),'caveat':'About14% larger than old construction head. Preserve framing in later turn/chin lift. Neutral diagnostic, not actual Canvas scene. Alpha including original faint halo remains unchanged.'}
(P/'registration_B.json').write_text(json.dumps(registration,ensure_ascii=False,indent=2)+'\n')
result={'status':'LOCAL_HAIR_CORRECTION_READY_FOR_ASTRA_MOTHER_LOCK','raw_path':str(RAW.relative_to(ROOT)),'raw_sha256':RAW_SHA,'fixed_color_master':str(MASTER.relative_to(ROOT)),'fixed_color_master_sha256':MASTER_SHA,'candidate':'candidates/F000_hair_corrected_rgba.png','candidate_sha256':sha(candidate.read_bytes()),'candidate_RGBA_sha256':sha(out.tobytes()),'native_size':[1024,1536],'method':'Three separately seeded connected opaque brown-hair components; per-region median RGB subtraction with protected stroke/highlight sets and distance/shadow feather. No spatial warp, no synthesis, no global grading.','regions':regions,'checks':checks,'image_generation_calls_this_fix':0,'total_S24_image_generation_calls':1,'F006_F009_F012_started':False,'remaining_gate':'Astra lock exact corrected mother SHA before deriving later states.'}
(P/'correction_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sha256':result['candidate_sha256'],'checks':checks,'regions':{n:{'subtract':v['subtract_RGB'],'after_mean_delta':v['after_mean_delta_vs_master'],'after_median_delta':v['after_median_delta_vs_master']}for n,v in regions.items()},'B_top_margin':round(margin,2)},ensure_ascii=False,indent=2))
