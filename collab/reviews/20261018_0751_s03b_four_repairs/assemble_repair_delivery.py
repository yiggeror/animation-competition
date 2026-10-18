from pathlib import Path
import json,hashlib,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;D=R/'repair_delivery'
for p in ['originals','prompts','author_records','qa/onion50']:(D/p).mkdir(parents=True,exist_ok=True)
inputs={
'd04':R/'repairs/d04/d04_f08_repair01_original.png',
'd09':R/'repairs/d09_d10/originals/d09_f19_repair_call01.png',
'd10':R/'repairs/d09_d10/originals/d10_f22_repair_call02.png',
'd12':R/'repairs/d12/originals/S03b_d12_f28_repair01.png'}
M=json.loads((R/'delivery/manifest.json').read_text());font=ImageFont.truetype(str(R/'refs/NotoSansSC-VF.ttf'),22)
canvas=(1672,942)
def over(im):
 bg=Image.new('RGBA',canvas,(126,126,126,255));bg.alpha_composite(im,(0,0));return bg.convert('RGB')
frames=[];rows=[];raw={}
for s in M['states']:
 id=s['id'];p=inputs.get(id,R/'delivery'/s['path']);b=p.read_bytes();im=Image.open(p).convert('RGBA');raw[id]=over(im)
 info={'id':id,'f':s['f'],'hold':s['hold'],'source_commit':None if id in inputs else '5010ac54b7c66acdd89cec84e92deae996d5cc01','path':('originals/'+p.name) if id in inputs else 'collab/reviews/20261018_0730_s03b_14_candidates/'+s['path'],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'size':im.size,'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'status':'REJECTED: diagnostic only; hand-fruit overshoots d13' if id=='d12' else 'CANDIDATE: see REVIEW.md; not scene-approved'};rows.append(info)
 if id in inputs:shutil.copyfile(p,D/'originals'/p.name)
 frame=raw[id].copy();dr=ImageDraw.Draw(frame);dr.rectangle((0,0,1100,40),fill='#ffbbbb' if id=='d12' else '#eeeeee');dr.text((10,4),f'仅诊断 {id} F{s["f"]:02d}–{s["f"]+s["hold"]-1:02d}'+('：d12仍失败，勿接入' if id=='d12' else '：未签原速/接景通过'),font=font,fill='#111111');frames.append(frame)
for id in inputs:
 i=int(id[1:]);a=f'd{i-1:02d}';b=f'd{i+1:02d}'
 for label,x,y in [('previous',a,id),('next',id,b)]:
  onion=Image.blend(raw[x],raw[y],.5);dr=ImageDraw.Draw(onion);dr.rectangle((0,0,900,38),fill='#eeeeee');dr.text((10,3),f'实图50% {x} + 50% {y}；左上原点，不缩放原件',font=font,fill='#111111');onion.save(D/'qa/onion50'/f'{id}_{label}.jpg',quality=90)
sheet=Image.new('RGB',(1672,1120),'#dddddd')
for i,im in enumerate(frames):sheet.paste(im.resize((418,236)),((i%4)*418,(i//4)*280))
sheet.save(D/'qa/14_state_repair_diagnostic.jpg',quality=93)
video=D/'qa/repair_diagnostic_48f_SILENT_d12_REJECTED.mp4'
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1672x942','-framerate','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
for s,im in zip(M['states'],frames):
 for _ in range(s['hold']):p.stdin.write(im.tobytes())
p.stdin.close();assert p.wait()==0
probe=subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]).decode();(D/'qa/preview_probe.json').write_text(probe)
(D/'all14_source_map.json').write_text(json.dumps({'diagnostic_only':True,'d12_repair_adopted':False,'original_initial_generation_calls':14,'additional_repair_calls':4,'total_generation_calls':18,'additional_automatic_calls_allowed':0,'scene_approved':False,'canvas_note':'QA only: top-left aligned 1672x942 canvas pads transparent edge rows/columns; no original pixel modifications/resizing','states':rows},ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(R/'repairs/d04/prompt.txt',D/'prompts/d04.txt')
for id,n in [('d09','01'),('d10','02')]:shutil.copyfile(R/f'repairs/d09_d10/logs/repair_call{n}_{id}_prompt.txt',D/f'prompts/{id}.txt')
call=json.loads((R/'repairs/d12/logs/call01_d12_repair.json').read_text());(D/'prompts/d12.txt').write_text(call['prompt']+'\n')
for name in ['d04','d09_d10','d12']:
 for src in [R/'repairs'/name,R/'repairs'/name/'logs']:
  if src.exists():
   for p in src.glob('*'):
    if p.is_file() and p.suffix in ['.json','.txt','.md'] and 'tool_result' not in p.name:shutil.copyfile(p,D/'author_records'/(name+'_'+p.name))
for src in ['d12/qa/intermediate_position_guide.png','d12/qa/boundary_contact.jpg','d04/qa/d03_d04_d05_active_contact.jpg']:
 p=R/'repairs'/src;shutil.copyfile(p,D/'qa'/p.name)
print(json.dumps({'originals':len(list((D/'originals').glob('*'))),'prompts':len(list((D/'prompts').glob('*'))),'probe':json.loads(probe)},ensure_ascii=False))
