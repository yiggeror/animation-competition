"""Astra's explicit one-column exception. Original raw is never changed.
No scale/warp/crop/translation: retain all 1671 original columns at (0,0).
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;F=P/'F020';R=F/'same_raw_minimal_registration_001';R.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'S20_F020_attempt001_raw_1671x941.png';B=np.array(Image.open(raw).convert('RGBA'));assert B.shape==(941,1671,4)
raw_sha=sha(raw);pad=np.zeros((941,1672,4),dtype='uint8');pad[:,:1671]=B
assert np.array_equal(pad[:,:1671],B) and not pad[:,1671].any()
Image.fromarray(pad).save(R/'F020_same_raw_right_transparent_column_copy.png')
s8=json.loads((P/'F008/status.json').read_text());assert s8['state']=='AUTHOR_ACCEPTED'
src=P/'F008'/s8['accepted_png'];A=np.array(Image.open(src).convert('RGBA'))
M=np.array(Image.open(F/'inputs/04_edit_white.png'))==255
out=A.copy();out[M]=pad[M]
assert not np.any(out[~M]!=A[~M])
Image.fromarray(out).save(R/'F020_mask_return_candidate.png')
bg=Image.new('RGBA',(1672,941),'#bbc0c4');bg.alpha_composite(Image.fromarray(out));bg=bg.convert('RGB')
bg.save(R/'candidate_full_gray.png')
for name,box in [('receiving_grips',(775,325,890,450)),('whole_arms',(590,320,1000,495)),('shoe_ankle',(515,770,715,930))]:
 bg.crop(box).resize(((box[2]-box[0])*5,(box[3]-box[1])*5),Image.Resampling.NEAREST).save(R/(name+'_5x.png'))
review=json.loads((F/'author_visual_review.json').read_text());(R/'prior_dimension_gate_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
report={'authority':'Astra actual review approves F020 content and allows one right transparent column; retain original columns and origin; no scaling.',
 'raw_sha256_unchanged':sha(raw),'raw_size':[1671,941],'copy_size':[1672,941],
 'original_1671_columns_RGBA_changes':0,'right_added_column_RGBA':[0,0,0,0],'origin_shift':[0,0],
 'scale':[1,1],'warped':False,'source_accepted008_sha256':sha(src),'black_domain_RGBA_changed':0,
 'candidate':str((R/'F020_mask_return_candidate.png').relative_to(F)),
 'actual_hand_occlusion_and_seam_review':'PENDING','new_model_calls':0}
assert sha(raw)==raw_sha=='1445b6f3fbb24e83fe30bebd32608b539be79d9a0fa209de919cb4fe5f8fa8d6'
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
status=json.loads((F/'status.json').read_text());status.update({'state':'AUTHORIZED_SAME_RAW_ONE_COLUMN_COPY_REVIEW_PENDING','candidate':report['candidate'],'accepted_png':None,'black_domain_composite_executed':True,'one_column_exception_authorized_by_Astra':True,'raw_modified':False,'in_flight':0})
(F/'status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(report,indent=2))
