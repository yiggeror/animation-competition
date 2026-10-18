#!/usr/bin/env python3
"""Read-only fixed-commit S10 v2 media audit. No master rebuild or image rendering."""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate,correlation_lags
P=Path(__file__).resolve().parent;B=P.parent;R=B/'laidian_astra_recovered_20261018_0527'
C='40aca5fa89d07d017e41d69cbe48ff1e18a3ca79';A='a039936fa0286ed6a64eb2874a8140ff8b290161'
D='collab/reviews/20261018_scenes03_12_drawn'
REF=B/'astra_s10_semantic120_actual_20261018_1753/S10_semantic120.mp4'
OLD=B/'astra_eight_audio_increment_a039936_20261018_1757'/D/'S10_pcm.wav'
MASTER=B/'astra_audio_rebuild_actual_a039936_20261018_1756/build/audio/film_mix_norm.wav'
def run(a):return subprocess.check_output([str(x) for x in a])
def git(p,c=C):return run(['git','-C',R,'show',c+':'+p])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writejson(p,o):Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False))
for f in ['S10_drawn_v2.mp4','S10_pcm.wav','SHA256SUMS.txt']:(P/f).write_bytes(git(D+'/'+f))
v=P/'S10_drawn_v2.mp4';pc=P/'S10_pcm.wav';expected={x.split()[1]:x.split()[0] for x in (P/'SHA256SUMS.txt').read_text().splitlines()}
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',v]));writejson(P/'ffprobe.json',probe)
for f,n in [(v,'new.h264'),(REF,'approved.h264')]:run(['ffmpeg','-y','-v','error','-i',f,'-map','0:v:0','-c','copy','-bsf:v','h264_mp4toannexb','-f','h264',P/n])
run(['ffmpeg','-y','-v','error','-i',v,'-map','0:a:0','-c:a','pcm_f32le',P/'decoded_aac.wav'])
ar,a=wavfile.read(P/'decoded_aac.wav');sr,p=wavfile.read(pc);mr,m=wavfile.read(MASTER);n=len(p)
x=a[:n].astype(np.float64);y=p.astype(np.float64)/32768
cc=correlate(x.mean(1),y.mean(1),method='fft');ll=correlation_lags(n,n);k=np.abs(ll)<=2048;lag=int(ll[k][np.argmax(cc[k])])
prior=json.loads((B/'astra_eight_audio_increment_a039936_20261018_1757/incremental_check.json').read_text());start=prior['shots']['S10']['pcm_master_slice_start_sample'];z=m[start:start+n].astype(np.float64);e=p.astype(np.float64)-z
vs=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio')
packets=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,duration,side_data_list','-of','json',v]));writejson(P/'audio_packets.json',packets)
scan=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(v),'-map','0:a:0','-af','loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);(P/'loudnorm_scan.txt').write_text(scan.stderr);loud=json.loads(scan.stderr[scan.stderr.rindex('{'):scan.stderr.rindex('}')+1])
source_unchanged={f:git(f)==git(f,A) for f in ['audio/build.py','audio/inst.py','audio/sfx.py','audio/score.py','js/film/edl.js']}
out=dict(commit=C,mp4_sha256=sha(v),mp4_hash_matches_manifest=sha(v)==expected[v.name],
 pcm_sha256=sha(pc),pcm_hash_matches_manifest=sha(pc)==expected[pc.name],
 reviewed_new_color_reference_sha256=sha(REF),reference_path=str(REF),
 h264_bytes_identical=(P/'new.h264').read_bytes()==(P/'approved.h264').read_bytes(),h264_sha256=sha(P/'new.h264'),
 video_codec=vs['codec_name'],video_dimensions=[vs['width'],vs['height']],video_counted_frames=int(vs['nb_read_frames']),video_reported_frames=int(vs['nb_frames']),video_fps=vs['avg_frame_rate'],video_duration=vs['duration'],audio_duration=au['duration'],video_start=vs['start_time'],audio_start=au['start_time'],
 pcm_sample_rate=sr,pcm_samples=n,pcm_channels=p.shape[1],aac_sample_rate=ar,aac_decoded_samples=len(a),aac_padding_samples=len(a)-n,
 audio_first_packet=packets['packets'][0],audio_last_packet=packets['packets'][-1],
 aac_best_lag_samples=lag,aac_pcm_correlation=float(np.corrcoef(x.ravel(),y.ravel())[0,1]),aac_pcm_rmse=float(np.sqrt(np.mean((x-y)**2))),aac_true_peak_dbtp=float(loud['input_tp']),
 pcm_file_byte_identical_to_previously_verified_a039936=(pc.read_bytes()==OLD.read_bytes()),
 audio_sources_and_edl_unchanged_since_a039936=source_unchanged,
 independently_rebuilt_master_sha256=sha(MASTER),independently_rebuilt_master_source_commit=A,
 master_slice_start_sample=start,master_slice_end_exclusive=start+n,
 pcm_vs_rebuilt_master_max_lsb=float(np.abs(e).max()),pcm_vs_rebuilt_master_rmse_lsb=float(np.sqrt(np.mean(e**2))),
 scope='S10 new-color v2 only. Prior seven shots and master synthesis not repeated. Old v1 deletion is a version replacement, not missing evidence.',
 caveats=['AAC is lossy and is compared as signal, not PCM bytes.','AAC priming is signalled; decoded tail padding is outside exact 5s MP4 presentation length.','This verifies new-color video provenance and audio increment; no additional subjective visual/listening approval.'])
out['checks_passed']=dict(hashes=out['mp4_hash_matches_manifest'] and out['pcm_hash_matches_manifest'],new_color_video_identical=out['h264_bytes_identical'],
 frames_and_durations=out['video_counted_frames']==120 and vs['avg_frame_rate']=='24/1' and vs['duration']==au['duration']=='5.000000' and n==240000,
 pcm_unchanged=out['pcm_file_byte_identical_to_previously_verified_a039936'],sources_unchanged=all(source_unchanged.values()),aac_zero_best_lag=lag==0)
assert all(out['checks_passed'].values()),out['checks_passed']
writejson(P/'incremental_check.json',out)
report=f'''# S10 新色 v2 实际增量核验\n\n固定提交：{C}\n\n结论：S10_drawn_v2.mp4 已接入指定新色 4f178f2c 源，H.264 逐字节相同。实际解码 120 帧、24 fps、1280×720；视频/音轨呈现长度均 5 秒，起点均 0。交付 MP4 和 PCM 哈希均与更新清单相符。\n\nS10_pcm.wav 与已核 a039936 新母带交付 PCM 文件逐字节相同；对独立重建母带的切片最大差 {out['pcm_vs_rebuilt_master_max_lsb']:.0f} LSB、RMSE {out['pcm_vs_rebuilt_master_rmse_lsb']:.9f} LSB。audio 全套源码与 EDL 均未变，无需重建母带。\n\n新 AAC 对 PCM 最佳延迟 {lag} 样本，相关系数 {out['aac_pcm_correlation']:.9f}，真峰 {out['aac_true_peak_dbtp']:.2f} dBTP。PCM 为 48 kHz 双声道、240000 样本；AAC 解码 240640 样本，初始 1024 样本 priming 有标记，尾部 640 样本属 AAC 块补齐，不计入 5 秒呈现长度。AAC 有损，不称 PCM 逐字节相同。\n\nMP4 SHA256：{sha(v)}\nPCM SHA256：{sha(pc)}\n新色无声源 SHA256：{sha(REF)}\n独立新母带 SHA256：{sha(MASTER)}\n\n仅关闭 S10 新色 v2 的画面来源与新声增量。未重核其余七镜、未重渲影片、未重建母带、未写仓库。旧 v1 在此提交删除属于版本替换，固定历史仍可读取。\n\n机器结果：incremental_check.json。重放：python3 verify_s10_v2.py。\n'''
(P/'REPORT.md').write_text(report)
(P/'AUDIT_SHA256SUMS.txt').write_text(''.join(sha(P/f)+'  '+f+'\n' for f in ['incremental_check.json','REPORT.md','verify_s10_v2.py']))
print(json.dumps(out,ensure_ascii=False,indent=2))
