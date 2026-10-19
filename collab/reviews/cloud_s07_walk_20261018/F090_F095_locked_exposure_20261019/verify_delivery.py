#!/usr/bin/env python3
"""Read-only complete source/hash and full10f actual decode verification."""
from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,numpy as np
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in json.loads((R/'package_manifest.json').read_text())['files']:assert sha(R/row['path'])==row['sha256'],row['path']
for row in json.loads((R/'sources/source_manifest.json').read_text())['files']:
 assert sha(R/'sources'/row['snapshot'])==row['sha256'];assert subprocess.check_output(['git','show',f"{row['source_commit']}:{row['source_path']}"])==(R/'sources'/row['snapshot']).read_bytes()
report=json.loads((R/'exposure/actual_decode_checks.json').read_text());seq=[90]*5+[95]*5;assert report['sequence']==seq and report['new_generation_calls']==0
for tone,entry in report['backgrounds'].items():
 video=R/entry['video'];assert sha(video)==entry['sha256'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames','-of','json',str(video)]));assert len(probe['streams'])==1;st=probe['streams'][0];assert(st['width'],st['height'],st['r_frame_rate'],st['nb_frames'])==(1280,720,'24/1','10')
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);frames=np.frombuffer(raw,np.uint8).reshape((-1,720,1280,3));assert len(frames)==10;refs={f:np.asarray(Image.open(R/'exposure'/tone/f'F{f:03d}_reference.png').convert('RGB')).astype(float)for f in [90,95]}
 for i,im in enumerate(frames):
  err={f:float(np.abs(im.astype(float)-ref).mean())for f,ref in refs.items()};assert min(err,key=err.get)==seq[i];assert abs(err[seq[i]]-entry['decoded_frames'][i]['RGB_MAE'])<1e-10
  if i in [0,4,5,6,9]:assert np.array_equal(im,np.asarray(Image.open(R/'exposure'/tone/f'actual_decoded_{i:02d}.png')))
print('PASS: two locked git-byte-exact sources;full package hashes;10f/24fps/noaudio both streams;all20 actual source states;requested actual frames0/4/5/6/9 match video.')
