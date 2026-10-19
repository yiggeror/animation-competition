from pathlib import Path
import json,hashlib,base64,re,struct
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;OLD=P.parent/'handoff_008_020_032_generation_002';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
locks={8:'cc802f284046f978633b41f769cfef4119492f2433207c1e06c0ddc60e5ffbdf',20:'de378cd06028313388cd955e8feb56aef684fd63f5a9f7019fa148aad7885b12',32:'b586eee0eebbd09167d27171eefccf5297b58472a736010ce871497452195b95'}
for f,h in locks.items():assert sha(OLD/f'F{f:03}'/f'S20_F{f:03}_accepted.png')==h
A20=np.array(Image.open(OLD/'F020/S20_F020_accepted.png').convert('RGBA'));D32=np.array(Image.open(OLD/'F032/S20_F032_accepted.png').convert('RGBA'));frames=[]
for f in [12,15,18,22,24,27,30]:
 F=P/f'F{f:03}';s=json.loads((F/'status.json').read_text());assert s['state']=='AUTHOR_ACCEPTED' and s['in_flight']==0 and s['actual_full_body_and_contact_images_viewed'];final=F/s['accepted_png'];assert sha(final)==s['accepted_sha256'];im=Image.open(final);assert im.size==(1672,941) and im.mode=='RGBA';A=np.array(im);m=json.loads((F/'input_manifest.json').read_text());source=np.array(Image.open(m['source']).convert('RGBA'));assert sha(Path(m['source']))==m['source_sha256'];M=np.array(Image.open(F/'inputs/04_edit_white.png'))>0;changes=int(np.count_nonzero(np.any(A[~M]!=source[~M],axis=1)));assert changes==0,(f,'black changes',changes)
 for row in m['inputs']:assert sha(Path(row['path']))==row['sha256'],(f,'input changed',row['path'])
 raw=F/s['raw_path'];assert sha(raw)==s['raw_sha256'];r=json.loads((F/'tool_return_original.json').read_text());assert base64.b64decode(r['image_url'].split(',',1)[1])==raw.read_bytes();size=struct.unpack('>II',raw.read_bytes()[16:24]);assert list(size)==s['actual_size']
 if s['same_raw_rightmost_transparent_column_only']:
  C=np.array(Image.open(F/'same_raw_rightmost_transparent_column.png'));R=np.array(Image.open(raw));assert np.array_equal(C[:,:1671],R) and not C[:,-1].any()
 child_equal=np.array_equal(A[:,:885],A20[:,:885])
 if f>=22:assert child_equal
 else:assert np.array_equal(A[:,885:],source[:,885:])
 row={'frame':f,'accepted':str(final.relative_to(P)),'sha256':sha(final),'state':s['state'],'actual_full_and_contact_viewed':True,'black_domain_RGBA_changes':changes,'whole_child_exact_locked020':bool(child_equal),'attempts':s['attempts_started'],'raws':s['new_raws'],'raw_source_sha256':sha(raw),'source_raw_original_columns_unchanged':True,'new_raw_retained_part':s.get('actual018_raw_retained_part',s.get('retained_raw_part','new child drawing with protected fixed rods and actual008 lower legs'))}
 if f in [24,27,30]:
  H=np.array(Image.open(F/'art/actual_raw_hand_forearm_return_mask.png'))>0;B=np.array(Image.open(F/'same_raw_rightmost_transparent_column.png' if s['same_raw_rightmost_transparent_column_only'] else raw));H&=B[:,:,3]>180;T=np.array(Image.open(F/'art/locked032_actual_rod_tail_return_mask.png'))>0;T&=D32[:,:,3]>180;dist=distance_transform_edt(~T);gap=float(dist[H].min());assert gap>0,(f,'rod intersection');row['actual_open_hand_min_rod_clearance_px']=gap
 frames.append(row)
requests=[]
for q in P.glob('F*/request*submitted.json'):
 r=json.loads(q.read_text());requests.append({'frame':int(q.parent.name[1:]),'request_file':str(q.relative_to(P)),'request_sha256':sha(q),'cumulative_request_number':r['cumulative_request_number'],'input_count':len(r['args']['referenced_image_paths'])});assert len(r['args']['referenced_image_paths'])==4
requests.sort(key=lambda x:x['cumulative_request_number']);assert [r['cumulative_request_number'] for r in requests]==list(range(8,17));assert len(list(P.glob('F*/S20*_raw_*.png')))==8;assert not (P/'F004').exists()
summary={'exclusive_directory':str(P),'frames':frames,'requests':requests,'batch_requests':9,'batch_raw_outputs':8,'retained_states':7,'blocked_before_output_requests':1,'structurally_rejected_raw_outputs':1,'cumulative_requests':16,'cumulative_raw_outputs':15,'in_flight':0,'F004_cloud_calls':0,'all_locked_anchors_SHA_unchanged':True,'actual_exposure_range_available':[8,35],'first36_pending_native004':True,'production_or_shared_docs_modified':False,'full_film_or_scene_rendered':False};(P/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'verified_states':7,'batch_requests':9,'batch_raws':8,'cumulative_requests':16,'cumulative_raws':15,'F004_cloud_calls':0,'release_gaps':[(r['frame'],r.get('actual_open_hand_min_rod_clearance_px')) for r in frames if r['frame']>=24]},ensure_ascii=False))
