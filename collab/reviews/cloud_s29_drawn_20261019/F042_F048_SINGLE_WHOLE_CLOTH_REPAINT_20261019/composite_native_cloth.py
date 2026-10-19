from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,sys
R=Path(__file__).resolve().parent;B=R.parent
OLD=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
reports=json.loads((OLD/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']
f=int(sys.argv[1]);d=R/f'F{f:03d}';r=next(v for v in reports if v['frame']==f)
rawp=d/'RAW_UNTOUCHED.png';raw=np.array(Image.open(rawp).convert('RGBA'));H,W=raw.shape[:2];assert (W,H)==(1024,1536)
basep=OLD/f'candidate/F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png';base=np.array(Image.open(basep).convert('RGBA'))
human=np.array(Image.open(d/'HUMANS_PROTECTED_COORDINATES.png').convert('L'))>0
props=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
# Full native cloth is one component in already-current-M canvas coordinates.
# Do not refit/warp/resize it, or move the already-approved arms.
lab,n=nd.label(raw[:,:,3]>=128);counts=np.bincount(lab.ravel());counts[0]=0
native=nd.binary_fill_holes(lab==counts.argmax())
extent=nd.binary_dilation(native,iterations=2)
cloth=np.zeros_like(raw);cloth[extent]=raw[extent]
cloth[native,3]=255 # Opaque cotton surface; keep original edge AA outside the solid face.
oldface=Image.new('L',(W,H));ImageDraw.Draw(oldface).polygon([(250,881),(327,794),(375,747),(485,745),(506,668),(603,666),(691,634),(752,626),(844,678),(932,741),(1015,818),(1020,992),(975,1051),(947,1076),(925,1058),(864,1025),(838,1035),(812,1077),(763,1040),(693,1026),(622,1017),(542,1000),(472,978),(407,956),(332,931),(266,908)],fill=255)
oldface=np.array(oldface)>0
# Preserve existing body/silhouette outside the freshly drawn sheet. Clearing an
# approximate old cloth polygon there would delete the original underlay and
# create an artificial gray seam. The only obsolete exposed upper protrusion is
# retired against the actual new, single native top contour (never a rectangle).
top=np.full(W,H,dtype=int)
for cx in range(W):
 ys=np.flatnonzero(native[:,cx])
 if len(ys):top[cx]=ys[0]
yy,xx=np.indices((H,W))
retire=oldface&(yy<top[xx])&(top[xx]<H)&(xx>=500) # C1 is x499; retain the original torso/near-arm underlay on its left.
v=base.copy();v[retire&~human&~props]=0
v=np.array(Image.alpha_composite(Image.fromarray(v),Image.fromarray(cloth)))
# Existing actual layering is authoritative; preserve the exact accepted pixels.
v[human|props]=base[human|props]
out=d/'REINTEGRATED_RGBA.png';Image.fromarray(v).save(out)
bg=Image.new('RGBA',(W,H),(236,239,242,255));bg.alpha_composite(Image.fromarray(v));bg.convert('RGB').save(d/'REINTEGRATED_FULL_ON_GRAY.png')
bg.crop((470,625,1018,1088)).convert('RGB').save(d/'REINTEGRATED_CONTACT_NORMAL_SIZE.png')
Image.fromarray(cloth).save(d/'EXTRACTED_ONE_NATIVE_CLOTH.png')
changed=np.any(v!=base,2)
interior=nd.binary_erosion(native,iterations=2)
y,x=np.where(native)
report={'frame':f,'new_generation_requests':1,'retries':0,'source_base_commit':'8c41ca4517978ca3a4e6a44260ed1d3426f12edd','raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'cloth_output_canvas':[W,H],'existing_M_unchanged':r['single_similarity_complete_arm_hand_and_cloth'],'cloth_reintegration_transform':'identity in the already-current-M final canvas; no fit, resize or warp','native_cloth_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'native_cloth_opaque_component_pixels':int(native.sum()),'native_cloth_interior_pixels_alpha_under250':int(((cloth[:,:,3]<250)&interior).sum()),'actual_human_protection_RGBA_changes':int(changed[human].sum()),'true_original_props_protection_RGBA_changes':int(changed[props].sum()),'layer_order':'existing body/silhouette outside new sheet retained; obsolete upper cloth protrusion retired along new native top edge; opaque one-piece new cloth; then exact existing human/true-prop pixels','status':'PENDING_ACTUAL_NORMAL_SIZE_REVIEW'}
(d/'REINTEGRATION_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
