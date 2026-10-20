"""Receive sole native F128. One similarity for whole actual native upper.

No white-mask clipping, independent palm/head moves, rod cleanup or native
shape repair. Preserve generated painted guides so the actual gate sees them.
"""
from pathlib import Path
import json,hashlib,math,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening,binary_dilation,median_filter,label,map_coordinates
F=Path(__file__).resolve().parent; I=F.parent; P=I.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'raw_original.png'
assert sha(raw)=='4245be9d5e57736d268c39a0bb4227212a64853013d5ce0ec36257c9b050080a'
R=np.array(Image.open(raw).convert('RGBA')); H,W=R.shape[:2]; assert (W,H)==(1672,941)
manifest=json.loads((I/'INPUT_MANIFEST.json').read_text())
A=np.array(Image.open(manifest['source120']).convert('RGBA'))
assert sha(Path(manifest['source120']))==manifest['source120_sha256']
yy,xx=np.indices((H,W)); r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)
# Trace the real native garment/skin boundary only where generated legs join.
# The complete head, both arms and ALL actual skirt folds outside this lower
# corridor are retained, regardless of technical white-domain silhouette.
yellow=(R[:,:,3]>180)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>500)&(yy<740)
core=binary_opening(yellow,iterations=2); hem=np.full(W,np.nan)
for x in range(650,1250):
    ys=np.flatnonzero(core[:,x])
    if not len(ys):continue
    last=int(ys.max()); q=np.flatnonzero(yellow[last:min(last+10,H),x])
    if len(q):last+=int(q.max())
    q=np.arange(last,min(last+5,H)); q=q[R[q,x,3]>20]
    if len(q):last=int(q[np.argmin(r[q,x]+g[q,x]+b[q,x])])
    hem[x]=last
ok=np.isfinite(hem); assert ok.sum()>480
hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]); hem=median_filter(hem,size=3)
ownership=~((yy>500)&(yy>hem[xx])&(xx<960))
cc,_=label((R[:,:,3]>24)&ownership); girl=int(cc[350,760]); assert girl>0
keep=binary_dilation(cc==girl,iterations=2)&ownership&(R[:,:,3]>0)
native=np.zeros_like(R); native[keep]=R[keep]
assert np.array_equal(native[keep],R[keep])
Image.fromarray(native).save(F/'native_complete_new_upper_whole_skirt_short_guides_UNREPAIRED.png')
Image.fromarray(np.uint8(keep)*255).save(F/'actual_native_complete_upper_ownership_mask.png')
shutil.copyfile(I/'inputs/04_complete_upper_whole_skirt_white_full_legs_black_mask.png',F/'actual_request_white_black_mask.png')
obs=json.loads((F/'observed_raw_grip_axis_measurements.json').read_text())
x=np.array(obs['observed_raw_grip_landmarks'],float)
geo=json.loads((I/'MECHANISM_INPUT_BASELINE_THIS_GATE.json').read_text())
y=np.array([row['B_master'] for row in geo['F128_root_pose_rods']['rods']],float)
# Exactly one global similarity. Both measured anatomical grip contacts define
# the fit; all head/neck/chest/arms/whole-skirt samples receive the SAME matrix.
mx=x.mean(0); my=y.mean(0); xc=x-mx; yc=y-my
vx=x[1]-x[0]; vy=y[1]-y[0]
# Two landmarks have rank one. Use the explicit orientation-preserving
# complex ratio, avoiding the undetermined reflection of a rank-one SVD.
angle=math.atan2(vy[1],vy[0])-math.atan2(vx[1],vx[0])
rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
scale=float(np.linalg.norm(vy)/np.linalg.norm(vx)); linear=scale*rot; t=my-linear@mx
assert np.linalg.det(rot)>0 and .65<scale<.85
inv=np.linalg.inv(linear); offset=-inv@t
sx=inv[0,0]*xx+inv[0,1]*yy+offset[0]
sy=inv[1,0]*xx+inv[1,1]*yy+offset[1]
a=native[:,:,3].astype(float)/255; pm=native[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0); wa=wa0.clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
N=np.zeros_like(A); N[:,:,3]=np.rint(wa*255).astype('uint8')
N[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8')
N[N[:,:,3]<3]=0
Image.fromarray(N).save(F/'registered_complete_new_upper_whole_skirt_short_guides_UNREPAIRED.png')
lower=np.array(Image.open(I/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png').convert('RGBA'))
C=np.array(Image.open(I/'fixed_original_C_rods_scene_layer.png').convert('RGBA'))
old=np.array(Image.open(P/'next_F120_passive_decay_input_001/generation_001/registered_complete_new_upper_whole_skirt_two_T.png').convert('RGBA'))
Cpart=C.copy(); Cpart[:,850:]=0
G=A.copy(); G[:,:850]=0; oldchild=(old[:,:,3]>0)&(xx>=850); G[oldchild]=C[oldchild]
base=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G))
base=Image.alpha_composite(base,Image.fromarray(lower)); T=np.array(Image.alpha_composite(base,Image.fromarray(N)))
visible=(lower[:,:,3]>0)&(old[:,:,3]==0)&(N[:,:,3]==0)&(yy>=650)&(xx<850); T[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(N[:,:,3]==0); T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(old[:,:,3]==0)
assert not np.any(gmask&(N[:,:,3]>0)); T[gmask]=A[gmask]
support=(yy>=760)&(xx<850)&(A[:,:,3]>0)
cm=(C[:,:,3]>0)&(old[:,:,3]==0)&(N[:,:,3]==0)&(xx<850)
for region in [visible,gmask,support,cm]:assert np.array_equal(T[region],A[region])
final=F/'F128_uniform_registered_whole_native_upper_fixed_full_lower_CANDIDATE.png'
Image.fromarray(T).save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4'); bg.alpha_composite(Image.fromarray(T))
bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,mag in [('native_contacts',(350,345,750,580),3),
                     ('under_hem',(550,620,825,760),3),('support',(480,800,795,935),2)]:
    c=bg.crop(box).convert('RGB'); c.save(F/f'actual_{name}_1x.png')
    c.resize((c.width*mag,c.height*mag),Image.Resampling.NEAREST).save(F/f'actual_{name}_{mag}x.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4'); oldbg.alpha_composite(Image.fromarray(A))
box=(350,125,1020,720); pair=Image.new('RGB',(1340,595))
pair.paste(oldbg.crop(box).convert('RGB'),(0,0)); pair.paste(bg.crop(box).convert('RGB'),(670,0))
pair.save(F/'120_left_actual128_right_same_canvas_upper_hands_1x.png')
# Full lower-leg support comparison; no repair or clipping to hide mismatches.
pair=Image.new('RGB',(650,320)); box=(475,615,800,935)
pair.paste(oldbg.crop(box).convert('RGB'),(0,0)); pair.paste(bg.crop(box).convert('RGB'),(325,0))
pair.save(F/'120_left_actual128_right_whole_roots_legs_support_1x.png')
pred=(linear@x.T).T+t
angles=[]
for axis,row in zip(obs['axes_y_mx_b'],geo['F128_root_pose_rods']['rods']):
    painted=linear@np.array([1.,axis[0]]); aa=np.array(row['A_master']); bb=np.array(row['B_master'])
    true=bb-aa
    delta=(math.degrees(math.atan2(painted[1],painted[0])-math.atan2(true[1],true[0]))+90)%180-90
    angles.append({'id':row['id'],'native_painted_guide_minus_true_axis_deg':delta})
report={'status':'ONE_NATIVE_F128_UNREPAIRED_CANDIDATE_ACTUAL_ASTRA_GATE_PENDING',
        'image_tool_submissions':1,'raw_outputs':1,'automatic_retries':0,
        'approved_input_commit':'0feec6990a25992f0ced0d57419a3f9a9c4ddbff',
        'raw_sha256':sha(raw),'raw_original_unmodified':True,
        'raw_size':[W,H],'native_component_retained_RGBA_exact_original':True,
        'actual_complete_native_hem_not_technical_white_mask':True,
        'generated_legs_shoes_used':False,'generated_grandma_C_used':False,
        'whole_component_resampling_count':1,'uniform_scale':scale,
        'rotation_degrees_screen_clockwise':math.degrees(math.atan2(rot[1,0],rot[0,0])),
        'translation_xy_px':t.tolist(),'source_to_final_matrix_2x3':np.column_stack([linear,t]).tolist(),
        'observed_raw_anatomical_grips':x.tolist(),'target_fixed_grips':y.tolist(),
        'registered_observed_grips':pred.tolist(),
        'grip_fit_RMS_px':float(np.sqrt(np.mean(np.sum((pred-y)**2,axis=1)))),
        'no_individual_head_palm_finger_arm_or_skirt_repairs':True,
        'native_painted_guides_and_visible_L_tail_preserved_for_honest_gate':True,
        'native_guide_axis_deviations':angles,
        'fixed_visible_lower_RGBA_changes':0,'actual_support_foreground_RGBA_changes':0,
        'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,
        'true_mechanism_roots_pose_rods_will_remain_exact_baseline':True,
        'final_png':final.name,'final_png_sha256':sha(final),
        'adopted':False,'exposure_frozen':False,'132_prepared_or_called':False}
(F/'registration_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(F/'FINAL_PNG_SHA256.txt').write_text(sha(final)+'  '+final.name+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
