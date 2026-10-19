"""Receive ONE actual F120; one whole-component similarity, fixed complete lower."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening,binary_dilation,median_filter,label,map_coordinates
F=Path(__file__).resolve().parent;I=F.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'raw_original.png';assert sha(raw)=='8f0a24461428347a6ad5a6406b7837958b67cfcc6f4f64cb041f8c6d2bae4a3a'
R=np.array(Image.open(raw).convert('RGBA'));RH,RW=R.shape[:2];assert (RW,RH)==(1672,941)
m=json.loads((I/'INPUT_MANIFEST.json').read_text());source=Path(m['source112_file']);assert sha(source)==m['source112_sha256'];A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2]
yy,xx=np.indices((RH,RW));r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)
# Trace the actual complete native garment hem, including ink/AA. No white
# construction silhouette is used to crop this native drawing.
# Separate the actual generated scene-C shafts at their real head/flower
# occlusion. Those shafts and grandma are not part of the new child component.
wood=(R[:,:,3]>100)&(r>120)&(g>65)&(r>g+10)&(b<g*.8);points=[[],[]]
for xcol in range(815,861):
 ys=np.flatnonzero(wood[:,xcol]&(np.arange(RH)>240)&(np.arange(RH)<330))
 parts=np.split(ys,np.where(np.diff(ys)>3)[0]+1);parts=[q for q in parts if 2<=len(q)<=12]
 if len(parts)>=2:
  for index,q in enumerate(parts[:2]):points[index].append((xcol,float(np.median(q))))
assert min(map(len,points))>35
cm1,cb1=np.polyfit(np.array(points[0])[:,0],np.array(points[0])[:,1],1);cm2,cb2=np.polyfit(np.array(points[1])[:,0],np.array(points[1])[:,1],1)
flower=binary_dilation((r>120)&(g<70)&(b<70)&(xx>680)&(xx<765)&(yy>235)&(yy<315),iterations=2)
haircore=(R[:,:,3]>80)&(r<175)&(g<125)&(b<120)&(r>g+7)&(xx>650)&(xx<835)&(yy>205)&(yy<370)
hairguard=binary_dilation(binary_opening(haircore,iterations=2),iterations=2)
topC=(abs(yy-cm1*xx-cb1)/math.sqrt(1+cm1*cm1)<6)&(xx>=731)&~flower&~hairguard
bottomC=(abs(yy-cm2*xx-cb2)/math.sqrt(1+cm2*cm2)<6)&(xx>=733)&~flower&~hairguard
sceneC=topC|bottomC;Image.fromarray(np.uint8(sceneC)*255).save(F/'native_scene_C_ownership_excluded_mask.png')
yellow=(R[:,:,3]>180)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>500)&(yy<710)
core=binary_opening(yellow,iterations=2);hem=np.full(RW,np.nan)
for xcol in range(500,1020):
 ys=np.flatnonzero(core[:,xcol])
 if not len(ys):continue
 last=int(ys.max());q=np.flatnonzero(yellow[last:min(last+9,RH),xcol])
 if len(q):last+=int(q.max())
 q=np.arange(last,min(last+4,RH));hem[xcol]=int(q[np.argmin(r[q,xcol]+g[q,xcol]+b[q,xcol])])
ok=np.isfinite(hem);assert ok.sum()>400
hem=np.interp(np.arange(RW),np.flatnonzero(ok),hem[ok]);hem=median_filter(hem,size=3)
# Only the generated lower-body corridor needs a garment/skin split.
# Preserve the WHOLE original native hem/ink outside that corridor, including
# curled far-right folds; no columnwise clipping of garment-only areas.
ownership=~sceneC&~((yy>500)&(yy>hem[xx])&(xx<760))&(xx<1010)
cc,count=label((R[:,:,3]>24)&ownership);girl=int(cc[410,620]);assert girl>0
keep=binary_dilation(cc==girl,iterations=2)&ownership&(R[:,:,3]>0)
native=np.zeros_like(R);native[keep]=R[keep];nativefile=F/'native_complete_new_upper_whole_skirt_two_T.png';Image.fromarray(native).save(nativefile)
assert np.array_equal(native[keep],R[keep])
Image.fromarray(np.uint8(keep)*255).save(F/'actual_native_complete_upper_ownership_mask.png')
yy,xx=np.indices((H,W))
fit=json.loads((F/'fit_landmarks_source_and_gated_target.json').read_text());x=np.array(fit['source'],float);y=np.array(fit['target'],float);w=np.array(fit['weights'],float)
mx=(x*w[:,None]).sum(0)/w.sum();my=(y*w[:,None]).sum(0)/w.sum();xc=x-mx;yc=y-my
u,d,vt=np.linalg.svd((xc*w[:,None]).T@yc);rot=vt.T@u.T;scale=float(d.sum()/(w[:,None]*xc*xc).sum());linear=scale*rot;t=my-linear@mx
assert np.linalg.det(rot)>0 and .94<scale<1.05
inv=np.linalg.inv(linear);offset=-inv@t;sx=inv[0,0]*xx+inv[0,1]*yy+offset[0];sy=inv[1,0]*xx+inv[1,1]*yy+offset[1]
# One premultiplied float resampling of the complete new native component.
a=native[:,:,3].astype(float)/255;pm=native[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
N=np.zeros_like(A);N[:,:,3]=np.rint(wa*255).astype('uint8');N[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');N[N[:,:,3]<3]=0
registered=F/'registered_complete_new_upper_whole_skirt_two_T.png';Image.fromarray(N).save(registered)
lowerfile=Path(m['fixed_complete_lower_file']);clayer=Path(m['original_C_rods_layer']);assert sha(lowerfile)==m['fixed_complete_lower_sha256'] and sha(clayer)==m['original_C_rods_sha256']
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'));Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0
U0=np.array(Image.open(I/'source112_adopted_complete_upper_head_skirt_two_T.png').convert('RGBA'));oldchild=(U0[:,:,3]>0)&(xx>=850);G[oldchild]=C[oldchild]
base=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));base=Image.alpha_composite(base,Image.fromarray(lower));B=np.array(Image.alpha_composite(base,Image.fromarray(N)))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(yy>=650)&(xx<850);B[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(N[:,:,3]==0);B[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0);assert not np.any(gmask&(N[:,:,3]>0));B[gmask]=A[gmask]
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(xx<850)
assert np.array_equal(B[visible],A[visible]) and np.array_equal(B[support],A[support]) and np.array_equal(B[gmask],A[gmask]) and np.array_equal(B[cm],A[cm])
final=F/'F120_uniform_registered_upper_fixed_full_lower_candidate.png';Image.fromarray(B).save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,mag in [('contacts',(200,285,800,575),3),('under_hem',(560,635,800,755),3),('support',(480,800,795,935),2)]:
 c=bg.crop(box).convert('RGB');c.save(F/f'actual_{name}_1x.png');c.resize((c.width*mag,c.height*mag),Image.Resampling.NEAREST).save(F/f'actual_{name}_{mag}x.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A));box=(210,125,1010,720);pair=Image.new('RGB',(1600,595));pair.paste(oldbg.crop(box).convert('RGB'),(0,0));pair.paste(bg.crop(box).convert('RGB'),(800,0));pair.save(F/'112_left_actual120_right_same_canvas_upper_hands_1x.png')
pred=(linear@x.T).T+t
report={'status':'ONE_NATIVE_F120_WHOLE_COMPONENT_REGISTERED_FIXED_FULL_LOWER_ASTRA_TERMINAL_GATE_PENDING','image_tool_submissions':1,'raw_outputs':1,'automatic_retries':0,'approved_input_commit':'3a1c11921f3afc8afb0f903861d9b34f4d1af776','raw_sha256':sha(raw),'raw_original_unmodified':True,'actual_raw_size':[RW,RH],'final_canvas_size':[W,H],'native_complete_component_file':nativefile.name,'native_component_retained_RGBA_exact_original':True,'native_G_C_scene_pixels_used':False,'native_scene_C_semantic_exclusion_mask':'native_scene_C_ownership_excluded_mask.png','native_scene_C_axis_fits':[[float(cm1),float(cb1)],[float(cm2),float(cb2)]],'native_complete_actual_hem_not_technical_white_mask':True,'native_complete_hem_revision':'Preserve complete actual garment-only folds; initial receive clipped a far-right ink fold and is archived. Same raw and same registration.','initial_receive_candidate_sha256':'553ccd4d0a2050e7c0d5025b5ea1b578732b25568d267da3f60d55ab6984a4aa','source_component_resampling_count':1,'uniform_scale':scale,'rotation_degrees_screen_clockwise':math.degrees(math.atan2(rot[1,0],rot[0,0])),'translation_xy_px':t.tolist(),'source_to_final_matrix_2x3':np.column_stack([linear,t]).tolist(),'observed_2D_anchor_RMS_px':float(np.sqrt((w*np.sum((pred-y)**2,axis=1)).sum()/w.sum())),'actual_anchor_predictions':{name:p.tolist() for name,p in zip(fit['names'],pred)},'all_new_head_neck_both_complete_arms_palms_wrists_torso_whole_skirt_and_two_T_same_transform':True,'local_hand_arm_rod_or_head_repairs':False,'generated_legs_shoes_used':False,'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_RGBA_or_geometry_changes':0,'actual_existing_visible_legs_shoes_RGBA_changes':0,'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'new_root_skin_or_old_edge_repairs':False,'final_png':final.name,'final_png_sha256':sha(final),'adopted':False,'propagated':False,'new_exposure_frozen':False,'later_states_prepared_or_called':False}
(F/'registration_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['uniform_scale','rotation_degrees_screen_clockwise','translation_xy_px','observed_2D_anchor_RMS_px','final_png_sha256']},ensure_ascii=False))
