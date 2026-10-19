"""Read-only archive and pixel-distance verification; creates one QA record only."""
from pathlib import Path
import base64, hashlib, json, subprocess
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

P = Path(__file__).resolve().parent.parent
BASE = P.parent
sha = lambda b: hashlib.sha256(b).hexdigest()
authority = json.loads((P/'requests/authority_and_SHA_BEFORE_CALL.json').read_text())
args_file = P/'requests/arguments_call01_FINAL_EXACT.json'
args = json.loads(args_file.read_text())
old_path = BASE/'F063_pixel_plate_request_gate_991b3ea5/requests/arguments_PREPARED_NOT_CALLED.json'
root = Path(subprocess.check_output(['git','rev-parse','--show-toplevel'], cwd=P, text=True).strip())
old = json.loads(subprocess.check_output(['git','show',authority['frozen_source_commit']+':'+str(old_path.relative_to(root))], cwd=root))
assert old['prompt'].count(authority['old_sentence']) == 1
old['prompt'] = old['prompt'].replace(authority['old_sentence'], authority['replacement_sentence'])
assert args == old
assert sha(args['prompt'].encode()) == authority['prompt_final_string_SHA256']
assert sha(args_file.read_bytes()) == authority['arguments_final_file_SHA256']
inputs = []
for entry in authority['three_unchanged_inputs']:
    q = Path(entry['path'])
    b = q.read_bytes()
    assert sha(b) == entry['SHA256']
    assert b == subprocess.check_output(['git','show',authority['frozen_source_commit']+':'+str(q.relative_to(root))], cwd=root)
    inputs.append({'path': str(q.relative_to(root)), 'sha256': sha(b), 'source_commit_byte_equal': True})
state = json.loads((P/'requests/execution_state.json').read_text())
ret_bytes = (P/'requests/call01_raw_tool_return.json').read_bytes()
ret = json.loads(ret_bytes)
raw_bytes = (P/'originals/F063_pixel_plate_call01_RAW.png').read_bytes()
assert raw_bytes == Path(state['raw_host']).read_bytes() == base64.b64decode(ret['image_url'].split(',',1)[1])
assert sha(raw_bytes) == state['raw_SHA256']
assert sha(ret_bytes) == state['raw_return_SHA256']
with Image.open(P/'originals/F063_pixel_plate_call01_RAW.png') as im:
    assert im.size == (1145,1374) and im.mode == 'RGBA'
    alpha = np.array(im)[:,:,3]
R = P/'independent_review_61sol'
manifest = json.loads((R/'manifest.json').read_text())
for f in manifest['files']:
    assert sha((R/f['path']).read_bytes()) == f['sha256'], f['path']
receiver = np.array(Image.open(R/'masks/ACTUAL_receiver_alpha128_MANUAL_SEMANTIC_ROI.png')) > 0
assert not (receiver & (alpha < 128)).any()
scale = 770/1145
distances = {}
for label, name in [('actual_RAW_lamp', 'ACTUAL_propfront_alpha128_MANUAL_SEMANTIC_ROI.png'), ('actual_near_grip', 'ACTUAL_neargrip_alpha128_MANUAL_SEMANTIC_ROI.png')]:
    mask = np.array(Image.open(R/'masks'/name)) > 0
    assert not (mask & (alpha < 128)).any()
    d = float(distance_transform_edt(~mask)[receiver].min())
    distances[label] = {'raw_pixels': d, 'native_pixels': d*scale, 'overlap_pixels': int((mask & receiver).sum())}
fixed = np.array(Image.open(BASE/'F063_real_prop_pixel_plate_DIAGNOSTIC_20261019/layers/FE70_whole_visible_prop_SINGLE_RIGID_transform.png'))[:,:,3] >= 128
sy,sx = np.where(fixed)
ry,rx = np.where(receiver)
rd = cKDTree(np.column_stack((sx,sy))).query(np.column_stack((rx,ry))*scale+[550,0])[0]
distances['unresampled_fixed_original_prop'] = {'native_pixels':float(rd.min()), 'source_mask_carved_for_receiver':False}
assert abs(distances['actual_RAW_lamp']['native_pixels'] - 7.518656518230734) < 1e-9
assert abs(float(rd.min()) - 10.157281274236573) < 1e-8
result = {
    'state':'ACTUAL_REVIEW_HOLD_RECEIVER_CLEARANCE_PENDING_ASTRA_ACTION_DECISION',
    'requests':1,'originals':1,'active':0,'retries':0,'candidate_created':False,
    'archive_three_way_identical':True,'raw_sha256':sha(raw_bytes),
    'raw_return_sha256':sha(ret_bytes),'raw_dimensions':[1145,1374],
    'exact_authorized_one_sentence_replacement_verified':True,'unchanged_inputs':inputs,
    'independent_review_manifest_files_verified':len(manifest['files']),
    'independent_review_manifest_sha256':sha((R/'manifest.json').read_bytes()),
    'one_whole_uniform_inverse':{'scale':scale,'offset':[550,0],'native_crop':[550,0,1320,924]},
    'root_independent_distance_recomputation_from_saved_actual_semantic_masks':distances,
    'semantic_uncertainty_native_pixels':2*scale,'target_receiver_clearance_native_pixels':15,
    'actual_viewed_by_root':['qa/RAW_actual_alpha_composite_gray.png','qa/plate_vs_RAW_whole_registration_dark.png','qa/RAW_complete_arm_grip_receiver_gray_2x.png','independent_review_61sol/qa/ACTUAL_complete_two_arm_chains_gray.png','independent_review_61sol/qa/ACTUAL_whole_palm_lamp_and_grip_gray_3x.png','independent_review_61sol/qa/ACTUAL_whole_palm_lamp_and_grip_dark_3x.png'],
    'visual_findings':['Near sleeve, low elbow, forearm, wrist and whole grasp read continuously; receiving palm visibly clears both prop and gripping hand.', 'Requested receiver clearance is not maintained against either raw or fixed original prop. No separate fit or patch was attempted.', 'Exact slider reach and partially occluded grasp station are not certified; the partly occluded tail band is not a complete-diameter measurement.'],
    'production_mother_approved':False,'following_F069_opened':False,
}
(P/'qa/root_actual_review_HOLD.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
