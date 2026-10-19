#!/usr/bin/env python3
"""Read-only fixed evidence verification; no image calls or mutations."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess
R=Path(__file__).resolve().parent;root=R.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in json.loads((R/'package_manifest.json').read_text())['files']:assert sha(R/row['path'])==row['sha256'],row['path']
for row in json.loads((R/'sources/snapshot_manifest.json').read_text())['exact_copies']:
 rel=R.parent.relative_to(root)/row['source_package']/row['source_path']
 b=subprocess.check_output(['git','show',f"{row['source_commit']}:{rel}"])
 assert b==(R/row['snapshot_path']).read_bytes(),row['source_path']
geo=json.loads((R/'qa/fixed_comparison_geometry_and_limits.json').read_text());assert geo['new_image_calls']==0 and geo['F069_unopened'] and not geo['trial_geometry_modified']
assert sha(R/'fixed_trial/F063_single_group_026_backplate_TRIAL_HOLD.png')=='6ca8123da6afd1eafe7c78b51e819aac352bc9d90d3de0c6a988d3fdecf606e9'
old=Image.open(R/'sources/F044_same_rigid_grip_torch_SOURCE.png').convert('RGBA');m=np.array(geo['old_comparison_only']['M']);t=np.array(geo['old_comparison_only']['t']);assert np.allclose(np.linalg.svd(m,compute_uv=False),[1,1]);inv=np.linalg.inv(m);it=-inv@t
registered=old.transform((1672,941),Image.Transform.AFFINE,(*inv[0],it[0],*inv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
assert np.array_equal(np.asarray(registered),np.asarray(Image.open(R/'comparison/F044_complete_unit_at_frozen_TL_REVIEW_ONLY.png')))
new=Image.open(R/'fixed_trial/F063_same_transform_near_arm_grip_COMPLETE_prop.png').convert('RGBA');crop=tuple(geo['comparison_crop_native'])
for tone,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 for name,unit in [('044',registered),('063',new)]:
  bg=Image.new('RGBA',(1672,941),color);bg.alpha_composite(unit)
  assert np.array_equal(np.asarray(bg.crop(crop).convert('RGB')),np.asarray(Image.open(R/f'comparison/{tone}_{name}_same_TL_native1x.png')))
for src,box,dst in [('sources/F063_local_repair_RAW_same_source.png',(430,480,1270,835),'comparison/F063_RAW_full_torch_and_grasp_context_1x.png'),('sources/F044_same_rigid_grip_torch_SOURCE.png',(990,250,1220,690),'comparison/F044_original_whole_unit_and_grasp_1x.png'),('sources/F044_frozen_production_mother_REFERENCE_ONLY.png',(970,250,1240,700),'comparison/F044_flat_mother_whole_torch_and_near_hand_context_1x.png')]:
 assert np.array_equal(np.asarray(Image.open(R/src).crop(box)),np.asarray(Image.open(R/dst)))
print('PASS: package hashes;18 git-byte-exact snapshots; unchanged6ca8 trial/new fullgroup; old wholeunit s1 replay;1:1 true panes and source crops;0calls/069closed.')
