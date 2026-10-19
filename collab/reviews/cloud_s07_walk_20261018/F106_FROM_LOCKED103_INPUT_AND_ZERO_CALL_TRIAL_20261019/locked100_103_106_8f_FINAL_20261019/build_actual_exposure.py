from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parent;P=R.parent;B=P.parent;REPO=P.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={100:B/'F100_WHOLE_RAW_BLOUSE_FINAL_20261019/candidate/F100_WHOLE_RAW_BLOUSE_final_RGBA_PENDING_ASTRA.png',103:B/'F103_REPAIR_NATIVE_call02_fa796ff9_20261019/candidate/F103_REPAIR_call02_PROTECTED_SEMANTIC_TRIAL_PENDING_ASTRA.png',106:P/'zero_call_semantic_cloth_trial_20261019/candidate/F106_ZERO_CALL_LOCKED103_WHOLE_CHAIN_actual106_CLOTH_BACKPLATE_PENDING_ASTRA.png'}
expected={100:'7dc803e92e69cb90a84465f4b25e64f5ba9ea62b6b3853bd9a66b658f9951b2b',103:'06443a17f780d7a72a293c27686099ffaf72ba827b00e3290059c3061cd2ad90',106:'13bd048bc8a23519ab284c31ae477b1adea387d45df77fa55efafb8d850bec21'}
for d in ['sources','exposure','frames_tmp','decoded_tmp','qa']:(R/d).mkdir(parents=True,exist_ok=True)
for n,p in paths.items():
 assert sha(p)==expected[n]
 shutil.copyfile(p,R/f'sources/F{n:03d}_ACTUAL_LOCKED.png')
images={n:Image.open(p).convert('RGBA')for n,p in paths.items()};size=(1960,1080);assert all(im.size==size for im in images.values())
states=[100,103,106];order=[100,100,100,103,103,103,106,106]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
checks={'state':'LOCKED_ACTUAL100x3_103x3_106x2_PENDING_ACTUAL_VIEW','source_SHA256':{str(n):sha(p)for n,p in paths.items()},'source_commits':{'100':'61766ddbbde81bf1a15e7b846211ea8a25d8950f','103':'84334c3f7b0ab72e9e700ae3e165617945ef615e','106':'68553dd89134163ab1c3c5482c8711f15d4f6156'},'source_origin':'all actual locked final PNGs; no inputs or technical prepose','native_registration':'1960x1080 at0,0; no scale,crop,part movement or recolor','exposure':{'100':3,'103':3,'106':2,'total':8,'fps':24,'duration':8/24},'native_new_requests':0,'F106_total':{'requests':1,'raw':1,'retries':0,'new_final_repair_requests':0},'variants':{}}
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 refs={}
 for n,im in images.items():
  bg=Image.new('RGBA',size,col);bg.alpha_composite(im);refs[n]=np.array(bg.convert('RGB'))
 for i,n in enumerate(order):Image.fromarray(refs[n]).save(R/f'frames_tmp/{tone}_{i:02d}.png')
 video=R/f'exposure/S07_LOCKED100x3_103x3_106x2_{tone}_ACTUAL8f_24fps.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(R/f'frames_tmp/{tone}_%02d.png'),'-frames:v','8','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(R/f'qa/ffprobe_{tone}.json').write_text(json.dumps(probe,indent=2)+'\n')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vsync','0',str(R/f'decoded_tmp/{tone}_%02d.png')],check=True)
 files=sorted((R/'decoded_tmp').glob(f'{tone}_*.png'));assert len(files)==8;classes=[]
 for i,p in enumerate(files):
  z=np.array(Image.open(p).convert('RGB')).astype(float);errs=[float(np.abs(z-refs[n].astype(float)).mean())for n in states];got=states[int(np.argmin(errs))];assert got==order[i];classes.append({'decoded_index':i,'source_state':got,'expected_state':order[i],'matching_MAE':min(errs)})
 stream=next(s for s in probe['streams']if s['codec_type']=='video');assert stream['avg_frame_rate']=='24/1'and int(stream['nb_read_frames'])==8 and not any(s['codec_type']=='audio'for s in probe['streams'])
 checks['variants'][tone]={'video_SHA256':sha(video),'decoded_frames':8,'fps':stream['avg_frame_rate'],'duration':float(stream['duration']),'audio_streams':0,'all8_actual_states_correct':True,'all8_classifications':classes}
 board=Image.new('RGB',(1920,1190),(232,238,244));dr=ImageDraw.Draw(board)
 for j,i in enumerate([2,3,5,6]):
  z=Image.open(files[i]).convert('RGB');x=j*480;dr.text((x+8,6),f'ACTUAL decode{i}/F{order[i]:03d}',font=font,fill='#36536b');board.paste(z.crop((1300,0,1890,1080)).resize((472,864)),(x,32));board.paste(z.crop((1510,285,1810,475)).resize((470,298)),(x,890))
 board.save(R/f'qa/ACTUAL8f_decoded2_3_5_6_full_and_true_grip_{tone}.png')
# Original table and the already verified fixed late-shot camera. Draw only the
# actual final whole-action PNG; scene tableLamp(0) is disabled for every frame.
bgp=REPO/'assets/paint/bg_01_room_wide.png';background=Image.open(bgp).convert('RGBA');assert background.size==(1672,941)
scale=.36410361842105265;tx=627.0254537171638;ty=402.7604324894813
camera_crop=(720,360,1488,792)
sceneviews={}
for n,im in images.items():
 mapped=im.transform(background.size,Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC,fillcolor=0)
 scene=background.copy();scene.alpha_composite(mapped)
 view=scene.crop(camera_crop).resize((1280,720),Image.Resampling.LANCZOS);view.save(R/f'qa/F{n:03d}_ORIGINAL_TABLE_FIXED_CAMERA_actual_geometry.png');sceneviews[n]=view
board=Image.new('RGB',(1920,1000),(232,238,244));dr=ImageDraw.Draw(board)
for j,n in enumerate(states):
 dr.text((j*640+8,8),f'F{n:03d} original table / one lamp / fixed camera',font=font,fill='#36536b');board.paste(sceneviews[n].resize((640,360)).convert('RGB'),(j*640,36));board.paste(sceneviews[n].crop((780,350,1120,560)).resize((612,378)).convert('RGB'),(j*640+10,430))
board.crop((0,0,1920,830)).save(R/'qa/ORIGINAL_TABLE_fixed_camera_100_103_106_support_and_lift.png')
checks['table_camera']={'background_source':'assets/paint/bg_01_room_wide.png','background_SHA256':sha(bgp),'native_to_world':{'s':scale,'tx':tx,'ty':ty},'same_fixed_world_crop':camera_crop,'preview_size':[1280,720],'original_scene_tableLamp_0_draws':0,'whole_action_PNG_draws_per_frame':1,'original_known_lamp_base_native103':[1743.939126549811,657.0645151728758],'locked106_same_base_native':[1743.939126549811,657.0645151728758-12.359119141727836],'base_world103':[1262,642],'base_world106':[1262,637.5],'same_whole_motion_group_native_dy':-12.359119141727836,'stationary_table_shadow_native_transform':[0,0],'table_shadow_baseline_only_not_lifted_lighting_certification':True,'render_scope':'three actual locked-state composites on original table with verified fixed camera; unlit geometry proof, no coded people, no full scene or108f render'}
(R/'qa/actual8_decode_and_table_source_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
for d in ['frames_tmp','decoded_tmp']:shutil.rmtree(R/d)
print(json.dumps({k:{q:v[q]for q in ['video_SHA256','decoded_frames','fps','duration','all8_actual_states_correct']}for k,v in checks['variants'].items()},indent=2))
