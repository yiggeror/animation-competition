from pathlib import Path
import json,hashlib,shutil,base64,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,distance_transform_edt
P=Path(__file__).resolve().parent;F=P/'F032';Q=F/'qa';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=Path('/workspace/generated_images/exec-555bf2bd-a16e-4097-b3ac-4972a3b36acc.png')
raw=F/'S20_F032_attempt001_raw.png';shutil.copyfile(original,raw)
dim=list(struct.unpack('>II',raw.read_bytes()[16:24]));assert dim==[1672,941],dim
assert base64.b64decode(json.loads((F/'tool_return_original.json').read_text())['image_url'].split(',',1)[1])==raw.read_bytes()
s20=json.loads((P/'F020/status.json').read_text());assert s20['state']=='AUTHOR_ACCEPTED'
source=P/'F020'/s20['accepted_png'];A=np.array(Image.open(source).convert('RGBA'));B=np.array(Image.open(raw).convert('RGBA'))
M=np.array(Image.open(F/'inputs/04_release_only_edit_white.png'))==255
out=A.copy();out[M]=B[M]
assert not np.any(out[~M]!=A[~M]) and np.array_equal(out[:,:885],A[:,:885])
candidate=F/'S20_F032_candidate.png';Image.fromarray(out).save(candidate)
bg=Image.new('RGBA',(1672,941),'#bdc2c5');bg.alpha_composite(Image.fromarray(out));bg=bg.convert('RGB');bg.save(Q/'candidate_full_gray.png')
for name,box,sc in [('release_and_both_grips',(775,325,1100,540),4),('adult_R_open_fingers',(912,435,1025,530),8),('old_palm_tail_region',(885,405,980,477),6),('wrist_shirt_join',(990,435,1055,515),6)]:
 bg.crop(box).resize(((box[2]-box[0])*sc,(box[3]-box[1])*sc),Image.Resampling.NEAREST).save(Q/(name+'_actual.png'))
# Receiving grip/whole child exact; the new supply hand is tested against real
# final bamboo pixels in the original shaft corridors, not against a guide circle.
skin=(out[:,:,3]>180)&(out[:,:,0]>190)&(out[:,:,1]>130)&(out[:,:,2]>100)
roi=np.zeros(M.shape,bool);roi[440:530,910:1023]=skin[440:530,910:1023]
cc,n=label(roi);k=cc[487,978];assert k>0,'No open palm at expected release position.'
hand=cc==k
reg=json.loads((P.parent/'F000/f000_scene_gate_001/registration_input.json').read_text())['rods']
rods=np.zeros(M.shape,bool)
yy,xx=np.indices(M.shape)
for role in ['T_H','T_S']:
 r=reg[role];corr=(np.abs(yy-(r['slope']*xx+r['intercept']))<4)&(xx>=775)&(xx<=950)
 brown=(out[:,:,0]>out[:,:,1]+15)&(out[:,:,1]>out[:,:,2]+12)&(out[:,:,2]<155)&(out[:,:,3]>150)
 rods|=corr&brown
D=distance_transform_edt(~rods);clearance=float(D[hand].min());assert clearance>5,clearance
s=json.loads((F/'status.json').read_text());s.update({'state':'RAW_RETURNED_COMPOSITE_VISUAL_REVIEW_PENDING','in_flight':0,'new_raws':1,'raw_path':raw.name,'raw_sha256':sha(raw),'actual_size':dim,'original_tool_path':str(original),'candidate':candidate.name})
(F/'status.json').write_text(json.dumps(s,indent=2)+'\n')
report={'raw_sha256':sha(raw),'candidate_sha256':sha(candidate),'actual_size':dim,'black_domain_RGBA_changed':0,'actual020_whole_child_and_receiver_grips_RGBA_changed':0,'high_jade_L_and_crane_rods_black_protected':True,'actual_open_palm_skin_to_bamboo_clearance_px':clearance,'new_model_calls_this_state':1,'new_model_calls_round_total':3,'cumulative_requests':7,'cumulative_raws':7,'visual_review':'PENDING_ACTUAL_CROPS'}
(F/'receipt_and_protection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
