#!/usr/bin/env python3
"""Freeze existing actual evidence; zero calls, zero geometry micro-adjustments."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_erosion
import json,hashlib,shutil,numpy as np
R=Path(__file__).resolve().parent;P=R.parent/'F063_same_source_registration_gate_20261019'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['sources','fixed_trial','comparison','qa','masks']:(R/d).mkdir(exist_ok=True)
copy_map={
 'sources/F063_local_repair_RAW_same_source.png':'sources/F063_local_repair_RAW_same_source.png',
 'sources/F044_same_rigid_grip_torch_SOURCE.png':'sources/F044_same_rigid_grip_torch_SOURCE.png',
 'sources/F044_frozen_production_mother_REFERENCE_ONLY.png':'sources/F044_frozen_production_mother_REFERENCE_ONLY.png',
 'sources/F063_frozen_target_geometry.json':'sources/F063_frozen_target_geometry.json',
 'sources/F044_actual_head_neck_collar_guard.png':'masks/F044_actual_head_neck_collar_guard.png',
 'sources/F044_actual_stable_near_ruffle_guard.png':'masks/F044_actual_stable_near_ruffle_guard.png',
 'sources/F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png':'masks/F044_stable_skirt_guard_UNCHANGED_FROM_PREVIOUS_GATE.png',
 'candidate/F063_single_group_026_backplate_TRIAL_HOLD.png':'fixed_trial/F063_single_group_026_backplate_TRIAL_HOLD.png',
 'candidate/same_transform_near_arm_grip_COMPLETE_prop.png':'fixed_trial/F063_same_transform_near_arm_grip_COMPLETE_prop.png',
 'candidate/same_transform_complete_group_ONE_RESAMPLE.png':'fixed_trial/F063_same_transform_complete_group_ONE_RESAMPLE.png',
 'candidate/SOURCE_same_raw_complete_visible_arms_grasp_prop.png':'fixed_trial/F063_SOURCE_same_raw_complete_visible_arms_grasp_prop.png',
 'geometry/registration_and_source_checks.json':'fixed_trial/registration_and_source_checks.json',
 'qa/root_independent_tail_material_extent.json':'fixed_trial/root_independent_tail_material_extent.json',
 'qa/root_actual_same_source_review_HOLD.json':'fixed_trial/root_actual_same_source_review_HOLD.json',
 'qa/61sol_final_same_source_trial_HOLD.json':'fixed_trial/61sol_final_same_source_trial_HOLD.json',
 'qa/full_registered_026_trial_gray.png':'fixed_trial/full_registered_026_trial_gray.png',
 'qa/full_registered_026_trial_dark.png':'fixed_trial/full_registered_026_trial_dark.png',
 'masks/raw_complete_prop_actual_material.png':'masks/F063_raw_complete_prop_actual_material.png',
}
rows=[]
for src,dst in copy_map.items():
 shutil.copyfile(P/src,R/dst);assert sha(P/src)==sha(R/dst)
 rows.append({'source_commit':'68cde1d99a833a6b1f879f2ea0f44f042a4a6961','source_package':str(P.name),'source_path':src,'snapshot_path':dst,'sha256':sha(R/dst)})
assert sha(R/'fixed_trial/F063_single_group_026_backplate_TRIAL_HOLD.png')=='6ca8123da6afd1eafe7c78b51e819aac352bc9d90d3de0c6a988d3fdecf606e9'
(R/'sources/snapshot_manifest.json').write_text(json.dumps({'exact_copies':rows},ensure_ascii=False,indent=2)+'\n')
frozen=json.loads((R/'sources/F063_frozen_target_geometry.json').read_text());geo=json.loads((R/'fixed_trial/registration_and_source_checks.json').read_text())
M=np.asarray(frozen['unit_M']);t=np.asarray(frozen['unit_t']);inv=np.linalg.inv(M);it=-inv@t
old=Image.open(R/'sources/F044_same_rigid_grip_torch_SOURCE.png').convert('RGBA')
old_at_TL=old.transform((1672,941),Image.Transform.AFFINE,(*inv[0],it[0],*inv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
old_at_TL.save(R/'comparison/F044_complete_unit_at_frozen_TL_REVIEW_ONLY.png')
new_at_TL=Image.open(R/'fixed_trial/F063_same_transform_near_arm_grip_COMPLETE_prop.png').convert('RGBA')
raw=Image.open(R/'sources/F063_local_repair_RAW_same_source.png').convert('RGBA')
# Original raw/full-grip and old full-unit crops are contextual source views,
# not additional edited candidates and not used to paint/repair the trial.
raw.crop((430,480,1270,835)).save(R/'comparison/F063_RAW_full_torch_and_grasp_context_1x.png')
old.crop((990,250,1220,690)).save(R/'comparison/F044_original_whole_unit_and_grasp_1x.png')
Image.open(R/'sources/F044_frozen_production_mother_REFERENCE_ONLY.png').crop((970,250,1240,700)).save(R/'comparison/F044_flat_mother_whole_torch_and_near_hand_context_1x.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14)
crop=(800,480,1290,720);cw,ch=490,240
oldmask=np.asarray(old_at_TL)[:,:,3]>=128;newmask=np.asarray(new_at_TL)[:,:,3]>=128
oldedge=oldmask&~binary_erosion(oldmask);newedge=newmask&~binary_erosion(newmask)
for tone,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 panels=[]
 for label,unit in [('044原完整灯/握手；整组s1,R+78.508°',old_at_TL),('063实际新灯/握手；沿用冻结共同M',new_at_TL)]:
  base=Image.new('RGBA',(1672,941),color);base.alpha_composite(unit);pane=base.crop(crop).convert('RGB');pane.save(R/f'comparison/{tone}_{label[:3]}_same_TL_native1x.png');panels.append((label,pane))
 outline=Image.new('RGBA',(1672,941),color);a=np.array(outline);a[oldedge]=[0,210,230,255];a[newedge]=[255,151,47,255];outline=Image.fromarray(a).crop(crop).convert('RGB')
 outline.save(R/f'comparison/{tone}_same_TL_outer_contours_native1x.png')
 # All three actual comparison panes pasted at exactly1native pixel per sheet pixel.
 sheet=Image.new('RGB',(1020,570),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,(label,pane) in enumerate(panels):
  x=10+j*510;sheet.paste(pane,(x,38));d.text((x,10),label,font=small,fill='#26343e')
 sheet.paste(outline,(10,320));d.text((10,290),'外轮廓含可见握手；青044 / 橙063；同T/L、1native px=1px',font=small,fill='#26343e')
 d.text((520,322),'固定比较，不是新候选',font=font,fill='#26343e')
 d.text((520,360),'轴长同376.001native；尾径044≈83±4',font=small,fill='#26343e')
 d.text((520,390),'063≈55.72±3.25native，约少33%',font=small,fill='#26343e')
 d.text((520,430),'手遮挡处没有补画隐藏轮廓。',font=small,fill='#26343e')
 d.text((520,460),'完整新臂/原图/试件另存；试件仍HOLD。',font=small,fill='#26343e')
 d.text((520,500),'旧044腕端历史技术边不作为新臂合格证。',font=small,fill='#26343e')
 sheet.save(R/f'comparison/{tone}_actual_same_TL_complete_prop_grip_and_contours_1x.png')
 # Show current entire trial without modifying any original composition or M.
 trial=Image.open(R/'fixed_trial/F063_single_group_026_backplate_TRIAL_HOLD.png').convert('RGBA');bg=Image.new('RGBA',trial.size,color);bg.alpha_composite(trial)
 bg.crop((620,500,1280,870)).resize((1320,740),Image.Resampling.NEAREST).convert('RGB').save(R/f'qa/current_fixed_complete_trial_connections_{tone}_2x.png')
assert np.allclose(np.linalg.svd(M,compute_uv=False),[1,1])
report={'status':'FIXED_REVIEW_BUNDLE_STOP_MICROADJUST_PENDING_ASTRA_DIRECTION','new_image_calls':0,'F069_unopened':True,'current_trial_sha256':sha(R/'fixed_trial/F063_single_group_026_backplate_TRIAL_HOLD.png'),'trial_geometry_modified':False,'new_registered_group_modified':False,'old_comparison_only':{'scale':1,'rotation_degrees':frozen['unit_R_degrees'],'M':frozen['unit_M'],'t':frozen['unit_t'],'whole_prop_and_grasp_transform_together':True,'not_adopted_into_new_trial':True},'new_existing_transform_unchanged':geo['single_similarity'],'common_T':frozen['T_target'],'common_L':frozen['L_target'],'common_axis_length_native':geo['frozen_axis_native'],'comparison_crop_native':list(crop),'comparison_sheet_native_px_per_px':1,'full_projected_tail_diameters':geo['full_tail_diameter_visible_projection'],'contour_semantics':'Actual alpha128 outer silhouette of complete visible unit, includes grip and arm where within crop. No invented outline behind the hand. Not physical3D calipers.','source_limits':['044 unit is the archived historicalb877 complete grasp/prop source; 104alpha128 flattened-motherRGBA differences previously documented, so not claimed bitwise equal to flat044 mother.','Original044 whole unit contains a historical technical wrist fringe/cut; shown honestly for review, not certified as new arm anatomy.','New063 common-M registration locks axis length but exposes approximately33percent tail diameter conflict, sleeve/body seams and253stable-skirt overlap; current complete trial remainsHOLD.'],'decision_reserved_for_Astra':['Keep complete original044 grasp/prop group and attach an actual new full arm, or approve a minimal complete grasp/prop shape repair. Neither is executed by this fixed package.']}
(R/'qa/fixed_comparison_geometry_and_limits.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'exact_snapshots':len(rows),'trial_sha256':report['current_trial_sha256'],'old_scale':1,'new_scale':geo['single_similarity']['scale'],'status':report['status']},ensure_ascii=False,indent=2))
