from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,subprocess,json,hashlib
R=Path(__file__).resolve().parent; v=R/'batch1_S01_S03_S04_1080p.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]));(R/'probe.json').write_text(json.dumps(probe,indent=2)+'\n')
(R/'grandma_roi').mkdir(exist_ok=True);(R/'selected_frames').mkdir(exist_ok=True)
sets={'s01_first_cycle':[0,16,19,22,24,38,40,41,43,44,46,47,50,53], 's01_first_look':[53,56,59,67,68,70,71,73,76,79], 's01_middle_cycles':[103,107,109,111,113,114,116,117,120,123,126,128,130,131,133,134], 's01_second_look_and_tail':[180,183,186,194,195,197,198,200,203,206,224,226,262,264,266,269,272,287]}
full={0,19,38,41,44,59,126,186,287,288,390,393,396,431,432,462,495,510,528,549,555,558,561,623};N=1920*1080*3
p=subprocess.Popen(['ffmpeg','-v','error','-i',str(v),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE);rows=[];n=0
while True:
 b=p.stdout.read(N)
 if not b:break
 assert len(b)==N
 a=np.frombuffer(b,np.uint8).reshape(1080,1920,3);black=np.all(a<8,axis=2);rr=black.mean(1)>.999;cc=black.mean(0)>.999
 def edge(q):
  out=0
  for x in q:
   if not x:break
   out+=1
  return out
 rows.append({'frame':n,'top':edge(rr),'bottom':edge(rr[::-1]),'left':edge(cc),'right':edge(cc[::-1])});im=Image.fromarray(a)
 if n<288:im.crop((940,480,1225,930)).save(R/'grandma_roi'/f'{n:04}.png')
 if n in full:im.save(R/'selected_frames'/f'F{n:03}.jpg',quality=94)
 if n==0:im.crop((510,600,900,820)).save(R/'S01_F000_xiaoman.png')
 if n in [288,390,393,396,431]:im.crop((600,180,1300,940)).save(R/'selected_frames'/f'F{n:03}_s03_roi.png')
 n+=1
rc=p.wait();print('decoder exit',rc,'frames',n,flush=True);assert rc==0 and n==624
for name,fs in sets.items():
 sh=Image.new('RGB',(285*3,324*((len(fs)+2)//3)),(42,42,42));d=ImageDraw.Draw(sh)
 for j,f in enumerate(fs):
  im=Image.open(R/'grandma_roi'/f'{f:04}.png').crop((0,0,285,300));x=j%3*285;y=j//3*324;sh.paste(im,(x,y+24));d.text((x+5,y+5),f'S01 F{f:03}',fill='white')
 sh.save(R/f'{name}_contact.jpg',quality=95)
metrics={'commit':'93bc0c611b2076e12afeac9e232e5ecf76e5d863','file_sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'decoded_frames':n,'shot_intervals_decoded':{'S01':[0,288],'S03':[288,432],'S04':[432,624]},'black_edge_test':'contiguous edge rows/columns with >99.9% pixels all RGB<8','edge_maxima':{k:max(r[k] for r in rows) for k in ['top','bottom','left','right']},'frames_with_black_edge':[r for r in rows if any(r[k] for k in ['top','bottom','left','right'])],'contact_frames':sets,'all_edges':rows}
(R/'visual_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:metrics[k] for k in ['decoded_frames','edge_maxima','frames_with_black_edge']}));print('video:',[(s.get('codec_name'),s.get('width'),s.get('height'),s.get('nb_frames'),s.get('start_time'),s.get('duration')) for s in probe['streams']])
