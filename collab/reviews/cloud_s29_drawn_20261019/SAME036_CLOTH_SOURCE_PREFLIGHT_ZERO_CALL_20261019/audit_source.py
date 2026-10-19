from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019';S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019';T=B/'F036_F042_F048_SCENE_TRANSITIONS_ZERO_CALL_20261019';W,H=1024,1536
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def stats(m):
 y,x=np.where(m);return {'pixels':int(m.sum()),'bbox_inclusive':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())]}
backp=S/'layers/ONE_M_ACTUAL_COTTON_BACK.png';frontp=S/'layers/ONE_M_ACTUAL_SOFT_LIP_FRONT.png';oldp=B/'F030_REPAIR_NATIVE_call01_20261019/originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png'
back,front,old=rgba(backp),rgba(frontp),rgba(oldp)
generated=np.array(Image.open(P/'masks/GENERATED_PROP_CONTEXT_REPLACEMENT_ONLY.png').convert('L'))>0
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
props=rgba(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')[:,:,3]>0
# Exact audited cloth source domain from the existing030->036 preparation.
domain=poly([[510,693],[590,718],[642,700],[695,661],[710,649],[734,658],[766,682],[811,711],[900,750],[960,807],[1001,867],[1005,903],[958,1025],[903,1067],[850,1012],[780,1018],[688,999],[623,966],[582,961],[530,990],[451,967],[350,932],[272,900],[257,877],[303,840],[349,806],[403,772],[461,741]])
native=(back[:,:,3]>=250)|(front[:,:,3]>=250)
cleanbase=domain&~generated&~near&(old[:,:,3]>=250)
# A tiled technical fill/translated rectangle is not original-coordinate cotton.
needed=nd.binary_erosion(domain,iterations=3)&~near&~props
missing=needed&generated&~native
rgb=old[:,:,:3].astype(float)
gold=(rgb[:,:,0]>rgb[:,:,2]*1.25)&(rgb[:,:,1]>rgb[:,:,2]*1.12)&(rgb[:,:,0]>90)
green=(rgb[:,:,1]>rgb[:,:,0]*1.10)&(rgb[:,:,1]>rgb[:,:,2]*1.10)&(rgb[:,:,1]>45)
confirmed=missing&(gold|green) # actual non-cotton raw030 pixels, not just a broad exclusion polygon
regions={}
for name,box in [('crane_upper_face',(400,720,870,825)),('crane_stem_and_middle_face',(550,790,700,900)),('turtle_near_lower_face',(260,815,560,925)),('rod_corridors_and_lower_drape',(450,850,985,1010))]:
 x0,y0,x1,y1=box;m=np.zeros((H,W),bool);m[y0:y1,x0:x1]=True;regions[name]={'window_exclusive':box,'excluded_material_gap':stats(missing&m),'confirmed_raw_non_cotton':stats(confirmed&m)}
available=np.zeros_like(old);available[cleanbase]=old[cleanbase]
available=np.array(Image.alpha_composite(Image.fromarray(available),Image.fromarray(back)));available=np.array(Image.alpha_composite(Image.fromarray(available),Image.fromarray(front)))
Image.fromarray(available).save(R/'NATIVE_SOURCE_CANDIDATE_COVERAGE_NOT_COMPLETE.png')
Image.fromarray(missing.astype('uint8')*255).save(R/'UNCOVERED_EXCLUDED_SOURCE_OUTSIDE_TRUE_PROPS.png')
Image.fromarray(confirmed.astype('uint8')*255).save(R/'CONFIRMED_RAW_NON_COTTON_OUTSIDE_TRUE_PROPS.png')
lockedp=S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png';locked=rgba(lockedp)
highlight=locked.copy();highlight[missing,:3]=(245,147,170);highlight[missing,3]=255;highlight[confirmed,:3]=(218,20,62)
def gray(a):
 g=Image.new('RGBA',(W,H),(236,239,242,255));g.alpha_composite(Image.fromarray(a));return g.convert('RGB')
crop=(240,625,1024,1100);cw,ch=784,475
sheet=Image.new('RGB',(cw*3,(ch+30)*2),(236,239,242));draw=ImageDraw.Draw(sheet)
states=[(36,lockedp),(42,T/'F042_FRONT_LIP_OVER_OUTER_FEATHER_RGBA.png'),(48,T/'F048_FRONT_LIP_OVER_OUTER_FEATHER_RGBA.png')]
for i,(f,p) in enumerate(states):sheet.paste(gray(rgba(p)).crop(crop),(cw*i,30));draw.text((cw*i+8,8),f'LOCKED F{f:03d} | 1:1 pixels | NO NEW MAPPING',fill='black')
for i,(name,a) in enumerate([('036 source candidate coverage; not a clean donor',available),('Pink: excluded material gap; red: raw non-cotton',highlight),('036 BACK + FRONT only; no technical backing',np.array(Image.alpha_composite(Image.fromarray(back),Image.fromarray(front))))]):
 y=ch+30;sheet.paste(gray(a).crop(crop),(cw*i,y+30));draw.text((cw*i+8,y+8),name,fill='black')
sheet.save(R/'LOCKED_STATES_AND_036_CLEAN_SOURCE_GAPS_1TO1.png')
files=[lockedp,backp,frontp,oldp,P/'layers/ACTUAL030_CLOTH_CONTEXT_BASE_TECHNICAL_ONLY.png',P/'masks/GENERATED_PROP_CONTEXT_REPLACEMENT_ONLY.png',S/'layers/LOCKED030_CONTINUOUS_REAL_COTTON_UNDERLAY.png']
oldreports={v['frame']:v for v in json.loads((B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL/geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']}
points={'C1':{'native':[499,747],'source':'existing common030 near-hand/neck3 contact; frozen, not a new anatomical measurement'},'far_pinch036':{'native':json.loads((S/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json').read_text())['mapped_anchors'][2],'source':'locked036 geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json mapped_anchors[2]'}}
for f in [42,48]:points[f'far_pinch{f:03d}']={'native':oldreports[f]['mapped_anchors'][2],'source':'8c fixed one-group mapped_anchors[2]; manual read uncertainty about3px'}
for name,region in regions.items():
 x0,y0,x1,y1=region['window_exclusive'];cy,cx=np.where(confirmed[y0:y1,x0:x1]);cx=cx+x0;cy=cy+y0
 if len(cx):
  k=np.argmin((cx-(x0+x1)/2)**2+(cy-(y0+y1)/2)**2);x,y=int(cx[k]),int(cy[k]);region['actual_non_cotton_source_example']={'xy':[x,y],'raw030_RGBA':old[y,x].tolist(),'BACK_alpha':int(back[y,x,3]),'FRONT_alpha':int(front[y,x,3]),'true_prop_alpha':int(props[y,x]),'locked036_flat_RGBA':locked[y,x].tolist()}
result={'status':'HOLD_SOURCE_INSUFFICIENT_BEFORE_ANY_DEFORMATION','new_generation_calls':0,'new_mapping_candidates':0,'actual_back_and_front_layers_opened_by_root_and_existing_helper':True,'source_candidate_coverage':'Original-coordinate raw030 outside technical replacement mask, plus locked036 BACK/FRONT; excludes mirror tile and translated rectangle. Candidate layers retain a few non-cotton edge pixels; this is an upper coverage audit, not a clean donor.','missing_outside_true_props_and_near_hand_conservative':stats(missing),'confirmed_raw_non_cotton_no036_coverage':stats(confirmed),'regions':regions,'two_contact_points':points,'locked_states_unchanged_SHA256':[{'state':f,'path':str(p.relative_to(B)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for f,p in states],'source_SHA256':[{ 'path':str(p.relative_to(B)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'forbidden_existing_substrates':{'mirror_tile':{'raw030_crop':[540,813,607,860],'destination':'GENERATED_PROP_CONTEXT_REPLACEMENT_ONLY mask, mirrored modulo tile'},'rectangle':{'raw030_crop':[650,700,735,738],'destination':[790,792,875,830]}},'limitation':'Broad exclusion-mask gap counts are conservative, not exact intrinsic source-occlusion area. Red subset confirms actual raw gold/green non-cotton material outside fixed true props with no opaque036 cloth layer coverage. No mesh or pattern replacement was attempted.'}
(R/'SOURCE_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'missing':result['missing_outside_true_props_and_near_hand_conservative'],'confirmed':result['confirmed_raw_non_cotton_no036_coverage'],'regions':regions},indent=2))
