from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,subprocess
O=Path(__file__).resolve().parent; R=O.parent
srcs=[Path('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png'),O/'candidates/S08_F030_whole_turn_same_raw_final_color_RGBA.png']
a=np.array(Image.open(R/'F030_same_raw_semantic_v6/candidates/F030_projected_forearm_UNCLEAN_DIAGNOSTIC_RGBA.png'));b=np.array(Image.open(srcs[1]));m=np.array(Image.open(R/'F030_same_raw_semantic_v6/masks/projected_near_forearm_actual_alpha.png'))>0;c=(a!=b).any(2)&m
skin=(a[:,:,0].astype(int)-a[:,:,1]>16)&(a[:,:,1].astype(int)-a[:,:,2]>8)
p=O/'geometry/color_masks_and_checks.json';v=json.loads(p.read_text());v['near_arm_extraction_domain_changed']=v.pop('near_arm_changed');v['near_arm_skin_changed']=int((c&skin).sum());v['near_arm_extraction_domain_changes_explanation']='402 extraction-domain pixels are blue blouse/cuff contamination inside broad extraction alpha; true near-arm skin remains exactly unchanged. All differences satisfy B>R and B>G.';v['near_arm_domain_changed_all_blue']=bool(np.all((a[c,2]>a[c,0])&(a[c,2]>a[c,1])));p.write_text(json.dumps(v,indent=2))
manifest={'scope':'ISOLATED neutral character exposure, not actual Canvas lamp/table/fire scene','fps':24,'frame_count':6,'exposures':[{'state':'F027','frames':3},{'state':'F030','frames':3}],'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in srcs],'videos':[]}
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 d=O/'isolated_6f'/tag;d.mkdir(parents=True,exist_ok=True)
 for i in range(6):
  im=Image.open(srcs[i//3]).convert('RGBA');out=Image.alpha_composite(Image.new('RGBA',im.size,bg),im).convert('RGB');out.save(d/f'{i:02d}.png')
 vid=d.parent/f'F027x3_F030x3_24fps_ISOLATED_{tag}.mp4'
 subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(d/'%02d.png'),'-frames:v','6','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(vid)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(vid)]))
 assert probe['streams'][0]['nb_read_frames']=='6';dec=d/'decoded';dec.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(vid),str(dec/'%02d.png')],check=True)
 panel=Image.new('RGB',(1620,800),bg[:3]);panel.paste(Image.open(dec/'01.png').crop((530,280,1340,1080)),(0,0));panel.paste(Image.open(dec/'04.png').crop((530,280,1340,1080)),(810,0));panel.save(d.parent/f'DECODED_two_states_{tag}.jpg')
 manifest['videos'].append({'path':str(vid),'sha256':hashlib.sha256(vid.read_bytes()).hexdigest(),'bytes':vid.stat().st_size,'ffprobe':probe})
(O/'isolated_6f/EXPOSURE_AND_DECODE_CHECK.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
