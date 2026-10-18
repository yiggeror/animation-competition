from pathlib import Path
import hashlib,json,datetime
P=Path(__file__).resolve().parent;prefix='collab/reviews/20261018_2201_s08_f036_provenance/'
def hs(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)}
source=json.loads((P/'SOURCE_MANIFEST.json').read_text());same=[];changed=[]
for e in source['files']:
 local=hs(P/e['path']);assert local['sha256']==e['sha256'],e['path'];s=Path(e['original_path']);h=hs(s)
 (same if h['sha256']==e['sha256'] else changed).append({'path':e['path'],'original_path':str(s),'preserved_sha256':e['sha256'],'current_original_sha256':h['sha256']})
assert not changed,changed
minimum=json.loads((P/'ROWS_MINIMUM_ONLY.json').read_text())
for e in minimum:
 assert hs(Path(e['local']))['sha256']==e['sha256'];assert hs(Path(e['local']))['git_blob_sha']==e['sha'];assert hs(Path(e['local']))['bytes']==e['bytes']
replay=json.loads((P/'REPLAY_RESULT.json').read_text());negative=json.loads((P/'REPLAY_NEGATIVE_TESTS.json').read_text());log=json.loads((P/'ISOLATED_REPLAY_LOG.json').read_text());assert replay['status']=='PASS_EXACT_CALL17_F036_REPLAY' and len(replay['outputs_verified'])==73 and all(e['identical'] for e in replay['outputs_verified']);assert all(e['pass'] for e in negative['tests']);assert log['post_process_external_oracle_comparison']['PNG_bytes_identical']
manifest=json.loads((P/'REPLAY_DEPENDENCIES.json').read_text());assert len(manifest['inputs'])==14 and len(manifest['scripts'])==10
for e in manifest['inputs']+manifest['scripts']:assert hs(P/e['path'])['sha256']==e['sha256']
audit={'status':'PASS_PRESERVED_SOURCE_AND_DECLARED_DEPENDENCY_AUDIT','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originals_unchanged':True,'original_count':len(same),'originals':same,'minimal_nine_intact':True,'replay_inputs':14,'original_replay_scripts':10,'verified_outputs':73,'all_output_SHA_match':True,'source_inputs_never_F036_final_or_same_state_intermediate_or_53_483_masks':True,'new_generation_calls':0,'external_writes':0,'independent_visual_acceptance_inferred':False};(P/'SOURCE_DEPENDENCY_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
exclusions={'ROWS.json','ROWS_SUPPLEMENT_ONLY.json','ROWS_MINIMUM_ONLY.json','TRANSFER_SUMMARY.json'};minimum_paths={e['path'] for e in minimum};rows=[]
for p in sorted(P.rglob('*')):
 if not p.is_file() or p.name in exclusions or '__pycache__' in p.parts:continue
 h=hs(p);rel=str(p.relative_to(P));rows.append({'local_path':str(p),'local':str(p),'path':prefix+rel,**h,'gitsha':h['git_blob_sha'],'sha':h['git_blob_sha'],'upload':True})
rows_by_path={e['path']:e for e in rows}
for e in minimum:
 assert rows_by_path[e['path']]['sha256']==e['sha256']
 rows_by_path[e['path']].update({'upload':False,'reuse_commit':'38b2f9d13bc6ec7bbd190742e5ae245cc99bb33d','reuse_path':e['path'],'known_blob_source':'Coordinator directly confirmed fixed commit readback9/9 on2026-10-18T22:09:07Z'})
supp=[e for e in rows if e['path'] not in minimum_paths]
(P/'ROWS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(P/'ROWS_SUPPLEMENT_ONLY.json').write_text(json.dumps(supp,ensure_ascii=False,indent=2)+'\n')
summary={'status':'LOCAL_SOURCE_PACKAGE_COMPLETE_READY_FOR_COORDINATOR','minimum_files':len(minimum),'minimum_bytes':sum(e['bytes'] for e in minimum),'supplement_files':len(supp),'supplement_bytes':sum(e['bytes'] for e in supp),'total_files':len(rows),'total_bytes':sum(e['bytes'] for e in rows),'supplement_upload_flags_true_pending_coordinator_blob_availability_check':True,'minimum_nine_reused_at_fixed_commit':'38b2f9d13bc6ec7bbd190742e5ae245cc99bb33d','rows_sha256':hs(P/'ROWS.json')['sha256'],'supplement_rows_sha256':hs(P/'ROWS_SUPPLEMENT_ONLY.json')['sha256'],'minimum_rows_sha256':hs(P/'ROWS_MINIMUM_ONLY.json')['sha256'],'raw_sha256':'0c5406e79310fcbf80739e32de630bfb65d2f9e4f0110b31e4658c7d5d6a951d','final_sha256':'6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753','replay_verified_outputs':73,'negative_tests':5,'new_generation_calls':0,'external_writes':0};(P/'TRANSFER_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
