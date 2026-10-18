#!/usr/bin/env python3
"""Stage only declared sources, run offline replay, then compare external oracle after process exits."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess,sys
ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--sandbox',type=Path,required=True);ap.add_argument('--verify-against',type=Path);args=ap.parse_args()
p=args.package_root.resolve();s=args.sandbox.resolve()
if s.exists():raise SystemExit('Refusing to overwrite existing sandbox')
s.mkdir(parents=True);bundle=s/'bundle';bundle.mkdir();m=json.loads((p/'REPLAY_DEPENDENCIES.json').read_text());files=['replay_f036.py','REPLAY_DEPENDENCIES.json']+[e['path'] for e in m['inputs']+m['scripts']];assert len(files)==len(set(files))
for rel in files:
 d=bundle/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/rel,d)
pre=sorted(str(f.relative_to(bundle)) for f in bundle.rglob('*') if f.is_file());assert pre==sorted(files)
command=[sys.executable,'-I',str(bundle/'replay_f036.py'),'--out',str(s/'output')];start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(command,cwd=s,capture_output=True,text=True)
(s/'ISOLATED_REPLAY.stdout.txt').write_text(r.stdout);(s/'ISOLATED_REPLAY.stderr.txt').write_text(r.stderr)
log={'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'cwd':str(s),'exit_code':r.returncode,'pre_run_files':pre,'only_declared_inputs_scripts_manifest_and_replayer':True,'F036_final_and_intermediate_images_present_before_replay':False,'network_used':False,'new_generation_calls':0}
if r.returncode==0:
 output=s/'output/tree/astra_s08_first_mother_20261018_1433/F036_color_final/candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png';log['output_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
 if args.verify_against:
  import numpy as np
  from PIL import Image
  oracle=args.verify_against.resolve();a=np.array(Image.open(output).convert('RGBA'));b=np.array(Image.open(oracle).convert('RGBA'));assert a.shape==b.shape;log['post_process_external_oracle_comparison']={'different_RGBA_pixels':int(np.any(a!=b,2).sum()),'max_channel_error':int(np.abs(a.astype(int)-b.astype(int)).max()),'PNG_bytes_identical':output.read_bytes()==oracle.read_bytes(),'expected_sha256':hashlib.sha256(oracle.read_bytes()).hexdigest(),'actual_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(s/'ISOLATED_REPLAY_LOG.json').write_text(json.dumps(log,indent=2)+'\n');print(json.dumps(log,indent=2));sys.exit(r.returncode)
