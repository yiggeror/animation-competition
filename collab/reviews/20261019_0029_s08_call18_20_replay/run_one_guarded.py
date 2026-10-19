from pathlib import Path
import sys,os,json,runpy,traceback,time
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;W=B/'worktree';OLD=Path('/workspace/scratch/f060b5601755/astra_s08_first_mother_20261018_1433')
step=sys.argv[1];args=sys.argv[2:];target=W/args[0];events=[];blocked=[];active=True

def within(p,r):
 try:return Path(p).resolve().is_relative_to(r)
 except (TypeError,ValueError):return False

def audit(event,args):
 if not active:return
 if event.startswith('socket.') or event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:
  blocked.append({'event':event,'reason':'No network or process spawning permitted inside source replay'});raise RuntimeError(blocked[-1]['reason'])
 if event=='open':
  path=args[0]
  if isinstance(path,int):return
  mode=args[1];flags=args[2]
  if within(path,OLD):
   blocked.append({'event':event,'path':str(path),'reason':'Artist-tree access forbidden after materialization'});raise RuntimeError(blocked[-1]['reason'])
  write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  if write and not within(path,B):
   blocked.append({'event':event,'path':str(path),'reason':'Write outside isolated replay root forbidden'});raise RuntimeError(blocked[-1]['reason'])
  if within(path,W):events.append({'action':'write' if write else 'read','path':str(Path(path).resolve().relative_to(W))})
 if event in ['os.listdir','os.scandir'] and args and within(args[0],OLD):
  blocked.append({'event':event,'path':str(args[0]),'reason':'Artist-tree directory traversal forbidden'});raise RuntimeError(blocked[-1]['reason'])
sys.addaudithook(audit)
sys.argv=[str(target)]+args[1:];os.chdir(W);start=time.monotonic();error=None;code=0
try:runpy.run_path(str(target),run_name='__main__')
except BaseException as e:
 code=1;error=repr(e);traceback.print_exc()
finally:
 active=False
 uniq={}
 for e in events:uniq[(e['action'],e['path'])]=e
 (B/'reports'/f'{step}_IO_AUDIT.json').write_text(json.dumps({'step':step,'script':str(target.relative_to(W)),'arguments':sys.argv[1:],'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3),'error':error,'blocked_operations':blocked,'worktree_file_operations':sorted(uniq.values(),key=lambda x:(x['path'],x['action']))},indent=2)+'\n')
sys.exit(code)
