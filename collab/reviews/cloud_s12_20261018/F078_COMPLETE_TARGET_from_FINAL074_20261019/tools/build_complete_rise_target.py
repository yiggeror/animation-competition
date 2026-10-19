"""Visible whole-person REFERENCE ONLY from FINAL074; never actual new art.
Hip advances/up by6degree thigh rotation about fixed knee; upper body+whole arms
rigid3degree back turn. Current complete ground-support pixels retained.
True props use the identical rigid upper transform; neither shaft slides.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,math,hashlib
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F074_PANTS_LOCAL_actual_call01_20261019';OLD=R/'F074_COMPLETE_TARGET_from_LOCKED070_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=M/'candidate/F074.png';assert sha(source)=='2fbceafa0d533d727e6b72f0e292c63f98295ee34dd4a677a51e62785b768900';b=Image.open(source).convert('RGBA');B=np.array(b);H=np.array([336.,1040.]);K=np.array([600.,1200.])
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
RL=rot(6);RU=rot(-3);Ht=K+RL@(H-K);tN=Ht-RU@H;UN=np.c_[RU,tN];origin=np.array([275.,112.]);tS=.7*tN+origin-RU@origin;US=np.c_[RU,tS]
Y,X=np.mgrid[:1536,:1024]
feet=np.asarray(Image.open(R/'F074_PANTS_CONTINUITY_INPUT_GATE_20261019/masks/CURRENT074_BOTH_SHOES_BARE_ANKLES_HARD_PROTECT.png').convert('L'))>0
farShin=Image.new('L',(1024,1536));ImageDraw.Draw(farShin).polygon([(235,1100),(300,1095),(395,1150),(265,1210),(220,1190)],fill=255)
fixed=(Y>=1140)|feet|(np.asarray(farShin)>0)
rigid=(Y<=880)|((X>=600)&(Y<=1035))
controls={}
def upper(q):return RU@np.asarray(q)+tN
def desired(q):
 q=np.asarray(q,float);x,y=q
 if y>=1140:return q
 if y<=900 or (x>=600 and y<=1035):return upper(q)
 if y<=1040:
  u=np.clip((y-900)/140,0,1);u=u*u*(3-2*u);return Ht+rot(-3+9*u)@(q-H)
 u=np.clip((1140-y)/100,0,1);u=u*u*(3-2*u);return q+u*((K+RL@(q-K))-q)
def add(q,why):
 q=np.array(q,float);xx,yy=np.rint(q).astype(int);xx=np.clip(xx,0,1023);yy=np.clip(yy,0,1535);target=q if fixed[yy,xx] else desired(q);controls[tuple(q)]=(q,target,why)
for y in [0,160,260,360,460,560,660,760,840,880]:
 for x in [0,130,260,390,520,650,780,910,1023]:add([x,y],'whole upper body/head/arms rigid; actual final074 only')
for y in [900,930,960,990,1020,1040,1070,1100,1120,1140,1170,1220,1300,1390,1535]:
 for x in [0,130,190,250,310,370,430,490,550,610,670,730,850,1023]:add([x,y],'whole pelvis/thigh transition to fixed current knee/shin/shoe supports')
add(H,'visible estimated hip follows6degree thigh arc, not hidden joint measurement');add(K,'fixed knee support pivot estimate')
rows=list(controls.values());src=np.array([v[0]for v in rows]);dst=np.array([v[1]for v in rows]);rbf=RBFInterpolator(dst,src-dst,kernel='thin_plate_spline',smoothing=.2)
y,x=np.mgrid[0:1536:2,0:1024:2];p=np.c_[x.ravel(),y.ravel()];d=np.empty_like(p,dtype=float)
for i in range(0,len(p),10000):d[i:i+10000]=rbf(p[i:i+10000])
d=d.reshape(768,512,2);dx=map_coordinates(d[:,:,0],[Y/2,X/2],order=1,mode='nearest');dy=map_coordinates(d[:,:,1],[Y/2,X/2],order=1,mode='nearest');sx=X+dx;sy=Y+dy
# Head and BOTH entire arm/closed-hand silhouettes are exactly one rigid source transform, not finger warps.
invU=np.linalg.inv(np.vstack([UN,[0,0,1]]))[:2];ux=invU[0,0]*X+invU[0,1]*Y+invU[0,2];uy=invU[1,0]*X+invU[1,1]*Y+invU[1,2];upperOwn=(uy<=880)|((ux>=600)&(uy<=1035));sx[upperOwn]=ux[upperOwn];sy[upperOwn]=uy[upperOwn]
a=B.astype(float)/255;a[:,:,:3]*=a[:,:,3:4];n=np.stack([map_coordinates(a[:,:,i],[sy,sx],order=1,mode='constant')for i in range(4)],axis=2);v=n[:,:,3]>0;n[v,:3]/=n[v,3:4];n=np.uint8(np.clip(n*255+.5,0,255));n[fixed]=B[fixed];assert np.array_equal(n[fixed],B[fixed]);im=Image.fromarray(n);im.save(O/'anatomy/F078_COMPLETE_RISE_REFERENCE_ONLY.png');Image.fromarray(np.uint8(fixed)*255).save(O/'masks/CURRENT_FINAL074_KNEES_SHINS_INSTEP_SHOES_FIXED_REFERENCE.png')
sourceFG=Image.open(M/'layers/F074_FG_true_front_fingers.png').convert('RGBA');fgOwner=np.asarray(sourceFG.transform((1024,1536),Image.Transform.AFFINE,tuple(invU.ravel()),Image.Resampling.BICUBIC))[:,:,3]>0;fg=np.zeros_like(n);fg[fgOwner]=n[fgOwner];back=n.copy();back[fgOwner]=0;assert np.array_equal(np.maximum(back,fg),n);Image.fromarray(back).save(O/'anatomy/F078_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F078_REFERENCE_FRONT_GRIPS.png')
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
first=Image.new('RGBA',(1024,1536),'#e1e4e6');first.alpha_composite(im);dr=ImageDraw.Draw(first);dr.text((18,18),'F078: HIPS LEAVE HEELS / THIGHS TURN OVER FIXED KNEES',font=font(22),fill='#25313b');dr.text((18,55),'FINAL074 actual pixels / COMPLETE BODY POSE REFERENCE ONLY',font=font(20),fill='#25313b');dr.text((18,91),'Pelvis advances+up; waist/chest/head and BOTH complete arms follow.',font=font(18),fill='#25313b');dr.text((18,1410),'Current final074 knees/shins/insteps/BOTH shoes remain planted.',font=font(20),fill='#25313b');dr.text((18,1450),'Natural full-body redraw required. No new shin length or knee bulk.',font=font(19),fill='#25313b');first.convert('RGB').save(O/'inputs/01_F078_COMPLETE_HIP_LEAVES_HEELS_TARGET.png')
props0=Image.open(M/'actual_scene/F074_code_props_actual_layer.png').convert('RGBA');invS=np.linalg.inv(np.vstack([US,[0,0,1]]))[:2];props=props0.transform((1920,1080),Image.Transform.AFFINE,tuple(invS.ravel()),Image.Resampling.BICUBIC);props.save(O/'code_props/F078_TRUE_CRANE_TWO_RODS_SAME_RIGID_GRIPS.png')
# Static room/box and small cloth unloading patch only; no old body is a pose source.
base=Image.open(R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png').convert('RGBA');bg=base.copy();k=4;c=Image.new('RGBA',(1920*k,1080*k));cd=ImageDraw.Draw(c);cd.polygon([(int(x*k),int(y*k))for x,y in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
for j in range(16):
 cx=1050+j*52;cy=784+(j%2)*6
 for x,y,r in [(cx,cy,4),(cx+26,cy-9,2.5)]:cd.ellipse(((x-r)*k,(y-r)*k,(x+r)*k,(y+r)*k),fill=(235,235,225,179))
c=c.resize((1920,1080),Image.Resampling.LANCZOS);bg.paste(c.crop((1430,780,1560,800)),(1430,780))
# Pressure fold released; faint cloth shadow derived from the current true crane alpha, not a made-up dot.
alpha=props.getchannel('A');shadow=alpha.transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3));sa=np.asarray(shadow);cm=Image.new('L',(1920,1080));ImageDraw.Draw(cm).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255);sa=np.uint8(sa*.07)*(np.asarray(cm)>0);shade=Image.new('RGBA',(1920,1080),(14,20,30,0));shade.putalpha(Image.fromarray(sa));bg.alpha_composite(shade);bg.save(O/'code_props/F078_BOX_CLOTH_UNLOADED_CONTEXT.png')
def scene(img):return img.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=bg.copy();ctx.alpha_composite(Image.open(M/'actual_scene/F074_native_ground_shadows_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(back)));ctx.alpha_composite(props);ctx.alpha_composite(scene(Image.fromarray(fg)));ctx.alpha_composite(Image.open(M/'actual_scene/F074_box_front_actual_layer.png'));ctx.save(O/'anatomy/F078_SAME_COMPLETE_BODY_TRUE_PROPS_REFERENCE_ONLY.png')
old=Image.open(OLD/'code_props/F074_BACKGROUND_WITH_CLOTH_UNLOADING_REFERENCE.png').convert('RGBA')
for name in ['native_ground_shadows','BG_person_registered','code_props','FG_index_registered','box_front']:old.alpha_composite(Image.open(M/f'actual_scene/F074_{name}_actual_layer.png'))
board=Image.new('RGB',(2880,1080),'#e1e4e6');board.paste(ctx.convert('RGB'));dd=ImageDraw.Draw(board);dd.text((18,18),'SAME F078 FULL RISE + TRUE RIGID SHAFTS / ORIGINAL BOX + GROUND',font=font(24),fill='white');box=(1100,560,1660,830)
for pos,img,title in [((1950,150),old,'FINAL074 crane/cloth ONLY'),((1950,590),ctx,'F078 true crane/cloth ONLY')]:
 board.paste(img.crop(box).resize((900,390),Image.Resampling.NEAREST).convert('RGB'),pos);dd.text((pos[0],pos[1]-35),title,font=font(22),fill='#25313b')
dd.text((1950,1020),'No full-air-gap claim from root displacement.',font=font(18),fill='#25313b');board.save(O/'inputs/02_SAME_F078_TRUE_RODS_CRANE_BOX_GROUND_CONTEXT.png')
third=Image.new('RGB',(1024,1024),'#e1e4e6');dd=ImageDraw.Draw(third);dd.text((18,18),'FINAL074 IDENTITY / LOCAL MATERIAL ONLY / NO OLD WHOLE POSE',font=font(21),fill='#25313b')
for title,box,pos,size in [('PARTIAL FACE / GLASSES / NECK',(540,330,735,560),(40,140),(440,470)),('ORIGINAL BLUE FLOWERS',(420,700,500,780),(550,140),(420,300)),('FINAL074 NAVY / SHOE MATERIAL',(140,1210,260,1300),(550,570),(420,300))]:
 z=b.crop(box);bb=Image.new('RGBA',z.size,'#e1e4e6');bb.alpha_composite(z);third.paste(bb.resize(size,Image.Resampling.NEAREST).convert('RGB'),pos);dd.text((pos[0],pos[1]-30),title,font=font(17),fill='#25313b')
third.save(O/'inputs/03_ONLY_FINAL074_IDENTITY_AND_LOCAL_MATERIAL.png')
points={'crane_root':[1329,733],'body_hinge':[1276.1986905564156,731.9467944476169],'neck3_hinge':[1491.5314905035327,672.6642052957592],'body_free':[945.2616943917175,756.9063357461391],'neck3_free':[924.1059238245394,687.1297395769899],'near_grip':[953.7,756.269911774929],'far_grip':[947.9703435271945,686.5213574356443]};new={k:(RU@np.array(v)+tS).tolist()for k,v in points.items()};rod={}
for name,start,end in [('BODY','body_free','body_hinge'),('NECK3','neck3_free','neck3_hinge')]:
 l0=np.linalg.norm(np.array(points[end])-points[start]);l1=np.linalg.norm(np.array(new[end])-new[start]);assert abs(l0-l1)<1e-9;rod[name]={'source_projected_length':float(l0),'target_projected_length':float(l1)}
g={'status':'F078_COMPLETE_VISIBLE_RISE_INPUT_GATE_ONLY','sole_final074':{'commit':'3bd6e9e748bee6d166fa0baee8961df046e92366','path':str(source),'SHA256':sha(source)},'hip_source_VISIBLE_ESTIMATE':H.tolist(),'fixed_knee_pivot_VISIBLE_ESTIMATE':K.tolist(),'source_and_target_femur_projected_proxy_length':float(np.linalg.norm(H-K)),'thigh_proxy_rotation_degrees':6,'hip_target':Ht.tolist(),'hip_delta_native':(Ht-H).tolist(),'upper_body_head_both_complete_arms_rotation_degrees':-3,'one_complete_upper_rigid_native_matrix':UN.tolist(),'true_prop_closed_grips_same_rigid_scene_matrix':US.tolist(),'true_points_source':points,'true_points_target':new,'rod_length_checks':rod,'crane_plane_inclination_degrees':55,'whole_projected_assembly_rigid_roll_degrees':-3,'current_final074_fixed_support_RGBA_exact_in_REFERENCE':True,'support_mask':'masks/CURRENT_FINAL074_KNEES_SHINS_INSTEP_SHOES_FIXED_REFERENCE.png','visible_joint_estimates_uncertainty_native':'about15to25px, not hidden3D bone measurement','new_model_calls':0,'new_actual078_Canvas':0,'reference_pixels_not_actual_new_character_art':True,'source_controls':src.tolist(),'target_controls':dst.tolist()}
(O/'geometry/F078_COMPLETE_RISE_AND_TRUE_CONTACTS.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps({k:v for k,v in g.items()if k not in ['source_controls','target_controls']},indent=2))
