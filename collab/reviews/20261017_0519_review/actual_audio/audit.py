from pathlib import Path
import subprocess,json,hashlib,concurrent.futures,numpy as np
from scipy.io import wavfile
OUT=Path('/tmp/laidian-audit-delivery-1a90-audio'); REPO=Path('/workspace/animation-competition'); COMMIT='d1f3fbc0aa0d5dca15d2fee03c6cdc135bc0273d'
NAMES=['s02_phone','s05_phone','s06_socket','s08_lamp','s09_torch','s10_beam','s12_box','s20_backstage','s25_dog','s28_power_on']
for d in ['input','decoded_audio','logs','source']:(OUT/d).mkdir(exist_ok=True)
def gitbytes(path,commit=COMMIT):return subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=REPO)
def audit(name):
 rel=f'renders/checkpoint2/{name}_preview.mp4'; data=gitbytes(rel); file=OUT/'input'/f'{name}_preview.mp4';file.write_bytes(data)
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]));a=[s for s in p['streams'] if s['codec_type']=='audio'];v=[s for s in p['streams'] if s['codec_type']=='video'];r={'name':name,'path':rel,'fixed_copy':str(file),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'probe':p,'video':[{k:s.get(k) for k in ['codec_name','width','height','r_frame_rate','avg_frame_rate','duration','start_time','nb_frames']} for s in v],'audio':[{k:s.get(k) for k in ['codec_name','sample_rate','channels','channel_layout','duration','start_time','bit_rate']} for s in a]}
 if a:
  dec=subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-f','f32le','-c:a','pcm_f32le','-']);x=np.frombuffer(dec,dtype='<f4').reshape(-1,a[0]['channels']);sr=int(a[0]['sample_rate']);wav=OUT/'decoded_audio'/f'{name}.wav';wavfile.write(wav,sr,x)
  ff=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(file),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True);(OUT/'logs'/f'{name}_loudnorm.log').write_text(ff.stderr);start=ff.stderr.rfind('{');end=ff.stderr.rfind('}')
  st=json.loads(ff.stderr[start:end+1]) if ff.returncode==0 else {'error':ff.returncode}
  absx=np.abs(x);rms=np.sqrt(np.mean(x.astype(np.float64)**2,axis=0));peak=float(absx.max());r['decoded']={'path':str(wav),'format':'IEEE float32 WAV decoded from delivered AAC; not original master/stem','sample_rate':sr,'channels':a[0]['channels'],'samples_per_channel':len(x),'duration_s':len(x)/sr,'rms_per_channel':rms.tolist(),'rms_dbfs_per_channel':(20*np.log10(rms)).tolist(),'mean_dc_per_channel':np.mean(x.astype(np.float64),axis=0).tolist(),'peak_sample_linear':peak,'peak_sample_dbfs':float(20*np.log10(peak)),'all_zero':bool(np.all(x==0)),'fraction_samples_abs_gt_1e_5':float(np.mean(absx>1e-5)),'samples_abs_ge_1':int(np.count_nonzero(absx>=1)),'loudnorm_input_integrated_lufs':st.get('input_i'),'loudnorm_input_true_peak_dbtp':st.get('input_tp'),'loudnorm_input_lra_lu':st.get('input_lra'),'loudnorm_full_json':st}
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rows=list(ex.map(audit,NAMES))
for path in ['js/film/edl.js','js/code/s05.js','js/code/phone_img.js','js/code/phone.js','audio/build.py']:
 f=OUT/'source'/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(gitbytes(path))
(OUT/'source/package.json').write_text('{"type":"module"}\n')
oldrel='renders/checkpoint2/film_preview_v1.mp4';current=gitbytes(oldrel);old_hash='51e5b1d93c83b2ea484973ba9030f2f5dc6728e8a8ea28e6141fa8c2bbba51af'
manifest={'commit':COMMIT,'delivery_commit':'1a90bb7','method':'Fixed-commit git-show media, ffprobe, FFmpeg decode float32, actual loudnorm input measurements only; no listening or audio synthesis','items':rows,'old_full_film':{'path':oldrel,'sha256':hashlib.sha256(current).hexdigest(),'hash_matches_previously_audited_5b2504f':hashlib.sha256(current).hexdigest()==old_hash},'claimed_master_sha256':'7438aa3c51e07925acbc4b9ed5717c66de3c135cbcd7f9775ea2cca9d0796e65','master_received':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['name'],r['video'],r['audio'],{k:r['decoded'][k] for k in ['duration_s','all_zero','loudnorm_input_integrated_lufs','loudnorm_input_true_peak_dbtp','peak_sample_dbfs','mean_dc_per_channel']})
print(manifest['old_full_film'])
