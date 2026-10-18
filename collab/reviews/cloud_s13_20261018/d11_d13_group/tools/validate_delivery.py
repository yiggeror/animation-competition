#!/usr/bin/env python3
"""Validate drawing provenance/timing; semantic drawing review is manual."""
from pathlib import Path
from PIL import Image
import ast
import hashlib
import json
import re
import subprocess

P = Path(__file__).resolve().parents[1]
R = P.parent
REPO = R.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
locked = {
    'd01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png': '91715601ae814bd84a3dc8d6ce43f1cc809a7bdd74e7390fefffe579f6882050',
    'd02_d04_segment/approved_local/F018_d02_eyes_up.png': '306ac1e2013a020b6a2e177d150f58ca34d1b17cdbbfc5488f166013dc06cd7e',
    'd02_d04_segment/approved_local/F024_d03_whole_head_right.png': 'c04f4fcc60e6539cd7de3048e692a1986866e24cfffe4c702f03538c19decd5e',
    'd02_d04_segment/approved_local/F030_d04_awake_closed_mouth.png': '994b085de94c9accbadfd9dea858aaa41814376ce42280b6a3c5fb3846b9f590',
    'd05_d07_segment/approved_local/F036_d05_pretend_drowsy.png': '6031e55e4b60d5ce61ef6064a01b9c09e4736477cad5611d91f3c2b1112332e9',
    'd05_d07_segment/approved_local/F040_d06_yawn_start.png': 'b077b6e0b759f1965f1e2d9499c8a3760ca4e3ffb19fc68e574160bafd546be6',
    'd05_d07_segment/approved_local/F044_d07_yawn_opening.png': '93ca7ffbb96bec1add190c170904886d8cdb316df38cbfa337c1a8cf2bc87fff',
    'd08_d10_group/approved_local/F050_d08_yawn_peak.png': 'f14a522b0bd007ced18ab37fb0abaa25cfdca37a31309bc4c7271091d130c897',
    'd08_d10_group/approved_local/F058_d09_sustained_breath.png': '689689322eed3ef9999754de862eab47190de7c177432a747caf271d52236a4d',
    'd08_d10_group/approved_local/F068_d10_yawn_release.png': 'b64b67f0262596c1dc150f71b9dce05e14aa12589a8214f2cc4612dd685a00be',
}
for path, expected in locked.items():
    p = R / path
    assert sha(p) == expected, path
    committed = subprocess.check_output(['git', 'show', '9ed9d4fe:' + str(p.relative_to(REPO))], cwd=REPO)
    assert p.read_bytes() == committed, path

ledger = json.loads((R / 'provenance/generation_ledger.json').read_text())
assert ledger['image_generation_requests'] == ledger['successful_raw_images'] == len(ledger['raw_outputs']) == 15
assert ledger['unique_adopted_pose_count'] == 13 and ledger['rejected_raw_outputs'] == 2
assert ledger['isolated_PNG_layer_previews'] == 4
new = ledger['raw_outputs'][-3:]
expected_new = [
    '65414abf51e5332d60519d47ca8a41fdc12d3c3b279183765c8030df8f39838b',
    '86c9623ef72008bbbd1bc6730c7f3b99c6a08fdfa05443c4ff73bb5a3b886b73',
    '29418e08e7b0285fb8690add34878d600532c8a1d39f55379a915ffbca570660',
]
source = R / list(locked)[-1]
for n, (row, expected) in enumerate(zip(new, expected_new), 13):
    req = json.loads((P / f'requests/call_{n:03}_request.json').read_text())
    resp = json.loads((P / f'requests/call_{n:03}_response.json').read_text())
    meta = json.loads((P / f'requests/call_{n:03}_tool_return_metadata.json').read_text())
    assert req['args']['referenced_image_paths'] == [str(source)]
    assert req['dependency_sha256'] == sha(source) == resp['inputs'][0]['sha256']
    assert req['args']['transparent_background'] is True and req['args']['prompt']
    raw, out, default = R / row['path'], R / row['adopted_output'], Path(row['source_tool_path'])
    assert sha(raw) == sha(out) == sha(default) == expected == resp['raw_sha256']
    assert resp['tool_original_path'] in meta['output_hint']
    with Image.open(out) as im:
        im.load()
        assert im.mode == 'RGBA' and im.size == (1024, 1536)
    source = out

plan = json.loads((R / 'geometry/S13_reference_plan.json').read_text())
keys = plan['keys']
assert plan['frames'] == sum(k['hold'] for k in keys) == 120
assert plan['fps'] == 24 and plan['drawing_count'] == len(keys) == 16
assert [(k['f'], k['hold'], k['head_yaw_deg']) for k in keys[10:13]] == [(78, 6, 24), (84, 3, 24), (87, 3, 8)]
assert keys[11]['mouth_aperture_H'] == keys[12]['mouth_aperture_H'] == 0
assert keys[15]['f'] == 100 and keys[15]['hold'] == 20
assert all(a['f'] + a['hold'] == b['f'] for a, b in zip(keys, keys[1:]))
ex = json.loads((P / 'qa/exposure_90f_validation.json').read_text())
assert ex['frames'] == 90 and ex['fps'] == '24/1' and ex['audio_streams'] == 0
assert ex['timeline'][-3:] == [[78, 6], [84, 3], [87, 3]] and ex['d14_present'] is False
assert [r['frame'] for r in ex['decode_checks']] == [68, 77, 78, 83, 84, 86, 87, 89]
assert all(r['expected'] == r['decoded_nearest'] for r in ex['decode_checks'])
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(P / 'qa/isolated_90f_through_d13.mp4')], text=True))
assert len(probe['streams']) == 1
s = probe['streams'][0]
assert s['nb_frames'] == '90' and s['r_frame_rate'] == '24/1' and (s['width'], s['height']) == (1280, 720)

for p in R.rglob('*.json'):
    json.loads(p.read_text())
for p in R.rglob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
images = list(R.rglob('*.png')) + list(R.rglob('*.jpg'))
for p in images:
    with Image.open(p) as im:
        im.verify()
for md in [R / 'README.md', P / 'README.md', R / 'd08_d10_group/README.md']:
    for link in re.findall(r'\]\(([^)]+)\)', md.read_text()):
        if not link.startswith(('http:', 'https:', '#')):
            assert (md.parent / link.split('#')[0]).exists(), (md, link)

result = {
    'status': 'PASS', 'locked_drawings_unchanged': 10, 'native_new_outputs_equal_raw_and_tool_default': 3,
    'strict_chain': 'locked_d10→d11→d12→d13', 'canvas_RGBA': [1024, 1536],
    'reference_frames': 120, 'reference_states': 16, 'F100_unchanged': True,
    'isolated_preview_frames': 90, 'fps': 24, 'audio_streams': 0,
    'decoded_boundary_frames': [68, 77, 78, 83, 84, 86, 87, 89],
    'all_delivery_images_decodable': len(images), 'JSON_and_Python_parse': True, 'README_relative_links': True,
    'manual_semantic_review': 'Actual same-scale drawings, mouth/jaw/neck closeups, three alpha bases and decoded boundaries viewed. F084–086 fully closed before F087 whole-head turn.',
    'not_verified': ['Canvas scene', 'scene lighting', 'audio', 'd14–d16', 'full S13'],
}
(P / 'qa/delivery_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
