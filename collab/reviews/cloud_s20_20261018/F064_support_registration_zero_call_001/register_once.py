from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import maximum_filter1d

F=Path(__file__).resolve().parent;P=F.parent
sp=P/'next_F064_candidate_input_001/generation_001/F064_native_child_locked_G_candidate.png'
rp=P/'next_F061_candidate_input_001/generation_001/F061_native_child_locked_G_candidate.png'
A=np.array(Image.open(sp).convert('RGBA'));REF=np.array(Image.open(rp).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
yellow=(A[:,:,3]>128)&(r>170)&(g>100)&(b<g*.6)&(yy>640)&(yy<710)&(xx<835)
hem=np.full(W,np.nan)
for x in range(540,815):
    ys=np.flatnonzero(yellow[:,x])
    if len(ys):hem[x]=ys.max()
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]);hem=maximum_filter1d(hem,size=3)+3
legs=(A[:,:,3]>0)&(xx<835)&(yy>hem[xx])
near_poly=Image.new('L',(W,H));ImageDraw.Draw(near_poly).polygon([(680,660),(765,660),(765,815),(785,860),(790,935),(630,935),(630,893),(641,879),(667,865),(690,850),(704,835),(690,785),(675,735)],fill=255)
near=legs&(np.array(near_poly)>0);far=legs&~near
Image.fromarray(np.uint8(far)*255).save(F/'native_far_whole_leg_mask.png');Image.fromarray(np.uint8(near)*255).save(F/'native_near_whole_leg_mask.png')

def bearing(a,lo,hi):
    pts=[]
    for x in range(lo,hi+1):
        ys=np.flatnonzero((a[:,x,3]>128)&(np.arange(H)>875))
        if len(ys):pts.append([x,float(ys.max())])
    return np.median(np.array(pts),axis=0)

regions={'far':{'source':[(536,559),(617,633)],'reference':[(522,545),(601,611)]},'near':{'source':[(652,675),(752,771)],'reference':[(625,648),(710,731)]}}
outlayers=[];receipts=[]
for role,mask in [('far',far),('near',near)]:
    spec=regions[role];src=np.array([bearing(A,*z) for z in spec['source']]);dst=np.array([bearing(REF,*z) for z in spec['reference']])
    cs=src.mean(0);ct=dst.mean(0);u,s,vt=np.linalg.svd((src-cs).T@(dst-ct));R=vt.T@u.T
    if np.linalg.det(R)<0:vt[-1]*=-1;R=vt.T@u.T
    t=ct-R@cs;pred=(R@src.T).T+t
    layer=np.zeros_like(A);layer[mask]=A[mask];Image.fromarray(layer).save(F/(role+'_native_complete_visible_leg_shoe.png'))
    inv=R.T;offset=-inv@t;aff=(inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1])
    transformed=Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC)
    transformed.save(F/(role+'_one_rigid_registered_leg_shoe.png'));outlayers.append(transformed)
    receipts.append({'role':role,'source_bearing_points':src.tolist(),'reference061_bearing_points':dst.tolist(),'bearing_centroid_displacement_xy':(ct-cs).tolist(),'one_final_rigid_R':R.tolist(),'translation_xy':t.tolist(),'rotation_degrees':math.degrees(math.atan2(R[1,0],R[0,0])),'scale':1,'bearing_residual_px':np.linalg.norm(pred-dst,axis=1).tolist(),'image_resamplings':1,'no_knee_ankle_or_shoe_cut':True})
base=A.copy();base[legs]=0
out=Image.new('RGBA',(W,H));out.alpha_composite(outlayers[0]);out.alpha_composite(outlayers[1]);out.alpha_composite(Image.fromarray(base));B=np.array(out)
freeze_upper=yy<=hem[xx];B[freeze_upper]=A[freeze_upper];B[:,835:]=A[:,835:];out=Image.fromarray(B)
Image.fromarray(B).save(F/'F064_whole_leg_rigid_support_DIAGNOSTIC_NOT_ADOPTED.png')
gray=Image.new('RGBA',(W,H),'#bdc1c4');gray.alpha_composite(out);gray.convert('RGB').save(F/'actual_registered_full_DIAGNOSTIC.jpg',quality=96)
support=Image.new('RGB',(1260,270),'#bdc1c4')
for i,arr in enumerate([REF,B]):
    bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(arr));support.paste(bg.crop((480,800,795,935)).convert('RGB').resize((630,270),Image.Resampling.NEAREST),(i*630,0))
support.save(F/'061_left_registered064_right_support_same_scale_2x.png')
gray.crop((565,665,755,735)).resize((1140,420),Image.Resampling.NEAREST).convert('RGB').save(F/'actual_under_hem_join_6x_DIAGNOSTIC.png')
assert np.array_equal(B[yy<=hem[xx]],A[yy<=hem[xx]])
assert np.array_equal(B[:,835:],A[:,835:])
gaps=[]
for x in range(600,631):
    first=int(math.floor(hem[x]))+1;ys=np.flatnonzero((B[first:735,x,3]>128))
    if len(ys):gaps.append(int(ys[0]))
report={'status':'RIGID_SUPPORT_REGISTERED_BUT_VISIBLE_UNDER_HEM_ROOT_GAP_NOT_NATURAL_NOT_ADOPTABLE','source064_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'reference061_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'image_calls':0,'registrations':receipts,'far_under_hem_gap_px_max':max(gaps),'far_under_hem_gap_px_median':float(np.median(gaps)),'source_legs_removed_only_below_original_skirt_hem':True,'source_upper_body_skirt_arms_T_rods_grandma_RGBA_unchanged':True,'leg_layers_native_only_no_old061_leg_or_shoe_paste':True,'no_scaling_stretching_or_root_skin_fabrication':True,'conclusion':'foot support can be registered rigidly, but native far-leg top moves below fixed skirt hem and exposes an unpainted root gap; no natural join under current constraints','adopted':False,'propagated':False}
(F/'registration_receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipts,ensure_ascii=False,indent=2))
