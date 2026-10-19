"""One authorized two-rigid-segment diagnosis per real090 arm. No model calls.
Technical opaque volumes are reference-only and explicitly require new ink.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent
M=R/'F090_COMPLETE_actual_call01_20261019';P=R/'F090_COMPLETE_TARGET_FROM_FINAL086_20261019'
assert not (O/'reference/F090_SOLE_COMPLETE_TWO_ARM_RECONNECT_TARGET.png').exists(),'One diagnostic only, no repeat'
for d in ['reference','geometry','prompts','requests','provenance','layers','qa','scene','actual_scene']:(O/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(M/'candidate/F090.png')=='0f1caa9edf588cdf525b728770a9079ac97b01c81ff09a398ec468add59ee209'
src=Image.open(M/'candidate/F090.png').convert('RGBA');A=np.asarray(src)
old=json.loads((M/'geometry/ONE_JOINT_REGISTRATION_ALL_RESIDUALS_AND_SUPPORT.json').read_text());F=np.asarray(old['one_whole_raw_to_native_matrix']);q=old['all_point_results_no_dropped_knees_elbows']
pose=json.loads((P/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text())
polys={
 'R_upper':[(475,454),(558,450),(614,490),(652,550),(679,621),(656,699),(694,742),(650,776),(605,788),(539,803),(516,747),(491,668),(483,600),(475,530)],
 'R_forearm_hand':[(601,754),(649,729),(685,751),(737,790),(792,819),(843,842),(910,855),(932,851),(932,832),(946,816),(965,819),(980,832),(986,855),(984,880),(965,905),(935,923),(912,924),(875,911),(826,892),(766,871),(713,853),(675,831),(636,800),(612,779)],
 'L_upper':[(563,450),(614,466),(667,493),(696,536),(717,579),(707,623),(686,654),(649,679),(620,688),(611,653),(620,615),(604,563),(575,523)],
 'L_forearm_hand':[(614,666),(648,648),(690,649),(741,655),(791,655),(809,638),(830,640),(844,656),(865,657),(901,640),(921,628),(938,629),(951,639),(965,657),(970,681),(962,705),(945,724),(921,721),(907,711),(878,707),(848,704),(829,718),(810,718),(798,704),(766,715),(726,728),(690,733),(651,721),(629,698)]}
def points(M,p):return np.c_[np.asarray(p),np.ones(len(p))]@M.T
def poly_mask(p):
 m=Image.new('L',src.size);ImageDraw.Draw(m).polygon([tuple(x) for x in p],fill=255);return np.asarray(m)>0
masks={k:poly_mask(points(F,v)) for k,v in polys.items()}
# Exclusive original ownership; near arm is foreground, no second competing arm.
used=np.zeros(A.shape[:2],bool)
for k in ['R_forearm_hand','R_upper','L_forearm_hand','L_upper']:
 masks[k]&=~used;used|=masks[k]
base=A.copy();base[used]=0
tech=Image.new('RGBA',src.size);td=ImageDraw.Draw(tech)
# Previously occluded shirt below the moving sleeve is missing from the raw.
# Flat opaque blue identifies only that newly exposed arm-root region, never art.
core=poly_mask(points(F,[(560,450),(650,490),(715,580),(696,678),(632,774),(541,800),(473,695),(461,564)]))
patch=used&core&(A[:,:,3]>128)
ta=np.zeros_like(A);ta[patch]=[49,101,166,255];tech.alpha_composite(Image.fromarray(ta))
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def rigid(p,t,d):
 rr=rot(d);return np.c_[rr,np.asarray(t)-rr@np.asarray(p)]
def angle(a,b):return math.degrees(math.atan2(b[1],b[0])-math.atan2(a[1],a[0]))
def warp(im,m,resample=Image.Resampling.BICUBIC):
 inv=np.linalg.inv(np.vstack([m,[0,0,1]]))[:2];return im.transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),resample)
arms={};blocks={};jointvolumes=Image.new('RGBA',src.size);jd=ImageDraw.Draw(jointvolumes)
for r in ['R','L']:
 s,e,c=[np.asarray(q[r+'_'+k]['registered']) for k in ['shoulder','elbow','true_grip']];t=np.asarray(q[r+'_true_grip']['target'])
 u=np.linalg.norm(e-s);f=np.linalg.norm(c-e);v=t-s;d=np.linalg.norm(v)
 if not abs(u-f)<d<u+f:raise RuntimeError(r+' has no two-rigid-segment reach; stop without pixel trial')
 aa=(u*u-f*f+d*d)/(2*d);hh=math.sqrt(u*u-aa*aa)
 v0=c-s;v1=e-s;branch=1 if v0[0]*v1[1]-v0[1]*v1[0]>=0 else -1
 et=s+aa*v/d+branch*hh*np.array([-v[1],v[0]])/d
 au=angle(e-s,et-s);af=angle(c-e,t-et);U=rigid(s,s,au);V=rigid(e,et,af)
 assert np.allclose(points(U,[e])[0],et) and np.allclose(points(V,[c])[0],t)
 assert np.allclose(U[:,:2].T@U[:,:2],np.eye(2)) and np.allclose(V[:,:2].T@V[:,:2],np.eye(2))
 for part,mat in [('upper',U),('forearm_hand',V)]:
  k=r+'_'+part;z=np.zeros_like(A);z[masks[k]]=A[masks[k]];im=warp(Image.fromarray(z),mat);blocks[k]=im;im.save(O/f'layers/{k}_REAL_SOURCE_RIGID_ONLY.png')
 # Complete flat technical elbow and shoulder volume under the unchanged source
 # pixels, clearly needs coherent native redrawing instead of copied mesh seams.
 radius=30 if r=='R' else 25
 jd.ellipse((et[0]-radius,et[1]-radius,et[0]+radius,et[1]+radius),fill=(213,142,91,255))
 jd.line([tuple(s),tuple(et)],fill=(51,111,186,255),width=80 if r=='R' else 66)
 jd.ellipse((s[0]-39,s[1]-39,s[0]+39,s[1]+39),fill=(51,111,186,255))
 wrist=np.asarray(q[r+'_wrist']['registered']);neww=points(V,[wrist])[0]
 shaft=np.asarray(pose['prop_plan']['rods'][r]['hinge_scene'])-np.asarray(pose['prop_plan']['rods'][r]['grip_scene'])
 arms[r]={'source_shoulder_elbow_wrist_grip':[s.tolist(),e.tolist(),wrist.tolist(),c.tolist()],'target_shoulder_elbow_wrist_grip':[s.tolist(),et.tolist(),neww.tolist(),t.tolist()],
 'upper_length_fixed_native':float(u),'whole_forearm_elbow_to_grip_fixed_native':float(f),'reach_native':float(d),'natural_original_bend_branch':branch,'upper_rotation_degrees':au,'whole_forearm_wrist_palm_rotation_degrees':af,
 'upper_rigid_matrix':U.tolist(),'whole_forearm_wrist_palm_rigid_matrix':V.tolist(),'scale_each_segment':1,'grip_mapping_error_native':float(np.linalg.norm(points(V,[c])[0]-t)),
 'wrist_palm_direction_vs_projected_shaft_degrees':angle(t-neww,shaft),'no_independent_finger_hand_move':True}
out=Image.fromarray(base);out.alpha_composite(tech);out.alpha_composite(jointvolumes)
for k in ['L_upper','L_forearm_hand','R_upper','R_forearm_hand']:out.alpha_composite(blocks[k])
out.save(O/'layers/F090_REFERENCE_ONLY_COMPLETE_RECONNECTED_PERSON.png')
# Exact source head, waist/pants/support outside this one declared arm diagnostic.
dst=np.asarray(out);changed=np.any(dst!=A,axis=2);Image.fromarray(np.uint8(changed)*255).save(O/'geometry/ACTUAL_CHANGED_ARM_DIAGNOSTIC_DOMAIN.png')
assert not changed[:340].any() and not changed[970:].any(),'Unrelated head or pants touched'
front=Image.new('L',src.size);fd=ImageDraw.Draw(front)
for r,key in [('L','far_LEFT_jade_front_digits'),('R','near_RIGHT_bare_front_digits')]:
 pp=old['actual_raw_front_digit_ownership'][key];coords=points(F,pp);coords=points(np.asarray(arms[r]['whole_forearm_wrist_palm_rigid_matrix']),coords);fd.polygon([tuple(x) for x in coords],fill=255)
own=np.asarray(front)>0;fg=np.zeros_like(dst);fg[own]=dst[own];bg=dst.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F090_REFERENCE_BG.png');Image.fromarray(fg).save(O/'layers/F090_REFERENCE_FG_FRONT_DIGITS.png')
assert np.array_equal(np.maximum(bg,fg),dst)
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(out);dr=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for y,txt in [(18,'F090 / ONE ZERO-CALL TWO-RIGID-SEGMENT ARM DIAGNOSIS'),(49,'REAL090 source pixels + OPAQUE TECHNICAL JOINT VOLUMES'),(80,'REFERENCE ONLY: complete shoulder/elbow/forearm joins need new ink'),(1420,'Head / real waist-pants / fixed support unchanged; no scaling or mesh'),(1451,'Closed palms move only with WHOLE forearm. True60deg rods frozen.')]:dr.text((18,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'reference/F090_SOLE_COMPLETE_TWO_ARM_RECONNECT_TARGET.png')
proof={'status':'SOLE_ZERO_IMAGEGEN_TWO_RIGID_ARM_DIAGNOSTIC_REFERENCE_NOT_PRODUCTION','source_commit':'042e0ce9cc081e4abac896b7b451aa3d2cf4fc0b','registered_real090_source_SHA256':sha(M/'candidate/F090.png'),'arms':arms,'arm_source_ownership_raw_polygons':polys,
 'diagnostic_scheme_count':1,'new_whole_registrations':0,'independent_hand_or_finger_transformations':0,'segment_scales':1,'mesh_warps':0,'imagegen_calls':0,'next094_calls':0,'technical_volumes_are_production_pixels':False,
 'source_head_RGBA_changes_y_lt340':int(changed[:340].sum()),'source_pants_and_support_RGBA_changes_y_ge970':int(changed[970:].sum()),'new_exposed_arm_root_technical_patch_pixels':int(patch.sum()),'all_changed_reference_pixels':int(changed.sum()),'natural_joint_ink_needed':True,'actual_reference_scene_Canvas':0,'production_actual090_Canvas_count_remains':1}
(O/'geometry/ONE_SCHEME_RIGID_ARM_REACH_AND_PIXEL_OWNERSHIP.json').write_text(json.dumps(proof,indent=2)+'\n')
(O/'provenance/call_ledger.json').write_text(json.dumps({'status':'ZERO_CALL_REFERENCE_RECONNECT_NEEDS_NATIVE_JOINT_INK','new_model_calls':0,'new_production_poses':0,'diagnostic_schemes':1,'reference_Canvas':0,'new094_calls':0},indent=2)+'\n')
print(json.dumps({'arms':{r:{k:v for k,v in a.items() if k in ['upper_rotation_degrees','whole_forearm_wrist_palm_rotation_degrees','grip_mapping_error_native','wrist_palm_direction_vs_projected_shaft_degrees']} for r,a in arms.items()},'head_pants_support_changes':0,'reference_only':True},indent=2))
