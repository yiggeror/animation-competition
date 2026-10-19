#!/usr/bin/env python3
"""Validate the0-generation detail/F000 gate without re-rendering anything."""
from pathlib import Path
import json,hashlib,csv,math,re,ast,subprocess,sys
from PIL import Image
import numpy as np
sys.dont_write_bytecode=True
import build_references as r
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1];G=D/'provenance/gate_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((G/'protocol_and_baseline.json').read_text())
for name in ['S20_216f_beats.csv','S20_216f_frame_phase_map.csv','S20_reference_plan.json']:assert sha(D/name)==base['locked_file_sha256'][name],name
with (D/'S20_216f_frame_phase_map.csv').open() as fp:frames=list(csv.DictReader(fp))
assert [int(x['frame']) for x in frames]==list(range(216));assert frames[132]['phase']=='B11' and frames[144]['camera']=='CAMG';assert all(x['camera']=='CAM20' for x in frames[:144])
details=json.loads((G/'same_view_details.json').read_text())
for v in details['records']:
 main=Image.open(D/v['main_PNG']).convert('RGBA').crop(v['main_crop_bounds_xyxy']);native=Image.open(D/v['native_detail']).convert('RGBA');assert np.array_equal(np.array(main),np.array(native));assert sha(D/v['native_detail'])==v['native_detail_sha256'];assert v['positive_uniform_scale']==4 and v['rotation_degrees']==0 and not v['horizontal_flip'] and not v['vertical_flip']
 v['final_main_PNG_sha256']=sha(D/v['main_PNG']);v['final_main_crop_RGBA_exact_to_native_detail']=True
(G/'same_view_details.json').write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n')
bands=details['independent_contact_bands'];assert len(bands)==4 and len(set((b['key'],b['rod']) for b in bands))==4
for b in bands:assert b['thumb_side_xy']!=b['opposed_finger_side_xy']
assert next(x for x in bands if x['rod']=='TH')['centre_xy'][1]<next(x for x in bands if x['rod']=='TS')['centre_xy'][1]
assert next(x for x in bands if x['rod']=='CN')['centre_xy'][1]<next(x for x in bands if x['rod']=='CB')['centre_xy'][1]
transfers=json.loads((G/'three_time_transfers.json').read_text());assert len(transfers)==3
for key,rods,givers,receivers in [('T',['TH','TS'],['G.R','G.R'],['X.R','X.L']),('CB',['CB'],['G.L'],['G.R']),('CN',['CN'],['G.L'],['G.R'])]:
 v=transfers[key];assert len(v['states'])==3 and v['frames']=={'T':[8,20,32],'CB':[36,42,47],'CN':[132,138,143]}[key]
 for rod,giver,receiver in zip(rods,givers,receivers):
  a,b,c=[set(s[rod]) for s in v['states']];assert giver in a and receiver not in a;assert {giver,receiver}<=b;assert receiver in c and giver not in c
 for state in v['states']:assert all(state[rod] for rod in v['rods'])
# Preserve non-transferred crane support in both self-transfer diagrams.
assert all(s['CN']==['G.L'] for s in transfers['CB']['states']);assert all(s['CB']==['G.R'] for s in transfers['CN']['states'])
F=D/'F000';manifest=json.loads((F/'input_manifest.json').read_text());request=json.loads((F/'request_prepared.json').read_text());state=json.loads((F/'F000_start_state.json').read_text());primary=F/'inputs/F000_fullbody_four_rods.png'
assert state['frame']==0 and state['child_contact_count']==0 and state['held_rod_count']==4 and state['F020_used_as_input'] is False
assert state['holders']=={'TH':['G.R'],'TS':['G.R'],'CB':['G.L'],'CN':['G.L']};assert set(state['child_hands_open'])=={'X.R','X.L'}
assert state['child_pose']['R']!=r.FIGS['A_X']['R'] and state['child_pose']['L']!=r.FIGS['A_X']['L'];assert Image.open(primary).size==(1672,941)
for actor in [state['grandma_pose'],state['child_pose']]:
 for hand in ['R','L']:
  sh,el,wr=actor[hand];assert math.dist(sh,el)<= (100 if actor['k']=='G' else 90)+1e-6;assert math.dist(el,wr)<=(90 if actor['k']=='G' else 80)+1e-6
assert request['submitted'] is False and request['attempts']==0 and len(request['args']['referenced_image_paths'])==5;assert request['args']['transparent_background'] is True
assert request['args']['prompt']==(F/'prompt_zh.txt').read_text()
for item in [manifest['unique_pose_input'],*manifest['identity_inputs']]:
 p=ROOT/item['repo_path'];assert p.exists() and sha(p)==item['sha256'] and str(p) in request['args']['referenced_image_paths'];assert 'F020' not in str(p)
assert sha(primary)==manifest['unique_pose_input']['sha256'];assert sha(primary)!=sha(D/'reference/S20_K01_F020_handoff.png')
def distance_to_segment(p,a,b):
 vx,vy=b[0]-a[0],b[1]-a[1];u=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)));return math.hypot(p[0]-a[0]-u*vx,p[1]-a[1]-u*vy)
clearance={}
for hand in ['L','R']:
 p=r.world(state['child_pose'],state['child_pose']['palms'][hand]);clearance[hand]=min(distance_to_segment(p,a['start'],a['end']) for a in state['rod_axes'])*.94;assert clearance[hand]>65
for item in json.loads((D/'provenance/reference_render.json').read_text())['files']:
 assert sha(D/item['source'])==item['source_sha256'] and sha(D/item['PNG'])==item['sha256'];assert list(Image.open(D/item['PNG']).size)==item['size']
for row in json.loads((D/'provenance/source_manifest.json').read_text())['sources']:assert sha(ROOT/row['path'])==row['sha256']
for p in (D/'tools').glob('*.py'):ast.parse(p.read_text())
outside=subprocess.check_output(['git','diff','--name-only','58a44a4','--',':!collab/reviews/cloud_s20_20261018'],cwd=ROOT,text=True).strip();assert not outside
proof={'action_protocol_frozen':True,'reference_and_F000_input_gate':'PENDING_ASTRA_SMALL_GATE','zero_image_generation_calls':True,'zero_submitted_image_requests':True,'216f_phase_CSV_and_plan_byte_identical_to58a44a4':True,'original_cut_frame':144,'original_flip_frame':132,'same_view_details_final_main_RGBA_exact':2,'same_view_positive_scale':4,'same_view_mirror_or_rotation':False,'K02_order':'R/T_H aboveL/T_S','K03_order':'orangeC_N abovegreenC_B','independent_thumb_opposed_finger_contact_bands':4,'three_transfers_three_timepoints_each':True,'giver_kept_closed_in_shared_state_before_release':True,'unique_F000_PNG_SHA256':sha(primary),'unique_F000_size':[1672,941],'F000_G_L':['C_B','C_N'],'F000_G_R':['T_H','T_S'],'F000_child_contacts':0,'F000_projected_arm_lengths_within_frozen_construction_targets':True,'F000_child_palm_to_rod_min_distance_px':clearance,'F020_in_prepared_input_list':False,'prepared_input_count':5,'outside_exclusive_directory_changes':[],'production_ready':False}
(G/'verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps(proof,ensure_ascii=False,indent=2))
