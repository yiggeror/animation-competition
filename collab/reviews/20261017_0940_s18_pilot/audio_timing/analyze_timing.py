from pathlib import Path
import json,math,hashlib,wave
import numpy as np
p=Path('/tmp/laidian-s18-pilot-audit/audio_timing')
keys=json.loads((p/'source/docs/keyframes/S18.json').read_text())['keys']
table=[]
for i,k in enumerate(keys):
 f=math.ceil(k['t']*24-1e-10)
 nextf=math.ceil(keys[i+1]['t']*24-1e-10) if i+1<len(keys) else 72
 table.append({'key':i+1,'declared_seconds':k['t'],'first_frame_when_t_gte_start':f,'actual_seconds':f/24,'hold_frames_until_next_declared_key':nextf-f,'note':k['note']})
# Proposal only, no timeline or code is applied. Keep current audio and 3-frame grid.
seq=[(0,1),(6,2),(9,3),(15,4),(18,5),(21,6),(24,7),(27,8),(30,9),(33,8),(36,9),(39,8),(42,9),(45,10),(54,11),(63,12)]
r={'fps':24,'frame_numbering':'zero-based; samples at t=f/24; three-second shot F0..F71, exclusive end F72',
 'current_literal_key_sampling':table,
 'old_fallback':{'T_PU':0.42,'first_laugh_frame':11,'first_laugh_seconds':11/24,'note':'Only used if flip loading fails; flip branch returns before T_PU gate.'},
 'audio_event':{'type':'synthesized pipa note in music, source comment says 噗; not a recorded vocal/laugh SFX','local_s':0.6,'absolute_s':115.6,'sample_rate':48000,'local_pcm_placement_sample':28800,'absolute_pcm_placement_sample':5548800,'continuous_frame_coordinate':14.4,'nearest_integer_frame':14,'nearest_frame_seconds':14/24,'three_frame_grid_nearest':15,'three_frame_grid_seconds':15/24},
 'recommended_if_reusing_current_master':{'pu_frame':15,'pu_seconds':15/24,'audio_leads_picture_seconds':15/24-0.6,'timeline_frames':[{'f':f,'t':f/24,'key':k} for f,k in seq],'note':'Proposal for frame selection, not an adopted edit or perceptual lip-sync approval.'},
 'alternative_if_plan_PU_F12_is_kept':{'pu_frame':12,'pu_seconds':0.5,'current_audio_lags_seconds':0.1,'required_future_audio_cue':'T(\'S18\', 12 / 24)','must_rebuild_and_remeasure_new_outputs':True},
 'S31':{'start':206.5,'current_F0_light_gain':1.0,'range_on': [0.97,1.03],'T_BOB':0.6,'removed_click_local_time':0.6,'removed_click_absolute_time':207.1,'plan_conflict_lines':[30,65]}}
(p/'timing.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
# Read actual unchanged master only. RMS is a mixed-waveform diagnostic, not vocal recognition.
wp=Path('/tmp/laidian-audio-final-no-extra-click/film_mix_norm.wav')
with wave.open(str(wp),'rb') as w:
 sr=w.getframerate();ch=w.getnchannels();w.setpos(int(115.4*sr));data=np.frombuffer(w.readframes(int(.5*sr)),dtype='<i2').reshape(-1,ch).astype(np.float64)/32768
rows=[]
for i in range(50):
 y=data[i*480:(i+1)*480]
 rows.append({'S18_local_start_s':round(.4+i*.01,3),'window_ms':10,'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(y*y))+1e-20)),'peak_dbfs':float(20*np.log10(np.max(np.abs(y))+1e-20))})
(p/'actual_wav_window_levels.json').write_text(json.dumps({'method':'Read unchanged verified WAV samples; 10ms stereo RMS/peak. No event source isolation or subjective listening; mixed signal levels are not proof of a vocal sound.','wave_sha256':hashlib.sha256(wp.read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n')
print(json.dumps({'current_literal_key_sampling':table,'audio_event':r['audio_event']},ensure_ascii=False,indent=2))
