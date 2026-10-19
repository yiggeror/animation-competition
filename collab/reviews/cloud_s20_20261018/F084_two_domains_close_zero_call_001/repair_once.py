"""One authorized zero-call F084 two-domain repair; own F084 image pixels only."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes,binary_opening,map_coordinates,label
F=Path(__file__).resolve().parent;P=F.parent;S=P/'next_F084_peak_input_001/generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=S/'F084_uniform_registered_fixed_lower_DIAGNOSTIC_NOT_ADOPTED.png'
assert sha(source)=='1bf65e3373979dc4317d52b223b72eaa75db9cad3652d628d733f438de73c784'
A=np.array(Image.open(source).convert('RGBA'));U=np.array(Image.open(S/'registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'))
H,W=A.shape[:2];yy,xx=np.indices((H,W));r,g,b=U[:,:,:3].astype(float).transpose(2,0,1)
C=np.array(Image.open(P/'next_F084_peak_input_001/fixed_original_C_rods_scene_layer.png').convert('RGBA'))
ref=P/'F079_head_neck_scale_close_zero_call_001/F079_own_head_neck_volume_closed_candidate.png'
assert sha(ref)=='2a2fbbee3aaff0b6289b4bb8df756193fe70e37ab9a552af8192c13e459930af'
def mask_poly(points):
 im=Image.new('L',(W*4,H*4));d=ImageDraw.Draw(im);d.polygon([(round(x*4),round(y*4)) for x,y in points],fill=255)
 return np.asarray(im.resize((W,H),Image.Resampling.LANCZOS)).astype(float)/255
def bezier(a,b,c,d,n=50):
 t=np.linspace(0,1,n)[:,None];return ((1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)).tolist()
def stroke(points,width=1.15):
 im=Image.new('L',(W*4,H*4));d=ImageDraw.Draw(im);d.line([(round(x*4),round(y*4)) for x,y in points],fill=255,width=round(width*4),joint='curve')
 return np.asarray(im.resize((W,H),Image.Resampling.LANCZOS)).astype(float)/255
def shaft(a,b,halfwidth):
 a=np.array(a,float);v=np.array(b,float)-a;v2=v@v;t=((xx-a[0])*v[0]+(yy-a[1])*v[1])/v2;dist=np.abs((xx-a[0])*v[1]-(yy-a[1])*v[0])/np.sqrt(v2)
 return (dist<halfwidth)&(t>=0)&(t<=1)
# Preserve both actual rigid shafts, X, and native grasp pixels.
TH=shaft((282.,435.5),(420.5,344.5),5.8);TS=shaft((298.,271.),(466.5,459.5),6.2)
real_guard=(TH|TS)&(A[:,:,3]>0)
third=mask_poly([(431.7,347.4),(441.2,345.2),(479.,456.5),(465.7,461.)])
Rdomain=mask_poly([(401,327),(440,321),(463,335),(488,371),(497,409),(497,430),(455,432),(426,405),(412,377),(400,352)])
Ldomain=mask_poly([(429,419),(452,417),(468,428),(484,420),(505,433),(521,466),(517,504),(474,512),(449,497),(444,460),(433,445)])
hand_domain=(Rdomain>0)|(Ldomain>0)|(third>0)
Rcurve=bezier((435.2,395.3),(435.8,406.5),(446.5,419.3),(460.5,422.5))+bezier((460.5,422.5),(472.,425.5),(485.,424.5),(497.,421.5))[1:]
Rinside=mask_poly([(430,343),(477,337),(509,388),(509,416)]+Rcurve[::-1]+[(426,388)])
Lcurve=bezier((484.,425.),(473.,425.),(460.4,435.5),(461.8,447.))+bezier((461.8,447.),(462.5,454.4),(470.,458.),(477.6,449.6))[1:]
Ledge=bezier((484.,425.),(473.,425.),(460.4,435.5),(461.8,447.))+bezier((461.8,447.),(462.0,451.2),(464.3,454.2),(467.1,456.1))[1:]
Linside=mask_poly(Ledge+[(450,461),(450,489),(474,509),(526,511),(526,468),(508,435)])
Rrepair=third*Rinside;Lrepair=third*Linside;Rrepair[real_guard]=0;Lrepair[real_guard]=0
air=third*np.clip(1-Rinside,0,1)*np.clip(1-Linside,0,1);air[real_guard]=0
B=A.copy().astype(float)
# Continue adjacent same-row skin from this exact native 084 palm, not 079.
for weight,shift in [(Rrepair,19.),(Lrepair,18.)]:
 skin=np.stack([map_coordinates(A[:,:,k].astype(float),[yy,xx+shift],order=1,mode='nearest') for k in range(4)],2);weight=weight[:,:,None];B=B*(1-weight)+skin*weight
B*=1-air[:,:,None]
for curve in [Rcurve,Lcurve]:
 ink=stroke(curve)*np.maximum(third,binary_dilation(third>.1,iterations=2));ink[real_guard]=0
 B=B*(1-ink[:,:,None])+np.array([89,55,32,255.])*ink[:,:,None]
B=np.rint(B).clip(0,255).astype('uint8');B[B[:,:,3]<3]=0;B[real_guard]=A[real_guard];B[~hand_domain]=A[~hand_domain]
for name,mask in [('complete_both_palm_contact_semantic_domain',hand_domain),('extra_third_shaft_actual_removal_mask',third),('two_native_true_shafts_X_and_grips_protection_mask',real_guard),('own084_far_palm_skin_continuation_mask',Rrepair),('own084_near_thumb_skin_continuation_mask',Lrepair),('exposed_third_shaft_restored_transparency_mask',air)]:
 Image.fromarray(np.rint(mask*255).astype('uint8')).save(F/f'{name}.png')
def hair_measure(a):
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);m=(a[:,:,3]>180)&(r<170)&(g<130)&(b<120)&(r>g+7)&(yy>145)&(yy<325)&(xx>480)&(xx<750)
 cc,n=label(m);sizes=np.bincount(cc.ravel());m=cc==(np.argmax(sizes[1:])+1);y,x=np.where(m)
 return {'pixels':int(len(x)),'x_005_995':np.quantile(x,[.005,.995]).tolist(),'y_005_995':np.quantile(y,[.005,.995]).tolist(),'centroid':[float(x.mean()),float(y.mean())]}
baseline=hair_measure(np.array(Image.open(ref).convert('RGBA')));before=hair_measure(A)
width=lambda m:m['x_005_995'][1]-m['x_005_995'][0]
width_ratio=width(baseline)/width(before);area_scale=math.sqrt(baseline['pixels']/before['pixels']);scale=math.sqrt(width_ratio*area_scale)
tx=baseline['centroid'][0]-scale*before['centroid'][0];ty=((baseline['centroid'][1]-scale*before['centroid'][1])+2*(338.-scale*337.))/3
assert .91<scale<.95
alpha=U[:,:,3]>0
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>555)&(xx<724)&(yy>337)&(yy<410)&alpha;white=binary_opening(white,iterations=1)
yellow=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U[:,:,3]>180)&(yy>332);yellow=binary_opening(yellow,iterations=1)
clothes=binary_dilation(white,iterations=2)|binary_dilation(yellow,iterations=2)
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha;neck=binary_dilation(skin&(xx>586)&(xx<680)&(yy>325)&(yy<380),iterations=2)&alpha&~clothes
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5));pony=binary_dilation(hair&alpha&(xx>658)&(xx<792)&(yy>282)&(yy<405),iterations=2)&alpha&~clothes
head=(alpha&(xx>480)&(xx<792)&(yy<342))|neck|pony;head=binary_fill_holes(head)&alpha&~clothes
oldhead=np.zeros_like(U);oldhead[head]=U[head];Image.fromarray(oldhead).save(F/'084_own_complete_head_hair_face_ponytail_neck_source.png');Image.fromarray(np.uint8(head)*255).save(F/'source_complete_head_neck_semantic_mask.png')
def amount(x,y):
 boundary=376.-(25./65.)*(x-607.);t=np.clip((boundary-y-2.)/25.,0.,1.);k=t*t*(3.-2.*t)
 return np.where((x>=590)&(x<=684)&(y>=325),k,1.)
x0,y0,x1,y1=480,115,798,414;oy,ox=np.mgrid[y0:y1,x0:x1];sx=(ox-tx)/scale;sy=(oy-ty)/scale
for _ in range(14):
 k=amount(sx,sy);denom=1+k*(scale-1);sx=(ox-k*tx)/denom;sy=(oy-k*ty)/denom
a=oldhead[:,:,3].astype(float)/255.;pm=oldhead[:,:,:3].astype(float)*a[:,:,None];wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros((y1-y0,x1-x0,4),np.uint8);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
newhead=np.zeros_like(U);newhead[y0:y1,x0:x1]=patch;Image.fromarray(newhead).save(F/'084_own_head_hair_neck_one_continuous_scale.png')
base=B.copy();base[head]=C[head];final=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(newhead)))
body=(U[:,:,3]>0)&~head;body_restore=body&~hand_domain;final[body_restore]=A[body_restore]
fixed_collar=clothes&(U[:,:,3]>0);final[fixed_collar]=A[fixed_collar];anchor=head&(amount(xx,yy)==0);final[anchor]=A[anchor]
head_domain=head|(newhead[:,:,3]>0);domain=head_domain|hand_domain;final[~domain]=A[~domain]
out=F/'F084_two_domains_closed_candidate.png';Image.fromarray(final).save(out)
Image.fromarray(np.uint8(head_domain)*255).save(F/'head_neck_and_C_occlusion_domain.png');Image.fromarray(np.uint8(domain)*255).save(F/'two_authorized_semantic_domains.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(final));bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,mag in [('two_true_rods_contacts',(265,260,745,550),3),('head_neck',(485,125,790,410),3),('neck_collar',(565,325,720,405),3),('under_hem',(560,640,785,755),3),('support',(480,800,795,935),2)]:
 c=bg.crop(box).convert('RGB');c.save(F/f'actual_{name}_1x.png');c.resize((c.width*mag,c.height*mag),Image.Resampling.NEAREST).save(F/f'actual_{name}_{mag}x.png')
refbg=Image.new('RGBA',(W,H),'#bdc1c4');refbg.alpha_composite(Image.open(ref).convert('RGBA'))
for name,box in [('head_neck',(485,125,790,410)),('upper_hands_action',(235,125,865,720))]:
 bw,bh=box[2]-box[0],box[3]-box[1];pair=Image.new('RGB',(2*bw,bh));pair.paste(refbg.crop(box).convert('RGB'),(0,0));pair.paste(bg.crop(box).convert('RGB'),(bw,0));pair.save(F/f'079_left_repaired084_right_{name}_same_canvas_1x.png')
diff=np.any(A!=final,axis=2)
assert not np.any(diff&~domain) and not np.any(diff&real_guard) and not np.any(diff&(yy>=550)) and not np.any(diff&body_restore)
report={'status':'ONE_ZERO_CALL_F084_TWO_DOMAIN_CANDIDATE_ASTRA_REVIEW_PENDING','new_image_calls':0,'source084_commit':'07690a02a51bba4652cc06d1ef7f6fc73ab8eb1e','source084_file':str(source),'source084_sha256':sha(source),'reference079_file':str(ref),'reference079_sha256':sha(ref),'head_measurements':{'correct079':baseline,'source084':before,'candidate084':hair_measure(final)},'complete_own_head_uniform_scale':scale,'head_translation_xy':[tx,ty],'head_rotation_added_degrees':0,'head_neck_resampling_count':1,'neck_method':'own084 continuous inverse warp; C1 decay within 25px to original oblique collar attachment','old079_or076_pixels_pasted':False,'true_TH_axis_endpoints_px':[[282.,435.5],[420.5,344.5]],'true_TS_axis_endpoints_px':[[298.,271.],[466.5,459.5]],'true_two_shafts_and_grips_RGBA_changes':int((diff&real_guard).sum()),'third_steep_connector_removed_without_moving_true_axes_or_grips':True,'hand_repair_method':'same084 adjacent own palm pixels continued across extra shaft occlusion within complete palm domains; interrupted external contours reconnected; no old palms pasted','head_changed_pixels':int((diff&head_domain).sum()),'palm_contact_changed_pixels':int((diff&hand_domain).sum()),'outside_two_domains_RGBA_changes':int((diff&~domain).sum()),'protected_upper_arms_torso_whole_skirt_RGBA_changes':int((diff&body_restore).sum()),'fixed_collar_RGBA_changes':int((diff&fixed_collar).sum()),'all_y550_plus_skirt_full_legs_shoes_RGBA_changes':int((diff&(yy>=550)).sum()),'grandma_RGBA_changes':int((diff&(xx>=850)).sum()),'C_axis_geometry_changed':False,'C_only_head_occlusion_updated':True,'final_png':out.name,'final_png_sha256':sha(out),'adopted':False,'propagated':False,'new_exposure_frozen':False,'further_states_prepared_or_called':False}
(F/'repair_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
