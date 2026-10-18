#!/usr/bin/env python3
"""Copy only six declared inputs plus the replay script/manifest, then run.
The optional locked final is read by this harness only AFTER subprocess exit.
All evidence is written inside a NEW sandbox. No existing output is overwritten.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess, sys
ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--sandbox',type=Path,required=True);ap.add_argument('--verify-against',type=Path);args=ap.parse_args()
p=args.package_root.resolve();sandbox=args.sandbox.resolve()
if sandbox.exists():raise SystemExit('Refusing to overwrite existing sandbox')
sandbox.mkdir(parents=True)
m=json.loads((p/'REPLAY_DEPENDENCIES.json').read_text());files=['replay_f027.py','REPLAY_DEPENDENCIES.json']+[e['path'] for e in m['inputs']]
assert len(files)==8 and len(set(files))==8
for rel in files:
 dest=sandbox/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/rel,dest)
pre=sorted(str(f.relative_to(sandbox)) for f in sandbox.rglob('*') if f.is_file());assert pre==sorted(files)
command=[sys.executable,'replay_f027.py','--out','output']
start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(command,cwd=sandbox,capture_output=True,text=True)
(sandbox/'ISOLATED_REPLAY.stdout.txt').write_text(result.stdout);(sandbox/'ISOLATED_REPLAY.stderr.txt').write_text(result.stderr)
log={'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'cwd':str(sandbox),'exit_code':result.returncode,'pre_run_files':pre,'only_six_inputs_plus_script_and_manifest':True,'reference_final_present_during_replay':False,'network_used':False,'new_generation_calls':0}
if result.returncode==0:
 output=sandbox/'output/S08_F027_grandma_match_box_RGBA.png'
 log['output_SHA256']=hashlib.sha256(output.read_bytes()).hexdigest()
 if args.verify_against:
  import numpy as np
  from PIL import Image
  # This external oracle never enters the isolated directory or subprocess.
  oracle=args.verify_against.resolve();a=np.array(Image.open(output));b=np.array(Image.open(oracle))
  log['post_run_external_oracle_comparison']={'different_RGBA_pixels':int(np.any(a!=b,axis=2).sum()),'max_channel_error':int(np.abs(a.astype(int)-b.astype(int)).max()),'PNG_bytes_identical':output.read_bytes()==oracle.read_bytes(),'expected_SHA256':hashlib.sha256(oracle.read_bytes()).hexdigest(),'actual_SHA256':hashlib.sha256(output.read_bytes()).hexdigest()}
(sandbox/'ISOLATED_REPLAY_LOG.json').write_text(json.dumps(log,indent=2)+'\n');print(json.dumps(log,indent=2));sys.exit(result.returncode)
