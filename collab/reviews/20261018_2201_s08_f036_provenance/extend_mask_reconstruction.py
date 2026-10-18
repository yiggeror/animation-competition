from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parent;R=P.parent/'astra_s08_first_mother_20261018_1433';M=P/'REPLAY_DEPENDENCIES.json';m=json.loads(M.read_text());sm=json.loads((P/'SOURCE_MANIFEST.json').read_text());records={e['path']:e for e in sm['files']};H='F036_box_layer_source_diagnostic/history_before_layer_correction/'
def hs(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)}
def cp(rel,role):
 d=P/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,d);records[rel]={'path':rel,'original_path':str(R/rel),'role':role,**hs(d)};return {'path':rel,**hs(d)}
maskrels=['F036_box_layer_source_diagnostic/EXCLUDE_near_archive_old_blue_collar_NOT_HAND.png','F036_box_layer_source_diagnostic/EXTRA483_original033_body_box_fringe.png']
m['inputs']=[x for x in m['inputs'] if x['path'] not in maskrels]
oldseal=cp(H+'F036_FINAL_LOCKED/seal.py','original_historical_pre_correction_seal_recomputed_in_replay');oldseal['target']='F036_FINAL_LOCKED/seal.py'
oldpart=cp(H+'F036_LAYER_PARTITION/build_partition.py','original_historical_pre_correction_partition_recomputed_in_replay');oldpart['target']='F036_LAYER_PARTITION/build_partition.py'
need=['F036_FINAL_LOCKED/F036_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png','F036_FINAL_LOCKED/F036_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png','F036_FINAL_LOCKED/F036_near_distal_hard_guard_footprint.png','F036_LAYER_PARTITION/frames/F036_table_box_original_pixels.png']
oldpart['archive_outputs_after']=[{'source':r,'target':H+r} for r in need]
for rel in need:
 q=R/(H+rel);m['expected'][H+rel]=hs(q)['sha256']
rebuild=cp('F036_box_layer_source_diagnostic/rebuild_explicit_masks.py','original_author_script_rebuild53_and483_masks_from_reconstructed_history');rebuild['target']=rebuild['path']
for rel in maskrels:m['expected'][rel]=hs(R/rel)['sha256']
m['scripts']=[e for e in m['scripts'] if e['path'] not in {oldseal['path'],oldpart['path'],rebuild['path']}];i=next(i for i,e in enumerate(m['scripts']) if e['path']=='F036_FINAL_LOCKED/seal.py');m['scripts'][i:i]=[oldseal,oldpart,rebuild]
m['scope']='Deterministic same-call17-raw postprocessing, all five actual submitted references,53/483 correction masks reconstructed from generated pre-correction history, corrected independent hands and exclusive three layers.14 declared original upstream/raw resources; no F036 final, intermediate, or correction-mask image as input.'
m['final_correction_masks_are_inputs']=False;m['final_correction_masks_reconstructed_from_generated_history']=True
M.write_text(json.dumps(m,indent=2)+'\n');sm['files']=list(records.values());(P/'SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2)+'\n');print(len(m['inputs']),len(m['scripts']),len(m['expected']))
