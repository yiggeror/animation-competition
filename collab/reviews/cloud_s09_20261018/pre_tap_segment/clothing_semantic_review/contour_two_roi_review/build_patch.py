#!/usr/bin/env python3
"""Copy same-coordinate source RGBA in exactly two approved contour ROIs; no generation."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SEMANTIC = ROOT.parent
PRE = SEMANTIC.parent
BASE = PRE.parent
for directory in ['candidate', 'crops', 'masks', 'qa']:
    (ROOT / directory).mkdir(exist_ok=True)
source_path = SEMANTIC / 'candidates/same_call05_continuous_cloth_pending_review.png'
donor_path = PRE / 'originals/d06_call05_raw.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source_path) == 'db697c53dfa7b890ccc788c58264c65c7d4d6cb7cde04029dfe0a1a419f73714'
assert sha(donor_path) == '05b3301da1652178ee0c39f3b5df181551cd1627f34ec4726e529c127f1ac93c'
before = Image.open(source_path).convert('RGBA')
donor = Image.open(donor_path).convert('RGBA')
assert before.size == donor.size == (1672, 941)
a, d = np.array(before), np.array(donor)
# Coordinator coordinates are INCLUSIVE; Pillow boxes below are exclusive at right/bottom.
boxes = {'left': [618, 829, 631, 847], 'right': [968, 843, 982, 857]}
contexts = {'left': [595, 805, 656, 871], 'right': [945, 820, 1006, 886]}
edit = np.zeros(a.shape[:2], dtype=bool)
c = a.copy()
per_roi = {}
for name, (x0, y0, x1, y1) in boxes.items():
    edit[y0:y1, x0:x1] = True
    c[y0:y1, x0:x1] = d[y0:y1, x0:x1]
    changed = np.any(c[y0:y1, x0:x1] != a[y0:y1, x0:x1], axis=2)
    per_roi[name] = {
        'box_xyxy_exclusive': [x0, y0, x1, y1],
        'area_px': (x1-x0)*(y1-y0), 'changed_RGBA_pixels': int(changed.sum()),
        'changed_alpha_pixels': int((c[y0:y1, x0:x1, 3] != a[y0:y1, x0:x1, 3]).sum()),
        'candidate_RGBA_equals_donor_in_whole_ROI': bool(np.array_equal(c[y0:y1, x0:x1], d[y0:y1, x0:x1]))}
assert edit.sum() == 430
assert np.array_equal(c[~edit], a[~edit])
assert np.array_equal(c[:, :, 3][~edit], a[:, :, 3][~edit])
previous_hard = np.array(Image.open(SEMANTIC / 'masks/hard_protection_all.png')) > 0
assert np.array_equal(c[previous_hard & ~edit], a[previous_hard & ~edit])
candidate = Image.fromarray(c)
candidate_path = ROOT / 'candidate/F031_exact_two_ROIs_NOT_LOCKED.png'
candidate.save(candidate_path)
Image.fromarray((edit*255).astype('uint8')).save(ROOT / 'masks/two_ROIs_only.png')
for name, box in contexts.items():
    for label, im in [('before', before), ('donor_call05', donor), ('after', candidate)]:
        im.crop(box).save(ROOT / f'crops/{name}_{label}_context.png')

font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font = ImageFont.truetype(font_path, 22)
small = ImageFont.truetype(font_path, 18)
for bg_name, bg_color in [('gray', (194, 199, 204)), ('dark', (29, 33, 39))]:
    sheet = Image.new('RGB', (1260, 840), (245, 246, 248))
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 15), f'031仅两处外缘RGBA接回 · {bg_name}底 · 每源像素放大5倍 · 新增生成0', font=font, fill='#202833')
    for row, (name, box) in enumerate(contexts.items()):
        for col, (title, im) in enumerate([('修前', before), ('call05同位供体', donor), ('限定ROI接回／边界仍待核', candidate)]):
            crop = im.crop(box)
            background = Image.new('RGBA', crop.size, bg_color + (255,))
            background.alpha_composite(crop)
            enlarged = background.convert('RGB').resize((crop.width*5, crop.height*5), Image.Resampling.NEAREST)
            x, y = 24 + col*412, 93 + row*374
            sheet.paste(enlarged, (x, y))
            draw.text((x, y-30), f'{name} · {title}', font=small, fill='#202833')
            x0,y0,x1,y1=boxes[name]
            draw.rectangle((x+(x0-box[0])*5, y+(y0-box[1])*5, x+(x1-box[0])*5-1, y+(y1-box[1])*5-1), outline='#ce5366', width=2)
    sheet.save(ROOT / f'qa/two_ROIs_before_donor_after_{bg_name}.png')

lock = json.loads((BASE / 'switch_segment/locked/F000_lock.json').read_text())
registered = candidate.transform((1536,864), Image.Transform.AFFINE,
    tuple(lock['registration']['inverse_pillow_affine']), resample=Image.Resampling.BICUBIC, fillcolor=(0,0,0,0))
registered.save(ROOT / 'candidate/F031_registered_NOT_LOCKED.png')
view = registered.crop((280,80,1304,656)).resize((1280,720), Image.Resampling.LANCZOS)
view.save(ROOT / 'qa/F031_1280x720_NOT_LOCKED.png')
def edge(ar, y, side):
    x0, x1 = (600,655) if side == 'left' else (945,1000)
    xs = np.flatnonzero(ar[y,x0:x1,3] > 128) + x0
    return int(xs.min() if side == 'left' else xs.max()) if len(xs) else None
boundary_rows = {side: [dict(y=y, before=edge(a,y,side), donor=edge(d,y,side), after=edge(c,y,side))
    for y in rows] for side,rows in [('left',[837,838,839,840,845,846,847]),('right',[851,852,853,855,856,857,858])]}
report = {
    'status': 'EXACT_APPROVED_ROI_COPY_VERIFIED_BUT_BOUNDARY_CLIPS_NOT_LOCKED',
    'authorization': 'Astra: only left raw x618..630/y829..846 and right x968..981/y843..856; same-call05 full RGBA; no generation; all other pixels and alpha locked.',
    'new_native_calls': 0, 'S09_native_calls_unchanged': 12, 'F031_native_calls_unchanged': 7,
    'F037_native_calls': 0, 'F042_native_calls': 0,
    'source_before': {'path': str(source_path.relative_to(BASE)), 'sha256': sha(source_path)},
    'donor': {'path': str(donor_path.relative_to(BASE)), 'sha256': sha(donor_path), 'translation': [0,0], 'scale': 1, 'full_RGBA_copy': True},
    'candidate': {'path': str(candidate_path.relative_to(BASE)), 'sha256': sha(candidate_path)},
    'ROIs': per_roi, 'edit_mask_pixels': int(edit.sum()),
    'total_changed_RGBA_pixels': int(np.any(c != a, axis=2).sum()),
    'total_changed_alpha_pixels': int((c[:,:,3] != a[:,:,3]).sum()),
    'RGBA_changes_outside_two_ROIs': int(np.any(c[~edit] != a[~edit], axis=1).sum()),
    'alpha_changes_outside_two_ROIs': int((c[:,:,3][~edit] != a[:,:,3][~edit]).sum()),
    'previous_hard_protection_changes_except_authorized_ROIs': int(np.any(c[previous_hard & ~edit] != a[previous_hard & ~edit], axis=1).sum()),
    'complete_hands_prop_head_neck_unchanged': True,
    'registration_unchanged': True,
    'visible_alpha128_contour_rows_before_donor_after': boundary_rows,
    'actual_view_findings': [
        'Approved rectangles were copied exactly, but gray/dark actual inspection shows bounds clip the continuous donor contour; not a smooth-join pass.',
        'Left y838 after first visible x623; y839 retains x617 outside approved x>=618, leaving the old contour island.',
        'Right y856 after last visible x981; y857 retains x973 outside approved y<=856, leaving an8px retreat.',
        'No unauthorized extension or alpha painting used to hide the boundary problem.'],
    'next_gate': 'Astra review exact pixel boundary evidence and choose permitted contour extent/method; whole031 remains unlocked,037/042 not dispatched.'}
(ROOT / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k: report[k] for k in ['status','new_native_calls','edit_mask_pixels','total_changed_RGBA_pixels','total_changed_alpha_pixels','RGBA_changes_outside_two_ROIs','alpha_changes_outside_two_ROIs','previous_hard_protection_changes_except_authorized_ROIs']}, ensure_ascii=False))
