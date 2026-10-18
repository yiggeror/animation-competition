#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,shutil,numpy as np
P=Path(__file__).resolve().parents[1];R=P.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records=[(15,6,'exec-de5c2f67-00ca-4880-b92e-6b84bfb1609a.png'),(19,7,'exec-280b6880-9e02-4a0c-be05-3e2505691bf9.png')]
for f,n,toolname in records:
 raw=P/f'originals/S24_F{f:03}_call_{n:03}_raw.png';assert raw.read_bytes()==(Path('/workspace/generated_images')/toolname).read_bytes()
 reqfile=P/f'requests/F{f:03}_call_{n:03}_request.json';req=json.loads(reqfile.read_text());req['status']='actual_native_returned_author_accepted_after_visual_and_color_gate';reqfile.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
 for x in req['inputs']:assert sha(Path(x['path']))==x['sha256']
 c=P/f'candidates/F{f:03}_rgba.png';report=json.loads((P/f'qa/F{f:03}_color_validation.json').read_text());assert sha(c)==report['candidate_sha256']
 response={'call_id':req['call_id'],'status':'AUTHOR_ACCEPTED_CANDIDATE_ASTRA_REVIEW_PENDING','raw':str(raw.relative_to(P)),'raw_sha256':sha(raw),'tool_original_path':'/workspace/generated_images/'+toolname,'candidate':str(c.relative_to(P)),'candidate_sha256':sha(c),'inputs':req['inputs'],'raw_size':[1024,1536],'raw_mode':'RGBA','model_version':'not returned by tool','local_color_step':'explicit masks relative to raw;no geometry warp;fixed corrected mother0485c6fe palette'}
 (P/f'requests/F{f:03}_call_{n:03}_response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2)+'\n')
frames={12:R/'d02_d04_segment/candidates/F012_rgba.png',15:P/'candidates/F015_rgba.png',19:P/'candidates/F019_rgba.png'}
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im):
 bg=Image.new('RGBA',im.size,(209,215,215,255));bg.alpha_composite(im);return bg.convert('RGB')
board=Image.new('RGB',(1440,780),'#f3f0e8');draw=ImageDraw.Draw(board)
S=Path('/tmp/s24_012_023_neutral_source');D=Path('/tmp/s24_012_023_neutral_decoded');S.mkdir(exist_ok=True);D.mkdir(exist_ok=True);seq=[12]*3+[15]*4+[19]*5
for i,(f,path)in enumerate(frames.items()):
 im=Image.open(path).convert('RGBA');panel=comp(im);panel.thumbnail((470,705));board.paste(panel,(i*480+5,45));draw.text((i*480+10,10),f'F{f:03} '+('已锁衔接态'if f==12 else'合格候选'),font=font(25),fill='#25333d')
 placed=im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);panel=comp(placed).resize((1280,720),Image.Resampling.LANCZOS);ImageDraw.Draw(panel).text((10,8),f'S24 F{f:03} DRAWING LAYER ONLY / NOT CANVAS SCENE',font=font(22),fill='#333333')
 for idx,k in enumerate(seq):
  if k==f:panel.save(S/f'{idx:05}.png')
board.save(P/'qa/00_locked012_and_015_019_partial.jpg',quality=97)
mp4=P/'qa/S24_F012_023_neutral12f_24fps_NOT_SCENE.mp4';subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(S/'%05d.png'),'-frames:v','12','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation',str(mp4)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(mp4)],text=True));v=probe['streams'][0];assert v['nb_frames']=='12'and v['r_frame_rate']=='24/1'and float(v['duration'])==.5 and len(probe['streams'])==1
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);checks=[]
for idx,k in enumerate(seq):
 a=np.array(Image.open(S/f'{idx:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{idx+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50;checks.append({'timeline_frame':idx+12,'drawing_start':k,'source_sha256':sha(S/f'{idx:05}.png'),'MSE':mse})
(P/'qa/neutral12_encoding_validation.json').write_text(json.dumps({'status':'PASS_PARTIAL_DRAWING_LAYER_ONLY_NOT_SCENE','timeline':[12,23],'frames':12,'fps':24,'seconds':.5,'F024_substituted_or_held':False,'mp4_sha256':sha(mp4),'checks':checks},ensure_ascii=False,indent=2)+'\n')
print('PASS archive015019 and12fneutral timeline012–023 only;024absent,not substituted;original native files retained')
