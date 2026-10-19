from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,hashlib,shutil,subprocess
import numpy as np
R=Path(__file__).resolve().parent;B=R.parent
p=argparse.ArgumentParser();p.add_argument('--f060',required=True);p.add_argument('--f062',required=True);args=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={58:B/'F060_F062_TWO_turn_bridge_INPUTS_20261019/sources/F058_LOCKED044.png',60:Path(args.f060),62:Path(args.f062),63:B/'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png'}
assert sha(paths[63])=='0abc3fd9cfcf7964f825ac7be0227fb9f588da709809f6d15362063741e545ef'
for d in ['sources','exposure','qa','frames_tmp','decoded_tmp']:(R/d).mkdir(parents=True,exist_ok=True)
for n,src in paths.items():
 dst=R/f'sources/F{n:03d}_ACTUAL.png';shutil.copyfile(src,dst);paths[n]=dst
images={n:Image.open(p).convert('RGBA')for n,p in paths.items()}
assert all(im.size==(1672,941)for im in images.values())
order=[58,58,60,60,62,63,63,63,63,63,63];states=[58,60,62,63]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
check={'state':'REVIEW_ONLY_ACTUAL11F_HOLD060_PENDING062_PROP_OCCLUSION','production_adoption':False,'F060_reason':'Actual tailcap presses/covers far forearm; receiving air fails','F062_limit':'Visible air and short sleeves pass limited view; hidden tail/full rigid group pending Astra','native_requests_this_exposure':0,'source_SHA256':{str(n):sha(p)for n,p in paths.items()},'registration':'native1672x941 at0,0 without scale/crop;31px caption strip only','exposure':{'058':2,'060':2,'062':1,'063':6,'frames':11,'fps':24,'duration':11/24},'variants':{}}
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 refs={}
 for n,im in images.items():
  bg=Image.new('RGBA',(1672,972),col);bg.alpha_composite(im);ImageDraw.Draw(bg).text((12,946),f'F{n:03d} actual RAW review / HOLD060;062 full prop pending /058x2 060x2 062x1 063x6 /24fps',font=font,fill='#36536b'if tone=='gray'else'#d4e1eb');refs[n]=np.array(bg.convert('RGB'))
 for i,n in enumerate(order):Image.fromarray(refs[n]).save(R/f'frames_tmp/{tone}_{i:02d}.png')
 video=R/f'exposure/S09_058x2_060x2_062x1_063x6_{tone}_ACTUAL11f_REVIEW_ONLY_HOLD060.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(R/f'frames_tmp/{tone}_%02d.png'),'-frames:v','11','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(R/f'qa/ffprobe_{tone}.json').write_text(json.dumps(probe,indent=2)+'\n')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vsync','0',str(R/f'decoded_tmp/{tone}_%02d.png')],check=True)
 files=sorted((R/'decoded_tmp').glob(f'{tone}_*.png'));assert len(files)==11;classes=[]
 for i,f in enumerate(files):
  im=np.array(Image.open(f).convert('RGB')).astype(float);errors=[float(np.abs(im-refs[n].astype(float)).mean())for n in states];got=states[int(np.argmin(errors))];assert got==order[i];classes.append({'decoded_index':i,'expected_state':order[i],'actual_state':got,'matching_MAE':min(errors)})
 stream=next(s for s in probe['streams']if s['codec_type']=='video');assert stream['avg_frame_rate']=='24/1'and int(stream['nb_read_frames'])==11 and not any(s['codec_type']=='audio'for s in probe['streams'])
 check['variants'][tone]={'video_SHA256':sha(video),'decoded_frames':11,'fps':stream['avg_frame_rate'],'duration':float(stream['duration']),'audio_streams':0,'all11_decoded_states_correct':True,'all11_classification':classes}
 sheet=Image.new('RGB',(1920,1230),(232,238,244));dr=ImageDraw.Draw(sheet)
 for j,i in enumerate([1,2,3,4,5,10]):
  im=Image.open(files[i]).convert('RGB');x=j%3*640;y=j//3*615;dr.text((x+8,y+5),f'ACTUAL decode{i}/F{order[i]:03d}',font=font,fill='#36536b');sheet.paste(im.crop((550,0,1320,924)).resize((462,554)),(x+80,y+32))
 sheet.save(R/f'qa/ACTUAL11f_decoded_turn_transition_{tone}.png')
 close=Image.new('RGB',(1920,720),(232,238,244));dr=ImageDraw.Draw(close)
 for j,i in enumerate([2,4,5]):
  im=Image.open(files[i]).convert('RGB');x=j*640;dr.text((x+8,6),f'ACTUAL F{order[i]:03d} sleeves/whole arms/receiver air',font=font,fill='#36536b');close.paste(im.crop((575,440,1295,825)).resize((640,342)),(x,36));close.paste(im.crop((845,500,1285,820)).resize((440,320)),(x+95,392))
 close.save(R/f'qa/ACTUAL11f_complete_arms_grip_receiver_clearance_{tone}.png')
(R/'qa/actual_all11_decode_checks.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
for d in ['frames_tmp','decoded_tmp']:shutil.rmtree(R/d)
print(json.dumps({k:{q:v[q]for q in ['video_SHA256','decoded_frames','fps','duration','all11_decoded_states_correct']}for k,v in check['variants'].items()},indent=2))
