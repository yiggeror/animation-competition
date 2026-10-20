"""Copy published prefix packets + the actual108-frame return; verify240 decoded frames."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parent
tailOriginal=Path('/tmp/s14_actual_backstage132_239_108frames_20261020')
tail=R/'actual_backstage132_239'
assembled=R/'assembled'
final=assembled/'S14_FULL240_10S_BACKSTAGE_CANDIDATE.mp4'
if tail.exists() or final.exists():raise RuntimeError('Existing deliverables retained; no overwrite')
log=json.loads((tailOriginal/'EXECUTION_LOG.json').read_text())
assert len(log['renderedFrames'])==108 and log['status']=='TECHNICAL_COMPLETE_PENDING_ACTUAL_VISUAL_REVIEW'
assert log['backstageOcclusion']['visibleHeadAndRaisedArmsPixelsInOriginalRoom']==0
tail.mkdir()
for p in tailOriginal.iterdir():
 if p.suffix in {'.mp4','.png','.json'}:shutil.copy2(p,tail/p.name)
for name in ['s14_scene.mjs','s14_tail.mjs','preview.html','render_actual.cjs','BACKSTAGE_RETURN_132_167_EXPOSURE_PROPOSAL.json','BACKSTAGE_INPUTS_AT_RENDER.json']:
 shutil.copy2(R/name,tail/('SOURCE_AT_RENDER_'+name))
def run(args):
 r=subprocess.run(args,check=True,capture_output=True)
 if r.stderr:raise RuntimeError(r.stderr.decode())
 return r.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(p):return [s.rsplit(',',1)[-1].strip() for s in p.read_text().splitlines() if s and not s.startswith('#')]
def decode(video,destination):
 destination.write_bytes(run(['ffmpeg','-v','error','-xerror','-i',str(video),'-an','-f','framehash','-hash','sha256','-']))
prefix=assembled/'S14_PREFIX000_131_132F_CUT_GATE_PENDING.mp4'
chunks=assembled/'BACKSTAGE_SOURCE_CHUNKS.txt'
chunks.write_text('\n'.join("file '"+str(p)+"'" for p in [prefix,tail/'S14_ACTUAL_SEGMENT.mp4'])+'\n')
run(['ffmpeg','-n','-v','error','-f','concat','-safe','0','-i',str(chunks),'-c','copy','-movflags','+faststart',str(final)])
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)]))
v=probe['streams'][0]
assert len(probe['streams'])==1 and v['codec_type']=='video'
assert int(v['nb_read_frames'])==240 and v['r_frame_rate']=='24/1' and (v['width'],v['height'])==(1920,1080)
assert abs(float(probe['format']['duration'])-10)<1e-6
decode(tail/'S14_ACTUAL_SEGMENT.mp4',tail/'ACTUAL108_COMPLETE_DECODE_FRAMEHASH.txt')
fullHash=assembled/'ACTUAL_FULL240_DECODE_FRAMEHASH.txt'
decode(final,fullHash)
expected=[]
for folder in ['actual_grandma000_017','actual_grandma018_029','actual_grandma030_095','actual_close096_131']:
 files=list((R/folder).glob('*FRAMEHASH.txt'));assert len(files)==1
 expected.extend(hashes(files[0]))
assert len(expected)==132 and hashes(fullHash)==expected+hashes(tail/'ACTUAL108_COMPLETE_DECODE_FRAMEHASH.txt')
encoded=assembled/'encoded_cut_keys';encoded.mkdir()
run(['ffmpeg','-n','-v','error','-i',str(final),'-vf','select=eq(n\\,95)+eq(n\\,96)+eq(n\\,131)+eq(n\\,132)','-fps_mode','vfr',str(encoded/'CUT_%02d.png')])
mapping=[]
board=Image.new('RGB',(1920,1120),'#171a1d');draw=ImageDraw.Draw(board)
for i,f in enumerate([95,96,131,132]):
 p=encoded/f'CUT_{i+1:02d}.png';im=Image.open(p).convert('RGB');x=(i%2)*960;y=(i//2)*560
 board.paste(im.resize((960,540)),(x,y+20));draw.text((x+8,y+4),f'ACTUAL ENCODED F{f:03d}',fill='white')
 mapping.append({'frame':f,'path':str(p.relative_to(R)),'sha256':sha(p)})
board.save(assembled/'ACTUAL_ENCODED_095_096_131_132_CUTS.jpg',quality=94)
rec={
 'status':'COMPLETE240_FRAME10_SECOND_CANDIDATE_PENDING_DIRECTOR_AND_WORLD_REVIEW',
 'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'file':str(final.relative_to(R)),'sha256':sha(final),'bytes':final.stat().st_size,
 'sourceMP4s':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in [prefix,tail/'S14_ACTUAL_SEGMENT.mp4']],
 'assembly':'ffmpeg concat demuxer, H264 packet copy. Original000–131 decoded hashes all132 match published segment hashes; new108 decoded hashes also match exactly.',
 'decodeVerifiedFrames':240,'frameRate':'24/1','durationSeconds':10,'width':1920,'height':1080,'audioStreams':0,
 'fullDecodedSequenceExactlyMatchesSourceChunks':True,
 'backstageOcclusion':log['backstageOcclusion'],
 'encodedCutFrames':mapping,'probe':probe,
 'newImageGenerationCalls':0,'newDrawings':0,
 'reviewPending':['095→096 cut omits stool descent/approach/bend.','131→132 return-cut staging and proposed132–167 child exposure timing.','S15 world/camera correspondence is not proved by2D original-painted-room registration.','179→180 adopted head/neck pose change remains visible for director judgment.'],
 'notClaimed':'Not a ready/EDL/audio update or final director approval. NoS15 changes.'
}
(assembled/'FULL240_ASSEMBLY_AND_DECODE.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:rec[k] for k in ['status','file','sha256','bytes','decodeVerifiedFrames','backstageOcclusion']},ensure_ascii=False))
