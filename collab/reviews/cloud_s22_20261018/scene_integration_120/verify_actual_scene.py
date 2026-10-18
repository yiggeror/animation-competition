#!/usr/bin/env python3
"""Inspect artifacts decoded from the actual120f scene MP4, never a proxy layer."""
from pathlib import Path
import csv,hashlib,json,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'provenance/actual_scene120_manifest.json').read_text());mp=D/manifest['clip'];m=json.loads((D/'resource_map.json').read_text());lock=json.loads((D/'tail_lock.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp)],text=True));s=probe['streams'];assert len(s)==1 and s[0]['codec_type']=='video';v=s[0]
assert [v['width'],v['height']]==[1920,1080] and v['r_frame_rate']=='24/1' and v['avg_frame_rate']=='24/1' and int(v['nb_read_frames'])==120 and float(probe['format']['duration'])==5
assert sha(mp)==manifest['sha256'];assert manifest['module_sha256']==sha(D/'S22_drawn.js');assert manifest['errors']==[]
assert not any(x['status']>=400 and x['url'].split('?')[0].endswith(('.png','.js','.json')) for x in manifest['http']);assert not any('h22_together' in x['url'] for x in manifest['http'])
for r in m['exposures']:
 assert sha(R/r['url'].lstrip('/'))==r['sha256']
 assert len([f for f in manifest['frame_sha256'] if r['start']<=f['frame']<=r['end']])==r['hold']
for f in manifest['frame_sha256']:
 assert sha(D/'scene120/frames'/f['file'])==f['sha256']
assert next(r for r in m['exposures'] if r['id']=='F108')['sha256']=='e0d31242883ad1dca5e5ce1c838257228e5d980ace1605ea93e2a31349f5a704'
assert sum(r['hold'] for r in m['exposures'])==120
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);qa=D/'qa';qa.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='s22_actual_decode_') as td:
 td=Path(td);subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp),'-vsync','0',str(td/'%05d.png')],check=True)
 decoded=sorted(td.glob('*.png'));assert len(decoded)==120
 # All120 actual decoded frames in five consecutive one-second sheets.
 for sec in range(5):
  board=Image.new('RGB',(2880,1176),(24,24,24));d=ImageDraw.Draw(board)
  for j,f in enumerate(range(sec*24,(sec+1)*24)):
   im=Image.open(decoded[f]).convert('RGB').resize((480,270));x=(j%6)*480;y=(j//6)*294;board.paste(im,(x,y+24));state=next(r['id'] for r in m['exposures'] if r['start']<=f<=r['end']);d.text((x+6,y+3),f'F{f:03} / {state} / {f/24:.3f}s',font=font,fill='white')
  board.save(qa/f'actual_decoded_second_{sec}.jpg',quality=94)
 board=Image.new('RGB',(2560,1152),(24,24,24));d=ImageDraw.Draw(board)
 for j,r in enumerate(m['exposures']):
  x=(j%4)*640;y=(j//4)*384;im=Image.open(decoded[r['start']]).convert('RGB').resize((640,360));board.paste(im,(x,y+24));d.text((x+6,y+3),f"{r['id']} / {r['start']:03}-{r['end']:03} / hold{r['hold']}",font=font,fill='white')
 board.save(qa/'actual_12_states.jpg',quality=95)
 # The previously visible tip lies around(x153,y1075) in the final camera.
 edge_frames=[107,108,113,114,119];crop=(120,1035,205,1080);board=Image.new('RGB',(510*len(edge_frames),300),(24,24,24));d=ImageDraw.Draw(board)
 for j,f in enumerate(edge_frames):
  im=Image.open(decoded[f]).convert('RGB').crop(crop).resize((510,270));board.paste(im,(510*j,30));d.text((510*j+5,5),f'Actual MP4 F{f:03} lower edge 6x',font=font,fill='white')
 board.save(qa/'actual_tail_lower_edge_6x.png')
 decoded_hash=[{'frame':f,'sha256':sha(p)} for f,p in enumerate(decoded)]
report={'actual_scene_mp4_sha256':sha(mp),'actual_canvas_frames':120,'actual_decoded_frames':len(decoded_hash),'decoded_all_frame_sha256':decoded_hash,'video_size':[1920,1080],'fps':'24/1','duration_seconds':5,'audio_streams':0,'all12_resource_SHA_match':True,'F108_uses_only_cleaned_SHA':True,'all120_exposure_bindings_match':True,'all120_canvas_original_SHA_match':True,'old_h22_sprite_requested':False,'failed_scene_resource_HTTP':0,'production_EDL_audio_ready_changed':False,'new_image_generation_calls':0,'QA_sheets':['qa/actual_12_states.jpg',*[f'qa/actual_decoded_second_{s}.jpg' for s in range(5)],'qa/actual_tail_lower_edge_6x.png'],'visual_review':'pending author actual image inspection; see separate author_visual_review.json after inspection'}
review_path=D/'provenance/author_visual_review.json'
if review_path.exists():
 review=json.loads(review_path.read_text())
 assert review['actual_mp4_sha256']==report['actual_scene_mp4_sha256']
 report['visual_review']='Completed; see provenance/author_visual_review.json for actual viewed images and scope.'
 report['visual_review_record_sha256']=sha(review_path)
(D/'provenance/actual_scene120_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='decoded_all_frame_sha256'},ensure_ascii=False,indent=2))
