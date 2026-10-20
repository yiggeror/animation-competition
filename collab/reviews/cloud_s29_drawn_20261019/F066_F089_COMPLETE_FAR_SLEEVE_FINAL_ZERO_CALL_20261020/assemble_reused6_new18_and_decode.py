"""Reuse old066–071; join newly rendered072–089. No browser rendering here."""
from pathlib import Path
from PIL import Image, ImageDraw
import subprocess, json, hashlib

R = Path(__file__).resolve().parent
plan = json.loads((R/'SOURCES_EXPOSURE_AND_T_LAYER.json').read_text())
old = Path(plan['historical24f']['path'])
new = R/'S29_F072_F089_NEW18_ACTUAL_SCENE_1080p24.mp4'
final = R/'S29_F066_F089_REUSED6_NEW18_ACTUAL_1080p24_SILENT.mp4'
sha = lambda b: hashlib.sha256(b).hexdigest()
def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def decode(p,pix):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','rawvideo','-pix_fmt',pix,'pipe:1'])
def check(p,n):
    d=probe(p); v=next(s for s in d['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',n)
    assert not any(s['codec_type']=='audio' for s in d['streams'])
    return d
assert sha(old.read_bytes()) == plan['historical24f']['SHA256']
run=json.loads((R/'ACTUAL_BROWSER_RUN.json').read_text())
assert run['pass'] and run['sourceUnchanged']
assert [f['globalFrame'] for f in run['frames']]==list(range(72,90))
op=check(old,24); np=check(new,18)
(R/'FFPROBE_NEW18.json').write_text(json.dumps(np,indent=2)+'\n')
oy=decode(old,'yuv420p'); ny=decode(new,'yuv420p'); size=1920*1080*3//2
assert len(oy)==size*24 and len(ny)==size*18
joined=oy[18*size:24*size]+ny
assert not final.exists(), 'Fixed final already exists; refusing overwrite.'
argv=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','yuv420p','-s','1920x1080','-r','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(final)]
result=subprocess.run(argv,input=joined,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
fp=check(final,24); (R/'FFPROBE_FINAL24.json').write_text(json.dumps(fp,indent=2)+'\n')
fy=decode(final,'yuv420p'); assert fy==joined
orgb=decode(old,'rgb24'); nrgb=decode(new,'rgb24'); frgb=decode(final,'rgb24'); rs=1920*1080*3
assert len(frgb)==rs*24
rows=[]; images={}; keys=R/'actual_decoded_keys'; keys.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1920,1620),(225,228,231)); draw=ImageDraw.Draw(sheet)
for i in range(24):
    f=i+66; b=frgb[i*rs:(i+1)*rs]
    im=Image.frombytes('RGB',(1920,1080),b); images[f]=im
    expected=orgb[(18+i)*rs:(19+i)*rs] if i<6 else nrgb[(i-6)*rs:(i-5)*rs]
    assert b==expected,(f,'RGB differing')
    row={'global_frame':f,'state':66 if f<72 else 72 if f<78 else 78 if f<84 else 84,'decoded_YUV420_SHA256':sha(fy[i*size:(i+1)*size]),'decoded_RGB24_SHA256':sha(b),'exact_against':'old066–071 decoded history' if i<6 else 'new072–089 actual browser MP4','differing_RGB_channels':0,'differing_YUV_samples':0}
    rows.append(row)
    im.save(keys/f'S29_F{f:03d}_ACTUAL_DECODED.png')
    sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*270))
    draw.text(((i%4)*480+8,(i//4)*270+8),f'{f:03d} '+('REUSED' if i<6 else 'NEW'),fill='white',stroke_width=1,stroke_fill='black')
sheet.save(R/'ALL24_REUSED6_NEW18_ACTUAL_DECODED_CONTACT.png')
# All crops are actual decoded pixels at 1:1, never drawings substituting for output.
sw=Image.new('RGB',(1200,1230),(232,235,239)); d=ImageDraw.Draw(sw)
for row,(a,b) in enumerate([(71,72),(77,78),(83,84)]):
    for col,f in enumerate([a,b]):
        x=col*600; y=row*410
        sw.paste(images[f].crop((350,350,950,730)),(x,y+30))
        d.text((x+8,y+9),f'ACTUAL {f:03d} '+('REUSED' if f<72 else 'NEW'),fill='black')
sw.save(R/'THREE_SWITCHES_COMPLETE_ARMS_CONTACTS_ACTUAL_1TO1.png')
sleeve=Image.new('RGB',(540,780),(232,235,239)); d=ImageDraw.Draw(sleeve)
for row,(a,b) in enumerate([(71,72),(77,78),(83,84)]):
    for col,f in enumerate([a,b]):
        x=col*270; y=row*260
        sleeve.paste(images[f].crop((740,330,1010,560)),(x,y+30))
        d.text((x+8,y+9),f'ACTUAL {f:03d}',fill='black')
sleeve.save(R/'THREE_SWITCHES_COMPLETE_FAR_SLEEVE_ACTUAL_1TO1.png')
report={'status':'ALL24_EXACT_YUV_AND_RGB_PENDING_ACTUAL_VISUAL_REVIEW','new_browser_scene_render_count':18,'new_browser_global_frames':list(range(72,90)),'old066_071_browser_redrawn':False,'generation_calls':0,'history24_SHA256_unchanged':sha(old.read_bytes()),'new18_MP4_SHA256':sha(new.read_bytes()),'final24_MP4_SHA256':sha(final.read_bytes()),'new18_frames':18,'final24_frames':24,'fps':'24/1','width':1920,'height':1080,'duration_seconds':1,'audio':False,'final_codec':next(s for s in fp['streams'] if s['codec_type']=='video')['codec_name'],'final_profile':next(s for s in fp['streams'] if s['codec_type']=='video').get('profile'),'assembly':'Original066–071 decoded YUV420 planes reused verbatim; appended new072–089 actualrender YUV. LosslessH264 qp0 preserves all planes, independently decoded RGB exact too.','ffmpeg_assembly_arguments':argv,'ffmpeg_stderr':result.stderr.decode(),'frame_exact_checks':rows,'scene_sources_unchanged':run['sourceUnchanged'],'history_directory_modified':False,'ready_claimed':False}
(R/'REUSED6_NEW18_ACTUAL_DECODE_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['frame_exact_checks','ffmpeg_assembly_arguments']},ensure_ascii=False,indent=2))
