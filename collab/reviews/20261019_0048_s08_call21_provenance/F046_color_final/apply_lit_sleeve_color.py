from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;R=D.parent;V=R/'F046_same_raw_geometry_candidate_v10';P=R/'F043_FINAL_LOCKED';G=R/'F046_input_gate'
for d in ['candidates','masks','geometry','qa']:(D/d).mkdir(exist_ok=True)
p=V/'candidates/S08_F046_same_raw_three_interfaces_RGBA.png';a=np.array(Image.open(p));old=np.array(Image.open(P/'S08_F043_grandma_match_box_RGBA.png'));out=a.copy();H,W=a.shape[:2];Y,X=np.indices((H,W))
def load(p):return np.array(Image.open(p).convert('L'))>0
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([(756,687),(815,674),(846,694),(865,725),(891,751),(922,780),(959,817),(908,835),(850,880),(811,894),(775,872),(773,808),(749,752)],fill=255);sp=np.array(m)>0
r,g,b=[a[:,:,i].astype(float)for i in range(3)];blue=(b-r>35)&(g-r>15)&(b-g>15)&(r>60)&(r<180)&(a[:,:,3]>230)
origcollar=load(V/'masks/RESTORE_complete_original043_upper_collar.png');material=sp&blue&~origcollar&np.any(a!=old,2)
# Preserve lower-valued fold valleys / sleeve inner shadows; only actual exposed lit material receives the correction.
light=np.minimum.reduce([np.clip((r-92)/10,0,1),np.clip((g-143)/10,0,1),np.clip((b-199)/10,0,1)])
weight=np.clip(distance_transform_edt(material)/4,0,1)*light;weight[~material]=0
delta=np.rint(weight[:,:,None]*np.array([3,2,1])).astype(int);out[:,:,:3]=np.clip(a[:,:,:3].astype(int)+delta,0,255).astype('uint8');changed=np.any(out!=a,2)
assert np.array_equal(out[:,:,3],a[:,:,3]);nh=load(G/'masks/F046_fixed_near_distal_and_original_sourceover_AA_guard.png');seat=load(G/'masks/F046_true_low_rod_seat_core.png');box=load(G/'masks/F046_fixed_table_box_guard.png');assert not(changed&(nh|seat|box)).any()
Image.fromarray(np.rint(weight*255).astype('uint8')).save(D/'masks/F046_lit_new_sleeve_soft_weight.png');Image.fromarray(material.astype('uint8')*255).save(D/'masks/F046_lit_new_sleeve_semantic_permission.png');Image.fromarray(changed.astype('uint8')*255).save(D/'masks/F046_actual_color_changed.png')
fp=D/'candidates/S08_F046_same_raw_final_color_RGBA.png';Image.fromarray(out).save(fp)
f0=np.array(Image.open(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png'));samples=[('flat_blue1',[780,720,803,742]),('flat_blue2',[805,732,825,750]),('flat_blue3',[790,744,812,757]),('lower_lit_blue',[820,799,850,832])]
def stat(ar,bb):
 x1,y1,x2,y2=bb;z=ar[y1:y2,x1:x2].astype(int);mm=(z[:,:,3]>250)&(z[:,:,2]-z[:,:,0]>25)&(z[:,:,1]>100)&(z[:,:,0]>55)&(z[:,:,0]<175);v=z[:,:,:3][mm];return {'n':len(v),'mean':v.mean(0).tolist(),'median':np.median(v,0).tolist()}
ref=stat(f0,[639,731,680,773]);re=[]
for n,bb in samples:
 before=stat(a,bb);after=stat(out,bb);re.append({'part':n,'box':bb,'F000_reference':ref,'before':before,'after':after,'delta_after_vs000':(np.array(after['mean'])-ref['mean']).tolist()})
rep={'status':'FINAL_COLOR_CANDIDATE_PENDING_DUAL_VISUAL_AND_6F_REVIEW','source_geometry_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'native_calls':21,'new_lit_sleeve_max_RGB':[3,2,1],'changed_pixels':int(changed.sum()),'alpha_changed':0,'outside_semantic_permission_changed':int((changed&~material).sum()),'true_near_hand_rodseat_box_changed':0,'skin_changed':int((changed&((r-b)>24)&((r-g)>10)).sum()),'original_collar_changed':int((changed&origcollar).sum()),'head_y_lt674_changed':int(changed[:674].sum()),'notes':'Only actual new near sleeve lit blue. Crossing-fold upper sample is shadow diagnostic and not forced to±4. Skin and wrist, original head/chest, dark folds/inner sleeve, white flowers and ink kept. Underlying far archive remains independent; true near arm occludes it by actual contour.','samples':re};(D/'geometry/COLOR_MASK_AND_CHECKS.json').write_text(json.dumps(rep,indent=2))
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(out));prev=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(old));bg.convert('RGB').save(D/'qa'/f'candidate_{tag}.png');pan=Image.new('RGB',(1660,750),col[:3]);pan.paste(prev.crop((640,280,1470,1030)),(0,0));pan.paste(bg.crop((640,280,1470,1030)),(830,0));pan.save(D/'qa'/f'F043_F046_actual_same_scale_{tag}.png')
 for n,bb,sc in [('whole_arm',(700,680,1470,1020),2),('near_wrist',(1130,760,1290,910),4),('shoulder_body',(745,675,1040,900),3)]:
  cc=bg.crop(bb);cc.resize((cc.width*sc,cc.height*sc)).save(D/'qa'/f'{n}_{tag}.png')
 ov=np.zeros_like(out);ov[material]=[60,210,90,90];oo=Image.alpha_composite(bg,Image.fromarray(ov));oo.crop((730,660,1070,930)).resize((1020,810)).convert('RGB').save(D/'qa'/f'actual_color_permission_{tag}.png')
 fd=D/'qa'/('frames_'+tag);fd.mkdir(exist_ok=True)
 for n,z in enumerate([old,old,old,out,out,out]):Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(z)).convert('RGB').save(fd/f'{n:03d}.png')
print(json.dumps(rep,indent=2))
