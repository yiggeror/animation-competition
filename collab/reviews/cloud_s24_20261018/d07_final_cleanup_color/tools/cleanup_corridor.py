#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
from scipy import ndimage as ndi
H=Path(__file__).resolve().parents[1];P=H.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=P/'d07_F024_zero_call_repair/candidates/F024_original_pixel_sleeve_repair_rgba.png';assert sha(source)=='8c695f4020cc00e61b19d26a6818e0aa3c22abf752bb897a88cb3b561e69dd62'
raw=P/'d05_d07_segment/originals/S24_F024_call_008_REJECTED_sleeve_crop_raw.png';assert sha(raw)=='4a29d857b82802a60dfa57549130a2bb16dd073e96765e7a29ceb33165737b8e'
a=np.array(Image.open(source).convert('RGBA'));donor=np.array(Image.open(raw).convert('RGBA').transform((1024,1536),Image.Transform.AFFINE,(1,-.25,373,0,1,24),Image.Resampling.BICUBIC));out=a.copy();yy,xx=np.indices(a.shape[:2]);r,g,b,al=np.moveaxis(a.astype('int16'),2,0)
# Real yellow/white frill and the complete native black edge/AA around it.
cloth=(al>=245)&(((r>180)&(g>120)&(b<130)&(g>b+60))|((r>220)&(g>220)&(b>205)))&(yy>=1360)
frillguard=ndi.distance_transform_edt(~cloth)<=2.5
Image.fromarray((frillguard*255).astype('uint8')).save(H/'masks/real_frill_color_stroke_AA_protected.png')
# Isolate the first-raw arm before the alpha transfer: source dress pixels must never enter the void.
raw_a=np.array(Image.open(raw).convert('RGBA'));rr,gg,bb,aa=np.moveaxis(raw_a.astype('int16'),2,0)
raw_skin=(aa>=245)&(rr>170)&(gg>100)&(bb>115)&(rr>gg+15)&(gg>bb+10)&(yy>1390)&(xx>790)
lab,_=ndi.label(raw_skin);arm_cut=ndi.binary_dilation(lab==lab[1500,900],iterations=4)
arm_cut=Image.fromarray((arm_cut*255).astype('uint8')).transform((1024,1536),Image.Transform.AFFINE,(1,-.25,373,0,1,24),Image.Resampling.BICUBIC)
left_alpha=np.rint(donor[:,:,3].astype(float)*np.array(arm_cut)/255).astype('uint8')
Image.fromarray(left_alpha).save(H/'masks/first_raw_arm_registered_alpha_no_dress.png')
paths={'left':[(782,1441),(812,1439),(823,1458),(817,1474),(794,1474),(781,1458)],'right':[(928,1420),(942,1421),(945,1435),(944,1454),(931,1454),(926,1438)]}
rows=[];union=np.zeros_like(cloth)
for name,pts in paths.items():
 m=Image.new('L',(1024,1536));ImageDraw.Draw(m).polygon(pts,fill=255);domain=(np.array(m)>0)&~frillguard
 if name=='right':domain&=donor[:,:,3]>=245
 w=np.minimum(1,ndi.distance_transform_edt(domain)/2)
 # Clear the entire old exposed line, not merely its centre pixels.
 if name=='right':w[domain&(r<190)&(g<150)]=1
 # Foreground/background alpha is repaired only on left. The right corridor is inside opaque bare skin.
 aa=a[:,:,3].astype(float)/255;da=(left_alpha if name=='left'else a[:,:,3]).astype(float)/255
 oa=aa*(1-w)+da*w
 rgb=np.divide(a[:,:,:3]*aa[:,:,None]*(1-w[:,:,None])+donor[:,:,:3]*da[:,:,None]*w[:,:,None],oa[:,:,None],out=np.zeros_like(a[:,:,:3],dtype=float),where=oa[:,:,None]>0)
 sel=w>0;out[sel,:3]=np.rint(rgb[sel]).clip(0,255).astype('uint8');out[sel,3]=np.rint(oa[sel]*255).astype('uint8')
 union|=domain
 Image.fromarray(np.rint(w*255).astype('uint8')).save(H/f'masks/{name}_corridor_weight.png')
 rows.append({'corridor':name,'polygon':pts,'changed_pixels':int(np.any(out!=a,2)[domain].sum()),'alpha_changes':int(np.count_nonzero(a[:,:,3][domain]!=out[:,:,3][domain]))})
changed=np.any(out!=a,2);assert not np.any(changed&~union);assert not np.any(changed&frillguard);assert not np.any(changed[:1400]);assert not np.any(changed[1475:])
Image.fromarray(out).save(H/'candidates/F024_cleanup_before_color.png');Image.fromarray((changed*255).astype('uint8')).save(H/'masks/cleanup_actual_changes.png')
for name,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 panel=Image.new('RGB',(1590,850),'#eeebe3');d=ImageDraw.Draw(panel)
 for i,(im,label)in enumerate([(a,'4a203f2'),(out,'corridor cleanup')]):
  bg=Image.new('RGBA',(1024,1536),(*col,255));bg.alpha_composite(Image.fromarray(im));crop=bg.convert('RGB').crop((775,1405,970,1480)).resize((780,300));panel.paste(crop,(i*795,45));d.text((i*795+5,15),label,fill='black')
  crop=bg.convert('RGB').crop((925,1423,951,1455)).resize((208,256));panel.paste(crop,(i*795+10,380));crop=bg.convert('RGB').crop((783,1440,822,1475)).resize((312,280));panel.paste(crop,(i*795+270,380))
 panel.save(H/f'qa/cleanup_{name}_before_after.jpg',quality=98)
report={'source_commit':'4a203f2fa3e56603b30c4fa2faf26ca134047074','source_sha256':sha(source),'output_sha256':sha(H/'candidates/F024_cleanup_before_color.png'),'donor_raw008_sha256':sha(raw),'donor_inverse_affine':[1,-.25,373,0,1,24],'corridors':rows,'changed_pixels':int(changed.sum()),'alpha_changed_pixels':int(np.count_nonzero(a[:,:,3]!=out[:,:,3])),'outside_corridors_changes':0,'real_frill_color_stroke_AA_changes':0,'head_neck_ears_hair_chest_changes':int(changed[:1400].sum()),'image_calls':0,'status':'ACTUAL_VISUAL_REVIEW_REQUIRED'}
(H/'qa/cleanup_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
