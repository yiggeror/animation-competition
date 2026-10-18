#!/usr/bin/env python3
"""Read fixed a039936 git objects; audit eight actual delivered MP4/PCM pairs. Writes only this audit directory.
Requires python3 numpy scipy, ffmpeg, ffprobe, node. Never checks out or edits source tree.
Rerun: python3 /absolute/path/to/verify_eight.py
"""
from pathlib import Path
import subprocess,json,hashlib,sys,platform
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate,correlation_lags
P=Path(__file__).resolve().parent;BASE=P.parent
REPO=BASE/'laidian_astra_recovered_20261018_0527'
COMMIT='a039936fa0286ed6a64eb2874a8140ff8b290161'
OLD='da55623dc0a451ebb62b0df3ffde9b36c31501c6'
OLDROOT=BASE/'astra_audio_rebuild_20261018_da55623'
OPEN='collab/reviews/20261018_opening_drawn_wip'
SCENES='collab/reviews/20261018_scenes03_12_drawn'
SHOTS={
'S01':(OPEN,'S01_drawn_v2.mp4','astra_s01_contact_actual_20261018_1727/S01_contact_full84.mp4',84),
'S04':(OPEN,'S04_drawn_v2.mp4','astra_s04_contact_actual_20261018_1727/S04_contact_color_final72.mp4',72),
'S05a':(OPEN,'S05a_drawn_v4.mp4','astra_s05a_semantic60_actual_20261018_1742/S05a_semantic60.mp4',60),
'S02a':(OPEN,'S02a_drawn_v6.mp4','astra_eight_audio_increment_a039936_20261018_1757/prior_ca7be38d/S02a_drawn_v6.mp4',60),
'S03':(OPEN,'S03_drawn_v3.mp4','astra_eight_audio_increment_a039936_20261018_1757/prior_ca7be38d/S03_drawn_v3.mp4',96),
'S03a':(OPEN,'S03a_drawn_v4.mp4','astra_s03a_color36_actual_20261018_1727/S03a_color36.mp4',36),
'S10':(SCENES,'S10_drawn_v1.mp4','astra_s10_audio_actual_20261018_1607/S10_drawn_v1.mp4',120),
'S13':(SCENES,'S13_drawn_v1.mp4','astra_s13_color120_actual_20261018_1723/S13_color120_720p24.mp4',120),
}
def run(args,**kw):return subprocess.check_output([str(x) for x in args],**kw)
def git(path,rev=COMMIT):return run(['git','-C',REPO,'show',rev+':'+path])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def export(path):
 out=P/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(git(path));return out

def probe(p,count=False):
 args=['ffprobe','-v','error']
 if count:args+=['-count_frames']
 return json.loads(run(args+['-show_streams','-show_format','-of','json',p]))
def audio_metrics(x,y):
 assert x.shape==y.shape
 e=x-y
 return {'rmse':float(np.sqrt(np.mean(e**2))),'max_abs_error':float(np.max(np.abs(e))),
 'correlation':float(np.corrcoef(x.ravel(),y.ravel())[0,1]),'rms_reference':float(np.sqrt(np.mean(y**2))),
 'snr_db':float(10*np.log10(np.mean(y**2)/np.mean(e**2))) if np.any(e) else None,
 'equal_fraction':float(np.mean(x==y))}
# Verify reusable historical master source, not merely its directory name.
helpers=['audio/build.py','audio/inst.py','audio/sfx.py','audio/score.py','js/film/edl.js','package.json']
provenance={}
for h in helpers:
 local=OLDROOT/h
 provenance[h]={'local_sha256':sha(local),'matches_old_git_blob':local.read_bytes()==git(h,OLD),
 'latest_sha256':hashlib.sha256(git(h)).hexdigest()}
 export(h)
old_shots=json.loads(run(['node','-e',"import('./js/film/edl.js').then(m=>console.log(JSON.stringify(m.SHOTS)))"],cwd=OLDROOT))
new_shots=json.loads(run(['node','-e',"import('./js/film/edl.js').then(m=>console.log(JSON.stringify(m.SHOTS)))"],cwd=P))
starts={};t=0
for s in new_shots: starts[s['id']]=t;t+=s['dur']
oldtiming=[(s['id'],s['dur']) for s in old_shots];newtiming=[(s['id'],s['dur']) for s in new_shots]
old_master=OLDROOT/'build/audio/film_mix_norm.wav';mr,m=wavfile.read(old_master)
result={'commit':COMMIT,'old_master_source_commit':OLD,'old_master_source_provenance':provenance,
'old_and_new_edl_timing_equal':oldtiming==newtiming,'old_master_path':str(old_master),'old_master_sha256':sha(old_master),
'old_master_rate':mr,'old_master_samples':len(m),'python':sys.version,'numpy':np.__version__,
'ffmpeg':run(['ffmpeg','-version']).decode().splitlines()[0],'shots':{},
'boundaries':['Signal/bitstream audit only; not a fresh subjective visual or listening approval.',
'Full delivery-file hash, PCM reference comparison, and lossy AAC comparison are separate checks.',
'New S01 F012/F034/F035 and S04 F007 source timing is checked against independently rebuilt audio; actual action frame selection is inherited from the separate visual reviewer.']}
for sid,(d,name,src,nf) in SHOTS.items():
 sd=P/sid;sd.mkdir(exist_ok=True)
 v=export(d+'/'+name);pcm=export(d+'/'+sid+'_pcm.wav');manifest=export(d+'/SHA256SUMS.txt')
 expected={line.split()[1]:line.split()[0] for line in manifest.read_text().splitlines() if line.strip()}
 reference=BASE/src
 vp=probe(v,True);rp=probe(reference,True)
 (sd/'mp4_probe.json').write_text(json.dumps(vp,indent=2));(sd/'reference_probe.json').write_text(json.dumps(rp,indent=2))
 for source,out in [(v,'delivered.h264'),(reference,'approved_silent.h264')]:
  run(['ffmpeg','-y','-v','error','-i',source,'-map','0:v:0','-c','copy','-bsf:v','h264_mp4toannexb','-f','h264',sd/out])
 decoded=sd/'decoded_aac.wav';run(['ffmpeg','-y','-v','error','-i',v,'-map','0:a:0','-c:a','pcm_f32le',decoded])
 ar,a=wavfile.read(decoded);pr,p=wavfile.read(pcm);n=min(len(a),len(p))
 x=a[:n].astype(np.float64);y=p[:n].astype(np.float64)/32768
 mono_x=x.mean(1);mono_y=y.mean(1)
 c=correlate(mono_x,mono_y,method='fft');lags=correlation_lags(n,n);keep=np.abs(lags)<=2048
 lag=int(lags[keep][np.argmax(c[keep])])
 start=round(starts[sid]*mr);master_slice=m[start:start+len(p)].astype(np.float64)
 vstr=next(s for s in vp['streams'] if s['codec_type']=='video');astr=next(s for s in vp['streams'] if s['codec_type']=='audio')
 packets=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,pts_time,duration_time,side_data_list','-of','json',v]))
 (sd/'audio_packets.json').write_text(json.dumps(packets,indent=2))
 peak=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(v),'-map','0:a:0','-af','loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 (sd/'loudnorm_scan.txt').write_text(peak.stderr)
 loud=json.loads(peak.stderr[peak.stderr.rindex('{'):peak.stderr.rindex('}')+1])
 out={'mp4_path':str(v),'mp4_sha256':sha(v),'mp4_hash_matches_manifest':sha(v)==expected[name],
 'pcm_sha256':sha(pcm),'pcm_hash_matches_manifest':sha(pcm)==expected[sid+'_pcm.wav'],
 'silent_reference_path':str(reference),'silent_reference_sha256':sha(reference),
 'video_elementary_sha256':sha(sd/'delivered.h264'),'silent_elementary_sha256':sha(sd/'approved_silent.h264'),
 'video_elementary_bytes_equal':(sd/'delivered.h264').read_bytes()==(sd/'approved_silent.h264').read_bytes(),
 'video_codec':vstr['codec_name'],'video_dimensions':[vstr['width'],vstr['height']],
 'expected_frames':nf,'video_read_frames':int(vstr['nb_read_frames']),'video_reported_frames':int(vstr['nb_frames']),
 'video_fps':vstr['avg_frame_rate'],'video_start_time':vstr['start_time'],'video_duration':vstr['duration'],
 'audio_codec':astr['codec_name'],'audio_channels':astr['channels'],'audio_stream_duration':astr['duration'],
 'audio_stream_duration_ts':astr['duration_ts'],'audio_stream_time_base':astr['time_base'],'audio_stream_start_time':astr['start_time'],
 'audio_first_packet':packets['packets'][0],'audio_last_packet':packets['packets'][-1],
 'pcm_rate':pr,'pcm_samples':len(p),'pcm_channels':p.shape[1],'pcm_duration':len(p)/pr,
 'aac_decoded_rate':ar,'aac_decoded_samples':len(a),'aac_decoded_duration':len(a)/ar,
 'aac_decoded_trailing_samples_beyond_pcm':len(a)-len(p),'aac_best_lag_samples':lag,
 'aac_vs_pcm_zero_lag':audio_metrics(x,y),'aac_vs_pcm_channel_correlations':[float(np.corrcoef(x[:,i],y[:,i])[0,1]) for i in range(2)],
 'aac_sample_peak_dbfs':float(20*np.log10(np.abs(a).max())),
 'aac_true_peak_dbtp_ffmpeg_loudnorm':float(loud['input_tp']),
 'pcm_master_slice_start_sample':start,'pcm_master_slice_end_sample_exclusive':start+len(p),
 'delivered_pcm_vs_old_master_lsb':audio_metrics(p.astype(np.float64),master_slice),
 'pcm_sample_peak_dbfs':float(20*np.log10(np.abs(p.astype(np.float64)).max()/32768))}
 result['shots'][sid]=out
 (P/'incremental_check.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({'shot':sid,'h264_identical':out['video_elementary_bytes_equal'],'frames':out['video_read_frames'],'seconds':out['video_duration'],
 'pcm_samples':len(p),'aac_samples':len(a),'lag':lag,'corr':out['aac_vs_pcm_zero_lag']['correlation'],
 'old_master_max_lsb':out['delivered_pcm_vs_old_master_lsb']['max_abs_error'],'old_master_rmse_lsb':out['delivered_pcm_vs_old_master_lsb']['rmse'],
 'true_peak_dbtp':out['aac_true_peak_dbtp_ffmpeg_loudnorm']}),flush=True)
(P/'audio_build_delta.patch').write_bytes(run(['git','-C',REPO,'diff',OLD,COMMIT,'--','audio/']))
(P/'edl_delta.patch').write_bytes(run(['git','-C',REPO,'diff',OLD,COMMIT,'--','js/film/edl.js']))
print('Complete:',P/'incremental_check.json',flush=True)
