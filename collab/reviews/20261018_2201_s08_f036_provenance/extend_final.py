from pathlib import Path
import hashlib,json,shutil,datetime
P=Path(__file__).resolve().parent;R=P.parent/'astra_s08_first_mother_20261018_1433';m=json.loads((P/'REPLAY_DEPENDENCIES.json').read_text());sm=json.loads((P/'SOURCE_MANIFEST.json').read_text());records={e['path']:e for e in sm['files']}
def hs(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'bytes':len(b)}
def cp(src,rel,role):
 d=P/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,d);assert src.read_bytes()==d.read_bytes();e={'path':rel,'original_path':str(src),'role':role,**hs(d)};records[rel]=e;return e
for name in ['EXCLUDE_near_archive_old_blue_collar_NOT_HAND.png','EXTRA483_original033_body_box_fringe.png']:
 rel='F036_box_layer_source_diagnostic/'+name;e=cp(R/rel,rel,'explicit_author_final_archive_and_layer_correction_mask');m['inputs']=[x for x in m['inputs'] if x['path']!=rel];m['inputs'].append({'path':rel,'target':rel,**hs(P/rel)})
for folder in ['F036_FINAL_LOCKED','F036_LAYER_PARTITION']:
 for q in sorted((R/folder).iterdir()):
  if q.is_file() and q.suffix in ['.py','.json','.js']:cp(q,str(q.relative_to(R)),'author_final_corrected_original_source_or_contract')
 for q in sorted((R/folder).rglob('*.png')):
  if 'qa' not in q.parts and 'history' not in str(q):m['expected'][str(q.relative_to(R))]=hs(q)['sha256']
for rel in ['F036_FINAL_LOCKED/seal.py','F036_LAYER_PARTITION/build_partition.py']:
 m['scripts']=[x for x in m['scripts'] if x['path']!=rel];m['scripts'].append({'path':rel,'target':rel,**hs(P/rel)})
rel='F036_box_layer_source_diagnostic/source_checks.json';cp(R/rel,rel,'original_483_fringe_ownership_diagnostic')
for q in sorted((R/'F036_color_final/geometry').glob('*.json')):cp(q,str(q.relative_to(R)),'unchanged_original_material_diagnostic')
m['final_seal_and_partition']='Corrected archive53 old blue collar exclusion and runtime box1665 with483 original033 fringe retained in body; independent visual approval is not inferred by this replay.'
m['scope']='Deterministic same-call17-raw postprocessing, all five references, corrected independent-hand archive and three exclusive layers from explicit upstream033/000/canvas inputs and two author correction masks. No F036 final/intermediate image as input. Frozen actual registration applied.'
(P/'REPLAY_DEPENDENCIES.json').write_text(json.dumps(m,indent=2)+'\n');sm['files']=list(records.values());sm['final_correction_captured_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/'SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2)+'\n')
print(json.dumps({'replay_inputs':len(m['inputs']),'replay_scripts':len(m['scripts']),'expected_outputs':len(m['expected'])},indent=2))
