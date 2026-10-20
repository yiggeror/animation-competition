"""Audit single actual scene against passed mechanism, make review crops."""
from pathlib import Path
import hashlib,json,math,base64
import numpy as np
from PIL import Image
F=Path(__file__).resolve().parent; I=F.parent; P=I.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reg=json.loads((F/'registration_and_protection.json').read_text())
cfg=json.loads((F/'scene_config.json').read_text())
baseline=json.loads((I/'MECHANISM_INPUT_BASELINE_THIS_GATE.json').read_text())
old_scene=I.parent/'finite_current_branch_scene_001'
actual=json.loads((F/'actual_CAM20_128_geometry.json').read_text())
old=json.loads((old_scene/'actual_CAM20_128_geometry.json').read_text())
assert cfg['camera']==baseline['camera'] and cfg['reg']==baseline['registration']
assert actual['camera']==old['camera']
assert actual['root_input_baseline_established_this_gate']==old['root_candidate_not_frozen']
assert actual['pose']==old['pose'] and actual['people_to_CAM20']==old['people_to_CAM20']
errors=[]
for row,prev,base in zip(actual['rods'],old['rods'],baseline['F128_root_pose_rods']['rods']):
    for field in ['A_master','B_master','B_world','candidate_A_B_length_m']:
        assert row[field]==prev[field]==base[field]
    for field in ['A_screen','B_screen','width_screen','local_point_mm']:
        assert row[field]==prev[field]
    errors.append({'id':row['id'],'A_screen_displacement_px':0,
                   'B_screen_displacement_px':0,'rod_length_change_m':0})
assert actual['finite_A_B_only'] and actual['external_handle_tail_m']==0
assert 'ERROR ' not in (F/'browser_console.log').read_text()
N=np.array(Image.open(F/'registered_complete_new_upper_whole_skirt_short_guides_UNREPAIRED.png').convert('RGBA'))
T=np.array(Image.open(F/reg['final_png']).convert('RGBA'))
source=P/'next_F120_passive_decay_input_001/generation_001/F120_uniform_registered_upper_fixed_full_lower_candidate.png'
A=np.array(Image.open(source).convert('RGBA')); H,W=A.shape[:2]; yy,xx=np.indices((H,W))
U0=np.array(Image.open(P/'next_F120_passive_decay_input_001/generation_001/registered_complete_new_upper_whole_skirt_two_T.png').convert('RGBA'))
lower=np.array(Image.open(I/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png').convert('RGBA'))
C=np.array(Image.open(I/'fixed_original_C_rods_scene_layer.png').convert('RGBA'))
counts={}
for name,region in [('support',(yy>=760)&(xx<850)&(A[:,:,3]>0)),
    ('grandma',(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0)),
    ('visible_lower',(lower[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(yy>=650)&(xx<850)),
    ('visible_C',(C[:,:,3]>0)&(U0[:,:,3]==0)&(N[:,:,3]==0)&(xx<850))]:
    change=int(np.any(T[region]!=A[region],axis=1).sum()); assert change==0
    counts[name]={'compared_pixels':int(region.sum()),'RGBA_changes':change}
contacts=[]
for row in baseline['F128_root_pose_rods']['rods']:
    bx,by=row['B_master']; area=(xx+.5-bx)**2+(yy+.5-by)**2<=(4.083333333333328/2)**2
    own=(N[:,:,3]>220)
    contacts.append({'id':row['id'],'B_master':row['B_master'],
        'master_round_terminal_disk_samples':int(area.sum()),
        'terminal_disk_covered_by_complete_native_component_samples':int((area&own).sum()),
        'note':'Coverage is raster evidence only; actual palm/guide anatomy and axes require Astra image gate.'})
for stem in ['actual','albedo']:
    name=f'CAM20_F128_current_branch_{stem}.png'
    im=Image.open(F/name).convert('RGB')
    assert im.size==(1920,1080)
    im.crop((400,360,1100,875)).save(F/f'CAM20_F128_true_finite_rods_both_palms_{stem}_1x.png')
    c=im.crop((510,535,810,860))
    c.save(F/f'CAM20_F128_true_finite_two_grips_{stem}_1x.png')
    c.resize((900,975),Image.Resampling.NEAREST).save(F/f'CAM20_F128_true_finite_two_grips_{stem}_3x.png')
assert sha(F/'raw_original.png')=='4245be9d5e57736d268c39a0bb4227212a64853013d5ce0ec36257c9b050080a'
original_return=json.loads((F/'tool_return_original.json').read_text())
returned_bytes=base64.b64decode(original_return['image_url'].split(',',1)[1])
assert hashlib.sha256(returned_bytes).hexdigest()==sha(F/'raw_original.png')
assert sha(F/reg['final_png'])==reg['final_png_sha256']
actual_args=json.loads((F/'tool_args_exact.json').read_text())
request=json.loads((F/'request_receipt.json').read_text())
for p,row in zip(actual_args['referenced_image_paths'],request['inputs']):assert sha(Path(p))==row['sha256']
assert sha(F/'actual_request_white_black_mask.png')==request['inputs'][3]['sha256']
report={'status':'EVIDENCE_COMPLETE_ACTUAL_F128_ASTRA_MINIMUM_GATE_PENDING',
        'generation_requests':1,'raw_outputs':1,'automatic_retries':0,'actual_CAM20_rendered_frames':[128],
        'actual_scene_camera_root_pose_scale_facing_rods_unchanged':True,
        'source_original_turtle_scale':1.3,'finite_endpoint_audits':errors,
        'native_terminal_disk_coverage':contacts,'fixed_protection_audits':counts,
        'one_uniform_registration_only':True,'local_shape_or_grip_or_rod_repairs':False,
        'actual_input_snapshot_SHAs_and_request_mask_verified':True,
        'exact_original_tool_return_PNG_bytes_match_saved_raw':True,
        'known_native_painted_guide_axis_deviations':reg['native_guide_axis_deviations'],
        'known_native_L_painted_tail_preserved':True,
        'native_pose_and_skirt_differ_from_construction_reference_retained':True,
        'raw_original_sha256':sha(F/'raw_original.png'),
        'candidate_sha256':sha(F/reg['final_png']),
        'actual_CAM20_scene_sha256':sha(F/'CAM20_F128_current_branch_actual.png'),
        'actual_CAM20_albedo_sha256':sha(F/'CAM20_F128_current_branch_albedo.png'),
        'adopted':False,'exposure_frozen':False,'132_opened':False}
(F/'ACTUAL_SCENE_AND_RECEIVING_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
