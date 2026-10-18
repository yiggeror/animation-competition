from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,distance_transform_edt
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent
base=Image.open(R/'candidates/S03a_F017.png').convert('RGBA');a=np.array(base);raw=np.array(Image.open(R/'raw/F021_tails_v1.png').convert('RGBA'));gar=np.array(Image.open(R/'masks/source_fixed_garment_semantic.png'))>0;Y,X=np.indices(a.shape[:2]);H,W=Y.shape
polys={'left':[(606,678),(623,691),(648,706),(677,720),(714,731),(716,751),(686,777),(636,792),(548,795),(531,763),(553,715),(580,689)],'right':[(987,682),(1069,682),(1135,660),(1205,690),(1210,790),(1184,817),(1062,819),(1000,790),(978,742),(977,705)]}
union=np.zeros((H,W),bool);layers={};records={}
for n,pts in polys.items():
 p=Image.new('L',base.size);ImageDraw.Draw(p).polygon(pts,fill=255);roi=np.array(p)>0;m=roi&~gar;union|=m;layer=a.copy();layer[~m]=0
 valid=(layer[:,:,3]>180)&(layer[:,:,0]<140)&(layer[:,:,1]<120)&(layer[:,:,2]<110)
 # The generator supplies only hidden-under-shoulder continuation colors/strands.
 donor_roi=((X>590)&(X<720)&(Y>690)&(Y<773)) if n=='left' else ((X>997)&(X<1195)&(Y>689)&(Y<784))
 donor=donor_roi&(raw[:,:,3]>240)&(raw[:,:,0]<140)&(raw[:,:,1]<120)&(raw[:,:,2]<110)
 _,inds=distance_transform_edt(~donor,return_indices=True);fill=np.zeros((H,W),bool);sy=np.full((H,W),-1,np.int16);sx=sy.copy()
 for x in np.where(valid.any(axis=0))[0]:
  ys=np.where(valid[:,x])[0];last=int(ys[-1]);
  if last<715 or last>796:continue
  if not np.any(gar[last+1:min(last+9,H),x]):continue
  # Hidden extension only; original visible hair and all roots remain original.
  for y in range(last+1,min(last+38,835)):
   if not gar[y,x]:continue
   tx=min(W-1,max(0,x+(45 if n=='left' else 13)));ty=max(0,y-42);dy,dx=inds[:,ty,tx];c=raw[dy,dx].astype(float);edge=a[last,x].astype(float);v=np.clip((y-last)/10,0,1);layer[y,x]=np.rint(edge*(1-v)+c*v).astype('uint8');layer[y,x,3]=255;fill[y,x]=True;sy[y,x]=dy;sx[y,x]=dx
 Image.fromarray(fill.astype('uint8')*255).save(R/f'masks/tail_{n}__hidden_donor_fill.png');np.savez_compressed(R/f'masks/tail_{n}__donor_source_xy.npz',source_x=sx,source_y=sy);Image.fromarray(layer).save(R/f'diagnostics/tail_{n}__extended_layer.png');visible=a.copy();visible[~m]=0;layers[n]=(layer,m,visible);records[n]={'hidden_fill_pixels':int(fill.sum()),'donor_source':'raw/F021_tails_v1.png','donor_nearest_hair_roi':([590,690,720,773] if n=='left' else [997,689,1195,784])}
Image.fromarray(union.astype('uint8')*255).save(R/'masks/F021_F023__pixel_tail_allowed.png')
for f,shifts in [('021',{'left':(25,-5),'right':(18,-7)}),('023',{'left':(11,-2),'right':(8,-3)})]:
 out=a.copy();maps={}
 for n,(dx,dy) in shifts.items():
  layer,m,visible=layers[n];top=690 if n=='left' else 685;bottom=780;t=np.clip((Y-top)/(bottom-top),0,1);t=t*t*(3-2*t);sx=X-dx*t;sy=Y-dy*t
  # Premultiplied alpha resampling avoids coloured fringe from transparent pixels.
  af=layer[:,:,3].astype(float)/255;wa=map_coordinates(af,[sy,sx],order=1,mode='constant',cval=0);rgb=[]
  for k in range(3):
   v=map_coordinates(layer[:,:,k].astype(float)*af,[sy,sx],order=1,mode='constant',cval=0);rgb.append(np.divide(v,wa,out=np.zeros_like(v),where=wa>1e-6))
  sample=np.stack(rgb+[wa*255],axis=2)
  # Only bridge newly exposed narrow gaps directly above the fixed shoulder.
  # Never expose a rectangular hidden extension outside the shoulder silhouette.
  vf=visible[:,:,3].astype(float)/255;va=map_coordinates(vf,[sy,sx],order=1,mode='constant',cval=0);vr=[]
  for k in range(3):
   z=map_coordinates(visible[:,:,k].astype(float)*vf,[sy,sx],order=1,mode='constant',cval=0);vr.append(np.divide(z,va,out=np.zeros_like(z),where=va>1e-6))
  original_sample=np.stack(vr+[va*255],axis=2);bridge=np.zeros((H,W),bool)
  for col in np.where((va>.6).any(axis=0))[0]:
   ys=np.where((va[:,col]>.6)&(Y[:,col]>720))[0]
   if not len(ys):continue
   last=int(ys[-1]);gs=np.where(gar[last+1:,col])[0]
   if not len(gs):continue
   first=last+1+int(gs[0]);gap=first-last
   if gap<=15 and not (n=='right' and col>=(1128 if f=='021' else 1117)):bridge[last:first+1,col]=True
  # Fully preserve resampled original visible hair; donor fills only its uncovered support.
  newly=(va<.98)&(wa>va)&bridge
  combined=original_sample.copy();combined[newly]=sample[newly]
  Image.fromarray(newly.astype('uint8')*255).save(R/f'masks/F{f}__{n}_visible_donor_patch.png')
  active=m&(t>0);out[active]=np.clip(np.rint(combined[active]),0,255).astype('uint8');maps[n]={'tip_delta':[dx,dy],'zero_displacement_until_y':top,'full_displacement_by_y':bottom,'interpolation':'premultiplied bilinear; smoothstep zero-derivative root ramp'}
  np.savez_compressed(R/f'masks/F{f}__{n}_inverse_map.npz',source_x=sx[m].astype('float32'),source_y=sy[m].astype('float32'),dest_x=X[m].astype('int16'),dest_y=Y[m].astype('int16'))
 # Actual generated tapered central tip closes the newly exposed cut, without touching the root.
 tipmask=Image.new('L',base.size);ImageDraw.Draw(tipmask).polygon([(1144,729),(1183,727),(1187,745),(1176,767),(1158,779),(1143,784),(1149,763),(1149,745)],fill=255);tm=np.array(tipmask)>0
 offset=0 if f=='021' else -10;vertical=2 if f=='021' else 6
 dsx=1144+(X-(1106+offset))/1.25;dsy=Y-vertical
 donor=np.stack([map_coordinates(raw[:,:,k].astype(float),[dsy,dsx],order=1,mode='constant',cval=0) for k in range(4)],axis=2);donor=np.clip(np.rint(donor),0,255).astype('uint8');dm=map_coordinates(tm.astype(float),[dsy,dsx],order=1,mode='constant',cval=0)>.2
 local=(X>1104-(10 if f=='023' else 0))&(X<1157-(10 if f=='023' else 0))&(Y>748+(4 if f=='023' else 0))&(Y<798+(4 if f=='023' else 0))
 use=dm&local&union&~gar&(out[:,:,3]<245)&(donor[:,:,3]>0)&(donor[:,:,0]<140)&(donor[:,:,1]<120)&(donor[:,:,2]<110)
 # Alpha-over the donor only into the exposed empty support; existing original strands remain intact.
 aa=donor[:,:,3].astype(float)/255;ba=out[:,:,3].astype(float)/255;oa=aa+ba*(1-aa);com=out.copy()
 for k in range(3):com[:,:,k]=np.clip(np.rint(np.divide(donor[:,:,k]*aa+out[:,:,k]*ba*(1-aa),oa,out=np.zeros_like(oa),where=oa>0)),0,255).astype('uint8')
 com[:,:,3]=np.rint(oa*255).astype('uint8');out[use]=com[use]
 Image.fromarray(use.astype('uint8')*255).save(R/f'masks/F{f}__generated_taper_tip_patch.png')
 # A one-column newly exposed occlusion crack uses nearby generated interior hair.
 crack=(X>=1048-(10 if f=='023' else 0))&(X<=1060-(10 if f=='023' else 0))&(Y>=754)&(Y<=782)&union&~gar&(out[:,:,3]<120)
 yy=np.clip(Y-30,0,H-1);xx=np.clip(X+30,0,W-1);hair=raw[yy,xx];crack&=(hair[:,:,0]<140)&(hair[:,:,1]<120)&(hair[:,:,2]<110)&(hair[:,:,3]>240);out[crack]=hair[crack]
 Image.fromarray(crack.astype('uint8')*255).save(R/f'masks/F{f}__generated_interior_crack_patch.png')
 notch=Image.new('L',base.size);ox=0 if f=='021' else -10;oy=0 if f=='021' else 4;npnts=[(1111,763),(1119,764),(1118,771),(1111,781)] if f=='021' else [(1112,774),(1121,774),(1119,783),(1112,783)];ImageDraw.Draw(notch).polygon(npnts,fill=255);nm=(np.array(notch)>0)&union&~gar&(out[:,:,3]<240)
 ny=np.clip(Y-15,0,H-1);nx=np.clip(X+43-ox,0,W-1);h=raw[ny,nx];nm&=(h[:,:,3]>240)&(h[:,:,0]<140)&(h[:,:,1]<120)&(h[:,:,2]>h[:,:,1]*.5);out[nm]=h[nm];Image.fromarray(nm.astype('uint8')*255).save(R/f'masks/F{f}__generated_notch_closure.png')

 changed=np.any(out!=a,axis=2);assert not np.any(changed&~union);assert not np.any(changed&gar)
 dest=R/f'candidates/S03a_F{f}.png'
 if dest.exists() and f=='021' and not (R/'diagnostics/F021_REJECTED_GENERATED_ROOT_KINKS.png').exists():shutil.copyfile(dest,R/'diagnostics/F021_REJECTED_GENERATED_ROOT_KINKS.png')
 Image.fromarray(out).save(dest);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j={'status':'PIXEL_COMPOSITE_TAIL_REVIEW_PENDING','method':'Coordinator approved original-pixel smooth free-tail deformation; unchanged whole head and roots; prior generated free-hair donor only extends previously occluded hair below shoulder before deformation','source_017_sha256':sha(R/'candidates/S03a_F017.png'),'generated_donor_sha256':sha(R/'raw/F021_tails_v1.png'),'candidate_sha256':sha(dest),'tail_maps':maps,'donor_records':records,'changed_pixels':int(changed.sum()),'changed_outside_tail_mask':int((changed&~union).sum()),'fixed_garment_changed':int((changed&gar).sum()),'head_face_eyes_mouth_neck_roots_exact_F017':True,'new_imagegen_calls':0};(R/f'qa/F{f}__pixel_tail_validation.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
# Actual same-scale sequence on both light and dark backgrounds.
for bg,name in [((239,239,232,255),'light'),((32,37,44,255),'dark')]:
 board=Image.new('RGB',(1460*3,490),'white');d=ImageDraw.Draw(board)
 for k,f in enumerate(['017','021','023']):
  i=Image.open(R/f'candidates/S03a_F{f}.png').convert('RGBA');flat=Image.alpha_composite(Image.new('RGBA',i.size,bg),i).convert('RGB');d.text((1460*k+10,10),f+' SAME ROOT / FREE TAIL PHASE',fill='black');board.paste(flat.crop((500,610,1230,830)).resize((1460,440)),(1460*k,40))
 board.save(R/f'qa/F017_F021_F023__pixel_tail_{name}.png')
