"""Explicitly authorized zero-call local retouch; real source art stays immutable.
Only off-axis nibs, the022 wrist join and the detached old wrist line may change.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent;OLD=PACK/'first36_gap_fill_001';S=8
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def poly_mask(points,size=(1672,941)):
 im=Image.new('L',(size[0]*S,size[1]*S));ImageDraw.Draw(im).polygon([(x*S,y*S) for x,y in points],fill=255);return np.array(im.resize(size,Image.Resampling.LANCZOS),float)/255

def curve(p):
 p=np.array(p,float);return np.array([(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3] for t in np.linspace(0,1,160)])
def line_mask(points,width=1.15):
 im=Image.new('L',(1672*S,941*S));ImageDraw.Draw(im).line([(round(x*S),round(y*S)) for x,y in points],fill=255,width=round(width*S));return np.array(im.resize((1672,941),Image.Resampling.LANCZOS),float)/255

def save(f,A,B,allowed,notes):
 delta=np.any(A!=B,axis=2);assert not np.any(delta&~allowed);im=Image.fromarray(B);out=P/f'S20_F{f:03}_cleanup_candidate.png';im.save(out);Image.fromarray((delta*255).astype('uint8')).save(P/f'F{f:03}_changed_pixels.png')
 bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);box=(775,328,860,399) if f in [12,15] else (895,385,1042,485);scale=8 if f in [12,15] else 6;bg.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.NEAREST).convert('RGB').save(P/f'F{f:03}_after_close.png');bg.convert('RGB').save(P/f'F{f:03}_after_full.png')
 # Before/after proof at identical scale and origin; no other pose is rendered.
 bb=Image.new('RGBA',im.size,'#bdc1c4');bb.alpha_composite(Image.fromarray(A));left=bb.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.NEAREST).convert('RGB');right=bg.crop(box).resize(left.size,Image.Resampling.NEAREST).convert('RGB');board=Image.new('RGB',(left.width*2,left.height),'#bdc1c4');board.paste(left,(0,0));board.paste(right,(left.width,0));board.save(P/f'F{f:03}_before_after.png')
 ys,xs=np.where(delta);return {'frame':f,'source':str((OLD/f'F{f:03}'/f'S20_F{f:03}_accepted.png').relative_to(PACK)),'source_sha256':sha(OLD/f'F{f:03}'/f'S20_F{f:03}_accepted.png'),'candidate':out.name,'candidate_sha256':sha(out),'changed_pixels':int(delta.sum()),'actual_change_bbox':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],'outside_allowed_RGBA_changes':0,'repair':notes}
rows=[]
for f in [12,15]:
 A=np.array(Image.open(OLD/f'F{f:03}'/f'S20_F{f:03}_accepted.png').convert('RGBA'));B=A.copy();yy,xx=np.indices(A.shape[:2]);x0,x1=800.5,(811.0 if f==12 else 810.0);y0,y1=(352.0,346.5) if f==12 else (352.5,347.0)
 # Trim only the duplicate wood horn above the actual hand boundary. The true
 # bamboo front segment x<=800 and its hard axis remain untouched.
 top=y0+(y1-y0)*(xx-x0)/(x1-x0);trim=(xx>=801)&(xx<=int(x1))&(yy>=340)&(yy<top-.4)
 # Keep rightmost actual knuckle: the off-axis nib narrows before this boundary.
 trim&=((xx<=807) if f==12 else (xx<=804));B[trim]=0
 # The isolated015 short tip is entirely in transparent space, far off T_H.
 if f==15:B[330:340,780:786]=0
 allowed=np.zeros(A.shape[:2],bool);allowed[339:354,800:812]=True
 if f==15:allowed[330:340,780:786]=True
 # Remove low alpha remainder only within the same explicit nib window.
 rows.append(save(f,A,B,allowed,'Remove off-axis short bamboo nib only;015 also remove isolated detached tip. Primary shaft, fingers and contact remain original pixels.'))
# 022: restore the new real palm heel below the hand, clearing the detached old
# source line. Rebuild only a24px wrist junction using existing real skin pixels.
f=22;A=np.array(Image.open(OLD/'F022/S20_F022_accepted.png').convert('RGBA'));B=A.copy();R=np.array(Image.open(OLD/'F022/same_raw_rightmost_transparent_column.png').convert('RGBA'));D=np.array(Image.open(PACK/'handoff_008_020_032_generation_002/F020/S20_F020_accepted.png').convert('RGBA'));yy,xx=np.indices(A.shape[:2])
ghost=(xx>=944)&(xx<970)&(yy>=456)&(yy<478);B[ghost]=R[ghost];q=ghost&(R[:,:,3]<=20);B[q]=0
up=curve([(964,418.0),(973,420.5),(976,426.5),(992,427.3)]);low=curve([(964,456.0),(971,458.1),(978,462.4),(992,462.7)])
shape=poly_mask(np.concatenate([up,low[::-1]],axis=0));inkmask=np.maximum(line_mask(up),line_mask(low));region=(xx>=964)&(xx<989)&(yy>=410)&(yy<478)
def nearest_material(arr,xmin):
 r,g,b=arr[:,:,:3].astype(float).transpose(2,0,1);valid=(arr[:,:,3]>200)&(r>185)&(g>135)&(b>95)&(r>g+10)&(g>b+4)&(xx>=xmin)&(xx<=1002)&(yy>=429)&(yy<=452)
 _,inds=distance_transform_edt(~valid,return_indices=True);return arr[inds[0],inds[1]].astype(float)
MR,MD=nearest_material(R,976),nearest_material(D,990);t=np.clip((xx-964)/24,0,1);t=t*t*(3-2*t);fill=MR*(1-t[:,:,None])+MD*t[:,:,None];fill[:,:,3]*=shape
# Boundary color is sampled from the existing original forearm outline.
samples=D[425:429,985:1000];use=(samples[:,:,3]>100)&(samples[:,:,0]<145)&(samples[:,:,1]<120);ink=np.median(samples[use,:3],axis=0);assert len(samples[use])>0
layer=Image.fromarray(np.clip(np.rint(fill),0,255).astype('uint8'));ed=np.zeros_like(A);ed[:,:,:3]=np.rint(ink).astype('uint8');ed[:,:,3]=np.rint(inkmask*255).astype('uint8');layer.alpha_composite(Image.fromarray(ed));L=np.array(layer)
# The24px patch meets unchanged real art at each side, without a vertical edge.
edge=np.minimum(np.clip((xx-964)/2,0,1),np.clip((989-xx)/2,0,1));w=edge[:,:,None];C=np.rint(B*(1-w)+L*w).astype('uint8');B[region]=C[region]
allowed=((xx>=943)&(xx<990)&(yy>=408)&(yy<479));assert np.array_equal(B[:,:943],A[:,:943]);assert np.array_equal(B[:,990:],A[:,990:]);rows.append(save(f,A,B,allowed,'Clear detached old wrist line using unchanged raw022 palm edge; blend only wrist junction from actual raw022 and locked020 internal skin, restore continuous top/lower contour. No finger or rod changes.'))
(P/'verification.json').write_text(json.dumps({'source_commit':'643be12444c9afd42a6ffd6686e97ed7b85dea15','image_model_calls':0,'raw_outputs':0,'F004_cloud_calls':0,'candidates_only':True,'frames':rows,'full_film_or_scene_render':False,'prior_sources_modified':False},ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False,indent=2))
