from pathlib import Path
import json,hashlib,re
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate
B=Path(__file__).resolve().parents[1];A=B/'actual';I=B.parents[1]/'batch1_v3_actual'
sr,oi=wavfile.read(I/'film_mix_norm_8902b59d_0-30s.wav');assert sr==48000 and oi.dtype==np.int16 and oi.shape==(1440000,2)
_,ri=wavfile.read(B/'isolated/build/audio/film_mix_norm.wav');ri=ri[:30*sr]
_,dec=wavfile.read(A/'decoded_pts_f32.wav');dec=dec.astype(np.float64);opus=oi.astype(np.float64)/32768
mapping=[('S01',0,0,12),('S03',12,16,6),('S04',18,22,8)]
expected=np.concatenate([opus[s*sr:(s+n)*sr] for _,_,s,n in mapping])
def db(v):return float(20*np.log10(max(float(v),1e-30)))
def compare(start,end,lag=None):
 a=round(start*sr);z=round(end*sr);ref=expected[a:z];n=len(ref)
 if lag is None:
  pad=4800;lo=max(0,a-pad);hi=min(len(dec),z+pad);search=dec[lo:hi]
  cc=sum(correlate(search[:,c],ref[:,c],mode='valid',method='fft') for c in [0,1]);e=np.concatenate(([0.],np.cumsum(np.sum(search*search,axis=1))));es=e[n:]-e[:-n];cc/=np.sqrt(np.maximum(es*np.sum(ref*ref),1e-50));lag=lo+int(np.argmax(cc))-a
 obs=dec[a+lag:z+lag];g=float(np.sum(ref*obs)/np.sum(ref*ref));d=obs-ref;err=obs-g*ref;rms=lambda v:float(np.sqrt(np.mean(v*v)))
 return {'edit_seconds':[float(start),float(end)],'lag_samples':lag,'correlation':float(np.corrcoef(ref.ravel(),obs.ravel())[0,1]),'gain_ratio':g,'gain_db':db(g),'source_rms_dbfs':db(rms(ref)),'decoded_rms_dbfs':db(rms(obs)),'difference_rms_dbfs':db(rms(d)),'residual_snr_db':db(rms(g*ref)/rms(err))}
def pcm_diff(a,z):
 v=oi[a*sr:z*sr].astype(np.int32);u=ri[a*sr:z*sr].astype(np.int32);d=v-u;den=float(np.sum(u.astype(float)**2));g=float(np.sum(v.astype(float)*u)/den);vals,counts=np.unique(d,return_counts=True)
 return {'master_seconds':[a,z],'values':int(d.size),'different_values':int(np.count_nonzero(d)),'max_difference_lsb':int(abs(d).max()),'difference_rms_dbfs':db(np.sqrt(np.mean(d.astype(float)**2))/32768),'correlation':float(np.corrcoef(u.ravel(),v.ravel())[0,1]),'gain_ratio':g,'delta_counts':{str(k):int(c) for k,c in zip(vals,counts)}}
windows=[]
for shot,es,ms,dur in mapping:
 for off in [0.1]+list(range(1,dur)):
  windows.append({'shot':shot,**compare(es+off,min(es+off+0.6,es+dur-0.1))})
lags={w['lag_samples'] for w in windows};assert len(lags)==1;common_lag=next(iter(lags))
shot_metrics=[{'shot':shot,'source_master_seconds':[ms,ms+dur],**compare(es,es+dur,common_lag)} for shot,es,ms,dur in mapping]
events=json.loads((B/'analysis/runtime_events.json').read_text());cue_windows=[]
for e in events['events']:
 t=e['scheduled_seconds'];cue_windows.append({'type':e['type'],'frame':e['scheduled_frame_at_24fps'],'source_seconds':t,**compare(t-0.025,t+0.075)})
for local in [3.8,4.0]:cue_windows.append({'type':'S03_bite','local_seconds':local,'source_seconds':16+local,**compare(12+local-0.025,12+local+0.075)})
cue_windows.append({'type':'S04_power_cut','local_seconds':0.6,'source_seconds':22.6,**compare(18.55,18.95)})
frames=json.loads((A/'audio_pts.json').read_text())['frames'];anomalies=[]
for i,(p,q) in enumerate(zip(frames,frames[1:])):
 delta=p['pts']+p['nb_samples']-q['pts']
 if delta:anomalies.append({'frame_index':i,'previous_pts':p['pts'],'previous_pts_seconds':p['pts']/sr,'previous_nb_samples':p['nb_samples'],'next_pts':q['pts'],'next_pts_seconds':q['pts']/sr,'overlap_samples':delta,'overlap_ms':delta/sr*1000})
v=json.loads((A/'video_pts.json').read_text())['frames'];boundary=[{'edit_cut_seconds':n,'video_frame':int(n*24),'video_pts_seconds':v[int(n*24)]['best_effort_timestamp']/12288,'audio_content_reference_pts_seconds':n+common_lag/sr} for n in [0,12,18]]
probe=json.loads((A/'mp4_probe.json').read_text());loud=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',(A/'loudnorm.txt').read_text(),re.S)[-1])
r={'fixed_media_commit':'2e5270b39a74f87807d1e774975cac1f69d0f2a2','fixed_audio_source_commit':'2e5270b39a74f87807d1e774975cac1f69d0f2a2','input_file_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [I/'film_mix_norm_8902b59d_0-30s.wav',I/'batch1_S01_S03_S04_1080p.mp4']},'pcm_sha256_received_0_30':hashlib.sha256(oi.tobytes()).hexdigest(),'pcm_sha256_independent_0_30':hashlib.sha256(ri.tobytes()).hexdigest(),'pcm_difference_total':pcm_diff(0,30),'pcm_difference_shots':[pcm_diff(ms,ms+du) for _,_,ms,du in mapping],'audio_full_edit':compare(0,26,common_lag),'audio_shots':shot_metrics,'alignment_windows':windows,'event_windows':cue_windows,'video_audio_reference_boundaries':boundary,'audio_pts_overlaps':anomalies,'decode_method':'aresample=async=1:min_hard_comp=0.00001:first_pts=0, then stereo normalized cross correlation and least-squares gain. Overlap correction is explicit; sample-concatenation WAV length is not treated as actual A/V lag.','pts_respected_decode_frames':len(dec),'audio_vs_video_reference_delta_ms':(common_lag/sr-v[0]['best_effort_timestamp']/12288)*1000,'measured_audio':{k:loud[k] for k in ['input_i','input_tp','input_lra']},'limits':['+3 frames after suspended-bean poses is authored audio scheduling, not verified physical bowl contact.','PTS-respecting waveform alignment is not an actual playback/listening test. AAC overlaps remain a container property, not proof of a specific perceived delay.','Full production master 8902… file/PCM SHA cannot be verified from a 0–30-second slice.','No subjective listening or visual contact review.']}
r['boundary_waveform_windows']=[{'cut_seconds':cut,**compare(cut+start,cut+end,common_lag)} for cut in [12,18] for start,end in [(-.1,-.025),(-.025,.025),(0,.01),(0,.025),(.025,.1),(.1,.3)]]
(A/'verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps({k:r[k] for k in ['pcm_sha256_received_0_30','pcm_sha256_independent_0_30','pcm_difference_total','audio_full_edit','audio_shots','video_audio_reference_boundaries','audio_pts_overlaps','measured_audio']},ensure_ascii=False,indent=2))
print('Event windows',len(cue_windows),'correlation range',min(x['correlation'] for x in cue_windows),max(x['correlation'] for x in cue_windows),'lags',sorted({x['lag_samples'] for x in cue_windows}))
