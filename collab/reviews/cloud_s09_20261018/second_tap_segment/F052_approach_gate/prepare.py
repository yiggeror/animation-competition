#!/usr/bin/env python3
"""F052 actual rigid-source approach input only; no native generation."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_closing,binary_fill_holes
R=Path(__file__).resolve().parent;S=R/'sources'
for d in ['reference','masks','qa','requests','geometry']:(R/d).mkdir(exist_ok=True)
assert not (R/'requests/execution_state.json').exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for f in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/f['path'])==f['sha256']
assert sha(S/'F048_locked.png')=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9'
assert sha(S/'F044_locked.png')=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9'
assert sha(S/'F031_pure_whole_torch_and_grip.png')=='5e39cda65ed11384debda248a3f6c1393ec2f16261d2da25cb7a4ccb40ef0862'
im=Image.open(S/'F048_locked.png').convert('RGBA');a=np.array(im);size=im.size;yy,xx=np.indices(a.shape[:2]);rgb=a[:,:,:3].astype(int);hsv=np.array(im.convert('RGB').convert('HSV'))
def mask(n):return np.array(Image.open(S/n).convert('L'))>0
def moved(z,dy):
 q=Image.new(z.mode,z.size);q.paste(z,(0,dy));return q
def poly(pts):
 q=Image.new('L',size);ImageDraw.Draw(q).polygon([tuple(map(float,p))for p in pts],fill=255);return np.array(q)>0
def capsule(pts,r):
 pts=[tuple(map(float,p))for p in pts];q=Image.new('L',size);d=ImageDraw.Draw(q);d.line(pts,fill=255,width=2*r+1)
 for x,y in pts:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(q)>0
reg=json.loads((S/'F044_preparation.json').read_text())['registration_unchanged'];scale=reg['scale']
rows=list(csv.DictReader((S/'exposure.csv').open()));event=next(v for v in rows if int(v['start_frame_0'])==52);assert int(event['hold'])==4 and int(event['end_frame_inclusive'])==55
pure=Image.open(S/'F031_pure_whole_torch_and_grip.png').convert('RGBA');p0=np.array(pure);old=moved(pure,-32);oldarr=np.array(old);new=moved(pure,22);n=np.array(new);oldmat=oldarr[:,:,3]>0;newmat=n[:,:,3]>0
assert not np.any(a[oldmat]!=oldarr[oldmat]),'Mother048 actual whole unit must equal pure031-32, including real AA.'
alt=moved(Image.open(S/'F044_detached_unit_COMPARISON_ONLY.png').convert('RGBA'),11);altarr=np.array(alt);routes=np.any(n!=altarr,axis=2)
release_image=moved(Image.open(S/'wrist44_technical_extraction_edge90.png').convert('L'),11);release=(np.array(release_image)>0)&newmat
assert release.sum()==90 and not np.any(release&(abs(yy-xx+463)>7))
assert release[591:].sum()==0,'No torch or gripping fingers may enter wrist-only extraction release.'
(R/'geometry/wrist_release90_source_map.json').write_text(json.dumps({'pixels':int(release.sum()),'plane':'abs((y-x)+463)<=7','operation':'single proximal extraction edge release only; original input RGBA still unchanged','source_mappings':[{'target052_xy':[int(x),int(y)],'pure031_xy':[int(x),int(y-22)],'mother048_xy':[int(x),int(y-54)],'actual_RGBA':n[y,x].tolist()}for y,x in zip(*np.where(release))]},ensure_ascii=False,indent=2)+'\n')
base=a.copy();base[oldmat|newmat]=0;pre=Image.alpha_composite(Image.fromarray(base),new);pa=np.array(pre)
assert np.array_equal(pa[newmat],n[newmat])
new.save(R/'reference/F052_pure031_unit_plus22_SOURCE.png');Image.fromarray(oldarr).save(R/'reference/F048_pure031_unit_minus32_SOURCE.png');pre.save(R/'reference/F052_actual_source_preposition_NOT_ART.png')

# Material is derived from the actual048 cuff, not transplanted044 geometry.
# The polygon follows the visible ruffle outside and its real inner opening.
cuff_roi=poly([(639,679),(645,648),(661,632),(684,616),(709,607),(738,606),(766,608),(779,615),(783,632),(776,640),(751,628),(742,625),(732,637),(719,645),(704,644),(696,650),(700,660),(695,671),(686,675),(681,682),(686,690),(679,701),(671,711),(650,716),(639,710),(637,693)])
skin=(hsv[:,:,0]<=28)&(hsv[:,:,1]>40)&(rgb[:,:,0]>155)&(rgb[:,:,0]-rgb[:,:,1]>15)&(rgb[:,:,1]-rgb[:,:,2]>12)&(rgb[:,:,2]>90)&(a[:,:,3]>20)
yellow=(hsv[:,:,0]>=29)&(hsv[:,:,0]<=60)&(hsv[:,:,1]>90)&(rgb[:,:,0]>145)&(a[:,:,3]>0)
cuff_core=binary_fill_holes(binary_closing(yellow&cuff_roi,iterations=1))
near_ruffle=binary_dilation(cuff_core,iterations=1)&cuff_roi&(a[:,:,3]>0)&~skin
# Explicitly retain complete embedded white dots and crease ink on the same
# connected yellow material; never the previous near-arm skin or cut edge.
oldarm_mask=mask('old048_complete_near_arm.png')
oldcorridor=capsule([(707,670),(852,707),(1037,537)],54)
oldactual=(oldarm_mask|oldcorridor)&(a[:,:,3]>0)&skin&~oldmat&~near_ruffle
oldoutline=binary_dilation(oldactual,iterations=3)&(a[:,:,3]>0)
future=capsule([(707,670),(858,716),(1037,591)],56)
receiver=mask('fixed_palm_actual_material.png')&(a[:,:,3]>0)
oldactual&=~receiver
head=mask('head_neck_collar_actual.png')&(a[:,:,3]>0)&~binary_dilation(oldactual,iterations=2)&~oldmat
far_roi=poly([(934,539),(1028,539),(1040,617),(1029,686),(932,707)])
far_yellow=(rgb[:,:,0]>180)&(rgb[:,:,1]>135)&(rgb[:,:,2]<100)&(a[:,:,3]>20)&far_roi
far_material=binary_dilation(binary_fill_holes(binary_closing(far_yellow,iterations=2)),iterations=2)&far_roi&(a[:,:,3]>0)
far_material&=~binary_dilation(oldactual,iterations=3)&~oldmat
far_puff_guard=far_material&~future
far_arm_roi=poly([(928,675),(1035,675),(1065,727),(1230,705),(1240,795),(1085,824),(1015,859),(964,855),(940,810),(921,753)])
far_arm_guard=far_arm_roi&(a[:,:,3]>0)&~binary_dilation(oldactual,iterations=3)&~oldmat&~future
rigid_guard=newmat&~release
waist=(yy>=777)&(a[:,:,3]>0)
guards={'head_neck_collar_actual':head,'near_ruffle_ACTUAL048_material':near_ruffle,'far_puff_actual_visible_except_new_foreground':far_puff_guard,'far_arm_actual_visible_except_new_foreground':far_arm_guard,'fixed_receiver_palm_actual_material':receiver,'pure_rigid_unit_except90_technical_wrist':rigid_guard,'waist_skirt_actual_material':waist}
hard=np.logical_or.reduce(list(guards.values()))
vacated=oldmat&~newmat
semantic=binary_dilation(oldarm_mask|oldoutline,iterations=8)|oldcorridor|future|vacated|release
semantic|=poly([(673,621),(781,600),(874,600),(990,514),(1085,515),(1107,665),(1025,721),(915,777),(821,786),(699,731),(664,690)])
edit=semantic&~hard
crop=(620,240,1240,860);inside=(xx>=620)&(xx<1240)&(yy>=240)&(yy<860)
assert not np.any(edit&~inside&(pa[:,:,3]>20))
edit&=inside
assert (release&edit).sum()==90
for name,z in {**guards,'F052_complete_near_arm_and_vacated_WHITE_EDIT_PENDING':edit,'old048_actual_near_arm_material':oldactual,'new_full_near_arm_corridor_GUIDE_ONLY':future,'old_unit_vacated_material':vacated,'actual_near_ruffle_polygon_GUIDE_ONLY':cuff_roi,'wrist_technical_extraction90_RELEASE':release,'F031_pure_original_unit_alpha_material':p0[:,:,3]>0}.items():Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
pre.crop(crop).save(R/'reference/F052_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F052_crop_WHITE_EDIT_PENDING.png')
# Actual layer contours, not an estimated old diameter or assumed palm plane.
scan=[]
for x in range(1090,1178):
 cy=np.flatnonzero(n[600:710,x,3]>=128);py=np.flatnonzero((a[695:790,x,3]>=128)&receiver[695:790,x])
 if len(cy)and len(py):
  c=int(cy[-1]+600);p=int(py[0]+695);scan.append({'x':x,'tailcap_last_alpha128_y':c,'palm_first_alpha128_y':p,'clear_native_rows':p-c-1})
assert scan and min(v['clear_native_rows']for v in scan)==37
(R/'geometry/actual_cap_palm_gap_scan.json').write_text(json.dumps(scan,indent=2)+'\n')
old44ruffle=mask('old044_ruffle_COMPARISON_ONLY.png');a44=np.array(Image.open(S/'F044_locked.png').convert('RGBA'))
route_report={'primary':'pure031+22 == true pure031-32 from mother048 moved+54; no resampling','mother048_unit_alpha_positive_RGBA_changes':int(np.any(a[oldmat]!=oldarr[oldmat],axis=1).sum()),'alternate_comparison_only':'detached044+11; NOT adopted because its old042 flattened/wrist AA differs','all_RGBA_differences':int(routes.sum()),'differences_in_union_alpha_positive':int((routes&((n[:,:,3]>0)|(altarr[:,:,3]>0))).sum()),'differences_at_pure031_alpha_ge240':int((routes&(n[:,:,3]>=240)).sum()),'both_alpha0_RGB_only_differences':int((routes&(n[:,:,3]==0)&(altarr[:,:,3]==0)).sum()),'difference_coordinates_and_RGBA':[{'xy':[int(x),int(y)],'pure031_RGBA':n[y,x].tolist(),'detached044_RGBA':altarr[y,x].tolist()}for y,x in zip(*np.where(routes))]}
(R/'geometry/two_source_routes_ACTUAL_NOT_IDENTICAL.json').write_text(json.dumps(route_report,ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(im,col):
 q=Image.new('RGBA',size,col);q.alpha_composite(im);return q
for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 q=bg(pre,col);q.convert('RGB').save(R/f'qa/F052_full_{tag}.png');wash=Image.new('RGBA',size,(220,35,120,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));ov=q.copy();ov.alpha_composite(wash)
 sheet=Image.new('RGB',(1860,655),(237,242,246));d=ImageDraw.Draw(sheet)
 for i,(title,z)in enumerate([('锁048真实蓄势母态',bg(im,col)),('052整件下54／预摆非画稿',q),('完整近臂／腾空白域待输入审',ov)]):sheet.paste(z.crop(crop).convert('RGB'),(i*620,35));d.text((i*620+5,8),title,font=font,fill='#26343e')
 sheet.save(R/f'qa/F048_F052_actual_preposition_and_domain_{tag}.png')
 det=Image.new('RGB',(900,620),(237,242,246));d=ImageDraw.Draw(det)
 for i,(title,z)in enumerate([('048实际手筒／纯掌',im),('052实际37native离掌',pre)]):
  det.paste(bg(z,col).crop((1070,580,1220,785)).resize((450,615),Image.Resampling.NEAREST).convert('RGB'),(i*450,25));d.text((i*450+4,3),title,font=font,fill='#26343e')
 det.save(R/f'qa/actual_tailcap_fixed_palm_gap_{tag}.png')
 cf=bg(im,col);h=Image.new('RGBA',size,(20,150,210,0));h.putalpha(Image.fromarray(near_ruffle.astype('uint8')*130));cf.alpha_composite(h);cf.crop((630,590,795,735)).resize((660,580),Image.Resampling.NEAREST).convert('RGB').save(R/f'qa/ACTUAL048_near_ruffle_protection_{tag}.png')
report={'status':'F052_ONLY_ACTUAL_INPUT_PREPARED_PENDING_AUTHOR_REVIEW_NO_CALL','mother048_SHA':sha(S/'F048_locked.png'),'context044_SHA':sha(S/'F044_locked.png'),'pure031_SHA':sha(S/'F031_pure_whole_torch_and_grip.png'),'preposition_SHA':sha(R/'reference/F052_actual_source_preposition_NOT_ART.png'),'frame':52,'hold':4,'inclusive_frames':[52,55],'whole_true_hand_torch_translation_from048_native':[0,54],'absolute_from031_native':[0,22],'relative_to042_native':[0,-37],'rotation':0,'scale':1,'resampling':False,'registration':reg,'crop_xyxy':crop,'white_pixels':int(edit.sum()),'wrist_extraction_release_pixels':int(release.sum()),'wrist_release_plane':'abs((y-x)+463)<=7, actual proximal ROI and material, exact90; no grasp fingers/torch','actual_minimum_clear_native_rows':min(v['clear_native_rows']for v in scan),'actual_minimum_clear_registered_px':min(v['clear_native_rows']for v in scan)*scale,'cap_palm_opaque_overlap':int(((n[:,:,3]>=128)&receiver&(a[:,:,3]>=128)).sum()),'source052_rigid_foreground_RGBA_changes':int(np.any(pa[newmat]!=n[newmat],axis=1).sum()),'fixed_palm_RGBA_changes':int(np.any(pa[receiver]!=a[receiver],axis=1).sum()),'guard_intersections':{k:int((edit&v).sum())for k,v in guards.items()},'near_ruffle_actual_material_pixels':int(near_ruffle.sum()),'old044_ruffle_mask_actual048_RGBA_differences':int((old44ruffle&np.any(a44!=a,axis=2)).sum()),'actual_source_skin_pixels_frozen_as_near_ruffle':int((near_ruffle&skin).sum()),'old_actual_neararm_uneditable_except_genuine_hard':int((oldactual&~edit&~hard).sum()),'old_actual_neararm_in_guard':int((oldactual&hard).sum()),'outside_old_new_unit_changes':int(np.any(pa[~(oldmat|newmat)]!=a[~(oldmat|newmat)],axis=1).sum()),'source_snapshot_manifest':'sources/snapshot_manifest.json','two_routes':'geometry/two_source_routes_ACTUAL_NOT_IDENTICAL.json','new_image_calls':0,'F056_unopened':True,'limits':['Old048 arm remains only inside whole WHITE redraw domain; no finished052 articulation claimed.','Only actual materials/AA protect; no alpha0 guard moat. Visible far layers can be occluded by new foreground neararm.','Cuff derived from actual048 yellow/white/ink material; old044ruffle is comparison only.','90pixel extraction edge release once is not permission to redraw fingers or flashlight.','Actual native output and048x4/052x4/056x2 exposure must pass later; no056 preparation yet.']}
assert all(v==0 for v in report['guard_intersections'].values()) and report['fixed_palm_RGBA_changes']==0 and report['source052_rigid_foreground_RGBA_changes']==0 and report['outside_old_new_unit_changes']==0
(R/'preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit only WHITE pixels of image2 on image1, a620x620 transparent F052 preposition crop. Image3 is the locked real F044 full character for near-arm proportions and adjacent-pose continuity. Image4 is the locked real F048 mother for identity, receiving hand, cuffs, colors and body. Return exactly the same620x620 transparent crop and framing. No resizing, zoom, rotation, mirroring or background.

F052 is the SECOND TAP APPROACH,4frames, before the next tailcap contact. The entire genuine original near RIGHT gripping hand and flashlight have ALREADY moved DOWN54native pixels from048, leaving exactly37native clear rows (23.299748registered pixels) above the unchanged real far LEFT receiving palm. Do not move/rotate/resize them again. Keep the whole original flashlight length/diameter/lens/tailcap/switch OFF, four gripping fingers, thumb and palm geometry. Only the explicitly WHITE90pixel technical proximal wrist extraction edge may be joined as forearm contour; no finger/torch redesign. The flashlight tailcap remains separated from the palm, not touching the lamp head or fingertips. Do not carry skin with the cap.

Redraw the COMPLETE near RIGHT arm from the original image-left yellow ruffle opening through one natural upper arm, bent elbow, whole forearm to the new original wrist. The full old048 arm inside WHITE is obsolete: replace the whole contour, internal shade and articulation, not a wrist-seam patch or a thin bridge. Match accepted F044/048 real upper-arm and forearm volumes and child proportions, one continuous chain, no split, stretch, extra elbow or double cuff arc. Keep original BLACK actual048 yellow cuff material/white dots/crease lines; join its inner opening naturally without retaining artificial cut edges. No detached old ink/skin scraps.

Restore continuous actual yellow dress/white dots/crease planes in the old arm vacated area and clear the old torch/arm outline remnants. The actual round far yellow sleeve and far arm are BACK layers. Preserve genuine visible BLACK material; the new near arm can naturally cover their proximal parts where WHITE releases foreground corridor. Do not freeze hidden far-layer alpha in front of new skin, invent a pointed/forked rear sleeve, or leave a floating edge. The full real receiving LEFT palm, distal far forearm, head, face, hair, gaze, white collar, waist/skirt and all BLACK genuine material stay fixed. Preserve flat warm skin and darker cel shadow separately, exact original palette/ink and sharp material AA; no global recolor, glow, text, guides, motion blur or new objects. Only F052; F056 has not begun.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F052_crop_RGBA_NOT_ART.png'),str(R/'masks/F052_crop_WHITE_EDIT_PENDING.png'),str(S/'F044_locked.png'),str(S/'F048_locked.png')],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/input_freeze_PENDING_REVIEW.json').write_text(json.dumps({'status':'PREPARED_ONLY_NOT_EXECUTED','inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'new_image_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('F052×4仅实际源像素输入预备，未生成/未提交；F056未开。\n\n唯一母048=锁037 68ce16…。真正pure031手筒5e39…整体+22native，等同母048真实pure031−32整体下54，scale1/rot0/不重采样。044拆分手筒+11只比较，实际AA不全同，差异坐标逐项保存，不混用042扁平接合。真cap/固定掌扫描37native=23.299748registered离掌。\n\n完整近臂、旧臂/旧筒腾空衣片白域要原生新绘，不沿旧断边补腕。实际048 cuff材料重新辨别，旧044ruffle仅比较。真实头领/固定掌/原袖材料/裙腰保；远袖和远臂按实际可见材料保护，允许新近臂自然遮挡。纯手筒实际proxwrist技术提取边恰90px一次释放，坐标/plane记录，不开放真实抓握指掌/筒体。\n\n建议620x620 crop(620,240,1240,860)，预摆+白罩+锁044比例上下文+锁048身份上下文。所有输入依赖已快照，prepare不调用imagegen。先实际输入审，后由主作者单次绘图和独立实审，再考虑056复用。\n')
print(json.dumps({k:report[k]for k in ['status','preposition_SHA','white_pixels','near_ruffle_actual_material_pixels','actual_minimum_clear_native_rows','actual_minimum_clear_registered_px','old_actual_neararm_in_guard']},ensure_ascii=False))
