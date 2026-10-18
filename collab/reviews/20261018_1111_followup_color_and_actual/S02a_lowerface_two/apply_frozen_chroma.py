from pathlib import Path
import argparse,json,hashlib
from PIL import Image
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--base-dir',type=Path);a=p.parse_args();R=Path(__file__).resolve().parent;D=a.base_dir or R/'source_copies';O=R/'replayed';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
for s in json.loads((R/'candidate_validation.json').read_text())['assets']:
 n=s['name'];src=D/f'{n}.png';assert sha(src)==s['base_sha256'],'Base SHA mismatch: use the prior semantic neck/collar candidate, not the raw original.'
 im=np.array(Image.open(src).convert('RGBA'));out=im.copy();f=np.load(R/'masks'/f'{n}__exact_chroma_application.npz');x0,y0,x1,y1=f['xyxy'];rgb=im[y0:y1,x0:x1,:3].astype(float);Y=rgb@np.array([.2126,.7152,.0722]);tgt=Y[:,:,None]+f['target_chroma'];out[y0:y1,x0:x1,:3]=np.round(rgb+(tgt-rgb)*f['weight'][:,:,None]).clip(0,255).astype('uint8');dest=O/f'{n}__lowerface_cool_candidate.png';Image.fromarray(out).save(dest);assert sha(dest)==s['output_sha256'],'Replay mismatch';checks.append({'name':n,'exact_frozen_replay_sha_identical':True})
(R/'frozen_replay_check.json').write_text(json.dumps(checks,indent=2));print(checks)
