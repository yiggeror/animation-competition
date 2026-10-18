from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess
O=Path(__file__).resolve().parent; R=O.parent
srcs=[R/'F033_FINAL_LOCKED/S08_F033_grandma_match_box_RGBA.png',O/'candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png']
manifest={'scope':'ISOLATED neutral character exposure, not actual Canvas lamp/table/fire scene','fps':24,'frame_count':5,'exposures':[{'state':'F033','frames':3},{'state':'F036','frames':2}],'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in srcs],'videos':[]}
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 d=O/'isolated_5f'/tag;d.mkdir(parents=True,exist_ok=True)
 for i in range(5):
  im=Image.open(srcs[i//3]).convert('RGBA');out=Image.alpha_composite(Image.new('RGBA',im.size,bg),im).convert('RGB');out.save(d/f'{i:02d}.png')
 vid=d.parent/f'F033x3_F036x2_24fps_ISOLATED_{tag}.mp4'
 subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(d/'%02d.png'),'-frames:v','5','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(vid)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(vid)]))
 assert probe['streams'][0]['nb_read_frames']=='5';dec=d/'decoded';dec.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(vid),str(dec/'%02d.png')],check=True)
 panel=Image.new('RGB',(1700,800),bg[:3]);panel.paste(Image.open(dec/'01.png').crop((620,280,1470,1080)),(0,0));panel.paste(Image.open(dec/'04.png').crop((620,280,1470,1080)),(850,0));panel.save(d.parent/f'DECODED_two_states_{tag}.jpg')
 manifest['videos'].append({'path':str(vid),'sha256':hashlib.sha256(vid.read_bytes()).hexdigest(),'bytes':vid.stat().st_size,'ffprobe':probe})
(O/'isolated_5f/EXPOSURE_AND_DECODE_CHECK.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
