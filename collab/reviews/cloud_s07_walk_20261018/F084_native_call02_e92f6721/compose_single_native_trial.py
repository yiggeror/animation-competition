#!/usr/bin/env python3
"""One genuine native whole-trouser output plus five unchanged whole source layers.

The only geometry mapping is the approved whole-image 65/128 inverse and crop
offset. Material selection extracts returned art; it draws no new anatomy.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label, binary_closing, binary_fill_holes, binary_dilation, binary_erosion
import hashlib, json, shutil
import numpy as np

R = Path(__file__).resolve().parent
F = R / 'frozen_input_e92f6721'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for folder in ['candidate', 'production_layers', 'masks', 'qa']:
    (R / folder).mkdir(exist_ok=True)
for entry in json.loads((F / 'PACKAGE_SHA256.json').read_text())['files']:
    assert sha(F / entry['path']) == entry['sha256']
raw_path = R / 'originals/F084_call02_RAW.png'
assert sha(raw_path) == '543bf9fee8f3b96c284660abee6a298bea9c14b6b0b98eedc0a35b68e197ef70'
raw = Image.open(raw_path).convert('RGBA')
assert raw.size == (1024, 1536)
aligned = raw.resize((520, 780), Image.Resampling.LANCZOS)
aligned.save(R / 'qa/call02_known_whole_inverse_520x780.png')
size = (1672, 1080)
n = np.zeros((1080, 1672, 4), np.uint8)
n[280:1060, 1000:1520] = np.array(aligned)
rgb = n[:, :, :3].astype(int)
yy, xx = np.indices(n.shape[:2])
# The navy interiors of BOTH returned whole legs, not a thin shoe connection.
seed = ((n[:, :, 3] >= 128) & (rgb[:, :, 2] - rgb[:, :, 0] > 5)
        & (rgb[:, :, 2] - rgb[:, :, 0] < 35)
        & (rgb[:, :, 2] - rgb[:, :, 1] > 3)
        & (rgb.max(axis=2) < 130) & (yy >= 500) & (yy <= 1007))
labs, _ = label(seed)
counts = np.bincount(labs.ravel()); counts[0] = 0
components = np.flatnonzero(counts > 1000)
assert len(components) == 2
core = binary_fill_holes(binary_closing(np.isin(labs, components), iterations=2))
material = binary_dilation(core, iterations=2) & (n[:, :, 3] > 0) & (yy >= 498) & (yy <= 1009)
blue_blouse = (rgb[:, :, 2] - rgb[:, :, 0] >= 35) & (rgb.max(axis=2) > 75)
skin = (rgb[:, :, 0] > 140) & (rgb[:, :, 0] - rgb[:, :, 1] > 15) & (rgb[:, :, 1] - rgb[:, :, 2] > 8)
sole_white = rgb.min(axis=2) > 150
trim = material & (blue_blouse | ((yy >= 850) & (skin | sole_white)))
material &= ~trim
pants = n.copy(); pants[~material] = 0
# Preserve the actual returned RGB and alpha, including AA. No color or shape repair.
Image.fromarray(pants).save(R / 'production_layers/native_complete_trousers_original_color_TRIAL.png')
Image.fromarray(material.astype('uint8') * 255).save(R / 'masks/actual_complete_native_trouser_material.png')
Image.fromarray(trim.astype('uint8') * 255).save(R / 'masks/returned_nontrouser_material_excluded.png')
names = ['far_shoe_ankle_SWING', 'far_complete_arm_jade_hand', 'body_head_blouse',
         'near_complete_arm', 'near_shoe_ankle_SUPPORT_FIXED']
sources = {}
for name in names:
    src = F / 'sources' / f'F084_FROZEN_{name}.png'
    dst = R / 'production_layers' / f'source_F084_{name}.png'
    shutil.copyfile(src, dst)
    assert sha(src) == sha(dst)
    sources[name] = Image.open(dst).convert('RGBA')
foreground = np.logical_or.reduce([np.array(sources[name])[:, :, 3] >= 128
                                  for name in names if name != 'far_shoe_ankle_SWING'])
visible_color = binary_erosion(material & (n[:, :, 3] >= 128) & ~foreground, iterations=4)
mean = rgb[visible_color].mean(axis=0)
references = {}
for frame in [57, 62]:
    anchor = np.array(Image.open(F / 'sources' / f'F0{frame}_palette_ARCHIVE_NOT_REQUEST.png').convert('RGBA'))
    ar = anchor[:, :, :3].astype(int)
    am = np.array(Image.open(F / 'sources' / f'F0{frame}_actual_pants_material_mask.png').convert('L')) > 0
    sel = binary_erosion(am & (anchor[:, :, 3] >= 128)
                         & (ar[:, :, 2] - ar[:, :, 0] > 5)
                         & (ar[:, :, 2] - ar[:, :, 0] < 35)
                         & (ar.max(axis=2) < 130), iterations=4)
    refmean = ar[sel].mean(axis=0)
    references[str(frame)] = {'source_sha256': sha(F / 'sources' / f'F0{frame}_palette_ARCHIVE_NOT_REQUEST.png'),
                              'reference_mean_rgb': refmean.tolist(),
                              'native084_mean_rgb': mean.tolist(),
                              'delta_rgb': (mean - refmean).tolist(),
                              'within4': bool(np.all(np.abs(mean - refmean) <= 4))}
assert all(v['within4'] for v in references.values())
order = ['far_shoe_ankle_SWING', 'native_trousers', 'far_complete_arm_jade_hand',
         'body_head_blouse', 'near_complete_arm', 'near_shoe_ankle_SUPPORT_FIXED']
canvas = Image.new('RGBA', size)
for name in order:
    canvas.alpha_composite(Image.fromarray(pants) if name == 'native_trousers' else sources[name])
candidate = R / 'candidate/F084_call02_complete_volume_PENDING_ASTRA.png'
canvas.save(candidate)
font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 17)
for tone, color in [('gray', (213, 223, 231, 255)), ('dark', (35, 43, 52, 255))]:
    bg = Image.new('RGBA', size, color); bg.alpha_composite(canvas)
    bg.convert('RGB').save(R / f'qa/F084_call02_source_layered_full_{tone}_TRIAL.png')
    bg.crop((1000, 280, 1520, 1060)).convert('RGB').save(R / f'qa/F084_call02_source_layered_crop_{tone}_TRIAL.png')
    boxes = [('真实衣摆／完整腰臀', (1180, 500, 1400, 655)),
             ('远原鞋在近胫后／真实裤口', (1185, 840, 1385, 985)),
             ('近原鞋／承重裤口', (1185, 900, 1390, 1045)),
             ('双原袖根／无移动原臂', (1170, 325, 1425, 435))]
    sheet = Image.new('RGB', (1100, 710), (235, 241, 246)); draw = ImageDraw.Draw(sheet)
    for j, (title, box) in enumerate(boxes):
        q = bg.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2), Image.Resampling.NEAREST)
        x, y = (j % 2) * 550, (j // 2) * 355 + 35
        sheet.paste(q.convert('RGB'), (x, y)); draw.text((x+5, y-27), title, font=font, fill='#263440')
    sheet.save(R / f'qa/F084_call02_actual_connections_{tone}_TRIAL.png')
report = {'status': 'ONE_CALL02_NATIVE_COMPLETE_VOLUME_SOURCE_LAYERED_TRIAL_PENDING_ASTRA',
          'raw_sha256': sha(raw_path), 'candidate_sha256': sha(candidate),
          'only_geometry_transform': {'whole_inverse_scale': '65/128', 'offset': [1000, 280],
                                      'raw_size': [1024, 1536], 'native_crop_size': [520, 780]},
          'native_navy_component_sizes': [int(counts[i]) for i in components],
          'complete_native_trouser_material_pixels': int(material.sum()),
          'returned_nontrouser_pixels_excluded': int(trim.sum()),
          'native_RGB_correction': [0, 0, 0], 'native_alpha_or_shape_repair': False,
          'palette_vs_locked_mothers': references, 'source_layer_order_back_to_front': order,
          'all_five_source_layer_sha256_unchanged': True,
          'far_whole_source_shoe_is_a_back_layer_not_a_foreground_hardguard': True,
          'native_pants_over_far_source_shoe_alpha128_pixels': int(((pants[:, :, 3] >= 128) & (np.array(sources['far_shoe_ankle_SWING'])[:, :, 3] >= 128)).sum()),
          'correction_requests': 1, 'correction_originals': 1,
          'total_F084_requests': 2, 'total_F084_originals': 2,
          'new_calls_for_adoption': 0, 'F090_unopened': True,
          'limits': 'No locked state or exposure acceptance. Actual waist, both ankle/cuffs, sleeve roots and volume/depth require review. Soft joint guides are not measured hard joints; far-knee flexion remains an Astra action-amplitude decision.'}
(R / 'qa/one_native_source_layered_trial_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
