from pathlib import Path
import hashlib,json,shutil,datetime
from PIL import Image
P=Path(__file__).resolve().parent;W=P.parent;R=W/'astra_s08_first_mother_20261018_1433';prefix='collab/reviews/20261018_2201_s08_f036_provenance/'
req=json.loads((R/'F036_native_call17/request.json').read_text()); frozen=json.loads((R/'F036_native_call17/FROZEN_INPUT_MANIFEST.json').read_text());status=json.loads((R/'F036_native_call17/status.json').read_text())
def hashes(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)}
assert hashes(R/'F036_native_call17/request.json')['sha256']==hashes(R/'F036_input_gate/request.json')['sha256']==frozen['request_sha256']=='029ba7688874d2ccc40c4503158f038f95aa93dc52d1eeaeaaa063e781a4a728'
assert req['prompt']==(R/'F036_native_call17/prompt.txt').read_text();assert len(req['referenced_image_paths'])==5
rels=['F036_native_call17/request.json','F036_native_call17/prompt.txt']+[str(Path(x).relative_to(R)) for x in req['referenced_image_paths']]+['F036_native_call17/raw/F036_whole_turn_arms_native_raw.png']
records=[]
for rel in rels:
 src=R/rel;dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert src.read_bytes()==dst.read_bytes();records.append({'path':rel,'original_path':str(src),**hashes(dst)})
for f in frozen['files']:assert hashes(Path(f['path']))['sha256']==f['sha256']
assert hashes(Path(status['original_native_path']))['sha256']==status['raw_sha256']==hashes(P/rels[-1])['sha256']=='0c5406e79310fcbf80739e32de630bfb65d2f9e4f0110b31e4658c7d5d6a951d'
assert Image.open(P/rels[-1]).size==(1293,1217)
receipt={'status':'PRESERVED_EXACT_CALL17_ORIGINALS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_sha256':frozen['request_sha256'],'prompt_sha256':hashes(P/rels[1])['sha256'],'actual_reference_count':5,'references_ordered':rels[2:7],'actual_five_reference_files_opened_for_preservation_review':True,'visual_review_scope':'These exact five submitted files were opened and inspected on 2026-10-18 at preservation time; this is source-identification review, not a new anatomy/material acceptance or a claim about pre-call review.','native_generation_calls_for_this_state':1,'native_raws_for_this_state':1,'new_generation_calls_for_preservation':0,'raw_sha256':status['raw_sha256'],'raw_size':[1293,1217],'raw_preserved_matches_original_native_output':True,'total_native_calls':17,'total_successful_raws':17,'total_tool_submissions':18,'total_old_parameter_validation_failures':1,'same_raw_semantic_v1_through_v9_and_color_are_not_generation_calls':True,'actual_request_revision':'AIR871_CLEAN; frozen request SHA exact','early_input_history':'F036_input_gate/history/pre_871_air_islands is not the actual submitted five-image set and remains separated from this minimum package.','final_candidate_sha256':'6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753','final_status_scope':'Parent coordinator reports current shape and color double-reviewed; author FINAL/layer seal is being preserved separately. No independent visual-acceptance claim is inferred from hashes.','composition_contract_scope':'Near hand and real far hand/jade source-over, transparent lever seat, and footprint releases must retain explicit source/mask provenance in the supplement; numbers do not constitute visual approval.','files':records,'original_status_record':status,'original_frozen_input_manifest':frozen}
(P/'MINIMUM_SOURCE_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');rels.append('MINIMUM_SOURCE_RECEIPT.json')
# Local evidence does not establish remote-blob availability; coordinator may safely deduplicate after checking repository objects.
rows=[]
for rel in rels:
 p=P/rel;h=hashes(p);rows.append({'local_path':str(p),'local':str(p),'path':prefix+rel,**h,'gitsha':h['git_blob_sha'],'sha':h['git_blob_sha'],'upload':True})
(P/'ROWS_MINIMUM_ONLY.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'files':len(rows),'bytes':sum(e['bytes'] for e in rows),'upload':sum(e['upload'] for e in rows),'rows':str(P/'ROWS_MINIMUM_ONLY.json')},indent=2))
