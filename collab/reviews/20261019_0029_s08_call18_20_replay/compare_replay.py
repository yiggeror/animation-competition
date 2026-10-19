from pathlib import Path
import hashlib,json,collections
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;W=B/'worktree';R=Path('/workspace/scratch/f060b5601755/astra_s08_first_mother_20261018_1433');P=Path('/workspace/scratch/f060b5601755/astra_s08_recent_sources_20261018_2355');PREFIX='collab/reviews/20261018_2355_s08_call18_20_provenance/'
rows=json.loads((B/'reports/EXPECTED_ARCHIVED_ROWS.json').read_text());byrel={x['path'][len(PREFIX):]:x for x in rows};seed=json.loads((B/'reports/SEED_MANIFEST.json').read_text());seedpaths={s['path'] for s in seed['seed_files']}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audits=[json.loads(p.read_text()) for p in sorted((B/'reports').glob('*_IO_AUDIT.json'))];written=set();reads=set()
for a in audits:
 for x in a['worktree_file_operations']:(written if x['action']=='write' else reads).add(x['path'])
comparisons=[];digestmap={}
for rel in sorted(written):
 p=W/rel
 if not p.is_file():continue
 original=R/rel;expected_row=byrel.get(rel);e={'path':rel,'replayed_sha256':sha(p),'bytes':p.stat().st_size,'expected_reference':'archived ROWS in committed source bundle' if expected_row else 'existing same-stage local output, outside minimal archive'}
 if original.is_file():
  e['original_source_sha256']=sha(original);e['expected_sha256']=expected_row['sha256'] if expected_row else e['original_source_sha256'];e['exact_sha_match']=e['replayed_sha256']==e['expected_sha256'];e['original_matches_archived_row']=None if expected_row is None else e['original_source_sha256']==expected_row['sha256'];digestmap[e['replayed_sha256']]=e['expected_sha256']
  if p.suffix.lower()=='.png' and not e['exact_sha_match']:
   aa=np.array(Image.open(p));bb=np.array(Image.open(original));e['pixel_shape_equal']=aa.shape==bb.shape
   if aa.shape==bb.shape:e['different_pixels']=int(np.any(aa!=bb,axis=2).sum()) if aa.ndim==3 else int((aa!=bb).sum());e['max_channel_difference']=int(np.max(np.abs(aa.astype(int)-bb.astype(int))))
 else:e.update(expected_sha256=None,exact_sha_match=None,note='No matching historical local output found; not fabricated.')
 comparisons.append(e)

def diff(a,b,path='$'):
 out=[]
 if type(a)!=type(b):return [{'path':path,'expected':a,'actual':b}]
 if isinstance(a,dict):
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append({'path':path+'.'+k,'expected':a.get(k,'<missing>'),'actual':b.get(k,'<missing>')})
   else:out+=diff(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):out.append({'path':path+'.length','expected':len(a),'actual':len(b)})
  for i,(x,y) in enumerate(zip(a,b)):out+=diff(x,y,f'{path}[{i}]')
 elif a!=b:out.append({'path':path,'expected':a,'actual':b})
 return out

def normalize(x,hashes=False):
 if isinstance(x,str):
  x=x.replace(str(W),str(R));return digestmap.get(x,x) if hashes else x
 if isinstance(x,list):return [normalize(y,hashes) for y in x]
 if isinstance(x,dict):return {k:normalize(v,hashes) for k,v in x.items()}
 return x
for e in comparisons:
 if e['exact_sha_match'] is False and e['path'].endswith('.json'):
  old=json.loads((R/e['path']).read_text());new=json.loads((W/e['path']).read_text());d=diff(old,normalize(new))
  if not d:e['difference_class']='ROOT_PATH_REBASE_ONLY'
  else:
   dd=diff(old,normalize(new,True));e['difference_class']='ROOT_PATH_AND_REFERENCED_METADATA_HASH_REBASE_ONLY' if not dd else 'SUBSTANTIVE_METADATA_DIFFERENCE';e['normalized_json_differences']=dd if dd else d

# Sealed manifests legitimately include the SHA and byte length of path-rebased JSON.
# Normalize only entries whose referenced file independently proved root-path-only.
root_only={str(R/e['path']):e for e in comparisons if e.get('difference_class')=='ROOT_PATH_REBASE_ONLY'}
def normalize_manifest(x):
 if isinstance(x,list):return [normalize_manifest(v) for v in x]
 if isinstance(x,dict):
  z={k:normalize_manifest(v) for k,v in x.items()};ref=root_only.get(z.get('path',''))
  if ref and z.get('sha256')==ref['replayed_sha256'] and z.get('bytes')==ref['bytes']:
   z['sha256']=ref['expected_sha256'];z['bytes']=(R/ref['path']).stat().st_size
  return z
 if isinstance(x,str):return x.replace(str(W),str(R))
 return x
for e in comparisons:
 if e.get('difference_class')=='SUBSTANTIVE_METADATA_DIFFERENCE' and e['path'].endswith('/SEALED_MANIFEST.json'):
  old=json.loads((R/e['path']).read_text());new=json.loads((W/e['path']).read_text());dd=diff(old,normalize_manifest(new))
  if not dd:
   e['difference_class']='ROOT_PATH_AND_REFERENCED_METADATA_HASH_AND_SIZE_REBASE_ONLY'
   e['difference_explanation']='All remaining differences are manifest references to independently verified root-path-only JSON files, including their changed SHA256 and byte length.'
   e['normalized_json_differences']=[]
  else:e['normalized_json_differences']=dd

finals=[]
for f in ['F038','F041','F043']:
 p=W/f'{f}_FINAL_LOCKED'/f'S08_{f}_grandma_match_box_RGBA.png'
 if not p.exists():continue
 a=np.array(Image.open(p));ims=[Image.open(W/f'{f}_LAYER_PARTITION/frames'/f'{f}_{n}_original_pixels.png') for n in ['body_behind','table_box','forearms_elbows']];arrays=[np.array(x) for x in ims];reb=np.array(Image.alpha_composite(Image.alpha_composite(ims[0],ims[1]),ims[2]));out={'frame':f,'final_sha256':sha(p),'expected_sha256':byrel[str(p.relative_to(W))]['sha256'],'mother_exact':sha(p)==byrel[str(p.relative_to(W))]['sha256'],'RGBA_reconstruction_exact':bool(np.array_equal(reb,a)),'RGB_original_in_each_layer':all(np.array_equal(x[:,:,:3],a[:,:,:3]) for x in arrays),'exclusive_alpha':bool((sum((x[:,:,3]>0).astype(int) for x in arrays)<=1).all()),'alpha_sum_equal_final':bool(np.array_equal(sum(x[:,:,3].astype(int) for x in arrays),a[:,:,3])),'layers':[]}
 for n in ['body_behind','table_box','forearms_elbows']:
  lp=W/f'{f}_LAYER_PARTITION/frames'/f'{f}_{n}_original_pixels.png';rr=byrel[str(lp.relative_to(W))];out['layers'].append({'path':str(lp.relative_to(W)),'sha256':sha(lp),'expected_sha256':rr['sha256'],'exact':sha(lp)==rr['sha256']})
 finals.append(out)
original_changes=[]
for rel,row in byrel.items():
 if not Path(row['local']).is_relative_to(R):continue
 if sha(row['local'])!=row['sha256']:original_changes.append(rel)
actual_seed_reads=reads&seedpaths;derived_reads=reads-seedpaths;derived_before_seed_final=not any('_FINAL_LOCKED/' in p or '_LAYER_PARTITION/' in p for p in seedpaths if not p.startswith('F036_'))
report={'source_commit_as_reported_by_coordinator':'67dd8e34698a4bee2e5e7dfde72bc55170210d2b','executed_steps':len(audits),'all_steps_exit_zero':all(a['exit_code']==0 for a in audits),'blocked_operations':[x for a in audits for x in a['blocked_operations']],'only_two_root_literal_replacements':seed['root_only_script_patches'],'current_frame_final_or_candidate_preseeded':not derived_before_seed_final,'source_original_changes_after_replay':original_changes,'network_or_repository_operations':0,'finals':finals,'output_summary':dict(collections.Counter('EXACT' if e['exact_sha_match'] else e.get('difference_class','MISSING_EXPECTED_OR_PIXEL_MISMATCH') for e in comparisons)),'generated_outputs':comparisons,'freshly_generated_paths':sorted(written),'artifact_reads':sorted(reads),'unseeded_derived_read_paths':sorted(derived_reads)}
(B/'reports/REPLAY_FULL_COMPARISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
summary={k:report[k] for k in ['executed_steps','all_steps_exit_zero','blocked_operations','current_frame_final_or_candidate_preseeded','source_original_changes_after_replay','network_or_repository_operations','output_summary']};summary['final_mothers_exact']=len(finals)==3 and all(x['mother_exact'] for x in finals);summary['nine_layer_hashes_exact']=sum(len(x['layers']) for x in finals)==9 and all(y['exact'] for x in finals for y in x['layers']);summary['three_RGBA_reconstructions_exact']=len(finals)==3 and all(x['RGBA_reconstruction_exact'] for x in finals);summary['substantive_differences']=[e for e in comparisons if e['exact_sha_match'] is False and e.get('difference_class') not in ['ROOT_PATH_REBASE_ONLY','ROOT_PATH_AND_REFERENCED_METADATA_HASH_REBASE_ONLY','ROOT_PATH_AND_REFERENCED_METADATA_HASH_AND_SIZE_REBASE_ONLY']]
(B/'reports/REPLAY_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
