from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess
R=Path(__file__).resolve().parent
video=R/'S29_F048_F071_ACTUAL_SCENE_1080p24.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(R/'FFPROBE.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=[s for s in probe['streams']if s['codec_type']=='video'];assert len(vs)==1
v=vs[0];assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',24)
assert not any(s['codec_type']=='audio'for s in probe['streams'])
frames=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
size=1920*1080*3;assert len(frames)==24*size
keys=R/'decoded_keys';keys.mkdir(exist_ok=True);images={};checks=[]
sheet=Image.new('RGB',(1920,1620),(225,228,231));draw=ImageDraw.Draw(sheet)
for i in range(24):
    b=frames[i*size:(i+1)*size];im=Image.frombytes('RGB',(1920,1080),b);f=i+48;images[f]=im
    checks.append({'global_frame':f,'RGB24_SHA256':hashlib.sha256(b).hexdigest()})
    if f in [48,53,54,59,60,65,66,71]:im.save(keys/f'S29_F{f:03d}_DECODED.png')
    sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*270));draw.text(((i%4)*480+8,(i//4)*270+8),f'{f:03d}',fill='white',stroke_width=1,stroke_fill='black')
sheet.save(R/'ALL24_ACTUAL_DECODED_CONTACT.png')
contact=Image.new('RGB',(1640,1470),(236,239,242));draw=ImageDraw.Draw(contact)
for i,f in enumerate([53,54,59,60,65,66]):
    contact.paste(images[f].crop((500,620,1320,1080)),((i%2)*820,(i//2)*490+30));draw.text(((i%2)*820+8,(i//2)*490+8),f'ACTUAL DECODED {f:03d} | ORIGINAL OUTPUT SIZE',fill='black')
contact.save(R/'THREE_SWITCHES_ACTUAL_CLOTH_1TO1.png')
report={'video_SHA256':hashlib.sha256(video.read_bytes()).hexdigest(),'decoded_frames':24,'width':1920,'height':1080,'fps':'24/1','duration_seconds':1,'has_audio':False,'actual_decode_hashes':checks,'visual_status':'PENDING_ACTUAL_DECODED_REVIEW'}
(R/'DECODE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='actual_decode_hashes'},indent=2))
