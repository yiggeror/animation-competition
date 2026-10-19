from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,csv
R=Path(__file__).resolve().parent;B=R.parent;repo=R.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
master=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png';lockedp=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/F048/CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png'
assert sha(master)=='18b478ba2734d3f7f30e254c73284c80bd8d4f4c7e428a4a304a461916c010f9'
assert sha(lockedp)=='7cfb050414a6fde23fddf3f44bf2c83ddaae54f0be6b25d3babb874dda40b298'
idx=json.loads((R/'ACTUAL_SOURCE_AND_PROPOSED_INPUT_INDEX.json').read_text())
for x in idx['files']:assert sha(repo/x['path'])==x['SHA256'],x['path']
locked=rgba(lockedp);previouscover=np.zeros((1536,1024),bool);checks=[];heldarm=None
for f in [54,60,66]:
 d=R/f'F{f:03d}';r=json.loads((d/'CONTACT_AND_ARM_CHECK.json').read_text());m=json.loads((d/'CLOTH_MAPPING.json').read_text());a=rgba(d/f'F{f:03d}_TECHNICAL_INPUT_NOT_NATIVE_RGBA.png');near=rgba(d/'NEAR_FULL_ARM_NATIVE_REFERENCE_GUIDE_RGBA.png')
 assert a.shape==(1536,1024,4);assert m['inverted_triangles']==0 and m['stage1_locked_map']['inverted_triangles']==0
 assert np.array_equal(a[:420],locked[:420]),'head/eye changed';assert np.array_equal(a[1100:],locked[1100:]),'legs/body changed'
 assert r['near_whole_palm_props_overlap_pixels']==0
 if f>=60:assert r['near_whole_palm_cloth_alpha_coverage_fraction']==1.
 if heldarm is not None:assert np.array_equal(near,heldarm),'pressing near arm moved between060 and066'
 if f==60:heldarm=near
 arm=r['whole_near_arm'];C=np.array(arm['target_cuff']);E=np.array(arm['target_elbow']);W=np.array(arm['target_wrist']);assert abs(np.linalg.norm(E-C)-90)<1e-8 and abs(np.linalg.norm(W-E)-270)<1e-8
 cover=np.array(Image.open(d/'ACTUAL_OUTER_FEATHER_COVER_MASK.png'))>0;assert not np.any(previouscover&~cover);previouscover=cover
 checks.append({'frame':f,'whole_palm_props_overlap':0,'cloth_support_fraction':r['near_whole_palm_cloth_alpha_coverage_fraction'],'feather_cover':int(cover.sum()),'head_eyes_lower_body_RGBA_changes':0,'near_forearm_foreground_prop_overlap':r['near_forearm_and_upper_arm_foreground_prop_occlusion_pixels'],'cloth_inversions':m['inverted_triangles']})
a=rgba(B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/F048/FROM_ONE_COMPLETE_MASTER_CLOTH_RGBA.png');b=rgba(R/'F054/ONE_SAME_MATERIAL_MAPPED_CLOTH_RGBA.png');change=np.any(a!=b,2);y,x=np.nonzero(change);assert change.sum()==670 and x.min()>=430 and x.max()<=526 and y.min()>=688 and y.max()<=768
planned=json.loads((R/'PLANNED_PROMPTS_NOT_EXECUTED/PLANNED_INPUTS_NOT_ACTUAL_TOOL_CALLS.json').read_text());assert len(planned)==3 and all(x['executed'] is False for x in planned)
rows=list(csv.DictReader((R/'EXPOSURE_NEW_EXPLICIT_DIRECTIVE.csv').open()));assert [(int(x['first_frame']),int(x['last_frame']))for x in rows]==[(48,53),(54,59),(60,65),(66,71)]
out={'status':'PASS_TECHNICAL_PACK_CONSISTENCY_ONLY_NOT_NATIVE_OR_SCENE','generation_calls':0,'renders':0,'authoritative_source_hashes_verified':len(idx['files']),'locked048_and_sole_complete_master_unchanged':True,'new054_cloth_changes_only_released_source_domain_pixels':int(change.sum()),'near060_and066_arm_byte_identical':True,'exposures_explicit_new_directive':rows,'actual_visual_review':'root plus existing cloud; see ACTUAL_TECHNICAL_REVIEW.json','remaining_gate':'Astra actual-image input freeze; then native whole-chain drawing; no generation run','states':checks}
(R/'FINAL_ZERO_CALL_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
