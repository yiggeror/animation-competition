from pathlib import Path
import json,hashlib,subprocess,shutil,csv
import numpy as np
from PIL import Image,ImageDraw
O=Path('collab/reviews/cloud_s12_20261018/F030_close_grip_from_locked026_20261019');G=O/'group_delivery';G.mkdir();(G/'final_native').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();c30='d7ab7768e0d99e92a02de321a466d47ec4ca5788'
S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019';M=O.parent/'F026_index_repair_actual_call01_20261019'
plans=[(22,25,'59497f0bcdd4c004dfacfce5bbe4f62bbaefe3c2',S/'candidate/F022.png',S/'actual_scene/F022_canvas.png','2c28bafe7ee05c5b234711fc551dd2a4d358143ea2615dc0a2282428aa744332','1a0732e0fc879d086c04255dfdb507799d2be59fd21bfc91be025fd9cf809a2f','LOCKED_THUMB_FIRST'),(26,29,'3ac42dabd48a08c420b4071c766abdb7894d9050',M/'candidate/F026.png',M/'actual_scene/F026_canvas.png','34515fa0f42af3c360004b7530142d7c077b9ba344da7eccd0dad26042eb4934','0bf8fe07e236f0a8a139807c65033e47028512954118de8a6748a80d9e820d6c','LOCKED_INDEX_WRAP'),(30,33,c30,O/'candidate/F030.png',O/'actual_scene/F030_canvas.png','ace73556d7e6527c6e13779219a66f541f497078f9d05ed691612345042ef9b1','95f8e3bf3f15c2c6515bd8647fcf289613769b22cf9c228fdfb858d875b83ae2','AUTHOR_PASS_CLOSED_LEFT_GRIP_DIRECT_REVIEW')]
rows=[];B=Path('build/S12_F022_F026_F030_12f_actualCanvas_exposure');D=Path('build/S12_F022_F026_F030_12f_actualCanvas_decoded');assert not B.exists() and not D.exists();B.mkdir();D.mkdir();frameledger=[]
for f,last,commit,native,canvas,nh,ch,status in plans:
 assert sha(native)==nh and sha(canvas)==ch
 for p in [native,canvas]:assert p.read_bytes()==subprocess.check_output(['git','show',commit+':'+str(p)])
 export=G/f'final_native/F{f:03d}.png';shutil.copyfile(native,export);assert sha(export)==nh
 r={'first_frame':f,'last_frame':last,'hold_frames':4,'fps':24,'fixed_source_commit':commit,'source_native_PNG_path':str(native),'native_PNG_SHA256':nh,'group_native_export':str(export),'source_actual_Canvas_path':str(canvas),'actual_Canvas_SHA256':ch,'state':status};rows.append(r)
 for frame in range(f,last+1):
  p=B/f'{frame:05d}.png';shutil.copyfile(canvas,p);assert sha(p)==ch;frameledger.append({'frame':frame,'native_state':f,'native_SHA256':nh,'fixed_source_commit':commit,'actual_Canvas_source_SHA256':ch,'held_frame_PNG_SHA256':sha(p),'new_Canvas_render':False})
(G/'fixed_native_Canvas_sources.json').write_text(json.dumps(rows,indent=2)+'\n');(G/'all12_actual_Canvas_hold_ledger.json').write_text(json.dumps(frameledger,indent=2)+'\n')
with (G/'final_PNG_commit_path_SHA_and_exposure.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
video=G/'S12_F022_F026_F030_12f_actualCanvas_hold.mp4';cmd=['ffmpeg','-v','error','-framerate','24','-start_number','22','-i',str(B/'%05d.png'),'-frames:v','12','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation',str(video)];subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));vs=[s for s in probe['streams'] if s['codec_type']=='video'];assert len(probe['streams'])==len(vs)==1;v=vs[0];assert(int(v['nb_frames']),v['width'],v['height'],v['r_frame_rate'],float(v['duration']))==(12,1920,1080,'24/1',.5);(G/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
subprocess.run(['ffmpeg','-v','error','-i',str(video),str(D/'%02d.png')],check=True);decoded=sorted(D.glob('*.png'));assert len(decoded)==12;checks=[]
for i,p in enumerate(decoded):
 ref=Path(rows[i//4]['source_actual_Canvas_path']);a=np.array(Image.open(p).convert('RGB')).astype(float);b=np.array(Image.open(ref).convert('RGB')).astype(float);mse=float(np.mean((a-b)**2));assert mse<25;checks.append({'timeline_frame':22+i,'source_actual_Canvas_SHA256':sha(ref),'decoded_frame_SHA256':sha(p),'RGB_MSE':mse})
(G/'all12_actual_source_decode_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
board=Image.new('RGB',(1440,300),'#202426');hand=Image.new('RGB',(1980,654),'#202426');ds=ImageDraw.Draw(board);dh=ImageDraw.Draw(hand)
for k,(i,state) in enumerate([(0,22),(4,26),(8,30)]):
 im=Image.open(decoded[i]).convert('RGB');board.paste(im.resize((480,270)),(k*480,25));ds.text((k*480+8,6),f'ACTUAL CANVAS HOLD / F{state:03d} x4 / MP4 DECODE',fill='white');crop=im.crop((900,718,1010,822)).resize((660,624),Image.Resampling.NEAREST);hand.paste(crop,(k*660,30));dh.text((k*660+8,9),f'ACTUAL DECODE / F{state:03d} x4',fill='white')
board.save(G/'actual_hold_MP4_decoded_three_states.jpg',quality=95);hand.save(G/'actual_hold_MP4_decoded_hand_three_states.jpg',quality=95)
report={'status':'THREE_STATE_ACTUAL_CANVAS_HOLD_EXPOSURE_VERIFIED_NOT_NEW_PRODUCTION_RENDER','timeline_frames':[22,33],'frames':12,'fps':'24/1','size':[1920,1080],'duration_seconds':.5,'audio_streams':0,'holds':[[22,25,4],[26,29,4],[30,33,4]],'new_scene_Canvas_renders_for_this_group':0,'reused_unique_actual_Canvas_frames':[22,26,30],'exposure_is_frozen_actual_Canvas_holds_including_existing_light_grain':True,'not_a_claim_of_newly_rendered_per_frame_production':True,'final_native_exports_byte_equal_fixed_source_commits':True,'source_native_and_Canvas_bindings_in_manifest':True,'no_post_manifest_native_colour_or_AA_change':True,'new_imagegen_calls_for_group':0,'F030_call_count_total':1,'new034_or_right_hand_calls':0,'MP4_SHA256':sha(video),'max_decoded_RGB_MSE':max(x['RGB_MSE'] for x in checks),'F026_lower_air_convention':{'pixel_centres':3,'pixel_square_boundaries':2},'F030_lower_air_convention':{'pixel_centres':3,'pixel_square_boundaries':2}};(G/'exposure_verification.json').write_text(json.dumps(report,indent=2)+'\n');(G/'encode_command.json').write_text(json.dumps(cmd,indent=2)+'\n')
(G/'README.md').write_text('''# Final022 /026 /030 native and actual-Canvas exposure delivery

`final_PNG_commit_path_SHA_and_exposure.csv` and `fixed_native_Canvas_sources.json` give all three final native PNGs, exact immutable source commits/paths/SHA, and their corresponding actualCanvas SHA. `final_native/F022.png`, `F026.png`, `F030.png` are byte-identical convenience copies.022 and026 retain their official locks unchanged;030 is the author-passed actual closed grasp for the direct reviewer.

Exposure:022–025,026–029,030–033, **4frames each at24fps**,12frames /0.5s /1920×1080 /silent. `S12_F022_F026_F030_12f_actualCanvas_hold.mp4` holds each existing verified actualCanvas4times. **This is actualCanvas exposure verification, not new per-frame production rendering.** Existing light/grain is frozen within each hold. No old scene was rerendered; no extra imagegen or newCanvas capture is used for this group. All12 source-copy hashes and decoded MSE are recorded; three decoded scene/hand keys were inspected.

Only actual source ownership/depth compositing was used for030. The native palette/form shade and accepted022/026 pixels were kept; no later colour/AA operation changes these final hashes or the linked exposure sources. The current source/native binding is explicit and immutable.030’s new foreground can naturally cover old occluded edges while actual thumb first-touch and index contact patches stay exact. The accepted lower-air convention is **3pixel-centres /2pixel-square boundaries**, not3px boundary air.

Next dependency only: near RIGHT must first establish its body-rod grip. After BOTH grips hold, a separately approved segment may raise hip/chest/shoulders/head together with knees/shins/instep on the floor, then lift crane/toward lamp. No direct030→dual-grip-rise jump.034/right-hand continuation remains closed; see the parent packet’s dependency JSON. No shared ready/EDL/audio edits.
''')
with(O/'README.md').open('a') as f:f.write('\nGroup exposure delivered under `group_delivery/`: all3fixed commit/path/SHA rows and022–025/026–029/030–033 four-frame holds are provided; it is cached actualCanvas exposure verification, not fresh production rendering.\n')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':manifest.append(sha(p)+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS').write_text('\n'.join(manifest)+'\n');print(json.dumps({'F030_source_commit':c30,'group_report':report,'final_native_rows':[{k:r[k] for k in ['first_frame','fixed_source_commit','native_PNG_SHA256','source_native_PNG_path']} for r in rows]}))
