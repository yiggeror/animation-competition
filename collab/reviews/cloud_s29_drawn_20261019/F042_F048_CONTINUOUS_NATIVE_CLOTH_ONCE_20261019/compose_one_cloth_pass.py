from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;Q=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019';OLD=Q/'single_group_reintegration_TRIAL';P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
reports=json.loads((OLD/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
prop=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
H,W=near.shape;yy,xx=np.indices((H,W))
def poly(pts):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0

def warp(v,M):
 v=v.astype('float32');v[:,:,:3]*=v[:,:,3:4]/255;inv=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2].reshape(-1)
 out=np.stack([np.array(Image.fromarray(v[:,:,k],mode='F').transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)) for k in range(4)],2);out=np.clip(out,0,255);a=out[:,:,3:4]/255;out[:,:,:3]=np.divide(out[:,:,:3],a,out=np.zeros_like(out[:,:,:3]),where=a>1e-6);return np.round(np.clip(out,0,255)).astype('uint8')

def shape_warp(m,M):
 v=np.zeros((H,W,4),dtype='uint8');v[:,:,3]=m.astype('uint8')*255;return warp(v,M)[:,:,3]>0

polys={42:[(259,879),(326,800),(374,750),(486,745),(514,735),(548,722),(584,710),(620,698),(649,681),(740,659),(785,687),(874,732),(947,789),(978,828),(999,867),(1008,905),(972,933),(1001,952),(1008,986),(976,1040),(947,1072),(923,1055),(863,1020),(837,1033),(812,1076),(763,1033),(695,1019),(625,1010),(544,994),(476,972),(411,950),(337,924),(275,904)],
48:[(258,879),(328,800),(375,750),(489,745),(515,735),(550,721),(585,709),(625,685),(671,656),(699,649),(728,681),(784,708),(836,732),(895,766),(955,807),(982,834),(998,869),(1005,905),(972,932),(1001,958),(1005,990),(974,1042),(946,1073),(922,1055),(864,1021),(839,1033),(812,1074),(763,1033),(693,1020),(625,1010),(542,993),(473,971),(407,947),(333,922),(273,902)]}
result=[]
for r in reports:
 f=r['frame'];M=np.array(r['single_similarity_complete_arm_hand_and_cloth'],float)
 basep=OLD/'candidate'/f'F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png';base=np.array(Image.open(basep).convert('RGBA'));assert hashlib.sha256(basep.read_bytes()).hexdigest()==r['candidate_sha256']
 rawp=Q/f'F{f:03d}'/'originals'/f'S29_F{f:03d}_call01_RAW_UNTOUCHED.png';raw=np.array(Image.open(rawp).convert('RGBA'));rgb=raw[:,:,:3].astype(float)
 # Continuous whole source surface: outer selection follows the actual ridge/hem,
 # with native-alpha contour refinement. No blue/flower pixel thresholding.
 contour=poly(polys[f]);native_alpha=nd.binary_dilation(raw[:,:,3]>=128,iterations=1)&(raw[:,:,3]>0)
 full_native_face=contour&native_alpha
 source=full_native_face.copy()
 # Exclude real source humans and the generated contextual puppet/feather/rod shapes.
 warm=(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,0]>105)&(rgb[:,:,1]>60)
 jade=(rgb[:,:,1]>rgb[:,:,0]*1.04)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
 human_roi=(yy<747)&(xx>420)&(xx<850)
 humans=nd.binary_dilation((warm|jade)&human_roi,iterations=2)
 fake=poly([(325,736),(492,725),(622,735),(749,748),(816,785),(890,840),(851,851),(784,825),(700,818),(590,821),(473,820),(382,802),(325,782)])
 fake|=poly([(257,820),(422,812),(557,843),(582,922),(455,934),(255,908)])
 fake|=poly([(604,786),(660,787),(662,894),(603,895)])
 fake|=poly([(720,758),(786,773),(846,804),(897,852),(887,866),(815,836),(760,818),(715,795)])
 gold=(rgb[:,:,0]>rgb[:,:,2]*1.25)&(rgb[:,:,1]>rgb[:,:,2]*1.12)&(rgb[:,:,0]>90)
 fake|=nd.binary_dilation(gold&source,iterations=8)
 source&=~fake&~humans
 material=np.zeros_like(raw);material[source]=raw[source];newcloth=warp(material,M)
 # Existing accepted full arm/sleeve/palm/fingers are a top, unchanged layer.
 oldarm_source=np.array(Image.open(OLD/'masks'/f'F{f:03d}_RAW_COMPLETE_FAR_ARM_AND_SLEEVE.png').convert('L'))>0
 armguard=shape_warp(oldarm_source,M);armguard=nd.binary_dilation(armguard,iterations=1)
 fixed=(yy<640)&(xx<490);fixed|=yy<470;fixed|=yy>=1076
 guard=near|prop|armguard|fixed
 # Retire the old8c cloth contribution over the COMPLETE replacement face,
 # including its obsolete top protrusion and old lower sampling boundaries.
 old_cloth_face=poly([(250,881),(327,794),(375,747),(485,745),(506,668),(603,666),(691,634),(752,626),(844,678),(932,741),(1015,818),(1020,992),(975,1051),(947,1076),(925,1058),(864,1025),(838,1035),(812,1077),(763,1040),(693,1026),(622,1017),(542,1000),(472,978),(407,956),(332,931),(266,908)])
 mapped_face=shape_warp(full_native_face,M)
 replacement=(old_cloth_face|mapped_face)&~guard
 v=base.copy();v[replacement]=0
 # No old8c cloth remains as hidden backing in the retired face.
 v=np.array(Image.alpha_composite(Image.fromarray(v),Image.fromarray(newcloth)));v[guard]=base[guard]
 intended=nd.binary_erosion(mapped_face,iterations=2)&~guard
 missing=intended&(newcloth[:,:,3]<128)
 fake_projected=shape_warp(fake&full_native_face,M)&missing
 human_projected=shape_warp(humans&full_native_face,M)&missing
 gold_core=gold&full_native_face
 certain_generated_gold=shape_warp(gold_core,M)&missing
 def metrics(mask):
  y,x=np.where(mask)
  return {'pixels':int(mask.sum()),'bbox_inclusive':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())]}
 Image.fromarray(replacement.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_WHOLE_OLD_CLOTH_RETIRED.png')
 Image.fromarray(missing.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_UNAVAILABLE_CLOTH_AFTER_PROTECTION.png')
 outp=R/f'F{f:03d}_CONTINUOUS_RAW_CLOTH_RGBA_TRIAL.png';Image.fromarray(v).save(outp)
 g=Image.new('RGBA',(W,H),(236,239,242,255));g.alpha_composite(Image.fromarray(v));g.convert('RGB').save(R/f'F{f:03d}_FULL_ON_GRAY.png');crop=g.crop((475,635,1005,1065));crop.resize((795,645)).convert('RGB').save(R/f'F{f:03d}_CLOTH_SEAM_CONTACT_ON_GRAY.png')
 Image.fromarray(source.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_ONE_CONTINUOUS_RAW_COTTON_SOURCE.png');Image.fromarray(guard.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_CURRENT_8C_TOP_PROTECTIONS.png')
 changed=np.any(v!=base,2)
 result.append({'frame':f,'source_raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'source_8c_candidate_sha256':hashlib.sha256(basep.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(outp.read_bytes()).hexdigest(),'M_exactly_read_not_refit':M.tolist(),'raw_cotton_selected_pixels':int(source.sum()),'whole_old8c_cloth_retired_pixels':int(replacement.sum()),'unavailable_exposed_cloth':metrics(missing),'projected_generated_prop_exclusion':metrics(fake_projected),'projected_human_occlusion':metrics(human_projected),'confirmed_raw_gold_core_not_cotton':metrics(certain_generated_gold),'near_C1_RGBA_changed':int(changed[near].sum()),'existing_complete_far_arm_RGBA_changed':int(changed[armguard].sum()),'true_original_props_all_RGBA_changed':int(changed[prop].sum()),'fixed_head_chest_lowerlegs_guard_RGBA_changed':int(changed[fixed].sum()),'new_generation_calls':0,'cotton_RGB_source':'this state original raw only, same coordinate M; no 036 donor crop','status':'HOLD_EXPOSED_SOURCE_CLOTH_GAPS_AFTER_FULL_OLD_CLOTH_RETIREMENT'})
json.dump({'source_commit':'8c41ca4517978ca3a4e6a44260ed1d3426f12edd','one_pass_only':True,'reports':result},open(R/'geometry/ONE_PASS_SOURCE_M_PROTECTION.json','w'),indent=2)
print(json.dumps(result,indent=2))
