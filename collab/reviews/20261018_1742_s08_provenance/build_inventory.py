from pathlib import Path
from collections import defaultdict
import json,hashlib,csv,shutil
ROOT=Path('/workspace/scratch/f060b5601755');OUT=Path(__file__).resolve().parent
BASE=ROOT/'astra_s08_first_mother_20261018_1433'
MANIFESTS=[BASE/'S08_FIRST5_PROVENANCE/manifest.json',BASE/'S08_EYES_CALLS06_07_PROVENANCE/manifest.json']
PREFIX='collab/reviews/20261018_1742_s08_provenance'
OBJ=OUT/'objects';OBJ.mkdir(exist_ok=True);(OUT/'original_manifests').mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
entries=[]; issues=[]; calls=[]; source_manifests=[]
def category(ptr):
 if '/calls/' in ptr:
  if '/actual_inputs/' in ptr:return 'batch02_actual_inputs_masks_scripts'
  return 'batch01_raw_request_prompt'
 if any(x in ptr for x in ['/final_adoptions/','/frame_outputs/']):return 'batch03_output_anchors_optional'
 if ptr=='/prior_first5_manifest':return 'batch00_original_manifests'
 return 'batch02_actual_inputs_masks_scripts'
def walk(v,ptr,mf):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():
   p=Path(v['path']); item={'source_path':str(p),'expected_sha256':v['sha256'],'expected_bytes':v['bytes'],'source_manifest':str(mf),'json_pointer':ptr,'role':v.get('role'), 'category':category(ptr)}
   if not p.is_file():item.update(status='BLOCKED_MISSING',target=None);issues.append(item)
   else:
    data=p.read_bytes();item.update(bytes=len(data),sha256=sha(data),git_blob_sha1=blob(data))
    item['status']='VERIFIED' if item['sha256']==item['expected_sha256'] and item['bytes']==item['expected_bytes'] else 'BLOCKED_MISMATCH'
    if item['status']!='VERIFIED':item['target']=None;issues.append(item)
   entries.append(item);return
  for k,w in v.items():walk(w,ptr+'/'+k,mf)
 elif isinstance(v,list):
  for k,w in enumerate(v):walk(w,ptr+'/'+str(k),mf)
for mf in MANIFESTS:
 data=mf.read_bytes();m=json.loads(data)
 descriptor={'source_path':str(mf),'expected_sha256':sha(data),'expected_bytes':len(data),'source_manifest':str(mf),'json_pointer':'','role':'immutable_original_manifest','category':'batch00_original_manifests','bytes':len(data),'sha256':sha(data),'git_blob_sha1':blob(data),'status':'VERIFIED'}
 entries.append(descriptor);source_manifests.append(dict(descriptor))
 shutil.copyfile(mf,OUT/'original_manifests'/(mf.parent.name+'_manifest.json'))
 walk(m,'',mf)
 for c in m['calls']:
  request=Path(c['request']['path']);prompt_desc=c.get('actual_prompt_exact_text',c.get('actual_prompt'));prompt=Path(prompt_desc['path'])
  request_data=json.loads(request.read_bytes()); prompt_data=prompt.read_bytes();request_prompt=request_data['prompt'].encode('utf-8')
  check={'call_number':c['call_number'],'purpose':c['purpose'],'source_manifest':str(mf),'raw_source':c['raw']['path'],'request_source':str(request),'prompt_source':str(prompt),'prompt_bytes_exactly_match_request_prompt_utf8':prompt_data==request_prompt,'actual_inputs_match_request_order':request_data['referenced_image_paths']==[x['path'] for x in c['actual_inputs']],'native_transparent_background':request_data.get('transparent_background'),'actual_inputs_count':len(c['actual_inputs'])}
  if not check['prompt_bytes_exactly_match_request_prompt_utf8'] or not check['actual_inputs_match_request_order']:issues.append({'status':'BLOCKED_CALL_CONTENT_MISMATCH',**check})
  calls.append(check)
groups=defaultdict(list)
for e in entries:
 if e['status']=='VERIFIED':groups[e['sha256']].append(e)
order={'batch01_raw_request_prompt':0,'batch00_original_manifests':1,'batch02_actual_inputs_masks_scripts':2,'batch03_output_anchors_optional':3}
objects=[]
for key,group in sorted(groups.items()):
 exts=sorted({Path(e['source_path']).suffix.lower().lstrip('.') or 'bin' for e in group});ext=exts[0];name=key+'.'+ext;target=PREFIX+'/objects/'+name
 source=Path(group[0]['source_path']);dest=OBJ/name
 shutil.copyfile(source,dest);data=dest.read_bytes();assert sha(data)==key
 priority=min((e['category'] for e in group),key=order.get)
 obj={'sha256':key,'git_blob_sha1':blob(data),'bytes':len(data),'extension':ext,'source_paths':sorted(set(e['source_path'] for e in group)),'source_path_preferred':str(source),'staged_absolute_path':str(dest),'target':target,'upload_batch':priority,'roles':sorted(set(e['role'] for e in group if e['role'])),'categories':sorted(set(e['category'] for e in group)),'source_occurrences':[{'source_manifest':e['source_manifest'],'json_pointer':e['json_pointer'],'role':e['role']} for e in group]}
 objects.append(obj)
 for e in group:e['target']=target;e['staged_absolute_path']=str(dest)
paths=[]
for source in sorted(set(e['source_path'] for e in entries)):
 es=[e for e in entries if e['source_path']==source];valid=[e for e in es if e['status']=='VERIFIED']; blocked=[e for e in es if e['status']!='VERIFIED']
 if blocked:
  paths.append({'source_path':source,'status':'BLOCKED','issues':blocked,'target':None});continue
 e=valid[0];assert len({x['sha256'] for x in valid})==1
 paths.append({k:e[k] for k in ['source_path','status','bytes','sha256','git_blob_sha1','target','staged_absolute_path']}|{'categories':sorted(set(x['category'] for x in valid)),'roles':sorted(set(x['role'] for x in valid if x['role']))})
batches=[]
for cat in order:
 os=[o for o in objects if o['upload_batch']==cat]
 batches.append({'batch':cat,'unique_objects':len(os),'bytes':sum(o['bytes'] for o in os),'sha256s':[o['sha256'] for o in os]})
summary={'status':'READY_LOCAL_UNCHANGED_BYTES' if not issues else 'PARTIAL_BLOCKED_SEE_ISSUES','scope':'All original file descriptors in the two specified provenance manifests, plus the manifests themselves. No inferred script dependency closure; no generated/repaired image and no upload. Output anchors are optional separate batch.','target_prefix':PREFIX,'calls':7,'call_numbers':[c['call_number'] for c in calls],'all_request_prompts_and_ordered_inputs_exact':all(c['prompt_bytes_exactly_match_request_prompt_utf8'] and c['actual_inputs_match_request_order'] for c in calls),'descriptor_occurrences_including_manifests':len(entries),'unique_source_paths':len(paths),'unique_objects_by_sha256':len(objects),'total_unique_bytes':sum(o['bytes'] for o in objects),'deduplicated_source_path_count':len(paths)-len(objects),'blocked_count':len(issues),'batches':batches}
for name,data in [('OBJECTS.json',objects),('PATH_TO_TARGET.json',paths),('MANIFEST_OCCURRENCES.json',entries),('CALLS_REQUEST_PROMPT_CHECKS.json',calls),('ORIGINAL_MANIFESTS.json',source_manifests),('BLOCKED_FILES.json',issues),('SUMMARY.json',summary)]:
 (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
with (OUT/'PATH_TO_TARGET.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t');keys=['source_path','status','bytes','sha256','git_blob_sha1','target','staged_absolute_path'];w.writerow(keys)
 for p in paths:w.writerow([p.get(k,'') for k in keys])
for b in batches:
 selected=[o for o in objects if o['sha256'] in b['sha256s']]
 (OUT/(b['batch']+'.json')).write_text(json.dumps({'batch':b['batch'],'objects':selected,'unique_objects':b['unique_objects'],'bytes':b['bytes']},ensure_ascii=False,indent=2)+'\n')
for c in calls:
 c['raw_target']=next(p['target'] for p in paths if p['source_path']==c['raw_source']);c['request_target']=next(p['target'] for p in paths if p['source_path']==c['request_source']);c['prompt_target']=next(p['target'] for p in paths if p['source_path']==c['prompt_source'])
(OUT/'CALLS_REQUEST_PROMPT_CHECKS.json').write_text(json.dumps(calls,ensure_ascii=False,indent=2)+'\n')
(OUT/'objects_SHA256SUMS').write_text(''.join(o['sha256']+'  objects/'+Path(o['staged_absolute_path']).name+'\n' for o in objects))
(OUT/'objects_GIT_BLOB_SHA1SUMS').write_text(''.join(o['git_blob_sha1']+'  objects/'+Path(o['staged_absolute_path']).name+'\n' for o in objects))
print(json.dumps({k:v for k,v in summary.items() if k!='batches'},ensure_ascii=False,indent=2))
for b in batches:print(b['batch'],b['unique_objects'],b['bytes'],round(b['bytes']/1048576,6),'MiB')
if issues:print(json.dumps(issues,ensure_ascii=False,indent=2))
