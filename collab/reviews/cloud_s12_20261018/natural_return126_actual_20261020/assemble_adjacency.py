"""Reuse110–113 exact actualPNGs, render only unretained114–119 and120–125 natural peak."""
from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];OUT=P/'actual';OUT.mkdir(exist_ok=True)
full=ROOT/'collab/reviews/20261020_s12_hair_skin_final/S12_hair_skin_fixed_8s_audio.mp4'
frames=[P.parent/'natural_tail110_actual_20261020/new_actual_keys'/f'F{f}.png' for f in range(110,114)]+[P.parent/'natural_peak120_actual_20261020/baseline114119_actual_keys'/f'F{f}.png' for f in range(114,120)]+[P.parent/'natural_peak120_actual_20261020/new_actual_keys'/f'F{f}.png' for f in range(120,126)]+[P/'new_actual_keys'/f'F{f}.png' for f in range(126,132)]+[P.parent/'natural_tail110_actual_20261020/new_actual_keys/F132.png']+[P/'baseline133137_actual_keys'/f'F{f}.png' for f in range(133,138)]
silent=OUT/'S12_110_137_actual.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
for p in frames:proc.stdin.write(p.read_bytes())
proc.stdin.close();assert proc.wait()==0
audio=Path('/tmp/s12_return126_original_audio.m4a')
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(110/24),'-i',str(full),'-t',str(28/24),'-vn','-c:a','copy',str(audio)],check=True)
video=OUT/'S12_110_137_actual_original_audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(28/24),'-movflags','+faststart',str(video)],check=True)
def packets(f,kind):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams',kind,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(f)]))['packets']
source_hashes={p['data_hash'] for p in packets(full,'a:0')};assert all(p['data_hash'] in source_hashes for p in packets(video,'a:0'));assert packets(silent,'v:0')==packets(video,'v:0')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(vs['nb_read_frames'])==28 and vs['r_frame_rate']=='24/1'
record={'status':'TRUE110120126132_LIFT_RETURN_ACTUAL;GAZE144_PENDING','sourceCommit':'bf114cee35ce85be628a50be34a1afa12e7aa055','bodySHA256':'3d3b35f2d1da9090556758194f332958df2b88b75f917a7935d2e35facc5ee29','sourceRangeInclusive':[110,137],'frames':28,'fps':24,'videoSeconds':28/24,'containerSeconds':float(probe['format']['duration']),'reusedTruePNGFrames':list(range(110,126))+[132],'newReturnFrames':list(range(126,132)),'newBaselineFrames':list(range(133,138)),'newBrowserFramesTotal':11,'timing':'Exact original110–137 source time and originalAAC; no filmEDL edit','missingActions':['144 whole head-neck down-gaze and settle'],'filmEDLChanged':False,'originalAudioPacketPayloadsVerified':True,'videoPayloadEqualSilentActual':True,'sourceFinalMovieSHA256':hashlib.sha256(full.read_bytes()).hexdigest(),'output':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'actualPNGInputs':[{'frame':110+i,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(frames)]}
(OUT/'delivery_and_consumption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='actualPNGInputs'},ensure_ascii=False))
