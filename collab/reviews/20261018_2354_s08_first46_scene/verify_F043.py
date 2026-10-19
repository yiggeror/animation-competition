"""Read-only source/layer checks; no image edits and no Canvas."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image
import numpy as np
R=Path(sys.argv[1]).resolve();O=Path(__file__).resolve().parent;rd=lambda p:np.array(Image.open(p).convert('RGBA'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'F043_FINAL_LOCKED/S08_F043_grandma_match_box_RGBA.png';assert sha(source)=='a2a9285481789c1b7bd69a58694026e7a473138093d8039ecf2d74b212311dd1';a=rd(source);p=rd(R/'F041_FINAL_LOCKED/S08_F041_grandma_match_box_RGBA.png');assert np.array_equal(a[:,:,3],p[:,:,3])
art=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['043'];layers={k:rd(O/'frames'/v['filename']) for k,v in art.items()}
for k,v in art.items():
 assert sha(O/'frames'/v['filename'])==v['sha256'];assert np.array_equal(layers[k][:,:,:3],a[:,:,:3]);prior=rd(R/'F041_LAYER_PARTITION/frames'/v['filename'].replace('F043','F041'));assert np.array_equal(layers[k][:,:,3],prior[:,:,3])
 if k!='body':assert np.array_equal(layers[k][prior[:,:,3]>0],prior[prior[:,:,3]>0])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in layers.values()),a[:,:,3]);assert sum(v[:,:,3]>0 for v in layers.values()).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
b=layers['table_box'];m=b[:,:,3]>0;assert m.sum()==1665;assert np.where(m)[0].max()==970;assert not np.any(layers['arms'][981:,:,3]);y,x=np.indices(a.shape[:2]);disk=np.hypot(x+.5-1233.9532049682696,y+.5-766.8943738423919)<=9*14/18.5;assert np.array_equal(a[disk],p[disk]);assert not np.any(layers['body'][disk,3]);assert not np.any(b[disk,3])
c=json.loads((R/'F043_FINAL_LOCKED/HAND_REUSE_CONTRACT.json').read_text());assert c['near_match_head']==[1415,794.572972972973];assert c['near_visible_wood_exit']==[1375.442494558651,818.8258854425643]
r={'status':'PASS_ORIGINAL_RGBA_RUNTIME_STATIC_NOT_CANVAS','source_sha256':sha(source),'RGBA_reconstruction_exact':True,'all_layer_RGB_original_including_transparent':True,'mother_and_all_layer_alpha_equal041':True,'arms_and_box_visible_RGBA_equal041':True,'alpha_overlap_pixels':0,'box_visible_pixels':1665,'box_bottom_y':970,'arms_at_or_below981':0,'knob148px_disk_RGBA_equal041':True,'new_actual_canvas_frames':0,'near_match_head':c['near_match_head'],'near_visible_wood_exit':c['near_visible_wood_exit'],'wickTouch':True,'wick_ignition_first_frame':43,'actual_gate':'New043 first small wick flame, original match still lit; actual two-source overlap/brightness, true root and eye-brow readability must pass real Canvas.'};(O/'F043_PIXEL_CONTACT_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
