"""Read-only F020 original-pixel and translated-match audit; never writes images."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'F020_FINAL_LOCKED/S08_F020_grandma_match_box_RGBA.png';assert sha(src)=='ff4fad4d91762f7a5e8687741d0d09747e466474b91c4f4d0d8f9df032d516e6'
a=np.array(Image.open(src).convert('RGBA'));arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['020'];ls={}
for role,meta in arts.items():
 p=O/'frames'/meta['filename'];assert sha(p)==meta['sha256'];ls[role]=np.array(Image.open(p).convert('RGBA'));assert np.array_equal(ls[role][:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in ls.values()),a[:,:,3]);overlap=sum(v[:,:,3]>0 for v in ls.values());assert overlap.max()==1
reb=Image.fromarray(ls['body']);reb=Image.alpha_composite(reb,Image.fromarray(ls['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(ls['arms']));assert np.array_equal(np.array(reb),a)
b=ls['table_box'][:,:,3]>0;assert int(b.sum())==1665;assert not np.any(ls['body'][:,:,3][b]);assert not np.any(ls['arms'][:,:,3][b]);yy,xx=np.where(b);by,bx=np.where(ls['table_box'][:,:,3]>128)
box017=np.array(Image.open(R/'F017_LAYER_PARTITION/frames/F017_table_box_original_pixels.png').convert('RGBA'));assert np.array_equal(box017[:,:,3],ls['table_box'][:,:,3]);assert np.array_equal(box017[b],ls['table_box'][b])
prior=np.array(Image.open(R/'F017_FINAL_LOCKED/S08_F017_grandma_match_box_RGBA.png').convert('RGBA'));guard_path=R/'F020_input_gate/masks/F020_true_hand_match_hard_guard_except_wrist_collar.png';g=np.array(Image.open(guard_path))>0;y,x=np.where(g);before=prior[y-5,x+12];after=a[y,x];assert len(x)==7631;assert np.array_equal(before,after)
assert np.array_equal(a[787,1062],prior[782,1074]);assert np.array_equal(a[824,1034],prior[819,1046])
result={'status':'PASS_ORIGINAL_RGBA_PARTITION_AND_F020_CONTACT_IDENTITY_ONLY_NOT_CANVAS','source_sha256':sha(src),'all_layer_RGB_original_including_transparent':True,'overlap_alpha_pixels':int((overlap>1).sum()),'RGBA_reconstruction_exact':True,'table_box_pixels':1665,'table_box_alpha_in_body_or_arms':0,'table_box_visible_RGBA_and_alpha_exact_same_as017':True,'table_box_bbox_exclusive':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'table_box_alpha_gt128_base':int(by.max()),'near_hand_match_rigid_translation':[-12,5],'near_hand_match_guard_pixels':7631,'near_hand_match_guard_changed_RGBA_pixels':0,'guard_file_sha256':sha(guard_path),'translated_guard_RGBA_sha256':hashlib.sha256(after.tobytes()).hexdigest(),'near_match_head':[1062,787],'near_match_head_RGBA':a[787,1062].tolist(),'near_grip':[1034,824],'near_grip_RGBA':a[824,1034].tolist(),'near_match_length':float(np.hypot(28,37)),'mechanism_lift':0,'lever_contact':False,'original_pixels_repositioned_by_this_scene':0,'image_files_modified':0,'actual_canvas_frames':0,'note':'The hand/match translation is already part of the approved drawing; scene code applies no transform. Use the exact semantic hard guard, not a rectangular ROI containing changed neighboring pixels.'}
(O/'PIXEL_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
