"""One native F079 output; whole upper/skirt/T similarity; fixed full lower."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening,median_filter,label

F=Path(__file__).resolve().parent;I=F.parent;P=I.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'raw_original.png';assert sha(raw)=='a123aa6476714c44dc2c5a45735b4c0827ecb11c1a8ee86ae9d483d198073f28'
R=np.array(Image.open(raw).convert('RGBA'));H,W=R.shape[:2];assert (W,H)==(1672,941)
manifest=json.loads((I/'INPUT_MANIFEST.json').read_text());source=Path(manifest['source076_final_file']);A=np.array(Image.open(source).convert('RGBA'))
assert sha(source)==manifest['source076_sha256']
yy,xx=np.indices((H,W));r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)
# Follow the actual full new skirt hem, never the technical input mask.
yellow=(R[:,:,3]>180)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>500)&(yy<700)
core=binary_opening(yellow,iterations=2);hem=np.full(W,np.nan)
for x in range(630,1150):
 ys=np.flatnonzero(core[:,x])
 if not len(ys):continue
 last=int(ys.max());q=np.flatnonzero(yellow[last:min(last+9,H),x])
 if len(q):last+=int(q.max())
 q=np.arange(last,min(last+5,H));hem[x]=int(q[np.argmin(r[q,x]+g[q,x]+b[q,x])])
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]);hem=median_filter(hem,size=3)
keep=(R[:,:,3]>0)&~((yy>500)&(yy>hem[xx]));cc,count=label(keep);sizes=np.bincount(cc.ravel());main=int(np.argmax(sizes[1:])+1);keep=cc==main
native=np.zeros_like(R);native[keep]=R[keep];nativefile=F/'native_complete_new_upper_whole_skirt_both_T.png';Image.fromarray(native).save(nativefile)

# Joint head volume, chest/waist and skirt-root fit to the passed F079 target.
# The complete two arms/hands and both T rods receive this SAME transform.
names=['main_hair_crown','main_hair_front','main_hair_back','chin','neck_sternum','chest_volume','near_shoulder_volume','waist_far','waist_near','far_root_under_new_hem','near_root_under_new_hem']
fit=json.loads((F/'fit_landmarks_source_and_gated_target.json').read_text())
x=np.array(fit['source'],float);y=np.array(fit['target'],float);w=np.array(fit['weights'],float);mx=(x*w[:,None]).sum(0)/w.sum();my=(y*w[:,None]).sum(0)/w.sum();xc=x-mx;yc=y-my
u,d,vt=np.linalg.svd((xc*w[:,None]).T@yc);rot=vt.T@u.T;scale=float(d.sum()/(w[:,None]*xc*xc).sum());linear=scale*rot;t=my-linear@mx;inv=np.linalg.inv(linear);offset=-inv@t
assert np.linalg.det(rot)>0 and .8<scale<.88
registeredfile=F/'registered_complete_new_upper_whole_skirt_both_T.png'
if registeredfile.exists():Nim=Image.open(registeredfile).convert('RGBA')
else:
 Nim=Image.fromarray(native).convert('RGBa').transform((W,H),Image.Transform.AFFINE,tuple(np.column_stack([inv,offset]).ravel()),Image.Resampling.BICUBIC).convert('RGBA');Nim.save(registeredfile)
N=np.array(Nim)
lowerfile=Path(manifest['fixed_complete_lower_file']);assert sha(lowerfile)==manifest['fixed_complete_lower_sha256'];lower=np.array(Image.open(lowerfile).convert('RGBA'))
clayer=Path(manifest['original_C_rods_layer']);assert sha(clayer)==manifest['original_C_rods_sha256'];C=np.array(Image.open(clayer).convert('RGBA'));Cpart=C.copy();Cpart[:,850:]=0
G=A.copy();G[:,:850]=0
base=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));base=Image.alpha_composite(base,Image.fromarray(lower));out=Image.alpha_composite(base,Nim);B=np.array(out)
U0=np.array(Image.open(P/'next_F076_fixed_lower_input_001/generation_001/registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(yy>=650)&(xx<850)
B[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(N[:,:,3]==0);B[fringe]=A[fringe]
gmask=(xx>=860)&(A[:,:,3]>0);assert not np.any(gmask&(N[:,:,3]>0));B[gmask]=A[gmask]
out=Image.fromarray(B);final=F/'F079_uniform_registered_upper_fixed_full_lower_candidate.png';out.save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(out);bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,magnify in [('contacts',(250,310,740,550),3),('under_hem',(560,640,785,755),3),('support',(480,800,795,935),2)]:
 crop=bg.crop(box).convert('RGB');crop.save(F/f'actual_{name}_1x.png');crop.resize((crop.width*magnify,crop.height*magnify),Image.Resampling.NEAREST).save(F/f'actual_{name}_{magnify}x.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A));box=(485,140,850,755);old=oldbg.crop(box).convert('RGB');new=bg.crop(box).convert('RGB');card=Image.new('RGB',(old.width*2,old.height),'#bdc1c4');card.paste(old,(0,0));card.paste(new,(old.width,0));card.save(F/'076_left_registered079_right_upper_and_roots_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(xx<850)
assert np.array_equal(B[visible],A[visible]) and np.array_equal(B[support],A[support]) and np.array_equal(B[gmask],A[gmask]) and np.array_equal(B[cm],A[cm])
pred=(linear@x.T).T+t;angle=math.degrees(math.atan2(rot[1,0],rot[0,0]))
report={'status':'ONE_F079_NATIVE_ORIGINAL_AND_UNIFORM_REGISTERED_FIXED_SUPPORT_CANDIDATE_ASTRA_FINAL_GATE_PENDING','new_image_calls':1,'raw_outputs':1,'automatic_retries':0,'approved_input_commit':'7ce637858b94c2322730fefad0beaf04e09106cc','raw_sha256':sha(raw),'raw_size':[W,H],'native_component_sha256':sha(nativefile),'native_component_pixels_exact_original':True,'native_new_complete_skirt_not_clipped_to_technical_mask':True,'source_component_resampling_count':1,'uniform_scale':scale,'rotation_degrees_screen_clockwise':angle,'translation_xy_px':t.tolist(),'source_to_final_matrix_2x3':np.column_stack([linear,t]).tolist(),'joint_landmark_RMSE_px':float(np.sqrt((w*np.sum((pred-y)**2,axis=1)).sum()/w.sum())),'landmarks':[{'name':n,'source_xy':a.tolist(),'target_xy':b.tolist(),'weight':float(c)} for n,a,b,c in zip(names,x,y,w)],'all_head_neck_torso_complete_arms_palms_wrists_skirt_and_two_T_same_transform':True,'individual_hand_arm_or_rod_adjustments':False,'generated_legs_and_shoes_used':False,'fixed_complete_lower_source':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_layer_RGBA_changes':0,'fixed_lower_geometry_or_alpha_changes':0,'existing_visible_complete_legs_shoes_RGBA_changes':0,'actual_support_y760_plus_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'visible_original_C_outside_child_RGBA_changes':0,'new_root_skin_or_old_edge_repairs':False,'natural_skirt_foreground_overlap_with_full_hidden_roots':int(((lower[:,:,3]>0)&(yy<705)&(N[:,:,3]>240)).sum()),'registered_component_sha256':sha(registeredfile),'final_png':final.name,'final_png_sha256':sha(final),'adopted':False,'propagated':False,'new_exposure_frozen':False,'further_states_prepared_or_called':False}
(F/'registration_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['uniform_scale','rotation_degrees_screen_clockwise','translation_xy_px','joint_landmark_RMSE_px','natural_skirt_foreground_overlap_with_full_hidden_roots','final_png_sha256']},ensure_ascii=False))
