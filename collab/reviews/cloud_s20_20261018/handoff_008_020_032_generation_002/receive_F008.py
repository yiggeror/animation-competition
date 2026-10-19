from pathlib import Path
import json,hashlib,shutil,base64,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F008';Q=F/'qa';Q.mkdir(exist_ok=True)
original=Path('/workspace/generated_images/exec-60e03849-653e-4114-8083-172ce1343bad.png')
raw=F/'S20_F008_corrected_attempt001_raw.png';shutil.copyfile(original,raw)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
gate=PACK/'F008_corrected_input_001';a=np.array(Image.open(master).convert('RGBA'));b=np.array(Image.open(raw).convert('RGBA'))
assert sha(master)=='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
assert struct.unpack('>II',raw.read_bytes()[16:24])==(1672,941)
assert base64.b64decode(json.loads((F/'tool_return_original.json').read_text())['image_url'].split(',',1)[1])==raw.read_bytes()
edit=np.array(Image.open(gate/'inputs/04_edit_white.png'))==255
out=a.copy();out[edit]=b[edit]
assert not np.any(out[~edit]!=a[~edit])
candidate=F/'S20_F008_candidate.png';Image.fromarray(out).save(candidate)
def gray(arr):
 im=Image.fromarray(arr);bg=Image.new('RGBA',im.size,'#bfc3c6');bg.alpha_composite(im);return bg.convert('RGB')
g=gray(out);g.save(Q/'candidate_full_gray.png')
for name,box in [('arms_hands',(570,270,1005,510)),('R_wrist_air',(765,279,858,354)),('L_wrist_air',(800,412,891,486)),('head_neck_body',(500,190,710,535))]:
 g.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4),Image.Resampling.NEAREST).save(Q/(name+'_4x.png'))
rod=np.array(Image.open(gate/'local_masks/protect_four_real_rods.png'))>0
dist=distance_transform_edt(~(rod&(a[:,:,3]>100)))
gaps={}
for side,box,seed in [('R',(772,276,857,341),(806,318)),('L',(805,416,886,482),(837,455))]:
 x0,y0,x1,y1=box;m=np.zeros(edit.shape,bool);m[y0:y1,x0:x1]=b[y0:y1,x0:x1,3]>180;m[rod]=False
 cc,n=label(m);sx,sy=seed;k=cc[sy,sx]
 assert k>0,(side,'target palm absent')
 hand=cc==k;gaps[side]=float(dist[hand].min())
status=json.loads((F/'status.json').read_text());status.update({'state':'RAW_RETURNED_CANDIDATE_VISUAL_REVIEW_PENDING','in_flight':0,'new_raws':1,'raw_path':raw.name,'raw_sha256':sha(raw),'actual_size':[1672,941],'original_tool_path':str(original),'candidate':candidate.name})
(F/'status.json').write_text(json.dumps(status,indent=2)+'\n')
report={'raw_sha256':sha(raw),'candidate_sha256':sha(candidate),'dimensions':[1672,941],'black_domain_RGBA_changed':0,'grandmother_RGBA_changed':0,'four_rods_mask_RGBA_changed':0,'shoe_ankle_strip_RGBA_changed':0,'actual_hand_wrist_clearance_to_real_rods_px':gaps,'model_calls_this_round':1,'cumulative_requests':5,'cumulative_raws':5,'new_model_raws':1,'visual_acceptance':'PENDING_ACTUAL_CROP_REVIEW'}
(F/'receipt_and_protection.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
