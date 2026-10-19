"""One own096 complete far-R palm/wrist local target. No image calls."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_fill_holes
F=Path(__file__).resolve().parent;P=F.parent
m=json.loads((F/'fixed_axes_and_contact.json').read_text())
source=P/'next_F096_active_pull_input_001/generation_001/F096_uniform_registered_upper_fixed_full_lower_candidate.png'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(source)==m['source_sha256']
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));X=np.array(m['fixed_X']);pin=np.array(m['new_R_TH_grip'])
hm,hb=m['T_H_axis_slope_intercept'];sm,sb=m['T_S_axis_slope_intercept']
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
old=poly([(366,374),(396,363),(416,374),(434,389),(485,389),(485,435),(441,435),(417,432),(397,428),(381,419),(371,406),(366,391)])
loose=poly([(358,365),(399,358),(423,373),(436,386),(485,387),(485,440),(430,440),(409,438),(390,433),(375,427),(365,414),(358,398)])
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
skin_owner=(r>165)&(g>95)&(b>g*.65)&(r>g+10)&(A[:,:,3]>0)&loose
old|=binary_dilation(skin_owner,iterations=2)&loose
Image.fromarray(np.uint8(old)*255).save(F/'source_R_complete_palm_short_wrist_semantic_mask.png')
ds=(yy-sm*xx-sb)/math.sqrt(1+sm*sm);dh=(yy-hm*xx-hb)/math.sqrt(1+hm*hm)
# Restore this SAME hand's skin hidden by the two old overlapping shafts before
# moving its complete thumb/fingers/palm/wrist. No old-pose hand is pasted.
hand=np.zeros_like(A);hand[old]=A[old]
under=old&((abs(ds)<7)|(abs(dh)<6))
donorx=np.full_like(xx,415);donory=np.clip(yy-10,392,400)
skin=np.stack([map_coordinates(A[:,:,k].astype(float),[donory,donorx],order=1,mode='nearest') for k in range(4)],2)
skin[:,:,3]=255;hand[under]=np.rint(skin[under]).astype('uint8')
Image.fromarray(hand).save(F/'own096_R_palm_wrist_under_old_shafts_construction_source.png')
# Source-native features move together in one continuous complete-palm field;
# the final 35px of wrist root decays to the fixed original forearm.
src=np.array([[380,390],[379,379],[396,369],[411,376],[429,390],[439,392],[439,430],[378,401],[387,412],[399,421],[411,427],[478,391],[478,404],[478,419],[478,434],[350,340],[495,340],[350,449],[495,449]],float)
dst=np.array([pin,pin+[0,-7],pin+[18,-18],pin+[30,-10],pin+[42,7],[451,388],[451,420],pin+[-3,9],pin+[5,16],pin+[13,23],pin+[22,29],[478,391],[478,404],[478,419],[478,434],[350,340],[495,340],[350,449],[495,449]],float)
rbf=RBFInterpolator(src,dst-src,kernel='thin_plate_spline',degree=1,smoothing=0)
def field(points):
 d=rbf(points);fade=np.clip((478-points[:,0])/28,0,1);fade=fade*fade*(3-2*fade)
 # Exact feature positions remain full through the complete palm; only the
 # short wrist-root portion x450..478 blends continuously into fixed forearm.
 d*=np.where(points[:,0]<=450,1,fade)[:,None];return d
oy,ox=np.mgrid[330:449,345:490];dest=np.column_stack([ox.ravel(),oy.ravel()]).astype(float);coords=dest.copy()
for _ in range(14):coords=dest-field(coords)
sx=coords[:,0].reshape(ox.shape);sy=coords[:,1].reshape(oy.shape)
alpha=hand[:,:,3].astype(float)/255;pm=hand[:,:,:3].astype(float)*alpha[:,:,None]
wa=map_coordinates(alpha,[sy,sx],order=1,mode='constant',cval=0)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros(ox.shape+(4,),np.uint8);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
new=np.zeros_like(A);new[330:449,345:490]=patch;new[:,478:]=0
Image.fromarray(new).save(F/'own096_R_complete_palm_continuous_short_wrist_target.png')
def beam_profile(slope,intercept,centerx):
 u=np.array([1.,slope]);u/=np.linalg.norm(u);n=np.array([-u[1],u[0]]);d=(yy-slope*xx-intercept)/math.sqrt(1+slope*slope)
 cx=centerx+d*n[0];cy=slope*centerx+intercept+d*n[1]
 prof=np.stack([map_coordinates(A[:,:,k].astype(float),[cy,cx],order=1,mode='constant',cval=0) for k in range(4)],2)
 return u,d,np.rint(prof).clip(0,255).astype('uint8')
hu,hd,hprof=beam_profile(hm,hb,310);su,sd,sprof=beam_profile(sm,sb,325)
alongH=(xx-X[0])*hu[0]+(yy-X[1])*hu[1]
extension=(alongH>=-20)&(alongH<=47)&(abs(hd)<8)
TH=np.zeros_like(A);TH[extension]=hprof[extension]
# All unchanged visible TH before X and its puppet end remain original. Only
# the previously hidden same-axis interval is continued, with own beam profile.
base=A.copy();base[loose]=0
B=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(TH)))
B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(new)))
front=TH.copy();front[alongH>38]=0
B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(front)))
# Thumb pad lies above its ONLY TH shaft; curled finger pads stay below it.
thumb_side=(new[:,:,3]>0)&(hd<-.7)&(alongH>15)&(alongH<45)
B[thumb_side]=new[thumb_side]
domain=binary_dilation(loose|(new[:,:,3]>0)|extension,iterations=5)&(xx<478)&(yy<449)
# T_S is restored on its EXACT existing axis, before the released old-hand
# background. Original opaque painted beam pixels remain exact; only former
# skin-blended antialias edges acquire their actual air-side profile matte.
ts_zone=(abs(sd)<8)&domain
TS=np.zeros_like(A);TS[ts_zone]=sprof[ts_zone]
core=ts_zone&(sprof[:,:,3]>245)&(b<g*.70)&(r>g+7)
TS[core]=A[core]
B=np.array(Image.alpha_composite(Image.fromarray(B),Image.fromarray(TS)))
B[core]=A[core]
B[~domain]=A[~domain];B[:,478:]=A[:,478:]
h_visible=(alongH<-7)&(abs(hd)<7)&domain&(abs(sd)>8)
B[h_visible]=A[h_visible]
out=F/'F096_R_only_TH_contact_target.png';Image.fromarray(B).save(out)
white=domain.copy();white[abs(sd)<7]=False
white[h_visible]=False
# The real intersection remains fixed; only hand ownership leaves its vicinity.
xcore=(np.hypot(xx-X[0],yy-X[1])<7)&(sprof[:,:,3]>245)&(abs(hd)<6)
white[xcore]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(F/'mask_complete_R_palm_wrist_only.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
bg.crop((245,310,755,550)).convert('RGB').save(F/'fixed_axes_contacts_1x_REVIEW_ONLY.png')
diff=np.any(B!=A,axis=2)
assert not np.any(diff&~domain) and not np.any(diff[:,478:]) and not np.any(diff[449:]) and not np.any(diff&core)
profile_n=np.arange(-12,12.025,.025);hn=np.array([-hu[1],hu[0]])
profile_a=map_coordinates(A[:,:,3].astype(float),[hm*310+hb+profile_n*hn[1],310+profile_n*hn[0]],order=1)
profile_width=float((profile_a>127).sum()*.025)
report={'status':'ONE_ZERO_CALL_COMPLETE_FAR_R_SINGLE_TH_CONTACT_TARGET_ASTRA_GATE_PENDING','new_image_calls':0,'source096_commit':m['source_commit'],'source096_file':str(source),'source096_sha256':sha(source),'construction_only_not_new_native_art':True,'own096_hand_used_no_older_hand_pasted':True,'complete_palm_and_short_wrist_continuous_field':True,'fixed_X':X.tolist(),'new_R_TH_grip':pin.tolist(),'X_to_new_R_grip_distance_along_TH_px':40.,'T_H_axis_unchanged':[hm,hb],'T_S_axis_unchanged':[sm,sb],'T_H_profile_source_center':[310,float(hm*310+hb)],'T_H_native_profile_alpha_half_width_full_px':profile_width,'T_H_recovered_contact_interval_relative_to_X_px':[-7,47],'T_H_original_visible_before_X_minus7_RGBA_changes':int((diff&h_visible).sum()),'T_H_hand_end_7px_after_grip_is_inferred_and_hidden_not_a_measured_original_endpoint':True,'T_H_puppet_end_unchanged':True,'T_S_puppet_end_and_near_L_grip_unchanged':True,'T_S_original_opaque_beam_core_RGBA_changes':int((diff&core).sum()),'T_S_former_skin_AA_edge_only_released_to_native_air_profile_matte':True,'all_x478_plus_shoulders_elbows_body_RGBA_changes':int(diff[:,478:].sum()),'all_y449_plus_near_L_palm_torso_skirt_legs_RGBA_changes':int(diff[449:].sum()),'outside_complete_local_domain_RGBA_changes':int((diff&~domain).sum()),'final_target_sha256':sha(out),'adopted':False,'generation_authorized':False,'later_states_prepared':False,'exposure_frozen':False}
(F/'target_record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
