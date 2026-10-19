from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parent;B=R.parent;size=(1960,1080);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in['sources','frames_reference','exposure','decoded_gray','decoded_dark','qa']:(R/d).mkdir(exist_ok=True)
src095=B/'F100_next_gate_20261019/sources/F095_dcf919f4_LOCKED_MOTHER.png';src100=B/'F100_WHOLE_RAW_BLOUSE_FINAL_20261019/candidate/F100_WHOLE_RAW_BLOUSE_final_RGBA_PENDING_ASTRA.png';lampp=B/'F100_local_arm_call02_input_GATE_20261019/sources/ORIGINAL_fixed_lamp_same_native_registration.png'
assert sha(src095)=='dcf919f412fd379a34ea69329210a418547dcccc089e1b36aa208024a04fdca4';assert sha(src100)=='7dc803e92e69cb90a84465f4b25e64f5ba9ea62b6b3853bd9a66b658f9951b2b'
for n,p in [('F095_locked_original.png',src095),('F100_locked_original.png',src100),('FIXED_original_lamp.png',lampp)]:shutil.copyfile(p,R/'sources'/n)
lamp=Image.open(lampp).convert('RGBA');p095=Image.new('RGBA',size);p095.alpha_composite(Image.open(src095).convert('RGBA'),(0,0));p095.alpha_composite(lamp,(0,0));p100=Image.open(src100).convert('RGBA');assert p100.size==size
#100 already contains this original lamp exactly once; never double-composite its AA.
a095=np.array(p095);a100=np.array(p100);la=np.array(lamp);lm=la[:,:,3]>0;lamp_diff=int(np.any(a095[lm]!=a100[lm],axis=1).sum())
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
checks={'status':'LOCKED_STATIC_EXPOSURE_ONLY_PENDING_ACTUAL_DECODE_VIEW','sources':{'095':{'sha256':sha(src095),'size':Image.open(src095).size},'100':{'sha256':sha(src100),'size':p100.size},'lamp':{'sha256':sha(lampp),'size':lamp.size}},'canvas':[1960,1080],'registration':'native origin(0,0), canvas extension only, no scale or independent fit','exposure':{'095':5,'100':3,'total':8,'fps':24,'expected_duration_seconds':8/24},'static_color_edits':False,'lamp_same_position_composite_RGBA_differing_pixels_alphaGT0':lamp_diff,'lamp_alpha_GT0_pixels':int(lm.sum()),'100_already_contains_original_lamp_not_overlaid_twice':True,'variants':{}}
for tone,bgcol in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 frames=[]
 for state,img in[(95,p095),(100,p100)]:
  z=Image.new('RGBA',size,bgcol);z.alpha_composite(img);z=z.convert('RGB');z.save(R/f'frames_reference/F{state:03d}_{tone}.png');frames.append(np.array(z))
  for i in(range(0,5)if state==95 else range(5,8)):z.save(R/f'frames_reference/{tone}_{i:02d}.png')
 video=R/f'exposure/S07_F095x5_F100x3_{tone}_ACTUAL_8f_24fps.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(R/f'frames_reference/{tone}_%02d.png'),'-frames:v','8','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vsync','0',str(R/f'decoded_{tone}/frame_%02d.png')],check=True)
 decoded=sorted((R/f'decoded_{tone}').glob('frame_*.png'));assert len(decoded)==8;classification=[]
 for i,p in enumerate(decoded):
  z=np.array(Image.open(p).convert('RGB')).astype(float);mae=[float(np.abs(z-f.astype(float)).mean())for f in frames];got=[95,100][int(np.argmin(mae))];expected=95 if i<5 else 100;classification.append({'frame':i,'state':got,'expected':expected,'MAE_to095':mae[0],'MAE_to100':mae[1]});assert got==expected
 stream=next(s for s in probe['streams']if s['codec_type']=='video');assert stream['avg_frame_rate']=='24/1'and int(stream['nb_read_frames'])==8 and not any(s['codec_type']=='audio'for s in probe['streams'])
 checks['variants'][tone]={'video_sha256':sha(video),'width':stream['width'],'height':stream['height'],'avg_frame_rate':stream['avg_frame_rate'],'decoded_frame_count':len(decoded),'duration_seconds':float(stream['duration']),'audio_streams':0,'classification_all_actual_frames':classification,'all_decoded_states_correct':True}
 (R/f'qa/ffprobe_{tone}.json').write_text(json.dumps(probe,indent=2)+'\n')
 sheet=Image.new('RGB',(2040,770),(233,239,244));dr=ImageDraw.Draw(sheet)
 for j,i in enumerate([0,4,5,7]):
  im=Image.open(decoded[i]).convert('RGB');sheet.paste(im.resize((490,270)),(j*510+10,30));dr.text((j*510+10,5),f'ACTUAL frame{i} / F{95 if i<5 else 100:03d}',font=font,fill='#36536b');c=im.crop((1320,180,1830,900));sheet.paste(c.resize((306,432),Image.Resampling.NEAREST),(j*510+100,325))
 sheet.save(R/f'qa/actual_decoded_0_4_5_7_{tone}_contact_sheet.png')
 conn=Image.new('RGB',(1280,1380),(233,239,244));dr=ImageDraw.Draw(conn)
 for j,i in enumerate([4,5]):
  im=Image.open(decoded[i]).convert('RGB')
  for k,(box,title)in enumerate([((1420,220,1810,465),'Sleeve/wholehand/fixed bail'),((1340,450,1660,745),'Whole blouse/waist/farhand'),((1340,940,1585,1035),'Fixed shoes / ground')]):
   c=im.crop(box);w,h=c.size;targetw=620;targeth=round(h*targetw/w);c=c.resize((targetw,targeth),Image.Resampling.NEAREST)
   y=[35,465,1100][k];conn.paste(c,(j*640+10,y));dr.text((j*640+10,y-27),f'actual frame{i}: '+title,font=font,fill='#36536b')
 conn.save(R/f'qa/actual_decoded_4_to5_key_connections_{tone}.png')
(R/'qa/actual_decode_and_source_checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
