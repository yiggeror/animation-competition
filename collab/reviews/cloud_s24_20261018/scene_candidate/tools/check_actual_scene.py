from pathlib import Path
import hashlib,json,subprocess,shutil,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[5];S=Path(__file__).resolve().parents[1];P=S.parent;B=ROOT/'build/S24_scene60';Q=S/'qa';OUT=S/'actual_scene';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert json.loads((S/'final_lock.json').read_text())['approved']
idx=json.loads((P/'d08_d09_final_segment/asset_index.json').read_text())['rows']
by_start={r['start']:r for r in idx}
manifest=json.loads((Q/'runtime_source_manifest.json').read_text())
for r in manifest['recursive_JS_dependencies']:assert sha(ROOT/r['path'])==r['sha256'],r
for r in idx:assert sha(P/'d08_d09_final_segment'/r['asset'])==r['sha256']
imgs=sorted(B.glob('*.png'));assert [p.name for p in imgs]==[f'{f:05d}.png' for f in range(60)]
for p in imgs:
 with Image.open(p) as im:assert im.size==(1920,1080);im.verify()
events=[json.loads(l) for l in (Q/'actual_browser_events.jsonl').read_text().splitlines()]
frames=sorted([e for e in events if e['event']=='actual_frame'],key=lambda e:e['frame']);assert len(frames)==60
assert [e['frame'] for e in frames]==list(range(60))
errors=[e for e in events if e['event'] in ['pageerror','requestfailed','audit_error']];assert not errors,errors
resources=[e for e in events if e['event']=='resource']
http_errors=[e for e in resources if e['status']>=400]
assert all(e['path']=='/favicon.ico' for e in http_errors),http_errors
for r in idx:
 url='/collab/reviews/cloud_s24_20261018/d08_d09_final_segment/'+r['asset']
 rs=[e for e in resources if e['path']==url]
 assert rs and all(e['status']==200 and e['sha256']==r['sha256'] for e in rs),(r,rs)
for r in manifest['recursive_JS_dependencies']:
 if r['path']=='js/lamp/shots/s24.js':continue
 rs=[e for e in resources if e['path']=='/'+r['path']]
 assert rs and all(e['status']==200 and e['sha256']==r['sha256'] for e in rs),r
for name in ['s24_drawn.js','final_lock.json']:
 url='/collab/reviews/cloud_s24_20261018/scene_candidate/'+name
 rs=[e for e in resources if e['path']==url];assert rs and all(e['sha256']==sha(S/name) for e in rs)
for font in ['MaShanZheng-Regular.ttf','NotoSansSC-VF.ttf']:
 rs=[e for e in resources if e['path']=='/assets/fonts/'+font];assert rs and all(e['status']==200 for e in rs)
for e in frames:
 r=next(r for r in idx if r['start']<=e['frame']<=r['end_inclusive']);assert e['exposure']['start']==r['start'] and e['exposure']['sha256']==r['sha256'];assert sha(B/f"{e['frame']:05d}.png")==e['png_sha256']
vsrc=ROOT/'build/S24_scene60_1920x1080_24fps.mp4';video=OUT/'S24_scene60_1920x1080_24fps.mp4';shutil.copyfile(vsrc,video)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));write(Q/'actual_scene_ffprobe.json',probe)
streams=probe['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video'
v=streams[0];assert v['width']==1920 and v['height']==1080 and int(v['nb_frames'])==60 and v['r_frame_rate']=='24/1' and abs(float(v['duration'])-2.5)<1e-9
T=ROOT/'build/S24_scene60_decoded_check';T.mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vsync','0','-start_number','0',str(T/'%05d.png')],check=True)
decoded=sorted(T.glob('*.png'));assert len(decoded)==60
records=[]
for f,e in enumerate(frames):
 a=np.asarray(Image.open(B/f'{f:05d}.png').convert('RGB'),dtype=np.float32);b=np.asarray(Image.open(T/f'{f:05d}.png').convert('RGB'),dtype=np.float32)
 mse=float(np.mean((a-b)**2));assert mse<50,(f,mse)
 records.append({'frame':f,'exposure_start':e['exposure']['start'],'native_asset_SHA256':e['exposure']['sha256'],'actual_Canvas_PNG_SHA256':e['png_sha256'],'decoded_PNG_SHA256':sha(T/f'{f:05d}.png'),'decoded_vs_same_source_MSE':mse,'browser_page':e['page']})
selected=[0,5,6,8,9,11,12,14,15,18,19,23,24,31,32,39,40,59]
K=OUT/'decoded_keyframes';K.mkdir(exist_ok=True)
for f in selected:shutil.copyfile(T/f'{f:05d}.png',K/f'F{f:03d}.png')
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(fontpath,22)
def board(names,cols,size,crop,out):
 width,height=size;rows=math.ceil(len(names)/cols);c=Image.new('RGB',(width*cols,(height+32)*rows),(238,234,224));d=ImageDraw.Draw(c)
 for n,f in enumerate(names):
  im=Image.open(K/f'F{f:03d}.png').convert('RGB')
  if crop:im=im.crop(crop)
  im=im.resize((width,height),Image.Resampling.LANCZOS);x=n%cols*width;y=n//cols*(height+32);c.paste(im,(x,y+32));r=next(r for r in idx if r['start']<=f<=r['end_inclusive']);d.text((x+5,y+3),f'F{f:03d} actual decode / native{r["start"]:03d}',font=font,fill=(28,34,42))
 c.save(OUT/out,quality=94)
board([0,6,9,12,15,19,24,32,40],3,(640,360),None,'00_all9_actual_scene_decodes.jpg')
board(selected,3,(640,360),None,'01_all_exposure_boundaries_actual_decodes.jpg')
board([24,31,32,39,40,59],3,(640,700),(620,40,1320,800),'02_peak_settle_hold_actual_face_neck_tails.jpg')
board([19,24,32,40],2,(800,400),(610,680,1330,1040),'03_actual_sleeve_edges_scene.jpg')
report={'status':'ACTUAL60_CANVAS_RENDER_ENCODE_RESOURCE_SHA_PASS_VISUAL_REVIEW_REQUIRED','entry_sha256':sha(S/'s24_drawn.js'),'final_lock_sha256':sha(S/'final_lock.json'),'actual_scene_frames':60,'size':[1920,1080],'fps':'24/1','duration':2.5,'audio_streams':0,'MP4_sha256':sha(video),'actual_render_successful_runs':1,'earlier_initialization_failure_before_any_frame':1,'native_image_generation_calls_this_task':0,'native_assets_changed':0,'original_scene_JS_dependencies_unchanged':len(manifest['recursive_JS_dependencies']),'actual_network_resources':len(resources),'native_asset_network_success_count':sum(1 for e in resources if '/d08_d09_final_segment/candidates/' in e['path']),'actual_HTTP_errors':http_errors,'page_errors':errors,'console_errors':[e for e in events if e['event']=='console_error'],'all60_source_and_decoded_records':records,'max_decoded_same_source_MSE':max(r['decoded_vs_same_source_MSE'] for r in records),'exposure_holds':[r['hold'] for r in idx],'frame040_059_use_same_locked_native_SHA':len({r['native_asset_SHA256'] for r in records[40:]})==1,'note':'Actual scene pixels change within a hold because inherited flicker/fog/grain/time continue;native exposure remains fixed. Not a claim of byte-identical scene frames during holds.','decoded_keyframe_numbers':selected,'F040_native_border_note':'native x1023 y1255/1256 black ink tangency retained;no transparent margin claim','scene_ready_registered':False,'audio_or_EDL_edits':False}
write(Q/'actual_scene_validation.json',report)
print(json.dumps({k:v for k,v in report.items() if k not in ['all60_source_and_decoded_records','actual_HTTP_errors']},ensure_ascii=False,indent=2))
