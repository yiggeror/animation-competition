from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,hashlib,math
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates
R=Path(__file__).resolve().parents[5];P=R/'collab/reviews/cloud_s12_20261018';M=P/'BLUE_sleeve_root_actual_call01_20261019/F064';O=P/'F070_COMPLETE_TARGET_from_LOCKED064_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ['inputs','anatomy','geometry','masks','reference','code_props','prompts','requests','provenance','qa']:(O/d).mkdir(exist_ok=True)
b=Image.open(M/'candidate/F064.png').convert('RGBA');B=np.array(b);assert sha(M/'candidate/F064.png')=='905cab5393450737da89823b9e24915a05268cdcf2a96023e208e2a9c12dea4d';H=np.array([330.,1060.]);hipD=np.array([-3.,-5.]);deltaScene=np.array([-3.,-24.]);delta=deltaScene/.7

def rot(a):
 t=math.radians(a);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def torso(q):
 q=np.array(q,float);yy=q[1];ang=-4. if yy<=880 else -4+3*np.clip((yy-880)/180,0,1);weight=1 if yy<=1060 else np.clip((1140-yy)/80,0,1);return H+hipD*weight+rot(ang*weight)@(q-H)
controls={}
def add(s,t,why):controls[tuple(np.round(s,4))]=(np.array(s,float),np.array(t,float),why)
# Original loose-clothing hip/shoulder centres are visual construction estimates, not hidden3D measurements.
for yy in [320,390,460,530,600,650]:
 for xx in [430,500,570,640,710,775]:add([xx,yy],torso([xx,yy]),'rigid head/neck/chest follow, no face squash')
for yy in [650,710,770,830,890,950,1010,1060]:
 for xx in [170,240,310,380,450,520,580,630]:
  if yy<790 and xx<260:continue
  add([xx,yy],torso([xx,yy]),'spine/chest/waist/pelvis coordinated rotation')
for yy in [1120,1170,1250,1330,1450,1535]:
 for xx in [0,130,260,390,520,650,780,910,1023]:add([xx,yy],[xx,yy],'ground and lower support fixed')
for xx,yy in [[0,0],[1023,0],[0,1535],[1023,1535],[330,1060],[180,1030],[480,1080],[550,1100]]:add([xx,yy],torso([xx,yy])if yy>=1000 and yy<1120 else[xx,yy],'pelvic rock / image guard')
arms={}
def ik(S,E,W,St,Wt):
 l1=np.linalg.norm(E-S);l2=np.linalg.norm(W-E);v=Wt-St;d=np.linalg.norm(v);assert abs(l1-l2)<d<l1+l2,'Target arm unreachable without bone stretch';u=v/d;a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a));n=np.array([-u[1],u[0]]);c=St+a*u;candidates=[c+h*n,c-h*n];expected=.5*(torso(E)+E+delta);Et=min(candidates,key=lambda q:np.linalg.norm(q-expected));return Et,l1,l2
for name,S,E,W,widths in [('near_RIGHT',np.array([553.,766.]),np.array([704.,945.]),np.array([886.,992.]),[32,26,18]),('far_LEFT',np.array([566.,708.]),np.array([724.,850.]),np.array([889.,858.]),[27,23,16])]:
 St=torso(S);Wt=W+delta;Et,l1,l2=ik(S,E,W,St,Wt);arms[name]={'source_S_E_W':[S.tolist(),E.tolist(),W.tolist()],'target_S_E_W':[St.tolist(),Et.tolist(),Wt.tolist()],'projected_source_lengths':[float(l1),float(l2)],'projected_target_lengths':[float(np.linalg.norm(Et-St)),float(np.linalg.norm(Wt-Et))]}
 for a0,b0,a1,b1,r0,r1 in [(S,E,St,Et,widths[0],widths[1]),(E,W,Et,Wt,widths[1],widths[2])]:
  u=(b0-a0)/np.linalg.norm(b0-a0);v=(b1-a1)/np.linalg.norm(b1-a1);n=np.array([-u[1],u[0]]);nt=np.array([-v[1],v[0]])
  for f in [0,.25,.5,.75,1]:
   p=a0+(b0-a0)*f;q=a1+(b1-a1)*f;rr=r0*(1-f)+r1*f
   for k in [-1,0,1]:add(p+k*n*rr,q+k*nt*rr,'complete arm fixed-length joint/cross-section reference')
# Whole original closed hands, naked near right wrist and far jade move together with TRUE rods.
for xs,ys in [(range(874,1023,22),range(930,1064,22)),(range(838,1000,22),range(790,926,22))]:
 for xx in xs:
  for yy in ys:add([xx,yy],np.array([xx,yy])+delta,'whole closed grip follows rigid prop shift; no fingertip pull')
rows=list(controls.values());src=np.array([v[0]for v in rows]);dst=np.array([v[1]for v in rows]);rbf=RBFInterpolator(dst,src-dst,kernel='thin_plate_spline',smoothing=.2)
# Reference construction only: warp REAL source pixels, no painted body/fingers. Coarse displacement field is smooth.
yc,xc=np.mgrid[0:1536:2,0:1024:2];pts=np.c_[xc.ravel(),yc.ravel()];disp=np.empty_like(pts,dtype=float)
for k in range(0,len(pts),12000):disp[k:k+12000]=rbf(pts[k:k+12000])
disp=disp.reshape(768,512,2);y,x=np.mgrid[:1536,:1024];dx=map_coordinates(disp[:,:,0],[y/2,x/2],order=1,mode='nearest');dy=map_coordinates(disp[:,:,1],[y/2,x/2],order=1,mode='nearest');coords=[y+dy,x+dx]
near=(x>=874)&(y>=925)&(y<1080);far=(x>=838)&(y>=790)&(y<925);handOwn=(near|far)&(B[:,:,3]>0);body=B.copy();body[((x>=878)&near)|((x>=842)&far)]=0;ap=body.astype(float)/255;ap[:,:,:3]*=ap[:,:,3:4];out=np.stack([map_coordinates(ap[:,:,k],coords,order=1,mode='constant')for k in range(4)],axis=2);good=out[:,:,3]>0;out[good,:3]/=out[good,3:4];out=np.uint8(np.clip(out*255+.5,0,255));hand=np.zeros_like(B);hand[handOwn]=B[handOwn];hand=Image.fromarray(hand,'RGBA').transform((1024,1536),Image.Transform.AFFINE,(1,0,-delta[0],0,1,-delta[1]),Image.Resampling.BICUBIC);pose=np.array(Image.alpha_composite(Image.fromarray(out,'RGBA'),hand))
fixed=(y>=1170)
C=P/'F048_F052_actual_20261019/F052/contact_masks'
for f in C.glob('*.png'):fixed|=np.array(Image.open(f).convert('L'))>0
pose[fixed]=B[fixed];assert np.array_equal(pose[fixed],B[fixed]);Image.fromarray(pose,'RGBA').save(O/'anatomy/F070_COMPLETE_KNEELING_BODY_TARGET_REFERENCE_ONLY.png');Image.fromarray(np.uint8(fixed)*255).save(O/'masks/NATIVE_ORIGINAL_KNEES_SHINS_INSTEP_SHOES_FIXED.png')
fg0=Image.open(M/'layers/F064_FG_true_front_fingers.png').convert('RGBA');fgShift=np.array(fg0.transform((1024,1536),Image.Transform.AFFINE,(1,0,-delta[0],0,1,-delta[1]),Image.Resampling.BICUBIC));fo=fgShift[:,:,3]>0;fg=np.zeros_like(pose);fg[fo]=pose[fo];back=pose.copy();back[fo]=0;assert np.array_equal(np.maximum(back,fg),pose)
Image.fromarray(back,'RGBA').save(O/'anatomy/F070_REFERENCE_BG.png');Image.fromarray(fg,'RGBA').save(O/'anatomy/F070_REFERENCE_FRONT_GRIPS.png')
# First model image is ONE visible complete target, no alternate old whole-body image.
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
first=Image.new('RGBA',(1024,1536),'#e1e4e6');first.alpha_composite(Image.fromarray(pose,'RGBA'));dr=ImageDraw.Draw(first);dr.text((18,18),'F070 WHOLE KNEELING BODY TAKES CRANE LOAD',font=font(25),fill='#25313b');dr.text((18,57),'Hip/pelvis -> chest/back -> neck/head + BOTH COMPLETE ARMS.',font=font(20),fill='#25313b');dr.text((18,91),'Real locked064 pixels / POSE REFERENCE ONLY / redraw natural anatomy.',font=font(18),fill='#25313b');dr.text((18,1410),'Original knee/shin/instep and BOTH shoe supports fixed. Both grips continuous.',font=font(18),fill='#25313b');dr.text((18,1450),'No isolated shoulder lift, translated torso slab, stretched bones or pulled fingertips.',font=font(17),fill='#25313b');first.convert('RGB').save(O/'inputs/01_F070_COMPLETE_VISIBLE_KNEELING_TARGET.png')
# Exact true props move as a unit with both original closed grips. This is code-prop reference, not a character rig.
props0=Image.open(M/'actual_scene/F064_code_props_actual_layer.png').convert('RGBA');props=props0.transform((1920,1080),Image.Transform.AFFINE,(1,0,-deltaScene[0],0,1,-deltaScene[1]),Image.Resampling.BICUBIC);props.save(O/'code_props/F070_TRUE_CRANE_TWO_RODS_REFERENCE.png')
I=P/'right_hand_lower_rod_inputs_20261019/first034_040/code_props';base=Image.open(I/'background_box_cloth_UNCHANGED.png').convert('RGBA');bg=base.copy()
# Code cloth pressure reference: reconstruct only tiny original fold region, not the wooden box/room.
K=4;cloth=Image.new('RGBA',(1920*K,1080*K));cd=ImageDraw.Draw(cloth);cd.polygon([(int(xx*K),int(yy*K))for xx,yy in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
for i in range(16):
 cx=1050+i*52;cy=784+(i%2)*6
 for xx,yy,rr in [(cx,cy,4),(cx+26,cy-9,2.5)]:cd.ellipse(((xx-rr)*K,(yy-rr)*K,(xx+rr)*K,(yy+rr)*K),fill=(235,235,225,179))
cloth=cloth.resize((1920,1080),Image.Resampling.LANCZOS);bg.paste(cloth.crop((1430,780,1560,800)),(1430,780))
def cubic(a,b,c,d,n=32):return [(1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)for t in np.linspace(0,1,n)]
fold=Image.new('RGBA',(1920,1080));fd=ImageDraw.Draw(fold);p=cubic([1438,793],[1462,790],[1489,800],[1510,797])+cubic([1510,797],[1524,795],[1537,789],[1547,790])+[np.array([1547,796])]+cubic([1547,796],[1524,801],[1496,802],[1475,799])+[np.array([1438,798])];fd.polygon([tuple(q)for q in p],fill=(17,29,49,28));fd.line([tuple(q)for q in cubic([1445,796],[1466,795],[1486,801],[1509,797])],fill=(12,19,31,46),width=1);bg.alpha_composite(fold)
# Faint cast/contact shadow derives from actual crane alpha, not an invented support dot.
alpha=props.getchannel('A');shadow=alpha.transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(2.5));sa=np.array(shadow);clothMask=Image.new('L',(1920,1080));ImageDraw.Draw(clothMask).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255);sa=np.uint8(sa*.13)*(np.array(clothMask)>0);shade=Image.new('RGBA',(1920,1080),(14,20,30,0));shade.putalpha(Image.fromarray(sa));bg.alpha_composite(shade);bg.save(O/'code_props/F070_BACKGROUND_WITH_CLOTH_UNLOADING_REFERENCE.png')
def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=bg.copy();ctx.alpha_composite(Image.open(M/'actual_scene/F064_native_ground_shadows_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(back,'RGBA')));ctx.alpha_composite(props);ctx.alpha_composite(scene(Image.fromarray(fg,'RGBA')));front=Image.open(M/'actual_scene/F064_box_front_actual_layer.png');ctx.alpha_composite(front);ctx.save(O/'anatomy/F070_REFERENCE_FULL_SCENE_NOT_ACTUAL_DRAWING.png')
old=base.copy()
for name in ['native_ground_shadows','BG_person_registered','code_props','FG_index_registered','box_front']:old.alpha_composite(Image.open(M/f'actual_scene/F064_{name}_actual_layer.png'))
board=Image.new('RGB',(2880,1080),'#e1e4e6');board.paste(ctx.convert('RGB'));dd=ImageDraw.Draw(board);dd.text((18,18),'F070 SAME COMPLETE TARGET + TRUE RODS / LOAD TRANSFER REFERENCE ONLY',font=font(24),fill='white');box=(1100,680,1600,835)
for pos,img,title in [((1950,160),old,'LOCKED064 crane/cloth before'),((1950,590),ctx,'F070 visible body edge / cloth unloading target')]:
 board.paste(img.crop(box).resize((920,285),Image.Resampling.NEAREST).convert('RGB'),pos);dd.text((pos[0],pos[1]-40),title,font=font(22),fill='#25313b')
dd.text((1950,860),'Judge actual silhouette/cloth/rim pixels;',font=font(22),fill='#25313b');dd.text((1950,895),'translation is NOT a claimed air-gap measure.',font=font(22),fill='#25313b');dd.text((1950,960),'Knees/shins/feet + box remain original.',font=font(20),fill='#25313b');board.save(O/'inputs/02_SAME_F070_TRUE_RODS_CLOTH_TRANSFER_CONTEXT.png')
third=Image.new('RGB',(1024,1024),'#e1e4e6');dd=ImageDraw.Draw(third);dd.text((18,18),'ONLY LOCKED064 IDENTITY / LOCAL MATERIAL, NO OLD WHOLE POSE',font=font(21),fill='#25313b')
for title,box,pos,size in [('FACE / GLASSES / NECK IDENTITY',(560,430,755,640),(40,140),(440,470)),('ORIGINAL BLUE FLOWERS',(420,750,500,830),(550,140),(420,300)),('TROUSER / SHOE MATERIAL',(160,1210,260,1310),(550,570),(420,300))]:
 im=b.crop(box);panel=Image.new('RGBA',im.size,'#e1e4e6');panel.alpha_composite(im);third.paste(panel.resize(size,Image.Resampling.NEAREST).convert('RGB'),pos);dd.text((pos[0],pos[1]-30),title,font=font(18),fill='#25313b')
third.save(O/'inputs/03_ONLY_IDENTITY_LOCAL_MATERIAL.png')
# Explicit true endpoints / exact projected rod lengths; body/hip centres remain uncertain visual estimates.
points={'crane_root':[1335,775],'body_hinge':[1282.1986905564156,773.9467944476169],'neck3_hinge':[1497.5314905035327,714.6642052957592],'body_free':[951.2616943917175,798.9063357461391],'neck3_free':[930.1059238245394,729.1297395769899],'near_grip':[959.7,798.269911774929],'far_grip':[953.9703435271945,728.5213574356443]};newpts={k:(np.array(v)+deltaScene).tolist()for k,v in points.items()};ge={'status':'COMPLETE_VISIBLE_F070_INPUT_GATE_ONLY','sole_mother064':{'commit':'25d26c12f7350935f0b0bcf6ff3b0275e4daa53b','path':str((M/'candidate/F064.png').relative_to(R)),'SHA256':sha(M/'candidate/F064.png')},'hip_pivot_VISIBLE_ESTIMATE':H.tolist(),'pelvis_rock_native':hipD.tolist(),'head_neck_chest_rotation_degrees':-4,'waist_pelvis_rotation_degrees_range':[-4,-1],'all_arms':arms,'source_control_points':src.tolist(),'target_control_points':dst.tolist(),'control_meanings':[q[2]for q in rows],'all_controls_REFERENCE_ONLY_not_measured_hidden_bones':True,'source_bangle_centre_NOT_used_as_wrist_joint':True,'true_full_hand_and_props_scene_delta':deltaScene.tolist(),'original_true_points_scene':points,'new_true_points_scene':newpts,'crane_plane_fold_degrees':55,'ground_support_RGBA_fixed_exact':True,'source_RGB_only_reference_no_code_fingers_or_body_paint':True,'reference_mesh_NOT_actual_character_art':True,'cloth_pressure_reference_weight':.25,'gap_not_inferred_from_displacement':True,'first_full_target_actual_generation_calls':0,'first_full_target_actual_Canvas':0,'074_not_executable':True};(O/'geometry/F070_COMPLETE_BODY_AND_TRUE_CONTACTS.json').write_text(json.dumps(ge,indent=2)+'\n')
print(json.dumps({'created_three_actual_visible_input_PNGs':True,'controls':len(rows),'arms':arms,'ground_support_exact':True,'hand_crane_delta_scene':deltaScene.tolist(),'imagegen_calls':0}))
