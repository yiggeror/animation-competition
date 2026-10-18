#!/usr/bin/env python3
"""Compare the authorized one-line timing change and decode the real scene MP4."""
from pathlib import Path
import csv,hashlib,json,math,shutil,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;D=HERE.parent;REPO=D.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((HERE/'provenance/authorization_and_baseline.json').read_text());manifest=json.loads((D/'provenance/actual_scene120_manifest.json').read_text());movie=D/manifest['clip'];before_movie=Path('/tmp/S22_before_turtle_timing_fix.mp4')
if not before_movie.exists() or sha(before_movie)!=baseline['before_scene_mp4_sha256']:
 with before_movie.open('wb') as fp:
  subprocess.run(['git','show',baseline['base_commit']+':'+str(movie.relative_to(REPO))],cwd=REPO,stdout=fp,check=True)
assert sha(movie)==manifest['sha256'];assert sha(before_movie)==baseline['before_scene_mp4_sha256']
before=(HERE/'provenance/before_S22_drawn.js.txt').read_text();after=(D/'S22_drawn.js').read_text();assert before.replace('sstep(1.4+k,1.72+k,t)','sstep(1.5+k,1.82+k,t)')==after
for f,digest in baseline['locked_binding_files_sha256'].items():assert sha(D/f)==digest,f
for r in baseline['locked12_resources']:assert sha(REPO/r['url'].lstrip('/'))==r['sha256'],r['id']
assert manifest['module_sha256']==sha(D/'S22_drawn.js')
previous_manifest=json.loads((HERE/'provenance/before_actual_scene120_manifest.json').read_text())
changed_canvas_frames=[a['frame'] for a,b in zip(previous_manifest['frame_sha256'],manifest['frame_sha256']) if a['sha256']!=b['sha256']]
expected_curve_frames=[f for k in range(4) for f in range(34+24*k,44+24*k)]
assert set(changed_canvas_frames).issubset(expected_curve_frames),changed_canvas_frames
assert all(any(f in changed_canvas_frames for f in range(34+24*k,44+24*k)) for k in range(4))
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def step(t,start):return sum(smooth(start+k,start+.32+k,t) for k in range(4))
frames=[n for start in [36,60,84,108] for n in [start-1,start,start+1]];rows=[]
for start in [36,60,84,108]:
 k=(start-36)//24
 for f in [start-1,start,start+1]:
  t=f/24;old=step(t,1.4);new=step(t,1.5);pose=next(r['id'] for r in baseline['locked12_resources'] if r['start']<=f<=r['end']);rows.append({'push':k+1,'frame':f,'time_seconds':f'{t:.8f}','position':['before','start','after'][f-start+1],'human_state':pose,'old_turtleStep':f'{old:.10f}','new_turtleStep':f'{new:.10f}','new_walk_parameter':1 if .02<new%1<.98 else .15})
  if f<=start:assert abs(new-k)<1e-12
  else:assert new>k
  if f==start-1:assert old>k+.08
with (HERE/'timing_comparison.csv').open('w',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
selector='select='+ '+'.join(f'eq(n\\,{f})' for f in frames)
with tempfile.TemporaryDirectory(prefix='s22_timing_decode_') as td:
 td=Path(td)
 for label,mp in [('before',before_movie),('after',movie)]:
  dest=td/label;dest.mkdir();subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp),'-vf',selector,'-fps_mode','vfr','-start_number','0',str(dest/'%03d.png')],check=True)
  assert len(list(dest.glob('*.png')))==12
  if label=='after':
   for j,f in enumerate(frames):shutil.copyfile(dest/f'{j:03d}.png',HERE/'decoded_actual'/f'F{f:03d}.png')
 # Full actual new scene triplets:4 rows x3 frames, originals retained above.
 board=Image.new('RGB',(1920,1560),(24,24,24));dr=ImageDraw.Draw(board)
 for j,row in enumerate(rows):
  x=(j%3)*640;y=(j//3)*390;im=Image.open(td/'after'/f'{j:03d}.png').convert('RGB').resize((640,360));board.paste(im,(x,y+30));dr.text((x+7,y+5),f"Push{row['push']} / F{row['frame']:03d} / {row['human_state']} / {row['position']}",font=font,fill='white')
 board.save(HERE/'qa/actual_four_push_triplets.jpg',quality=95)
 # Per-push before/after turtle crops from the old and new actual films.
 for g,start in enumerate([36,60,84,108]):
  board=Image.new('RGB',(1920,810),(24,24,24));dr=ImageDraw.Draw(board)
  for r,label in enumerate(['before','after']):
   for k in range(3):
    j=g*3+k;f=frames[j];im=Image.open(td/label/f'{j:03d}.png').convert('RGB').crop((1040,20,1920,530)).resize((640,371));board.paste(im,(k*640,r*405+34));st=rows[j]['old_turtleStep' if label=='before' else 'new_turtleStep'];dr.text((k*640+7,r*405+7),f'{label.upper()} F{f:03d} / step{st}',font=font,fill='white')
  board.save(HERE/'qa'/f'push_F{start:03d}_before_after.jpg',quality=95)
result={'base_commit':baseline['base_commit'],'before_scene_mp4_sha256':baseline['before_scene_mp4_sha256'],'after_scene_mp4_sha256':sha(movie),'before_module_sha256':baseline['before_module_sha256'],'after_module_sha256':sha(D/'S22_drawn.js'),'one_line_curve_change_only':True,'changed_actual_Canvas_frames':changed_canvas_frames,'unchanged_actual_Canvas_frames_outside_four_curve_windows':120-len(changed_canvas_frames),'old_intervals':[[1.4+k,1.72+k] for k in range(4)],'new_intervals':[[1.5+k,1.82+k] for k in range(4)],'new_start_frames':[36,60,84,108],'all12_image_SHA_unchanged':True,'resource_map_JSON_JS_exposure_CSV_tail_lock_byte_identical':True,'actual_decoded_requested_frames':frames,'actual_decoded_requested_frame_SHA256':{f'F{f:03d}':sha(HERE/'decoded_actual'/f'F{f:03d}.png') for f in frames},'timing_comparison':rows,'rest_turtlePose_time_and_walk_logic_unchanged':True,'scene_camera_light_colour_code_unchanged':True,'audio_integrated':False,'production_ready':False,'shared_EDL_audio_ready_changed':False,'new_image_generation_calls':0}
(HERE/'provenance/timing_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['timing_comparison','actual_decoded_requested_frame_SHA256']},ensure_ascii=False,indent=2))
