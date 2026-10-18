from pathlib import Path
import json,hashlib,subprocess,shutil,math,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path.cwd();S=R/'collab/reviews/cloud_s24_20261018/scene_candidate';O=S/'bite_fix_93705f2';Q=O/'qa';A=O/'actual_scene';A.mkdir(exist_ok=True);C=O/'cut_evidence';C.mkdir(exist_ok=True)
FIX='93705f2f4d910a3b4805c602e8cc2c5bc2adda16';OLD='155d25986b9d6bb38acc8f09043ca74922e4dd16'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIX
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
m=json.loads((Q/'runtime_source_manifest.json').read_text());native=json.loads((Q/'native9_baseline.json').read_text())['rows']
delta=[]
for x in m['runtime_inputs']:
 p=R/x['path'];assert sha(p)==x['sha256'],x
 if x['basis']=='fixed93705f2':
  assert p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+x['path']])
  old=subprocess.check_output(['git','show',OLD+':'+x['path']]);h=hashlib.sha256(old).hexdigest()
  if h!=x['sha256']:delta.append({'path':x['path'],'old_SHA256':h,'fixed_SHA256':x['sha256']})
assert [r['path'] for r in delta]==['js/lamp/shots/s23.js'],delta
write(Q/'runtime_delta_from155.json',delta)
for x in native:
 p=R/x['path'];assert sha(p)==x['sha256'];assert p.read_bytes()==subprocess.check_output(['git','show',OLD+':'+x['path']])
 with Image.open(p) as im:assert im.size==(1024,1536);im.verify()
oldentry=subprocess.check_output(['git','show',OLD+':collab/reviews/cloud_s24_20261018/scene_candidate/s24_drawn.js']).decode();assert (S/'s24_drawn.js').read_text()==oldentry.replace(m['entry_only_replacement']['old'],m['entry_only_replacement']['new'])
def deps(path,seen=None):
 seen=set() if seen is None else seen
 if path in seen:return seen
 seen.add(path)
 for spec in re.findall(r'''(?:from\s*|import\s*)['"]([^'"]+)['"]''',path.read_text()):
  if spec.startswith('.'):
   child=(path.parent/spec).resolve()
   if child.suffix=='.js':deps(child,seen)
 return seen
s23_deps={str(p.relative_to(R)) for p in deps(R/'js/lamp/shots/s23.js')}
summary={};decodes={};sources={}
for tag,build_name,video_name,frames in [('s24','S24_bite_fix_93705f2_scene60','S24_bite_fix_93705f2_scene60_1920x1080_24fps.mp4',list(range(60))),('s23','S23_bite_fix_93705f2_tail2','S23_bite_fix_93705f2_tail2_1920x1080_24fps.mp4',[118,119])]:
 B=R/'build'/build_name;sources[tag]=B;assert sorted(p.name for p in B.glob('*.png'))==[f'{f:05d}.png' for f in frames]
 events=[json.loads(x) for x in (Q/f'{tag}_actual_browser_events.jsonl').read_text().splitlines()];fs=sorted([x for x in events if x['event']=='actual_frame'],key=lambda x:x['frame']);assert [x['frame'] for x in fs]==frames
 rendererrors=[x for x in events if x['event'] in ['pageerror','requestfailed']];assert not rendererrors,rendererrors
 res=[x for x in events if x['event']=='resource'];httperrors=[x for x in res if x['status']>=400];assert all(x['path']=='/favicon.ico' for x in httperrors),httperrors
 for x in m['runtime_inputs']:
  if x['basis']=='fixed93705f2' and x['path'].startswith('js/') and (tag=='s24' or x['path'] in s23_deps):
   rows=[r for r in res if r['path']=='/'+x['path']]
   assert rows and all(r['status']==200 and r.get('sha256')==x['sha256'] for r in rows),(tag,x)
 if tag=='s24':
  for x in native:
   rows=[r for r in res if r['path']=='/'+x['path']];assert rows and all(r['status']==200 and r.get('sha256')==x['sha256'] for r in rows),(tag,x)
  for name in ['s24_drawn.js','final_lock.json']:
   rel='collab/reviews/cloud_s24_20261018/scene_candidate/'+name;rows=[r for r in res if r['path']=='/'+rel];assert rows and all(r.get('sha256')==sha(R/rel) for r in rows)
 video=(A/'S24_scene60_bite_fixed_1920x1080_24fps.mp4') if tag=='s24' else (C/'S23_fixed_tail118_119_1920x1080_24fps.mp4');shutil.copyfile(R/'build'/video_name,video)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));write(Q/f'{tag}_ffprobe.json',probe)
 assert len(probe['streams'])==1;v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'24/1',len(frames));assert abs(float(v['duration'])-len(frames)/24)<1e-6
 D=R/'build'/f'{build_name}_decoded';D.mkdir(exist_ok=True);subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-fps_mode','passthrough','-start_number',str(frames[0]),str(D/'%05d.png')],check=True);decodes[tag]=D
 checks=[]
 for f,e in zip(frames,fs):
  p=B/f'{f:05d}.png';assert sha(p)==e['png_sha256'];a=np.asarray(Image.open(p).convert('RGB'),np.float32);b=np.asarray(Image.open(D/f'{f:05d}.png').convert('RGB'),np.float32);assert a.shape==(1080,1920,3);mse=float(np.mean((a-b)**2));assert mse<50
  if tag=='s24':
   n=next(x for x in native if x['start']<=f<x['start']+x['hold']);assert e['exposure']['start']==n['start'] and e['exposure']['sha256']==n['sha256']
  checks.append({'frame':f,'actual_Canvas_SHA256':sha(p),'decoded_SHA256':sha(D/f'{f:05d}.png'),'decoded_vs_source_RGB_MSE':mse,'native_start':e['exposure']['start'] if e['exposure'] else None})
 summary[tag]={'actual_frames':len(frames),'frame_numbers':frames,'size':[1920,1080],'fps':'24/1','duration':float(v['duration']),'audio_streams':0,'MP4_SHA256':sha(video),'frame_checks':checks,'max_RGB_MSE':max(x['decoded_vs_source_RGB_MSE'] for x in checks),'pageerrors_or_requestfailed':rendererrors,'audit_body_capture_errors':[x for x in events if x['event']=='audit_error'],'console_errors':[x for x in events if x['event']=='console_error'],'recorded_HTTP_errors':httperrors,'native_network_SHA_verified_count':sum(1 for r in res if '/candidates/F' in r['path'])}
keys=[0,5,6,8,9,11,12,14,15,18,19,23,24,31,32,39,40,59];K=A/'decoded_keyframes';K.mkdir(exist_ok=True)
for f in keys:shutil.copyfile(decodes['s24']/f'{f:05d}.png',K/f'F{f:03d}.png')
raw=A/'canvas_keyframes';raw.mkdir(exist_ok=True)
for f in [0,24,40,59]:shutil.copyfile(sources['s24']/f'{f:05d}.png',raw/f'F{f:03d}.png')
for f in [118,119]:
 shutil.copyfile(sources['s23']/f'{f:05d}.png',C/f'S23_F{f:03d}_Canvas.png');shutil.copyfile(decodes['s23']/f'{f:05d}.png',C/f'S23_F{f:03d}_decoded.png')
shutil.copyfile(K/'F000.png',C/'S24_F000_decoded.png')
# Eight consecutive real frames at the cut: S23 118/119 -> S24 000..005, no invented hold or tween.
J=R/'build/S23_to_S24_bite_fixed_actual8';J.mkdir(exist_ok=True);mapping=[]
for j,(tag,f) in enumerate([('s23',118),('s23',119)]+[('s24',f) for f in range(6)]):
 p=sources[tag]/f'{f:05d}.png';shutil.copyfile(p,J/f'{j:05d}.png');mapping.append({'clip_frame':j,'shot':tag.upper(),'shot_frame':f,'original_Canvas_SHA256':sha(p)})
cut=C/'S23_to_S24_actual8_1920x1080_24fps.mp4';assert not cut.exists(),'Do not encode a second time without reason'
subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(J/'%05d.png'),'-frames:v','8','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation',str(cut)],check=True)
cp=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(cut)]));assert len(cp['streams'])==1;cv=cp['streams'][0];assert (int(cv['nb_frames']),cv['width'],cv['height'],cv['r_frame_rate'])==(8,1920,1080,'24/1');write(Q/'cut8_ffprobe.json',cp)
CD=R/'build/S23_to_S24_bite_fixed_actual8_decoded';CD.mkdir(exist_ok=True);subprocess.run(['ffmpeg','-v','error','-y','-i',str(cut),'-fps_mode','passthrough','-start_number','0',str(CD/'%05d.png')],check=True)
for row in mapping:
 j=row['clip_frame'];a=np.asarray(Image.open(J/f'{j:05d}.png').convert('RGB'),np.float32);b=np.asarray(Image.open(CD/f'{j:05d}.png').convert('RGB'),np.float32);mse=float(np.mean((a-b)**2));assert mse<50;row['cut_decoded_SHA256']=sha(CD/f'{j:05d}.png');row['cut_vs_original_Canvas_RGB_MSE']=mse
shutil.copyfile(CD/'00001.png',C/'cut_F001_S23_F119_decoded.png');shutil.copyfile(CD/'00002.png',C/'cut_F002_S24_F000_decoded.png')
write(Q/'cut8_source_mapping.json',{'MP4_SHA256':sha(cut),'frames':mapping,'fps':24,'duration_fraction':'8/24','audio':False,'actual_source_only':True})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
def board(items,cols,tw,th,out):
 im=Image.new('RGB',(cols*tw,math.ceil(len(items)/cols)*(th+36)),'#eae4d9');d=ImageDraw.Draw(im)
 for i,(p,label,crop) in enumerate(items):
  a=Image.open(p).convert('RGB');a=a.crop(crop) if crop else a;a=a.resize((tw,th),Image.Resampling.LANCZOS);x=i%cols*tw;y=i//cols*(th+36);im.paste(a,(x,y+36));d.text((x+5,y+4),label,font=font,fill='#25343d')
 im.save(out,quality=96)
board([(K/f'F{f:03d}.png',f'S24 F{f:03d} 实际MP4解码',None) for f in [0,6,9,12,15,19,24,32,40]],3,640,360,A/'00_all9_actual_scene_decodes.jpg')
board([(K/f'F{f:03d}.png',f'S24 F{f:03d} 实际MP4解码',None) for f in keys],3,640,360,A/'01_all_exposure_boundaries_actual_decodes.jpg')
board([(K/f'F{f:03d}.png',f'S24 F{f:03d} 真解码咬合', (420,830,650,1080)) for f in [0,6,9,12,15,19,24,32,40,59]],5,460,500,A/'02_contact_across_all9_and_last.jpg')
board([(C/'cut_F001_S23_F119_decoded.png','切换片真解码 S23 F119',None),(C/'cut_F002_S24_F000_decoded.png','切换片真解码 S24 F000',None)],2,960,540,C/'00_actual_cut_fullframes.jpg')
board([(C/'cut_F001_S23_F119_decoded.png','切换真解码 S23 F119 嘴喙',(1140,700,1340,930)),(C/'cut_F002_S24_F000_decoded.png','切换真解码 S24 F000 嘴喙',(450,850,650,1080))],2,600,690,C/'01_actual_cut_contact_closeups.jpg')
oldpng=C/'old155_S24_F059_decoded.png';oldpng.write_bytes(subprocess.check_output(['git','show',OLD+':collab/reviews/cloud_s24_20261018/scene_candidate/actual_scene/decoded_keyframes/F059.png']))
board([(oldpng,'旧155 F059 脱口', (420,830,650,1080)),(K/'F000.png','新937 F000 咬住',(420,830,650,1080)),(K/'F059.png','新937 F059 保持',(420,830,650,1080))],3,460,500,C/'02_old_gap_vs_fixed_first_last.jpg')
read_only=json.loads((Q/'read_only_runtime_fetch.json').read_text());assert read_only['renderFrame_calls']==0 and len(read_only['rows'])==34 and all(r['pass'] for r in read_only['rows'])
summary['read_only_HTTP34_SHA_pass']=True
summary['audit_note']='Body capture eviction errors retained;NotoSansSC response SHA was absent from render audit;separate no-render browser fetch verified all34 HTTP inputs including both fonts. Not zero audit errors.'
summary.update({'status':'ACTUAL_RENDER_DECODE_AND_SOURCE_PASS_VISUAL_REVIEW_REQUIRED','fixed_shared_runtime_commit':FIX,'private_base_commit':OLD,'entry_one_line_only':True,'new_entry_SHA256':sha(S/'s24_drawn.js'),'native9_unchanged':True,'locked_native_rows':native,'only_used_shared_runtime_difference_from155':delta,'shared_source_edits':0,'native_image_generation_calls':0,'EDL_audio_ready_changes':0,'render_invocations':{'s24_full60':1,'s23_tail2_only':1},'S23_full120_rendered':False,'cut8_encoded_once':True})
write(Q/'actual_delivery_validation.json',summary)
print(json.dumps({'status':summary['status'],'s24_MP4_SHA256':summary['s24']['MP4_SHA256'],'s24_frames':summary['s24']['actual_frames'],'s24_max_MSE':summary['s24']['max_RGB_MSE'],'s23_tail_frames':summary['s23']['actual_frames'],'audit_body_errors':{t:len(summary[t]['audit_body_capture_errors']) for t in ['s24','s23']},'native9_SHA_unchanged':True},ensure_ascii=False))
