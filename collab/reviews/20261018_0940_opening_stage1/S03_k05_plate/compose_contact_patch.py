from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
r=Path(__file__).resolve().parent
base=Image.open(r/'S03_k05_fixed_plate_candidate_v3.png').convert('RGBA'); donor=Image.open(r/'call01_contact_repair_original.png').convert('RGBA')
s=donor.width/300
# Uniform inverse mapping; no stretching or registration of the source character.
d=donor.transform((300,166),Image.Transform.AFFINE,(s,0,0,0,s,0),Image.Resampling.BICUBIC)
full=Image.new('RGBA',base.size);full.paste(d,(280,775))
m=Image.new('L',base.size);pts=[(368,901),(380,903),(422,904),(463,902),(472,907),(468,916),(446,920),(397,922),(379,920),(367,914)]
ImageDraw.Draw(m).polygon(pts,fill=255);m=m.filter(ImageFilter.GaussianBlur(1.0));ma=np.array(m);ma[:899]=0;ma[895:905,:368]=0
# Only the original partly occluded bottom silhouette and tiny plate-contact zone.
a=np.array(base);b=np.array(full);weight=ma[:,:,None]/255;out=a.copy();out[:,:,:3]=np.rint(a[:,:,:3]*(1-weight)+b[:,:,:3]*weight).astype('uint8');out[:,:,3]=a[:,:,3]
res=Image.fromarray(out);res.save(r/'S03_k05_fixed_plate_candidate_v4.png');Image.fromarray(ma).save(r/'contact_repair_mask.png');d.save(r/'call01_contact_uniform_inverse.png')
diff=np.any(out!=a,axis=2);yy,xx=np.where(diff)
meta={'generation_calls':1,'generated_original_size':list(donor.size),'input_crop_xyxy':[280,775,580,941],'uniform_inverse_scale':s,'source_crop_size':[300,166],'rounding_y_extent':166*s,'target':'only lower fruit contour and tiny contact; original source alpha untouched','candidate_sha256':hashlib.sha256((r/'S03_k05_fixed_plate_candidate_v4.png').read_bytes()).hexdigest(),'changed_vs_v3_pixels':int(diff.sum()),'changed_vs_v3_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'mask_outside_changed_pixels':int(diff[ma==0].sum()),'alpha_changed_pixels':int((out[:,:,3]!=a[:,:,3]).sum()),'unchanged_above_y899':bool(np.array_equal(a[:899],out[:899])),'status':'pending independent visual contact review'}
(r/'contact_repair_v4.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta))
row=Image.new('RGB',(1800,390),'#ccc')
for i,(im,label) in enumerate([(base,'v3: plate copy; old clipped fruit base'),(res,'v4: locally generated complete base/contact'),(Image.blend(base,res,0.5),'50% overlay')]):
 cr=im.crop((280,775,580,941));bg=Image.new('RGBA',cr.size,(205,205,205,255));bg.alpha_composite(cr);row.paste(bg.convert('RGB').resize((600,332)),(i*600,36));ImageDraw.Draw(row).text((i*600+8,10),label,fill='black')
row.save(r/'contact_repair_v4_review.jpg')
