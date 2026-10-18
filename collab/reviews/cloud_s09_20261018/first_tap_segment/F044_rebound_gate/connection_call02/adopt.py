#!/usr/bin/env python3
"""Adopt actual local native repair; restore genuine source material once."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;T=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
trial=P/'candidate/F044_complete_native_arm_rigid_fit_TRIAL.png'
raw=R/'originals/F044_call02_raw.png'
a=np.array(Image.open(trial).convert('RGBA'));h,w=a.shape[:2]
im=Image.open(raw).convert('RGBA');assert im.size==(1536,1024)
aligned=im.resize((540,360),Image.Resampling.LANCZOS)
aligned.save(R/'qa/native_whole_crop_uniform_alignment.png')
n=np.zeros_like(a);n[500:860,620:1160]=np.array(aligned)
edit=np.array(Image.open(R/'masks/F044_explicit_connection_domain.png'))>0
out=a.copy();out[edit]=n[edit]
# The trial duplicated the translucent foreground AA. Restore each authentic
# source RGBA once, using its actual material mask, never a rectangular guard.
palm=np.array(Image.open(T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png').convert('RGBA'))
mother=np.array(Image.open(T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png').convert('RGBA'))
pm=np.array(Image.open(P/'masks/fixed_receiver_palm_material.png'))>0
rr=np.array(Image.open(P/'masks/near_ruffle_actual_material.png'))>0
out[pm]=palm[pm];out[rr]=mother[rr]
candidate=P/'candidate/F044_native_connections_PENDING_ACTUAL_REVIEW.png'
Image.fromarray(out).save(candidate)
for name,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 b=Image.new('RGBA',(w,h),color);b.alpha_composite(Image.fromarray(out))
 b.convert('RGB').save(P/f'qa/F044_connected_full_{name}.png')
 b.crop((620,420,1240,860)).convert('RGB').save(P/f'qa/F044_connected_crop_{name}.png')
unit=np.array(Image.open(P/'reference/F044_rigid_hand_torch_up48_SOURCE.png').convert('RGBA'))
release=np.array(Image.open(R/'masks/proximal_wrist_extraction_edge_release.png'))>0
unitcore=(unit[:,:,3]==255)&~release
changed=np.any(out!=a,axis=2)
report={'status':'ACTUAL_LOCAL_REPAIR_ADOPTED_VISUAL_REVIEW_PENDING','candidate_sha256':sha(candidate),'source_trial_sha256':sha(trial),'native_raw_sha256':sha(raw),'raw_size':list(im.size),'whole_crop_uniform_scale':540/1536,'crop_xyxy':[620,500,1160,860],'no_limb_warp':True,'explicit_native_domain_pixels':int(edit.sum()),'local_native_changed_pixels':int((edit&changed).sum()),'source_AA_restored_once':True,'fixed_palm_RGBA_changes_vs_true037':int(np.any(out[pm]!=palm[pm],axis=1).sum()),'near_ruffle_RGBA_changes_vs_mother':int(np.any(out[rr]!=mother[rr],axis=1).sum()),'genuine_rigid_unit_opaque_core_changes_except90_wrist_cut':int(np.any(out[unitcore]!=unit[unitcore],axis=1).sum()),'outside_native_and_source_AA_domain_changes':int((changed&~(edit|pm|rr)).sum()),'F044_requests':2,'F044_originals':2,'S09_requests':19,'S09_originals':18,'F048_unopened':True}
(P/'qa/native_connections_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
