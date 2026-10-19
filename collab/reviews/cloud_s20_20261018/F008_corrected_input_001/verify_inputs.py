from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
assert sha(master)=='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
A=np.array(Image.open(master).convert('RGBA'))
B=np.array(Image.open(P/'inputs/01_F008_unique_opaque_pose_target.png').convert('RGBA'))
C=np.array(Image.open(P/'art/child_complete_new_pose.png').convert('RGBA'))
M=np.array(Image.open(P/'inputs/04_edit_white.png'))
old=np.array(Image.open(PACK/'handoff_008_020_032_reference_001/F008/04_edit_white.png'))
rods=np.array(Image.open(P/'local_masks/protect_four_real_rods.png'))>0
assert set(np.unique(M))=={0,255} and not np.any((M>0)&(old==0))
assert not np.any(B[M==0]!=A[M==0])
assert not np.any(B[:,885:]!=A[:,885:]) and not np.any(B[840:]!=A[840:])
assert not np.any(B[rods]!=A[rods])
assert not M[840:].any() and not M[:,885:].any() and not M[rods].any()
box=(535,270,1005,510)
expected=np.array(Image.fromarray(B).crop(box).resize((1410,720),Image.Resampling.NEAREST))
assert np.array_equal(expected,np.array(Image.open(P/'inputs/02_same_view_approach_3x.png')))
geometry=json.loads((P/'target_construction.json').read_text())
frozen=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][0]['state']
assert geometry['frozen_008']==frozen
for side in ['R','L']:
 for s,e in zip(frozen[side+'_chain'],frozen[side+'_chain'][1:]):
  s=np.array(s);e=np.array(e);v=e-s;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
  for t in np.linspace(.05,.95,31):
   for offset in [-3,0,3]:
    x,y=np.rint(s+v*t+n*offset).astype(int)
    assert C[y,x,3]>=250,(side,x,y,C[y,x,3])
for x,y in [(630,445),(604,565),(648,390),(740,344),(770,468)]:assert C[y,x,3]==255
dist=distance_transform_edt(~(rods&(A[:,:,3]>100)))
gaps={}
for side,(x0,y0,x1,y1) in [('R',(778,279,850,340)),('L',(808,420,882,480))]:
 hand=np.zeros(M.shape,bool);hand[y0:y1,x0:x1]=C[y0:y1,x0:x1,3]>200
 gaps[side]=float(dist[hand].min());assert gaps[side]>3
# Validate every SVG path command (the initial author's broken Q was repaired).
counts={'M':2,'L':2,'H':1,'V':1,'C':6,'S':4,'Q':4,'T':2,'A':7,'Z':0}
for node in ET.parse(P/'art/child_complete_new_pose.svg').getroot().iter():
 if node.tag.split('}')[-1]!='path':continue
 toks=re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',node.attrib['d']);i=0
 while i<len(toks):
  c=toks[i].upper();i+=1;j=i
  while i<len(toks) and toks[i].upper() not in counts:i+=1
  n=i-j;k=counts[c];assert (k and n>0 and n%k==0) or (k==0 and n==0)
manifest=json.loads((P/'input_manifest.json').read_text())
args=json.loads((P/'request_prepared.json').read_text())['tool_args']
assert len(args['referenced_image_paths'])==4
for row,file in zip(manifest['inputs'],args['referenced_image_paths']):
 path=Path(file);assert path.parent==P/'inputs' and sha(path)==row['sha256']
 assert list(Image.open(path).size)==row['size']
assert not any('F000_master_clean' in f or 'generation_001' in f for f in args['referenced_image_paths'])
report={'status':'CORRECTED_FOUR_ACTUAL_INPUTS_PREPARED / PENDING_SHORT_GATE',
 'new_image_model_calls':0,'new_raws':0,'submitted':False,
 'source_mother_sha256_unchanged':sha(master),'old_full_mother_in_references':False,
 'old_gray_child_body_or_low_arms_in_target':False,'first_target_new_body_is_opaque':True,
 'both_complete_arm_paths_raster_opacity_pass':True,'target_bones_equal_frozen_F008':True,
 'black_domain_RGBA_changed':0,'grandmother_RGBA_changed':0,'four_rods_mask_RGBA_changed':0,
 'shoe_ankle_strip_RGBA_changed':0,'white_mask_subset_of_previous_approved_child_domain':True,
 'detail_is_exact_3x_crop':True,'actual_distal_hand_wrist_to_real_rod_clearance_px':gaps,
 'third_reference_has_only_head_and_internal_materials':True,
 'all_four_images_actually_viewed':True,
 'input_only_not_a_model_output_or_accepted_animation_drawing':True,
 'cause_claim':'Observed input redesign; no assertion about model internal behavior.'}
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
files=sorted(f for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt')
(P/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+f.relative_to(P).as_posix()+'\n' for f in files))
print(json.dumps(report,ensure_ascii=False,indent=2))
