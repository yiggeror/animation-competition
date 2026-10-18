#!/usr/bin/env python3
"""Replay native patch and explicit mother lock; make technical QA only."""
from pathlib import Path
import base64,hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s09-seam-review-mpl')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse
ROOT=Path(__file__).resolve().parent;PRE=ROOT.parent;BASE=PRE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
args=json.loads((ROOT/'requests/call07_arguments.json').read_text())
assert args['prompt']==(ROOT/'requests/call07_prompt.txt').read_text().rstrip('\n')
ret=json.loads((ROOT/'requests/call07_raw_return.json').read_text())
raw=ROOT/'originals/d06_call07_raw.png'
assert raw.read_bytes()==base64.b64decode(ret['image_url'].split(',',1)[1])
source=PRE/'reference/d06_size_preposition_for_native_seam.png'
pre=Image.open(source).convert('RGBA');native=Image.open(raw).convert('RGBA')
assert native.size==pre.size==(1672,941)
mask=Image.open(ROOT/'masks/native_seam_and_vacated_background.png').convert('L')
vacated=np.array(Image.open(ROOT/'masks/vacated_old_upper_transparency.png'))>0
edit=Image.composite(native,pre,mask);ea=np.array(edit);pa=np.array(pre)
ea[vacated]=pa[vacated];edit=Image.fromarray(ea)
assert np.array_equal(ea[np.array(mask)==0],pa[np.array(mask)==0])
edit.save(ROOT/'candidates/d06_preposition_seam_locked.png')
mother_path=PRE/'candidates/d05_raw_locked.png';mother=Image.open(mother_path).convert('RGBA')
action=Image.open(ROOT/'masks/action_domain_final.png').convert('L')
candidate=Image.composite(edit,mother,action);ca=np.array(candidate);ma=np.array(mother);aa=np.array(action)
assert np.array_equal(ca[aa==0],ma[aa==0])
protected=np.array(Image.open(ROOT/'masks/protected_mother_head_neck_collar.png'))>0
assert np.array_equal(ca[protected],ma[protected])
# Whole visible hands, lamp and full rear cap retain source positions and original pixels.
for name,box in [('right_grip',(1028,377,1196,554)),('left_palm',(1015,700,1231,805)),
                 ('lamp_head',(1064,253,1205,374)),('complete_rear_cap',(1080,599,1190,674))]:
 x0,y0,x1,y1=box
 # Grip rectangle also contains the611 authorized red-barrel pixels; the actual skin is protected separately.
 expected=ea if name=='right_grip' else pa
 assert np.array_equal(ca[y0:y1,x0:x1],expected[y0:y1,x0:x1]),name
grip=np.array(Image.open(ROOT/'masks/protected_right_grip.png'))>0
assert np.array_equal(ea[grip],pa[grip])
actual_grip=np.array(Image.open(ROOT/'masks/protected_right_grip_actual.png'))>0
assert np.array_equal(ca[actual_grip],pa[actual_grip])
candidate.save(ROOT/'candidates/d06_raw_locked_pending_clothing.png')
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
reg=candidate.transform((1536,864),Image.Transform.AFFINE,tuple(lock['registration']['inverse_pillow_affine']),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
reg.save(ROOT/'candidates/d06_registered_pending_clothing.png')
reg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'qa/F031_1280x720_pending_clothing.png')
scale=lock['registration']['scale'];tr=np.array(lock['registration']['translation_xy'])
lamp=np.array([1135.,278.]);tail=np.array([1134.,654.]);axis=float(np.linalg.norm(tail-lamp))
gap=62.;lift=20/scale
states=[]
for f,dy,intent in [(31,0,'actual candidate, no contact'),(37,-lift,'technical anticipation target only, not generated'),(42,gap,'technical first contact target only, not generated')]:
 states.append({'frame':f,'status':intent,'prop_and_grip_translation_native':[0,dy],
  'lamp_axis_center_native':(lamp+[0,dy]).tolist(),'tail_axis_center_native':(tail+[0,dy]).tolist(),
  'lamp_axis_center_registered':((lamp+[0,dy])*scale+tr).tolist(),
  'tail_axis_center_registered':((tail+[0,dy])*scale+tr).tolist(),
  'tail_outer_bottom_native':660+dy,'palm_surface_native_approx':[1134,722],
  'outer_silhouette_gap_native_approx':gap-dy,
  'outer_silhouette_gap_registered_approx':(gap-dy)*scale,
  'palm_frozen':True,'axis_length_native':axis,'rear_cap_diameter_native_approx':83,
  'arm_limit':'Prop plus near grip is rigid; wrist target moves, elbow/forearm must be redrawn with complete chain and real sleeve continuity, not translated as one whole arm.'})
measure={'status':'SEAM_PATCH_ADOPTED_FULL_POSE_PENDING_ASTRA_AND_OCCLUDED_CLOTHING',
 'new_native_calls_this_round':1,'d06_native_calls_total':7,'pre_tap_calls_total':8,'all_S09_calls_total':12,
 'historical_prepared_request':'../requests/d06_call07_arguments.json was never executed; this round executed seam_repair/requests/call07_arguments.json only.',
 'raw_original_sha256':sha(raw),'native_size':[1672,941],'raw_return_byte_equal':True,
 'source_preposition_sha256':sha(source),'source_call05_sha256':sha(PRE/'originals/d06_call05_raw.png'),
 'locked_mother_sha256':sha(mother_path),'native_adopted_changed_pixels':int(np.any(ea!=pa,axis=2).sum()),
 'native_patch_outside_mask_changed_pixels':0,'body_outside_action_domain_changed_pixels':0,
 'protected_mother_head_neck_collar_changed_pixels':0,'whole_hands_lamp_cap_source_byte_equal':True,
 'measurements_manual_native':{'complete_axis_center_to_center':axis,'axis_uncertainty':8,
  'lamp_diameter':128,'lamp_diameter_uncertainty':5,'complete_rear_cap_diameter':83,'rear_cap_uncertainty':4,
  'tail_outer_bottom_y':660,'receiver_upper_face_y_on_axis_approx':722,'visible_gap':gap,'visible_gap_range':[60,65]},
 'measurements_registered':{'complete_axis':axis*scale,'complete_rear_cap_diameter':83*scale,'visible_gap':gap*scale},
 'comparison_to_locked_mother':{'mother_axis_registered_approx':240.2052476443473,
   'corrected_axis_registered_approx':axis*scale,'difference_percent':100*(axis*scale/240.2052476443473-1),
   'full_mother_cap_diameter':'unobservable due to right-hand occlusion; do not use visible44 as full diameter'},
 'explicit_domains':['masks/native_seam_and_vacated_background.png','masks/action_domain_final.png','masks/protected_mother_head_neck_collar.png'],
 'remaining_blocker':'Old near arm originally occludes torso/waist/skirt in locked mother. Source05 has fill pixels but clothing registration differs; cut white dots/fold joins remain in explicit action domain. No clean locked mother pixels exist at those original occlusions. This full pose is not locked or a next-pose source.',
 'not_generated':[37,42],'withdrawn_constraints':['44native full cap diameter','old2.29registered near-hand envelope'],
 'technical_contact_states':states}
(ROOT/'qa/measurements_and_lock_checks.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2)+'\n')
(ROOT/'reference/F037_F042_actual_size_contact_targets.json').write_text(json.dumps({'status':'TECHNICAL_ONLY_PENDING_F031_FULL_APPROVAL','registration':lock['registration'],'states':states},ensure_ascii=False,indent=2)+'\n')

fig,axs=plt.subplots(1,3,figsize=(17,8))
for ax,im,title in zip(axs,[pre,edit,candidate],['67px真实预摆','唯一call07局部采用','锁母头身恢复候选／衣片待审']):
 ax.imshow(im);ax.set_facecolor('#e1e6ea');ax.set_xlim(520,1290);ax.set_ylim(930,0);ax.set_title(title);ax.axis('off')
fig.tight_layout();fig.savefig(ROOT/'qa/three_stage_comparison.png',dpi=130);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(16,7))
axs[0].imshow(edit);axs[0].set_xlim(1035,1240);axs[0].set_ylim(810,245);axs[0].set_facecolor('#e1e6ea');axs[0].set_title('031真实道具／掌面')
axs[0].plot([1134,1134],[660,722],color='#c34156',lw=2);axs[0].annotate('约62raw净空',(1145,691),fontsize=10)
for ax,s in zip(axs[1:],states[1:]):
 dy=s['prop_and_grip_translation_native'][1];ax.set_xlim(1020,1245);ax.set_ylim(820,205);ax.set_aspect('equal');ax.axhline(722,c='#499b83',lw=2)
 ax.plot([1135,1134],[278+dy,654+dy],c='#a53b4a',lw=8);ax.add_patch(Ellipse((1134,651+dy),83,18,facecolor='#d0d4d8',edgecolor='#535b65'))
 ax.add_patch(Ellipse((1135,278+dy),128,30,facecolor='#c1c7cd',edgecolor='#535b65'))
 ax.plot([1090,1134,1170],[733,722,738],c='#499b83',lw=7)
 ax.plot([1134,1134],[660+dy,722],c='#c34156',lw=2,ls='--')
 ax.text(1025,780,f"间隙约{s['outer_silhouette_gap_native_approx']:.1f}raw／{s['outer_silhouette_gap_registered_approx']:.1f}注册px",fontsize=10)
 ax.set_title(f"F{s['frame']:03}施工目标／尚未画")
fig.suptitle('按修后完整轴／尾盖重算：灰色是技术符号，不能进片；031通过才037',fontsize=15)
fig.tight_layout();fig.savefig(ROOT/'reference/F037_F042_actual_size_contact_targets.png',dpi=140);plt.close(fig)
for name,im,maskpath in [('native',pre,'native_seam_and_vacated_background.png'),('action',candidate,'action_domain_final.png')]:
 bg=Image.new('RGBA',pre.size,(224,230,235,255));bg.alpha_composite(im);ov=Image.new('RGBA',pre.size,(201,45,113,0));ov.putalpha(Image.open(ROOT/'masks'/maskpath).point(lambda v:round(v*.3)));bg.alpha_composite(ov);bg.convert('RGB').save(ROOT/f'qa/{name}_final_domain_overlay.png')
print(json.dumps({k:measure[k] for k in ['native_adopted_changed_pixels','native_patch_outside_mask_changed_pixels','body_outside_action_domain_changed_pixels','protected_mother_head_neck_collar_changed_pixels','whole_hands_lamp_cap_source_byte_equal']},ensure_ascii=False))
