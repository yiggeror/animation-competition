"""Read-only locked F064 runtime pixel and occlusion check. No Canvas rasterization."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
import numpy as np
R=Path(sys.argv[1]).resolve();O=Path(__file__).resolve().parent;F=R/'F064_FINAL_LOCKED';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda p:np.array(Image.open(p).convert('RGBA'))
c=json.loads((F/'HAND_REUSE_CONTRACT.json').read_text());mother=F/'S08_F064_grandma_match_box_RGBA.png';assert sha(mother)=='29a09ab0fca025b063c01bf53a9f69d62fde2f8a7ece34d81533c2022b63deab';assert c['near_match_head']==[1282.6806826223356,928.1901186474938];assert c['near_visible_wood_exit']==[1236.6785550080258,934.2567696970257];assert abs(np.linalg.norm(np.array(c['near_match_head'])-c['near_visible_wood_exit'])-46.400431032481)<1e-8
assert c['root_rebuild_whole_domain_pixels']==2569 and c['root_recomposed_vs_flat_differences']==1007 and c['root_recomposed_max_RGBA_difference']==[241,207,174,255];assert c['near_true_distal_with_AA_pixels']==6839 and c['near_sourceover_hard_vs_final_changed']==0
sealed=json.loads((F/'SEALED_MANIFEST.json').read_text());assert sealed['status']=='FINAL_DUAL_STATIC_COLOR_FORMAL5F_LAYER_REUSE_APPROVED'
for r in sealed['files']:assert sha(Path(r['path']))==r['sha256'],r['path']
a=rd(mother);arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['064'];layers={k:rd(O/'frames'/v['filename']) for k,v in arts.items()}
for k,v in arts.items():
 p=O/'frames'/v['filename'];assert sha(p)==v['sha256'];assert p.read_bytes()==(R/'F064_LAYER_PARTITION/frames'/p.name).read_bytes();assert np.array_equal(layers[k][:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in layers.values()),a[:,:,3]);assert sum(v[:,:,3]>0 for v in layers.values()).max()==1
box=layers['table_box'];visible=box[:,:,3]>0;prior=rd(R/'F061_LAYER_PARTITION/frames/F061_table_box_original_pixels.png');full=prior[:,:,3]>0;occluded=full&~visible
assert full.sum()==1665 and visible.sum()==1629 and occluded.sum()==36;assert not np.any(visible&~full);assert np.array_equal(box[visible],prior[visible]);assert np.all(layers['arms'][occluded,3]>0);assert not np.any(layers['body'][occluded,3]);assert np.any(a[occluded]!=prior[occluded],axis=1).sum()==30
assert (F/'F064_fixed_table_box_RGBA.png').read_bytes()==(R/'F061_FINAL_LOCKED/F061_fixed_table_box_RGBA.png').read_bytes();assert not np.any(layers['arms'][981:,:,3]);assert np.where(visible)[0].max()==970
y,x=np.indices(a.shape[:2]);disk=np.hypot(x+.5-1233.9532049682696,y+.5-766.8943738423919)<=9*14/18.5;p=rd(R/'F061_FINAL_LOCKED/S08_F061_grandma_match_box_RGBA.png');assert np.array_equal(a[disk],p[disk]);assert not np.any(layers['body'][disk,3]);assert not np.any(box[disk,3])
out={'status':'PASS_F064_ORIGINAL_RUNTIME_PIXELS_NOT_CANVAS','mother_sha256':sha(mother),'all_runtime_layer_RGB_original':True,'RGBA_reconstruction_exact':True,'alpha_overlap_pixels':0,'complete_original_box_archive_pixels':1665,'complete_original_box_archive_byte_equal_F061':True,'current_visible_box_pixels':1629,'true_front_arm_occludes_original_box_pixels':36,'occluded_original_box_RGBA_changed':30,'visible_box_RGBA_same_F061':True,'box_bottom_y':970,'arms_at_or_below981':0,'low_knob148px_RGBA_equal_F061':True,'near_match_head':c['near_match_head'],'near_visible_wood_exit':c['near_visible_wood_exit'],'source_reuse_contract_disclosure':c['root_recomposition_baseline_disclosure'],'new_actual_canvas_frames':0};(O/'F064_PIXEL_CONTACT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
