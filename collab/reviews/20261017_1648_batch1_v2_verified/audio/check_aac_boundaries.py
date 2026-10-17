from pathlib import Path
import subprocess,json,hashlib
from collections import defaultdict
import numpy as np
from scipy.io import wavfile
B=Path(__file__).resolve().parent;I=B.parents[2]/'batch1_v2_actual';mp4=I/'batch1_S01_S03_S04_1080p.mp4'
pack=json.loads((B/'audio_packets.json').read_text())['packets'];pts=json.loads((B/'audio_pts.json').read_text())['frames']
adts=subprocess.check_output(['ffmpeg','-v','error','-i',str(mp4),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
frames=[];pos=0
while pos<len(adts):
 h=adts[pos:pos+7];assert h[0]==255 and h[1]&240==240
 n=((h[3]&3)<<11)|(h[4]<<3)|(h[5]>>5);hdr=7 if h[1]&1 else 9
 frame=adts[pos:pos+n];assert len(frame)==n
 assert 'SHA256:'+hashlib.sha256(frame[hdr:]).hexdigest()==pack[len(frames)]['data_hash']
 frames.append(frame);pos+=n
assert len(frames)==len(pack)==1223
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(mp4),'-map','0:a:0','-c:a','pcm_f32le','-f','f32le','pipe:1']);raw=np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(np.float64)
sr,pcm=wavfile.read(I/'film_mix_norm_8d36fab8_0-30s.wav');pcm=pcm.astype(np.float64)/32768
_,aligned=wavfile.read(B/'decoded_pts_f32.wav');aligned=aligned.astype(np.float64)
def metric(a,b):
 g=float(np.sum(a*b)/np.sum(a*a));err=b-g*a
 rms=lambda v:float(np.sqrt(np.mean(v*v)))
 return {'correlation':float(np.corrcoef(a.ravel(),b.ravel())[0,1]),'gain_ratio':g,'snr_db':float(20*np.log10(rms(g*a)/max(rms(err),1e-30))),'rms_reference_dbfs':float(20*np.log10(rms(a))),'rms_observed_dbfs':float(20*np.log10(max(rms(b),1e-30)))}
results=[]
for label,first,last,ms,dur,es in [('S01',0,564,0,12,0),('S03',564,847,16,6,12),('S04',847,1223,22,8,18)]:
 decoded=subprocess.check_output(['ffmpeg','-v','error','-f','aac','-i','pipe:0','-c:a','pcm_f32le','-f','f32le','pipe:1'],input=b''.join(frames[first:last]));x=np.frombuffer(decoded,dtype='<f4').reshape(-1,2).astype(np.float64)
 assert len(x)==(last-first)*1024
 ref=pcm[ms*sr:(ms+dur)*sr];ind=x[1024:1024+len(ref)];seq=raw[(first+1)*1024:(first+1)*1024+len(ref)];at=aligned[es*sr+1024:(es+dur)*sr+1024]
 r={'shot':label,'aac_packet_range':[first,last],'decoded_frame_count':len(x),'source_samples':len(ref),'samples_beyond_leading_priming_and_source':len(x)-1024-len(ref),'full_independent_decode_vs_reference':metric(ref,ind),'full_pts_corrected_concat_vs_reference':metric(ref,at),'first_windows':[]}
 for start,end in [(0,.010),(0,.025),(.025,.100),(.100,.300)]:
  a=round(start*sr);z=round(end*sr);r['first_windows'].append({'local_seconds':[start,end],'independent_decode':metric(ref[a:z],ind[a:z]),'continuous_decode_no_pts':metric(ref[a:z],seq[a:z]),'pts_corrected_concat':metric(ref[a:z],at[a:z]),'independent_vs_continuous_pcm_max_abs':float(np.max(abs(ind[a:z]-seq[a:z])))})
 results.append(r)
hashes=defaultdict(list)
for i,p in enumerate(pack):hashes[p['data_hash']].append(i)
dups={h:ix for h,ix in hashes.items() if len(ix)>1}
r={'method':'AAC packets copied into ADTS without re-encoding; each payload hash checked against ffprobe. Source segment packet groups independently decoded and compared with continuous/PTS-corrected decoding.','packet_count':len(pack),'all_adts_payload_hashes_match':True,'nonmonotonic_dts':[(i,p['dts'],q['dts']) for i,(p,q) in enumerate(zip(pack,pack[1:])) if q['dts']<=p['dts']],'nonmonotonic_pts':[(i,p['pts'],q['pts']) for i,(p,q) in enumerate(zip(pack,pack[1:])) if q['pts']<=p['pts']],'duplicate_payload_groups':dups,'segments':results}
(B/'aac_boundary_diagnostics.json').write_text(json.dumps(r,indent=2))
print('DTS/PTS monotonic:',not r['nonmonotonic_dts'],not r['nonmonotonic_pts']);print('Duplicate packet payloads',dups)
for x in results:
 print(x['shot'],'tail padding samples',x['samples_beyond_leading_priming_and_source'])
 for w in x['first_windows']:print(w['local_seconds'],'independent corr',w['independent_decode']['correlation'],'continuous',w['continuous_decode_no_pts']['correlation'],'PTS',w['pts_corrected_concat']['correlation'],'ind/seq maxdiff',w['independent_vs_continuous_pcm_max_abs'])
