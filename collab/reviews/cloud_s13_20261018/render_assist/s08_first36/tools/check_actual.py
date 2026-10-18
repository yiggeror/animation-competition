#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,shutil,numpy as np
H=Path(__file__).resolve().parents[1];ROOT=Path.cwd();FIXED='2a8fcb919cc4efe59169be80650d10621427ef25';SRC=ROOT/'collab/reviews/20261018_2034_s08_first36_scene';S=ROOT/'build/S08_first36';D=Path('/tmp/s08_first36_actual_decoded');D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIXED
entry=SRC/'s08_first36_scene.js';assert sha(entry)=='58ab66325e19ff46d0b295ec428bfc7afd5137a02de6c415582f7fd32179f754'
assert sorted(p.name for p in (ROOT/'build/S08_first36_increment').glob('*.png'))==['00033.png','00034.png','00035.png']
assert sorted(p.name for p in S.glob('*.png'))==[f'{n:05}.png'for n in range(36)]
base=json.loads((H/'old33_saved_PNG_baseline.json').read_text());reuse=[]
for row in base['frames']:
 p=ROOT/row['path'];q=S/f"{row['frame']:05}.png";assert sha(p)==row['sha256']==sha(q);reuse.append({'frame':row['frame'],'sha256':sha(q),'reused_saved_actual_Canvas':True,'rerendered':False})
static=json.loads((H/'static_regression_run.json').read_text());assert static['first33_contract_samples_exact']==132 and static['first33_draw_commands_lighting_and_fire_identical'] and static['old_image_files_byte_equal']==30 and static['original_scene_draw_source_byte_equal']
runtime=[]
for row in json.loads((SRC/'RUNTIME_ROWS.json').read_text()):
 p=ROOT/row['repository_relative_path'];assert sha(p)==row['sha256'] and p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}']);runtime.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
for p in [ROOT/'tools/js/frames.cjs',ROOT/'js/paint/paintshot.js',ROOT/'js/code/s08.js',ROOT/'assets/paint/bg_01_room_wide.png']:
 assert p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}'])
mp4=H/'S08_first36_1920x1080_24fps.mp4';assert sha(mp4)==sha(ROOT/'build/S08_first36_1920x1080_24fps.mp4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)]));v=probe['streams'][0]
assert len(probe['streams'])==1 and(v['nb_read_frames'],v['avg_frame_rate'],v['width'],v['height'])==('36','24/1',1920,1080)and float(v['duration'])==1.5
subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);assert len(list(D.glob('*.png')))==36
checks=[]
for f in range(36):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 if f>=33:
  hot=b[665:725,1204:1256];assert np.any((hot[:,:,0]>=240)&(hot[:,:,1]>=150)&(hot[:,:,2]>=60))
  wick=b[780:808,1403:1428];assert not np.any((wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60))
 checks.append({'frame':f,'source_PNG_sha256':sha(S/f'{f:05}.png'),'origin':'reused actual33 cache'if f<33 else'new actual2a8f Canvas render','decoded_vs_source_MSE':mse})
# Native original-pixel one-box and transparent-grip checks, separate from actual visual acceptance.
box=np.array(Image.open(SRC/'frames/F033_table_box_original_pixels.png'));oldbox=np.array(Image.open(SRC/'frames/F030_table_box_original_pixels.png'));mask=box[:,:,3]>0;assert mask.sum()==1665 and np.array_equal(box[:,:,3],oldbox[:,:,3])and np.array_equal(box[mask],oldbox[mask]);ys,xs=np.where(box[:,:,3]>128);assert ys.max()==970
for name in ['body_behind','forearms_elbows']:
 a=np.array(Image.open(SRC/f'frames/F033_{name}_original_pixels.png'));assert not np.any((a[:,:,3]>0)&mask)
arm=np.array(Image.open(SRC/'frames/F033_forearms_elbows_original_pixels.png'));gate=json.loads((SRC/'F033_PIXEL_CONTACT_CHECK.json').read_text());cx,cy=gate['independent_low_knob_center'];x,y=int(cx),int(cy);seat=arm[y:y+2,x:x+2,3].tolist();assert min(min(z)for z in seat)==0
assert not np.any(arm[981:,:,3]>0)
selected=[32,33,34,35]
for f in [32,33,34,35]:shutil.copyfile(D/f'{f+1:05}.png',H/f'decoded/F{f:03}.png')
for f in [33,34,35]:shutil.copyfile(S/f'{f:05}.png',H/f'canvas_new/F{f:03}.png')
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
board([32,33,34,35],'00_requested_actual_decodes.jpg',cols=2)
board(selected,'01_whole_arms_table_front_actual.jpg',box=(660,620,1500,1035),tile=(850,415))
board(selected,'02_real_low_grip_rod_globe_actual2x.jpg',box=(1180,690,1520,910),tile=(690,450),scale=2)
board(selected,'05_near_wrist_seam_foreground_actual2x.jpg',box=(1000,650,1300,910),tile=(610,520),scale=2)
board(selected,'03_match_head_actual3x.jpg',box=(1150,650,1340,860),tile=(580,630),cols=4,scale=3)
board(selected,'04_single_box_original_contact_actual3x.jpg',box=(1035,930,1175,1005),tile=(430,225),cols=5,scale=3)
events=[json.loads(l) for l in (H/'qa/actual_browser_events.jsonl').read_text().splitlines()]
actual=sorted([r for r in events if r['event']=='actual_frame'],key=lambda r:r['frame']);assert [r['frame'] for r in actual]==[33,34,35]
for r in actual:assert r['png_sha256']==sha(S/f"{r['frame']:05}.png") and r['exposure']['asset']=='033' and r['exposure']['head']==[1230,707]
errors=[r for r in events if r['event'] in ['pageerror','requestfailed','audit_error']];assert not errors,errors
resources=[r for r in events if r['event']=='resource']
for role in ['body_behind','forearms_elbows','table_box']:
 path=SRC/f'frames/F033_{role}_original_pixels.png';rows=[r for r in resources if r['path']=='/'+str(path.relative_to(ROOT))];assert rows and all(r['status']==200 for r in rows)
probe_assets=json.loads((H/'qa/independent_browser_asset_sha_probe.json').read_text());assert probe_assets['actual_render_frames_in_probe']==0
for r in probe_assets['rows']:assert r['status']==200 and r['bytes']>0 and r['sha256']==sha(ROOT/r['path'])
assert arm[800,1127,3]==0
oldarm=np.array(Image.open(SRC/'frames/F030_forearms_elbows_original_pixels.png'))
yy,xx=np.indices(arm.shape[:2]);disk=(xx+.5-cx)**2+(yy+.5-cy)**2<=gate['independent_low_knob_radius']**2
assert int(disk.sum())==148 and np.array_equal(arm[disk],oldarm[disk])
report={'status':'ASSEMBLED36_FROM_REUSED33_PLUS_NEW3_ENCODE_PASS_ACTUAL_VISUAL_REVIEW_REQUIRED','fixed_commit':FIXED,'entry_sha256':sha(entry),'assembled_frames':36,'actually_rendered_this_task':[33,34,35],'reused_frames':list(range(33)),'full36_rerendered':False,'actual_increment_render_runs':1,'tool_invocations':2,'earlier_audit_initialization_failure_frames':0,'actual_resource_rows':resources,'asset_SHA_probe':probe_assets,'actual_empty_response_body_observations':sum(r.get('bytes')==0 for r in resources if 'F033_' in r['path']),'actual_frame_trace':actual,'page_errors':errors,'source_low_knob_disk148_RGBA_exact030':True,'obsolete_far_archive_point1127_800_runtime_alpha':0,'size':[1920,1080],'fps':'24/1','duration':1.5,'audio_streams':0,'frame036_and_later_rendered':False,'reused33_SHA_validation':reuse,'new_source_runtime_SHA_validation':runtime,'first33_static_regression_result':'static_regression_run.json','source_box':{'visible_pixels':1665,'bottom_y':970,'alpha_and_visible_RGBA_exact030':True,'body_or_arms_duplicate_box_pixels':0},'actual_low_seat_source_alpha_2x2':seat,'low_lever_geometry':{'angle':-.35,'lift':1,'center':gate['independent_low_knob_center'],'total_globe_rise_contract_px':83.24324324324324},'actual_match_head033':[1230,707],'head_delta030_to033':[82,-10],'wick_ignition':0,'all36_encoding_checks':checks,'max_encoded_MSE':max(r['decoded_vs_source_MSE']for r in checks),'mp4_sha256':sha(mp4)}
(H/'actual36_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(H/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frames':36,'reused':33,'new_actual':3,'mp4_sha256':sha(mp4),'max_MSE':report['max_encoded_MSE'],'seat_alpha':seat}))
