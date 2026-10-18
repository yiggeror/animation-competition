#!/usr/bin/env python3
"""Recompose raw/source layers in a fresh tree without chosen068/073 PNG inputs."""
from pathlib import Path
import json,hashlib,tempfile,shutil,subprocess,time
R=Path(__file__).resolve().parent;B=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
started=time.monotonic();inputs=[];results=[]
with tempfile.TemporaryDirectory(prefix='s07-068-073-isolated-')as tmp:
 D=Path(tmp)/B.name;D.mkdir()
 def copy(rel):
  src=B/rel;dst=D/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);inputs.append({'path':str(rel),'sha256':sha(src)})
 for rel in ['F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png','F062_native_call01/masks/native_complete_trousers_full_source_material.png','F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png','F068_next_gate/geometry/preparation_checks.json']:
  copy(Path(rel))
 for folder in ['F068_next_gate','F073_next_gate']:
  for directory in ['layers','originals']:
   for p in sorted((B/folder/directory).glob('*.png')):copy(p.relative_to(B))
  copy(Path(folder)/'compose_native.py')
 for rel in ['F073_next_gate/compose_repair02.py','F073_next_gate/repair_call02/originals/F073_call02_raw.png','F073_next_gate/sources/F068_far_shoe_ankle_LANDED.png','segment_057_078_delivery/build_exposure.py']:copy(Path(rel))
 (D/'F073_next_gate/repair_call02/qa').mkdir(parents=True,exist_ok=True)
 for script in ['F068_next_gate/compose_native.py','F073_next_gate/compose_native.py','F073_next_gate/compose_repair02.py']:
  subprocess.run(['python',str(D/script)],check=True,capture_output=True,text=True)
 for folder,stage,chosen in [('F068_next_gate','F068_complete_native_layered_PENDING_ACTUAL_REVIEW.png','F068_single_native_final_PENDING_ASTRA.png'),('F073_next_gate','F073_repaired_complete_native_layered_PENDING_ACTUAL_REVIEW.png','F073_single_native_final_PENDING_ASTRA.png')]:
  fresh=D/folder/'candidate'/stage;shutil.copyfile(fresh,D/folder/'candidate'/chosen)
  # Target bytes enter only the external comparison, after child processes.
  results.append({'artifact':f'{folder}/candidate/{chosen}','expected_sha256':sha(B/folder/'candidate'/chosen),'replayed_sha256':sha(fresh)})
  for p in sorted((D/folder/'production_layers').glob('*.png')):
   rel=p.relative_to(D);results.append({'artifact':str(rel),'expected_sha256':sha(B/rel),'replayed_sha256':sha(p)})
 subprocess.run(['python',str(D/'segment_057_078_delivery/build_exposure.py')],check=True,capture_output=True,text=True)
 rel=Path('segment_057_078_delivery/exposure/S07_F057x5_F062x6_F068x5_F073x6_actual_layer_24fps_PENDING.mp4');results.append({'artifact':str(rel),'expected_sha256':sha(B/rel),'replayed_sha256':sha(D/rel)})
 assert all(x['expected_sha256']==x['replayed_sha256']for x in results)
report={'status':'ISOLATED_RAW_AND_LAYER_REPLAY_SHA_IDENTICAL','elapsed_seconds':time.monotonic()-started,'chosen068_and073_targets_not_provided_to_child_processes':True,'legitimate_locked057_062_inputs_provided':True,'no_network_or_image_generation':True,'inputs':inputs,'artifacts':results,'identical_artifacts':len(results)}
(R/'qa').mkdir(exist_ok=True);(R/'qa/isolated_replay_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','elapsed_seconds','identical_artifacts']},ensure_ascii=False))
