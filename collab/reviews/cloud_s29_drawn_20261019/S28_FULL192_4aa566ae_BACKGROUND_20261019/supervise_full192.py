"""Detached supervisor for the user's fixed, unchanged real-frame renderer."""
from pathlib import Path
import subprocess,os,json,time,hashlib,urllib.request

SRC=Path('/workspace/s28-three-frame-20261019-76c44a19')
OUT=Path('/tmp/s28-full192')
OUT.mkdir(parents=True,exist_ok=True)
state={'supervisor_pid':os.getpid(),'source_executor_commit':'4aa566ae2714513ef54ae30bc403cf50dde5941c',
       'source_entry_commit':'8a86a552fba1a822aae0f27ca53e2b0defb4e392','source_worktree':str(SRC),
       'output':str(OUT),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
       'status':'STARTING','frames_requested':192,'real_frame_rendering_no_pose_cache':True}
def save():
    temp=OUT/'RUN_STATE.json.tmp';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(OUT/'RUN_STATE.json')
server=render=None
try:
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=SRC,text=True).strip()==state['source_executor_commit']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=SRC,text=True)
    assert not (OUT/'FRAME_SHA256.jsonl').exists(),'Existing ledger: no duplicate/overwrite'
    script=SRC/'collab/reviews/20261019_0930_s28_full192_actual/render_full192.cjs'
    state['exact_renderer_sha256']=hashlib.sha256(script.read_bytes()).hexdigest()
    server=subprocess.Popen(['python3','-m','http.server','8197','--bind','127.0.0.1'],cwd=SRC,stdin=subprocess.DEVNULL,stdout=(OUT/'HTTP8197.log').open('ab'),stderr=subprocess.STDOUT)
    state['http_pid']=server.pid;save()
    for _ in range(30):
        try:
            urllib.request.urlopen('http://127.0.0.1:8197/collab/reviews/20261019_0930_s28_full192_actual/preview.html',timeout=2).close();break
        except OSError:time.sleep(.2)
    else:raise RuntimeError('HTTP8197 did not become ready')
    env=dict(os.environ);env['S28_OUTPUT_DIR']=str(OUT)
    render=subprocess.Popen(['node',str(script)],cwd=SRC,env=env,stdin=subprocess.DEVNULL,stdout=(OUT/'RENDER_STDOUT.log').open('ab'),stderr=subprocess.STDOUT)
    state.update(renderer_pid=render.pid,status='RUNNING');save()
    code=render.wait();state.update(exit_code=code,status='FINISHED' if code==0 else 'FAILED')
except BaseException as e:
    state.update(status='FAILED',error=repr(e))
finally:
    if server is not None:
        server.terminate()
        try:server.wait(timeout=5)
        except subprocess.TimeoutExpired:server.kill()
    state['ended_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
