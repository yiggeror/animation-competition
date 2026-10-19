"""Finite source/material/contact checks. Does NOT certify native drawing/anatomy."""
from pathlib import Path
from PIL import Image
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parent;repo=R.parents[3]; B=R.parent
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((R/'SOURCE_GEOMETRY_AND_ZERO_CALL_CHECK.json').read_text())
assert report['generation_calls']==0 and report['scene_render_calls']==0
for p,s in report['sources'].items():assert sha(repo/p)==s,(p,s)
lockedp=B/'F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019/F066_UNCHANGED_LOCKED_RGBA.png'
clothp=B/'F054_F060_F066_FULL_TARGET_GATE_ZERO_CALL_20261019/F066/ONE_SAME_MATERIAL_MAPPED_CLOTH_RGBA.png'
propsp=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png'
for src,name in [(lockedp,'LOCKED066_ACTUAL_REFERENCE_RGBA.png'),(clothp,'LOCKED066_SAME_SOURCE_CLOTH_RGBA.png'),(propsp,'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png')]:assert src.read_bytes()==(R/name).read_bytes()
assert sha(clothp)=='2e81977c98e057439ed661dc29d41957a4e1bb4a99df56d1157a7957de7c615e'
assert sha(propsp)=='c006b3fb3d05d29a4a3d16b06496308bce34797e93a76bc80c0e5511cdcd2704'
locked=a(lockedp);cloth=a(clothp);Y,X=np.indices(cloth.shape[:2]);fixed=(Y>=820)|(X<=499);protect=(Y<420)|(Y>=1100)
near0=a(B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F066/reintegration/EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png')
far0=a(B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F066/reintegration/ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png')
n=np.array([.625,.781]);n/=np.linalg.norm(n);dd=(X-546)*n[0]+(Y-530)*n[1];rigid=(dd>=45)&(far0[:,:,3]>0)
edge=int(np.where(cloth[:,430,3]>128)[0].max());assert edge==959
rows=[];refs={}
for f,dx,dy in [(72,-21,40),(78,-41,75),(84,-41,75)]:
 d=R/f'F{f:03d}';c=a(d/'ONE_CONTINUOUS_SAME_SOURCE_CLOTH_RGBA.png');t=a(d/f'F{f:03d}_FULL_TECHNICAL_TARGET_NOT_NATIVE_DRAWING_RGBA.png');nr=a(d/'COMPLETE_NEAR_ARM_HAND_TECHNICAL_GUIDE_RGBA.png');fr=a(d/'COMPLETE_FAR_ARM_JADE_HAND_TECHNICAL_GUIDE_RGBA.png')
 assert np.array_equal(c[fixed],cloth[fixed]);assert np.array_equal(t[protect],locked[protect])
 if f<84:assert np.array_equal(nr,near0)
 yy,xx=np.where(rigid);assert np.array_equal(fr[yy+dy,xx+dx],far0[yy,xx]),f
 meta=json.loads((d/'CLOTH_SURFACE_MAPPING.json').read_text());assert meta['inverted_triangles']==0 and meta['min_signed_area_ratio']>0
 assert json.loads((d/'CONTACT_AND_LAYER_GATE.json').read_text())['generation_calls']==0
 names=[R/'LOCKED066_ACTUAL_REFERENCE_RGBA.png',d/f'F{f:03d}_FULL_TECHNICAL_TARGET_NOT_NATIVE_DRAWING_RGBA.png',d/'ONE_CONTINUOUS_SAME_SOURCE_CLOTH_RGBA.png']
 refs[str(f)]=[dict(path=str(p.relative_to(repo)),sha256=sha(p))for p in names]
 rows.append(dict(frame=f,protected_head_gaze_legs_RGBA_changes=0,lower_support_cloth_RGBA_changes=0,near_arm_exact066=f<84,whole_far_jade_hand_rigid_RGBA_changes=0,rigid_group_source_pixels=int(rigid.sum()),cloth_min_area_ratio=meta['min_signed_area_ratio'],source_SHA256_verified=True))
assert np.array_equal(a(R/'F078/ONE_CONTINUOUS_SAME_SOURCE_CLOTH_RGBA.png'),a(R/'F084/ONE_CONTINUOUS_SAME_SOURCE_CLOTH_RGBA.png'))
assert np.array_equal(a(R/'F078/COMPLETE_FAR_ARM_JADE_HAND_TECHNICAL_GUIDE_RGBA.png'),a(R/'F084/COMPLETE_FAR_ARM_JADE_HAND_TECHNICAL_GUIDE_RGBA.png'))
(R/'PLANNED_REFERENCE_ORDER_NOT_EXECUTED.json').write_text(json.dumps(dict(generation_calls=0,prompts_executed=False,references=refs),indent=2)+'\n')
out=dict(status='PASS_FINITE_INPUT_SOURCE_MATERIAL_CONSTRAINTS_ONLY',generation_calls=0,scene_render_calls=0,source_files=len(report['sources']),copied_locked_references_byte_exact=True,true_two_puppets_four_rods_RGBA_unchanged=True,near_front_edge_measured_from_actual066=[430,edge],cloth078_to084_RGBA_changes=0,far_arm078_to084_RGBA_changes=0,rows=rows,not_certified=['native whole-arm anatomy','final soft-fold drawing','final native thumb/index contact','actual scene switch continuity','Astra input approval'])
(R/'INDEPENDENT_FINITE_INPUT_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
