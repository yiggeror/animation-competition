"""Independently decode and archive the completed authorized S07 continuation. Never renders."""
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
from PIL import Image,ImageDraw,ImageFont
META=Path(__file__).resolve().parent;BASE=META.parent;ROOT=BASE.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=json.loads((META/'RUN_STATE.json').read_text())
assert state['state']=='COMPLETED' and state['exit_code']==0
assert state['completed_frames']==state['frames_sent_to_encoder']==108
assert state['prior_S01_S04_render_calls']==0 and state['context_attributes']['willReadFrequently'] is False
assert len(state['approvedSampleChecks'])==5 and all(x['pass'] for x in state['approvedSampleChecks'])
assert all(x['pass'] for x in state['sourceChecks']+state['sourceChecksAfter'])
assert not state['errors'] and all(x['status']<400 for x in state['http'])
src=Path(state['output_dir'])/'S07';dest=BASE/'S07'
assert not dest.exists(),'Never overwrite another S07 delivery'
check=json.loads((src/'CLIP_CHECK.json').read_text());ledger=json.loads((src/'FRAME_LEDGER.json').read_text())
assert [r['frame'] for r in ledger]==list(range(108))
movie=src/'S07_opening_corrected_1080p24.mp4';assert sha(movie)==check['sha256']
# Verify the original completed scenes are unchanged; these commands do not render them.
retained={}
for s in ['S01','S04']:
 c=json.loads((BASE/s/'CLIP_CHECK.json').read_text());p=BASE/s/Path(c['file']).name
 assert sha(p)==c['sha256'];retained[s]={'video_sha256':sha(p),'unchanged':True}
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)],text=True))
assert len(probe['streams'])==1
v=probe['streams'][0]
assert v['codec_type']=='video' and int(v['nb_read_frames'])==108 and (v['width'],v['height'])==(1920,1080) and v['avg_frame_rate']=='24/1'
assert abs(float(probe['format']['duration'])-4.5)<.001
decode=Path('/tmp/opening-s07-fresh-independent-decode-20261019');decode.mkdir(exist_ok=False)
fullhash=decode/'FULL_DECODED_RGB24_FRAME_SHA256.txt'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',str(movie),'-map','0:v:0','-an','-c:v','rawvideo','-pix_fmt','rgb24','-f','framehash','-hash','sha256',str(fullhash)]
dec=subprocess.run(cmd,text=True,capture_output=True)
assert dec.returncode==0,dec.stderr
rows=[r for r in fullhash.read_text().splitlines() if r and not r.startswith('#')]
assert len(rows)==108
parsed=[[x.strip() for x in row.split(',')] for row in rows]
assert [int(r[2]) for r in parsed]==list(range(108)) and all(int(r[4])==1920*1080*3 for r in parsed)
# Independent retained-frame decode is for actual visual inspection, not lossless PNG comparison.
frames=check['keyframes'];expr='+'.join('eq(n\\,%d)'%f for f in frames)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',str(movie),'-vf','select='+expr,'-vsync','0',str(decode/'decoded_%03d.png')],check=True,capture_output=True)
pngs=sorted(decode.glob('decoded_*.png'));assert len(pngs)==len(frames)
decoded=dict(zip(frames,pngs))
for p in pngs:
 with Image.open(p) as im:assert im.size==(1920,1080)
focus=[0,3,6,8,38,39,43,53,56,57,99,100,103,106,107]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def sheet(choices,box,cols,name):
 w,h=(box[2]-box[0],box[3]-box[1]) if box else (480,270)
 if box:
  factor=min(1.6,480/w);w,h=round(w*factor),round(h*factor)
 panel=Image.new('RGB',(w*cols,((len(choices)+cols-1)//cols)*(h+28)),'#edf0f2');draw=ImageDraw.Draw(panel)
 for i,f in enumerate(choices):
  x=(i%cols)*w;y=(i//cols)*(h+28)
  with Image.open(decoded[f]) as im:
   im=im.convert('RGB');im=im.crop(box) if box else im;panel.paste(im.resize((w,h)),(x,y+28))
  draw.text((x+8,y+4),f'S07 decoded F{f:03d}',font=font,fill='#23364d')
 panel.save(decode/name,quality=93)
sheet(focus,None,4,'INDEPENDENT_DECODED_FOCUS_REVIEW.jpg')
sheet([0,3,6,8],(610,620,900,865),2,'INDEPENDENT_PHONE_CABLE_CONTACTS.jpg')
sheet([99,100,103,106,107],(1390,555,1695,820),3,'INDEPENDENT_TAIL_LAMP_BOX_CONTACTS.jpg')
# Archive only after independent full decode and all strict producer gates passed.
shutil.copytree(src,dest)
for frame in frames:
 assert sha(dest/f'S07_F{frame:03d}.png')==ledger[frame]['sha256']
for name in ['FULL_DECODED_RGB24_FRAME_SHA256.txt','INDEPENDENT_DECODED_FOCUS_REVIEW.jpg','INDEPENDENT_PHONE_CABLE_CONTACTS.jpg','INDEPENDENT_TAIL_LAMP_BOX_CONTACTS.jpg']:
 shutil.copyfile(decode/name,dest/name)
(dest/'FFPROBE_INDEPENDENT.json').write_text(json.dumps(probe,indent=2)+'\n')
verification={'shot':'S07','video_sha256':sha(dest/movie.name),'frames':108,'duration_seconds':4.5,'width':1920,'height':1080,'fps':'24/1','audio_streams':0,'independent_full_decode_exit_code':dec.returncode,'independent_full_decoded_RGB24_frame_count':len(rows),'independent_full_decoded_RGB24_frame_bytes':1920*1080*3,'full_decode_command':cmd,'full_decode_stderr':dec.stderr,'native_key_PNGs_match_actual_frame_ledger':True,'all_108_native_PNG_SHA_rows_present':True,'approved_five_sample_checks':check['approvedSampleChecks'],'independent_decoded_key_frames':frames,'decoded_focus_frames':focus,'source_frozen_checks_before_after_pass':True,'fresh_canvas_default_attributes':state['context_attributes'],'prior_S01_S04_render_calls':0,'S01_S04_retained':retained,'new_imagegen_calls':0,'visual_full_clip_review':'PENDING_MAIN_CONTINUOUS_REVIEW','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(dest/'DELIVERY_VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n')
(dest/'MANIFEST_SHA256.json').write_text(json.dumps({p.name:sha(p) for p in sorted(dest.iterdir()) if p.is_file() and p.name!='MANIFEST_SHA256.json'},indent=2)+'\n')
shutil.copyfile(Path(state['output_dir'])/'S07_FRESH_CHECK.json',META/'S07_FRESH_CHECK.json')
print(json.dumps({'archived':str(dest),'mp4_sha256':verification['video_sha256'],'decoded_frames':len(rows),'strict_sample_passes':len(state['approvedSampleChecks'])}))
