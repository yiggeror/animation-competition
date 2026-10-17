from pathlib import Path
import json, hashlib
B=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
c04=B/'originals/g01_s01_c04.png'
c04b=B/'originals/g01_s01_c04b.png'
empty=D/'c06b_empty_two_well_reference_native.png'
locator=B/'evidence/s01_c04b_pod_crop_native.png'
common='Keep the complete transparent frame and her identity: round glasses, grey bun, three red hairpin beads. Preserve both hands, fingers, the pod with exactly TWO seated beans, blouse, shoulders, bangle, basin, legs, shoes and every stool corner/foot exactly as image 1. No loose pea, extra object or text.'
items=[
('c05c_last_bean', '末豆推出（待审）', [c04b,empty,locator],
 'Precise local edit. Image 1 is the only full-frame edit target. Image 2 is ONLY an empty-shell surface/shape reference; image 3 locates the raised left bean in image 1. In image 1 replace the rounded green body around (281,660), within [264,644,299,677), with a pale EMPTY concave well like image 2. Keep the original short pod silhouette and two-well layout; both wells must now be empty, with no green sphere or raised seed inside. The earlier airborne pea has landed. Show only the LAST pea falling below the hands, lower than the former pea. Keep all fingers, pose, face, basin, shoes, stool and framing as image 1. Final count: zero in pod, zero held, one in air, exactly two empty wells. Transparent background; no annotations.',
 ['左腔定位框内确实消失凸豆；两穴都有可读的空腔表面，不能仅把豆染浅或加阴影。','手内0豆、荚内0豆、空中恰1末豆；前一颗不再保持原空中位置或变成第二颗。','外壳仍是 c04b 同一短两穴荚，角度/长度/尖端和手接触连续；c06b 仅提供空壳表面，身体不得迁入。']),
('f01_half_blink','半闭眼（c04 持稳）',[c04],
 'Edit only the eyelids of image 1 for the halfway closing phase of a natural blink. Both upper lids cover about half the visible irises; both eyes remain visibly partly open, still directed down at the pod. Keep the exact head angle, pupils, eyebrows, smile and glasses position. '+common,
 ['两眼各约半开，仍能看到瞳/虹膜；不是全闭、不是只变视线。','脸角、嘴形、眉形不额外变化；眼镜不得盖住错误眼睛。','与 c04 全开、f02 全闭可组成可见开合阶梯。']),
('f02_full_blink','全闭眼（c04 持稳）',[c04],
 'Edit only the eyelids of image 1 for the fully closed phase of a relaxed natural blink. Both eyes are completely shut with simple gently downward-curving eyelid lines; no iris, pupil or white remains visible. Keep the exact head angle, eyebrows, slight open smile and glasses position. '+common,
 ['两眼真正全闭，不能残留眼白/黑瞳。','眼睑是自然闭合线，不画成抬颊大笑眯眼。','头、口、手荚与 c04/f01 相容；f01 未通过不能用别态冒充。']),
('f03_half_turn','半抬／半转向小满',[c04],
 'Edit only her head, neck and eye direction in image 1. Make a small halfway movement from the current downward working pose toward a child off-screen to her LEFT and SLIGHTLY BELOW her eyes: slightly reduce the downward head pitch and turn a little farther left. Eyes lead left-and-down, never upward. Keep the same gentle slight-open smile. This is an intermediate, not a completed head turn. '+common,
 ['确有小幅头颈姿态变化，不仅挪瞳孔；幅度应介于 c04 与 f04。','视线朝画面左方略下，不能仰视左上灯位。','肩、手和两豆持稳；眼镜鼻梁结合正常，三红珠/发髻身份保留。']),
('f04_child_smile','看小满微笑',[c04],
 'Edit only her head, neck, gaze and mouth in image 1. She pauses with the pod held still and turns toward the child off-screen to her LEFT and SLIGHTLY BELOW eye level. Keep a modest three-quarter-left view and a neutral-to-slightly-down chin; both eyes clearly look left and a little downward. Give a small warm closed-mouth smile. The turn is a little farther than the intermediate, not a profile or upward lamp gaze. '+common,
 ['完整注意力到左方略下小满位置，双眼方向一致；具体实景视线仍待 Opus 确认。','与 c04/f03 有可读区别，温和闭口微笑，不变惊讶／大笑。','荚内两豆及两手位置不变；返回可复用 f03 后回 c04，是否自然须接景实看。'])]
manifest={'status':'DRAFT ONLY; waiting for parent to relay Opus feedback; no image_gen calls authorized or executed by this preparation.',
 'max_future_calls':5,'transparent_background':True,
 'target_master':{'width':779,'height':1355,'anchors':[[538,1274],[745,1215]],'third_point':[759,884],'third_point_max_residual_px':3},
 'gaze_assumption':'Child is to grandma screen-left and slightly below eye level; parent inference, not yet verified in actual S01 shot by Opus.',
 'c06b_shape_reference':{'source':str(B/'originals/g01_s01_c06b.png'),'source_sha256':hashlib.sha256((B/'originals/g01_s01_c06b.png').read_bytes()).hexdigest(),'native_crop_box':[315,815,440,890],'native_crop_size':[125,75]},
 'items':[]}
for id,title,refs,prompt,checks in items:
 item={'status':'draft_not_executed','id':id,'title':title,'references':[{'index':i+1,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(refs)],'image_gen_arguments':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':True},'semantic_acceptance':checks}
 file=D/(id+'.json');file.write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
 manifest['items'].append({'id':id,'draft_file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(D/'DRAFT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Prepared exactly five draft requests; image_gen was not called.')
