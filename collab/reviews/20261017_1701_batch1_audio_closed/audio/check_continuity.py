from pathlib import Path
import subprocess,json,hashlib,wave,sys
from collections import defaultdict
import numpy as np
import scipy
from scipy.io import wavfile
A=Path(__file__).resolve().parent;B=A.parent;I=B.parents[1]/'batch1_v3_actual';mp4=I/'batch1_S01_S03_S04_1080p.mp4'
pack=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a','-show_packets','-show_entries','packet=pts,dts,duration,data_hash,side_data_list','-show_data_hash','sha256','-of','json',str(mp4)]))['packets']
raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(mp4),'-map','0:a:0','-c:a','pcm_f32le','-f','f32le','pipe:1']),dtype='<f4').reshape(-1,2)
sr,aligned=wavfile.read(A/'decoded_pts_f32.wav');assert sr==48000
hashes=defaultdict(list)
for i,p in enumerate(pack):hashes[p['data_hash']].append(i)
r={'sample_rate':sr,'packet_count':len(pack),'nonmonotonic_pts':[(i,p['pts'],q['pts']) for i,(p,q) in enumerate(zip(pack,pack[1:])) if q['pts']<=p['pts']],'nonmonotonic_dts':[(i,p['dts'],q['dts']) for i,(p,q) in enumerate(zip(pack,pack[1:])) if q['dts']<=p['dts']],'packet_timeline_discontinuities':[(i,p['pts']+p['duration']-q['pts']) for i,(p,q) in enumerate(zip(pack,pack[1:])) if p['pts']+p['duration']!=q['pts']],'duplicate_payload_groups':{h:ix for h,ix in hashes.items() if len(ix)>1},'initial_packet':pack[0],'last_packet':pack[-1],'decoded_frames':len(raw),'pts_compensated_frames':len(aligned),'raw_vs_pts_whole_array_bitwise_equal':bool(np.array_equal(raw,aligned)),'raw_f32le_pcm_sha256':hashlib.sha256(raw.tobytes()).hexdigest(),'pts_f32le_pcm_sha256':hashlib.sha256(aligned.tobytes()).hexdigest(),'cut_windows':[]}
for cut in [12,18]:
 lo=int((cut-.1)*sr);hi=int((cut+.1)*sr);r['cut_windows'].append({'cut_seconds':cut,'interval_seconds':[cut-.1,cut+.1],'raw_vs_pts_bitwise_equal':bool(np.array_equal(raw[lo:hi],aligned[lo:hi])),'different_sample_values':int(np.count_nonzero(raw[lo:hi]!=aligned[lo:hi])),'nearby_packets':[p for p in pack if (cut-.04)*sr<=p['pts']<=(cut+.04)*sr]})
r['environment']={'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],'node':subprocess.check_output(['node','--version'],text=True).strip()}
r['independent_build_outputs']={}
for p in (B/'isolated/build/audio').glob('*.wav'):
 with wave.open(str(p)) as f: rate=f.getframerate();n=f.getnframes();channels=f.getnchannels();width=f.getsampwidth();pcm=f.readframes(n)
 r['independent_build_outputs'][p.name]={'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'sample_rate':rate,'channels':channels,'sample_width_bytes':width,'frames':n,'duration_seconds':n/rate}
(A/'continuity.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in r.items() if k not in ['cut_windows','independent_build_outputs']},ensure_ascii=False,indent=2));print('New master',r['independent_build_outputs']['film_mix_norm.wav'])
