#!/usr/bin/env python3
"""Compose already-registered review images; no registration, warp or interpolation."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json,shutil,subprocess
P=Path(__file__).resolve().parent
B=Path('/tmp/laidian-s18-pilot-audit/generated_k06_character')
source_manifest=json.loads((B/'source_manifest.json').read_text())
SRC=[('v2',B/'v2/evidence/v2_diagnostic_registered_to_master_635x1175_RGBA.png',B/'v2/registration_measurements.json'),('v1',B/'evidence/v1_diagnostic_registered_to_master_635x1175_RGBA.png',B/'registration_measurements.json'),('master',Path('/workspace/animation-competition/assets/chars/x18_laugh.png'),None)]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for sub in ['inputs','frames','repeat_frames','evidence']: (P/sub).mkdir(exist_ok=True)
shutil.copyfile(B/'source_manifest.json',P/'inputs/source_manifest.json')
I=[[1,0,0],[0,1,0],[0,0,1]]
def mm(A,B):return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
inputs=[];images={}
for ident,path,regpath in SRC:
 original=source_manifest['sources'][ident]
 assert sha(original['path'])==original['sha256']
 snap=P/'inputs'/f'{ident}_registered.png';shutil.copyfile(path,snap);assert sha(path)==sha(snap)
 im=Image.open(snap).convert('RGBA');assert im.size==(635,1175)
 if regpath:
  reg=json.loads(regpath.read_text());A=reg['candidate_native_to_master_matrix'];t=reg['translation'];M=[[A[0][0],A[0][1],t[0]],[A[1][0],A[1][1],t[1]],[0,0,1]]
  shutil.copyfile(regpath,P/'inputs'/f'{ident}_registration_measurements.json')
 else:M=I
 inputs.append({'id':ident,'role':'new generated image' if ident!='master' else 'existing k07 master','original':original,'registered_path':str(path),'registered_snapshot':str(snap.relative_to(P)),'registered_sha256':sha(snap),'registered_size':[635,1175],'original_to_registered_matrix':M,'registration_applied_by':'character_audit before this composition' if regpath else 'identity','clip_stage_registration_or_warp':False})
 images[ident]=im
fps=24;BG=(218,218,218,255);sequence=['v2']*3+['v1']*3+['master']*3
fmeta=[]
for i,ident in enumerate(sequence):
 im=Image.new('RGBA',(636,1176),BG);im.alpha_composite(images[ident],(0,0));out=P/'frames'/f'f{i:03d}.png';im.convert('RGB').save(out)
 q=next(x for x in inputs if x['id']==ident)
 fmeta.append({'frame_index':i,'time_s':i/fps,'duration_s':1/fps,'source_id':ident,'source_original_sha256':q['original']['sha256'],'source_registered_sha256':q['registered_sha256'],'registered_to_frame_matrix':I,'original_to_frame_matrix':q['original_to_registered_matrix'],'path':str(out.relative_to(P)),'sha256':sha(out)})
F='/workspace/animation-competition/assets/fonts/NotoSansSC-VF.ttf';title=ImageFont.truetype(F,32);sub=ImageFont.truetype(F,20);small=ImageFont.truetype(F,18)
T=[[1,0,162],[0,1,96],[0,0,1]];rmeta=[]
for i in range(36):
 ident=sequence[i%9];loop=i//9+1;im=Image.new('RGBA',(960,1280),BG);im.alpha_composite(images[ident],(162,96));d=ImageDraw.Draw(im)
 d.text((28,12),'近口三态诊断，非完整S18',font=title,fill='#202020')
 d.text((28,51),'2 张新图 + 1 张既有母版｜24fps｜每态 3 帧｜原速重复 4 次',font=sub,fill='#333333')
 tag={'v2':'v2：新图（较低近口态）','v1':'v1：新图（较高近口态）','master':'k07：既有母版（捂嘴终态）'}[ident]
 d.text((28,77),f'第 {loop}/4 轮  {tag}',font=small,fill='#333333')
 out=P/'repeat_frames'/f'f{i:03d}.png';im.convert('RGB').save(out);q=next(x for x in inputs if x['id']==ident)
 rmeta.append({'frame_index':i,'time_s':i/fps,'duration_s':1/fps,'cycle':loop,'source_frame_index':i%9,'source_id':ident,'source_original_sha256':q['original']['sha256'],'source_registered_sha256':q['registered_sha256'],'registered_to_frame_matrix':T,'original_to_frame_matrix':mm(T,q['original_to_registered_matrix']),'path':str(out.relative_to(P)),'sha256':sha(out)})
# One frame per state, native scale. These are visual review evidence, not extra keys.
strip=Image.new('RGB',(636*3,1176),(218,218,218))
for i,f in enumerate([0,3,6]):strip.paste(Image.open(P/'frames'/f'f{f:03d}.png'),(i*636,0))
strip.save(P/'evidence/three_states_native.png')
commands=[];outputs=[]
for name,framepath,count in [('near_mouth_9f_24fps',P/'frames',9),('near_mouth_repeat4_titled',P/'repeat_frames',36)]:
 out=P/(name+'.mp4');cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-framerate','24','-start_number','0','-i',str(framepath/'f%03d.png'),'-frames:v',str(count),'-an','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
 subprocess.run(cmd,check=True);commands.append(cmd)
 probe=['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames,duration:format=duration','-of','json',str(out)]
 info=json.loads(subprocess.check_output(probe));s=info['streams'][0];assert s['nb_read_frames']==str(count);assert s['r_frame_rate']=='24/1';assert abs(float(s['duration'])-count/24)<1e-6
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
 outputs.append({'path':out.name,'sha256':sha(out),'probe':info,'frame_count':count,'duration_s':count/24,'audio':False})
 # Decoded evidence confirms actual encoded output; no timing interpolation.
 for f in ([0,3,6] if count==9 else []):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out),'-vf',f'select=eq(n\\,{f})','-vsync','0','-frames:v','1',str(P/'evidence'/f'decoded_f{f:03d}.png')],check=True)
manifest={'title':'近口三态诊断，非完整S18','status':'diagnostic only; not adopted production assets','actual_input_count':{'new_generated_images':2,'existing_master_images':1},'sequence':'v2 → v1 → existing master k07; 3 unchanged holds each','fps':24,'frame_count':9,'duration_s':.375,'background_rgba':list(BG),'raw_composition_size':[636,1176],'raw_padding':'one gray pixel right and bottom for even H.264 dimensions; source 635x1175 is not resized','repeat_composition_size':[960,1280],'repeat_placement':[162,96],'repeat_count':4,'repeat_duration_s':1.5,'image_operations':['use supplied registered RGBA as-is','alpha composite over uniform gray','integer translation only at clip stage','PNG RGB export and ordinary H.264 YUV420 encoding'],'prohibited_operations_not_used':['new registration','local edits','warp','scale','crop','interpolation','crossfade','motion smoothing'],'limitations':['Only near-mouth three-state diagnosis, not full 3-second S18 laugh-to-cover action.','Generated v1/v2 do not accurately obey requested low elbow; neckline and sleeve-dot drift remain visible.','Previously registered candidate source images already use global similarity/resampling from character_audit; this stage does not apply another fit.','Existing alpha is respected, with no new background keying or repair; source gray RGB under transparent pixels is not painted as an opaque rectangle.','No audio added.'], 'inputs':inputs,'frames':fmeta,'repeat_frames':rmeta,'outputs':outputs,'ffmpeg_commands':commands,'composition_script_sha256':sha(__file__)}
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'outputs':outputs,'inputs':[{'id':q['id'],'sha256':q['registered_sha256']} for q in inputs]},ensure_ascii=False,indent=2))
