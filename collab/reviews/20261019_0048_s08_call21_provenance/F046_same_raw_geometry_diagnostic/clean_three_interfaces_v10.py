from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,binary_dilation,map_coordinates
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent.parent;V=R/'F046_same_raw_geometry_candidate_v9_cloth';D=R/'F046_same_raw_geometry_candidate_v10';G=R/'F046_input_gate';P=R/'F043_FINAL_LOCKED'
for d in ['candidates','masks','qa','geometry']:(D/d).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(P/'S08_F043_grandma_match_box_RGBA.png'));q=np.array(Image.open(R/'F046_result_nominal/registered/F046_registered_scene_patch_RGBA.png'));v=np.array(Image.open(V/'candidates/S08_F046_same_raw_continuous_arm_cloth_RGBA.png'));out=v.copy();H,W=v.shape[:2];Y,X=np.indices((H,W))
def poly(p):
 z=Image.new('L',(W,H));ImageDraw.Draw(z).polygon(p,fill=255);return np.array(z)>0
def put(src,m,wt):
 global out
 # True source texels are used at full strength for ink/white detail; only plain internal blue joins feather.
 gray=np.max(src[:,:,:3],2)<110;white=np.min(src[:,:,:3],2)>210;wt[m&(gray|white)]=1
 val=np.rint(out[:,:,:3]*(1-wt[:,:,None])+src[:,:,:3]*wt[:,:,None]).astype('uint8');out[m,:3]=val[m];out[m,3]=src[m,3]
# One complete original043 upper collar; actual raw sleeve/lapel edge below intersects it at the natural y750 junction.
upper=poly([(831,680),(888,680),(916,725),(943,755),(922,776),(890,755),(870,729),(844,706)])
put(a,upper,np.clip(distance_transform_edt(upper)/5,0,1))
# Entire actual native inner sleeve/lapel join, not isolated line fragments. Source sleeve geometry from same registered raw.
inner=poly([(835,713),(862,704),(882,728),(907,744),(942,759),(973,786),(992,821),(990,844),(952,842),(936,817),(902,784),(866,751)])
# Keep original collar on its actual right side of the left fold above the natural joining point.
inner&=~poly([(865,680),(942,680),(942,753),(892,753),(879,731)])
rawskin=(q[:,:,0].astype(int)-q[:,:,2].astype(int)>24)&(q[:,:,0].astype(int)-q[:,:,1].astype(int)>10)&(q[:,:,0]>110)
inner|=poly([(817,710),(863,704),(890,730),(905,755),(882,773),(834,754)]);inner&=~rawskin&(q[:,:,3]>230)
put(q,inner,np.clip(distance_transform_edt(inner)/6,0,1))
# Actual raw full placket below the unchanged chest button, continuing to the real foreground occlusion.
yy=Y.astype(float);sy=np.where(yy>800,800+(yy-800)*.8,yy);co=np.array([sy,X.astype(float)]);qa=q[:,:,3]/255.;pm=q[:,:,:3]*qa[:,:,None];pa=map_coordinates(qa,co,order=1,mode='constant',cval=0);pp=np.stack([map_coordinates(pm[:,:,j],co,order=1,mode='constant',cval=0)for j in range(3)],2);qp=np.dstack((np.rint(pp/np.maximum(pa[:,:,None],1e-8)).clip(0,255).astype('uint8'),np.rint(pa*255).astype('uint8')))
qpskin=(qp[:,:,0].astype(int)-qp[:,:,2].astype(int)>24)&(qp[:,:,0].astype(int)-qp[:,:,1].astype(int)>10)&(qp[:,:,0]>110)
placket=poly([(960,793),(1040,793),(1040,873),(960,873)])&~qpskin&(qp[:,:,3]>230)
put(qp,placket,np.clip(distance_transform_edt(placket)/6,0,1))
# Foreground skin and true hand stay exactly v7 over every cloth repair.
arm=np.array(Image.open(R/'F046_same_raw_geometry_candidate_v9_base/registered/ACTUAL_native_near_arm_transformed_only_RGBA.png'));front=arm[:,:,3]>0
out[front]=v[front]
# Same raw21 bright neutral pixels outside lower-arm ink are identified as the suspended old AA strip, not skin or truehand.
clear=np.zeros((H,W),dtype=bool) # Actual source cloth was excluded before identical warp; no target color-threshold cleanup.
nh=np.array(Image.open(G/'masks/F046_fixed_near_distal_and_original_sourceover_AA_guard.png'))>0
perm=upper|inner|placket|clear;diff=np.any(out!=v,2);assert not (diff&~perm).any();assert np.array_equal(out[nh],v[nh])
p=D/'candidates/S08_F046_same_raw_three_interfaces_RGBA.png';Image.fromarray(out).save(p)
for n,m in [('RESTORE_complete_original043_upper_collar',upper),('ADOPT_complete_raw_inner_sleeve_lapel_edge',inner),('ADOPT_actual_raw_placket_to_forearm_occlusion',placket),('CLEAR_suspended_raw_neutral_outer_AA_strip',clear),('EXPLICIT_three_interfaces_union',perm),('ACTUAL_change',diff)]:Image.fromarray(m.astype('uint8')*255).save(D/'masks'/f'{n}.png')
rep={'status':'THREE_INTERFACES_SAME_RAW_PENDING_INCREMENTAL_REVIEW','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed':int(diff.sum()),'target_outer_AA_color_clear':0,'source_cloth_band_excluded_before_same_warp':True,'placket_source_y_scale_below800':1.25,'near_true_distal_change':0,'outside_explicit_union_change':0,'arm_geometry': 'same forearm warp and true hand; source whiteflower cloth band removed beforewarp; original collar and raw sleeve/placket joins only','native_calls':21};(D/'geometry/THREE_INTERFACE_CHECKS.json').write_text(json.dumps(rep,indent=2))
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(out));old=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(a));bg.convert('RGB').save(D/'qa'/f'candidate_{tag}.png');pan=Image.new('RGB',(1660,750),col[:3]);pan.paste(old.crop((640,280,1470,1030)),(0,0));pan.paste(bg.crop((640,280,1470,1030)),(830,0));pan.save(D/'qa'/f'F043_F046_actual_same_scale_{tag}.png')
 for n,box,sc in [('whole_arm',(700,680,1470,1020),2),('near_wrist',(1130,760,1290,910),4),('shoulder_body',(815,680,1040,890),4)]:
  cc=bg.crop(box);cc.resize((cc.width*sc,cc.height*sc)).save(D/'qa'/f'{n}_{tag}.png')
print(json.dumps(rep,indent=2))
