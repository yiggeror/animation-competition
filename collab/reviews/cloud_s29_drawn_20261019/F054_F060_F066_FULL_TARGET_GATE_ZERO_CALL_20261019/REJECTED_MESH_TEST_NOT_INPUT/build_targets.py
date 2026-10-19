"""Zero-generation TECHNICAL INPUTS. Native skin reference + one frozen cloth source.
These deliberately incomplete technical composites are NOT finished drawn states.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
from scipy.spatial import Delaunay
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent; B=R.parent; repo=R.parents[3]
L=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019'; P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019'; PRE=B/'F036_SAME_MASTER_MAP042048_SCENE13_ZERO_CALL_20261019'
def load(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p):Image.fromarray(a).save(p)
def save_mask(m,p):save((m*255).astype('uint8'),p)
def comp(*aa):
 out=Image.new('RGBA',(1024,1536))
 for a in aa:out.alpha_composite(Image.fromarray(a))
 return np.array(out)
def premul_map(a,coords):
 p=a.astype(float);p[:,:,:3]*=p[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(p[:,:,k],[coords[:,:,1],coords[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
 z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-6)
 z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
Y,X=np.indices((1536,1024));pix=np.column_stack([X.ravel(),Y.ravel()])
def mesh_coords(src,dst):
 tri=Delaunay(dst);si=tri.find_simplex(pix);valid=si>=0;ss=np.maximum(si,0);b2=np.einsum('ijk,ik->ij',tri.transform[ss,:2],pix-tri.transform[ss,2]);ba=np.column_stack([b2,1-b2.sum(1)]);co=np.einsum('ij,ijk->ik',ba,src[tri.simplices[ss]]);co[~valid]=-100
 sv=src[tri.simplices];tv=dst[tri.simplices];sd=np.linalg.det(np.stack([sv[:,1]-sv[:,0],sv[:,2]-sv[:,0]],2));td=np.linalg.det(np.stack([tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]],2));ratio=np.divide(td,sd,out=np.zeros_like(td),where=np.abs(sd)>1e-8)
 return co.reshape(1536,1024,2),{'inverted_triangles':int((ratio<=0).sum()),'min_signed_area_ratio':float(ratio.min()),'source_landmarks':src.tolist(),'target_landmarks':dst.tolist(),'triangles':tri.simplices.tolist()}
def ongray(a):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
lockedp=L/'F048/CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png';locked=load(lockedp)
masterp=L/'ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png';master=load(masterp)
rawp=B/'F036_SINGLE_CLEAN_CLOTH_MASTER_NATIVE_CALL01_20261019/RAW_UNTOUCHED.png';raw=load(rawp)
propp=P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png';props=load(propp);pm=props[:,:,3]>0
far=load(L/'F048/EXACT_CURRENT_ARM_FOREGROUND_RGBA.png');near_domain=mask(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png')
rgb=locked[:,:,:3].astype(float);skin=(rgb[:,:,0]>rgb[:,:,2]+27)&(rgb[:,:,0]>110)&(rgb[:,:,1]>65)&(locked[:,:,3]>0)
lab,_=nd.label(nd.binary_closing(skin&near_domain,iterations=2));oldnear=nd.binary_dilation(nd.binary_fill_holes(lab==lab[670,175]),iterations=2)&near_domain
save_mask(oldnear,R/'LOCKED048_OLD_NEAR_ARM_REMOVAL_MASK.png')
# Newly revealed material: only alpha-bearing pixels of the SAME raw, near old hand.
reveal=nd.binary_dilation(oldnear,iterations=3)&(X>=360)&(Y>=690)&(master[:,:,3]<128)&(raw[:,:,3]>0)
extended=master.copy();extended[reveal]=raw[reveal];extended[reveal&(raw[:,:,3]>=128),3]=255
save(extended,R/'SAME_MASTER_ONLY_NEAR_RELEASE_SOURCE_EXTENSION_RGBA.png');save_mask(reveal,R/'SAME_RAW_NEAR_RELEASE_EXTENSION_ONLY_MASK.png')
# Both original arm silhouettes are removed; the exposed shirt is an explicitly
# marked low-detail volume guide, never invented cotton or a final native body.
base=locked.copy();base[oldnear|(far[:,:,3]>0)]=0
shirt=Image.new('RGBA',(1024,1536));sd=ImageDraw.Draw(shirt);sd.polygon([(115,585),(230,610),(260,643),(405,652),(470,662),(525,735),(455,805),(350,818),(120,755)],fill=(102,158,221,255))
sh=np.array(shirt);sh[:,:,:3]=np.clip(sh[:,:,:3].astype(float)*(1-.08*np.clip((Y-610)/220,0,1)[:,:,None]),0,255).astype('uint8');sh[sh[:,:,3]==0]=0
# Patch only the genuinely missing skin silhouette; retain source blouse outside.
unknown=oldnear&(extended[:,:,3]<128);patch=np.zeros_like(sh);patch[unknown]=sh[unknown];base=comp(base,patch)
save_mask(unknown,R/'EXPOSED_SHIRT_MUST_BE_NATIVE_REDRAW_MASK.png')
# Pure skin/ink source; no old P cloth, old P shirt or old far hand enters targets.
palmp=repo/'collab/reviews/20261017_1813_s29_complete_candidates/complete6_actual/raw/P.png';palma=load(palmp);palmask=mask(R/'P_NATIVE_BARE_NEAR_ARM_ONLY_MASK.png');skinonly=np.zeros_like(palma);skinonly[palmask]=palma[palmask]
CS=np.array([287.,631.]);ES=np.array([280.,708.]);WS=np.array([493.,756.]);C=np.array([174.,611.]);upper=90.;fore=270.
def ik(W):
 v=W-C;d=np.linalg.norm(v);u=v/d;n=np.array([-u[1],u[0]]);a=(upper**2-fore**2+d*d)/(2*d);h=np.sqrt(max(0,upper**2-a*a));return C+a*u+h*n
# A native-reference arm guide articulated as whole upper arm/forearm/palm.
def native_arm(W,deg):
 E=ik(W);srct=np.array([(x,y)for y in range(590,837,14)for x in range(214,648,14)],float)
 srcu=(ES-CS)/np.linalg.norm(ES-CS);srcun=np.array([-srcu[1],srcu[0]]);dstu=(E-C)/upper;dstun=np.array([-dstu[1],dstu[0]])
 srcf=(WS-ES)/np.linalg.norm(WS-ES);srcfn=np.array([-srcf[1],srcf[0]]);dstf=(W-E)/fore;dstfn=np.array([-dstf[1],dstf[0]])
 v=srct-CS;u=C+(v@srcu)[:,None]*dstu*(upper/np.linalg.norm(ES-CS))+(v@srcun)[:,None]*dstun*1.15
 v=srct-ES;f=E+(v@srcf)[:,None]*dstf*(fore/np.linalg.norm(WS-ES))+(v@srcfn)[:,None]*dstfn*1.15
 blend=np.clip((srct[:,1]-674)/36,0,1);dst=u*(1-blend[:,None])+f*blend[:,None]
 z=np.deg2rad(deg);A=.9*np.array([[np.cos(z),-np.sin(z)],[np.sin(z),np.cos(z)]]);hand=(srct-WS)@A.T+W
 blend=np.clip((srct[:,0]-462)/30,0,1);dst=dst*(1-blend[:,None])+hand*blend[:,None]
 coords,m=mesh_coords(srct,dst);a=premul_map(skinonly,coords)
 # Exact whole-palm transformed source domain for contact verification.
 handsource=skinonly.copy();handsource[X<493]=0;hm=premul_map(handsource,coords)[:,:,3]>128
 m.update({'native_source_cuff':CS.tolist(),'native_source_elbow':ES.tolist(),'native_source_wrist':WS.tolist(),'target_cuff':C.tolist(),'target_elbow':E.tolist(),'target_wrist':W.tolist(),'projected_upper_guide_length':float(np.linalg.norm(E-C)),'projected_forearm_guide_length':float(np.linalg.norm(W-E)),'whole_palm_rotation_degrees':deg,'whole_palm_uniform_scale':.9,'not_measured_3D_bones':True})
 return a,hm,m
oldmap=json.loads((PRE/'F048/MAPPING_CHECK.json').read_text());msrc=np.array(oldmap['source_landmarks']);mdst=np.array(oldmap['target_landmarks']);C2=np.array([711.098467936869,662.61030076984])
feather=mask(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png');cover0=mask(S/'masks/ONLY_ACTUAL_SOFT_LIP_ALLOWED_REAL_OUTER_FEATHER_COVER.png');previouscover=cover0.copy()
reports=[];panels=[]
for frame,delta,W,deg in [(54,np.array([0.,0.]),np.array([402.,657.]),-12),(60,np.array([-14.,3.]),np.array([470.,805.]),6),(66,np.array([-30.,8.]),np.array([470.,805.]),6)]:
 d=R/f'F{frame:03d}';d.mkdir(exist_ok=True)
 # Extra supported-lap anchor; all three targets share one source material.
 src=np.vstack([msrc,[[535,835],[420,820],[650,840]]]);dst=np.vstack([mdst,[[535,835],[420,820],[650,840]]])
 w=np.maximum(0,1-np.abs(dst[:,0]-C2[0])/240)**2*np.maximum(0,1-np.abs(dst[:,1]-C2[1])/270)**2;w[(dst[:,1]>=835)|(dst[:,0]<=499)]=0
 dst+=w[:,None]*delta
 # Existing continuous lip/T moves with inward fold; lower lap/ridge fixed.
 it=np.where(np.linalg.norm(src-[842,807],axis=1)<.1)[0][0];dst[it]+={54:[0,0],60:[-7,-4],66:[-14,-8]}[frame]
 coords,clothmeta=mesh_coords(src,dst);assert clothmeta['inverted_triangles']==0
 cloth=premul_map(extended,coords);save(cloth,d/'ONE_SAME_MATERIAL_MAPPED_CLOTH_RGBA.png');(d/'CLOTH_MAPPING.json').write_text(json.dumps(clothmeta,indent=2)+'\n')
 # Foreground far wrist/jade/hand stay a single rigid group; root is stationary.
 fw=np.clip((X-545)/80,0,1);fw=fw*fw*(3-2*fw);fcoords=np.stack([X-fw*delta[0],Y-fw*delta[1]],2);fararm=premul_map(far,fcoords)
 neararm,handmask,armmeta=native_arm(W,deg);save(neararm,d/'NEAR_FULL_ARM_NATIVE_REFERENCE_GUIDE_RGBA.png');save(fararm,d/'FAR_FULL_ARM_NATIVE_REFERENCE_GUIDE_RGBA.png')
 # Finite lip facet. Its only puppet overlap is the original outer feather.
 lip=Image.new('L',(1024,1536));ld=ImageDraw.Draw(lip)
 if frame>=60:ld.polygon([(827,795),(853,809),(859,819),(846,822),(824,808)],fill=255)
 if frame>=66:ld.polygon([(814,783),(850,802),(860,814),(852,825),(818,800)],fill=255)
 frontdomain=(np.array(lip)>0)&(cloth[:,:,3]>128);frontdomain|=cover0
 cover=previouscover|(frontdomain&feather);assert np.all(cloth[cover,3]>128);previouscover=cover.copy()
 # Visible front cloth is exactly mapped source cloth. No puppet or rod is warped.
 liprgba=np.zeros_like(cloth);liprgba[frontdomain&(~pm|feather)]=cloth[frontdomain&(~pm|feather)]
 save_mask(cover,d/'ACTUAL_OUTER_FEATHER_COVER_MASK.png');save_mask(frontdomain,d/'FINITE_FRONT_LIP_DOMAIN_MASK.png')
 target=comp(base,cloth,props,liprgba,fararm,neararm);save(target,d/f'F{frame:03d}_TECHNICAL_INPUT_NOT_NATIVE_RGBA.png')
 hm=handmask;overlap=int((hm&pm).sum());support=float((cloth[:,:,3][hm]>128).mean())
 # Native redraw union includes whole near arm and revealed shirt, never fingers alone.
 edit=nd.binary_dilation(oldnear|(neararm[:,:,3]>0)|unknown|(fararm[:,:,3]>0)|(far[:,:,3]>0),iterations=8)&(Y>=420)&(Y<=880)
 save_mask(edit,d/'WHOLE_ARMS_AND_EXPOSED_SHIRT_NATIVE_REDRAW_MASK.png')
 report={'frame':frame,'exposure':[frame,frame+5],'status':'TECHNICAL_INPUT_GATE_PENDING_ASTRA_NOT_FINISHED_NATIVE_DRAWING','generation_calls':0,'near_state':{54:'fully release neck3; entire open palm above cloth/crane',60:'palm lands on clear cloth beside crane; pressure support',66:'same palm stabilizes folded cloth'}[frame],'far_state':'same material point remains pinched; whole jade/wrist/hand follows inward lip','far_delta_from048':delta.tolist(),'far_contact_target':(C2+delta).tolist(),'far_contact_source_material_point_same':True,'whole_near_arm':armmeta,'near_whole_palm_props_overlap_pixels':overlap,'near_whole_palm_cloth_alpha_coverage_fraction':support,'palm_support_required':frame>=60,'outer_feather_cover_pixels':int(cover.sum()),'original_props_RGBA_SHA256':sha(propp),'original_props_geometry_changed':False,'four_original_rods_geometry_changed':False,'same_master_SHA256':sha(masterp),'source_raw_SHA256':sha(rawp),'unknown_shirt_is_unfinished_volume_guide':True}
 if frame>=60:assert overlap==0 and support>.99,(frame,overlap,support)
 (d/'CONTACT_AND_ARM_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report)
 full=ongray(target);annot=full.copy();ad=ImageDraw.Draw(annot)
 ad.rectangle((0,0,1024,36),fill='white');ad.text((12,10),f'F{frame:03d} x6 | TECHNICAL INPUT ONLY - NATIVE WHOLE-ARM / SHIRT DRAWING STILL REQUIRED',fill='black')
 for name,pt,col in [('C',C,'#00b7cd'),('E',np.array(armmeta['target_elbow']),'#00b7cd'),('W',W,'#00b7cd'),('same cloth C2',C2+delta,'#e63d85')]:
  x,y=pt;ad.ellipse((x-4,y-4,x+4,y+4),fill=col);ad.text((x+6,y-14),name,fill=col,stroke_width=1,stroke_fill='white')
 ad.line([tuple(C),tuple(armmeta['target_elbow']),tuple(W)],fill='#00b7cd',width=2)
 # Neck support release and grounded lap remain separate, actual source coordinates.
 ad.ellipse((493,741,505,753),outline='#ff7000',width=2);ad.text((505,745),'old neck3 support: RELEASED',fill='#b34c00',stroke_width=1,stroke_fill='white')
 ad.text((530,930),'same supported lap / original 4 rods',fill='#267a34',stroke_width=1,stroke_fill='white')
 annot.save(d/f'F{frame:03d}_WHOLE_ARMS_CONTACTS_TECHNICAL.png');full.crop((100,450,1024,1010)).save(d/'ARMS_CLOTH_PROPS_1TO1.png')
 panels.append(annot)
sheet=Image.new('RGB',(1536,800),(232,235,239));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(panels):sheet.paste(p.resize((512,768)),(i*512,32));dr.text((i*512+10,10),['054 RELEASE + HOVER','060 LAND ON CLOTH','066 HOLD + INWARD FOLD'][i],fill='black')
sheet.save(R/'THREE_FULL_TECHNICAL_TARGETS_REVIEW.png')
normal=Image.new('RGB',(1848,1160),(232,235,239));dr=ImageDraw.Draw(normal)
for i,f in enumerate([48,54,60,66]):
 a=locked if f==48 else load(R/f'F{f:03d}/F{f:03d}_TECHNICAL_INPUT_NOT_NATIVE_RGBA.png');normal.paste(ongray(a).crop((100,450,1024,1010)),((i%2)*924,(i//2)*580+20));dr.text(((i%2)*924+8,(i//2)*580+4),f'F{f:03d} | '+('LOCKED native start'if f==48 else 'TECHNICAL reference, not native final'),fill='black')
normal.save(R/'LOCKED048_TO_THREE_TARGETS_ARMS_1TO1.png')
(R/'ZERO_CALL_SOURCE_AND_GEOMETRY_CHECK.json').write_text(json.dumps({'generation_calls':0,'renders':0,'locked048_SHA256':sha(lockedp),'master_SHA256':sha(masterp),'raw_SHA256':sha(rawp),'source_near_native_reference':str(palmp.relative_to(repo)),'source_near_native_reference_SHA256':sha(palmp),'old_near_arm_removed_pixels':int(oldnear.sum()),'same_raw_source_extension_pixels':int(reveal.sum()),'extension_RGB_differences_from_raw':int(np.any(extended[reveal,:3]!=raw[reveal,:3],1).sum()),'unknown_revealed_shirt_guide_pixels':int(unknown.sum()),'states':[{k:v for k,v in r.items()if k!='whole_near_arm'}for r in reports]},indent=2)+'\n')
print(json.dumps([{k:r[k]for k in ['frame','near_whole_palm_props_overlap_pixels','near_whole_palm_cloth_alpha_coverage_fraction','outer_feather_cover_pixels']}for r in reports],indent=2))
