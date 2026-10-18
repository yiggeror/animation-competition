#!/usr/bin/env python3
"""F063 source-material target GUIDE and whole redraw domain only; no native call or finished pose."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,label,distance_transform_edt
import numpy as np,json,math,hashlib
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'requests/execution_state.json').exists()
for d in ['reference','layers','masks','geometry','qa','requests']:(R/d).mkdir(exist_ok=True)
for f in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/f['path'])==f['sha256']
source=S/'F044_fe70_LOCKED_mother.png';assert sha(source)=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9'
mother=Image.open(source).convert('RGBA');a=np.array(mother);size=mother.size;assert size==(1672,941);yy,xx=np.indices(a.shape[:2])
unit=Image.open(S/'F044_actual_same_rigid_grip_torch_layer.png').convert('RGBA');u=np.array(unit)
def mask(name):return np.array(Image.open(S/name).convert('L'))>0
def polygon(ps):
 q=Image.new('L',size);ImageDraw.Draw(q).polygon([tuple(map(float,p))for p in ps],fill=255);return np.array(q)>0
def capsule(ps,r):
 ps=[tuple(map(float,p))for p in ps];q=Image.new('L',size);d=ImageDraw.Draw(q);d.line(ps,fill=255,width=2*r+1)
 for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(q)>0
G=np.array([1134.519,470.]);Gp=np.array([1049.533,598.588]);theta=78.508;t=math.radians(theta);M=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);tr=Gp-M@G
P=np.array([1120.,717.]);Pp=np.array([1151.292,645.375]);handtr=Pp-P
L=np.array([1135.,289.]);T=np.array([1134.,665.]);Lp=M@L+tr;Tp=M@T+tr
assert np.allclose(Lp,[1227.,563.],atol=.002)and np.allclose(Tp,[858.338,636.929],atol=.002)
def rigid(z,m,v):
 assert np.allclose(m.T@m,np.eye(2),atol=1e-12)
 inv=m.T;iv=-inv@v;return z.transform(size,Image.Transform.AFFINE,(*inv[0],iv[0],*inv[1],iv[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
newunit=rigid(unit,M,tr);nu=np.array(newunit)
# This is an explicit actual whole-hand material extraction with one technical
# wrist cut; it is NOT a new hand drawing or a frozen063 five-finger judgement.
raw_receiver=mask('F044_receiver_source_mask_NOT_AUTOMATIC_GUARD.png')
hand_region=polygon([(1060,708),(1230,703),(1230,802),(1098,802),(1045,770),(1068,742)])
palm=raw_receiver&hand_region&(a[:,:,3]>0);labs,_=label(palm);cts=np.bincount(labs.ravel());cts[0]=0;palm=labs==cts.argmax()
ha=a.copy();ha[~palm]=0;hand=Image.fromarray(ha);newhand=rigid(hand,np.eye(2),handtr);nh=np.array(newhand)
unit.save(R/'layers/F044_original_same_rigid_unit_GUIDE_SOURCE.png');hand.save(R/'layers/F044_actual_receiver_whole_hand_GUIDE_SOURCE.png');newunit.save(R/'layers/F063_rigid_whole_unit_TARGET_GUIDE_NOT_ART.png');newhand.save(R/'layers/F063_whole_left_hand_surface_target_GUIDE_NOT_ART.png')
# Base is only technical composition: old unit and old receiver are vacated,
# old arms remain obsolete evidence entirely inside the forthcoming white domain.
oldunit=u[:,:,3]>0;base=a.copy();base[oldunit|palm]=0;pre=Image.fromarray(base);pre.alpha_composite(newunit);pre.alpha_composite(newhand)
head=mask('F044_actual_head_neck_collar_guard.png')&(a[:,:,3]>0)
ruffle=mask('F044_actual_stable_near_ruffle_guard.png')&(a[:,:,3]>0)
# The head is frozen. A 2D rotated technical WRIST cut can overlap its outline;
# restore actual mother head above that GUIDE, document it, never freeze that cut.
prea=np.array(pre);prea[head]=a[head];pre=Image.fromarray(prea)
oldnear=polygon([(630,590),(795,580),(1055,470),(1215,390),(1225,710),(1030,800),(785,790),(630,735)])
oldfar=polygon([(920,650),(1035,650),(1080,715),(1245,695),(1240,810),(1090,845),(1000,865),(925,820)])
nearnew=capsule([(704,670),(790,735),(965,530)],57)
farnew=capsule([(975,690),(1010,780),(1090,690)],46)
# Real skirt except all explicitly obsolete/new far arm and receiver territory.
# No hand skin or prior arm ink is guarded as dress simply because y>=777.
skirt=mask('F044_actual_waist_skirt_material_mask.png')&(a[:,:,3]>0)&~oldfar&~farnew
hard=head|ruffle|skirt
semantic=binary_dilation(oldunit|palm,iterations=12)|binary_dilation((nu[:,:,3]>0)|(nh[:,:,3]>0),iterations=14)|oldnear|oldfar|nearnew|farnew
crop=(600,230,1300,900);inside=(xx>=600)&(xx<1300)&(yy>=230)&(yy<900);edit=semantic&~hard
clipped=int((edit&~inside&((prea[:,:,3]>20)|(a[:,:,3]>20))).sum());assert clipped==0
edit&=inside
for name,z in [('F063_complete_unit_both_full_arms_old_new_vacated_WHITE_EDIT_PENDING_ASTRA',edit),('HARD_actual_head_neck_collar',head),('HARD_actual_stable_near_ruffle_ONLY',ruffle),('HARD_actual_stable_waist_skirt_except_old_new_arm',skirt),('full_redraw_semantic_envelope_GUIDE_ONLY',semantic),('old_unit_vacated_material',oldunit),('old_receiver_actual_hand_material',palm),('rotated_unit_technical_wrist_over_head_PROJECTION_CONFLICT_NOT_FROZEN',(nu[:,:,3]>0)&head)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
pre.save(R/'reference/F063_actual_source_target_GUIDE_NOT_ART.png');pre.crop(crop).save(R/'reference/F063_crop_RGBA_TARGET_GUIDE_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F063_crop_WHITE_EDIT_PENDING_ASTRA.png')
gap={};tip_src=palm&(xx>=1160)&(yy<=760);ta=np.zeros_like(a);ta[tip_src]=a[tip_src];tip=np.array(rigid(Image.fromarray(ta),np.eye(2),handtr))[:,:,3]
for th in [1,20,128,240]:
 um=nu[:,:,3]>=th;hm=nh[:,:,3]>=th;dist,ind=distance_transform_edt(~um,return_indices=True);ys,xs=np.where(hm);i=int(np.argmin(dist[ys,xs]));hy,hx=int(ys[i]),int(xs[i]);uy,ux=int(ind[0,hy,hx]),int(ind[1,hy,hx]);tm=tip>=th
 gap[str(th)]={'whole_unit_left_hand_overlap_pixels':int((um&hm).sum()),'minimum_pixel_center_distance_native':float(dist[hy,hx]),'nearest_left_hand_xy':[hx,hy],'nearest_unit_xy':[ux,uy],'fingertip_region_minimum_pixel_center_distance_native':float(dist[tm].min())}
assert gap['128']['whole_unit_left_hand_overlap_pixels']==0
head_conflict=(nu[:,:,3]>=128)&head;hc=nu[head_conflict,:3].astype(int);skincheck=(hc[:,0]>140)&(hc[:,1]>90)&(hc[:,0]-hc[:,1]>15)
hy,hx=np.where(head_conflict);inverse_conflict=(np.stack([hx,hy],axis=1)-tr)@M
source_unit_core=u[:,:,3]>=240;source_unit_opaque=u[:,:,3]==255
unit_vs_flat={str(th):int(np.any(u[u[:,:,3]>=th]!=a[u[:,:,3]>=th],axis=1).sum())for th in [128,240,255]}
# Recorded geometry is only the fixed-axis rigid target and visible source-point
# correspondence. 32 along normal is NOT claimed to be contour clearance.
axis=L-T;frac=float(np.dot(G-T,axis)/np.dot(axis,axis));s=.6297229219143576;off=np.array([241.2216624685139,83.47607052896726]);Lp_reg=Lp*s+off;Lp_preview=(Lp_reg-np.array([280.,80.]))*1.25
checks={'status':'F063_SOURCE_TARGET_GUIDE_AND_FULL_MASK_PREPARED_PENDING_ASTRA_NOT_GENERATED','mother044_sha256':sha(source),'native_canvas':[1672,941],'frame':63,'hold':6,'inclusive_frames':[63,68],'switch':'OFF','light_on':False,'unit_source_sha256':sha(S/'F044_actual_same_rigid_grip_torch_layer.png'),'unit_source_RGBA_difference_vs_flat_fe70_by_source_alpha_threshold':unit_vs_flat,'unit_source_role':'Same genuine044 rigid-unit material lineage; source031/042 AA separation is historical, no026 grip pixels adopted; guide only, complete new unit must be native redrawn.','unit_transform':{'rotation_degrees':theta,'scale':1,'matrix':M.tolist(),'translation_native':tr.tolist(),'G_source':G.tolist(),'G_target':Gp.tolist(),'actual_G_mapped':(M@G+tr).tolist(),'source_lamp_axis':L.tolist(),'source_tail_axis':T.tolist(),'actual_L_target':Lp.tolist(),'actual_T_target':Tp.tolist(),'fixed_target_rounding_tolerance_native':.002,'axis_source_native':float(np.linalg.norm(axis)),'axis_target_native':float(np.linalg.norm(Lp-Tp)),'axis_registered_approx':float(np.linalg.norm(axis))*s,'grip_axis_fraction_from_tail':frac,'AA_resampling':'One entire-unit BICUBIC rotation/translation, no nonuniform scale or piece-by-piece hand/torch warp; 2D target only.'},'left_hand_surface_target':{'source_visible_surface_proxy':[1120,717],'proxy_definition':'Artificially chosen corresponding visible contact-surface point on the original actual palm, based on contact semantics relayed by parent/Astra; not interior geometric center or anatomical measurement.','source_interior_center_approx_not_mapped':[1120,750],'target_fixed':Pp.tolist(),'translation_native':handtr.tolist(),'additional_rotation_degrees':0,'future069_surface_contact':[1145,614],'normal_given':[.196620,.980480],'nominal_normal_offset_native':32,'point_distance_not_material_contact_proof':True,'actual_source_material_main_component_pixels':int(palm.sum()),'source_mask_low_alpha_or_nonhand_points_outside_explicit_hand_region_discarded':int((raw_receiver&~palm).sum()),'full_hand_technical_wrist_cut_not_frozen':True},'actual_material_gap_scan':gap,'head_projection_conflict':{'alpha128_pixels':int(head_conflict.sum()),'bbox_native_inclusive':[int(np.where(head_conflict)[1].min()),int(np.where(head_conflict)[0].min()),int(np.where(head_conflict)[1].max()),int(np.where(head_conflict)[0].max())],'warm_skin_test_count':int(skincheck.sum()),'remaining_pixels_include_wrist_ink_AA_not_assumed_all_skin':int(len(skincheck)-skincheck.sum()),'inverse_source_wrist_bbox_fractional':[float(inverse_conflict[:,0].min()),float(inverse_conflict[:,1].min()),float(inverse_conflict[:,0].max()),float(inverse_conflict[:,1].max())],'description':'Rotated old technical proximal wrist material intersects fixed hair/head outline; not torch body/cap/grip-axis displacement. Actual head restored unchanged. Entire new near hand/wrist/arm must be naturally native redrawn; technical cut/2D silhouette cannot be frozen as finished anatomy.','Astra_input_review_required':True},'head_guard_preposition_RGBA_changes':int(np.any(prea[head]!=a[head],axis=1).sum()),'stable_near_ruffle_preposition_RGBA_changes':int(np.any(prea[ruffle]!=a[ruffle],axis=1).sum()),'crop_xyxy':crop,'crop_size':[700,670],'white_pixels':int(edit.sum()),'clipped_editable_actual_alpha20_material':clipped,'guard_intersections':{k:int((edit&v).sum())for k,v in [('head_neck_collar',head),('actual_stable_near_ruffle',ruffle),('actual_stable_waist_skirt',skirt)]},'hard_guard_actual_alpha0_pixels':int((hard&(a[:,:,3]==0)).sum()),'old_unit_uneditable_except_stable_head_cuff_skirt':int((oldunit&~edit&~hard).sum()),'new_unit_uneditable_except_fixed_head_projection_conflict':int(((nu[:,:,3]>0)&~edit&~head&~ruffle&~skirt).sum()),'registration':{'scale':s,'translation_native_to_registered':off.tolist(),'preview_registered_crop':[280,80,1304,656],'preview_crop_scale':1.25},'future073_frozen_lamp_anchor':{'registered':[1013.892,438.010],'preview_720p':[917.365,447.513],'computed_from_current_rounded_target_registered':Lp_reg.tolist(),'computed_preview':Lp_preview.tolist(),'actual_native_lamp_and_ON_still_need_new_image_confirmation':True},'future_schedule_only':[[69,72,4,'TRANSIT',False],[73,76,4,'ON',True],[77,84,8,'ON',True],[85,95,11,'ON',True]],'new_calls':0,'scope_limit':'Only063 input guide/mask. Not073light artwork, no069/073 new pose mask, not a six-state batch approval.'}
assert checks['head_guard_preposition_RGBA_changes']==0;assert checks['stable_near_ruffle_preposition_RGBA_changes']==0;assert not any(checks['guard_intersections'].values());assert checks['hard_guard_actual_alpha0_pixels']==0
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,c):
 q=Image.new('RGBA',size,c);q.alpha_composite(z);return q
for tone,c in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=bg(pre,c);z.convert('RGB').save(R/f'qa/F063_full_target_{tone}_NOT_ART.png');ov=z.copy();wash=Image.new('RGBA',size,(219,36,121,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*110));ov.alpha_composite(wash)
 z.crop(crop).convert('RGB').save(R/f'qa/F063_crop_target_{tone}_NOT_ART.png');ov.crop(crop).convert('RGB').save(R/f'qa/F063_complete_redraw_overlay_{tone}.png')
 sheet=Image.new('RGB',(2120,740),(236,241,246));d=ImageDraw.Draw(sheet)
 for j,(title,q)in enumerate([('锁044生产母fe70／唯一形体源',bg(mother,c)),('063同源刚体目标／非成态',z),('新手筒＋双整臂全白／待Astra输入审',ov)]):sheet.paste(q.crop(crop).convert('RGB'),(j*710,45));d.text((j*710+5,8),title,font=font,fill='#24343f')
 sheet.save(R/f'qa/F044_F063_actual_target_and_full_domain_{tone}.png')
 pair=Image.new('RGB',(1400,670),(236,241,246));pair.paste(z.crop(crop).convert('RGB'),(0,0));pair.paste(Image.fromarray(edit.astype('uint8')*255).crop(crop).convert('RGB'),(700,0));pair.save(R/f'qa/F063_actual_crop_and_WHITE_MASK_{tone}.png')
 # Actual source layers only in gap panel, no painted fingers/arm reconstruction.
 q=Image.new('RGBA',size,c);q.alpha_composite(newunit);q.alpha_composite(newhand);q.crop((800,450,1300,750)).resize((1000,600),Image.Resampling.NEAREST).convert('RGB').save(R/f'qa/actual_rigid_unit_and_whole_left_hand_gap_{tone}_GUIDE.png')
 q=bg(pre,c).crop((900,450,1030,565)).resize((650,575),Image.Resampling.NEAREST);q.convert('RGB').save(R/f'qa/technical_wrist_head_projection_conflict_{tone}_GUIDE.png')
 # Source palm surface visible correspondence and source internal center are
 # diagnostic annotations, not generated pose pixels.
 q=bg(mother,c).crop((1020,690,1240,810)).resize((880,480),Image.Resampling.NEAREST).convert('RGB');d=ImageDraw.Draw(q)
 for pt,txt,col in [((1120,717),'source surface proxy1120,717','#197da1'),((1120,750),'interior center NOT mapped','#b67a27')]:
  x=(pt[0]-1020)*4;y=(pt[1]-690)*4;d.ellipse((x-7,y-7,x+7,y+7),outline=col,width=3);d.text((x+10,y-15),txt,fill=col)
 q.save(R/f'qa/source_palm_surface_correspondence_{tone}.png')
prompt='''F063 ONLY, PREPARED NOT CALLED. On image1 draw only WHITE image2; same700x670 transparent crop, fixed framing/scale. Image3 is the unique locked real F044fe70 whole mother. Image4 F026 is ONLY right/slightly-up torch angle, lamp-mouth perspective, and support layering context: NEVER replace the current gripping position with026 or copy its other grip. Image5 is the same real044 rigid hand/torch source for material and size.

The child kneels waist-up facing screenRIGHT. F063 holds6frames063–068: switch remains OFF, light DARK; eyes return to the switch. After the second tail tap/rebound the flashlight returns to its operating angle. The whole actual near RIGHT hand/torch was rigidly projected as a TARGET GUIDE only: scale1 rotation+78.508degrees; original grip-axisG1134.519,470 mapsG1049.533,598.588; lamp-axis end1227,563 and tail-axis end858.338,636.929 in full1672x941 native canvas. Crop origin600,230. Preserve the same physical torch size, silver head/cap proportions and grip location51.86percent from the tail, no lengthening or old175/44diameter substitution. It is now directed right/slightly upward. The source thumb/switch is partly hidden: draw the real OFF configuration consistently; do not assert an unseen mechanical endpoint by copying a code point.

REDRAW THE COMPLETE WHITE NEW TORCH/GRIPPING HAND AND BOTH COMPLETE ARMS naturally as one coherent real action. Every old/new upper arm, elbow, forearm, wrist and hand/cuff transition belongs to the full redraw, together with exposed clothing/transparent voids behind obsolete silhouettes. The projected source-piece boundaries are technical cuts, NOT finished anatomy. Especially the old2D rotated near wrist root exits upper-left and overlaps frozen hair near full-native946..969,487..519; it is only a guide. Keep actual BLACK head/hair/neck/collar unchanged and redraw the whole new near hand/wrist naturally into the full new arm without entering hair, changing grip fraction, moving the torch target or drawing a narrow bridge. One natural arm from the actual stable near ruffle opening through a real elbow into a consistent complete gripping hand; no disconnected wrist, duplicate sleeve, crossed forearms, split/warped hand or retained old source cut.

The far anatomical LEFT whole palm is APPROACHING UNDER the FRONT torch section and MUST NOT support/touch yet in063. Its intended future contact-SURFACE point is full-native1151.292,645.375, not an interior geometric center. The actual old visible source upper-surface proxy1120,717 was translated to that point, while the old interior center1120,750 naturally remains below it. This is only a visible source correspondence, not measured anatomy. It is32native along the normal(.196620,.980480) away from the future069 true surface contact1145,614. The point offset is NOT a promise of actual finger clearance: retain a real visible gap for the entire actual palm and all fingertips. Current whole-source guide has15native minimum alpha128 pixel-center distance from the WHOLE right-hand/torch group and no overlap; fingertips also clear. Do not freeze the guide wrist cut or old far hand position. Redraw the full far upper arm/elbow/forearm/wrist and open hand continuously from its sleeve, with natural palm thickness, plausible five-finger ownership and no hand growing from the torso. No anticipatory wrapping/supporting the barrel, fingertip contact or penetrations.

Only real stable near ruffle material, actual head/neck/collar and stable skirt are BLACK guarded. Rear sleeve/arm may be naturally occluded by the new near foreground arm; never use full hidden-layer alpha or transparent ROI boxes to cut new foreground. The far hand is below the torch; real nearer right grip fingers wrap the unchanged grip location with proper front/back ownership. Match realfe70 identity, separate skin flats/warm cel shadow, yellow material/complete white dots and dark ink. Clear all obsolete upright torch/old near-arm/old far-hand/forearm AA outlines and reconstruct exposed yellow cloth continuously, not thin seams or copied cut fragments. Do not paint frozen face, move only facial features, relight or add props/guide colors. No light before073. This request is only063, not069/073/077/085.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F063_crop_RGBA_TARGET_GUIDE_NOT_ART.png'),str(R/'masks/F063_crop_WHITE_EDIT_PENDING_ASTRA.png'),str(source),str(S/'F026_angle_lens_support_CONTEXT_ONLY.png'),str(S/'F044_actual_same_rigid_grip_torch_layer.png')],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/inputs_PENDING_ASTRA_NOT_FROZEN_FOR_CALL.json').write_text(json.dumps({'status':'REFERENCE_AND_MASK_ONLY_ASTRA_INPUT_REVIEW_REQUIRED_NOT_CALLED','inputs':[{'path':str(Path(p).relative_to(R)),'sha256':sha(p)}for p in args['referenced_image_paths']],'head_projection_conflict_must_be_visually_reviewed':True,'new_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('''# S09 F063 单态实际材料目标 / 全域待新画

唯一生产母044fe70；仅准备真实source刚体目标guide和完整重画白域，未生成/提交，不是动作或六态通过。026只供略向右上角/灯口透视/托掌前后上下文，不换当前握位。

G1134.519,470→1049.533,598.588；同源整手筒+78.508°、scale1，L1227,563/T858.338,636.929（小数四舍五入误差<.002），原握轴距尾51.86%保持。实际轴376native≈236.777registered与旧240.205的1.43%人工误差不作拉长理由。

063掌点按父/Astra接触语义为同一掌垫的拟接触上表面，不是内部几何中心。人工可见源表面1120,717→1151.292,645.375；源内部1120,750不映射该点。目标沿法线距069表面点32只是点距，绝不冒称物理接触/材料间隙。实际整左手对完整新握手筒alpha128重叠0、最近像素中心距15native；未额外旋转或移动目标。原手/腕切口不冻成新手形。

必须披露：刚体旋转的旧技术腕片与固定头发/头guard有203个alpha≥128像素重叠，bbox946..969/487..519，源映射在旧腕肤料及边线AA区，不是筒体。母头领原样恢复。它说明2Dguide不能作为成态手腕；完整新握手/近臂要原生重画，绕开固定发梢，不以窄条桥补回。本包带局部实图/白域供Astra裁定输入，不声称此新拓扑已自然通过。

看qa/F044_F063_actual_target_and_full_domain_gray.png及dark，qa/F063_actual_crop_and_WHITE_MASK_gray.png；实际gap近图qa/actual_rigid_unit_and_whole_left_hand_gap_gray_GUIDE.png；腕/头局部qa/technical_wrist_head_projection_conflict_gray_GUIDE.png；源掌点解释qa/source_palm_surface_correspondence_gray.png。

整新手筒、近远两整臂、原远掌及完整目标掌、旧新腾空/显露衣片均WHITE。仅实际头领/稳定近ruffle/稳定裙料硬保，不保技术腕边或旧远手。建议crop600,230,1300,900=700×670；请求特标PREPARED_NOT_CALLED且非已冻结调用输入，必须先由Astra/原作者实看。

063–068×6 OFF暗；069–072×4 TRANSIT仍暗；073–076×4首次ON亮；077–084×8整头确认；085–095×11稳亮向右。新滑键机械端点/真实掌垫接触/灯口原生透视仍由真实新图验证。旧源开关端点被拇指遮挡，不称已实测。无069等新图/白域。
''',encoding='utf8')
print(json.dumps({'preposition_SHA':sha(R/'reference/F063_actual_source_target_GUIDE_NOT_ART.png'),'mask_SHA':sha(R/'masks/F063_complete_unit_both_full_arms_old_new_vacated_WHITE_EDIT_PENDING_ASTRA.png'),'white_pixels':int(edit.sum()),'actual_gap128':gap['128'],'head_overlap':checks['head_projection_conflict'],'guard_intersections':checks['guard_intersections'],'new_calls':0},ensure_ascii=False,indent=2))
