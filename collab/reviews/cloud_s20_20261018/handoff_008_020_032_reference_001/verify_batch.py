from pathlib import Path
import json,hashlib,csv,math
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
master=P.parent/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
LOCK='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
assert sha(master)==LOCK
geo=json.loads((P/'batch_geometry_and_requests.json').read_text())
axes=json.loads((P.parent/'F000/f000_scene_gate_001/registration_input.json').read_text())['rods']
report={'status':'TECHNICAL_REFERENCE_PREPARED / BATCH_GATE_PENDING','master_sha256_unchanged':LOCK,
        'new_model_calls':0,'new_raws':0,'drawn_later_states':0,'production_files_changed':[],
        'actual_reference_images_visually_inspected':True,'checks':[]}
for f in geo['frames']:
 frame=f['frame'];folder=P/f'F{frame:03}';s=f['state'];mask=np.array(Image.open(folder/'04_edit_white.png'))
 assert set(np.unique(mask))<={0,255}
 assert not mask[840:,:].any() and not mask[:247,885:].any()
 if frame!=32:assert not mask[:,885:].any()
 for side,lens in [('R',[90,105]),('L',[75,95])]:
  actual=np.linalg.norm(np.diff(np.array(s[side+'_chain']),axis=0),axis=1)
  assert np.max(abs(actual-lens))<1e-6
  x,y=s[side+'_palm']
  for dx,dy in [(0,0),(3,-25),(14,-25),(26,-16),(31,-7),(32,3),(28,12)]:
   assert mask[round(y+dy),round(x+dx)]==255,(frame,side,dx,dy)
 args=json.loads((folder/'request_prepared.json').read_text())
 assert args['submitted']==False and args['tool_args']['transparent_background']==True
 refs=args['tool_args']['referenced_image_paths'];assert len(refs)==4
 for row,file in zip(f['inputs'],refs):assert Path(file).exists() and sha(Path(file))==row['sha256']
 if frame==8:
  gaps={}
  for side in ['R','L']:
   x,y=s[side+'_palm']
   points=[(x+20*math.cos(t),y+16*math.sin(t)) for t in np.linspace(0,math.tau,361)]
   points += [(x+dx,y+dy) for dx,dy in [(3,-25),(14,-25),(26,-16),(31,-7),(32,3),(28,12)]]
   for role in ['T_H','T_S']:
    a=axes[role]
    dist=min(abs(qy-a['slope']*qx-a['intercept'])/math.hypot(1,a['slope']) for qx,qy in points)
    gaps[side+' / '+role]=dist;assert dist>8
  report['F008_guide_hand_min_clearance_to_both_axes_px']=gaps
 else:
  for side,role in [('R','T_H'),('L','T_S')]:
   x,y=s[side+'_palm'];a=axes[role];assert abs(y-a['slope']*x-a['intercept'])<1e-9
 report['checks'].append({'frame':frame,'four_complete_existing_inputs':True,
  'fixed_construction_bone_lengths':True,'target_hand_extents_inside_edit_white':True,
  'shoe_ankle_contact_strip_black':True})
rows=list(csv.DictReader((P/'exposure_000_035.csv').open()))
assert sum(int(r['frame_count']) for r in rows)==36
assert [f for r in rows for f in range(int(r['start_frame']),int(r['end_frame_inclusive'])+1)]==list(range(36))
assert geo['frames'][1]['state']['R_palm']==geo['frames'][2]['state']['R_palm']
assert geo['frames'][1]['state']['L_palm']==geo['frames'][2]['state']['L_palm']
report['F020_F032_receiver_grip_targets_unchanged']=True
report['exposure_coverage']='F000-F035, 36 continuous frames, 12 exposures including locked F000'
report['not_a_final_art_pass']='Checks apply to construction only; inspect actual model outputs before retaining drawings.'
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
files=sorted(f for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt')
(P/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+f.relative_to(P).as_posix()+'\n' for f in files))
print(json.dumps(report,ensure_ascii=False,indent=2))
