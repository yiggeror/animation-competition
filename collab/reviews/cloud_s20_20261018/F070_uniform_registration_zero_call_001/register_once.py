"""One global similarity, one native component resampling; no image calls."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw

F=Path(__file__).resolve().parent;P=F.parent;I=P/'next_F070_fixed_lower_input_001';G0=I/'generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=G0/'raw_original.png';nativefile=G0/'native_new_complete_upper_arms_whole_skirt_T_rods.png'
fixedsource=P/'F067_near_leg_support_root_zero_call_001/F067_near_support_and_root_closed_candidate.png'
lowerfile=I/'fixed_complete_lower_067_roots_legs_shoes.png'
assert sha(source)=='085ea3a700a0d362acb4cef81a88afdd81a1f409053114e911fe30972b7484c5'
assert sha(fixedsource)=='80a84871aaaa4eddd621e457fa4dae0b95494332d788119ae650ff85356e1dd8'
assert sha(lowerfile)=='d9bab4c9e2b9d95814d6d7cddcd8494ef82cf020532507b1e1d0aaf52d084253'
A=np.array(Image.open(fixedsource).convert('RGBA'));H,W=A.shape[:2]

# Manually read corresponding volume/attachment landmarks on the actual raw
# and approved whole F070 target. Hands and T rods are not fitted separately.
names=['main_hair_crown','main_hair_front','main_hair_back','chin','neck_sternum','chest_volume','near_shoulder_volume','waist_far','waist_near','far_root_under_new_hem','near_root_under_new_hem']
x=np.array([[730,25],[606,135],[845,110],[671,235],[737,267],[779,331],[800,260],[744,412],[846,393],[727,651],[865,646]],float)
y=np.array([[619,164],[518,252],[709,235],[572,334],[629,365],[664,415],[682,357],[633,489],[708,467],[594,686],[714,683]],float)
w=np.array([1,1,1,1,1,1,1,1,1,2,2],float)
mx=(x*w[:,None]).sum(0)/w.sum();my=(y*w[:,None]).sum(0)/w.sum();xc=x-mx;yc=y-my
u,d,vt=np.linalg.svd((xc*w[:,None]).T@yc);rot=vt.T@u.T
assert np.linalg.det(rot)>0
scale=float(d.sum()/(w[:,None]*xc*xc).sum());linear=scale*rot;translation=my-linear@mx
matrix=np.column_stack([linear,translation]);inv=np.linalg.inv(linear);offset=-inv@translation
pred=(linear@x.T).T+translation;angle=math.degrees(math.atan2(rot[1,0],rot[0,0]))
assert .80<scale<.88 and abs(angle)<3

# One source-to-final warp in premultiplied RGBA; every head/arm/hand/skirt/T
# pixel receives exactly this same transform, with no intermediary resample.
native=Image.open(nativefile).convert('RGBA')
coef=tuple(np.column_stack([inv,offset]).ravel())
registeredfile=F/'070_complete_new_upper_whole_skirt_both_T_one_similarity.png'
if registeredfile.exists():
    registered=Image.open(registeredfile).convert('RGBA')
else:
    registered=native.convert('RGBa').transform((W,H),Image.Transform.AFFINE,coef,Image.Resampling.BICUBIC).convert('RGBA')
    registered.save(registeredfile)
N=np.array(registered);lower=np.array(Image.open(lowerfile).convert('RGBA'))
yy,xx=np.indices((H,W))
# The new natural hem reveals several pixels of the OLD skirt's former ink
# just below it. Remove only this internal proximal residue using skin from
# the SAME fixed far leg; alpha, contour and all leg geometry remain fixed.
lr,lg,lb=lower[:,:,:3].astype(float).transpose(2,0,1)
cleanup=(xx>=598)&(xx<=646)&(yy>=682)&(yy<=689)&(N[:,:,3]==0)&(lower[:,:,3]>200)&(((lr<220)&(lg<170))|(lb<lg*.7))
cleanlower=lower.copy();cy,cx=np.where(cleanup);cleanlower[cy,cx,:3]=A[696,cx,:3]
patch=np.zeros_like(A);patch[cleanup]=cleanlower[cleanup];Image.fromarray(patch).save(F/'same_far_leg_skin_old_skirt_residue_cleanup_only.png')
Image.fromarray(np.uint8(cleanup)*255).save(F/'old_skirt_residue_cleanup_mask.png')

axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
props=Image.new('RGBA',(W*4,H*4));draw=ImageDraw.Draw(props)
for role in ['C_N','C_B']:
    q=axes[role];pts=[tuple(v*4 for v in q['shaft_tip_master_px']),tuple(v*4 for v in [952,q['slope']*952+q['intercept']])]
    draw.line(pts,fill='#675034',width=16);draw.line(pts,fill='#b28b52',width=10)
propsA=np.array(props.resize((W,H),Image.Resampling.LANCZOS));propsA[:,835:]=0
grandma=A.copy();grandma[:,:835]=0
base=Image.alpha_composite(Image.fromarray(propsA),Image.fromarray(grandma))
base=Image.alpha_composite(base,Image.fromarray(cleanlower));out=Image.alpha_composite(base,registered);B=np.array(out)
gmask=(xx>=860)&(A[:,:,3]>0)
assert not np.any(gmask&(N[:,:,3]>0));B[gmask]=A[gmask]
fixed_visible=np.array(Image.open(I/'actual_retained_visible_whole_legs_and_shoes_mask.png').convert('L'))>0
unoccluded=fixed_visible&(N[:,:,3]==0)
# Restore original source antialias bytes on the semantic full lower domain;
# the registered skirt alone determines any new natural foreground occlusion.
B[unoccluded&~cleanup]=A[unoccluded&~cleanup]
# Reinstate source low-alpha (1..8) support fringes excluded by the semantic
# prep component, with no change to any leg contour, knee, ankle or shoe.
source_support_fringe=(yy>=736)&(xx<835)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(N[:,:,3]==0)
B[source_support_fringe]=A[source_support_fringe]
out=Image.fromarray(B);final=F/'F070_uniform_registered_upper_fixed_full_lower_candidate.png';out.save(final)

bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(out);bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A))
for name,box,magnify in [('contacts',(280,300,740,540),3),('under_hem',(560,640,780,760),3),('support',(480,800,795,935),2)]:
    crop=bg.crop(box).convert('RGB');crop.save(F/f'actual_{name}_1x.png');crop.resize((crop.width*magnify,crop.height*magnify),Image.Resampling.NEAREST).save(F/f'actual_{name}_{magnify}x.png')
for name,box in [('067_left_registered070_right_upper_1x',(490,140,845,710)),('067_left_registered070_right_skirt_roots_1x',(550,570,845,760))]:
    old=oldbg.crop(box).convert('RGB');new=bg.crop(box).convert('RGB');card=Image.new('RGB',(old.width*2,old.height),'#bdc1c4');card.paste(old,(0,0));card.paste(new,(old.width,0));card.save(F/(name+'.png'))

assert np.array_equal(B[unoccluded&~cleanup],A[unoccluded&~cleanup]) and np.array_equal(B[gmask],A[gmask])
support=(yy>=760)&(xx<835)&(A[:,:,3]>0)
assert np.array_equal(B[support],A[support])
roots=(lower[:,:,3]>0)&(yy<705)
joint_error=np.sqrt((w*np.sum((pred-y)**2,1)).sum()/w.sum())
report={
 'status':'ONE_ZERO_CALL_F070_WHOLE_NATIVE_COMPONENT_SIMILARITY_REGISTERED_CANDIDATE_ASTRA_GATE_PENDING',
 'new_image_calls':0,'raw_originals_used':1,'image_generation_retries':0,
 'source_commit':'750baee43a331448b511b2c3b228fca4101dcf75',
 'source_original':str(source),'source_original_sha256':sha(source),
 'native_semantic_component':str(nativefile),'native_semantic_component_sha256':sha(nativefile),
 'fit_reference':str(I/'inputs/01_unique_complete_F070_fixed_lower_target_REVIEW_ONLY.png'),
 'scale_uniform':scale,'rotation_degrees_screen_clockwise':angle,
 'translation_xy_px':translation.tolist(),'source_to_final_matrix_2x3':matrix.tolist(),
 'source_component_resampling_count':1,'resampling':'premultiplied RGBA bicubic, direct native-to-final',
 'no_individual_arm_hand_or_T_rod_transform':True,'no_nonuniform_skirt_scale':True,
 'landmarks':[{'name':n,'source_xy':a.tolist(),'target_xy':b.tolist(),'weight':float(c),'registered_xy':d.tolist(),'residual_xy':e.tolist()} for n,a,b,c,d,e in zip(names,x,y,w,pred,pred-y)],
 'weighted_joint_landmark_RMSE_px':float(joint_error),
 'fixed_complete_lower_source':str(lowerfile),'fixed_complete_lower_source_sha256':sha(lowerfile),
 'fixed_complete_lower_layer_RGBA_changes':0,
 'fixed_complete_lower_layer_alpha_and_geometry_changes':int(np.any(cleanlower[:,:,3]!=lower[:,:,3]).sum()),
 'unoccluded_fixed_complete_legs_shoes_excluding_old_skirt_residue_output_RGBA_changes':int(np.any(B[unoccluded&~cleanup]!=A[unoccluded&~cleanup],axis=1).sum()),
 'actual_067_support_y760_plus_foreground_RGBA_changes':int(np.any(B[support]!=A[support],axis=1).sum()),
 'actual_grandma_foreground_RGBA_changes':int(np.any(B[gmask]!=A[gmask],axis=1).sum()),
 'actual_hidden_root_pixels_covered_by_new_skirt':int((roots&(N[:,:,3]>240)).sum()),
 'new_skirt_complete_natural_foreground':True,'old_skirt_foreground_pasted':False,
 'root_or_skirt_cleanup_applied':True,
 'cleanup':'only revealed old skirt ink/residue inside far proximal root, x598..646/y682..689, same fixed far leg skin from y696; alpha and geometry unchanged',
 'cleanup_RGB_pixel_count':int(cleanup.sum()),
 'registered_component_sha256':sha(registeredfile),
 'final_png':final.name,'final_png_sha256':sha(final),
 'adopted':False,'propagated':False,'new_exposure_frozen':False,'further_states_prepared_or_called':False
}
(F/'registration_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['scale_uniform','rotation_degrees_screen_clockwise','translation_xy_px','weighted_joint_landmark_RMSE_px','actual_hidden_root_pixels_covered_by_new_skirt','final_png_sha256']},ensure_ascii=False))
