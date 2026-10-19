"""Independent source/one-transform/fixed-backplate verification; no new art."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
REPO=P.parents[3]
OWN=REPO/'collab/reviews/cloud_s09_20261018'


def j(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def rgba(path):return np.array(Image.open(path).convert('RGBA'))
def mask(name):return np.array(Image.open(P/'masks'/name).convert('L'))>0


def main():
    for row in j(P/'package_manifest.json')['files']:
        assert sha((P/row['path']).read_bytes())==row['sha256'],row['path']
    S=P/'sources'
    for row in j(S/'snapshot_manifest.json')['files']:
        assert sha((S/row['path']).read_bytes())==row['sha256'],row['path']
    exact_sources={
        'F026_original_coordinate_clothing_BACKPLATE.png':'post058_switch_preparation_20261018/sources/F026_OFF_reset.png',
        'F044_frozen_production_mother_REFERENCE_ONLY.png':'first_tap_segment/F044_rebound_gate/candidate/F044_complete_local_native_arm_PENDING_ASTRA.png',
        'F063_local_repair_RAW_same_source.png':'F063_local_repair_call01_e6619045/originals/F063_local_repair_call01_RAW.png',
        'F044_same_rigid_grip_torch_SOURCE.png':'F063_rebuilt_volume_input_gate_20261019/sources/F044_same_rigid_grip_torch_SOURCE.png',
        'F044_actual_complete_old_near_arm_mask.png':'F063_rebuilt_volume_input_gate_20261019/sources/F044_actual_complete_old_near_arm_mask.png',
        'F044_actual_head_neck_collar_guard.png':'F063_rebuilt_volume_input_gate_20261019/sources/F044_actual_head_neck_collar_guard.png',
        'F044_actual_stable_near_ruffle_guard.png':'F063_rebuilt_volume_input_gate_20261019/sources/F044_actual_stable_near_ruffle_guard.png',
        'F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png':'F063_rebuilt_volume_input_gate_20261019/sources/F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png',
        'F063_frozen_target_geometry.json':'F063_rebuilt_volume_input_gate_20261019/geometry/preparation_checks.json',
    }
    for target,source in exact_sources.items():
        assert (S/target).read_bytes()==(OWN/source).read_bytes(),target
    # Exact donor authority is a committed original, not an image chosen by fit.
    donor_path='collab/reviews/cloud_s09_20261018/post058_switch_preparation_20261018/sources/F026_OFF_reset.png'
    assert (S/'F026_original_coordinate_clothing_BACKPLATE.png').read_bytes()==subprocess.check_output(['git','show','3764f0d36f19544d3365344565207ced7e456fcd:'+donor_path],cwd=REPO)
    g=j(P/'geometry/registration_and_source_checks.json')
    m=np.array(g['single_similarity']['M']);t=np.array(g['single_similarity']['t']);s=g['single_similarity']['scale']
    assert np.allclose(m.T@m,np.eye(2)*s*s,atol=1e-14) and np.linalg.det(m)>0
    for key,dest in [('T_tail_ellipse_center','frozen_target_T'),('L_lamp_ellipse_center','frozen_target_L')]:
        assert np.allclose(m@np.array(g['source_axis_points_manual'][key])+t,g[dest],atol=1e-9)
    raw=rgba(S/'F063_local_repair_RAW_same_source.png')
    selected=mask('raw_same_source_all_group.png')
    source=rgba(P/'candidate/SOURCE_same_raw_complete_visible_arms_grasp_prop.png')
    assert np.array_equal(source,np.where(selected[:,:,None],raw,0))
    inv=np.linalg.inv(m);it=-inv@t
    expected=Image.fromarray(source).transform((1672,941),Image.Transform.AFFINE,(*inv[0],it[0],*inv[1],it[1]),resample=Image.Resampling.BICUBIC,fillcolor=0)
    e=np.array(expected);e[e[:,:,3]==0]=0
    group=rgba(P/'candidate/same_transform_complete_group_ONE_RESAMPLE.png')
    assert np.array_equal(e,group)
    far=Image.open(P/'candidate/same_transform_far_complete_arm_VISIBLE.png').convert('RGBA')
    near=Image.open(P/'candidate/same_transform_near_arm_grip_COMPLETE_prop.png').convert('RGBA')
    grouped=Image.new('RGBA',(1672,941));grouped.alpha_composite(far);grouped.alpha_composite(near)
    assert np.array_equal(np.array(grouped),group)
    mother=rgba(S/'F044_frozen_production_mother_REFERENCE_ONLY.png');donor=rgba(S/'F026_original_coordinate_clothing_BACKPLATE.png')
    assert np.array_equal(mother[480:560,720:890],donor[480:560,720:890])
    cleared=mask('old044_arm_prop_WEAK_AA_cleared.png')
    kept=mask('original044_actual_available_cloth_kept_during_clear.png')
    assert not (kept&cleared).any()
    back=mask('F026_continuous_body_backplate_same_coordinate.png')
    back_expected=np.zeros(mother.shape[:2],bool);back_expected[565:786,690:936]=True
    assert np.array_equal(back,back_expected)
    base=mother.copy();base[cleared]=0
    replay=Image.fromarray(np.where(back[:,:,None],donor,0).astype('uint8'))
    replay.alpha_composite(Image.fromarray(base));replay.alpha_composite(far);replay.alpha_composite(near)
    out=np.array(replay);guards=mask('original044_actual_head_ruffle_skirt_restored.png');out[guards]=mother[guards]
    actual=rgba(P/g['candidate_path'])
    assert np.array_equal(out,actual) and np.array_equal(actual[guards],mother[guards])
    assert not (guards&(mother[:,:,3]==0)).any()
    skirt=np.array(Image.open(S/'F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png').convert('L'))>0
    skirt&=mother[:,:,3]>0
    overlap=int(((np.array(near)[:,:,3]>=128)&skirt).sum())
    assert overlap==g['new_registered_near_material_intersect_stable_skirt_alpha128']==253
    assert int(mask('F026_old_silver_ACTUALLY_NOT_OPAQUE_COVERED.png').sum())==0
    assert all(group[y,x,3]>=253 for x,y in [(840,650),(850,640),(930,650)])
    assert g['image_calls']==0 and g['069_unopened'] is True
    assert sha((P/g['candidate_path']).read_bytes())==g['candidate_SHA256']
    print(json.dumps({'status':'PASS_SOURCE_SINGLE_TRANSFORM_AND_CORRECT_BACK_LAYER_CHECKS_TRIAL_REMAINS_HOLD','source_files_byte_exact':len(exact_sources),'single_group_resampling_verified':True,'F026_original_coordinate_backplate_verified':True,'collar_RGBA_equal_pixels':13600,'frozen_guard_RGBA_changes':0,'visible_confirmed_old_silver_core':0,'near_arm_stable_skirt_intersection_alpha128':overlap,'candidate_SHA256':g['candidate_SHA256'],'new_image_calls':0,'F069_unopened':True}))


if __name__=='__main__':main()
