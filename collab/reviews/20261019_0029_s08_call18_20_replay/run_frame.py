from pathlib import Path
import json,subprocess,sys,hashlib,time
B=Path(__file__).resolve().parent;plan=json.loads((B/'reports/PLAN.json').read_text());frame=sys.argv[1];rows=[]
for i,(f,args) in enumerate(plan['commands'],1):
 if f!=frame:continue
 tag=f'{i:02d}_{f}_{Path(args[0]).stem}';log=B/'logs'/f'{tag}.log';start=time.monotonic()
 with log.open('w') as out:
  p=subprocess.run([sys.executable,'-B',str(B/'run_one_guarded.py'),tag,*args],stdout=out,stderr=subprocess.STDOUT,cwd=B/'worktree',timeout=180)
 entry={'step':tag,'exit_code':p.returncode,'log':str(log),'elapsed_seconds':round(time.monotonic()-start,3)};rows.append(entry);print(json.dumps(entry),flush=True)
 if p.returncode:
  print(log.read_text()[-8000:],flush=True);break
(B/'reports'/f'{frame}_RUN.json').write_text(json.dumps(rows,indent=2)+'\n')
final=B/'worktree'/f'{frame}_FINAL_LOCKED'/f'S08_{frame}_grandma_match_box_RGBA.png'
if final.exists():
 h=hashlib.sha256(final.read_bytes()).hexdigest();print(json.dumps({'frame':frame,'final_sha256':h,'expected_sha256':plan['expected_final_sha256'][frame],'exact':h==plan['expected_final_sha256'][frame]}))
