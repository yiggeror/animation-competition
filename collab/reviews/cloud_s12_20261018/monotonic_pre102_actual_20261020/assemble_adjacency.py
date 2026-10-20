"""Four new real frames and twelve unchanged actual frames; no full-shot render."""
from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
OUT=P/'actual';OUT.mkdir(exist_ok=True)
CACHE=Path('/tmp/s12_monotonic_reused_actual');CACHE.mkdir(exist_ok=True)
full=ROOT/'collab/reviews/20261020_s12_hair_skin_final/S12_hair_skin_fixed_8s_audio.mp4'
natural=P.parent/'natural102_actual_20261020/actual/S12_094_109_actual.mp4'
def decode(source,start,count,prefix):
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vf',f'trim=start_frame={start}:end_frame={start+count}','-frames:v',str(count),'-fps_mode','passthrough',str(CACHE/(prefix+'%02d.png'))],check=True)
 return [CACHE/(prefix+f'{i+1:02d}.png') for i in range(count)]
first=decode(full,90,4,'old90_')
last=decode(natural,8,8,'natural102_')
new=[P/'new_actual_keys'/f'F{f}.png' for f in [94,95,98,99]]
frames=first+new+last
silent=OUT/'S12_monotonic_adjacency_16f.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
for path in frames:proc.stdin.write(path.read_bytes())
proc.stdin.close();assert proc.wait()==0
audio=CACHE/'original_interval.m4a'
subprocess.run(['ffmpeg','-v','error','-y','-ss','3.75','-i',str(full),'-t',str(16/24),'-vn','-c:a','copy',str(audio)],check=True)
video=OUT/'S12_monotonic_adjacency_16f_original_audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(16/24),'-movflags','+faststart',str(video)],check=True)
def packets(f,kind):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams',kind,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(f)]))['packets']
source_hashes={p['data_hash'] for p in packets(full,'a:0')}
assert all(p['data_hash'] in source_hashes for p in packets(video,'a:0'))
assert packets(silent,'v:0')==packets(video,'v:0')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(vs['nb_read_frames'])==16 and vs['r_frame_rate']=='24/1'
plan=[]
for n,path in enumerate(frames):
 source_f=90+n if n<6 else 98+n-6 if n<8 else 102+n-8
 plan.append({'outputFrame':n,'diagnosticTimelineFrame':90+n,'sourceActualFrame':source_f,'kind':'new_browser_actual' if 4<=n<8 else 'reused_actual_decoded_png','actualPNG':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
record={'status':'SHORT_PHASE_TIMING_DIAGNOSTIC_NOT_FINAL_EDL','newSourceCommit':'0825f3ad10fc53de57d3d688b16c40222aa992f1','newSourceSHA256':'8b604715c01cc71e50ad8360b3aa5dea39a873bffcfc2d95a2ab4964f4491f5f','frames':16,'fps':24,'videoSeconds':16/24,'containerSeconds':float(probe['format']['duration']),'newBrowserFrames':4,'reusedDecodedActualFrames':12,'full8sEDLChanged':False,'tail':'Known bad110+ not rerendered, new source pending from author','audio':'Corresponding original sourceAAC packets directly copied; no encoding/mix change','source90MovieSHA256':hashlib.sha256(full.read_bytes()).hexdigest(),'source102106MovieSHA256':hashlib.sha256(natural.read_bytes()).hexdigest(),'output':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'framePlan':plan}
(OUT/'delivery_and_frame_plan.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='framePlan'},ensure_ascii=False))
