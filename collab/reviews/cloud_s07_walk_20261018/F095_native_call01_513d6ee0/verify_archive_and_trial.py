#!/usr/bin/env python3
"""Read-only raw/frozen provenance and whole-source candidate reconstruction."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,base64,subprocess
R=Path(__file__).resolve().parent;F=R/'frozen_input_513d6ee0';A=R/'registration_audit_61sol';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((R/'package_manifest.json').read_text())
for row in manifest['files']:assert sha(R/row['path'])==row['sha256'],row['path']
commit='513d6ee09b583411096af66dc29075888da36f6c';prefix='collab/reviews/cloud_s07_walk_20261018/F095_next_gate_20261019/'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',prefix],text=True).splitlines();assert len(paths)==52
for p in paths:assert subprocess.check_output(['git','show',f'{commit}:{p}'])==(F/Path(p).relative_to(prefix)).read_bytes(),p
state=json.loads((R/'requests/execution_state.json').read_text());assert state['request_count']==state['original_count']==1 and state['active_request_count']==0
rawfile=R/'originals/F095_call01_RAW.png';host=Path(state['raw_host_path']);rawreturn=json.loads((R/'requests/call01_raw_tool_return.json').read_text());rawbytes=rawfile.read_bytes();assert base64.b64decode(rawreturn['image_url'].split(',',1)[1])==rawbytes
if host.exists():assert host.read_bytes()==rawbytes
assert sha(rawfile)=='0fb9780d5151adb6a7f14d0e226d55f5e14e12fe270a5d9f90389269f79ead3d'
raw=np.array(Image.open(rawfile).convert('RGBA'));mask=np.array(Image.open(A/'masks/RAW_one_complete_navy_pants_source_material.png').convert('L'))>0
pantsraw=np.array(Image.open(A/'candidate/RAW_original_color_whole_trousers_EXTRACTED_TRIAL.png').convert('RGBA'));assert np.array_equal(pantsraw[mask],raw[mask])and np.all(pantsraw[~mask]==0)
pants=Image.new('RGBA',(1672,1080));pants.alpha_composite(Image.fromarray(pantsraw).resize((540,810),Image.Resampling.LANCZOS),(1120,250));assert np.array_equal(np.array(pants),np.array(Image.open(A/'candidate/F095_whole_native_pants_COMMON_INVERSE_ORIGINAL_COLOR_TRIAL.png')))
trial=Image.new('RGBA',(1672,1080));keys=['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_COLLECTED_LANDED']
for key in keys:
 if key=='far_complete_arm_jade_hand':trial.alpha_composite(pants)
 trial.alpha_composite(Image.open(F/'layers'/f'F095_{key}.png').convert('RGBA'))
assert np.array_equal(np.array(trial),np.array(Image.open(A/'candidate/F095_same_inverse_original_pants_and_source_layers_TRIAL_NOT_APPROVED.png')))
assert sha(A/'candidate/F095_same_inverse_original_pants_and_source_layers_TRIAL_NOT_APPROVED.png')=='dcf919f412fd379a34ea69329210a418547dcccc089e1b36aa208024a04fdca4'
g=json.loads((A/'geometry/actual_common_registration_and_material.json').read_text());assert g['whole_inverse']=={'s':135/256,'offset':[1120,250],'no_independent_fit':True}
assert g['actual_visible_sole_material']['all_visible_union_bbox_local_halfopen']==g['expected_visible_sole_material']['all_visible_union_bbox_local_halfopen'];assert g['actual_boundary_to_expected_px']['max']==g['expected_boundary_to_actual_px']['max']==1
assert g['raw_pants_kept_RGBA_changes']==0 and not g['F100_opened']
print('PASS:52 frozen git-byte-exact;one request/one raw;host/archive/base64 equal;actual original pants RGBA;one135/256+[1120,250] transform;full5source-layer replay equalsdcf919f4;no per-partfit/no100.')
