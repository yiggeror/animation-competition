"""Derive S31's local smile variant while retaining A's neck, hair and body.

Usage: python tools/cutout_s31_reaction.py SOURCE_A SOURCE_B --out assets/chars
       --report-dir /tmp/s31-reaction-assets
Reuses the reviewed S29 neutral-background extraction and card-map pipeline.
Only approved source pixels are composited; no anatomy is painted or warped.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source_a')
p.add_argument('source_b')
p.add_argument('--out', default='assets/chars')
p.add_argument('--report-dir', required=True)
a = p.parse_args()
out, report = Path(a.out), Path(a.report_dir)
out.mkdir(parents=True, exist_ok=True)
report.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent
sha = lambda f: hashlib.sha256(Path(f).read_bytes()).hexdigest()

with tempfile.TemporaryDirectory(prefix='s31-smile-') as tmp:
    dirs = [Path(tmp) / 'a', Path(tmp) / 'b']
    for source, dest in zip([a.source_a, a.source_b], dirs):
        subprocess.run([sys.executable, str(here / 'cutout_s29_blow.py'), source,
                        '--out', str(dest)], check=True)
    ia, ib = [Image.open(d / 'g29_prepare_blow.png').convert('RGBA') for d in dirs]
    if ia.size != (1024, 1536) or ib.size != ia.size:
        raise ValueError('Approved A/B must share the unchanged 1024x1536 frame')
    ar, br = [np.asarray(im).astype(np.float32) / 255 for im in (ia, ib)]
    mask = Image.new('L', ia.size)
    # Mouth / cheeks only; keep A's glasses, eyes, hair, bun, neck and collar.
    face_poly = [(150, 695), (540, 695), (550, 755), (520, 810),
                 (430, 855), (345, 879), (235, 885), (150, 850)]
    ImageDraw.Draw(mask).polygon(face_poly, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    # The lower spectacle rims end above y700. Keep those original pixels,
    # then ease into the cheek replacement over the next 12 source rows.
    gate = np.clip((np.arange(1536, dtype=np.float32) - 700) / 12, 0, 1)
    gate = gate * gate * (3 - 2 * gate)
    mask = Image.fromarray(np.round(np.asarray(mask) * gate[:, None]).astype(np.uint8))
    k = np.asarray(mask, dtype=np.float32)[..., None] / 255
    aa, ba = ar[..., 3:4], br[..., 3:4]
    alpha = aa * (1 - k) + ba * k
    premul = ar[..., :3] * aa * (1 - k) + br[..., :3] * ba * k
    rgb = np.divide(premul, alpha, out=np.zeros_like(premul), where=alpha > 1e-8)
    rgba = np.round(np.concatenate([rgb, alpha], axis=-1) * 255).clip(0, 255).astype(np.uint8)
    # Keep truly untouched pixels byte-identical, including transparent RGB.
    rgba[np.asarray(mask) == 0] = np.asarray(ia)[np.asarray(mask) == 0]
    card = Image.fromarray(rgba)
    alb = out / 'g31_release_smile.png'
    card.save(alb)
    keep = Image.new('L', ia.size)
    ImageDraw.Draw(keep).polygon([(0, 0), (1024, 0), (1024, 750), (702, 750),
        (677, 843), (642, 952), (570, 1058), (531, 978), (493, 917),
        (459, 881), (431, 851), (410, 841), (0, 900)], fill=255)
    shadow = Image.new('RGBA', ia.size, (0, 0, 0, 0))
    shadow.putalpha(Image.fromarray(np.minimum(rgba[..., 3], np.asarray(keep))))
    sh = out / 'g31_release_smile_shadow.png'
    shadow.save(sh)
    nrm, mat = out / 'g31_release_smile_n.png', out / 'g31_release_smile_m.png'
    subprocess.run([sys.executable, '-I', str(here / 'card_maps.py'), str(alb),
                    str(nrm), str(mat), '35', '.55'], check=True)
    check = Image.new('RGBA', ia.size, (42, 61, 54, 255))
    check.alpha_composite(card)
    check.convert('RGB').save(report / 'cutout_check.jpg')
    mask.save(report / 'face_replacement_mask.png')
    delta = np.any(rgba != np.asarray(ia), axis=-1)
    ys, xs = np.where(delta)
    manifest = {
        'source_a': str(Path(a.source_a)), 'source_a_sha256': sha(a.source_a),
        'source_b': str(Path(a.source_b)), 'source_b_sha256': sha(a.source_b),
        'alignment_b_xy': [0, 0], 'face_polygon': face_poly,
        'feather_px': 6, 'method': 'Premultiplied local A/B source-pixel replacement; A outside feather retained byte-identically; existing S29 head/neck projection boundary',
        'changed_rgba_pixels_vs_derived_a': int(delta.sum()),
        'changed_bbox_xyxy': [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)],
        'outputs': [{'path': str(f), 'sha256': sha(f)} for f in [alb, nrm, mat, sh]],
        'helpers': [{'path': str(f), 'sha256': sha(f)} for f in [Path(__file__), here / 'cutout_s29_blow.py', here / 'card_maps.py']],
    }
    (report / 'asset_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))
