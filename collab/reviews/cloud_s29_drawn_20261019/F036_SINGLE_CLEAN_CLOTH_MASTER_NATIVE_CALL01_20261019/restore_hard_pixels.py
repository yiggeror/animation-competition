from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;S=R.parent/'F036_SINGLE_CLEAN_CLOTH_MASTER_INPUT_GATE_ZERO_CALL_20261019'
raw=np.array(Image.open(R/'RAW_UNTOUCHED.png').convert('RGBA'))
white=np.array(Image.open(S/'02_ONLY_SOURCE_GAPS_WHITE_PROTECTED_BLACK.png').convert('L'))>0
hard=np.array(Image.open(S/'HARD_PROTECTED_ORIGINAL_CLOTH_MASK.png').convert('L'))>0
face=np.array(Image.open(S/'WHOLE_LOCKED036_CLOTH_DOMAIN.png').convert('L'))>0
source=np.array(Image.open(S/'HARD_PROTECTED_ORIGINAL_CLOTH_RGBA.png').convert('RGBA'))
result=np.zeros_like(raw);result[white]=raw[white];result[hard]=source[hard]
out=R/'HARD_RESTORE_TRIAL_HOLD_RGBA.png';Image.fromarray(result).save(out)
for name,a in [('RAW_ON_GRAY.png',raw),('HARD_RESTORE_TRIAL_HOLD_ON_GRAY.png',result)]:
 g=Image.new('RGBA',(1024,1536),(236,239,242,255));g.alpha_composite(Image.fromarray(a));g.convert('RGB').save(R/name)
sheet=Image.new('RGB',(1568,505),(236,239,242));d=ImageDraw.Draw(sheet)
for i,name in enumerate(['RAW_ON_GRAY.png','HARD_RESTORE_TRIAL_HOLD_ON_GRAY.png']):
 sheet.paste(Image.open(R/name).crop((240,625,1024,1100)),(i*784,30));d.text((i*784+8,8),['ONE RAW | 1:1','HOLD: HARD105492 RESTORED | 1:1'][i],fill='black')
sheet.save(R/'RAW_AND_HARD_RESTORE_HOLD_1TO1.png')
interior=nd.binary_erosion(face,iterations=3);low=white&interior&(result[:,:,3]<250);y,x=np.where(low)
report={'requests':1,'retries':0,'raw_SHA256':hashlib.sha256((R/'RAW_UNTOUCHED.png').read_bytes()).hexdigest(),'hard_restore_trial_SHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'hard_protected_pixels':int(hard.sum()),'hard_RGBA_changes':int(np.any(result[hard]!=source[hard],1).sum()),'new_material_pixels_allowed':int(white.sum()),'all_white_RGBA_equal_the_one_raw':bool(np.array_equal(result[white],raw[white])),'interior_low_alpha_under250':int(low.sum()),'low_alpha_bbox_inclusive':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())],'low_alpha_note':'79 low-alpha points are not declared true material gaps from count alone; the blocking actual-image finding is material/fold discontinuity after exact hard restoration.','status':'HOLD_AFTER_ONE_RAW_AND_EXACT_HARD_RESTORE_NO_MAPPING','normal_size_actual_review_by_root_and_existing_cloud_helper':True,'raw_actual_finding':'Continuous cotton and approximately036 small dense flower family; no visible person/puppet/rod or broad transparency slot.','blocking_hard_restore_findings':[{'native_bbox_inclusive':[425,790,615,895],'finding':'visible L-shaped/right-angle material and fold discontinuity; right vertical border about x615'},{'native_bbox_inclusive':[545,735,754,750],'finding':'old/new upper horizontal material/fold and flower-phase boundary'},{'area':'right diagonal strips','finding':'protected old cloth and new raw folds/pattern do not join as one continuous surface'}],'new_mapping_candidates':0,'new_scene_renders':0}
(R/'MASTER_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
