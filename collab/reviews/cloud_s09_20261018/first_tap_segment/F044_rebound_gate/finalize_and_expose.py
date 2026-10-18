#!/usr/bin/env python3
"""Finalize actual044 and expose recovery using genuine locked037 source pose."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.cluster.vq import kmeans2
import numpy as np,json,hashlib,shutil,tempfile,subprocess
R=Path(__file__).resolve().parent;T=R.parent;E=R/'exposure';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p42=T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png'
p37=T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png'
p44=R/'candidate/F044_complete_local_native_arm_PENDING_ASTRA.png'
shutil.copyfile(R/'candidate/F044_complete_local_native_arm_TRIAL.png',p44)
D=T/'F048_recovery_reuse_gate';(D/'candidate').mkdir(parents=True,exist_ok=True);(D/'qa').mkdir(exist_ok=True)
p48=D/'candidate/F048_recovery_TRUE_LOCKED_F037_REUSE_PENDING_ASTRA.png';shutil.copyfile(p37,p48)
assert sha(p48)==sha(p37)=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9'
reg=json.loads((R/'preparation.json').read_text())['registration_unchanged'];s=reg['scale'];tx,ty=reg['translation_xy'];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
paths={42:p42,44:p44,48:p48};refs={};sources={}
for f,p in paths.items():
 im=Image.open(p).convert('RGBA');z=im.transform((1536,864),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));z.save(E/f'F{f:03d}_registered.png')
 for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
  b=Image.new('RGBA',z.size,col);b.alpha_composite(z);preview=b.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');preview.save(E/f'F{f:03d}_{name}.png')
  if name=='gray':refs[f]=np.array(preview)
 sources[f]={'path':str(p),'sha256':sha(p),'native_canvas':[1672,941]}
seq=[42]*2+[44]*4+[48]*4;video=E/'S09_F042x2_F044x4_F048x4_actual_layer_24fps_PENDING.mp4'
with tempfile.TemporaryDirectory(prefix='s09-042-044-048-') as tmp:
 d=Path(tmp)
 for i,f in enumerate(seq):Image.fromarray(refs[f]).save(d/f'{i:04d}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(d/'%04d.png'),'-frames:v',str(len(seq)),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);decoded=np.frombuffer(raw,dtype=np.uint8).reshape((-1,720,1280,3));assert len(decoded)==len(seq)
rows=[]
for i,a in enumerate(decoded):
 errors={f:float(np.abs(a.astype(float)-r.astype(float)).mean())for f,r in refs.items()};best=min(errors,key=errors.get);assert best==seq[i];rows.append({'clip_frame':i,'expected':seq[i],'actual_closest_source':best,'RGB_MAE':errors[best]})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18);sheet=Image.new('RGB',(1920,770),(238,242,246));d=ImageDraw.Draw(sheet)
for k,i in enumerate([0,1,2,5,6,9]):
 z=Image.fromarray(decoded[i]);z.save(E/f'actual_decoded_{i:02d}.png');x=(k%3)*640;y=(k//3)*385;sheet.paste(z.resize((640,360)),(x,y+25));d.text((x+6,y+2),f'实际解码clip{i} / F{seq[i]:03d}',font=font,fill='#26343e')
sheet.save(E/'actual_decoded_0_1_2_5_6_9.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))
report={'status':'10FRAME_ACTUAL_PNG_EXPOSURE_DECODED_PENDING_VISUAL_REVIEW','sources':sources,'sequence':seq,'fps':24,'no_tween':True,'no_audio':True,'isolated_PNG_not_full_scene_or_film':True,'registration':reg,'video_sha256':sha(video),'probe':probe,'all_decoded_frames':rows,'max_MAE':max(r['RGB_MAE']for r in rows),'F048_authentic_source_reuse_not_new_generation':True}
(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Native skin colors only; separate shadow/flat/highlight centroids, no correction.
color={}
for f,mask in [(42,R/'masks/old_near_arm_actual_material.png'),(44,R/'connection_call02/masks/native_actual_near_arm_material.png')]:
 a=np.array(Image.open(paths[f]).convert('RGBA'));rgb=a[:,:,:3].astype(int);m=np.array(Image.open(mask))>0;m&=(rgb[:,:,0]>205)&(rgb[:,:,1]>120)&(rgb[:,:,2]>80)&(a[:,:,3]>=250);v=rgb[m];cs,lab=kmeans2(v.astype(float),3,minit='++',rng=6);cs=sorted([{'pixels':int((lab==i).sum()),'RGB_mean':cs[i].tolist()}for i in range(3)],key=lambda x:x['RGB_mean'][1]);color[f]={'pixels':len(v),'mean':v.mean(axis=0).tolist(),'shadow_flat_highlight':cs}
diff=np.array([c['RGB_mean']for c in color[44]['shadow_flat_highlight']])-np.array([c['RGB_mean']for c in color[42]['shadow_flat_highlight']]);assert abs(diff).max()<4
color['centroid_delta044_minus042']=diff.tolist();color['separate_material_max_channel_mean_delta']=float(abs(diff).max());color['correction_applied']=False;color['limits']='Deterministic whole material clustering; same exact coordinates are different bent surfaces. Does not prove anatomical bone lengths or replace actual visual review.'
(R/'qa/semantic_skin_color_checks.json').write_text(json.dumps(color,ensure_ascii=False,indent=2)+'\n')
recover={'status':'TRUE_EXISTING_POSE_REUSE_PENDING_ASTRA_TOLERANCE_REVIEW','source_frame':37,'source_sha256':sha(p37),'candidate_sha256':sha(p48),'frame':48,'hold':4,'inclusive_frames':[48,51],'new_image_calls':0,'new_originals':0,'whole_image_RGBA_changes':0,'source_locked_geometry_registration_unchanged':True,'desired_gap_registered_approx':55,'actual_source_gap_native_rows':91,'actual_source_gap_registered_px':91*s,'difference_vs_nominal55_registered_px':91*s-55,'rationale':'Recovery returns to the same previously locked raised anticipation pose. Reuse the genuine whole artwork, with the same original hand/torch, fixed palm, head/gaze and character; no code-drawn limb or part warp. Report actual57.3048 rather than claim exact55. Astra must accept the +2.3048px tolerance or request new native048; not silently exact.'}
(D/'qa/reuse_and_gap_checks.json').write_text(json.dumps(recover,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'F044':sha(p44),'F048':sha(p48),'video':sha(video),'MAE':report['max_MAE'],'color_max_delta':color['separate_material_max_channel_mean_delta'],'recovery':recover},ensure_ascii=False,indent=2))
