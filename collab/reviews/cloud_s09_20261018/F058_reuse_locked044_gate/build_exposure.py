#!/usr/bin/env python3
"""Decode actual056->0587f and preceding locked48..6215f, no new art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,tempfile,csv
R=Path(__file__).resolve().parent;E=R/'exposure';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for q in json.loads((R/'sources/SOURCE_INDEX.json').read_text())['files']:assert sha(R/q['local_path'])==q['sha256']
files={48:R/'sources/F048_locked.png',52:R/'sources/F052_LOCKED_a107.png',56:R/'sources/F056_exact_locked042.png',58:R/'candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png'}
assert sha(files[58])==sha(R/'sources/F044_locked_source_for058.png')=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9'
reg={'scale':.6297229219143576,'translation_xy':[241.2216624685139,83.47607052896726]};s=reg['scale'];tx,ty=reg['translation_xy'];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
images={k:Image.open(p).convert('RGBA')for k,p in files.items()};assert all(v.size==(1672,941)for v in images.values())
palm=np.array(Image.open(R/'sources/fixed_receiver_palm_material.png').convert('L'))>0;mother=np.array(images[48]);gaps={}
for f,z in images.items():
 v=np.array(z);values=[]
 for x in range(1093,1174):
  py=np.where((mother[695:790,x,3]>=128)&palm[695:790,x])[0]+695
  if len(py):
   p=int(py.min());tail=np.where(v[550:p,x,3]>=128)[0]+550
   if len(tail):values.append(p-int(tail.max())-1)
 gaps[f]=int(min(values));assert gaps[f]=={48:91,52:37,56:0,58:48}[f]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
sources={f:{'path':str(p.relative_to(R)),'sha256':sha(p),'true_original_event':{56:42,58:44}.get(f,f)}for f,p in files.items()}
report={'status':'ACTUAL_HELD_SOURCE_EXPOSURE_DECODE_PASS_VISUAL_PENDING','sources':sources,'F058_source_byte_changes':0,'new_native_requests':0,'new_originals':0,'registration':reg,'constant_preview_crop_xyxy':[280,80,1304,656],'actual_gap_native_rows':gaps,'actual_gap_registered_px':{f:n*s for f,n in gaps.items()},'actual_F058_clearance_accepted_instead_of_nominal35':True,'clips':{},'limits':'Isolated original held PNGs,24fps,noaudio,not full scene/film. New15f encoded from unchanged locked sources; previous approved10f bitstream is not claimed copied.'}
for bg,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 refs={}
 for f,im in images.items():
  world=im.transform((1536,864),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));world.save(E/f'F{f:03d}_registered.png')
  b=Image.new('RGBA',world.size,col);b.alpha_composite(world);v=b.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');v.save(E/f'F{f:03d}_{bg}.png');refs[f]=np.array(v)
 for label,start,seq,inspect in [('F056x2_F058x5',56,[56]*2+[58]*5,[0,1,2,6]),('F048x4_F052x4_F056x2_F058x5',48,[48]*4+[52]*4+[56]*2+[58]*5,[4,7,8,9,10,14])]:
  O=E/f'{label}_{bg}';O.mkdir(exist_ok=True);video=O/f'S09_{label}_{bg}_24fps.mp4'
  with tempfile.TemporaryDirectory(prefix='s09-058-')as tmp:
   T=Path(tmp)
   for i,f in enumerate(seq):Image.fromarray(refs[f]).save(T/f'{i:02d}.png')
   subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(T/'%02d.png'),'-frames:v',str(len(seq)),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);decoded=np.frombuffer(raw,np.uint8).reshape((-1,720,1280,3));assert len(decoded)==len(seq)
  scores=[]
  for i,v in enumerate(decoded):
   errors={f:float(np.abs(v.astype(float)-z.astype(float)).mean())for f,z in refs.items()};best=min(errors,key=errors.get);assert best==seq[i];scores.append({'clip_frame':i,'scene_frame':start+i,'event':seq[i],'true_source_event':sources[seq[i]]['true_original_event'],'decoded_nearest':best,'expected_RGB_MAE':errors[seq[i]]})
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]));st=probe['streams'];assert len(st)==1 and(st[0]['width'],st[0]['height'],st[0]['r_frame_rate'],st[0]['nb_frames'])==(1280,720,'24/1',str(len(seq)))
  cols=2 if len(inspect)==4 else 3;sheet=Image.new('RGB',(cols*640,770),(236,242,247));d=ImageDraw.Draw(sheet)
  for j,i in enumerate(inspect):
   z=Image.fromarray(decoded[i]);z.save(O/f'actual_decoded_{i:02d}.png');x=(j%cols)*640;y=(j//cols)*385;sheet.paste(z.resize((640,360)),(x,y+25));d.text((x+3,y+2),f'实解码clip{i}／F{start+i:03d}／事件{seq[i]:03d}',font=font,fill='#263440')
  sheet.save(O/'actual_decoded_contact_sheet.png')
  for i in ([1,2]if start==56 else[9,10]):Image.fromarray(decoded[i]).crop((550,260,1140,680)).resize((1180,840),Image.Resampling.NEAREST).save(O/f'actual_decoded_{i:02d}_hands_cuffs_2x.png')
  clip={'path':str(video.relative_to(R)),'sha256':sha(video),'sequence':seq,'scene_frames_inclusive':[start,start+len(seq)-1],'probe':probe,'decoded_frames':scores,'max_expected_RGB_MAE':max(q['expected_RGB_MAE']for q in scores),'no_tween_no_new_drawing':True}
  (O/'actual_decode_checks.json').write_text(json.dumps(clip,ensure_ascii=False,indent=2)+'\n');report['clips'][label+'_'+bg]=clip
with (R/'source_exposure_mapping_048_062.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(['scene_frame','state_event','original_source_event','source_sha256','switch','light_on'])
 for i,e in enumerate([48]*4+[52]*4+[56]*2+[58]*5):w.writerow([48+i,e,sources[e]['true_original_event'],sources[e]['sha256'],'OFF',False])
(R/'qa/actual_decode_and_gap_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actual_gaps':gaps,'clips':{k:{'frames':len(v['sequence']),'sha256':v['sha256'],'max_RGB_MAE':v['max_expected_RGB_MAE']}for k,v in report['clips'].items()}},ensure_ascii=False,indent=2))
