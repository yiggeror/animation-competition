"""Visible F086 REFERENCE ONLY from sole FINAL082. No image model/real Canvas.
Hip/thighs advance; torso/head rise; both full arms/true closed grips/props use
ONE shared rigid arm transform. Fixed real shins/ankles/shoes/blank stay native.
Full round knees + natural fold interfaces are active from the first drawing.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,math,hashlib
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,distance_transform_edt,binary_dilation

O=Path(__file__).resolve().parents[1];R=O.parent
M=R/'F082_COMPLETE_PANTS_JOIN_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
srcpath=M/'candidate/F082.png'
assert sha(srcpath)=='ce1ea797ed8ae89212e436905da207447c6ec8fd6df6a1f2d7671c43ff4e7fa6'
assert sha(M/'actual_scene/F082_canvas.png')=='5051b6e5994f46127cd235a203efc5f899cdeb5c237af28604bc9b9881e7f97f'
B=np.asarray(Image.open(srcpath).convert('RGBA'));Y,X=np.mgrid[:1536,:1024]
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
H=np.array([390.,950.]);K=np.array([610.,1200.]);SC=np.array([540.,600.])
RL,RT,RA=rot(6),rot(-5),rot(-2)
Ht=K+RL@(H-K);tT=Ht-RT@H;UT=np.c_[RT,tT]
SCt=RT@SC+tT;tA=SCt-RA@SC;UA=np.c_[RA,tA]
origin=np.array([275.,112.]);tAS=.7*tA+origin-RA@origin;US=np.c_[RA,tAS]
curve=np.array([[1070,225],[1085,235],[1098,270],[1112,315],[1130,360],[1150,400],[1170,445],[1190,485],[1215,520],[1245,550],[1270,552],[1290,540],[1304,540],[1315,560],[1350,580],[1535,580]],float)
valleyX=np.interp(np.arange(1536),curve[:,0],curve[:,1])
feet=np.asarray(Image.open(M/'geometry/SHOE_ANKLE_AND_SURROUNDING_EMPTY_HARD_PROTECT.png').convert('L'))>0
# Fixed region stops behind the whole natural fold connector. It does not own
# the full knee circle or a horizontal strip at1210.
shin=(Y>=1070)&(X<=valleyX[Y]-24)&(Y<=1325)
fixed=feet|shin|((Y>1316)&(X>=235)&(X<=760))
active=~fixed
actual074=np.asarray(Image.open(R/'F074_PANTS_LOCAL_actual_call01_20261019/candidate/F074.png').convert('RGBA'))
ground=np.zeros((1536,1024),bool)
for x in range(220,651):
 ys=np.flatnonzero(actual074[:,x,3]>=128)
 if len(ys) and ys.max()>=1290:ground[int(ys.max()),x]=True
groundBand=distance_transform_edt(~ground)<=3
for name,m in [('FINAL082_REAL_SHINS_ANKLES_SHOES_AND_EMPTY_FIXED',fixed),('F086_COMPLETE_ACTIVITY_THROUGH_BOTH_ROUND_KNEES_AND_FOLDS',active),('ORIGINAL_TRUE_SHOES_ANKLES_SURROUNDING_EMPTY_HARD',feet),('GROUND_GEOMETRY_ONLY_ALLOW_REAL_NEW_PEN_WITHIN_3PX',groundBand)]:Image.fromarray(np.uint8(m)*255).save(O/f'masks/{name}.png')
master=np.zeros_like(B);master[fixed]=B[fixed];Image.fromarray(master).save(O/'anatomy/FINAL082_TRUE_FIXED_SUPPORT_MASTER_NATIVE.png')

# Both complete arm/sleeve/closed-grip source groups share one rigid transform;
# smooth shoulder-root interpolation belongs only to this planning reference.
arm=Image.new('L',(1024,1536));dr=ImageDraw.Draw(arm)
polys=[[(545,558),(615,568),(700,600),(805,625),(916,632),(1008,631),(1023,742),(953,749),(815,724),(705,706),(642,725),(585,678),(551,624)],[(494,579),(555,579),(616,616),(659,684),(785,724),(906,758),(1023,762),(1023,889),(925,888),(799,840),(664,778),(600,806),(538,755),(507,681)]]
for p in polys:dr.polygon(p,fill=255)
# Keep an empty-pixel margin with the same rigid arm mapping, so inverse-field
# interpolation outside the polygon cannot leave a duplicate forearm sliver.
armMask=binary_dilation(np.asarray(arm)>0,iterations=12)
def torso(q):return RT@np.asarray(q)+tT
def arms(q):return RA@np.asarray(q)+tA
def desired(q):
 q=np.asarray(q,float);x,y=q;xx=int(np.clip(round(x),0,1023));yy=int(np.clip(round(y),0,1535))
 if fixed[yy,xx]:return q
 if armMask[yy,xx]:return arms(q)
 if y<=820:return torso(q)
 if y<=950:
  u=np.clip((y-820)/130,0,1);u=u*u*(3-2*u)
  return Ht+rot(-5+11*u)@(q-H)
 # Femoral motion flows into complete active rounded knee faces; only the
 # actual shin support and geometric floor position taper it to zero.
 u=np.clip((1313-y)/200,0,1);u=u*u*(3-2*u)
 supportDistance=max(0.,x-(valleyX[yy]-24))
 v=np.clip(supportDistance/75,0,1);v=v*v*(3-2*v)
 return q+u*v*((K+RL@(q-K))-q)
controls={}
def add(q,why):
 q=np.asarray(q,float);controls[tuple(q)]=(q,desired(q),why)
for y in [0,150,260,360,460,520,560,600,640,690,740,780,820,850,890,920,950,980,1020,1060,1100,1130,1160,1190,1220,1250,1280,1300,1313,1340,1390,1535]:
 for x in [0,130,190,230,270,310,350,390,430,470,510,550,590,630,670,710,780,900,1023]:add([x,y],'complete source-pixel visual reference, fixed true supports and natural active folds')
for y in range(1070,1315,20):
 add([max(235,valleyX[y]-24),y],'fixed shin edge, NOT a fixed old knee circle')
 add([valleyX[y]+10,y],'complete natural fold interface INCLUDED in new activity')
add(H,'hip visual estimate rebound from FINAL082 actual; not hidden joint proof');add(K,'stationary knee support proxy');add(SC,'shared arm-root midpoint visual proxy')
rows=list(controls.values());s=np.array([v[0] for v in rows]);t=np.array([v[1] for v in rows]);rbf=RBFInterpolator(t,s-t,kernel='thin_plate_spline',smoothing=.35)
y,x=np.mgrid[0:1536:2,0:1024:2];p=np.c_[x.ravel(),y.ravel()];d=np.empty_like(p,float)
for i in range(0,len(p),8000):d[i:i+8000]=rbf(p[i:i+8000])
d=d.reshape(768,512,2)
sx=X+map_coordinates(d[:,:,0],[Y/2,X/2],order=1,mode='nearest');sy=Y+map_coordinates(d[:,:,1],[Y/2,X/2],order=1,mode='nearest')
invA=np.linalg.inv(np.vstack([UA,[0,0,1]]))[:2]
ax=invA[0,0]*X+invA[0,1]*Y+invA[0,2];ay=invA[1,0]*X+invA[1,1]*Y+invA[1,2]
armOwn=map_coordinates(armMask.astype(float),[ay,ax],order=0,mode='constant')>.5
sx[armOwn]=ax[armOwn];sy[armOwn]=ay[armOwn]
invT=np.linalg.inv(np.vstack([UT,[0,0,1]]))[:2]
tx=invT[0,0]*X+invT[0,1]*Y+invT[0,2];ty=invT[1,0]*X+invT[1,1]*Y+invT[1,2]
head=ty<500;sx[head]=tx[head];sy[head]=ty[head]
pm=B.astype(float)/255;pm[:,:,:3]*=pm[:,:,3:4]
n=np.stack([map_coordinates(pm[:,:,i],[sy,sx],order=1,mode='constant') for i in range(4)],axis=2)
vis=n[:,:,3]>0;n[vis,:3]/=n[vis,3:4];n=np.uint8(np.clip(n*255+.5,0,255));n[fixed]=B[fixed]
assert np.array_equal(n[fixed],B[fixed])
Image.fromarray(n).save(O/'anatomy/F086_COMPLETE_VISIBLE_SOURCE_PIXEL_REFERENCE_ONLY.png')
fgSource=Image.open(M/'layers/F082_FG_true_front_fingers.png').convert('RGBA')
fgOwn=np.asarray(fgSource.transform((1024,1536),Image.Transform.AFFINE,tuple(invA.ravel()),Image.Resampling.BICUBIC))[:,:,3]>0
fg=np.zeros_like(n);fg[fgOwn]=n[fgOwn];bg=n.copy();bg[fgOwn]=0
assert np.array_equal(np.maximum(bg,fg),n)
Image.fromarray(bg).save(O/'anatomy/F086_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F086_REFERENCE_TRUE_FRONT_GRIPS.png')
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
first=Image.new('RGBA',(1024,1536),'#e1e4e6');first.alpha_composite(Image.fromarray(n));dr=ImageDraw.Draw(first)
for y,txt,size in [(18,'F086 / HIPS ADVANCE UP / WHOLE BODY RISE / COMPLETE ROUND KNEES',20),(55,'SOLE FINAL082 ACTUAL PIXELS / REFERENCE ONLY, NOT NEW DRAWING',19),(91,'Both full arms + closed grips + TRUE shafts/crane move together.',18),(1410,'Both moving thighs + COMPLETE knee faces + natural shin folds: NEW ART.',18),(1450,'Fixed real shins / ankles / shoes / empty support space stay native.',18)]:dr.text((18,y),txt,font=font(size),fill='#25313b')
first.convert('RGB').save(O/'inputs/01_F086_COMPLETE_VISIBLE_RISE_FROM_FINAL082.png')

props0=Image.open(M/'actual_scene/F082_code_props_actual_layer.png').convert('RGBA');invS=np.linalg.inv(np.vstack([US,[0,0,1]]))[:2]
props=props0.transform((1920,1080),Image.Transform.AFFINE,tuple(invS.ravel()),Image.Resampling.BICUBIC);props.save(O/'code_props/F086_TRUE_RIGID_RODS_CRANE_SAME_BOTH_GRIPS.png')
base=Image.open(R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png').convert('RGBA')
bgScene=base.copy();k=4;cloth=Image.new('RGBA',(1920*k,1080*k));cd=ImageDraw.Draw(cloth)
cd.polygon([(int(x*k),int(y*k)) for x,y in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
for j in range(16):
 cx0=1050+j*52;cy=784+(j%2)*6
 for xx,yy,rr in [(cx0,cy,4),(cx0+26,cy-9,2.5)]:cd.ellipse(((xx-rr)*k,(yy-rr)*k,(xx+rr)*k,(yy+rr)*k),fill=(235,235,225,179))
cloth=cloth.resize((1920,1080),Image.Resampling.LANCZOS);bgScene.paste(cloth.crop((1430,780,1560,800)),(1430,780))
shadow=props.getchannel('A').transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3))
clip=Image.new('L',(1920,1080));ImageDraw.Draw(clip).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255)
sa=np.uint8(np.asarray(shadow)*.07)*(np.asarray(clip)>0);shade=Image.new('RGBA',(1920,1080),(14,20,30,0));shade.putalpha(Image.fromarray(sa));bgScene.alpha_composite(shade)
bgScene.save(O/'code_props/F086_BOX_CLOTH_UNLOAD_CONTEXT_REFERENCE.png')
def scene(z):return z.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=bgScene.copy();ctx.alpha_composite(Image.open(M/'actual_scene/F082_native_ground_shadows_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(bg)));ctx.alpha_composite(props);ctx.alpha_composite(scene(Image.fromarray(fg)));ctx.alpha_composite(Image.open(M/'actual_scene/F082_box_front_actual_layer.png'))
ctx.save(O/'anatomy/F086_SAME_BODY_TRUE_PROPS_CONTEXT_REFERENCE_ONLY.png');dr=ImageDraw.Draw(ctx);dr.text((18,18),'F086 SAME BODY / TRUE RIGID RODS / ORIGINAL SUPPORTS + BOX / UNLIT REFERENCE ONLY',font=font(22),fill='white');ctx.convert('RGB').save(O/'inputs/02_SAME_F086_TRUE_RODS_CRANE_BOX_GROUND_CONTEXT.png')

scope=Image.new('RGBA',(1024,1536),'#e1e4e6');scope.alpha_composite(Image.fromarray(n));overlay=np.zeros_like(n)
overlay[active]=[238,150,45,85];overlay[fixed]=[15,185,130,110];connector=active&(Y>=1060)&(X>=235)&(X<=740);overlay[connector]=[180,75,220,100];overlay[:,:,3]=np.uint8(overlay[:,:,3].astype(float)*n[:,:,3]/255)
scope.alpha_composite(Image.fromarray(overlay));dr=ImageDraw.Draw(scope)
for y,txt,color in [(18,'F086 ADOPTION STRATEGY / SAME POSE / NOT A THIRD MODEL POSE','#25313b'),(58,'Orange: full new head / torso / hips / BOTH complete arms and thighs.','#8b4f0a'),(90,'Purple: BOTH full round knees + complete natural shin fold interfaces.','#76258e'),(122,'Green: real shins / ankles / shoes / empty support space stays native.','#096c51'),(1430,'Ground line = geometry only. New real pen within3px; no old arc paste.','#25313b')]:dr.text((18,y),txt,font=font(18),fill=color)
scope.convert('RGB').save(O/'reference/SAME_F086_COMPLETE_KNEES_NATURAL_FOLDS_AND_HARD_SUPPORT_STRATEGY.png')

oldg=json.loads((R/'F082_ACTIVE_TARGET_FIXED074_SUPPORTS_20261019/geometry/F082_COMPLETE_ACTIVE_RISE_TRUE_CONTACTS_AND_SUPPORT_DOMAIN.json').read_text());points=oldg['true_points_target_F082'];new={k:(RA@np.asarray(v)+tAS).tolist() for k,v in points.items()};rods={}
for name,start,end in [('BODY','body_free','body_hinge'),('NECK3','neck3_free','neck3_hinge')]:
 l0=float(np.linalg.norm(np.array(points[end])-points[start]));l1=float(np.linalg.norm(np.array(new[end])-new[start]));assert abs(l0-l1)<1e-9;rods[name]={'source_projected_scene':l0,'target_projected_scene':l1}
g={'status':'F086_VISIBLE_FULL_BODY_INPUT_GATE_ONLY_NOT_NEW_ART','sole_final082':{'commit':'30b8223b6292aacbb6011d1eb871f5cb170a4876','path':str(srcpath),'SHA256':sha(srcpath),'actual_Canvas_SHA256':sha(M/'actual_scene/F082_canvas.png')},'visual_proxies_NOT_HIDDEN_BONES':{'hip_source':H.tolist(),'stationary_knee_support':K.tolist(),'shared_arm_root_midpoint':SC.tolist(),'uncertainty_native':'about15to25px'},'hip_target':Ht.tolist(),'hip_delta_native':(Ht-H).tolist(),'thigh_proxy_turn_degrees':6,'hip_knee_proxy_distance_source':float(np.linalg.norm(H-K)),'hip_knee_proxy_distance_target':float(np.linalg.norm(Ht-K)),
 'whole_head_torso_rise_degrees':-5,'head_torso_native_matrix':UT.tolist(),'both_complete_arms_closed_grips_shared_turn_degrees':-2,'whole_both_arms_closed_grips_native_matrix':UA.tolist(),'same_true_rods_crane_scene_rigid_matrix':US.tolist(),'arm_root_midpoint_source':SC.tolist(),'arm_root_midpoint_target':SCt.tolist(),'true_points_source_FINAL082':points,'true_points_target_F086':new,'rod_rigidity_checks':rods,'crane_plane_inclination_degrees':55,'total_projected_rigid_roll_from_FINAL074_degrees':-8,
 'fixed_support_native_identity_RGBA_changes':0,'fixed_support_visible_pixels':int((fixed&(B[:,:,3]>0)).sum()),'no_fixed_knee_outer_circle_or_y1210_cut':True,'ground_line_is_geometry_only_new_pen_within3native':True,'source_reference_pixels_adopted_as_production_art':0,'source_controls':s.tolist(),'target_controls':t.tolist(),'new_model_calls':0,'new_actual086_Canvas':0,'new090_model_calls':0}
(O/'geometry/F086_FULL_RISE_BOTH_ARM_TRUE_PROP_AND_FIXED_SUPPORT_GEOMETRY.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps({k:v for k,v in g.items() if k not in ['source_controls','target_controls']},indent=2))
