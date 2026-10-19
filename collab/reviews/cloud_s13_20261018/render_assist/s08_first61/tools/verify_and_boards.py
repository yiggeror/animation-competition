from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil,urllib.parse
R=Path('.');O=R/'collab/reviews/cloud_s13_20261018/render_assist/s08_first61';FIXED='b99ce952dbdd6efc65344bf70c159b2cebebc612';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
rows=[]
for f in range(61):
 p=R/'build/S08_first61'/f'{f:05d}.png';dec=R/'build/S08_first61_decoded'/p.name;a=np.array(Image.open(p).convert('RGB'),np.float32);b=np.array(Image.open(dec).convert('RGB'),np.float32);assert a.shape==b.shape==(1080,1920,3)
 rows.append({'frame':f,'origin':'reused2ee2133d_actual58' if f<58 else 'new_actual_b99ce952','source_PNG_SHA256':sha(p),'decoded_PNG_SHA256':sha(dec),'decoded_same_source_RGB_MSE':float(np.mean((a-b)**2))})
base=json.loads((O/'reused58_baseline.json').read_text());assert all(x['source_PNG_SHA256']==y['source_PNG_SHA256'] and Path(x['source_cache']).read_bytes()==(R/'build/S08_first61'/f"{x['frame']:05d}.png").read_bytes() for x,y in zip(base['rows'],rows))
for f in range(58,61):assert (O/f'canvas_new/F{f:03d}.png').read_bytes()==(R/'build/S08_first61_increment'/f'{f:05d}.png').read_bytes()==(R/'build/S08_first61'/f'{f:05d}.png').read_bytes()
frames=[57,58,59,60];(O/'decoded').mkdir(exist_ok=True)
for f in frames:shutil.copyfile(R/'build/S08_first61_decoded'/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
for name,crop,scale in [('00_actual_057_060.jpg',(0,0,1920,1080),.5),('01_smoke_root_wick_actual4x.jpg',(1270,690,1455,870),4),('02_hands_low_lever_single_box_actual2x.jpg',(1110,730,1445,983),2)]:
 w=int((crop[2]-crop[0])*scale);h=int((crop[3]-crop[1])*scale);board=Image.new('RGB',(w*2,(h+30)*2),(30,32,34));d=ImageDraw.Draw(board)
 for i,f in enumerate(frames):
  im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((w,h),Image.Resampling.NEAREST if scale>1 else Image.Resampling.LANCZOS);x=(i%2)*w;y=(i//2)*(h+30);board.paste(im,(x,y+30));d.text((x+10,y+5),f'ACTUAL MP4 DECODE F{f:03d}',font=font(19),fill='white')
 board.save(O/name,quality=96)
readback=json.loads((O/'fixed_commit_71_paths_readback.json').read_text());assert len(readback)==71
for r in readback:
 p=R/r['path'];assert sha(p)==r['sha256'] and p.read_bytes()==subprocess.check_output(['git','show',FIXED+':'+r['path']])
events=[json.loads(l) for l in (O/'actual_network_events.jsonl').read_text().splitlines()];actual=[e for e in events if e['event']=='actual_frame'];assert sorted(e['frame'] for e in actual)==[58,59,60];assert all(e['PNG_SHA256']==rows[e['frame']]['source_PNG_SHA256'] for e in actual)
responses=[e for e in events if e['event']=='response'];inputs=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in responses if e['status']==200}):
 p=R/name;assert p.is_file() and p.read_bytes()==subprocess.check_output(['git','show',FIXED+':'+name]);inputs.append({'path':name,'sha256':sha(p),'git_fixed_original_bytes_equal':True})
(O/'observed_runtime_fixed_bytes.json').write_text(json.dumps(inputs,indent=2)+'\n')
network={'actual_render_runs':1,'actual_frames':[58,59,60],'browser_versions':sorted({e['version'] for e in events if e['event']=='browser_launched'}),'actual_frame_PNG_matches_direct_deliveries':True,'observed_non200_responses':[e for e in responses if e['status']!=200],'requestfailed':[e for e in events if e['event']=='requestfailed'],'pageerrors':[e for e in events if e['event']=='pageerror'],'console_errors_with_actual_locations':[e for e in events if e['event']=='console_error'],'F058_asset_responses':[e for e in responses if '/frames/F058_' in e['url']],'observed_successful_runtime_files_Git_exact':len(inputs),'favicon_caveat':'Exact console location preserved; response event can omit favicon404. Not a blanket all-requests200 claim.'}
assert not network['requestfailed'] and not network['pageerrors'];assert len(network['F058_asset_responses'])==6 and all(e['status']==200 for e in network['F058_asset_responses']);(O/'actual_network_summary.json').write_text(json.dumps(network,indent=2)+'\n')
static=json.loads((O/'static_TEST_RESULT.json').read_text());assert static['old_first58_subframe_samples_exact']==232 and static['old_layer_files_SHA256_and_bytes_verified']==51 and static['match_flame_light_glow_off_from053'] and static['smoke_three_strokes_exact_original_formula'] and static['F061_and_later_rejected']
probe=json.loads((O/'ffprobe.json').read_text());ss=probe['streams'];assert len(ss)==1 and ss[0]['codec_type']=='video' and ss[0]['nb_frames']=='61' and ss[0]['r_frame_rate']=='24/1' and ss[0]['width']==1920 and ss[0]['height']==1080
v={'status':'ACTUAL61_ENCODE_SOURCE_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':FIXED,'entry_SHA256':sha(R/'collab/reviews/20261019_0207_s08_first61_scene/s08_first61_scene.js'),'actual_new_frames':[58,59,60],'reused_frames':58,'reuse_delivery_commit':'2ee2133d0966eab25c5b2bbb1be40d768f45b8b8','full61_rerendered':False,'actual_increment_runs':1,'assembly_encoding_runs':1,'frames':61,'fps':'24/1','size':[1920,1080],'duration_fraction':'61/24','duration_ffprobe':float(probe['format']['duration']),'audio_streams':0,'F061_and_later_rendered':False,'MP4_SHA256':sha(O/'S08_first61_1920x1080_24fps.mp4'),'max_encoded_RGB_MSE':max(r['decoded_same_source_RGB_MSE'] for r in rows),'all61_source_decode_checks':rows,'fixed_commit_paths_readback_after_render_and_static':71,'runtime_rows':57,'smoke_root_scene':[1333.5355768960655,827.4023133073218],'actual_browser_Canvas_SHA_matches':True,'imagegen_calls':0,'S12_shared_or_ready_changes':0};assert v['max_encoded_RGB_MSE']<20;(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if k!='all61_source_decode_checks'},indent=2))
