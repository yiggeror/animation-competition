from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,urllib.parse,subprocess,shutil
root=Path('.');out=root/'collab/reviews/cloud_s13_20261018/render_assist/s08_first49'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
rows=[]
for f in range(49):
 p=root/'build/S08_first49'/f'{f:05d}.png';dec=root/'build/S08_first49_decoded'/p.name
 a=np.asarray(Image.open(p).convert('RGB'),np.float32);b=np.asarray(Image.open(dec).convert('RGB'),np.float32)
 assert a.shape==b.shape==(1080,1920,3)
 rows.append({'frame':f,'origin':'reused07966095_actual46' if f<46 else 'new_actual_2360f4ec','source_PNG_SHA256':sha(p),'decoded_PNG_SHA256':sha(dec),'decoded_same_source_RGB_MSE':float(np.mean((a-b)**2))})
old=json.loads((out/'reused46_baseline.json').read_text());assert all(x['source_PNG_SHA256']==y['source_PNG_SHA256'] for x,y in zip(old['rows'],rows))
for f in [46,47,48]: assert (out/f'canvas_new/F{f:03d}.png').read_bytes()==(root/'build/S08_first49_increment'/f'{f:05d}.png').read_bytes()
(out/'decoded').mkdir(exist_ok=True)
for f in [45,46,47,48]:shutil.copyfile(root/'build/S08_first49_decoded'/f'{f:05d}.png',out/f'decoded/F{f:03d}.png')
board=Image.new('RGB',(1920,1128),(27,29,31));d=ImageDraw.Draw(board)
for i,f in enumerate([45,46,47,48]):
 im=Image.open(out/f'decoded/F{f:03d}.png').convert('RGB');im=im.resize((960,540));x=(i%2)*960;y=(i//2)*564;board.paste(im,(x,y+24));d.text((x+12,y+3),f'ACTUAL MP4 DECODE F{f:03d}',font=font(17),fill='white')
board.save(out/'00_actual_045_048.jpg',quality=95)
for filename,crop,scale in [('01_separate_flames_actual6x.jpg',(1300,745,1445,815),6),('02_hands_pipe_low_lever_single_box_actual.jpg',(1080,710,1455,980),2),('03_brows_and_eyes_actual3x.jpg',(930,520,1145,650),3)]:
 ww=(crop[2]-crop[0])*scale;hh=(crop[3]-crop[1])*scale
 imout=Image.new('RGB',(ww*2,(hh+30)*2),(35,37,39));dd=ImageDraw.Draw(imout)
 for i,f in enumerate([45,46,47,48]):
  im=Image.open(out/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((ww,hh),Image.Resampling.NEAREST);x=(i%2)*ww;y=(i//2)*(hh+30);imout.paste(im,(x,y+30));dd.text((x+12,y+5),f'ACTUAL DECODE F{f:03d}',font=font(19),fill='white')
 imout.save(out/filename,quality=96)
# Every observed successful local URL is also checked against this fixed Git tree.
events=[json.loads(x) for x in (out/'actual_network_events.jsonl').read_text().splitlines()]
actual=[r for r in events if r['event']=='actual_frame'];assert sorted(r['frame'] for r in actual)==[46,47,48]
assert all(r['PNG_SHA256']==rows[r['frame']]['source_PNG_SHA256'] for r in actual)
responses=[r for r in events if r['event']=='response'];runtime=[]
for path in sorted({urllib.parse.unquote(urllib.parse.urlparse(r['url']).path).lstrip('/') for r in responses if r['status']==200}):
 p=root/path;assert p.is_file(),path
 blob=subprocess.check_output(['git','show','2360f4ec:'+path]);assert p.read_bytes()==blob,path
 runtime.append({'path':path,'sha256':sha(p),'git_original_bytes_equal':True})
(out/'observed_runtime_fixed_bytes.json').write_text(json.dumps(runtime,indent=2)+'\n')
summary={'actual_render_runs':1,'actual_frames':[46,47,48],'actual_frame_PNG_matches_direct_deliveries':True,'browser_versions':sorted({r['version'] for r in events if r['event']=='browser_launched'}),'observed_responses':len(responses),'observed_non200_responses':[r for r in responses if r['status']!=200],'requestfailed':[r for r in events if r['event']=='requestfailed'],'pageerrors':[r for r in events if r['event']=='pageerror'],'console_errors_with_actual_locations':[r for r in events if r['event']=='console_error'],'F046_asset_responses':[r for r in responses if '/frames/F046_' in r['url']],'all_observed_successful_inputs_git_original_bytes':True,'favicon_caveat':'If the console has a favicon404 location but no response event, do not invent a response event or claim all requests200. Historical first41 URL remains unknown.'}
assert len(summary['F046_asset_responses'])==6 and all(r['status']==200 for r in summary['F046_asset_responses'])
assert not summary['pageerrors'] and not summary['requestfailed']
(out/'actual_network_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
probe=json.loads((out/'ffprobe.json').read_text());streams=probe['streams'];assert len(streams)==1;s=streams[0];assert s['codec_type']=='video' and s['nb_frames']=='49' and s['r_frame_rate']=='24/1' and s['width']==1920 and s['height']==1080
entry=root/'collab/reviews/20261019_0040_s08_first49_scene/s08_first49_scene.js'
v={'status':'ACTUAL49_ENCODE_SOURCE_CHECK_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':'2360f4ec51535624342a066497ee1f9c6f0c666f','entry_SHA256':sha(entry),'actual_new_frames':[46,47,48],'reused_frames':46,'reuse_delivery_commit':'07966095db7028677e884702cc784e69c172d0f2','full49_rerendered':False,'actual_increment_runs':1,'assembly_encoding_runs':1,'frames':49,'fps':'24/1','size':[1920,1080],'duration_fraction':'49/24','duration_ffprobe':float(probe['format']['duration']),'audio_streams':0,'F049_and_later_rendered':False,'MP4_SHA256':sha(out/'S08_first49_1920x1080_24fps.mp4'),'max_encoded_RGB_MSE':max(r['decoded_same_source_RGB_MSE'] for r in rows),'all49_source_decode_checks':rows,'fixed_input_rows':51,'observed_successful_runtime_file_count':len(runtime),'actual_browser_Canvas_SHA_matches':True,'imagegen_calls':0}
(out/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if k!='all49_source_decode_checks'},indent=2))
