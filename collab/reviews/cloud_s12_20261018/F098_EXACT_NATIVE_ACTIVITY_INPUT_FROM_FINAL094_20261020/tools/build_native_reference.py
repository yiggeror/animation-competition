"""Move real final094 source groups; small joining guides are reference only.
No TPS, garment RGB threshold, code person, or production-pixel adoption.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json
from scipy.ndimage import binary_dilation,binary_fill_holes,label
from scipy.ndimage import map_coordinates
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F094_LOCAL_ARMS_KNEES_actual_call01_20261019'
g=json.loads((O/'geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text());src=Image.open(M/'candidate/F094.png').convert('RGBA');B=np.array(src);Y,X=np.mgrid[:1536,:1024]
def polygon(points):
 m=Image.new('L',src.size);ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def part(mask):
 a=B.copy();a[~mask]=0;return Image.fromarray(a)
def warp(im,m):
 inv=np.linalg.inv(np.vstack([np.asarray(m),[0,0,1]]))[:2];return im.transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC)
def at(m,p):return np.asarray(m)@np.r_[p,1.]
def softpart(mask,weight):
 a=B.copy();a[~mask]=0;a[:,:,3]=np.uint8(np.rint(a[:,:,3]*weight));a[a[:,:,3]==0]=0;return Image.fromarray(a)
fixed=np.array(Image.open(R/'F094_LOCAL_REPAIR_INPUT_FROM_BODY_ONLY_DIAGNOSTIC_20261019/masks/HARD_ACTUAL_POSITIVE_SHINS_AND_SHOE_AIR.png').convert('L'))>0
fixed|=Y>=1320
UT=g['whole_torso_head_rigid_matrix'];TH=g['thigh_rigid_matrix']
# Whole actual garments, including every white flower/gray fold; no RGB classes.
shirt=polygon([(330,0),(770,0),(770,385),(710,405),(706,438),(704,477),(719,510),(715,548),(697,576),(682,606),(668,639),(640,674),(643,721),(657,764),(670,812),(681,859),(691,902),(684,924),(661,916),(642,884),(596,864),(550,842),(507,820),(481,805),(474,760),(443,798),(409,783),(375,774),(351,761),(379,717),(409,677),(443,639),(456,588),(451,541),(455,479),(465,420),(478,378),(493,345),(382,345)])
Rmask=polygon([(482,398),(540,398),(590,415),(615,453),(622,500),(632,544),(616,560),(635,595),(649,630),(675,655),(731,694),(786,736),(820,758),(850,766),(879,761),(903,756),(913,740),(927,736),(944,746),(952,759),(951,779),(940,794),(924,807),(882,826),(849,826),(812,816),(765,792),(704,757),(653,726),(608,699),(581,669),(557,630),(534,591),(511,602),(473,573),(457,522),(457,464),(470,419)])
Lmask=polygon([(650,662),(655,639),(670,609),(692,587),(716,577),(752,556),(778,546),(792,538),(808,537),(824,544),(840,555),(865,557),(890,560),(906,566),(918,585),(921,611),(914,633),(900,646),(882,645),(863,633),(843,619),(819,609),(803,606),(787,598),(742,620),(700,644),(669,659)])
collar=polygon([(490,319),(620,337),(650,379),(650,428),(609,458),(572,425),(525,402),(487,380)])
# Remove both old competing arm silhouettes. Independent source masks may overlap.
torso=shirt&~((Rmask|Lmask)&(Y>570)&~collar)&~fixed
pants=(Y>735)&(X<760)&~shirt&~Rmask&~Lmask&~fixed
out=Image.new('RGBA',src.size)
# Reuse the actual rounded knees and upper-shin folds at their qualified support.
# Moving upper thighs blend into that SAME real source across a narrow fold band.
# Continuous actual-cloth reference: rigid hip / rigid thigh / existing knee,
# with narrow smooth transitions between these three groups. This is a reference
# material remap only, never production art; it creates no new navy shape.
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
I=np.array([[1.,0.,0.],[0.,1.,0.]])
t1=smooth((np.arange(1536)-890)/110);t2=smooth((np.arange(1536)-980)/90)
mat=(1-t1[:,None,None])*np.array(UT)+t1[:,None,None]*np.array(TH)
mat=(1-t2[:,None,None])*mat+t2[:,None,None]*I
ms=np.concatenate([mat,np.tile([[[0.,0.,1.]]],(1536,1,1))],axis=1);inv=np.linalg.inv(ms)[:,:2]
sx=inv[:,0,0,None]*X+inv[:,0,1,None]*Y+inv[:,0,2,None]
sy=inv[:,1,0,None]*X+inv[:,1,1,None]*Y+inv[:,1,2,None]
P=np.array(part(pants)).astype(float);aa=P[:,:,3]/255.;prem=P[:,:,:3]*aa[:,:,None]
alpha=np.clip(map_coordinates(aa,[sy,sx],order=1,mode='constant'),0,1)
rgb=np.stack([map_coordinates(prem[:,:,c],[sy,sx],order=1,mode='constant') for c in range(3)],axis=2)
rgb=np.divide(rgb,alpha[:,:,None],out=np.zeros_like(rgb),where=alpha[:,:,None]>0)
cl=np.dstack([np.clip(np.rint(rgb),0,255),np.rint(alpha*255)]).astype(np.uint8)
out.alpha_composite(Image.fromarray(cl))
out.alpha_composite(part((Y>=1070)&~fixed))
# The old knee silhouette is an actual good rounded source, never a navy plate.
out.alpha_composite(warp(part(torso),UT))
guide=Image.new('RGBA',src.size);d=ImageDraw.Draw(guide)
pieces={};guide_records=[]
for role,mask in [('L',Lmask),('R',Rmask)]:
 a=g['arms'][role];s,e,w,c=[np.array(a['source_final094'][k]) for k in ['shoulder','elbow','wrist','true_grip']]
 v=w-e;along=((X-e[0])*v[0]+(Y-e[1])*v[1])/np.linalg.norm(v)
 if role=='R':hand=mask&(X>=891)&(Y>=725)&(Y<=835)
 else:
  jade=polygon([(785,608),(773,601),(769,586),(774,564),(786,548),(800,536),(814,536),(826,544),(830,559),(828,580),(818,598),(805,608),(790,610)])
  hand=mask&(jade|((X>=812)&(Y>=530)&(Y<=670)))
 upper=mask&~hand&(along<29)
 fore=mask&~hand&(along>-34)
 # Keep the rigid hand/bangle complete, and trim the departing forearm softly.
 # Small smooth wrist underlap joins the two actual groups; no long source stub.
 farfade=np.clip((810-X)/35,0,1) if role=='L' else np.clip((900-X)/28,0,1)
 for name,mk,m,weight in [('upper',upper,a['upper_rigid_matrix'],np.ones_like(X)),('forearm',fore,a['forearm_rigid_matrix'],farfade),('whole_hand',hand,a['whole_hand_bangle_same_rod_angle_matrix'],np.ones_like(X))]:
  im=warp(softpart(mk,weight),m)
  if role=='L' and name=='forearm':
   a0=np.array(im);a0[X>742]=0;im=Image.fromarray(a0)
  pieces[role+'_'+name]=im
  im.save(O/f'anatomy/{role}_{name}_FINAL094_SOURCE_GROUP.png')
 # Local wrist guide occupies only the actual sleeve/skin interface corridor.
 uv=(w-e)/np.linalg.norm(w-e)
 q1=at(a['forearm_rigid_matrix'],w-uv*(48 if role=='L' else 18))
 q2=at(a['whole_hand_bangle_same_rod_angle_matrix'],w-uv*(45 if role=='L' else 4))
 radius=15 if role=='L' else 18
 # Rounded capsule, short and beneath real source pixels.
 if role=='L':
  cp=np.array([(728,532),(740,515),(748,515),(750,531),(746,553),(736,580),(729,588),(724,565)],float);curve=[]
  for i in range(len(cp)):
   p0,p1,p2,p3=[cp[j%len(cp)] for j in [i-1,i,i+1,i+2]]
   for t in np.linspace(0,1,10,endpoint=False):curve.append(tuple(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
  d.polygon(curve,fill=(236,170,117,255))
  guide_records.append({'role':role,'type':'small_smooth_tapered_wrist_underlap','control_points':cp.tolist(),'reference_only':True})
 else:
  d.line([tuple(q1),tuple(q2)],fill=(236,170,117,255),width=2*radius)
  for q in [q1,q2]:d.ellipse((q[0]-radius,q[1]-radius,q[0]+radius,q[1]+radius),fill=(236,170,117,255))
  guide_records.append({'role':role,'type':'short_rounded_wrist_underlap_only','endpoints':[q1.tolist(),q2.tolist()],'radius':radius,'reference_only':True})
out.alpha_composite(guide)
for role in ['L','R']:
 for name in ['upper','forearm','whole_hand']:out.alpha_composite(pieces[role+'_'+name])
# The arm retraction reveals a small real garment underlap. Use actual blue
# flower cloth from the same locked mother, rather than inventing a flat tube.
oa=np.array(out);corridor=polygon([(607,540),(660,542),(674,584),(664,651),(638,673),(606,640)])
gap=binary_dilation((oa[:,:,3]<128)&corridor,iterations=3)&corridor
cloth=warp(part((X>=480)&(X<=532)&(Y>=606)&(Y<=734)),[[1,0,130],[0,1,-65]])
ca=np.array(cloth);ca[~gap]=0;under=Image.fromarray(ca);under.alpha_composite(out);out=under
Image.fromarray(ca).save(O/'anatomy/SMALL_REVEALED_RIB_REAL_CLOTH_UNDERLAP.png')
n=np.array(out);n[fixed]=B[fixed]
# Minimal swept activity domain, padded 10px, with qualified support/air hard-fixed.
activity=binary_dilation((B[:,:,3]>0)|(n[:,:,3]>0),iterations=10)&~fixed
protected=~activity;n[protected]=B[protected]
assert np.array_equal(n[protected],B[protected]);assert np.array_equal(n[fixed],B[fixed])
Image.fromarray(n).save(O/'anatomy/F098_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png')
Image.fromarray(np.uint8(activity)*255).save(O/'masks/ALLOW_MINIMAL_NATIVE_ACTIVITY.png')
Image.fromarray(np.uint8(protected)*255).save(O/'masks/HARD_PROTECTED_NATIVE_SUPPORT_AND_OUTSIDE.png')
Image.fromarray(np.uint8(fixed)*255).save(O/'masks/HARD_QUALIFIED_FINAL094_SHINS_SHOES_AIR.png')
Image.fromarray(np.array(guide)).save(O/'anatomy/SMALL_WRIST_JOINING_GUIDES_REFERENCE_ONLY.png')
fg0=Image.open(M/'layers/F094_FG_true_front_fingers.png').convert('RGBA');F=np.array(fg0);own=np.zeros((1536,1024),bool)
for role in ['L','R']:
 z=F.copy();z[Y>=700 if role=='L' else Y<700]=0
 own|=np.array(warp(Image.fromarray(z),g['arms'][role]['whole_hand_bangle_same_rod_angle_matrix']))[:,:,3]>0
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'anatomy/F098_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F098_REFERENCE_FG_REAL_FRONT_FINGERS.png')
assert not np.any((fg[:,:,3]>0)&(bg[:,:,3]>0));assert np.array_equal(np.maximum(fg,bg),n)
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(Image.fromarray(n));dr=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for y,txt in [(18,'F098 / EXACT NATIVE ACTIVITY EDIT / ONE CORRECT TARGET'),(45,'FINAL094 REAL SOURCE GROUPS / INPUT REFERENCE ONLY'),(1370,'Hip, waist, chest, shoulders and whole head rise together.'),(1400,'Real closed hands follow shafts; jade on far LEFT wrist.'),(1430,'Reuse natural rounded knees; lower legs/shoes stay planted.'),(1460,'Only small joint seams need natural redrawing. No plates.')]:dr.text((18,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'inputs/01_F098_EXACT_NATIVE_ACTIVITY_TARGET.png')
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&activity
lab,count=label(holes);regions=[]
for i in range(1,count+1):
 yy,xx=np.where(lab==i)
 if len(xx)>8:regions.append({'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]})
qa={'status':'REFERENCE_ASSEMBLY_VISUAL_READBACK_PENDING_NOT_PRODUCTION_ART','imagegen098_calls':0,'imagegen102_calls':0,'actual098_person_Canvas':0,'protected_RGBA_differences':0,'qualified_support_RGBA_differences':0,'BG_FG_overlap':0,'BG_FG_RGBA_reconstruction_differences':0,'whole_person_mesh_or_TPS':False,'pants_reference_only_transition':'actual cloth only: rigid hip to thigh y890-1000; thigh to existing knees y980-1070, smooth coordinate transition; no new navy shapes','small_rib_underlap':'same-mother actual flower cloth source x480..532 y606..734, translation(+130,-65), clipped to newly revealed corridor','RGB_garment_threshold':False,'pre_move_R_subtracted_from_L':False,'new_large_knee_or_waist_plates':False,'guide_regions':guide_records,'internal_low_alpha_regions_for_actual_review':regions,'allowed_pixels':int(activity.sum()),'source_native_size':[1024,1536]}
(O/'qa/NATIVE_SOURCE_GROUP_REFERENCE_READBACK.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa,indent=2))
