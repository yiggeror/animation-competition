from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate,correlation_lags
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;V=P/'opening_v5.mp4'
def run(a,**kw):return subprocess.check_output([str(x) for x in a],**kw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
probe=json.loads((P/'ffprobe.json').read_text());vs=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio')
sr,x=wavfile.read(P/'opening_v5_pcm.wav');n=len(x)
a=np.frombuffer(run(['ffmpeg','-v','error','-i',V,'-map','0:a','-f','f32le','-']),dtype=np.float32).reshape(-1,2);xx=a[:n].astype(float);yy=x.astype(float)/32768
cc=correlate(xx.mean(1),yy.mean(1),method='fft');ll=correlation_lags(n,n);near=np.abs(ll)<=2048;lag=int(ll[near][np.argmax(cc[near])])
pk=json.loads(run(['ffprobe','-v','error','-select_streams','a','-show_packets','-of','json',V]))['packets']
loud=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(V),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;(P/'loudnorm_scan.txt').write_text(loud);lj=json.loads(loud[loud.rindex('{'):loud.rindex('}')+1])
r=dict(commit='44883e8c502a6066a33c67be0e58cf7185554759',video_sha256=sha(V),pcm_sha256=sha(P/'opening_v5_pcm.wav'),frames=int(vs['nb_read_frames']),dimensions=[vs['width'],vs['height']],fps=vs['avg_frame_rate'],video_duration=vs['duration'],audio_duration=au['duration'],video_start=vs['start_time'],audio_start=au['start_time'],pcm_samples=n,pcm_rate=sr,aac_decoded_samples=len(a),aac_best_lag_samples=lag,aac_pcm_correlation=float(np.corrcoef(xx.ravel(),yy.ravel())[0,1]),aac_pcm_rmse=float(np.sqrt(np.mean((xx-yy)**2))),aac_true_peak_dbtp=float(lj['input_tp']),aac_integrated_lufs=float(lj['input_i']),aac_first_packet=pk[0],aac_last_packet=pk[-1],aac_present_end_sample=int(pk[-1]['pts'])+int(pk[-1]['duration']),subjective_listening=False)
(P/'actual_audio_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
frames=[0,12,36,60,83,84,143,144,203,204,299,300,314,317,325,335,336,383,384,385,396,414,418,432,455,456,503,504,575,576,635,636,646,647,654,665,666,675,681,682,694,705,706,721,722,730,738,747,760,761,778,779,790,801,812,817,821,822,825,827,828,829,830,833,847,855,873,879,896,908,912,926,936,944,952,958,966,973]
filt="select='"+'+'.join('eq(n,%d)'%f for f in frames)+"',scale=480:270"
b=run(['ffmpeg','-v','error','-i',V,'-vf',filt,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-']);arr=np.frombuffer(b,np.uint8).reshape(-1,270,480,3);assert len(arr)==len(frames)
for start in range(0,len(frames),15):
 part=list(zip(frames,arr))[start:start+15];out=Image.new('RGB',(1440,5*294),'#222');d=ImageDraw.Draw(out)
 for k,(f,im) in enumerate(part):
  px=k%3*480;py=k//3*294;out.paste(Image.fromarray(im),(px,py));d.text((px+8,py+274),f'actual opening frame {f} | {f/24:.3f}s',fill='white')
 out.save(P/f'actual_edges_{start//15}.jpg',quality=90)
print('ACTUAL EDGES decoded',len(frames),flush=True)
