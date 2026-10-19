#!/usr/bin/env python3
"""Zero-call whole far-palm translation guide and full distal-arm local gate."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,label,distance_transform_edt
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['reference','masks','qa','geometry','requests']:(R/d).mkdir(exist_ok=True)
assert not(R/'requests/execution_state.json').exists()
p=S/'F063_call01_RAW_UNCHANGED.png';assert sha(p)=='8943ae4194c77bf6a87ec43bb62d0970c8ac29b28733827c0b7107e079945489'
im=Image.open(p).convert('RGBA');a=np.array(im);h,w=a.shape[:2];yy,xx=np.indices((h,w));fg=a[:,:,3]>0;rgb=a[:,:,:3].astype(int)
def poly(ps):
 z=Image.new('L',(w,h));ImageDraw.Draw(z).polygon(ps,fill=255);return np.array(z)>0
def save_mask(name,z):Image.fromarray(z.astype('uint8')*255).save(R/'masks'/name)
def material_skin(domain):
 warm=(rgb[:,:,0]>160)&(rgb[:,:,1]>100)&(rgb[:,:,0]-rgb[:,:,1]>15)&(rgb[:,:,0]-rgb[:,:,1]<110)&(rgb[:,:,1]-rgb[:,:,2]>13)&fg&domain
 warm=binary_fill_holes(warm)&domain
 # Complete visible brown/black outline and actual AA, never neutral metal/red.
 edge=binary_dilation(warm,iterations=4)&fg&domain
 brown_or_ink=(rgb.max(axis=2)<135)|((rgb[:,:,0]-rgb[:,:,1]>8)&(rgb[:,:,1]-rgb[:,:,2]>7))
 return binary_fill_holes(warm|(edge&brown_or_ink))&domain&fg
# Transverse wrist cut is technical extraction only, not a new wrist anatomy.
hand_domain=poly([(952,737),(1025,685),(1240,685),(1246,835),(1027,835),(1014,815)])
hand=material_skin(hand_domain)
# Keep the complete hand component; remove any disconnected red/metal edge seeds.
lab,n=label(hand);sizes=np.bincount(lab.ravel());sizes[0]=0;hand=lab==int(sizes.argmax())
# Carry the original low-alpha outer silhouette too: unpremultiplied alpha1/2
# may contain red RGB and must not be misclassified as rigid torch material.
hand_low_AA=binary_dilation(hand,iterations=8)&hand_domain&fg&(a[:,:,3]<128)
hand|=hand_low_AA
# Bright neutral pixels at the shared contact are actual silver, not palm.
neutral_silver=(rgb.max(axis=2)>135)&(rgb[:,:,0]-rgb[:,:,1]<25)&(rgb[:,:,1]-rgb[:,:,2]<22)&(a[:,:,3]>=128)
metal_contact_not_transported=hand&neutral_silver
hand&=~neutral_silver
# The old palm/three touching fingers own the dark contact line; metal under them
# is occluded unknown source, not reconstructed in this input guide.
shift=np.zeros_like(a);shift[49:]=np.where(hand[:-49,:,None],a[:-49],0)
shiftmask=shift[:,:,3]>0
wholehand=np.where(hand[:,:,None],a,0).astype('uint8');Image.fromarray(wholehand).save(R/'reference/source_complete_visible_far_hand_RGBA.png');Image.fromarray(shift).save(R/'reference/target_same_whole_hand_INTEGER_dy49_RGBA.png')
near_domain=poly([(127,693),(254,696),(400,775),(735,600),(890,608),(928,653),(924,730),(903,765),(861,797),(810,815),(760,806),(639,868),(425,980),(300,992),(205,963),(135,867)])
near=material_skin(near_domain)
# Whole actual distal arm: transverse elbow cut, both forearm contours, old wrist
# and every visible hand/finger. Full old/new air domain is separately white.
far_domain=poly([(695,943),(724,892),(849,815),(978,727),(1030,697),(1234,690),(1250,835),(1044,847),(944,959),(808,1057),(736,1060),(694,1013)])
far_material=(far_domain&fg)&~near
# All source near hand/arm material is stable foreground even at overlaps.
far_material|=hand
# Actual prop/receiver bounding silhouette, never all foreground in an ROI.
unit_domain=poly([(448,666),(527,651),(760,604),(887,592),(1049,529),(1165,497),(1210,499),(1241,523),(1250,568),(1248,701),(1225,734),(1170,744),(1102,735),(1031,713),(922,738),(840,771),(546,793),(471,782),(450,752)])
prop=unit_domain&fg&~near&~hand
# Silver lower border only: confined by real adjacent metal+old touching-finger
# silhouette in the authorized x1080..1230/y690..755 neighborhood.
silver_roi=(xx>=1080)&(xx<=1230)&(yy>=690)&(yy<=755)
metal=(np.abs(rgb[:,:,0]-rgb[:,:,1])<32)&(np.abs(rgb[:,:,1]-rgb[:,:,2])<26)&fg
known_silver=prop&silver_roi&metal
silver=binary_dilation(hand,iterations=6)&silver_roi&(prop|hand)  # only actual old-finger contact-edge neighborhood
# New lower elbow-to-wrist corridor, old material and both complete hand positions.
c=Image.new('L',(w,h));d=ImageDraw.Draw(c);pts=[(750,1020),(839,958),(926,883),(996,841),(1035,810)];d.line(pts,fill=255,width=153)
for x,y in pts:d.ellipse((x-76,y-76,x+76,y+76),fill=255)
corridor=np.array(c)>0
allowed_old=far_material|silver
stable_actual=fg&~allowed_old
# No hidden layer or empty-alpha rectangle is ever made hard.
white=(corridor|binary_dilation(far_material|hand|shiftmask,iterations=8)|silver)&~stable_actual
white|=silver&~near
stable_actual=fg&~white
# Input removes all old palm material; unknown occluded metal remains visibly
# unfilled, white, pending the authorized future native local repair.
out=a.copy();out[hand]=0
# Clear a short old wrist/forearm attachment triangle. It is WHITE, not painted.
cut=poly([(943,759),(1019,810),(1039,831),(1008,857),(961,822),(925,793)])&far_material
out[cut]=0
base=Image.fromarray(out);base.alpha_composite(Image.fromarray(shift));A=base;B=Image.fromarray(white.astype('uint8')*255)
A.save(R/'reference/A_same_raw_whole_hand_down49_FULL_CONTEXT_NOT_PRODUCTION.png');B.save(R/'reference/B_complete_far_forearm_and_hand_WHITE_REFERENCE.png')
for name,z in [('source_complete_visible_far_hand_material.png',hand),('target_same_complete_hand_down49_material.png',shiftmask),('source_near_arm_and_grasp_actual_material_HARD.png',near),('source_old_far_forearm_whole_material.png',far_material),('source_actual_prop_visible_material.png',prop),('silver_lower_rim_local_allowed_UNKNOWN_BEHIND_OLD_FINGERS.png',silver),('old_wrist_cut_WHITE_NOT_ANATOMY.png',cut),('HARD_local_context_actual_visible_material.png',stable_actual),('WHITE_complete_far_forearm_old_new_hand_air.png',white)]:save_mask(name,z)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 def bg(z):
  v=Image.new('RGBA',(w,h),col);v.alpha_composite(z);return v
 before=bg(im);after=bg(A);overlay=after.copy();wash=Image.new('RGBA',(w,h),(225,28,116,0));wash.putalpha(B.point(lambda x:90 if x else 0));overlay.alpha_composite(wash)
 sheet=Image.new('RGB',(w*3,h+34),(235,240,245));dr=ImageDraw.Draw(sheet)
 for j,(title,z)in enumerate([('RAW CONTEXT / NOT PRODUCTION MOTHER',before),('INTEGER whole hand dy49 / PREPOSITION NOT ART',after),('WHITE full distal arm / actual stable context',overlay)]):sheet.paste(z.convert('RGB'),(j*w,34));dr.text((j*w+12,6),title,font=font,fill='black')
 sheet.resize((1923,round((h+34)*.5))).save(R/f'qa/whole_context_target_and_full_white_{tone}.png')
 box=(900,655,1260,920);sheet=Image.new('RGB',(1080,299),(235,240,245));dr=ImageDraw.Draw(sheet)
 for j,(title,z)in enumerate([('SOURCE contact',before),('TARGET whole hand +49',after),('FULLWHITE includes exposed old palm',overlay)]):sheet.paste(z.crop(box).convert('RGB'),(j*360,34));dr.text((j*360+4,5),title,font=font,fill='black')
 sheet.resize((1620,448)).save(R/f'qa/whole_palm_fingertips_gap_and_white_{tone}.png')
 after.crop((650,690,1260,1110)).save(R/f'qa/full_far_forearm_old_new_{tone}.png')
def distance_pair(moving,fixed):
 dist,ind=distance_transform_edt(~fixed,return_indices=True);ys,xs=np.where(moving);j=int(np.argmin(dist[ys,xs]));y,x=int(ys[j]),int(xs[j]);return {'euclidean_pixel_center_distance':float(dist[y,x]),'moving_xy':[x,y],'fixed_xy':[int(ind[1,y,x]),int(ind[0,y,x])],'overlap_pixels':int((moving&fixed).sum())}
# Conservative scan of all moved visible source material vs known fixed visible
# prop and near grip. Silver source behind old fingers is explicitly unknown.
gaps={}
for threshold in [1,128,240]:
 moving=shift[:,:,3]>=threshold;fixedprop=prop&(a[:,:,3]>=threshold)&~silver;fixednear=near&(a[:,:,3]>=threshold)
 gaps[str(threshold)]={'whole_hand_vs_known_fixed_prop_excluding_allowed_unknown_rim':distance_pair(moving,fixedprop),'whole_hand_vs_near_grasp':distance_pair(moving,fixednear)}
# Also report every moved point vs all visible prop incl rim, without pretending
# an original occluded boundary exists; this is the stricter current-visible scan.
gaps['all_known_prop_alpha1']=distance_pair(shiftmask,prop)
fingertips={}
for name,(cx,cy)in [('visible_digit_left',(1110,714)),('visible_digit_middle',(1171,712)),('visible_digit_right',(1206,715))]:
 tip=shiftmask&(((xx-cx)**2+(yy-(cy+49))**2)<=22**2)
 assert tip.any()
 fingertips[name]={'source_tip_proxy':[cx,cy],'moved_tip_proxy':[cx,cy+49],'ROI_proxy_not_anatomical_measurement':True,'all_actual_tip_material_vs_known_prop':distance_pair(tip,prop),'all_actual_tip_material_vs_near_grasp':distance_pair(tip,near)}
gaps['visible_fingertip_material_subsets']=fingertips

ys,xs=np.where(shiftmask);handbbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
checks={'status':'PREPARED_LOCAL_PALM_INPUT_PENDING_ROOT_ASTRA_NO_CALL','source_raw_SHA256':sha(p),'context_raw_NOT_production_mother':True,'production_mother_044_SHA256':'fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9','source_size':[w,h],'whole_hand_affine':{'matrix':[[1,0],[0,1]],'translation_raw_pixels':[0,49],'scale':1,'integer_slice_no_resampling':True,'complete_visible_hand_and_all_visible_fingers_unsplit':True,'technical_wrist_cut_poly':[[952,737],[1025,685],[1240,685],[1246,835],[1027,835],[1014,815]],'occluded_anatomical_fingers_not_invented':True},'whole_hand_source_pixels':int(hand.sum()),'outer_original_low_alpha_AA_included_pixels':int(hand_low_AA.sum()),'actual_bright_neutral_silver_contact_pixels_excluded_from_hand':int(metal_contact_not_transported.sum()),'shifted_source_RGBA_exact':bool(np.array_equal(shift[49:][hand[:-49]],a[:-49][hand[:-49]])),'moved_material_bbox_halfopen':handbbox,'moved_material_crop_margin_L_T_R_B':[handbbox[0],handbbox[1],w-handbbox[2],h-handbbox[3]],'source_hand_top_or_bottom_clipped_pixels':int(hand[-49:].sum()),'local_context_HARD_actual_visible_pixels':int(stable_actual.sum()),'hard_alpha0_pixels':int((stable_actual&~fg).sum()),'white_pixels':int(white.sum()),'hard_white_intersection':int((stable_actual&white).sum()),'near_arm_grasp_white_intersection':int((near&white).sum()),'moved_whole_hand_outside_white':int((shiftmask&~white).sum()),'outside_white_RGBA_changes':int((np.any(np.array(A)!=a,axis=2)&~white).sum()),'silver_local_allowed_pixels':int(silver.sum()),'source_occluded_silver_under_old_fingers':'UNKNOWN: no yellow/grey/skin RGB painted into it; guide deletes old palm and exposes missing-source area, must be restored by future native local edit. No reconstructed rim gap claim.','gap_known_visible_material_scans_raw_pixels':gaps,'distance_caveat':'Pixel-center Euclidean distance is to CURRENT visible fixed material, not a recovered unknown silver lower rim; not a contact or future069 acceptance. 49 is guide amount only.','hand_ownership_extraction':'Manual transverse-wrist domain plus actual warm skin component, complete internal material/ink/AA envelope; source fingertip/silver occlusion line has manual source ownership uncertainty, all such contact-edge is white. Source untouched.','source_mask_selection_not_anatomical_measurement':True,'local_context_vs_final_production':'Local context outside white is retained raw for local-call registration ONLY. Final extraction may use actual new double arms and necessary silver rim only, returned to frozen044 real head/collar/ruffle/clothes/skirt/background with actual registration and seams rechecked. Raw altered head/clothes must never be adopted wholesale.','registration_initial_diagnostic_only':{'raw_width_to_original_frozen_700crop_uniform_inverse':700/1282,'approx_native_offset':[600,230],'not_final_registration_or_seam_pass':True},'new_calls':0,'069_unopened':True}
assert checks['shifted_source_RGBA_exact']and checks['source_hand_top_or_bottom_clipped_pixels']==0
assert checks['hard_alpha0_pixels']==checks['hard_white_intersection']==checks['near_arm_grasp_white_intersection']==checks['moved_whole_hand_outside_white']==checks['outside_white_RGBA_changes']==0
checks['source_snapshot_SHA256']={q.name:sha(q)for q in sorted(S.iterdir())if q.is_file()}
checks['production044_original_coordinate_guards']={'not_mapped_as_raw_context_guard':True,'head_collar':'F044_NATIVE_GUARD_head_neck_collar_actual.png','near_ruffle':'F044_NATIVE_GUARD_near_ruffle_actual_material.png','waist_skirt':'F044_NATIVE_GUARD_waist_and_skirt_actual_material.png','far_puff':'F044_NATIVE_GUARD_far_puff_actual_visible.png','note':'Original native coordinates and source RGBA retained; later actual new-arm registration and foreground occlusion must be checked, not blind hard-lock of hidden far layers.'}
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit A only within the complete local far-forearm/hand region shown by B, preserving this exact1282x1227 transparent canvas and all other visible local-context pixels. A is a technical whole-hand preposition, not finished anatomy or a production mother. The far anatomical LEFT whole hand, all visible fingers, palm thickness and source ink were shifted together by exactly49pixels down, without scaling, resampling or moving individual fingers. Preserve that complete-hand identity and obtain clearly visible air between every receiving finger/palm and the flashlight or near grasp. This is F063, OFF and unlit, not the later supported F069.
Redraw one continuous far forearm from the retained low elbow through a natural wrist into this whole receiving palm. The old/new forearm, wrist cut, vacated old palm and all connecting air are editable; never trace the technical extraction cut as anatomy. Keep the near complete arm and grasp, the flashlight rigid shape and switch, and the far sleeve/upper arm fixed. Restore only the small permitted lower silver-ring edge that was actually hidden by the old touching fingers; no larger prop redesign. Keep the original line and flat shadow style. Do not add fingers, duplicate a hand or touch the receiving hand to the ring. Return the same cropped transparent composition, without guides.
The surrounding raw head/clothes are local context only. Production adoption will extract only genuinely corrected new double-arm material and necessary silver-edge material, register them back to frozen044 source layers, and separately verify all sleeve/wrist/prop joins; the raw face, head and changed clothes must never replace frozen044.'''
(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(R/'reference/A_same_raw_whole_hand_down49_FULL_CONTEXT_NOT_PRODUCTION.png'),str(R/'reference/B_complete_far_forearm_and_hand_WHITE_REFERENCE.png')],'transparent_background':True},indent=2)+'\n')
(R/'README.md').write_text('''# F063 local whole-palm-away input gate — NO CALL

A is the same raw context with the complete visible receiving hand translated once by integer(0,+49); no individual finger move, scale or skin painting. Old hand and a short technical wrist cut are removed, with all old/new distal forearm/hand and vacated material WHITE. This is a preparation guide, not a finished arm or reconstructed rim. B is an editing-region reference, not an API hardmask.

The original touching fingers hid real silver material; removing them does not recover that unknown rim. Only the permitted actual lower-rim neighborhood is editable. Gap scans measure actual moved source material against currently visible fixed prop/grasp, explicitly not against an invented silver boundary. Source extraction mask/ink ownership at the old shared contact edge is manual and wholly editable.

IMPORTANT: raw063 changed original head/clothes. RAW HEAD/CLOTHES ARE LOCAL CONTEXT ONLY, NOT A FROZEN PRODUCTION MOTHER. Production mother remains locked044 fe70d79e…381cfad9. After any authorized future local correction, adopt only actual new double-arm material and necessary silver-edge material, register back to frozen044 head/collar/ruffle/clothes/skirt/background, and actually verify sleeve/wrist/prop seams. The width-defined raw→700crop inverse is an initial diagnostic only, not accepted final registration. Frozen044 source/guards are archived as separate original-coordinate sources, never shifted to match altered raw.

Input gate only; NO GENERATION, pending root/Astra image review. No069 or following state prepared. Run prepare.py from this package to reproduce A/B and source masks. Actual hand gap and full-white scope require root/Astra review before a single local request is authorized.
''')
print(json.dumps({'checks':{k:checks[k]for k in ['whole_hand_source_pixels','moved_material_bbox_halfopen','white_pixels','near_arm_grasp_white_intersection','moved_whole_hand_outside_white','outside_white_RGBA_changes','gap_known_visible_material_scans_raw_pixels']}},indent=2))
