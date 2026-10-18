#!/usr/bin/env python3
"""A/B/C/D corrected084: no old pants; frozen real anchors; neutral mask; schematic volume and true swatches."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,minimum_filter,label
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for q in ['reference_native','inputs_1024x1536','masks','geometry','qa','requests']:(R/q).mkdir(exist_ok=True)
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['path'])==v['sha256']
g=json.loads((S/'F084_frozen_targets_and_proxy_metadata.json').read_text());size=(1672,1080);yy,xx=np.indices((1080,1672));crop=(1000,280,1520,1060);cropoff=np.array(crop[:2]);localsize=(520,780)
order=['far_shoe_ankle_SWING','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SUPPORT_FIXED']
layers={k:Image.open(S/f'F084_FROZEN_{k}.png').convert('RGBA')for k in order};alpha={k:np.array(v)[:,:,3]for k,v in layers.items()}
Afull=Image.new('RGBA',size)
for k in order:Afull.alpha_composite(layers[k])
A=Afull.crop(crop);out=np.array(Afull)
def visible(k):
 front=np.zeros((1080,1672),bool)
 for v in order[order.index(k)+1:]:front|=alpha[v]>0
 return(alpha[k]>0)&~front

def capsule(points,r):
 pts=[tuple(map(float,p))for p in points];im=Image.new('L',size);d=ImageDraw.Draw(im);d.line(pts,fill=255,width=2*r+1)
 for x,y in pts:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(im)>0
roots={k:np.array(v)for k,v in g['actual_sleeve_roots_native'].items()};sleeves=np.zeros((1080,1672),bool)
for root in roots.values():sleeves|=capsule([root+[-20,-4],root+[20,14]],15)
Hn=np.array(g['hidden_near_hip_proxy_native']);Hf=np.array(g['hidden_far_hip_proxy_native']);Kn=np.array(g['near_knee_soft_corridor_native']);Kf=np.array(g['far_knee_soft_corridor_native']);An=np.array(g['actual_near_ankle_proxy_native']);Af=np.array(g['actual_far_ankle_proxy_native'])
bodyguard=(alpha['body_head_blouse']>0)&~sleeves;armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves;nearfootguard=visible('near_shoe_ankle_SUPPORT_FIXED')
future_near_shin=capsule([Kn,An+[0,-12]],48)&(yy<An[1]+3)
farfootvisible=visible('far_shoe_ankle_SWING');future_far_foot_occlusion_release=farfootvisible&future_near_shin
farfootguard=farfootvisible&~future_near_shin
hard=bodyguard|armguard|nearfootguard|farfootguard
neutral=(xx>=1100)&(xx<1500)&(yy>=490)&(yy<1000)
# Only neutral rectangle and existing small sleeve seams define the edit domain.
# Projected near-shin release SUBTRACTS a rear-foot guard; no old pants mask or
# silhouette has been read, copied, translated, or used to shape this rectangle.
edit=(neutral|sleeves)&~hard
inside=(xx>=1000)&(xx<1520)&(yy>=280)&(yy<1060);assert not np.any(edit&~inside);edit&=inside
B=Image.fromarray(edit.astype('uint8')*255).crop(crop)
for name,z in [('neutral_rectangle_native',neutral),('actual_stable_body_guard_except_sleeves',bodyguard),('actual_visible_whole_arms_guard_except_sleeves',armguard),('near_fixed_actual_foot_guard',nearfootguard),('far_actual_visible_foot_guard_except_new_front_shin',farfootguard),('far_whole_source_layer_NOT_A_HIDDEN_GUARD',alpha['far_shoe_ankle_SWING']>0),('future_near_shin_occludes_back_shoe_RELEASE',future_far_foot_occlusion_release),('existing_small_sleeve_seams',sleeves),('complete_neutral_white_EDIT_REFERENCE',edit)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
A.save(R/'reference_native/A_frozen_real_anchors_NO_OLD_PANTS_520x780.png');B.save(R/'reference_native/B_neutral_rectangle_edit_REFERENCE_520x780.png')
# C is explicitly a diagram: broad pelvis/thigh/knee/calf geometric volumes,
# rear LEFT ochre then front RIGHT blue, untextured schematic material, not art.
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
C=Image.new('RGBA',localsize,(234,240,244,255));d=ImageDraw.Draw(C)
d.text((12,12),'C 体量技术示意 / NOT ART / 非骨测',font=font,fill='#273d4b');d.text((12,35),'宽腰臀→整大腿→软膝→小腿；不作最终人物轮廓',font=small,fill='#536978')
# Full waist/pelvis volume: deliberately polygonal technical box/trapezoid,
# never copied from079 silhouette. H markers lie inside its coarse envelope.
d.polygon([(204,260),(369,260),(376,319),(348,365),(279,382),(222,349)],fill='#ced8e0',outline='#607c91',width=3)
d.text((223,274),'WAIST / PELVIS',font=small,fill='#445b6c')
def volume_chain(h,k,a,rth,rcalf,col,edge,tag):
 pts=[np.array(h)-cropoff,np.array(k)-cropoff,np.array(a)-cropoff]
 for p,q,r1,r2 in [(pts[0],pts[1],rth,rth*.88),(pts[1],pts[2],rcalf,rcalf*.82)]:
  v=q-p;nn=np.array([-v[1],v[0]])/np.linalg.norm(v);corn=[p+nn*r1,q+nn*r2,q-nn*r2,p-nn*r1]
  d.polygon([tuple(t)for t in corn],fill=col,outline=edge,width=3)
 x,y=pts[1];rr=rcalf*.95;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col,outline=edge,width=3)
 # Whole calf into existing actual ankle is a volume direction; real shape and
 # clothing must be entirely drawn by the future native edit, not copied.
 for p,lab in zip(pts,['hidden H','soft K','actual A']):
  x,y=p;d.ellipse((x-5,y-5,x+5,y+5),fill=edge);d.text((x+8,y-9),lab,font=small,fill=edge)
 d.line([tuple(p)for p in pts],fill=edge,width=2);return pts
# The genuine raised far shoe is a BACK layer, drawn before new near volume.
C.alpha_composite(layers['far_shoe_ankle_SWING'].crop(crop));d=ImageDraw.Draw(C)
farpts=volume_chain(Hf,Kf,Af,45,36,'#ddc3a5','#a27038','far LEFT back')
nearpts=volume_chain(Hn,Kn,An,47,38,'#a6c7d9','#3c7c9f','near RIGHT front')
# Exact placed original shoes only, at the same local positions as A. They are
# anchors in a technical plate; the whole rear foot remains available below new
# pants and may be occluded by the front near-shin diagram where appropriate.
feet=Image.new('RGBA',size);feet.alpha_composite(layers['far_shoe_ankle_SWING']);feet.alpha_composite(layers['near_shoe_ankle_SUPPORT_FIXED']);footcrop=feet.crop(crop)
# Near support shoe stays front. The far source layer is already behind the
# whole volume; it never cuts a shoe-shaped hole through the new front shin.
C.alpha_composite(layers['near_shoe_ankle_SUPPORT_FIXED'].crop(crop));d=ImageDraw.Draw(C);d.line((175,742,402,742),fill='#3c7c9f',width=2);d.line((175,679,402,679),fill='#a27038',width=2)
d.text((12,85),'NEAR RIGHT = FRONT / SUPPORT',font=small,fill='#3c7c9f');d.text((12,106),'FAR LEFT = BACK / PASSING',font=small,fill='#a27038');d.text((12,132),'真实鞋锚可见性展示；生产层far鞋在新近裤后',font=small,fill='#536978');d.text((12,152),'Anear≈246,678 / Afar≈271,611',font=small,fill='#536978');d.text((12,174),'Knear≈301,492 / Kfar≈396,460 仅软走廊',font=small,fill='#536978');d.text((12,756),'示意体积不可印入画稿，整裤仍需一次完整真绘',font=small,fill='#273d4b')
C.save(R/'reference_native/C_wide_complete_leg_volume_TECHNICAL_NOT_ART_520x780.png')
# D contains ONLY interior rectangular real057/062 material swatches, no whole
# figure, limb silhouette, failedraw, joint guide, generated or code-filled cloth.
D=Image.new('RGBA',localsize,(234,240,244,255));dd=ImageDraw.Draw(D);dd.text((12,12),'D 真实布料 / 墨线 / 母色；无人物轮廓',font=font,fill='#273d4b');dd.text((12,36),'原生矩形内料1:1取样；不用于复制旧姿态',font=small,fill='#536978')
patches=[]
for j,frame in enumerate([57,62]):
 sp=S/f'F0{frame}_palette_ARCHIVE_NOT_REQUEST.png';mp=S/f'F0{frame}_actual_pants_material_mask.png';orig=np.array(Image.open(sp).convert('RGBA'));mm=np.array(Image.open(mp).convert('L'))>0;mm=binary_fill_holes(mm);rgb=orig[:,:,:3].astype(int)
 valid=mm&(orig[:,:,3]>=250)&(rgb.max(axis=2)<145)
 ok=minimum_filter(valid.astype('uint8'),size=(64,48),mode='constant')>0
 ys,xs=np.where(ok);assert len(xs)>0,'Need genuine interior cloth rectangle'
 # Select real upper/lower cloth locations to include different fold planes.
 choices=[]
 for targetY in ([700,800]if frame==57 else[680,800]):
  scores=np.abs(ys-targetY)+np.abs(xs-xs.mean())*.03
  for used in choices:scores+=np.where(np.hypot(xs-used[0],ys-used[1])<65,1e6,0)
  q=int(np.argmin(scores));choices.append((int(xs[q]),int(ys[q])))
 for i,(cx,cy)in enumerate(choices):
  box=(cx-24,cy-32,cx+24,cy+32);patch=Image.fromarray(orig).crop(box);pa=np.array(patch);assert pa.shape==(64,48,4)and np.all(valid[cy-32:cy+32,cx-24:cx+24])
  dx=35+i*240;dy=110+j*290;D.paste(patch,(dx,dy));dd=ImageDraw.Draw(D);dd.text((dx,dy-27),f'F0{frame} native cloth {i+1}',font=small,fill='#273d4b');dd.text((dx,dy+78),str(box),font=small,fill='#536978')
  # Native enlarged color rectangles are intentionally NOT created: every
  # swatch remains original1:1 source material before whole-image128/65 scale.
  patches.append({'source':sp.name,'source_sha256':sha(sp),'source_box_halfopen':list(box),'native_D_box_halfopen':[dx,dy,dx+48,dy+64],'source_RGBA_exact_in_native_D':True,'all_source_pixels_inside_actual_pants_material_and_alpha250':True})
D.save(R/'reference_native/D_actual057_062_fabric_ink_palette_NO_FIGURE_520x780.png')
# All FOUR full reference canvases receive exactly ONE common uniform scale.
refs=[('A',R/'reference_native/A_frozen_real_anchors_NO_OLD_PANTS_520x780.png'),('B',R/'reference_native/B_neutral_rectangle_edit_REFERENCE_520x780.png'),('C',R/'reference_native/C_wide_complete_leg_volume_TECHNICAL_NOT_ART_520x780.png'),('D',R/'reference_native/D_actual057_062_fabric_ink_palette_NO_FIGURE_520x780.png')]
reqpaths=[]
for letter,p in refs:
 z=Image.open(p);assert z.size==(520,780);filter=Image.Resampling.NEAREST if letter=='B'else Image.Resampling.LANCZOS;target=R/'inputs_1024x1536'/f'{letter}_whole_canvas_128over65_PREPARED.png';z.resize((1024,1536),filter).save(target);reqpaths.append(target)
for tone,c in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2080,825),(236,241,246));dr=ImageDraw.Draw(sheet)
 for j,(letter,p)in enumerate(refs):
  z=Image.open(p).convert('RGBA');bg=Image.new('RGBA',localsize,c);bg.alpha_composite(z);sheet.paste(bg.convert('RGB'),(j*520,40));dr.text((j*520+6,7),letter+' / native520×780 / 全幅统一放大',font=font,fill='#273d4b')
 sheet.save(R/f'qa/four_native_references_{tone}.png')
 z=Image.new('RGBA',localsize,c);z.alpha_composite(A);z.convert('RGB').save(R/f'qa/A_neutral_anchors_{tone}.png');ov=z.copy();wash=Image.new('RGBA',localsize,(219,36,121,0));wash.putalpha(B.point(lambda x:110 if x else 0));ov.alpha_composite(wash);ov.convert('RGB').save(R/f'qa/B_actual_neutral_white_overlay_{tone}.png')
# Fixed two paragraphs from parent/Astra. No extra legacy long prompt or inputs.
prompt='''Edit image A as a cropped restoration, not as a new character illustration. Keep exactly its shoulder/blouse-to-feet 2:3 canvas, scale and anchor positions. The head is outside this crop. Do not add a head, zoom out, recenter a person or fit a full figure. Image B is the permitted editing-region reference; image C shows soft joint directions only and must never appear in the art; image D is fabric/ink/color only.
Complete ONE coherent natural waist, pelvis and both whole navy trouser legs in the empty editable area. There is intentionally no old leg silhouette to preserve. The near anatomical RIGHT leg bears weight on the existing lower shoe. The far anatomical LEFT thigh passes forward to image-right, with a flexed knee and calf returning to the existing raised shoe directly above it. The two existing shoe x-ranges nearly coincide; do not invent a foot behind them. Keep the two placed original shoe/ankle targets, blouse and complete arms in their exact positions. The far shoe is a complete rear layer: the new foreground near shin may naturally cover the marked overlap, never leave a shoe-shaped hole through the shin. Preserve full thigh, knee-back and calf volume with the original flat navy, shadow and ink style. Join naturally under the real blouse and into both actual ankle targets; connect only the small permitted sleeve seams. Return the same cropped transparent composition. No additional shoe, hand, head, guide or following state.'''
(R/'requests/prompt_ASTRA_SHORT_EXACT_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(p)for p in reqpaths],'transparent_background':True};assert len(args['referenced_image_paths'])==4
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
feetchecks={}
for n in ['near_shoe_ankle_SUPPORT_FIXED','far_shoe_ankle_SWING']:
 ar=np.array(layers[n]);ys,xs=np.where(ar[:,:,3]>=128);feetchecks[n]={'native_sole_alpha128':int(ys.max()),'crop_local_sole_alpha128':int(ys.max()-280),'crop_local_xspan_alpha128':[int(xs.min()-1000),int(xs.max()-1000)],'layer_sha256':sha(S/f'F084_FROZEN_{n}.png'),'changed_from_frozen_RGBA_pixels':0}
assert feetchecks['near_shoe_ankle_SUPPORT_FIXED']['crop_local_sole_alpha128']==742;assert feetchecks['far_shoe_ankle_SWING']['crop_local_sole_alpha128']==679
assert feetchecks['near_shoe_ankle_SUPPORT_FIXED']['crop_local_xspan_alpha128']==[199,374];assert feetchecks['far_shoe_ankle_SWING']['crop_local_xspan_alpha128']==[204,373]
lab,_=label(edit);probes={}
for n,p in [('nearH',Hn),('nearK',Kn),('nearA_approach',An+[0,-25]),('farH',Hf),('farK',Kf),('farA_approach',Af+[0,-25])]:
 x,y=np.rint(p).astype(int);probes[n]={'native_xy':[int(x),int(y)],'white':bool(edit[y,x]),'component':int(lab[y,x])}
assert all(v['white']for v in probes.values())and len({v['component']for v in probes.values()})==1
checks={'status':'CORRECTED084_FOUR_NEUTRAL_INPUTS_PREPARED_PENDING_PARENT_ASTRA_NO_CALL','frame':84,'hold':6,'crop_native':[1000,280,1520,1060],'native_input_size':[520,780],'requested_four_image_size':[1024,1536],'whole_canvas_uniform_forward_scale':128/65,'unique_inverse_scale':65/128,'native_full_mapping':'(x_native,y_native)=(x_tool*65/128+1000,y_tool*65/128+280), whole image only; no part scale, shoe move, or full-person fit.','frozen_five_source_layers':[{'name':k,'sha256':sha(S/f'F084_FROZEN_{k}.png'),'native_RGBA_not_modified':True}for k in order],'A_composite_order_back_to_front':order,'A_old079_or_old084_trouser_layer_pixels_adopted':0,'A_inputs_are_only_five_frozen_real_layers':True,'B_base_rectangle_native_halfopen':[1100,490,1500,1000],'B_depends_on_old_pants_contours':False,'B_reference_not_true_tool_hardmask':True,'white_pixels':int(edit.sum()),'protected_intersections':{k:int((edit&v).sum())for k,v in [('actual_body_except_sleeves',bodyguard),('complete_visible_arms_except_sleeves',armguard),('near_real_support_foot',nearfootguard),('far_real_visible_foot_except_future_front_occlusion',farfootguard)]},'hard_guard_alpha0_pixels':int((hard&(out[:,:,3]==0)).sum()),'far_whole_source_foot_unchanged_future_front_shin_occlusion_release_pixels':int(future_far_foot_occlusion_release.sum()),'feet':feetchecks,'continuous_neutral_white_probes':probes,'C_back_to_front':['real_far_raised_shoe','schematic_far_leg_volume','schematic_near_leg_volume','real_near_support_shoe'],'C':'Manually constructed broad waist/pelvis, two full thigh/knee/calf technical volumes with far behind near, plus soft H/K/A and real shoe anchors; NOT art or measured bones; never adopted as native pixels. No old pose silhouette.','D_true_interior_cloth_samples':patches,'four_request_inputs':[{'letter':v[0],'path':str(p.relative_to(R)),'sha256':sha(p)}for v,p in zip(refs,reqpaths)],'exact_short_prompt_sha256':sha(R/'requests/prompt_ASTRA_SHORT_EXACT_PREPARED_NOT_CALLED.txt'),'new_calls':0,'post_output_gate':'Actual whole native pants pose/volume and both real shoe anchors must register before source-protected composition; do not restore source shoes then hide a wrong pose with thin bridges.','next_state_unopened':True}
assert not any(checks['protected_intersections'].values());assert checks['hard_guard_alpha0_pixels']==0
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
(R/'requests/inputs_PENDING_ASTRA_REVIEW.json').write_text(json.dumps({'status':'PREPARED_NOT_CALLED_FOUR_INPUTS_ONLY','inputs':checks['four_request_inputs'],'prompt_sha256':checks['exact_short_prompt_sha256'],'tool_mask_is_reference_only':True,'new_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('''# F084纠正中性四图输入门（未调用）

A只叠冻结084五真实层：头衣、双整臂、两整鞋；裤区域空白，没有079旧裤/失败084裤/旧后腿轮廓。B只用native中性矩形[1100,490,1500,1000]减真实可见保护域＋原袖根小窗，不依赖旧裤mask或姿态。后鞋完整底层保留，但未来前近胫走廊不以隐藏后鞋alpha挡住新裤。

C是明确非画稿/非骨测的手工技术volume diagram：宽腰臀→两完整大腿→软膝→小腿，far后near前，软H/K/A连到真实鞋锚，不复制旧轮廓、不只给细线点。C不得进入画稿像素。D只从锁057/062真实内部裤料取原生1:1矩形布料/阴影/墨色样片，无人物/肢体外轮廓。

四参考均先520×780，再整幅唯一128/65放大1024×1536。source native层不动；唯一逆映射65/128＋cropoffset(1000,280)，禁止分部缩放/挪鞋/全身fit。mask只是编辑范围参考，不是工具hardmask。

request只有inputs_1024x1536/A/B/C/D四PNG，原作者提供的两段短prompt逐字保留，无旧长prompt、母全身或失败RAW附图。source内全身palette仅档案，绝不列请求参考。

近支撑shoe localsole742、x199–374；远抬shoe localsole679、x204–373，五源不改。真正输出必须先整体腰臀双腿体量/前后层、固定真鞋锚点注册合格，再用真实冻结材料保护重组；不能恢复真鞋后用窄桥掩盖错姿。本包只输入门，交Astra审，不调用生成、不扩090。
''',encoding='utf8')
print(json.dumps({'A_sha256':checks['four_request_inputs'][0]['sha256'],'B_sha256':checks['four_request_inputs'][1]['sha256'],'C_sha256':checks['four_request_inputs'][2]['sha256'],'D_sha256':checks['four_request_inputs'][3]['sha256'],'white_pixels':int(edit.sum()),'guard_intersections':checks['protected_intersections'],'alpha0guard':checks['hard_guard_alpha0_pixels'],'feet':feetchecks,'patches':patches},ensure_ascii=False,indent=2))
