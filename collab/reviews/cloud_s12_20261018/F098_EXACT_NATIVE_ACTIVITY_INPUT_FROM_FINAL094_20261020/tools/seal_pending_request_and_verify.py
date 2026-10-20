"""Read back actual PNG pixels and seal an explicitly UNsubmitted request."""
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F094_LOCAL_ARMS_KNEES_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert('RGBA'))
g=json.loads((O/'geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text());p=g['prop_plan'];l=json.loads((O/'provenance/SOLE_FINAL094_MOTHER.json').read_text())
assert sha(Path(l['native_path']))==l['native_SHA256'];assert sha(Path(l['actual_Canvas_path']))==l['actual_Canvas_SHA256']
N=arr(O/'anatomy/F098_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png');B=arr(M/'candidate/F094.png')
bg=arr(O/'anatomy/F098_REFERENCE_BG.png');fg=arr(O/'anatomy/F098_REFERENCE_FG_REAL_FRONT_FINGERS.png')
allow=np.array(Image.open(O/'masks/ALLOW_MINIMAL_NATIVE_ACTIVITY.png'))>0
prot=np.array(Image.open(O/'masks/HARD_PROTECTED_NATIVE_SUPPORT_AND_OUTSIDE.png'))>0
support=np.array(Image.open(O/'masks/HARD_QUALIFIED_FINAL094_SHINS_SHOES_AIR.png'))>0
assert np.array_equal(allow,~prot);assert not np.any(allow&support)
protected_diff=int(np.count_nonzero(np.any(N!=B,axis=2)&prot));support_diff=int(np.count_nonzero(np.any(N!=B,axis=2)&support))
overlap=int(np.count_nonzero((bg[:,:,3]>0)&(fg[:,:,3]>0)));reconstruction=int(np.count_nonzero(np.any(np.maximum(bg,fg)!=N,axis=2)))
assert protected_diff==support_diff==overlap==reconstruction==0
read=json.loads((O/'qa/TRUE_PROP_REFERENCE_READBACK.json').read_text());assert not read['browser_errors'];assert read['person_draws']==0
numeric={}
for role,a in g['arms'].items():
 H=np.array(a['whole_hand_bangle_same_rod_angle_matrix']);c=np.r_[a['source_final094']['true_grip'],1];t=np.array(a['target']['true_grip'])
 handres=float(np.linalg.norm(H@c-t));assert handres<1e-8;assert np.allclose(H[:,:2].T@H[:,:2],np.eye(2));assert abs(np.linalg.det(H[:,:2])-1)<1e-8
 rod=p['rods'][role];v=np.array(rod['free_camera3D_scene_units'])-np.array(rod['hinge_camera3D_scene_units']);lengthres=abs(float(np.linalg.norm(v))-rod['physical_length_scene_units'])
 hingres=float(np.linalg.norm(np.array(read['hinges_scene'][role])-rod['hinge_scene']));assert lengthres<1e-8 and hingres<1e-7
 numeric[role]={'rigid_complete_hand_grip_residual_native':handres,'rigid_hand_scale':1,'independent_finger_moves':0,'physical_rod_length_scene':rod['physical_length_scene_units'],'physical_rod_length_residual':lengthres,'actual_makeCrane_hinge_residual_scene':hingres,'native_true_grip':a['target']['true_grip'],'straight_reach_spare_native':a['straight_reach_spare_native']}
def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=Image.open(O/'code_props/F098_BOX_CLOTH_UNLOAD_CONTEXT_REFERENCE.png').convert('RGBA')
for im in [Image.open(M/'actual_scene/F094_native_ground_shadows_actual_layer.png').convert('RGBA'),scene(Image.fromarray(bg)),Image.open(O/'code_props/F098_TRUE_CRANE_AND_TWO_PHYSICALLY_RIGID_RODS_REFERENCE.png').convert('RGBA'),scene(Image.fromarray(fg)),Image.open(M/'actual_scene/F094_box_front_actual_layer.png').convert('RGBA')]:ctx.alpha_composite(im)
contextdiff=int(np.count_nonzero(np.any(np.array(ctx)!=arr(O/'anatomy/F098_SAME_PERSON_TRUE_PROP_BOX_GROUND_CONTEXT_REFERENCE_ONLY.png'),axis=2)));assert contextdiff==0
files=['inputs/01_F098_EXACT_NATIVE_ACTIVITY_TARGET.png','inputs/02_SAME_F098_TRUE70_PAPER_RODS_BOX_GROUND_CONTEXT.png'];inputs=[]
for f in files:
 q=O/f
 with Image.open(q) as im:
  im.load();size=list(im.size)
 inputs.append({'order':len(inputs)+1,'path':str(q.resolve()),'SHA256':sha(q),'decoded_size':size,'actually_opened_and_visually_reviewed':True})
promptpath=O/'prompts/F098_FULL_PENDING_PROMPT.txt';prompt=promptpath.read_text()
request={'status':'INPUT_GATE_PENDING_NOT_SUBMITTED','explicit_generation_gate_passed':False,'tool_name':'image_gen.imagegen','tool_calls_made':0,'args':{'prompt':prompt,'referenced_image_paths':[x['path'] for x in inputs],'transparent_background':True},'input_order_and_SHA256':inputs,'full_prompt_file':str(promptpath.resolve()),'full_prompt_SHA256':sha(promptpath),'sole_source_final094_native_SHA256':l['native_SHA256'],'expected_native_output_size':[1024,1536],'no_raw098_output_exists':True,'production_candidate_exists':False}
(O/'requests/F098_EXACT_PENDING_REQUEST_NOT_SUBMITTED.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
report={'status':'TWO_ACTUALLY_VIEWED_REFERENCES_SEALED_FOR_ASTRA_INPUT_GATE_NOT_A_FINISHED_DRAWING','input_PNGs':inputs,'full_prompt_SHA256':sha(promptpath),'request_submitted':False,'new098_imagegen_calls':0,'new102_imagegen_calls':0,'new098_raw_outputs':0,'actual098_person_Canvas':0,'code_prop_reference_batches':1,'code_prop_person_draws':0,'comparison_native_file':'anatomy/F098_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png','protected_native_RGBA_differing_pixels':protected_diff,'qualified_final094_support_RGBA_differing_pixels':support_diff,'reference_BG_FG_overlap_pixels':overlap,'reference_BG_FG_RGBA_reconstruction_differing_pixels':reconstruction,'input2_same_person_context_RGBA_reconstruction_differing_pixels':contextdiff,'paper_degrees':70,'root_scene':p['root_scene'],'actual_hinges_and_rigid_hands':numeric,'visual_readback':['Final complete input01 and final complete input02 actually opened after wrist cleanup.','Real hands/bangle and both shaft axes examined in actual context crop.','Chest/waist alpha gaps and displaced knee ghost from internal assembly removed before sealing.','Head/face/collar and natural existing knee cloth retained from the sole final094.','Remaining sleeve/elbow/wrist and small rib cloth material joins require natural new drawing; not claimed production-qualified.'],'generation_blocker':'Astra must review these exact two inputs / request before the sole proposed098 generation. No generation is authorized by this report.'}
(O/'qa/FINAL_INPUT_GATE_READBACK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
critical=files+['prompts/F098_FULL_PENDING_PROMPT.txt','requests/F098_EXACT_PENDING_REQUEST_NOT_SUBMITTED.json','geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json','provenance/SOLE_FINAL094_MOTHER.json','masks/ALLOW_MINIMAL_NATIVE_ACTIVITY.png','masks/HARD_PROTECTED_NATIVE_SUPPORT_AND_OUTSIDE.png','masks/HARD_QUALIFIED_FINAL094_SHINS_SHOES_AIR.png','qa/FINAL_INPUT_GATE_READBACK.json']
(O/'SHA256SUMS').write_text(''.join(sha(O/f)+'  '+f+'\n' for f in critical))
print(json.dumps({'status':report['status'],'input_SHA256':[x['SHA256'] for x in inputs],'protected_RGBA_diff':protected_diff,'support_RGBA_diff':support_diff,'context_RGBA_diff':contextdiff,'calls098':0,'calls102':0},indent=2))
