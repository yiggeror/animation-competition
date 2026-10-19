from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parent;REPO=R.parents[3]
indices=[0,15,16,24,25,37,38,39,53,56,57,61,62,67,68,72,73,78,79,83,84,89,90,94,95,99,100,102,103,105,106,107]
video=REPO/'build/S07_full108.mp4';copy=R/'S07_full108_abc2059_1920x1080_24fps_ACTUAL.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert video.is_file();shutil.copyfile(video,copy)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(R/'ffprobe_actual108.json').write_text(json.dumps(probe,indent=2)+'\n')
stream=next(s for s in probe['streams']if s['codec_type']=='video')
assert [stream['width'],stream['height']]==[1920,1080]
assert stream['avg_frame_rate']=='24/1' and int(stream['nb_read_frames'])==108
assert abs(float(stream['duration'])-4.5)<.00001
out=R/'decoded_actual_mp4';out.mkdir(exist_ok=True)
select='+'.join(f'eq(n\\,{i})'for i in indices)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+select,'-vsync','0',str(out/'selected_%02d.png')],check=True)
selected=sorted(out.glob('selected_*.png'));assert len(selected)==32
for p,i in zip(selected,indices):p.replace(out/f'F{i:03d}.png')
for i in indices:assert Image.open(out/f'F{i:03d}.png').size==(1920,1080)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
qa=R/'boundary_sheets';qa.mkdir(exist_ok=True)
for part in range(4):
 board=Image.new('RGB',(1920,620),(227,234,240));draw=ImageDraw.Draw(board)
 for j,i in enumerate(indices[part*8:part*8+8]):
  x=(j%4)*480;y=(j//4)*310;im=Image.open(out/f'F{i:03d}.png').convert('RGB');board.paste(im.resize((480,270)),(x,y+32));draw.text((x+8,y+7),f'ACTUAL MP4 decode F{i:03d}',font=font,fill='#36536b')
 board.save(qa/f'actual_decoded_boundaries_{part+1:02d}.png')
for a,b,name,boxes in [
 (56,57,'056_to057_cut_and_ground',[(0,0,1920,1080),(900,710,1310,1000)]),
 (99,100,'099_to100_single_lamp',[(0,0,1920,1080),(1390,535,1660,795)]),
 (103,106,'103_to106_same_grip_lamp_lift',[(0,0,1920,1080),(1390,535,1660,795)])]:
 board=Image.new('RGB',(1920,1160),(227,234,240));draw=ImageDraw.Draw(board)
 for j,i in enumerate([a,b]):
  im=Image.open(out/f'F{i:03d}.png').convert('RGB');x=j*960;draw.text((x+12,8),f'ACTUAL MP4 F{i:03d}: {name}',font=font,fill='#36536b');board.paste(im.resize((960,540)),(x,38));crop=im.crop(boxes[1]);crop.thumbnail((900,540));board.paste(crop,(x+30,610))
 board.save(qa/f'ACTUAL_{name}.png')
before=json.loads((R/'source_before_render.json').read_text())
unchanged={p:sha(REPO/p)==v for p,v in before['source_file_SHA256'].items()}
assert all(unchanged.values())
summary=json.loads((R/'browser_resource_summary.json').read_text())
assert not summary['request_failures'] and not summary['page_errors']
manifest={'fixed_source_commit':'abc2059eb84adb74e39958a7105441257fc52115','video_path':copy.name,'video_SHA256':sha(copy),'build_video_SHA256':sha(video),'video_bytes':copy.stat().st_size,'frames':108,'fps':24,'duration_seconds':4.5,'size':[1920,1080],'audio_streams':sum(s['codec_type']=='audio'for s in probe['streams']),'decoded_actual_MP4_frame_indices':indices,'decoded_actual_MP4_frame_SHA256':{f'F{i:03d}':sha(out/f'F{i:03d}.png')for i in indices},'all108_source_rendered_PNGs_present':all((REPO/f'build/S07_full108/{i:05d}.png').is_file()for i in range(108)),'production_files_unchanged':unchanged,'browser_scene_request_failures':summary['request_failures'],'browser_page_errors':summary['page_errors'],'browser_console_errors':summary['console_errors'],'visual_review':'PENDING_ACTUAL_IMAGES','scope':'Only fixed S07 full108 actual render and decoded evidence; no imagegen, production edits,EDL/audio/ready changes'}
(R/'actual_render_and_decode_checks.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k]for k in ['video_path','video_SHA256','video_bytes','frames','fps','duration_seconds','size','audio_streams','production_files_unchanged']},indent=2))
