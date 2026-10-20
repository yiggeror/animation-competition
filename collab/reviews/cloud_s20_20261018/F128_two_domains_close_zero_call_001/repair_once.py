"""Astra-authorized F128 two-domain zero-call closure, one candidate only."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_erosion,binary_opening,binary_fill_holes,label,map_coordinates
F=Path(__file__).resolve().parent; P=F.parent
S=P/'next_F128_mid_roll_input_001/character_four_inputs_001/generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=S/'F128_uniform_registered_whole_native_upper_fixed_full_lower_CANDIDATE.png'
assert sha(source)=='0abeac189e8894f263291a3018446beccf0d55c4fe02f9b6cd85ca9ae97511aa'
shutil.copyfile(source,F/'source_d240ffae_UNMODIFIED_candidate.png')
A=np.array(Image.open(source).convert('RGBA'))
U=np.array(Image.open(S/'registered_complete_new_upper_whole_skirt_short_guides_UNREPAIRED.png').convert('RGBA'))
H,W=A.shape[:2]; yy,xx=np.indices((H,W)); r,g,b=U[:,:,:3].astype(float).transpose(2,0,1)
C=np.array(Image.open(S.parent/'fixed_original_C_rods_scene_layer.png').convert('RGBA'))
measure=json.loads((F/'measurements_before.json').read_text())
scale=measure['selected_uniform_own_head_scale']; pivot=np.array(measure['pivot_current_actual_neck_collar_contact'])
assert 1.10<scale<1.16
tx,ty=pivot-scale*pivot

# Domain 1: only the old NATIVE painted guide ink outside actual own skin.
# The mechanism's real finite A/B axes are not part of this raster cleanup.
skin=(U[:,:,3]>20)&(r>165)&(g>90)&(b>g*.65)&(r>g+12)
skin=binary_fill_holes(binary_opening(skin,iterations=1))
cc,_=label(binary_dilation(skin,iterations=2)); ids=[int(cc[421,422]),int(cc[529,480])]
assert ids[0]>0 and ids[1]>0 and ids[0]!=ids[1]
palms_guard=np.zeros((H,W),bool)
for side,idx in zip(['R','L'],ids):
    guard=binary_fill_holes(binary_erosion(cc==idx,iterations=1))&(U[:,:,3]>0)
    assert guard.sum()>4000
    palms_guard|=guard
    Image.fromarray(np.uint8(guard)*255).save(F/f'complete_native_{side}_arm_palm_skin_ink_protection_mask.png')
reg=json.loads((S/'registration_and_protection.json').read_text())
matrix=np.array(reg['source_to_final_matrix_2x3'])
transform=lambda p:matrix[:,:2]@np.array(p)+matrix[:,2]
rawobs=json.loads((S/'observed_raw_grip_axis_measurements.json').read_text())
rawpins=rawobs['observed_raw_grip_landmarks']
def corridor(a,z,halfwidth):
    a=np.array(a); z=np.array(z); v=z-a; length=np.linalg.norm(v); v/=length
    along=(xx-a[0])*v[0]+(yy-a[1])*v[1]
    dist=abs((xx-a[0])*v[1]-(yy-a[1])*v[0])
    return (dist<halfwidth)&(along>-5)&(along<length+2)
areas=np.zeros((H,W),bool)
for xstart,axis,pin in zip([454.,516.],rawobs['axes_y_mx_b'],rawpins):
    q=[xstart,axis[0]*xstart+axis[1]]
    areas|=corridor(transform(q),transform(pin),4.5)
areas|=(xx>=478)&(xx<=507)&(yy>=547)&(yy<=563)
wood=(U[:,:,3]>0)&(r>70)&(g>40)&(r>g+10)&(b<g*.74)
wood=binary_dilation(wood&areas,iterations=1)
erase=areas&wood&(U[:,:,3]>0)&~palms_guard
clean=U.copy(); clean[erase]=0
Image.fromarray(np.uint8(erase)*255).save(F/'domain1_old_exterior_painted_guides_removal_mask.png')
Image.fromarray(clean).save(F/'native_upper_exterior_painted_guides_only_cleared.png')

# Domain 2: own complete head, face, hair, flower, pony and continuous neck.
# Reference F120 pixels are never used for this image; they supplied metrics.
alpha=U[:,:,3]>0
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>575)&(xx<740)&(yy>340)&(yy<430)&alpha
yellow=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U[:,:,3]>180)&(yy>340)
clothes=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(yellow,iterations=1),iterations=2)
neckskin=binary_dilation(skin&(xx>610)&(xx<705)&(yy>335)&(yy<402),iterations=2)&alpha&~clothes
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=binary_dilation(hair&alpha&(xx>700)&(xx<835)&(yy>320)&(yy<450),iterations=2)&alpha&~clothes
head=(alpha&(xx>565)&(xx<835)&(yy<365))|neckskin|pony
head=binary_fill_holes(head)&alpha&~clothes
# Keep complete connected head ownership including its faint outer AA halo.
# Main-head pixels above350 cannot be clothing. Around the lower neck/pony,
# a bounded halo excludes distant thin clothing AA arcs. This also prevents
# stale old head AA pixels from being restored as fixed "body" over new hair.
head_cc,_=label(head&(U[:,:,3]>100)); head_id=int(head_cc[285,625]); assert head_id>0
head=(binary_fill_holes(binary_dilation(head_cc==head_id,iterations=8))|(yy<350))&head
oldhead=np.zeros_like(U); oldhead[head]=U[head]
Image.fromarray(oldhead).save(F/'own128_complete_head_face_all_hair_flower_neck_source.png')
Image.fromarray(np.uint8(head)*255).save(F/'source_complete_head_neck_semantic_mask.png')
cols=np.array(measure['states'][1]['actual_lower_neck_skin_boundary_columns'])
def amount(x,y):
    boundary=np.interp(x,cols[:,0],cols[:,1])
    v=np.clip((boundary-y-1.)/28.,0.,1.); smooth=v*v*(3.-2.*v)
    return np.where((x>=620)&(x<=699)&(y>=345),smooth,1.)
# Whole head/all hair use the identical uniform scale. Only the lower own neck
# continuously decays to identity at its measured curved collar attachment.
x0,y0,x1,y1=545,135,850,465; oy,ox=np.mgrid[y0:y1,x0:x1]
sx=(ox-tx)/scale; sy=(oy-ty)/scale
for _ in range(20):
    k=amount(sx,sy); denominator=1+k*(scale-1)
    sx=(ox-k*tx)/denominator; sy=(oy-k*ty)/denominator
a=oldhead[:,:,3].astype(float)/255; pm=oldhead[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0); wa=wa0.clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,i],[sy,sx],order=3,mode='constant',cval=0) for i in range(3)],2)
patch=np.zeros((y1-y0,x1-x0,4),np.uint8); patch[:,:,3]=np.rint(wa*255).astype('uint8')
patch[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8')
patch[patch[:,:,3]<3]=0
newhead=np.zeros_like(U); newhead[y0:y1,x0:x1]=patch
Image.fromarray(newhead).save(F/'own128_complete_head_all_hair_one_scale_continuous_neck.png')

# Fixed body + fixed underlying C geometry. Old/new head occlusion may differ.
body=(U[:,:,3]>0)&~head&~erase
base=A.copy(); base[erase]=C[erase]; base[head]=C[head]
B=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(newhead)))
B[body]=A[body]
collar=clothes&(U[:,:,3]>0); B[collar]=A[collar]
anchor=head&(amount(xx,yy)==0); B[anchor]=A[anchor]
head_domain=head|(newhead[:,:,3]>0); domain=head_domain|erase
B[~domain]=A[~domain]
# Same correction on the isolated native upper used by final receiving.
closed=clean.copy(); closed[head]=0
closed=np.array(Image.alpha_composite(Image.fromarray(closed),Image.fromarray(newhead)))
closed[body]=U[body]; closed[collar]=U[collar]; closed[anchor]=U[anchor]
Image.fromarray(closed).save(F/'complete_native_upper_whole_skirt_two_domains_closed.png')
final=F/'F128_two_domains_closed_CANDIDATE.png'; Image.fromarray(B).save(final)
diff=np.any(A!=B,axis=2)
for name,mask in [('domain2_complete_head_neck_and_C_occlusion_mask',head_domain),
                  ('two_authorized_domains_mask',domain),('actual_changed_pixels_mask',diff),
                  ('fixed_native_body_collar_arms_whole_skirt_protection_mask',body|collar)]:
    Image.fromarray(np.uint8(mask)*255).save(F/(name+'.png'))
assert not np.any(diff&~domain) and not np.any(diff&body)
assert not np.any(diff&palms_guard) and not np.any(diff&collar)
assert not np.any(diff&(yy>=570)) and not np.any(diff&(xx>=850))
bg=Image.new('RGBA',(W,H),'#bdc1c4'); bg.alpha_composite(Image.fromarray(B))
bg.convert('RGB').save(F/'actual_full_gray_1x.jpg',quality=96)
for name,box,mag in [('palms_cleared_native',(350,345,750,580),3),
                     ('head_neck',(490,125,850,465),2),('neck_collar',(595,335,730,417),4),
                     ('under_hem',(550,620,825,760),2),('support',(480,800,795,935),2)]:
    q=bg.crop(box).convert('RGB');q.save(F/f'actual_{name}_1x.png')
    q.resize((q.width*mag,q.height*mag),Image.Resampling.NEAREST).save(F/f'actual_{name}_{mag}x.png')
ref=Image.open(P/'next_F120_passive_decay_input_001/generation_001/F120_uniform_registered_upper_fixed_full_lower_candidate.png').convert('RGBA')
refbg=Image.new('RGBA',(W,H),'#bdc1c4'); refbg.alpha_composite(ref)
for name,box in [('head_chest',(490,125,850,520)),('upper_hands',(350,125,1020,720))]:
    cw,ch=box[2]-box[0],box[3]-box[1]; pair=Image.new('RGB',(cw*2,ch))
    pair.paste(refbg.crop(box).convert('RGB'),(0,0));pair.paste(bg.crop(box).convert('RGB'),(cw,0))
    pair.save(F/f'120_left_closed128_right_same_canvas_{name}_1x.png')
beforebg=Image.new('RGBA',(W,H),'#bdc1c4');beforebg.alpha_composite(Image.fromarray(A))
box=(490,125,850,465);card=Image.new('RGB',(720,340));card.paste(beforebg.crop(box).convert('RGB'),(0,0));card.paste(bg.crop(box).convert('RGB'),(360,0));card.save(F/'same128_before_left_closed_right_head_neck_1x.png')
report={'status':'ONE_ZERO_CALL_F128_TWO_DOMAIN_CANDIDATE_ACTUAL_ASTRA_GATE_PENDING',
        'new_image_calls':0,'raw_outputs_added':0,'source128_commit':'d240ffaecd878f04f5591815e6b341356f257702',
        'source128_sha256':sha(source),'source128_copy_sha256':sha(F/'source_d240ffae_UNMODIFIED_candidate.png'),
        'reference120_only_used_for_measurements_no_pixels_pasted':True,
        'complete_own_head_face_all_hair_flower_uniform_scale':scale,
        'scale_pivot_own_neck_collar':pivot.tolist(),'added_rotation_deg':0,
        'free_head_translation_added':[0,0],
        'head_neck_resampling_count':1,
        'neck_method':'Same complete own head warp with C1 decay to identity over28px above measured curved own collar root; native collar ink/body fixed.',
        'palms_fingers_wrists_and_complete_arms_RGBA_changes':int((diff&palms_guard).sum()),
        'body_collar_torso_arms_whole_skirt_RGBA_changes':int((diff&(body|collar)).sum()),
        'all_y570_plus_skirt_full_lower_support_RGBA_changes':int((diff&(yy>=570)).sum()),
        'grandma_x850_plus_RGBA_changes':int((diff&(xx>=850)).sum()),
        'outside_two_domains_RGBA_changes':int((diff&~domain).sum()),
        'exterior_old_painted_guides_removed_pixels':int(erase.sum()),
        'true_rod_axes_lengths_endpoints_roots_changed':False,
        'old_painted_guide_removal_not_real_finite_rod_shortening':True,
        'native_surprised_expression_and_upward_attention_retained':True,
        'C_geometry_unchanged_only_head_occlusion_changes':True,
        'final_png':final.name,'final_png_sha256':sha(final),
        'adopted':False,'exposure_frozen':False,'132_opened':False}
(F/'repair_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(F/'FINAL_PNG_SHA256.txt').write_text(sha(final)+'  '+final.name+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
