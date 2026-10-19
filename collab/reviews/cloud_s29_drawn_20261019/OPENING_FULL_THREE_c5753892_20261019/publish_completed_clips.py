"""Archive and publish each completed original clip; never renders or restarts."""
from pathlib import Path
import subprocess,json,time,hashlib,shutil,datetime,os
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;ROOT=R.parents[3];OUT=Path('/tmp/opening-continuity-full')
BRANCH='cloud/opening-full-three-20261019-c5753892';REL=str(R.relative_to(ROOT))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(args,**kw):return subprocess.run(args,cwd=ROOT,check=True,**kw)
def publish(message):
 run(['git','add','--sparse','--',REL],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 run(['git','commit','-m',message],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 run(['git','push','origin',BRANCH],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'})
 return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
done={};status={'started_utc':now(),'state':'WATCHING_EXISTING_RENDER','render_restart_calls':0,'published':done}
try:
 while True:
  for s,n in [('S01',84),('S04',72),('S07',108)]:
   if s in done or not (OUT/s/'CLIP_CHECK.json').exists():continue
   check=json.loads((OUT/s/'CLIP_CHECK.json').read_text());ledger=json.loads((OUT/s/'FRAME_LEDGER.json').read_text())
   assert check['frames']==n and [v['frame'] for v in ledger]==list(range(n))
   assert all(v['pass'] for v in check['approvedSampleChecks'])
   dest=R/s;assert not dest.exists(),'Never silently overwrite a completed archive'
   shutil.copytree(OUT/s,dest)
   movie=dest/Path(check['file']).name;assert sha(movie)==check['sha256']
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)],text=True))
   assert len(probe['streams'])==1;v=probe['streams'][0]
   assert v['codec_type']=='video' and int(v['nb_read_frames'])==n and (v['width'],v['height'])==(1920,1080) and v['avg_frame_rate']=='24/1'
   (dest/'FFPROBE_INDEPENDENT.json').write_text(json.dumps(probe,indent=2)+'\n')
   for frame in check['keyframes']:
    p=dest/f'{s}_F{frame:03d}.png';assert sha(p)==ledger[frame]['sha256']
   decode=Path('/tmp/opening-full-independent-decode')/s;decode.mkdir(parents=True,exist_ok=False)
   expr='+'.join('eq(n\\,%d)'%f for f in check['keyframes'])
   run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(movie),'-vf','select='+expr,'-vsync','0',str(decode/'decoded_%03d.png')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   decoded=sorted(decode.glob('decoded_*.png'));assert len(decoded)==len(check['keyframes'])
   cols=4;rows=(len(decoded)+cols-1)//cols;sheet=Image.new('RGB',(1920,rows*298),'#edf0f2');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
   for i,(p,frame) in enumerate(zip(decoded,check['keyframes'])):
    x=(i%cols)*480;y=(i//cols)*298
    with Image.open(p) as im:assert im.size==(1920,1080);sheet.paste(im.convert('RGB').resize((480,270)),(x,y+26))
    draw.text((x+8,y+3),f'{s} decoded F{frame:03d}',font=font,fill='#23364d')
   sheet.save(dest/'INDEPENDENT_DECODED_KEYS_REVIEW.jpg',quality=91)
   verification={'shot':s,'frames':n,'video_sha256':sha(movie),'independent_decoded_frame_count':int(v['nb_read_frames']),'independently_decoded_key_sequence':check['keyframes'],'approved_seven_subset_checks':check['approvedSampleChecks'],'audio_streams':0,'native_key_PNGs_byteexact_to_actual_frame_ledger':True,'distinct_actual_frame_SHA_count':len({v['sha256'] for v in ledger}),'visual_full_clip_review':'PENDING_MAIN_REVIEW','archived_utc':now()}
   (dest/'DELIVERY_VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n')
   files=sorted(p for p in dest.iterdir() if p.is_file() and p.name!='MANIFEST_SHA256.json');(dest/'MANIFEST_SHA256.json').write_text(json.dumps({p.name:sha(p) for p in files},indent=2)+'\n')
   (R/'README.md').write_text('# Opening corrected actual full shots\n\nFixed source c57538925035118c0f8901fc2f22f478fbf803b4; one original streaming render, no restart. Each completed shot is archived and independently decoded before its own publication.\n\nCompleted: '+', '.join([*done,s])+'. Video, original key PNGs, all frame hashes, CLIP_CHECK and independent decode checks are in each shot directory. Full visual review and audio/EDL remain with main coordination. Runtime HTTP final report follows the same original process when all three finish.\n')
   commit=publish('collab: deliver completed corrected opening '+s+' actual clip')
   done[s]={'commit':commit,'video_sha256':sha(movie),'published_utc':now()};status['published']=done;(R/'PUBLICATION_STATE.json').write_text(json.dumps(status,indent=2)+'\n')
   print(json.dumps({'shot_published':s,**done[s]}),flush=True)
  state=json.loads((R/'RUN_STATE.json').read_text())
  if state['state'] in ('COMPLETED','FAILED'):
   if (OUT/'FULL_THREE_CHECK.json').exists():shutil.copyfile(OUT/'FULL_THREE_CHECK.json',R/'FULL_THREE_CHECK.json')
   status.update(state='COMPLETE' if len(done)==3 and state.get('exit_code')==0 else 'STOPPED_WITH_PARTIAL_RESULTS',finished_utc=now(),render_exit_code=state.get('exit_code'))
   (R/'PUBLICATION_STATE.json').write_text(json.dumps(status,indent=2)+'\n')
   final_commit=publish('collab: seal opening three-clip source and HTTP checks')
   print(json.dumps({'final_commit':final_commit,'state':status['state']}),flush=True);break
  time.sleep(5)
except BaseException as e:
 status.update(state='PUBLISHER_ERROR_NO_RENDER_RESTART',error=repr(e),updated_utc=now())
 (R/'PUBLICATION_STATE.json').write_text(json.dumps(status,indent=2)+'\n');raise
