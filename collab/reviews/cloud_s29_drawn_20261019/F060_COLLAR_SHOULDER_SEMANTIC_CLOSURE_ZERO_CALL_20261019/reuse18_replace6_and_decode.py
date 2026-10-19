"""Assemble already rendered6 with original18. Never browser-renders a frame.

Lossless YUV420 H264 keeps the original18 decoded YUV AND RGB samples exact.
The new6 standard H264 MP4 remains separately available as the actual render.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,hashlib
R=Path(__file__).resolve().parent
H=R.parent/'F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019'
old=H/'S29_F048_F071_ACTUAL_SCENE_1080p24.mp4'
new=R/'S29_F060_F065_ACTUAL_SCENE_1080p24.mp4'
final=R/'S29_F048_F071_REUSED18_REPLACED060_065_LOSSLESS.mp4'
sha=lambda b:hashlib.sha256(b).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def decode(p,pix):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','rawvideo','-pix_fmt',pix,'pipe:1'])
def check_video(p,n):
    d=probe(p);v=next(s for s in d['streams']if s['codec_type']=='video')
    assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',n)
    assert not any(s['codec_type']=='audio'for s in d['streams'])
    return d
plan=json.loads((R/'SOURCES_EXPOSURE_AND_T_LAYER.json').read_text())
assert sha(old.read_bytes())==plan['historical24f']['SHA256']
run=json.loads((R/'ACTUAL_BROWSER_RUN.json').read_text());assert run['pass']and run['sourceUnchanged']
assert[f['globalFrame']for f in run['frames']]==list(range(60,66))
oldprobe=check_video(old,24);newprobe=check_video(new,6)
(R/'FFPROBE_NEW6.json').write_text(json.dumps(newprobe,indent=2)+'\n')
oy=decode(old,'yuv420p');ny=decode(new,'yuv420p');size=1920*1080*3//2
assert len(oy)==size*24 and len(ny)==size*6
parts=[ny[(i-12)*size:(i-11)*size]if 12<=i<18 else oy[i*size:(i+1)*size]for i in range(24)]
joined=b''.join(parts)
assert not final.exists(),'Refusing overwrite of rebuilt24 review; history is separate.'
args=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','yuv420p','-s','1920x1080','-r','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(final)]
result=subprocess.run(args,input=joined,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
fp=check_video(final,24);(R/'FFPROBE_REBUILT24.json').write_text(json.dumps(fp,indent=2)+'\n')
fy=decode(final,'yuv420p');assert fy==joined
orgb=decode(old,'rgb24');nrgb=decode(new,'rgb24');frgb=decode(final,'rgb24');rs=1920*1080*3
assert len(frgb)==rs*24
reuse=[];replacement=[];images={}
keys=R/'actual_decoded_keys';keys.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1920,1620),(225,228,231));draw=ImageDraw.Draw(sheet)
for i in range(24):
    f=i+48;b=frgb[i*rs:(i+1)*rs];im=Image.frombytes('RGB',(1920,1080),b);images[f]=im
    expected=nrgb[(i-12)*rs:(i-11)*rs]if 12<=i<18 else orgb[i*rs:(i+1)*rs]
    assert b==expected,(f,'RGB notexact')
    row={'global_frame':f,'decoded_YUV420_SHA256':sha(fy[i*size:(i+1)*size]),'decoded_RGB24_SHA256':sha(b),'exact_against':'new6actualvideo'if 12<=i<18 else'original24history','differing_RGB_channels':0,'differing_YUV_samples':0}
    (replacement if 12<=i<18 else reuse).append(row)
    if f in [59,60,61,62,63,64,65,66]:im.save(keys/f'S29_F{f:03d}_ACTUAL_DECODED.png')
    sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*270));draw.text(((i%4)*480+8,(i//4)*270+8),f'{f:03d} '+('NEW'if 12<=i<18 else'REUSED'),fill='white',stroke_width=1,stroke_fill='black')
sheet.save(R/'ALL24_REUSED18_NEW6_ACTUAL_DECODED_CONTACT.png')
sw=Image.new('RGB',(540,560),(232,235,239));d=ImageDraw.Draw(sw)
for i,f in enumerate([59,60,65,66]):
    sw.paste(images[f].crop((690,320,960,570)),((i%2)*270,(i//2)*280+30));d.text(((i%2)*270+8,(i//2)*280+9),f'ACTUAL {f:03d} '+('NEW'if f in [60,65]else'REUSED'),fill='black')
sw.save(R/'TWO_SWITCHES_SHOULDER_ACTUAL_OUTPUT_1TO1.png')
before=Image.frombytes('RGB',(1920,1080),orgb[12*rs:13*rs])
ba=Image.new('RGB',(540,280),(232,235,239));d=ImageDraw.Draw(ba)
for i,(im,label)in enumerate([(before,'HISTORY060'),(images[60],'NEW060')]):
    ba.paste(im.crop((690,320,960,570)),(i*270,30));d.text((i*270+8,8),label+' actual1:1',fill='black')
ba.save(R/'HISTORY_VS_NEW060_ACTUAL_SHOULDER_1TO1.png')
report={'status':'ONLY_SIX_BROWSER_FRAMES_REPLACED_OTHER18_EXACT_YUV_AND_RGB_PENDING_VISUAL_REVIEW','new_browser_scene_render_count':6,'new_browser_global_frames':list(range(60,66)),'other18_browser_redrawn':False,'new_generation':0,'history24_SHA256_unchanged':sha(old.read_bytes()),'new6_MP4_SHA256':sha(new.read_bytes()),'rebuilt24_MP4_SHA256':sha(final.read_bytes()),'new6_frames':6,'rebuilt24_frames':24,'fps':'24/1','width':1920,'height':1080,'audio':False,'rebuilt24_codec':next(s for s in fp['streams']if s['codec_type']=='video')['codec_name'],'rebuilt24_profile':next(s for s in fp['streams']if s['codec_type']=='video').get('profile'),'assembly':'Original18 decoded YUV420 planes reused verbatim, replacement6 from new actualrender MP4; losslessH264 qp0 finalencoding preserves everyYUV sample. Independently decodedRGB ofall18 equals original too. New6 standardH264 actualrender remains separate.','ffmpeg_assembly_arguments':args,'ffmpeg_stderr':result.stderr.decode(),'original18_YUV_and_RGB_exact':reuse,'new6_YUV_and_RGB_exact_against_new_actual_render':replacement,'scene_sources_unchanged':run['sourceUnchanged'],'history_directory_modified':False,'ready_claimed':False}
(R/'REUSED18_REPLACEMENT6_ACTUAL_DECODE_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['original18_YUV_and_RGB_exact','new6_YUV_and_RGB_exact_against_new_actual_render','ffmpeg_assembly_arguments']},indent=2))
