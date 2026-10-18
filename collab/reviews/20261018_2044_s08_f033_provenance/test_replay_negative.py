from pathlib import Path
import json,shutil,subprocess,sys,tempfile
P=Path(__file__).resolve().parent;m=json.loads((P/'REPLAY_DEPENDENCIES.json').read_text());results=[]
base=Path(tempfile.mkdtemp(prefix='astra_f033_negative_'));files=['replay_f033.py','REPLAY_DEPENDENCIES.json']+[e['path'] for e in m['inputs']]
def case(name,mutate,extra=()):
 t=base/name;t.mkdir()
 for rel in files:
  d=t/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/rel,d)
 mutate(t);res=subprocess.run([sys.executable,str(t/'replay_f033.py'),'--out',str(t/'output'),*map(str,extra)],capture_output=True,text=True)
 results.append({'case':name,'exit_code':res.returncode,'failed_as_required':res.returncode!=0,'stderr_tail':res.stderr[-2000:]});assert res.returncode!=0,name
case('undeclared_final_read_denied',lambda t:None,['--probe-read',P/'final/S08_F033_whole_turn_same_raw_final_color_RGBA.png'])
case('tampered_raw_rejected',lambda t:(t/m['inputs'][-1]['path']).write_bytes((t/m['inputs'][-1]['path']).read_bytes()+b'X'))
case('missing_original_source_rejected',lambda t:(t/m['inputs'][0]['path']).unlink())
case('existing_output_not_overwritten',lambda t:(t/'output').mkdir())
assert 'Undeclared read:' in results[0]['stderr_tail'];assert 'AssertionError: raw' in results[1]['stderr_tail'];assert 'FileNotFoundError' in results[2]['stderr_tail'];assert 'Refusing to overwrite' in results[3]['stderr_tail']
(P/'REPLAY_NEGATIVE_TESTS.json').write_text(json.dumps({'status':'PASS_ALL_NEGATIVE_TESTS','new_image_generation_calls':0,'external_writes':0,'cases':results},indent=2)+'\n');print(json.dumps(results,indent=2))
