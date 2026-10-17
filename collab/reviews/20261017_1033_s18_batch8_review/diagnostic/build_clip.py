#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess
P=Path(__file__).resolve().parent;R=Path('/workspace/animation-competition');B=Path('/tmp/batch8_registration');V=Path('/tmp/laidian-s18-pilot-audit/generated_k06_character/v2')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype(str(R/'assets/fonts/NotoSansSC-VF.ttf'),26);smallfont=ImageFont.truetype(str(R/'assets/fonts/NotoSansSC-VF.ttf'),19)
keys=['x16_original','k02','k03','k04','k05','k06_v2','k07_original','k08','k09','k10','k11']
paths=[R/'assets/chars/x16_arms_loose.png']+[B/'registered_rgba'/f'x18_{k}_registered_635x1175.png' for k in ['k02','k03','k04','k05']]+[V/'evidence/v2_diagnostic_registered_to_master_635x1175_RGBA.png',R/'assets/chars/x18_laugh.png']+[B/'registered_rgba'/f'x18_{k}_registered_635x1175.png' for k in ['k08','k09','k10','k11']]
timeline=[[0,0],[6,1],[9,2],[15,3],[18,4],[21,5],[24,6],[27,7],[30,8],[33,7],[36,8],[39,7],[42,8],[45,9],[54,10],[63,8],[66,6]]
reg={v['key']:v for v in json.loads((B/'registration_measurements.json').read_text())['frames']};vreg=json.loads((V/'registration_measurements.json').read_text())
frames=[];states=[];canvases=[];gray=(220,220,220,255);place=[162,68];W,H=960,1280
for i,(key,p) in enumerate(zip(keys,paths)):
 im=Image.open(p).convert('RGBA');assert im.size==(635,1175)
 canvas=Image.new('RGBA',(W,H),gray);canvas.alpha_composite(im,tuple(place));c=canvas.convert('RGB');d=ImageDraw.Draw(c)
 d.text((26,12),'S18 三秒关键帧诊断｜非成片',font=font,fill='#222222');d.text((26,45),'灰底 / 24fps / 硬切曝光 / 无音轨',font=smallfont,fill='#444444')
 d.text((26,1250),f'{key}　仅检查身份跳变与循环；不代表自然表演通过',font=smallfont,fill='#333333');canvases.append(c)
 entry={'index':i,'state':key,'input_path':str(p),'input_sha256':sha(p),'input_size':[635,1175],'placement_matrix':[[1,0,place[0]],[0,1,place[1]],[0,0,1]]}
 if key in reg:
  q=reg[key];entry.update({'original_path':q['source_path'],'original_sha256':q['source_sha256'],'original_size':q['source_size'],'original_to_input_matrix':q['homogeneous_matrix']})
 elif key=='k06_v2':
  entry.update({'previous_registration_measurements':str(V/'registration_measurements.json'),'previous_registration_sha256':sha(V/'registration_measurements.json'),'original_to_input_matrix':[[*vreg['candidate_native_to_master_matrix'][0],vreg['translation'][0]],[*vreg['candidate_native_to_master_matrix'][1],vreg['translation'][1]],[0,0,1]],'registration_reused_without_refit':True})
 else:entry['original_to_input_matrix']=[[1,0,0],[0,1,0],[0,0,1]]
 states.append(entry)
for f in range(72):
 idx=max(j for j,(at,_) in enumerate(timeline) if at<=f);state=timeline[idx][1];frames.append({'frame':f,'time_seconds':f/24,'state_index':state,'state':keys[state]})
mp4=P/'S18_72f_24fps_diagnostic.mp4'
cmd=['ffmpeg','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
with (P/'ffmpeg.log').open('w') as log:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 for fr in frames:proc.stdin.write(canvases[fr['state_index']].tobytes())
 proc.stdin.close();code=proc.wait();assert code==0
# One diagnostic sheet with all eleven true states, no sequential PNG export.
cols=4;tw,th=254,504;sheet=Image.new('RGB',(tw*cols,th*3),(245,245,245));d=ImageDraw.Draw(sheet)
for i,(key,p) in enumerate(zip(keys,paths)):
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,gray);bg.alpha_composite(im);thumb=bg.convert('RGB').resize((254,470),Image.Resampling.LANCZOS);x=(i%cols)*tw;y=(i//cols)*th;sheet.paste(thumb,(x,y+34));d.text((x+6,y+6),f'{i}: {key}',font=smallfont,fill='black')
sheet.save(P/'key_states_contact_sheet.jpg',quality=94)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)]));streams=probe['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video';v=streams[0];assert int(v['nb_read_frames'])==72 and v['avg_frame_rate']=='24/1' and abs(float(probe['format']['duration'])-3)<1e-9
subprocess.run(['ffmpeg','-v','error','-i',str(mp4),'-f','null','-'],check=True)
left=next(x for x in vreg['anchor_matches'] if x['name']=='C_leftfoot');right=next(x for x in vreg['anchor_matches'] if x['name']=='B_rightfoot')
v2diff={'existing_method':'old v2 fit used left seat corner plus right foot, not this batch two-foot fit','left_foot_registered':left['registered'],'left_foot_current_batch_target':[22,1142],'left_foot_delta_px':[left['registered'][0]-22,left['registered'][1]-1142],'right_foot_registered':right['registered'],'right_foot_current_batch_target':[312,1142],'right_foot_delta_px':[right['registered'][0]-312,right['registered'][1]-1142],'no_additional_registration_applied':True}
manifest={'purpose':'S18 full three-second key-state diagnostic; no claim of natural performance approval','width':W,'height':H,'frame_count':72,'fps':24,'duration_seconds':3,'audio_streams':0,'states':states,'timeline':timeline,'frames':frames,'composition':'Original 635x1175 registered/native input placed at integer (162,68), no rescale/crop/interpolation/local correction. Alpha composited on RGB220 gray; titled; hard cuts only. H264 encoding is lossy.','k06_v2_registration_difference':v2diff,'inputs':'8 new batch candidates + 1 prior generated k06 v2 + 2 existing mother poses; no k06 v1','ffmpeg_command':cmd,'ffprobe':{'codec':v['codec_name'],'pix_fmt':v['pix_fmt'],'nb_read_frames':v['nb_read_frames'],'avg_frame_rate':v['avg_frame_rate'],'duration':probe['format']['duration']},'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(P.iterdir()) if p.is_file() and p.name!='manifest.json'}}
dump(P/'manifest.json',manifest)
print(json.dumps({'mp4':str(mp4),'sha256':sha(mp4),'manifest_sha256':sha(P/'manifest.json'),'v2_difference':v2diff,'frame_count':72,'duration_seconds':3},ensure_ascii=False,indent=2))
