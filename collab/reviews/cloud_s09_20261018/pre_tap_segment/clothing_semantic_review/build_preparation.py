#!/usr/bin/env python3
"""Semantic clothing-only masks and same-raw continuous fabric candidate; no generation."""
from pathlib import Path
import hashlib,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s09-semantic-clothing-mpl')
import numpy as np
from scipy.ndimage import label,binary_dilation
from PIL import Image,ImageDraw,ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parent;PRE=ROOT.parent;BASE=PRE.parent
for d in ['crops','masks','candidates','qa','reference']:(ROOT/d).mkdir(exist_ok=True)
current_path=PRE/'seam_repair/candidates/d06_raw_locked_pending_clothing.png'
donor_path=PRE/'originals/d06_call05_raw.png'
current=Image.open(current_path).convert('RGBA');donor=Image.open(donor_path).convert('RGBA')
a=np.array(current);b=np.array(donor);size=current.size;yy,xx=np.indices(a.shape[:2])
assert current.size==donor.size==(1672,941)
def polygon(points):
 m=Image.new('L',size);ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
zones={
 'chest_broken_white_dot':polygon([(806,603),(848,603),(857,622),(850,643),(816,643),(805,632)]),
 'old_arm_vacated_torso_and_waist':polygon([(668,694),(715,702),(780,754),(823,776),(883,737),(930,695),(944,743),(935,791),(963,815),(665,818),(645,793)]),
 'continuous_skirt_folds':polygon([(653,781),(684,781),(736,785),(788,788),(840,789),(895,786),(936,781),(961,814),(1010,879),(1040,940),(540,940),(573,897),(603,848),(628,814)])}
# Complete actual skin chains, including the far receiving palm, not a two-strip skirt mask.
hsv=np.array(current.convert('RGB').convert('HSV'))
skin=(hsv[:,:,0]>=10)&(hsv[:,:,0]<=28)&(hsv[:,:,1]>=45)&(hsv[:,:,1]<=175)&(hsv[:,:,2]>155)&(a[:,:,3]>64)&((yy>570)|((xx>1000)&(yy>380)))
lab,n=label(skin);counts=np.bincount(lab.ravel());ids=np.where(counts>1200)[0];ids=ids[ids!=0]
arms_skin=np.isin(lab,ids);arms_skin=binary_dilation(arms_skin,iterations=6)
# Conservative full sleeve/cuff protection keeps anatomy, attached cloth ruffles and arm silhouettes fixed.
near_sleeve=polygon([(589,497),(638,483),(689,500),(719,552),(720,601),(752,605),(779,623),(781,646),(749,671),(698,716),(655,718),(624,696),(589,678),(575,642),(578,584)])
far_sleeve=polygon([(928,503),(978,529),(1019,569),(1026,628),(1028,658),(1016,689),(973,695),(947,672),(940,625),(926,577)])
# The far palm's curled fingers have separated skin islands; protect the WHOLE actual palm rectangle.
complete_left_palm=(xx>=1010)&(xx<=1235)&(yy>=695)&(yy<=815)
arms=arms_skin|near_sleeve|far_sleeve|complete_left_palm
head_neck_collar=yy<=590  # Includes a conservative shirt collar margin; chest repair is below603.
torch=polygon([(1035,160),(1235,160),(1235,690),(1035,690)])
# Preserve all true visible alpha boundaries; do not treat the off-shot canvas crop as a drawn contour.
fg=a[:,:,3]>128;outer=fg&binary_dilation(~fg,iterations=7)
hard=head_neck_collar|arms|torch|outer|(~fg)
opaque=(a[:,:,3]>=245)&(b[:,:,3]>=245)
combined=np.zeros(a.shape[:2],bool)
for name,z in zones.items():
 eligible=z&~hard&opaque;zones[name]=eligible;combined|=eligible
 assert eligible.any(),name
 Image.fromarray((eligible*255).astype(np.uint8)).save(ROOT/f'masks/{name}.png')
hard_im=Image.fromarray((hard*255).astype(np.uint8));hard_im.save(ROOT/'masks/hard_protection_all.png')
Image.fromarray((arms*255).astype(np.uint8)).save(ROOT/'masks/complete_arms_sleeves_cuffs.png')
Image.fromarray((outer*255).astype(np.uint8)).save(ROOT/'masks/visible_outer_contour_band.png')
mask=Image.fromarray((combined*255).astype(np.uint8));mask.save(ROOT/'masks/semantic_clothing_union.png')
assert not (combined&hard).any()
# No rescale, no warp, no painted texture: same coordinates from continuous source05 fabric.
candidate=Image.composite(donor,current,mask);c=np.array(candidate)
# Native foreground alpha is mostly253/254. Copy donor RGB, retain the locked candidate's exact alpha.
c[:,:,3]=a[:,:,3];candidate=Image.fromarray(c)
assert np.array_equal(c[~combined],a[~combined])
assert np.array_equal(c[hard],a[hard])
assert np.array_equal(c[:,:,3],a[:,:,3])
candidate.save(ROOT/'candidates/same_call05_continuous_cloth_pending_review.png')
crop_boxes={'chest_broken_white_dot':[790,595,870,651],
 'old_arm_vacated_torso_and_waist':[645,688,965,821],
 'continuous_skirt_folds':[565,780,1035,941],
 'all_semantic_clothing':[565,590,1035,941]}
for name,box in crop_boxes.items():
 for kind,im in [('current',current),('donor_call05',donor),('candidate',candidate),('edit_mask',mask),('hard_protection',hard_im)]:im.crop(box).save(ROOT/f'crops/{name}_{kind}.png')
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
reg=candidate.transform((1536,864),Image.Transform.AFFINE,tuple(lock['registration']['inverse_pillow_affine']),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
reg.save(ROOT/'candidates/same_call05_registered_pending_review.png')
reg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'qa/same_call05_1280x720_pending_review.png')
bg=Image.new('RGBA',size,(225,230,234,255));bg.alpha_composite(current)
ov=Image.new('RGBA',size,(212,38,112,0));ov.putalpha(mask.point(lambda v:round(v*.45)));bg.alpha_composite(ov);bg.convert('RGB').save(ROOT/'qa/full_semantic_domain_overlay.png')
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
fig,axs=plt.subplots(3,3,figsize=(14,13))
for row,(name,box) in enumerate(list(crop_boxes.items())[:3]):
 for col,(title,im) in enumerate([('当前031',current),('call05同位连续衣片',donor),('纯像素接回候选／待审',candidate)]):
  ax=axs[row,col];ax.imshow(im);ax.set_facecolor('#e1e6ea');ax.set_xlim(box[0],box[2]);ax.set_ylim(box[3],box[1]);ax.set_title(f'{title}\n{name}',fontsize=11);ax.axis('off')
fig.tight_layout();fig.savefig(ROOT/'qa/three_semantic_regions_comparison.png',dpi=135);plt.close(fig)
checks={'status':'SEMANTIC_CROP_MASK_AND_SAME_RAW_CLOTH_CANDIDATE_PENDING_ASTRA',
 'new_native_calls':0,'all_S09_native_calls_unchanged':12,'F031_calls_unchanged':7,'F037_calls':0,'F042_calls':0,
 'source_current':{'path':str(current_path.relative_to(BASE)),'sha256':hashlib.sha256(current_path.read_bytes()).hexdigest(),'locked_by_Astra':'hands,complete prop,size and air gap only; full pose not locked'},
 'continuous_clothing_donor':{'path':str(donor_path.relative_to(BASE)),'sha256':hashlib.sha256(donor_path.read_bytes()).hexdigest(),'translation':[0,0],'scale':1,'warp':False,'code_drawn_pixels':False},
 'semantic_crop_boxes_native_xyxy':crop_boxes,'semantic_mask_pixels':{k:int(v.sum()) for k,v in zones.items()},
 'hard_protection':'head/neck/collar conservative through590; complete actual skin chains+dilated outlines; complete sleeves/cuffs; prop; visible outer alpha contour7px; transparent background',
 'hard_protected_pixels':int(hard.sum()),'mask_hard_protection_overlap':int((combined&hard).sum()),
 'candidate_outside_semantic_mask_changes':int(np.any(c[~combined]!=a[~combined],axis=1).sum()),
 'candidate_hard_domain_changes':int(np.any(c[hard]!=a[hard],axis=1).sum()),
 'candidate_alpha_changes':int((c[:,:,3]!=a[:,:,3]).sum()),
 'complete_left_palm_box_native':[1010,695,1235,815],
 'complete_left_palm_hard_coverage':bool(hard[complete_left_palm].all()),
 'candidate_native_pixels_taken':int(np.any(c!=a,axis=2).sum()),
 'no_donor_claim_outside_mask':'Source05 body/head pixels are never used outside the semantic fabric union; full arm/prop/head/outer silhouette remains current locked source.',
 'remaining_review':'Inspect full white dots, uninterrupted waist/skirt folds and donor joins at hard boundaries. This is a review candidate, not accepted artwork; no new native clothing repair until semantic masks are reviewed.',
 'optional_next_action_if_source_join_fails':'After Astra review, one local clothing-only connection request inside approved semantic crop/mask; preserve all hard regions. No whole person or prop request.'}
(ROOT/'qa/coverage_and_lock_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:checks[k] for k in ['new_native_calls','semantic_mask_pixels','mask_hard_protection_overlap','candidate_outside_semantic_mask_changes','candidate_hard_domain_changes','candidate_alpha_changes','candidate_native_pixels_taken']},ensure_ascii=False))
