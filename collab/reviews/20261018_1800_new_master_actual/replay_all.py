#!/usr/bin/env python3
"""Replay actual a039936 audio rebuild and all eight media comparisons.
Only these two isolated audit directories are written. No Git checkout or external mutation.
Requires the existing local git object clone and designated reviewed media references.
"""
from pathlib import Path
import subprocess,sys,json,hashlib
import numpy,scipy
P=Path(__file__).resolve().parent;BASE=P.parent
B=BASE/'astra_audio_rebuild_actual_a039936_20261018_1756';B.mkdir(exist_ok=True)
REPO=BASE/'laidian_astra_recovered_20261018_0527'
C='a039936fa0286ed6a64eb2874a8140ff8b290161';OLD='ca7be38d85b64345c6d374f981b798974c53d423'
files={}
for f in ['audio/build.py','audio/inst.py','audio/sfx.py','audio/score.py','js/film/edl.js','package.json']:
 b=subprocess.check_output(['git','-C',str(REPO),'show',C+':'+f]);q=B/f;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 files[f]=dict(sha256=hashlib.sha256(b).hexdigest(),git_blob=subprocess.check_output(['git','-C',str(REPO),'rev-parse',C+':'+f]).decode().strip())
(B/'source_manifest.json').write_text(json.dumps(dict(commit=C,files=files,numpy=numpy.__version__,scipy=scipy.__version__),indent=2))
for name in ['S02a_drawn_v6.mp4','S03_drawn_v3.mp4']:
 q=P/'prior_ca7be38d'/name;q.parent.mkdir(exist_ok=True);q.write_bytes(subprocess.check_output(['git','-C',str(REPO),'show',OLD+':collab/reviews/20261018_opening_drawn_wip/'+name]))
with (B/'rebuild.log').open('w') as f:
 subprocess.run([sys.executable,'-u','audio/build.py'],cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
for script,log in [('verify_eight.py','verify.log'),('compare_rebuilt_master.py','master_compare.log')]:
 with (P/log).open('w') as f:
  subprocess.run([sys.executable,str(P/script)],stdout=f,stderr=subprocess.STDOUT,check=True)
print(P/'incremental_check.json')
