"""Read-only raster/manifest verification; writes the local audit report only."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
F=Path(__file__).resolve().parent; P=F.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((F/'INPUT_MANIFEST.json').read_text())
args=json.loads((F/'tool_args_prepared_NOT_SUBMITTED.json').read_text())
baseline=json.loads((F/'MECHANISM_INPUT_BASELINE_THIS_GATE.json').read_text())
source=Path(m['source120']); A=np.array(Image.open(source).convert('RGBA'))
assert sha(source)==m['source120_sha256']=='40d73e42505d5e7c83dc22d33511e5a2e4862dc35b5a4ff210e50eca8ef2bf5c'
assert len(m['inputs'])==len(args['referenced_image_paths'])==4
for q,p in zip(m['inputs'],args['referenced_image_paths']):
    assert q['path']==p and sha(Path(p))==q['sha256']
    assert list(Image.open(p).size)==q['size']
assert m['new_image_calls']==m['raw_outputs']==m['retries']==0
assert not m['submitted'] and not m['generation_authorized'] and not m['frozen_exposure']
T=np.array(Image.open(m['inputs'][0]['path']).convert('RGBA')); H,W=T.shape[:2]
mask=np.array(Image.open(m['inputs'][3]['path']).convert('RGB'))
assert np.array_equal(mask[:,:,0],mask[:,:,1]) and np.array_equal(mask[:,:,1],mask[:,:,2])
assert set(np.unique(mask).tolist())=={0,255}
mask=mask[:,:,0]>0; yy,xx=np.indices((H,W))
upper_source=P/'next_F120_passive_decay_input_001/generation_001/registered_complete_new_upper_whole_skirt_two_T.png'
old=np.array(Image.open(upper_source).convert('RGBA'))
new=np.array(Image.open(F/'new_complete_upper_whole_skirt_with_short_contacts_CONSTRUCTION_ONLY.png').convert('RGBA'))
lower=np.array(Image.open(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png').convert('RGBA'))
C=np.array(Image.open(F/'fixed_original_C_rods_scene_layer.png').convert('RGBA'))
support=(yy>=760)&(xx<850)&(A[:,:,3]>0)
grandma=(xx>=850)&(A[:,:,3]>0)&(old[:,:,3]==0)
visible_lower=(lower[:,:,3]>0)&(old[:,:,3]==0)&(new[:,:,3]==0)&(yy>=650)&(xx<850)
all_exposed_lower=(lower[:,:,3]>0)&(new[:,:,3]==0)&(yy>=650)&(xx<850)
visible_C=(C[:,:,3]>0)&(old[:,:,3]==0)&(new[:,:,3]==0)&(xx<850)
counts={}
for name,region in [('actual_support',support),('grandma',grandma),
                    ('visible_fixed_lower',visible_lower),('visible_original_C',visible_C)]:
    counts[name]={'compared_pixels':int(region.sum()),
                  'RGBA_changed_pixels':int(np.any(T[region]!=A[region],axis=1).sum())}
    assert counts[name]['RGBA_changed_pixels']==0
assert not np.any(mask[all_exposed_lower]) and not np.any(mask[grandma]) and not np.any(mask[736:])
for bone in m['bone_reference_2D_only']:
    for key in ['projected_upper_length_source_target','projected_forearm_length_source_target']:
        assert abs(bone[key][0]-bone[key][1])<1e-10
for p in m['complete_palm_field_audit']: assert p['max_translation_residual_px']<0.05
geometry=F.parent/'finite_current_branch_scene_001/candidate_geometry.json'
assert sha(geometry)==baseline['candidate_geometry_sha256']
grips=[r['B_master'] for r in baseline['F128_root_pose_rods']['rods']]
assert grips==[[400.3988637166487,402.6996190692074],[463.6082671920906,508.76677359903914]]
for q in m['short_contacts_only_not_puppet_or_long_rods']: assert q['external_tail_after_B_px']==0
report={'status':'PASS_ZERO_CALL_F128_INPUT_PREPARATION_ONLY',
        'not_native_art_or_generation_acceptance':True,'actual_images_opened_for_review':[
            'inputs/01_unique_complete_F128_target_REVIEW_ONLY.png','contacts_1x_REVIEW_ONLY.png',
            'inputs/03_120_identity_head_collar_cloth_shoes_patches_only.png',
            'inputs/04_complete_upper_whole_skirt_white_full_legs_black_mask.png',
            '120_left_128_target_right_same_canvas_upper_hands_1x.png',
            'whole_skirt_hidden_roots_target_left_mask_right_1x.png'],
        'new_image_calls':0,'raw_outputs':0,'retries':0,'exact_F128_grips':grips,
        'protection_pixel_audits':counts,'binary_full_mask':True,
        'full_exposed_lower_and_grandma_black':True,
        'mechanism_baseline_source_sha_unchanged':True,
        'source120_native_accepted_sha_unchanged':True,
        'complete_palms_max_field_error_px':[p['max_translation_residual_px'] for p in m['complete_palm_field_audit']],
        'four_input_sha256':[q['sha256'] for q in m['inputs']]}
(F/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
