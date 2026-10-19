from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation,binary_fill_holes,map_coordinates,distance_transform_edt
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F046_input_gate';N=R/'F046_result_nominal';P=R/'F043_FINAL_LOCKED';C=R/'F046_same_raw_geometry_candidate_v9_base'
for d in ['candidates','qa','masks','geometry','registered']:(C/d).mkdir(parents=True,exist_ok=True)
q=np.array(Image.open(N/'registered/F046_registered_scene_patch_RGBA.png').convert('RGBA'));a=np.array(Image.open(P/'S08_F043_grandma_match_box_RGBA.png'));pre=np.array(Image.open(G/'inputs/F046_scene_preplaced_NO_ROD_RGBA.png'));H,W=a.shape[:2];Y,X=np.indices((H,W));w=np.array(Image.open(G/'masks/F046_WHITE_near_sleeve_arm_wrist_and_exposed_background.png'))>0
load=lambda p:np.array(Image.open(p).convert('L'))>0
def poly(pts):
 z=Image.new('L',(W,H));ImageDraw.Draw(z).polygon(pts,fill=255);return np.array(z)>0
def save(name,m):Image.fromarray(m.astype('uint8')*255).save(C/'masks'/f'{name}.png')
E=np.array([975.,914.]);WS=np.array([1158.,791.]);WT=np.array([1204.847686868556,829.476655293115]);vs=WS-E;vt=WT-E;Ls=np.linalg.norm(vs);Lt=np.linalg.norm(vt);es=vs/Ls;ns=np.array([-es[1],es[0]]);et=vt/Lt;theta=np.arctan2(np.cross(es,et),np.dot(es,et));k=Lt/Ls
# Round elbow retained. Smooth cubic centreline distributes the forearm turn, instead of concentrated point-axis rotation.
from scipy.spatial import cKDTree
u0=30.;span=Ls-u0;P0=E+u0*es;P1=P0+es*(span/3);P2=WT-et*(np.linalg.norm(WT-P0)/3);P3=WT

def curve(u):
 z=np.clip((u-u0)/span,0,1);zz=z[...,None];C0=(1-zz)**3*P0+3*(1-zz)**2*zz*P1+3*(1-zz)*zz**2*P2+zz**3*P3
 D=3*((1-zz)**2*(P1-P0)+2*(1-zz)*zz*(P2-P1)+zz**2*(P3-P2))/span
 DD=6*((1-zz)*(P2-2*P1+P0)+zz*(P3-2*P2+P1))/(span*span)
 low=u<=u0;high=u>=Ls
 C0[low]=E+u[low,None]*es;D[low]=es;DD[low]=0
 C0[high]=WT+(u[high,None]-Ls)*et*k;D[high]=et*k;DD[high]=0
 return C0,D,DD
sample=np.arange(-500,601,.5);cs,_,_=curve(sample);points=np.stack((X,Y),2).reshape(-1,2);tree=cKDTree(cs);_,idx=tree.query(points,workers=2);u=sample[idx].reshape(H,W)
for _ in range(4):
 cc,dd,ddd=curve(u);err=cc-np.stack((X,Y),2);du=np.sum(err*dd,2)/np.maximum(np.sum(dd*dd,2)+np.sum(err*ddd,2),.2);u-=np.clip(du,-2,2)
cc,dd,ddd=curve(u);nn=np.stack((-dd[:,:,1],dd[:,:,0]),2);nn/=np.linalg.norm(nn,axis=2)[:,:,None];v=np.sum((np.stack((X,Y),2)-cc)*nn,2);sx=E[0]+u*es[0]+v*ns[0];sy=E[1]+u*es[1]+v*ns[1];coords=np.array([sy,sx])
rr,gg,bb=[q[:,:,i].astype(int)for i in range(3)];skin=(rr-bb>24)&(rr-gg>10)&(rr>110)&(q[:,:,3]>100)&(X>830)&(X<1330)&(Y>700)&(Y<975);lab,num=label(skin);nearlabel=lab[910,970];assert nearlabel>0;nearskin=binary_fill_holes(lab==nearlabel);nearfull=binary_dilation(nearskin,iterations=3)&(q[:,:,3]>0)
# Retain the complete actual near skin up to the proximal wrist collar only; discard the model's wrong hand/match.
Us=(X-E[0])*es[0]+(Y-E[1])*es[1];source_skin=nearfull&(Us<Ls+14);blue_edge=(bb-rr>10)&(bb-gg>7)&(np.maximum.reduce([rr,gg,bb])>80);source_skin&=~blue_edge
false_cloth_band=(X>=1118)&(X<=1144)&(X+Y>=1972)&(X+Y<=1980);source_skin&=~false_cloth_band
# Independent skin warp keeps the entire round elbow and near upper-arm pixels.
source_arm=source_skin
z=q.copy();z[~source_arm]=0;pa=z[:,:,3].astype(float)/255;pm=z[:,:,:3].astype(float)*pa[:,:,None];wa=map_coordinates(pa,coords,order=1,mode='constant',cval=0);wp=np.stack([map_coordinates(pm[:,:,j],coords,order=1,mode='constant',cval=0)for j in range(3)],2);wrgb=np.divide(wp,np.maximum(wa[:,:,None],1e-9));warp=np.dstack((np.rint(wrgb).clip(0,255).astype('uint8'),np.rint(wa*255).clip(0,255).astype('uint8')));warp[warp[:,:,3]==0]=0
# Keep actual043 chest/body. Clear only obsolete near skin/hand; restored far anatomy is an independent back layer.
body=np.array(Image.open(R/'F043_LAYER_PARTITION/frames/F043_body_behind_original_pixels.png'));bodyvis=body[:,:,3]>0
nearenv=poly([(832,852),(945,795),(1020,836),(1100,835),(1230,785),(1442,773),(1450,900),(1280,925),(1100,966),(992,972),(915,938),(832,876)])
old_arm=load(R/'F043_LAYER_PARTITION/masks/F043_arms_binary.png')&nearenv
oldhand=load(P/'F043_true_near_hand_match_INDEPENDENT_FOREGROUND_footprint.png')
ar,ag,ab=[a[:,:,i].astype(int)for i in range(3)];oldskin=(ar-ab>24)&(ar-ag>10)&(ar>110)&(a[:,:,3]>100)&(Y>790);ol,nn=label(oldskin);oldskin=binary_fill_holes(ol==ol[905,990]);clear_native=(binary_dilation(oldskin,iterations=3)&nearenv)|oldhand
base=a.copy();base[clear_native]=0
# Genuine visible far forearm that pre-exists above the old near forearm.
fararm=poly([(1051,861),(1057,849),(1080,835),(1101,822),(1121,812),(1134,814),(1144,839),(1107,846)])
base[fararm]=a[fararm]
# Raw blue cloth is used only for newly uncovered torso, not original chest replacements.
raw_cloth_roi=poly([(832,849),(930,835),(1032,893),(1026,976),(882,978),(806,929)])
restore_body=clear_native&~bodyvis&raw_cloth_roi&(q[:,:,3]>0)&~binary_dilation(skin,iterations=2)
base[restore_body]=q[restore_body]
# Complete shoulder-to-sleeve corridor: native sleeve lower part unchanged, shoulder cap smoothly registered to the original fixed shoulder.
source_blue=poly([(735,680),(875,680),(917,742),(970,815),(970,835),(910,862),(870,900),(815,925),(730,910)])&(q[:,:,3]>0)&~source_skin
sl=q.copy();sl[~source_blue]=0
zz=np.clip((Y-705)/115,0,1);smooth=zz*zz*(3-2*zz);lateral=np.clip((845-X)/50,0,1)
# Up to28px horizontal cap correction, exactly0 at/below820. Forearm and native cuff not affected.
srcx=X+28*(1-smooth)*lateral;srcy=Y.astype(float);co=np.array([srcy,srcx]);aa=sl[:,:,3]/255.;pp=sl[:,:,:3].astype(float)*aa[:,:,None]
sa=map_coordinates(aa,co,order=1,mode='constant',cval=0);sp=np.stack([map_coordinates(pp[:,:,j],co,order=1,mode='constant',cval=0)for j in range(3)],2)
sleeve_zone=poly([(710,680),(875,680),(917,742),(964,793),(974,838),(915,866),(874,904),(815,930),(710,918)])
t=np.clip((Y-683)/12,0,1);t=t*t*(3-2*t);origalpha=a[:,:,3]/255.;origpm=a[:,:,:3].astype(float)*origalpha[:,:,None]
ba=origalpha*(1-t)+sa*t;bp=origpm*(1-t[:,:,None])+sp*t[:,:,None];br=np.divide(bp,np.maximum(ba[:,:,None],1e-9));sleeve=np.dstack((np.rint(br).clip(0,255).astype('uint8'),np.rint(ba*255).clip(0,255).astype('uint8')));sleeve[sleeve[:,:,3]==0]=0
# Overlay only actual cloth. Transparent source outside the inner polygon is not a hole in the fixed chest.
leftedge=np.full(H,10000.)
for yy in range(680,918):
 xx=np.where((sleeve[yy,:,3]>100)&sleeve_zone[yy])[0]
 if len(xx):leftedge[yy]=float(xx.min())
outer_clear=sleeve_zone&(X<leftedge[:,None])&(X<800)&(Y<890)
base[outer_clear]=0
adoptcloth=sleeve_zone&(sleeve[:,:,3]>0)
# The inner cuff and silhouette remain exact; internal blue-cloth joins feather only where both actual sources are opaque.
innerdistance=distance_transform_edt(sleeve_zone);bfactor=np.clip(innerdistance/8.,0,1)
blues=(base[:,:,2].astype(int)-base[:,:,0].astype(int)>5)&(base[:,:,3]>230)&(sleeve[:,:,3]>230)
weight=np.where(blues,bfactor,1.)
repl=sleeve.copy();repl[:,:,:3]=np.rint(base[:,:,:3]*(1-weight[:,:,None])+sleeve[:,:,:3]*weight[:,:,None]).astype('uint8')
lowpolyAA=adoptcloth&(repl[:,:,3]<230)&(base[:,:,3]>230)&(X>leftedge[:,None]+3)
ww=repl[:,:,3]/255.;repl[lowpolyAA,:3]=np.rint(repl[lowpolyAA,:3]*ww[lowpolyAA,None]+base[lowpolyAA,:3]*(1-ww[lowpolyAA,None])).astype('uint8');repl[lowpolyAA,3]=base[lowpolyAA,3]
base[adoptcloth]=repl[adoptcloth]
# Extend permission only over this disclosed continuous shoulder/sleeve corridor.
original_white=w.copy();w|=sleeve_zone
farunder=np.array(Image.open(P/'F043_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png'));ff=load(P/'F043_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png');jaa=load(P/'F043_far_original_jade_AA_requires_same_raw_skin_underlay.png');base[ff]=farunder[ff];base[jaa]=a[jaa]
com=Image.alpha_composite(Image.fromarray(base),Image.fromarray(warp));n=np.array(Image.open(G/'inputs/F046_true_near_hand_match_INDEPENDENT_RGBA.png'));nh=load(G/'masks/F046_fixed_near_distal_and_original_sourceover_AA_guard.png');root=load(G/'masks/F046_near_proximal_collar_release.png');under=np.array(com);com=Image.alpha_composite(com,Image.fromarray(n));z=np.array(com)
# Original complete collar alpha supplies real outer edge; its RGB seam is internally feathered into actual native skin, never fill a transparent hole.
blend=root&(under[:,:,3]>230)&(n[:,:,3]>230)&~nh
wt=np.clip((X-1191)/18,0,1);wt=wt*wt*(3-2*wt)
z[blend,:3]=np.rint(under[blend,:3]*(1-wt[blend,None])+z[blend,:3]*wt[blend,None]).astype('uint8')
# Immutable NO_ROD preplacement is the black-domain anchor. Only white-domain native materials may change here.
out=pre.copy();out[w]=z[w];out[nh]=pre[nh]
res=Image.fromarray(out);dest=C/'candidates/S08_F046_same_raw_arm_geometry_DIAGNOSTIC_RGBA.png';res.save(dest);Image.fromarray(warp).save(C/'registered/ACTUAL_native_near_arm_transformed_only_RGBA.png');Image.fromarray(base).save(C/'registered/ACTUAL_native_body_and_original_far_underlay_RGBA.png')
for name,m in [('SOURCE_complete_near_skin_capped_before_wrong_hand',source_skin),('SOURCE_actual_blue_sleeve',source_blue),('CLEAR_native_wrong_foreground_and_lower_far_hand',clear_native),('RESTORE_original043_actual_body_exposed_under_old_native_arm',restore_body),('ACTUAL_transformed_near_arm_alpha',warp[:,:,3]>0),('EXPLICIT_white_permission',w),('RELEASE_complete_shoulder_sleeve_corridor',sleeve_zone),('RELEASE_added_beyond_input_white',w&~original_white),('RESTORE_original_far_forearm_visible',fararm),('COLLAR_internal_source_skin_feather',blend),('EXCLUDE_source_whiteflower_cloth_below_actual_black_forearm',false_cloth_band),('CLEAR_old_outer_sleeve_only',outer_clear),('ADOPT_actual_raw_sleeve_cloth',adoptcloth)]:save(name,m)
for tag,bgcol in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),bgcol),res);orig=Image.alpha_composite(Image.new('RGBA',(W,H),bgcol),Image.fromarray(a));bg.convert('RGB').save(C/'qa'/f'candidate_{tag}.png');pan=Image.new('RGB',(1660,750),bgcol[:3]);pan.paste(orig.crop((640,280,1470,1030)),(0,0));pan.paste(bg.crop((640,280,1470,1030)),(830,0));pan.save(C/'qa'/f'F043_F046_actual_same_scale_{tag}.png')
 for name,bb,sc in [('whole_arm',(700,680,1470,1020),2),('near_wrist',(1130,760,1290,910),4),('elbow',(875,845,1060,990),4)]:
  cc=bg.crop(bb);cc.resize((cc.width*sc,cc.height*sc)).save(C/'qa'/f'{name}_{tag}.png')
 grid=bg.copy();d=ImageDraw.Draw(grid);d.line((690,981,1470,981),fill=(230,85,55),width=2);grid.crop((700,680,1470,1020)).resize((1540,680)).save(C/'qa'/f'actual_elbow_with_table981_{tag}.png')
rep={'status':'ZERO_CALL_GEOMETRY_DIAGNOSTIC_REVISED_ELBOW_ROUTE_NOT_APPROVED','candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_raw_sha256':'3f2793867cf321aaf5a54ed1bb2d59022f6683181bfe75d3ae7b6d7a886fa3ea','elbow_fixed_actual':[975,914],'wrist_source':WS.tolist(),'wrist_target_actual_collar':WT.tolist(),'source_forearm_projection':float(Ls),'target_projection':float(Lt),'axial_factor':float(k),'rotation_clockwise_deg':float(np.rad2deg(theta)),'terminal_axis_calibration_y_plus6':'Actual native wrist section was about6px above original collar section; source cross-section unchanged; actual endpoints now meet source collar edges','sleeve_cap_horizontal_correction_max28_to_zero_y820':True,'explicit_added_permission_pixels':int((w&~original_white).sum()),'transverse_factor':1,'round_elbow_unchanged_radius_forearm30px':True,'smooth_transition_forearm_distance':[30,float(Ls)],'method':'cubic centreline: tangent continuous at elbow; cross-sectional thickness1; original sleeve unwarped; real independent palm-root collar restored for connection','outside_white_diff_vs_NO_ROD':int(np.sum(np.any(out!=pre,2)&~w)),'near_hard_changed':int(np.sum(np.any(out[nh]!=pre[nh],1))),'notes':'Original raw sleeve/upper arm/round elbow kept; only continuous foreground forearm remapped. Wrong native hands/match/far lower arm not adopted. Old sourcecloth restored only where actual043 body visible. Some boundary/underlay and wrist collar gaps may remain and must be actually reviewed; no final claim.'};(C/'geometry/DEFORMATION_AND_CHECKS.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
