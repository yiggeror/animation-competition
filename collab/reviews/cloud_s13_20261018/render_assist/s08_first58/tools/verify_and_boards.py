from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil,urllib.parse
R=Path('.');O=R/'collab/reviews/cloud_s13_20261018/render_assist/s08_first58';SRC=R/'collab/reviews/20261019_0134_s08_first58_scene';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
rows=[]
for f in range(58):
 p=R/'build/S08_first58'/f'{f:05d}.png';dec=R/'build/S08_first58_decoded'/p.name;a=np.array(Image.open(p).convert('RGB'),np.float32);b=np.array(Image.open(dec).convert('RGB'),np.float32);assert a.shape==b.shape==(1080,1920,3)
 rows.append({'frame':f,'origin':'reused51bb229_actual53' if f<53 else 'new_actual_3e558463','source_PNG_SHA256':sha(p),'decoded_PNG_SHA256':sha(dec),'decoded_same_source_RGB_MSE':float(np.mean((a-b)**2))})
base=json.loads((O/'reused53_baseline.json').read_text());assert all(x['source_PNG_SHA256']==y['source_PNG_SHA256'] for x,y in zip(base['rows'],rows))
for f in range(53,58):assert (O/f'canvas_new/F{f:03d}.png').read_bytes()==(R/'build/S08_first58_increment'/f'{f:05d}.png').read_bytes()==(R/'build/S08_first58'/f'{f:05d}.png').read_bytes()
(O/'decoded').mkdir(exist_ok=True)
for f in range(52,58):shutil.copyfile(R/'build/S08_first58_decoded'/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
board=Image.new('RGB',(1920,1692),(27,29,31));d=ImageDraw.Draw(board)
for i,f in enumerate(range(52,58)):
 im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').resize((960,540));x=(i%2)*960;y=(i//2)*564;board.paste(im,(x,y+24));d.text((x+10,y+3),f'ACTUAL MP4 DECODE F{f:03d}',font=font(17),fill='white')
board.save(O/'00_actual_052_057.jpg',quality=95)
for file,crop,scale in [('01_extinction_smoke_root_actual4x.jpg',(1285,680,1455,830),4),('02_hands_pipe_low_lever_single_box_actual2x.jpg',(1110,680,1435,983),2),('03_brows_and_eyes_actual3x.jpg',(930,520,1145,650),3)]:
 w=(crop[2]-crop[0])*scale;h=(crop[3]-crop[1])*scale;board=Image.new('RGB',(w*3,(h+30)*2),(33,35,37));d=ImageDraw.Draw(board)
 for i,f in enumerate(range(52,58)):
  im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((w,h),Image.Resampling.NEAREST);x=(i%3)*w;y=(i//3)*(h+30);board.paste(im,(x,y+30));d.text((x+10,y+5),f'ACTUAL DECODE F{f:03d}',font=font(19),fill='white')
 board.save(O/file,quality=96)
for r in json.loads((O/'fixed_packet_readback.json').read_text()):
 p=R/r['path'];assert sha(p)==r['sha256'] and p.read_bytes()==subprocess.check_output(['git','show','3e558463:'+r['path']])
events=[json.loads(l) for l in (O/'actual_network_events.jsonl').read_text().splitlines()];actual=[e for e in events if e['event']=='actual_frame'];assert sorted(e['frame'] for e in actual)==list(range(53,58));assert all(e['PNG_SHA256']==rows[e['frame']]['source_PNG_SHA256'] for e in actual)
responses=[e for e in events if e['event']=='response'];inputs=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in responses if e['status']==200}):
 p=R/name;assert p.is_file() and p.read_bytes()==subprocess.check_output(['git','show','3e558463:'+name]);inputs.append({'path':name,'sha256':sha(p),'git_fixed_original_bytes_equal':True})
(O/'observed_runtime_fixed_bytes.json').write_text(json.dumps(inputs,indent=2)+'\n')
network={'actual_render_runs':1,'actual_frames':list(range(53,58)),'browser_versions':sorted({e['version'] for e in events if e['event']=='browser_launched'}),'actual_frame_PNG_matches_direct_deliveries':True,'observed_non200_responses':[e for e in responses if e['status']!=200],'requestfailed':[e for e in events if e['event']=='requestfailed'],'pageerrors':[e for e in events if e['event']=='pageerror'],'console_errors_with_actual_locations':[e for e in events if e['event']=='console_error'],'F046_reuse_asset_responses':[e for e in responses if '/frames/F046_' in e['url']],'observed_successful_runtime_files_Git_exact':len(inputs),'favicon_caveat':'Console favicon404 location may exist without response event. Preserve exact events, do not say all requests200 or infer historical unknown first41URL.'}
assert not network['requestfailed'] and not network['pageerrors'];assert len(network['F046_reuse_asset_responses'])==6 and all(e['status']==200 for e in network['F046_reuse_asset_responses']);(O/'actual_network_summary.json').write_text(json.dumps(network,indent=2)+'\n')
static=json.loads((O/'static_TEST_RESULT.json').read_text());assert static['old_first53_subframe_samples_exact']==212 and static['old_layer_files_SHA256_and_bytes_verified']==51 and static['match_flame_light_glow_off_from053'] and static['smoke_three_strokes_exact_original_formula']
probe=json.loads((O/'ffprobe.json').read_text());ss=probe['streams'];assert len(ss)==1 and ss[0]['codec_type']=='video' and ss[0]['nb_frames']=='58' and ss[0]['r_frame_rate']=='24/1' and ss[0]['width']==1920 and ss[0]['height']==1080
v={'status':'ACTUAL58_ENCODE_SOURCE_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':'3e5584634257dd9aca95aeba7273ddc643ea6351','entry_SHA256':sha(SRC/'s08_first58_scene.js'),'actual_new_frames':list(range(53,58)),'reused_frames':53,'reuse_delivery_commit':'51bb229998fd8c8a407b09d2156b5df764de4d3e','full58_rerendered':False,'actual_increment_runs':1,'assembly_encoding_runs':1,'frames':58,'fps':'24/1','size':[1920,1080],'duration_fraction':'58/24','duration_ffprobe':float(probe['format']['duration']),'audio_streams':0,'F058_and_later_rendered':False,'MP4_SHA256':sha(O/'S08_first58_1920x1080_24fps.mp4'),'max_encoded_RGB_MSE':max(r['decoded_same_source_RGB_MSE'] for r in rows),'all58_source_decode_checks':rows,'fixed_packet_files_readback':68,'runtime_rows':54,'F053_to057_source_asset':'046, exact heldF051 art; no newnative','smoke_root_scene':[1350,782.572972972973],'actual_browser_Canvas_SHA_matches':True,'imagegen_calls':0,'S12_shared_or_ready_changes':0};(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if k!='all58_source_decode_checks'},indent=2))
