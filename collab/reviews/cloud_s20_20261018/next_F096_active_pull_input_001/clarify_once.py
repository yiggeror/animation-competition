"""Astra's one minimal zero-call F096 contact/root/air clarification. Pose fixed."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,map_coordinates
F=Path(__file__).resolve().parent;I=F/'inputs';S=F/'clarification_source';S.mkdir(exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
sources=[(I/'01_unique_complete_F096_target_REVIEW_ONLY.png',S/'target_before.png'),(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png',S/'upper_before.png'),(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png',S/'mask_before.png')]
for src,dst in sources:
 if not dst.exists():shutil.copyfile(src,dst)
assert sha(S/'target_before.png')=='ee067680cfddfc69fcececb4d39f393ac9e7699ff3edb2fa2bf568a8a4e80eeb'
A=np.array(Image.open(S/'target_before.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
m=json.loads((F/'INPUT_MANIFEST.json').read_text())
def poly(points):
 im=Image.new('L',(W*4,H*4));ImageDraw.Draw(im).polygon([(round(x*4),round(y*4)) for x,y in points],fill=255)
 return np.asarray(im.resize((W,H),Image.Resampling.LANCZOS)).astype(float)/255
def bez(a,b,c,d,n=60):
 t=np.linspace(0,1,n)[:,None];return ((1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)).tolist()
def line(points,width=1.1):
 im=Image.new('L',(W*4,H*4));ImageDraw.Draw(im).line([(round(x*4),round(y*4)) for x,y in points],fill=255,width=round(width*4),joint='curve')
 return np.asarray(im.resize((W,H),Image.Resampling.LANCZOS)).astype(float)/255
def shaft_guard(axis,width=6.1):
 f=np.array(axis['front']);p=np.array(axis['pin']);v=p-f;length=np.linalg.norm(v);v/=length
 along=(xx-f[0])*v[0]+(yy-f[1])*v[1];distance=abs((xx-f[0])*v[1]-(yy-f[1])*v[0])
 return (distance<width)&(along>=-5)&(along<=length+5)
rods=shaft_guard(m['T_rods'][0])|shaft_guard(m['T_rods'][1])
# Keep the actual current near-L complete palm/wrist and rear gripping fingers.
Lguard=poly([(472,395),(483,395),(498,402),(518,410),(540,430),(560,447),(562,472),(532,483),(500,482),(480,468),(472,451),(476,438),(484,433),(477,419),(469,409)])>0
fingers=poly([(406,356),(431,359),(440,370),(440,385),(443,397),(445,406),(440,414),(429,411),(418,398),(407,384),(399,369)])>0
Rdomain=poly([(400,340),(447,335),(475,355),(496,385),(510,397),(504,418),(477,432),(449,447),(425,428),(411,402),(400,372)])>0
# One simple own far-palm heel, from the genuine fourth curled finger to wrist.
heel=bez((428,410),(435,417),(444,420),(452,417))
heel+=bez((452,417),(460,415),(467,412),(474,408))[1:]
heel+=bez((474,408),(482,405),(491,403),(499,405))[1:]
hp=np.array(heel);boundary=np.interp(xx,hp[:,0],hp[:,1])
remove=Rdomain&(xx>=428)&(xx<480)&(yy>=394)&(yy<448)&(yy>boundary+.4)&~Lguard&~rods&~fingers
B=A.copy().astype(float);B[remove]=0
fill=poly([(439,396),(462,396),(477,401),(480,409),(467,414),(452,418),(441,415)])
fill[(~Rdomain)|Lguard|rods|fingers]=0
donorx=np.clip(xx+8,447,466);donory=yy-23
skin=np.stack([map_coordinates(A[:,:,k].astype(float),[donory,donorx],order=1,mode='nearest') for k in range(4)],2);skin[:,:,3]=255
B=B*(1-fill[:,:,None])+skin*fill[:,:,None]
ink=line(heel)*Rdomain;ink[Lguard|rods|fingers]=0
B=B*(1-ink[:,:,None])+np.array([91,58,38,255.])*ink[:,:,None]
# Complete small sleeve/upper-arm root ownership, not a narrow cut-strip.
Lroot=poly([(601,424),(619,426),(621,440),(607,467),(593,469),(582,458),(596,437)])
cloth=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(A[:,:,3]>150)
clothguard=binary_dilation(cloth,iterations=1)
oldedge=(r<155)&(g<135)&(b<120)
rootfill=Lroot*((A[:,:,3]<235)|oldedge);rootfill[clothguard]=0
own=np.stack([map_coordinates(A[:,:,k].astype(float),[yy,xx+20],order=1,mode='nearest') for k in range(4)],2);own[:,:,3]=255
B=B*(1-rootfill[:,:,None])+own*rootfill[:,:,None]
rootedge=bez((602,427),(598,436),(590,449),(588,456))+bez((588,456),(588,461),(592,464),(598,464))[1:]
edge=line(rootedge)*Lroot;edge[clothguard]=0
B=B*(1-edge[:,:,None])+np.array([88,56,37,255.])*edge[:,:,None]
# Clear only air before/outside the actual rigid T_S front. Keep its real tip.
air=(xx>=299)&(xx<351)&(yy>=273)&(yy<329)&~rods
B[air]=0
B=np.rint(B).clip(0,255).astype('uint8');B[B[:,:,3]<3]=0
domain=Rdomain|(Lroot>0)|air
B[~domain]=A[~domain];B[rods]=A[rods];B[Lguard]=A[Lguard]
diff=np.any(B!=A,axis=2)
assert not np.any(diff&~domain) and not np.any(diff&rods) and not np.any(diff&Lguard)
Image.fromarray(B).save(I/'01_unique_complete_F096_target_REVIEW_ONLY.png')
U=np.array(Image.open(S/'upper_before.png').convert('RGBA'));U[diff]=B[diff];Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
contact=bg.crop((260,245,745,555)).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((1455,930),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
bg.crop((570,405,680,485)).convert('RGB').save(F/'sleeve_root_1x_REVIEW_ONLY.png')
white=np.array(Image.open(S/'mask_before.png').convert('L'))>0
white|=binary_dilation(Rdomain|(Lroot>0),iterations=5)
visible=np.array(Image.open(F/'actual_retained_visible_complete_legs_shoes_mask.png').convert('L'))>0;white[visible]=False;white[736:]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
box=(570,640,785,755);card=Image.new('RGB',(430,115));card.paste(bg.crop(box).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(box),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
report={'status':'ONE_MINIMAL_ZERO_CALL_F096_CLARIFICATION_ASTRA_VISUAL_GATE_PENDING','new_image_calls':0,'source_commit':'6c7a398096cd5d7c43dc41b54ce57dc31ea56995','source_before_target_sha256':sha(S/'target_before.png'),'whole_action_rebuilt':False,'far_palm_method':'remove old near-palm ownership below own genuine curled fingers; own adjacent far-palm skin and one simple heel contour; rough construction only','near_current_complete_palm_wrist_and_grip_RGBA_changes':int((diff&Lguard).sum()),'two_true_rods_tips_axes_and_grips_RGBA_changes':int((diff&rods).sum()),'outside_three_semantic_domains_RGBA_changes':int((diff&~domain).sum()),'all_y470_plus_other_arm_torso_skirt_full_lower_RGBA_changes':int(diff[470:].sum()),'head_neck_changes':int((diff&(xx>480)&(yy<335)).sum()),'fixed_identity_input_sha256':sha(I/'03_090_identity_head_clothes_shoes_patches_only.png'),'target_png_sha256':sha(I/'01_unique_complete_F096_target_REVIEW_ONLY.png'),'adopted':False,'generation_authorized':False,'later_states_prepared':False,'exposure_frozen':False}
assert report['all_y470_plus_other_arm_torso_skirt_full_lower_RGBA_changes']==0 and report['head_neck_changes']==0
(F/'clarification_record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
