"""Read-only independent checks for the zero-call local input gate."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, label

P = Path(__file__).resolve().parent
OWN = P.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))


def mask(name):
    return np.array(Image.open(P / 'masks' / name).convert('L')) > 0


def nearest(moving, fixed):
    distance = distance_transform_edt(~fixed)
    return float(distance[moving].min())


def main():
    manifest = json.loads((P / 'package_manifest.json').read_text())
    for row in manifest['files']:
        assert sha(P / row['path']) == row['sha256'], row['path']
    source_pairs = {
        'F063_call01_RAW_UNCHANGED.png': 'F063_native_call01_b01dc6c/originals/F063_call01_RAW.png',
        'F044_fe70_PRODUCTION_MOTHER_ARCHIVE_NOT_REQUEST.png': 'first_tap_segment/F044_rebound_gate/candidate/F044_complete_local_native_arm_PENDING_ASTRA.png',
        'F044_NATIVE_GUARD_head_neck_collar_actual.png': 'F063_rebuilt_volume_input_gate_20261019/sources/F044_actual_head_neck_collar_guard.png',
        'F044_NATIVE_GUARD_near_ruffle_actual_material.png': 'F063_rebuilt_volume_input_gate_20261019/sources/F044_actual_stable_near_ruffle_guard.png',
        'F044_NATIVE_GUARD_waist_and_skirt_actual_material.png': 'first_tap_segment/F044_rebound_gate/masks/waist_and_skirt_actual_material.png',
        'F044_NATIVE_GUARD_far_puff_actual_visible.png': 'first_tap_segment/F044_rebound_gate/masks/far_puff_actual_visible.png',
    }
    for target, source in source_pairs.items():
        assert (P / 'sources' / target).read_bytes() == (OWN / source).read_bytes(), target
    raw = rgba(P / 'sources/F063_call01_RAW_UNCHANGED.png')
    a = rgba(P / 'reference/A_same_raw_whole_hand_down49_FULL_CONTEXT_NOT_PRODUCTION.png')
    source = rgba(P / 'reference/source_complete_visible_far_hand_RGBA.png')
    target = rgba(P / 'reference/target_same_whole_hand_INTEGER_dy49_RGBA.png')
    hand = mask('source_complete_visible_far_hand_material.png')
    moved = mask('target_same_complete_hand_down49_material.png')
    white = mask('WHITE_complete_far_forearm_old_new_hand_air.png')
    hard = mask('HARD_local_context_actual_visible_material.png')
    near = mask('source_near_arm_and_grasp_actual_material_HARD.png')
    prop = mask('source_actual_prop_visible_material.png')
    silver = mask('silver_lower_rim_local_allowed_UNKNOWN_BEHIND_OLD_FINGERS.png')
    b = np.array(Image.open(P / 'reference/B_complete_far_forearm_and_hand_WHITE_REFERENCE.png'))
    assert raw.shape == a.shape == source.shape == target.shape == (1227, 1282, 4)
    assert np.array_equal(source, np.where(hand[:, :, None], raw, 0))
    expected = np.zeros_like(source)
    expected[49:] = source[:-49]
    assert np.array_equal(target, expected) and not hand[-49:].any()
    assert np.array_equal(moved, target[:, :, 3] > 0)
    assert int(hand.sum()) == int(moved.sum()) == 22088
    assert np.array_equal(b, white.astype('uint8') * 255)
    changed = np.any(a != raw, axis=2)
    assert not (changed & ~white).any()
    assert not (near & white).any() and not (hard & white).any()
    assert not (hard & (raw[:, :, 3] == 0)).any()
    assert not (moved & ~white).any() and not (moved & prop).any() and not (moved & near).any()
    for x, y in [(750, 1020), (980, 815), (1120, 799), (1110, 714)]:
        assert white[y, x], (x, y)
    yy, xx = np.where(silver)
    assert xx.min() >= 1080 and xx.max() <= 1230 and yy.min() >= 690 and yy.max() <= 755
    _, components = label(white)
    distances = {'all_known_prop': nearest(moved, prop), 'near_grasp': nearest(moved, near), 'known_prop_except_allowed_silver': nearest(moved, prop & ~silver)}
    assert abs(distances['all_known_prop'] - 32.7566787083184) < 1e-10
    assert abs(distances['near_grasp'] - 66.84309986827361) < 1e-10
    assert abs(distances['known_prop_except_allowed_silver'] - 41.14608122288197) < 1e-10
    args = json.loads((P / 'requests/arguments_PREPARED_NOT_CALLED.json').read_text())
    assert args['prompt'] + '\n' == (P / 'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text()
    assert args['transparent_background'] is True
    assert len(args['referenced_image_paths']) == 2
    assert not (P / 'requests/execution_state.json').exists()
    print(json.dumps({'status': 'PASS_ZERO_CALL_PREPARATION_ONLY_PENDING_ASTRA', 'source_snapshots_byte_exact': len(source_pairs), 'whole_hand_pixels': int(hand.sum()), 'single_integer_translation': [0, 49], 'white_pixels': int(white.sum()), 'white_connected_components_including_edge_specks': components, 'outside_white_changes': 0, 'near_grasp_white_overlap': 0, 'hard_alpha0': 0, 'current_visible_material_pixel_center_distances': distances, 'new_image_calls': 0, 'unknown_occluded_silver_restored': False, '044_final_registration_and_seams_verified': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
