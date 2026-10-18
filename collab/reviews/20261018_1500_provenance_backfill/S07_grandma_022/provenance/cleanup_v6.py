from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_dilation
import numpy as np,json,hashlib
D=Path('astra_s07_f022_prepare_20261018_1357');W,H=1024,1536;a=np.array(Image.open(D/'candidates/F022_local_v4.png').convert('RGBA'));b=np.array(Image.open(D/'candidates/F022_call01_registered_source.png').convert('RGBA'))
m=Image.new('L',(W,H));dr=ImageDraw.Draw(m)
# Same-raw shoulder/neck contour repair. Boundary follows the blue collar below the unchanged bun, not the hair silhouette.
dr.polygon([(367,795),(377,785),(382,783),(390,787),(401,789),(414,790),(428,789),(440,790),(465,793),(465,819),(370,819)],fill=255)
# Remove a narrow old cutout fringe at the front pants edge exposed by the hand release; no knee/foot movement.
dr.polygon([(318,1294),(333,1294),(336,1347),(318,1347)],fill=255)
ma=np.array(m);out=a.copy();out[ma>0]=b[ma>0];im=Image.fromarray(out);im.save(D/'candidates/F022_local_v6.png');m.save(D/'masks/F022_same_raw_neck_front_edge_v6.png');uni=np.maximum(np.array(Image.open(D/'masks/F022_final_source_target_union_v4.png')),ma);Image.fromarray(uni).save(D/'masks/F022_final_union_v6.png');prev=np.array(Image.open(D/'sources/F018_LOCKED_rgba.png'));diff=np.any(out!=prev,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F022_actual_diff_v6.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:
 co=Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB');co.save(D/f'review/F022_local_v6_{n}.jpg',quality=98)
 if n=='gray':co.crop((330,755,475,850)).resize((870,570)).save(D/'review/F022_v6_neck_gray.jpg',quality=98);co.crop((290,1265,440,1370)).resize((750,525)).save(D/'review/F022_v6_pants_edge_gray.jpg',quality=98)
check={'sha256':hashlib.sha256((D/'candidates/F022_local_v6.png').read_bytes()).hexdigest(),'v4_to_v6_changed_pixels':int(np.any(out!=a,axis=2).sum()),'v4_to_v6_outside_cleanup_mask':int(np.any(out!=a,axis=2)[ma==0].sum()),'from_F018_changed_pixels':int(diff.sum()),'outside_final_union_changed':int(diff[uni==0].sum()),'status':'INDEPENDENT_FINAL_REVIEW_PENDING'};(D/'geometry/F022_final_checks_v6.json').write_text(json.dumps(check,indent=2));print(check)
