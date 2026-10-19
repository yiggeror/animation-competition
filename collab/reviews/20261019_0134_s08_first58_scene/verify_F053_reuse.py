"""Read-only locked pixel audit; no image writes and no Canvas rendering."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
import numpy as np
R=Path(sys.argv[1]).resolve();O=Path(__file__).resolve().parent;F=R/'F053_FINAL_LOCKED';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda p:np.array(Image.open(p).convert('RGBA'))
c=json.loads((F/'HAND_REUSE_CONTRACT.json').read_text());mother=F/'S08_F053_grandma_match_box_RGBA.png';assert sha(mother)=='7722c85545660ae240acc72d512985572b1a5ba5532780b150b4b8274c385ec2';assert mother.read_bytes()==(R/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png').read_bytes();assert c['near_match_head']==[1350,782.572972972973];assert c['near_visible_wood_exit']==[1310.442494558651,806.8258854425643];assert c['root_rebuild_whole_domain_pixels']==2383 and c['root_recomposition_diff_pixels']==57 and c['root_recomposition_max_RGBA_difference']==[100,49,13,0]
a=rd(mother);arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))['046'];layers={k:rd(O/'frames'/v['filename']) for k,v in arts.items()}
for k,v in arts.items():
 p=O/'frames'/v['filename'];assert sha(p)==v['sha256'];assert p.read_bytes()==(R/'F046_LAYER_PARTITION/frames'/p.name).read_bytes();assert np.array_equal(layers[k][:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(np.uint16) for v in layers.values()),a[:,:,3]);assert sum(v[:,:,3]>0 for v in layers.values()).max()==1
assert np.count_nonzero(layers['table_box'][:,:,3])==1665;assert not np.any(layers['arms'][981:,:,3]);assert np.where(layers['table_box'][:,:,3])[0].max()==970
out={'status':'PASS_F053_EXACT_ORIGINAL_F046_PIXEL_REUSE_NOT_CANVAS','mother_sha256':sha(mother),'mother_entire_file_equals046':True,'runtime_original_layers_equal046':True,'RGBA_reconstruction_exact':True,'alpha_overlap_pixels':0,'box_visible_pixels':1665,'box_bottom_y':970,'arms_at_or_below981':0,'near_match_head':c['near_match_head'],'root_rebuild_whole_domain_pixels':2383,'root_recomposition_diff_pixels':57,'root_recomposition_max_RGBA_difference':[100,49,13,0],'new_actual_canvas_frames':0};(O/'F053_REUSE_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
