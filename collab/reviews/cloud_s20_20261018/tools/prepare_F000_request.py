#!/usr/bin/env python3
"""Write the exact, inspectable future request; never calls imagegen."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1];F=D/'F000';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pose=F/'inputs/F000_fullbody_four_rods.png';assert pose.exists() and Image.open(pose).size==(1672,941)
inputs=[(pose,'唯一F000起始体量/四杆持有输入：小满零接触，奶奶持四杆'),(ROOT/'collab/refs/grandma_turnaround_current03_draft.png','奶奶身份/全身比例与左腕玉镯'),(ROOT/'collab/refs/grandma_expressions_current02.png','奶奶面部身份、中性颈肤与温和起始表情'),(ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png','小满身份/双马尾/衣裙/完整身体'),(ROOT/'collab/refs/xiaoman_expressions_current03.png','小满面部身份与自然表情')]
rows=[]
for i,(p,role) in enumerate(inputs,1):
 assert 'F020' not in str(p) and 'handoff.png' not in str(p)
 im=Image.open(p);rows.append({'order':i,'repo_path':str(p.relative_to(ROOT)),'actual_local_path':str(p),'role':role,'sha256':sha(p),'size':list(im.size)})
state=json.loads((F/'F000_start_state.json').read_text());assert state['child_contact_count']==0 and state['held_rod_count']==4
manifest={'status':'PREPARED_NOT_SUBMITTED','frame':0,'unique_pose_input':rows[0],'identity_inputs':rows[1:],'F020_is_not_an_input':True,'all_referenced_files_exist':True,'image_generation_calls':0,'attempts':0,'raw_generated_outputs':[],'request_requires_Astra_F000_input_gate':True,'initial_holders':state['holders']}
(F/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
req={'tool':'image_gen.imagegen','submitted':False,'attempts':0,'status':'PREPARED_NOT_SUBMITTED','args':{'prompt':(F/'prompt_zh.txt').read_text(),'transparent_background':True,'referenced_image_paths':[str(p) for p,_ in inputs]},'portable_input_manifest':'input_manifest.json','note':'Local paths are concrete for this worktree; use repo_path+SHA when moving the prepared request. NoF020 pose and no generated character output.'}
(F/'request_prepared.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
# A QA-only crop derived from the unique input; it is deliberately not an imagegen input.
qa=F/'qa';qa.mkdir(exist_ok=True);im=Image.open(pose).convert('RGBA');crop=(940,340,1110,555);small=im.crop(crop).resize((680,860));board=Image.new('RGB',(960,1040),'#f6f7f8');board.paste(small.convert('RGB'),(40,110));dr=ImageDraw.Draw(board);font=ImageFont.truetype(str(ROOT/'assets/fonts/NotoSansSC-VF.ttf'),24)
dr.text((25,20),'F000实际输入裁片：G.L两鹤签，G.R两龟签',font=font,fill='#263440')
col={'TH':'#167d9f','TS':'#b24779','CN':'#c47b24','CB':'#3d7f57'}
contacts=[]
for a in state['rod_axes']:
 px=.94*a['contact'][0]+200;py=.94*a['contact'][1]-80;dx=a['contact'][0]-a['start'][0];dy=a['contact'][1]-a['start'][1];ll=math.hypot(dx,dy);u=(dx/ll,dy/ll);n=(-u[1],u[0]);cx=40+(px-crop[0])*4;cy=110+(py-crop[1])*4
 for sign in [-1,1]:dr.line((cx-4*u[0]*4+sign*3*n[0]*4,cy-4*u[1]*4+sign*3*n[1]*4,cx+4*u[0]*4+sign*3*n[0]*4,cy+4*u[1]*4+sign*3*n[1]*4),fill=col[a['id']],width=3)
 dr.text((750,cy-12),a['id']+' '+a['owner'],font=font,fill=col[a['id']]);contacts.append({'rod':a['id'],'owner':a['owner'],'input_contact_centre_px':[px,py],'thumb_and_finger_contact_sides':True})
dr.text((25,994),'QA接触剖示；不在实际生图输入清单内。',font=font,fill='#263440');board.save(qa/'F000_hold_contacts_same_view.png')
(F/'qa/contact_record.json').write_text(json.dumps({'source_unique_F000_PNG_sha256':sha(pose),'crop_xyxy':crop,'positive_scale':4,'mirror':False,'contacts':contacts,'this_annotated_crop_is_not_in_prepared_request':True,'image_generation_calls':0},ensure_ascii=False,indent=2)+'\n')
print('Prepared5 exact input paths + complete prompt. UniqueF000SHA:',sha(pose));print('Imagegen submitted:false / attempts0 / noF020 input.')
