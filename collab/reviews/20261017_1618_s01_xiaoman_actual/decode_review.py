from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,subprocess,json,hashlib
R=Path(__file__).resolve().parent;(R/'roi_frames').mkdir(exist_ok=True);(R/'full_selected').mkdir(exist_ok=True)
v=R/'S01_xiaoman_new_1080p_noaudio.mp4';p=subprocess.Popen(['ffmpeg','-v','error','-i',str(v),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
rows=[];n=0;full={0,6,14,54,63,141,180,228,287};N=1920*1080*3
while True:
 b=p.stdout.read(N)
 if not b:break
 if len(b)!=N:raise RuntimeError('short frame')
 a=np.frombuffer(b,dtype=np.uint8).reshape(1080,1920,3);nearblack=np.all(a<8,axis=2).mean(axis=1)>.999;bottom=0
 for q in nearblack[::-1]:
  if not q:break
  bottom+=1
 top=0
 for q in nearblack:
  if not q:break
  top+=1
 rows.append({'frame':n,'top_fullwidth_black_rows':top,'bottom_fullwidth_black_rows':bottom});im=Image.fromarray(a);im.crop((510,590,900,810)).save(R/'roi_frames'/f'{n:04}.png')
 if n in full:im.save(R/'full_selected'/f'F{n:03}.jpg',quality=93)
 n+=1
assert p.wait()==0
sets={'first_cycle':[0,2,4,6,8,10,12,14,16],'later_k14':[40,42,44,85,87,89,127,129,131,166,168,170,214,216,218,250,252,254],'game_faces':[17,18,29,30,31,32,33,34,35,36,53,54,62,63,80,81,140,141,179,180,188,189,227,228,275,276,278,280,282,287]}
for name,fs in sets.items():
 sh=Image.new('RGB',(390*3,(220+24)*((len(fs)+2)//3)),(45,45,45));d=ImageDraw.Draw(sh)
 for j,f in enumerate(fs):
  im=Image.open(R/'roi_frames'/f'{f:04}.png');x=(j%3)*390;y=(j//3)*244;sh.paste(im,(x,y+24));d.text((x+5,y+7),f'F{f:03}',fill='white')
 sh.save(R/f'{name}_actual_contact.jpg',quality=95)
(R/'visual_metrics.json').write_text(json.dumps({'commit':'5edaa205a3d73abfd520e94d5bafe0e790d6b7c0','file_sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'decoded_frames':n,'crop_box':[510,590,900,810],'contact_frames':sets,'edge_rows':rows},indent=2)+'\n')
print('decoded',n,'bottom band frames',sum(x['bottom_fullwidth_black_rows']>0 for x in rows),'max',max(x['bottom_fullwidth_black_rows'] for x in rows),'last',max(x['frame'] for x in rows if x['bottom_fullwidth_black_rows']>0));print('examples',[rows[f] for f in [0,24,48,72,96,120,144,287]])
