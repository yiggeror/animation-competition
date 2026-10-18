"""Decode only the requested frames from the two actual Chromium MP4s."""
from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent
segments=[('S07_first25',0,25,[0,2,3,5,6,7,8,15,16,17,18,21,22,24],(4,4)),
          ('S07_x39_56',39,18,[39,42,43,45,46,48,49,52,53,56],(5,2))]
results=[]
for name,start,count,frames,tile in segments:
    video=P/(name+'.mp4');d=P/(name+'_decoded');d.mkdir(exist_ok=True)
    q=subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],capture_output=True,text=True,check=True)
    (P/(name+'_ffprobe.json')).write_text(q.stdout)
    info=json.loads(q.stdout);v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1280,720,'24/1',count)
    for absolute in frames:
        local=absolute-start
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f'select=eq(n\\,{local})','-frames:v','1',str(d/f'F{absolute:03d}.png')],check=True)
    select='+'.join(f'eq(n\\,{f-start})' for f in frames)
    text='F%{n}' if start==0 else 'F%{eif\\:n+39\\:d}'
    fil="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='"+text+"':x=12:y=12:fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.7,"+f'select={select},scale=426:240,tile={tile[0]}x{tile[1]}'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',fil,'-frames:v','1',str(P/(name+'_contact.png'))],check=True)
    results.append({'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,
        'absolute_start_frame':start,'absolute_end_frame':start+count-1,'decoded_frame_count':count,'fps':24,'size':[1280,720],
        'duration':count/24,'has_audio':any(s['codec_type']=='audio' for s in info['streams']),
        'requested_absolute_frames':frames,'MP4_local_frame_mapping':f'local=absolute-{start}'})
(P/'actual_video_manifest.json').write_text(json.dumps({'source_commit':'60159846257c803263b4eab675ba35487fff12ce','render_method':'actual unchanged project module in Chromium; decoded with ffmpeg','segments':results,'not_rendered_ranges':[[25,38],[57,107]],'complete_shot':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
