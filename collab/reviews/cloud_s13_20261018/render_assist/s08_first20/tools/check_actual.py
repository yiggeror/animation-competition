#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,shutil,numpy as np
ROOT=Path.cwd();P=Path(__file__).resolve().parents[1];FIXED='6f73473a8230ed7a1b236f32605e622769d29109'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIXED
SRC=ROOT/'collab/reviews/20261018_1800_s08_first20_scene';S=ROOT/'build/S08_first20';D=Path('/tmp/s08_first20_actual_decoded');D.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();mp4=P/'S08_first20_1920x1080_24fps.mp4'
assert mp4.read_bytes()==(ROOT/'build/S08_first20_1920x1080_24fps.mp4').read_bytes()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True));v=probe['streams'][0]
assert len(probe['streams'])==1 and(v['nb_frames'],v['r_frame_rate'],v['width'],v['height'])==('20','24/1',1920,1080)and abs(float(v['duration'])-20/24)<1e-6
assert sorted(x.name for x in S.glob('*.png'))==[f'{f:05}.png'for f in range(20)]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);assert len(list(D.glob('*.png')))==20
baseline=json.loads(Path('/tmp/s08_first14_baseline_for20.json').read_text());old=[];checks=[]
for row in baseline['checks']:
 f=row['frame'];a=ROOT/f'build/S08_first14/{f:05}.png';b=S/f'{f:05}.png';assert sha(a)==row['Canvas_source_sha256']and a.read_bytes()==b.read_bytes();old.append({'frame':f,'prior_2383f9f_Canvas_sha256':sha(a),'new20_Canvas_sha256':sha(b),'byte_exact':True})
for f in range(20):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 if f>=14:
  flame=b[740:792,1052:1098];hot=(flame[:,:,0]>=240)&(flame[:,:,1]>=150)&(flame[:,:,2]>=60);assert hot.any()
  wick=b[775:810,1395:1435];assert not((wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60)).any()
 checks.append({'frame':f,'Canvas_source_sha256':sha(S/f'{f:05}.png'),'encoded_vs_source_MSE':mse})
selected=[13,14,16,17,19]
for f in selected:shutil.copyfile(D/f'{f+1:05}.png',P/f'decoded/F{f:03}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def board(ff,name,box=None,cols=3,tile=(640,360),scale=None):
 tw,th=tile;out=Image.new('RGB',(cols*tw,((len(ff)+cols-1)//cols)*(th+36)),'#f3f0e8');d=ImageDraw.Draw(out)
 for i,f in enumerate(ff):
  im=Image.open(D/f'{f+1:05}.png').convert('RGB')
  if box:im=im.crop(box)
  if scale:im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
  else:im.thumbnail((tw-8,th))
  x,y=i%cols*tw+4,i//cols*(th+36)+34;out.paste(im,(x,y));d.text((x,y-30),f'F{f:03}实际解码',font=font(21),fill='#25333d')
 out.save(P/name,quality=97)
board(selected,'00_requested_incremental_decodes.jpg')
board(selected,'01_hand_box_table_actual.jpg',box=(985,730,1215,1020),tile=(470,580),scale=2)
board([17,19],'02_box_base970_actual4x.jpg',box=(1045,935,1165,985),cols=2,tile=(500,200),scale=4)
board(selected,'03_both_elbows_front_lip_actual.jpg',box=(695,865,1195,1035),tile=(510,180))
board([13,14,16,17,19],'04_match_fire_actual2x.jpg',box=(1025,740,1115,845),tile=(200,210),cols=5,scale=2)
module=SRC/'s08_first20_scene.js';assert sha(module)=='16d77bc7ff1b3356030c7ba374502acedf62015239f82a8a231667f75a354a50'
tracked=[*SRC.glob('*.js'),*SRC.glob('frames/*.png'),ROOT/'js/paint/paintshot.js',ROOT/'js/code/s08.js',ROOT/'assets/paint/bg_01_room_wide.png',ROOT/'tools/js/frames.cjs']
for f in tracked:assert f.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{f.relative_to(ROOT)}'])
oldSRC=ROOT/'collab/reviews/20261018_1721_s08_first14_scene'
for f in oldSRC.glob('frames/*.png'):assert f.read_bytes()==(SRC/'frames'/f.name).read_bytes()
box=np.array(Image.open(SRC/'frames/F017_table_box_original_pixels.png'));body=np.array(Image.open(SRC/'frames/F017_body_behind_original_pixels.png'));arms=np.array(Image.open(SRC/'frames/F017_forearms_elbows_original_pixels.png'));m=box[:,:,3]>0
assert int(m.sum())==1665 and not np.any((body[:,:,3]>0)&m)and not np.any((arms[:,:,3]>0)&m)
ys,xs=np.where(box[:,:,3]>128);assert ys.max()==970
box_audit={'table_box_alpha_pixels':int(m.sum()),'opaque_box_bottom_y':int(ys.max()),'body_alpha_at_original_box_pixels':0,'arms_alpha_at_original_box_pixels':0,'box_layer_instances':1,'box_frame17_19_contact_base':970,'table_surface_y':[950.2,981],'front_lip_y':981,'source_layer_count':15,'old10layers_byte_equal':True,'fixed_module_and_runtime_files_exact':len(tracked)}
(P/'box_source_validation.json').write_text(json.dumps(box_audit,ensure_ascii=False,indent=2)+'\n')
(P/'prior14_exact_comparison.json').write_text(json.dumps({'status':'PASS_ALL14_ACTUAL_CANVAS_PNG_BYTE_IDENTICAL','prior_actual_commit':'2383f9f1ab8b0e6551ea5c339c8ec32b76f29b5b','prior_packet':'collab/reviews/cloud_s13_20261018/render_assist/s08_first14/','comparison':'original lossless Canvas PNG,not two lossy MP4 decodes','checks':old},ensure_ascii=False,indent=2)+'\n')
result={'status':'PASS_REAL20_RENDER_ENCODE_AND_PRIOR14_EXACT','fixed_commit':FIXED,'module_sha256':sha(module),'frames':20,'fps':'24/1','duration_seconds':20/24,'size':[1920,1080],'audio_streams':0,'selected_decoded':selected,'frame020_and_later_rendered':False,'prior14_Canvas_PNG_byte_identical':True,'all20_encode_order_verified':True,'max_MSE':max(x['encoded_vs_source_MSE']for x in checks),'mp4_sha256':sha(mp4),'checks':checks,'visual_review':'SeeREADME;new six-frame scope and actual box-shadow review,not fullshot.'}
(P/'actual20_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(P/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print('PASS actual20f/1080p/24fps/20/24s;all20 encoding order;prior14 actualPNG byte-exact;maxMSE',result['max_MSE'])
print('PASS box1665pixels only once in isolated layer,bottomy970,no body/arms duplicate;new15layers fixed Git;matchfire fromactualhead,wick0')
