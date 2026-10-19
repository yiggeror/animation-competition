#!/usr/bin/env python3
"""Read-only input archive and real-contour verification, isolated replay in tmp."""
from pathlib import Path
from PIL import Image
from scipy.ndimage import distance_transform_edt
import json,numpy as np,hashlib,subprocess,tempfile,shutil
R=Path(__file__).resolve().parent;repo=R.parents[3];S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in json.loads((R/'package_manifest.json').read_text())['files']:assert sha(R/row['path'])==row['sha256'],row['path']
for row in json.loads((S/'snapshot_manifest.json').read_text())['files']:
 assert subprocess.check_output(['git','show',f"{row['source_commit']}:{row['source_path']}"])==(S/row['snapshot']).read_bytes()
P=R/'real_prop_reference_61sol'
for row in json.loads((P/'sources/snapshot_manifest.json').read_text())['files']:
 rel=Path(row['origin_path']).relative_to(repo);assert subprocess.check_output(['git','show',f'3ef32eda4654c02fae336ee949f464af69836ab1:{rel}'])==(P/'sources'/row['snapshot']).read_bytes()
g=json.loads((R/'geometry/input_gate_checks.json').read_text());reach=json.loads((R/'geometry/continuous_reach_and_real_reference_checks.json').read_text());assert g['calls']==0 and not g['F069_input_or_art_created'] and not(R/'requests/execution_state.json').exists()
assert g['previous_thin_prop_adopted_pixels']==g['previous_old044_grasp_adopted_pixels']==0 and not g['fragmentary026_body_backplate_used'] and not g['current_far_palm_frozen']
a=np.asarray(Image.open(R/'reference/A_F063_full_target_NOT_ART_native.png'));mother=np.asarray(Image.open(S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png'));guard=np.zeros(a.shape[:2],bool)
for p in ['HARD_actual_head_neck_collar','HARD_actual_near_whole_ruffle','HARD_actual_stable_skirt']:guard|=np.asarray(Image.open(R/'masks'/f'{p}.png').convert('L'))>0
assert np.array_equal(a[guard],mother[guard])and not np.any(guard&(mother[:,:,3]==0))
white=np.asarray(Image.open(R/'masks/WHITE_complete_torso_near_fullarm_grip_fullprop_far_fullarm_hand_air.png').convert('L'))>0;assert not np.any(white&guard)
for p in ['TECH_complete_torso_NOT_ART','TECH_complete_near_arm_grip_NOT_ART','SOFT_actual_receiver_whole_hand_NOT_HARD']:
 z=np.asarray(Image.open(R/'masks'/f'{p}.png').convert('L'))>0;assert not np.any(z&~white&~guard)
real=np.asarray(Image.open(P/'reference/04_same_frozen_TL_real_visible_prop_SCALE1_NOT_GESTURE.png'));hand=np.asarray(Image.open(R/'layers/F063_actual_whole_receiver_hand_REPOSITIONED_SOFT_NOT_FROZEN.png'))
for alpha in [1,16,128]:
 pm=real[:,:,3]>=alpha;hm=hand[:,:,3]>=alpha;value=float(distance_transform_edt(~pm)[hm].min());assert abs(value-reach['actual_gap063_by_alpha'][str(alpha)]['gap_native'])<1e-10 and not np.any(pm&hm)
assert g['near_technical_volume_intersection_head']==g['near_technical_volume_intersection_stable_skirt']==g['far_technical_volume_intersection_head']==g['far_technical_volume_intersection_stable_skirt']==0
assert [s['real_hand_to_real_prop_by_alpha']['128']['gap_native']for s in reach['steps']]==[15,12,9,6,3,0]
for step in reach['steps']:
 assert abs(step['upper_proxy_length']-reach['far_proxy_lengths_not_measured_bones']['upper'])<1e-8 and abs(step['fore_proxy_length']-reach['far_proxy_lengths_not_measured_bones']['fore'])<1e-8
 assert step['far_proxy_and_hand_head_intersection']==step['far_proxy_and_hand_stable_skirt_intersection']==0
args=json.loads((R/'requests/arguments_PREPARED_NOT_CALLED.json').read_text());assert args['prompt']==(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text().rstrip('\n')and len(args['referenced_image_paths'])==5 and args['transparent_background']
for k,p in zip('ABCDE',args['referenced_image_paths']):assert Path(p)==R/f'reference/{k}_F063_PREPARED_NOT_CALLED_1280x1536.png' and Image.open(p).size==(1280,1536)
# Reconstruct the entire set from real-source snapshots and technical scripts,
# in isolation; actual source bytes and previously-reviewed inputs stay untouched.
with tempfile.TemporaryDirectory(prefix='s09-full-action-gate-')as tmp:
 T=Path(tmp);shutil.copytree(S,T/'sources');Q=T/'real_prop_reference_61sol';Q.mkdir();shutil.copytree(P/'sources',Q/'sources');shutil.copyfile(P/'prepare_real_prop.py',Q/'prepare_real_prop.py')
 for group in ['qa','geometry','masks','reference','requests','layers']:(T/group).mkdir(exist_ok=True)
 for name in ['prepare_gate.py','complete_input_and_reach.py']:shutil.copyfile(R/name,T/name)
 for script in [Q/'prepare_real_prop.py',T/'prepare_gate.py',T/'complete_input_and_reach.py']:subprocess.run(['python',str(script)],check=True,stdout=subprocess.DEVNULL)
 for group in ['reference','layers','masks']:
  for p in (R/group).glob('*.png'):assert p.read_bytes()==(T/group/p.name).read_bytes(),str(p)
 for p in (P/'reference').glob('*.png'):assert p.read_bytes()==(Q/'reference'/p.name).read_bytes()
 for name in ['input_gate_checks.json','continuous_reach_and_real_reference_checks.json']:assert json.loads((R/'geometry'/name).read_text())==json.loads((T/'geometry'/name).read_text())
print('PASS:12 sources git-byte-exact;5 complete inputs isolated replay;real whole-palm/source-prop gaps;head/ruffle/skirtRGBA0;whiteguards0;continuous equal-proxy reach;0calls/noF069input.')
