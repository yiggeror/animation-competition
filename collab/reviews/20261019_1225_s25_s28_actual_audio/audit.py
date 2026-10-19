from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate,correlation_lags
P=Path(__file__).resolve().parent
ROOT=P.parent
OLD=ROOT/'astra_opening_v4_571cf92_20261019/rebuild'
def run(a):return subprocess.check_output([str(x) for x in a])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def shots(p):return json.loads(run(['node','-e',"import("+json.dumps(str(p/'js/film/edl.js'))+").then(m=>console.log(JSON.stringify(m.SHOTS)))"]))
new=shots(P/'source');old=shots(OLD)
source={f:sha(P/'source'/f)==sha(OLD/f) for f in ['audio/build.py','audio/inst.py','audio/score.py','audio/sfx.py','package.json']}
same_timing=[(s['id'],s['dur']) for s in new]==[(s['id'],s['dur']) for s in old]
assert all(source.values()) and same_timing
sr,master=wavfile.read(OLD/'build/audio/film_mix_norm.wav'); assert sr==48000
starts={};t=0
for s in new: starts[s['id']]=round(t*sr);t+=s['dur']
baselines={'S25':ROOT/'astra_s25_browser_actual_20261019_0926/S25_export_only_diagnostic_actual144.mp4','S28':ROOT/'s28_rod_clearance_review/stage_module_candidate/full192_actual_03d5a24/originals/S28_FULL192_24FPS_8S.mp4'}
events={'S25':[1.2,4.6,5.35],'S28':[.2,1.4,5.5]}
result={'commit':'582bd1b6b89bfc52b58143ab76a778750ea987cd','independent_master_source_commit':'571cf92dff016d6b7a954250515dc78d398538c1','source_bytes_same':source,'edl_timing_same':same_timing,'independent_master_sha256':sha(OLD/'build/audio/film_mix_norm.wav'),'subjective_listening':False,'shots':{}}
for sid in ['S25','S28']:
 v=P/(sid+'_drawn_v1.mp4');pcm=P/(sid+'_pcm.wav');probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',v]));vs=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio')
 raw=run(['ffmpeg','-v','error','-i',v,'-map','0:v:0','-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-']);base=run(['ffmpeg','-v','error','-i',baselines[sid],'-map','0:v:0','-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])
 rate,x=wavfile.read(pcm);n=len(x);ref=master[starts[sid]:starts[sid]+n];diff=x.astype(float)-ref.astype(float)
 a=np.frombuffer(run(['ffmpeg','-v','error','-i',v,'-map','0:a:0','-f','f32le','-']),np.float32).reshape(-1,2);xx=a[:n].astype(float);yy=x.astype(float)/32768
 cc=correlate(xx.mean(1),yy.mean(1),method='fft');ll=correlation_lags(n,n);near=np.abs(ll)<=2048;lag=int(ll[near][np.argmax(cc[near])])
 loud=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(v),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr;(P/(sid+'_loudnorm.txt')).write_text(loud);lj=json.loads(loud[loud.rindex('{'):loud.rindex('}')+1])
 pk=json.loads(run(['ffprobe','-v','error','-select_streams','a','-show_packets','-of','json',v]))['packets']
 ev=[]
 for tm in events[sid]:
  lo=max(0,round((tm-.1)*sr));hi=min(n,round((tm+.3)*sr));d=diff[lo:hi];ev.append({'time':tm,'frame_at_24fps':tm*24,'sample':round(tm*sr),'window_max_lsb':float(np.abs(d).max()),'window_rmse_lsb':float(np.sqrt(np.mean(d*d)))})
 r={'mp4_sha256':sha(v),'pcm_sha256':sha(pcm),'video_stream_identical_to_approved_silent':raw==base,'h264_sha256':hashlib.sha256(raw).hexdigest(),'frames':int(vs['nb_read_frames']),'dimensions':[vs['width'],vs['height']],'fps':vs['avg_frame_rate'],'video_duration':vs['duration'],'aac_duration':au['duration'],'video_start':vs['start_time'],'aac_start':au['start_time'],'pcm_samples':n,'pcm_rate':rate,'master_slice':[starts[sid],starts[sid]+n],'pcm_master_max_lsb':float(np.abs(diff).max()),'pcm_master_rmse_lsb':float(np.sqrt(np.mean(diff*diff))),'aac_decoded_samples':len(a),'aac_best_lag_samples':lag,'aac_pcm_correlation':float(np.corrcoef(xx.ravel(),yy.ravel())[0,1]),'aac_true_peak_dbtp':float(lj['input_tp']),'aac_integrated_lufs':float(lj['input_i']),'aac_first_packet':pk[0],'aac_last_packet':pk[-1],'event_windows':ev,'edl':next(s for s in new if s['id']==sid)}
 result['shots'][sid]=r
 (P/'ACTUAL_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(sid,json.dumps({k:r[k] for k in ['video_stream_identical_to_approved_silent','frames','pcm_samples','pcm_master_max_lsb','aac_best_lag_samples','aac_pcm_correlation','aac_true_peak_dbtp']}),flush=True)
print('COMPLETE',flush=True)
