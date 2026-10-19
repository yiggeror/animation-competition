from pathlib import Path
import json,hashlib,shutil,subprocess
from PIL import Image,ImageDraw
import numpy as np

R=Path(__file__).resolve().parent
P=R.parent/'REGISTER_REAL_PROPS_zero_call_v1_20261019'
(R/'inputs').mkdir(exist_ok=True)
sources=[(P/'layers/REGISTERED_COMPLETE_MOTHER_ORIGINAL_PROPS.png','00_LOCKED_MOTHER_REAL_PUPPETS.png'),
         (P/'scene/S29_F000_FORMAL_CAMERA_REAL_ORIGINAL_PROPS.png','01_LOCKED_CAMERA_LIGHT_ONLY.png')]
for src,name in sources:shutil.copyfile(src,R/'inputs'/name)
data=json.loads((R/'geometry/THREE_ACTUAL_TARGETS.json').read_text())
common='''Create exactly ONE complete new native 2D animation drawing for S29 of the film 来电, at the one state specified below. This is one coherent full seated grandmother, not a pasted arm, an alternate-pose sheet, a timeline, or a finished-scene background.

Input roles:
1. The LOCKED complete mother with the REAL original crane, turtle and four rods: authoritative identity, proportion, colors, shy closed-mouth downward gaze, near anatomical RIGHT bare wrist and neck3 support, both thighs/stool/feet, and fixed prop registration.
2. The complete NEW VOLUME TARGET is a labeled TECHNICAL real-pixel contact probe. Orange joints, annotations, temporary articulated arm pieces, sleeve/shoulder cut seams, wrist/elbow splice lines, tiled cloth shading and sampled texture are only planning aids. Draw a NEW coherent complete anatomical far arm and soft cloth volume. Never copy the guide's rectangular shoulder patch, cut edges, pasted elbow or technical lines as artwork. The target is not an accepted native drawing.
3. The actual target contact crops show the COMPLETE far shoulder/sleeve/elbow/wrist/pinch and the fixed near-palm/real-neck3 contact. Follow real contact and depth, not a numerical label alone.
4. The locked current camera frame is only framing, room light direction and orientation reference. Do not draw its background, inherit the old closed bundle, old procedural cloth warp, child-held puppet, AB turn timing, or later phone action.

Keep the same complete head/skull/bun/glasses, elderly face, neck/chest, quiet downward eyes and restrained smile as the locked mother. Preserve near-black ink, silver hair with red-bead pin, LIGHT BLUE short-sleeved white-flower blouse and dark INDIGO opaque cotton with small white resist-print motifs. Match the mother material colors on every state, not a preceding result. Correct any temporary target splice into natural anatomy without changing the accepted identity or proportions. Keep the full source head, both feet, stool and whole arms within one portrait canvas, preferably the same 1024x1536 layout and neutral material lighting.

The near anatomical RIGHT bare hand, its complete upper arm/forearm/wrist, and the original crane neck3 support remain steady at the locked mother contact. Do not release, slide, swap, mirror, add a bracelet or let new cloth pass through that supporting palm. Real neck3 passes under the curved fingers/inside the palm as in the locked original-prop layer. Do not move the crane to chase a different hand.

Redraw the ENTIRE anatomical LEFT far shoulder-to-sleeve-to-elbow-to-forearm-to-wrist-to-hand chain in the new target pose. One jade bangle belongs to this same wrist and travels with the hand; it is never a separately pasted ornament. The same thumb and opposing curved finger pads retain the SAME MATERIAL POINT on the cotton edge; no regrip or release occurs. Wrist follows the hand, elbow bends continuously, far chain remains behind the near support chain. Approximate joint coordinates are soft projected targets, not measured 3D bones or permission to squash limb widths.

Cotton is one FULL CONTINUOUS OPAQUE sheet supported on both thighs. Its held edge has actual thickness between the thumb and opposing pads, and joins a complete soft folded surface back to the lap. The lifting face is behind the resting puppets/rods; the turning leading lip comes in front only as specified for this state. These are two faces of ONE folded sheet, never separate fabric pieces. Draw soft curves, drape, local compression/folds and a broad cotton face. Do not make a ribbon, bag handle, cutout hole, transparent cotton, rigid tray, pointed triangle, inflated pillow, sealed parcel or new knot. The contact must be visible in actual drawn fingers/cloth, not a circle or an annotation. No new cloth crosses the fixed near support palm.

Both thin flat ORIGINAL leather puppets and all four straight rods remain with grandmother, resting on the same lap. Their shape, pose, scale, neck chain, true body/neck3 and shell/head rod entries and registration remain unchanged from input1. Cotton may occlude only the actual part beneath its drawn fold; never delete a full rod, detach a joint, bend a shaft, invent a decorative head, move a puppet to fit the cloth, or transfer anything to the girl. Generated prop context will still require independent registration against the real originals after the raw return; do not treat a redrawn puppet as adopted production geometry.

Story limits: S29 remains12 seconds/288 frames at24fps. Mother000 is held through023; cloth action begins024=1.0s. Phone sound remains5.5s; girl/phone look and later poses have independent inputs and are outside this drawing. There is no S28/S29 handover. Later cloth crossing the support hand requires releasing that hand first, which has NOT happened in this group.

Output ONE new full native figure on transparent background. Only grandmother, stool, continuous cotton and fixed puppet/rod context. No room, girl, phone, captions, guide lines, numbers, comparison layout, extra hands or partial character. Do not animate or warp the technical probe as a substitute for this drawing.
'''
actions={
24:'F024 / 1.000s: LEFT EDGE STARTS LIFTING. Retain the same cotton pinch and gently lift it from the locked mother [845,744] toward soft target A=[827,700]. Full far hand/bangle turns about −8 degrees from the mother and the whole elbow/shoulder chain follows naturally. The opaque cotton face rises behind the fixed feather/rod group; the turning front lip does NOT newly cover the original outer tail feathers yet. No packed parcel.',
30:'F030 / 1.250s: SAME PINCH CARRIES COTTON INWARD. Carry A to approximately [785,688], toward the puppet body, with full hand/bangle about −16 degrees from the mother. Elbow and wrist follow continuously, no sliding fingertips. The complete folded cotton face is visible and connected back to the lap, still behind the tail feathers. Do not prematurely cover the outer feathers or turn the cloth into a hollow arc/ribbon.',
36:'F036 / 1.500s: FIRST SMALL NEW COVER OF TAIL. Same pinch lowers/inward to A≈[742,718], full hand/bangle about −4 degrees from the mother. Show the first small turning lip of the continuous cotton actually settling IN FRONT of a little outer feather area; most contents remain visible. Do not make a sealed or fully wrapped bundle, move the original tail, or let the fold cross the steady right support palm. The exact guide pixel count is not a physical-contact certificate; draw a believable cotton-on-thin-leather overlap.'}
plans=[]
for frame in [24,30,36]:
    prompt=common+'\nTHIS SINGLE STATE:\n'+actions[frame]+'\n'
    (R/f'prompts/F{frame:03d}_FULL_PROMPT_PLANNED_NOT_EXECUTED.txt').write_text(prompt)
    refs=[R/'inputs/00_LOCKED_MOTHER_REAL_PUPPETS.png',R/f'targets/F{frame:03d}_COMPLETE_NEW_VOLUME_TARGET_TECHNICAL.png',R/f'contacts/F{frame:03d}_COMPLETE_ARM_AND_TWO_CONTACTS_TARGET.png',R/'inputs/01_LOCKED_CAMERA_LIGHT_ONLY.png']
    args={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':True}
    (R/f'prompts/F{frame:03d}_ARGUMENTS_PLANNED_NOT_EXECUTED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
    plans.append({'frame':frame,'status':'PLANNED_ONLY_WAITING_ASTRA_TARGET_GATE','request_count':0,'input_sha256':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in refs]})
(R/'prompts/THREE_PLANNED_INPUT_SETS_SHA256.json').write_text(json.dumps(plans,indent=2)+'\n')
(R/'CALL_STATE_ZERO.json').write_text(json.dumps({'actual_new_imagegen_requests':0,'new_raw_outputs':0,'status':'THREE_TARGETS_READY_FOR_ASTRA_DESIGN_GATE_ONLY','planned_after_gate_frames':[24,30,36],'new_calls_authorized_now':False,'no_auto_retry':True},indent=2)+'\n')

original=np.array(Image.open(P/'layers/REGISTERED_COMPLETE_MOTHER_ORIGINAL_PROPS.png').convert('RGBA'))
checks=[]
for state in data['targets']:
    f=state['frame'];probe=np.array(Image.open(R/f'native_probes/F{f:03d}_WHOLE_TARGET_REAL_PIXEL_PROBE_NOT_NEW_DRAWING.png').convert('RGBA'))
    item={'frame':f,'head_RGBA_exact':bool(np.array_equal(probe[:400],original[:400])),
          'lower_legs_stool_shoes_RGBA_exact':bool(np.array_equal(probe[1070:],original[1070:])),
          'near_palm_RGBA_exact':state['near_palm_exact_RGBA_from_locked_mother'],
          'front_cotton_over_near_palm':state['moving_cloth_over_near_palm_pixels'],
          'cloth_at_pinch_A':state['actual_cloth_mask_at_pinch'],
          'complete_opaque_rear_cloth_connected':state['full_opaque_cloth_rear_face_connected_to_A_and_lap'],
          'tail_core_covered_front':state['actual_original_black_tail_core_pixels_covered']}
    assert all(item[k] for k in ['head_RGBA_exact','lower_legs_stool_shoes_RGBA_exact','near_palm_RGBA_exact','cloth_at_pinch_A','complete_opaque_rear_cloth_connected'])
    assert item['front_cotton_over_near_palm']==0
    for name in ['upper','forearm','hand_and_bangle_together']:
        m=np.array(state['human_matrices_reference_only'][name])[:,:2]
        assert np.allclose(m.T@m,np.eye(2),atol=1e-6) and np.isclose(np.linalg.det(m),1,atol=1e-6)
    checks.append(item)
assert [v['tail_core_covered_front'] for v in checks][:2]==[0,0] and 0<checks[-1]['tail_core_covered_front']<838
(R/'qa/ACTUAL_TARGET_CHECKS.json').write_text(json.dumps({'checks':checks,'original_props_rods_same_input_SHA':hashlib.sha256((P/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png').read_bytes()).hexdigest(),'scope':'technical target preparation only; no 3D bone or continuous sweep proof'},indent=2)+'\n')

out=Image.new('RGB',(1440,500),'#edf0f2');d=ImageDraw.Draw(out)
for i,f in enumerate([24,30,36]):
    im=Image.open(R/f'native_probes/F{f:03d}_WHOLE_TARGET_REAL_PIXEL_PROBE_NOT_NEW_DRAWING.png').convert('RGBA');bg=Image.new('RGBA',im.size,'#edf0f2');bg.alpha_composite(im)
    out.paste(bg.crop((780,730,900,835)).resize((480,420)).convert('RGB'),(480*i,50));d.text((480*i+10,10),f'F{f:03d} actual target / fixed original tail',fill='#263f55')
out.save(R/'contacts/ACTUAL_TAIL_COVER_024_030_036.png')
(R/'AUTHORITY_FIRST3_Chinese.txt').write_text('''Astra已主审锁545341ea首母，不重复生成。S29保12秒/288f、5.5s手机声与两偶归奶奶；000保持到023，现配声包布从1.0s开始。024远左夹布沿起提，030同夹点带布向偶身内折，036布沿初盖尾羽；近右裸腕仍稳扶原neck3，双膝/坐凳/原四杆不跳，布必须实际连到被夹边、不能穿稳扶掌。先三图/接触小门，过后连续3次，无需整36态长报告。后续过掌须先放扶掌再盖，不猜交签；孩子手机回看后段待独立输入。当前0新调用。''',encoding='utf-8')
(R/'README.md').write_text('''# S29 首组三态完整目标 · 0新调用 · 待Astra设计门

先看 `targets/F024_COMPLETE_NEW_VOLUME_TARGET_TECHNICAL.png`、`F030_…png`、`F036_…png`，再看对应 `contacts/F024_COMPLETE_ARM_AND_TWO_CONTACTS_TARGET.png` 等三张。真实锁母整身、原两偶/四杆、全远臂与软布两面都在同一目标图内。**这是实际锁母像素临时构成的完整体量/接触probe，非三张新画稿；肩袖/肘腕拼缝明确要在原生绘制中整体重画，不得当代码人物成稿采用。**

同一夹布材料点A：000 `[845,744]` → 024 `[827,700]` 起提 → 030 `[785,688]` 内折 → 036 `[742,718]` 初落盖。玉镯随整手，腕由整手导出，完整远臂同支肘链接回本侧肩。源肩/肘/腕 `[525,465]/[641,632]/[778,680]` 为±25px隐藏肩软代理；203.3/145.2px为投影参考，不是3D实测骨长。

整块不透明后褶面自A/B夹沿连续回膝上柔褶区域，真实偶/杆在后褶面前；转下来的前折沿在偶/杆前。**两面属于同一棉布，不是两块布、细带或布洞。** 当前前折沿盖住真实黑尾羽保守core的像素为024/030=0，036仅36/838；这只是实像素遮挡小门，不能代替实际薄皮/棉布接触观感。近掌C1 `[536,750]` RGBA逐像素保持，移动前折布对近掌重叠0；双偶四杆来源/位置同首母，不移偶迎合布面。

000–023保持首母，024=1.0s承包布声；024–029、030–035仅为这一小段边界，036的终止帧不猜。整镜仍12秒/288f，5.5s手机声不动；后续过掌先放掌，手机回看后段另立输入。本包不补整36态长表。

完整逐张prompt、四实际准备输入SHA及可提交参数见 `prompts/`，均标PLANNED_NOT_EXECUTED；`CALL_STATE_ZERO.json`记录0请求/0新原件。只有Astra三态设计/接触门通过后才执行这三次，不提前开图。

`geometry/THREE_ACTUAL_TARGETS.json`、`qa/ACTUAL_TARGET_CHECKS.json`保留完整链、夹沿A/B、布面mask、原偶恒定和局限。全部目标已实际打开；实看记录另附。参考工具代码只准备目标，不提供成片动作或新绘图来源。只写独占目录，首母包、生产代码、共享文档和Opus留言均不改。
''',encoding='utf-8')
print(json.dumps({'prepared_frames':[24,30,36],'new_requests':0,'checks':checks},indent=2))
