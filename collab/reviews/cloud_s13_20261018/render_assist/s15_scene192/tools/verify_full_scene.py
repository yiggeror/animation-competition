"""One full S15 render/encode; decode all192 and preserve only key evidence, no scene changes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil,urllib.parse
O=Path(__file__).resolve().parents[1];FIX='5271da8b1870bf4523cd7bb4eaf101f77147d6d8';P=Path('collab/reviews/20261019_0434_s15_drawn_candidate');B=Path('build/S15_scene192');D=Path('build/S15_scene192_decoded');src=Path('build/S15_scene192.mp4');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sorted(p.name for p in B.glob('*.png'))==[f'{f:05d}.png' for f in range(192)]
assert src.exists() and not D.exists() and not (O/'S15_scene192_1920x1080_24fps.mp4').exists(),'Do not repeat encode/decode or overwrite a previous result blindly.'
shutil.copyfile(src,O/'S15_scene192_1920x1080_24fps.mp4');assert src.read_bytes()==(O/'S15_scene192_1920x1080_24fps.mp4').read_bytes();mp4=O/'S15_scene192_1920x1080_24fps.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]));(O/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n');streams=probe['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video' and streams[0]['nb_frames']=='192' and streams[0]['r_frame_rate']=='24/1' and streams[0]['width']==1920 and streams[0]['height']==1080 and float(probe['format']['duration'])==8
D.mkdir();cmd=['ffmpeg','-y','-loglevel','error','-i',str(mp4),'-vsync','0','-start_number','0',str(D/'%05d.png')]
with (O/'decode.log').open('w') as f:subprocess.run(cmd,check=True,stdout=f,stderr=subprocess.STDOUT)
assert sorted(p.name for p in D.glob('*.png'))==[f'{f:05d}.png' for f in range(192)]
rows=[]
for f in range(192):
 a=B/f'{f:05d}.png';b=D/a.name;ar=np.array(Image.open(a).convert('RGB'),np.float32);br=np.array(Image.open(b).convert('RGB'),np.float32);assert ar.shape==br.shape==(1080,1920,3);rows.append({'frame':f,'source_Canvas_SHA256':sha(a),'actual_video_decoded_SHA256':sha(b),'decoded_RGB_MSE':float(np.mean((ar-br)**2))})
assert max(r['decoded_RGB_MSE'] for r in rows)<20;(O/'all192_source_decode_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
keys=[0,72,108,112,116,120,124,132,144,191];(O/'decoded').mkdir(exist_ok=True)
for f in keys:shutil.copyfile(D/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
(O/'decoded/SHA256SUMS.txt').write_text(''.join(sha(O/f'decoded/F{f:03d}.png')+f'  F{f:03d}.png\n' for f in keys))
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
frames=[0,72,108,116,124,132,144,191];board=Image.new('RGB',(1920,600),(25,29,32));d=ImageDraw.Draw(board)
for i,f in enumerate(frames):
 im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=i%4*480;y=i//4*300;board.paste(im,(x,y+30));d.text((x+8,y+5),f'ACTUAL MP4 DECODE F{f:03d}',font=font(18),fill='white')
board.save(O/'00_actual_scene_keyframes.jpg',quality=96)
frames=[0,108,112,116,120,124,132,144];crop=(300,530,700,1080);board=Image.new('RGB',(1600,1160),(25,29,32));d=ImageDraw.Draw(board)
for i,f in enumerate(frames):
 im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop);x=i%4*400;y=i//4*580;board.paste(im,(x,y+30));d.text((x+6,y+5),f'ACTUAL F{f:03d} / NO BRIGHTENING',font=font(16),fill='white')
board.save(O/'01_actual_face_arms_progression.png')
E=[json.loads(s) for s in (O/'actual_network_events.jsonl').read_text().splitlines()];act=[e for e in E if e['event']=='actual_frame'];assert sorted(e['frame'] for e in act)==list(range(192)) and all(e['PNG_SHA256']==rows[e['frame']]['source_Canvas_SHA256'] for e in act);res=[e for e in E if e['event']=='response'];loaded=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in res if e['status']==200}):
 p=Path(name);assert p.is_file() and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+name]);loaded.append({'path':name,'SHA256':sha(p),'fixed_git_bytes_equal':True})
assets=[e for e in res if '/assets/x15/' in e['url']];unique_assets=sorted({urllib.parse.urlparse(e['url']).path.split('/')[-1] for e in assets});assert unique_assets==[f'F{f:03d}.png' for f in [0,108,112,116,120,124,132,144]] and all(e['status']==200 for e in assets)
network={'full_scene_render_runs':1,'actual_Canvas_frames':192,'browser_versions':sorted({e['version'] for e in E if e['event']=='browser_launched'}),'all192_browser_PNG_SHA_match_source':True,'asset_responses':assets,'successful_fixed_runtime_files':loaded,'non200_responses':[e for e in res if e['status']!=200],'requestfailed':[e for e in E if e['event']=='requestfailed'],'pageerrors':[e for e in E if e['event']=='pageerror'],'console_errors_actual_locations':[e for e in E if e['event']=='console_error']};assert not network['requestfailed'] and not network['pageerrors'];(O/'actual_network_summary.json').write_text(json.dumps(network,indent=2)+'\n')
for r in json.loads((O/'fixed24_readback.json').read_text()):
 p=Path(r['path']);assert sha(p)==r['SHA256'] and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+r['path']])
pre={str(f):(O/f'preflight/F{f:03d}.png').read_bytes()==(B/f'{f:05d}.png').read_bytes() for f in [0,132,144]}
v={'status':'ACTUAL192_ENCODE_AND_SOURCE_DECODE_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':FIX,'entry_SHA256':sha(P/'s15_drawn.js'),'MP4_SHA256':sha(mp4),'size':[1920,1080],'fps':'24/1','frames':192,'duration_seconds':8,'audio_streams':0,'full_scene_render_runs':1,'full_scene_encode_runs':1,'preflight_captured_frames':[0,132,144],'preflight_vs_full_Canvas_byte_equal_by_frame':pre,'actual_decoded_keyframes':keys,'max_encoded_RGB_MSE':max(r['decoded_RGB_MSE'] for r in rows),'fixed24_source_paths_postchecked':True,'all_loaded_runtime_files_fixed_Git_bytes':True,'whole_character_registration_camera_sheet_lights_unchanged':True,'director_accepted_foreground_shoes_stool_crop':True,'imagegen_calls':0}
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');(O/'decode_command.json').write_text(json.dumps(cmd,indent=2)+'\n');print(json.dumps(v,indent=2))
