"""F082 source-pixel POSE/ADOPTION REFERENCE ONLY. Zero image-model/Canvas calls.

The only activity mother is FINAL078 c31ae5cc. Fixed supports retain FINAL074
pixels through FINAL078's accepted exclusive static layer. This reference warp
is never a new drawing, a repair output, or an anatomical/bone certification.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import json, math, hashlib
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates, binary_dilation

O = Path(__file__).resolve().parents[1]
R = O.parent
M = R / 'F078_NARROW_JOIN_actual_call01_20261019'
S = R / 'F074_PANTS_LOCAL_actual_call01_20261019'
for name in ['inputs','anatomy','masks','geometry','reference','code_props','prompts','requests','provenance','qa']:
    (O / name).mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = M / 'candidate/F078.png'
support_source = M / 'layers/F078_FIXED074_STATIC_SUPPORTS.png'
assert sha(source) == 'c31ae5cced3a8f3480265e15082836210dced780abcb733530565d5828b0fbee'
assert sha(S/'candidate/F074.png') == '2fbceafa0d533d727e6b72f0e292c63f98295ee34dd4a677a51e62785b768900'
B = np.asarray(Image.open(source).convert('RGBA'))
B074 = np.asarray(Image.open(S/'candidate/F074.png').convert('RGBA'))
STATIC078 = np.asarray(Image.open(support_source).convert('RGBA'))
Y, X = np.mgrid[:1536,:1024]
H = np.array([370.,970.])
K = np.array([610.,1200.])
def rot(d):
    a = math.radians(d)
    return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
RL, RU = rot(5), rot(-3)
Ht = K + RL @ (H-K)
tN = Ht - RU @ H
UN = np.c_[RU,tN]
origin = np.array([275.,112.])
tS = .7*tN + origin - RU@origin
US = np.c_[RU,tS]

# Reuse the real accepted semantic join, allowing its next bending connector
# to move in a curved 30-native-pixel allowance. No horizontal trouser cut.
old = json.loads((R/'F078_FIXED074_SUPPORTS_ZERO_CALL_20261019/geometry/TRUE_SOURCE_SEMANTIC_OWNERSHIP.json').read_text())
seam = np.array(old['seam_y_by_native_x'],float)
boundary = np.minimum(seam+30,1209.)
feet = np.asarray(Image.open(R/'F078_FIXED074_SUPPORTS_ZERO_CALL_20261019/masks/ORIGINAL074_SHOES_ANKLES_HARD.png').convert('L'))>0
foot_guard = binary_dilation(feet,iterations=3)
fixed = (Y>=boundary[X]) | foot_guard | (Y>=1210)
adopt = ~fixed
oldjoin = np.asarray(Image.open(M/'geometry/FROZEN18457_ADOPTION_DOMAIN.png').convert('L'))>0
assert not np.any(oldjoin & fixed), 'New active domain must contain the true preceding bending connector.'
fixed_visible = fixed & (B[:,:,3]>0)
assert np.array_equal(B[fixed_visible],B074[fixed_visible]), 'Visible persistent supports must remain actual074 pixels.'
assert np.array_equal(B[fixed_visible],STATIC078[fixed_visible]), 'No active078 pixels can enter the fixed support master.'
fixed_layer = np.zeros_like(B)
fixed_layer[fixed] = B[fixed]
fixed_layer[fixed_layer[:,:,3]==0] = 0
Image.fromarray(fixed_layer).save(O/'anatomy/FINAL074_TRUE_STATIC_SHINS_ANKLES_SHOES_NATIVE_MASTER.png')
for name,a in [('F082_ACTIVE_UPPER_BOTH_THIGHS_AND_MOVING_KNEE_CONNECTOR',adopt),('F082_FIXED_FINAL074_SUPPORT_OWNERSHIP',fixed),('F082_BOTH_ORIGINAL_SHOES_ANKLES_HARD_GUARD',foot_guard),('F082_MOVING_KNEE_UPPER_CONNECTION_REGION',adopt & (Y>=seam[X]-45) & (X>=220) & (X<=720))]:
    Image.fromarray(np.uint8(a)*255).save(O/f'masks/{name}.png')

# Whole upper/head/BOTH complete arms and palms move by one rigid transform.
# A smooth reference field connects pelvis/thigh turn to static support pixels.
# Natural newly drawn cloth must replace this reference interpolation later.
def upper(q): return RU @ np.asarray(q) + tN
def desired(q):
    q = np.asarray(q,float)
    x,y = q
    xx = int(np.clip(round(x),0,1023)); yy = int(np.clip(round(y),0,1535))
    if fixed[yy,xx]: return q
    if y<=840 or (x>=640 and y<=1035): return upper(q)
    if y<=970:
        u = np.clip((y-840)/130,0,1); u = u*u*(3-2*u)
        return Ht + rot(-3+8*u)@(q-H)
    u = np.clip((boundary[xx]-y)/85,0,1); u = u*u*(3-2*u)
    return q+u*((K+RL@(q-K))-q)
controls = {}
def add(q,why):
    q = np.asarray(q,float)
    controls[tuple(q)] = (q,desired(q),why)
for y in [0,160,260,360,460,560,660,760,800,840,870,900,930,960,970,1000,1030,1060,1090,1120,1150,1180,1209,1240,1300,1390,1535]:
    for x in [0,130,190,250,310,370,430,490,550,610,640,700,780,910,1023]:
        add([x,y],'source actual078 whole-body visual reference, current actual074 fixed supports')
for x in range(180,751,25):
    add([x,boundary[x]],'curved semantic static support boundary, not a straight slice')
    add([x,boundary[x]-45],'moving natural knee upper connector')
add(H,'hip visible estimate rebound from FINAL078, NOT old074 target coordinates')
add(K,'fixed knee visual proxy, not a hidden3D bone measurement')
rows = list(controls.values())
src = np.array([v[0] for v in rows]); dst = np.array([v[1] for v in rows])
rbf = RBFInterpolator(dst,src-dst,kernel='thin_plate_spline',smoothing=.2)
y,x = np.mgrid[0:1536:2,0:1024:2]; p = np.c_[x.ravel(),y.ravel()]
d = np.empty_like(p,dtype=float)
for i in range(0,len(p),10000): d[i:i+10000] = rbf(p[i:i+10000])
d = d.reshape(768,512,2)
sx = X+map_coordinates(d[:,:,0],[Y/2,X/2],order=1,mode='nearest')
sy = Y+map_coordinates(d[:,:,1],[Y/2,X/2],order=1,mode='nearest')
invU = np.linalg.inv(np.vstack([UN,[0,0,1]]))[:2]
ux = invU[0,0]*X+invU[0,1]*Y+invU[0,2]
uy = invU[1,0]*X+invU[1,1]*Y+invU[1,2]
upperOwn = (uy<=840)|((ux>=640)&(uy<=1035))
sx[upperOwn] = ux[upperOwn]; sy[upperOwn] = uy[upperOwn]
a = B.astype(float)/255; a[:,:,:3] *= a[:,:,3:4]
n = np.stack([map_coordinates(a[:,:,i],[sy,sx],order=1,mode='constant') for i in range(4)],axis=2)
v = n[:,:,3]>0; n[v,:3] /= n[v,3:4]
n = np.uint8(np.clip(n*255+.5,0,255))
n[fixed] = B[fixed]
assert np.array_equal(n[fixed],B[fixed])
im = Image.fromarray(n)
im.save(O/'anatomy/F082_COMPLETE_VISIBLE_REFERENCE_ONLY.png')
active = n.copy(); active[fixed]=0
Image.fromarray(active).save(O/'anatomy/F082_ACTIVE_REFERENCE_ONLY_NOT_NEW_DRAWING.png')
sourceFG = Image.open(M/'layers/F078_FG_true_front_fingers.png').convert('RGBA')
fgOwn = np.asarray(sourceFG.transform((1024,1536),Image.Transform.AFFINE,tuple(invU.ravel()),Image.Resampling.BICUBIC))[:,:,3]>0
fg = np.zeros_like(n); fg[fgOwn] = n[fgOwn]
back = n.copy(); back[fgOwn] = 0
assert np.array_equal(np.maximum(back,fg),n)
Image.fromarray(back).save(O/'anatomy/F082_REFERENCE_BG.png')
Image.fromarray(fg).save(O/'anatomy/F082_REFERENCE_FRONT_GRIPS.png')
font = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
first = Image.new('RGBA',(1024,1536),'#e1e4e6'); first.alpha_composite(im)
dr = ImageDraw.Draw(first)
for xy,txt,size in [((18,18),'F082 / PELVIS RISE + BOTH COMPLETE THIGHS + NATURAL KNEE JOIN',20),((18,55),'FINAL078 actual pixels / VISIBLE POSE REFERENCE ONLY',20),((18,91),'Full lower legs shown to judge chain. Fixed support pixels are context.',18),((18,1410),'Adopt future NEW upper + pelvis + thighs + bending knee connector.',19),((18,1450),'FINAL074 lower shins / ankles / BOTH shoes remain native fixed master.',18)]:
    dr.text(xy,txt,font=font(size),fill='#25313b')
first.convert('RGB').save(O/'inputs/01_F082_FULL_VISIBLE_RISE_FROM_FINAL078.png')

# Current TRUE shafts/crane pixels use the identical rigid upper/grip transform.
props0 = Image.open(M/'actual_scene/F078_code_props_actual_layer.png').convert('RGBA')
invS = np.linalg.inv(np.vstack([US,[0,0,1]]))[:2]
props = props0.transform((1920,1080),Image.Transform.AFFINE,tuple(invS.ravel()),Image.Resampling.BICUBIC)
props.save(O/'code_props/F082_TRUE_CRANE_RODS_SAME_RIGID_GRIPS_REFERENCE.png')
base = Image.open(R/'right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png').convert('RGBA')
bg = base.copy(); k=4
c = Image.new('RGBA',(1920*k,1080*k)); cd=ImageDraw.Draw(c)
cd.polygon([(int(x*k),int(y*k)) for x,y in [(1010,800),(1850,800),(1838,764),(1022,764)]],fill='#2f4a78')
for j in range(16):
    cx=1050+j*52; cy=784+(j%2)*6
    for x,y,r in [(cx,cy,4),(cx+26,cy-9,2.5)]:
        cd.ellipse(((x-r)*k,(y-r)*k,(x+r)*k,(y+r)*k),fill=(235,235,225,179))
c=c.resize((1920,1080),Image.Resampling.LANCZOS)
bg.paste(c.crop((1430,780,1560,800)),(1430,780))
alpha=props.getchannel('A')
shadow=alpha.transform((1920,1080),Image.Transform.AFFINE,(1,-.04/.06,795*.04/.06,0,1/.06,800-795/.06),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3))
cm=Image.new('L',(1920,1080)); ImageDraw.Draw(cm).polygon([(1010,800),(1850,800),(1838,764),(1022,764)],fill=255)
sa=np.uint8(np.asarray(shadow)*.07)*(np.asarray(cm)>0)
shade=Image.new('RGBA',(1920,1080),(14,20,30,0)); shade.putalpha(Image.fromarray(sa)); bg.alpha_composite(shade)
bg.save(O/'code_props/F082_BOX_CLOTH_UNLOADED_CONTEXT_REFERENCE.png')
def scene(z):
    return z.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx=bg.copy()
ctx.alpha_composite(Image.open(M/'actual_scene/F078_native_ground_shadows_actual_layer.png'))
ctx.alpha_composite(scene(Image.fromarray(back)))
ctx.alpha_composite(props)
ctx.alpha_composite(scene(Image.fromarray(fg)))
ctx.alpha_composite(Image.open(M/'actual_scene/F078_box_front_actual_layer.png'))
ctx.save(O/'anatomy/F082_SAME_BODY_TRUE_PROPS_SCENE_REFERENCE_ONLY.png')
board=Image.new('RGB',(2880,1080),'#e1e4e6'); board.paste(ctx.convert('RGB'))
dd=ImageDraw.Draw(board); dd.text((18,18),'F082 SAME BODY + TRUE RIGID RODS / SCENE REFERENCE ONLY, NOT ACTUAL CANVAS',font=font(23),fill='white')
actual078=Image.open(M/'actual_scene/F078_canvas.png').convert('RGB')
box=(1100,530,1690,820)
for pos,img,title in [((1950,150),actual078,'FINAL078 actual crane/cloth ONLY'),((1950,625),ctx,'F082 proposed crane/cloth ONLY')]:
    board.paste(img.crop(box).resize((900,442),Image.Resampling.NEAREST).convert('RGB'),pos)
    dd.text((pos[0],pos[1]-35),title,font=font(22),fill='#25313b')
board.save(O/'inputs/02_SAME_F082_TRUE_RODS_CRANE_BOX_GROUND_REFERENCE.png')

# Explicit complete-body ownership picture: same pose, not an alternative pose.
third=Image.new('RGBA',(1024,1536),'#e1e4e6'); third.alpha_composite(im)
connector=adopt & (Y>=seam[X]-45) & (X>=220) & (X<=720)
overlay=np.zeros_like(n); visible=n[:,:,3]>0
overlay[adopt&visible]=[238,150,45,85]
overlay[fixed&visible]=[15,185,130,120]
overlay[connector&visible]=[180,75,220,145]
overlay[:,:,3]=np.uint8(overlay[:,:,3].astype(float)*n[:,:,3]/255)
third.alpha_composite(Image.fromarray(overlay)); dd=ImageDraw.Draw(third)
curve=[(x,float(boundary[x])) for x in range(220,721,4)]
dd.line(curve,fill='#912bb7',width=3)
for xy,txt,size,color in [((18,18),'F082 ACTUAL ADOPTION DOMAIN / SAME FULL VISIBLE TARGET',22,'#25313b'),((18,58),'ORANGE: future new head / upper body / full arms / hips / BOTH thighs',18,'#8b4f0a'),((18,90),'PURPLE: natural bending knee-upper connector INCLUDED in first draw',18,'#76258e'),((18,122),'GREEN: FINAL074 fixed supports; new lower legs / feet NOT adopted',18,'#096c51'),((18,1410),'Curved semantic join may bend with action. No horizontal cut.',20,'#25313b'),((18,1450),'Reference only. Future true drawing must replace ALL orange/purple.',19,'#25313b')]:
    dd.text(xy,txt,font=font(size),fill=color)
third.convert('RGB').save(O/'inputs/03_SAME_F082_ACTIVE_AND_FIXED_SEMANTIC_OWNERSHIP.png')

oldgeom=json.loads((R/'F078_COMPLETE_TARGET_from_FINAL074_20261019/geometry/F078_COMPLETE_RISE_AND_TRUE_CONTACTS.json').read_text())
points=oldgeom['true_points_target']
new={k:(RU@np.asarray(v)+tS).tolist() for k,v in points.items()}
rods={}
for label,start,end in [('BODY','body_free','body_hinge'),('NECK3','neck3_free','neck3_hinge')]:
    l0=float(np.linalg.norm(np.array(points[end])-points[start]))
    l1=float(np.linalg.norm(np.array(new[end])-new[start]))
    assert abs(l0-l1)<1e-9
    rods[label]={'source_projected_length_scene':l0,'target_projected_length_scene':l1}
g={'status':'F082_VISIBLE_ACTIVE_TARGET_INPUT_GATE_ONLY_NOT_NEW_ART',
   'sole_activity_mother':{'commit':'16791e6a6b84093bc4bdc44ad83c6c89863072fc','path':str(source),'SHA256':sha(source)},
   'permanent_static_support_source':{'commit':'3bd6e9e748bee6d166fa0baee8961df046e92366','path':str(S/'candidate/F074.png'),'SHA256':sha(S/'candidate/F074.png'),'accepted_exclusive_source':str(support_source),'exclusive_source_SHA256':sha(support_source)},
   'hip_source_VISIBLE_ESTIMATE':H.tolist(),'fixed_knee_VISIBLE_ESTIMATE':K.tolist(),'hip_target_VISIBLE_ESTIMATE':Ht.tolist(),'hip_delta_native':(Ht-H).tolist(),
   'thigh_proxy_rotation_degrees':5,'projected_hip_to_knee_proxy_length_source':float(np.linalg.norm(H-K)),'projected_hip_to_knee_proxy_length_target':float(np.linalg.norm(Ht-K)),
   'whole_upper_head_both_complete_arms_rigid_rotation_degrees':-3,'one_upper_rigid_native_matrix':UN.tolist(),'same_true_rods_closed_grips_rigid_scene_matrix':US.tolist(),
   'true_points_source_FINAL078':points,'true_points_target_F082':new,'rigid_projected_rod_checks':rods,'crane_plane_inclination_degrees':55,'added_projected_assembly_roll_degrees':-3,'total_projected_assembly_roll_from_FINAL074_degrees':-6,
   'curved_active_to_static_boundary_y_by_native_x':boundary.tolist(),'new_join_allowance_from_preceding_semantic_seam_native':30,'hard_y1210down_static':True,
   'adoption_mask':'masks/F082_ACTIVE_UPPER_BOTH_THIGHS_AND_MOVING_KNEE_CONNECTOR.png','adoption_domain_pixels':int(adopt.sum()),'all18457_preceding_natural_join_pixels_inside_new_active_domain':True,
   'hard_shoe_ankle_guard_pixels':int(foot_guard.sum()),'fixed_visible_RGBA_pixels_equal_original074':int(fixed_visible.sum()),'fixed_reference_RGBA_changes':int(np.count_nonzero(np.any(n[fixed]!=B[fixed],axis=1))),
   'no_newly_generated_shin_ankle_shoe_adoption':True,'source_reference_pixels_adopted_as_final_art':0,'new_model_calls':0,'new_actual082_Canvas':0,
   'joint_estimate_uncertainty_native':'about15to25px visible estimates; no hidden3D/bone proof','reference_interpolation_is_not_a_natural_redraw':True,
   'source_controls':src.tolist(),'target_controls':dst.tolist()}
(O/'geometry/F082_COMPLETE_ACTIVE_RISE_TRUE_CONTACTS_AND_SUPPORT_DOMAIN.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps({k:v for k,v in g.items() if k not in ['source_controls','target_controls','curved_active_to_static_boundary_y_by_native_x']},indent=2))
