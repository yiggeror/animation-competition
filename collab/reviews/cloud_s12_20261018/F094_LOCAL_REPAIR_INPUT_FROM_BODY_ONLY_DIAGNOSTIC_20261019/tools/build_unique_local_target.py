"""One corrected local target on Astra's selected094 body registration.
Smooth opaque anatomical guides + qualified090 closed palms; no pointed raw
wrist block, no old competing arm. All guides remain reference-only.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,math
from scipy.ndimage import binary_dilation
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F090_SAME_RAW_SEMANTIC_OWNERSHIP_FIXED_20261019';P=R/'F094_COMPLETE_TARGET_FROM_LOCKED090_20261019'
plan=json.loads((O/'geometry/ONE_CORRECT_LOCAL_ARMS_AND_CONDITIONAL_KNEES_PLAN.json').read_text());diag=json.loads((O/'geometry/GIVEN_BODY_DIAGNOSTIC_ALL_POINTS_PUBLIC.json').read_text());F=np.asarray(diag['raw_to_native_matrix'])
src=Image.open(O/'body_diagnostic/BODY_DIAGNOSTIC_NATIVE_WITH_FAILED_ARMS_VISIBLE.png').convert('RGBA');B=np.asarray(src);H90=np.asarray(Image.open(M/'candidate/F090.png').convert('RGBA'));Y,X=np.mgrid[:1536,:1024]
def mp(points):return np.c_[np.asarray(points),np.ones(len(points))]@F.T
def poly(points):
 q=Image.new('L',src.size);ImageDraw.Draw(q).polygon([tuple(p) for p in points],fill=255);return np.asarray(q)>0
def capsule(mask,a,b,ra,rb):
 d=ImageDraw.Draw(mask);a=np.asarray(a);b=np.asarray(b);v=(b-a)/np.linalg.norm(b-a);n=np.array([-v[1],v[0]])
 d.polygon([tuple(a+ra*n),tuple(b+rb*n),tuple(b-rb*n),tuple(a-ra*n)],fill=255)
 for p,r in [(a,ra),(b,rb)]:d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=255)
armmask=Image.new('L',src.size)
for role,a in plan['arms'].items():
 old={k:diag['all_predeclared_points_public_including_failed_grips'][role+'_'+k]['registered'] for k in ['shoulder','elbow','wrist','true_grip']}
 for q in [old,a]:
  capsule(armmask,q['shoulder'],q['elbow'],78,62);capsule(armmask,q['elbow'],q['wrist'],60,51);capsule(armmask,q['wrist'],q['true_grip'],62,65)
bad_raw=[(785,570),(885,570),(930,715),(780,735)]
old_near_sleeve_raw=[(530,414),(597,416),(646,458),(673,511),(689,572),(699,622),(698,656),(626,687),(547,720),(547,674),(519,621),(501,570),(495,516),(500,459)]
old_near_skin_raw=[(604,645),(698,645),(735,705),(818,750),(895,793),(948,790),(978,810),(980,865),(953,894),(915,902),(859,900),(790,870),(715,825),(655,790),(600,750),(585,700)]
old_skin=poly(mp(old_near_skin_raw))
arm=np.asarray(armmask)>0;arm|=poly(mp(bad_raw))|poly(mp(old_near_sleeve_raw))|old_skin

collar_raw=[(531,329),(575,325),(637,358),(672,394),(725,421),(768,431),(765,465),(788,501),(795,540),(776,584),(767,606),(728,626),(692,613),(668,572),(645,524),(621,480),(596,447),(565,421),(535,401),(519,374)]
collar=binary_dilation(poly(mp(collar_raw)),iterations=2)
waist=poly([(410,685),(580,680),(620,730),(652,815),(690,925),(440,840),(350,760)])&~old_skin # Actual old arm is not protected waist cloth.
fixed=np.asarray(Image.open(P/'masks/LOCKED090_REAL_SHINS_ANKLES_SHOES_BLANK_FIXED.png').convert('L'))>0
hardshoe=np.asarray(Image.open(R/'F090_COMPLETE_TARGET_FROM_FINAL086_20261019/masks/REAL_ORIGINAL_SHOES_ANKLES_SURROUNDING_EMPTY_HARD.png').convert('L'))>0
fixed_positive=fixed&(np.asarray(Image.open(M/'candidate/F090.png'))[:,:,3]>0)
knee=poly([(370,1055),(430,1030),(500,1053),(580,1080),(685,1088),(748,1170),(748,1298),(700,1319),(540,1319),(442,1260),(330,1198),(300,1120),(325,1060)])
knee&=~(fixed_positive|hardshoe);knee&=(Y<=1319)
arm&=~(collar|waist|fixed|(Y<390)|(Y>=850))
allowed=arm|knee;protected=~allowed
# Complete actual torso core remains continuous. Only newly exposed old-arm
# footprints inside it receive clearly opaque reference cloth, never flat fill
# as production. Old outside-arm alpha is cleared in the one correction domain.
core=poly([(455,390),(606,390),(676,449),(720,530),(716,590),(677,632),(647,675),(638,715),(646,760),(662,815),(690,925),(550,880),(460,840),(384,805),(351,761),(395,690),(439,617),(458,550)])
n=B.copy();n[arm&~core]=0;n[arm&core&(B[:,:,3]>0)]=[43,86,145,255]
base=Image.fromarray(n)
def rounded_volume(s,e,wstart,wend,col,outline):
 s=np.asarray(s);e=np.asarray(e);d=e-s;u=d/np.linalg.norm(d);normal=np.array([-u[1],u[0]])
 c=Image.new('RGBA',src.size);q=ImageDraw.Draw(c)
 q.polygon([tuple(s+wstart*normal),tuple(e+wend*normal),tuple(e-wend*normal),tuple(s-wstart*normal)],fill=col)
 for p,r in [(s,wstart),(e,wend)]:q.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=col)
 return c
def forearm_volume(e,w,g,rs=34,re=25,skin=(242,171,110,255)):
 e=np.asarray(e);w=np.asarray(w);g=np.asarray(g);v=w-e;l=np.linalg.norm(v);hd=(g-w)/np.linalg.norm(g-w)
 controls=[e,e+.35*v,w-.32*l*hd,w];left=[];right=[]
 for t in np.linspace(0,1,65):
  a,b,c,d=controls;p=(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
  tangent=3*(1-t)**2*(b-a)+6*(1-t)*t*(c-b)+3*t*t*(d-c);tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]]);radius=(1-t)*rs+t*re
  left.append(tuple(p+radius*normal));right.append(tuple(p-radius*normal))
 im=Image.new('RGBA',src.size);d=ImageDraw.Draw(im);d.polygon(left+right[::-1],fill=skin);d.line(left,fill=(181,112,66,255),width=2);d.line(right,fill=(181,112,66,255),width=2)
 d.ellipse((e[0]-rs,e[1]-rs,e[0]+rs,e[1]+rs),fill=skin);return im
hands={};newarms={}
for role,a in plan['arms'].items():
 s=np.asarray(a['shoulder']);e=np.asarray(a['elbow']);w=np.asarray(a['wrist']);g=np.asarray(a['true_grip']);u=(e-s)/np.linalg.norm(e-s)
 join=w
 if role=='R':join=np.asarray(a['whole_true_hand_matrix_from_final090_same65deg_rod'])@np.array([900.,790.,1.])
 im=forearm_volume(e,join,g,34 if role=='R' else 31,25,(242,171,110,255) if role=='R' else (246,193,143,255))
 sleeve=rounded_volume(s,e-60*u,53 if role=='R' else 45,43 if role=='R' else 37,(57,118,191,255) if role=='R' else (105,156,211,255),(34,76,126,255));im.alpha_composite(sleeve)
 # Qualified090 real palms only. Complete bangle is selected as one semantic
 # ellipse plus the complete palm; no old pointed094 forearm is supplied.
 if role=='L':
  hmask=poly([(815,654),(804,648),(802,636),(807,618),(817,601),(831,587),(842,583),(851,585),(858,593),(861,605),(859,621),(852,638),(839,652),(825,658)])|((X>=844)&(Y>=565)&(Y<=705))
 else:
  old=json.loads((P/'geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())['arms']['R']['source_actual090'];sw=np.asarray(old['wrist']);sg=np.asarray(old['true_grip']);v=sg-sw;along=((X-sw[0])*v[0]+(Y-sw[1])*v[1])/np.dot(v,v)
  hmask=(X>=892)&(Y>=730)&(Y<=850) # Whole palm/fingers with a clean short wrist interface; no long forearm stub.
 hp=np.zeros_like(H90);hp[hmask]=H90[hmask];mat=np.asarray(a['whole_true_hand_matrix_from_final090_same65deg_rod']);inv=np.linalg.inv(np.vstack([mat,[0,0,1]]))[:2]
 hand=Image.fromarray(hp).transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);hands[role]=hand;im.alpha_composite(hand);newarms[role]=im
# Far arm behind protected actual central shirt; near arm in front, with the
# original complete collar/chest restored once at the final protected mask.
base.alpha_composite(newarms['L']);base.alpha_composite(newarms['R'])
n=np.asarray(base).copy();n[~arm]=B[~arm]
# Complete both-knee / upper-shin-return guide. Only this small domain changes;
# all main hip/pants above it and actual positive shins/shoes remain original.
outline=np.array([(399,1055),(450,1045),(510,1060),(580,1081),(681,1090),(727,1188),(731,1260),(710,1298),(664,1313),(617,1316),(568,1312),(517,1305),(466,1283),(420,1240),(366,1180),(326,1130),(351,1093),(389,1067)],float)
sm=[]
for i in range(len(outline)):
 p0,p1,p2,p3=[outline[j%len(outline)] for j in [i-1,i,i+1,i+2]]
 for t in np.linspace(0,1,16,endpoint=False):sm.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
envelope=poly(sm)
trim=knee&~envelope&(((X<410)&(Y<1150))|((X>650)&(Y>1140)))
n[trim]=0;n[knee&envelope]=[54,58,78,255] # Preserve continuous real upper knee cloth; trim only the old flag and final outer contact edge.

# Readable natural fold guides, explicitly new-ink anatomical target only.
im=Image.fromarray(n);d=ImageDraw.Draw(im)
d.line([(442,1093),(488,1165),(554,1214),(618,1256),(654,1281)],fill=(39,43,61,255),width=3)
d.line([(378,1132),(430,1165),(485,1220),(537,1268)],fill=(39,43,61,255),width=3)
n=np.asarray(im).copy();n[protected]=B[protected];Image.fromarray(n).save(O/'layers/CORRECTED_LOCAL_REFERENCE_ONLY_PERSON.png')
assert np.array_equal(n[protected],B[protected])
for name,mask in [('ALLOW_COMPLETE_BOTH_ARMS',arm),('ALLOW_COMPLETE_BOTH_KNEES_UPPER_SHIN_FOLDS',knee),('ALLOW_UNION_LOCAL_REPAIR',allowed),('HARD_PROTECTED_BODY_COLLAR_WAIST_PANTS_SUPPORT',protected),('HARD_ORIGINAL_COLLAR_AND_CENTRAL_CHEST',collar),('HARD_ACTUAL_POSITIVE_SHINS_AND_SHOE_AIR',fixed_positive|hardshoe)]:Image.fromarray(np.uint8(mask)*255).save(O/f'masks/{name}.png')
fg90=np.asarray(Image.open(M/'layers/F090_FG_true_front_fingers.png').convert('RGBA'));own=np.zeros((1536,1024),bool)
for role,a in plan['arms'].items():
 q=fg90.copy();q[Y>=710 if role=='L' else Y<710]=0;mat=np.asarray(a['whole_true_hand_matrix_from_final090_same65deg_rod']);inv=np.linalg.inv(np.vstack([mat,[0,0,1]]))[:2];own|=np.asarray(Image.fromarray(q).transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST))[:,:,3]>0
own&=arm;fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'layers/CORRECT_TARGET_REFERENCE_BG.png');Image.fromarray(fg).save(O/'layers/CORRECT_TARGET_REFERENCE_FG.png');assert np.array_equal(np.maximum(bg,fg),n)
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(Image.fromarray(n));d=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for y,txt in [(16,'F094 / AUTHORITATIVE LOCAL CORRECTION / ONLY ONE POSE'),(43,'Exact body-only registration retained; NO new whole-person draw'),(70,'Smooth COMPLETE arms + real090 closed palms; no pointed raw wrist'),(1370,'OPAQUE TECHNICAL ARMS / BOTH FULL KNEE-FOLD DOMAINS: NEW INK'),(1400,'Actual head / collar / chest / waist / main pants / shins / shoes LOCKED'),(1430,'REFERENCE ONLY. New image calls0;098 calls0.')]:d.text((16,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'inputs/01_AUTHORITATIVE_CORRECT_LOCAL_ARMS_KNEES_BODY_LOCKED.png')
q={'status':'UNIQUE_CORRECT_LOCAL_TARGET_REFERENCE_ONLY_READY_FOR_VISUAL_REVIEW','source_body_native_SHA256':diag['native_SHA256'],'new_imagegen':0,'new098_calls':0,'body_matrix_searches':0,'given_body_matrix_applied_once':True,'arm_domain_pixels':int(arm.sum()),'knee_domain_pixels':int(knee.sum()),'protected_RGBA_changes':0,'hard_shin_shoe_source_RGBA_changes':0,'technical_volumes_production_pixels':False,'raw094_pointed_wrist_blocks_used_as_target':False,'qualified090_palms_unchanged_scale':1}
(O/'qa/LOCAL_REFERENCE_DOMAIN_SOURCE_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
