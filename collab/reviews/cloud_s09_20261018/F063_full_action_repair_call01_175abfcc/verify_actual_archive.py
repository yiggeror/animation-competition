#!/usr/bin/env python3
"""Read-only single-call/source/raw provenance and literal inverse check."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,base64,subprocess
R=Path(__file__).resolve().parent;F=R/'frozen_input_175abfcc';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in json.loads((R/'package_manifest.json').read_text())['files']:assert sha(R/row['path'])==row['sha256'],row['path']
commit='175abfcc8f22fcbcd8689279a97ab88d436c7c33';prefix='collab/reviews/cloud_s09_20261018/F063_full_grip_shape_repair_gate_20261019/';paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',prefix],text=True).splitlines();assert len(paths)==78
for p in paths:assert subprocess.check_output(['git','show',f'{commit}:{p}'])==(F/Path(p).relative_to(prefix)).read_bytes()
req=R/'requests/arguments_call01_FINAL_EXACT.json';pp=R/'requests/prompt_call01_FINAL_EXACT.txt';args=json.loads(req.read_text());authority=json.loads((R/'requests/astra_authority_final_SHAs_zero_inflight.json').read_text());state=json.loads((R/'requests/execution_state.json').read_text())
assert state['request_count']==state['original_count']==1 and state['active_request_count']==0
assert sha(req)==authority['final_request_file_SHA256']=='1bf32a103707026023b0a0515509ce2a2751f678ede5db7ce3569bd723f140b4';assert sha(pp)==authority['final_prompt_file_SHA256']=='ac700bb6a3b0d46ce8564e7c14804078e8670a2b97e15038581d14339ed751b0';assert args['prompt']==pp.read_text().rstrip('\n')
suffix='The far upper arm must originate from its own far sleeve; its occluded portion stays behind the near forearm and must never branch out of the near forearm.'
old=(F/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text().rstrip('\n');assert args['prompt']==old+'\n'+suffix
for k,p in zip('ABCDE',args['referenced_image_paths']):assert sha(p)==sha(F/f'reference/{k}_F063_PREPARED_NOT_CALLED_1280x1536.png')
rawpath=R/'originals/F063_full_action_call01_RAW.png';raw=rawpath.read_bytes();j=json.loads((R/'requests/call01_raw_tool_return.json').read_text());assert base64.b64decode(j['image_url'].split(',',1)[1])==raw
host=Path(state['raw_host_path']);assert not host.exists()or host.read_bytes()==raw;assert sha(rawpath)=='be78fe901b39d838c867326b517ed26ee72ed6488c683f94e06b0487a6df020f'
im=Image.open(rawpath).convert('RGBA');assert im.size==(1145,1374)
s=77/128;literal=im.transform((1672,941),Image.Transform.AFFINE,(1/s,0,-550/s,0,1/s,0),Image.Resampling.BICUBIC,fillcolor=0);assert np.array_equal(np.asarray(literal),np.asarray(Image.open(R/'diagnostic/F063_LITERAL_77over128_plus550_0_HOLD_NOT_ADOPTED.png')))
g=json.loads((R/'geometry/fixed_inverse_actual_shape_and_gap_HOLD.json').read_text());assert not g['production_candidate_created']and not g['old_head_ruffle_skirt_guard_restoration_performed']and g['F069_unopened'];assert g['literal_approved_inverse']['s']==s and g['literal_approved_inverse']['no_resolution_normalization_adopted']and g['literal_approved_inverse']['no_partfit']
assert g['scale_independent_tail_to_axis_ratio_delta_vs_original044']<-.20 and g['actual_whole_prop_to_far_palm_outline_gaps']['128']['literal_inverse_native_gap']<10
print('PASS:78 frozen git-byte-exact;five unchanged inputs/exact appended final sentence;final SHAs;one request/one raw;three-way raw bytes;literal77/128 only;HOLD/no candidate/no069.')
