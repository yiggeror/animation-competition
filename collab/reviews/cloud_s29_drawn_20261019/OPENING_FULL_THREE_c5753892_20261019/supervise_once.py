from pathlib import Path
import subprocess,os,json,datetime,socket,time,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[3]
OUT=Path('/tmp/opening-continuity-full')
SCRIPT='collab/reviews/20261019_1203_opening_full_gate/render_full_three.cjs'
FIXED='c57538925035118c0f8901fc2f22f478fbf803b4'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==FIXED
assert not OUT.exists(),'Existing output: refuse duplicate render'
s=socket.socket();s.bind(('127.0.0.1',8199));s.close()
state={'source_commit':FIXED,'started_utc':now(),'supervisor_pid':os.getpid(),'output_dir':str(OUT),'script':SCRIPT,'script_sha256':hashlib.sha256((ROOT/SCRIPT).read_bytes()).hexdigest(),'state':'STARTING','new_imagegen_calls':0,'reruns':0}
server=None;node=None
try:
 server=subprocess.Popen(['python3','-m','http.server','8199','--bind','127.0.0.1'],cwd=ROOT,stdout=(R/'http_actual.log').open('wb'),stderr=subprocess.STDOUT)
 for _ in range(100):
  try:
   with socket.create_connection(('127.0.0.1',8199),timeout=.1):break
  except OSError:time.sleep(.03)
 else:raise RuntimeError('HTTP8199 failed to start')
 env=os.environ.copy();env['OPENING_OUTPUT_DIR']=str(OUT)
 node=subprocess.Popen(['node',SCRIPT],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=(R/'render_actual.log').open('wb'),stderr=subprocess.STDOUT)
 state.update(state='RUNNING',node_pid=node.pid,http_pid=server.pid)
 (R/'RUN_STATE.json').write_text(json.dumps(state,indent=2)+'\n')
 code=node.wait();state.update(state='COMPLETED' if code==0 else 'FAILED',exit_code=code,finished_utc=now(),script_unchanged=hashlib.sha256((ROOT/SCRIPT).read_bytes()).hexdigest()==state['script_sha256'])
except BaseException as e:
 state.update(state='FAILED',error=repr(e),finished_utc=now())
finally:
 if node and node.poll() is None:node.terminate()
 if server and server.poll() is None:
  server.terminate()
  try:server.wait(timeout=5)
  except subprocess.TimeoutExpired:server.kill()
 state['http_server_stopped']=server is None or server.poll() is not None
 (R/'RUN_STATE.json').write_text(json.dumps(state,indent=2)+'\n')
