from pathlib import Path
import json,hashlib,subprocess,shutil,csv
from urllib.parse import urlparse,unquote
from PIL import Image,ImageDraw,ImageFont
R=Path.cwd();O=R/'collab/reviews/cloud_s24_20261018/production_migration_af005f0';Q=O/'qa';B=R/'build/S24_production60';OLD=R/'build/S24_bite_fix_93705f2_scene60';FIX='af005f039ef0155ac93c2ff86c5a804cb8aac7ff';SRC='1e64ae9356d6335430d4783cf4976e1569ed1923';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIX;assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
baseline=json.loads((Q/'ACTUAL_BASELINE_60_SHA256.json').read_text());rows=baseline['frames'];assert len(rows)==60;olddata=subprocess.check_output(['git','show',SRC+':'+baseline['source_validation_path']]);assert hashlib.sha256(olddata).hexdigest()==baseline['source_validation_sha256'];assert subprocess.check_output(['git','rev-parse',SRC+':'+baseline['source_validation_path']],text=True).strip()==baseline['source_validation_blob'];assert sorted(p.name for p in B.glob('*.png'))==[r['filename'] for r in rows]
events=[json.loads(l) for l in (Q/'actual_network_events.jsonl').read_text().splitlines()];frames=sorted([e for e in events if e['event']=='actual_frame'],key=lambda e:e['frame']);assert [e['frame'] for e in frames]==list(range(60));assert len([e for e in events if e['event']=='browser_launched'])==1
errors=[e for e in events if e['event'] in ['pageerror','requestfailed']];assert not errors,errors
requests=[e for e in events if e['event']=='request'];responses=[e for e in events if e['event']=='response'];reviews=[e for e in requests if '/collab/reviews/' in unquote(e['url'])];assert not reviews,reviews
production=[e for e in responses if urlparse(e['url']).path.startswith(('/js/','/assets/'))];assert production and all(e['status']==200 for e in production),[e for e in production if e['status']!=200]
manifest=json.loads((Q/'fixed_production_runtime.json').read_text())
for x in manifest['rows']:
 p=R/x['path'];assert sha(p)==x['sha256'];assert p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+x['path']])
lock=json.loads((R/'assets/chars/x24/final_lock.json').read_text());images=[]
for x in lock['assets']:
 path=f"/assets/chars/x24/F{x['start']:03d}.png";rs=[e for e in responses if urlparse(e['url']).path==path];assert rs and all(e['status']==200 for e in rs);images.append({'path':path,'expected_native_SHA256':x['sha256'],'HTTP_statuses':[e['status'] for e in rs],'requests':len(rs)})
locks=[e for e in responses if urlparse(e['url']).path=='/assets/chars/x24/final_lock.json'];assert locks and all(e['status']==200 for e in locks);s23=[e for e in responses if urlparse(e['url']).path=='/js/lamp/shots/s23.js'];assert s23 and all(e['status']==200 for e in s23);assert subprocess.check_output(['git','hash-object','js/lamp/shots/s23.js'],text=True).strip()=='7bf079d18839964271c3e743247509ed3840326d'
comparisons=[]
for r,e in zip(rows,frames):
 f=r['frame'];p=B/r['filename'];old=OLD/r['filename'];h=sha(p);oldh=sha(old);assert oldh==r['sha256'];assert h==e['PNG_SHA256'];assert abs(e['t']-f/24)<1e-12
 x=next(x for x in lock['assets'] if x['start']<=f<x['start']+x['hold']);assert e['exposure']['path']==f"/assets/chars/x24/F{x['start']:03d}.png" and e['exposure']['sha256']==x['sha256'];same=p.read_bytes()==old.read_bytes()
 with Image.open(p) as im:assert im.size==(1920,1080);im.verify()
 comparisons.append({'frame':f,'filename':r['filename'],'production_SHA256':h,'approved_baseline_SHA256':r['sha256'],'SHA256_equal':h==r['sha256'],'literal_bytes_equal_to_existing_approved_raw':same,'native_exposure_start':x['start'],'native_SHA256':x['sha256']})
differences=[r for r in comparisons if not r['SHA256_equal'] or not r['literal_bytes_equal_to_existing_approved_raw']]
(Q/'all60_byte_comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
with (Q/'all60_byte_comparisons.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(comparisons[0]),lineterminator='\n');w.writeheader();w.writerows(comparisons)
result={'status':'PASS_ACTUAL_PRODUCTION60_EXACT_APPROVED_BASELINE' if not differences else 'DIFFERENCES_STOP_NO_RERENDER','fixed_production_commit':FIX,'baseline_source_commit':SRC,'baseline_runtime_commit':baseline['runtime_commit'],'production_entry':'js/anim/s24_drawn.js','entry_SHA256':manifest['entry_SHA256'],'S23_git_blob':'7bf079d18839964271c3e743247509ed3840326d','S23_SHA256':manifest['S23_SHA256'],'actual_new_production_render_invocations':1,'actual_new_production_frames':60,'approved_baseline_rerender_invocations':0,'same_SHA256_frames':sum(r['SHA256_equal'] for r in comparisons),'same_literal_bytes_frames':sum(r['literal_bytes_equal_to_existing_approved_raw'] for r in comparisons),'different_frames':differences,'size':[1920,1080],'sampling_fps':24,'sampling_duration':2.5,'new_MP4_encoding_runs':0,'new_audio_outputs':0,'native9_assets_changed':0,'original_lock_changed':False,'source_restore_five_path_substitutions_exact':True,'reviews_network_requests':reviews,'reviews_network_request_count':0,'production_JS_assets_responses':len(production),'production_JS_assets_non200':[],'native9_HTTP':images,'lock_HTTP_statuses':[e['status'] for e in locks],'lock_requests':len(locks),'native_image_HTTP_responses':sum(r['requests'] for r in images),'S23_HTTP_statuses':[e['status'] for e in s23],'pageerrors_requestfailed':errors,'all_response_HTTP_errors':[e for e in responses if e['status']>=400],'console_errors':[e for e in events if e['event']=='console_error'],'browser':[e for e in events if e['event']=='browser_launched'][0],'shared_source_edits':0,'imagegen_calls':0,'EDL_audio_ready_edits':0,'notes':['All60areactualproductionCanvasPNGs,notMP4decodedframes;old60cachewasreadonlyandmatchedsourceledger.','Consolefavicon404preservedifpresent;notanallHTTP200claim.ProductionJS/9images/lockassetsallobserved200.']}
(Q/'actual_production_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');assert not differences,differences
A=O/'actual_production_samples';A.mkdir(exist_ok=True)
for f in [0,24,59]:shutil.copyfile(B/f'{f:05d}.png',A/f'F{f:03d}_Canvas.png')
keys=[0,6,9,12,15,19,24,32,40];im=Image.new('RGB',(1920,3*396),'#eee8dc');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
for i,f in enumerate(keys):
 a=Image.open(B/f'{f:05d}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS);x=i%3*640;y=i//3*396;im.paste(a,(x,y+36));d.text((x+6,y+5),f'生产实渲 F{f:03d} / 原PNG等字节',font=font,fill='#25343d')
im.save(A/'00_all9_production_actual.jpg',quality=95)
print(json.dumps({k:result[k] for k in ['status','fixed_production_commit','same_SHA256_frames','same_literal_bytes_frames','reviews_network_request_count','native_image_HTTP_responses','lock_HTTP_statuses','S23_git_blob','pageerrors_requestfailed','console_errors']},ensure_ascii=False))
