from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parent
chunks=[r/'grandma_front132_pro3_integration_20261020/incoming_library/S14_GRANDMA_HANG_FINAL_000_131_1080p24_SILENT.mp4',p/'actual_three_bridges132_189/S14_THREE_BRIDGES_PULL_TO_ARMS_132_189_58F.mp4']
out=p/'S14_STANDING_THREE_BRIDGES_FULL_190F_1080P24_SILENT.mp4'
if out.exists():raise RuntimeError('Preserve existing assembled movie')
assert hashlib.sha256(chunks[0].read_bytes()).hexdigest()=='6f8475c0984caba2071c6beb4611765918a357e26267966d12be61c57ee8f097'
concat=p/'THREE_BRIDGES_PACKET_SOURCES.txt';concat.write_text(''.join("file '"+str(f)+"'\n" for f in chunks))
subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
def probe(f):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames','-show_entries','format=duration,size','-of','json',str(f)],text=True))
def hashes(f):
 text=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:v:0','-f','framemd5','-'],text=True)
 return [line.split(',')[-1].strip() for line in text.splitlines() if line and not line.startswith('#')]
expected=[];sources=[]
for f in chunks:
 h=hashes(f);expected+=h;sources.append({'path':str(f),'frames':len(h),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
actual=hashes(out);assert actual==expected and len(actual)==190
pr=probe(out);assert pr['streams'][0]['nb_read_frames']=='190' and pr['streams'][0]['r_frame_rate']=='24/1'
record={'status':'COMPLETE190_THREE_BRIDGES_CANDIDATE_PENDING_MOTION_REVIEW','sourceChunks':sources,'fullVideo':{'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},'all190DecodedYUVFrameHashesMatchSourceChunks':True,'grandmaPrefixReencoded':False,'grandmaPrefixRerendered':False,'childFrames':58,'newDrawingStates':13,'newSceneRenders':45,'unchangedPullFramesReusedWithoutSceneRerender':13,'oldTotalFrames':240,'newTotalFrames':190,'EDLShortenedSeconds':50/24,'musicEdited':False,'sharedPush':False,'motionApproval':False,'probe':pr}
(p/'THREE_BRIDGES_FULL_ASSEMBLY_AND_DECODE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
