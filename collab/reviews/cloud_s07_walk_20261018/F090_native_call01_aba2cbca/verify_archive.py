"""Read-only verification; no image generation, fitting or source rewriting."""
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import json
import subprocess

import numpy as np
from PIL import Image
from scipy.ndimage import label

P = Path(__file__).resolve().parent
REPO = P.parents[3]
FROZEN = P / 'frozen_input_aba2cbca'
AUTHORITY = 'aba2cbcac5dfa10cb68d1098f9bed16ba4da2383'
PREFIX = 'collab/reviews/cloud_s07_walk_20261018/F090_next_gate_20261019/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get_json(path):
    return json.loads(path.read_text())


def git_bytes(path):
    return subprocess.check_output(['git', 'show', AUTHORITY + ':' + path], cwd=REPO)


def sole_material(im):
    a = np.array(im.convert('RGBA'))
    rgb = a[:, :, :3].astype(np.int16)
    mask = (a[:, :, 3] >= 128) & (rgb.min(axis=2) > 145) & (np.ptp(rgb, axis=2) < 65)
    mask[:735] = False
    mask[790:] = False
    labs, count = label(mask)
    rows = []
    for n in range(1, count + 1):
        y, x = np.where(labs == n)
        if len(x) > 150:
            rows.append({'pixels': len(x), 'bbox_native_crop_local_halfopen': [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1], 'centroid_xy': [float(x.mean()), float(y.mean())]})
    return sorted(rows, key=lambda row: row['centroid_xy'][0])


def main():
    state = get_json(P / 'requests/execution_state.json')
    assert state['requests_sent'] == state['originals_received'] == 1
    assert state['automatic_retry_authorized'] is False and state['F095_unopened'] is True
    manifest = get_json(FROZEN / 'package_manifest.json')
    for row in manifest['files']:
        data = (FROZEN / row['path']).read_bytes()
        assert ('bytes' not in row or len(data) == row['bytes']) and sha(data) == row['sha256'], row['path']
        assert data == git_bytes(PREFIX + row['path']), row['path']
    assert (FROZEN / 'package_manifest.json').read_bytes() == git_bytes(PREFIX + 'package_manifest.json')
    args = get_json(P / 'requests/arguments_call01_EXACT.json')
    assert args == get_json(FROZEN / 'requests/arguments_PREPARED_NOT_CALLED.json')
    assert args['prompt'] == (P / 'requests/prompt_call01_EXACT.txt').read_text()
    # Frozen human-readable draft has one terminal newline; actual JSON prompt does not.
    assert args['prompt'] + '\n' == (FROZEN / 'requests/prompt_DRAFT_PENDING_ASTRA_NOT_CALLED.txt').read_text()
    for path, row in zip(args['referenced_image_paths'], manifest['requested_images']):
        assert Path(path).read_bytes() == (FROZEN / row['path']).read_bytes()
    raw_bytes = (P / 'originals/F090_call01_RAW.png').read_bytes()
    identity = get_json(P / 'originals/source_identity.json')
    raw_return = get_json(P / 'requests/call01_raw_tool_return.json')
    assert raw_bytes == base64.b64decode(raw_return['image_url'].split(',', 1)[1])
    assert sha(raw_bytes) == identity['sha256']
    host = Path(identity['host_path'])
    host_verified = host.exists()
    if host_verified:
        assert host.read_bytes() == raw_bytes
    raw = Image.open(BytesIO(raw_bytes)).convert('RGBA')
    assert raw.size == (1024, 1536)
    # Fixed approved whole inverse, never fit to the generated shoes.
    actual = raw.resize((540, 810), Image.Resampling.LANCZOS)
    a = Image.open(FROZEN / 'reference_native/A_real_five_layers_no_old_pants_540x810.png')
    expected_rows = sole_material(a)
    actual_rows = sole_material(actual)
    evidence = get_json(P / 'qa/actual_visible_sole_material_registration_HOLD.json')
    assert expected_rows == evidence['frozen_A'] and actual_rows == evidence['actual_raw']
    delta = [[actual_rows[i]['centroid_xy'][j] - expected_rows[i]['centroid_xy'][j] for j in range(2)] for i in range(2)]
    assert delta == evidence['actual_minus_frozen_native_crop_local_centroid_delta']
    assert abs(delta[0][0]) > 45 and abs(delta[1][0]) > 35
    delivery = P / 'DELIVERY_SHA256.json'
    if delivery.exists():
        for row in get_json(delivery)['files']:
            assert sha((P / row['path']).read_bytes()) == row['sha256'], row['path']
    print(json.dumps({'status': 'PASS_ARCHIVE_CHECKS_OUTPUT_REMAINS_HOLD', 'frozen_files_verified': len(manifest['files']), 'host_available_and_verified': host_verified, 'requests': 1, 'originals': 1, 'sole_material_delta_native_px': delta, 'candidate_adopted': False, 'F095_unopened': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
