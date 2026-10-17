#!/usr/bin/env python3
"""Audit untouched S30 candidate. Fixed source templates. No output image rescue."""
import hashlib
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / 'batch2_scope/pilot_preparation/measure_pilot.py'
sys.path.insert(0, str(HELPER.parent))
from measure_pilot import (grayscale_visible, match_anchor, solve_two_point_similarity,
    apply_similarity, premultiplied, rgba_array, pixel_metrics, globally_registered_for_metrics)

def evaluate(master, candidate, config):
    failures = []
    result = {'candidate_mode': candidate.mode, 'candidate_size': list(candidate.size),
        'fit_points': ['A', 'B'], 'independent_check': 'H', 'failures': failures,
        'candidate_to_master': None, 'independent_H_residual_px': None,
        'measurement_scope': 'Untouched original; no prep, body composite or rescue warp.',
        'automatic_visual_acceptance': False}
    if tuple(candidate.size) != tuple(config['canvas']):
        failures.append('canvas_mismatch')
        return result
    if candidate.mode != 'RGBA': failures.append('RGBA_required')
    ca = rgba_array(candidate)
    if not np.any(ca[:, :, 3] == 0): failures.append('transparent_background_missing')
    mg = grayscale_visible(master, config['alpha_composite_gray'])
    cg = grayscale_visible(candidate, config['alpha_composite_gray'])
    matches = {name: match_anchor(mg, cg, spec, config) for name, spec in config['anchors'].items()}
    result['matches'] = matches
    invalid = []
    for name, match in matches.items():
        if match['peak_on_search_boundary']: invalid.append(name + '_boundary_peak_invalid_match')
        if match['ncc'] < config['ncc_minimum']: invalid.append(name + '_NCC_below_frozen_minimum')
        if match['peak_margin'] < config['ncc_peak_margin_minimum']: invalid.append(name + '_ambiguous_peak')
    failures.extend(invalid)
    result['registration_valid'] = not invalid
    mp = premultiplied(rgba_array(master)); cp = premultiplied(ca)
    mask = np.zeros(mp.shape[:2], dtype=bool); mask[500:, :] = True
    result['non_target_raw'] = pixel_metrics(mp, cp, mask)
    result['protected_regions_raw'] = {}
    for name, (x0, y0, x1, y1) in config['protected_regions'].items():
        local = np.zeros_like(mask); local[y0:y1, x0:x1] = True
        result['protected_regions_raw'][name] = pixel_metrics(mp, cp, local)
    if invalid:
        result['H_status'] = 'Not reported: one or more fixed-window matches invalid. No enlarged search.'
        return result
    fit = solve_two_point_similarity([matches[n]['point'] for n in ('A', 'B')],
        [config['anchors'][n]['point'] for n in ('A', 'B')])
    result['candidate_to_master'] = fit.tolist()
    held = apply_similarity([matches['H']['point']], fit)[0]
    result['independent_H_mapped_to_master'] = held.tolist()
    residual = float(np.linalg.norm(held - np.array(config['anchors']['H']['point'])))
    result['independent_H_residual_px'] = residual
    result['H_status'] = 'Valid held-out point, not used in A/B fit.'
    scale = float(np.hypot(fit[0, 0], fit[1, 0])); rotation = math.degrees(math.atan2(fit[1, 0], fit[0, 0]))
    result['global_similarity'] = {'scale': scale, 'rotation_degrees': rotation, 'translation_xy': fit[:, 2].tolist(),
        'A_B_fit_residual_is_not_independent_evidence': True}
    if residual > config['H_residual_max_px']: failures.append('H_residual_above_3px')
    if abs(scale - 1) > config['similarity_scale_deviation_max']: failures.append('global_scale_deviation')
    if abs(rotation) > config['similarity_rotation_abs_max_deg']: failures.append('global_rotation_deviation')
    aligned = globally_registered_for_metrics(candidate, fit, mp.shape[:2])
    result['protected_regions_registered'] = {}
    for name, (x0, y0, x1, y1) in config['protected_regions'].items():
        local = np.zeros_like(mask); local[y0:y1, x0:x1] = True
        result['protected_regions_registered'][name] = pixel_metrics(mp, aligned, local)
    return result

if __name__ == '__main__':
    config = json.loads((HERE / 'measurement_config.json').read_text())
    master = Path(config['master_path'])
    if hashlib.sha256(master.read_bytes()).hexdigest() != config['master_sha256']:
        raise SystemExit('Frozen master hash mismatch.')
    candidate = HERE / 'output/x30_halfpull_onecall_original.png'
    result = evaluate(Image.open(master), Image.open(candidate), config)
    result.update({'master_sha256': config['master_sha256'], 'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'config_sha256': hashlib.sha256((HERE / 'measurement_config.json').read_bytes()).hexdigest(),
        'measurement_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_script_sha256': hashlib.sha256(HELPER.read_bytes()).hexdigest()})
    (HERE / 'candidate_measurement.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
