#!/usr/bin/env python3
"""Reproduce diagnostic plates only. No anatomy warps or production art output."""
from pathlib import Path
import base64, hashlib, json, os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/s07-f057-review-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
QA = ROOT/'qa'
QA.mkdir(exist_ok=True)
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
raw = ROOT/'originals/F057_call01_raw.png'
im = Image.open(raw)
result = json.loads((ROOT/'requests/F057_call01_raw_return.json').read_text())
assert raw.read_bytes() == base64.b64decode(result['image_url'].split(',',1)[1])
args = json.loads((ROOT/'requests/F057_call01_arguments.json').read_text())
assert args['prompt'] == (ROOT/'requests/F057_call01_prompt.txt').read_text().rstrip('\n')
assert im.size == (1672,941) and im.mode == 'RGBA'
guide = ROOT/'reference/F057_world_reference_at_call01.png'
assert guide.read_bytes() == (BASE/'arm_swing_v2/F057_world_reference.png').read_bytes()
ref = Image.open(BASE/'sources/grandma_turnaround_current03_draft.png')
crop = Image.open(ROOT/'reference/grandma_true_right_profile.png')
assert ref.crop((910,10,1125,758)).tobytes() == crop.tobytes()
state = json.loads((BASE/'arm_swing_v2/arm_swing_states.json').read_text())['states'][0]

# Human estimates on the native PNG, not measured anatomical/3D joints.
# Cloud review independently estimated head190±5, ankle span289±10.
marks = {'head_top_y':14, 'chin_y':204, 'head_center_x':832,
         'near_ankle':[967,852], 'far_ankle':[678,848],
         'near_wrist':[676,536], 'far_jade_wrist':[988,475],
         'near_sole_y':915, 'far_sole_y':911}
head_height = marks['chin_y']-marks['head_top_y']
scale = 75.1/head_height
tx = state['head_center'][0]-scale*marks['head_center_x']
ty = 775-scale*(marks['near_sole_y']+marks['far_sole_y'])/2
world = lambda p: [scale*p[0]+tx,scale*p[1]+ty]
measured = {k:world(marks[k]) for k in ['near_ankle','far_ankle','near_wrist','far_jade_wrist']}
span = (marks['near_ankle'][0]-marks['far_ankle'][0])*scale
provenance = {
 'status':'AUTHOR_AND_READ_ONLY_CLOUD_REJECTED_STEP_WIDTH_PENDING_ASTRA',
 'native_calls':1,'native_outputs':1,'accepted_drawings':0,
 'tool':'image_gen.imagegen native tool; no external API/service',
 'raw_original':{'path':str(raw.relative_to(BASE)), 'sha256':sha(raw), 'size':list(im.size),
   'mode':im.mode, 'raw_return_base64_byte_equal':True,
   'host_original_path':'/workspace/generated_images/exec-0c805013-8e40-4506-b078-53f72d880842.png',
   'host_byte_equality_verified_on_extraction':True},
 'inputs':[
   {'role':'technical construction guide; not character art','path':str(guide.relative_to(BASE)),
    'sha256':sha(guide),'actual_call_path':args['referenced_image_paths'][0]},
   {'role':'true current03 right profile; never mirrored','path':'F057_first_image/reference/grandma_true_right_profile.png',
    'sha256':sha(ROOT/'reference/grandma_true_right_profile.png'),
    'crop_xyxy':[910,10,1125,758], 'source':'sources/grandma_turnaround_current03_draft.png'},
   {'role':'full identity turnaround','path':'sources/grandma_turnaround_current03_draft.png',
    'sha256':sha(BASE/'sources/grandma_turnaround_current03_draft.png'),
    'source_commit':'60159846257c803263b4eab675ba35487fff12ce'}],
 'manual_estimates_native':marks,
 'uncertainty':'Head190±5native and horizontal ankle span289±10native; wrist and ankle centers are approximate visible landmarks, not recovered skeleton.',
 'diagnostic_uniform_transform_only':{'s':scale,'tx':tx,'ty':ty,
    'purpose':'QA plate, not production registration. Match head size, head x, mean sole floor; no local warp or bone replacement.',
    'world_size':[1672,941]},
 'diagnostic_landmarks_world':measured,
 'head_normalized_horizontal_ankle_span_world':span,
 'target_ankle_span_world':64,
 'span_difference_world':span-64,
 'failure':'About114±7world span versus64. Uniform scale to fit64 would make head about42world instead of75.1. No accepted mother pose; do not expand other10.',
 'actual_visual_findings':[
   'Right-facing identity and right bare wrist/left jade ownership readable.',
   'Near right foot forward, far left foot behind; neither shoe is visibly cropped.',
   'Both sleeve-arm-wrist-palm chains visually continuous; no definite disconnection or body penetration found. Occluded digits cannot be counted completely.',
   'Far left wrist swings farther forward/higher than reference; uniform QA plate shows residual. Do not turn this into an unsupported topology failure.',
   'Full canvas/world position ignored by generator. Character occupies nearly full941height; one uniform registration was tested only diagnostically.',
   'G037 standing-source scale verification pending; head75.1 remains construction target.'],
 'preservation':'Original PNG, full prompt/arguments/raw return kept unchanged. No pixel cleanup, masks, art edits, scene render or additional native call.',
 'remaining_permission':'Only first057 had been authorized; other10 remain unapproved. S09 separately paused.'}
(QA/'review.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')

fig,axs = plt.subplots(1,3,figsize=(17,7))
for ax,lim,title in zip(axs,[(680,950,240,0),(590,1090,650,300),(580,1110,940,780)],
                       ['实际头部包络／人工估读','双腕与袖臂连续性','裸踝与两鞋底／原图坐标']):
 ax.set_facecolor('#eeeeee');ax.imshow(im);ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.grid(alpha=.3);ax.tick_params(labelsize=8);ax.set_title(title)
fig.tight_layout();fig.savefig(QA/'raw_coordinate_inspection.png',dpi=130);plt.close(fig)

fig,axs = plt.subplots(1,2,figsize=(14,9))
axs[0].imshow(im);axs[0].set_facecolor('#eeeeee');axs[0].set_xlim(560,1120);axs[0].set_ylim(940,0)
axs[0].set_title('原生首图；完整原件未改像素')
for k in ['near_ankle','far_ankle','near_wrist','far_jade_wrist']:
 axs[0].scatter(*marks[k],c='#b74553',s=25);axs[0].annotate(k,marks[k],xytext=(4,-12),textcoords='offset points',fontsize=8)
for y in [marks['head_top_y'],marks['chin_y']]:axs[0].axhline(y,color='#ae5c69',lw=.8)
ax=axs[1]
ax.imshow(im,extent=(tx,tx+1672*scale,ty+941*scale,ty),interpolation='bilinear')
ax.axhline(775,color='#666666',lw=1)
for a,b in [('shoulder','near_elbow'),('near_elbow','near_wrist'),('far_shoulder','far_elbow'),('far_elbow','far_wrist'),('hip','near_knee'),('near_knee','near_ankle'),('far_hip','far_knee'),('far_knee','far_ankle')]:
 ax.plot([state[a][0],state[b][0]],[state[a][1],state[b][1]],c='#278ca0',lw=1.5,ls='--')
for k in ['near_ankle','far_ankle','near_wrist','far_wrist']:
 ax.scatter(*state[k],facecolors='none',edgecolors='#08778c',s=80,lw=1.5)
for k,p in measured.items():ax.scatter(*p,c='#b74553',s=24)
ax.annotate('参考踝距64',(865,798),fontsize=11,color='#08778c')
ax.annotate(f'原图按头归一约{span:.1f}；过宽',(850,820),fontsize=11,color='#a03543')
ax.annotate('青虚线／空圈=施工参考\n红点=原图人工估读\n仅整体等比／不作生产注册',(790,380),fontsize=11)
ax.set_xlim(780,1040);ax.set_ylim(845,355);ax.set_title('诊断叠图：头75.1＋平均鞋底775')
fig.suptitle('S07 F057 首图未过步幅门；其余10张未生成',fontsize=17)
fig.tight_layout();fig.savefig(QA/'uniform_scale_comparison.png',dpi=140);plt.close(fig)
print(json.dumps({'raw_byte_preserved':True,'prompt_match':True,'input_guide_exact':True,'head_normalized_span_world':span,'target':64,'status':'REJECTED_PENDING_ASTRA'},ensure_ascii=False))
