from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,subprocess,shutil
R=Path(__file__).resolve().parent; Q=R/'qa'; E=Q/'native36';E.mkdir(exist_ok=True)
seq=[('000',8),('008',3),('011',3),('014',3),('017',4),('021',2),('023',2),('025',3),('028',8)]
W,H=1672,941; background=(239,239,232,255); report={'fps':24,'total_frames':36,'duration_seconds':1.5,'exposures':[],'status':'ISOLATED_CEL_TIMING_PREVIEW__NOT_INTEGRATED_FILM_PASS','foreground_hand_watermelon':'not baked; remains separate Opus foreground layer','native_mp4_size':[1672,942],'padding':'one background row on bottom only; no image scaling','variants':{}}
for variant in ['original','color_v2']:
 outdir=E/variant;outdir.mkdir(exist_ok=True); fi=0; flats={}; cells={}; hashes={}
 for f,hold in seq:
  p=R/f'color_calibration_v2/S03a_F{f}_color_v2.png' if variant=='color_v2' and f in ['014','017','021','023','025'] else R/f'candidates/S03a_F{f}.png'
  a=Image.open(p).convert('RGBA'); assert a.size==(W,H);cells[f]=a;flat=Image.alpha_composite(Image.new('RGBA',a.size,background),a).convert('RGB');flats[f]=flat
  pad=Image.new('RGB',(W,H+1),background[:3]);pad.paste(flat,(0,0)); hashes[f]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':str(p.relative_to(R))}
  start=fi
  for _ in range(hold):pad.save(outdir/f'{fi:03d}.png');fi+=1
  if variant=='original':report['exposures'].append({'cel':f,'start':start,'end_exclusive':fi,'hold':hold})
 assert fi==36
 video=E/f'S03a_36f_24fps_{variant}_ISOLATED.mp4';subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','24','-start_number','0','-i',str(outdir/'%03d.png'),'-frames:v','36','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]))
 board=Image.new('RGB',(1440,1500),'white');d=ImageDraw.Draw(board)
 for k,(f,hold) in enumerate(seq):
  x=(k%3)*480;y=(k//3)*500;d.text((x+10,y+8),f'F{f} x{hold} | {variant} | same camera / no foreground',fill='black');board.paste(flats[f].crop((470,30,1230,790)).resize((465,465)),(x+7,y+30))
 board.save(E/f'all9_same_camera_{variant}.png')
 board=Image.new('RGB',(1800,520),'white');d=ImageDraw.Draw(board)
 for k,f in enumerate(['017','021','023','025','028']):
  d.text((k*360+10,8),f'F{f} | {variant}',fill='black');board.paste(flats[f].crop((510,65,1200,890)).resize((345,413)),(k*360+7,40))
 board.save(E/f'return5_same_camera_{variant}.png');report['variants'][variant]={'cel_sources':hashes,'video':str(video.relative_to(R)),'ffprobe':probe}
(E/'exposure_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
