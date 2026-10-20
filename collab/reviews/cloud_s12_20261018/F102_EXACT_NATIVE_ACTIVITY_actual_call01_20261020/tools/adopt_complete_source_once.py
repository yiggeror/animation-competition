"""One complete whole-original affine102 correction; never a similarity claim.
All10 regions incl both knees/support retained; complete sourceRGBA adoption.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,numpy as np
from scipy.ndimage import binary_fill_holes,label
O=Path(__file__).resolve().parents[1];R=O.parent;P=R/'F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020';M=R/'F098_EXACT_NATIVE_ACTIVITY_actual_call01_20261020'
assert not (O/'candidate/F102.png').exists(),'Already adopted once. Do not register again.'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawpath=O/'originals/F102_exact_native_activity_call01_raw.png';assert sha(rawpath)=='44bb4ed1db0d9131cd5c1b84a637bb90d3f4c932ee1a1720905817a7dab5338b'
raw=Image.open(rawpath).convert('RGBA');B=np.array(Image.open(M/'candidate/F098.png').convert('RGBA'));T=np.array(Image.open(P/'anatomy/F102_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png').convert('RGBA'))
probe=json.loads((O/'geometry/READ_ONLY_ALL_REGIONS_DRIFT_MEASUREMENTS.json').read_text());F=np.array(probe['one_proposed_common_affine']);samples=probe['rows']
for a in samples:a['distance_native']=a['distance'];a['distance_scene']=.7*a['distance'];assert a['NCC']>.5
scales=np.linalg.svd(F[:,:2])[1];ratio=float((scales[0]/scales[1]-1)*100)
measure={'status':'ONE_WHOLE_ORIGINAL_AFFINE_NOT_UNIFORM_SIMILARITY','raw_SHA256':sha(rawpath),'common_raw_to_native_matrix':F.tolist(),'linear_singular_values':scales.tolist(),'axis_scale_ratio_difference_percent':ratio,'actual_surface_measurements_all_regions':samples,'read_only_NCC_analysis_rescale_not_output_registration':probe['analysis_only_rescale'],'visible_grip_proxy_uncertainty':'approx3-5px; surface templates not hidden bone measurements','all10_regions_including_both_knees_and_shoe_used':True,'independent_limb_hand_finger_knee_transforms':0,'applied_whole_source_registrations':1,'new102_imagegen_calls':1,'new106_imagegen_calls':0}
(O/'geometry/MEASURED_NATIVE_DRIFT_AND_ONE_COMMON_FIT.json').write_text(json.dumps(measure,indent=2)+'\n')
def neutral(im):
 q=Image.new('RGBA',im.size,'#e1e4e6');q.alpha_composite(im);return q.convert('RGB')
inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2]
registered_path=O/'geometry/ONE_COMMON_REGISTERED_COMPLETE_RAW.png'
if registered_path.exists():reg=Image.open(registered_path).convert('RGBA') # reuse source staged before mask-path error; no second transform
else:
 reg=raw.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);reg.save(registered_path)
G=np.array(reg)
allow=np.array(Image.open(P/'masks/ALLOW_MINIMAL_NATIVE_ACTIVITY.png').convert('L'))>0;protected=~allow
support=np.array(Image.open(P/'masks/HARD_QUALIFIED_FINAL098_SHINS_SHOES_AIR.png').convert('L'))>0
n=B.copy();n[allow]=G[allow];Image.fromarray(n).save(O/'candidate/F102.png')
assert np.array_equal(n[allow],G[allow]);assert np.array_equal(n[protected],B[protected]);assert np.array_equal(n[support],B[support])
# Whole source front-digit ownership only; these source polygons are transformed
# by the SAME one common F as all the rest of the drawing, never separately.
frontpolys={'L_far_jade_actual_curled_front_digits':[(870,543),(889,541),(901,554),(901,575),(891,594),(875,604),(857,600),(861,584),(875,569)],'R_near_bare_actual_curled_front_digits':[(920,795),(937,783),(950,793),(958,810),(952,833),(937,852),(919,855),(906,841),(917,825)]}
front=Image.new('L',raw.size);d=ImageDraw.Draw(front)
for poly in frontpolys.values():d.polygon(poly,fill=255)
front=front.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST);own=(np.array(front)>0)&allow
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F102_BG_person.png');Image.fromarray(fg).save(O/'layers/F102_FG_true_front_fingers.png')
assert not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0));assert np.array_equal(np.maximum(bg,fg),n)
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&allow;lab,c=label(holes);regions=[]
for i in range(1,c+1):
 yy,xx=np.where(lab==i)
 if len(xx)>8:regions.append({'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]})
proof={'status':'COMPLETE_SEMANTIC_RAW_NATIVE_ADOPTED_ACTUAL_CANVAS_PENDING','raw_SHA256':sha(rawpath),'complete_common_registered_source_SHA256':sha(O/'geometry/ONE_COMMON_REGISTERED_COMPLETE_RAW.png'),'native_SHA256':sha(O/'candidate/F102.png'),'one_whole_source_native_matrix':F.tolist(),'new_source_RGBA_differences_to_common_registered_raw_inside_allowed':0,'outside_allowed_final098_RGBA_differences':0,'qualified_final098_shins_shoes_air_RGBA_differences':0,'original_alpha_policy':'raw full RGBA under one common geometric transform; no RGB/alpha filters, no opacity forcing, no semantic holes discarded','BG_FG_overlap':0,'BG_FG_RGBA_reconstruction_differences':0,'source_front_digit_polygons':frontpolys,'low_alpha_internal_components_for_actual_readback':regions,'technical_reference_pixels_adopted':0,'sparse_patch_adoption':False,'garment_RGB_thresholds':False,'new102_imagegen_calls':1,'raw_outputs':1,'repeat_imagegen':0,'new106_imagegen_calls':0,'actual102_Canvas':0}
(O/'geometry/COMPLETE_SOURCE_AND_FIXED_SUPPORT_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
neutral(Image.fromarray(n)).save(O/'diagnostics/ADOPTED_COMPLETE_REAL102_NATIVE.png')
board=Image.new('RGB',(1536,800),'#e1e4e6');d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for i,(name,im) in enumerate([('Frozen102 target / reference only',Image.fromarray(T)),('Unique raw / common coordinate correction',reg),('Complete actual102 / fixed final098 support',Image.fromarray(n))]):board.paste(neutral(im).resize((512,768)),(i*512,32));d.text((i*512+5,7),name,font=font,fill='#25313b')
board.save(O/'diagnostics/TARGET_COMMON_SOURCE_ADOPTED_SAME_SCALE.png')
print(json.dumps({'native_SHA256':proof['native_SHA256'],'common_matrix':F.tolist(),'grip_residuals_native':{a['region']:a['distance_native'] for a in samples if 'grip' in a['region']},'protected_RGBA_diff':0,'source_RGBA_diff':0,'internal_low_alpha_components':regions},indent=2))
