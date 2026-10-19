"""Read-only corrected input verification. No failed raw or generation reads."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
REPO=P.parents[3]
COMMIT='aba2cbcac5dfa10cb68d1098f9bed16ba4da2383'
PREFIX='collab/reviews/cloud_s07_walk_20261018/F090_next_gate_20261019/'


def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest=json.loads((P/'package_manifest.json').read_text())
    for row in manifest['files']:
        assert sha((P/row['path']).read_bytes())==row['sha256'],row['path']
    sm=json.loads((P/'sources/snapshot_manifest.json').read_text())
    mappings={'approved_geometry_preparation_checks.json':'geometry/preparation_checks.json','approved_prepare.py':'prepare.py','approved_sources_snapshot_manifest.json':'sources/snapshot_manifest.json'}
    prefixes={'approved_reference_native/':'reference_native/','approved_inputs_1024x1536/':'inputs_1024x1536/','approved_layers/':'layers/','approved_original_source_archive_NOT_REQUEST/':'sources/'}
    git_verified=0
    for row in sm['files']:
        data=(P/'sources'/row['path']).read_bytes()
        assert sha(data)==row['sha256']
        if row['path']=='authority_20261019.txt':
            # New parent direction is an authority record, not an old git source.
            continue
        source=mappings.get(row['path'])
        for k,v in prefixes.items():
            if row['path'].startswith(k):source=v+row['path'][len(k):]
        assert source is not None,row['path']
        assert data==subprocess.check_output(['git','show',COMMIT+':'+PREFIX+source],cwd=REPO),row['path']
        git_verified+=1
    native=P/'sources/approved_reference_native'
    old_a=rgba(native/'A_real_five_layers_no_old_pants_540x810.png')
    old_c=rgba(native/'C_complete_new_landing_volume_TECHNICAL_NOT_ART_540x810.png')
    new_a=rgba(P/'reference_native/A_real_layers_plus_approved_volume_NOT_ART_540x810.png')
    real=old_a[:,:,3]>0
    assert np.array_equal(old_a[real],new_a[real])
    volume=rgba(P/'reference_native/approved_C_literal_volume_RGBA.png')
    vm=np.array(Image.open(P/'masks/approved_C_literal_technical_volume.png'))>0
    insert=np.array(Image.open(P/'masks/volume_inserted_ONLY_IN_A_EMPTY.png'))>0
    white=np.array(Image.open(P/'masks/WHITE_approved_neutral.png'))>0
    assert np.array_equal(volume[vm],old_c[vm])
    assert np.array_equal(new_a[insert],old_c[insert])
    assert np.array_equal(insert,vm&~real) and int(insert.sum())==53340
    assert not (vm&~white&~real).any()
    source_input=P/'sources/approved_inputs_1024x1536'
    old_ar=rgba(source_input/'A_whole_canvas_256over135_PREPARED.png')
    new_ar=rgba(P/'inputs_1024x1536/A_real_fixed_layers_plus_volume_NOT_ART_PREPARED.png')
    assert np.array_equal(old_ar[old_ar[:,:,3]>0],new_ar[old_ar[:,:,3]>0])
    for key in ['B','D']:
        assert (P/f'reference_native/{key}_APPROVED_BYTE_IDENTICAL_540x810.png').read_bytes()==(native/({'B':'B_neutral_edit_reference_540x810.png','D':'D_real057_062_interior_fabric_NO_FIGURE_540x810.png'}[key])).read_bytes()
        assert (P/f'inputs_1024x1536/{key}_APPROVED_BYTE_IDENTICAL_PREPARED.png').read_bytes()==(source_input/f'{key}_whole_canvas_256over135_PREPARED.png').read_bytes()
    layers=list((P/'production_reference_layers').glob('*.png'))
    assert len(layers)==5
    for f in layers:
        assert f.read_bytes()==(P/'sources/approved_layers'/f.name).read_bytes()
    args=json.loads((P/'requests/arguments_PREPARED_NOT_CALLED.json').read_text())
    assert args['prompt']+'\n'==(P/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text()
    assert len(args['referenced_image_paths'])==4 and args['transparent_background'] is True
    assert all(Image.open(path).size==(1024,1536) for path in args['referenced_image_paths'])
    assert not (P/'requests/execution_state.json').exists()
    print(json.dumps({'status':'PASS_CORRECTED_INPUT_PREPARATION_ONLY_PENDING_ASTRA','approved_source_files_equal_git':git_verified,'five_real_layers_byte_exact':5,'B_D_native_and_request_byte_exact':True,'A_real_RGBA_changes_native_and_request':[0,0],'literal_approved_C_volume_insert_pixels':53340,'unprotected_volume_outside_white':0,'new_image_calls':0,'failed_raw_pose_used':False,'F095_unopened':True}))


if __name__=='__main__':main()
