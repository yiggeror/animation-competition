from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ['qa','frames_reference','exposure','decoded_gray','decoded_dark']:(R/d).mkdir(exist_ok=True)
paths={63:R/'sources/F063_LOCKED0abc.png',69:R/'sources/F069_LOCKED_bc64924f.png',73:R/'candidate/F073_SHORT_PUFF_BARE_ARMS_own_push_FIRST_ON.png',77:R/'candidate/F077_SHORT_PUFF_073_body_original_head_state.png',85:R/'candidate/F085_SHORT_PUFF_073_body_original_head_state.png'}
imgs={n:Image.open(p).convert('RGBA')for n,p in paths.items()}
static=json.loads((R/'qa/static_source_checks.json').read_text())
check={'status':'ACTUAL_SHORT_PUFF_TAIL_EXPOSURE_PENDING_VISUAL_REVIEW','head_composition':static['heads'],'source_SHA256':{str(n):sha(p)for n,p in paths.items()},'source_review_commit':'4a9bd2206c3138e9896bb4105ae37d3947512bfb','native_requests':0,'variants':{},'registration':'native1672x941 at0,0;1672x972 QA video adds31px caption strip only; no drawing scale/crop','exposure':{'063':6,'069':4,'073':4,'077':8,'085':11,'total':33,'fps':24,'duration':33/24}}
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
for tone,col in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2940,580),(233,239,244));dr=ImageDraw.Draw(sheet)
 for j,n in enumerate([73,77,85]):
  bg=Image.new('RGBA',(1672,941),col);bg.alpha_composite(imgs[n]);c=bg.crop((600,390,1090,650)).resize((980,520),Image.Resampling.NEAREST);sheet.paste(c.convert('RGB'),(j*980,40));dr.text((j*980+10,8),f'ACTUAL F{n:03d}: approved073 body / whole head-neck state',font=font,fill='#36536b')
 sheet.save(R/f'qa/F073_F077_F085_actual_collar_shoulders_{tone}_2x.png')
# Exposure files contain actual accepted RGBA states, no new inbetweens or blending.
frames=[]
for n,count in[(63,6),(69,4),(73,4),(77,8),(85,11)]:frames.extend([n]*count)
for tone,col in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 expected=[]
 for n in[63,69,73,77,85]:
  z=Image.new('RGBA',(1672,972),col);z.alpha_composite(imgs[n]);d=ImageDraw.Draw(z);d.text((12,945),f'F{n:03d} locked actual state / 063x6 069x4 073x4 077x8 085x11 /24fps',font=font,fill='#233d52'if tone=='gray'else'#d4e1eb');z=z.convert('RGB');z.save(R/f'frames_reference/F{n:03d}_{tone}.png');expected.append(np.array(z))
 for i,n in enumerate(frames):shutil.copyfile(R/f'frames_reference/F{n:03d}_{tone}.png',R/f'frames_reference/{tone}_{i:02d}.png')
 video=R/f'exposure/S09_F063x6_F069x4_F073x4_F077x8_F085x11_{tone}_ACTUAL_33f_24fps.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(R/f'frames_reference/{tone}_%02d.png'),'-frames:v','33','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(R/f'qa/ffprobe_{tone}.json').write_text(json.dumps(probe,indent=2)+'\n')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vsync','0',str(R/f'decoded_{tone}/frame_%02d.png')],check=True);files=sorted((R/f'decoded_{tone}').glob('frame_*.png'));assert len(files)==33
 cls=[]
 for i,p in enumerate(files):
  im=np.array(Image.open(p).convert('RGB')).astype(float);mae=[float(np.abs(im-z.astype(float)).mean())for z in expected];got=[63,69,73,77,85][int(np.argmin(mae))];assert got==frames[i];cls.append({'index':i,'source_frame':i+63,'actual_class':got,'expected':frames[i],'matching_MAE':mae[[63,69,73,77,85].index(got)]})
 stream=next(s for s in probe['streams']if s['codec_type']=='video');assert stream['avg_frame_rate']=='24/1'and int(stream['nb_read_frames'])==33 and not any(s['codec_type']=='audio'for s in probe['streams']);check['variants'][tone]={'video_sha256':sha(video),'size':[stream['width'],stream['height']],'decoded_frames':33,'fps':stream['avg_frame_rate'],'duration':float(stream['duration']),'audio_streams':0,'all33_decoded_classification_correct':True,'all33_actual_classification':cls}
 indices=[5,6,9,10,13,14,21,22,32];board=Image.new('RGB',(1800,1110),(233,239,244));bd=ImageDraw.Draw(board)
 for j,i in enumerate(indices):
  im=Image.open(files[i]).convert('RGB');tile=im.crop((550,0,1320,924)).resize((300,360));x=(j%6)*300;y=(j//6)*400+32;board.paste(tile,(x,y));bd.text((x+5,y-27),f'decode{i}/F{frames[i]:03d}',font=font,fill='#36536b')
 board.crop((0,0,1800,800)).save(R/f'qa/ACTUAL_33f_decoded_transition_contact_sheet_{tone}.png')
 # Focus collar/shoulder and complete operating hands/torch/light from ACTUAL decodes.
 cboard=Image.new('RGB',(1500,1100),(233,239,244));cd=ImageDraw.Draw(cboard)
 for j,i in enumerate([13,14,21,22,32]):
  im=Image.open(files[i]).convert('RGB');x=(j%3)*500;y=(j//3)*540+30;c=im.crop((650,440,1285,800));c.thumbnail((500,500));cboard.paste(c,(x,y));cd.text((x+8,y-25),f'actual decode{i}/F{frames[i]:03d}',font=font,fill='#36536b')
 cboard.crop((0,0,1500,1000)).save(R/f'qa/ACTUAL_decoded_collar_full_hands_torch_{tone}.png')
(R/'qa/short_composition_and_actual_decode_checks.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps({'heads':check['head_composition'],'gray_video':check['variants']['gray']['video_sha256'],'dark_video':check['variants']['dark']['video_sha256'],'decoded':33,'duration':33/24},indent=2))

# Minimal delivery: retain actual contact/closeup sheets and MP4s, not repeated frames.
for folder in['frames_reference','decoded_gray','decoded_dark']:
 for p in(R/folder).glob('*.png'):p.unlink()
 try:(R/folder).rmdir()
 except OSError:pass
