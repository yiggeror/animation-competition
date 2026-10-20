"""Reproduce engineering-guide cleanup from immutable adopted art and masks.

No image generation or character transforms. Run from the repository root.
Outputs go to /tmp by default; --out can target a separate review directory.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess

import numpy as np
from PIL import Image

P = Path(__file__).resolve().parent
FRONT = P.parent
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, default=Path('/tmp/s20_front_rebuild'))
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
rows = json.loads((FRONT / 'front_source_adoption.json').read_text())

def original(row):
    data = subprocess.check_output(['git', 'show', row['sourceCommit'] + ':' + row['source']])
    assert hashlib.sha256(data).hexdigest() == row['originalSHA256']
    return np.array(Image.open(io.BytesIO(data)).convert('RGBA'))

mother = original(rows[0])
approved_path = 'collab/reviews/cloud_s20_20261018/cam20_lower_only_plus2_zero_call_003/people_F000_rods_rotated.png'
approved_bytes = subprocess.check_output(['git', 'show', rows[0]['sourceCommit'] + ':' + approved_path])
assert hashlib.sha256(approved_bytes).hexdigest() == rows[0]['CGuideStage']['sha256']
corrected = np.array(Image.open(io.BytesIO(approved_bytes)).convert('RGBA'))
delta = np.any(mother != corrected, axis=2)
for row in rows:
    art = original(row)
    apply = delta & np.all(art == mother, axis=2)
    art[apply] = corrected[apply]
    mask = np.array(Image.open(P / f"F{row['key']:03}_shaft_only_mask.png").convert('L')) > 0
    art[mask] = 0
    dest = args.out / row['production']
    Image.fromarray(art).save(dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == row['productionSHA256'], dest
print('Rebuilt and verified all12 production RGBA files; no character pixel transform.')
