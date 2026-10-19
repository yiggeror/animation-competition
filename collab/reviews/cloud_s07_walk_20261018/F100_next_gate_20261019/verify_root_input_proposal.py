#!/usr/bin/env python3
"""Read-only F100 proposal audit; isolated existing-prop/input replay, never imagegen."""
from pathlib import Path
from PIL import Image
import hashlib, json, subprocess, sys, tempfile, shutil
import numpy as np
from scipy.ndimage import distance_transform_edt
R=Path(__file__).resolve().parent
REPO=next(p for p in R.parents if (p/'.git').exists())
BASE='69db09b1b032f6ac1a4cbec06918d646d32c991a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert('RGBA'))
checked=[]
for row in json.loads((R/'sources/snapshot_manifest.json').read_text())['files']:
 p=R/'sources'/row['snapshot'];assert sha(p)==row['sha256'],p
 if ':frames' not in row['source_path']:
  b=subprocess.check_output(['git','show',BASE+':'+row['source_path']],cwd=REPO)
  assert p.read_bytes()==b,p
  checked.append(row['snapshot'])
args=json.loads((R/'requests/arguments_PREPARED_NOT_CALLED.json').read_text())
assert args['prompt']==(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').read_text().rstrip('\n')
assert args['transparent_background'] is True
assert [Path(x).name for x in args['referenced_image_paths']]==[f'{x}_F100_PREPARED_NOT_CALLED.png' for x in 'ABCD']
assert all(Path(x).read_bytes()==(R/'inputs_1024x1536'/Path(x).name).read_bytes() for x in args['referenced_image_paths'])
assert all(Image.open(R/'inputs_1024x1536'/Path(x).name).size==(1024,1536) for x in args['referenced_image_paths'])
g=json.loads((R/'geometry/F100_full_input_proposal_checks.json').read_text())
assert g['calls']==0 and g['F100_hold']==[100,102] and g['100_only_no103or106_input']
assert g['cropped_native']==[1240,0,1960,1080] and g['whole_inverse_scale']==45/64 and g['whole_inverse_offset']==[1240,0]
for file,src in [('F100_near_whole_shoe_FIXED.png','F095_near_shoe_ankle_COLLECTED_LANDED.png'),('F100_far_whole_shoe_FIXED.png','F095_far_shoe_ankle_SUPPORT_FIXED.png'),('F095_original_whole_trousers_FIXED_ARCHIVE.png','F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png')]:
 assert (R/'layers'/file).read_bytes()==(R/'sources'/src).read_bytes()
# Both source body and complete far arm use one scale-one rigid affine.
rig=g['body_lean_alternatives'][1];M=np.array(rig['M']);t=np.array(rig['t']);assert np.allclose(M.T@M,np.eye(2)) and np.isclose(np.linalg.det(M),1)
changes={}
for src,out in [('F095_body_head_blouse.png','F100_body_head_chest_whole_RIGID16.png'),('F095_far_complete_arm_jade_hand.png','F100_far_complete_arm_jade_whole_RIGID16.png')]:
 iv=np.linalg.inv(M);it=-iv@t
 expect=Image.open(R/'sources'/src).convert('RGBA').transform((1960,1080),Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
 n=int(np.any(np.array(expect)!=arr(R/'layers'/out),axis=2).sum());assert n==0,(out,n);changes[out]=n
# Real full palm/fingers to whole real prop material, independent of point/ellipse guides.
p=arr(R/'reference/existing_table_lamp_NATIVE_same_registration.png');h=arr(R/'layers/F100_whole_near_palm_fingers_R60_SOFT_GUIDE_NOT_FROZEN.png');gaps={}
for threshold in [1,16,128,240]:
 pm=p[:,:,3]>=threshold;hm=h[:,:,3]>=threshold;dist=distance_transform_edt(~pm);v=float(dist[hm].min());n=int((pm&hm).sum());assert n==0 and np.isclose(v,g['real_whole_hand_to_REAL_lamp_gap_by_alpha'][str(threshold)]['min_gap_native']);gaps[str(threshold)]={'native_gap':v,'overlap':n}
white=np.array(Image.open(R/'masks/WHITE_complete_near_arm_openhand_old_new_void_sleeve_waist.png'))>0
hard=np.zeros_like(white)
for m in (R/'masks').glob('HARD_*.png'):hard|=np.array(Image.open(m))>0
assert not (white&hard).any()
release=np.array(Image.open(R/'masks/OLD_near_hand_occlusion_cut_edge_RELEASED_NOT_TRUE_PANTS_CORE.png'))>0
pants=arr(R/'sources/F095_locked_actual_whole_trousers_ORIGINAL_COLOR.png');disp=arr(R/'layers/F100_pants_DISPLAY_only_old_cut_edge_released.png')
assert np.array_equal(pants[~release[:,:1672]],disp[~release[:,:1672]])
assert not disp[release[:,:1672]].any()
# Exact function copy and original existing lamp registration, without scene/person rendering.
html=(R/'reference/existing_lamp_ONLY_exact_source.html').read_text();src=(R/'sources/existing_lamp_source_s08.js').read_text();start=src.index('function lamp(');brace=src.index('{',start);depth=0;end=None
for i in range(brace,len(src)):
 if src[i]=='{':depth+=1
 elif src[i]=='}':
  depth-=1
  if depth==0:end=i+1;break
assert src[start:end] in html
assert 'x.translate(1262,642);x.scale(-.17,.17);x.translate(-LX,-LB);lamp(x,0,false);' in html
helper_manifest=json.loads((R/'package_manifest.json').read_text())
for row in helper_manifest['files']:assert sha(R/row['path'])==row['SHA256'],row
replayed=[]
with tempfile.TemporaryDirectory(prefix='s07_F100_root_isolated_') as d:
 T=Path(d)/'gate';shutil.copytree(R,T)
 subprocess.run([sys.executable,str(T/'build_prop_reference_html.py')],check=True,capture_output=True,timeout=10)
 assert (T/'reference/existing_lamp_ONLY_exact_source.html').read_bytes()==(R/'reference/existing_lamp_ONLY_exact_source.html').read_bytes()
 subprocess.run(['node',str(T/'render_existing_prop.cjs')],check=True,capture_output=True,timeout=30)
 assert np.array_equal(arr(T/'reference/existing_table_lamp_NATIVE_same_registration.png'),p)
 subprocess.run([sys.executable,str(T/'prepare_sources_and_contact.py')],check=True,capture_output=True,timeout=30)
 subprocess.run([sys.executable,str(T/'prepare_F100_proposed_input.py')],check=True,capture_output=True,timeout=30)
 for folder in ['reference','reference_native','inputs_1024x1536','layers','masks']:
  for f in sorted((R/folder).glob('*.png')):
   other=T/f.relative_to(R);assert other.exists() and np.array_equal(np.array(Image.open(f)),np.array(Image.open(other))),str(f)
   replayed.append(str(f.relative_to(R)))
manifest=R/'root_package_manifest.json';manifest_count=None
if manifest.exists():
 rows=json.loads(manifest.read_text())['files']
 for row in rows:assert sha(R/row['path'])==row['sha256'],row
 manifest_count=len(rows)
print(json.dumps({'status':'PROVENANCE_AND_REPLAY_PASS__INPUT_ART_HOLD__NOT_FROZEN_NOT_CALLED','source_git_commit':BASE,'source_git_byte_equal_count':len(checked),'helper_manifest_hash_count':len(helper_manifest['files']),'same_rigid_body_fararm_RGBA_changes':changes,'original_pants_and_both_whole_shoes_byte_identical':True,'old_near_hand_cut_edge_released_pixels':int(release.sum()),'whole_hand_to_real_prop':gaps,'white_hard_overlap':0,'exact_existing_prop_only_browser_RGBA_replay':True,'isolated_replayed_PNG_count':len(replayed),'four_inputs_isolated_replay_RGBA_equal':True,'all_manifest_hashes_PASS':manifest_count,'imagegen_calls':0,'F103_F106_input':False,'limits':'Only source/provenance/compositing/geometry checks; new full arm and broad missing waist are NOT_ART. Lean16 and projected95/110 are proposals, not measured anatomy. Retained navy/blue interface still visibly repeats the old hanging-hand negative contour. Waist is not repaired. Freeze and native drawing require Astra review.'},ensure_ascii=False,indent=2))
