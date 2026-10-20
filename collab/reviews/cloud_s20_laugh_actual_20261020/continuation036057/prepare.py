"""Consume six adopted drawings; register only original turtle and finite props.

Run from repo root after the geometry-only model probe. No people are generated
or transformed. Earlier world lengths were not frozen: retain each adopted
visible finite shaft endpoint, and disclose the resulting world registration.
"""
from pathlib import Path
import copy
import hashlib
import io
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_closing, binary_dilation, binary_fill_holes, binary_opening, label
from scipy.optimize import root

P = Path(__file__).resolve().parent
ASSETS = Path('assets/chars/g20')
REV = '86cd914a919c84fe2aec9583e66ddca8d8d550aa'
BASE = 'collab/reviews/cloud_s20_20261018/'
probe = json.loads((P / 'model_probe.json').read_text())
frozen = json.loads((ASSETS / 'frozen_stage.json').read_text())
binding = json.loads((P.parent / 'integration_000_143/036_057_exposure.adopted.json').read_text())

def get(path):
    return subprocess.check_output(['git', 'show', REV + ':' + path])

def read(path):
    return json.loads(get(BASE + path))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

b = probe['camera_basis']
C, right, up, fwd = [np.array(b[k]) for k in ['C', 'right', 'up', 'fwd']]
focal = b['focal']
pm = np.array(probe['pm'])
reg = probe['reg']
base = np.array(reg['base_world_m'])

def project(p):
    d = np.array(p) - C
    return np.array([960 + focal * (d @ right) / (d @ fwd), 540 - focal * (d @ up) / (d @ fwd)])

def master(p):
    return np.linalg.solve(np.array([[pm[0], pm[2]], [pm[1], pm[3]]]), np.array(p) - pm[4:])

def world(p):
    return base + right * ((p[0] - reg['ox']) / reg['pixels_per_cm'] / 100) + up * ((reg['oy'] - p[1]) / reg['pixels_per_cm'] / 100)

def card(rt, pt):
    q0 = project([rt[0], .004, rt[1]])
    qx = project([rt[0] + .1, .004, rt[1]])
    qz = project([rt[0], .004, rt[1] + .1])
    return q0 - (qx - q0) * pt[0] / 100 + (qz - q0) * pt[1] / 100

def on_sheet(p):
    ray = fwd + right * ((p[0] - 960) / focal) + up * ((540 - p[1]) / focal)
    return C + ray * ((.004 - C[1]) / ray[1])

def rotate(p, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [c * p[0] - s * p[1], s * p[0] + c * p[1]]

old_c = read('cam20_crane_lamp_left_001/registration_input.json')['rods']
q39 = read('F039_whole_source_diagnostic_001/uniform_transform_and_clamps.json')
q42 = read('continuation_042_054_generation_001/F042/semantic_closed_registration.json')
q54 = read('continuation_042_054_generation_001/F054/receipt_and_protection.json')
write(P / 'native039_registration.adopted.json', q39)
write(P / 'native042_registration.adopted.json', q42)
write(P / 'native054_registration.adopted.json', q54)
write(P / 'model_probe.json', probe)
records = []
states = []

for hold in binding['holds']:
    key = hold['state']
    raw = get(hold['file'])
    assert hashlib.sha256(raw).hexdigest() == hold['sha256']
    A = np.array(Image.open(io.BytesIO(raw)).convert('RGBA'))
    H, W = A.shape[:2]
    y, x = np.indices((H, W))
    if key == 36:
        axes = []
        for role in ['T_H', 'T_S']:
            q = frozen['registration']['rods'][role]
            axes.append({'id': role, 'slope': q['slope'], 'intercept': q['intercept'], 'front': q['shaft_tip_master_px'], 'tail': [944, q['slope'] * 944 + q['intercept']]})
        geometry = {'turtle': {'root': frozen['geometry']['turtle_root_m'], 'pose': frozen['geometry']['puppet_poses']['turtle']}, 'rods': []}
        for i, role in enumerate(['T_H', 'T_S']):
            old = frozen['geometry']['rod_endpoints'][i + 2]
            st = probe['states']['frozen0']
            a = on_sheet(card(st['root'], st['points'][role]))
            end = world(old['grip_master_px'])
            geometry['rods'].append({'id': role, 'part': old['part'], 'at': old['at'], 'A_world': a.tolist(), 'end_world': end.tolist(), 'length_m': float(np.linalg.norm(end - a))})
        rationale = '036 retains the exact000–035 original turtle and finite endpoints; the child slides on the same shafts.'
    else:
        if key == 39:
            axes = []
            for row in q39['same_two_shaft_rigid_layer_test']['shafts']:
                a, z = row['ends_px']
                slope = (z[1] - a[1]) / (z[0] - a[0])
                axes.append({'id': row['role'], 'slope': slope, 'intercept': a[1] - slope * a[0], 'front': a, 'tail': z, 'clamp': row['new_clamp_px']})
            m = np.array(q39['same_two_shaft_rigid_layer_test']['matrix_2x3'])
            target = float((m[:, :2] @ np.array(frozen['geometry']['rod_endpoints'][2]['master_px']) + m[:, 2])[0])
            anchor_id = 'T_H'
        else:
            table = q54 if key == 54 else q42
            axes = copy.deepcopy(table['native_T_axes'])
            target = axes[1]['front'][0]
            anchor_id = 'T_S'
        # 045/047 retain the exact adopted042 child, hence one turtle hold.
        source_frame = 42 if key in [45, 47] else key
        st = probe['states'][str(source_frame)]
        points = st['points']
        def residual(v):
            pp = {k: rotate(p, v[2]) for k, p in points.items()}
            out = []
            for role, axis in zip(['T_H', 'T_S'], axes):
                p = master(card(v[:2], pp[role]))
                out.append((p[1] - axis['slope'] * p[0] - axis['intercept']) / math.hypot(1, axis['slope']))
            out.append(master(card(v[:2], pp[anchor_id]))[0] - target)
            return out
        fit = root(residual, [st['root'][0], st['root'][1], .3 - st['pose']['rootAngle']])
        assert fit.success
        pose = copy.deepcopy(st['pose'])
        pose['rootAngle'] += float(fit.x[2])
        geometry = {'turtle': {'root': fit.x[:2].tolist(), 'pose': pose}, 'rods': [], 'nativeAxisResidualMasterPx': residual(fit.x)}
        for i, axis in enumerate(axes):
            role = axis.get('id', ['T_H', 'T_S'][i])
            a_screen = card(fit.x[:2], rotate(points[role], fit.x[2]))
            a = on_sheet(a_screen)
            end = world(axis['tail'])
            geometry['rods'].append({'id': role, 'part': 'head' if role == 'T_H' else 'shell', 'at': [20, 0] if role == 'T_H' else [0, 40], 'A_world': a.tolist(), 'end_world': end.tolist(), 'A_master': master(a_screen).tolist(), 'end_master': axis['tail'], 'length_m': float(np.linalg.norm(end - a))})
        rationale = 'Original1.3 turtle, unchanged internal pose; whole root/rotation registered to the two actual adopted finite axes.039 uses its rigid-pair reference;042+ binds shell to its visible finite front. No source input palm target or world-length historical-freeze claim.'
    # Engineering guides only. Skin/ink envelopes remain native and untouched.
    rr, gg, bb = A[:, :, :3].astype(float).transpose(2, 0, 1)
    wood = (A[:, :, 3] > 0) & (rr > 30) & (rr > gg + 7) & (gg > bb + 7) & (bb < gg * .80)
    skin = (A[:, :, 3] > 0) & (rr > 165) & (gg > 110) & (bb > gg * .70) & (rr > gg + 10)
    cores, _ = label(binary_opening(A[:, :, 3] > 160, iterations=4))
    sizes = np.bincount(cores.ravel())
    solid = (cores > 0) & (sizes[cores] > 1000)
    skin_ids, skin_count = label(skin)
    touching = np.unique(skin_ids[binary_dilation(solid, iterations=5) & skin])
    touching = touching[touching > 0]
    native_skin = np.isin(skin_ids, touching)
    protected = binary_dilation(binary_fill_holes(binary_closing(native_skin, iterations=2)), iterations=3)
    protected |= binary_dilation(solid, iterations=4)
    corridors = np.zeros((H, W), dtype=bool)
    for axis in axes:
        m, b0 = axis['slope'], axis['intercept']
        lo = min(axis['front'][0], axis['tail'][0]) - 5
        hi = max(axis['front'][0], axis['tail'][0]) + 5
        corridors |= (x >= lo) & (x <= hi) & (np.abs(y - m * x - b0) / math.hypot(1, m) < 7)
    for role in ['C_B', 'C_N']:
        q = old_c[role]
        corridors |= (x >= 670) & (x <= 956) & (np.abs(y - q['slope'] * x - q['intercept']) / math.hypot(1, q['slope']) < 7)
    # Include AA guide pixels regardless of hidden RGB; solid native silhouettes
    # and all skin envelopes are protected before clearing this exterior mask.
    erase = corridors & (A[:, :, 3] > 0) & ~protected
    B = A.copy()
    B[erase] = 0
    assert np.array_equal(B[~erase], A[~erase])
    assert np.array_equal(B[protected], A[protected])
    mask = P / f'F{key:03}_engineering_only_mask.png'
    Image.fromarray(erase.astype('uint8') * 255).save(mask)
    name = f'F{key:03}_people.png'
    Image.fromarray(B).save(ASSETS / name)
    geometry['registrationRationale'] = rationale
    geometry['originalTurtleScale'] = 1.3
    geom_name = f'F{key:03}_geometry.json'
    write(ASSETS / geom_name, geometry)
    states.append({'key': key, 'start': hold['start_inclusive'], 'end': hold['end_exclusive'] - 1, 'people': name, 'geometry': geom_name, 'stage': 'turn_and_crane_handoff'})
    records.append({'key': key, 'sourceCommit': REV, 'source': hold['file'], 'sourceSHA256': hold['sha256'], 'production': name, 'productionSHA256': hashlib.sha256((ASSETS / name).read_bytes()).hexdigest(), 'removedEngineeringPixels': int(erase.sum()), 'protectedNativeSkinUnchanged': True, 'allOtherPixelsUnchanged': True, 'newImageCalls': 0})
write(P / 'source_and_cleanup.json', records)
q = json.loads((ASSETS / 'sequence.json').read_text())
q['states'] = sorted([s for s in q['states'] if s['key'] < 36 or s['key'] > 57] + states, key=lambda s: s['start'])
q['availableIntervals'] = [[0, 57]] + ([[132, 143]] if q['closure'].get('child') else [])
q['publicExposureIntervalsNotYetIntegrated'] = []
q['missingExposure'] = '058–131 new candidate package received; actual native shaft measurements and original-scene consumption still pending.'
write(ASSETS / 'sequence.json', q)
print('Prepared six adopted whole drawings and22 explicit exposures; no person transform or image call.')
