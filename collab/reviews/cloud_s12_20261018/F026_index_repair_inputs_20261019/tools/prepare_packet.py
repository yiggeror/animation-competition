from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_inputs_20261019')
R=Path('collab/reviews/cloud_s12_20261018/batch_F026_F030_from_locked022_20261019')
S=Path('collab/reviews/cloud_s12_20261018/F022_full_arm_repair_20261019/uniform_map_rejoin_20261019')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=R/'originals/F026_raw_call01.png'
assert sha(raw)=='cb9dfd6a60e6f33860e35432cf6f797abe61cd0749e00ac20629ab7dddd3a8d4'
assert sha(O/'reference/LOCKED_F022_STATIC_BASE.png')=='2c28bafe7ee05c5b234711fc551dd2a4d358143ea2615dc0a2282428aa744332'
shutil.copyfile(raw,O/'reference/F026_original_raw_call01_UNCHANGED.png')
# Complete proposed request: saved for review, never submitted.
prompt='''Create ONE newly drawn transparent local hand repair for scene S12, frame 026. This is a precise 1024×1024 local drawing plate, not a whole person. Draw an anatomically continuous entire index finger from the actual locked022 palm root through MCP, PIP and DIP to its rounded fleshy pad, with the index curling in front of the upper shaft then turning UNDER its lower edge, opposing the stationary actual thumb. This is the beginning of a real thumb/index grasp. The other three fingers stay loosely open, not a closed fist.

The three attached images have distinct roles.
1. INPUT 1 is the target CANDIDATE: actual locked022 far wrist, jade bracelet, palm and stationary thumb, with one whole projected index volume. It is a reference-only source-pixel construction, not finished art. Its target joint arrangement is the requested new pose; its pixel seams, stretched texture, compositing defects and angular transitions MUST NOT be copied. Redraw one organic continuous index with credible bone proportions, skin volume, knuckle flexion, rounded pad, ink and soft shading. There must be no disconnected distal tip, no long rubber finger, no capsule, no extra finger, and no old/new index ghost. The proposed MCP at native (960,923) is an estimate from the actual locked022 palm crease, not a measured hidden bone. PIP is approximately (985,938), DIP (984,957), pad centre (976.52,963.83). Keep the root attached to this real palm and solve the whole joint chain naturally rather than pulling only the tip to a coordinate. These are target approximations, not permission to distort anatomy.
2. INPUT 2 has EXACTLY THE SAME hand target over the frozen actual Canvas upper and lower shaft raster. These true shafts are 7 scene pixels wide, not idealized guides. Read their real thickness and depth. The palm and rear digits are behind the rods; the whole new curling index crosses the front face of the upper rod, with the pad below that upper rod and opposed to the unchanged thumb first touch. The lower rod must have visible air from the ENTIRE new index pad, including the outer ink and antialias fringe. Do not grasp or touch the lower rod. Do not move either rod to fit the hand. The background and rods are explanatory context only: DO NOT draw them in the output.
3. INPUT 3 contains local material, ink, thumb-pad and jade patches from the SAME actual locked022 hand. Use these colours, line quality and gentle volume shading. It contains no competing complete hand pose. Do not import the failed026 whole hand/body colour or its previous wrong endpoint. Do not copy any label or diagram line.

Output a real newly drawn far wrist/palm/index local transparent patch in this SAME plate registration. The only production-adoptable edit will be the entire newly drawn index plus the smallest necessary palm-root transition. The complete valid locked022 arm, jade bracelet, palm, actual thumb and its exact first-touch contact, and all other digits will be preserved from locked022 outside that edit domain. Draw enough true wrist/palm context to make the index attachment and shade intelligible, but do not reinterpret or move that context. This is not a request to regenerate the whole body or shift the whole hand. No arm/body/head, near-right hand, prop, crane, cloth, box, background, ground shadow, text, joints, dots, arrows, crop marks or guide labels may appear.

Plate geometry is fixed: native crop [816,816,1024,1024], uniformly enlarged 4× to 832×832, padded by 96 pixels on every side, producing 1024×1024. Forward mapping: plate=(native-(816,816))*4+(96,96); inverse native=plate/4+(792,792). Keep this scale, handedness, wrist entry and palm position. No recentering, zoom, arbitrary padding or whole-image shift. Return the hand on a genuinely transparent alpha background; no checkerboard, grey matte, white fringe or detached ink. Draw ONE pose and ONE hand only. No collage or multiple attempts. Maintain natural whole-index anatomy and round volume at its tip; the rod explanation must resolve as a real front-under wrap when composited later. The actual drawn source may later be separated into mutually exclusive rear palm/digit pixels behind the frozen rods and foreground index pixels above them; their union must reconstruct the actual source RGBA exactly. That separation is a compositing step after drawing, not a reason to draw an incomplete index.
'''
pp=O/'prompts/F026_whole_index_local_repair_prompt.txt';pp.write_text(prompt)
inputs=[O/'inputs/01_locked022_whole_index_TARGET_REFERENCE.png',O/'inputs/02_same_target_frozen_actual_rods.png',O/'inputs/03_locked022_local_material_patches.png']
request={'status':'PREPARED_ONLY_NOT_SUBMITTED','call_allowed':False,'required_next_gate':'Independent reviewer 01a15188-00cc-7705-b91f-7b18102ba0d0 must review this fixed commit and actual 3 images, then explicitly authorize the unique call. No duplicate main review requested.','tool':'image_gen.imagegen','args':{'prompt':prompt,'referenced_image_paths':[str(p.resolve()) for p in inputs],'transparent_background':True},'inputs':[{'path':p.relative_to(O).as_posix(),'SHA256':sha(p)} for p in inputs],'prompt_SHA256':sha(pp),'F030':'BLOCKED; no request binding, no call','new_calls_in_this_packet':0}
(O/'requests/F026_local_repair_PREPARED_NOT_SUBMITTED.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
# Actual-raster clearance of the reference construction only, not an accepted drawing or Canvas render.
index=Image.open(O/'geometry/reference_only_projected_index_native.png').convert('RGBA')
scene=index.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
pa=np.array(Image.open(S/'actual_scene/F022_code_props_actual_layer.png').convert('RGBA'))
sy,sx=np.mgrid[:1080,:1920];A=np.array([951.2616943917175,798.9063357461391]);B=np.array([1282.1986905564156,773.9467944476169]);V=B-A
u=np.clip(((sx-A[0])*V[0]+(sy-A[1])*V[1])/(V@V),0,1);dist=np.sqrt((sx-(A[0]+u*V[0]))**2+(sy-(A[1]+u*V[1]))**2)
lower=(dist<=6)&(pa[:,:,3]>0)&(sx>=947)&(sx<=1288)
dt=distance_transform_edt(~lower);ia=np.array(scene)[:,:,3];rows=[]
for threshold in [1,8,32,128]:
 m=(ia>=threshold)&(sy>=775)&(sx>=930)&(sx<=980);rows.append({'reference_alpha_threshold':threshold,'min_pixel_centre_air_to_actual_lower_rod':float(dt[m].min()),'reference_pixels':int(m.sum())})
(O/'geometry/reference_only_actual_raster_lower_air.json').write_text(json.dumps({'status':'REFERENCE_PROJECTION_MEASUREMENT_ONLY_NOT_PRODUCTION_PASS','actual_7px_prop_raster_SHA256':sha(S/'actual_scene/F022_code_props_actual_layer.png'),'lower_rod_actual_raster_restricted_by_known_line':True,'measurements':rows,'warning':'This only measures the displayed projection study. It cannot validate anatomy or a future drawn output. Full future drawn pad/ink/AA must be measured again.'},ensure_ascii=False,indent=2)+'\n')
# A proposed edit domain is an explicit candidate for review, not an approved production adoption mask.
old=np.array(Image.open(O/'geometry/old_index_trace_native.png'))>0;new=np.array(index)[:,:,3]>0
mask=(old|new)
th=np.array(Image.open(S/'masks/thumb_alpha_native.png').convert('RGBA'))[:,:,3]>0;mask[th]=False
Image.fromarray(np.uint8(mask)*255,'L').save(O/'geometry/proposed_whole_index_edit_domain_NOT_APPROVED.png')
# Preserve and describe all source data and the diagnostic nature of this packet.
prov={'parent_thread':'01a0fbb9-4718-7063-bf5b-9bf34d41700f','independent_reviewer_thread':'01a15188-00cc-7705-b91f-7b18102ba0d0','source_delivery_commit':'af2644bf032a9b3558d1d40ee437e68968081b3f','locked022_delivery_commit':'59497f0bcdd4c004dfacfce5bbe4f62bbaefe3c2','unique_static_production_base':{'file':'reference/LOCKED_F022_STATIC_BASE.png','SHA256':sha(O/'reference/LOCKED_F022_STATIC_BASE.png')},'unchanged_original026':{'file':'reference/F026_original_raw_call01_UNCHANGED.png','SHA256':sha(raw),'original_tool_path':'/workspace/generated_images/exec-24652d54-0293-4f80-a4b0-7abf3edd8ad9.png'},'sources':[{'path':str(p),'SHA256':sha(p)} for p in [S/'candidate/F022_far_arm_exclusive.png',S/'masks/thumb_alpha_native.png',S/'actual_scene/F022_code_props_actual_layer.png']],'new_imagegen_calls':0,'new_scene_Canvas_renders':0,'S12_historical_imagegen_calls':8,'F030_calls':0,'no_production_changes':True,'volume_study_limitation':'Only the isolated source026 index texture is used to visualize volume after an explicitly recorded articulated projection; the complete026 hand/body/colour/old endpoint is not a production mother. The actual output must be newly drawn; this construction is never accepted artwork. Independent reviewer must decide whether this target construction is adequate before any call.'}
(O/'provenance/source_manifest.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
geom=json.loads((O/'geometry/plate_and_anatomy.json').read_text());sd=np.array([984.,936.]);sp=np.array([981.,942.5]);td=np.array([984.,957.]);tp=np.array([976.52,963.83]);us=(sp-sd)/np.linalg.norm(sp-sd);ut=(tp-td)/np.linalg.norm(tp-td);vs=np.array([-us[1],us[0]]);vt=np.array([-ut[1],ut[0]]);cm=np.outer(ut,us)+np.outer(vt,vs)
geom.update({'distal_reference_volume_projection':{'source_DIP_direction_reference':sd.tolist(),'source_pad_centre':sp.tolist(),'target_DIP_direction_reference':td.tolist(),'target_pad_centre':tp.tolist(),'linear_matrix':cm.tolist(),'translation':(tp-cm@sp).tolist(),'source_transverse_scale':1.0,'projected_longitudinal_scale':1.0,'scope':'reference only; actual source round cap, not code-drawn capsule; never production adoption'},'MCP_PIP_DIP_PAD_plate':[[672,524],[772,584],[768,660],[738.08,687.32]]})
(O/'geometry/plate_and_anatomy.json').write_text(json.dumps(geom,ensure_ascii=False,indent=2)+'\n')
review={'status':'AUTHOR_VIEWED_INPUT_CANDIDATE_ONLY_INDEPENDENT_GATE_REQUIRED','actual_images_viewed':[p.relative_to(O).as_posix() for p in inputs]+['diagnostics/00_whole_registration_triptych.jpg','diagnostics/01_locked022_true_hand_trace_grid.png','diagnostics/02_whole026_down32_hand_trace_grid.png'],'findings':['Whole026 +32 only restores registration. It is not accepted, and is not the production static base.','Inputs1/2 show the same complete projected index over the actual locked022 wrist/palm/unchanged thumb, with the old index removed within the traced candidate domain. This is a reference construction, not an actual newly drawn finger.','The new index crosses in front of the true upper shaft and the rounded distal pad turns below it. The actual lower shaft raster remains visible with space.','MCP is estimated from the actual022 palm crease at (960,923); hidden bone lengths are not measured or certified by this 2D study.','Local texture projection leaves visible transition seams and should be read as a volume/pose candidate. It cannot satisfy a finished anatomical drawing gate. The independent reviewer must decide whether this construction sufficiently communicates the correct target; if not, do not call.','Input3 contains only locked022 local material/ink patches, no competing complete pose.'],'blocked':['Unique imagegen call has not been authorized against these new fixed inputs.','No future actual026 drawing exists for this local repair.','F030 remains blocked.'],'new_calls':0}
(O/'provenance/author_visual_gate.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
(O/'README.md').write_text('''# S12 F026 whole-index local input candidate — 0 calls

For the independent reviewer `01a15188-00cc-7705-b91f-7b18102ba0d0`, and Astra/root `01a0fbb9-4718-7063-bf5b-9bf34d41700f`. This packet is input preparation only. Do not submit the saved request until the independent reviewer explicitly authorizes the unique call. F030 stays blocked. No duplicate main-review request is made.

## Actual three inputs

1. `inputs/01_locked022_whole_index_TARGET_REFERENCE.png`: actual022 far wrist/palm/thumb plus one whole new index **projection study**, with MCP/PIP/DIP/pad annotations. Actual static palm is the locked022 base; the old index is removed in the candidate edit domain.
2. `inputs/02_same_target_frozen_actual_rods.png`: exactly the same target with the frozen actual7-scene-pixel upper/lower rod raster and the new index in front. Full pad, ink and lower-rod space can be inspected.
3. `inputs/03_locked022_local_material_patches.png`: only local material/ink patches from the same022 hand; no second complete pose.

The first two are source-pixel volume references, **not newly drawn production fingers**. A first022-texture mesh produced a thin strip/root gap; it was rejected and is retained under `diagnostics/FAILED_v2_thin_index_root_gap.png`. The current candidate uses only the isolated actual026 index volume, articulated onto the actual022 palm, with a real rounded source distal pad. It does not use the026 complete hand/body or old endpoint as a target. It contains visible construction seams; these cannot count as finished anatomy. Independent review must decide whether the candidate communicates a credible target before authorizing any image call. If this isolated volume use is outside the reviewer’s intended scope, reject the input candidate; it is not a production substitution.

## Frozen production base and mapping

Unique production static base remains `2c28bafe7ee05c5b234711fc551dd2a4d358143ea2615dc0a2282428aa744332` (`reference/LOCKED_F022_STATIC_BASE.png`). Preserve its complete valid arm/jade/palm and actual thumb first touch. The later actual drawing may contribute only the whole index and the needed root transition. All protected pixels, including invisible-alpha RGB, must remain exact022 RGBA. The proposed mask in `geometry/` is not an approved adoption mask.

Native crop `[816,816,1024,1024]` →4×→832 square, pad96 on each side→1024square. Forward `plate=4*native-3168`, inverse `native=.25*plate+792`. Only the far hand is shown; near hand is excluded. MCP estimate `(960,923)` comes from the actual palm crease, not the old mechanically reused point. PIP `(985,938)`, DIP `(984,957)`, pad `(976.52,963.83)` are approximate target anatomy. Projected segment lengths are proposals, not measured hidden bones. Explicit meshes and distal matrix are recorded in `geometry/plate_and_anatomy.json` and reproducible source in `tools/build_inputs.py`.

## Diagnostic and saved request

Original026 raw is copied unchanged with SHA `cb9dfd6a60e6f33860e35432cf6f797abe61cd0749e00ac20629ab7dddd3a8d4`. Exact fullnative `(x,y)→(x,y+32)` is retained only as a diagnostic: it restores registration but does not make026 accepted or become the static mother. No further whole-image downward shift is proposed.

Complete prompt: `prompts/F026_whole_index_local_repair_prompt.txt`. Complete bound request and the three input hashes: `requests/F026_local_repair_PREPARED_NOT_SUBMITTED.json`. The request has `call_allowed:false` and has never been submitted. No imagegen calls, no new Canvas rendering, no030 request, no production/ready/EDL/audio/shared document changes.

The author opened all three actual inputs. This is a candidate handoff with a remaining **target construction/anatomy approval gate**, not a claimed approved reference or completed drawing. `provenance/author_visual_gate.json` records the limits explicitly; actual-raster lower-rod measurements are reference-only and must be repeated on any future actual drawn pad/ink/AA.
''')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':manifest.append(sha(p)+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS').write_text('\n'.join(manifest)+'\n')
print(json.dumps({'files':len(manifest),'prompt_SHA256':sha(pp),'request_SHA256':sha(O/'requests/F026_local_repair_PREPARED_NOT_SUBMITTED.json'),'calls':0,'reference_lower_air':rows},ensure_ascii=False))
