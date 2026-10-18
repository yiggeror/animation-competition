"""Read-only original-RGBA audit. This does not generate, edit, or render any image."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent
R=Path(sys.argv[1]).resolve()
arts=json.loads((O/'layer_contract.js').read_text().split(' = ',1)[1].rstrip(';\n'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];head_arrays={}
expected={'014':'d1727966cfc41b5a61f91c8b19cf8177fe88f12ce20c7d4a1036305b3fbe3d51','017':'4e7be236953bee57aa8c3ecfc142893ab15c67095fae4b77718ff6aba0b1ec20'}
for f,roles in arts.items():
 src=R/f'F{f}_FINAL_LOCKED'/f'S08_F{f}_grandma_match_box_RGBA.png'
 if f in expected:assert sha(src)==expected[f]
 a=np.array(Image.open(src).convert('RGBA'));ls={}
 assert a.shape==(1080,1920,4)
 for role,meta in roles.items():
  path=O/'frames'/meta['filename'];assert sha(path)==meta['sha256']
  ls[role]=np.array(Image.open(path).convert('RGBA'));assert np.array_equal(ls[role][:,:,:3],a[:,:,:3])
 alpha=sum(v[:,:,3].astype(np.uint16) for v in ls.values())
 assert np.array_equal(alpha,a[:,:,3])
 overlap=sum(v[:,:,3]>0 for v in ls.values());assert overlap.max()==1
 # Pillow composition is a source-pixel identity test, not scene rendering.
 im=Image.fromarray(ls['body'])
 for role in ['table_box','arms']:
  if role in ls:im=Image.alpha_composite(im,Image.fromarray(ls[role]))
 assert np.array_equal(np.array(im),a)
 row={'asset':f,'source_sha256':sha(src),'layer_count':len(ls),'overlap_alpha_pixels':int((overlap>1).sum()),'alpha_sum_equal':True,'all_layer_RGB_original_including_transparent':True,'RGBA_reconstruction_exact':True}
 if f in ['005','014','017']:
  roi=a[770:832,1034:1086];head_arrays[f]=roi
  row['match_hand_ROI_xyxy']=[1034,770,1086,832];row['match_hand_ROI_RGBA_sha256']=hashlib.sha256(roi.tobytes()).hexdigest()
  row['match_head_xy']=[1074,782];row['match_head_RGBA']=a[782,1074].tolist();row['grip_xy']=[1046,819];row['grip_RGBA']=a[819,1046].tolist()
 if f=='017':
  b=ls['table_box'][:,:,3]>0;y,x=np.where(b);by,bx=np.where(ls['table_box'][:,:,3]>128)
  assert int(b.sum())==1665
  assert not np.any(ls['body'][:,:,3][b]);assert not np.any(ls['arms'][:,:,3][b])
  row.update(table_box_alpha_pixels=int(b.sum()),table_box_bbox_exclusive=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],table_box_silhouette_alpha_gt128_base=int(by.max()),table_box_alpha_pixels_in_body_or_arms=0)
 rows.append(row)
assert np.array_equal(head_arrays['005'],head_arrays['014']) and np.array_equal(head_arrays['014'],head_arrays['017'])
result={'status':'PASS_ORIGINAL_PIXEL_IDENTITY_ONLY_NOT_CANVAS','rows':rows,'near_hand_match_005_014_017_exact_RGBA_same':True,'image_generation_calls':0,'image_files_modified':0,'actual_canvas_frames':0,'F017_contact_projection':{'measured_base_alpha_gt128':970,'source_box_y_inclusive':[947,970],'sy':-.055,'unblurred_projected_y_inclusive':[970,971.265],'blur_px':.65,'opacity':.22,'dx':0,'dy':0,'table_surface_y':[950.2,981],'actual_visual_contact_status':'PENDING_ACTUAL_CANVAS_NOT_ASSERTED'}}
(O/'PIXEL_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
