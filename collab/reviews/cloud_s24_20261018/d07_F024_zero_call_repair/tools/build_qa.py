#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import numpy as np,json,hashlib,subprocess,tempfile
H=Path(__file__).resolve().parents[1];P=H.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cand=H/'candidates/F024_original_pixel_sleeve_repair_rgba.png';base=P/'d05_d07_segment/originals/S24_F024_call_008_REJECTED_sleeve_crop_raw.png'
f19=P/'d05_d07_segment/candidates/F019_rgba.png';master=P/'d01_hair_color_fix/candidates/F000_hair_corrected_rgba.png'
a=np.array(Image.open(base).convert('RGBA'));out=np.array(Image.open(cand).convert('RGBA'));delta=np.any(a!=out,2)
yy,xx=np.indices(delta.shape)
# Full tail material and skin/neck coverage, plus both whole collar flaps and their lines.
r,g,b,al=np.moveaxis(a.astype('int16'),2,0)
hair=(al>=248)&(r>30)&(r<130)&(r>g+7)&(g>b+2)&(yy<1040)&((yy<1000)|(xx<700))
skin=(al>=248)&(r>150)&(g>90)&(b>65)&(r>g+10)&(g>b+10)&(g-b<70)&(r-g<100)&(yy<1090)&((yy<1000)|(xx<750))
white=(al>=248)&(r>220)&(g>220)&(b>205)&(yy>900)&(yy<1200)
labs,_=ndi.label(white); collar=np.zeros(delta.shape,bool)
for x,y in [(420,1050),(640,1100)]:
 assert labs[y,x]>0
 collar |= labs==labs[y,x]
collar=ndi.binary_dilation(collar,iterations=4)
for name,m in [('hair_entire_head_and_tails',hair),('face_ears_neck_skin',skin),('whole_collar_with_stroke_AA',collar)]:
 assert not np.any(delta&m),(name,int((delta&m).sum()))
 Image.fromarray((m*255).astype('uint8')).save(H/f'masks/protected_{name}.png')
# Colour is measured only; this user request is original-pixel repair, so no protected RGB is recoloured.
def mat(im,k):
 r,g,b,a=np.moveaxis(im.astype('int16'),2,0);o=a>=248
 if k=='hair':return o&(r>35)&(r<125)&(r>g+7)&(g>b+2)&(g<95)&(b<85)
 if k=='skin':return o&(r>150)&(g>90)&(b>65)&(r>g+10)&(g>b+10)&(g-b<70)&(r-g<100)
 return o&(r>180)&(g>120)&(b<130)&(r>g+10)&(g>b+60)
def stat(im,roi,k):
 x,y,X,Y=roi;cut=im[y:Y,x:X];v=cut[:,:,:3][mat(cut,k)].astype(float);assert len(v)>100
 return {'roi':roi,'n':len(v),'median':np.median(v,0).tolist(),'mean':v.mean(0).round(5).tolist()}
config=json.loads((P/'d05_d07_segment/qa/F019_color_config.json').read_text())
m=np.array(Image.open(master).convert('RGBA'));colors=[]
for name,c in config['regions'].items():
 cur=stat(out,c['roi'],c['type']);ref=stat(m,c['master_roi'],c['type']);diff=np.subtract(cur['mean'],ref['mean']).round(5).tolist()
 colors.append({'material':name,'current':cur,'locked_mother':ref,'mean_RGB_delta':diff,'within_4':max(abs(v)for v in diff)<=4})
(H/'qa/color_measurement_NO_COLOR_EDIT.json').write_text(json.dumps({'method':'same F019 material ROI for diagnostic comparison only; no colour changes in this repair','locked_mother_sha256':sha(master),'rows':colors,'all_within_4':all(c['within_4']for c in colors)},ensure_ascii=False,indent=2)+'\n')
# Exact B registration and exact hold schedule. These are neutral raster layer previews, not Canvas scene frames.
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,col):
 bg=Image.new('RGBA',im.size,(*col,255));bg.alpha_composite(im);return bg.convert('RGB')
validation={};selected=[];frame_rows=[]
for bgname,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 with tempfile.TemporaryDirectory(prefix='s24_f019_024_') as td:
  td=Path(td);expected=[]
  for i in range(13):
   state=19 if i<5 else 24;path=f19 if state==19 else cand
   im=Image.open(path).convert('RGBA').transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC)
   frame=comp(im,col);file=td/f'{i:04}.png';frame.save(file);expected.append(sha(file))
   if bgname=='gray':frame_rows.append({'local_frame':i,'scene_frame':19+i,'drawing_start':state,'source_sha256':sha(path),'registered_RGB_PNG_sha256':sha(file)})
  target=H/f'qa/S24_F019_031_{bgname}_13f_24fps_NOT_SCENE.mp4'
  cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(td/'%04d.png'),'-frames:v','13','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
  subprocess.run(cmd,check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]));v=next(s for s in probe['streams']if s['codec_type']=='video')
  assert int(v['nb_read_frames'])==13 and v['avg_frame_rate']=='24/1' and v['width']==1920 and v['height']==1080
  assert not any(s['codec_type']=='audio'for s in probe['streams'])
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(target),str(td/'decoded_%03d.png')],check=True)
  for n in [0,4,5,12]:
   decoded=Image.open(td/f'decoded_{n+1:03}.png').convert('RGB');dest=H/f'qa/decoded_{bgname}_local{n:02}_scene{n+19:03}.jpg';decoded.save(dest,quality=98)
   if n in [0,5,12]:selected.append((dest,f'{bgname} · scene {19+n:03} · '+('019×5'if n<5 else'024×8')))
  validation[bgname]={'mp4_sha256':sha(target),'width':1920,'height':1080,'decoded_frames':13,'rate':'24/1','duration':v.get('duration'),'source_hold_schedule':[[19,5],[24,8]],'no_audio':True,'not_Canvas_scene':True}
# Actual decoded frame contact sheet.
sheet=Image.new('RGB',(1920,1290),'#edeae2');d=ImageDraw.Draw(sheet)
for i,(file,label)in enumerate(selected):
 im=Image.open(file);im.thumbnail((960,540));x=(i%3)*640;y=(i//3)*645;im=im.resize((640,360));sheet.paste(im,(x,y+50));d.text((x+10,y+10),label,font=font(22),fill='#24303a')
sheet=sheet.crop((0,0,1920,1055));sheet.save(H/'qa/actual_decoded_exposure_contact.jpg',quality=97)
# Native full and chin-neck/ear comparison.
for crop,name,sz in [((0,0,1024,1536),'full',(1400,1095)),((150,510,940,1190),'neck_ears',(1600,760))]:
 panel=Image.new('RGB',sz,'#eeeae2');d=ImageDraw.Draw(panel)
 for i,(file,label)in enumerate([(f19,'019 · 前态'),(cand,'024 · 原像素接回')]):
  im=comp(Image.open(file).convert('RGBA'),(160,167,172)).crop(crop);im.thumbnail((sz[0]//2-20,sz[1]-60));panel.paste(im,(i*(sz[0]//2)+10,50));d.text((i*(sz[0]//2)+12,10),label,font=font(25),fill='#24303a')
 panel.save(H/f'qa/F019_F024_{name}.jpg',quality=98)
(H/'qa/exposure_encoding_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
(H/'qa/exposure_source_frames.json').write_text(json.dumps(frame_rows,ensure_ascii=False,indent=2)+'\n')
(H/'qa/additional_protected_domains.json').write_text(json.dumps({'hair_entire_head_and_tails_changes':int((delta&hair).sum()),'face_ears_neck_skin_changes':int((delta&skin).sum()),'whole_collar_with_stroke_AA_changes':int((delta&collar).sum()),'no_new_generation':True},indent=2)+'\n')
print(json.dumps({'exposure':validation,'color':colors,'protected_hair_skin_collar_RGBA_changes':0},ensure_ascii=False,indent=2))
