"""One native complete far-R palm/wrist; one similarity; fixed096 semantic rejoin."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,binary_dilation
F=Path(__file__).resolve().parent;P=F.parent;R=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'raw_original.png';assert sha(raw)=='0216dfe595932f339ca6bff279c067eb77deea8858e458ed2e8fd8510f8a0509'
N0=np.array(Image.open(raw).convert('RGBA'));rh,rw=N0.shape[:2];assert (rw,rh)==(1460,1078)
target=P/'F096_R_only_TH_contact_target.png';assert sha(target)=='f247bc21f2f9c7bfe175d515ad144ebb25d85e26a262f31e0c19a98de7a3e98f'
A=np.array(Image.open(target).convert('RGBA'))
original=R/'next_F096_active_pull_input_001/generation_001/F096_uniform_registered_upper_fixed_full_lower_candidate.png';O=np.array(Image.open(original).convert('RGBA'))
H,W=A.shape[:2];yy,xx=np.indices((H,W));ny,nx=np.indices((rh,rw))
def polygon(shape,points):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
own=polygon((rh,rw),[(650,302),(714,289),(800,252),(861,274),(910,323),(934,373),(969,391),(1070,390),(1070,598),(993,590),(920,552),(872,514),(840,531),(786,534),(747,514),(715,478),(686,435),(678,410),(681,377),(652,352)])
nr,ng,nb=N0[:,:,:3].astype(float).transpose(2,0,1)
# Keep the actual complete native skin/ink silhouette, not the technical mask.
# Native scene shafts are context, so their visible wood is excluded from the
# skin ownership gap and the exact existing TH/TS are used beneath/above it.
nm,ni=-0.6213237924865819,787.1298091830652
native_TH_distance=abs(ny-nm*nx-ni)/math.sqrt(1+nm*nm)
native_wood=(nb<ng*.70)&(nr>ng+8)&(native_TH_distance<25)
keep=own&(N0[:,:,3]>0)&~native_wood
component=np.zeros_like(N0);component[keep]=N0[keep]
Image.fromarray(component).save(F/'native_complete_R_palm_short_wrist_semantic_component.png')
fit=json.loads((F/'whole_palm_registration_landmarks.json').read_text());M=np.array(fit['matrix']);linear=M[:,:2];t=M[:,2];inv=np.linalg.inv(linear);offset=-inv@t
sx=inv[0,0]*xx+inv[0,1]*yy+offset[0];sy=inv[1,0]*xx+inv[1,1]*yy+offset[1]
a=component[:,:,3].astype(float)/255;pm=component[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
N=np.zeros_like(A);N[:,:,3]=np.rint(wa*255).astype('uint8');N[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');N[N[:,:,3]<3]=0
Image.fromarray(N).save(F/'registered_whole_native_R_palm_short_wrist_one_similarity.png')
axes=json.loads((P/'fixed_axes_and_contact.json').read_text());hm,hb=axes['T_H_axis_slope_intercept'];sm,sb=axes['T_S_axis_slope_intercept'];X=np.array(axes['fixed_X'])
hd=(yy-hm*xx-hb)/math.sqrt(1+hm*hm);sd=(yy-sm*xx-sb)/math.sqrt(1+sm*sm)
hu=np.array([1.,hm]);hu/=np.linalg.norm(hu);hn=np.array([-hu[1],hu[0]])
along=(xx-X[0])*hu[0]+(yy-X[1])*hu[1]
# Reuse the already approved SAME TH profile/axis/hidden hand-end. No new rod.
cx=310+hd*hn[0];cy=hm*310+hb+hd*hn[1]
profile=np.stack([map_coordinates(O[:,:,k].astype(float),[cy,cx],order=1,mode='constant',cval=0) for k in range(4)],2)
TH=np.zeros_like(A);thregion=(along>=-35)&(along<=47)&(abs(hd)<8);TH[thregion]=np.rint(profile[thregion]).clip(0,255).astype('uint8')
local=polygon((H,W),[(345,330),(449,330),(478,375),(478,449),(345,449)])
base=A.copy();base[local&(xx<478)]=0
base=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(TH)))
# At x478 the actual native/fixed outer contours already agree to ~1px.
# Preserve native alpha/ink. Feather only overlapping skin RGB, never turn an
# opaque old-forearm rectangle into a premature silhouette below the new wrist.
mix=np.clip((xx-468)/10,0,1);mix=mix*mix*(3-2*mix)
cr,cg,cb=N[:,:,:3].astype(float).transpose(2,0,1)
skin_overlap=(xx>=468)&(xx<478)&(N[:,:,3]>220)&(O[:,:,3]>220)&(cr>170)&(cg>95)&(cb>cg*.65)&(cr>cg+10)
join=N.copy();blend=N[:,:,:3]*(1-mix[:,:,None])+O[:,:,:3]*mix[:,:,None]
join[skin_overlap,:3]=np.rint(blend[skin_overlap]).clip(0,255).astype('uint8')
B=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(join)))
# Actual entire TS and intersection context remain EXACT from approved096.
ts_fixed=(abs(sd)<8)&local;B[ts_fixed]=A[ts_fixed]
th_original=(along<-7)&(abs(hd)<7)&(abs(sd)>8)&local;B[th_original]=A[th_original]
domain=(local|binary_dilation(N[:,:,3]>0,iterations=2))&(xx<478)&(yy>=330)&(yy<449)
B[~domain]=A[~domain];B[:,478:]=O[:,478:];B[449:]=O[449:]
final=F/'F096_R_single_TH_native_local_candidate.png';Image.fromarray(B).save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
c=bg.crop((240,295,565,535)).convert('RGB');c.save(F/'actual_contacts_1x.png');c.resize((975,720),Image.Resampling.NEAREST).save(F/'actual_contacts_3x.png')
Image.fromarray(np.uint8(domain)*255).save(F/'actual_complete_R_palm_short_wrist_rejoin_domain.png')
diff=np.any(B!=O,axis=2)
assert not np.any(diff[:,478:]) and not np.any(diff[449:])
assert np.array_equal(B[ts_fixed],A[ts_fixed])
report={'status':'ONE_NATIVE_F096_FAR_R_SINGLE_TH_LOCAL_CANDIDATE_ASTRA_TERMINAL_PENDING','image_tool_submissions':1,'raw_outputs':1,'automatic_retries':0,'only_two_matched_3x_crop_inputs':True,'approved_target_commit':'928a60d081f854149a9bdc2de945060bac77d292','raw_output_original_path':'/workspace/generated_images/exec-5dc10783-991f-4d08-8fbf-3eccb10c466e.png','raw_sha256':sha(raw),'requested_local_size':[975,720],'actual_raw_size':[rw,rh],'raw_original_unmodified':True,'whole_native_palm_component_resampling_count':1,'whole_component_similarity':fit,'separate_finger_or_grip_moves':False,'technical_white_mask_hard_clipping':False,'native_component_ownership':'complete own native thumb, four curled fingers, palm heel and short wrist; scene wood context removed semantically, fixed shafts retained','short_wrist_attachment':'actual native/fixed contour match within~1px at x478; native alpha retained, only last10px of overlapping skin RGB feathered; no hand/finger local warp','fixed_TS_axis_tip_L_grip_and_visible_RGBA_changes':0,'X_fixed_original_context':True,'TH_same_axis_profile_and_previous_inferred_hidden_end_unchanged':True,'all_x478_plus_original_shoulders_elbows_body_RGBA_changes':int(diff[:,478:].sum()),'all_y449_plus_original_near_L_palm_torso_skirt_full_legs_RGBA_changes':int(diff[449:].sum()),'black_context_native_redrawing_used':False,'final_png':final.name,'final_png_sha256':sha(final),'adopted':False,'later_states_prepared':False,'new_exposure_frozen':False}
(F/'receive_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','raw_sha256','final_png_sha256','all_x478_plus_original_shoulders_elbows_body_RGBA_changes','all_y449_plus_original_near_L_palm_torso_skirt_full_legs_RGBA_changes']},ensure_ascii=False))
