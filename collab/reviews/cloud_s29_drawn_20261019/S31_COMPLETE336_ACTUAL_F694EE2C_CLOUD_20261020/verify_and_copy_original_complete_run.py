"""Verify/copy the ONE existing full run. Never launches any scene renderer."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, subprocess, shutil, datetime, numpy as np

R=Path(__file__).resolve().parent
receipt_path=Path('/tmp/s31_complete_336_f694ee2c_launch.json')
receipt=json.loads(receipt_path.read_text()); source=Path(receipt['cwd'])
out=Path(receipt['outputDirectory']); log_path=out/'EXECUTION_LOG.json'
assert log_path.exists(), 'Original run still pending; continue waiting, never restart.'
log=json.loads(log_path.read_text())
assert log['status']=='passed', 'Original run failed; preserve actual result, never restart.'
assert receipt['fixedCommit']=='f694ee2c3b36aa21c1476faa7268a96148f820f4'
assert receipt['pid']==11232
assert (log['renderedFrames'],log['expectedFrames'],log['width'],log['height'],log['fps'])==(336,336,1920,1080,24)
assert [p['frame'] for p in log['pngs']]==[0,36,116,179,180,335]
assert log['originalBSelfRepeat']['containsA'] is False
assert log['boundary']['frame']==180 and log['boundary']['exactMatch']
assert log['boundary']['differingChannels']==log['boundary']['maxAbsoluteDifference']==log['boundary']['totalAbsoluteDifference']==0
assert log['boundary']['referenceSHA256']==log['boundary']['afterASHA256']==log['originalBSelfRepeat']['repeatSHA256']
assert not log['requestFailed'] and not log['pageErrors']
assert all(r['status']<400 or r['url'].endswith('/favicon.ico') for r in log['responses'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=[]
for path,before in receipt['all42PackageFilesBefore'].items():
    after=sha(source/path); assert before==after,path
    frozen.append({'path':path,'beforeSHA256':before,'afterSHA256':after,'exact':True})
assert len(frozen)==42 and len(receipt['runtime40Exact'])==40
video=out/'S31_COMPLETE_336_VIDEO_ONLY.mp4'
assert video.exists() and not (out/'S31_COMPLETE_336_VIDEO_ONLY.partial.mp4').exists()
assert sha(video)==log['video']['sha256']
assert sorted(p.name for p in out.glob('F*.png'))==[f'F{n:03d}.png' for n in [0,36,116,179,180,335]]
assert not (R/'S31_COMPLETE_336_VIDEO_ONLY.mp4').exists(), 'Fixed delivery already copied; inspect instead of overwrite.'
probe_cmd=['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]
probe=json.loads(subprocess.check_output(probe_cmd))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1','24/1',336)
assert abs(float(v['duration'])-14)<1e-6 and abs(float(probe['format']['duration'])-14)<1e-6
assert not any(s['codec_type']=='audio' for s in probe['streams'])
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
(R/'INDEPENDENT_FULL336_FFPROBE.json').write_text(json.dumps(probe,indent=2)+'\n')
decode_cmd=['ffmpeg','-v','error','-xerror','-i',str(video),'-map','0:v:0','-pix_fmt','yuv420p','-f','framehash','-hash','sha256','pipe:1']
decoded=subprocess.run(decode_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
assert not decoded.stderr,decoded.stderr.decode()
framehash=decoded.stdout.decode(); rows=[s for s in framehash.splitlines() if s and not s.startswith('#')]
assert len(rows)==336
parsed=[[s.strip() for s in row.split(',')] for row in rows]
assert [int(r[2]) for r in parsed]==list(range(336))
assert all(int(r[4])==1920*1080*3//2 for r in parsed)
(R/'ACTUAL336_DECODED_YUV420_FRAMEHASH.txt').write_text(framehash)
selected=[0,12,36,48,66,69,75,96,108,110,112,114,116,120,129,164,179,180,192,204,216,228,240,264,288,312,324,335]
assert len(selected)==len(set(selected))==28
vf='select='+ '+'.join(f'eq(n\\,{f})' for f in selected)
rgb_cmd=['ffmpeg','-v','error','-xerror','-i',str(video),'-vf',vf,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
sampled=subprocess.run(rgb_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
assert not sampled.stderr,sampled.stderr.decode()
size=1920*1080*3; assert len(sampled.stdout)==size*len(selected)
sheet=Image.new('RGB',(1920,2030),(232,235,239)); draw=ImageDraw.Draw(sheet)
sample_rows=[]; images={}
for i,f in enumerate(selected):
    data=sampled.stdout[i*size:(i+1)*size]; im=Image.frombytes('RGB',(1920,1080),data);images[f]=im
    x=i%4*480;y=i//4*290
    sheet.paste(im.resize((480,270)),(x,y+20));draw.text((x+8,y+3),f'ACTUAL MP4 F{f:03d}',fill='black')
    sample_rows.append({'frame':f,'actualDecodedRGB24SHA256':hashlib.sha256(data).hexdigest()})
sheet.save(R/'ACTUAL_MP4_28_SAMPLES_CONTACT.png')
keys=[]; key_sheet=Image.new('RGB',(1920,1680),(232,235,239));draw=ImageDraw.Draw(key_sheet)
for i,row in enumerate(log['pngs']):
    p=out/row['filename'];assert sha(p)==row['sha256']
    with Image.open(p) as im:
        assert im.format=='PNG' and im.size==(1920,1080);im.verify()
    im=Image.open(p).convert('RGB'); a=np.asarray(im,dtype=np.int16); b=np.asarray(images[row['frame']],dtype=np.int16)
    d=np.abs(a-b)
    keys.append({**row,'copiedByteExact':True,'lossyVideoVsOriginalPNG_RGB_MAE':float(d.mean()),'lossyVideoVsOriginalPNG_RGB_maxAbsoluteDifference':int(d.max())})
    shutil.copyfile(p,R/p.name);assert sha(p)==sha(R/p.name)
    x=i%2*960;y=i//2*560;key_sheet.paste(im.resize((960,540)),(x,y+20));draw.text((x+8,y+3),f'ORIGINAL PNG F{row["frame"]:03d}',fill='black')
key_sheet.save(R/'SIX_ORIGINAL_PNG_CONTACT.png')
shutil.copyfile(video,R/video.name);assert sha(video)==sha(R/video.name)
shutil.copyfile(log_path,R/'EXECUTION_LOG.json')
shutil.copyfile(receipt_path,R/'ORIGINAL_LAUNCH_RECEIPT.json')
shutil.copyfile(receipt['stdoutLog'],R/'ORIGINAL_RUN_STDOUT.log')
observer=Path('/tmp/s31_complete_336_f694ee2c_observation.jsonl')
if observer.exists():shutil.copyfile(observer,R/'READ_ONLY_RUN_OBSERVATIONS.jsonl')
for name in ['S31_COMPLETE_CANDIDATE_BINDINGS.json','S31_COMPLETE_RUNTIME_RELOCATION.json']:
    shutil.copyfile(source/name,R/name)
shutil.copyfile(source/'README.md',R/'FROZEN_SOURCE_README.md')
shutil.copyfile(source/'scene_preview/render_complete_serial.cjs',R/'ORIGINAL_RENDER_COMPLETE_SERIAL.cjs')
report={'status':'TECHNICAL_PASS_PENDING_COMPLETED_ACTUAL_VISUAL_REVIEW','checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixedCommit':receipt['fixedCommit'],'originalRenderPID':receipt['pid'],'newSceneRendersInVerification':0,'newGenerationCalls':0,'originalFullRunCount':1,'actualVideo':{'file':video.name,'SHA256':sha(video),'bytes':video.stat().st_size,'frames':336,'fps':'24/1','durationSeconds':14,'width':1920,'height':1080,'audio':False,'byteExactCopy':True},'independentFull336Decode':{'exitCode':decoded.returncode,'stderr':decoded.stderr.decode(),'decodedFrameCount':len(rows),'firstPTS':0,'lastPTS':335,'allYUV420SizesExact':True,'command':decode_cmd},'independentOriginalBSelfRepeat':log['originalBSelfRepeat'],'exactB180Boundary':log['boundary'],'sixOriginalPNGs':keys,'all42FrozenPackageFiles':frozen,'frozen40RuntimeFilesExact':True,'originalExecutionLogByteExact':sha(log_path)==sha(R/'EXECUTION_LOG.json'),'no336PNGSequenceWritten':True,'sampledMP4FramesInOneContactSheetOnly':sample_rows,'probeCommand':probe_cmd,'RGBSampleCommand':rgb_cmd,'wholeShotReadyClaimed':False}
(R/'COMPLETE_ACTUAL_RUN_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','fixedCommit','originalRenderPID','originalFullRunCount','actualVideo','independentOriginalBSelfRepeat','exactB180Boundary','originalExecutionLogByteExact','no336PNGSequenceWritten']},ensure_ascii=False,indent=2))
