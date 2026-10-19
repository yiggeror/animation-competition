"""Read-only pixel/manifest gate for reference preparation, not model-art QA."""
from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np

O=Path(__file__).resolve().parents[1]
ROOT=O.parents[3]
R=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
req=json.loads((O/'requests/F082_COMPLETE_ACTIVE_INPUT_GATE_NOT_EXECUTABLE.json').read_text())
manifest=json.loads((O/'provenance/source_manifest.json').read_text())
geom=json.loads((O/'geometry/F082_COMPLETE_ACTIVE_RISE_TRUE_CONTACTS_AND_SUPPORT_DOMAIN.json').read_text())
ledger=json.loads((O/'provenance/call_ledger.json').read_text())
assert req['call_allowed'] is False and req['tool_arguments'] is None
assert req['new082_model_calls']==req['new082_actual_Canvas']==req['new082_usable_drawn_poses']==0
assert ledger['imagegen_calls']==ledger['actual082_Canvas']==ledger['usable_new082_drawn_poses']==0
assert ledger['source_pixels_adopted_as_final_art']==0
assert not (O/'actual_scene').exists() and not (O/'originals').exists()
prompt=O/'prompts/F082_COMPLETE_ACTIVE_DRAWING_FULL_INPUT_GATE.txt'
assert sha(prompt)==req['prompt_SHA256']
assert prompt.read_text()==req['proposed_exact_arguments_for_Astra_review_only']['prompt']
for q in req['actual_three_input_PNGs']:
    path=ROOT/q['path']
    assert sha(path)==q['SHA256']
    with Image.open(path) as im:
        im.load()
        assert list(im.size)==q['size']
for q in manifest['sources']:
    path=Path(q['path'])
    if not path.is_absolute(): path=ROOT/path
    assert sha(path)==q['SHA256'],str(path)
for entry in ['sole_activity_mother','permanent_static_support_source']:
    q=geom[entry]
    assert sha(Path(q['path']))==q['SHA256']
def rgba(path): return np.asarray(Image.open(path).convert('RGBA'))
base=rgba(R/'F078_NARROW_JOIN_actual_call01_20261019/candidate/F078.png')
original074=rgba(R/'F074_PANTS_LOCAL_actual_call01_20261019/candidate/F074.png')
n=rgba(O/'anatomy/F082_COMPLETE_VISIBLE_REFERENCE_ONLY.png')
active=rgba(O/'anatomy/F082_ACTIVE_REFERENCE_ONLY_NOT_NEW_DRAWING.png')
static=rgba(O/'anatomy/FINAL074_TRUE_STATIC_SHINS_ANKLES_SHOES_NATIVE_MASTER.png')
mask=lambda path: np.asarray(Image.open(path).convert('L'))>0
adopt=mask(O/'masks/F082_ACTIVE_UPPER_BOTH_THIGHS_AND_MOVING_KNEE_CONNECTOR.png')
fixed=mask(O/'masks/F082_FIXED_FINAL074_SUPPORT_OWNERSHIP.png')
foot=mask(O/'masks/F082_BOTH_ORIGINAL_SHOES_ANKLES_HARD_GUARD.png')
oldjoin=mask(R/'F078_NARROW_JOIN_actual_call01_20261019/geometry/FROZEN18457_ADOPTION_DOMAIN.png')
assert np.all(adopt^fixed) and not np.any(adopt&fixed)
assert not np.any(adopt&foot) and not np.any(adopt[1210:])
assert not np.any(oldjoin&fixed)
assert np.array_equal(n[fixed],base[fixed])
v=fixed&(base[:,:,3]>0)
assert np.array_equal(n[v],original074[v])
assert np.array_equal(n[foot],base[foot])
combined=np.maximum(active,static)
visible=(combined[:,:,3]>0)|(n[:,:,3]>0)
assert np.array_equal(combined[visible],n[visible])
assert np.array_equal(combined[:,:,3],n[:,:,3])
assert not np.any((active[:,:,3]>0)&(static[:,:,3]>0))
bg=rgba(O/'anatomy/F082_REFERENCE_BG.png')
fg=rgba(O/'anatomy/F082_REFERENCE_FRONT_GRIPS.png')
assert np.array_equal(np.maximum(bg,fg),n)
U=np.asarray(geom['one_upper_rigid_native_matrix'])
P=np.asarray(geom['same_true_rods_closed_grips_rigid_scene_matrix'])
origin=np.array([275.,112.])
assert np.allclose(U[:,:2].T@U[:,:2],np.eye(2))
assert np.allclose(U[:,:2],P[:,:2])
assert np.allclose(P[:,2],.7*U[:,2]+origin-U[:,:2]@origin)
for key,point in geom['true_points_source_FINAL078'].items():
    assert np.allclose(P[:,:2]@np.asarray(point)+P[:,2],geom['true_points_target_F082'][key])
for q in geom['rigid_projected_rod_checks'].values():
    assert abs(q['source_projected_length_scene']-q['target_projected_length_scene'])<1e-9
for script in (O/'tools').glob('*.py'):
    compile(script.read_text(),str(script),'exec')
print(json.dumps({'status':'REFERENCE_PREPARATION_CHECKS_PASS_NOT_DRAWING_QUALIFICATION',
    'actual_three_inputs_SHA_and_decode_checks':3,'manifest_source_SHA_checks':len(manifest['sources']),
    'prompt_matches_exact_proposed_request':True,'call_allowed':False,'imagegen_calls':0,'actual082_Canvas':0,'new082_usable_drawn_poses':0,
    'activity_source_SHA256':sha(Path(geom['sole_activity_mother']['path'])),'static_source_SHA256':sha(Path(geom['permanent_static_support_source']['path'])),
    'reference_fixed_region_RGBA_changed_pixels':0,'fixed_visible_original074_RGBA_equal_pixels':int(v.sum()),
    'original074_shoe_ankle_guard_excluded_from_new_adoption':True,'all_y1210down_excluded_from_new_adoption':True,
    'entire_preceding18457_connector_included_in_new_active_domain':True,
    'active_fixed_visible_RGBA_reconstruction_differences':0,'active_fixed_alpha_reconstruction_differences':0,'active_fixed_alpha_overlap':0,
    'fully_transparent_hidden_RGB_reconstruction_difference_pixels':int(np.any(combined!=n,axis=2)[~visible].sum()),
    'BG_FG_complete_RGBA_reconstruction_differences':0,'one_upper_and_true_grips_prop_rigid_transform_consistent':True,'projected_rod_length_differences_below':1e-9,
    'separate_knee_shin_shoe_warps':0,'source_reference_pixels_adopted_as_new_art':0},indent=2))
