from PIL import Image,ImageDraw,ImageFilter,ImageChops
from pathlib import Path
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent
S=R.parents[1]/'astra_s03b_painted_pilot_20261018/refs/painted'
(R/'candidates').mkdir(exist_ok=True);(R/'masks').mkdir(exist_ok=True)
def native(p):
 im=Image.open(p).convert('RGBA'); c=Image.new('RGBA',(1672,941));c.paste(im,(0,0));return c
def poly_mask(points,blur=0):
 m=Image.new('L',(1672,941));ImageDraw.Draw(m).polygon(points,fill=255);return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m
# F009 local generated iris/white region. Only local uniform sampling from 1254-square raw to source 512-square crop; no global registration.
base=native(S/'S03_grandma_k01_F005_t0.20.png');raw=Image.open(R/'originals/S03_F009_localeyes_call04.png').convert('RGBA');head=raw.resize((512,512),Image.Resampling.LANCZOS);gen=Image.new('RGBA',base.size);gen.paste(head,(620,80));out=base.copy();allmask=Image.new('L',base.size)
# Eye interiors only. Generated irises are isolated with explicit ellipse masks then relocated; generated sclera pixels fill old iris positions without moving the source eyelids.
ops=[('eye_left',[(781,297),(789,291),(802,289),(815,294),(823,302),(820,309),(812,314),(799,314),(789,310),(783,304)],(7,3)),('eye_right',[(892,309),(901,303),(914,302),(927,305),(937,313),(931,320),(919,325),(906,327),(897,324),(892,318)],(2,1))]
iris_bounds=[(779,290,806,315),(891,303,917,328)]
for (name,points,(dx,dy)),bounds in zip(ops,iris_bounds):
 mask=poly_mask(points,0)
 oldiris=Image.new('L',base.size);ImageDraw.Draw(oldiris).ellipse((793,293,823,317) if name=='eye_left' else (896,305,926,329),fill=255);mask=ImageChops.lighter(mask,oldiris).filter(ImageFilter.GaussianBlur(.4))
 # Real generated sclera sampling from clear white to the right of the generated left iris.
 whites=gen.crop((810,295,820,309)).resize((70,40),Image.Resampling.BICUBIC)
 donor=out.copy(); x0,y0,x1,y1=(min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points));donor.paste(whites,(x0,y0))
 ir=gen.crop(bounds);scale=8;im=Image.new('L',(ir.width*scale,ir.height*scale));ImageDraw.Draw(im).ellipse((0,0,ir.width*scale-1,ir.height*scale-1),fill=255);im=im.resize(ir.size,Image.Resampling.LANCZOS)
 donor.paste(ir,(bounds[0]+dx,bounds[1]+dy),im)
 out=Image.composite(donor,out,mask);allmask=ImageChops.lighter(allmask,mask);mask.save(R/f'masks/F009_{name}.png')
# Preserve the actual generated pinching hand from call02; feather on interior forearm/shirt only and preserve the hand-pod contact.
pinchmask=poly_mask([(640,700),(667,678),(695,650),(729,638),(770,646),(805,670),(830,695),(831,723),(810,743),(788,766),(746,775),(705,774),(678,759),(641,743)],1.2)
hand=native(R/'originals/S03_F009_call02.png');out=Image.composite(hand,out,pinchmask);allmask=ImageChops.lighter(allmask,pinchmask);pinchmask.save(R/'masks/F009_pinch.png');allmask.save(R/'masks/F009_all_changes.png');out.save(R/'candidates/S03_F009_local_composite_v1.png')
# F017 whole new head perspective, original body except explicit head/neck mask.
base17=native(S/'S03_grandma_k02_F013_t0.55.png');g17=Image.open(R/'originals/S03_F017_localhead_call05.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);donor17=base17.copy();donor17.paste(g17,(600,0))
mask17=poly_mask([(620,0),(1080,0),(1080,378),(989,389),(940,397),(922,424),(897,469),(861,512),(840,491),(811,460),(782,423),(743,394),(680,381),(620,378)],1.0)
out17=Image.composite(donor17,base17,mask17);out17.save(R/'candidates/S03_F017_local_composite_v1.png');mask17.save(R/'masks/F017_head_neck.png')
checks=[]
for f,b,o,m in [(9,base,out,allmask),(17,base17,out17,mask17)]:
 a=np.array(b);c=np.array(o);mm=np.array(m);changed=np.any(a!=c,axis=2);checks.append({'frame':f,'size':o.size,'outside_mask_changed_pixels':int(np.sum(changed & (mm==0))),'total_changed_pixels':int(changed.sum()),'mask_bbox':m.getbbox()})
(R/'pixel_lock_checks.json').write_text(json.dumps(checks,indent=2))
meta={'method':'Explicit authorized local-mask composition; all raw imagegen outputs retained; local crop output normalized uniformly to source crop dimensions only; no full-character registration, warp, or old-face translation to simulate head turn.','F009':{'base':'k01','eyes_raw':'S03_F009_localeyes_call04.png','local_crop':[620,80,1132,592],'raw_size':raw.size,'mapped_size':[512,512],'generated_eye_field_translations':{'left':[7,3],'right':[2,1]},'pinch_raw':'S03_F009_call02.png','masks':[x[0] for x in ops]+['pinch']},'F017':{'base':'k02','head_raw':'S03_F017_localhead_call05.png','local_crop':[600,0,1112,512],'mask':'masks/F017_head_neck.png'},'checks':checks}
(R/'local_composition_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(json.dumps(checks,indent=2))
