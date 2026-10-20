"""One common whole-raw native coordinate correction, never separate limbs.
Complete semantic RGBA adoption; native protected support from sole final094.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,numpy as np
from scipy.ndimage import sobel,binary_fill_holes,label
from scipy.signal import correlate
O=Path(__file__).resolve().parents[1];R=O.parent;P=R/'F098_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL094_20261020';M=R/'F094_LOCAL_ARMS_KNEES_actual_call01_20261019'
assert not (O/'candidate/F098.png').exists(),'Common registration already applied: do not re-fit.'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawpath=O/'originals/F098_exact_native_activity_call01_raw.png'
assert sha(rawpath)=='a020a9a5bc5d7776a9686f6cf8722127760a270fae64bc937378331beed99b8c'
raw=Image.open(rawpath).convert('RGBA');B=np.array(Image.open(M/'candidate/F094.png').convert('RGBA'));T=np.array(Image.open(P/'anatomy/F098_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png').convert('RGBA'))
def neutral(im):
 q=Image.new('RGBA',im.size,'#e1e4e6');q.alpha_composite(im);return q.convert('RGB')
def edge(im):
 a=np.array(im.convert('L'),float);return np.hypot(sobel(a,0),sobel(a,1))
A=edge(neutral(raw));E=edge(Image.open(P/'inputs/01_F098_EXACT_NATIVE_ACTIVITY_TARGET.png'))
g=json.loads((P/'geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text())
spec=[('far_grip',(833,530,886,601),g['arms']['L']['target']['true_grip'],4),('near_grip',(879,730,924,809),g['arms']['R']['target']['true_grip'],4),('glasses',(642,183,716,264),[679,223.5],1),('ear_bun',(448,237,589,319),[518.5,278],1),('shoulder_cloth',(484,416,580,529),[532,472.5],1),('collar',(521,324,632,400),[576.5,362],1),('hip_cloth',(540,716,625,824),[582.5,770],2),('complete_knee_fold',(576,1142,702,1269),[639,1205.5],2),('shoe_support',(78,1260,233,1313),[155.5,1286.5],1)]
samples=[]
for name,(x0,y0,x1,y1),target,weight in spec:
 tpl=E[y0:y1,x0:x1];h,w=tpl.shape;bx0=max(0,x0-45);by0=max(0,y0-45);roi=A[by0:min(1536,y1+65),bx0:min(1024,x1+65)];tpl=tpl-tpl.mean()
 num=correlate(roi,tpl,mode='valid',method='fft');ones=np.ones((h,w));sm=correlate(roi,ones,mode='valid',method='fft');ss=correlate(roi*roi,ones,mode='valid',method='fft');score=num/np.sqrt(np.maximum(ss-sm*sm/(h*w),1e-8)*np.sum(tpl*tpl))
 j,i=np.unravel_index(np.argmax(score),score.shape);shift=np.array([bx0+i-x0,by0+j-y0],float);assert score[j,i]>.5
 samples.append({'region':name,'actual_surface_template_native':[x0,y0,x1,y1],'target':target,'source_raw_visible_proxy':(np.array(target)+shift).tolist(),'raw_delta_native':shift.tolist(),'NCC':float(score[j,i]),'weight':weight})
S=np.array([a['source_raw_visible_proxy'] for a in samples]);D=np.array([a['target'] for a in samples]);W=np.sqrt([a['weight'] for a in samples]);F=np.linalg.lstsq(np.c_[S,np.ones(len(S))]*W[:,None],D*W[:,None],rcond=None)[0].T
for a,q in zip(samples,np.c_[S,np.ones(len(S))]@F.T):
 a['common_registered_visible_proxy']=q.tolist();a['residual_native']=(q-a['target']).tolist();a['distance_native']=float(np.linalg.norm(q-a['target']));a['distance_scene']=.7*a['distance_native']
measure={'status':'ONE_COMMON_WHOLE_SOURCE_AFFINE_READBACK_NO_LOCAL_LIMB_FITS','raw_SHA256':sha(rawpath),'common_raw_to_native_matrix':F.tolist(),'linear_singular_values':np.linalg.svd(F[:,:2])[1].tolist(),'actual_surface_measurements_all_regions':samples,'uncertainty':'Surface NCC proxies, approx3-5px grip, larger sleeve-hidden anatomical uncertainty; not bone measurement. Manual visual Canvas contact gate remains required.','independent_hand_finger_arm_knee_transforms':0,'applied_whole_source_registrations':1,'multiple_generated_candidates':False,'model_calls':1}
(O/'geometry/MEASURED_NATIVE_DRIFT_AND_ONE_COMMON_FIT.json').write_text(json.dumps(measure,indent=2)+'\n')
inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2]
reg=raw.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.BICUBIC);reg.save(O/'geometry/ONE_COMMON_REGISTERED_COMPLETE_RAW.png');G=np.array(reg)
allow=np.array(Image.open(P/'masks/ALLOW_MINIMAL_NATIVE_ACTIVITY.png').convert('L'))>0;protected=~allow
support=np.array(Image.open(P/'masks/HARD_QUALIFIED_FINAL094_SHINS_SHOES_AIR.png').convert('L'))>0
n=B.copy();n[allow]=G[allow];Image.fromarray(n).save(O/'candidate/F098.png')
assert np.array_equal(n[allow],G[allow]);assert np.array_equal(n[protected],B[protected]);assert np.array_equal(n[support],B[support])
# Whole source front-digit ownership only; these source polygons are transformed
# by the SAME one common F as all the rest of the drawing, never separately.
frontpolys={'L_far_jade_actual_curled_front_digits':[(871,552),(887,548),(899,559),(903,577),(895,595),(879,605),(864,601),(865,586),(875,573)],'R_near_bare_actual_curled_front_digits':[(915,749),(929,738),(943,749),(951,766),(948,786),(935,803),(918,805),(906,793),(915,780)]}
front=Image.new('L',raw.size);d=ImageDraw.Draw(front)
for poly in frontpolys.values():d.polygon(poly,fill=255)
front=front.transform(raw.size,Image.Transform.AFFINE,tuple(inv.ravel()),Image.Resampling.NEAREST);own=(np.array(front)>0)&allow
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F098_BG_person.png');Image.fromarray(fg).save(O/'layers/F098_FG_true_front_fingers.png')
assert not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0));assert np.array_equal(np.maximum(bg,fg),n)
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&allow;lab,c=label(holes);regions=[]
for i in range(1,c+1):
 yy,xx=np.where(lab==i)
 if len(xx)>8:regions.append({'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]})
proof={'status':'COMPLETE_SEMANTIC_RAW_NATIVE_ADOPTED_ACTUAL_CANVAS_PENDING','raw_SHA256':sha(rawpath),'complete_common_registered_source_SHA256':sha(O/'geometry/ONE_COMMON_REGISTERED_COMPLETE_RAW.png'),'native_SHA256':sha(O/'candidate/F098.png'),'one_whole_source_native_matrix':F.tolist(),'new_source_RGBA_differences_to_common_registered_raw_inside_allowed':0,'outside_allowed_final094_RGBA_differences':0,'qualified_final094_shins_shoes_air_RGBA_differences':0,'original_alpha_policy':'raw full RGBA under one common geometric transform; no RGB/alpha filters, no opacity forcing, no semantic holes discarded','BG_FG_overlap':0,'BG_FG_RGBA_reconstruction_differences':0,'source_front_digit_polygons':frontpolys,'low_alpha_internal_components_for_actual_readback':regions,'technical_reference_pixels_adopted':0,'sparse_patch_adoption':False,'garment_RGB_thresholds':False,'new098_imagegen_calls':1,'raw_outputs':1,'repeat_imagegen':0,'new102_imagegen_calls':0,'actual098_Canvas':0}
(O/'geometry/COMPLETE_SOURCE_AND_FIXED_SUPPORT_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
neutral(Image.fromarray(n)).save(O/'diagnostics/ADOPTED_COMPLETE_REAL098_NATIVE.png')
board=Image.new('RGB',(1536,800),'#e1e4e6');d=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for i,(name,im) in enumerate([('Frozen098 target / reference only',Image.fromarray(T)),('Unique raw / common coordinate correction',reg),('Complete actual098 / fixed final094 support',Image.fromarray(n))]):board.paste(neutral(im).resize((512,768)),(i*512,32));d.text((i*512+5,7),name,font=font,fill='#25313b')
board.save(O/'diagnostics/TARGET_COMMON_SOURCE_ADOPTED_SAME_SCALE.png')
print(json.dumps({'native_SHA256':proof['native_SHA256'],'common_matrix':F.tolist(),'grip_residuals_native':{a['region']:a['distance_native'] for a in samples if 'grip' in a['region']},'protected_RGBA_diff':0,'source_RGBA_diff':0,'internal_low_alpha_components':regions},indent=2))
