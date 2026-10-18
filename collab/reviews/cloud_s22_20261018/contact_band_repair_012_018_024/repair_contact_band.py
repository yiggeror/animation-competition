#!/usr/bin/env python3
"""Authorized same-raw continuous contact-band repair and local F024 settling.
No image generation. Existing drawings supply every material/shape; masks only
select old contact ink, and a smooth local resampling field moves four ends.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd, sparse
from scipy.sparse.linalg import spsolve

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
REG=ROOT/'contact_registration_012_018_024'; RAW=ROOT/'contact_012_018_024'
CFG=json.loads((REG/'provenance/segmentation_config.json').read_text())
REGSHA=json.loads((REG/'provenance/pixel_invariants.json').read_text())
MOTHER=ROOT/'F000_color_repair/candidate/F000_repaired.png'
mother=np.array(Image.open(MOTHER).convert('RGBA')); h,w=mother.shape[:2]; yy,xx=np.mgrid[:h,:w]
C=np.array(Image.open(REG/'masks/locked_F000_child_and_rod.png'),float)/255
FROZEN_BOXES={'wrist_crease':[655,640,690,674],'visible_palm':[710,595,755,625],'child_thumb_nail':[846,506,879,541],'child_pinch':[760,470,893,566],'single_rod':[950,0,1672,510]}
FROZEN=np.zeros((h,w),bool)
for x0,y0,x1,y1 in FROZEN_BOXES.values(): FROZEN[y0:y1,x0:x1]|=C[y0:y1,x0:x1]>=128/255
# One connected, generously bounded contact ROI. No rectangular cutouts of ink.
roi_im=Image.new('L',(w,h)); ImageDraw.Draw(roi_im).polygon([(615,590),(760,570),(916,563),(929,615),(915,691),(845,755),(709,760),(623,712)],fill=255)
ROI=np.array(roi_im)>0
roi_feather=np.clip(nd.distance_transform_edt(ROI)/9,0,1)
NAILS={
 'F018':[(859,632,12,15),(784,672,15,12),(741,686,15,13),(709,700,13,12)],
 'F024':[(864,638,12,15),(781,672,15,13),(732,690,15,13),(699,707,13,12)]}
MOVES=[(-1,-2),(2,-3),(3,-3),(3,-4)]
for sub in ['candidate','masks','qa','provenance']: (HERE/sub).mkdir(exist_ok=True)

def ellipse(cx,cy,rx,ry,expand=0): return ((xx-cx)/(rx+expand))**2+((yy-cy)/(ry+expand))**2<=1
def over(top,below):
 at=top[:,:,3:4]; ab=below[:,:,3:4]; ao=at+ab*(1-at)
 rgb=np.divide(top[:,:,:3]*at+below[:,:,:3]*ab*(1-at),ao,out=np.zeros_like(top[:,:,:3]),where=ao>0)
 return np.concatenate([rgb,ao],2)
def harmonic(rgb,mask):
 """Dirichlet interpolation across selected obsolete ink, preserving gradients."""
 result=rgb.astype(float).copy(); y,x=np.where(mask); n=len(y)
 if not n:return result
 ids=np.full(mask.shape,-1,int); ids[y,x]=np.arange(n)
 rr=[]; cc=[]; vv=[]; rhs=np.zeros((n,3))
 for i,(py,px) in enumerate(zip(y,x)):
  degree=0
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   qy,qx=py+dy,px+dx
   if qy<0 or qy>=h or qx<0 or qx>=w:continue
   if rgb[qy,qx,0]<10 and not mask[qy,qx]:continue
   degree+=1; j=ids[qy,qx]
   if j>=0:rr.append(i);cc.append(j);vv.append(-1)
   else:rhs[i]+=rgb[qy,qx]
  rr.append(i);cc.append(i);vv.append(max(degree,1))
 mat=sparse.csr_matrix((vv,(rr,cc)),shape=(n,n)); result[y,x]=spsolve(mat,rhs)
 return result
def warp(a,ux,uy,order=1):
 coords=[yy-uy,xx-ux]
 if a.ndim==2:return nd.map_coordinates(a,coords,order=order,mode='constant',cval=0)
 return np.stack([nd.map_coordinates(a[:,:,k],coords,order=order,mode='constant',cval=0) for k in range(a.shape[2])],2)
def comp_bg(a,bg):
 im=Image.fromarray(a); plate=Image.new('RGBA',im.size,(*bg,255)); plate.alpha_composite(im);return plate.convert('RGB')
def mask_save(name,m):Image.fromarray(np.rint(np.clip(m,0,1)*255).astype('uint8')).save(HERE/'masks'/name)

metrics={}
for name,cfg in CFG.items():
 path=REG/'candidate'/f'{name}_registered.png'; assert hashlib.sha256(path.read_bytes()).hexdigest()==REGSHA[name]['candidate_sha256']
 before=np.array(Image.open(path).convert('RGBA')); a=before.astype(float)/255
 if name=='F012':
  Image.fromarray(before).save(HERE/'candidate/F012_contact_fixed.png');metrics[name]={'unchanged_from_registration':True,'new_image_calls':0};continue
 rawpath=RAW/name/'originals'/cfg['raw']; assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==cfg['sha']
 raw=np.array(Image.open(rawpath)); skin=(raw[:,:,3]>128)&(raw[:,:,0]>210)&(raw[:,:,1]>145)&(raw[:,:,2]>100)
 labels,n=nd.label(skin); sizes=np.bincount(labels.ravel()); major=labels.copy(); major[~np.isin(labels,np.where(sizes>=100)[0][1:])]=0
 child_skin=skin&np.isin(labels,cfg['child']); adult_skin=skin&~np.isin(labels,cfg['child'])&(major>0)
 dc=nd.distance_transform_edt(~child_skin); dg=nd.distance_transform_edt(~adult_skin)
 dc_locked=nd.distance_transform_edt(C<.5)
 fg=np.array(Image.open(REG/'masks'/f'{name}_adult_foreground.png'),float)/255
 thumb_shape=np.array(Image.open(REG/'masks'/f'{name}_thumb_segmentation.png'))>0
 thumb=nd.binary_dilation(thumb_shape,iterations=9)&(fg>.01)
 protect_nails=np.zeros((h,w),bool)
 for i,(cx,cy,rx,ry) in enumerate(NAILS[name]):protect_nails|=ellipse(cx,cy,rx,ry,1 if i==0 else 6)
 pad_fg=fg.copy();pad_fg[nd.binary_dilation(thumb,iterations=3)]=0
 band=ROI&(dc_locked<=27)&(C<.04)&~thumb&~protect_nails
 # The original opaque drawing distinguishes true external adult ink from the
 # artificial holes in the registered candidate. Retain that physical exterior.
 raw_inside=nd.distance_transform_edt(raw[:,:,3]>=128)
 true_outer=(raw[:,:,3]>=128)&(raw_inside<=4)
 distances=[nd.distance_transform_edt(~(skin&(labels==k))) for k in cfg['pads']]
 second_pad_distance=np.partition(np.stack(distances),1,axis=0)[1]
 true_digit_separator=second_pad_distance<=5
 # Old child/adult boundary is obsolete wherever it falls outside the locked
 # child. Keep adult/adult digit separators and every protected nail plate.
 old_echo=band&(before[:,:,3]>=128)&(before[:,:,0]<242)&(dc<=13)&(dg<=16)&~true_outer&~true_digit_separator
 erase=nd.binary_dilation(old_echo,iterations=3)&ROI&(C<.04)&~thumb&~protect_nails&~true_outer&~true_digit_separator
 # Clear pale anti-alias remnants across the entire wrist return band as well.
 wrist_return=ROI&(xx<730)&(yy>660)&(dc_locked>1)&(dc_locked<18)&(dc<=15)&(dg<=22)&(C<.04)&(raw[:,:,3]>=128)&~thumb&~protect_nails&~true_outer&~true_digit_separator
 erase|=wrist_return
 # Remove any canonical child ink accidentally present in the adult foreground
 # texture before resampling it. The actual child is reinserted unmoved below.
 inside_child=nd.distance_transform_edt(C>=.5)
 texture_ink=(C>=.04)&(inside_child<=7)&(before[:,:,0]<215)&ROI&~protect_nails
 erase_texture=erase|nd.binary_dilation(texture_ink,iterations=1)&ROI&~thumb&~protect_nails
 clean_rgb=harmonic(before[:,:,:3],erase_texture)/255
 cleaned=a.copy();cleaned[:,:,:3]=np.clip(clean_rgb,0,1)
 # Adult layer has the stable child removed; retain the true original foreground
 # thumb/fingertips so they can still overlap the child locally.
 adult=cleaned.copy()
 retained=np.array(Image.open(REG/'masks'/f'{name}_adult_retained.png'))>0
 old_join=np.array(Image.open(REG/'masks'/f'{name}_local_reconnect.png'))>0
 backing=ROI&(raw[:,:,3]>=128)&(dg<=22)&(inside_child<=7)&(dc_locked<=18)&~true_outer
 presence=retained|old_join|backing
 # Real adult skin must remain opaque under the locked child's anti-aliased
 # contour. The previous split-alpha matte otherwise leaves dotted gray seams.
 bad_backing=backing&(before[:,:,3]<240)&~thumb&~protect_nails
 _, donor_ix=nd.distance_transform_edt(~adult_skin,return_indices=True)
 adult[:,:,:3][bad_backing]=raw[tuple(donor_ix)][:,:,:3][bad_backing]/255
 adult[:,:,3][backing]=np.maximum(adult[:,:,3][backing],raw[:,:,3][backing]/255)
 adult[:,:,3]*=presence
 child_interior=(C>=.5)&(inside_child>5)
 adult[:,:,3]*=1-child_interior*(1-fg)
 ux=np.zeros((h,w));uy=np.zeros((h,w));nail_core_dest=[]
 if name=='F024':
  kernels=[]
  for (cx,cy,rx,ry),(dx,dy) in zip(NAILS[name],MOVES):
   r=np.sqrt((xx-(cx+dx))**2+(yy-(cy+dy))**2)/78
   k=np.where(r<1,(1-r)**4*(4*r+1),0);kernels.append(k)
  total=np.sum(kernels,axis=0);factor=np.clip(total/.4,0,1)
  for k,(dx,dy) in zip(kernels,MOVES):
   ux+=k*dx/np.maximum(total,1e-8)*factor;uy+=k*dy/np.maximum(total,1e-8)*factor
  for (cx,cy,rx,ry),(dx,dy) in zip(NAILS[name],MOVES):
   r=np.sqrt(((xx-(cx+dx))/(rx+8))**2+((yy-(cy+dy))/(ry+8))**2)
   z=np.clip((1.6-r)/.6,0,1);z=z*z*(3-2*z)
   ux=ux*(1-z)+dx*z;uy=uy*(1-z)+dy*z
   nail_core_dest.append((ellipse(cx+dx,cy+dy,rx,ry),dx,dy))
  for m,dx,dy in nail_core_dest:ux[m]=dx;uy[m]=dy
  ux*=roi_feather;uy*=roi_feather;ux[thumb]=0;uy[thumb]=0
 else:
  for cx,cy,rx,ry in NAILS[name]:nail_core_dest.append((ellipse(cx,cy,rx,ry)&(C<.04),0,0))
 moved=warp(adult,ux,uy,3);moved[:,:,3]=np.clip(moved[:,:,3],0,1)
 front=warp(fg,ux,uy,1);front[thumb]=fg[thumb]
 # Along this continuous band the locked child is the single contact boundary;
 # the adult end surfaces remain visible below it. Only the actual adult thumb
 # retains its established foreground overlap on the child's hand back.
 front[(C>.01)&~thumb]=0
 # Stable real child pixels, including the sole hand/rod contour.
 child=mother.astype(float)/255;child[:,:,3]=C
 back_order=over(child,moved);front_order=over(moved,child)
 result=back_order*(1-front[:,:,None])+front_order*front[:,:,None]
 # Blend only in the one continuous ROI, at a distance from line endings.
 out=np.rint(np.clip(result*roi_feather[:,:,None]+a*(1-roi_feather[:,:,None]),0,1)*255).astype('uint8')
 # Preserve the locked visible child, without turning old foreground contact ink
 # into another child silhouette. Foreground true fingertip coverage remains.
 ccore=(C>=.5)&(front<.01)&ROI
 out[ccore]=mother[ccore]
 out[thumb]=before[thumb]
 for m,dx,dy in nail_core_dest:
  y,x=np.where(m);out[y,x]=before[y-dy,x-dx]
 # Heal only tiny contact notches with neighbouring original RGBA pixels.
 gy,gx=np.mgrid[-2:3,-2:3];closed=nd.binary_closing(out[:,:,3]>=128,structure=gx*gx+gy*gy<=4)
 near_child=nd.distance_transform_edt(C<.5)
 notches=closed&(out[:,:,3]<128)&(raw[:,:,3]>=128)&ROI&(near_child<=5)&(dg<=16)&~thumb&~FROZEN
 for m,dx,dy in nail_core_dest:notches[m]=False
 if np.any(notches):
  _, donor_ix=nd.distance_transform_edt(out[:,:,3]<128,return_indices=True)
  donor=out[tuple(donor_ix)];out[notches]=donor[notches]
 assert np.array_equal(out[FROZEN],mother[FROZEN])
 assert np.array_equal(out[thumb],before[thumb])
 assert np.array_equal(out[~ROI],before[~ROI])
 # Verify thickness/colour by exact translated nail pixels, independently of RGB
 # interpolation elsewhere; digit order is never exchanged.
 for m,dx,dy in nail_core_dest:
  y,x=np.where(m);assert np.array_equal(out[y,x],before[y-dy,x-dx])
 outpath=HERE/'candidate'/f'{name}_contact_fixed.png';Image.fromarray(out).save(outpath)
 mask_save(f'{name}_continuous_ROI.png',ROI.astype(float));mask_save(f'{name}_obsolete_contact_ink.png',erase.astype(float))
 mask_save(f'{name}_texture_ink_removed.png',erase_texture.astype(float));mask_save(f'{name}_thumb_frozen.png',thumb.astype(float))
 mask_save(f'{name}_nails_protected.png',protect_nails.astype(float));mask_save(f'{name}_foreground_after.png',front)
 delta=np.any(before!=out,axis=2);mask_save(f'{name}_actual_changed_pixels.png',delta.astype(float))
 np.savez_compressed(HERE/'provenance'/f'{name}_local_field.npz',dx=ux.astype('float32'),dy=uy.astype('float32'))
 for bgname,bg in [('gray',(115,115,115)),('white',(255,255,255)),('black',(0,0,0))]:comp_bg(out,bg).save(HERE/'qa'/f'{name}_fixed_on_{bgname}.png')
 crop=(620,550,920,745);comp_bg(out,(115,115,115)).crop(crop).resize((1200,780)).save(HERE/'qa'/f'{name}_continuous_band_4x.png')
 overlay=np.array(comp_bg(before,(115,115,115)),float);z=erase[:,:,None]*.75;overlay=overlay*(1-z)+np.array([255,0,160])*z
 Image.fromarray(np.rint(overlay).astype('uint8')).save(HERE/'qa'/f'{name}_removed_ink_overlay.png')
 y,x=np.where(delta);metrics[name]=dict(source_sha256=REGSHA[name]['candidate_sha256'],candidate_sha256=hashlib.sha256(outpath.read_bytes()).hexdigest(),obsolete_ink_mask_pixels=int(erase.sum()),contact_notch_pixels=int(notches.sum()),changed_pixels=int(delta.sum()),changed_bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],frozen_child_regions_RGBA_exact=True,adult_thumb_RGBA_exact=True,outside_continuous_ROI_RGBA_exact=True,nail_exact_integer_translations=MOVES if name=='F024' else[],new_image_calls=0)
(HERE/'provenance/pixel_checks.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
