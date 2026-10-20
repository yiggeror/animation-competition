"""Exact actualPNG106 plus seven necessary changed optical/110 frames."""
from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];OUT=P/'actual';OUT.mkdir(exist_ok=True)
full=ROOT/'collab/reviews/20261020_s12_hair_skin_final/S12_hair_skin_fixed_8s_audio.mp4'
frames=[P.parent/'natural102_actual_20261020/actual/F106.png']+[P/'new_actual_keys'/f'F{f}.png' for f in range(107,114)]
silent=OUT/'S12_106_113_actual.mp4'
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
for p in frames:proc.stdin.write(p.read_bytes())
proc.stdin.close();assert proc.wait()==0
audio=Path('/tmp/s12_tail110_original_audio.m4a')
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(106/24),'-i',str(full),'-t',str(8/24),'-vn','-c:a','copy',str(audio)],check=True)
video=OUT/'S12_106_113_actual_original_audio.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(8/24),'-movflags','+faststart',str(video)],check=True)
def packets(f,kind):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams',kind,'-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(f)]))['packets']
source_hashes={p['data_hash'] for p in packets(full,'a:0')};assert all(p['data_hash'] in source_hashes for p in packets(video,'a:0'));assert packets(silent,'v:0')==packets(video,'v:0')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(OUT/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(vs['nb_read_frames'])==8 and vs['r_frame_rate']=='24/1'
record={'status':'TRUE106110_ADJACENCY_AND132_SINGLE_FRAME;TAIL_ACTIONS_PENDING','sourceCommit':'1132fc467abe0faf0496e3e77bbd102042ae619b','bodySHA256':'93bf8635caf24f2113813971a377a86241f61567c60b37fda52ea70c8132cfce','sourceRangeInclusive':[106,113],'frames':8,'fps':24,'videoSeconds':8/24,'containerSeconds':float(probe['format']['duration']),'reusedTruePNGFrames':[106],'new110Frames':[110,111,112,113],'newOpticalOnlyFrames':[107,108,109],'additionalActualKey':132,'newBrowserFramesTotal':8,'opticalTransmission':{'106':0,'107':0.15625,'108':0.5,'109':0.84375,'110':1},'unchanged':'Complete body/palms, true paper joints and finite lengths, scene lights/camera, original audioAAC and final8s file','missingActions':['120/126 genuine small lift and return','144 whole head-neck down-gaze and settle'],'filmEDLChanged':False,'originalAudioPacketPayloadsVerified':True,'videoPayloadEqualSilentActual':True,'sourceFinalMovieSHA256':hashlib.sha256(full.read_bytes()).hexdigest(),'output':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'actualPNGInputs':[{'frame':106+i,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(frames)]}
(OUT/'delivery_and_consumption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='actualPNGInputs'},ensure_ascii=False))
