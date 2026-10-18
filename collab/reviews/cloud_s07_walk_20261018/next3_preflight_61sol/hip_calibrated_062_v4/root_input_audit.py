#!/usr/bin/env python3
"""Independently check actual F062 input PNGs; this does not create final art."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label

R = Path(__file__).resolve().parent
meta = json.loads((R / 'geometry/preparation_checks.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = R.parent.parent / 'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png'
proposal = R / 'reference/F062_hip_calibrated_source_pixels_NOT_ART.png'
assert sha(source) == meta['source_sha256']
assert sha(proposal) == meta['proposal_sha256']
a = np.array(Image.open(source).convert('RGBA'))
b = np.array(Image.open(proposal).convert('RGBA'))
assert a.shape == b.shape == (1080, 1672, 4)

def mask(name):
    x = np.array(Image.open(R / 'masks' / (name + '.png')).convert('L'))
    assert set(np.unique(x)).issubset({0, 255})
    return x > 0

edit = mask('F062_full_pants_and_sleeves_WHITE_EDIT_PENDING')
guards = {name: mask(name) for name in [
    'HARD_complete_head_blouse_except_sleeve',
    'HARD_visible_complete_arms_except_sleeve',
    'HARD_visible_complete_shoes_ankles',
]}
overlaps = {name: int((edit & g).sum()) for name, g in guards.items()}
assert not any(overlaps.values())
near = mask('SOURCE_near_shoe_ankle_FIXED')
near_layer = np.array(Image.open(R / 'layers/F062_near_shoe_ankle_FIXED.png').convert('RGBA'))
near_changes = int(np.any(b[near] != a[near], axis=1).sum())
assert near_changes == 0
assert np.array_equal(near_layer[near], a[near])
assert not near_layer[~near].any()
sole = int(np.where(near_layer[:, :, 3] >= 128)[0].max())
assert sole == 1022

reg = meta['registration']
body = a.copy()
body[~mask('SOURCE_body_head_blouse')] = 0
dx, dy = np.array(meta['head_blouse_delta_world']) / reg['s']
expected_body = np.array(Image.fromarray(body).transform(
    (1672, 1080), Image.Transform.AFFINE, (1, 0, -dx, 0, 1, -dy),
    resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0)))
actual_body = np.array(Image.open(R / 'layers/F062_body_head_blouse.png').convert('RGBA'))
assert np.array_equal(expected_body, actual_body)

chain = np.array(meta['near062_chain_native'])
src_chain = np.array(meta['near_source_chain_native'])
lengths = np.linalg.norm(np.diff(chain, axis=0), axis=1) * reg['s']
src_lengths = np.linalg.norm(np.diff(src_chain, axis=0), axis=1) * reg['s']
assert np.allclose(lengths, src_lengths, atol=1e-8, rtol=0)
assert np.array_equal(chain[2], src_chain[2])
components, _ = label(edit)
points = [chain[0], chain[1], chain[2] - [0, 25]]
ids = [int(components[round(y), round(x)]) for x, y in points]
assert ids[0] > 0 and len(set(ids)) == 1

x0, y0, x1, y1 = meta['mask']['crop_xyxy']
crop = np.array(Image.open(R / 'reference/F062_crop_RGBA_NOT_ART.png').convert('RGBA'))
crop_mask = np.array(Image.open(R / 'masks/F062_crop_WHITE_EDIT_PENDING.png').convert('L')) > 0
assert np.array_equal(crop, b[y0:y1, x0:x1])
assert np.array_equal(crop_mask, edit[y0:y1, x0:x1])
assert int(edit.sum()) == meta['mask']['pixels']

report = {
    'status': 'ACTUAL_PREPOSITION_AND_MASK_AUTHOR_REVIEW_PASS_PENDING_ASTRA_INPUT_GATE',
    'scope': 'S07 F062 input only; no finished art, generation approval,068/073 work or scene readiness claimed.',
    'source_sha256': sha(source),
    'proposal_sha256': sha(proposal),
    'crop_sha256': sha(R / 'reference/F062_crop_RGBA_NOT_ART.png'),
    'crop_mask_sha256': sha(R / 'masks/F062_crop_WHITE_EDIT_PENDING.png'),
    'near_shoe_source_RGBA_changes': near_changes,
    'near_actual_sole_native': sole,
    'near_actual_sole_world': sole * reg['s'] + reg['ty'],
    'head_blouse_matches_original_beat_translation_exactly': True,
    'near_proxy_lengths_world_source': src_lengths.tolist(),
    'near_proxy_lengths_world_F062': lengths.tolist(),
    'near_hip_knee_cuff_same_white_component': ids,
    'actual_edit_protection_overlap_pixels': overlaps,
    'actual_crop_size': [x1 - x0, y1 - y0],
    'actual_views': [
        'qa/F057_F062_actual_pixels_and_chain_comparison.png',
        'qa/F062_crop_and_edit_domain_PENDING.png',
        'qa/actual_fixed_near_and_swing_far_feet.png',
        'masks/F062_crop_WHITE_EDIT_PENDING.png',
    ],
    'visual_findings': [
        'Entire near trouser volume from waist/hips through knee to cuff is editable, including technical piece cracks and knee-back turn.',
        'Head and blouse retain the original beat; fixed whole near shoe and bare ankle remain at the same support position.',
        'Far hip is an explicit manual volume guide, not anatomical measurement; the whole far trouser is editable.',
        'Visible arms, hands, jade bracelet and actual visible feet remain protected except small sleeve connections.',
    ],
    'new_image_requests': 0,
}
(R / 'root_actual_input_review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
