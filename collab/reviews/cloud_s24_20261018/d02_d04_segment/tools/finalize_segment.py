#!/usr/bin/env python3
"""Archive native outputs, inspect candidate pixels and encode neutral drawing-layer timing only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,shutil,datetime
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=R/'d01_hair_color_fix/candidates/F000_hair_corrected_rgba.png'
assert sha(master)=='0485c6fe2ee6ec05d762a6b1c531ed9764e7e77223b6cce455b54f50f99eff22'
records=[
 (6,2,'S24_F006_call_002_raw.png','/workspace/generated_images/exec-81abc347-0b54-40e0-8189-7e371b5d8c5d.png'),
 (9,3,'S24_F009_call_003_REJECTED_overshoot_raw.png','/workspace/generated_images/exec-ec8c9e0b-2366-4f80-9773-6a056759612f.png'),
 (9,4,'S24_F009_call_004_raw.png','/workspace/generated_images/exec-68bc1d7b-bce3-4105-9332-48af9993da88.png'),
 (12,5,'S24_F012_call_005_raw.png','/workspace/generated_images/exec-672ee534-b7c7-4480-a26a-32dd21a55e7a.png'),
]
for f,n,name,tool_path in records:
 raw=P/'originals'/name;assert raw.read_bytes()==Path(tool_path).read_bytes()
 request_path=P/f'requests/F{f:03}_call_{n:03}_request.json';req=json.loads(request_path.read_text())
 for i,inp in enumerate(req['inputs']):assert sha(Path(inp['path']))==inp['sha256']
 assert req['inputs'][0]['sha256']==sha(master)
 assert all('F000_native_rgba.png'not in x['path'] and 'REJECTED'not in x['path']for x in req['inputs'])
 if n==3:
  req['status']='executed_native_return_REJECTED_overshoot_retained'
 else:
  req['status']='executed_native_return_author_accepted_after_actual_structure_and_color_review'
  report=json.loads((P/f'qa/F{f:03}_color_validation.json').read_text());assert report['raw_sha256']==sha(raw)
  response={'call_id':req['call_id'],'tool':'image_gen.imagegen','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_version':'not returned by tool','inputs':req['inputs'],'raw':str(raw.relative_to(P)),'raw_sha256':sha(raw),'tool_original_path':tool_path,'raw_size':list(Image.open(raw).size),'raw_mode':Image.open(raw).mode,'returned_fields':['image_url','output_hint'],'is_error':False,'candidate':report['candidate'],'candidate_sha256':report['candidate_sha256'],'status':'author_accepted_candidate;Astra_segment_review_pending'}
  (P/f'requests/F{f:03}_call_{n:03}_response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2)+'\n')
 request_path.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')

font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,col=(209,215,215,255)):
 bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);return bg.convert('RGB')
files=[(0,master)]+[(f,P/f'candidates/F{f:03}_rgba.png')for f in [6,9,12]]
sheet=Image.new('RGB',(1600,720),'#f3f0e8');d=ImageDraw.Draw(sheet)
jaw=Image.new('RGB',(1920,520),'#f3f0e8');jd=ImageDraw.Draw(jaw)
bboard=Image.new('RGB',(1920,330),'#f3f0e8');bd=ImageDraw.Draw(bboard)
bases=Image.new('RGB',(1360,1640),'#f3f0e8');bcd=ImageDraw.Draw(bases)
geometry=[]
for i,(f,path)in enumerate(files):
 im=Image.open(path).convert('RGBA');assert im.size==(1024,1536)
 native=comp(im);panel=native.copy();panel.thumbnail((390,615));sheet.paste(panel,(i*400+5,50));d.text((i*400+8,13),f'F{f:03} '+('已锁新修母'if f==0 else'新原生候选'),font=font(24),fill='#25333d')
 panel=native.crop((165,520,915,1190));panel.thumbnail((470,450));jaw.paste(panel,(i*480+4,50));jd.text((i*480+8,12),f'F{f:03} 眼/颏颈/耳根',font=font(23),fill='#25333d')
 placed=im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);view=comp(placed);bboard.paste(view.resize((480,270)),(i*480,45));bd.text((i*480+8,10),f'F{f:03} B=.70+(590,20)',font=font(21),fill='#25333d')
 for j,color in enumerate([(245,245,245,255),(33,39,48,255),(112,140,126,255)]):
  panel=comp(im,color);panel.thumbnail((330,500));bases.paste(panel,(i*340+5,j*540+35));bcd.text((i*340+7,j*540+5),f'F{f:03} '+['浅底','深底','彩底'][j],font=font(22),fill='#25333d')
 bbox=im.getchannel('A').point(lambda v:255 if v>=248 else 0).getbbox()
 geometry.append({'frame':f,'candidate_sha256':sha(path),'opaque_alpha_threshold':248,'opaque_native_bbox':list(bbox),'opaque_top_margin_scene_px':round(20+.7*bbox[1],2),'registration':{'scale':.7,'translation':[590,20]},'diagnostic':'opaque bbox includes arms/dress bottom;top is cowlick. Faint original halo is not removed.'})
d.text((12,670),'眼先006→头起009→过正面012；闭口、短尾、同B注册。非实际Canvas接景，非全镜。',font=font(24),fill='#805840')
sheet.save(P/'qa/00_locked_mother_and_three_states.jpg',quality=97);jaw.save(P/'qa/01_eyes_jaw_neck_ear_roots.jpg',quality=97);bboard.save(P/'qa/02_all4_B_neutral_NOT_SCENE.jpg',quality=97);bases.save(P/'qa/03_all4_three_backgrounds.jpg',quality=97)
assert min(x['opaque_top_margin_scene_px']for x in geometry)>75
(P/'qa/registration_and_top_margins.json').write_text(json.dumps({'states':geometry,'not_scene_render':True,'angle_caveat':'Design yaw values are not measured angles in generated drawings.'},ensure_ascii=False,indent=2)+'\n')

# Neutral authored-layer exposure, explicitly labelled; no code character or original scene.
S=Path('/tmp/s24_segment15_neutral_sources');S.mkdir(exist_ok=True)
D=Path('/tmp/s24_segment15_neutral_decoded');D.mkdir(exist_ok=True)
seq=[0]*6+[6]*3+[9]*3+[12]*3;source={f:path for f,path in files}
for f in set(seq):
 im=Image.open(source[f]).convert('RGBA');placed=im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);panel=comp(placed).resize((1280,720),Image.Resampling.LANCZOS);draw=ImageDraw.Draw(panel);draw.rectangle((0,0,1280,37),fill='#f3f0e8');draw.text((12,5),f'S24 F{f:03} DRAWING LAYER ONLY / NEUTRAL QA / NOT CANVAS SCENE',font=font(20),fill='#333333')
 for frame,state in enumerate(seq):
  if state==f:panel.save(S/f'{frame:05}.png')
mp4=P/'qa/S24_first15_neutral_layer_24fps_NOT_SCENE.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(S/'%05d.png'),'-frames:v','15','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation',str(mp4)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True));v=probe['streams'][0];assert len(probe['streams'])==1 and v['nb_frames']=='15' and v['r_frame_rate']=='24/1' and float(v['duration'])==.625
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True)
rows=[]
for f,state in enumerate(seq):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 rows.append({'frame':f,'drawing_start':state,'source_sha256':sha(S/f'{f:05}.png'),'encoded_MSE':mse})
(P/'qa/neutral_decoded').mkdir(exist_ok=True)
preview=Image.new('RGB',(1920,650),'#f3f0e8');pd=ImageDraw.Draw(preview)
for i,f in enumerate([0,5,6,8,9,11,12,14]):
 panel=Image.open(D/f'{f+1:05}.png').convert('RGB');panel.thumbnail((470,265));x,y=i%4*480+5,i//4*320+40;preview.paste(panel,(x,y));pd.text((x,y-30),f'F{f:03}中性层实际解码',font=font(21),fill='#25333d')
 if f in [0,6,9,12,14]:shutil.copyfile(D/f'{f+1:05}.png',P/f'qa/neutral_decoded/F{f:03}.png')
preview.save(P/'qa/04_neutral15_actual_encoded_decodes_NOT_SCENE.jpg',quality=97)
(P/'qa/neutral15_encoding_validation.json').write_text(json.dumps({'status':'PASS_ISOLATED_NATIVE_DRAWING_LAYER_EXPOSURE_ONLY','frames':15,'fps':24,'seconds':.625,'scene_render':False,'mp4_sha256':sha(mp4),'all15_encode_order_verified':True,'max_MSE':max(x['encoded_MSE']for x in rows),'checks':rows},ensure_ascii=False,indent=2)+'\n')
print('Archived4calls:3candidate states+1rejected native009;all input SHA verified;old light mother/rejected image not input')
print('B opaque top margins',[(x['frame'],x['opaque_top_margin_scene_px'])for x in geometry])
print('Neutral layer15f/24fps/.625s encoded+decoded;no Canvas scene or later poses')
