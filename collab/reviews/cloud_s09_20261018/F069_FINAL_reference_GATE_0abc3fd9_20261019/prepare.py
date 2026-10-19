from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation,distance_transform_edt
import numpy as np,math,json,hashlib,shutil,argparse
R=Path(__file__).resolve().parent;B=R.parent
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
# One UNIQUE new double-arm/whole-grip technical target. No old near thumb/grip remains.
oldnear=binary_dilation(near,iterations=2)&(a[:,:,3]>0)&~(hg|sg)
base=a.copy();base[oldfar|oldnear]=0;A=Image.fromarray(base)
vol=Image.new('RGBA',sz);vd=ImageDraw.Draw(vol)
def capsule(p,q,rp,rq,color):
 p=np.array(p);q=np.array(q);d=q-p;n=np.array([-d[1],d[0]])/np.linalg.norm(d)
 vd.polygon([tuple(p+n*rp),tuple(q+n*rq),tuple(q-n*rq),tuple(p-n*rp)],fill=color,outline='#294b68')
 for z,r in [(p,rp),(q,rq)]:vd.ellipse((z[0]-r,z[1]-r,z[0]+r,z[1]+r),fill=color,outline='#294b68',width=2)
root=np.array([945.,695.]);capsule(root,cuff,34,31,(101,163,202,255));capsule(cuff,E,31,30,(101,163,202,255));capsule(E,NW,30,25,(119,182,218,255));A.alpha_composite(vol);A.alpha_composite(nh)
# Only already-final063 VISIBLE prop pixels may return. Never paste pureprop old cut edges.
actualprop=(np.array(prop)[:,:,3]>0)&~oldnear
assembled=np.array(A);assembled[actualprop]=a[actualprop];A=Image.fromarray(assembled)
# Barrel behind the old grasp is UNKNOWN. A flat blue design-only surface marks the
# missing real source, never claims a recovered red pixel or measured hidden contour.
L=np.array([1227.0002384706622,562.9985264074178]);T=np.array([858.3388552980175,636.9294709248006]);axisunit=(L-T)/np.linalg.norm(L-T);normal=np.array([-axisunit[1],axisunit[0]])
ax=(x-T[0])*axisunit[0]+(y-T[1])*axisunit[1];nn=(x-T[0])*normal[0]+(y-T[1])*normal[1]
unknownbarrel=oldnear&(ax>=135)&(ax<=260)&(abs(nn)<=29)
uim=Image.new('RGBA',sz);uz=np.array(uim);uz[unknownbarrel]=[83,115,142,255];uim=Image.fromarray(uz);A.alpha_composite(uim)
nearvol=Image.new('RGBA',sz);nd=ImageDraw.Draw(nearvol)
def ncap(p,q,rp,rq,col=(116,180,220,255)):
 p=np.array(p);q=np.array(q);v=q-p;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
 nd.polygon([tuple(p+n*rp),tuple(q+n*rq),tuple(q-n*rq),tuple(p-n*rp)],fill=col,outline='#294b68')
 for z,r in[(p,rp),(q,rq)]:nd.ellipse((z[0]-r,z[1]-r,z[0]+r,z[1]+r),fill=col,outline='#294b68',width=2)
nearroot=np.array([705.,666.]);nearE=np.array([790.,730.]);nearW=np.array([1035.,630.]);G063=np.array([1049.533,598.588]);G069=G063+35*axisunit
ncap(nearroot,nearE,32,36);ncap(nearE,nearW,36,25)
# Full inward-rolled palm and thumb-root mass, with four curled whole fingers.
nd.polygon([(1027,611),(1060,570),(1083,560),(1105,570),(1110,592),(1105,620),(1091,633),(1070,639),(1050,640),(1032,640)],fill=(116,180,220,255),outline='#294b68',width=2)
ncap((1058,609),(1080,591),23,25)
for k,(p,q) in enumerate([((1088,600),(1108,612)),((1088,608),(1106,620)),((1080,616),(1098,627)),((1070,622),(1088,630))]):ncap(p,q,9,8,(103+5*k,168+4*k,210+3*k,255))
# Thumb emerges from the SAME whole-palm root; it is not an isolated stretched source finger.
ncap((1080,580),(1102,590),17,15);ncap((1102,590),(1123,599),13,11)
A.alpha_composite(nearvol)
# Head/collar/skirt source materials stay fixed; hidden far alpha never cuts near foreground.
arr=np.array(A);arr[hg|sg]=a[hg|sg];A=Image.fromarray(arr)
final_foreground=actualprop&~(np.array(nearvol)[:,:,3]>0)&~hg&~sg
va=np.array(vol)[:,:,3]>0
nearop=poly([(960,548),(1020,530),(1086,544),(1148,583),(1146,637),(1104,668),(1010,652),(956,627)])
slmask=np.array(Image.open(R/'sources/SLIDER_original.png').convert('L'))>0
unitM=np.array([[.19923110917411352,-.9799525320836987],[.9799525320836987,.19923110917411352]]);unitt=np.array([1284.0792113302323,-606.8253880588991]);ui=unitM.T;ut=-ui@unitt
sl=Image.fromarray(slmask.astype('uint8')*255).transform(sz,Image.Transform.AFFINE,(*ui[0],ut[0],*ui[1],ut[1]),Image.Resampling.NEAREST,fillcolor=0);sl=np.array(sl)>0
actionfront=poly([(663,544),(922,520),(1100,540),(1158,580),(1270,618),(1265,710),(1080,815),(948,800),(815,777),(674,751)])
white=binary_dilation(oldfar|oldnear|va|(np.array(nearvol)[:,:,3]>0)|(np.array(nh)[:,:,3]>0)|nearop|unknownbarrel|actionfront,iterations=8)
# Visible fixed prop excluding actual slider-operation vicinity is protected; not hidden alpha.
fixedprop=actualprop&~binary_dilation((np.array(nearvol)[:,:,3]>0)|sl,iterations=3)
white&=~(hg|sg|fixedprop)
Bim=Image.fromarray(white.astype('uint8')*255).convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
d=ImageDraw.Draw(A);d.text((562,12),'F069 UNIQUE FULL-GRIP + PAD SUPPORT TARGET / NOT ART',font=font,fill='#286589');d.text((925,822),'Blue = full new far chain; old gesture removed.',font=sm,fill='#65b5e7')
C=A.copy();cd=ImageDraw.Draw(C);chain=[root,cuff,E,NW]
cd.line([tuple(p) for p in chain],fill='#d63e91',width=3)
for p in chain:cd.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#d63e91')
cd.line([tuple(p) for p in [nearroot,nearE,nearW,G069]],fill='#874faf',width=3);cd.ellipse((1118,594,1128,604),outline='#a3416c',width=2)
cd.text((975,514),'WHOLE grip +35 toward head, inward roll; SOFT',font=sm,fill='#a5466e')
cd.text((995,838),'Projected chain proxies only; no measured bones.',font=sm,fill='#486985')
D=Image.new('RGBA',sz,(233,238,243,255));dr=ImageDraw.Draw(D);dr.text((566,18),'D — ACTUAL SOURCE MATERIAL ONLY / NOT A POSE TARGET',font=font,fill='#36536b')
def pastecrop(box,xy,scale=1):
 c=src.crop(box)
 if scale!=1:c=c.resize((round(c.width*scale),round(c.height*scale)),Image.Resampling.LANCZOS)
 D.alpha_composite(c,xy)
pastecrop((550,0,1010,540),(565,55),.68);pastecrop((712,510,802,587),(1040,95),2);pastecrop((760,540,840,600),(1040,300),2)
dr.text((570,780),'Identity / internal cloth only. NO competing hand/arm pose.',font=font,fill='#36536b');dr.text((980,235),'REAL internal cloth / ink / palette only.',font=sm,fill='#36536b');dr.text((980,258),'No old grasp or receiver gesture in D.',font=sm,fill='#a34b6b')
# Crop is the accepted current063 pixel-plate canvas; output transform remains one uniform resize.
crop=(550,0,1320,924); tool=(1280,1536)
for n,z in [('A',A),('B',Bim),('C',C),('D',D)]:
 z.crop(crop).save(O/f'reference_native/{n}_F069_SOFT_NOT_FROZEN_native770x924.png');z.crop(crop).resize(tool,Image.Resampling.NEAREST if n=='B' else Image.Resampling.LANCZOS).save(O/f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png')
nearvol.save(O/'layers/unique_near_whole_grip_BLUE_NOT_ART.png');uim.save(O/'layers/UNKNOWN_barrel_behind_old_grasp_NOT_REAL_RGB.png');nh.save(O/'layers/whole_actual_palm_R15_translate30_minus20_SOFT.png');handim.save(O/'layers/source_whole_palm_and_full_fingers.png');vol.save(O/'layers/full_far_arm_BLUE_NOT_ART.png')
for n,z in [('SOURCE_whole_palm_full_fingers.png',hand),('REMOVE_old_far_arms_and_hand_gesture.png',oldfar),('F069_full_far_chain_and_near_wrist_palm_operation_WHITE.png',white),('HARD_actual_head_skirt_only.png',hg|sg),('HARD_visible_prop_except_slider_operation.png',fixedprop)]:save_mask(n,z)
for tone,col in [('gray',(215,222,230,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1280,768),(225,231,238));sd=ImageDraw.Draw(sheet)
 for j,n in enumerate('ABCD'):
  z=Image.open(O/f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png').convert('RGBA');bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);sheet.paste(bg.resize((320,384)).convert('RGB'),(j*320,0))
 for j,box in enumerate([(920,660,1265,810),(1055,575,1270,710)]):
  z=A.crop(box);bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);bg=bg.resize((640,320),Image.Resampling.NEAREST);sheet.paste(bg.convert('RGB'),(j*640,430))
 sd.text((12,394),'UNIQUE opaque full hand targets; full near palm rolls +35 axially. Actual anatomy/contact must be drawn.',font=font,fill='#36536b');sheet.save(O/f'qa/four_inputs_and_full_pad_contact_{tone}.png')
# Actual dark lens emitter index, not nominal axis endpoint and not a new light drawing.
lenssource=np.array([1133.03882756,285.65702322]);lens=unitM@lenssource+unitt;L=np.array([1227.0002384706622,562.9985264074178]);T=np.array([858.3388552980175,636.9294709248006]);uaxis=(L-T)/np.linalg.norm(L-T)
em=src.copy();ed=ImageDraw.Draw(em);ed.ellipse((lens[0]-5,lens[1]-5,lens[0]+5,lens[1]+5),outline='#55b6ed',width=2);ed.line([tuple(lens),tuple(lens+uaxis*60)],fill='#55b6ed',width=2);e=em.crop((1090,520,1300,680));bg=Image.new('RGBA',e.size,(35,43,52,255));bg.alpha_composite(e);bg.resize((840,640),Image.Resampling.NEAREST).save(O/'qa/F073_actual_DARK_lens_emitter_index_NOT_ON.png')
ov=ha&pa;yy,xx=np.where(ov);near128=np.array(Image.open(R/'sources/NEAR_actual_skin.png').convert('L'))>=128;g=float(distance_transform_edt(~near128)[ha].min());contacts=np.stack([xx,yy],axis=1).tolist()
def bbox(z):
 yy,xx=np.where(z);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
info={'status':'SOFT_GROUP_INPUT_REFERENCE_NOT_FROZEN_NO_CALL','mother_sha256':sha(R/'sources/F063_LOCKED.png'),'crop_native':list(crop),'tool_uniform_scale':128/77,'tool_inverse':'77/128 + [550,0]','whole_hand_only_transform':{'angle_screen_y_down_deg':15,'scale':1,'pivot_visible_surface_proxy':[1138,643],'post_rotation_translation':[30,-20],'matrix':M.tolist(),'translation':t.tolist(),'bicubic_AA_resampling':True,'no_individual_finger_transform':True},'full_far_chain':{'own_sleeve_soft_root':root.tolist(),'visible_cuff_proxy':cuff.tolist(),'elbow_soft':E.tolist(),'wrist_soft':NW.tolist(),'source_projected_segments':[float(u),float(v)],'note':'Manual 2D visible segment proxies, not anatomical bone lengths; all new chain must be drawn coherently.'},'alpha128_material_contact':{'whole_hand_true_prop_overlap_pixels':int(ov.sum()),'xy':contacts,'contact_source_xy':[list(iv@(np.array(q)-t)) for q in contacts],'interpretation':'First raster contact is proximal palm heel/pad surface, not distal fingers; no pressure/thickness/ownership acceptance inferred. All fingers remain one source transform.','whole_hand_to_current_near_grip_min_distance_native':g,'A_unoccluded_final063_visible_prop_inheritance_RGBA_differences':int(np.any(np.array(A)[final_foreground]!=a[final_foreground],axis=1).sum()),'current_near_grip_overlap_pixels':int((ha&near128).sum())},'near_operation_gate':{'visible_thumb_tip_manual':[1065,574],'visible_slider_material_centroid':[1123.02601904,598.86240543],'distance_2d_native':float(np.linalg.norm(np.array([1065,574])-np.array([1123.02601904,598.86240543]))),'verified_reach':False,'whole_grip_axial_SOFT_target_native':35,'G063_unchanged':G063.tolist(),'G069_SOFT_new_grip_station':G069.tolist(),'near_elbow_soft':nearE.tolist(),'near_wrist_soft':nearW.tolist(),'current063_itself_changed':False,'requirement':'Whole wrist/palm/thumb root and full grip must roll/regrip coherently; never stretch isolated thumb or move slider. Actual drawn069 must prove reach and far support ownership.'},'white_bbox':bbox(white),'guard_overlap_pixels':{'head_skirt':int((white&(hg|sg)).sum()),'fixed_visible_prop':int((white&fixedprop).sum())},'F073_dependency':{'must_use_future_accepted_069_mother':True,'first_ON_frames':[73,76],'TRANSIT_dark_frames':[69,72],'actual_dark_lens_source_center':lenssource.tolist(),'actual063_dark_lens_reference_center':lens.tolist(),'direction_L_minus_T_unit':uaxis.tolist(),'source_lens_area2627_bbox':[1080,270,1187,302],'meaning':'Actual dark neutral lens area fit reference only, not exact optical/mechanical measurement. Existing white reflections remain OFF.','new_light_not_drawn':True},'intermediate_reference_need':'One complete hand/rigid-lamp/full-arms turning reference if Astra requests; no fake interpolation and no change to058x5+063x6.', 'remaining_gates':['Root/Astra review far pad/forearm/ownership target; raster6pixel contact is not palm-load acceptance.','Near whole-hand/thumb-root actual operation reach still open, explicitly not passed.','069 actual image, natural far chain and thumb operation must pass before073 inputs are frozen.','No verified mechanical end stops; forward push is toward true lamp end.'],'calls':0}
(O/'geometry/F069_SOFT_contact_and_F073_dependencies.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
prompt='Prepare F069 (frames69–72, TRANSIT and entirely dark) from image A. A is a NOT_ART full-arm/palm technical target, not finished anatomy. B identifies the complete far sleeve/arm/wrist/palm and near whole-wrist/palm/thumb-root operation region. C repeats the same composition with soft projected chain indices. D supplies actual source identity and materials only; its old far-hand gesture is not a target.\n\nDraw one continuous far LEFT sleeve-to-elbow-to-wrist-to-whole-palm chain, rooted in its own sleeve behind the near forearm. The palm heel/pad must genuinely support the front cylinder with full thickness, while the fingers roll under with explicit front/back ownership. The whole source palm is a soft R+15 degree placement, not a rigid anatomy constraint or proof of support. Do not retain the old competing far hand or a cut wrist.\n\nDraw the near complete wrist/palm/thumb root and gripping fingers coherently so the thumb naturally operates the actual visible slider toward the lamp end. Current thumb-to-key reach is NOT verified. Solve it through a natural whole-hand roll or necessary small whole-grip adjustment, not an isolated stretched thumb, moved switch or finger bridge. Keep the full rigid torch scale, axis, source materials and fixed identity, collar and skirt. No light, no additional limbs, no guide colors or labels in the eventual drawing. This draft is not frozen and no generation is authorized.\n'
(O/'requests/F069_prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt)
(O/'requests/F073_dependency_prompt_DRAFT_ONLY.txt').write_text('Use only the future accepted actual069 drawing as mother. Keep genuine palm-pad support and complete hand/arm ownership. F073–076 is the first ON/light interval;069–072 remains dark. Finish the coherent whole-thumb/slider action only after actual069 operation geometry is accepted. The actual dark lens-area reference, not nominalL, defines a soft emitter fit; light travels along actualL-minus-T. Preserve existing dark-state white reflections as reflections. No073 input or request may freeze before069 acceptance. No generation authorized.\n')
(O/'requests/arguments_PREPARED_NOT_FROZEN_NOT_CALLED.json').write_text(json.dumps({'status':'DRAFT_INPUT_REFERENCE_ONLY_NO_CALL_PERMISSION','images':[f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png' for n in 'ABCD'],'prompt_file':'F069_prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt','frozen':False},indent=2)+'\n')
(O/'README.md').write_text('F069/F073 group input reference only; ZERO GENERATION, pending root/Astra review.\n\nMother063 is final0abc3fd9. A has one new complete far-arm blue NOT_ART volume and the complete real palm rolled+15deg then translated(+30,-20); the old far gesture is removed. The6 alpha128 contact pixels are palm heel first-touch around1126..1137/y616..618; currentneargrip air3.61native and0overlap. These are technical raster diagnostics, not pressure, thickness, five-finger or anatomy acceptance.\n\nNear whole wrist/palm/thumb-root natural reach is explicitly unresolved; currentgrip is source context, not a frozen069 gesture. No isolated thumb bridge was drawn. B covers full old/new far chain and necessary complete near operation region; fixed real prop is protected except actual slider operation area. Projected far-chain proxies are not measured bones. All blue/labels must be replaced by actual drawing.\n\n073 depends on an accepted actual069 mother.069x4 stays dark;073x4 first ON;077x8 confirms with wholehead;085x11 steady bright. Actual dark-lens emitter fit is archived; no light is drawn and no mechanical endstop is claimed.058x5→063x6 remains unchanged. This is a group reference and draft, not a frozen request.\n')
# FINAL authority overrides every earlier conditional whole-grip wording.
prompt="""Create F069 only, frames 69–72: the supporting palm is established and the second switch push is in TRANSIT, but the flashlight is still entirely dark. Preserve image A's 1280x1536 transparent canvas, common scale and composition. Its parent is the locked actual F063, SHA 0abc3fd9cfcf7964f825ac7be0227fb9f588da709809f6d15362063741e545ef. Do not reinterpret this as a new F063 or illuminate it early.

A contains ONE opaque new two-hand target. Blue is a NOT_ART volume guide, not a finished drawing or measured anatomy. The old near grip/thumb-on-top gesture has intentionally been removed. The full near grip advances approximately 35 native pixels toward the lamp head along the unchanged real cylinder axis, then rolls inward as one coherent wrist, palm, thumb-root and all gripping fingers. The thumb pad must naturally reach the actual black slider while the other fingers wrap underneath the barrel. Draw the whole near sleeve attachment, arm and natural wrist-to-palm connection coherently. Do not stretch an isolated thumb, paste a wrist, retain a competing old hand, move the slider, or move/resize/rotate the lamp to manufacture contact. The action is a whole-grip change in F069; locked F063 remains unchanged. The soft hand volumes indicate intent, not a demand to reproduce the diagram's joints or outlines.

Redraw the far LEFT sleeve-root, upper arm, elbow, forearm, natural wrist and complete supporting palm as one continuous chain from its own sleeve, behind the near arm. Its palm heel/pad supports the red neck/front-cylinder or lamp-head underside, with full palm thickness and lightly wrapping fingers. Fingertip brushing alone is not support. The entire actual palm is rolled as one soft source group; no individual source finger was stretched. Keep the two forearms and hands legible with consistent front/back ownership and no anatomical crossing. Near gripping fingers may appropriately occlude the rear supporting hand; never fuse them or create an extra wrist.

B is the complete semantic action-band reference, including both sleeves/arms, all old/new hand spaces, necessary front-blouse cloth and the revealed cylinder area. It is not an executable hard mask. The dark-blue patch behind the previous grasp explicitly marks UNKNOWN hidden barrel material, not recovered true red pixels or a new physical cylinder neck. Draw that continuous cylinder surface at the same real axis, scale and proportions. C is exactly the same pose with soft construction indices. D supplies actual identity and internal clothing materials only; it contains no alternate hand pose.

Keep the original head, face, neck/collar, stable skirt and unedited body identity. Make natural continuous sleeve/blouse joins throughout the permitted band. Keep the rigid flashlight, cap/head proportions, actual slider housing and axis fixed; the visible key's measured material index is not a certified mechanical end stop. Push toward the lamp end but do not show ON yet. No glow, beam, additional hands, guide colors/text, opaque background or following state. Return one transparent F069 drawing only.
"""
(O/'requests/F069_prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt)
paths=[str((R/f'inputs_1280x1536/{n}_F069_PREPARED_NOT_FROZEN_1280x1536.png').resolve()) for n in 'ABCD']
(O/'requests/arguments_PREPARED_NOT_FROZEN_NOT_CALLED.json').write_text(json.dumps({'status':'FINAL_REFERENCE_GATE_PENDING_ROOT_ASTRA_NOT_CALLED','prompt':prompt,'referenced_image_paths':paths,'transparent_background':True,'requested_outputs':1,'current_calls':0,'permission':'THIS PACKAGE PREPARES INPUTS ONLY; author/root owns all calls','common_inverse':'77/128 + [550,0]'},ensure_ascii=False,indent=2)+'\n')
info['status']='FINAL_REFERENCE_GATE_SOFT_TARGET_PENDING_REVIEW_NO_CALL'
info['authority_latest']='Latest Astra overrides the preceding no-axial-shift message: allow whole near grip35native toward head and inward roll; real axis/key/lamp fixed. Unique opaque new full hand target required. D identity/cloth only. Both full sleeves/front garment may be repaired.063locked mother untouched.'
info['near_operation_gate']['verified_reach']=False
info['near_operation_gate']['meaning']='Blue whole-hand target reaches slider index by whole-palm/root reconstruction; actual native anatomy/contact still must be verified. No old nearhand is left in A, no isolated thumb bridge or source finger stretching.'
info['near_operation_gate']['motion35_axis_unit']=axisunit.tolist()
info['near_operation_gate']['motion35_delta_native']=(35*axisunit).tolist()
info['near_operation_gate']['near_hand_volume_bbox_NOT_ART']=bbox(np.array(nearvol)[:,:,3]>0)
info['near_operation_gate']['near_far_projected_overlap_pixels_SOFT_front_near']=int(((np.array(nearvol)[:,:,3]>=128)&ha).sum())
info['near_operation_gate']['overlap_interpretation']='Small diagram projected overlap is explicitly near in front of far palm/wrist; not claimed anatomy/pressure proof. Actual069 must resolve full finger ownership.'
info['alpha128_material_contact']['whole_hand_to_OLD063_near_grip_min_distance_native']=info['alpha128_material_contact'].pop('whole_hand_to_current_near_grip_min_distance_native')
info['alpha128_material_contact']['OLD063_near_grip_overlap_pixels']=info['alpha128_material_contact'].pop('current_near_grip_overlap_pixels')
info['alpha128_material_contact']['legacy_distance_not_new069_clearance']=True
info['unknown_revealed_barrel']={'mask_pixels':int(unknownbarrel.sum()),'source_real_RGBA_invented':False,'meaning':'Blue hidden-barrel technical surface must be drawn with real final scale; no pureprop oldcut pixels pasted.'}
info['new_geometry_bbox']=bbox(va|(np.array(nearvol)[:,:,3]>0)|(np.array(nh)[:,:,3]>0))
info['remaining_gates']=['Root/Astra reference review and author input freeze before any call.','Actual069 complete near whole-hand slider reach, genuine far pad load and natural continuous arms must pass; blue volume is not five-finger acceptance.','073 follows actual accepted069 with stable support and firstON; no independent pose refreeze implied.']
(O/'geometry/F069_SOFT_contact_and_F073_dependencies.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
(O/'requests/F073_dependency_prompt_DRAFT_ONLY.txt').write_text('Use the actual accepted F069 as the only next mother. Preserve its complete load-bearing far palm, both coherent full hands and all accepted proportions/axis/rigid torch. Finish the switch push naturally at the real visible slider; F073–076 is the first ON/light interval while069–072 remains dark. Keep the hands and support stable. The actual dark-lens area reference center(1229.88547047,560.41064554)native, fitted from true original visible lens pixels, is a soft emitter reference; use the actual accepted069 lens face and axisL-minus-T. Do not treat existing white reflections as earlierON. Preserve the accepted body and frame composition. No073 A is frozen before actual069 adoption. This is a batch dependency draft, not a request executed here.\n')
(O/'requests/AUTHORITY_latest_supersedes_no_axial_shift.txt').write_text('Astra latest via root: allow near whole grip30–40native, choose35SOFT, along fixed real axis toward head with natural inward roll. Whole wrist/palm/thumb-root/fingers must be one opaque new target; no stretched lone thumb, lamp/key move, old competing grip or transparency overlay. Far supports redneck/head underside. Full front and both sleeves may be repaired. D identity/cloth only.069dark;073firstON using actual accepted069. This supersedes the preceding cancellation of axial motion. Source063remains0abc, unchanged.\n')
(O/'README.md').write_text('FINAL F069 reference gate, input preparation only; ZERO GENERATION / ZERO GIT. Source063locked0abc is unchanged. Latest authority ALLOWS new069 whole grip35native toward the fixed lamp end plus inward roll, superseding the earlier no-shift instruction.\n\nA has ONE opaque near full sleeve/arm/wrist/palm/thumb-root/four-finger volume in blue NOT_ART, and one complete far arm with full rolled actual palm. The old near grip/old thumb-on-top and old far gesture are removed. B opens the entire semantic action band/front/sleeves, including the revealed unknown barrel and old/new spaces; head/collar/skirt and true fixed prop outside the new hand operation stay protected. C is the identical pose plus soft chain; D ONLY identity/internal cloth, no old hands.\n\nThe small dark-blue exposed-barrel surface is explicitly UNKNOWN real material behind the old grip, never claimed as recovered RGB or a physical neck. Pureprop is measurement only; visible existing prop pixels come from final063 composed source. All blue is technical and must become continuous actual drawing. Far6px raster pad contact remains a soft placement diagnostic; old3.61gap refers to OLD063neargrip, not new069ownership. Newnear/far diagram overlap is explicitly near foreground, not anatomy proof. Full real hand reach/contact/pressure and five-finger ownership require actual069 review.\n\n069x4 TRANSIT stays dark.073x4 is firstON and uses actual accepted069;077x8headconfirm and085x11steadyON remain unchanged. Source dark lens fitted center(1229.88547047,560.41064554)native is only a soft emitter reference. No mechanical endstop or finished073A is frozen. Full draft/request parameters archived; root owns calls.\n')
manifest={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['manifest.json','replay_check.json']}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'A':manifest['inputs_1280x1536/A_F069_PREPARED_NOT_FROZEN_1280x1536.png'],'B':manifest['inputs_1280x1536/B_F069_PREPARED_NOT_FROZEN_1280x1536.png'],'contact':len(contacts),'near_gap':g,'emitter':lens.tolist(),'elbow':E.tolist()}))
