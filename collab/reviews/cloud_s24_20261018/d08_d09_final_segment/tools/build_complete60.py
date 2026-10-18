#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,tempfile
H=Path(__file__).resolve().parents[1];spec=json.loads((H/'asset_index.json').read_text());rows=spec['rows'];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert len(rows)==9 and sum(r['hold']for r in rows)==60
for r in rows:assert sha(H/r['asset'])==r['sha256']
assert rows[6]['sha256']=='44137d740ac5d07ca0258019c28cdf8f9b648d77ba79eda07f366f24503753db'
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,col):
 bg=Image.new('RGBA',im.size,(*col,255));bg.alpha_composite(im);return bg.convert('RGB')
# Source drawing contacts are actual native PNGs, not skeletal or code-person substitutes.
board=Image.new('RGB',(1800,1605),'#eeebe3');d=ImageDraw.Draw(board)
for i,r in enumerate(rows):
 im=comp(Image.open(H/r['asset']).convert('RGBA'),(160,167,172));im.thumbnail((580,495));x=i%3*600+10;y=i//3*535+40;board.paste(im,(x,y));d.text((x,y-32),f"F{r['start']:03} ×{r['hold']}",font=font(23),fill='#25333d')
board.save(H/'qa/00_actual_all9_drawings.jpg',quality=98)
selected=[0,6,9,12,15,19,24,31,32,39,40,49,59];reports={};end_indices=[]
for label,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 with tempfile.TemporaryDirectory(prefix='s24_full60_')as td:
  td=Path(td);source_rows=[];assigned=[]
  for r in rows:
   native=Image.open(H/r['asset']).convert('RGBA');placed=native.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);rgb=comp(placed,col)
   for f in range(r['start'],r['start']+r['hold']):
    p=td/f'{f:04}.png';rgb.save(p);source_rows.append({'frame':f,'drawing_start':r['start'],'native_asset_sha256':r['sha256'],'placed_source_RGB_PNG_sha256':sha(p)});assigned.append(r['start'])
  assert len(source_rows)==60 and assigned[31:41]==[24,32,32,32,32,32,32,32,32,40]
  assert all(source_rows[f]['native_asset_sha256']==rows[-1]['sha256']for f in range(40,60))
  assert len({source_rows[f]['placed_source_RGB_PNG_sha256']for f in range(40,60)})==1
  movie=H/f'qa/S24_complete60_{label}_1920x1080_24fps_NOT_SCENE.mp4'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(td/'%04d.png'),'-frames:v','60','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)]));v=probe['streams'][0];assert len(probe['streams'])==1 and(v['nb_read_frames'],v['avg_frame_rate'],v['width'],v['height'],float(v['duration']))==('60','24/1',1920,1080,2.5)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(movie),'-fps_mode','passthrough',str(td/'decoded_%03d.png')],check=True);assert len(list(td.glob('decoded_*.png')))==60
  checks=[]
  for f in range(60):
   a=np.array(Image.open(td/f'{f:04}.png').convert('RGB'),dtype=float);b=np.array(Image.open(td/f'decoded_{f+1:03}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50;checks.append({'frame':f,'drawing_start':assigned[f],'decoded_vs_source_MSE':mse})
  contact=Image.new('RGB',(1920,((len(selected)+2)//3)*396),'#eeebe3');d=ImageDraw.Draw(contact)
  for i,f in enumerate(selected):
   im=Image.open(td/f'decoded_{f+1:03}.png').convert('RGB');im.save(H/f'qa/decoded_{label}_F{f:03}.jpg',quality=98);im=im.resize((640,360));x=i%3*640;y=i//3*396+34;contact.paste(im,(x,y));d.text((x+8,y-30),f'F{f:03} actual decoded · drawing{assigned[f]:03}',font=font(20),fill='#25333d')
  contact.save(H/f'qa/01_actual_decoded60_{label}_contact.jpg',quality=98)
  # Focused boundary evidence: the last settled drawing persists through059.
  b2=Image.new('RGB',(1920,792),'#eeebe3');d2=ImageDraw.Draw(b2)
  for i,f in enumerate([24,31,32,39,40,59]):
   im=Image.open(td/f'decoded_{f+1:03}.png').convert('RGB').crop((600,55,1315,810));im.thumbnail((630,350));x=i%3*640+5;y=i//3*396+34;b2.paste(im,(x,y));d2.text((x,y-30),f'F{f:03} real decoded',font=font(21),fill='#25333d')
  b2.save(H/f'qa/02_settle_hold_boundaries_{label}_decoded.jpg',quality=98)
  reports[label]={'mp4_sha256':sha(movie),'frames':60,'size':[1920,1080],'rate':'24/1','duration':2.5,'audio_streams':0,'is_scene':False,'B_registration':[.7,590,20],'drawings':9,'frame040_059_source_identical':True,'all60_source_rows':source_rows,'all60_encoding_checks':checks,'max_encoded_MSE':max(x['decoded_vs_source_MSE']for x in checks)}
(H/'qa/complete60_validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{z:v[z]for z in ['mp4_sha256','frames','duration','max_encoded_MSE','frame040_059_source_identical']}for k,v in reports.items()},ensure_ascii=False))
