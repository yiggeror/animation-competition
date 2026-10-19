from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
props=rgba(B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')[:,:,3]>0
old=rgba(B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019/candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png')
plan=json.loads((R/'SOURCES_EXPOSURE_AND_T_LAYER.json').read_text());checks=[]
for f in [42,48]:
 r=json.loads((R/f'F{f:03d}/MAPPING_CHECK.json').read_text());s=np.array(r['source_landmarks']);t=np.array(r['target_landmarks'])
 i=np.where(np.all(s==[499,747],axis=1))[0][0];assert np.array_equal(t[i],[499,747]);assert r['far_pinch_residual']==0 and r['inverted_triangles']==0
 v=rgba(R/f'F{f:03d}/SAME036_MAPPED_REINTEGRATED_RGBA.png')
 h=np.array(Image.open(B/f'F042_F048_SINGLE_WHOLE_CLOTH_REPAINT_20261019/F{f:03d}/HUMANS_PROTECTED_COORDINATES.png').convert('L'))>0
 frozen=rgba(B/f'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL/candidate/F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png')
 assert np.array_equal(v[h],frozen[h]);assert np.array_equal(v[props],old[props])
 checks.append({'frame':f,'C1_residual':0,'far_residual':0,'human_RGBA_changes':0,'true_actual_alpha_prop_and_T_RGBA_changes':0})
for s in plan['sources']:assert sha(Path(s['used']))==s['sha256']
run=json.loads((R/'ACTUAL_BROWSER_RUN.json').read_text());decode=json.loads((R/'DECODE_CHECK.json').read_text());probe=json.loads((R/'FFPROBE.json').read_text())
assert run['pass'] and run['sourceUnchanged'] and len(run['frames'])==13
assert all(v['wholeMotherSceneMatrix']==[1.0026666666666666,0,0,1.0026666666666666,277.33333333333303,-6] for v in run['frames'])
assert run['sourceBefore']==json.loads((B/'F036_F042_F048_SCENE_TRANSITIONS_ZERO_CALL_20261019/ACTUAL_BROWSER_RUN.json').read_text())['sourceBefore']
assert decode['video_SHA256']==run['mp4_SHA256']==sha(R/'S29_F036_F048_ACTUAL_SCENE_1080p24.mp4')
assert decode['decoded_frames']==13 and len(decode['actual_decode_hashes'])==13 and not decode['has_audio']
assert int(probe['streams'][0]['nb_read_frames'])==13 and probe['streams'][0]['r_frame_rate']=='24/1'
assert sha(B/'F036_SINGLE_CLEAN_CLOTH_MASTER_NATIVE_CALL01_20261019/RAW_UNTOUCHED.png')=='b8e3ade55a06042ee48123524528450f8f259cba7aae61c6a262394400d76b23'
assert sha(B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019/F036_COMPLETE_FOLD_CLOTH_RGBA.png')==plan['one_shared_master_SHA256']
for p in R.rglob('*.py'):compile(p.read_text(),str(p),'exec')
for p in R.rglob('*.json'):json.loads(p.read_text())
report={'fresh_verification':'PASS_NUMERICAL_PROVENANCE_TRUE_ALPHA','overall_visual_contact_gate':'HOLD_FAR_PINCH_REMAINS','generation_calls_this_task':0,'checks':checks,'actual_prop_alpha_pixels':int(props.sum()),'shared_master_SHA256':plan['one_shared_master_SHA256'],'actual_video_SHA256':run['mp4_SHA256'],'actual13f_source_camera_light_code_unchanged':True,'decoded_frames':13,'no_audio':True}
(R/'FRESH_FINAL_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
