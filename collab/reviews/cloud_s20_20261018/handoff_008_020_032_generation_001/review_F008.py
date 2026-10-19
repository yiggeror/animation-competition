"""Retain the one real raw; show why its unchanged gesture fails the approved target.
Binary mask composite is QA ONLY, never an accepted drawing or arm reconstruction.
"""
from pathlib import Path
import json,hashlib,shutil,datetime,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F008';Q=F/'qa';Q.mkdir(exist_ok=True)
ORIGINAL=Path('/workspace/generated_images/exec-1ab6085f-6473-47ff-8705-d1c0d1f5b770.png')
RAW=F/'S20_F008_attempt001_raw.png';shutil.copyfile(ORIGINAL,RAW)
MASTER=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
GATE=PACK/'handoff_008_020_032_reference_001/F008'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=Image.open(MASTER).convert('RGBA');raw=Image.open(RAW).convert('RGBA')
assert sha(MASTER)=='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
assert sha(ORIGINAL)==sha(RAW)
dim=list(struct.unpack('>II',RAW.read_bytes()[16:24]));assert dim==[1672,941],dim
a=np.array(master);b=np.array(raw);mask=np.array(Image.open(GATE/'04_edit_white.png'))==255
qa=a.copy();qa[mask]=b[mask]
assert not np.any(qa[~mask]!=a[~mask])
Image.fromarray(qa).save(Q/'S20_F008_rejected_mask_QA.png')

def matte(im):
 bg=Image.new('RGBA',im.size,'#bfc3c6');bg.alpha_composite(im.convert('RGBA'));return bg.convert('RGB')

matte(raw).save(Q/'raw_full_gray.png')
crop=(530,275,910,550)
fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(fontpath),25);small=ImageFont.truetype(str(fontpath),20)
board=Image.new('RGB',(2280,690),'#f3f4f5');d=ImageDraw.Draw(board)
for i,(title,img) in enumerate([
 ('母态55ce：原两掌低位',master),
 ('已批008目标：R上侧空掌／L下侧空掌',Image.open(GATE/'02_full_volume_target.png').convert('RGBA')),
 ('008唯一实物：仍旧低位手势，拒用',raw),
]):
 x=i*760;d.text((x+12,12),title,font=small,fill='#263743')
 board.paste(matte(img).crop(crop).resize((760,550),Image.Resampling.NEAREST),(x,55))
d.text((15,625),'008姿态未执行，不能把“仍空手”当作动作已完成；未提交020或032，也没有第二次008调用。',font=font,fill='#943d36')
board.save(Q/'mother_target_actual_comparison.png')

# Inspect expected target palm area: it should contain an open right hand.
target=(780,285,850,340)
matte(raw).crop(target).resize((560,440),Image.Resampling.NEAREST).save(Q/'raw_expected_R_palm_region_8x.png')
review={
 'result':'AUTHOR_REJECTED / APPROVED_F008_POSE_NOT_APPLIED',
 'actual_raw':RAW.name,'actual_raw_sha256':sha(RAW),'actual_dimensions':dim,
 'original_tool_path':str(ORIGINAL),'original_kept_unmodified':True,
 'source_master_sha256':sha(MASTER),'frozen_gate':'c1b1833b7dfe806ae2daa1b84ddacfb804070f3d',
 'actual_image_visual_findings':[
  'Actual child palms remain near mother-state low positions around y460-520.',
  'Approved F008 X.R target is [806,318], approaching T_H from above; no raised open palm is present there.',
  'The actual child shoulder/elbow/wrist gesture follows the source mother rather than the approved full-volume target.',
  'No drawn technical circles were copied, but this does not make the unchanged gesture a valid F008.',
 ],
 'acceptance_checks':{'canvas_size':'PASS 1672x941','approved_arm_pose':'FAIL',
  'hand_to_rod_preparation':'FAIL required approach missing','source_black_domain_in_QA_composite':'PASS zero RGBA changes',
  'retained_as_drawing':False,'author_acceptance':False},
 'QA_composite_only':'qa/S20_F008_rejected_mask_QA.png / not accepted or used as next-state reference',
 'tool_call_count_this_batch':1,'raw_count_this_batch':1,'cumulative_historical_plus_current_requests':4,
 'cumulative_historical_plus_current_raws':4,'retry_this_state':False,
 'F020_submitted':False,'F032_submitted':False,
 'next_states_blocked_by':'User requires predecessor actual self-review pass; one authorized F008 attempt was rejected.',
 'cause_scope':'Observed outcome only; no unsupported claim about the model internals or why it followed the mother.',
 'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
(F/'author_visual_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
status=json.loads((F/'status.json').read_text());status.update({'state':'AUTHOR_REJECTED_POSE_NOT_APPLIED',
 'in_flight':0,'new_raws':1,'actual_size':dim,'raw_sha256':sha(RAW),'raw_path':RAW.name,
 'original_tool_path':str(ORIGINAL),'retained_as_drawing':False,'accepted_png':None,'next_states_submitted':0,
 'next_states_blocked':True,'automatic_retry':False})
(F/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frame':8,'raw_sha256':sha(RAW),'actual_size':dim,'review':'REJECTED_POSE_NOT_APPLIED',
 'new_calls':1,'new_raws':1,'F020_submitted':False,'F032_submitted':False},indent=2))
