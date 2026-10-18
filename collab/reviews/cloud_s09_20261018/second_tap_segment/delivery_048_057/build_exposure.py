#!/usr/bin/env python3
"""Actual PNG second-tap10f plus two-contact16f, fixed registration, no tween."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,tempfile,subprocess
import numpy as np
R=Path(__file__).resolve().parent;S=R.parent;B=S.parent;T=B/'first_tap_segment';E=R/'exposure';E.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths={42:T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png',44:T/'F044_rebound_gate/candidate/F044_complete_local_native_arm_PENDING_ASTRA.png',48:T/'F048_recovery_reuse_gate/candidate/F048_recovery_TRUE_LOCKED_F037_REUSE_PENDING_ASTRA.png',52:S/'F052_approach_gate/candidate/F052_complete_native_final_PENDING_ASTRA.png',56:S/'F056_contact_reuse_gate/candidate/F056_second_contact_LOCKED_F042_REUSE_PENDING_ASTRA.png'}
assert sha(paths[42])==sha(paths[56])=='52bb96f9796878bbb9c928ad80c5af6b5a0580ad9f9c651384446f0caadd3f8f'
assert sha(paths[48])=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9'
reg=json.loads((T/'F044_rebound_gate/preparation.json').read_text())['registration_unchanged'];s=reg['scale'];tx,ty=reg['translation_xy'];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
refs={};sources={};equivalence={}
for f,p in paths.items():
 im=Image.open(p).convert('RGBA');assert im.size==(1672,941)
 world=im.transform((1536,864),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));world.save(E/f'F{f:03d}_registered.png')
 for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
  q=Image.new('RGBA',world.size,col);q.alpha_composite(world);q=q.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');q.save(E/f'F{f:03d}_{name}.png')
  if name=='gray':refs[f]=np.array(q)
 sources[f]={'path':str(p),'sha256':sha(p),'native_canvas':[1672,941]}
for f in paths:equivalence[f]=[g for g in paths if sources[f]['sha256']==sources[g]['sha256']]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
reports={}
for name,start,seq,inspect in [('second_tap_10f',48,[48]*4+[52]*4+[56]*2,[0,3,4,7,8,9]),('two_contacts_16f',42,[42]*2+[44]*4+[48]*4+[52]*4+[56]*2,[0,1,2,6,10,13,14,15])]:
 droot=E/name;droot.mkdir(exist_ok=True);video=droot/f'S09_{name}_actual_layer_24fps_PENDING.mp4'
 with tempfile.TemporaryDirectory(prefix='s09-'+name+'-')as tmp:
  d=Path(tmp)
  for i,f in enumerate(seq):Image.fromarray(refs[f]).save(d/f'{i:04d}.png')
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(d/'%04d.png'),'-frames:v',str(len(seq)),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);decoded=np.frombuffer(raw,np.uint8).reshape((-1,720,1280,3));assert len(decoded)==len(seq)
 rows=[]
 for i,a in enumerate(decoded):
  maes={f:float(abs(a.astype(float)-ref.astype(float)).mean())for f,ref in refs.items()};best=min(maes,key=maes.get);assert seq[i]in equivalence[best]
  rows.append({'clip_frame':i,'scene_frame':start+i,'expected_source_event':seq[i],'decoded_equivalent_source_ids':equivalence[best],'RGB_MAE':maes[best]})
 cols=3 if len(inspect)==6 else 4;sheet=Image.new('RGB',(cols*640,770),(238,242,246));dr=ImageDraw.Draw(sheet)
 for j,i in enumerate(inspect):
  q=Image.fromarray(decoded[i]);q.save(droot/f'actual_decoded_{i:02d}.png');x=(j%cols)*640;y=(j//cols)*385;sheet.paste(q.resize((640,360)),(x,y+25));dr.text((x+5,y+2),f'实解码clip{i}／F{start+i:03d}／源事件{seq[i]:03d}',font=font,fill='#26343e')
 sheet.save(droot/'actual_decoded_contact_sheet.png')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))
 report={'status':'ACTUAL_HELD_PNG_DECODE_SOURCE_ORDER_PASS_VISUAL_REVIEW_PENDING','sources':sources,'sequence':seq,'source_equivalence_classes':equivalence,'scene_frames_inclusive':[start,start+len(seq)-1],'fps':24,'no_audio':True,'no_tween':True,'isolated_PNG_not_full_scene_or_film':True,'registration':reg,'constant_preview_crop_xyxy':[280,80,1304,656],'video_sha256':sha(video),'probe':probe,'decoded_frames':rows,'max_RGB_MAE':max(v['RGB_MAE']for v in rows),'contact_event_scene_frames':[56]if name=='second_tap_10f'else[42,56],'numeric_source_gap_native_rows_by_event':{42:0,44:48,48:91,52:37,56:0},'same_bitmap_different_events_explained':'056 is byte-identical authentic locked042 reused after actual048→052 positive gaps. Pixel classification cannot distinguish42 from56; source-equivalence and temporal exposure indices are explicitly retained. Actual visual review of the intervening separation is required.'}
 (droot/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');reports[name]={'sha256':sha(video),'frames':len(seq),'max_RGB_MAE':report['max_RGB_MAE']}
(E/'summary.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');print(json.dumps(reports,ensure_ascii=False,indent=2))
