from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
PRE=B/'F036_SAME_MASTER_MAP042048_SCENE13_ZERO_CALL_20261019'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rawp=B/'F036_SINGLE_CLEAN_CLOTH_MASTER_NATIVE_CALL01_20261019/RAW_UNTOUCHED.png';raw=rgba(rawp)
oldmaster=rgba(B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019/F036_COMPLETE_FOLD_CLOTH_RGBA.png');masterp=R/'ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png';master=rgba(masterp)
domain=np.array(Image.open(R/'COMPLETE_OLD_HOLE_AND_AA_DOMAIN.png').convert('L'))>0
available=np.array(Image.open(R/'ONLY_ACTUAL_RAW_MATERIAL_ADDED.png').convert('L'))>0
assert sha(rawp)=='b8e3ade55a06042ee48123524528450f8f259cba7aae61c6a262394400d76b23'
assert np.array_equal(master[~domain],oldmaster[~domain])
assert np.array_equal(master[available,:3],raw[available,:3])
assert np.all(master[available&(raw[:,:,3]>=128),3]==255)
assert not np.any(available&(raw[:,:,3]==0))
props=rgba(B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')[:,:,3]>0
checks=[];yy,xx=np.indices((1536,1024));roi=(xx>=660)&(xx<=810)&(yy>=610)&(yy<=725)
for f in [36,42,48]:
 d=R/f'F{f:03d}';out=rgba(d/'CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png')
 previousp=B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019/F036_SAME_RAW_REINTEGRATED_RGBA.png'if f==36 else PRE/f'F{f:03d}/SAME036_MAPPED_REINTEGRATED_RGBA.png'
 before=rgba(previousp);assert np.array_equal(out[~roi],before[~roi]);assert np.array_equal(out[props],before[props])
 report=json.loads((d/'SOURCE_AND_COMPOSITION_CHECK.json').read_text());assert sha(Path(report['source_arm_RGBA_path']))==report['source_arm_SHA256']
 if f==36:
  assert np.array_equal(rgba(d/'EXACT_CURRENT_ARM_FOREGROUND_RGBA.png'),rgba(Path(report['source_arm_RGBA_path'])))
 else:
  prior=json.loads((PRE/f'F{f:03d}/MAPPING_CHECK.json').read_text());assert report['exact_existing_arm_M']==prior['arm_M_UNCHANGED'];assert sha(PRE/f'F{f:03d}/MAPPING_CHECK.json')==report['existing_cloth_mesh_report_SHA256']
 checks.append({'frame':f,'outside_contact_ROI_RGBA_changes':0,'actual_props_T_RGBA_changes':0,'source_arm_M_and_cloth_mesh_not_refit':True})
plan=json.loads((R/'SOURCES_EXPOSURE_AND_T_LAYER.json').read_text());assert plan['one_shared_master_SHA256']==sha(masterp)
for s in plan['sources']:assert sha(Path(s['used']))==s['sha256']
run=json.loads((R/'ACTUAL_BROWSER_RUN.json').read_text());decoded=json.loads((R/'DECODE_CHECK.json').read_text());probe=json.loads((R/'FFPROBE.json').read_text())
assert run['pass'] and run['sourceUnchanged'] and len(run['frames'])==13
assert run['sourceBefore']==json.loads((PRE/'ACTUAL_BROWSER_RUN.json').read_text())['sourceBefore']
assert all(v['wholeMotherSceneMatrix']==[1.0026666666666666,0,0,1.0026666666666666,277.33333333333303,-6]for v in run['frames'])
assert run['mp4_SHA256']==decoded['video_SHA256']==sha(R/'S29_F036_F048_ACTUAL_SCENE_1080p24.mp4')
assert decoded['decoded_frames']==13 and len(decoded['actual_decode_hashes'])==13 and not decoded['has_audio']
assert probe['streams'][0]['nb_read_frames']=='13' and probe['streams'][0]['r_frame_rate']=='24/1'
request=json.loads((R/'ONE_SCENE_RENDER_REQUEST.json').read_text());assert request['requested_runs']==1
for n,h in request['scene_code_copied_byte_exact'].items():assert sha(R/n)==h
coverage=json.loads((R/'OPAQUE_SOURCE_MATERIAL_COVERAGE_CHECK.json').read_text());assert all(v['transparent_or_semitransparent_hole_pixels_under250']==0 for v in coverage['results'])
for p in R.glob('*.py'):compile(p.read_text(),str(p),'exec')
for p in R.rglob('*.json'):json.loads(p.read_text())
report={'fresh_verification':'PASS','generation_calls':0,'actual13f_runs':1,'scope':'only old far-hand-hole and AA repair;036/042/048 and original13f','source_raw_SHA256':sha(rawp),'one_complete_master_SHA256':sha(masterp),'video_SHA256':run['mp4_SHA256'],'decoded_frames':13,'fps':24,'no_audio':True,'production_source_changes':0,'checks':checks,'mapped_opaque_source_material_coverage':coverage['results']}
(R/'FRESH_FINAL_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
