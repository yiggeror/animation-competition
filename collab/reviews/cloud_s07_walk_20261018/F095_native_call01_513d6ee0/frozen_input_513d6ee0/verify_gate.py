#!/usr/bin/env python3
"""Read-only provenance/geometry/gate check; replay writes only a temp directory."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess,tempfile,shutil
R=Path(__file__).resolve().parent;repo=R.parents[3];S=R/'sources'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in json.loads((R/'package_manifest.json').read_text())['files']:assert sha(R/row['path'])==row['sha256'],row['path']
count=0
for row in json.loads((S/'snapshot_manifest.json').read_text())['files']:
 assert sha(S/row['snapshot'])==row['sha256']
 if row['origin_path'].startswith('collab/'):
  actual=subprocess.check_output(['git','show',f"d714f5babacaa7a8d450fc4cb93b84e9ac821880:{row['origin_path']}"])
  assert actual==(S/row['snapshot']).read_bytes(),row['snapshot'];count+=1
assert count==10
G=json.loads((R/'geometry/preparation_checks.json').read_text());assert G['new_image_calls']==0 and G['other_states_unopened'];assert not(R/'requests/execution_state.json').exists()
assert G['source_locked090_SHA256']=='012e7bae3f7e39ca93467bf1d43ec003d3ed5a741816c67ee8fc67c5e1225156'
assert G['inclusive_hold']==[95,99] and G['body_affine']['scale']==1
for v in G['whole_arm_proposals'].values():
 m=np.asarray(v['M']);assert np.allclose(m.T@m,np.eye(2),atol=1e-12)and v['scale']==1 and v['same_complete_arm_fingers_jade_unsplit']and v['new095_arm_art_not_frozen']
assert (R/'layers/F095_far_shoe_ankle_SUPPORT_FIXED.png').read_bytes()==(S/'SOURCE_F090_far_shoe_ankle_LANDED.png').read_bytes()
assert G['near_whole_foot_affine']['world_delta']==[59,0] and G['near_whole_foot_affine']['t'][1]==0 and G['near_whole_foot_affine']['no_roll_no_Y_lift_no_individual_foot_edits']
for name in ['near_collected','far_support_FIXED']:assert G['feet'][name]['sole_alpha128_native']==1022
crop=tuple(G['crop_native']);white=np.asarray(Image.open(R/'masks/WHITE_full_neutral_pants_and_sleeve_seams.png').convert('L'))>0
for n in ['HARD_actual_body_except_sleeves','HARD_actual_complete_visible_arms_except_sleeves','HARD_actual_near_landed_visible_whole_foot','HARD_visible_far_support_material_NOT_hidden_alpha']:
 guard=np.asarray(Image.open(R/'masks'/f'{n}.png').convert('L'))>0;assert not np.any(white&guard)
assert not G['far_hidden_foot_alpha_used_as_guard'] and G['far_visible_material_released_for_near_new_shin']==417
assert all(p['white']for p in G['continuous_white_probes'].values())and len({p['component']for p in G['continuous_white_probes'].values()})==1
assert G['active_arms_feet_outside_crop']==G['volume_outside_crop']==G['technical_volume_uncovered_outside_white']==G['A_original_actual_material_RGBA_changes']==0
args=json.loads((R/'requests/arguments_PREPARED_NOT_CALLED.json').read_text());assert args['prompt']==(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text().rstrip('\n')
assert args['transparent_background'] is True and len(args['referenced_image_paths'])==4
assert [Path(p).name for p in args['referenced_image_paths']]==[f'{k}_F095_PREPARED_NOT_CALLED.png'for k in 'ABCD']
for row in G['inputs']:assert sha(R/row['path'])==row['sha256'] and Image.open(R/row['path']).size==(1024,1536)
assert (R/'inputs_1024x1536/D_F095_PREPARED_NOT_CALLED.png').read_bytes()==(S/'D057_062_actual_fabric_TOOL_APPROVED.png').read_bytes()
with tempfile.TemporaryDirectory(prefix='f095-zero-call-verify-')as temp:
 T=Path(temp);shutil.copytree(S,T/'sources');shutil.copyfile(R/'prepare.py',T/'prepare.py')
 subprocess.run(['python',str(T/'prepare.py')],check=True,stdout=subprocess.DEVNULL)
 for group in ['inputs_1024x1536','layers','reference_native','masks']:
  for p in sorted((R/group).glob('*.png')):assert p.read_bytes()==(T/group/p.name).read_bytes(),str(p)
 assert json.loads((T/'geometry/preparation_checks.json').read_text())==G
print('PASS: package hashes;10 source files git-byte-exact;4 inputs/5 layers/all masks isolated replay;whole rigid source transforms;fixed far shoe/whole near translation;real-material guards0;0calls/otherstatesclosed.')
