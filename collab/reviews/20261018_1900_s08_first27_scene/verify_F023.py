"""Original RGBA, transparent grip-seat and analytic lamp geometry audit. No image output."""
from pathlib import Path
import sys,json,hashlib,math
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'F023_FINAL_LOCKED/S08_F023_grandma_match_box_RGBA.png';assert sha(src)=='dc35d227078f37e18340635c95f721a5b8495ecbb87b802df51447d375987e47';a=np.array(Image.open(src).convert('RGBA'));arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['023'];layers={}
for role,meta in arts.items():
 p=O/'frames'/meta['filename'];assert sha(p)==meta['sha256'];layers[role]=np.array(Image.open(p).convert('RGBA'));assert np.array_equal(layers[role][:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in layers.values()),a[:,:,3]);overlap=sum(v[:,:,3]>0 for v in layers.values());assert overlap.max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
box=layers['table_box'][:,:,3]>0;assert box.sum()==1665;assert not np.any(layers['body'][:,:,3][box]);assert not np.any(layers['arms'][:,:,3][box]);prevbox=np.array(Image.open(R/'F020_LAYER_PARTITION/frames/F020_table_box_original_pixels.png').convert('RGBA'));assert np.array_equal(prevbox[:,:,3],layers['table_box'][:,:,3]);assert np.array_equal(prevbox[box],layers['table_box'][box])
previous=np.array(Image.open(R/'F020_FINAL_LOCKED/S08_F020_grandma_match_box_RGBA.png').convert('RGBA'));nearMask=R/'F023_FINAL_LOCKED/F023_true_near_hand_match_footprint.png';g=np.array(Image.open(nearMask))>0;yy,xx=np.where(g);assert len(xx)==7631;assert np.array_equal(a[yy,xx],previous[yy-4,xx-8]);assert np.array_equal(a[791,1070],previous[787,1062]);assert np.array_equal(a[828,1042],previous[824,1034])
farMask=R/'F023_FINAL_LOCKED/F023_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png';fm=np.array(Image.open(farMask))>0;far=np.array(Image.open(R/'F023_FINAL_LOCKED/F023_whole_closed_far_hand_jade_RGBA.png').convert('RGBA'));assert int(fm.sum())==18939;assert np.array_equal(a[fm],far[fm])
cx,cy=1254.0390495120525,737.5349762791033;radius=9*14/18.5;y,x=np.indices(a.shape[:2]);dist=np.hypot(x+.5-cx,y+.5-cy);disk=dist<=radius;inner=dist<=radius-1
assert not np.any(layers['body'][:,:,3][disk]);assert not np.any(layers['table_box'][:,:,3][disk]);assert int(((a[:,:,3]==0)&inner).sum())>0
stats={}
for k,m in [('knob_pixel_center_disk',disk),('knob_conservative_inner_disk',inner)]:
 alpha=a[:,:,3][m];stats[k]={'pixels':int(m.sum()),'fully_transparent':int((alpha==0).sum()),'partially_transparent':int(((alpha>0)&(alpha<255)).sum()),'fully_opaque_fingers':int((alpha==255).sum()),'analytic_underlying_knob_transmission_sum_pixels':float((1-alpha.astype(float)/255).sum())}
pivot=np.array([1301.4864864864865,791.545945945946]);tip=np.array([cx,cy]);shaft=[]
for length in [9,12,16,24,40,60,70]:
 point=tip+(pivot-tip)*length/np.linalg.norm(pivot-tip);px,py=np.floor(point).astype(int);shaft.append({'distance_from_tip':length,'xy':point.tolist(),'source_RGBA':a[py,px].tolist()})
report={'status':'PASS_ORIGINAL_RGBA_AND_ANALYTIC_GRIP_SEAT_ONLY_NOT_CANVAS','source_sha256':sha(src),'RGBA_reconstruction_exact':True,'all_layer_RGB_original_including_transparent':True,'overlap_alpha_pixels':0,'box_only_in_table_box_pixels':1665,'box_visible_RGBA_and_alpha_same_as020':True,'near_translation_from020':[8,4],'near_guard_pixels':7631,'near_guard_changed_RGBA_pixels':0,'near_guard_RGBA_sha256':hashlib.sha256(a[yy,xx].tobytes()).hexdigest(),'near_match_head':[1070,791],'near_visible_wood_exit':[1042,828],'near_head_RGBA':a[791,1070].tolist(),'far_whole_footprint_pixels':int(fm.sum()),'far_visible_pixels':int((fm&(a[:,:,3]>0)).sum()),'whole_far_hand_and_transparent_seat_copy_exact':True,'independent_knob_center':[cx,cy],'independent_knob_radius':radius,'body_or_box_opaque_over_knob_pixels':0,'alpha_at_center_four_pixels':a[737:739,1253:1255,3].tolist(),'analytic_grip_visibility':stats,'shaft_source_samples':shaft,'no_code_rod_or_knob_added_to_character_layers':True,'image_files_modified':0,'actual_canvas_frames':0,'actual_readability_status':'PENDING_REAL_CANVAS; analytic disk counts do not include Canvas edge antialiasing, lighting, grain, or visual judgement'}
(O/'F023_PIXEL_CONTACT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
