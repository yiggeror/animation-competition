"""Fresh evidence for final two-domain candidate. No generation or rendering."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,binary_dilation,label
F=Path(__file__).resolve().parent; P=F.parent
S=P/'next_F128_mid_roll_input_001/character_four_inputs_001/generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((F/'repair_and_protection.json').read_text())
m=json.loads((F/'measurements_before.json').read_text())
A=np.array(Image.open(F/'source_d240ffae_UNMODIFIED_candidate.png').convert('RGBA'))
B=np.array(Image.open(F/report['final_png']).convert('RGBA'))
H,W=B.shape[:2]; yy,xx=np.indices((H,W))
diff=np.any(A!=B,axis=2)
domains=np.array(Image.open(F/'two_authorized_domains_mask.png'))>0
erase=np.array(Image.open(F/'domain1_old_exterior_painted_guides_removal_mask.png'))>0
head=np.array(Image.open(F/'domain2_complete_head_neck_and_C_occlusion_mask.png'))>0
body=np.array(Image.open(F/'fixed_native_body_collar_arms_whole_skirt_protection_mask.png'))>0
assert sha(F/'source_d240ffae_UNMODIFIED_candidate.png')=='0abeac189e8894f263291a3018446beccf0d55c4fe02f9b6cd85ca9ae97511aa'
assert sha(F/report['final_png'])==report['final_png_sha256']
assert not np.any(diff&~domains) and not np.any(diff&body)
assert not np.any(diff&(yy>=570)) and not np.any(diff&(xx>=850))
for side in ['R','L']:
    g=np.array(Image.open(F/f'complete_native_{side}_arm_palm_skin_ink_protection_mask.png'))>0
    assert not np.any(diff&g)
# Main-head measurements after the same uniform part of the actual field.
# The anatomical lower-neck blend is excluded from these volume masks.
scale=m['selected_uniform_own_head_scale']; pivot=np.array(m['pivot_current_actual_neck_collar_contact'])
sx=(xx-pivot[0])/scale+pivot[0]; sy=(yy-pivot[1])/scale+pivot[1]
oldmask=np.array(Image.open(F/'measured_main_cranium_face_128_mask.png'))>0
source=np.array(Image.open(F/'own128_complete_head_all_hair_one_scale_continuous_neck.png').convert('RGBA'))
after=map_coordinates(oldmask.astype(float),[sy,sx],order=0,mode='constant',cval=0)>0
after&=source[:,:,3]>100
py,px=np.where(after)
aftermeasure={'area_px':int(after.sum()),'x_005_995':np.quantile(px,[.005,.995]).tolist(),
              'y_005_995':np.quantile(py,[.005,.995]).tolist(),
              'centroid':[float(px.mean()),float(py.mean())]}
ref=m['states'][0]; before=m['states'][1]
span=lambda q:q[1]-q[0]
aftermeasure['120_to_closed128_main_width_ratio']=span(ref['main_cranium_x_005_995'])/span(aftermeasure['x_005_995'])
aftermeasure['120_to_closed128_main_height_ratio']=span(ref['main_cranium_y_005_995'])/span(aftermeasure['y_005_995'])
aftermeasure['120_to_closed128_main_area_linear_ratio']=math.sqrt(ref['main_cranium_face_area']/aftermeasure['area_px'])
aftermeasure['main_crown_level_before_128_minus120_px']=before['main_cranium_y_005_995'][0]-ref['main_cranium_y_005_995'][0]
aftermeasure['main_crown_level_after_128_minus120_px']=aftermeasure['y_005_995'][0]-ref['main_cranium_y_005_995'][0]
aftermeasure['own_collar_root_level_difference_retained_px']=m['neck_collar_level_128_minus120'][1]
Image.fromarray(np.uint8(after)*255).save(F/'measured_main_cranium_face_128_after_mask.png')
(F/'measurements_after.json').write_text(json.dumps(aftermeasure,ensure_ascii=False,indent=2)+'\n')
cfg=json.loads((F/'scene_config.json').read_text()); oldcfg=json.loads((S/'scene_config.json').read_text())
actual=json.loads((F/'actual_CAM20_128_geometry.json').read_text()); prev=json.loads((S/'actual_CAM20_128_geometry.json').read_text())
assert cfg['camera']==oldcfg['camera'] and cfg['reg']==oldcfg['reg']
for k in ['camera','root_input_baseline_established_this_gate','pose','people_to_CAM20']:
    assert actual[k]==prev[k],k
for row,old in zip(actual['rods'],prev['rods']):
    for k in ['A_master','B_master','A_screen','B_screen','B_world','candidate_A_B_length_m','local_point_mm','width_screen']:
        assert row[k]==old[k],k
assert actual['finite_A_B_only'] and actual['external_handle_tail_m']==0
assert 'ERROR ' not in (F/'browser_console.log').read_text()
for typ in ['actual','albedo']:
    im=Image.open(F/f'CAM20_F128_current_branch_{typ}.png').convert('RGB'); assert im.size==(1920,1080)
    im.crop((400,360,1100,875)).save(F/f'CAM20_F128_true_finite_rods_both_palms_{typ}_1x.png')
    c=im.crop((510,535,810,860));c.save(F/f'CAM20_F128_true_finite_two_grips_{typ}_1x.png')
    c.resize((900,975),Image.Resampling.NEAREST).save(F/f'CAM20_F128_true_finite_two_grips_{typ}_3x.png')
    # Compare against previous native actual image at the same full camera.
    oldim=Image.open(S/f'CAM20_F128_current_branch_{typ}.png').convert('RGB')
    box=(790,220,1250,720);card=Image.new('RGB',(920,500))
    card.paste(oldim.crop(box),(0,0));card.paste(im.crop(box),(460,0))
    card.save(F/f'CAM20_before_left_closed_right_head_chest_{typ}_1x.png')
audit={'status':'ZERO_CALL_F128_TWO_DOMAIN_EVIDENCE_COMPLETE_ASTRA_ACTUAL_GATE_PENDING',
       'new_image_requests':0,'new_raw_outputs':0,'final_candidate_count':1,
       'camera_frames_only':[128],'local_same_frame_render_passes':2,
       'note_render_passes':'Initial receiving-mask AA diagnosis then final same F128 frame; no future frames or whole-shot render.',
       'uniform_own_head_scale':scale,'main_head_after_measurements':aftermeasure,
       'old120_head_or_feature_pixels_used':False,'independent_facial_feature_movement':False,
       'native_palms_fingers_wrists_arms_changes':0,'fixed_body_collar_whole_skirt_changes':0,
       'fixed_lower_support_changes':0,'grandma_changes':0,'outside_two_domains_changes':0,
       'only_exterior_painted_guides_removed':int(erase.sum()),
       'true_A_B_screen_world_endpoints_lengths_and_turtle_root_pose_camera_changes':0,
       'L_cap_sampling_not_used_as_standalone_contact_rejection':True,
       'normal_actual_two_grip_images_required_for_Astra_gate':True,
       'source_candidate_sha256':sha(F/'source_d240ffae_UNMODIFIED_candidate.png'),
       'final_candidate_sha256':sha(F/report['final_png']),
       'actual_CAM20_png_sha256':sha(F/'CAM20_F128_current_branch_actual.png'),
       'adopted':False,'exposure_frozen':False,'132_opened':False}
(F/'VERIFICATION.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(audit,ensure_ascii=False,indent=2))
