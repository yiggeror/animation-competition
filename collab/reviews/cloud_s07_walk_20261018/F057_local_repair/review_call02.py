#!/usr/bin/env python3
"""Preserve raw, restore locked domains, and measure the actual failed local repair."""
from pathlib import Path
import base64,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s07-call02-review')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
raw_path=ROOT/'originals/F057_call02_raw.png';raw=Image.open(raw_path).convert('RGBA')
ret=json.loads((ROOT/'requests/F057_call02_raw_return.json').read_text())
assert raw_path.read_bytes()==base64.b64decode(ret['image_url'].split(',',1)[1])
args=json.loads((ROOT/'requests/F057_call02_arguments.json').read_text())
assert args['prompt']==(ROOT/'requests/F057_call02_prompt.txt').read_text().rstrip('\n')
for row in json.loads((ROOT/'requests/F057_call02_inputs.json').read_text()):
 assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
prep=json.loads((ROOT/'reference/preparation.json').read_text());reg=prep['actual_source_checked_registration']
source=Image.open(ROOT/'reference/raw_source_bottom_padding_only.png').convert('RGBA')
mask=Image.open(ROOT/'masks/full_leg_chains_and_far_left_arm.png').convert('L')
protected=np.array(Image.open(ROOT/'masks/locked_head_body_near_right_arm.png'))>0
assert source.size==(1672,1080) and raw.size==(1560,1008)
# One global uniform size conversion, no separate head, arm or leg fitting.
q=raw.width/source.width
aligned=raw.transform(source.size,Image.Transform.AFFINE,(q,0,0,0,q,0),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
aligned.save(ROOT/'qa/call02_global_uniform_alignment_only.png')
candidate=Image.composite(aligned,source,mask)
a=np.array(source);c=np.array(candidate);m=np.array(mask)
assert np.array_equal(c[m==0],a[m==0])
assert np.array_equal(c[protected],a[protected])
candidate.save(ROOT/'candidates/F057_call02_locked_domains_NOT_PASSED.png')
inverse=(1/reg['s'],0,-reg['tx']/reg['s'],0,1/reg['s'],-reg['ty']/reg['s'])
world=candidate.transform((1672,941),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
world.save(ROOT/'candidates/F057_call02_world_NOT_PASSED.png')
bg=Image.new('RGBA',world.size,(226,231,235,255));bg.alpha_composite(world);bg.convert('RGB').save(ROOT/'qa/call02_world_actual_on_light.png')
manual={'near_ankle':[848,884],'far_ankle':[614,875],'far_jade_wrist':[911,474],
        'near_sole_y':944,'far_sole_y':938,'uncertainty':'ankle centers±10raw, wrist±5raw, sole±3raw; visible estimates, not3D bone reconstruction'}
to_world=lambda p:[reg['tx']+p[0]*reg['s']/q,reg['ty']+p[1]*reg['s']/q]
landmarks={k:to_world(manual[k]) for k in ['near_ankle','far_ankle','far_jade_wrist']}
span=(manual['near_ankle'][0]-manual['far_ankle'][0])*reg['s']/q
soles={k:reg['ty']+manual[k]*reg['s']/q for k in ['near_sole_y','far_sole_y']}
review={'status':'CALL02_LOCAL_REPAIR_NOT_PASSED_NO_FURTHER_CALLS',
 'this_round_native_calls':1,'S07_own_native_calls_total':2,'accepted_F057_drawings':0,'other10_native_calls':0,
 'raw_png_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'raw_return_byte_equal':True,
 'raw_output_size':list(raw.size),'requested_working_size':list(source.size),
 'source_raw_first_call':'../F057_first_image/originals/F057_call01_raw.png',
 'G037_fixed_source':'9ee7689d8ff56ab6c366a7f6d087197f0c8d6377',
 'G037_actual_head_world':reg['head_target'],'G037_never_mirrored':True,
 'uniform_raw_to_working_scale':1/q,'uniform_raw_to_working_translation':[0,0],
 'whole_figure_registration_to_world':reg,
 'outside_edit_mask_pixel_changes':0,'protected_head_body_near_right_arm_pixel_changes':0,
 'no_segment_scaling_or_warp':True,'manual_native_return':manual,'actual_world_landmarks':landmarks,
 'actual_horizontal_ankle_span_world_approx':span,'ankle_span_target_world':64,'ankle_span_uncertainty_world_approx':6,
 'actual_world_soles_approx':soles,'target_world_floor':775,'far_wrist_target_world':[942,623],
 'actual_image_findings':[
  'Real returned frame reconnected pants/legs and retains readable right-facing identity and right-bare/left-jade ownership.',
  'Step only partly narrowed; measured horizontal ankle span still~91world versus64. Near right foot remains too far forward.',
  'Far left wrist remains too far forward/high, about983,588 versus intended~942,623.',
  'Both soles remain roughly769–771world versus775; manual estimates have uncertainty but no ground-pass claim.',
  'Output changed canvas dimensions. Only one uniform whole-return alignment was applied before hard restoring source head, blouse and near arm.',
  'No full-pose acceptance, no extension to other10, no new request in flight.'],
 'next_gate':'Astra inspect actual source-scale and call02 return before any additional targeted repair. Do not repeat full person/numeric redraw or derive later poses from this failed output.'}
(ROOT/'qa/call02_actual_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
fig,axs=plt.subplots(1,2,figsize=(13,9))
axs[0].imshow(candidate);axs[0].set_xlim(560,1140);axs[0].set_ylim(1060,0);axs[0].set_facecolor('#e1e6ea');axs[0].set_title('原头身／近右臂锁回；局修实际图')
axs[1].imshow(world);axs[1].set_xlim(820,1025);axs[1].set_ylim(800,390);axs[1].set_facecolor('#e1e6ea');axs[1].set_title('实量对施工目标：未通过')
for k,p in landmarks.items():
 axs[1].scatter(*p,c='#b63c55',s=35);axs[1].annotate(k,p,fontsize=8)
for p in [[929,758],[865,758],[942,623]]:axs[1].scatter(*p,facecolors='none',edgecolors='#087f91',s=100,lw=2)
axs[1].axhline(775,c='#75808a');axs[1].text(825,790,f'踝距约{span:.1f}／目标64',color='#a23d52',fontsize=12)
fig.suptitle('F057仅本次局修1调用／总2；红点=返回实量，青圈=目标；其余10态0',fontsize=15)
fig.tight_layout();fig.savefig(ROOT/'qa/call02_actual_vs_targets.png',dpi=140);plt.close(fig)
print(json.dumps({'raw_byte_equal':True,'protected_changes':0,'outside_edit_changes':0,'actual_ankle_span':span,'target_span':64,'far_wrist_actual_world':landmarks['far_jade_wrist'],'soles':soles,'status':review['status']},ensure_ascii=False))
