from pathlib import Path
import json,hashlib,shlex,sys,importlib.metadata
P=Path('/workspace/scratch/f060b5601755/astra_s08_recent_sources_20261018_2355')
B=Path('/workspace/scratch/f060b5601755/astra_s08_recent_replay_20261019_0029');W=B/'worktree'
assert not B.exists(),'Refuse reusing an existing replay workspace'
for d in [W,B/'logs',B/'reports']:d.mkdir(parents=True)
rows=json.loads((P/'ROWS.json').read_text());rp=json.loads((P/'REPLAY.json').read_text());prefix='collab/reviews/20261018_2355_s08_call18_20_provenance/'
byrel={x['path'][len(prefix):]:x for x in rows}
commands=[(st['frame'],shlex.split(cmd)[1:]) for st in rp['steps'] for cmd in st['ordered_commands_from_new_root']]
scripts={cmd[0] for _,cmd in commands}
release='F043_same_raw_aa_v2/masks/PROPOSED_RELEASE_old_near_brow_lower_highlight_AA_2rows.png'
seed=[];patches=[];original_root='/workspace/scratch/f060b5601755/astra_s08_first_mother_20261018_1433'
for rel,row in byrel.items():
 include=(any(rel.startswith(f'{f}_native_call') or rel.startswith(f'{f}_input_gate/') for f in ['F038','F041','F043']) or rel.startswith('F036_FINAL_LOCKED/') or rel in scripts or rel==release)
 if not include:continue
 data=Path(row['local']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'],rel+' has changed since archived manifest'
 dst=W/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if rel in ['F038_same_raw_semantic_v6/build.py','F041_same_raw_semantic_v7/build.py']:
  s=data.decode();assert s.count(original_root)==1;data=s.replace(original_root,str(W)).encode();patches.append({'path':rel,'change':'Replace sole absolute R root literal only','original':original_root,'replacement':str(W),'source_sha256':row['sha256'],'replay_copy_sha256':hashlib.sha256(data).hexdigest()})
 dst.write_bytes(data);seed.append({'path':rel,'source_local':row['local'],'source_sha256':row['sha256'],'replay_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
for d in ['F038_color_final','F041_color_candidate','F043_same_raw_final_v3']:
 for s in ['masks','candidates','geometry','qa']:(W/d/s).mkdir(parents=True,exist_ok=True)
assert not any((W/f'{f}_FINAL_LOCKED').exists() or (W/f'{f}_LAYER_PARTITION').exists() for f in ['F038','F041','F043'])
assert not any((W/d/'candidates').exists() for d in ['F038_returned_raw_nominal','F041_returned_raw_nominal','F043_same_raw_aa_v2'])
(B/'reports/SEED_MANIFEST.json').write_text(json.dumps({'original_rows_sha256':hashlib.sha256((P/'ROWS.json').read_bytes()).hexdigest(),'committed_source_reference':'67dd8e34698a4bee2e5e7dfde72bc55170210d2b (provided by coordinator; no repository read)','seed_files':seed,'root_only_script_patches':patches,'final_or_intermediate_candidate_images_seeded':False,'upstream_F036_files_seeded':True,'environment':{'python':sys.version.split()[0],**{n:importlib.metadata.version(n) for n in ['Pillow','numpy','scipy']}},'expected_environment':rp['dependency_environment']},ensure_ascii=False,indent=2)+'\n')
(B/'reports/PLAN.json').write_text(json.dumps({'worktree':str(W),'commands':commands,'expected_final_sha256':rp['expected_final_sha256']},indent=2)+'\n')
(B/'reports/EXPECTED_ARCHIVED_ROWS.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'replay_root':str(B),'seed_files':len(seed),'commands':len(commands),'source_root_replacements':len(patches),'seeded_current_finals':0}))
