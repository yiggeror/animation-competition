"""Promote the public accepted000-105 sources; tail deliberately absent.
No art generation, pixel edits, exposure padding, or old code-person animation.
"""
from pathlib import Path
import json,math,hashlib,shutil,re
ROOT=Path(__file__).resolve().parents[5];R=ROOT/'collab/reviews/cloud_s12_20261018';O=ROOT/'assets/chars/g12';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={0:'d01_F000/same_raw_fix_20261019',12:'d02_F012_20261019/placket_tip_fix_20261019',18:'d03_F018_20261019/same_raw_fix_20261019',22:'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019',26:'F026_index_repair_actual_call01_20261019',30:'F030_close_grip_from_locked026_20261019',34:'F034_F040_actual_20261019/F034',40:'F034_F040_actual_20261019/F040',48:'F048_F052_actual_20261019/F048',52:'F048_F052_actual_20261019/F052',56:'F056_hypothenar_actual_call01_20261019',60:'BLUE_sleeve_root_actual_call01_20261019/F060',64:'BLUE_sleeve_root_actual_call01_20261019/F064',70:'F070_COMPLETE_actual_call01_20261019',74:'F074_PANTS_LOCAL_actual_call01_20261019',78:'F078_NARROW_JOIN_actual_call01_20261019',82:'F082_COMPLETE_PANTS_JOIN_actual_call01_20261019',86:'F086_COMPLETE_actual_call01_20261019',90:'F090_SAME_RAW_SEMANTIC_OWNERSHIP_FIXED_20261019',94:'F094_LOCAL_ARMS_KNEES_actual_call01_20261019',98:'F098_EXACT_NATIVE_ACTIVITY_actual_call01_20261020',102:'F102_EXACT_NATIVE_ACTIVITY_actual_call01_20261020'}
A=json.loads((R/'geometry/three_key_pose_proposal.json').read_text())['states'][0];AP=A['points_scene'];log=[];copied={}
def copy_asset(path,label):
 h=sha(path)
 if h not in copied:
  name=f'{label}_{h[:12]}.png';shutil.copyfile(path,O/name);copied[h]=name;log.append({'source':str(path.relative_to(ROOT)),'asset':name,'SHA256':h})
 return copied[h]
def basis(tilt,roll=0):
 b,a,t,z=map(math.radians,[15,12,tilt,roll]);u=[math.cos(b),-math.sin(a)*math.sin(b)];v=[-math.cos(t)*math.sin(b),-(math.sin(t)*math.cos(a)+math.cos(t)*math.cos(b)*math.sin(a))];c,s=math.cos(z),math.sin(z)
 return [[.72*(c*u[0]-s*u[1]),.72*(c*v[0]-s*v[1])],[.72*(s*u[0]+c*u[1]),.72*(s*v[0]+c*v[1])]]
def prop(frame):
 if frame<70:
  left=AP['free_gripL'] if frame<34 else ([931.5123178589768,757.1297395769899] if frame<40 else [930.1059238245394,729.1297395769899])
  return {'root':AP['crane_root'],'matrix':basis(55),'pose':A['code_pose'],'free':{'R':AP['free_gripR'],'L':left},'paperDegrees':55}
 early={70:('F070_COMPLETE_TARGET_from_LOCKED064_20261019/geometry/F070_COMPLETE_BODY_AND_TRUE_CONTACTS.json','new_true_points_scene',0),74:('F074_COMPLETE_TARGET_from_LOCKED070_20261019/geometry/F074_COMPLETE_BODY_AND_TRUE_CONTACTS.json','new_true_points_scene',0),78:('F078_COMPLETE_TARGET_from_FINAL074_20261019/geometry/F078_COMPLETE_RISE_AND_TRUE_CONTACTS.json','true_points_target',-3),82:('F082_ACTIVE_TARGET_FIXED074_SUPPORTS_20261019/geometry/F082_COMPLETE_ACTIVE_RISE_TRUE_CONTACTS_AND_SUPPORT_DOMAIN.json','true_points_target_F082',-6),86:('F086_COMPLETE_TARGET_FROM_FINAL082_20261019/geometry/F086_FULL_RISE_BOTH_ARM_TRUE_PROP_AND_FIXED_SUPPORT_GEOMETRY.json','true_points_target_F086',-8)}
 if frame in early:
  file,key,roll=early[frame];q=json.loads((R/file).read_text())[key];return {'root':q['crane_root'],'matrix':basis(55,roll),'pose':A['code_pose'],'free':{'R':q['body_free'],'L':q['neck3_free']},'paperDegrees':55}
 files={90:'F090_COMPLETE_TARGET_FROM_FINAL086_20261019/geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json',94:'F094_COMPLETE_TARGET_FROM_LOCKED090_20261019/geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json',98:'F098_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL094_20261020/geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json',102:'F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020/geometry/F102_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json'}
 p=json.loads((R/files[frame]).read_text())['prop_plan'];bb=p['paper_3D_camera_basis'];k=p['mm_to_scene_scale'];return {'root':p['root_scene'],'matrix':[[k*bb[0][0],k*bb[0][1]],[k*bb[1][0],k*bb[1][1]]],'pose':p['code_pose'],'free':{r:p['rods'][r]['free_scene'] for r in ['R','L']},'paperDegrees':p['paper_plane_inclination_degrees']}
pressure=R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png';states=[];keys=list(sources)
for i,frame in enumerate(keys):
 d=R/sources[frame];tag=f'F{frame:03d}';candidate=d/f'candidate/{tag}.png';assert candidate.exists(),candidate
 bgs=list((d/'layers').glob(tag+'_BG_*.png'));fgs=list((d/'layers').glob(tag+'_FG_*.png'))
 bg=copy_asset(bgs[0] if bgs else candidate,tag+'_BG');fg=copy_asset(fgs[0],tag+'_FG') if fgs else None
 scene=next((d/'scene').glob('s12_*.js'));text=scene.read_text();stage=pressure
 if 'async function bg()' in text:
  tail=text[text.index('async function bg()'):];match=re.search(r"new URL\('([^']+\.png)'",tail)
  if match:stage=(scene.parent/match.group(1)).resolve()
 state={'key':frame,'start':frame,'end':keys[i+1]-1 if i+1<len(keys) else 105,'bg':bg,'fg':fg,'background':copy_asset(stage,'stage'),'prop':prop(frame),'transmission':0}
 states.append(state);log.append({'frame':frame,'native_source':str(candidate.relative_to(ROOT)),'native_SHA256':sha(candidate),'end':state['end']})
shadow=copy_asset(R/'F102_EXACT_NATIVE_ACTIVITY_actual_call01_20261020/actual_scene/F102_native_ground_shadows_actual_layer.png','contact_shadow');front=copy_asset(R/'F102_EXACT_NATIVE_ACTIVITY_actual_call01_20261020/actual_scene/F102_box_front_actual_layer.png','box_front')
manifest={'fps':24,'totalFrames':192,'duration':8,'availableThrough':105,'status':'PUBLIC_FRONT_ONLY_TAIL_NOT_YET_ADOPTED','registration':{'x':275,'y':112,'scale':.7},'contactShadow':shadow,'boxFront':front,'states':states}
(O/'sequence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(R/'formal_scene_20261020/front_source_adoption.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'front_exposure_rows':len(states),'availableThrough':105,'unique_production_PNGs':len(copied),'tail_included':False}))
