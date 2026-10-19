#!/usr/bin/env python3
"""Read-only archive and actual full11f decode verification."""
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((R/'package_manifest.json').read_text())
for row in manifest['files']:assert sha(R/row['path'])==row['sha256'],row['path']
for row in json.loads((R/'sources/source_manifest.json').read_text())['files']:assert sha(R/'sources'/row['path'])==row['sha256']
checks=json.loads((R/'exposure/actual_decode_checks.json').read_text());seq=[84]*6+[90]*5
assert checks['sequence']==seq and checks['new_generation_calls']==0
for tone,entry in checks['backgrounds'].items():
    video=R/entry['video'];assert sha(video)==entry['sha256']
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames','-of','json',str(video)]))
    assert len(probe['streams'])==1
    stream=probe['streams'][0];assert (stream['width'],stream['height'],stream['r_frame_rate'],stream['nb_frames'])==(1280,720,'24/1','11')
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'])
    frames=np.frombuffer(data,np.uint8).reshape((-1,720,1280,3));assert len(frames)==11
    refs={f:np.asarray(Image.open(R/'exposure'/tone/f'F{f:03d}_reference.png').convert('RGB')).astype(float) for f in [84,90]}
    for i,frame in enumerate(frames):
        errors={f:float(np.abs(frame.astype(float)-ref).mean())for f,ref in refs.items()}
        assert min(errors,key=errors.get)==seq[i]
        assert abs(errors[seq[i]]-entry['decoded_frames'][i]['RGB_MAE'])<1e-10
        if i in [0,5,6,7,10]:assert np.array_equal(frame,np.asarray(Image.open(R/'exposure'/tone/f'actual_decoded_{i:02d}.png')))
print('PASS: full package/source hashes; both11f streams; all22 actual decoded source states; requested actual PNGs match video.')
