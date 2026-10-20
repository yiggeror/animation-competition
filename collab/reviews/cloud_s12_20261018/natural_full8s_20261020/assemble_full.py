"""One192-frame S12: unchanged final colour footage + adopted natural PNGs.

Use --render-missing after extracting the cumulative delta into the same repo.
Only missing actual sourcePNGs are rendered; source art and old audio stay fixed.
"""
from pathlib import Path
import argparse,collections,hashlib,json,subprocess

P=Path(__file__).resolve().parent;ROOT=P.parents[3];REVIEW=P.parent
OUT=P/'actual';OUT.mkdir(exist_ok=True)
CACHE=Path('/tmp/s12_natural_full8s_cache');CACHE.mkdir(exist_ok=True)
NEW=Path('/tmp/s12_full8s_new_actual')
SOURCE=ROOT/'collab/reviews/20261020_s12_hair_skin_final/S12_hair_skin_fixed_8s_audio.mp4'
SOURCE_SHA='4f0568b1c4727fda92be05dac275d58afbf2c4354868ca0e2cc6b2a8b045d5e5'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
args=argparse.ArgumentParser();args.add_argument('--render-missing',action='store_true');args=args.parse_args()
plan=[]
def add(out,source,path,module=None,body=None):
 plan.append({'outputFrame':out,'sourceActualFrame':source,'path':str(path),'module':module,'bodyPhase':body,'retimed':out!=source})
def mod(folder,name):return str((REVIEW/folder/name).relative_to(ROOT))
base=lambda f:CACHE/f'F{f:03d}.png'
for f in range(90):add(f,f,base(f),body='unchanged_final_colour_footage')
for f,s in zip(range(90,95),[90,91,92,93,93]):add(f,s,base(s),body='original90')
for f,s in zip(range(95,100),[94,95,98,99,99]):add(f,s,REVIEW/'monotonic_pre102_actual_20261020/new_actual_keys'/f'F{s}.png',mod('monotonic_pre102_actual_20261020','s12_monotonic_candidate.js'),'natural_pre102')
for f,s in zip(range(100,105),[102,103,104,105,105]):add(f,s,REVIEW/'natural102_actual_20261020/actual/F102.png' if s==102 else NEW/'source103105'/f'F{s}.png',mod('natural102_actual_20261020','s12_natural102_candidate.js'),'natural102')
for f,s in zip(range(105,110),[106,107,108,109,109]):add(f,s,REVIEW/'natural102_actual_20261020/actual/F106.png' if s==106 else REVIEW/'natural_tail110_actual_20261020/new_actual_keys'/f'F{s}.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural106')
for f in range(110,114):add(f,f,REVIEW/'natural_tail110_actual_20261020/new_actual_keys'/f'F{f}.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural110')
for f in range(114,120):add(f,f,REVIEW/'natural_peak120_actual_20261020/baseline114119_actual_keys'/f'F{f}.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural110')
for f in range(120,126):add(f,f,REVIEW/'natural_peak120_actual_20261020/new_actual_keys'/f'F{f}.png',mod('natural_peak120_actual_20261020','s12_natural_peak120_candidate.js'),'natural120_peak')
for f in range(126,132):add(f,f,REVIEW/'natural_return126_actual_20261020/new_actual_keys'/f'F{f}.png',mod('natural_return126_actual_20261020','s12_natural_return126_candidate.js'),'natural126_partial_return')
add(132,132,REVIEW/'natural_tail110_actual_20261020/new_actual_keys/F132.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural132_baseline')
for f in range(133,138):add(f,f,REVIEW/'natural_return126_actual_20261020/baseline133137_actual_keys'/f'F{f}.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural132_baseline')
for f in range(138,144):add(f,f,NEW/'baseline138143'/f'F{f}.png',mod('natural_tail110_actual_20261020','s12_natural_tail110_candidate.js'),'natural132_baseline')
for f in range(144,192):
 folder='gaze144159' if f<160 else 'gaze160175' if f<176 else 'gaze176191'
 add(f,f,NEW/folder/f'F{f}.png',mod('natural_gaze144_actual_20261020','s12_natural_gaze144_candidate.js'),'natural144_gaze_and_response')
assert len(plan)==192 and [p['outputFrame'] for p in plan]==list(range(192))
if not all(base(f).exists() for f in range(94)):
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(SOURCE),'-vf','trim=end_frame=94','-frames:v','94','-fps_mode','passthrough','-start_number','0',str(CACHE/'F%03d.png')],check=True)
missing=[p for p in plan if not Path(p['path']).exists()]
if missing and args.render_missing:
 groups=collections.defaultdict(set)
 for p in missing:groups[(str(Path(p['path']).parent),p['module'])].add(p['sourceActualFrame'])
 for (out,module),frames in groups.items():
  frames=sorted(frames)
  for start in range(0,len(frames),16):
   chunk=frames[start:start+16]
   subprocess.run(['node',str(REVIEW/'natural102_actual_20261020/render_stream.cjs'),out,'--module',module,'--first',str(min(chunk)),'--last',str(max(chunk)),'--preview','--keys',','.join(map(str,chunk))],cwd=ROOT,check=True)
assert all(Path(p['path']).is_file() for p in plan),'Missing actual PNGs; run --render-missing'
silent=CACHE/'S12_full_silent_staging.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
for p in plan:proc.stdin.write(Path(p['path']).read_bytes())
proc.stdin.close();assert proc.wait()==0
video=OUT/'S12_natural_fixed_8s_original_audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(video)],check=True)
def packets(f,kind):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams',kind,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(f)]))['packets']
assert packets(video,'a:0')==packets(SOURCE,'a:0'),'Original fullAAC payload changed'
assert packets(video,'v:0')==packets(silent,'v:0')
def pcm_hash(f):
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a:0','-f','f32le','-'])
 return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
original_pcm=pcm_hash(SOURCE);assert pcm_hash(video)==original_pcm,'Original decoded audio differs'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(vs['nb_read_frames'])==192 and vs['r_frame_rate']=='24/1' and float(vs['duration'])==8 and float(probe['format']['duration'])==8
for p in plan:
 path=Path(p['path']);p['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 if path.is_relative_to(ROOT):p['path']=str(path.relative_to(ROOT))
record={'status':'FULL192_ACTUAL_AWAITING_VISUAL_REVIEW','fps':24,'frames':192,'seconds':8,'originalSource':str(SOURCE.relative_to(ROOT)),'originalSourceSHA256':SOURCE_SHA,'originalAACPacketPayloadsIdentical':True,'decodedAudioIdentical':original_pcm,'filmEDLChanged':False,'entryExposure':[{'output':[90,94],'phase':'old90','count':5},{'output':[95,99],'phase':'near_terminal94/98','count':5},{'output':[100,104],'phase':'natural102','count':5},{'output':[105,109],'phase':'natural106','count':5}],'entryReason':'Same original20-frame interval, balanced5/5/5/5 exposure; no new whole-body drawing, no extension of the film or audio; new near-terminal body5frames rather than8.','uniqueActualPNGInputs':len({p['path'] for p in plan}),'originalUnchangedFirst90FramesDecodedAndReused':True,'noOldBadTailBodyLoaded':True,'output':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'framePlan':plan}
(OUT/'delivery_and_frame_plan.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='framePlan'},ensure_ascii=False))
