from pathlib import Path
import json,hashlib,subprocess,datetime
root=Path.cwd();I=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_inputs_20261019');O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_actual_call01_20261019')
assert not O.exists(),'Unique call already prepared; inspect state before any submission.'
for d in ['prompts','requests','provenance','originals','diagnostics','tools','candidate','layers','masks','actual_scene','scene','qa']:(O/d).mkdir(parents=True,exist_ok=True)
req=json.loads((I/'requests/F026_local_repair_PREPARED_NOT_SUBMITTED.json').read_text());p=req['args']['prompt'];old=p
needle='No arm/body/head, near-right hand';assert p.count(needle)==1
p=p.replace(needle,'No whole arm/body/head, near-right hand')
needle='or guide labels may appear.';assert p.count(needle)==1
p=p.replace(needle,needle+' Retain the same short forearm entry and wrist context visible at the left edge solely to preserve attachment and registration; do not extend, redesign or rescale the arm.')
needle='These are target approximations, not permission to distort anatomy.';assert p.count(needle)==1
p=p.replace(needle,needle+' The visible splice at the DIP and distal pad is a construction defect, not a second joint or an extra tip. Redraw one continuous three-phalange index with a single rounded pad and natural joint creases. Keep legitimate air between separate fingers, but do not reproduce cut seams inside the index or a disconnected palm root.')
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for item in req['inputs']:
 f=I/item['path'];fixed=subprocess.check_output(['git','show','d9ac06ee554bc217219d26580f028d8985d72356:'+str(f)]);assert f.read_bytes()==fixed and sha(fixed)==item['SHA256'];rows.append({'path':str(f),'SHA256':sha(fixed)})
args={'prompt':p,'referenced_image_paths':[str((root/I/x['path']).resolve()) for x in req['inputs']],'transparent_background':True}
(O/'prompts/F026_local_index_ACTUAL_prompt.txt').write_text(p)
actual={'tool':'image_gen.imagegen','args':args,'authorized_max_calls':1,'authorized_max_originals':1,'reference_freeze_commit':'d9ac06ee554bc217219d26580f028d8985d72356','inputs_unchanged':rows,'actual_prompt_SHA256':sha(p.encode()),'previous_prompt_SHA256':sha(old.encode()),'source_reviewer_thread':'01a15188-00cc-7705-b91f-7b18102ba0d0','authorization':'Final input gate passed; exactly the two specified textual revisions allowed without another review; execute unique one call. Preserve raw and receipt, then readonly scale/anatomy check, source-only minimal index/root composite if sound; major bone-chain/finger failure stop. F030 remains closed.'}
rp=O/'requests/F026_local_index_ACTUAL_request.json';rp.write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n')
ledger={'status':'PREPARED_AUTHORIZED_NOT_YET_SUBMITTED','new_calls_submitted':0,'authorized_calls':1,'S12_historical_calls_before_this':8,'F030_calls':0,'source_reviewer_thread':actual['source_reviewer_thread'],'actual_prompt_SHA256':actual['actual_prompt_SHA256'],'actual_request_SHA256':sha(rp.read_bytes()),'prepared_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(O/'provenance/call_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'actual_args':args,'prompt_SHA256':ledger['actual_prompt_SHA256'],'request_SHA256':ledger['actual_request_SHA256'],'ledger':str(O/'provenance/call_ledger.json')},ensure_ascii=False))
