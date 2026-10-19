from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation,distance_transform_edt
import numpy as np,math,json,hashlib,shutil,argparse
R=Path(__file__).resolve().parent;B=R.parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();O=Path(args.out) if args.out else R
for d in ['sources','layers','masks','reference_native','inputs_1280x1536','geometry','requests','qa']: (O/d).mkdir(parents=True,exist_ok=True)
files={'F063_LOCKED.png':B/'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png','TRUE_visible_prop.png':B/'F063_real_prop_pixel_plate_DIAGNOSTIC_20261019/layers/FE70_whole_visible_prop_SINGLE_RIGID_transform.png','NEAR_actual_skin.png':B/'F063_zero_call_semantic_reintegration_20261019/masks/NEW_complete_near_skin_chain_FRONT_of_prop.png','HEAD_guard.png':B/'F063_zero_call_semantic_reintegration_20261019/masks/KEEP_actual044_head_neck_complete_collar.png','SKIRT_guard.png':B/'F063_zero_call_semantic_reintegration_20261019/masks/KEEP_actual044_skirt_material.png','PROP_original.png':B/'F063_real_prop_pixel_plate_DIAGNOSTIC_20261019/layers/FE70_real_visible_prop_ONLY_original_coordinates.png','SLIDER_original.png':B/'F063_real_prop_pixel_plate_DIAGNOSTIC_20261019/masks/SOURCE_FE70_visible_slider_actual_material.png'}
# Snapshots make replay independent of mutable root outputs.
for n,p in files.items():
 sp=R/'sources'/n
 if not sp.exists(): shutil.copyfile(p,sp)
 if O!=R: shutil.copyfile(sp,O/'sources'/n)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n):return Image.open(R/'sources'/n).convert('RGBA')
src=load('F063_LOCKED.png');a=np.array(src);H,W=a.shape[:2];y,x=np.indices((H,W));sz=src.size
assert sha(R/'sources/F063_LOCKED.png')=='0abc3fd9cfcf7964f825ac7be0227fb9f588da709809f6d15362063741e545ef'
def ms(n):return np.array(Image.open(R/'sources'/n).convert('L'))>0
near=ms('NEAR_actual_skin.png');hg=ms('HEAD_guard.png');sg=ms('SKIRT_guard.png');prop=load('TRUE_visible_prop.png');pa=np.array(prop)[:,:,3]>=128
warm=(a[:,:,0]>160)&(a[:,:,0]>a[:,:,1]+16)&(a[:,:,1]>a[:,:,2]+8)&(a[:,:,2]>75)&(a[:,:,3]>=16);la,_=label(warm);far=binary_dilation(binary_fill_holes(la==la[765,1000]),iterations=2)&(a[:,:,3]>0)
oldW=np.array([1092.,694.]);P=np.array([1138.,643.]);hand=far&(((x-oldW[0])*.84+(y-oldW[1])*(-.54))>=0)
handim=Image.fromarray(np.where(hand[:,:,None],a,0).astype('uint8'))
th=math.radians(15);M=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);t=P-M@P+[30,-20];iv=M.T;it=-iv@t
nh=handim.transform(sz,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0);ha=np.array(nh)[:,:,3]>=128;NW=M@oldW+t
# Projected visible source-segment proxies, never an anatomical bone claim.
cuff=np.array([970.,744.]);oldE=np.array([995.,780.]);u=np.linalg.norm(oldE-cuff);v=np.linalg.norm(oldW-oldE);dd=np.linalg.norm(NW-cuff);axis=(NW-cuff)/dd;along=(u*u-v*v+dd*dd)/(2*dd);height=math.sqrt(max(0,u*u-along*along));E=cuff+along*axis+height*np.array([-axis[1],axis[0]])
def poly(points):
 z=Image.new('L',sz);ImageDraw.Draw(z).polygon([tuple(p) for p in points],fill=255);return np.array(z)>0
def save_mask(name,z):Image.fromarray(z.astype('uint8')*255).save(O/'masks'/name)
oldfar=poly([(919,676),(981,673),(1035,713),(1110,681),(1240,623),(1250,693),(1136,746),(1022,807),(957,806),(916,754)])|far
oldfar&=~(near|hg|sg|(np.array(prop)[:,:,3]>0))
# Deliberate empty old-arm area, not invented yellow clothing.
base=a.copy();base[oldfar]=0;A=Image.fromarray(base)
vol=Image.new('RGBA',sz);vd=ImageDraw.Draw(vol)
def capsule(p,q,rp,rq,color):
 p=np.array(p);q=np.array(q);d=q-p;n=np.array([-d[1],d[0]])/np.linalg.norm(d)
 vd.polygon([tuple(p+n*rp),tuple(q+n*rq),tuple(q-n*rq),tuple(p-n*rp)],fill=color,outline='#294b68')
 for z,r in [(p,rp),(q,rq)]:vd.ellipse((z[0]-r,z[1]-r,z[0]+r,z[1]+r),fill=color,outline='#294b68',width=2)
root=np.array([945.,695.]);capsule(root,cuff,34,31,(101,163,202,255));capsule(cuff,E,31,30,(101,163,202,255));capsule(E,NW,30,25,(119,182,218,255))
# Rear technical arm; original near chain remains the foreground owner.
A.alpha_composite(vol);A.alpha_composite(nh)
front=np.zeros_like(a);front[near]=a[near];A.alpha_composite(Image.fromarray(front))
# Existing final063 composed prop/neargrip is fixed; pureprop never pasted back.
# The pure prop is MEASUREMENT ONLY. Inherit final063 composed ownership exactly,
# so no old hand-hidden cut edge or competing cylinder neck can reappear.
final_foreground=(np.array(prop)[:,:,3]>0)|near
assembled=np.array(A);assembled[final_foreground]=a[final_foreground];A=Image.fromarray(assembled)
va=np.array(vol)[:,:,3]>0
nearop=poly([(960,548),(1020,530),(1086,544),(1148,583),(1146,637),(1104,668),(1010,652),(956,627)])
slmask=np.array(Image.open(R/'sources/SLIDER_original.png').convert('L'))>0
unitM=np.array([[.19923110917411352,-.9799525320836987],[.9799525320836987,.19923110917411352]]);unitt=np.array([1284.0792113302323,-606.8253880588991]);ui=unitM.T;ut=-ui@unitt
sl=Image.fromarray(slmask.astype('uint8')*255).transform(sz,Image.Transform.AFFINE,(*ui[0],ut[0],*ui[1],ut[1]),Image.Resampling.NEAREST,fillcolor=0);sl=np.array(sl)>0
white=binary_dilation(oldfar|va|(np.array(nh)[:,:,3]>0)|nearop,iterations=8)
# Visible fixed prop excluding actual slider-operation vicinity is protected; not hidden alpha.
fixedprop=(np.array(prop)[:,:,3]>0)&~binary_dilation(sl,iterations=3)
white&=~(hg|sg|fixedprop)
Bim=Image.fromarray(white.astype('uint8')*255).convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
d=ImageDraw.Draw(A);d.text((562,12),'F069 SOFT FULL-ARM / REAL WHOLE-PALM GUIDE — NOT ART',font=font,fill='#286589');d.text((925,822),'Blue = full new far chain; old gesture removed.',font=sm,fill='#65b5e7')
C=A.copy();cd=ImageDraw.Draw(C);chain=[root,cuff,E,NW]
cd.line([tuple(p) for p in chain],fill='#d63e91',width=3)
for p in chain:cd.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#d63e91')
cd.line([(1065,574),(1123.026,598.862)],fill='#c35b79',width=2)
cd.text((975,514),'Whole wrist/palm/thumb roll: NOT yet verified',font=sm,fill='#a5466e')
cd.text((995,838),'Projected chain proxies only; no measured bones.',font=sm,fill='#486985')
D=Image.new('RGBA',sz,(233,238,243,255));dr=ImageDraw.Draw(D);dr.text((566,18),'D — ACTUAL SOURCE MATERIAL ONLY / NOT A POSE TARGET',font=font,fill='#36536b')
def pastecrop(box,xy,scale=1):
 c=src.crop(box)
 if scale!=1:c=c.resize((round(c.width*scale),round(c.height*scale)),Image.Resampling.LANCZOS)
 D.alpha_composite(c,xy)
pastecrop((550,0,1010,540),(565,55),.68);pastecrop((920,620,1255,810),(570,470),1.45);pastecrop((970,535,1275,660),(980,75),1)
dr.text((570,780),'Original full far arm/palm material; no old gesture in A.',font=font,fill='#36536b');dr.text((980,235),'Current full grip/slider material only.',font=sm,fill='#36536b');dr.text((980,258),'Thumb is NOT proven to reach the key.',font=sm,fill='#a34b6b')
# Crop is the accepted current063 pixel-plate canvas; output transform remains one uniform resize.
crop=(550,0,1320,924); tool=(1280,1536)
for n,z in [('A',A),('B',Bim),('C',C),('D',D)]:
 z.crop(crop).save(O/f'reference_native/{n}_F069_SOFT_NOT_FROZEN_native770x924.png');z.crop(crop).resize(tool,Image.Resampling.NEAREST if n=='B' else Image.Resampling.LANCZOS).save(O/f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png')
nh.save(O/'layers/whole_actual_palm_R15_translate30_minus20_SOFT.png');handim.save(O/'layers/source_whole_palm_and_full_fingers.png');vol.save(O/'layers/full_far_arm_BLUE_NOT_ART.png')
for n,z in [('SOURCE_whole_palm_full_fingers.png',hand),('REMOVE_old_far_arms_and_hand_gesture.png',oldfar),('F069_full_far_chain_and_near_wrist_palm_operation_WHITE.png',white),('HARD_actual_head_skirt_only.png',hg|sg),('HARD_visible_prop_except_slider_operation.png',fixedprop)]:save_mask(n,z)
for tone,col in [('gray',(215,222,230,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1280,768),(225,231,238));sd=ImageDraw.Draw(sheet)
 for j,n in enumerate('ABCD'):
  z=Image.open(O/f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png').convert('RGBA');bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);sheet.paste(bg.resize((320,384)).convert('RGB'),(j*320,0))
 for j,box in enumerate([(920,660,1265,810),(1055,575,1270,710)]):
  z=A.crop(box);bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);bg=bg.resize((640,320),Image.Resampling.NEAREST);sheet.paste(bg.convert('RGB'),(j*640,430))
 sd.text((12,394),'SOFT contact only: full pad first-touch; fingers roll down. Near full-hand key reach remains unproved.',font=font,fill='#36536b');sheet.save(O/f'qa/four_inputs_and_full_pad_contact_{tone}.png')
# Actual dark lens emitter index, not nominal axis endpoint and not a new light drawing.
lenssource=np.array([1133.03882756,285.65702322]);lens=unitM@lenssource+unitt;L=np.array([1227.0002384706622,562.9985264074178]);T=np.array([858.3388552980175,636.9294709248006]);uaxis=(L-T)/np.linalg.norm(L-T)
em=src.copy();ed=ImageDraw.Draw(em);ed.ellipse((lens[0]-5,lens[1]-5,lens[0]+5,lens[1]+5),outline='#55b6ed',width=2);ed.line([tuple(lens),tuple(lens+uaxis*60)],fill='#55b6ed',width=2);e=em.crop((1090,520,1300,680));bg=Image.new('RGBA',e.size,(35,43,52,255));bg.alpha_composite(e);bg.resize((840,640),Image.Resampling.NEAREST).save(O/'qa/F073_actual_DARK_lens_emitter_index_NOT_ON.png')
ov=ha&pa;yy,xx=np.where(ov);near128=np.array(Image.open(R/'sources/NEAR_actual_skin.png').convert('L'))>=128;g=float(distance_transform_edt(~near128)[ha].min());contacts=np.stack([xx,yy],axis=1).tolist()
def bbox(z):
 yy,xx=np.where(z);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
info={'status':'SOFT_GROUP_INPUT_REFERENCE_NOT_FROZEN_NO_CALL','mother_sha256':sha(R/'sources/F063_LOCKED.png'),'crop_native':list(crop),'tool_uniform_scale':128/77,'tool_inverse':'77/128 + [550,0]','whole_hand_only_transform':{'angle_screen_y_down_deg':15,'scale':1,'pivot_visible_surface_proxy':[1138,643],'post_rotation_translation':[30,-20],'matrix':M.tolist(),'translation':t.tolist(),'bicubic_AA_resampling':True,'no_individual_finger_transform':True},'full_far_chain':{'own_sleeve_soft_root':root.tolist(),'visible_cuff_proxy':cuff.tolist(),'elbow_soft':E.tolist(),'wrist_soft':NW.tolist(),'source_projected_segments':[float(u),float(v)],'note':'Manual 2D visible segment proxies, not anatomical bone lengths; all new chain must be drawn coherently.'},'alpha128_material_contact':{'whole_hand_true_prop_overlap_pixels':int(ov.sum()),'xy':contacts,'contact_source_xy':[list(iv@(np.array(q)-t)) for q in contacts],'interpretation':'First raster contact is proximal palm heel/pad surface, not distal fingers; no pressure/thickness/ownership acceptance inferred. All fingers remain one source transform.','whole_hand_to_current_near_grip_min_distance_native':g,'A_final063_prop_and_near_grip_inheritance_RGBA_differences':int(np.any(np.array(A)[final_foreground]!=a[final_foreground],axis=1).sum()),'current_near_grip_overlap_pixels':int((ha&near128).sum())},'near_operation_gate':{'visible_thumb_tip_manual':[1065,574],'visible_slider_material_centroid':[1123.02601904,598.86240543],'distance_2d_native':float(np.linalg.norm(np.array([1065,574])-np.array([1123.02601904,598.86240543]))),'verified_reach':False,'whole_grip_30_to45_axial_shift':'possible SOFT redraw study only, NOT applied or frozen; current063 unchanged','requirement':'Whole wrist/palm/thumb root and full grip must roll/regrip coherently; never stretch isolated thumb or move slider. Actual drawn069 must prove reach and far support ownership.'},'white_bbox':bbox(white),'guard_overlap_pixels':{'head_skirt':int((white&(hg|sg)).sum()),'fixed_visible_prop':int((white&fixedprop).sum())},'F073_dependency':{'must_use_future_accepted_069_mother':True,'first_ON_frames':[73,76],'TRANSIT_dark_frames':[69,72],'actual_dark_lens_source_center':lenssource.tolist(),'actual063_dark_lens_reference_center':lens.tolist(),'direction_L_minus_T_unit':uaxis.tolist(),'source_lens_area2627_bbox':[1080,270,1187,302],'meaning':'Actual dark neutral lens area fit reference only, not exact optical/mechanical measurement. Existing white reflections remain OFF.','new_light_not_drawn':True},'intermediate_reference_need':'One complete hand/rigid-lamp/full-arms turning reference if Astra requests; no fake interpolation and no change to058x5+063x6.', 'remaining_gates':['Root/Astra review far pad/forearm/ownership target; raster6pixel contact is not palm-load acceptance.','Near whole-hand/thumb-root actual operation reach still open, explicitly not passed.','069 actual image, natural far chain and thumb operation must pass before073 inputs are frozen.','No verified mechanical end stops; forward push is toward true lamp end.'],'calls':0}
(O/'geometry/F069_SOFT_contact_and_F073_dependencies.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
prompt='Prepare F069 (frames69–72, TRANSIT and entirely dark) from image A. A is a NOT_ART full-arm/palm technical target, not finished anatomy. B identifies the complete far sleeve/arm/wrist/palm and near whole-wrist/palm/thumb-root operation region. C repeats the same composition with soft projected chain indices. D supplies actual source identity and materials only; its old far-hand gesture is not a target.\n\nDraw one continuous far LEFT sleeve-to-elbow-to-wrist-to-whole-palm chain, rooted in its own sleeve behind the near forearm. The palm heel/pad must genuinely support the front cylinder with full thickness, while the fingers roll under with explicit front/back ownership. The whole source palm is a soft R+15 degree placement, not a rigid anatomy constraint or proof of support. Do not retain the old competing far hand or a cut wrist.\n\nDraw the near complete wrist/palm/thumb root and gripping fingers coherently so the thumb naturally operates the actual visible slider toward the lamp end. Current thumb-to-key reach is NOT verified. Solve it through a natural whole-hand roll or necessary small whole-grip adjustment, not an isolated stretched thumb, moved switch or finger bridge. Keep the full rigid torch scale, axis, source materials and fixed identity, collar and skirt. No light, no additional limbs, no guide colors or labels in the eventual drawing. This draft is not frozen and no generation is authorized.\n'
(O/'requests/F069_prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt)
(O/'requests/F073_dependency_prompt_DRAFT_ONLY.txt').write_text('Use only the future accepted actual069 drawing as mother. Keep genuine palm-pad support and complete hand/arm ownership. F073–076 is the first ON/light interval;069–072 remains dark. Finish the coherent whole-thumb/slider action only after actual069 operation geometry is accepted. The actual dark lens-area reference, not nominalL, defines a soft emitter fit; light travels along actualL-minus-T. Preserve existing dark-state white reflections as reflections. No073 input or request may freeze before069 acceptance. No generation authorized.\n')
(O/'requests/arguments_PREPARED_NOT_FROZEN_NOT_CALLED.json').write_text(json.dumps({'status':'DRAFT_INPUT_REFERENCE_ONLY_NO_CALL_PERMISSION','images':[f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png' for n in 'ABCD'],'prompt_file':'F069_prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt','frozen':False},indent=2)+'\n')
(O/'README.md').write_text('F069/F073 group input reference only; ZERO GENERATION, pending root/Astra review.\n\nMother063 is final0abc3fd9. A has one new complete far-arm blue NOT_ART volume and the complete real palm rolled+15deg then translated(+30,-20); the old far gesture is removed. The6 alpha128 contact pixels are palm heel first-touch around1126..1137/y616..618; currentneargrip air3.61native and0overlap. These are technical raster diagnostics, not pressure, thickness, five-finger or anatomy acceptance.\n\nNear whole wrist/palm/thumb-root natural reach is explicitly unresolved; currentgrip is source context, not a frozen069 gesture. No isolated thumb bridge was drawn. B covers full old/new far chain and necessary complete near operation region; fixed real prop is protected except actual slider operation area. Projected far-chain proxies are not measured bones. All blue/labels must be replaced by actual drawing.\n\n073 depends on an accepted actual069 mother.069x4 stays dark;073x4 first ON;077x8 confirms with wholehead;085x11 steady bright. Actual dark-lens emitter fit is archived; no light is drawn and no mechanical endstop is claimed.058x5→063x6 remains unchanged. This is a group reference and draft, not a frozen request.\n')
manifest={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['manifest.json','replay_check.json']}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'A':manifest['inputs_1280x1536/A_F069_PREPARED_NOT_FROZEN_1280x1536.png'],'B':manifest['inputs_1280x1536/B_F069_PREPARED_NOT_FROZEN_1280x1536.png'],'contact':len(contacts),'near_gap':g,'emitter':lens.tolist(),'elbow':E.tolist()}))
