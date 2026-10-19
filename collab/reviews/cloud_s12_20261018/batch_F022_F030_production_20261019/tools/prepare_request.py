"""Bind actual continuity only after preceding real artwork passes self-review. No generator calls."""
from pathlib import Path
import json,hashlib,re,sys
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2];B=S/'batch_F022_F030_inputs_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['prompts','requests','originals','accepted','qa','provenance']:(O/name).mkdir(exist_ok=True)
clauses={22:'Draw only the per-frame contact specified below. In F022 only the far-left thumb pad first touches the UPPER OUTER SURFACE of the existing upper neck3 shaft; the palm and all other fingers stay above it with at least 3 scene pixels of real air, including outer ink and antialiasing. Do not draw an index wrap or a closed grasp in F022. Foreground finger pixels must come from the actual native artwork, never from added code fingers.',26:'Draw only the per-frame contact specified below. In F026 only the index newly wraps beneath/in front of the SAME existing upper neck3 shaft against the STATIONARY thumb. Palm and middle/ring/little remain above it without a completed grasp; all still-uncontacting digits keep at least3scene pixels real air including outer ink and antialiasing. Foreground finger pixels must come from the actual native artwork, never from added code fingers.',30:'Draw only the per-frame contact specified below. In F030 the remaining fingers complete the LEFT grasp around the SAME existing upper neck3 shaft; thumb and index contact remain stationary. The near right hand remains empty. Foreground finger pixels must come from the actual native artwork, never from added code fingers.'}
P={22:'(962,909)',26:'(967,918)',30:'(969,921)'}
lift='The crane remains cloth-supported and the body stays down throughout this segment. No F034 or later action is authorized here. A later lift remains forbidden until BOTH hands have separately established their planned grips and that later segment has been approved.'
footer='Image2 provides intrinsic material colors only. Ignore its outdated "Keep image1 F012 geometry" footer: geometry and temporal continuity come solely from the actual Image1 named in this request.'
old='Draw a plausible native grasp around the guide; future original-pixel finger layers must pass in front of the code upper shaft while rear palm stays behind, without double fingers.'
def prompt(f,prev,msha):
 t=(B/f'prompts/F{f:03d}.txt').read_text();lines=t.splitlines();lines[0]=f'S12 F{f:03d} ONLY, held F{f:03d}-F{f+3:03d}. Generate ONE native transparent1024x1536 RGBA grandmother on the SAME canvas and registration. No collage or another output stage.';t='\n'.join(lines)+'\n'
 t=re.sub(r'Image1 is the UNIQUE LOCKED F018 continuity mother, SHA256 [0-9a-f]+ \(approved commit[0-9a-f]+\)\. ', '',t,count=1)
 lead=f'Image1 is the {"LOCKED actual" if prev==18 else "ACCEPTED actual"} F{prev:03d} continuity mother, SHA256 {msha}.\n'
 assert old in t;t=t.replace(old,clauses[f]);phrase='crane stays cloth-supported, no lift/body rise before034.';assert phrase in t;t=t.replace(phrase,lift)
 t=t.replace('grasp cross-section G=(958,782.166145436) for ALL three stages.','fixed shaft cross-section G_AXIS_SCENE=(958,782.166145436); it is not a thumb-skin surface.')
 t=t.replace('Keep actual018 palm scale;','Keep actual Image1 palm scale, anchored to the accepted018 proportions;');t=t.replace('over a faded locked018 ghost;','over a faded locked018 construction ghost that is NOT a competing continuity mother;')
 t=re.sub(r'\. Native G=\[[^\]]+\]\.', '.',t)
 geom=f'P is the CURRENT index-MCP/palm reference, not a shaft contact or final-grip target; P{f:03d}={P[f]} native. G_AXIS=(975.714286,957.380208) native is the fixed shaft cross-section/future completed-grip reference, not the thumb\'s skin surface. T_SURFACE=(975.093564,952.418887) native is the nominal TOP OUTER shaft surface at that cross-section; the thumb pad touches T_SURFACE. Its construction centre is (974.348698,946.465302) with radius6 native. These are construction references: actual visible contour and the frozen7px code shaft decide contact. Do not paint labels or guides into artwork.'
 t=lead+t+'\n'+footer+'\n'+geom+'\nRetain the locked018 repaired shadow relationships: grey-blue shaded placket petals, blue fold plane, crown/bun gray without changing dark ear-back hair, ink or highlights. Compare intrinsic materials to Image2, not accumulating previous-frame color drift.\n'
 assert t.startswith(f'Image1 is the {"LOCKED actual" if prev==18 else "ACCEPTED actual"} F{prev:03d}') and old not in t and phrase not in t
 return t
# Explicit unbound future templates: no callable tool arguments or fake existing mother file.
for f,prev in [(26,22),(30,26)]:
 txt=prompt(f,prev,f'{{{{ACCEPTED_F{prev:03d}_SHA256}}}}');(O/f'prompts/F{f:03d}_TEMPLATE_NOT_BOUND.txt').write_text(txt)
 (O/f'requests/F{f:03d}_TEMPLATE_NOT_BOUND.json').write_text(json.dumps({'state':'NOT_BOUND_WAITING_FOR_REAL_PREVIOUS_ACCEPTANCE','execution_enabled':False,'output_frame':f,'requires_accepted_frame':prev,'future_image1':f'accepted/F{prev:03d}.png','prompt_template':txt,'fixed_material_board':str((B/'inputs/02_locked_F000_materials_ONLY.png').relative_to(R)),'approved_construction_board':str((B/f'inputs/03_F{f:03d}_VOLUME_CONTACT_CONSTRUCTION.png').relative_to(R)),'tool_arguments':None},indent=2)+'\n')
f=int(sys.argv[1]);prev={22:18,26:22,30:26}[f]
if prev==18:
 mother=B/'inputs/01_locked_F018.png';assert sha(mother)=='c63f57f53bc2f4bbca59dba4310ea55c0629b354520f8d0becbe88f932ff40be'
else:
 review=json.loads((O/f'qa/F{prev:03d}_self_review.json').read_text());mother=O/f'accepted/F{prev:03d}.png';assert review['status']=='ACCEPTED_FOR_NEXT_CONTINUITY' and review['accepted_SHA256']==sha(mother)
pp=O/f'prompts/F{f:03d}_EXACT.txt';rq=O/f'requests/F{f:03d}_call01.json';assert not rq.exists(),'Frozen request cannot be overwritten.';txt=prompt(f,prev,sha(mother));pp.write_text(txt)
paths=[mother,B/'inputs/02_locked_F000_materials_ONLY.png',B/f'inputs/03_F{f:03d}_VOLUME_CONTACT_CONSTRUCTION.png'];args={'prompt':txt,'referenced_image_paths':[str(p.resolve()) for p in paths],'transparent_background':True}
req={'status':'FROZEN_ACTUAL_REQUEST_BEFORE_UNIQUE_CALL','execution_enabled':True,'output_frame':f,'hold':4,'last_frame':f+3,'actual_continuity_mother_frame':prev,'tool':'image_gen.imagegen','tool_arguments':args,'prompt_SHA256':sha(pp),'actual_inputs':[{'order':i+1,'path':str(p.relative_to(R)),'sha256':sha(p)} for i,p in enumerate(paths)],'approved_input_package_commit':'1651ff2a56a1277d0e9132b688ae44d013da56f8','authorization':'Conditional one call each022->026->030; prior real accepted mother required, no retries; major anatomy/contact error stops sequence.'}
rq.write_text(json.dumps(req,indent=2)+'\n')
fp=O/f'provenance/F{f:03d}_freeze_SHA.json';fp.write_text(json.dumps({'frame':f,'previous_actual_frame':prev,'actual_mother_SHA256':sha(mother),'prompt_SHA256':sha(pp),'complete_request_SHA256':sha(rq),'calls_submitted':0},indent=2)+'\n')
ledger=O/'provenance/call_ledger.json'
if not ledger.exists():ledger.write_text(json.dumps({'authorized_max_calls_each':1,'source_S12_cumulative_calls':5,'calls_submitted':{'22':0,'26':0,'30':0},'returned_outputs':{'22':0,'26':0,'30':0},'inflight':None,'accepted_stages':[],'state':'F022_REQUEST_FROZEN_F026_F030_UNBOUND','scene_renders':0},indent=2)+'\n')
print(json.dumps({'frame':f,'mother_frame':prev,'prompt_SHA256':sha(pp),'request_SHA256':sha(rq),'tool_arguments':args}))
