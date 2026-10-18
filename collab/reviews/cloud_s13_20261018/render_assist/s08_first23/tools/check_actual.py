#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,shutil,numpy as np
P=Path(__file__).resolve().parents[1];ROOT=Path.cwd();FIXED='d6071b76c8b069c7112134320a69058b896ff1f5'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIXED
SRC=ROOT/'collab/reviews/20261018_1828_s08_first23_scene';S=ROOT/'build/S08_first23';D=Path('/tmp/s08_first23_actual_decoded');D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mp4=P/'S08_first23_1920x1080_24fps.mp4'
assert mp4.read_bytes()==(ROOT/'build/S08_first23_1920x1080_24fps.mp4').read_bytes()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True));v=probe['streams'][0]
assert len(probe['streams'])==1 and(v['nb_frames'],v['r_frame_rate'],v['width'],v['height'])==('23','24/1',1920,1080)and abs(float(v['duration'])-23/24)<1e-6
assert sorted(x.name for x in S.glob('*.png'))==[f'{f:05}.png'for f in range(23)]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);assert len(list(D.glob('*.png')))==23
checks=[]
for f in range(23):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 head=[1062,787]if f>=20 else[1074,782]if f>=5 else[1124,755]if f>=3 else[1076,764]
 if f>=20:
  x,y=head;crop=b[y-45:y+9,x-22:x+23];hot=(crop[:,:,0]>=240)&(crop[:,:,1]>=150)&(crop[:,:,2]>=60);assert hot.any()
  wick=b[775:810,1395:1435];assert not((wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60)).any()
 checks.append({'frame':f,'Canvas_source_sha256':sha(S/f'{f:05}.png'),'encoded_vs_source_MSE':mse,'actual_match_head':head})
selected=[0,13,17,19,20,22]
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
board(selected,'00_requested_actual_decodes.jpg')
board([19,20,22],'01_leave_box_whole_arms_actual.jpg',box=(670,690,1310,1030),tile=(650,350))
board([19,20,22],'02_empty_palm_high_rod_actual2x.jpg',box=(1100,690,1330,930),tile=(470,480),scale=2)
board([19,20,22],'03_match_true_head_actual3x.jpg',box=(1010,735,1100,860),tile=(280,375),scale=3)
board([17,19,20,22],'04_table_box_base970_actual4x.jpg',box=(1045,935,1165,985),tile=(490,200),cols=4,scale=4)
baseline=json.loads(Path('/tmp/s08_first20_baseline_for23.json').read_text());old=[]
# Union of old/new lever centerlines and tip radii derived from pivot/sc/angles,
# rounded outward with a small AA margin. This ROI excludes the character/box.
roi=[1225,720,1315,845];compare=Image.new('RGB',(960,1575),'#f3f0e8');draw=ImageDraw.Draw(compare)
for i,f in enumerate([0,13,17]):
 prior=ROOT/f'build/S08_first20/{f:05}.png';assert sha(prior)==baseline['checks'][f]['Canvas_source_sha256']
 a=np.array(Image.open(prior));b=np.array(Image.open(S/f'{f:05}.png'));m=np.any(a!=b,axis=2);outside=m.copy();x,y,X,Y=roi;outside[y:Y,x:X]=False;assert not outside.any()
 yy,xx=np.where(m);assert len(xx)>0
 old.append({'frame':f,'old20_source_sha256':sha(prior),'new23_source_sha256':sha(S/f'{f:05}.png'),'changed_pixels':len(xx),'actual_bbox_xyxy_exclusive':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'authorized_lever_roi':roi,'outside_ROI_changed_pixels':0})
 for col,(im,label)in enumerate([(Image.open(prior),'旧20低杆原实帧'),(Image.open(S/f'{f:05}.png'),'新23高杆原实帧')]):
  crop=im.convert('RGB').crop((1205,700,1360,860)).resize((465,480),Image.Resampling.NEAREST);x,y=col*480+5,i*525+38;compare.paste(crop,(x,y));draw.text((x,y-30),f'F{f:03} '+label,font=font(20),fill='#25333d')
compare.save(P/'05_old20_new23_lever_actual_comparison.jpg',quality=97)
(P/'old20_lamp_only_difference.json').write_text(json.dumps({'status':'PASS_OLD_ACTUAL20_SELECTED_DIFF_ONLY_LEVER','old_actual_commit':'69d2e31fb4a785b2a45abcacca170b05530b6ad7','old20_rerendered_this_task':False,'comparison':'old saved lossless Canvas PNG vs new23 saved lossless Canvas PNG;not MP4 decodes','geometric_basis':{'pivot':[1301.48649,791.54595],'scale':14/18.5,'old_initial_angle':.55,'new_initial_angle':-.85},'checks':old},ensure_ascii=False,indent=2)+'\n')
module=SRC/'s08_first23_scene.js';assert sha(module)=='26d3a8aeb40a9208040ff04c8535a450585330ca596076f0f16294191ae77cc7'
lamp=ROOT/'collab/reviews/20261018_1822_s08_lamp_mechanical_candidate/lamp_mechanical_candidate.js';assert sha(lamp)=='171aaace1079af7215788f38ebc2f35e4c0af09d8fd5d722009094443ff90bf1'
for f in [*SRC.glob('*.js'),*SRC.glob('frames/*.png'),lamp,ROOT/'js/code/s08.js',ROOT/'js/paint/paintshot.js',ROOT/'assets/paint/bg_01_room_wide.png',ROOT/'tools/js/frames.cjs']:assert f.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{f.relative_to(ROOT)}'])
box=np.array(Image.open(SRC/'frames/F020_table_box_original_pixels.png'));oldbox=np.array(Image.open(SRC/'frames/F017_table_box_original_pixels.png'));m=box[:,:,3]>0;assert int(m.sum())==1665 and np.array_equal(box[:,:,3],oldbox[:,:,3])and np.array_equal(box[m],oldbox[m]);ys,xs=np.where(box[:,:,3]>128);assert ys.max()==970
for role in ['body','arms']:
 im=np.array(Image.open(SRC/f'frames/F020_{"body_behind"if role=="body"else"forearms_elbows"}_original_pixels.png'));assert not np.any((im[:,:,3]>0)&m)
source={'status':'PASS_FIXED_SOURCE_AND_ONCE_ONLY_UNCHANGED_VISIBLE_BOX','module_sha256':sha(module),'local_lamp_sha256':sha(lamp),'native_layers':18,'box_visible_pixels':1665,'box_bottom_y':970,'F020_box_alpha_and_visibleRGBA_exact017':True,'box_alpha_duplicate_in_body_arms':0,'fixed_Git_bytes_unchanged':True,'match_head020_022':[1062,787],'lift_wick':0}
(P/'source_validation.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
result={'status':'PASS_REAL23_ENCODE_SOURCE_AND_LAMP_ONLY_DIFF','fixed_commit':FIXED,'frames':23,'fps':'24/1','size':[1920,1080],'seconds':23/24,'audio_streams':0,'selected_decoded':selected,'frame023_and_later_rendered':False,'old20_rerendered':False,'all23_encoding_order_verified':True,'max_MSE':max(x['encoded_vs_source_MSE']for x in checks),'mp4_sha256':sha(mp4),'checks':checks,'visual_review':'SeeREADME;partial shot only,not audio/fullshot ready.'}
(P/'actual23_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(P/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print('PASS real23f/1080p/24fps;all23 encoding order;maxMSE',result['max_MSE'])
print('PASS oldactual000/013/017differences1165/1167/1166pixels only lamp rod;outsideROI0;boxstillone1665pixels at970;020head1062,787;sourcefixed')
