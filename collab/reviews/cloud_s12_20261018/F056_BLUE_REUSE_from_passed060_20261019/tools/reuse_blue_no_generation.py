"""Exact authorized same-coordinate pixel reuse. Does not render or call imagegen.
If outputs exist, verify rather than overwrite. No other state is modified.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parents[1]
OLD=ROOT/'F056_hypothenar_actual_call01_20261019'
PRE=ROOT/'F060_forearm_ink_RGB_cleanup_20261019'
DONOR=ROOT/'BLUE_sleeve_root_actual_call01_20261019/F060'
BLUE=ROOT/'BLUE_sleeve_root_actual_call01_20261019'
arr=lambda p:np.asarray(Image.open(p).convert('RGBA'))
b=arr(OLD/'candidate/F056.png'); p=arr(PRE/'candidate/F060.png'); d=arr(DONOR/'candidate/F060.png')
m=np.asarray(Image.open(BLUE/'masks/APPROVED1868_BLUE_EDGE_ADOPTION_MASK.png').convert('L'))>0
assert int(m.sum())==1868
assert np.array_equal(b[885:985,455:625],p[885:985,455:625])
assert np.array_equal(b[m],p[m])
n=b.copy();n[m]=d[m]
assert np.count_nonzero(np.any(n!=b,axis=2))==1531
assert np.array_equal(n[~m],b[~m])
fg=arr(OLD/'layers/F056_FG_true_front_fingers.png')
bg=n.copy();bg[fg[:,:,3]>0]=0
for relative,a in [('candidate/F056.png',n),('layers/F056_BG_person.png',bg)]:
 dest=OUT/relative
 if dest.exists(): assert np.array_equal(arr(dest),a),relative
 else: dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(dest)
assert (OUT/'layers/F056_FG_true_front_fingers.png').read_bytes()==(OLD/'layers/F056_FG_true_front_fingers.png').read_bytes()
assert hashlib.sha256((OUT/'candidate/F056.png').read_bytes()).hexdigest()=='5eddb73f6c624ad0ad902e4b0958432ed75fc251ee297bf0ef036bd10a6c0268'
print('Verified exact approved1868 donor reuse and protected original056 foreground; imagegen0, Canvas0 in this tool.')
