#!/usr/bin/env python3
"""Only the24-frame third-push evidence; no full-prefix or scene rendering."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
for sub in ['exposure_stills','decoded_after','decoded_comparison','qa','provenance']:(HERE/sub).mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((HERE/'provenance/correction_checks.json').read_text())
rows=[]
for name,hold in [('F084',6),('F090',18)]:
 before=ROOT/checks[name]['source'];after=HERE/'candidate'/f'{name}_shadow_fixed.png'
 assert sha(before)==checks[name]['source_sha256'];assert sha(after)==checks[name]['candidate_sha256']
 def plate(path):
  a=Image.open(path).convert('RGBA');b=Image.new('RGBA',a.size,(115,115,115,255));b.alpha_composite(a);return b.convert('RGB')
 old,new=plate(before),plate(after)
 im=new.resize((1280,720));d=ImageDraw.Draw(im);d.rectangle((0,0,1030,36),fill=(25,25,25));d.text((10,3),f'S22 暗侧校准｜隔离非实景｜{name} ×{hold}｜仅084–107',font=font,fill='white')
 out=HERE/'exposure_stills'/f'{name}_after.png';im.save(out)
 compare=Image.new('RGB',(1280,560),(25,25,25));d=ImageDraw.Draw(compare)
 for i,(title,b) in enumerate([(name+' frozen BEFORE',old),(name+' shadow AFTER',new)]):
  compare.paste(b.crop((0,200,900,941)).resize((640,527)),(i*640,33));d.text((i*640+8,5),title,font=small,fill='white')
 cmp=HERE/'exposure_stills'/f'{name}_compare.png';compare.save(cmp)
 rows.append(dict(id=name,hold=hold,source_before=str(before.relative_to(ROOT)),before_sha256=sha(before),source_after=str(after.relative_to(ROOT)),after_sha256=sha(after),after_still=out.name,compare_still=cmp.name))

def encode(stem,kind,size,decoded_dir,selected):
 clip=HERE/(stem+'.mp4');command=['ffmpeg','-y','-v','error','-f','image2pipe','-framerate','24','-i','-','-frames:v','24','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',str(clip)]
 proc=subprocess.Popen(command,stdin=subprocess.PIPE);expected=[]
 for row in rows:
  data=(HERE/'exposure_stills'/row[kind+'_still']).read_bytes()
  for _ in range(row['hold']):proc.stdin.write(data);expected.append(row['id'])
 proc.stdin.close();assert proc.wait()==0
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True));assert len(probe['streams'])==1 and int(probe['streams'][0]['nb_read_frames'])==24 and probe['streams'][0]['r_frame_rate']=='24/1' and float(probe['format']['duration'])==1
 tw,th=size[0]//4,size[1]//4
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(clip),'-vf',f'scale={tw}:{th}','-f','rawvideo','-pix_fmt','rgb24','-'])
 frames=np.frombuffer(raw,np.uint8).reshape((24,th,tw,3)).astype(float)
 refs=np.stack([np.array(Image.open(HERE/'exposure_stills'/row[kind+'_still']).resize((tw,th))).astype(float) for row in rows]);errors=np.mean((frames[:,None]-refs[None])**2,axis=(2,3,4));actual=[rows[i]['id'] for i in errors.argmin(axis=1)];assert actual==expected
 for f in selected:
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/decoded_dir/f'F{84+f:03d}.png')],check=True)
 record=dict(clip=clip.name,sha256=sha(clip),fps=24,frames=24,duration_seconds=1,size=list(size),holds=[6,18],actual_decoded_identities=actual,holds_verified=True,global_frame_offset=84,rows=rows,command=command,ffprobe=probe,isolation_not_scene=True,new_image_calls=0)
 (HERE/'provenance'/(stem+'.json')).write_text(json.dumps(record,indent=2)+'\n')
 return {k:record[k] for k in ['clip','sha256','fps','frames','duration_seconds','size','holds_verified']}

clips=[encode('S22_084_107_shadow_fixed24','after',(1280,720),'decoded_after',[0,5,6,23]),encode('S22_084_107_before_after24','compare',(1280,560),'decoded_comparison',[5,6])]
board=Image.new('RGB',(940,1184),(25,25,25));d=ImageDraw.Draw(board)
for j,(title,folder) in enumerate([('Frozen5749423 actual decoded',ROOT/'third_push_084_090/decoded_actual'),('Shadow corrected actual decoded',HERE/'decoded_after')]):
 for i,f in enumerate([89,90]):
  im=Image.open(folder/f'F{f:03d}.png');assert im.size==(1280,720);x,y=i*470,j*592
  board.paste(im.crop((0,160,470,720)),(x,y+32));d.text((x+7,y+6),f'{title} F{f:03d}',font=small,fill='white')
board.save(HERE/'qa/decoded089_090_native_crop_before_after.png')
summary=dict(clips=clips,new_image_calls=0,cumulative_attempts=11,cumulative_successful_outputs=10,production_ready=False,no_F108=True,no_F114=True)
(HERE/'provenance/delivery_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
