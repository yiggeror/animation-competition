from pathlib import Path
import json,sys,hashlib,datetime,shutil
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);order=[12,15,18,22,24,27,30];assert f in order
F=P/f'F{f:03}';assert not (F/'request_submitted.json').exists()
if f!=12:assert json.loads((P/f'F{order[order.index(f)-1]:03}/status.json').read_text())['state']=='AUTHOR_ACCEPTED'
args=json.loads((F/'tool_args_prepared.json').read_text());m=json.loads((F/'input_manifest.json').read_text());snap=F/'submitted_input_snapshots';snap.mkdir(exist_ok=True)
for r in m['inputs']:
 p=Path(r['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(p,snap/f"{r['order']:02}_{p.name}")
req={'tool':'image_gen.imagegen','args':args,'submitted_inputs':m['inputs'],'frame':f,'attempt_this_state':1,'cumulative_request_number':8+len(list(P.glob('F*/request*submitted.json'))),'authorization':'Astra locked008/020/032; continuously fill012/015/018 then022/024/027/030 with actual self-review;004 exclusively native Astra, cloud004 calls0','submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(F/'request_submitted.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n');(F/'tool_args_exact.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n');(F/'prompt_submitted_zh.txt').write_text(args['prompt']+'\n');(F/'status.json').write_text(json.dumps({'state':'IN_FLIGHT','frame':f,'attempts_started':1,'in_flight':1,'new_raws':0,'automatic_retry':False},indent=2)+'\n')
print(json.dumps(args,ensure_ascii=False))
