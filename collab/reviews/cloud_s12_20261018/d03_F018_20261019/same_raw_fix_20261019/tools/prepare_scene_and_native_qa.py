from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;R=S.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=P/'originals/F018_raw_call01.png';candidate=O/'candidate/F018.png';m0=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png';m12=S/'d03_F018_inputs_20261019/inputs/01_locked_F012.png';a=np.array(Image.open(raw));b=np.array(Image.open(candidate));g=np.array(Image.open(O/'candidate/F018_geometry_only.png'));m=np.array(Image.open(m0));k=np.array(Image.open(m12));Q=O/'qa'
# Every original ground-contact polygon/base retained, but masks use actual repaired018 alpha.
base=json.loads((S/'d01_F000/qa/native_alpha_contacts_registration.json').read_text());contacts=[]
for c in base['contacts']:
 mask=Image.new('L',(1024,1536));ImageDraw.Draw(mask).polygon([tuple(v) for v in c['source_alpha_polygon_native']],fill=255);aa=np.minimum(b[:,:,3],np.array(mask));im=np.zeros_like(b);im[:,:,3]=aa;Image.fromarray(im).save(O/f"contact_masks/{c['name']}.png");contacts.append(c|{'alpha_pixels_nonzero':int(np.count_nonzero(aa)),'source_native_SHA256':sha(candidate),'path':f"../contact_masks/{c['name']}.png",'note':'Actual repaired018 alpha, original approved contact polygon/base. Far knee/shin occluded, not six visible supports.'})
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps({'native_candidate_SHA256':sha(candidate),'native_size':[1024,1536],'registration':{'scale':.7,'x':275,'y':112},'contacts':contacts,'all_six_contacts_independently_visible':False,'frame':18,'absolute_time':.75,'contact_transform_and_anchor_scheme_unchanged':True},indent=2)+'\n')
source=S/'d02_F012_20261019/placket_tip_fix_20261019/scene/s12_F012_scene.js';src=source.read_text();new=src.replace('F012','F018').replace('export const DURATION=13/24;','export const DURATION=19/24;').replace('!==12','!==18').replace('actual time .5','actual time .75')
(O/'scene/s12_F018_scene.js').write_text(new)
for start,end in [('let ROOM = null;','function nativeContactShadows'),('function nativeContactShadows','let cachedShadows,cachedProps;'),('},light:(t)=>','export async function renderFrame')]:assert src[src.index(start):src.index(end)]==new[new.index(start):new.index(end)]
for relative in ['../../../../../../js/paint/paintshot.js','../../../../../../js/lamp/crane.js','../../../../../../js/puppet.js','../../../geometry/three_key_pose_proposal.json','../qa/native_alpha_contacts_registration.json','../candidate/F018.png']:assert ((O/'scene')/relative).resolve().is_file(),relative
(O/'qa/scene_source_equivalence.json').write_text(json.dumps({'source_entry':str(source.relative_to(R)),'source_entry_SHA256':sha(source),'new_entry_SHA256':sha(O/'scene/s12_F018_scene.js'),'only_entry_changes':'Native asset/hash/contact data, strict frame18 gate, DURATION19/24 and labels; actualt.75','box_cloth_pressure_crane_plane55_rod_endpoints_light_camera_functions_byte_equal':True,'native_registration_unchanged':True,'source_pose_A0_unchanged':True,'old_code_character_not_used':True},indent=2)+'\n')
# Color gate on fixed raw018 whole-material masks; no post-correction sample shrinkage.
materials={}
for name in ['hair','blouse_blue','trousers']:
 sm=np.array(Image.open(P/f'qa/masks/raw_F018_{name}.png'))>0;mm=np.array(Image.open(P/f'qa/masks/locked_F000_{name}.png'))>0;delta=b[sm,:3].mean(0)-m[mm,:3].mean(0);materials[name]={'fixed_raw_material_pixels':int(sm.sum()),'fixed000_material_pixels':int(mm.sum()),'corrected_delta_vs000_RGB':delta.tolist(),'within4':bool(np.max(abs(delta))<=4)};assert materials[name]['within4']
# Protected skin face/near hand are exact; moving skin is resampling of the same raw.
near=np.array(Image.open(P/'qa/masks/F018_near_right_hand_skin.png'))>0;assert np.array_equal(b[near],a[near]);assert np.array_equal(b[:,:,3],g[:,:,3]);geomdomain=np.array(Image.open(O/'masks/geometry_edit_domain.png'))>0;colorchanged=np.array(Image.open(O/'masks/color_actual_RGB_changed.png'))>0;assert not np.any(np.any(b!=a,2)&~(geomdomain|colorchanged));assert np.array_equal(b[~geomdomain,3],a[~geomdomain,3])
for name in ['trousers']:
 mask=np.array(Image.open(P/f'qa/masks/raw_F018_{name}.png'))>0;assert np.array_equal(b[mask],a[mask])
# Static tip matched anchors, using same masks before/after.
tipstats={}
for plane in ['lit','shade']:
 for mat in ['blue','flowers']:
  mask=np.array(Image.open(O/f'masks/tip_{plane}_matched_{mat}.png'))>0
  if not mask.any():continue
  delta=b[mask,:3].mean(0)-k[mask,:3].mean(0);tipstats[plane+'_'+mat]={'pixels':int(mask.sum()),'delta_vs_final012_RGB':delta.tolist(),'small_sample':int(mask.sum())<30}
# Native physical-alpha gap and source mapping are preflight; actual raster gate is separate.
report={'candidate_SHA256':sha(candidate),'source_raw_SHA256':sha(raw),'geometry':json.loads((Q/'native_geometry_repair.json').read_text()),'materials':materials,'skin_disposition':'No native skin color edits; near hand/source mask exact; far skin moved once by premultiplied same-raw sampling.','tip_matched_static_samples':tipstats,'outside_geometry_or_color_support_RGBA_exact_raw':True,'alpha_outside_geometry_exact_raw':True,'near_right_hand_RGBA_exact_raw':True,'trousers_RGBA_exact_raw':True,'imagegen_calls':0,'native_scene_render_status':'NOT_RENDERED_YET'}
(Q/'native_repair_validation.json').write_text(json.dumps(report,indent=2)+'\n')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(ar,color=(205,208,211)):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(*color,255)),Image.fromarray(ar)).convert('RGB')
board=Image.new('RGB',(1536,1604),'white');d=ImageDraw.Draw(board)
for row,color in enumerate([(205,208,211),(36,38,42)]):
 for col,(ar,label) in enumerate([(m,'LOCKED000 MATERIAL'),(k,'LOCKED FINAL012'),(b,'REPAIRED018 SAME RAW')]):board.paste(flat(ar,color).resize((512,768)),(col*512,row*802+34));d.text((col*512+8,row*802+6),label,font=font(16),fill='black')
board.save(Q/'01_000_012_018_same_scale_gray_dark.jpg',quality=95)
for name,crop,scale,items in [('02_complete_arm_both_hands_before_after2x.jpg',(600,650,1024,1066),2,[(a,'RAW018'),(b,'REPAIRED018')]),('03_000_012_018_tip_color4x.jpg',(453,928,542,1062),4,[(m,'LOCKED000'),(k,'FINAL012'),(b,'REPAIRED018')])]:
 w=(crop[2]-crop[0])*scale;h=(crop[3]-crop[1])*scale;board=Image.new('RGB',(w*len(items),h+34),'#cdd0d3');d=ImageDraw.Draw(board)
 for c,(ar,label) in enumerate(items):board.paste(flat(ar).crop(crop).resize((w,h),Image.Resampling.NEAREST),(c*w,34));d.text((c*w+8,7),label,font=font(19),fill='black')
 board.save(Q/name,quality=96)
# True repaired drawing over the unchanged rod geometry, explicitly marked as diagnostic only.
D=json.loads((S/'geometry/three_key_pose_proposal.json').read_text())['states'][0]['points_scene'];diag=flat(b);d=ImageDraw.Draw(diag)
for rod,endkey in [('L','P_neck'),('R','P_body')]:
 start=(np.array(D['free_grip'+rod])-[275,112])/.7;end=(np.array(D[endkey])-[275,112])/.7;d.line([tuple(start),tuple(end)],fill=(62,42,30),width=10);d.line([tuple(start),tuple(end)],fill=(201,154,82),width=4)
diag.crop((700,780,1024,1065)).resize((972,855),Image.Resampling.NEAREST).save(Q/'04_all_fingers_unchanged_rods_DIAGNOSTIC3x.jpg',quality=96)
# Adapt the previous readback audit only; scene is rendered once at18/24.
s= (S/'d02_F012_20261019/same_raw_fix_20261019/tools/network_audit_chromium.cjs').read_text().replace('F012','F018').replace('frame:12','frame:18');(O/'tools/network_audit_chromium.cjs').write_text(s)
print(json.dumps({'candidate_SHA256':sha(candidate),'entry_SHA256':sha(O/'scene/s12_F018_scene.js'),'materials':materials,'tip_matched_samples':tipstats,'scene_time':.75,'next':'View native diagnostics, then one actual F018 render'},indent=2))
