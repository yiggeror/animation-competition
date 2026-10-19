"""F018 SINGLE input gate. Generates material-reference BOARD only; zero imagegen/render calls."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,numpy as np
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2]
for p in ['inputs','prompts','requests','provenance','qa']:(O/p).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source012=S/'d02_F012_20261019/placket_tip_fix_20261019/candidate/F012.png';source000=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png';source018=S/'first_left_grasp_inputs_20261019/inputs/F018_CONSTRUCTION.png'
assert sha(source012)=='063bc020f65f3e9485a57984f20703f0fbc96667a2f5a046ad713ee51d1beb88'
assert sha(source000)=='95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793'
assert sha(source018)=='bcfaffbed6cca5012be23222cefa1035360cf7c8ede97648de82efc603449b8a'
shutil.copyfile(source012,O/'inputs/01_locked_F012.png');shutil.copyfile(source018,O/'inputs/03_F018_CONSTRUCTION_UNCHANGED.png')
source=Image.open(source000).convert('RGBA');rgb=source.convert('RGB');arr=np.array(source)
patches=[('HAIR strands / light',(602,370,642,410)),('HAIR strands / shade',(490,505,514,529)),('SKIN / light',(650,554,682,586)),('SKIN / shade',(568,496,592,520)),('BLUE / lit fabric',(476,770,508,802)),('BLUE / folded shade',(485,988,501,1004)),('FLOWER / light',(502,765,534,797)),('FLOWER / shadow fill',(502,1015,510,1023)),('TROUSERS / main',(414,1168,454,1208)),('TROUSERS / fold',(270,1240,310,1280)),('SHOE / black cloth',(128,1260,148,1280)),('JADE / green',(826,812,838,824))]
board=Image.new('RGB',(960,1000),(236,238,238));d=ImageDraw.Draw(board);font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((22,18),'LOCKED F000 | MATERIAL COLORS ONLY',font=font(29),fill=(27,43,55));d.text((22,59),'Local RGB patches only. NO POSE / NO SHAPE INSTRUCTION.',font=font(20),fill=(116,57,32))
rows=[]
for i,(label,box) in enumerate(patches):
 x0=20+(i%4)*235;y0=112+(i//4)*252;crop=rgb.crop(box);tile=crop.resize((180,180),Image.Resampling.NEAREST);board.paste(tile,(x0+18,y0));d.text((x0,y0+190),label,font=font(15),fill=(27,43,55));d.text((x0,y0+215),','.join(map(str,box)),font=font(13),fill=(80,91,99))
 a=arr[box[1]:box[3],box[0]:box[2]];assert a[:,:,3].min()>=240,label
 assert np.array_equal(np.array(board)[y0:y0+180,x0+18:x0+198],np.array(tile))
 rows.append({'material':label,'source_native_box_xyxy':box,'source_native_size':list(crop.size),'source_min_alpha':int(a[:,:,3].min()),'display_tile_box':[x0+18,y0,x0+198,y0+180],'source_RGB_mean':a[:,:,:3].mean((0,1)).tolist(),'pixel_rule':'Exact source unpremultiplied RGB, no matte blend/color filter; nearest-neighbor magnification only.'})
d.text((22,903),'Authority: locked F000 95f80f2d...1ed793',font=font(19),fill=(27,43,55));d.text((22,937),'Use material tone + light/shadow relation. Keep image1 F012 geometry.',font=font(18),fill=(27,43,55));d.text((22,970),'Reference board, never a frame or a character-pose image.',font=font(16),fill=(116,57,32))
board.save(O/'inputs/02_locked_F000_materials_ONLY.png')
(O/'provenance/material_board_sources.json').write_text(json.dumps({'source_full_native_path':str(source000.relative_to(R)),'source_full_native_SHA256':sha(source000),'board_path':'inputs/02_locked_F000_materials_ONLY.png','board_SHA256':sha(O/'inputs/02_locked_F000_materials_ONLY.png'),'board_size':[960,1000],'source_full_pose_is_not_a_tool_input':True,'old103_not_a_tool_input':True,'tiles':rows},ensure_ascii=False,indent=2)+'\n')
prompt='''S12 drawn animation, F018 only, held for F018-F021. Make ONE native transparent 1024x1536 RGBA grandmother image on the same canvas and registration. This is the second approach, BEFORE any hand touches a rod. No other frame is requested.

INPUT ROLES AND PRIORITY:
Image 1 is the NEWLY LOCKED F012 continuity mother, SHA256 063bc020f65f3e9485a57984f20703f0fbc96667a2f5a046ad713ee51d1beb88. Use this image for the complete grandmother identity, anatomy, head/gaze, body pose, garment design, finished placket-tip folds and shaded flower colors, empty near right hand, kneeling legs and both shoes. Continue directly from this locked F012; do not go back to an earlier F000 character pose or an older F012 version.
Image 2 is a MATERIAL-ONLY LOCAL RGB BOARD cropped from the LOCKED F000 (source SHA256 95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793). It is the fixed intrinsic material-color reference: silver hair, warm skin light/shadow, dusty blue cloth light/fold shade, light flowers and SHADOWED flower fill, dark trousers, black cloth shoe and jade. The board contains no whole character pose. Use only these material colors and light/shadow relationships. Do not copy crop shapes, chunky preview pixels, card layout, labels or text into the drawing.
Image 3 is the ORIGINAL APPROVED F018 full-arm VOLUME CONSTRUCTION guide, unchanged. Follow its colored FAR LEFT arm volumes and native coordinate placement for this single approach step. Blue/grey/gold diagram colors, bones, dots, letters, rods and ghost body are construction only. The faint older ghost pose in this guide is not a new identity or pose mother; image 1 controls all unchanged character geometry. The pale proximal shoulder volume is HIDDEN beneath the blouse, never an exposed shoulder ball on the chest.

F018 ACTION:
The FAR LEFT jade-bangle upper arm, elbow, forearm, wrist and complete relaxed open hand continue forward and down from locked F012 toward the upper neck3 rod. Move the entire arm as a continuous anatomical chain, including the sleeve; remove the previous far-arm silhouette cleanly. Do not translate a detached hand or stretch a forearm. The far elbow stays outside the torso silhouette. Keep the fixed upper-arm .86H and forearm .64H lengths, with projection foreshortening as needed; H is the same mother head unit. One jade bangle stays proximal to the FAR LEFT wrist, never on the near right arm. Fingers remain soft and naturally curved, with coherent palm volume, thumb base and knuckles; not spread stiffly and not clenched.

NO CONTACT YET:
In F018 both hands are EMPTY. Every far-left digit remains ABOVE and clearly separated from the upper rod; keep at least 3 scene pixels of air between finger skin and the actual 7px rod outline. Do not wrap any finger around either guide axis, do not place the thumb pad on the rod, and do not close a grasp. F022 is the later first thumb-touch event; do not anticipate it in F018. The near right open hand remains at its locked F012 lower-left resting position and clearly separate from both rods. The crane is still supported by the cloth; no rod endpoint, crane root, prop plane, box or cloth support moves in this approach.

FIXED SCENE REFERENCE, NOT PAINTED PROPS:
Registration remains scale .70 at scene (275,112), native1024x1536 onto scene1920x1080. Upper/neck3 rod is fixed from scene (934.3125,785.1297) to (1497.5315,714.6642), outer outline width7px. Lower/body rod is fixed from scene (951.2617,798.9063) to (1282.1987,773.9468), outer outline width7px. Do NOT paint any rod, crane, cloth, box, scenery, cast shadow, axis, letter or arrow into the native character. These are guide coordinates only.

Native construction anchors for F018 (estimates, not substitutes for actual image review):
{"S": [644.0, 684.0], "E": [773.753, 830.870], "W": [905.300, 911.900], "G_OPEN_HAND_REFERENCE": [962.742, 923.298], "B": [872.413, 891.643]}
The guide label G is the OPEN-HAND construction reference above the rod, not a contact point on the rod and not a final-grasp target. Preserve the guide's visible air gap. The hidden shoulder estimate has +/-10-20 native pixel uncertainty; connect it naturally under the blouse without dislocation.

UNCHANGED AREAS AND MATERIALS:
Keep image 1 head, fine silver hair, thin round glasses, facial gaze, neck/chest, pelvis, NEAR RIGHT arm and empty hand, trouser folds, kneeling support and both COMPLETE cloth shoes unchanged in placement and structure. Preserve the newly locked F012 static lower placket TIP, its fold direction, blue shadow plane and grey-blue shaded flower fill; do not brighten shaded petals back to white or repaint the entire front placket. Retain natural skin, dusty blue cloth and mother shading; do not bleach skin, saturate blue, brighten trousers or accumulate a warmer palette from frame to frame. Compare skin/hair/blue/trousers using same-material regions against the fixed material authority within +/-4 RGB channel means; keep ink, fold lines, white-pattern edges and the original form gradients. The color board is a palette reference, not a new illumination or drawing style.

Transparent background with clean antialiasing; preserve fine hair and glasses. Full head, both knees/shins/shoes, far fingers and all contours must fit the native canvas with right-edge breathing room. No body lift, turn, new facial expression, hand swap, extra bangle, extra arm/digit, prop grip, diagram text or cropped shoe. Deliver F018 only.
'''
(O/'prompts/F018_full.txt').write_text(prompt)
inputs=[O/'inputs/01_locked_F012.png',O/'inputs/02_locked_F000_materials_ONLY.png',O/'inputs/03_F018_CONSTRUCTION_UNCHANGED.png']
roles=['newly locked F012 continuity mother','locked F000 local material board ONLY; no full old pose','original approved F018 volume guide UNCHANGED']
args={'prompt':prompt,'referenced_image_paths':[str(x) for x in inputs],'transparent_background':True}
request={'status':'F018_SINGLE_INPUT_GATE_PREPARED_NOT_EXECUTED','execution_enabled':False,'tool':'image_gen.imagegen','frame':18,'hold':4,'end_inclusive':21,'tool_arguments':args,'prompt_path':'prompts/F018_full.txt','prompt_SHA256':sha(O/'prompts/F018_full.txt'),'actual_three_inputs':[{'order':i+1,'role':role,'path':str(x.relative_to(R)),'sha256':sha(x)} for i,(x,role) in enumerate(zip(inputs,roles))],'scope':'Review this ONE F018 request only. No generation is performed and F022/F026/F030 are not opened.'}
(O/'requests/F018_NOT_EXECUTED.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
plan=json.loads((S/'first_left_grasp_inputs_20261019/geometry/stages_PROPOSAL.json').read_text());row=next(x for x in plan['stages'] if x['frame']==18)
(O/'provenance/approved_F018_volume_coordinates.json').write_text(json.dumps({'source_geometry':str((S/'first_left_grasp_inputs_20261019/geometry/stages_PROPOSAL.json').relative_to(R)),'original_volume_image_SHA256':sha(source018),'same_original_F018_state':row,'first_touch_is_future_F022':True,'crane_cloth_support_unchanged':True},ensure_ascii=False,indent=2)+'\n')
ledger={'source_parent_commit':'0c31714179fc8bcc8914fa313b8d3935c7a53aa3','locked_F012_SHA256':sha(source012),'locked_F000_material_source_SHA256':sha(source000),'original_F018_volume_SHA256':sha(source018),'prepared_frames':[18],'imagegen_calls':0,'inflight_this_worker':0,'new_scene_renders':0,'new_art_outputs':0,'prior_cumulative_S12_native_calls':4,'other_new_frame_requests_created':[],'state':'ONE_INPUT_GATE_READY_FOR_ASTRA_REVIEW'}
(O/'provenance/preparation_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'prompt_SHA256':request['prompt_SHA256'],'three_inputs':request['actual_three_inputs'],'execution_enabled':False},ensure_ascii=False,indent=2))
