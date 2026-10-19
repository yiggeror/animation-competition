"""Reuse approved64 original Canvas, add only actual064–074, encode/decode once."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,subprocess,urllib.parse,numpy as np
O=Path(__file__).resolve().parents[1]; FIX='1e68c985680596a8c73aee612640c4409584da35'; OLD='3324ea3c9adc76805f3fd0d5a1f5d95fa8717bec';P=Path('collab/reviews/20261019_0309_s08_first75_scene'); B=Path('build/S08_first75');D=Path('build/S08_first75_decoded');N=Path('build/S08_first75_increment');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not B.exists() and not D.exists() and not (O/'S08_first75_1920x1080_24fps.mp4').exists(),'Do not repeat assembly/encoding blindly.'
assert sorted(p.name for p in N.glob('*.png'))==[f'{f:05d}.png' for f in range(64,75)]
base=json.loads((O/'reused64_baseline.json').read_text());assert len(base['rows'])==64
B.mkdir();D.mkdir()
for row in base['rows']:
 p=Path(row['source_cache']);q=B/f"{row['frame']:05d}.png";assert sha(p)==row['source_PNG_SHA256'];shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes()
for f in range(64,75):
 p=N/f'{f:05d}.png';q=B/p.name;shutil.copyfile(p,q);shutil.copyfile(p,O/f'canvas_new/F{f:03d}.png');assert p.read_bytes()==q.read_bytes()==(O/f'canvas_new/F{f:03d}.png').read_bytes()
(O/'canvas_new/SHA256SUMS.txt').write_text(''.join(f'{sha(O/f"canvas_new/F{f:03d}.png")}  F{f:03d}.png\n' for f in range(64,75)))
mp4=O/'S08_first75_1920x1080_24fps.mp4';enc=['ffmpeg','-y','-loglevel','error','-framerate','24','-start_number','0','-i',str(B/'%05d.png'),'-frames:v','75','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation','-an',str(mp4)]
with (O/'encode.log').open('w') as log:subprocess.run(enc,check=True,stdout=log,stderr=subprocess.STDOUT)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]));(O/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n');s=probe['streams'];assert len(s)==1 and s[0]['codec_type']=='video' and s[0]['nb_frames']=='75' and s[0]['r_frame_rate']=='24/1' and s[0]['width']==1920 and s[0]['height']==1080
cmd=['ffmpeg','-y','-loglevel','error','-i',str(mp4),'-vsync','0','-start_number','0',str(D/'%05d.png')]
with (O/'decode.log').open('w') as log:subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
assert sorted(p.name for p in D.glob('*.png'))==[f'{f:05d}.png' for f in range(75)]
rows=[]
for f in range(75):
 p=B/f'{f:05d}.png';d=D/p.name;a=np.array(Image.open(p).convert('RGB'),np.float32);b=np.array(Image.open(d).convert('RGB'),np.float32);assert a.shape==b.shape==(1080,1920,3);rows.append({'frame':f,'source_PNG_SHA256':sha(p),'decoded_PNG_SHA256':sha(d),'decoded_RGB_MSE':float(np.mean((a-b)**2))})
assert max(r['decoded_RGB_MSE'] for r in rows)<20
(O/'all75_source_decode_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
frames=[63,64,65,66,68,69,71,72,74]
for f in frames:shutil.copyfile(D/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
for name,crop,scale in [('00_actual_selected9.jpg',(0,0,1920,1080),1/3),('01_table_hands_shadow_actual2x.jpg',(1110,850,1460,1005),2),('02_smoke_wick_actual2x.jpg',(1180,700,1465,1000),2)]:
 w=round((crop[2]-crop[0])*scale);h=round((crop[3]-crop[1])*scale);board=Image.new('RGB',(w*3,(h+32)*3),(25,29,32));draw=ImageDraw.Draw(board)
 for k,f in enumerate(frames):
  im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((w,h),Image.Resampling.NEAREST if scale>1 else Image.Resampling.LANCZOS);x=k%3*w;y=k//3*(h+32);board.paste(im,(x,y+32));draw.text((x+8,y+6),f'ACTUAL MP4 DECODE F{f:03d}',font=font(19),fill='white')
 board.save(O/name,quality=96)
# Post-render fixed bytes, successful actual requests and browser PNG readback.
for row in json.loads((O/'fixed104_readback.json').read_text())+json.loads((O/'fixed_common_runtime_preflight.json').read_text()):
 p=Path(row['path']);assert sha(p)==row['SHA256'] and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+row['path']])
ev=[json.loads(l) for l in (O/'actual_network_events.jsonl').read_text().splitlines()];acts=[e for e in ev if e['event']=='actual_frame'];assert sorted(e['frame'] for e in acts)==list(range(64,75));assert all(e['PNG_SHA256']==rows[e['frame']]['source_PNG_SHA256'] for e in acts)
res=[e for e in ev if e['event']=='response'];files=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in res if e['status']==200}):
 p=Path(name);assert p.is_file() and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+name]);files.append({'path':name,'SHA256':sha(p),'fixed_git_bytes_equal':True})
(O/'observed_runtime_fixed_bytes.json').write_text(json.dumps(files,indent=2)+'\n');newres=[e for e in res if '/frames/F' in e['url'] and any('/F'+f+'_' in e['url'] for f in ['064','066','069','072'])]
net={'actual_render_runs':1,'actual_frames':list(range(64,75)),'browser_versions':sorted({e['version'] for e in ev if e['event']=='browser_launched'}),'new15_layer_responses':newres,'non200_responses':[e for e in res if e['status']!=200],'requestfailed':[e for e in ev if e['event']=='requestfailed'],'pageerrors':[e for e in ev if e['event']=='pageerror'],'console_errors_with_actual_locations':[e for e in ev if e['event']=='console_error'],'successful_fixed_runtime_files':len(files),'browser_Canvas_PNG_SHA_matches_all11_deliveries':True}
assert len(newres)==30 and all(e['status']==200 for e in newres) and not net['requestfailed'] and not net['pageerrors'];(O/'actual_network_summary.json').write_text(json.dumps(net,indent=2)+'\n')
static=json.loads((O/'static_TEST_RESULT.json').read_text());assert static['old_first64_subframe_samples_exact']==256 and static['old_layer_files_SHA256_and_bytes_verified']==57 and static['new_layer_files_SHA256_verified']==15 and static['F075_and_later_rejected']
v={'status':'ACTUAL75_SOURCE_DECODE_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':FIX,'entry_SHA256':sha(P/'s08_first75_candidate.js'),'actual_new_frames':list(range(64,75)),'reused_original_Canvas_frames':64,'reuse_delivery_commit':OLD,'render_runs':1,'encoding_runs':1,'frames':75,'size':[1920,1080],'fps':'24/1','duration_seconds':float(probe['format']['duration']),'audio_streams':0,'MP4_SHA256':sha(mp4),'max_encoded_RGB_MSE':max(r['decoded_RGB_MSE'] for r in rows),'fixed_source_package_paths':104,'fixed_common_runtime_preflight_paths':8,'source_and_runtime_bytes_postchecked':True,'F066_onward_smoke_root_scene':[1253.6806826223356,954.1901186474938],'F064_F065_held_match_root_scene':[1282.6806826223356,928.1901186474938],'F075_or_later_rendered':False,'imagegen_calls':0}
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');(O/'assembly_commands.json').write_text(json.dumps({'render_runs':1,'rendered_only':list(range(64,75)),'old_Canvas_reused_without_render':64,'encoding_runs':1,'encode':enc,'decode':cmd},indent=2)+'\n');print(json.dumps(v,indent=2));print('new15 layer responses:',len(newres),'pageerrors',len(net['pageerrors']),'requestfailed',len(net['requestfailed']))
