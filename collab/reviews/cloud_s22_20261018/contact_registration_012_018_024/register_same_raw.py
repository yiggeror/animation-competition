#!/usr/bin/env python3
"""Explicitly authorized pixel registration of existing drawings; zero image calls.

Locked F000 child+rod pixels form the middle layer. Existing adult pixels form
the rear layer and the locally retained foreground thumb/four finger pads.
The spline below is a segmentation mask, never a generated hand or redraw.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INPUT=ROOT/'contact_012_018_024'
MOTHER=ROOT/'F000_color_repair/candidate/F000_repaired.png'
EXPECTED_MOTHER='d4e78e2d5b84a72588cf3af1ff23ce39cdc18d19dde2fbf1f8eaf44ba62d7ef5'
CONFIG={
 'F012':dict(raw='F012_call02_raw.png',sha='aaa4ee1ed1ee2142ebcfac245e5934e34ba55b6f86eed11c430fb7fb22cb523f',child=[443,471,472,474,476,482,483],pads=[],thumb_start=[575,455],thumb_curves=[[[600,450],[628,457],[648,477]],[[663,498],[683,503],[707,519]],[[738,531],[750,548],[736,564]],[[721,581],[690,563],[668,550]],[[645,536],[620,537],[597,524]],[[583,513],[578,504],[572,492]]]),
 'F018':dict(raw='F018_call01_raw.png',sha='062e9495d9b401e23bd9c8670b4c08f8f1d19c4c08cd1fc9328924fc62e8283d',child=[422,445,459,460,465,467],pads=[464,469,470,473],thumb_start=[575,450],thumb_curves=[[[600,447],[628,455],[651,476]],[[670,502],[693,508],[714,527]],[[740,548],[741,570],[725,582]],[[710,594],[683,578],[663,559]],[[642,545],[616,544],[595,529]],[[581,518],[573,508],[568,494]]]),
 'F024':dict(raw='F024_call01_raw.png',sha='75b367bc3eb000ae5e526bc2fa90762a4f990b6b380766554a1635608f89d1a5',child=[500,526,529,530,534,535],pads=[533,537,538,542],thumb_start=[578,444],thumb_curves=[[[602,441],[628,450],[651,471]],[[670,500],[696,508],[720,529]],[[745,548],[743,570],[727,580]],[[710,590],[683,574],[664,556]],[[643,542],[620,542],[598,529]],[[583,518],[575,505],[570,489]]])
}
for sub in ['candidate','masks','qa','provenance']:
 (HERE/sub).mkdir(exist_ok=True)
assert hashlib.sha256(MOTHER.read_bytes()).hexdigest()==EXPECTED_MOTHER
mother=np.asarray(Image.open(MOTHER).convert('RGBA')).copy()
h,w=mother.shape[:2]; yy,xx=np.mgrid[:h,:w]
opaque,n=nd.label(mother[:,:,3]>=128); assert n==2
c_id=int(opaque[700,500]); assert c_id>0
_,indices=nd.distance_transform_edt(opaque==0,return_indices=True)
nearest=opaque[tuple(indices)]
child_alpha=mother[:,:,3].astype(float)/255*(nearest==c_id)
child=mother.astype(float)/255
child[:,:,3]=child_alpha
Image.fromarray(np.rint(child_alpha*255).astype('uint8')).save(HERE/'masks/locked_F000_child_and_rod.png')

def spline_mask(start,curves):
 points=[np.array(start,float)]; p=points[0]
 for controls in curves:
  a,b,c=map(lambda q:np.array(q,float),controls)
  for t in np.linspace(0,1,40)[1:]:
   points.append((1-t)**3*p+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*c)
  p=c
 scale=4; im=Image.new('L',(w*scale,h*scale))
 ImageDraw.Draw(im).polygon([(int(x*scale),int(y*scale)) for x,y in points],fill=255)
 return np.array(im.resize((w,h),Image.Resampling.LANCZOS),float)/255

def over(top,below):
 at=top[:,:,3:4]; ab=below[:,:,3:4]; ao=at+ab*(1-at)
 rgb=np.divide(top[:,:,:3]*at+below[:,:,:3]*ab*(1-at),ao,out=np.zeros_like(top[:,:,:3]),where=ao>0)
 return np.concatenate([rgb,ao],axis=2)

def save_mask(name,mask):
 Image.fromarray(np.rint(np.clip(mask,0,1)*255).astype('uint8')).save(HERE/'masks'/name)

def preview(a,bg):
 im=Image.fromarray(a); plate=Image.new('RGBA',im.size,(*bg,255)); plate.alpha_composite(im)
 return plate.convert('RGB')

metrics={}
for name,cfg in CONFIG.items():
 rawpath=INPUT/name/'originals'/cfg['raw']; assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==cfg['sha']
 raw=np.asarray(Image.open(rawpath).convert('RGBA')).copy()
 skin=(raw[:,:,3]>128)&(raw[:,:,0]>210)&(raw[:,:,1]>145)&(raw[:,:,2]>100)
 labels,n=nd.label(skin); size=np.bincount(labels.ravel())
 major=labels.copy(); major[~np.isin(labels,np.where(size>=100)[0][1:])]=0
 dist,ix=nd.distance_transform_edt(major==0,return_indices=True)
 near=major[tuple(ix)]
 # Closed ink contours give actual pixel regions, classified by observed anatomy.
 old_child=np.isin(near,cfg['child'])
 adult=(~old_child)&(dist<=12)&(near>0)
 adult=nd.binary_dilation(adult,iterations=1)&(raw[:,:,3]>0)
 adult[xx>=916]=False
 # Remove the old shaft strip but retain the actual adjacent adult ink.
 old_rod=json.loads((INPUT/'provenance/actual_image_measurements.json').read_text())[name]
 old_axis=old_rod['rod_slope']*xx+old_rod['rod_y_intercept']
 adult[(xx>=880)&(np.abs(yy-old_axis)<17)&(dist>4)]=False
 thumb_polygon=spline_mask(cfg['thumb_start'],cfg['thumb_curves'])
 pads=np.isin(near,cfg['pads'])&(dist<=12)
 thumb_region=nd.binary_dilation(thumb_polygon>.05,iterations=6)
 front_bool=(thumb_region|pads)&adult
 front=nd.gaussian_filter(front_bool.astype(float),.65)
 front[nd.binary_erosion(front_bool,iterations=2)]=1
 # Transfer only the existing soft contact-side skin darkening, locally. Preserve
 # ink and the child's nail/pinch. There is no invented cast light or flat fill.
 c=child.copy(); distance=nd.distance_transform_edt(~front_bool)
 band=.5*(1+np.cos(np.pi*np.clip(distance/12,0,1)))*(1-front)
 valid=(old_child)&(raw[:,:,3]>=128)&(raw[:,:,0]>210)&(mother[:,:,0]>210)&(child_alpha>.99)
 delta=np.minimum(raw[:,:,:3].astype(float)-mother[:,:,:3],0)
 delta=np.maximum(delta,-14)
 denom=nd.gaussian_filter(valid.astype(float),2)
 smooth=np.stack([nd.gaussian_filter(delta[:,:,k]*valid,2)/np.maximum(denom,1e-6) for k in range(3)],axis=2)
 transfer=band*(denom>.05)*(child_alpha>.99)
 transfer[(xx>=815)&(xx<=900)&(yy>=470)&(yy<=570)]=0
 c[:,:,:3]=np.clip(c[:,:,:3]+smooth/255*transfer[:,:,None],0,1)
 adult_rgba=raw.astype(float)/255; adult_rgba[:,:,3]*=adult
 back_order=over(c,adult_rgba); front_order=over(adult_rgba,c)
 result=back_order*(1-front[:,:,None])+front_order*front[:,:,None]
 # Reconnect only the small contact-side slivers vacated by the old child edge.
 # The donors are real locked child / original adult skin pixels. They are rear
 # joins beneath the retained adult fingertip contours, never new finger shapes.
 dc=nd.distance_transform_edt(child_alpha<.5)
 da=nd.distance_transform_edt(~adult)
 join=(result[:,:,3]<.98)&(raw[:,:,3]>=128)&(dc<=13)&(da<=13)&(distance<=22)&(xx>=640)&(xx<=920)&(yy>=550)&(yy<=745)
 join[(xx>=815)&(yy<=570)]=False
 gy,gx=np.mgrid[-7:8,-7:8]; disk=gx*gx+gy*gy<=49
 closed=nd.binary_closing(result[:,:,3]>=.5,structure=disk)
 join &= closed
 cskin=(child_alpha>.5)&(mother[:,:,0]>210)&(mother[:,:,1]>145)&(mother[:,:,2]>100)
 gskin=skin&~np.isin(labels,cfg['child'])&(major>0)
 dcskin,ic=nd.distance_transform_edt(~cskin,return_indices=True)
 dgskin,ig=nd.distance_transform_edt(~gskin,return_indices=True)
 donor_c=mother[tuple(ic)][:,:,:3].astype(float)/255
 donor_g=raw[tuple(ig)][:,:,:3].astype(float)/255
 blend=dcskin/np.maximum(dcskin+dgskin,1e-6)
 donor=donor_c*(1-blend[:,:,None])+donor_g*blend[:,:,None]
 donor=np.clip(donor+smooth/255*band[:,:,None],0,1)
 join_coverage=nd.gaussian_filter(join.astype(float),.65)*(result[:,:,3]<.98)
 patch=np.zeros_like(result); patch[:,:,:3]=donor; patch[:,:,3]=raw[:,:,3]/255*join_coverage
 result=over(result,patch)
 out=np.rint(np.clip(result,0,1)*255).astype('uint8')
 # Exact preservation of adult foreground core and locked visible child core.
 adult_core=(front>.999)&adult&(raw[:,:,3]>=128)
 out[adult_core]=raw[adult_core]
 assert np.array_equal(out[adult_core],raw[adult_core])
 child_core=(child_alpha>=128/255)&(front==0)&(transfer==0)
 out[child_core]=mother[child_core]
 assert np.array_equal(out[child_core],mother[child_core])
 outpath=HERE/'candidate'/f'{name}_registered.png'; Image.fromarray(out).save(outpath)
 save_mask(f'{name}_adult_retained.png',adult.astype(float))
 save_mask(f'{name}_adult_foreground.png',front)
 save_mask(f'{name}_thumb_segmentation.png',thumb_polygon)
 save_mask(f'{name}_contact_transfer.png',transfer)
 save_mask(f'{name}_old_child_class.png',old_child.astype(float))
 save_mask(f'{name}_local_reconnect.png',join_coverage)
 for bgname,bg in [('gray',(115,115,115)),('white',(255,255,255)),('black',(0,0,0))]:
  preview(out,bg).save(HERE/'qa'/f'{name}_registered_on_{bgname}.png')
 crop=(530,410,930,755)
 preview(out,(115,115,115)).crop(crop).resize((1000,862)).save(HERE/'qa'/f'{name}_registered_contact_2_5x.png')
 overlay=preview(raw,(115,115,115)); pix=np.array(overlay).astype(float); f=front[:,:,None]*.45; pix=pix*(1-f)+np.array([70,200,255])*f
 Image.fromarray(np.rint(pix).astype('uint8')).save(HERE/'qa'/f'{name}_foreground_mask_overlay.png')
 metrics[name]=dict(source=str(rawpath.relative_to(ROOT)),source_sha256=cfg['sha'],candidate_sha256=hashlib.sha256(outpath.read_bytes()).hexdigest(),size=[w,h],adult_foreground_core_pixels=int(adult_core.sum()),adult_foreground_core_RGBA_exact=True,locked_child_core_pixels=int(child_core.sum()),locked_child_core_RGBA_exact=True,local_reconnect_pixels=int(join.sum()),contact_blend_radius_px=12,new_image_calls=0)
(HERE/'provenance/segmentation_config.json').write_text(json.dumps(CONFIG,indent=2)+'\n')
(HERE/'provenance/pixel_invariants.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
