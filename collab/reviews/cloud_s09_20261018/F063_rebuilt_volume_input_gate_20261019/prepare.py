#!/usr/bin/env python3
"""Five F063 rebuilt-volume technical inputs, zero native generation, no inherited old human silhouette."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_erosion,binary_fill_holes,minimum_filter,label,distance_transform_edt
import numpy as np,json,math,hashlib
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for n in ['reference','masks','geometry','qa','requests','authority']:(R/n).mkdir(exist_ok=True)
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['path'])==v['sha256']
mother=Image.open(S/'F044_fe70_LOCKED_mother.png').convert('RGBA');a=np.array(mother);size=mother.size;assert size==(1672,941);yy,xx=np.indices(a.shape[:2]);crop=(600,230,1300,900);local=(700,670)
u=Image.open(S/'F044_same_rigid_grip_torch_SOURCE.png').convert('RGBA');ua=np.array(u)
def mask(n):return np.array(Image.open(S/n).convert('L'))>0
def poly(ps):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon([tuple(map(float,p))for p in ps],fill=255);return np.array(z)>0
def capsule(ps,r):
 ps=[tuple(map(float,p))for p in ps];z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(ps,fill=255,width=2*r+1)
 for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
G=np.array([1134.519,470.]);Gp=np.array([1049.533,598.588]);deg=78.508;t=math.radians(deg);M=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);tr=Gp-M@G
L=np.array([1135.,289.]);T=np.array([1134.,665.]);P=np.array([1151.292,645.375]);normal=np.array([.196620,.980480]);axis=np.array([.980480,-.196620])
near=[np.array(p,float)for p in [(705,666),(790,730),(992,650)]];far=[np.array(p,float)for p in [(970,689),(1005,810),(1100,696)]]
def rigid(z):
 inv=M.T;v=-inv@tr;return z.transform(size,Image.Transform.AFFINE,(*inv[0],v[0],*inv[1],v[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
# ALL source human hand/wrist/palm/finger silhouette is excluded from input A.
# Deliberately broad enclosing polygon also drops a few occluded/internal prop
# pixels; those unknown surfaces are native-redraw territory, never code-filled.
oldhuman=poly([(999,528),(1034,482),(1060,442),(1080,417),(1112,396),(1146,390),(1189,404),(1190,516),(1142,518),(1092,546),(1050,574),(999,543)])&(ua[:,:,3]>0)
prop=ua.copy();prop[oldhuman]=0
Image.fromarray(oldhuman.astype('uint8')*255).save(R/'masks/source_unit_ALL_old_human_hand_and_wrist_EXCLUDED_FROM_A.png')
Image.fromarray(prop).save(R/'reference/source044_visible_PROP_ONLY_no_old_hand_RGBA.png')
newprop=rigid(Image.fromarray(prop));npv=np.array(newprop);newprop.save(R/'reference/F063_rigid_visible_PROP_ONLY_TARGET_GUIDE.png')
# Complete current old source-arm silhouettes plus their ink/AA are cleared,
# not simply a203px hair overlap or90px wrist edge release.
oldnear=mask('F044_actual_complete_old_near_arm_mask.png')
oldfar_region=poly([(919,653),(1035,653),(1083,704),(1240,696),(1240,805),(1091,847),(1000,865),(919,820)])
oldnear_region=poly([(630,590),(792,570),(1058,470),(1210,390),(1223,710),(1030,800),(785,788),(630,738)])
oldunit=ua[:,:,3]>0
# Technical tapered volumes, including full new wrists/hands. No source human
# pixels are transformed into new arms, palms or gripping hands.
Vfar=Image.new('RGBA',size);Vnear=Image.new('RGBA',size);handFar=Image.new('RGBA',size);handNear=Image.new('RGBA',size)
farcol=(192,175,150,255);faredge=(117,89,53,255);nearcol=(155,194,211,255);nearedge=(53,108,137,255)
def tapered(z,pts,radii,col,edge):
 d=ImageDraw.Draw(z)
 for p,q,r1,r2 in zip(pts[:-1],pts[1:],radii[:-1],radii[1:]):
  dv=q-p;n=np.array([-dv[1],dv[0]])/np.linalg.norm(dv);corn=[p+n*r1,q+n*r2,q-n*r2,p-n*r1];d.polygon([tuple(v)for v in corn],fill=col,outline=edge,width=2)
 for p,r in zip(pts,radii):
  x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline=edge,width=2)
tapered(Vfar,far,[31,45,24],farcol,faredge);tapered(Vnear,near,[31,40,27],nearcol,nearedge)
# Receiving palm: P is its future contact SURFACE proxy, not interior center.
# The whole new schematic open hand stays beneath the front tube, fingers up
# only to a slightly right/down-facing rim, never moved to force contact.
fp=[far[-1]+[-13,-9],np.array([1121,655]),P,np.array([1191,646]),np.array([1237,649]),np.array([1240,660]),np.array([1216,691]),np.array([1176,713]),np.array([1133,716]),far[-1]+[-12,17]]
d=ImageDraw.Draw(handFar);d.polygon([tuple(p)for p in fp],fill=farcol,outline=faredge,width=2)
for i in [0,1,2]:
 x=1190+i*16;d.line([(x,652),(x-12,678),(x-32,697)],fill=faredge,width=2)
d.line([tuple(far[-1]),(1136,684),(1178,675)],fill=faredge,width=2)
# Near wrist enters from LEFT/BELOW to a newly rolled schematic grip, never from
# the old upper-left cut. The grip's axis reference remains fixed G'.
tapered(handNear,[near[-1],Gp+normal*12],[27,34],nearcol,nearedge)
# A complete rounded technical occlusion block covers the entire missing old
# hand-occluded prop region. It is new GRIP VOLUME, never invented real red RGB.
relative=np.stack([xx-Gp[0],yy-Gp[1]],axis=-1);along=relative@axis;across=relative@normal
qx=np.maximum(np.abs(along-10)-57,0);qy=np.maximum(np.abs(across-7)-29,0);gripblock=qx*qx+qy*qy<=8*8
hh=np.array(handNear);hh[gripblock]=nearcol;boundary=gripblock&~binary_erosion(gripblock,iterations=2);hh[boundary]=nearedge
handNear=Image.fromarray(hh);d=ImageDraw.Draw(handNear)
for q in [-28,-3,22,47]:
 p0=Gp+axis*q-normal*25;p1=Gp+axis*(q+4)+normal*36;d.line([tuple(p0),tuple(p1)],fill=nearedge,width=2)
# Wide coherent redraw corridor, all obsolete human/torch and newly exposed
# yellow-cloth territory. The exact old stable skirt guard is never opened.
head=mask('F044_actual_head_neck_collar_guard.png')&(a[:,:,3]>0)
ruffle=mask('F044_actual_stable_near_ruffle_guard.png')&(a[:,:,3]>0)
skirt=mask('F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png')&(a[:,:,3]>0)
hard=head|ruffle|skirt
vfar=np.array(Vfar)[:,:,3]>0;vnear=np.array(Vnear)[:,:,3]>0;hfar=np.array(handFar)[:,:,3]>0;hnear=np.array(handNear)[:,:,3]>0
newgeometry=vfar|vnear|hfar|hnear|(npv[:,:,3]>0)
oldclear=binary_dilation(oldnear|oldunit,iterations=8)|oldfar_region|oldnear_region
semantic=oldclear|binary_dilation(newgeometry,iterations=10)
inside=(xx>=600)&(xx<1300)&(yy>=230)&(yy<900);edit=semantic&~hard
assert not np.any(edit&~inside&(a[:,:,3]>20));edit&=inside
base=a.copy();base[edit]=0
Afull=Image.fromarray(base)
for z in [Vfar,handFar,Vnear,newprop,handNear]:Afull.alpha_composite(z)
A=np.array(Afull);A[hard]=a[hard];Afull=Image.fromarray(A)
# NOT_ART text occupies an already editable former torch area; it is not hard
# protected and never part of a production drawing.
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
d=ImageDraw.Draw(Afull);d.text((1070,300),'NOT_ART',font=font,fill='#455e6d')
Afull.crop(crop).save(R/'reference/1_rebuilt_complete_volume_TARGET_NOT_ART_700x670.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'reference/2_complete_redraw_WHITE_REFERENCE_700x670.png')
# True head/collar material only, complete stable ruffle, internal flat skin and
# cloth swatches. No whole mother pose, old arms or hanging cut silhouettes.
R3=Image.new('RGBA',local,(234,240,244,255));dr=ImageDraw.Draw(R3);dr.text((10,6),'3 REAL IDENTITY / MATERIAL ONLY — NO OLD ARMS',font=small,fill='#314958')
identity=a.copy();identity[~head]=0;identity=Image.fromarray(identity).crop((550,15,1020,580));R3.alpha_composite(identity,(8,30))
ru=a.copy();ru[~ruffle]=0;R3.alpha_composite(Image.fromarray(ru).crop((630,600,790,725)),(510,55));dr=ImageDraw.Draw(R3);dr.text((510,190),'real near ruffle',font=small,fill='#314958')
rgb=a[:,:,:3].astype(int);valid=oldnear&(a[:,:,3]>=250)&(rgb[:,:,0]>180)&(rgb[:,:,1]>100)&(rgb[:,:,2]>80)&(rgb[:,:,0]-rgb[:,:,1]>15)&(rgb[:,:,1]-rgb[:,:,2]>12)
cent=minimum_filter(valid.astype('uint8'),size=(24,24),mode='constant')>0;ys,xs=np.where(cent);assert len(xs);i=int(np.argmin((xs-915)**2+(ys-665)**2));sx,sy=int(xs[i]),int(ys[i]);skinbox=(sx-12,sy-12,sx+12,sy+12);R3.paste(mother.crop(skinbox),(540,240));dr=ImageDraw.Draw(R3);dr.text((510,276),'actual interior skin',font=small,fill='#314958')
clothbox=(780,565,836,605);R3.paste(mother.crop(clothbox),(520,325));dr=ImageDraw.Draw(R3);dr.text((510,380),'actual yellow cloth',font=small,fill='#314958');R3.save(R/'reference/3_real_head_collar_ruffle_identity_material_NO_OLD_ARMS.png')
# Exact026 head crop, with only the foreign skin/its dark-AA border removed.
f26=Image.open(S/'F026_CONTEXT_archive_NOT_REQUEST.png').convert('RGBA');box4=(1155,485,1270,636);c4=np.array(f26.crop(box4));r4=c4[:,:,:3].astype(int);cy,cx=np.indices(c4.shape[:2]);skin4=(c4[:,:,3]>0)&(r4[:,:,0]>140)&(r4[:,:,1]>80)&(r4[:,:,0]-r4[:,:,1]>18)&(r4[:,:,0]-r4[:,:,1]<110)&(r4[:,:,1]-r4[:,:,2]>12)&(r4[:,:,1]-r4[:,:,2]<80)&(cx<18)&(cy>130)
edge4=binary_dilation(skin4,iterations=2)&(c4[:,:,3]>0)&(cx<18)&(cy>130)&(r4.max(axis=2)<120)
exclude4=skin4|edge4;kept4=c4.copy();kept4[exclude4]=0
# Remove only disconnected residual nonlamp specks outside the main lamp core
# plus its genuine2px AA band. Kept source RGBA remains byte-identical.
labs4,_=label(kept4[:,:,3]>=20);counts4=np.bincount(labs4.ravel());counts4[0]=0;main4=labs4==counts4.argmax();detached4=(kept4[:,:,3]>0)&~binary_dilation(main4,iterations=2);exclude4|=detached4;kept4[detached4]=0
Image.fromarray(kept4).save(R/'reference/4_exact026_lamp_head_crop_NO_FOREIGN_SKIN.png');Image.fromarray(exclude4.astype('uint8')*255).save(R/'masks/ref4_nonlamp_skin_and_edge_EXCLUDED.png')
# Reference5 is only original genuine unit material/scale/finger ownership.
# Whole technical wrist ROI is EXPLICITLY removed, not just the90px fringe.
techwrist=(xx>=1008)&(xx<=1075)&(yy>=490)&(yy<=566)&(ua[:,:,3]>0)
u5=ua.copy();u5[techwrist]=0;box5=(990,250,1220,690);R5=Image.new('RGBA',(350,535),(234,240,244,255));R5.alpha_composite(Image.fromarray(u5).crop(box5),(60,45));dr=ImageDraw.Draw(R5);dr.text((8,8),'5 REAL UNIT: SIZE / FINGER OWNERSHIP ONLY',font=small,fill='#314958');dr.text((8,490),'Old wrist1008..1075 /490..566 REMOVED',font=small,fill='#a85f37');dr.text((8,511),'DO NOT COPY OLD WRIST/HAND CONTOUR',font=small,fill='#a85f37');R5.save(R/'reference/5_original044_unit_material_old_technical_wrist_EXCLUDED.png');Image.fromarray(techwrist.astype('uint8')*255).save(R/'masks/ref5_FULL_technical_wrist_EXCLUDED.png')
refs=[R/'reference'/f for f in ['1_rebuilt_complete_volume_TARGET_NOT_ART_700x670.png','2_complete_redraw_WHITE_REFERENCE_700x670.png','3_real_head_collar_ruffle_identity_material_NO_OLD_ARMS.png','4_exact026_lamp_head_crop_NO_FOREIGN_SKIN.png','5_original044_unit_material_old_technical_wrist_EXCLUDED.png']]
# Source/mask records and exact corrected authority text.
for n,z in [('complete_old_near_arm_source_material',oldnear),('old_far_arm_hand_clear_region',oldfar_region),('ALL_old_arm_unit_vacated_envelope',oldclear),('full_new_technical_volume_envelope',newgeometry),('full_WHITE_edit_reference',edit),('UNCHANGED_actual_head_guard',head),('UNCHANGED_actual_near_ruffle_guard',ruffle),('UNCHANGED_actual_skirt_guard',skirt)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{n}.png')
# Material clearance is measured on the TECHNICAL new open hand vs visible true
# rigid prop and vs complete schematic near grip separately; not a native pass.
def gap(to,frm):
 if not frm.any()or not to.any():return None
 dist=distance_transform_edt(~to);return {'overlap_pixels':int((to&frm).sum()),'minimum_pixel_center_distance_native':float(dist[frm].min())}
far_hand_alpha=np.array(handFar)[:,:,3]>=128;prop_alpha=npv[:,:,3]>=128;near_hand_alpha=np.array(handNear)[:,:,3]>=128
# Temporary/instructional production ordering is far before near. Stable source
# parts stay exact, and no old human source pixels are used to draw new limbs.
checks={'status':'F063_REBUILT_FIVE_TECHNICAL_INPUTS_PENDING_ROOT_ASTRA_REVIEW_NO_CALL','mother044_sha256':sha(S/'F044_fe70_LOCKED_mother.png'),'crop_native':crop,'A_B_native_size':[700,670],'unit_R_degrees':deg,'unit_scale':1,'unit_M':M.tolist(),'unit_t':tr.tolist(),'G_target':Gp.tolist(),'L_target':(M@L+tr).tolist(),'T_target':(M@T+tr).tolist(),'P_fixed_surface':P.tolist(),'P_definition':'069surface1145,614 plus normal(.196620,.980480)*32, rounded; surface proxy not interior center, not physical contact proof','near_chain':[[705,666],[790,730],[992,650],Gp.tolist()],'near_technical_halfwidths':[31,40,27,34],'far_chain':[[970,689],[1005,810],[1100,696],P.tolist()],'far_technical_halfwidths_assumptions_not_frozen':[31,45,24],'near_elbow_bottom':770,'far_elbow_bottom':855,'far_elbow_to_crop_bottom':45,'technical_layer_order':['far_arm','far_open_palm','near_arm','actual_rigid_visible_prop','new_technical_near_grip','original_stable_head_ruffle_skirt'],'source_old_human_unit_pixels_excluded_from_A':int(oldhuman.sum()),'old_near_source_alpha_remaining_outside_WHITE_except_fixed_material':int((oldnear&~edit&~hard).sum()),'base_old_near_source_RGBA_visible_inside_white_after_clear':int((oldnear&edit&(base[:,:,3]>0)).sum()),'old_unit_source_material_remaining_in_A_base_after_clear':int((oldunit&edit&(base[:,:,3]>0)).sum()),'old_far_skin_visible_in_A_base_after_clear':int((oldfar_region&edit&(base[:,:,3]>0)).sum()),'new_human_pixels_in_A':'Only clearly technical drawn volume; no transformed/retained original human wrist, hand or arm pixels adopted for new limbs. Actual frozen face/neck/cuff material remains source.','white_pixels':int(edit.sum()),'guard_intersections':{n:int((edit&z).sum())for n,z in [('head',head),('near_ruffle',ruffle),('unchanged_skirt',skirt)]},'guard_source_alpha0_pixels':int((hard&(a[:,:,3]==0)).sum()),'near_elbow_bottom770_WHITE_value':int(edit[770,790])*255,'stable_skirt_row777_at790_WHITE_value':int(edit[777,790])*255,'stable_guard_final_RGBA_changes':int(np.any(A[hard]!=a[hard],axis=1).sum()),'new_technical_near_volume_overlap_head_pixels':int(((vnear|hnear)&head).sum()),'new_technical_near_volume_overlap_stable_skirt_pixels':int(((vnear|hnear)&skirt).sum()),'new_technical_far_volume_overlap_stable_skirt_pixels':int(((vfar|hfar)&skirt).sum()),'technical_far_hand_vs_true_visible_prop_gap':gap(prop_alpha,far_hand_alpha),'technical_far_hand_vs_new_near_grip_gap':gap(near_hand_alpha,far_hand_alpha),'ref3_source_head_mask_box':[550,15,1020,580],'ref3_skin_material_box':skinbox,'ref3_cloth_material_box':clothbox,'ref4_exact026_native_crop':box4,'ref4_nonlamp_excluded_pixels':int(exclude4.sum()),'ref4_kept_RGBA_changes':int(np.any(kept4[~exclude4]!=c4[~exclude4],axis=1).sum()),'ref5_original_unit_crop':box5,'ref5_technical_wrist_full_native_ROI_inclusive':[1008,490,1075,566],'ref5_source_technical_wrist_pixels_removed':int(techwrist.sum()),'request_inputs':[{'path':str(p.relative_to(R)),'sha256':sha(p),'size':list(Image.open(p).size)}for p in refs],'new_calls':0,'future_states_unopened':True}
assert not any(checks['guard_intersections'].values());assert checks['guard_source_alpha0_pixels']==0;assert checks['stable_guard_final_RGBA_changes']==0
assert checks['near_elbow_bottom770_WHITE_value']==255 and checks['stable_skirt_row777_at790_WHITE_value']==0
def bbox_record(z):
 ys,xs=np.where(z)
 if not len(xs):return None
 b=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 return {'bbox_native_halfopen':b,'bbox_crop_local_halfopen':[b[0]-600,b[1]-230,b[2]-600,b[3]-230],'blank_pixel_margins_left_top_right_bottom':[b[0]-600,b[1]-230,1300-b[2],900-b[3]],'all_inside_crop':bool((z&~inside).sum()==0)}
checks['new_complete_volume_including_prop_AA_bbox']=bbox_record(newgeometry)
checks['full_white_actual_bbox']=bbox_record(edit)
checks['new_complete_volume_pixels_outside_crop']=int((newgeometry&~inside).sum())
checks['new_complete_volume_not_WHITE_or_real_stable_guard']=int((newgeometry&~edit&~hard).sum())
checks['new_volume_under_stable_actual_ruffle_pixels']=int((newgeometry&ruffle).sum())
checks['reference_coordinate_mappings']={
 'A_B':{'source_native_crop':[600,230,1300,900],'local_xy_equals_native_minus':[600,230],'scale':1},
 'ref3_head_collar':{'source_crop':[550,15,1020,580],'paste_top_left':[8,30],'scale':1,'source_mask':'F044_actual_head_neck_collar_guard.png','mapping':'ref3=(source-[550,15])+[8,30]'},
 'ref3_near_ruffle':{'source_crop':[630,600,790,725],'paste_top_left':[510,55],'scale':1,'source_mask':'F044_actual_stable_near_ruffle_guard.png'},
 'ref3_skin':{'source_crop':skinbox,'paste_top_left':[540,240],'scale':1},
 'ref3_cloth':{'source_crop':clothbox,'paste_top_left':[520,325],'scale':1},
 'ref4':{'source_crop':box4,'local_xy_equals_source_minus':[1155,485],'scale':1,'excluded_pixels_mask':'masks/ref4_nonlamp_skin_and_edge_EXCLUDED.png','retained_source_RGBA_changed_pixels':0},
 'ref5':{'source_crop':box5,'paste_top_left':[60,45],'scale':1,'mapping':'ref5=(source-[990,250])+[60,45]','full_wrist_exclusion_native_inclusive':[1008,490,1075,566]}}
checks['reference_alpha_composition_note']='Refs3/5 source crops pasted at native1:1; masked head/ruffle/unit AA naturally alpha-composited over a neutral reference backdrop. Source RGBA files untouched; internal skin/cloth rectangles copied directly. Ref4 retained source RGBA exact.'
assert checks['new_complete_volume_pixels_outside_crop']==0 and checks['new_complete_volume_not_WHITE_or_real_stable_guard']==0
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',local,col);z.alpha_composite(Image.open(refs[0]).convert('RGBA'));z.convert('RGB').save(R/f'qa/A_rebuilt_volume_{tone}_NOT_ART.png');wash=Image.new('RGBA',local,(219,36,121,0));wash.putalpha(Image.open(refs[1]).convert('L').point(lambda x:110 if x else 0));ov=z.copy();ov.alpha_composite(wash);ov.convert('RGB').save(R/f'qa/B_full_domain_overlay_{tone}.png')
 sheet=Image.new('RGB',(1420,730),(235,241,245));dd=ImageDraw.Draw(sheet);sheet.paste(z.convert('RGB'),(0,40));sheet.paste(ov.convert('RGB'),(710,40));dd.text((8,8),'A COMPLETE NEW VOLUME / OLD ARMS REMOVED / NOT ART',font=small,fill='#314958');dd.text((718,8),'B WHOLE REDRAW + ACTUAL STABLE GUARDS',font=small,fill='#314958');sheet.save(R/f'qa/A_B_actual_rebuilt_input_{tone}.png')
# Proposed draft only, not an approved call. Exactly five references.
prompt="""Edit image1 as one F063 cropped restoration, keeping its700x670 transparent canvas and fixed scale. Image2 is the complete redraw-region reference. Image1 is an explicitly NOT_ART technical volume guide; replace its schematic limbs, grip and marks with real drawing. Image3 is actual head/collar, stable near ruffle and material only. Image4 is only the026 lamp-head perspective. Image5 is the current real torch size/finger-ownership reference with the entire old technical wrist removed; never inherit its old wrist or hand-back outline.
Draw BOTH complete new arms and hands with natural tapered volume. On the full1672x941 canvas, near RIGHT runs from ruffle705,666 through elbow790,730(halfwidth40), wrist992,650(halfwidth27), then enters the newly rolled grip from LEFT/BELOW at G1049.533,598.588. The near elbow bottom770 stays above the unchanged skirt guard from777. Far LEFT is behind:970,689→1005,810(elbow halfwidth45,bottom855)→1100,696→approaching palm. Connect real elbows, wrists and fingers, without crossed forearms, narrow bridges, duplicate cuffs, hanging cuts or old silhouettes. Hidden far material must never cut through the new foreground near arm.
Keep the same physical torch and51.86percent grip-axis position, with lamp axis1227,563 and tail858.338,636.929. Subtract croporigin600,230 from every full-canvas coordinate. The source visible prop was rigidly rotated+78.508degrees at scale1; missing hand-occluded tube material is new-drawing territory, not a cut contour to preserve. Far palm SURFACE P1151.292,645.375 remains32native along the normal from future069surface1145,614, not an interior center or proof of clearance: leave every palm/fingertip visibly off the tube. Rebuild all exposed yellow clothing/white dots and voids. Preserve actual fixed head/collar, near ruffle and unchanged skirt material. Match source skin/ink/material. Switch OFF and light DARK throughout063–068; no old175/44diameter, text, blue diagram colors, new props or following states."""
(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');(R/'requests/arguments_PREPARED_DRAFT_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(p)for p in refs],'transparent_background':True},ensure_ascii=False,indent=2)+'\n')
(R/'authority/latest_corrected_geometry.txt').write_text('Latest parent/Astra override: near elbow(790,730), halfwidth40 replaces withdrawn(790,752)/45; near bottom770, unchanged skirt guard from777 must not be opened. Far elbow(1005,810), halfwidth45, bottom855 remains. Near wrist(992,650), halfwidth27; far wrist(1100,696), width is technical assumption. G(1049.533,598.588), surfaceP(1151.292,645.375) unchanged. Only five rebuilt inputs, zero native calls; full sourcehuman hand/wrist excluded fromA; no old arms/handback/cut silhouette inherited.\n')
(R/'README.md').write_text('''# F063 rebuilt five-input technical gate — NO CALL

唯一生产母044fe70。旧被退回包不动。A/B固定nativecrop600,230,1300,900=700×670。A先清空完整旧双臂/旧手筒/旧手背/腕片及露衣域，只有真实固定头领/近ruffle/原裙料保留；完整新双臂/迎掌/滚转握手是明确NOT_ART的渐细代码体量，不冒充真画。源unit全人手片在A排除，刚性真实可见筒料仅R+78.508°scale1；不能继承旧腕切口。

近705666→790730/r40→992650/r27→G1049.533598.588，肘底770；远970689→1005810/r45→1100696(宽仅技术假设)→P1151.292645.375，底855，远先近后。原稳定裙guard完整原SHA不变，不能为撤回752/45方案开裙料。

3仅真实头领mask裁片、完整近ruffle及内部肤/衣料样片，无旧双臂整姿；4精确026灯头crop1155,485,1270,636，只剔外来指皮/边AA，保留灯料RGBA原样；5当前044源筒/握指仅尺度指属，完整技术腕ROI1008..1075/490..566明确清除，不用90px边条代替。

所有5图及mask/source/裁片/变换/技术假设见geometry/preparation_checks.json、sources/snapshot_manifest.json；requests只有5参考与未冻结英文草稿，NOT_CALLED。必须由原作者/Astra实图审后才可能调用；新手臂与五指自然度、真实握持/掌指间隙、真实筒透视仍待唯一原生结果实审。
''',encoding='utf8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
