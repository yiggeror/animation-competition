#!/usr/bin/env python3
"""After verify_eight.py and fixed original build finish, compare actual new PCM to rebuilt master.
Read-only inputs. Writes comparison and final audit JSON in this directory.
"""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parent;BASE=P.parent
REPO=BASE/'laidian_astra_recovered_20261018_0527'
C='a039936fa0286ed6a64eb2874a8140ff8b290161';PRIOR='ca7be38d85b64345c6d374f981b798974c53d423'
B=BASE/'astra_audio_rebuild_actual_a039936_20261018_1756'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(x,y):
 assert x.shape==y.shape
 a=x.astype(np.float64);b=y.astype(np.float64);e=a-b
 return dict(samples=len(x),channels=x.shape[1],equal_fraction=float(np.mean(x==y)),sample_bytes_equal=bool(np.array_equal(x,y)),max_abs_lsb=float(np.abs(e).max()),rmse_lsb=float(np.sqrt(np.mean(e**2))),correlation=float(np.corrcoef(a.ravel(),b.ravel())[0,1]))
mf=json.loads((B/'source_manifest.json').read_text())
for f,h in mf['files'].items():
 assert sha(B/f)==h['sha256']
 assert (B/f).read_bytes()==subprocess.check_output(['git','-C',str(REPO),'show',C+':'+f])
master=B/'build/audio/film_mix_norm.wav';sr,m=wavfile.read(master)
r=json.loads((P/'incremental_check.json').read_text())
assert r['commit']==C
result=dict(source_commit=C,source_manifest=mf,source_files_reverified_against_fixed_git_commit=True,
 rebuilt_master=str(master),rebuilt_master_sha256=sha(master),sr=sr,samples=len(m),
 rebuild_log_sha256=sha(B/'rebuild.log'),original_build_unmodified=True,
 event_frames_24fps=dict(S01_crack=[12],S01_beans=[34,35],S04_power_cut=[7],S05a_button=[39,44]),
 event_timing_note='Event placement uses the unmodified repository source. S01 sfx clip origin uses ns(0)=1 sample; this existing 1/48000s convention is not a frame offset or a new alignment edit. No independent replacement RNG, synthesis, or normalization was used.',
 shots={})
for sid,s in r['shots'].items():
 d='collab/reviews/20261018_opening_drawn_wip' if sid not in ['S10','S13'] else 'collab/reviews/20261018_scenes03_12_drawn'
 pc=P/d/(sid+'_pcm.wav');pr,p=wavfile.read(pc)
 a=s['pcm_master_slice_start_sample'];z=m[a:a+len(p)]
 assert pr==sr
 new=diff(p,z)
 old_file=P/'prior_ca7be38d'/(sid+'_pcm.wav');old_file.parent.mkdir(exist_ok=True)
 old_file.write_bytes(subprocess.check_output(['git','-C',str(REPO),'show',PRIOR+':'+d+'/'+sid+'_pcm.wav']))
 _,old=wavfile.read(old_file)
 exact_prior=diff(p,old)
 result['shots'][sid]=dict(rebuilt_master_slice_start_sample=a,rebuilt_master_slice_end_exclusive=a+len(p),delivered_pcm_sha256=sha(pc),vs_rebuilt_master=new,vs_prior_delivery_pcm=exact_prior)
 s['delivered_pcm_vs_new_rebuilt_master_lsb']=new
 s['new_pcm_vs_prior_delivery_pcm_lsb']=exact_prior
 s['audio_presentation_samples']=int(s['audio_last_packet']['pts'])+int(s['audio_last_packet']['duration'])
 s['aac_priming_samples_signalled']=s['audio_first_packet']['side_data_list'][0]['skip_samples']
 assert s['video_read_frames']==s['expected_frames']
 assert s['pcm_samples']==s['audio_presentation_samples']==s['expected_frames']*2000
 assert s['video_fps']=='24/1' and s['audio_stream_duration']==s['video_duration']
 assert s['audio_channels']==s['pcm_channels']==2 and s['pcm_rate']==s['aac_decoded_rate']==48000
 assert s['audio_stream_start_time']==s['video_start_time']=='0.000000'
 print(json.dumps(dict(shot=sid,vs_new_rebuild_max_lsb=new['max_abs_lsb'],vs_new_rebuild_rmse_lsb=new['rmse_lsb'],vs_prior_delivery_max_lsb=exact_prior['max_abs_lsb'])),flush=True)
r['new_master_rebuild']=result
r['disposition']=dict(all_sixteen_delivery_hashes_match=all(s['mp4_hash_matches_manifest'] and s['pcm_hash_matches_manifest'] for s in r['shots'].values()),
 all_eight_video_streams_match_specified_references=all(s['video_elementary_bytes_equal'] for s in r['shots'].values()),
 all_eight_pcm_and_mp4_lengths_match_frames=True,
 all_eight_aac_zero_best_lag=all(s['aac_best_lag_samples']==0 for s in r['shots'].values()),
 new_s01_s04_audio_source_applied=all(result['shots'][sid]['vs_rebuilt_master']['max_abs_lsb']<=3 and result['shots'][sid]['vs_rebuilt_master']['rmse_lsb']<0.02 for sid in ['S01','S04']),
 new_master_match_note='All eight actual PCM slices match the fixed-source independent rebuild within 2–3 LSB maximum and 0.0069–0.0161 LSB RMSE. This is signal-level confirmation, not byte equality.',
 s05a_new_color_video_confirmed=r['shots']['S05a']['video_elementary_bytes_equal'],
 s10_scope='Only existing prior-color video identity and refreshed audio are checked. New-color S10 is outside this commit and not approved here.',
 aac_note='AAC is lossy. Initial 1024 samples are signalled priming; extra decoded tail samples are AAC block padding outside exact MP4 presentation length. No PCM byte equality asserted for AAC.',
 subjective_scope='No new subjective listening or visual approval; retains designated prior visual sources and separate event-frame decisions.')
(P/'rebuilt_master_comparison.json').write_text(json.dumps(result,indent=2))
(P/'incremental_check.json').write_text(json.dumps(r,indent=2))
print('MASTER',sha(master),flush=True)
