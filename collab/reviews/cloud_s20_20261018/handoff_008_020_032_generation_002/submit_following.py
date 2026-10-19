"""Reserve one authorized following state and snapshot exact actual inputs.
Never performs a model call and never retries.
"""
from pathlib import Path
import json,hashlib,datetime,shutil,sys
from PIL import Image
P=Path(__file__).resolve().parent;frame=int(sys.argv[1]);assert frame in [20,32]
prev={20:8,32:20}[frame];status=json.loads((P/f'F{prev:03}/status.json').read_text())
assert status['state']=='AUTHOR_ACCEPTED'
F=P/f'F{frame:03}';assert not (F/'request_submitted.json').exists(),'Exactly one request per following state.'
args=json.loads((F/'tool_args_prepared.json').read_text());manifest=json.loads((F/'input_manifest.json').read_text())
snap=F/'submitted_input_snapshots';snap.mkdir(exist_ok=True)
for row,path in zip(manifest['inputs'],args['referenced_image_paths']):
 p=Path(path);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 assert list(Image.open(p).size)==row['size'];shutil.copyfile(p,snap/f"{row['order']:02}_{p.name}")
req={'tool':'image_gen.imagegen','args':args,'submitted_inputs':manifest['inputs'],'frame':frame,
 'attempt_this_state':1,'maximum_attempts_this_state':1,'cumulative_request_number':{20:6,32:7}[frame],
 'accepted_actual_predecessor':{'frame':prev,'path':str((P/f'F{prev:03}'/status['accepted_png']).resolve()),'sha256':status['accepted_sha256']},
 'authorization':'Astra: accepted actual corrected008 -> actual020 ->032; one each, self-review pass before continuation; no extra keys.',
 'submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(F/'request_submitted.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
(F/'tool_args_exact.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n');(F/'prompt_submitted_zh.txt').write_text(args['prompt']+'\n')
(F/'status.json').write_text(json.dumps({'state':'IN_FLIGHT','frame':frame,'attempts_started':1,'maximum_attempts':1,'automatic_retry':False,'in_flight':1,'new_raws':0,'predecessor_accepted_sha256':status['accepted_sha256']},indent=2)+'\n')
print('Reserved one F%03d request with %d actual inputs; predecessor accepted.'%(frame,len(args['referenced_image_paths'])))
