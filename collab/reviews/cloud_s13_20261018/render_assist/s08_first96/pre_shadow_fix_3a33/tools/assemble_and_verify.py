from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,subprocess,urllib.parse,numpy as np
O=Path(__file__).resolve().parents[1];FIX='3a33ac02c093fe38b2a3f381279fbd3d943d8813';OLD='5f25589722c5dfa4b1e5f97fdfb6d392ee10d107';B=Path('build/S08_first96');D=Path('build/S08_first96_decoded');N=Path('build/S08_first96_increment');P=Path('collab/reviews/20261019_0421_s08_first96_scene');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not B.exists() and not D.exists() and not (O/'S08_first96_1920x1080_24fps.mp4').exists();assert sorted(p.name for p in N.glob('*.png'))==[f'{i:05d}.png' for i in range(75,96)];B.mkdir();D.mkdir();base=json.loads((O/'reused75_baseline.json').read_text());assert len(base['rows'])==75
for r in base['rows']:
 p=Path(r['source_cache']);q=B/f"{r['frame']:05d}.png";assert sha(p)==r['source_PNG_SHA256'];shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes()
for f in range(75,96):
 p=N/f'{f:05d}.png';shutil.copyfile(p,B/p.name);shutil.copyfile(p,O/f'canvas_new/F{f:03d}.png');assert p.read_bytes()==(B/p.name).read_bytes()==(O/f'canvas_new/F{f:03d}.png').read_bytes()
(O/'canvas_new/SHA256SUMS.txt').write_text(''.join(sha(O/f'canvas_new/F{f:03d}.png')+f'  F{f:03d}.png\n' for f in range(75,96)))
mp4=O/'S08_first96_1920x1080_24fps.mp4';encode=['ffmpeg','-y','-loglevel','error','-framerate','24','-start_number','0','-i',str(B/'%05d.png'),'-frames:v','96','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation','-an',str(mp4)]
with (O/'encode.log').open('w') as log:subprocess.run(encode,check=True,stdout=log,stderr=subprocess.STDOUT)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]));(O/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n');s=probe['streams'];assert len(s)==1 and s[0]['codec_type']=='video' and s[0]['nb_frames']=='96' and s[0]['r_frame_rate']=='24/1' and s[0]['width']==1920 and s[0]['height']==1080 and float(probe['format']['duration'])==4
cmd=['ffmpeg','-y','-loglevel','error','-i',str(mp4),'-vsync','0','-start_number','0',str(D/'%05d.png')]
with (O/'decode.log').open('w') as log:subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
assert sorted(p.name for p in D.glob('*.png'))==[f'{i:05d}.png' for i in range(96)];rows=[]
for f in range(96):
 p=B/f'{f:05d}.png';q=D/p.name;a=np.array(Image.open(p).convert('RGB'),np.float32);b=np.array(Image.open(q).convert('RGB'),np.float32);assert a.shape==b.shape==(1080,1920,3);rows.append({'frame':f,'source_Canvas_SHA256':sha(p),'decoded_SHA256':sha(q),'decoded_RGB_MSE':float(np.mean((a-b)**2))})
assert max(r['decoded_RGB_MSE'] for r in rows)<20;(O/'all96_source_decode_checks.json').write_text(json.dumps(rows,indent=2)+'\n');keys=[74,75,77,78,79,80,81,82,87,88,90,91,93,94,95]
for f in keys:shutil.copyfile(D/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def board(name,frames,crop,scale,cols):
 w=round((crop[2]-crop[0])*scale);h=round((crop[3]-crop[1])*scale);im=Image.new('RGB',(w*cols,(h+30)*((len(frames)+cols-1)//cols)),(25,29,32));d=ImageDraw.Draw(im)
 for k,f in enumerate(frames):
  tile=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((w,h),Image.Resampling.NEAREST if scale>1 else Image.Resampling.LANCZOS);x=k%cols*w;y=k//cols*(h+30);im.paste(tile,(x,y+30));d.text((x+7,y+5),f'ACTUAL DECODE F{f:03d}',font=font(18),fill='white')
 im.save(O/name,quality=96)
board('00_actual_selected15.jpg',keys,(0,0,1920,1080),.2,5);board('01_release_return_actual1_5x.jpg',[77,78,79,80,81,82],(1110,600,1540,983),1.5,3);board('02_retreat_hands_box_match_actual2x.jpg',[75,78,82,88,91,95],(1010,770,1370,995),2,3)
for r in json.loads((O/'fixed_source_readback.json').read_text())+json.loads((O/'shared_runtime_old75_parity.json').read_text()):
 p=Path(r['path']);assert sha(p)==r['SHA256'] and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+r['path']])
E=[json.loads(s) for s in (O/'actual_network_events.jsonl').read_text().splitlines()];actual=[e for e in E if e['event']=='actual_frame'];assert sorted(e['frame'] for e in actual)==list(range(75,96));assert all(e['PNG_SHA256']==rows[e['frame']]['source_Canvas_SHA256'] for e in actual);res=[e for e in E if e['event']=='response'];loaded=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in res if e['status']==200}):
 p=Path(name);assert p.is_file() and p.read_bytes()==subprocess.check_output(['git','show',FIX+':'+name]);loaded.append({'path':name,'SHA256':sha(p),'fixed_git_bytes_equal':True})
(O/'observed_runtime_fixed_bytes.json').write_text(json.dumps(loaded,indent=2)+'\n');newres=[e for e in res if any('/F'+f+'_' in e['url'] for f in ['078','088','091','094'])];net={'actual_increment_render_runs':1,'actual_frames':list(range(75,96)),'all21_browser_PNG_SHA_match_source':True,'new16_layer_responses':newres,'successful_fixed_runtime_files':len(loaded),'pageerrors':[e for e in E if e['event']=='pageerror'],'requestfailed':[e for e in E if e['event']=='requestfailed'],'non200_responses':[e for e in res if e['status']!=200],'console_errors_actual_locations':[e for e in E if e['event']=='console_error']};assert len(newres)==32 and all(e['status']==200 for e in newres) and not net['pageerrors'] and not net['requestfailed'];(O/'actual_network_summary.json').write_text(json.dumps(net,indent=2)+'\n')
static=json.loads((O/'static_old75_parity.json').read_text());assert static['old75_subsamples']==300 and static['old_layer_files_exact']==72 and static['F096_rejected'];v={'status':'ACTUAL96_SOURCE_DECODE_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':FIX,'entry_SHA256':sha(P/'s08_first96_candidate.js'),'actual_new_frames':list(range(75,96)),'old_original_Canvas_reused':75,'reuse_delivery_commit':OLD,'actual_increment_runs':1,'encoding_runs':1,'frames':96,'fps':'24/1','size':[1920,1080],'duration_seconds':4,'audio_streams':0,'MP4_SHA256':sha(mp4),'max_encoded_RGB_MSE':max(r['decoded_RGB_MSE'] for r in rows),'fixed_source_package_paths':95,'F096_or_later_rendered':False,'imagegen_calls':0};(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');(O/'assembly_commands.json').write_text(json.dumps({'increment_runs':1,'new_only':list(range(75,96)),'old75_reused':True,'encoding_runs':1,'encode':encode,'decode':cmd},indent=2)+'\n');print(json.dumps(v,indent=2))
