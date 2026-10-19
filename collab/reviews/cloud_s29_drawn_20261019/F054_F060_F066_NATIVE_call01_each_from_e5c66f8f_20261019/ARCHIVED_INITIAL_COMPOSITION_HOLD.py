from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,sys
R=Path(__file__).resolve().parent;B=R.parent;G=B/'F054_F060_F066_FULL_TARGET_GATE_ZERO_CALL_20261019';P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sm(a,p):Image.fromarray(a).save(p)
def poly(pts):
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def comp(*aa):
 a=Image.new('RGBA',(1024,1536))
 for x in aa:a.alpha_composite(Image.fromarray(x))
 return np.array(a)
Y,X=np.indices((1536,1024));propsp=P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png';props=rgba(propsp);pm=props[:,:,3]>0;feather=mask(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png')
farpoly=poly([(478,354),(530,354),(630,480),(730,510),(790,565),(805,705),(680,705),(650,638),(622,631),(592,622),(558,606),(522,565),(495,578),(492,527),(498,465),(495,414)])
headpoly=poly([(215,25),(640,25),(640,335),(523,372),(488,417),(425,416),(383,357),(345,323),(260,299),(217,270)])
for f in map(int,sys.argv[1:]):
 d=R/f'F{f:03d}';q=d/'reintegration';q.mkdir(exist_ok=True);rawp=d/f'originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png';raw=rgba(rawp);target=rgba(d/'inputs/01_THIS_STATE_COMPLETE_UNANNOTATED_TARGET_RGBA.png');clothp=d/'inputs/03_THIS_STATE_SAME_SOURCE_CLOTH_RGBA.png';cloth=rgba(clothp)
 headguard=headpoly&(target[:,:,3]>0)
 rgb=raw[:,:,:3].astype(float);shirt=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15);skin=(rgb[:,:,0]>120)&(rgb[:,:,1]>65)&(rgb[:,:,2]>90)&(rgb[:,:,0]>rgb[:,:,2]+25);jade=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
 seed=(shirt|skin|jade)&(raw[:,:,3]>128)&(Y>=300)&(Y<=935)&(X>=40)&(X<=795);lab,_=nd.label(nd.binary_closing(seed,iterations=1));m=nd.binary_dilation(nd.binary_fill_holes(lab==lab[500,350]),iterations=1)&(raw[:,:,3]>0)
 # Keep the complete freshly drawn blouse rather than cutting flower stamps at
 # the former arm rectangle. Both sleeves, full blouse and whole arms are one
 # native-human source; head/legs/props/cotton stay separately protected.
 tr=target[:,:,:3].astype(float);ts=(tr[:,:,1]>95)&(tr[:,:,2]>135)&(tr[:,:,2]>tr[:,:,0]+15);tk=(tr[:,:,0]>120)&(tr[:,:,1]>65)&(tr[:,:,2]>90)&(tr[:,:,0]>tr[:,:,2]+25);tj=(tr[:,:,1]>tr[:,:,0]*1.05)&(tr[:,:,1]>tr[:,:,2]*1.03)&(tr[:,:,1]>50);tl,_=nd.label(nd.binary_closing((ts|tk|tj)&(target[:,:,3]>128)&(Y>=300)&(Y<=935)&(X>=40)&(X<=795),iterations=1));oldhuman=nd.binary_dilation(nd.binary_fill_holes(tl==tl[500,350]),iterations=2)
 edit=(mask(d/'inputs/FULL_WHITE_DOMAIN_BOTH_SLEEVES_ARMS_EXPOSED_BLOUSE.png')|oldhuman|m)&~headguard
 sm((edit*255).astype('uint8'),q/'COMPLETE_NATIVE_BLOUSE_BOTH_SLEEVES_ARMS_DOMAIN.png')
 human=np.zeros_like(raw);human[m&edit]=raw[m&edit];solid=m&edit&(human[:,:,3]>=128);human[solid,3]=255
 far=np.zeros_like(human);far[farpoly]=human[farpoly];body=human.copy();body[farpoly]=0
 # Exact native-blue root underlay bridges only the interior blouse seam.
 # It never restores the old wrist/jade/hand or an obsolete skin silhouette.
 rootunder=m&shirt&farpoly&(X<523)&(Y<585)&~headguard;body[rootunder]=human[rootunder]
 # ONE similarity of complete new far sleeve/arm/wrist/jade/hand, never fingers.
 root=np.array([500.,450.]);srcC=np.array({54:[715.,661.],60:[715.,665.],66:[696.,668.]}[f]);C2=np.array([711.098467936869,662.61030076984])+np.array({54:[0,0],60:[-14,3],66:[-30,8]}[f]);v=srcC-root;w=C2-root;u=np.dot(w,v)/np.dot(v,v);vrot=(w[1]*v[0]-w[0]*v[1])/np.dot(v,v);A=np.array([[u,-vrot],[vrot,u]]);t=root-A@root;inv=np.linalg.inv(A);co=np.stack([X,Y],2);co=(co-t)@inv.T
 z=far.astype(float);z[:,:,:3]*=z[:,:,3:4]/255;out=np.stack([nd.map_coordinates(z[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2);out[:,:,:3]=np.divide(out[:,:,:3],out[:,:,3:4]/255,out=np.zeros_like(out[:,:,:3]),where=out[:,:,3:4]>1e-8);farreg=np.rint(np.clip(out,0,255)).astype('uint8');farreg[farreg[:,:,3]==0]=0
 # Root seam feather occurs only in blue shirt within the open domain; all real
 # wrist/jade/fingers remain the same one similarity. No old-arm pixels returned.
 sm(human,q/'EXACT_NATIVE_HUMAN_RGBA_OPEN_DOMAIN.png');sm(farreg,q/'ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png');sm((m*255).astype('uint8'),q/'ACTUAL_NATIVE_HUMAN_COMPONENT_MASK.png')
 base=target.copy();base[edit]=0
 # All original finite front lip is kept; never restore neck ink through skin.
 cover=mask(G/f'F{f:03d}/ACTUAL_OUTER_FEATHER_COVER_MASK.png');front=mask(G/f'F{f:03d}/FINITE_FRONT_LIP_DOMAIN_MASK.png');lip=np.zeros_like(cloth);use=front&(~pm|feather);lip[use]=cloth[use]
 final=comp(base,cloth,props,lip,body,farreg);final[headguard]=target[headguard];final[1100:]=target[1100:]
 sm(final,q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png')
 bg=Image.new('RGBA',(1024,1536),(232,235,239,255));bg.alpha_composite(Image.fromarray(final));bg.convert('RGB').save(q/'FULL_ON_GRAY.png');bg.crop((80,450,800,925)).convert('RGB').save(q/'FULL_ARMS_CONTACTS_1TO1.png')
 nearhand=(body[:,:,3]>128)&skin&(X>=455)&(Y>=780)&(Y<=870);pov=int((nearhand&pm).sum());supp=float((cloth[:,:,3][nearhand]>128).mean())if nearhand.any()else None
 report={'state':f,'status':'PENDING_ACTUAL_NORMAL_SIZE_REINTEGRATION_REVIEW','generation_calls_state':1,'raw_SHA256':sha(rawp),'same_source_cloth_RGBA_SHA256':sha(clothp),'true_original_props_RGBA_SHA256':sha(propsp),'original_props_geometry_RGBA_changed':False,'four_original_rods_geometry_changed':False,'complete_far_group_single_similarity':{'source_root':root.tolist(),'target_root':root.tolist(),'source_material_pinch_readpoint':srcC.tolist(),'target_same_material_pinch':C2.tolist(),'matrix':A.tolist(),'translation':t.tolist(),'scale':float(np.sqrt(u*u+vrot*vrot)),'rotation_degrees':float(np.degrees(np.arctan2(vrot,u))),'contact_residual':float(np.linalg.norm(A@srcC+t-C2)),'manual_readpoint_uncertainty_pixels':3,'per_finger_transform':False},'complete_native_blossom_blouse_included_to_avoid_cut_flower_seams':True,'actual_new_native_human_foreground_used':True,'obsolete_technical_arm_or_plain_blue_shirt_returned':False,'cloth_and_generated_prop_pixels_excluded_from_human':True,'near_palm_test_region_note':'native near hand skin withx>=455,y780..870; foreground forearm is separately allowed above/in front of curved neck','near_palm_original_prop_overlap_pixels':pov,'near_palm_cloth_support_fraction':supp,'headguard_RGBA_changes':int(np.any(final[headguard]!=target[headguard],1).sum()),'candidate_RGBA_SHA256':sha(q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png')};(q/'INTEGRATION_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(f,'single far group scale',report['complete_far_group_single_similarity']['scale'],'palm overlap',pov,'support',supp)
