from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,hashlib
R=Path('/workspace/scratch/f060b5601755/s14_stage_setup_inputs_20261019_0756');U=Path('/tmp/laidian_s14_turn_sit_20261020');P=R/'x168_x179_turn_sit_zero_call';src=[];imgs=[];size=(1190,1350)
for f in [168,171,174,177,180]:
 p=U/f'X{f}_complete_stool_closed_FINAL_CANDIDATE.png' if f!=180 else R/'x180_x196_seated_settle_zero_call/X180_complete_cuff_restored_CANDIDATE.png'
 if f==180:
  im=Image.new('RGBA',size);im.alpha_composite(Image.open(p).convert('RGBA'),(-200,100))
 else:im=Image.open(p).convert('RGBA')
 bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(im);v=bg.convert('RGB');ImageDraw.Draw(v).text((22,20),f'X{f}  3f / 24fps',fill='#294953');imgs.append(v);src.append({'frame':f,'hold_frames':3,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_translation_if_locked180':[-200,100] if f==180 else [0,0]})
page=Image.new('RGB',(1980,450),'#f7f5ed')
for i,im in enumerate(imgs):page.paste(im.resize((396,450)),(396*i,0))
page.save(U/'X168_X171_X174_X177_X180_ACTUAL_COMPLETE_REVIEW.jpg',quality=94)
vid=U/'X168_X182_ACTUAL_3_3_3_3_3_FRAMES_24FPS.mp4';cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','634x720','-r','24','-i','-','-an','-c:v','libx264','-crf','0','-pix_fmt','yuv420p',str(vid)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for im in imgs:
 data=im.resize((634,720)).tobytes()
 for j in range(3):proc.stdin.write(data)
proc.stdin.close();assert proc.wait()==0
# Independent decode to verify actual frame count and repetitions, not just encoder assumptions.
z=subprocess.check_output(['ffmpeg','-v','error','-i',str(vid),'-f','rawvideo','-pix_fmt','rgb24','-']);n=len(z)//(634*720*3);assert n==15;dec=[]
for i in range(n):dec.append(hashlib.sha256(z[i*634*720*3:(i+1)*634*720*3]).hexdigest())
runs=[]
for h in dec:
 if runs and runs[-1]['decoded_frame_sha256']==h:runs[-1]['count']+=1
 else:runs.append({'decoded_frame_sha256':h,'count':1})
assert [x['count'] for x in runs]==[3,3,3,3,3]
rec={'status':'actual_15_frames_decoded_verified','fps':24,'frame_count':n,'range':[168,182],'states':src,'runs':runs,'review':str(U/'X168_X171_X174_X177_X180_ACTUAL_COMPLETE_REVIEW.jpg'),'video':str(vid),'video_sha256':hashlib.sha256(vid.read_bytes()).hexdigest(),'entry_dependency':'150–167 remains missing; this review does not claim continuity across that gap'};(P/'X168_X182_ACTUAL_EXPOSURE_VERIFIED.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
