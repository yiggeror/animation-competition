#!/usr/bin/env python3
"""Append actual generation provenance without fabricating model names or success."""
from pathlib import Path
import json,hashlib,sys,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parent
n=int(sys.argv[1]);pose=sys.argv[2];toolpath=sys.argv[3]
reqpath=P/f'requests/call_{n:03}_request.json';req=json.loads(reqpath.read_text())
raw=P/f'originals/S13_{pose}_call_{n:03}_raw.png';assert raw.is_file()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req['status']='completed_one_raw_image';reqpath.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
inputs=[{'path':p,'sha256':sha(Path(p)),'bytes':Path(p).stat().st_size} for p in req['args']['referenced_image_paths']]
res={'call_id':req['call_id'],'completed_recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'tool':'image_gen.imagegen','raw':str(raw.relative_to(P)),'raw_sha256':sha(raw),'tool_original_path':toolpath,
 'returned_fields':['image_url','output_hint'],'image_data_storage':'Full returned image is preserved as original PNG, inline base64 not duplicated.',
 'model_version':'not exposed','inputs':inputs,'is_error':False}
(P/f'requests/call_{n:03}_response.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
lp=ROOT/'provenance/generation_ledger.json';ledger=json.loads(lp.read_text())
cid=req['call_id']
if not any(r['call_id']==cid for r in ledger['raw_outputs']):
 ledger['raw_outputs'].append({'call_id':cid,'pose':pose,'path':str(raw.relative_to(ROOT)),'sha256':sha(raw),
 'source_tool_path':toolpath,'adoption_status':'self_review_pending'})
ledger['raw_outputs'][0]['adoption_status']='Astra_locked_registered_mother_91715601ae81'
ledger['stage']='d02_d04_authorized_segment_in_progress'
ledger['successful_raw_images']=len(ledger['raw_outputs'])
ledger['image_generation_requests']=len(ledger['raw_outputs'])+ledger.get('failed_requests',0)
ledger['post_d01_pose_requests']=len(ledger['raw_outputs'])-1
ledger['note']='d01 registered mother locked by Astra; d02→d03→d04 sequential authorization. Actual generated edits only; scope masks may restore accepted pixels outside intended edits; no code-painted anatomy.'
lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(cid,sha(raw))
