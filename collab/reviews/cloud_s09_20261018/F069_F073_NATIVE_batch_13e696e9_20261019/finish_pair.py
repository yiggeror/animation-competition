from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import label, binary_fill_holes, binary_erosion
import numpy as np
import json, hashlib

R = Path(__file__).resolve().parent
for d in ['candidate', 'layers', 'masks', 'geometry', 'qa']:
    (R / d).mkdir(exist_ok=True)
scale = 770 / 1145
size = (1672, 941)
mapped = {}
for state, name in [('F069', 'F069_NATIVE_RAW.png'),
                    ('F073', 'F073_NATIVE_RAW_BASE_before_LIGHT.png')]:
    raw = Image.open(R / state / 'originals' / name).convert('RGBA')
    assert raw.size == (1145, 1374)
    scene = Image.new('RGBA', size)
    scene.alpha_composite(raw.resize((770, 924), Image.Resampling.LANCZOS), (550, 0))
    mapped[state] = scene
    scene.save(R / 'layers' / f'{state}_ACTUAL_whole_uniform_scene.png')

# This code creates light only. All character, hand and prop RGB comes from the
# two separately archived native drawings. No fitted or procedural body parts.
a = np.array(Image.open(R / 'F073/originals/F073_NATIVE_RAW_BASE_before_LIGHT.png').convert('RGBA'))
y, x = np.indices(a.shape[:2])
rgb = a[:, :, :3].astype(float)
neutral = ((x > 985) & (x < 1058) & (y > 754) & (y < 924)
           & (a[:, :, 3] > 128)
           & ((rgb.max(2) - rgb.min(2)) < 22)
           & (rgb.max(2) < 125) & (rgb.min(2) > 20))
components, _ = label(neutral)
lens = binary_fill_holes(components == components[840, 1023])
yy, xx = np.where(lens)
center = np.array([xx.mean(), yy.mean()])
assert len(xx) == 4989
Image.fromarray(lens.astype('uint8') * 255).save(R / 'masks/F073_ACTUAL_dark_lens_full_RAW_coordinates.png')
inside = binary_erosion(lens, iterations=2)
light = np.zeros_like(a)
light[inside, :3] = [255, 249, 211]
light[inside, 3] = 220
raw_light = Image.fromarray(light)
scene_light = Image.new('RGBA', size)
scene_light.alpha_composite(raw_light.resize((770, 924), Image.Resampling.LANCZOS), (550, 0))
scene_light.save(R / 'layers/F073_ON_actual_lens_emission_only.png')

# Whole current torch direction from visible tail-cap center toward this actual
# lens, a soft 2D emitter index rather than an internal optical measurement.
tail = np.array([483., 906.])
unit = (center - tail) / np.linalg.norm(center - tail)
normal = np.array([-unit[1], unit[0]])
scene_center = center * scale + [550, 0]
Y, X = np.indices((size[1], size[0]))
dx, dy = X - scene_center[0], Y - scene_center[1]
t = dx * unit[0] + dy * unit[1]
cross = dx * normal[0] + dy * normal[1]
half = 52 + 0.18 * np.maximum(t, 0)
shape = np.clip(1 - (cross / half) ** 2, 0, 1) ** 1.35
opacity = 0.19 * np.exp(-np.maximum(t, 0) / 690) * shape * (t >= 0)
beam = np.zeros((size[1], size[0], 4), dtype='uint8')
beam[:, :, :3] = [255, 247, 204]
beam[:, :, 3] = (opacity * 255).astype('uint8')
beam = Image.fromarray(beam).filter(ImageFilter.GaussianBlur(2))
beam.save(R / 'layers/F073_ON_soft_beam_BEHIND_actual_drawing.png')

f069 = mapped['F069']
f073 = beam.copy()
f073.alpha_composite(mapped['F073'])
f073.alpha_composite(scene_light)
f069.save(R / 'candidate/F069_ACTUAL_scene_TRANSIT_DARK.png')
f073.save(R / 'candidate/F073_ACTUAL_scene_FIRST_ON.png')
geo = {'native_output_size': [1145, 1374], 'scene_size': list(size),
       'only_whole_inverse': '770/1145 + [550,0]',
       'actual073_lens_mask_pixel_count': len(xx),
       'actual073_lens_RAW_center': center.tolist(),
       'actual073_lens_scene_center': scene_center.tolist(),
       'current_visible_tail_cap_center_RAW_soft': tail.tolist(),
       'actual073_soft_lamp_direction': unit.tolist(),
       'light_creation_only': True, 'body_or_hand_procedural_drawing': False,
       'raws_unchanged': True,
       'head_neck_077_085_not_edited': True,
       'limits': 'Whole raw scene placement only; no per-part fit, no new source-head replacement, no optical/endstop certification.'}
(R / 'geometry/ACTUAL_scene_registration_and_lens_light.json').write_text(json.dumps(geo, indent=2) + '\n')

for tone, color in [('gray', (155, 155, 155, 255)), ('dark', (35, 43, 53, 255))]:
    full = Image.new('RGB', (1672, 941 * 2 + 60), (225, 231, 238))
    hands = Image.new('RGB', (1440, 610), (225, 231, 238))
    for i, (state, im) in enumerate([('F069 TRANSIT DARK', f069), ('F073 FIRST ON', f073)]):
        bg = Image.new('RGBA', size, color)
        bg.alpha_composite(im)
        full.paste(bg.convert('RGB'), (0, i * (941 + 30) + 30))
        ImageDraw.Draw(full).text((20, i * (941 + 30) + 10), state, fill=(30, 55, 70))
        close = bg.crop((810, 475, 1315, 790)).resize((720, 570), Image.Resampling.LANCZOS)
        hands.paste(close.convert('RGB'), (i * 720, 40))
        ImageDraw.Draw(hands).text((i * 720 + 15, 12), state, fill=(30, 55, 70))
    full.save(R / 'qa' / f'F069_F073_ACTUAL_complete_scene_pair_{tone}.png')
    hands.save(R / 'qa' / f'F069_F073_ACTUAL_full_hands_slider_support_LIGHT_{tone}.png')

print(json.dumps({'F069': hashlib.sha256((R / 'candidate/F069_ACTUAL_scene_TRANSIT_DARK.png').read_bytes()).hexdigest(),
                  'F073': hashlib.sha256((R / 'candidate/F073_ACTUAL_scene_FIRST_ON.png').read_bytes()).hexdigest(),
                  'lens': geo['actual073_lens_scene_center']}))
