from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,map_coordinates,median_filter

F=Path(__file__).resolve().parent;P=F.parent
src=P/'next_F067_candidate_input_001/generation_001/F067_native_child_locked_G_candidate.png'
ref=P/'F064_root_occlusion_cleanup_zero_call_001/F064_proximal_roots_continuous_candidate.png'
A=np.array(Image.open(src).convert('RGBA'));REF=np.array(Image.open(ref).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
yellow=(A[:,:,3]>120)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>630)&(yy<710)
hem=np.full(W,np.nan)
for x in range(540,835):
    ys=np.flatnonzero(yellow[:,x])
    if not len(ys):continue
    last=int(ys.max());q=np.arange(last,min(last+5,H));edge=int(q[np.argmin(r[q,x]+g[q,x]+b[q,x])])
    if edge+1<H and r[edge+1,x]<180 and b[edge+1,x]<g[edge+1,x]*.65:edge+=1
    hem[x]=edge
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]);med=median_filter(hem,size=7);hem[hem-med>=4]=med[hem-med>=4]
root_roi=(xx>=575)&(xx<=770)&(yy>=650)&(yy<736)
old_flesh=(r>170)&(g>100)&(b>g*.65)&(r>g+15)
garment=root_roi&(yy<=hem[xx])&(A[:,:,3]>4)&~old_flesh

# Split only in the real inter-leg air; the shoe split follows its front edge.
split=np.full(H,653.,float)
for y in range(700,851):
    xs=np.flatnonzero(A[y,560:800,3]>32)+560
    pieces=[q for q in np.split(xs,np.where(np.diff(xs)>1)[0]+1) if len(q)>12]
    if len(pieces)>=2:split[y]=(pieces[-2][-1]+pieces[-1][0])/2
for y in range(650,700):split[y]=split[700]
shoe_y=[850,860,870,878,885,890,897,904,935]
shoe_x=[695,680,664,650,642,636,628,620,620]
split[851:]=np.interp(np.arange(851,H),shoe_y,shoe_x)
near_mask=(A[:,:,3]>0)&(xx>=split[yy])&(xx<835)&(yy>=650)&(yy>hem[xx])
near=np.zeros_like(A);near[near_mask]=A[near_mask]
ids,n=label(near[:,:,3]>4);sizes=np.bincount(ids.ravel());main=ids==np.argmax(sizes[1:])+1;near[:,:,3][~main]=0
near_mask=(near[:,:,3]>0)
Image.fromarray(near).save(F/'067_native_complete_near_leg_shoe_only.png')
Image.fromarray(np.uint8(near_mask)*255).save(F/'original_near_leg_semantic_mask.png')

reference_near=np.array(Image.open(P/'F064_support_registration_zero_call_001/near_one_rigid_registered_leg_shoe.png').convert('RGBA'))
def sole(a):
    rr,gg,bb=a[:,:,:3].astype(float).transpose(2,0,1)
    red=(a[:,:,3]>128)&(rr>130)&(rr>gg*1.5)&(rr>bb*1.5)&(yy>895)
    xs=xx[red];lo,hi=int(xs.min()),int(xs.max());pts=[]
    for x in [lo+2,hi-2]:
        ys=np.flatnonzero((a[:,x,3]>128)&(np.arange(H)>890));pts.append([x,float(ys.max())])
    bottom=[]
    for x in range(lo,hi+1):
        ys=np.flatnonzero((a[:,x,3]>128)&(np.arange(H)>890))
        if len(ys):bottom.append([x,float(ys.max())])
    return np.array(pts),np.array(bottom)
sp,sc=sole(near);tp,tc=sole(reference_near)
cs=sp.mean(0);ct=tp.mean(0);u,s,vt=np.linalg.svd((sp-cs).T@(tp-ct));R=vt.T@u.T
if np.linalg.det(R)<0:vt[-1]*=-1;R=vt.T@u.T
t=ct-R@cs
# Match the actual lower bearing line without scaling the native shoe shape.
transformed_curve=(R@sc.T).T+t;ground_delta=float(np.quantile(tc[:,1],.9)-np.quantile(transformed_curve[:,1],.9));t[1]+=ground_delta
inv=R.T;offset=-inv@t;aff=(inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1])
registered=np.array(Image.fromarray(near).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC))
Image.fromarray(registered).save(F/'067_near_whole_leg_one_rigid_registration.png')

# Finish the proximal connection in this package. Knees/lower leg/shoe are not
# rescaled or deformed; this material comes only from the registered067 leg.
donor_y=736;xs=np.flatnonzero(registered[donor_y,:,3]>16);lo,hi=int(xs.min()),int(xs.max())
orig_y=690;source_pieces=[];xs0=np.flatnonzero(A[orig_y,560:800,3]>32)+560
source_pieces=[q for q in np.split(xs0,np.where(np.diff(xs0)>1)[0]+1) if len(q)>12]
upper_left=float(source_pieces[-1][0]);upper_right=float(source_pieces[-1][-1])
def curve(y,a,b):
    q=np.clip((y-686)/(736-686),0,1);q=q*q*(3-2*q);return a+(b-a)*q
cy,cx=np.indices((86,195));my=650+cy;mx=575+cx;left=curve(my,upper_left,lo);right=curve(my,upper_right,hi)
samplex=np.clip(lo+(mx-left)/(right-left)*(hi-lo),lo,hi)
rgb=np.stack([map_coordinates(registered[:,:,k].astype(float),[np.full_like(samplex,float(donor_y)),samplex],order=1,mode='nearest') for k in range(3)],2)
rgb-=np.clip((714-my)/30,0,1)[:,:,None]*np.array([1.,5.,5.])
maskim=Image.new('L',(195*8,86*8));draw=ImageDraw.Draw(maskim);rows=np.arange(650,740,dtype=float)
points=[((float(curve(y,upper_left,lo))-575)*8,(y-650)*8) for y in rows]+[((float(curve(y,upper_right,hi))-575)*8,(y-650)*8) for y in rows[::-1]]
draw.polygon(points,fill=255);cap=np.zeros_like(A);cap[650:736,575:770,:3]=np.rint(rgb).clip(0,255).astype('uint8');cap[650:736,575:770,3]=np.array(maskim.resize((195,86),Image.Resampling.LANCZOS))
# One continuous proximal silhouette, not two alpha-blended cut contours.
# At the native join it reaches the registered contour and material exactly.
finished=cap.copy();finished[736:]=registered[736:]
Image.fromarray(finished).save(F/'067_registered_near_leg_with_proximal_connection.png')
Image.fromarray(cap).save(F/'same067_near_proximal_skin_connection_only.png')
base=A.copy();base[near_mask]=0
# Complete root context: remove the old near-root residues, retain the far leg
# as the original native under-layer, then put the actual yellow hem in front.
far_root=(A[:,:,3]>0)&root_roi&(xx<split[yy])&~garment
base[root_roi&~garment]=0;base[far_root]=A[far_root]
out=Image.alpha_composite(Image.fromarray(base),Image.fromarray(finished));B=np.array(out);B[garment]=A[garment]
# Restore every unrelated upper-body/hand/rod/grandma pixel exactly.
allow=near_mask|(finished[:,:,3]>0)|root_roi;B[~allow]=A[~allow];B[yy<650]=A[yy<650];B[:,835:]=A[:,835:]
final=F/'F067_near_support_and_root_closed_candidate.png';Image.fromarray(B).save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96)
for name,box,scale in [('actual_under_hem',(575,660,760,755),3),('actual_support',(480,800,795,935),2)]:
    c=bg.crop(box).convert('RGB');c.save(F/(name+'_1x.png'));c.resize((c.width*scale,c.height*scale),Image.Resampling.NEAREST).save(F/(name+f'_{scale}x.png'))
board=Image.new('RGB',(630,135),'#bdc1c4')
for i,a in enumerate([REF,B]):
    q=Image.new('RGBA',(W,H),'#bdc1c4');q.alpha_composite(Image.fromarray(a));board.paste(q.crop((480,800,795,935)).convert('RGB'),(i*315,0))
board.save(F/'064_left_repaired067_right_support_same_scale_1x.png')
assert np.array_equal(finished[736:],registered[736:]);assert np.array_equal(B[yy<650],A[yy<650]);assert np.array_equal(B[:,835:],A[:,835:]);assert np.array_equal(B[garment],A[garment])
uncovered_far=(A[:,:,3]>0)&~near_mask&(finished[:,:,3]==0)&~root_roi
assert np.array_equal(B[uncovered_far],A[uncovered_far])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'ONE_ZERO_CALL_F067_NATIVE_NEAR_WHOLE_LEG_RIGID_SUPPORT_AND_ROOT_CLOSURE_ASTRA_GATE_PENDING','image_calls':0,'source067_file':str(src),'source067_sha256':sha(src),'reference064_file':str(ref),'reference064_sha256':sha(ref),'native_near_source_sha256':sha(F/'067_native_complete_near_leg_shoe_only.png'),'support_anchors_source':sp.tolist(),'support_anchors_reference064':tp.tolist(),'one_final_near_R':R.tolist(),'one_final_near_translation_xy':t.tolist(),'rotation_degrees':math.degrees(math.atan2(R[1,0],R[0,0])),'scale':1,'single_native_near_leg_image_resampling':1,'final_bearing_anchor_residual_px':np.linalg.norm((R@sp.T).T+t-tp,axis=1).tolist(),'lower_bearing_quantile_match_vertical_adjustment_px':ground_delta,'proximal_repair_only_above_y736':True,'registered_near_all_y736_plus_RGBA_exact':True,'no_old064_leg_or_shoe_pixels_pasted':True,'far_leg_no_transform_original_native_under_layer':True,'unoccluded_far_RGBA_exact':True,'original_upper_skirt_foreground_hands_T_rods_grandma_fixed':True,'final_png_sha256':sha(final),'adopted':False,'propagated':False}
(F/'status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
