#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,shutil,numpy as np
H=Path(__file__).resolve().parents[1];ROOT=Path.cwd();FIXED='25705ee43f0a7e169cd9cc4ba05d50a341d6f3b1';SRC=ROOT/'collab/reviews/20261018_1940_s08_first30_scene';S=ROOT/'build/S08_first30';D=Path('/tmp/s08_first30_actual_decoded');D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIXED
entry=SRC/'s08_first30_scene.js';assert sha(entry)=='1f4c6c48e331f4e97c1ae1f9f98cf6a09e88c7e6e4183644e9a116e37b2a5f58'
assert sorted(p.name for p in (ROOT/'build/S08_first30_increment').glob('*.png'))==['00027.png','00028.png','00029.png']
assert sorted(p.name for p in S.glob('*.png'))==[f'{n:05}.png'for n in range(30)]
base=json.loads((H/'old27_saved_PNG_baseline.json').read_text());reuse=[]
for row in base['frames']:
 p=ROOT/row['path'];q=S/f"{row['frame']:05}.png";assert sha(p)==row['sha256']==sha(q);reuse.append({'frame':row['frame'],'sha256':sha(q),'reused_saved_actual_Canvas':True,'rerendered':False})
static=json.loads((H/'static_regression_run.json').read_text());assert static['first27_contract_samples_exact']==108 and static['first27_draw_commands_lighting_and_fire_identical'] and static['old_image_files_byte_equal']==24 and static['original_scene_draw_source_byte_equal']
runtime=[]
for row in json.loads((SRC/'RUNTIME_ROWS.json').read_text()):
 p=ROOT/row['repository_relative_path'];assert sha(p)==row['sha256'] and p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}']);runtime.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
for p in [ROOT/'tools/js/frames.cjs',ROOT/'js/paint/paintshot.js',ROOT/'js/code/s08.js',ROOT/'assets/paint/bg_01_room_wide.png']:
 assert p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}'])
mp4=H/'S08_first30_1920x1080_24fps.mp4';assert sha(mp4)==sha(ROOT/'build/S08_first30_1920x1080_24fps.mp4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)]));v=probe['streams'][0]
assert len(probe['streams'])==1 and(v['nb_read_frames'],v['avg_frame_rate'],v['width'],v['height'])==('30','24/1',1920,1080)and float(v['duration'])==1.25
subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);assert len(list(D.glob('*.png')))==30
checks=[]
for f in range(30):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 if f>=27:
  hot=b[752:810,1056:1108];assert np.any((hot[:,:,0]>=240)&(hot[:,:,1]>=150)&(hot[:,:,2]>=60))
  wick=b[780:808,1403:1428];assert not np.any((wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60))
 checks.append({'frame':f,'source_PNG_sha256':sha(S/f'{f:05}.png'),'origin':'reused actual27 cache'if f<27 else'new actual257 Canvas render','decoded_vs_source_MSE':mse})
# Native original-pixel one-box and transparent-grip checks, separate from actual visual acceptance.
box=np.array(Image.open(SRC/'frames/F027_table_box_original_pixels.png'));oldbox=np.array(Image.open(SRC/'frames/F025_table_box_original_pixels.png'));mask=box[:,:,3]>0;assert mask.sum()==1665 and np.array_equal(box[:,:,3],oldbox[:,:,3])and np.array_equal(box[mask],oldbox[mask]);ys,xs=np.where(box[:,:,3]>128);assert ys.max()==970
for name in ['body_behind','forearms_elbows']:
 a=np.array(Image.open(SRC/f'frames/F027_{name}_original_pixels.png'));assert not np.any((a[:,:,3]>0)&mask)
arm=np.array(Image.open(SRC/'frames/F027_forearms_elbows_original_pixels.png'));gate=json.loads((SRC/'F027_PIXEL_CONTACT_CHECK.json').read_text());cx,cy=gate['independent_knob_center'];x,y=int(cx),int(cy);seat=arm[y:y+2,x:x+2,3].tolist();assert seat==gate['alpha_at_center_four_pixels']
selected=[25,26,27,28,29]
for f in [26,27,28,29]:shutil.copyfile(D/f'{f+1:05}.png',H/f'decoded/F{f:03}.png')
for f in [27,28,29]:shutil.copyfile(S/f'{f:05}.png',H/f'canvas_new/F{f:03}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def board(ff,name,box=None,cols=3,tile=(640,360),scale=None):
 tw,th=tile;im=Image.new('RGB',(tw*cols,((len(ff)+cols-1)//cols)*(th+38)),'#eeebe3');d=ImageDraw.Draw(im)
 for i,f in enumerate(ff):
  q=Image.open(D/f'{f+1:05}.png').convert('RGB')
  if box:q=q.crop(box)
  if scale:q=q.resize((q.width*scale,q.height*scale),Image.Resampling.NEAREST)
  else:q.thumbnail((tw-8,th))
  x,y=(i%cols)*tw+4,(i//cols)*(th+38)+34;im.paste(q,(x,y));d.text((x,y-30),f'F{f:03} 实际解码',font=font(21),fill='#25333d')
 im.save(H/name,quality=98)
board([26,27,28,29],'00_requested_actual_decodes.jpg',cols=2)
board(selected,'01_whole_arms_table_front_actual.jpg',box=(660,675,1320,1035),tile=(670,370))
board(selected,'02_real_low_grip_rod_globe_actual2x.jpg',box=(1180,690,1520,910),tile=(690,450),scale=2)
board(selected,'03_match_head_actual3x.jpg',box=(1025,750,1135,875),tile=(340,375),cols=5,scale=3)
board(selected,'04_single_box_original_contact_actual3x.jpg',box=(1035,930,1175,1005),tile=(430,225),cols=5,scale=3)
report={'status':'ASSEMBLED30_FROM_REUSED27_PLUS_NEW3_ENCODE_PASS_ACTUAL_VISUAL_REVIEW_REQUIRED','fixed_commit':FIXED,'entry_sha256':sha(entry),'assembled_frames':30,'actually_rendered_this_task':[27,28,29],'reused_frames':list(range(27)),'full30_rerendered':False,'actual_increment_render_runs':1,'size':[1920,1080],'fps':'24/1','duration':1.25,'audio_streams':0,'frame030_and_later_rendered':False,'reused27_SHA_validation':reuse,'new_source_runtime_SHA_validation':runtime,'first27_static_regression_result':'static_regression_run.json','source_box':{'visible_pixels':1665,'bottom_y':970,'alpha_and_visible_RGBA_exact025':True,'body_or_arms_duplicate_box_pixels':0},'actual_low_seat_source_alpha_2x2':seat,'low_lever_geometry':{'angle':-.35,'lift':1,'center':gate['independent_knob_center'],'total_globe_rise_contract_px':83.24324324324324},'actual_match_head027':[1082,797],'head_delta025_to027':[6,3],'wick_ignition':0,'all30_encoding_checks':checks,'max_encoded_MSE':max(r['decoded_vs_source_MSE']for r in checks),'mp4_sha256':sha(mp4)}
(H/'actual30_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(H/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frames':30,'reused':27,'new_actual':3,'mp4_sha256':sha(mp4),'max_MSE':report['max_encoded_MSE'],'seat_alpha':seat}))
