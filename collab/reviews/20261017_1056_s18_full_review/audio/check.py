from pathlib import Path
import wave,json,hashlib
import numpy as np
from scipy.signal import correlate
from PIL import Image,ImageDraw,ImageFont
p=Path('/tmp/laidian-audit-s18-full-fda4926-audio');master=Path('/tmp/laidian-audio-final-no-extra-click/film_mix_norm.wav');sr=48000
y=np.fromfile(p/'decoded_audio.f32le',dtype='<f4').reshape(-1,2).astype(np.float64)
with wave.open(str(master),'rb') as w:
 w.setpos(int(114.5*sr));x=np.frombuffer(w.readframes(int(4*sr)),dtype='<i2').reshape(-1,2).astype(np.float64)/32768
# Interior comparison avoids priming/tail samples, then recover absolute start from the best lag.
qy=y[4800:139200];n=len(qy);num=sum(correlate(x[:,c],qy[:,c],mode='valid',method='fft') for c in range(2));cs=np.r_[0,np.cumsum(np.sum(x*x,axis=1))];rho=num/np.sqrt(np.maximum((cs[n:]-cs[:-n])*np.sum(qy*qy),1e-30));best=int(np.argmax(rho));equiv_master_start=114.5+best/sr-4800/sr;lead=round((115-equiv_master_start)*sr)
z=x[24000:24000+144000];a=y[lead:lead+144000];gain=np.sum(a*z)/np.sum(z*z);cor=np.sum(a*z)/np.sqrt(np.sum(a*a)*np.sum(z*z))
v=json.loads((p/'video_frames.json').read_text())['frames'];vp=[float(q['best_effort_timestamp_time']) for q in v]
lg=(p/'loudnorm.log').read_text();l=json.loads(lg[lg.rfind('{'):lg.rfind('}')+1])
r={'decoded_samples':len(y),'decoded_seconds':len(y)/sr,'interior_best_correlation':float(rho[best]),'audio_master_equivalent_at_container_t0':equiv_master_start,'leading_decoded_samples_before_master_115':lead,'content_3s_comparison_correlation':float(cor),'content_fitted_gain':float(gain),'content_fitted_gain_db':float(20*np.log10(gain)),'content_clip_samples_abs_ge_1':int(np.count_nonzero(np.abs(a)>=1)),'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'loudnorm_input':l,'video_frames':len(v),'F0_PTS':vp[0],'F15_PTS':vp[15],'F71_PTS':vp[71],'video_frame_interval':1/24,'audio_PU_expected_container_time':lead/sr+.6,'F15_minus_audio_PU_ms':1000*(vp[15]-(lead/sr+.6)),'videoF0_minus_audio_content_start_ms':1000*(vp[0]-lead/sr),'method':'Actual decoded AAC compared to original 6980 WAV by normalized stereo correlation; interior search avoids priming. Source cue +0.6 converted using measured content offset; not a subjective audible-transient annotation.'}
(p/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
ids=[0,14,15,18,24,71];im=Image.new('RGB',(960*2,566*3),(245,245,245));d=ImageDraw.Draw(im)
for i,f in enumerate(ids):
 x0=(i%2)*960;y0=(i//2)*566;im.paste(Image.open(p/'frames'/f'{f:05d}.png'),(x0,y0+26));d.text((x0+8,y0+4),f'F{f} content={f/24:.6f}s PTS={vp[f]:.6f}',font=font,fill='black')
im.save(p/'actual_keys_subtitles.jpg',quality=94)
# All decoded-frame hashes bind the inspected evidence to the actual new MP4.
(p/'frame_hashes.json').write_text(json.dumps([{'f':i,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for i,q in enumerate(sorted((p/'frames').glob('*.png')))],indent=2)+'\n')
