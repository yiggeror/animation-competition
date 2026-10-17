from pathlib import Path
import subprocess,json
import numpy as np
from scipy.io import wavfile
B=Path(__file__).resolve().parent;I=B.parents[2]/'batch1_v2_actual';mp4=I/'batch1_S01_S03_S04_1080p.mp4'
raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(mp4),'-map','0:a:0','-c:a','pcm_f32le','-f','f32le','pipe:1']),dtype='<f4').reshape(-1,2)
sr,at=wavfile.read(B/'decoded_pts_f32.wav')
rows=[]
for label,first,cut in [('S03',564,12),('S04',847,18)]:
 x=raw[(first+1)*1024:(first+1)*1024+4800];y=at[cut*sr+1024:cut*sr+1024+4800]
 eq=np.all(x==y,axis=1);bad=np.flatnonzero(~eq);last_bad=int(bad[-1]) if len(bad) else -1
 ranges=[];prev=bool(eq[0]);start=0
 for j,e in enumerate(eq[1:],1):
  if bool(e)!=prev:ranges.append([start,j,prev]);start=j;prev=bool(e)
 ranges.append([start,len(eq),prev])
 # Match 128-sample snippets directly to nearby raw decoder samples.
 maps=[]
 for off in [-1024,-512,0,128,256,384,512,640,768,896,1024,1536]:
  ya=cut*sr+1024+off;snippet=at[ya:ya+128];center=(first+1)*1024+off
  lo=center-4096;hi=center+4096
  candidates=np.flatnonzero(np.all(raw[lo:hi]==snippet[0],axis=1))+lo
  exact=[int(k) for k in candidates if np.array_equal(raw[k:k+128],snippet)]
  maps.append({'aligned_content_offset_samples':off,'exact_raw_sample_start_count':len(exact),'exact_raw_sample_starts':exact[:8],'exact_raw_sample_start_min_max':[min(exact),max(exact)] if exact else [],'raw_expected_sample_start':center,'raw_minus_expected_samples':[k-center for k in exact[:8]]})
 rows.append({'shot':label,'cut_seconds':cut,'mismatch_content_head_samples':last_bad+1,'head_duration_ms':(last_bad+1)/48,'equality_ranges_in_first_100ms':ranges,'mapping':maps,'head_previous_tail_samples':last_bad,'head_previous_tail_bitwise_match':bool(np.array_equal(y[:last_bad],raw[(first+1)*1024-(1536 if label=='S03' else 1792):(first+1)*1024-(1536 if label=='S03' else 1792)+last_bad])),'last_mismatch_sample_matches_priming_last':bool(np.array_equal(y[last_bad],raw[first*1024+1023]))})
r={'method':'Bitwise float32 sample comparisons between continuous decoder output and explicit hard PTS-compensated aresample output. Content origin defined by independently verified packet grouping and 1024-sample priming.','segments':rows}
(B/'pts_content_mapping.json').write_text(json.dumps(r,indent=2));print([(v['shot'],v['mismatch_content_head_samples'],v['head_previous_tail_bitwise_match'],v['last_mismatch_sample_matches_priming_last']) for v in rows])
