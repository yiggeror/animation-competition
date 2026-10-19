from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation
import numpy as np, math, json, hashlib, shutil

R = Path(__file__).resolve().parent
B = R.parent
for d in ['sources','layers','masks','reference_native','inputs_1024x1536','geometry','requests','qa']:
    (R/d).mkdir(exist_ok=True)
paths = {
 'F100_LOCKED_7dc803e9.png': B/'F100_WHOLE_RAW_BLOUSE_FINAL_20261019/candidate/F100_WHOLE_RAW_BLOUSE_final_RGBA_PENDING_ASTRA.png',
 'F100_whole_actual_raw_blouse.png': B/'F100_WHOLE_RAW_BLOUSE_FINAL_20261019/layers/WHOLE_actual_call02_blouse_from_neck_to_full_hem.png',
 'F100_original_head_neck.png': B/'F100_WHOLE_RAW_BLOUSE_FINAL_20261019/layers/ORIGINAL16_head_hair_face_glasses_neck_NO_old_chest.png',
 'F100_near_complete_old_open_sleeve_arm_hand.png': B/'F100_zero_call_semantic_trial_20261019/layers/RAW_complete_new_near_sleeve_arm_hand.png',
 'F100_far_complete_arm_hand_jade.png': B/'F100_zero_call_semantic_trial_20261019/layers/SOURCE_complete_far_arm_hand_jade.png',
 'F100_passed_whole_pants.png': B/'F100_zero_call_semantic_trial_20261019/layers/BLEND_pants_wide_slanted_same_plane_overlap.png',
 'F100_far_whole_shoe_FIXED.png': B/'F100_local_arm_call02_input_GATE_20261019/sources/F100_far_whole_shoe_FIXED.png',
 'F100_near_whole_shoe_FIXED.png': B/'F100_local_arm_call02_input_GATE_20261019/sources/F100_near_whole_shoe_FIXED.png',
 'ORIGINAL_whole_lamp_and_shadow_FIXED.png': B/'F100_local_arm_call02_input_GATE_20261019/sources/ORIGINAL_fixed_lamp_same_native_registration.png',
 'FROZEN24_and106_geometry.json': B/'F100_103_106_closing_batch_20261019/next_states_61sol/geometry/batch_contact_and_proxy_checks.json',
}
for n,p in paths.items():
    if not (R/'sources'/n).exists(): shutil.copyfile(p,R/'sources'/n)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(R/'sources/F100_LOCKED_7dc803e9.png') == '7dc803e92e69cb90a84465f4b25e64f5ba9ea62b6b3853bd9a66b658f9951b2b'
size=(1960,1080)
def load(n):
    z=Image.open(R/'sources'/n).convert('RGBA');o=Image.new('RGBA',size);o.alpha_composite(z);return o
shirt=load('F100_whole_actual_raw_blouse.png');head=load('F100_original_head_neck.png')
oldnear=load('F100_near_complete_old_open_sleeve_arm_hand.png');far=load('F100_far_complete_arm_hand_jade.png')
pants=load('F100_passed_whole_pants.png');ff=load('F100_far_whole_shoe_FIXED.png');nf=load('F100_near_whole_shoe_FIXED.png')
lamp=load('ORIGINAL_whole_lamp_and_shadow_FIXED.png');mother=load('F100_LOCKED_7dc803e9.png')
replay=Image.new('RGBA',size)
for im in [ff,pants,far,head,shirt,oldnear,nf,lamp]: replay.alpha_composite(im)
assert np.array_equal(np.array(replay),np.array(mother)), 'locked100 component replay differs'

frozen=json.loads((R/'sources/FROZEN24_and106_geometry.json').read_text())
fixed=frozen['records'][1];H=np.array(fixed['shared_hidden_pivot_NOT_ANATOMY'])
angle=math.radians(8);M=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
t=H-M@H
def rigid(im):
    iv=M.T;it=-iv@t
    return im.transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
def point(p):return M@np.array(p)+t
oldmask=np.array(oldnear)[:,:,3]>0
clean=np.array(shirt);clean[binary_dilation(oldmask,iterations=2)]=0
upper=Image.new('RGBA',size)
for im in [far,head,shirt]:upper.alpha_composite(im)
upper24=rigid(upper);head24=rigid(head);far24=rigid(far);shirt24=rigid(shirt);oldnear24=rigid(oldnear)
upper24.save(R/'layers/F103_locked100_head_whole_cloth_fararm_COMMON_delta8_to24.png')
oldnear24.save(R/'layers/REMOVED_old100_open_sleeve_arm_hand_after_COMMON_delta8.png')

def poly(ps):
    im=Image.new('L',size);ImageDraw.Draw(im).polygon([tuple(p) for p in ps],fill=255);return np.array(im)>0
def capsule(d,p,q,r1,r2,col,outline='#385e77'):
    p=np.array(p);q=np.array(q);v=q-p;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
    d.polygon([tuple(p+n*r1),tuple(q+n*r2),tuple(q-n*r2),tuple(p-n*r1)],fill=col,outline=outline,width=2)
    for a,r in [(p,r1),(q,r2)]:d.ellipse((a[0]-r,a[1]-r,a[0]+r,a[1]+r),fill=col,outline=outline,width=2)

# Visible actual100 sleeve/skin indices, not old code bones. All are soft pose
# proxies. The ONLY fixed body fact is the already selected total24degree group.
shoulder=point([1530.,237.]);cuff=point([1552.,363.])
G=np.array(fixed['bail_top_material_reference']);W=G+[-48.,8.]
U,V=60.,140.;v=W-cuff;dist=np.linalg.norm(v);u=v/dist
along=(U*U-V*V+dist*dist)/(2*dist)
E=cuff+along*u+math.sqrt(U*U-along*along)*np.array([-u[1],u[0]])

waistps=[(1405,485),(1595,535),(1580,625),(1532,685),(1480,720),(1368,688),(1372,610),(1380,540)]
waistmask=poly(waistps);waist=Image.new('RGBA',size);wd=ImageDraw.Draw(waist)
wd.polygon(waistps,fill='#9baac4',outline='#5f7695',width=2)
# No technical waist-panel image is placed or saved in this repair draft.

near=Image.new('RGBA',size);nd=ImageDraw.Draw(near)
# A removed old sleeve/chest intersection is UNKNOWN cloth to redraw, never an
# old open arm left in A. This opaque fill prevents a competing transparent hole.
missing=np.zeros((1080,1960),dtype=bool)
z=np.array(near);z[missing]=[139,184,213,255];near=Image.fromarray(z);nd=ImageDraw.Draw(near)
# Preserve the ACTUAL short sleeve, not a sleeve-shaped code volume.
capsule(nd,cuff,E,25,19,'#efbf9f',outline='#956d54');capsule(nd,E,W,19,14,'#efbf9f',outline='#956d54')
gx,gy=G;wx,wy=W
nd.polygon([(wx-10,wy-12),(gx-27,gy-20),(gx+6,gy-16),(gx+17,gy+6),(gx+4,gy+25),(gx-28,gy+22),(wx-11,wy+13)],fill='#bba5d7',outline='#69507f',width=2)
rear=near.copy()
fingers=Image.new('RGBA',size);fd=ImageDraw.Draw(fingers)
for k in range(4):
    px=gx-13+10*k;py=gy-6+1.3*k
    fd.rounded_rectangle((px-6,py-15,px+6,py+13),radius=6,fill='#c7b0df',outline='#69507f',width=2)
fd.rounded_rectangle((gx-32,gy+6,gx+5,gy+19),radius=7,fill='#d7bee9',outline='#69507f',width=2)
# One coherent full hand, with source wire between rear palm and front fingers.
near.alpha_composite(fingers)
nearmask=np.array(near)[:,:,3]>0
rear.save(R/'layers/F103_ONE_NEW_BARE_arm_wrist_rear_palm_NOT_ART.png')
fingers.save(R/'layers/F103_front_curled_fingers_opposing_thumb_SAME_HAND_NOT_ART.png')

A=Image.new('RGBA',size)
for im in [ff,pants,upper24,nf,lamp,rear]:A.alpha_composite(im)
# Actual short-sleeve material owns the cuff boundary over the new bare upper arm.
sleeve100=poly([(1440,225),(1568,225),(1600,310),(1588,365),(1542,402),(1470,402),(1435,355)])
sleeve=np.zeros_like(np.array(shirt));sleeve[sleeve100]=np.array(shirt)[sleeve100]
A.alpha_composite(rigid(Image.fromarray(sleeve)))
wire_area=poly([(gx-30,gy-9),(gx+26,gy-9),(gx+26,gy+10),(gx-30,gy+10)])
la=np.array(lamp);wire=np.zeros_like(la);wire[wire_area]=la[wire_area]
A.alpha_composite(Image.fromarray(wire));A.alpha_composite(fingers)

actionfront=poly([(1470,210),(1650,250),(1675,455),(1630,590),(1560,725),(1350,725),(1350,530),(1410,355)])
white=binary_dilation(oldmask|(np.array(oldnear24)[:,:,3]>0)|nearmask|waistmask|actionfront,iterations=8)
operation=poly([(1640,302),(1795,302),(1795,390),(1655,415)])
lampguard=(la[:,:,3]>0)&~binary_dilation(nearmask|operation,iterations=7)
headguard=np.array(head24)[:,:,3]>0
feetguard=(np.array(ff)[:,:,3]>0)|(np.array(nf)[:,:,3]>0)
visiblefar=(np.array(far24)[:,:,3]>0)&~(np.array(shirt24)[:,:,3]>0)&~nearmask
white&=~(lampguard|headguard|feetguard|visiblefar)
for name,m in [('WHITE_whole_sleeve_arm_full_hand_and_continuous_waist.png',white),('HARD_fixed_lamp_EXCEPT_true_grip_occlusion.png',lampguard),('HARD_common24_actual_head_neck.png',headguard),('HARD_original_whole_shoes.png',feetguard),('HARD_common24_VISIBLE_far_arm_hand_jade.png',visiblefar)]:
    Image.fromarray(m.astype('uint8')*255).save(R/'masks'/name)
Bim=Image.fromarray(white.astype('uint8')*255).convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
ad=ImageDraw.Draw(A);ad.text((1246,10),'F103 ONE new whole-grip target / NOT ART / LAMP TABLE-SUPPORTED',font=small,fill='#3f7495')
C=A.copy();cd=ImageDraw.Draw(C)
chain=[shoulder,cuff,E,W,G];cd.line([tuple(p) for p in chain],fill='#8b388f',width=3)
for p in chain:cd.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill='#8b388f')
cd.text((1450,750),'Complete chain + full waist; actual anatomy must be drawn.',font=small,fill='#6485a5')
cd.text((1620,275),'front fingers / true wire / rear palm',font=small,fill='#914a85')
D=Image.new('RGBA',size,(233,238,243,255));dd=ImageDraw.Draw(D)
dd.text((1248,15),'D: LOCKED100 IDENTITY + INTERNAL CLOTH ONLY',font=font,fill='#36546e')
for box,xy,sc in [((1510,25,1735,260),(1260,65),1.25),((1460,445,1515,500),(1640,120),3),((1450,235,1585,398),(1260,470),2)]:
    im=mother.crop(box);im=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS);D.alpha_composite(im,xy)
dd.text((1260,790),'No old open hand / no competing arm pose.',font=font,fill='#36546e')
crop=(1240,0,1960,1080)
for n,im in [('A',A),('B',Bim),('C',C),('D',D)]:
    im.crop(crop).save(R/f'reference_native/{n}_F103_720x1080_PREPARED.png')
    im.crop(crop).resize((1024,1536),Image.Resampling.NEAREST if n=='B' else Image.Resampling.LANCZOS).save(R/f'inputs_1024x1536/{n}_F103_PREPARED_NOT_CALLED.png')
for tone,col in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
    sheet=Image.new('RGB',(1364,1024),(233,238,243))
    for j,n in enumerate('ABCD'):
        im=Image.open(R/f'inputs_1024x1536/{n}_F103_PREPARED_NOT_CALLED.png').convert('RGBA');bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);sheet.paste(bg.resize((341,512)).convert('RGB'),(j*341,0))
    bg=Image.new('RGBA',size,col);bg.alpha_composite(A)
    sheet.paste(bg.crop((1440,235,1820,485)).resize((760,500)).convert('RGB'),(0,524))
    sheet.paste(bg.crop((1350,460,1650,725)).resize((600,500)).convert('RGB'),(764,524))
    sheet.save(R/f'qa/F103_four_inputs_full_grip_waist_{tone}.png')
    bg.crop(crop).save(R/f'qa/F103_full_target_{tone}.png')

geo={'locked100_commit':'61766ddbbde81bf1a15e7b846211ea8a25d8950f','locked100_sha256':sha(R/'sources/F100_LOCKED_7dc803e9.png'),'locked100_component_RGBA_replay_identical':True,'total_group_degrees':24,'delta_from_actual100_degrees':8,'scale':1,'delta_M':M.tolist(),'delta_t':t.tolist(),'pivot':H.tolist(),'same_group':['actual100 head neck','actual100 whole continuous raw blouse','actual100 complete far arm hand jade'],'original_whole_shoes_fixed':True,'true_lamp_base_table_fixed':True,'real_bail_top':G.tolist(),'near_SOFT_actual100_shoulder_index_before_delta8':[1530,237],'near_SOFT_actual100_cuff_index_before_delta8':[1552,363],'complete_SOFT_chain':[p.tolist() for p in chain],'projected_links_cuff_elbow_wrist_SOFT_NOT_BONES':[U,V],'old_open_near_arm_in_A':False,'complete_unknown_waist_not_true_RGB':False,'real_actual100_navy_trousers_visible_no_apron_volume':True,'correct_actual100_SHORT_sleeve_preserved':True,'NEW_BARE_arm_volume_not_long_sleeve_recolored':True,'source_wire_released_for_real_front_finger_occlusion':True,'operation_white_guard_overlaps':{'head':int((white&headguard).sum()),'feet':int((white&feetguard).sum()),'fixed_lamp':int((white&lampguard).sum())},'F106_dependency':'actual accepted103 only; same whole hand and true whole physical lamp lift together by [0,-12.359119141727836]native =4.5world; do not use open hand','calls':0}
(R/'geometry/F103_actual100_common24_and_whole_grip.json').write_text(json.dumps(geo,ensure_ascii=False,indent=2)+'\n')
prompt='''Create ONE F103 drawing only, for frames103–105. This is the actual complete right-hand GRASP of the existing lantern bail while the original lantern base remains supported by the table. Mother identity/material is the locked F100 actual image, SHA7dc803e92e69cb90a84465f4b25e64f5ba9ea62b6b3853bd9a66b658f9951b2b. Preserve A's1024x1536 transparent canvas and common composition. This is a REPAIR INPUT DRAFT after a rejected first raw, NOT authorization to generate. The original real lantern must remain at A's exact fixed placement, silhouette and scale, including the real bail top around tool(716.7,476.3). Fit the new actual hand to this original wire; never move, resize or redesign the lantern to meet the hand. The previous raw moved the prop right, extended the short sleeve to the wrist and copied a technical waist panel as an apron; all three errors must be absent here.

A and C contain exactly one new opaque complete near sleeve-shoulder, upper arm, elbow, forearm, natural wrist, palm, four curled fingers and opposing thumb target. Blue/purple volumes and circles are NOT_ART construction only, never final anatomy or measured bones. Draw a natural complete arm and appropriately sized hand. The old100 open reaching hand/arm has been removed; do not retain it, overlay a second arm, paste a wrist or create a narrow hand bridge. The whole new hand must actually enclose the real original curved wire bail at its top. Show correct ownership of front fingers, wire and rear palm/thumb, with real thickness and opposition. A palm merely touching the line is not a grip. The real wire may be naturally occluded by front fingers; do not preserve an imaginary wire through the hand or cut a hand hole to expose it.

The accepted actual100 head, neck, entire continuous blue flower blouse and complete far LEFT arm/hand/jade are one scale1 group advanced by8degrees from100, reaching the already selected total24degree forward lean. Preserve that group composition and real identity/material. Both original complete shoes and lower leg support stay in their original positions. Make a continuous whole sleeve-to-chest/underarm and blouse-to-waist/hip cloth connection over the full B action band. A keeps the ACTUAL accepted100 dark navy trousers and real continuous short-sleeve blouse. There is no gray-blue waist panel to copy. Redraw only the necessary full waist/hip connection as the SAME navy trousers and same blue blouse; never add an apron, overskirt, rectangular patch or new garment. Do not leave a transparent waist hole, a narrow strip, a pasted chest block, an underarm split or an abrupt horizontal material cut. Keep the source color; no global recolor.

B opens the full semantic new/old near sleeve-arm-wholehand corridor and the complete front/waist connection needed for the lean. It is an action reference, not an executable rectangle. The actual lantern body, metal/glass proportions, base and existing table-shadow registration remain fixed; only grip-intersecting wire pixels may be naturally hidden by fingers. No lift occurs in103. D is small locked100 identity and internal clothing swatches only, with no alternate old hand pose. The far whole arm/hand/jade stays one coherent group behind the near action.

The actual short sleeve must end at the same real source cuff near the upper arm. From that real hem onward draw a BARE upper arm, anatomical elbow, BARE forearm and natural wrist into the complete grip. The peach volume is NEW BARE ARM construction only, not an existing sleeve recolored. Do not extend cloth to the wrist, add a wrist cuff or copy cloth folds into skin. D includes the real short sleeve and immediately adjacent bare skin with no hand pose. Finish all technical skin/purple hand areas as actual matching illustration with natural anatomy. Remove guides, text, diagram circles and reference-board elements. Return one transparent actual F103 drawing only, no opaque background, table/room painting, duplicate person or next106 lift state. Real full-hand enclosure and continuous clothing will be reviewed before106; do not perform106 now.
'''
(R/'requests/prompt_DRAFT_PENDING_FINAL_INPUT_GATE.txt').write_text(prompt)
args={'prompt':prompt,'referenced_image_paths':[str((R/f'inputs_1024x1536/{n}_F103_PREPARED_NOT_CALLED.png').resolve()) for n in 'ABCD'],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/state.json').write_text(json.dumps({'reference_gate':'PENDING_ASTRA_FOUR_ACTUAL_INPUTS_AND_FULL_PROMPT_REVIEW','calls':0,'native103_unique_call_after_gate_only':True,'F106_requires_actual_accepted103_whole_grip':True},indent=2)+'\n')
(R/'README.md').write_text("""# F103失败后修复输入草稿：短袖裸臂与原裤料，零调用

母图仍是锁100 61766ddb/7dc803e9，不用失败103作人物来源。锁100真实整件短袖蓝花上衣、头颈及远整臂同组再转8°到24°，脚和真灯保持原位。A/C直接保留真实短袖及袖口；唯一新近臂从袖下缘起为裸上臂、肘、裸前臂至完整新握。D补真实短袖口与相邻裸肤裁片，没有旧开放手。肉色胶囊和紫手明确NOT_ART，实际须重画自然解剖，不能复刻圆关节。

A已撤掉技术灰蓝腰块，直接显示原100真实海军蓝裤料。B仍覆盖完整袖臂全手、连续衣腰/髋连接，以清理新旧边缘叠接；不能生成围裙或新衣片。原真灯/底座落桌不动，握处原弧可被前指自然遮挡。完整prompt明确修复上一raw的长袖、腰块照抄、移灯三项问题。

此为失败后供Astra检查的输入草稿，不继承上一输入门调用许可；本草稿调用0，唯一已执行103 raw在相邻F103_NATIVE_call01_9c77230e_20261019/，尚未采用，106未启动。
""")
manifest={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'inputs':{n:manifest[f'inputs_1024x1536/{n}_F103_PREPARED_NOT_CALLED.png'] for n in 'ABCD'},'chain':geo['complete_SOFT_chain'],'overlap':geo['operation_white_guard_overlaps'],'calls':0}))
