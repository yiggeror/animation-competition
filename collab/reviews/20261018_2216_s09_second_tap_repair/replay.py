#!/usr/bin/env python3
"""Read fixed git objects; replay accepted source-only F052 and optional10f clips.
No network, native generation, checkout, source mutation, or repo writes.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import argparse,subprocess,hashlib,json,io
P=Path(__file__).resolve().parent
EXPECTED='a107f71d994c3302884eb3ebba0e8e4726b89bd5e36c2f8a8fa022f44ddfbb42'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--output',required=True);ap.add_argument('--encode',action='store_true');args=ap.parse_args();O=Path(args.output);O.mkdir(parents=True,exist_ok=True)
 refs=json.loads((P/'SOURCE_INDEX.json').read_text())['sources'];data={}
 for role,s in refs.items():
  if not s['required_for_replay']:continue
  b=subprocess.check_output(['git','-C',args.repo,'show',s['commit']+':'+s['path']]);assert sha(b)==s['sha256'],role;data[role]=b
 def arr(role):return np.array(Image.open(io.BytesIO(data[role])).convert('RGBA'))
 def smask(role):return np.array(Image.open(io.BytesIO(data[role])).convert('L'))>0
 def mask(n):return np.array(Image.open(P/'masks'/n).convert('L'))>0
 base=arr('preposition');unit=arr('rigid_hand_torch');raw=arr('call02_aligned');n0=np.zeros_like(base);n3=np.zeros_like(base);n0[500:860,620:1160]=raw;n3[500:860,623:1163]=raw
 back=mask('native_back_layer_dx0_mask.png');fg=mask('native_complete_near_band_dx3_mask.png');band=mask('complete_band_geometry.png');domain=mask('native_semantic_adoption_mask.png');release=smask('wrist_release90');um=unit[:,:,3]>0
 out=base.copy();out[back]=n0[back];out[fg]=n3[fg];out[um]=0;out[um&band]=n3[um&band];uf=unit.copy();uf[release]=0
 composite=Image.fromarray(out);composite.alpha_composite(Image.fromarray(uf));out=np.array(composite);core=(unit[:,:,3]>=240)&~release;out[core]=unit[core]
 fp=O/'F052_rgba_LOCKED_replayed.png';Image.fromarray(out).save(fp);assert sha(fp.read_bytes())==EXPECTED,'ReplayedPNG mismatch'
 accepted=P/'candidate/F052_rgba_LOCKED.png';assert sha(accepted.read_bytes())==EXPECTED
 for role,f in [('locked048',48),('locked042_as056',56)]: (O/f'F{f:03d}_exact_source.png').write_bytes(data[role])
 palm=smask('fixed_palm_mask');hard=palm|smask('head_mask')|smask('waist_mask');assert not np.any(out[hard]!=base[hard]);assert not np.any(out[core]!=unit[core]);diff=np.any(out!=base,axis=2);assert not (diff&~domain&~((unit[:,:,3]>0)&(unit[:,:,3]<240))).any()
 report={'status':'REPLAY_VERIFIED_SOURCE_EXACT','F052_sha256':EXPECTED,'F056_sha256':sha(data['locked042_as056']),'protected_hand_torch_core_pixels':int(core.sum()),'protected_hand_torch_core_differences':0,'fixed_palm_and_head_waist_differences':0,'outside_donor_or_genuine_AA_differences':0,'native_generation_calls':0,'exposure':{}}
 # Actual silhouette check from accepted final PNG, not nominal arithmetic.
 mother=arr('locked048');frames={48:mother,52:out,56:arr('locked042_as056')};s=.6297229219143576
 for f,v in frames.items():
  gaps=[]
  for x in range(1093,1174):
   py=np.where((mother[695:790,x,3]>=128)&palm[695:790,x])[0]+695
   if len(py):
    p=int(py.min());tail=np.where(v[550:p,x,3]>=128)[0]+550
    if len(tail):gaps.append(p-int(tail.max())-1)
  gap=min(gaps);assert gap=={48:91,52:37,56:0}[f];report.setdefault('actual_gap_native',{})[f]=gap
 if args.encode:
  tx,ty=241.2216624685139,83.47607052896726;sequence=[48]*4+[52]*4+[56]*2
  for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
   D=O/tag;D.mkdir(exist_ok=True);renders={}
   for f,a in frames.items():
    reg=Image.fromarray(a).transform((1536,864),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));bg=Image.new('RGBA',reg.size,col);bg.alpha_composite(reg);renders[f]=np.array(bg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB'))
   for i,f in enumerate(sequence):Image.fromarray(renders[f]).save(D/f'input_{i:02d}.png')
   video=D/f'S09_F048x4_F052x4_F056x2_{tag}_24fps.mp4';subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(D/'input_%02d.png'),'-frames:v','10','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]));stream=probe['streams'][0];assert(stream['width'],stream['height'],stream['r_frame_rate'],stream['nb_frames'])==(1280,720,'24/1','10')
   rb=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);decoded=np.frombuffer(rb,np.uint8).reshape((-1,720,1280,3));assert len(decoded)==10;scores=[]
   for i,a in enumerate(decoded):
    errors={f:float(np.abs(a.astype(float)-v.astype(float)).mean())for f,v in renders.items()};assert min(errors,key=errors.get)==sequence[i];scores.append({'frame':i,'expected':sequence[i],'nearest':min(errors,key=errors.get),'RGB_MAE':errors[sequence[i]]})
   report['exposure'][tag]={'sha256':sha(video.read_bytes()),'probe':probe,'all_decoded_frames':scores}
 (O/'REPLAY_VERIFICATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
