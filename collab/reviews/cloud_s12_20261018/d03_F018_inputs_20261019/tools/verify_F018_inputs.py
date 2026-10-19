"""Read-only F018 input-gate verification; writes this packet's QA report only."""
from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,numpy as np
O=Path(__file__).resolve().parents[1]; S=O.parent; R=S.parents[2]
PARENT='0c31714179fc8bcc8914fa313b8d3935c7a53aa3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,condition,**facts):
    checks.append({'check':name,'passed':bool(condition),**facts})
    assert condition,name
sources={
 'F012':(S/'d02_F012_20261019/placket_tip_fix_20261019/candidate/F012.png','063bc020f65f3e9485a57984f20703f0fbc96667a2f5a046ad713ee51d1beb88'),
 'F000':(S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png','95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793'),
 'F018':(S/'first_left_grasp_inputs_20261019/inputs/F018_CONSTRUCTION.png','bcfaffbed6cca5012be23222cefa1035360cf7c8ede97648de82efc603449b8a'),
}
for role,(p,expected) in sources.items():
    committed=subprocess.check_output(['git','show',f'{PARENT}:{p.relative_to(R).as_posix()}'],cwd=R)
    check(f'{role}_locked_source_git_literal_and_SHA',p.read_bytes()==committed and sha(p)==expected,source=str(p.relative_to(R)),sha256=sha(p))
check('Image1_exact_new_locked_F012_copy',(O/'inputs/01_locked_F012.png').read_bytes()==sources['F012'][0].read_bytes())
check('Image3_original_F018_byte_unchanged',(O/'inputs/03_F018_CONSTRUCTION_UNCHANGED.png').read_bytes()==sources['F018'][0].read_bytes())
boardmeta=json.loads((O/'provenance/material_board_sources.json').read_text())
boardp=O/boardmeta['board_path']; board=Image.open(boardp); source=Image.open(sources['F000'][0]).convert('RGBA')
check('Image2_board_dimensions_and_SHA',board.mode=='RGB' and board.size==(960,1000) and sha(boardp)==boardmeta['board_SHA256'],size=list(board.size),sha256=sha(boardp))
check('board_source_authority',boardmeta['source_full_native_SHA256']==sources['F000'][1] and boardmeta['source_full_pose_is_not_a_tool_input'] and boardmeta['old103_not_a_tool_input'])
check('local_material_tile_count',len(boardmeta['tiles'])==12)
for row in boardmeta['tiles']:
    box=row['source_native_box_xyxy']; tilebox=row['display_tile_box']
    crop=source.crop(box); alpha=np.array(crop)[:,:,3]
    expected=crop.convert('RGB').resize((tilebox[2]-tilebox[0],tilebox[3]-tilebox[1]),Image.Resampling.NEAREST)
    actual=board.crop(tilebox)
    check(f"board_exact_source_RGB_{row['material']}",np.array_equal(np.array(actual),np.array(expected)) and int(alpha.min())>=240 and max(crop.size)<=40,source_box=box,source_min_alpha=int(alpha.min()))
req=json.loads((O/'requests/F018_NOT_EXECUTED.json').read_text()); args=req['tool_arguments']; prompt=(O/req['prompt_path']).read_text()
check('one_disabled_F018_request_only',req['execution_enabled'] is False and req['frame']==18 and req['hold']==4 and req['end_inclusive']==21 and [p.name for p in (O/'requests').iterdir()]==['F018_NOT_EXECUTED.json'])
check('actual_prompt_exact',args['prompt']==prompt and sha(O/req['prompt_path'])==req['prompt_SHA256'],prompt_SHA256=req['prompt_SHA256'])
check('supported_tool_arguments_only',set(args)=={'prompt','referenced_image_paths','transparent_background'} and args['transparent_background'] is True and req['tool']=='image_gen.imagegen')
expected_names=['01_locked_F012.png','02_locked_F000_materials_ONLY.png','03_F018_CONSTRUCTION_UNCHANGED.png']
check('exactly_three_inputs_order',len(args['referenced_image_paths'])==3 and [Path(x).name for x in args['referenced_image_paths']]==expected_names and len(req['actual_three_inputs'])==3)
for i,(pstr,row) in enumerate(zip(args['referenced_image_paths'],req['actual_three_inputs'])):
    p=Path(pstr)
    check(f'actual_input_{i+1}_path_SHA_and_decode',p==O/'inputs'/expected_names[i] and p.exists() and row['order']==i+1 and p.relative_to(R).as_posix()==row['path'] and sha(p)==row['sha256'],sha256=sha(p),size=list(Image.open(p).size),mode=Image.open(p).mode)
check('no_full_F000_old103_or_original03_tool_input',not any(Path(p).name in {'locked_F000.png','F000.png','03.png'} for p in args['referenced_image_paths']) and '103ed4fb52c64b370560456ff0dde5a0820596ecfed9e28daee0f026aef7b4ff' not in prompt and 'ab88b69f5303229af379303a37b6e9e3c8cdb35cd05b3902b604871efb2b1671' not in prompt)
for text in ['NEWLY LOCKED F012','MATERIAL-ONLY LOCAL RGB BOARD','ORIGINAL APPROVED F018','both hands are EMPTY','at least 3 scene pixels','actual 7px rod outline','F022 is the later first thumb-touch','crane is still supported by the cloth','including the sleeve','static lower placket TIP','grey-blue shaded flower fill','both COMPLETE cloth shoes','Deliver F018 only']:
    check(f'prompt_required_clause:{text}',text in prompt)
geom=json.loads((O/'provenance/approved_F018_volume_coordinates.json').read_text())
sourcegeom=R/geom['source_geometry']; committedgeom=subprocess.check_output(['git','show',f'{PARENT}:{sourcegeom.relative_to(R).as_posix()}'],cwd=R)
check('original_geometry_git_literal',sourcegeom.read_bytes()==committedgeom)
original18=next(x for x in json.loads(sourcegeom.read_text())['stages'] if x['frame']==18)
check('F018_volume_coordinates_unchanged',geom['same_original_F018_state']==original18 and geom['original_volume_image_SHA256']==sources['F018'][1])
ledger=json.loads((O/'provenance/preparation_ledger.json').read_text())
check('no_calls_renders_outputs_or_other_new_frames',ledger['prepared_frames']==[18] and ledger['imagegen_calls']==ledger['inflight_this_worker']==ledger['new_scene_renders']==ledger['new_art_outputs']==0 and ledger['prior_cumulative_S12_native_calls']==4 and ledger['other_new_frame_requests_created']==[])
view=json.loads((O/'qa/actual_image_review.json').read_text())
check('all_three_actual_images_viewed',view['method']=='view_image of each actual image separately' and len(view['images'])==3 and all(x['actual_image_viewed'] for x in view['images']) and [x['sha256'] for x in view['images']]==[x['sha256'] for x in req['actual_three_inputs']])
status=subprocess.check_output(['git','status','--porcelain','-z','--untracked-files=all'],cwd=R).decode()
paths=[x[3:] for x in status.split('\0') if x]
check('working_changes_within_this_packet_only',all(x.startswith(O.relative_to(R).as_posix()+'/') for x in paths),changed_paths_outside_packet=[x for x in paths if not x.startswith(O.relative_to(R).as_posix()+'/')])
report={'status':'PASS','scope':'F018 SINGLE INPUT GATE ONLY. No generation or scene-render acceptance implied.','source_parent_commit':PARENT,'checks_passed':len(checks),'checks':checks}
(O/'qa/input_gate_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks_passed':len(checks),'inputs':[{'order':x['order'],'sha256':x['sha256']} for x in req['actual_three_inputs']],'prompt_SHA256':req['prompt_SHA256'],'imagegen_calls':0,'scene_renders':0},ensure_ascii=False,indent=2))
