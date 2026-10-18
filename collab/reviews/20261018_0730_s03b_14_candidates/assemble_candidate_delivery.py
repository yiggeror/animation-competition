from pathlib import Path
import json,re,hashlib,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parent
OUT=R/'delivery'
for d in ['originals','prompts','author_records','qa/onion50']: (OUT/d).mkdir(parents=True,exist_ok=True)
sources={}
for p in sorted((R/'outputs').rglob('*.png')):
    if '/qa/' in str(p):continue
    m=re.search(r'(d\d\d).*?(f\d\d)',p.name,re.I)
    if m:sources[m[1].lower()]=p
if len(sources)!=14:
    print(json.dumps({'ready':False,'original_count':len(sources),'ids':sorted(sources)}));raise SystemExit(0)
spec=json.loads((R/'freeze_v2/S03b.json').read_text());frames=[];rows=[]
font=ImageFont.truetype(str(R/'refs/NotoSansSC-VF.ttf'),23)
base=Image.open(R/'refs/painted/S03_grandma_k07_F079_t3.30.png').convert('RGBA')
def over(im):
    canvas=Image.new('RGBA',(1670,942),(126,126,126,255));canvas.alpha_composite(im,(0,0));return canvas.convert('RGB')
previous=over(base)
for k in spec['keys']:
    did=k['id'];p=sources[did];data=p.read_bytes();im=Image.open(p).convert('RGBA')
    name=f'{did}_f{k["f"]:02d}.png';shutil.copyfile(p,OUT/'originals'/name)
    rows.append({'id':did,'f':k['f'],'hold':k['hold'],'path':'originals/'+name,'source':str(p.relative_to(R)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),'size':list(im.size),'mode':im.mode,'alpha_extrema':im.getchannel('A').getextrema(),'status':'candidate; see REVIEW.md'})
    current=over(im);onion=Image.blend(previous,current,.5);d=ImageDraw.Draw(onion);d.rectangle((0,0,950,38),fill='#eeeeee');d.text((14,3),f'QA 50% 前一态 + 50% {did}；左上原点对齐，不缩放原件',font=font,fill='#111111');onion.save(OUT/'qa/onion50'/f'{did}_previous.jpg',quality=90)
    previous=current;display=current.copy();dd=ImageDraw.Draw(display);dd.rectangle((0,0,620,40),fill='#eeeeee');dd.text((10,4),f'未验收候选 {did} F{k["f"]:02d}–{k["f"]+k["hold"]-1:02d}',font=font,fill='#111111');frames.append(display)
    options=list((R/'outputs').rglob(f'*{did}*prompt*.txt'))+list((R/'outputs').glob(f'raise/prompts/{did}.txt'))
    if not options:
        options=list((R/'outputs').glob(f'chew/prompts/{did}*.txt'))
    if options:shutil.copyfile(options[0],OUT/'prompts'/f'{did}.txt')
    else:
        calls=list((R/'outputs/chew/logs').glob(f'call??_{did}.json'))
        if calls:
            call=json.loads(calls[0].read_text())
            (OUT/'prompts'/f'{did}.txt').write_text(call['prompt']+'\n')
            shutil.copyfile(calls[0],OUT/'author_records'/calls[0].name)

sheet=Image.new('RGB',(1672,1120),'#dddddd')
for i,im in enumerate(frames):sheet.paste(im.resize((418,236)),((i%4)*418,(i//4)*280))
sheet.save(OUT/'qa/all_14_contact.jpg',quality=93)
# Exact planned exposure on neutral gray, for debugging only. No scene, audio or interpolation.
proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1670x942','-framerate','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'qa/raw_sequence_48f_SILENT_NOT_SCENE.mp4')],stdin=subprocess.PIPE)
for k,im in zip(spec['keys'],frames):
    for _ in range(k['hold']):proc.stdin.write(im.tobytes())
proc.stdin.close();assert proc.wait()==0
probe=subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(OUT/'qa/raw_sequence_48f_SILENT_NOT_SCENE.mp4')]).decode()
(OUT/'qa/preview_probe.json').write_text(probe)
manifest={'generation_calls':14,'rerolls':0,'painted_targets':14,'scene_integration_approved':False,'frozen_reference_commit':'b1e19b85221f218376e29e2b08c4630118a7a9b0','spec_path':'collab/reviews/20261018_0712_s03b_pose_proposal/freeze_v2/S03b.json','raw_originals_unchanged':True,'qa_canvas_note':'All QA composites use top-left-aligned 1670x942 canvas; a 941-high original gets one transparent bottom row only in the QA composite. No original rescaled/cropped/modified.','states':rows}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for segment in ['raise','bite','chew']:
    for p in (R/'outputs'/segment).glob('*'):
        if p.is_file() and p.suffix.lower() in ['.json','.txt','.md']:
            shutil.copyfile(p,OUT/'author_records'/f'{segment}_{p.name}')
print(json.dumps({'ready':True,'count':len(rows),'prompt_count':len(list((OUT/'prompts').glob('*'))),'probe':json.loads(probe)},ensure_ascii=False))
