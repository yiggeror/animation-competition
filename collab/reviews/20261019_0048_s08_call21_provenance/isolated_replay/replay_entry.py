from pathlib import Path
import json,hashlib,shlex,shutil,sys,subprocess,difflib,time,platform,importlib.metadata
B=Path(__file__).resolve().parent;W=B/'worktree';P=B.parent/'astra_s08_call21_sources_20261019_0048';OLD=B.parent/'astra_s08_first_mother_20261018_1433'
GUARD_SOURCE="from pathlib import Path\nimport sys,os,json,runpy,traceback,time\nsys.dont_write_bytecode=True\nB=Path(__file__).resolve().parent;W=B/'worktree';OLD=Path('/workspace/scratch/f060b5601755/astra_s08_first_mother_20261018_1433')\nstep=sys.argv[1];args=sys.argv[2:];target=W/args[0];events=[];blocked=[];active=True\n\ndef within(p,r):\n try:return Path(p).resolve().is_relative_to(r)\n except (TypeError,ValueError):return False\n\ndef audit(event,args):\n if not active:return\n if event.startswith('socket.') or event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:\n  blocked.append({'event':event,'reason':'No network or process spawning permitted inside source replay'});raise RuntimeError(blocked[-1]['reason'])\n if event=='open':\n  path=args[0]\n  if isinstance(path,int):return\n  mode=args[1];flags=args[2]\n  if within(path,OLD):\n   blocked.append({'event':event,'path':str(path),'reason':'Artist-tree access forbidden after materialization'});raise RuntimeError(blocked[-1]['reason'])\n  write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))\n  if write and not within(path,B):\n   blocked.append({'event':event,'path':str(path),'reason':'Write outside isolated replay root forbidden'});raise RuntimeError(blocked[-1]['reason'])\n  if within(path,W):events.append({'action':'write' if write else 'read','path':str(Path(path).resolve().relative_to(W))})\n if event in ['os.listdir','os.scandir'] and args and within(args[0],OLD):\n  blocked.append({'event':event,'path':str(args[0]),'reason':'Artist-tree directory traversal forbidden'});raise RuntimeError(blocked[-1]['reason'])\nsys.addaudithook(audit)\nsys.argv=[str(target)]+args[1:];os.chdir(W);start=time.monotonic();error=None;code=0\ntry:runpy.run_path(str(target),run_name='__main__')\nexcept BaseException as e:\n code=1;error=repr(e);traceback.print_exc()\nfinally:\n active=False\n uniq={}\n for e in events:uniq[(e['action'],e['path'])]=e\n (B/'reports'/f'{step}_IO_AUDIT.json').write_text(json.dumps({'step':step,'script':str(target.relative_to(W)),'arguments':sys.argv[1:],'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3),'error':error,'blocked_operations':blocked,'worktree_file_operations':sorted(uniq.values(),key=lambda x:(x['path'],x['action']))},indent=2)+'\\n')\nsys.exit(code)\n"
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def prepare():
 assert not W.exists(),'Use a new empty replay directory; never reseed an existing replay.'
 (B/'run_one_guarded.py').write_text(GUARD_SOURCE)
 for p in [W,B/'logs',B/'reports',B/'original_scripts']:p.mkdir(parents=True,exist_ok=True)
 assert H(P/'ROWS.json')=='ce829e13c6701ae4696723f5fca558dee0e5cb9f5d899a07a3d24a4f8ad9cf87'
 seeds=json.loads((P/'REPLAY_SEED_AND_CLOSURE.json').read_text())['seed_files'];recipe=json.loads((P/'REPLAY_RECIPE.json').read_text());records=[];patches=[]
 for s in seeds:
  data=Path(s['local']).read_bytes();assert hashlib.sha256(data).hexdigest()==s['sha256'],s['source_relative_path']
  rel=s['source_relative_path'];dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if rel.endswith('.py'):
   orig=B/'original_scripts'/rel;orig.parent.mkdir(parents=True,exist_ok=True);orig.write_bytes(data)
  if rel=='F046_same_raw_geometry_diagnostic/validate_v10_geometry_union.py':
   before=data.decode();assert before.count(str(OLD))==1;after=before.replace(str(OLD),str(W));data=after.encode();patches.append({'path':rel,'type':'sole_absolute_root_literal_only','source_sha256':s['sha256'],'copy_sha256':hashlib.sha256(data).hexdigest(),'unified_diff':''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='original/'+rel,tofile='isolated/'+rel))})
  dst.write_bytes(data);records.append({**s,'isolated_sha256':H(dst)})
 # prepare_clear233.py was originally a one-off and expects these EMPTY output folders.
 scaff=['F046_old_air_semantic_candidate/'+s for s in ['candidates','masks','frames','geometry','qa']]
 for s in scaff:(W/s).mkdir(parents=True,exist_ok=True)
 assert not (W/'F046_FINAL_LOCKED').exists() and not (W/'F046_LAYER_PARTITION').exists()
 plan={'source_rows_sha256':H(P/'ROWS.json'),'commands':[shlex.split(c)[1:] for c in recipe['ordered_commands']],'seeds':records,'root_only_patches':patches,'empty_output_scaffolding':scaff,'current_frame_outputs_seeded':False,'oracle_image_reads_before_processing':False,'expected_final_sha256':recipe['expectations']['final_sha256'],'expected_layers':recipe['expectations']['final_layer_sha256'],'environment':{'python':platform.python_version(),**{x:importlib.metadata.version(x) for x in ['numpy','scipy','Pillow']}}};save(B/'reports/PLAN.json',plan)
 print(json.dumps({'prepared_seed_files':len(records),'commands':len(plan['commands']),'root_only_patches':len(patches),'current_outputs_seeded':0}),flush=True)
def run():
 plan=json.loads((B/'reports/PLAN.json').read_text());rows=[]
 for i,args in enumerate(plan['commands'],1):
  tag=f'{i:02d}_{Path(args[0]).stem}';log=B/'logs'/f'{tag}.log';start=time.monotonic()
  with log.open('w') as out:p=subprocess.run([sys.executable,'-B',str(B/'run_one_guarded.py'),tag,*args],stdout=out,stderr=subprocess.STDOUT,cwd=W,timeout=300)
  entry={'step':i,'tag':tag,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-start,3),'log':str(log.relative_to(B)),'log_sha256':H(log)};rows.append(entry);print(json.dumps(entry),flush=True);save(B/'reports/RUN.json',rows)
  if p.returncode:
   print(log.read_text()[-5000:],flush=True);return 1
 print(json.dumps({'final_sha256':H(W/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png'),'exact_expected':H(W/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png')==plan['expected_final_sha256']}),flush=True);return 0
def compare():
 from PIL import Image
 import numpy as np
 plan=json.loads((B/'reports/PLAN.json').read_text());runs=json.loads((B/'reports/RUN.json').read_text());assert len(runs)==9 and all(x['exit_code']==0 for x in runs),'Wait for all processing to exit before oracle reads.'
 seeds={r['source_relative_path'] for r in plan['seeds']};out=[];diffs=[];oracle={}
 def norm(x):
  if isinstance(x,str):return x.replace(str(W),str(OLD))
  if isinstance(x,list):return [norm(v) for v in x]
  if isinstance(x,dict):return {k:norm(v) for k,v in x.items()}
  return x
 def jd(a,b,path='$'):
  if type(a)!=type(b):return [{'field':path,'replay':a,'oracle':b}]
  if isinstance(a,dict):
   z=[]
   for k in sorted(set(a)|set(b)):
    if k not in a or k not in b:z.append({'field':path+'.'+k,'replay':a.get(k,'<missing>'),'oracle':b.get(k,'<missing>')})
    else:z+=jd(a[k],b[k],path+'.'+k)
   return z
  if isinstance(a,list):
   if len(a)!=len(b):return [{'field':path,'replay_length':len(a),'oracle_length':len(b),'replay':a,'oracle':b}]
   return [d for i,(x,y) in enumerate(zip(a,b)) for d in jd(x,y,path+f'[{i}]')]
  return [] if a==b else [{'field':path,'replay':a,'oracle':b}]
 for p in sorted(W.rglob('*')):
  if not p.is_file():continue
  rel=str(p.relative_to(W))
  if rel in seeds:continue
  q=OLD/rel;b=p.read_bytes();row={'path':rel,'replay_sha256':hashlib.sha256(b).hexdigest(),'replay_bytes':len(b),'oracle_exists':q.is_file()}
  if q.is_file():
   qb=q.read_bytes();row.update(oracle_sha256=hashlib.sha256(qb).hexdigest(),oracle_bytes=len(qb),byte_identical=b==qb);oracle[rel]={'sha256':row['oracle_sha256'],'bytes':len(qb)}
   if b!=qb:
    d={'path':rel,'replay_sha256':row['replay_sha256'],'oracle_sha256':row['oracle_sha256']}
    if p.suffix.lower()=='.png':
     a=np.array(Image.open(p));o=np.array(Image.open(q));eq=a.shape==o.shape and np.array_equal(a,o);d.update(kind='PNG_ENCODING_ONLY' if eq else 'PIXEL_DIFFERENCE',array_equal=eq,replay_shape=list(a.shape),oracle_shape=list(o.shape))
     if a.shape==o.shape:d['changed_pixels']=int(np.any(a!=o,axis=-1).sum()) if a.ndim>2 else int((a!=o).sum())
    elif p.suffix.lower()=='.json':
     a=json.loads(b);o=json.loads(qb);n=norm(a);d.update(kind='JSON_ABSOLUTE_ROOT_ONLY' if n==o else 'JSON_METADATA_DIFFERENCE',normalized_field_differences=jd(n,o))
    else:d.update(kind='NON_PNG_BYTE_DIFFERENCE',text_root_normalization_equal=norm(b.decode())==qb.decode())
    diffs.append(d)
  else:diffs.append({'path':rel,'kind':'GENERATED_OUTPUT_WITHOUT_AUTHOR_COUNTERPART'})
  out.append(row)
 # Disentangle manifest inventory, referenced digest propagation, and actual metadata changes.
 byrel={r['path']:r for r in out}
 for d in diffs:
  if d['kind']!='JSON_METADATA_DIFFERENCE' or not d['path'].endswith('SEALED_MANIFEST.json'):continue
  p=W/d['path'];q=OLD/d['path'];a=norm(json.loads(p.read_text()));o=json.loads(q.read_text());af={x['path']:x for x in a.pop('files',[])};of={x['path']:x for x in o.pop('files',[])};details=[]
  for name in sorted(set(af)&set(of)):
   x=af[name];y=of[name]
   if x==y:continue
   rel=name.removeprefix(str(OLD)+'/');lookuprel=('F046_handoff_preparation/history_a6_before233/'+Path(rel).name) if 'history_a6_before233/' in d['path'] else rel;z=byrel.get(lookuprel);expected=(z is not None and x.get('sha256')==z['replay_sha256'] and y.get('sha256')==z.get('oracle_sha256') and x.get('bytes')==z['replay_bytes'] and y.get('bytes')==z.get('oracle_bytes'))
   details.append({'path':rel,'referenced_file_digest_and_size_propagation':expected,'replay':x,'oracle':y})
  d['manifest_analysis']={'non_inventory_fields':jd(a,o),'only_in_replay':[x.removeprefix(str(OLD)+'/') for x in sorted(set(af)-set(of))],'only_in_author':[x.removeprefix(str(OLD)+'/') for x in sorted(set(of)-set(af))],'different_entries':details}
  d.pop('normalized_field_differences',None);d['kind']='MANIFEST_PATH_AND_REFERENCED_DIGEST_ONLY' if not d['manifest_analysis']['non_inventory_fields'] and not d['manifest_analysis']['only_in_replay'] and not d['manifest_analysis']['only_in_author'] and all(x['referenced_file_digest_and_size_propagation'] for x in details) else 'MANIFEST_OTHER_DIFFERENCE'
 mother=W/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png';a=np.array(Image.open(mother));paths=[W/'F046_LAYER_PARTITION/frames'/n for n in ['F046_body_behind_original_pixels.png','F046_table_box_original_pixels.png','F046_forearms_elbows_original_pixels.png']];layers=[np.array(Image.open(p)) for p in paths];reb=Image.alpha_composite(Image.alpha_composite(Image.fromarray(layers[0]),Image.fromarray(layers[1])),Image.fromarray(layers[2]));layercheck={'final_expected_hash_exact':H(mother)==plan['expected_final_sha256'],'three_layers_expected_hash_exact':all(H(p)==plan['expected_layers'][p.name] for p in paths),'mutually_exclusive_alpha':bool((sum(z[:,:,3]>0 for z in layers)).max()==1),'alpha_sum_exact':bool(np.array_equal(sum(z[:,:,3].astype(int) for z in layers),a[:,:,3])),'all_layer_RGB_original':all(np.array_equal(z[:,:,:3],a[:,:,:3]) for z in layers),'RGBA_recomposition_exact':bool(np.array_equal(np.array(reb),a))};assert all(layercheck.values()),layercheck
 # Verify every frozen source row again, after all processing and oracle comparison.
 source_rows=json.loads((P/'ROWS.json').read_text());changed=[r['path'] for r in source_rows if H(Path(r['local']))!=r['sha256']];assert not changed,changed
 audits=[json.loads((B/'reports'/f"{r['tag']}_IO_AUDIT.json").read_text()) for r in runs];assert not any(a['blocked_operations'] for a in audits)
 review={'status':'PASS_NINE_STEP_ISOLATED_REPLAY_EXACT_FINAL_AND_LAYERS','processing_steps':9,'all_exit_zero':True,'seed_files':len(seeds),'root_only_script_changes':len(plan['root_only_patches']),'outputs':len(out),'byte_identical_outputs':sum(r.get('byte_identical',False) for r in out),'PNG_outputs':sum(r['path'].endswith('.png') for r in out),'byte_identical_PNGs':sum(r['path'].endswith('.png') and r.get('byte_identical',False) for r in out),'pixel_differences':sum(d['kind']=='PIXEL_DIFFERENCE' for d in diffs),'root_only_JSON_differences':sum(d['kind']=='JSON_ABSOLUTE_ROOT_ONLY' for d in diffs),'manifest_path_digest_differences':sum(d['kind']=='MANIFEST_PATH_AND_REFERENCED_DIGEST_ONLY' for d in diffs),'manifest_inventory_differences':sum(bool(d.get('manifest_analysis',{}).get('only_in_author') or d.get('manifest_analysis',{}).get('only_in_replay')) for d in diffs),'substantive_character_or_layer_differences':0,'current_frame_output_seeds':0,'author_tree_changes':changed,'guard_blocked_operations':[],'oracle_read_phase':'Only after all nine child processes exited successfully. No oracle PNG or final/intermediate output was seeded.','layer_validation':layercheck,'differences':diffs,'all_output_comparisons':out}
 save(B/'COMPARISON.json',review)
 evidence={'plan':plan,'final_reproducible_entry_sha256':H(B/'replay_entry.py'),'entry_packaging_note':'After execution, the unchanged guard source and post-run compare function were embedded into the entry so four proof files suffice. The nine author scripts, one root-only patch, commands, guarded execution and logs were unchanged.','guard_sha256':H(B/'run_one_guarded.py'),'executions':[{**r,'stdout_stderr_complete':(B/r['log']).read_text(),'io_audit':a} for r,a in zip(runs,audits)],'guard_source':(B/'run_one_guarded.py').read_text(),'original_scripts_local_snapshot':'original_scripts/ contains unchanged copies; complete original scripts are already in the sealed source archive; the sole root replacement is included verbatim in plan.root_only_patches.'};save(B/'RUN_EVIDENCE.json',evidence)
 print(json.dumps({k:v for k,v in review.items() if k not in ['differences','all_output_comparisons']},indent=2),flush=True)

if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='prepare':prepare()
 elif mode=='run':sys.exit(run())
 elif mode=='compare':compare()
