from pathlib import Path
import hashlib,json,shutil,datetime
P=Path(__file__).resolve().parent;W=P.parent;R=W/'astra_s08_first_mother_20261018_1433';records={};deps=[];scripts=[]
def hs(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)}
def cp(src,rel,role):
 d=P/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,d);assert src.read_bytes()==d.read_bytes();records[rel]={'path':rel,'original_path':str(src),'role':role,**hs(d)};return records[rel]
def inp(src,rel,target):
 e=cp(src,rel,'declared_replay_input_upstream_original_or_same_call17_raw');deps.append({'path':rel,'target':target,**hs(P/rel)})
# Actual submitted references and original call records stay unchanged.
req=json.loads((R/'F036_native_call17/request.json').read_text())
for i,s in enumerate(req['referenced_image_paths']):cp(Path(s),str(Path(s).relative_to(R)),'actual_call17_reference_order_'+str(i+1))
for folder in ['F036_native_call17','F036_input_gate']:
 for n in ['request.json','prompt.txt','FROZEN_INPUT_MANIFEST.json','status.json']:
  if (R/folder/n).exists():cp(R/folder/n,folder+'/'+n,'unchanged_actual_call17_record')
raw='F036_native_call17/raw/F036_whole_turn_arms_native_raw.png';inp(R/raw,raw,raw)
folders=['F036_input_gate','F036_structure_gate','F036_color_final']+[f'F036_same_raw_semantic_v{i}' for i in range(1,10)]
for folder in folders:
 for q in sorted((R/folder).glob('*.py')):cp(q,str(q.relative_to(R)),'unchanged_original_source_script')
 for q in sorted((R/folder/'geometry').glob('*.json')):cp(q,str(q.relative_to(R)),'unchanged_source_diagnostic_or_contract')
for q in sorted((R/'F036_result_registered_nominal/geometry').glob('*.json')):cp(q,str(q.relative_to(R)),'nominal_registration_diagnostic')
for folder in ['F036_input_gate','F036_same_raw_semantic_v9','F036_color_final']:
 for q in sorted((R/folder/'masks').glob('*.png')):cp(q,str(q.relative_to(R)),'operation_mask_evidence_recomputed_by_replay_not_used_as_input')
for name in ['F036_preplaced_body_anchor_truehands_NO_ROD_RGBA.png','F036_preplaced_true_near_hand_match_RGBA.png','F036_original_underlying_far_hand_SEAT_RGBA.png']:
 cp(R/'F036_input_gate/inputs'/name,'F036_input_gate/inputs/'+name,'original_pixel_preplacement_evidence_recomputed_not_replay_input')
H=R/'F036_input_gate/history/pre_871_air_islands'
for q in sorted(H.rglob('*')):
 if q.is_file() and q.suffix in ['.json','.txt','.py','.png'] and 'qa' not in q.parts:cp(q,str(q.relative_to(R)),'history_pre_871_air_islands_NOT_actual_call17_input')
# Accepted upstream033 source layers are independent originals, not extracted from036 result.
needed=['S08_F033_grandma_match_box_RGBA.png','F033_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png','F033_true_near_hand_match_INDEPENDENT_FOREGROUND_footprint.png','F033_near_distal_hard_guard_footprint.png','F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png','F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png','F033_far_hand_jade_SEAT_hard_guard.png','F033_far_original_jade_AA_requires_same_raw_skin_underlay.png','F033_fixed_table_box_footprint.png']
for n in needed:inp(R/'F033_FINAL_LOCKED'/n,'dependencies/F033_FINAL_LOCKED/'+n,'F033_FINAL_LOCKED/'+n)
inp(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png','dependencies/F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png','F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png')
inp(W/'astra_s08_first33_actual_20261018_2047/canvas_new/F030.png','dependencies/actual030_canvas/F030.png','../astra_s08_first33_actual_20261018_2047/canvas_new/F030.png')
inp(Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),'dependencies/font/DejaVuSans.ttf','replay_font/DejaVuSans.ttf')
inp(R/'F036_structure_gate/geometry/F036_first_structure.json','F036_structure_gate/geometry/F036_first_structure.json','F036_structure_gate/geometry/F036_first_structure.json')
for rel in ['F033_LAYER_PARTITION/build_partition.py','F033_FINAL_LOCKED/HAND_REUSE_CONTRACT.json','F033_FINAL_LOCKED/SEALED_MANIFEST.json','F033_LAYER_PARTITION/LAYER_VALIDATION.json']:
 cp(R/rel,'original_upstream/'+rel,'upstream033_original_record')
script_defs=[('original_upstream/F033_LAYER_PARTITION/build_partition.py','F033_LAYER_PARTITION/build_partition.py'),('F036_input_gate/build_input.py','F036_input_gate/build_input.py'),('F036_input_gate/composite_returned_crop.py','F036_input_gate/composite_returned_crop.py'),('F036_same_raw_semantic_v9/build.py','F036_same_raw_semantic_v9/build.py'),('F036_color_final/apply_colors.py','F036_color_final/apply_colors.py')]
for rel,t in script_defs:scripts.append({'path':rel,'target':t,**hs(P/rel)})
final=R/'F036_color_final/candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png';assert hs(final)['sha256']=='6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753';cp(final,'final/'+final.name,'post_process_external_oracle_only_NEVER_replay_input')
index=[]
for folder in ['F036_result_registered_nominal']+[f'F036_same_raw_semantic_v{i}' for i in range(1,10)]:
 for q in sorted((R/folder/'candidates').glob('*.png')):index.append({'original_path':str(q),'retained_binary':False,'role':'same_call17_raw_diagnostic_stage','generation_call_increment':0,**hs(q)})
expected={}
def exp(rel,out=None):expected[out or rel]=hs(R/rel)['sha256']
exp('F033_LAYER_PARTITION/frames/F033_body_behind_original_pixels.png')
for q in sorted((R/'F036_input_gate/masks').glob('*.png')):exp(str(q.relative_to(R)))
for n in ['F036_preplaced_body_anchor_truehands_NO_ROD_RGBA.png','F036_preplaced_true_near_hand_match_RGBA.png','F036_original_underlying_far_hand_SEAT_RGBA.png']:exp('F036_input_gate/inputs/'+n)
for s in req['referenced_image_paths']:
 rel=str(Path(s).relative_to(R));out=rel.replace('_AIR871_CLEAN_1p5x','_1p5x');exp(rel,out)
for rel in ['F036_result_registered_nominal/candidates/S08_F036_whole_turn_arms_candidate_RGBA.png','F036_result_registered_nominal/registered/F036_registered_scene_patch_RGBA.png','F036_same_raw_semantic_v9/candidates/S08_F036_same_raw_semantic_RGBA.png','F036_color_final/candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png']:exp(rel)
for folder in ['F036_same_raw_semantic_v9','F036_color_final']:
 for q in sorted((R/folder/'masks').glob('*.png')):exp(str(q.relative_to(R)))
manifest={'schema_version':1,'scope':'Deterministic same-call17-raw postprocessing and all five submitted references from explicitly declared upstream033/000/canvas inputs. No F036 final/intermediate image is an input. Frozen actual registration applied; optimizer source preserved but not rerun.','inputs':deps,'scripts':scripts,'registration':json.loads((R/'F036_input_gate/geometry/RAW_UNIFORM_REGISTRATION.json').read_text()),'expected':expected,'final_seal_and_partition':'Pending author box-layer ownership resolution; separate supplement will follow.'}
(P/'REPLAY_DEPENDENCIES.json').write_text(json.dumps(manifest,indent=2)+'\n')
(P/'DIAGNOSTIC_EVIDENCE_INDEX.json').write_text(json.dumps({'valid_native_calls':17,'preserved_raws':17,'tool_submissions':18,'old_parameter_validation_failures':1,'call17_state_generations':1,'same_raw_stages':index,'pre_871_air_islands_history_is_not_submitted':True},indent=2)+'\n')
(P/'SOURCE_MANIFEST.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_root':str(R),'source_files_unchanged':True,'files':list(records.values())},indent=2)+'\n')
print(json.dumps({'files':len(records),'bytes':sum(e['bytes'] for e in records.values()),'replay_inputs':len(deps),'replay_scripts':len(scripts),'expected_outputs':len(expected)},indent=2))
