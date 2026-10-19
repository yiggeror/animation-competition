"""Freeze approved inputs, reserve exactly one attempt; never calls image API."""
from pathlib import Path
import sys,json,hashlib,shutil,subprocess,datetime
from PIL import Image
P=Path(__file__).resolve().parent;PACK=P.parent
GATE=PACK/'handoff_008_020_032_reference_001'
COMMIT='c1b1833b7dfe806ae2daa1b84ddacfb804070f3d'
frame=int(sys.argv[1]);assert frame in [8,20,32]
prev={20:8,32:20}.get(frame)
if prev:
 status=json.loads((P/f'F{prev:03}/status.json').read_text())
 assert status['state']=='AUTHOR_ACCEPTED',status
 assert (P/f'F{prev:03}'/status['accepted_png']).exists()
out=P/f'F{frame:03}';out.mkdir(exist_ok=True)
assert not (out/'request_submitted.json').exists(),'One attempt per state; no automatic retry.'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=json.loads((GATE/f'F{frame:03}/request_prepared.json').read_text())['tool_args']
rows=json.loads((GATE/f'F{frame:03}/input_manifest.json').read_text())
snap=out/'submitted_input_snapshots';snap.mkdir(exist_ok=True)
for row,file in zip(rows,args['referenced_image_paths']):
 p=Path(file);assert sha(p)==row['sha256'] and list(Image.open(p).size)==row['size']
 rel=p.relative_to(PACK.parents[2]).as_posix()
 frozen=subprocess.check_output(['git','show',COMMIT+':'+rel],cwd=PACK.parents[2])
 assert hashlib.sha256(frozen).hexdigest()==row['sha256']
 shutil.copyfile(p,snap/f"{row['order']:02}_{p.name}")
req={'tool':'image_gen.imagegen','frame':frame,'cumulative_request_number':{8:4,20:5,32:6}[frame],
 'attempt_this_state':1,'frozen_gate_commit':COMMIT,'args':args,'submitted_inputs':rows,
 'authorization':'Astra final batch gate: 008 -> 020 -> 032, at most one per state; continue only after actual predecessor self-review passes.',
 'submitted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out/'request_submitted.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
(out/'prompt_submitted_zh.txt').write_text(args['prompt']+'\n')
(out/'tool_args_exact.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(out/'status.json').write_text(json.dumps({'state':'IN_FLIGHT','frame':frame,'attempts_started':1,'maximum_attempts':1,
 'automatic_retry':False,'in_flight':1,'new_raws':0,'later_states_submitted':0,'frozen_gate_commit':COMMIT},indent=2)+'\n')
print(json.dumps({'prepared':frame,'inputs':len(rows),'all_frozen_bytes_match':True,'attempt_reserved':1}))
