from pathlib import Path
import sys,json,hashlib,subprocess,datetime,shutil
from PIL import Image
P=Path(__file__).resolve().parent;PACK=P.parent;FROZEN='6579fd242bb6db148ae196e5ab07960a4913bd32';order=[36,39,42,45,47,54];f=int(sys.argv[1]);assert f in order
if f!=36:
 prev=order[order.index(f)-1];st=json.loads((P/f'F{prev:03}/status.json').read_text());assert st['state']=='AUTHOR_ACCEPTED','Stop only dependent following states if actual structure failed.'
S=PACK/'next_036_057_inputs_002'/f'F{f:03}';F=P/f'F{f:03}';F.mkdir(exist_ok=True);assert not (F/'request_submitted.json').exists(),'No automatic duplicate submission.'
path=S/'tool_args_prepared_NOT_SUBMITTED.json';rel=str(path.relative_to(PACK.parents[2]));# git path is relative to repository root below
repo=PACK.parents[2];root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip());rel=str(path.relative_to(root));assert path.read_bytes()==subprocess.check_output(['git','show',FROZEN+':'+rel])
a=json.loads(path.read_text());m=json.loads((S/'input_manifest.json').read_text());extra='圆形肩/肘是施工体积，不得照抄成球；奶奶保持真实蓝花宽短袖，只有小满是黄泡袖。';a['prompt']=a['prompt']+'\n'+extra
snap=F/'actual_input_snapshots';snap.mkdir(exist_ok=True)
for row,pth in zip(m['inputs'],a['referenced_image_paths']):
 p=Path(pth);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];shutil.copyfile(p,snap/f"{row['order']:02}_{p.name}")
req={'tool':'image_gen.imagegen','args':a,'frame':f,'actual_inputs':m['inputs'],'frozen_input_commit':FROZEN,'only_prompt_append':extra,'attempt_this_state':1,'cumulative_cloud_request_number':17+order.index(f),'native004_calls_not_cloud':1,'authorization':'Astra six-state batch input gate passed;036->039->042->045->047->054 continuous generation and actual author review;048–053 reuse047; no per-state principal gate','submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for name,val in [('tool_args_exact.json',a),('request_submitted.json',req)]: (F/name).write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n')
(F/'prompt_submitted_zh.txt').write_text(a['prompt']+'\n');(F/'status.json').write_text(json.dumps({'frame':f,'state':'IN_FLIGHT','attempts_started':1,'in_flight':1,'new_raws':0,'automatic_retry':False,'cumulative_cloud_request_number':17+order.index(f)},indent=2)+'\n');print(json.dumps(a,ensure_ascii=False))
