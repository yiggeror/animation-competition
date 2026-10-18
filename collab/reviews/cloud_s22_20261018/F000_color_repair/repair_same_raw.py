#!/usr/bin/env python3
"""Authorized pixel-only F000 repair. No generation, warp, redraw or resampling."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / 'F000_first/originals/F000_call01_raw.png'
EXPECTED = '57f14bae2b0e48cf35e0270f7d7384e28719897282bd1ff02b036ec429e52353'
assert hashlib.sha256(RAW.read_bytes()).hexdigest() == EXPECTED
for sub in ['candidate', 'masks', 'qa', 'provenance']:
    (HERE / sub).mkdir(exist_ok=True)
a = np.asarray(Image.open(RAW).convert('RGBA')).copy()
h, w = a.shape[:2]
rgb, alpha = a[:, :, :3].astype(float), a[:, :, 3]
yy, xx = np.mgrid[:h, :w]

# Assign the two actual opaque volumes by their left-edge entry height.
opaque, count = nd.label(alpha >= 128)
assert count == 2
ordered = sorted(range(1, count + 1), key=lambda k: np.where((opaque == k) & (xx < 8))[0].mean())
g_id, x_id = ordered

# Both alpha>0 contours are connected by faint source pixels. Preserve that
# entire component, including its fine AA; only detached components are eligible.
nonzero, n = nd.label(alpha > 0, np.ones((3, 3)))
main_ids = np.unique(nonzero[alpha >= 128])
main = np.isin(nonzero, main_ids)
max_alpha = nd.maximum(alpha, nonzero, np.arange(n + 1))
distance = nd.distance_transform_edt(~main)
cleanup = (nonzero > 0) & ~main & (max_alpha[nonzero] <= 6) & (distance > 2)

# Protect the two painted thumbnail plates and their boundary lines. No other
# fingernail plate is drawn in this raw. Coordinates are measured in raw pixels.
nail_img = Image.new('L', (w, h))
draw = ImageDraw.Draw(nail_img)
draw.ellipse((660, 427, 700, 473), fill=255)
draw.ellipse((832, 502, 868, 535), fill=255)
nail_core = np.asarray(nail_img) > 0
nail_distance = nd.distance_transform_edt(~nail_core)
nail_weight = np.clip(nail_distance / 3, 0, 1)

# Warm skin selection with a continuous dark-tone roll-off. Deep ink is zero.
r, g, b = rgb.transpose(2, 0, 1)
warm = (r > g + 10) & (g > b + 10) & (g / np.maximum(r, 1) > .68) & (b / np.maximum(r, 1) > .5)
tone = np.clip(np.minimum.reduce([(r - 170) / 45, (g - 105) / 45, (b - 65) / 40]), 0, 1)
edge = np.clip((nd.distance_transform_edt(alpha >= 128) - 1) / 2, 0, 1)
base = warm * tone * edge * nail_weight
# Exclude the visible bamboo strip at the child's grip and beyond. The line
# follows the raw rod, not any scene movement; skin below the strip stays eligible.
rod = (xx >= 868) & (yy < 526 - .628 * (xx - 868))
weights = {
    'grandma': base * (opaque == g_id),
    'xiaoman': base * (opaque == x_id) * ~rod,
}
offsets = {'grandma': [1, 6, 12], 'xiaoman': [1, 3, 8]}
out = a.copy()
result = rgb.copy()
for role, weight in weights.items():
    result += weight[:, :, None] * np.array(offsets[role])
    Image.fromarray(np.rint(weight * 255).astype('uint8')).save(HERE / f'masks/{role}_skin_color.png')
out[:, :, :3] = np.clip(np.rint(result), 0, 255).astype('uint8')
out[cleanup, 3] = 0
Image.fromarray(nail_core.astype('uint8') * 255).save(HERE / 'masks/nails_protected.png')
Image.fromarray(rod.astype('uint8') * 255).save(HERE / 'masks/bamboo_excluded.png')
Image.fromarray(cleanup.astype('uint8') * 255).save(HERE / 'masks/disconnected_lowalpha_cleanup.png')
candidate = HERE / 'candidate/F000_repaired.png'
Image.fromarray(out).save(candidate)

boxes = {'grandma': [530, 318, 555, 338], 'xiaoman': [700, 594, 722, 610]}
targets = {'grandma': [254, 210, 177], 'xiaoman': [254, 205, 171]}
measurements = {}
for role, (x0, y0, x1, y1) in boxes.items():
    m = (alpha[y0:y1, x0:x1] >= 128) & warm[y0:y1, x0:x1]
    before = np.median(a[y0:y1, x0:x1, :3][m], axis=0)
    after = np.median(out[y0:y1, x0:x1, :3][m], axis=0)
    error = after - np.array(targets[role])
    assert np.max(np.abs(error)) <= 4
    measurements[role] = dict(box=boxes[role], valid_pixels=int(m.sum()), before_RGB=before.tolist(), after_RGB=after.tolist(), target_RGB=targets[role], error_RGB=error.tolist(), additive_offset_RGB=offsets[role])

changed = np.any(a[:, :, :3] != out[:, :, :3], axis=2)
dark = (r <= 170) & (alpha >= 128)
assert not np.any(changed & dark)
assert not np.any(changed & nail_core)
assert not np.any(changed & (alpha < 128))
assert not np.any((alpha != out[:, :, 3]) & ~cleanup)
assert np.array_equal(out[:, :, 3][main], alpha[main])
assert np.array_equal(out[cleanup, :3], a[cleanup, :3])
assert np.array_equal(out[rod & (opaque == x_id), :3], a[rod & (opaque == x_id), :3])
opaque_after, n_after = nd.label(out[:, :, 3] >= 128)
assert np.array_equal(opaque_after, opaque)
distance_g = nd.distance_transform_edt(opaque != g_id)
gap = float(distance_g[opaque == x_id].min())
metrics = dict(
    source=str(RAW.relative_to(ROOT)), source_sha256=EXPECTED,
    candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
    dimensions=[w, h], new_image_calls=0, cumulative_S22_image_calls=1,
    method='Independent additive RGB skin correction; no geometry change or fill replacement. Original shading differences remain, with dark-tone roll-off and nail/AA protection.',
    sampling=measurements, rgb_changed_pixels=int(changed.sum()),
    cleanup=dict(removed_alpha_pixels=int(cleanup.sum()), removed_component_ids=int(len(np.unique(nonzero[cleanup]))), max_removed_alpha=int(alpha[cleanup].max()), rule='8-connected alpha>0 components disconnected from both opaque hand/rod silhouettes; maximum component alpha <=6; more than 2px from the main alpha>0 contour. Main-connected AA retained exactly.'),
    protected=dict(dark_pixels=int(dark.sum()), nail_pixels=int((nail_core & (alpha >= 128)).sum()), dark_RGB_unchanged=True, nail_RGB_unchanged=True, bamboo_RGB_unchanged=True, main_connected_alpha_unchanged=True, all_RGB_under_alpha128_unchanged=True),
    geometry=dict(opaque_components_before=count, opaque_components_after=n_after, opaque_masks_identical=True, minimum_opaque_G_X_distance_px=gap, no_warp_or_resampling=True),
    review_status='Candidate for Astra mother-image approval. No F012/F024 generation.'
)
(HERE / 'provenance/correction_measurements.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n')

font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
def composite(data, bg):
    im = Image.fromarray(data)
    plate = Image.new('RGBA', im.size, (*bg, 255))
    plate.alpha_composite(im)
    return plate.convert('RGB')
for name, bg in [('gray', (115,115,115)), ('white', (255,255,255)), ('black', (0,0,0))]:
    before, after = composite(a, bg), composite(out, bg)
    before.save(HERE / f'qa/before_on_{name}.png')
    after.save(HERE / f'qa/after_on_{name}.png')
    canvas = Image.new('RGB', (w * 2, h + 35), (32,32,32))
    canvas.paste(before, (0,35)); canvas.paste(after, (w,35))
    d = ImageDraw.Draw(canvas); d.text((12,7), 'BEFORE - same raw', font=font, fill='white'); d.text((w+12,7), 'AFTER - pixel repair only', font=font, fill='white')
    canvas.save(HERE / f'qa/before_after_{name}.jpg', quality=95)
before, after = composite(a, (115,115,115)), composite(out, (115,115,115))
crop = (440,280,930,680)
contact = Image.new('RGB', (980*2,835), (32,32,32))
contact.paste(before.crop(crop).resize((980,800)), (0,35)); contact.paste(after.crop(crop).resize((980,800)), (980,35))
d = ImageDraw.Draw(contact); d.text((12,7), 'BEFORE - grip at 2x', font=font, fill='white'); d.text((992,7), 'AFTER - same geometry and nails', font=font, fill='white')
contact.save(HERE / 'qa/grip_before_after_2x.png')
overlay = composite(a, (115,115,115))
pixels = np.array(overlay).astype(float)
for role, color in [('grandma', [80,220,255]), ('xiaoman', [255,80,180])]:
    m = weights[role][:,:,None] * .5
    pixels = pixels*(1-m) + np.array(color)*m
Image.fromarray(np.rint(pixels).astype('uint8')).save(HERE / 'qa/color_masks_overlay.png')
print(json.dumps(metrics, ensure_ascii=False, indent=2))
