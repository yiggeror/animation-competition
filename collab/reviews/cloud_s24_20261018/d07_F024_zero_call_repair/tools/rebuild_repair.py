#!/usr/bin/env python3
"""Zero image calls. Rebuild S24 F024 original-pixel clothing/skin composite."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,math
from scipy import ndimage as ndi
HERE=Path(__file__).resolve().parents[1]
P=HERE.parent
for folder in ['masks','layers','candidates','qa','provenance']:(HERE/folder).mkdir(exist_ok=True)
A=Image.open(P/'d05_d07_segment/originals/S24_F024_call_008_REJECTED_sleeve_crop_raw.png').convert('RGBA')
D=Image.open(P/'d05_d07_segment/originals/S24_F024_call_009_REJECTED_pose_regression_raw.png').convert('RGBA')
# Source-space boundary follows armhole seam and complete lower frill. Exterior side is generous; alpha supplies true outside contour.
leftD=[(849,1015),(836,1037),(823,1065),(810,1100),(798,1135),(788,1172),(781,1208),(774,1242),(768,1270),(766,1295),(755,1318),(748,1340),(747,1356),(751,1372),(759,1383),(773,1392),(773,1400),(769,1412),(764,1426),(763,1436),(769,1444)]
bottomD=[(793,1449),(817,1447),(838,1438),(848,1425),(860,1417),(875,1417),(891,1421),(906,1420),(923,1414),(934,1409),(938,1431),(944,1438),(960,1432),(975,1421),(983,1407),(994,1396),(999,1384)]
leftA=[(864,1020),(850,1045),(837,1075),(823,1100),(810,1135),(801,1172),(794,1208),(785,1242),(779,1270),(778,1295),(767,1318),(759,1340),(758,1356),(762,1372),(771,1384),(785,1393),(785,1402),(780,1414),(775,1428),(772,1438),(778,1447)]
bottomA=[(803,1452),(828,1450),(848,1442),(858,1429),(870,1421),(885,1422),(902,1425),(919,1422),(938,1415),(950,1412),(953,1438),(960,1444),(976,1437),(993,1424),(1003,1410),(1011,1394)]
def cloth(im,left,bottom):
 mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(left+bottom+[(1050,1395),(1050,995),(865 if im is A else 849,1007)],fill=255)
 a=np.array(im);r,g,b,al=np.moveaxis(a.astype('int16'),2,0)
 skin=(r>170)&(g>105)&(b>120)&(r>g+15)&(g>b+10)
 yellow=(r>150)&(g>80)&(b<155)&(g>b+40)
 white=(r>200)&(g>200)&(b>180)
 nearcloth=ndi.distance_transform_edt(~yellow)<=2.5
 q=(np.array(mask)>0)&(al>=248)&~skin&(yellow|white|nearcloth)
 # Reintroduce two native antialias pixels around the opaque cloth while maintaining the internal seam.
 q=ndi.binary_dilation(q,iterations=3)
 # Follow the actual lower cloth boundary, excluding the continuing native arm outline.
 mat=yellow|white
 hem=np.full(1024,1375,dtype=int)
 for col in range(750,1024):
  ys=np.flatnonzero(mat[1380:1456,col]&(al[1380:1456,col]>=248))
  if len(ys):hem[col]=1380+int(ys[-1])+4
 hem=ndi.maximum_filter1d(hem,size=3)
 rows=np.arange(1536)[:,None]
 q &= ~((rows>hem[None,:])&(rows>=1390))
 return Image.fromarray((q*255).astype('uint8'))
md=cloth(D,leftD,bottomD);ma=cloth(A,leftA,bottomA)
md.save(HERE/'masks/call009_native_cloth.png');ma.save(HERE/'masks/call008_native_cloth.png')
def reg(im,angle,root=(860,1020)):
 t=math.radians(angle);c=math.cos(t);s=math.sin(t);x,y=root;u,v=850,1015
 inv=(c,s,u-c*x-s*y,-s,c,v+s*x-c*y)
 return im.transform(A.size,Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)
base=np.array(A);yy,xx=np.indices((1536,1024))
rt=reg(D.convert('RGBa'),2.5,root=(866,1019)).convert('RGBA');new=reg(md,2.5,root=(866,1019))
cloth=np.array(rt);cloth[:,:,3]=np.rint(cloth[:,:,3].astype(float)*np.array(new)/255).astype('uint8')
r,g,b,al=np.moveaxis(base.astype('int16'),2,0)
s=(r>170)&(g>105)&(b>120)&(r>g+15)&(g>b+10)&(al>=248)&(yy>1400)&(xx>790)
labels,n=ndi.label(s);s=labels==labels[1500,900]
armmask=ndi.binary_dilation(s,iterations=4)
arm=A.transform(A.size,Image.Transform.AFFINE,(1,-.25,373,0,1,24),Image.Resampling.BICUBIC)
aa=np.array(arm)
old=np.array(ma.filter(ImageFilter.MaxFilter(5)))
armmask_shift=Image.fromarray((armmask*255).astype('uint8')).transform(A.size,Image.Transform.AFFINE,(1,-.25,373,0,1,24),Image.Resampling.BICUBIC)
armwindow=(np.array(Image.fromarray(np.maximum(np.array(armmask_shift),armmask*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)))/255) * np.minimum(np.clip((yy-1400)/10,0,1),np.clip((1472-yy)/12,0,1))
# Correct premultiplied mix; using two sequential alpha-over fades would leave a translucent band.
w=armwindow;ap=base[:,:,3].astype(float)/255;bp=aa[:,:,3].astype(float)/255;op=ap*(1-w)+bp*w
rgb=np.divide(base[:,:,:3]*ap[:,:,None]*(1-w[:,:,None])+aa[:,:,:3]*bp[:,:,None]*w[:,:,None],op[:,:,None],out=np.zeros_like(aa[:,:,:3],dtype=float),where=op[:,:,None]>0)
body=base.copy();sel=w>0;body[sel,:3]=np.rint(rgb[sel]).clip(0,255).astype('uint8');body[sel,3]=np.rint(op[sel]*255).astype('uint8')
wipe=old/255*(1-armwindow)
# Preserve first-raw cloth at the armhole join; only the new garment may cover it.
# This prevents an alpha slit when the two drawn seam curves differ by 1–3px.
left_seam=np.where(np.any(old>0,axis=1),np.argmax(old>0,axis=1),1024)
join=(xx<(left_seam[:,None]+12))&(yy<1330)
wipe[join]*=np.clip((yy[join]-1300)/30,0,1)
body[:,:,3]=np.rint(body[:,:,3].astype(float)*(1-wipe)).astype('uint8')
res=Image.fromarray(body);res.alpha_composite(Image.fromarray(cloth));out=np.array(res)
support=(wipe>0)|(armwindow>0)|(np.array(new)>0);out[~support]=base[~support]

import hashlib,json
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
candidate=HERE/'candidates/F024_original_pixel_sleeve_repair_rgba.png'
Image.fromarray(out).save(candidate)
Image.fromarray(cloth).save(HERE/'layers/call009_registered_cloth_rgba.png')
Image.fromarray(aa).save(HERE/'layers/call008_under_cuff_skin_source_registered_rgba.png')
changed=np.any(out!=base,axis=2)
for name,arr in [('old_cloth_removal',wipe),('under_cuff_skin_weight',armwindow),('repair_support',support),('actual_changed',changed)]:
 Image.fromarray(np.rint(np.clip(arr,0,1)*255).astype('uint8')).save(HERE/f'masks/{name}.png')
new.save(HERE/'masks/call009_registered_cloth.png')
Image.fromarray((armmask*255).astype('uint8')).save(HERE/'masks/call008_native_upper_arm.png')
# Explicit protected areas, using original coordinates. The armhole transition is separately permitted.
head=yy<1000
chest=Image.new('L',A.size);ImageDraw.Draw(chest).polygon([(0,1000),(797,1000),(790,1050),(765,1100),(766,1135),(751,1200),(735,1295),(720,1360),(720,1535),(0,1535)],fill=255)
protected=head|(np.array(chest)>0)|(yy>=1472)
Image.fromarray((protected*255).astype('uint8')).save(HERE/'masks/protected_head_neck_collar_chest_lower_arm.png')
assert not np.any(changed&protected)
assert not np.any(changed&~support)
assert not np.any(out[1000:1450,1023,3]>=248)
# B is the frozen whole-layer registration, only for neutral diagnostics.
def comp(im,color):
 bg=Image.new('RGBA',im.size,(*color,255));bg.alpha_composite(im);return bg.convert('RGB')
for tag,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 full=comp(Image.fromarray(out),col);full.save(HERE/f'qa/F024_{tag}_full.jpg',quality=98)
 full.crop((710,980,1024,1500)).resize((628,1040)).save(HERE/f'qa/F024_{tag}_sleeve_2x.jpg',quality=98)
 full.crop((740,1370,1005,1500)).resize((1590,780)).save(HERE/f'qa/F024_{tag}_cuff_6x.jpg',quality=98)
for i,(im,name) in enumerate([(A,'call008_base'),(D,'call009_donor'),(Image.fromarray(out),'repair')]):
 comp(im,(160,167,172)).save(HERE/f'qa/{name}_gray_full.jpg',quality=98)
# Overlay actual changed support on the unchanged first raw.
vis=np.array(comp(A,(160,167,172)))
vis[changed]=np.rint(.35*vis[changed]+.65*np.array([220,45,155])).astype('uint8')
Image.fromarray(vis).save(HERE/'qa/protected_domain_actual_diff.jpg',quality=98)
bb=Image.fromarray((changed*255).astype('uint8')).getbbox()
sleeve=out[1000:1450,:,3]>=248
coords=np.argwhere(sleeve)
report={
 'candidate':str(candidate.relative_to(HERE)),'candidate_sha256':sha(candidate),
 'source_base_sha256':sha(P/'d05_d07_segment/originals/S24_F024_call_008_REJECTED_sleeve_crop_raw.png'),
 'source_donor_sha256':sha(P/'d05_d07_segment/originals/S24_F024_call_009_REJECTED_pose_regression_raw.png'),
 'image_generation_calls_this_repair':0,'color_edits_this_repair':0,
 'cloth_rigid_registration':{'native_pivot':[850,1015],'target_pivot':[866,1019],'clockwise_degrees':2.5,'resampling':'premultiplied RGBA bicubic'},
 'separate_skin_underlap':{'source':'call008 original upper-arm pixels only','inverse_affine':[1,-.25,373,0,1,24], 'destination_y_support':[1401,1471],'last12rows_fade_to_original':True,'note':'Narrow affine seam only; maximum extra horizontal shear 8px at y1440 compared with -5px rigid shift. Main upper arm at y>=1472 is exact. No generated or drawn pixels.'},
 'changed_pixels':int(changed.sum()),'changed_bbox':list(bb),'alpha_changes_in_repair':int(np.count_nonzero(base[:,:,3]!=out[:,:,3])),
 'protected_pixels':int(protected.sum()),'protected_RGBA_changes':int((changed&protected).sum()),
 'outside_repair_support_RGBA_changes':int((changed&~support).sum()),
 'head_neck_ears_tails_y0_999_RGBA_changes':int(changed[:1000].sum()),
 'lower_arm_y1472_on_RGBA_changes':int(changed[1472:].sum()),
 'rightmost_column_opaque_pixels_sleeve_y1000_1449':int((out[1000:1450,1023,3]>=248).sum()),
 'opaque_sleeve_max_x':int(coords[:,1].max()),'opaque_sleeve_right_margin_native_px':int(1023-coords[:,1].max()),
 'status':'ORIGINAL_PIXEL_COMPOSITE_FOR_ASTRA_REVIEW;NO_ASTRA_LOCK_CLAIM',
 'not_Canvas_scene':True,'F032_started':False
}
(HERE/'qa/repair_pixel_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
