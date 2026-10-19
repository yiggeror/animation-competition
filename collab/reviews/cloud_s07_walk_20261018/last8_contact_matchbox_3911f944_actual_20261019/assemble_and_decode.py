"""Reuse exact old lossless000..099 + eight newly rendered100..107; no scene rendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,subprocess,sys,numpy as np

R=Path(__file__).resolve().parent;W=R.parents[3]
OLD=Path('/workspace/s07-full108-render-20261019-abc2059/build/S07_full108')
NEW=W/'build/S07_last8_3911f944';MERGED=W/'build/S07_full108_reused100_new8_3911f944'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sorted(p.name for p in NEW.glob('*.png'))==[f'{i:05}.png' for i in range(100,108)]
for d in ['new_actual_png','decoded_actual_mp4','boundary_sheets']:(R/d).mkdir(exist_ok=True)
MERGED.mkdir(parents=True,exist_ok=True)
before=json.loads((R/'source_before_render_and_reuse100.json').read_text()); frames=[]
for i in range(108):
    src=(OLD if i<100 else NEW)/f'{i:05}.png';dst=MERGED/f'{i:05}.png'
    h=sha(src)
    if i<100:assert h==before['old_first100_exact_lossless_PNGs'][i]['sha256']
    shutil.copyfile(src,dst);assert sha(dst)==h
    im=Image.open(dst);assert im.size==(1920,1080)
    row={'frame':i,'source':'reused_f35f9ae2_lossless_PNG' if i<100 else 'new_render_fixed3911f944','sha256':h,'source_path':str(src)}
    if i>=100:
        saved=R/f'new_actual_png/F{i:03}.png';shutil.copyfile(src,saved);assert sha(saved)==h;row['delivered_png']=str(saved.relative_to(R))
    frames.append(row)
video=R/'S07_full108_REUSED100_NEW8_3911f944_1920x1080_24fps_ACTUAL.mp4'
cmd=['ffmpeg','-y','-v','error','-framerate','24','-start_number','0','-i',str(MERGED/'%05d.png'),'-frames:v','108','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation','-movflags','+faststart',str(video)]
if '--decode-existing' not in sys.argv:subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));streams=probe['streams'];assert len(streams)==1
st=streams[0];assert (st['width'],st['height'],st['avg_frame_rate'],int(st['nb_read_frames']))==(1920,1080,'24/1',108)
assert abs(float(st['duration'])-4.5)<1e-6
(R/'ffprobe_actual108.json').write_text(json.dumps(probe,indent=2)+'\n')
indices=[99,100,102,103,105,106,107]
select='+'.join(rf'eq(n\,{i})' for i in indices)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',f'select={select}','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'])
dec=np.frombuffer(raw,np.uint8).reshape((-1,1080,1920,3));assert len(dec)==len(indices)
decoded={};decode_checks=[]
for i,z in zip(indices,dec):
    p=R/f'decoded_actual_mp4/F{i:03}.png';Image.fromarray(z).save(p);decoded[i]=Image.fromarray(z)
    expected=np.array(Image.open(MERGED/f'{i:05}.png').convert('RGB'));mae=float(np.abs(z.astype(float)-expected.astype(float)).mean())
    assert mae<3
    decode_checks.append({'frame':i,'actual_decoded_png_sha256':sha(p),'decoded_vs_exact_source_RGB_MAE':mae})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
board=Image.new('RGB',(1920,1200),(226,235,242));dr=ImageDraw.Draw(board)
for j,i in enumerate(indices):
    x=(j%3)*640;y=(j//3)*400;board.paste(decoded[i].resize((640,360)),(x,y+30));dr.text((x+8,y+6),f'ACTUAL MP4 decode F{i:03}',font=font,fill='#263f53')
board.save(R/'boundary_sheets/ACTUAL_required7_full_scene.png')
def sheet(name,items,crop,scale=1):
    cw,ch=crop[2]-crop[0],crop[3]-crop[1];out=Image.new('RGB',(round(cw*scale)*len(items),round(ch*scale)+36),(226,235,242));d=ImageDraw.Draw(out)
    for j,(label,im) in enumerate(items):
        x=j*round(cw*scale);out.paste(im.crop(crop).resize((round(cw*scale),round(ch*scale))),(x,36));d.text((x+5,7),label,font=font,fill='#263f53')
    out.save(R/'boundary_sheets'/name)
sheet('ACTUAL_099_to100_person_foot_table.png',[(f'ACTUAL decoded F{i:03}',decoded[i]) for i in [99,100]],(1260,450,1660,1000),1.5)
sheet('ACTUAL_matchbox_single_lamp_099_100_103_106.png',[(f'ACTUAL F{i:03}',decoded[i]) for i in [99,100,103,106]],(1320,535,1600,800),1.5)
sheet('ACTUAL_103_to106_same_grip_lamp_lift.png',[(f'ACTUAL F{i:03}',decoded[i]) for i in [103,106]],(1320,500,1595,800),2)
# Old and new actual scene pixels: explicit comparison, no correction painted into frames.
old100=Image.open(OLD/'00100.png').convert('RGB')
sheet('OLD_actual100_vs_NEW_actual_decoded100_foot_shadow.png',[('OLD actual render100',old100),('NEW actual MP4 decoded100',decoded[100])],(1270,780,1510,970),2)
report={'status':'ACTUAL_LAST8_RENDER_AND_FULL108_REENCODE_PENDING_VISUAL_REVIEW','fixed_source_commit':before['fixed_source_commit'],'old_render_delivery_commit':before['old_render_delivery_commit'],'rendered_new_frames':list(range(100,108)),'rendered_new_frame_count':8,'reused_exact_lossless_first100_PNGs':True,'new_full108_scene_render':False,'all108_source_frame_SHA256':frames,'full108_mp4':str(video.relative_to(R)),'full108_mp4_sha256':sha(video),'size':[1920,1080],'fps':24,'frames':108,'duration_seconds':4.5,'audio_streams':0,'encode_command':cmd,'required_actual_decode_frames':indices,'actual_decode_checks':decode_checks,'production_changes':False,'new_imagegen_calls':0}
(R/'actual_render8_reuse100_encode108_checks.json').write_text(json.dumps(report,indent=2)+'\n')
with (R/'new8_PNG_SHA256SUMS.txt').open('w') as f:
    for row in frames[100:]:f.write(row['sha256']+'  '+row['delivered_png']+'\n')
print(json.dumps({'video':str(video),'SHA256':sha(video),'new_render_frames':8,'reused_old_PNGs':100,'actual_decoded_required':indices},indent=2))
