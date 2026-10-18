#!/usr/bin/env python3
from pathlib import Path
import argparse,json,shutil,subprocess,sys,datetime
ap=argparse.ArgumentParser();ap.add_argument('--sandbox',type=Path,required=True);a=ap.parse_args();P=Path(__file__).resolve().parent;S=a.sandbox.resolve()
if S.exists():raise SystemExit('Refuse existing test sandbox')
S.mkdir();m=json.loads((P/'REPLAY_DEPENDENCIES.json').read_text());files=['replay_f036.py','REPLAY_DEPENDENCIES.json']+[e['path'] for e in m['inputs']+m['scripts']];reports=[]
for name in ['missing_raw','tampered_raw','undeclared_final_read','network_denied','existing_output']:
 t=S/name;b=t/'bundle';b.mkdir(parents=True)
 for rel in files:
  d=b/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/rel,d)
 raw=b/'F036_native_call17/raw/F036_whole_turn_arms_native_raw.png';out=t/'output';cmd=[sys.executable,'-I',str(b/'replay_f036.py'),'--out',str(out)]
 if name=='missing_raw':raw.unlink()
 if name=='tampered_raw':v=bytearray(raw.read_bytes());v[-1]^=1;raw.write_bytes(v)
 if name=='undeclared_final_read':cmd+=['--probe-disallowed-read',str(P/'final/S08_F036_whole_turn_same_raw_final_color_RGBA.png')]
 if name=='network_denied':cmd+=['--probe-network']
 if name=='existing_output':out.mkdir();(out/'sentinel').write_text('keep me')
 r=subprocess.run(cmd,cwd=t,capture_output=True,text=True);expected={'missing_raw':'FileNotFoundError','tampered_raw':'Input hash mismatch','undeclared_final_read':'Undeclared replay input','network_denied':'Replay disallows network','existing_output':'Refusing to overwrite'}[name];passed=r.returncode!=0 and expected in (r.stdout+r.stderr)
 if name=='existing_output':passed &= (out/'sentinel').read_text()=='keep me'
 reports.append({'test':name,'pass':bool(passed),'returncode':r.returncode,'expected_failure':expected,'stderr_tail':r.stderr[-1800:]});assert passed,reports[-1]
report={'status':'PASS_FIVE_NEGATIVE_TESTS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'external_network_connection_attempts':0,'tests':reports};(S/'REPLAY_NEGATIVE_TESTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
