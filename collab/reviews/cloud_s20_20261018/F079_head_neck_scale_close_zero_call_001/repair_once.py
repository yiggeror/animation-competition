"""079 own complete head/hair/neck volume closure; zero image calls."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_fill_holes,binary_opening,map_coordinates

F=Path(__file__).resolve().parent;P=F.parent;S=P/'next_F079_fixed_lower_input_001/generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=S/'F079_uniform_registered_upper_fixed_full_lower_candidate.png'
assert sha(source)=='aa51acf975fb7a81e949cba36043ddae364708ddd12063207c42037d0cb0503b'
A=np.array(Image.open(source).convert('RGBA'));U=np.array(Image.open(S/'registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
ref=P/'next_F076_fixed_lower_input_001/generation_001/F076_uniform_registered_upper_fixed_full_lower_candidate.png'
measure=json.loads((F/'actual_volume_measurements_before.json').read_text());old,new=measure
rw=old['hair_core_x_quantiles'][1]-old['hair_core_x_quantiles'][0];nw=new['hair_core_x_quantiles'][1]-new['hair_core_x_quantiles'][0]
rh=old['hair_core_y_quantiles'][1]-old['hair_core_y_quantiles'][0];nh=new['hair_core_y_quantiles'][1]-new['hair_core_y_quantiles'][0]
scale=math.sqrt((rw/nw)*(rh/nh));assert .91<scale<.96
tx=old['hair_core_centroid'][0]-scale*new['hair_core_centroid'][0]
ty=((old['hair_core_centroid'][1]-scale*new['hair_core_centroid'][1])+2*(old['chin_lower_skin_centroid'][1]-scale*new['chin_lower_skin_centroid'][1]))/3

r,g,b=U[:,:,:3].astype(float).transpose(2,0,1);alpha=U[:,:,3]>0
collar_roi=(xx>560)&(xx<717)&(yy>338)&(yy<412)
white=(r>190)&(g>185)&(b>175)&(np.abs(r-g)<20)&(np.abs(g-b)<20)&collar_roi&alpha
white=binary_opening(white,iterations=1)
yellow=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U[:,:,3]>180)&(yy>345)
yellow=binary_opening(yellow,iterations=1)
# Foreground white collar and puff material/ink stay fixed. The ponytail is
# behind the shoulder in this original and remains behind the same material.
clothes_guard=binary_dilation(white,iterations=2)|binary_dilation(yellow,iterations=2)
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha
neck=skin&(xx>588)&(xx<676)&(yy>329)&(yy<378)
neck=binary_dilation(neck,iterations=2)&alpha&~clothes_guard
hair_color=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=hair_color&alpha&(xx>650)&(xx<790)&(yy>269)&(yy<400)
pony=binary_dilation(pony,iterations=2)&alpha&~clothes_guard
head=(alpha&(xx>480)&(xx<790)&(yy<346))|neck|pony
head&=~clothes_guard
# Fill only interior ownership holes, never shirt/white collar material.
head=binary_fill_holes(head)&alpha&~clothes_guard
oldhead=np.zeros_like(U);oldhead[head]=U[head]
Image.fromarray(oldhead).save(F/'079_own_complete_head_hair_face_ponytail_neck_source.png')
Image.fromarray(np.uint8(head)*255).save(F/'source_complete_head_neck_semantic_mask.png')

def amount(x,y):
 # Exact lower collar attachment follows the actual oblique neck opening.
 # Uniform head scale above the neck; smooth C1 decay to identity at its root.
 boundary=375.-(27./62.)*(x-605.)
 t=np.clip((boundary-y-2.)/24.,0.,1.);smooth=t*t*(3.-2.*t)
 return np.where((x>=590)&(x<=676)&(y>=330),smooth,1.)
x0,y0,x1,y1=480,120,795,410;oy,ox=np.mgrid[y0:y1,x0:x1];sx=(ox-tx)/scale;sy=(oy-ty)/scale
for _ in range(12):
 k=amount(sx,sy);denom=1+k*(scale-1);sx=(ox-k*tx)/denom;sy=(oy-k*ty)/denom
a=oldhead[:,:,3].astype(float)/255.;pm=oldhead[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros((y1-y0,x1-x0,4),np.uint8);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
newhead=np.zeros_like(U);newhead[y0:y1,x0:x1]=patch
Image.fromarray(newhead).save(F/'079_own_head_hair_neck_one_continuous_scale.png')

manifest=json.loads((P/'next_F079_fixed_lower_input_001/INPUT_MANIFEST.json').read_text());C=np.array(Image.open(manifest['original_C_rods_layer']).convert('RGBA'))
# Restore the SAME fixed scene shafts beneath the removed head. Then place
# only the transformed own head/neck and retain every existing body pixel.
base=A.copy();base[head]=C[head];B=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(newhead)))
body=(U[:,:,3]>0)&~head
B[body]=A[body]
fixed_collar=clothes_guard&(U[:,:,3]>0);B[fixed_collar]=A[fixed_collar]
anchor=head&(amount(xx,yy)==0);B[anchor]=A[anchor]
# Limit all changes to the union of actual old/new head ownership. C geometry
# is unchanged; only its visibility through the scaled head silhouette moves.
domain=head|(newhead[:,:,3]>0);B[~domain]=A[~domain]
final=F/'F079_own_head_neck_volume_closed_candidate.png';Image.fromarray(B).save(final)
Image.fromarray(np.uint8(domain)*255).save(F/'actual_changed_domain_head_neck_and_C_occlusion_only.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,mag in [('neck_collar',(555,325,712,402),3),('head_neck',(490,130,790,405),2)]:
 c=bg.crop(box).convert('RGB');c.save(F/f'actual_{name}_1x.png');c.resize((c.width*mag,c.height*mag),Image.Resampling.NEAREST).save(F/f'actual_{name}_{mag}x.png')
refbg=Image.new('RGBA',(W,H),'#bdc1c4');refbg.alpha_composite(Image.open(ref).convert('RGBA'));box=(490,130,790,405);pair=Image.new('RGB',(600,275));pair.paste(refbg.crop(box).convert('RGB'),(0,0));pair.paste(bg.crop(box).convert('RGB'),(300,0));pair.save(F/'076_left_repaired079_right_head_neck_1x.png')
diff=np.any(A!=B,axis=2)
assert not np.any(diff&~domain) and not np.any(diff&body) and not np.any(diff&fixed_collar)
assert not np.any(diff&(yy>=405)) and not np.any(diff&(xx<480))
report={'status':'ONE_ZERO_CALL_F079_OWN_COMPLETE_HEAD_HAIR_NECK_VOLUME_CLOSURE_ASTRA_GATE_PENDING','new_image_calls':0,'source079_commit':'36e68c61e26593288742eadf5981a87e54fd6407','source079_file':str(source),'source079_sha256':sha(source),'reference076_file':str(ref),'reference076_sha256':sha(ref),'scale_complete_head_hair_face_ponytail':scale,'uniform_head_translation_xy':[tx,ty],'head_scale_method':'geometric mean of measured primary hair width/height ratios; hair-center x and hair/chin y constraints; no strand or tail volume used','neck_method':'same inverse warp, C1 smooth decay to identity within 24px above actual oblique collar attachment; no pasted old head, feature moves, horizontal crop or color seam','head_neck_resampling_count':1,'own079_face_expression_hair_ponytail_flower_retained':True,'source076_pixels_pasted':False,'fixed_body_and_collar_RGBA_changes':int((diff&body).sum()),'outside_head_neck_C_occlusion_domain_RGBA_changes':int((diff&~domain).sum()),'all_y405_plus_arms_torso_skirt_legs_grandma_RGBA_changes':int((diff&(yy>=405)).sum()),'all_x480_minus_palms_T_rods_RGBA_changes':int((diff&(xx<480)).sum()),'new_head_only_C_visibility_restore_axes_unchanged':True,'final_png':final.name,'final_png_sha256':sha(final),'adopted':False,'propagated':False,'new_exposure_frozen':False,'other_states_prepared':False}
(F/'repair_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
