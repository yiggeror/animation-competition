"""Same-raw costume semantics only: real collars, dense dots, whole real sandals."""
from pathlib import Path
import math,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation,distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2]
S=np.array(Image.open(PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png').convert('RGBA'));V=np.array(Image.open(ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png').convert('RGB'));H,W=S.shape[:2];yy,xx=np.indices((H,W))
def poly(points,shape=(W,H)):
 im=Image.new('L',shape);ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def cloth_mask(A):
 r,g,b=A[:,:,:3].astype(float).transpose(2,0,1);y=(A[:,:,3]>150)&(r>160)&(g>105)&(r>g+12)&(b<g*.68)&(xx>470)&(xx<735)&(yy>340)&(yy<735);ids,n=label(y);sizes=np.bincount(ids.ravel());keep=np.flatnonzero(sizes>100);keep=keep[keep!=0];return binary_fill_holes(np.isin(ids,keep))
def white_dots(A,C):
 r,g,b=A[:,:,:3].astype(float).transpose(2,0,1);m=C&(A[:,:,3]>150)&(r>225)&(g>220)&(b>185)&((np.max(A[:,:,:3],2).astype(float)-np.min(A[:,:,:3],2))<55);ids,n=label(m);items=[]
 for k in range(1,n+1):
  ys,xs=np.where(ids==k)
  if 9<=len(xs)<=190 and max(xs.max()-xs.min(),ys.max()-ys.min())<=19:items.append((k,float(xs.mean()),float(ys.mean()),len(xs)))
 return ids,items
SC=cloth_mask(S);sid,sd=white_dots(S,SC);density=len(sd)/max(1,SC.sum());radius=float(np.median([math.sqrt(v[3]/math.pi) for v in sd]));spacing=math.sqrt(2/(math.sqrt(3)*density))
def restore_dots(A,frame):
 B=A.copy();C=cloth_mask(A);ids,dots=white_dots(A,C);old=np.isin(ids,[v[0] for v in dots]);old=binary_dilation(old,iterations=1)&C
 # Local harmonic fill uses only this same raw's surrounding yellow material.
 for k,cx,cy,area in dots:
  ys,xs=np.where(ids==k);x0=max(0,int(xs.min())-5);x1=min(W,int(xs.max())+6);y0=max(0,int(ys.min())-5);y1=min(H,int(ys.max())+6);mask=old[y0:y1,x0:x1];block=B[y0:y1,x0:x1,:3].astype(float);known=C[y0:y1,x0:x1]&~mask
  if not known.any():continue
  _,idx=distance_transform_edt(~known,return_indices=True);block[mask]=block[idx[0][mask],idx[1][mask]]
  for _ in range(45):
   ave=(np.roll(block,1,0)+np.roll(block,-1,0)+np.roll(block,1,1)+np.roll(block,-1,1))/4;block[mask]=ave[mask]
  B[y0:y1,x0:x1,:3][mask]=np.uint8(np.clip(block[mask],0,255))
 # Repeat one true032 dot as a fabric stamp; no new character geometry.
 def circular(v):
  ys,xs=np.where(sid==v[0]);w=xs.max()-xs.min()+1;h=ys.max()-ys.min()+1;return abs(v[3]/(w*h)-math.pi/4)+abs(math.log(w/h))
 pick=min([v for v in sd if v[3]>30],key=circular);m=sid==pick[0];white_material=np.median(S[m,:3],axis=0)
 scale=1 if frame==36 else .91817704063;step=spacing*scale*(.94 if frame==36 else 1);rad=radius*scale;diam=max(5,round(rad*2+2));ah=Image.new('L',(diam*4,diam*4));ImageDraw.Draw(ah).ellipse((4,4,diam*4-5,diam*4-5),fill=255);stampim=Image.new('RGBA',(diam,diam),tuple(int(v) for v in white_material)+(255,));stampim.putalpha(ah.resize((diam,diam),Image.Resampling.LANCZOS));safe=distance_transform_edt(C)>rad+2;canvas=Image.fromarray(B);count=0
 for row,y in enumerate(np.arange(348,731,step*.8660254)):
  for x in np.arange(480+(row%2)*step/2,735,step):
   xi,yi=round(x),round(y)
   if not safe[yi,xi]:continue
   st=np.array(stampim);factor=float(np.clip(np.mean(B[max(0,yi-2):yi+3,max(0,xi-2):xi+3,:3])/150,.80,1.02));st[:,:,:3]=np.clip(st[:,:,:3].astype(float)*factor,0,255).astype('uint8');sx=xi-st.shape[1]//2;sy=yi-st.shape[0]//2;ink=np.max(A[sy:sy+st.shape[0],sx:sx+st.shape[1],:3],2)<145;st[ink]=0;canvas.alpha_composite(Image.fromarray(st),(sx,sy));count+=1
 B=np.array(canvas);B[:,:,3]=A[:,:,3];return B,{'old_dots_removed':len(dots),'new_round_white_dots':count,'cloth_area_px':int(C.sum()),'032_reference_dots':len(sd),'032_dot_density_per_pixel':density,'real_white_pigment_source_center':[pick[1],pick[2]],'projected_spacing_px':step}
def rgb_extract(roi,kind):
 h,w=V.shape[:2];y,x=np.indices((h,w));x0,y0,x1,y1=roi;region=(x>=x0)&(x<x1)&(y>=y0)&(y<y1);sat=V.max(2).astype(int)-V.min(2).astype(int)
 if kind=='shoe':core=region&((sat>17)|(V.min(2)<120));core=binary_fill_holes(core)
 else:
  white=region&(V.min(2)>227)&(sat<42);ids,n=label(white);sizes=np.bincount(ids.ravel());ks=np.flatnonzero(sizes>45);ks=ks[ks!=0];core=binary_fill_holes(np.isin(ids,ks))
 edge=binary_dilation(core,iterations=1)&region;out=np.zeros((h,w,4),np.uint8);out[:,:,:3]=V;out[:,:,3]=edge*255;return out
front_collar=rgb_extract((260,240,380,294),'collar');side_collar=rgb_extract((730,233,818,301),'collar');side_shoe=rgb_extract((695,873,860,969),'shoe')
near_mask=poly([(535,853),(562,852),(582,859),(584,878),(597,889),(623,895),(632,904),(636,911),(635,916),(626,920),(601,925),(538,919),(522,908),(523,884)]);near_shoe=np.zeros_like(S);near_shoe[near_mask]=S[near_mask]
def similarity(layer,p0,p1,q0,q1):
 p0,p1,q0,q1=[np.array(p,float) for p in [p0,p1,q0,q1]];u=p1-p0;v=q1-q0;c=complex(*v)/complex(*u);a,b=c.real,c.imag;Q=np.array([[a,-b],[b,a]]);t=q0-Q@p0;inv=np.linalg.inv(Q);args=tuple(np.column_stack((inv,-inv@t)).ravel());out=np.array(Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,args,Image.Resampling.BICUBIC));return out,{'scale':abs(c),'rotation_degrees':math.degrees(math.atan2(b,a)),'matrix_2x3':np.column_stack((Q,t)).tolist(),'source_ankle_and_toe':[p0.tolist(),p1.tolist()],'target_ankle_and_toe':[q0.tolist(),q1.tolist()]}
records=[];results=[]
for f,path in [(36,PACK/'B04_B05_generation_002/F036/S20_F036_accepted.png'),(39,PACK/'F039_head_neck_repair_001/S20_F039_head_neck_accepted.png')]:
 A=np.array(Image.open(path).convert('RGBA'));B,dotinfo=restore_dots(A,f)
 if f==39:scale=.9;t=[316.3,142.4];donor=front_collar
 else:scale=.95;t=[626-778*.95,350-256*.95];donor=side_collar
 collar=np.array(Image.fromarray(donor).transform((W,H),Image.Transform.AFFINE,(1/scale,0,-t[0]/scale,0,1/scale,-t[1]/scale),Image.Resampling.BICUBIC));ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);skin=(A[:,:,3]>30)&(ar>170)&(ag>110)&(ab>ag*.72)&(ar>ag+9);hair=(A[:,:,3]>0)&(ar<140)&(ag<120)&(yy<375);collar[skin|hair]=0
 B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(collar)))
 configs=([('far',side_shoe,[760,925],[846,956],[654,866],[733,902],862,(612,860,743,914)),('near',near_shoe,[556,880],[633,918],[566,878],[653,916],874,(530,872,660,925))] if f==36 else [('far',side_shoe,[760,925],[846,956],[674,855],[733,902],852,(640,850,744,910)),('near',near_shoe,[556,880],[633,918],[556,866],[613,916],862,(523,856,624,925))])
 # Clear both obsolete closed shoes BEFORE laying either real sandal; this avoids
 # erasing the far sandal when the near shoe's old rectangle overlaps it.
 for role,donor,p0,p1,q0,q1,cut,box in configs:
  x0,y0,x1,y1=box;old=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1);red=(ar>ag+25)&(ar>ab+25)&(ar>110);sole=(np.max(A[:,:,:3],2)<155);clear=old&((red|sole)|(yy>=cut+8));B[clear]=0
 shoes=[]
 for role,donor,p0,p1,q0,q1,cut,box in configs:
  L,tr=similarity(donor,p0,p1,q0,q1);lr,lg,lb=L[:,:,:3].astype(float).transpose(2,0,1);shoe_material=(lr>lg+25)&(lr>lb+25)&(lr>110);outline=binary_dilation(shoe_material&(L[:,:,3]>150),iterations=1);L[(yy<cut)&~outline]=0
  donor_skin=(L[:,:,3]>150)&(lr>180)&(lg>120)&(lb>lg*.72)&~shoe_material;qx,qy=q0;patch=A[max(0,cut-18):cut-2,max(0,int(qx)-10):int(qx)+11];pr,pg,pb=patch[:,:,:3].astype(float).transpose(2,0,1);ps=(patch[:,:,3]>150)&(pr>180)&(pg>120)&(pb>pg*.72)
  if ps.any() and donor_skin.any():
   delta=np.median(patch[:,:,:3][ps],axis=0)-np.median(L[:,:,:3][donor_skin],axis=0);L[:,:,:3][donor_skin]=np.clip(L[:,:,:3][donor_skin].astype(float)+delta,0,255).astype('uint8')
  B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(L)));shoes.append({'role':role,'real_donor':'locked032 near sandal' if role=='near' else 'approvedv4 full side sandal','one_whole_sandal_similarity':tr,'native_shin_skin_kept_above_y':cut})
 out=P/f'S20_F{f:03}_costume_corrected.png';Image.fromarray(B).save(out);bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));results.append(bg.convert('RGB'));change=np.any(B!=A,2);Image.fromarray((change*255).astype('uint8')).convert('RGB').save(P/f'F{f:03}_material_change_mask.png')
 # All hands/arms and heads outside the collar transition remain the same raw pixels.
 assert np.array_equal(B[:335],A[:335]);assert np.array_equal(B[395:520,710:],A[395:520,710:]);assert np.array_equal(B[:,900:],A[:,900:])
 records.append({'frame':f,'source':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':out.name,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dot_restore':dotinfo,'real_collar_source':'approved v4 front' if f==39 else 'approved v4 profile','collar_registration':{'scale':scale,'translation':t},'sandals':shoes,'new_image_calls':0,'head_above335_RGBA_changes':0,'arm_grip_and_G_x710plus_RGBA_changes':0})
font=ImageFont.truetype(str(ROOT/'assets/fonts/NotoSansSC-VF.ttf'),22);board=Image.new('RGB',(1320,960),'#bdc1c4');d=ImageDraw.Draw(board)
for i,(f,im) in enumerate(zip([36,39],results)):
 crop=im.crop((480,160,900,935)).resize((504,930),Image.Resampling.LANCZOS);board.paste(crop,(i*660+15,30));d.text((i*660+15,3),f'F{f:03} 服装零调用修后 · 1.2倍同尺',font=font,fill='#263743')
board.save(P/'036_039_costume_corrected_side_by_side.png');(P/'source_and_registration.json').write_text(json.dumps({'new_image_calls':0,'same_raw_material_only':True,'frames':records},ensure_ascii=False,indent=2)+'\n');print(json.dumps(records,ensure_ascii=False))
