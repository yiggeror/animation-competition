from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2];FIXED='d2483baa791ae818219644093cf620303539371a';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((O/'provenance/actual_call01_request.json').read_text());approved=json.loads((O/'provenance/approved_request_UNCHANGED.json').read_text());assert q['tool_arguments']==approved['tool_arguments']
for row,pstr in zip(q['actual_three_inputs'],q['tool_arguments']['referenced_image_paths']):
 p=Path(pstr);assert sha(p)==row['sha256'] and p.read_bytes()==subprocess.check_output(['git','show',FIXED+':'+p.relative_to(R).as_posix()],cwd=R)
prompt=O/'prompts/F018_EXACT_APPROVED.txt';assert sha(prompt)=='fbadda161afa5914204269f5383d25dca0ec3a00fc1a733eb4a78767abd89185' and prompt.read_text()==q['tool_arguments']['prompt']
raw=O/'originals/F018_raw_call01.png';original=Path('/workspace/generated_images/exec-af430783-07d1-4303-8bab-6d6f54915eac.png');assert original.exists() and raw.read_bytes()==original.read_bytes() and sha(raw)=='fbc502639b90de00eb0b664a41af7898df15e92bf5d58ac9e172579121b486a3';im=Image.open(raw);im.load();assert im.size==(1024,1536) and im.mode=='RGBA'
ledger=json.loads((O/'provenance/call_ledger.json').read_text());assert ledger['tool_calls_submitted']==ledger['returned_outputs']==1 and ledger['inflight']==ledger['scene_renders']==0 and ledger['cumulative_S12_native_calls']==5 and not ledger['F022_opened']
audit=json.loads((O/'qa/actual_native_validation.json').read_text());assert not audit['all_actual_hand_skin_gaps_at_least3_scene_px'] and not audit['all_four_materials_pass'];assert audit['hand_to_fixed_rod_outline_gaps']['far_left']['L']['conservative_min_gap_to_7px_outline_scene_px']<0
assert not audit['materials']['hair']['within_4'] and not audit['materials']['blouse_blue']['within_4'] and audit['materials']['skin']['within_4'] and audit['materials']['trousers']['within_4']
paths=[x[3:] for x in subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=R).decode().splitlines()];assert all(x.startswith(O.relative_to(R).as_posix()+'/') for x in paths)
report={'integrity':'PASS_SOURCE_AND_ONE_CALL_RECORD','art_review':'NOT_LOCKED_GAP_AND_COLOR_FAIL','raw_SHA256':sha(raw),'exact_approved_prompt_and_three_input_bytes':True,'native_RGBA_unmodified':True,'tool_saved_original_retained_and_byte_equal':True,'unique_F018_calls':1,'S12_cumulative_native_calls':5,'new_scene_renders':0,'F022_opened':False,'working_changes_outside_own_packet':[]};(O/'qa/delivery_integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
