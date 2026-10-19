"""Decode the already-rendered unique run; never invokes the browser renderer.

python decode_full_run.py /workspace/s30-full288-ed1721c1-20261019
Streams RGB one frame at a time, saves 12 contact JPEGs and 10 finite decoded
key JPEGs; does not dump a full PNG/JPEG frame sequence.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess,sys,re
R=Path(__file__).resolve().parent
runtime=Path(sys.argv[1]);out=R/'actual_browser_frames'
video=out/'S30_COMPLETE_288f_24fps_NO_AUDIO.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(R/'FFPROBE_FULL288.json').write_text(json.dumps(probe,indent=2)+'\n')
vs=[s for s in probe['streams']if s['codec_type']=='video'];assert len(vs)==1
v=vs[0];assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',288)
assert not any(s['codec_type']=='audio'for s in probe['streams'])
assert abs(float(probe['format']['duration'])-12)<1e-6
browser=json.loads((out/'ACTUAL_BROWSER_RENDER_REPORT.json').read_text())
assert browser['all288']and browser['frames']==288
assert browser['rawSHAverified']==22
for k in ['missing','httpFailures','requestFailures']:assert not browser[k]
# Preserve the original script failure. A post-video repeat mismatch must not
# prevent independently checking or delivering the completed288f MP4.
repeat_pass=len(browser['isolation'])==5 and all(x['pass']for x in browser['isolation'])
if browser['errors']:
    assert browser['status']=='ERROR'
    assert all('Cross-renderer repeated-frame mismatch' in x for x in browser['errors'])
else:assert browser['status']=='RENDERED_FOR_VISUAL_REVIEW'
module=(runtime/'js/paint/shots/s30_drawn.js').read_text()
exp=json.loads(re.search(r',EXPOSURE=(\[.*?\]);',module).group(1));state_checks=[]
for f,s in enumerate(browser['states']):
    branch='north_tv'if f<40 else'south_door'if f<190 else'original_frozen_head'
    assert s['frame']==f and s['branch']==branch
    if f<190:
        row=next(e for e in exp if e['start']<=f<=e['end'])
        assert s['pose']==row['pose']and s['lit']==(f<144)
        assert s['holding']==(120<=f<147)and s['tvOn']==(f<27)
    state_checks.append({'frame':f,'branch':branch,'pose':s.get('pose'),'lit':s.get('lit'),'holding':s.get('holding'),'tvOn':s.get('tvOn')})
static=json.loads((R.parent/'CLOUD_ACTUAL_BROWSER_VERIFICATION.json').read_text())
protected=[]
for x in static['protected_source_files_verified_after_run']:
    actual=sha(runtime/x['path']);assert actual==x['SHA256'];protected.append({**x,'after_full_run_SHA256':actual})
keys=[0,26,27,39,40,54,96,114,120,132,138,143,144,146,147,162,180,189,190,287]
saved=sorted(out.glob('F*.jpg'));assert len(saved)==20
key_checks=[]
for f in keys:
    p=out/f'F{f:03d}.jpg';im=Image.open(p);assert im.format=='JPEG'and im.size==(1920,1080)
    old=R.parent/'actual_browser_frames'/p.name
    key_checks.append({'frame':f,'full_run_JPEG_SHA256':sha(p),'previous_static_JPEG_SHA256':sha(old),'same_as_previous_static':sha(p)==sha(old)})
review=R/'decoded_review';review.mkdir(exist_ok=True)
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
size=1920*1080*3;checks=[];previous=None
finite={27,39,40,120,138,143,144,147,190,287};sheet=None;draw=None
for f in range(288):
    b=proc.stdout.read(size);assert len(b)==size
    im=Image.frombytes('RGB',(1920,1080),b)
    checks.append({'frame':f,'RGB24_SHA256':hashlib.sha256(b).hexdigest()})
    if f%24==0:sheet=Image.new('RGB',(1920,824),(225,228,231));draw=ImageDraw.Draw(sheet)
    i=f%24;x=(i%6)*320;y=(i//6)*206;sheet.paste(im.resize((320,180)),(x,y+26));draw.text((x+8,y+6),f'{f:03d}  {f/24:.3f}s',fill='black')
    if f in finite:im.save(review/f'DECODED_F{f:03d}.jpg',quality=96,subsampling=0)
    if f%24==23:sheet.save(review/f'ALL_FRAMES_SECOND_{f//24:02d}.jpg',quality=96,subsampling=0)
assert not proc.stdout.read(1);assert proc.wait()==0
report={'status':'FULL288_VIDEO_COMPLETE_ISOLATION_HOLD'if not repeat_pass else'FULL288_TECHNICAL_CHECK_PASS_PENDING_ACTUAL_SEQUENCE_REVIEW','source_commit':'ed1721c17b4e27d1e72a4379cdd67eb3edfeef21','unique_authorized_full_browser_runs':1,'new_cloud_image_generation':0,'width':1920,'height':1080,'decoded_frames':288,'fps':'24/1','duration_seconds':12,'audio_streams':0,'mp4_SHA256':sha(video),'original_script_SHA256':sha(runtime/'collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs'),'protected_source_files_verified_after_full_run':protected,'all_22_raw_assets_verified':True,'five_repeat_JPEG_SHA_pass':repeat_pass,'original_script_exit_code':1 if browser['errors']else 0,'original_script_errors':browser['errors'],'actual_repeat_diagnostics':browser['isolation'],'diagnostics_not_executed_after_failure':[190,120]if len(browser['isolation'])==3 else[],'cross_run_static_key_comparison':key_checks,'browser_page_errors':[],'required_http_failures':0,'missing_assets':0,'request_failures':0,'frame_state_checks':state_checks,'all_decoded_RGB24_SHA256':checks,'stored_original_canvas_keys':20,'stored_decoded_full_size_keys':len(finite),'stored_all_frame_contact_sheets':12,'full_PNG_sequence_dumped':False,'shared_production_branch_modified':False,'ready_claimed':False,'notes':'Original renderer emits JPEG(.96) to ffmpeg; no PNG/RGBA zero-difference claim. Decoded JPEGs/contact sheets are finite visual evidence, not source states. Repeat failure preserved; failed repeat0 JPEG itself was not saved by original script, only its hash.'}
(R/'CLOUD_FULL288_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['protected_source_files_verified_after_full_run','cross_run_static_key_comparison','frame_state_checks','all_decoded_RGB24_SHA256']},indent=2))
