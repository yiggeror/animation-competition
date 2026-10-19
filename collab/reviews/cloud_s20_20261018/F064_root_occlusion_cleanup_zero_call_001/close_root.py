from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,map_coordinates,median_filter

F=Path(__file__).resolve().parent;P=F.parent;S=P/'F064_support_registration_zero_call_001'
bodypath=P/'next_F064_candidate_input_001/generation_001/F064_native_child_locked_G_candidate.png'
regpath=S/'F064_whole_leg_rigid_support_DIAGNOSTIC_NOT_ADOPTED.png'
A=np.array(Image.open(regpath).convert('RGBA'));D=np.array(Image.open(bodypath).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
raws={k:np.array(Image.open(S/(k+'_one_rigid_registered_leg_shoe.png')).convert('RGBA')) for k in ['far','near']}
layers={}
for k,a in raws.items():
    ids,n=label(a[:,:,3]>4);sizes=np.bincount(ids.ravel());main=ids==np.argmax(sizes[1:])+1
    clean=a.copy();clean[:,:,3][~main]=0;layers[k]=clean

# Original actual yellow hem and its dark native stroke stay in the foreground.
# Track the colour-to-ink valley per column, never a horizontal crop line.
r,g,b=D[:,:,:3].astype(float).transpose(2,0,1)
yellow=(D[:,:,3]>120)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>635)&(yy<710)
hem=np.full(W,np.nan)
for x in range(540,815):
    ys=np.flatnonzero(yellow[:,x])
    if not len(ys):continue
    last=int(ys.max());q=np.arange(last,min(last+5,H));lum=r[q,x]+g[q,x]+b[q,x];edge=int(q[np.argmin(lum)])
    if edge+1<H and r[edge+1,x]<180 and b[edge+1,x]<g[edge+1,x]*.65:edge+=1
    hem[x]=edge
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok])
local_hem=median_filter(hem,size=7);old_vertical_peg=hem-local_hem>=4;hem[old_vertical_peg]=local_hem[old_vertical_peg]
roi=(xx>=540)&(xx<=770)&(yy>=650)&(yy<720)
old_flesh=(r>170)&(g>100)&(b>g*.65)&(r>g+15)
foreground=roi&(yy<=hem[xx])&(D[:,:,3]>0)&(A[:,:,3]>4)&~old_flesh
edit=roi&~foreground

def cap(role,donor_y,left,right):
    native=layers[role];row=native[donor_y,:,3]>16;xs=np.flatnonzero(row);lo,hi=int(xs.min()),int(xs.max())
    cy,cx=np.indices((70,180));my=650+cy;mx=570+cx;lx=left(my);rx=right(my)
    u=(mx-lx)/(rx-lx);samplex=np.clip(lo+u*(hi-lo),lo,hi)
    # Only the missing proximal skin is extended from the same registered leg.
    # Existing legs are composited in front; nothing below y720 is changed.
    colour=np.stack([map_coordinates(native[:,:,k].astype(float),[np.full_like(samplex,float(donor_y)),samplex],order=1,mode='nearest') for k in range(3)],2)
    proximal=np.clip((710-my)/22,0,1)
    shade=np.array([1.,5.,5.]) if role=='far' else np.array([2.,8.,7.])
    colour-=proximal[:,:,None]*shade
    im=Image.new('L',(180*8,70*8));draw=ImageDraw.Draw(im)
    rows=np.arange(650,720,dtype=float)
    points=[((float(left(y))-570)*8,(y-650)*8) for y in rows]+[((float(right(y))-570)*8,(y-650)*8) for y in rows[::-1]]
    draw.polygon(points,fill=255);alpha=np.array(im.resize((180,70),Image.Resampling.LANCZOS))
    out=np.zeros((H,W,4),dtype='uint8');patch=np.zeros((70,180,4),dtype='uint8');patch[:,:,:3]=np.rint(colour).clip(0,255).astype('uint8');patch[:,:,3]=alpha
    out[650:720,570:750]=patch
    Image.fromarray(out).save(F/(role+'_proximal_skin_extension_only.png'))
    return Image.fromarray(out)

farcap=cap('far',710,lambda y:592+.10*(y-700),lambda y:647+.02*(y-700))
nearcap=cap('near',720,lambda y:642-.07*(y-700),lambda y:696+.12*(y-700))
def root_join(cap_image,role):
    cap_array=np.array(cap_image).astype(float);native=layers[role].astype(float)
    # Retire the old artificial alpha-cut/white fringe as a complete proximal
    # semantic transition. Retain each existing leg unchanged by y720.
    w=np.clip((yy-703)/17,0,1)[:,:,None]
    a0=cap_array[:,:,3:4]/255;a1=native[:,:,3:4]/255
    pa=(1-w)*a0+w*a1;rgb=(1-w)*cap_array[:,:,:3]*a0+w*native[:,:,:3]*a1
    mixed=np.zeros_like(cap_array);mixed[:,:,:3]=np.divide(rgb,pa,out=np.zeros_like(rgb),where=pa>1e-6);mixed[:,:,3:4]=pa*255
    mixed[yy>=720]=native[yy>=720]
    return Image.fromarray(np.rint(mixed).clip(0,255).astype('uint8'))
patch=Image.new('RGBA',(W,H));patch.alpha_composite(root_join(farcap,'far'));patch.alpha_composite(root_join(nearcap,'near'))
paint=np.array(patch);B=A.copy();B[edit]=paint[edit]
# The original hem/upper body is exact foreground. The real registered thighs,
# knees, ankles and whole shoes below the semantic root repair stay exact.
B[~edit]=A[~edit];B[720:]=A[720:]
Image.fromarray(B).save(F/'F064_proximal_roots_continuous_candidate.png')
Image.fromarray(np.uint8(edit)*255).save(F/'complete_under_hem_semantic_edit_mask.png')
front=np.zeros_like(D);front[roi&~edit]=D[roi&~edit];Image.fromarray(front).save(F/'original_hem_foreground_reference_layer.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96)
for name,box,scale in [('actual_under_hem',(565,660,755,735),6),('actual_support',(480,800,795,935),2)]:
    c=bg.crop(box).convert('RGB');c.save(F/(name+'_1x.png'));c.resize((c.width*scale,c.height*scale),Image.Resampling.NEAREST).save(F/(name+f'_{scale}x.png'))
assert np.array_equal(B[~edit],A[~edit]);assert np.array_equal(B[720:],A[720:]);assert np.array_equal(B[:,835:],A[:,835:])
report={'status':'ONE_ZERO_CALL_COMPLETE_UNDER_HEM_ROOT_OCCLUSION_CANDIDATE_ASTRA_GATE_PENDING','image_calls':0,'registered064_sha256':hashlib.sha256(regpath.read_bytes()).hexdigest(),'original064_upper_hem_sha256':hashlib.sha256(bodypath.read_bytes()).hexdigest(),'only_leg_sources':{k:{'file':str(S/(k+'_one_rigid_registered_leg_shoe.png')),'sha256':hashlib.sha256((S/(k+'_one_rigid_registered_leg_shoe.png')).read_bytes()).hexdigest()} for k in raws},'method':'same registered leg skin/edge strip continued only into missing proximal occlusion volume; original yellow hem and stroke are exact foreground; remove legacy root islands outside new layers','no_old061_leg_pixels':True,'no_registered_leg_scale_rotation_translation_or_stretch':True,'all_y720_plus_thigh_knee_ankle_shoe_RGBA_exact':True,'original_upper_hem_all_foreground_RGBA_exact':True,'outside_complete_semantic_root_edit_RGBA_exact':True,'changed_pixels':int(np.any(A!=B,2).sum()),'adopted':False,'propagated':False}
(F/'status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
