from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess
R=Path(__file__).resolve().parent;video=R/'S29_F036_F048_ACTUAL_SCENE_1080p24.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(R/'FFPROBE.json').write_text(json.dumps(probe,indent=2)+'\n')
frames=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
size=1920*1080*3;assert len(frames)==13*size
keys=R/'decoded_keys';keys.mkdir(exist_ok=True);images={};checks=[]
sheet=Image.new('RGB',(1920,1080),(225,228,231));draw=ImageDraw.Draw(sheet)
for i in range(13):
 b=frames[i*size:(i+1)*size];im=Image.frombytes('RGB',(1920,1080),b);images[i+36]=im
 checks.append({'global_frame':i+36,'RGB24_SHA256':hashlib.sha256(b).hexdigest()})
 if i+36 in [36,41,42,47,48]:im.save(keys/f'S29_F{i+36:03d}_DECODED.png')
 thumb=im.resize((480,270));sheet.paste(thumb,((i%4)*480,(i//4)*270));draw.text(((i%4)*480+8,(i//4)*270+8),f'{i+36:03d}',fill=(255,255,255),stroke_width=1,stroke_fill='black')
sheet.save(R/'ALL13_ACTUAL_DECODED_CONTACT.png')
contact=Image.new('RGB',(1640,980),(236,239,242));draw=ImageDraw.Draw(contact)
for i,f in enumerate([41,42,47,48]):
 contact.paste(images[f].crop((500,620,1320,1080)),((i%2)*820,(i//2)*490+30));draw.text(((i%2)*820+8,(i//2)*490+8),f'ACTUAL DECODED {f:03d} | CLOTH AT ORIGINAL OUTPUT SIZE',fill='black')
contact.save(R/'BOTH_SWITCHES_ACTUAL_CLOTH_1TO1.png')
tail=Image.new('RGB',(600,300),(236,239,242));draw=ImageDraw.Draw(tail)
for i,f in enumerate([36,42,48]):
 tail.paste(images[f].crop((1040,740,1240,990)),(i*200,30));draw.text((i*200+8,8),f'{f:03d} TRUE LIP/T',fill='black')
tail.save(R/'THREE_ACTUAL_LIP_T_1TO1.png')
report={'video_SHA256':hashlib.sha256(video.read_bytes()).hexdigest(),'decoded_frames':13,'width':1920,'height':1080,'fps':'24/1','duration_seconds':13/24,'has_audio':any(s['codec_type']=='audio'for s in probe['streams']),'actual_decode_hashes':checks,'visual_status':'PENDING_ACTUAL_DECODED_REVIEW'}
(R/'DECODE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='actual_decode_hashes'},indent=2))
