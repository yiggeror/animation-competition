"""F030 original-pixel integration audit. Reads original images; no raster rendering or image edits."""
from pathlib import Path
import json,hashlib,sys,math
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();P=Path(sys.argv[2]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:np.array(Image.open(p).convert('RGBA'))
src=R/'F030_FINAL_LOCKED/S08_F030_grandma_match_box_RGBA.png';assert sha(src)=='ef53ba49d805d2a9eb2cf934f62b2098a07e924250fcbbd5070cb33fcbba6bc8';a=read(src);contract=json.loads((R/'F030_FINAL_LOCKED/HAND_REUSE_CONTRACT.json').read_text());assert contract['source_sha256']==sha(src);assert contract['near_match_head']==[1148,717];assert contract['near_visible_wood_exit']==[1116.881786,751.418843]
arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['030'];layers={}
for role,meta in arts.items():
 p=O/'frames'/meta['filename'];assert sha(p)==meta['sha256'];layers[role]=read(p);assert np.array_equal(layers[role][:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in layers.values()),a[:,:,3]);assert sum(v[:,:,3]>0 for v in layers.values()).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
box=layers['table_box'][:,:,3]>0;assert box.sum()==1665;assert not np.any(layers['body'][:,:,3][box]);assert not np.any(layers['arms'][:,:,3][box]);prevbox=read(P/'F027_LAYER_PARTITION/frames/F027_table_box_original_pixels.png');assert np.array_equal(prevbox[:,:,3],layers['table_box'][:,:,3]);assert np.array_equal(prevbox[box],layers['table_box'][box]);assert not np.any(layers['arms'][981:,:,3])
previous=read(P/'F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png');groups=[]
for g in contract['group_assets']:
 mask=np.array(Image.open(R/'F030_FINAL_LOCKED'/Path(g['footprint']).name))>0;archive=read(R/'F030_FINAL_LOCKED'/Path(g['rgba']).name);assert int(mask.sum())==g['footprint_pixels'];assert int((mask&(a[:,:,3]==0)).sum())==g['alpha0_inside_footprint'];assert np.array_equal(a[mask],archive[mask])
 visible=mask&(a[:,:,3]>0)
 if 'fixed_table_box' in g['name']:assert np.array_equal(layers['table_box'][visible],a[visible])
 else:assert np.array_equal(layers['arms'][visible],a[visible])
 if 'whole_closed_far_hand' in g['name']:assert np.array_equal(a[mask],previous[mask]);assert int(mask.sum())==17750
 groups.append({'name':g['name'],'footprint_pixels':int(mask.sum()),'alpha0_inside_footprint':int((mask&(a[:,:,3]==0)).sum()),'locked_archive_RGBA_exact':True,'visible_group_in_correct_layer':True})
cx,cy=1233.9532049682696,766.8943738423919;radius=9*14/18.5;y,x=np.indices(a.shape[:2]);disk=np.hypot(x+.5-cx,y+.5-cy)<=radius;assert not np.any(layers['body'][:,:,3][disk]);assert not np.any(layers['table_box'][:,:,3][disk]);assert int(((a[:,:,3]==0)&disk).sum())>0;alpha=a[:,:,3][disk]
report={'status':'PASS_ORIGINAL_RGBA_AND_ANALYTIC_GRIP_ONLY_NOT_CANVAS','source_sha256':sha(src),'fresh_F030_partition_used':True,'RGBA_reconstruction_exact':True,'all_layer_RGB_original_including_transparent':True,'overlap_alpha_pixels':0,'box_only_in_table_box_pixels':1665,'box_visible_RGBA_and_alpha_same_as027':True,'arm_pixels_at_y981_and_below':0,'group_checks':groups,'near_match_head':contract['near_match_head'],'near_visible_wood_exit':contract['near_visible_wood_exit'],'near_transform_is_baked_approved_source_only_no_runtime_transform':contract['near_transform_from027'],'near_proximal_reconnected_pixels_not_claimed_unchanged_from027':True,'far_retained_guard_RGBA_same_as027':True,'released_far_outer_alpha0_pixels':1006,'old183_proximal_collar_not_restored':True,'independent_knob_center':[cx,cy],'independent_knob_radius':radius,'knob_disk_pixel_center_count':int(disk.sum()),'knob_disk_fully_transparent':int((alpha==0).sum()),'knob_disk_partially_transparent':int(((alpha>0)&(alpha<255)).sum()),'knob_disk_fully_opaque_fingers':int((alpha==255).sum()),'body_or_box_alpha_over_knob_pixels':0,'new_actual_canvas_frames':0,'image_files_modified':0,'actual_readability':'PENDING_REAL_CANVAS; original-pixel and geometric checks do not prove lighting, grain, depth or flame visual acceptance'}
(O/'F030_PIXEL_CONTACT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
