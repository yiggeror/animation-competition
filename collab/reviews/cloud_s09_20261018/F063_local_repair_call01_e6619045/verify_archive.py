"""Read-only archive/source checks. Never sends a generation request."""
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

P = Path(__file__).resolve().parent
REPO = P.parents[3]
COMMIT = 'e66190451f0dde828e35a351aa182c2a651d27d0'
PREFIX = 'collab/reviews/cloud_s09_20261018/F063_local_palm_input_gate_20261019/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def j(path):
    return json.loads(path.read_text())


def main():
    frozen = P / 'frozen_input_e6619045'
    for f in frozen.rglob('*'):
        if f.is_file():
            assert f.read_bytes() == subprocess.check_output(['git','show',COMMIT+':'+PREFIX+str(f.relative_to(frozen))],cwd=REPO)
    args = j(P/'requests/arguments_call01_EXACT.json')
    assert args == j(frozen/'requests/arguments_PREPARED_NOT_CALLED.json')
    assert args['prompt'] == (P/'requests/prompt_call01_EXACT.txt').read_text()
    for row in j(frozen/'package_manifest.json')['requested_images']:
        assert sha((frozen/row['path']).read_bytes()) == row['sha256']
    raw_bytes = (P/'originals/F063_local_repair_call01_RAW.png').read_bytes()
    identity = j(P/'originals/source_identity.json')
    result = j(P/'requests/call01_raw_tool_return.json')
    assert raw_bytes == base64.b64decode(result['image_url'].split(',',1)[1])
    assert sha(raw_bytes) == identity['sha256']
    host = Path(identity['host_path'])
    if host.exists():
        assert host.read_bytes() == raw_bytes
    raw = np.array(Image.open(BytesIO(raw_bytes)).convert('RGBA'))
    assert raw.shape == (1227,1282,4)
    for name in ['near_complete_arm','far_complete_arm']:
        mask = np.array(Image.open(P/f'masks/RAW_{name}_semantic_material.png'))>0
        extracted = np.array(Image.open(P/f'production_layers/RAW_{name}_EXTRACTED_ONLY.png'))
        assert np.array_equal(extracted,np.where(mask[:,:,None],raw,0))
    evidence = j(P/'qa/61sol_actual_measurement_evidence.json')
    domains = evidence['manual_material_masks_for_measurement_only']
    def domain(key):
        z=Image.new('L',(1282,1227));ImageDraw.Draw(z).polygon([tuple(v)for v in domains[key]],fill=255)
        return np.array(z)>0
    hand=domain('receiver_hand_domain_poly')&(raw[:,:,3]>=128)
    prop=domain('prop_domain_poly')&(raw[:,:,3]>=128)
    visible_gap=float(distance_transform_edt(~prop)[hand].min())
    assert abs(visible_gap-115.84903970253703)<1e-9
    mother=np.array(Image.open(frozen/'sources/F044_fe70_PRODUCTION_MOTHER_ARCHIVE_NOT_REQUEST.png').convert('RGBA'))
    trial=np.array(Image.open(P/'candidate/F063_frozen044_arm_registration_TRIAL_NOT_ACCEPTED.png').convert('RGBA'))
    hard=np.array(Image.open(P/'masks/F044_exact_head_ruffle_skirt_protection.png'))>0
    assert np.array_equal(trial[hard],mother[hard])
    for row in j(P/'adoption_sources/snapshot_manifest.json')['files']:
        assert sha((P/'adoption_sources'/row['path']).read_bytes())==row['sha256']
    state=j(P/'requests/execution_state.json')
    assert state['local_repair_requests_sent']==state['local_repair_originals_received']==1
    assert state['automatic_retry_authorized'] is False and state['F069_unopened'] is True
    delivery=P/'DELIVERY_SHA256.json'
    if delivery.exists():
        for row in j(delivery)['files']:
            assert sha((P/row['path']).read_bytes())==row['sha256'],row['path']
    print(json.dumps({'status':'PASS_ARCHIVE_AND_SOURCE_CHECKS_PRODUCTION_TRIAL_REMAINS_HOLD','local_requests':1,'local_originals':1,'raw_visible_gap_alpha128_pixel_centers':visible_gap,'frozen044_protected_pixels_verified':int(hard.sum()),'frozen044_protected_RGBA_changes':0,'new_raw_head_face_adopted':False,'finished_candidate_accepted':False,'F069_unopened':True}))


if __name__=='__main__':
    main()
