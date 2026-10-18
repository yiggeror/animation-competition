from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter,ImageFont
from scipy.ndimage import binary_dilation
import numpy as np, json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'F003_input_gate';src=R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png';a=Image.open(src).convert('RGBA');ar=np.array(a);raw02=Image.open(R/'repair02_result_v1/registered/F000_call02_registered_RGBA.png').convert('RGBA')
for q in ['inputs','masks','geometry','qa']:(O/q).mkdir(exist_ok=True)
# Clean only this placement copy: one tiny wrongly included old sleeve wedge is replaced by the same call02's genuine index pixels.
# F000 FINAL is immutable; this is crop-boundary preparation, never painted skin.
patch=Image.new('L',a.size,0);ImageDraw.Draw(patch).polygon([(1040,785),(1046,785),(1047,790),(1044,792),(1040,791)],fill=255)
clean=Image.composite(raw02,a,patch);patch.save(O/'masks/same_raw02_index_cleanup_before_placement.png')
# Actual entire near hand up to wrist crease, and actual match selected separately.
hm=Image.new('L',a.size,0);ImageDraw.Draw(hm).polygon([(943,825),(958,818),(980,807),(1000,798),(1015,790),(1024,784),(1030,786),(1034,784),(1041,784),(1047,790),(1053,790),(1058,793),(1059,801),(1055,814),(1054,832),(1045,854),(1027,870),(1012,876),(978,878),(955,873)],fill=255)
pm=Image.open(R/'repair02_result_v5b_semantic_cleanup/masks/NEW_actual_prop_full_footprint.png').convert('L');pa=np.array(pm);y,x=np.indices(pa.shape);pa[(x<1038)|(x>1088)|(y<750)|(y>825)]=0;pm=Image.fromarray(pa);near_m=ImageChops.lighter(hm,pm);near_m.save(O/'masks/near_hand_and_real_match_source_selection.png');nma=np.array(near_m);cl=np.array(clean).astype(int);blue=(cl[:,:,2]>cl[:,:,0]+10)&(cl[:,:,2]>cl[:,:,1]+3);nma[blue]=0;near_m=Image.fromarray(nma);near_m.save(O/'masks/near_hand_and_real_match_source_selection.png');near=clean.copy();near.putalpha(ImageChops.multiply(clean.getchannel('A'),near_m));near.save(O/'inputs/F003_source_hand_match_clean_cut_RGBA.png')
# Old bare arm and old hand occupancy are explicitly cleared; fill requires real redraw of arm/blouse/blank space in the permission mask.
old=Image.new('L',a.size,0);ImageDraw.Draw(old).polygon([(651,823),(731,788),(790,899),(942,826),(978,806),(1046,782),(1065,792),(1063,851),(1034,880),(967,882),(802,985),(772,1001),(747,992),(719,956)],fill=255);old=ImageChops.lighter(old,near_m)
pre=np.array(a);pre[np.array(old)>0]=0;pre=Image.fromarray(pre,'RGBA');pre.alpha_composite(near,(48,-9));pre.save(O/'inputs/F003_scene_preplaced_RGBA.png')
# Old occupancy plus new full upperarm-elbow-forearm corridor; only the small lower cuff can adapt to the new upper-arm direction.
white=old.filter(ImageFilter.MaxFilter(7));d=ImageDraw.Draw(white);d.polygon([(643,779),(732,766),(758,801),(844,887),(997,807),(1033,837),(1017,883),(847,975),(811,987),(777,967),(679,838),(644,840)],fill=255)
# Keep the preplaced entire hand and real props exact, except a wrist-only 5px collar for natural attachment.
placed_m=Image.new('L',a.size,0);placed_m.paste(near_m,(48,-9));protect=np.array(placed_m)>0;w=np.array(white);w[protect]=0
# The wrist collar stops well before the palm; permits only seam integration, no new hand pose.
collar=Image.new('L',a.size,0);ImageDraw.Draw(collar).polygon([(989,815),(998,813),(1008,863),(999,868),(991,861)],fill=255);ca=np.array(collar)>0;w[ca]=255
# Original far hand, bangle, and box are hard-protected; native image output will never replace them.
far=Image.open(R/'new_mother_measurements/far_hand_box_actual_pixel_cut_mask.png').convert('L');fp=np.array(far)>0;w[fp]=0
# Explicit actual preplaced match all pixels protected even where it crosses the front of the fixed striker.
match_placed=Image.new('L',a.size,0);match_placed.paste(pm,(48,-9));w[np.array(match_placed)>0]=0
white=Image.fromarray(w);white.save(O/'masks/F003_scene_white_allowed_black_frozen.png');placed_m.save(O/'masks/F003_preplaced_hand_match_protected.png');far.save(O/'masks/F003_far_hand_box_jade_protected.png');match_placed.save(O/'masks/F003_match_protected.png')
# Freeze only original visible pixels of body outside white plus the rigidly placed real hand/props. Transparent new arm area remains editable.
box=(585,615,1235,1045);scale=2;crop=pre.crop(box);crop.resize((1300,860),Image.Resampling.LANCZOS).save(O/'inputs/F003_arm_contact_crop_2x_RGBA.png');white.crop(box).resize((1300,860),Image.Resampling.NEAREST).save(O/'inputs/F003_arm_contact_crop_2x_WHITE_MASK.png')
# Context is a clean approved source with a single construction chain, not a rendered pose template.
context=Image.new('RGBA',a.size,(244,242,237,255));context.alpha_composite(a);context=Image.blend(Image.new('RGBA',a.size,(244,242,237,255)),context,.32);context.alpha_composite(Image.composite(a,Image.new('RGBA',a.size,0),far));context.alpha_composite(near,(48,-9));dd=ImageDraw.Draw(context);dd.line([(668,683),(716,805),(807.61,931.48),(1001,839)],fill=(203,60,42,255),width=3)
for xx,yy in [(668,683),(716,805),(807.61,931.48),(1001,839)]:dd.ellipse((xx-4,yy-4,xx+4,yy+4),fill=(203,60,42,255))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);dd.text((593,624),'STRUCTURE ONLY: near arm connects to fixed real hand; no red lines in output',fill='black',font=font);context.crop(box).resize((1300,860),Image.Resampling.LANCZOS).convert('RGB').save(O/'inputs/F003_chain_CONTEXT_ONLY.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',a.size,col);bg.alpha_composite(pre);bg.crop(box).resize((1300,860),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'preplaced_{label}.png');bg.crop((980,725,1220,895)).resize((960,680),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'contact_{label}.png')
 ov=Image.new('RGBA',a.size,0);oo=np.array(ov);oo[w>0]=[90,225,90,105];ov=Image.fromarray(oo);bg.alpha_composite(ov);bg.crop(box).resize((1300,860),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'mask_overlay_{label}.png')
contract={'status':'F003_INPUT_GATE_ONLY_NOT_CALLED','current_total_native_calls':3,'source_locked_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'crop_scene_box':box,'uniform_enlargement':2,'output_crop_size':[1300,860],'whole_hand_match_translation':[48,-9],'head_scene':[1124,755],'visible_grip_scene':[1096,792],'visible_match_length':46.400431032480725,'far_box_fixed_center':[1125,750],'near_chain_construction':{'shoulder':[668,683],'sleeve_exit_guide':[716,805],'elbow':[807.61,931.48],'wrist':[1001,839]},'coordinate_warning':'Projected construction only, not3D bone lengths. Keep continuous shoulder-sleeve-upperarm-elbow-forearm-wrist path. Small lower cuff adapts; shoulder/upper sleeve stays original.','same_raw_cleanup':{'source':'repair02_result_v1/registered/F000_call02_registered_RGBA.png','selection':'masks/same_raw02_index_cleanup_before_placement.png','pixels':int((np.array(patch)>0).sum()),'note':'Only placement copy; existing raw02 true index pixels replace accidentally included blue sleeve within index edge. No painted anatomy, no F000 modification.'},'hard_protection':'All rigidly placed near palm/fingers/match except5px wrist seam; full far hand/box/jade; all scene pixels outside explicit white.','allowed':'Redraw near upperarm/elbow/forearm and tiny lower sleeve opening; restore old arm/hand vacancies to correct blouse, far upperarm where occluded, or transparent empty air.','native_call_planned':False}
(O/'geometry/contract.json').write_text(json.dumps(contract,indent=2));print(json.dumps(contract,indent=2))
