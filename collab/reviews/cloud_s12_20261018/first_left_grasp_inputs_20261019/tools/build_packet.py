"""Build REVIEW-ONLY S12 first-left-grasp references. Never calls a generator/renderer."""
from pathlib import Path
import csv, hashlib, json, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
S12 = ROOT.parent
REPO = S12.parents[2]
MOTHER = S12/'d01_F000/same_raw_fix_20261019/candidate/F000.png'
IDENTITY = S12/'d01_F000/inputs/identity03_original.png'
ACTUAL = S12/'d01_F000/same_raw_fix_20261019/actual_scene/F000_Canvas.png'
EXPECTED = '95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(MOTHER) == EXPECTED
for d in ['inputs','reference','masks','geometry','prompts','requests','provenance','qa']:
    (ROOT/d).mkdir(exist_ok=True)
shutil.copyfile(MOTHER,ROOT/'inputs/locked_F000.png')
shutil.copyfile(IDENTITY,ROOT/'inputs/identity03_original.png')
mother = Image.open(MOTHER).convert('RGBA')
assert mother.size == (1024,1536)
g = json.loads((S12/'geometry/three_key_pose_proposal.json').read_text())
A = g['states'][0]
H = 293*.70
L1,L2,LG = .86*H,.64*H,.23*H
S = np.array([725.8,590.8,60.])
E0 = np.array([784.6,675.5,0.])
E0[2] = S[2] + math.sqrt(L1**2-np.linalg.norm(E0[:2]-S[:2])**2)
W0 = np.array([891.7,702.1,0.])
W0[2] = E0[2] - math.sqrt(L2**2-np.linalg.norm(W0[:2]-E0[:2])**2)
G0 = np.array([925.,702.1,0.])
G0[2] = W0[2] - math.sqrt(LG**2-np.linalg.norm(G0[:2]-W0[:2])**2)
end = np.array(A['points_scene']['free_gripL'])
attachment = np.array(A['points_scene']['P_neck'])
frac = (958-end[0])/(attachment[0]-end[0])
G1xy = end + frac*(attachment-end)
v = np.array(A['free_rod_grip_points_H']['L'])*(1-frac)+np.array(A['points_H']['P_neck'])*frac
pitch,yaw = map(math.radians,[12,15])
G1z = 215*(-math.sin(pitch)*v[1]+math.cos(pitch)*(math.sin(yaw)*v[0]+math.cos(yaw)*v[2]))
G1 = np.r_[G1xy,G1z]
W1 = np.array([916.,771.,G1z+math.sqrt(LG**2-np.linalg.norm(G1xy-np.array([916.,771.]))**2)])
spec = [(0,0,'ANCHOR FROM locked F000',False),
        (12,.32,'OPEN: whole arm advances',False),
        (18,.70,'OPEN: elbow + wrist follow',False),
        (22,.90,'THUMB FIRST: no closed grasp',False),
        (26,.98,'INDEX HOOK: not yet full grasp',False),
        (30,1.,'CLOSED LEFT: cloth still supports crane',True)]
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=lambda n:ImageFont.truetype(font_path,n)
BG=(242,244,243); INK=(29,43,57); BLUE=(55,141,193); SKIN=(102,181,216); GOLD=(232,169,45)
nearS=np.array([643.2,612.5]); nearE=np.array([674.,775.6]); nearW=np.array([805.6,812.])
nearTip=np.array([883.3,830.9])
def native(p): return (np.asarray(p)[:2]-[275,112])/.7
def scene(p): return np.asarray(p)*.7+[275,112]
def native_tuple(p): return tuple(native(p))
def capsule(draw,a,b,r0,r1,color,outline=INK,scale=1):
    a=np.array(a,dtype=float);b=np.array(b,dtype=float);v=b-a;v/=np.linalg.norm(v);n=np.array([-v[1],v[0]])
    q=[a+n*r0,b+n*r1,b-n*r1,a-n*r0]
    draw.polygon([tuple(x) for x in q],fill=color)
    for p,r in ((a,r0),(b,r1)):
        draw.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=color)
    draw.line([tuple(a+n*r0),tuple(b+n*r1)],fill=outline,width=max(1,int(scale*1.1)))
    draw.line([tuple(a-n*r0),tuple(b-n*r1)],fill=outline,width=max(1,int(scale*1.1)))
    # Shaded cross-sections communicate a solid cylinder, not a stick figure.
    for u in [.25,.5,.75]:
        p=a+(b-a)*u;r=r0+(r1-r0)*u
        draw.ellipse((p[0]-r*.95,p[1]-r*.28,p[0]+r*.95,p[1]+r*.28),outline=(225,239,245),width=max(1,int(scale*.8)))
def skeleton(draw,pts,T,width=2):
    draw.line([T(pts[k]) for k in ['S','E','W','G']],fill=(24,71,107),width=width)
    for k in ['S','E','W','G']:
        x,y=T(pts[k]);r=width*1.4
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(249,251,254),outline=INK,width=1)
def hand_shapes(stage):
    # All coordinates relative to wrist, in SCENE pixels. Construction only.
    palm=[(0,-8),(16,-17),(35,-16),(48,-8),(47,2),(33,11),(13,10),(0,8)]
    if stage in (0,12,18):
        palm=[(0,-8),(20,-13),(40,-7),(45,2),(35,13),(16,13),(0,8)]
        fingers=[[(40,-6),(56,-2),(65,8)],[(41,0),(54,7),(58,17)],[(38,6),(49,13),(50,20)],[(33,10),(41,16),(40,21)]]
        thumb=[(20,10),(34,17),(43,19)]
    elif stage==22:
        fingers=[[(43,-7),(57,-3),(61,7)],[(42,-1),(53,3),(53,8)],[(38,5),(46,7),(45,8)],[(33,7),(39,8),(39,9)]]
        # Tip touches the upper surface of the FIXED neck rod; other fingers above it.
        axis=(attachment-end)/np.linalg.norm(attachment-end)
        normal=np.array([-axis[1],axis[0]])
        w=next(s['points']['W'][:2] for s in stages if s['frame']==22)
        tip=G1xy-normal*(3.5+3.3)-w
        thumb=[(23,9),(35,9),tuple(tip)]
    elif stage==26:
        fingers=[[(46,-5),(55,4),(50,18)],[(40,0),(49,6),(47,11)],[(35,6),(43,9),(40,12)],[(29,9),(35,12),(32,14)]]
        thumb=[(23,8),(34,12),(42,9)]
    else:
        fingers=[[(46,-5),(55,4),(50,16)],[(40,0),(49,8),(44,16)],[(35,5),(42,11),(38,15)],[(29,9),(35,13),(31,14)]]
        thumb=[(23,8),(34,12),(42,8)]
    return palm,fingers,thumb

stages=[]
for frame,t,label,closed in spec:
    W=W0+(W1-W0)*t
    u=W-S;D=np.linalg.norm(u);u/=D
    a=(L1**2-L2**2+D**2)/(2*D);C=S+a*u
    r=math.sqrt(L1**2-a*a);n=E0-C;n-=np.dot(n,u)*u
    E=C+r*n/np.linalg.norm(n)
    vv=(G0-W0)*(1-t)+(G1-W1)*t
    G=W+LG*vv/np.linalg.norm(vv)
    B=W+.25*(E-W)
    pts={'S':S,'E':E,'W':W,'G':G,'B':B}
    stages.append({'frame':frame,'progress':t,'label':label,'fully_closed':closed,'points':pts})

def draw_volume(im,st,T,scale=1,show_near=True,labels=True,proximal_hidden=False):
    d=ImageDraw.Draw(im);p=st['points'];S2,E,W=[np.array(T(p[k])) for k in ['S','E','W']]
    if show_near:
        capsule(d,T(nearS),T(nearE),22*scale,16*scale,(189,184,181),scale=scale)
        capsule(d,T(nearE),T(nearW),16*scale,10*scale,(189,184,181),scale=scale)
        d.line([T(nearW),T(nearTip)],fill=(124,116,112),width=max(1,int(12*scale)))
    cuff=S2+.68*(E-S2)
    capsule(d,S2,cuff,26*scale,23*scale,BLUE,scale=scale)
    if proximal_hidden:
        # Proximal shoulder is under the existing blouse, not a ball painted on its front.
        hidden_end=S2+.25*(E-S2)
        capsule(d,S2,hidden_end,26*scale,25*scale,(211,225,232),outline=(136,165,183),scale=scale)
    capsule(d,cuff,E,19*scale,16*scale,SKIN,scale=scale)
    capsule(d,E,W,16*scale,9*scale,SKIN,scale=scale)
    x,y=T(p['B']);d.ellipse((x-10*scale,y-14*scale,x+10*scale,y+14*scale),fill=(58,141,116),outline=INK,width=max(1,int(2*scale)))
    d.ellipse((x-5*scale,y-9*scale,x+5*scale,y+9*scale),fill=SKIN,outline=(47,109,92),width=max(1,int(scale)))
    palm,fingers,thumb=hand_shapes(st['frame'])
    conv=lambda q:T(p['W'][:2]+q)
    d.polygon([conv(np.array(q)) for q in palm],fill=SKIN,outline=INK,width=max(1,int(scale)))
    for path in fingers:
        for a,b in zip(path,path[1:]):capsule(d,conv(np.array(a)),conv(np.array(b)),3.2*scale,2.8*scale,SKIN,scale=scale)
    for a,b in zip(thumb,thumb[1:]):capsule(d,conv(np.array(a)),conv(np.array(b)),4.1*scale,3.3*scale,GOLD,scale=scale)
    skeleton(d,p,T,max(1,int(scale*1.3)))
    if labels:
        for k,offset in [('S',(-32,-23)),('E',(6,-23)),('W',(-26,15)),('G',(6,16))]:
            x,y=T(p[k]);d.text((x+offset[0]*scale,y+offset[1]*scale),k,fill=INK,font=font(max(11,int(11*scale))))
    return d

def rods(d,T,scale=1):
    for name in ['L','R']:
        f=np.array(A['points_scene']['free_grip'+name]);e=np.array(A['points_scene']['P_neck' if name=='L' else 'P_body'])
        d.line([T(f),T(e)],fill=(55,39,27),width=max(1,round(7*scale)))
        d.line([T(f),T(e)],fill=(192,147,77),width=max(1,round(3*scale)))
    d.line([T([1000,800]),T([1080,800])],fill=(111,86,71),width=max(1,int(5*scale)))

def actual_gray():
    c=Image.new('RGBA',mother.size,(*BG,255))
    # Diagnostic ghost; never an edited production candidate.
    rgb=ImageOps.grayscale(mother.convert('RGB')).convert('RGB')
    rgb=Image.blend(Image.new('RGB',mother.size,'white'),rgb,.32).convert('RGBA')
    rgb.putalpha(mother.getchannel('A'))
    c=Image.alpha_composite(c,rgb)
    # Suppress the OLD far skin/bangle/hand in this diagnostic only; avoid a spare ghost arm.
    d=ImageDraw.Draw(c)
    d.polygon([(668,764),(714,745),(754,778),(820,790),(900,789),(1015,790),(1016,908),(899,909),(818,880),(735,867),(690,833)],fill=(*BG,255))
    return c

def edit_envelope(st):
    # White = guidance to redraw whole far sleeve/arm/hand, not a tool mask API.
    mask=Image.new('L',mother.size);md=ImageDraw.Draw(mask)
    for p in (stages[0]['points'],st['points']):
        for a,b,r in [('S','E',46),('E','W',31)]:
            md.line([native_tuple(p[a]),native_tuple(p[b])],fill=255,width=round(2*r/.7))
            for k in (a,b):
                x,y=native(p[k]);rr=r/.7;md.ellipse((x-rr,y-rr,x+rr,y+rr),fill=255)
        wx,wy=native(p['W']);md.rounded_rectangle((wx-22,wy-42, min(1023,wx+106),wy+53),radius=20,fill=255)
    return mask

for st in stages[1:]:
    f=st['frame'];im=actual_gray();T=lambda p:tuple(native(p))
    draw_volume(im,st,T,1/.7,False,proximal_hidden=True)
    d=ImageDraw.Draw(im);rods(d,T,1/.7)
    # Redraw foreground index hook for actual layer explanation at contact stages.
    if f in [26,30]:
        p=st['points'];_,fingers,_=hand_shapes(f)
        path=fingers[0]
        for a,b in zip(path,path[1:]):capsule(d,T(p['W'][:2]+a),T(p['W'][:2]+b),3.2/.7,2.8/.7,SKIN,scale=1/.7)
    d.rectangle((0,0,1024,129),fill=BG)
    d.text((22,15),f'F{f:03d} | CONSTRUCTION ONLY',font=font(28),fill=INK)
    d.text((22,53),'NOT CHARACTER ART / NOT AN ACTUAL FUTURE FRAME',font=font(20),fill=(165,62,32))
    d.text((22,89),st['label'],font=font(20),fill=INK)
    d.rectangle((0,1400,1024,1536),fill=BG)
    d.text((22,1413),'Native 1024x1536 | B=.70 + (275,112)',font=font(22),fill=INK)
    d.text((22,1451),'Keep mother head/body/near empty hand/legs fixed.',font=font(20),fill=INK)
    d.text((22,1484),'Blue=far-arm VOLUME; gold=thumb; grey=locked mother.',font=font(18),fill=INK)
    d.text((22,1510),'Pale proximal volume is HIDDEN under blouse; not a chest ball.',font=font(17),fill=INK)
    im.convert('RGB').save(ROOT/f'inputs/F{f:03d}_CONSTRUCTION.png')
    edit_envelope(st).save(ROOT/f'masks/F{f:03d}_far_arm_envelope_GUIDE.png')

# Full arm overview at a fixed scene scale, preserving whole S-E-W chain.
board=Image.new('RGB',(1800,1170),BG);d=ImageDraw.Draw(board)
d.text((24,16),'S12 F000 -> F030 | WHOLE FAR-ARM VOLUMES | REVIEW PROPOSAL',font=font(29),fill=INK)
d.text((24,58),'CONSTRUCTION ONLY. No generated art. Shoulder location/depth are estimates; actual F000 remains locked.',font=font(18),fill=(154,66,37))
for j,st in enumerate(stages):
    x0=(j%3)*600;y0=100+(j//3)*525
    panel=Image.new('RGB',(580,398),BG)
    pd=ImageDraw.Draw(panel)
    T=lambda p:tuple((np.array(p)[:2]-[610,555])*1.40+[8,15])
    draw_volume(panel,st,T,1.4,True)
    rods(pd,T,1.4)
    board.paste(panel,(x0+10,y0+55))
    d.rounded_rectangle((x0+8,y0+5,x0+592,y0+511),radius=12,outline=(172,185,191),width=2)
    d.text((x0+22,y0+19),f"F{st['frame']:03d}  {st['label']}",font=font(16),fill=INK)
    d.text((x0+22,y0+454),'Near right = grey, EMPTY / upper rod = neck3',font=font(15),fill=INK)
    d.text((x0+22,y0+480),'Upper .86H | forearm .64H | wrist->G .23H',font=font(15),fill=INK)
board.save(ROOT/'reference/01_full_arm_progression_CONSTRUCTION.jpg',quality=94)

# Three contact drawings: whole distal forearm + wrist + bangle + all digits.
contact=Image.new('RGB',(1800,1000),BG);d=ImageDraw.Draw(contact)
d.text((20,14),'THUMB -> INDEX -> FULL GRASP | fixed rods / crane remains on cloth',font=font(29),fill=INK)
d.text((20,57),'CONSTRUCTION, NOT ART. Blue hand is a contact/volume guide only. Rod width includes the actual 7px outline.',font=font(18),fill=(154,66,37))
for j,st in enumerate(stages[3:]):
    x0=j*600
    d.text((x0+20,105),f"F{st['frame']:03d} {st['label']}",font=font(17),fill=INK)
    panel=Image.new('RGB',(580,480),BG);pd=ImageDraw.Draw(panel)
    T=lambda p:tuple((np.array(p)[:2]-[860,727])*4+[12,30])
    draw_volume(panel,st,T,4,False,False)
    rods(pd,T,4)
    if st['frame'] in [26,30]:
        _,fs,_=hand_shapes(st['frame']);p=st['points']
        for a,b in zip(fs[0],fs[0][1:]):capsule(pd,T(p['W'][:2]+a),T(p['W'][:2]+b),3.2*4,2.8*4,SKIN,scale=4)
    contact.paste(panel,(x0+10,145))
    d.text((x0+20,646),'G = (958.000, 782.166) scene px',font=font(17),fill=INK)
    d.text((x0+20,678),'Far L / ONE jade bangle / continuous wrist',font=font(16),fill=INK)
    d.text((x0+20,714),['Thumb pad touches UPPER surface.','Index hooks the lower/front face.','Thumb/index oppose; other fingers curl.'][j],font=font(16),fill=INK)
    d.text((x0+20,748),['Other fingers above shaft, still OPEN.','Ring/little remain soft, not yet tight.','Straight shaft enters/exits same line.'][j],font=font(16),fill=INK)
    d.text((x0+20,788),'Lower rod belongs to EMPTY near right hand.',font=font(16),fill=INK)
    d.text((x0+20,820),'Do not grip both rods or move either endpoint.',font=font(16),fill=INK)
    d.text((x0+20,858),'Illustrated target: about 4px lower-rod clearance.',font=font(15),fill=(154,66,37))
    d.text((x0+20,891),'Actual native fingers/masks must be checked later.',font=font(15),fill=(154,66,37))
contact.save(ROOT/'reference/02_contact_sequence_CONSTRUCTION.jpg',quality=95)

# Full mother and actual scene evidence. No future scene was rendered.
ctx=Image.new('RGB',(1800,1100),BG);d=ImageDraw.Draw(ctx)
d.text((20,16),'LOCKED ACTUAL F000 ONLY | source evidence, not a future-frame preview',font=font(29),fill=INK)
small=Image.new('RGBA',mother.size,(210,212,214,255));small=Image.alpha_composite(small,mother);small.thumbnail((600,960))
ctx.paste(small.convert('RGB'),(20,100))
actual=Image.open(ACTUAL).convert('RGB');actual.thumbnail((1140,642));ctx.paste(actual,(640,100))
d.text((640,770),'Approved mother: 95f80f2d...1ed793 (complete SHA in README)',font=font(20),fill=INK)
d.text((640,811),'Registration .70+(275,112) | neck3 and body rods rest on rim.',font=font(19),fill=INK)
d.text((640,852),'First segment keeps the crane root, 55-degree plane, rod endpoints,',font=font(18),fill=INK)
d.text((640,884),'box, cloth contact, near empty hand and both knees/shoes fixed.',font=font(18),fill=INK)
d.text((640,940),'F034 upper-handle rise is outside this proposed segment.',font=font(20),fill=(154,66,37))
ctx.save(ROOT/'reference/00_locked_actual_F000_context.jpg',quality=94)

# Depth and split contract: prospective construction, no actual pixel masks fabricated.
dep=Image.new('RGB',(1600,1140),BG);d=ImageDraw.Draw(dep)
d.text((22,16),'DEPTH + LAYER CONTRACT | REVIEW CONSTRUCTION ONLY',font=font(30),fill=INK)
d.text((22,62),'View depth is an IK construction proxy, NOT measured hidden anatomy. Near right remains unchanged.',font=font(18),fill=(154,66,37))
for i,st in enumerate([stages[0],stages[2],stages[-1]]):
    T=lambda p,i=i:tuple((np.array([p[0],p[2]])-[700,30])*1.7+[35+i*525,160])
    ps=st['points'];capsule(d,T(ps['S']),T(ps['E']),21,16,BLUE,scale=1)
    capsule(d,T(ps['E']),T(ps['W']),15,9,SKIN,scale=1)
    d.line([T(ps['W']),T(ps['G'])],fill=GOLD,width=8)
    d.text((35+i*525,115),f"F{st['frame']:03d} x / construction depth",font=font(19),fill=INK)
    for k in ['S','E','W','G']:
        x,y=T(ps[k]);d.ellipse((x-4,y-4,x+4,y+4),fill=INK);d.text((x+6,y+4),k,font=font(16),fill=INK)
    d.text((35+i*525,490),'Depth stays on FAR side, no elbow pop.',font=font(16),fill=INK)
d.text((35,560),'Back -> front at the grasp (proposal for the integrator):',font=font(24),fill=INK)
rows=[('1', 'Locked room / contact shadows / box back / cloth', (200,203,205)),
      ('2', 'Actual new native body + rear far palm/arm pixels',BLUE),
      ('3', 'Unchanged actual CODE neck3 rod and crane (same endpoints)',GOLD),
      ('4', 'Actual native thumb/index FRONT pixels, exclusive partition',SKIN),
      ('5', 'Box front where applicable; hands remain left of x=1000', (151,109,77))]
for j,(num,txt,col) in enumerate(rows):
    y=610+j*69;d.rounded_rectangle((35,y,105,y+48),radius=9,fill=col,outline=INK);d.text((60,y+7),num,font=font(24),fill=INK)
    d.text((130,y+10),txt,font=font(20),fill=INK)
d.text((35,995),'F000 module currently puts all props above person: DO NOT reuse that order unchanged for a grasp.',font=font(19),fill=(154,66,37))
d.text((35,1030),'Future rear/front masks must partition ACTUAL generated native pixels and reconstruct RGBA exactly.',font=font(18),fill=INK)
d.text((35,1065),'This packet has NO future native pixels, no fabricated grip masks and no changed scene module.',font=font(18),fill=INK)
dep.save(ROOT/'reference/03_depth_and_layers_CONSTRUCTION.jpg',quality=94)

whole=Image.new('RGB',(1400,1160),BG);d=ImageDraw.Draw(whole)
d.text((20,12),'WHOLE BODY: F012 / F030 CONSTRUCTION | NO FUTURE ART',font=font(26),fill=INK)
for i,f in enumerate([12,30]):
    im=Image.open(ROOT/f'inputs/F{f:03d}_CONSTRUCTION.png');im.thumbnail((700,1050));whole.paste(im,(i*700,75))
whole.save(ROOT/'reference/04_whole_body_start_end_CONSTRUCTION.jpg',quality=94)

serialized=[]
for st in stages:
    serialized.append({k:v for k,v in st.items() if k!='points'}|{
      'points_scene_xy_depth_proxy':{k:v.tolist() for k,v in st['points'].items()},
      'points_native_xy':{k:native(v).tolist() for k,v in st['points'].items()},
      'bone_lengths_scene_proxy':{'upper_arm':float(np.linalg.norm(st['points']['E']-S)),
          'forearm':float(np.linalg.norm(st['points']['W']-st['points']['E'])),
          'wrist_to_G':float(np.linalg.norm(st['points']['G']-st['points']['W']))}})
geometry={
 'status':'PROPOSED REFERENCES / NOT GENERATED / ASTRA GATE REQUIRED',
 'head_H_scene':H,'head_H_native':293,'registration':{'scale':.7,'x':275,'y':112},
 'source_mother_sha256':EXPECTED,
 'manual_measurement_uncertainty_native_px':[10,20],
 'depth_model_note':'View-space construction only. Shoulder xy hidden estimate; z is not observed anatomy. Fixed lengths validate this drawing guide, not a future drawing.',
 'bone_lengths_H':{'upper_arm':.86,'forearm':.64,'wrist_to_G':.23},
 'fixed_upper_rod':{'free_end_scene':end.tolist(),'neck3_attachment_scene':attachment.tolist(),
    'grasp_G_scene':G1.tolist(),'grasp_fraction_from_free_end':frac,
    'free_end_to_G_scene_projected_px':float(np.linalg.norm(G1xy-end)),
    'stroke_width_scene_px':7},
 'fixed_lower_rod':{'free_end_scene':A['points_scene']['free_gripR'],'body_attachment_scene':A['points_scene']['P_body'],'stroke_width_scene_px':7},
 'fixed_crane':{'root_scene':A['points_scene']['crane_root'],'plane_tilt_degrees':55,'cloth_supported_through_frame':33},
 'near_R_unchanged_native':{'shoulder':[526,715],'elbow':[570,948],'wrist':[758,1000],'fingertip':[869,1027]},
 'bangle_rule':'One FAR LEFT jade bangle, proxy centre .25 forearm length proximal to wrist (.16H); bangle is not the wrist joint.',
 'G_note':'When open, G is a future contact construction landmark, not skin contact or palm centroid. F022 only thumb pad first touches; full left grasp is F030.',
 'stages':serialized}
(ROOT/'geometry/stages_PROPOSAL.json').write_text(json.dumps(geometry,ensure_ascii=False,indent=2)+'\n')

with (S12/'exposure_192f_PROPOSAL.csv').open() as f: rows=list(csv.DictReader(f))
selected=[r for r in rows if 12<=int(r['start'])<=30]
with (ROOT/'exposure_first_left_grasp.csv').open('w') as f:
    out=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');out.writeheader();out.writerows(selected)
assert [int(r['start']) for r in selected]==[12,18,22,26,30]
assert sum(int(r['hold']) for r in selected)==22

common='''S12 drawn animation, one native transparent 1024x1536 RGBA frame. Image 1 is the LOCKED actual mother F000, SHA256 95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793. Preserve this exact grandmother identity, fine silver hair and round thin glasses, neutral skin and dusty blue white-flower blouse, dark trousers and both complete cloth shoes. Image 2 is original identity03 for same-material PALETTE only, not its pose. Image 3 is a clearly labelled CONSTRUCTION guide for the complete FAR LEFT arm, not a finished drawing: ignore all blue/grey/gold diagram colors, lettering, dots, rods and bone lines. Use the guide's anatomical volumes and native coordinates; keep mother colors and line quality. The image 3 ghost mother is construction context only.\n\nDraw ONE whole grandmother on the SAME native canvas and framing. Keep mother head, facial gaze, neck, chest, pelvis, knees/shins/shoes and the complete NEAR RIGHT open empty hand unchanged in placement and identity; preserve body continuity. The allowed motion is the FAR LEFT arm from its shoulder under the blouse through the full upper arm, elbow, forearm, wrist and complete hand. Redraw the far sleeve together with the arm; cleanly remove the previous arm silhouette. Do not paste or translate an isolated hand. The far elbow stays visibly outside the torso silhouette. The arm may shorten by projection but its upper .86H and forearm .64H actual bone lengths must not change. Hidden far shoulder is estimated at native (644,684), +/-10-20px, not a point to dislocate. Keep ONE jade bangle on the far LEFT forearm proximal to its wrist; the near RIGHT forearm has no bangle. Fingers must have coherent knuckle volumes and naturally curved phalanges, thumb on opposite side to index, no extra digits or stretched palm.\n\nScene registration remains scale .70 at (275,112) on a 1920x1080 scene. In this segment the code neck3 rod is fixed from scene (934.3125,785.1297) to (1497.5315,714.6642), outline width7px. Proposed first-grasp centre G is scene (958,782.166145), native (975.714286,957.380208). The lower/body rod stays at scene (951.2617,798.9063) to (1282.1987,773.9468), outline width7px, and belongs to the STILL EMPTY near right hand. These rods are CONTACT GUIDES ONLY. Do NOT paint any rod, crane, cloth, box, cast shadow, scenery, diagram, words or arrows into the native character. The code shaft must later pass through the grasp with real native finger occlusion; draw fingers/palm coherently around this guide axis. Do not grip both rods, move the prop, lift the crane, raise the torso, swap hands or crop any shoe. The crane remains supported on the cloth.\n\nPreserve mother material colors: skin, blouse, hair, trousers each must compare to locked mother same-material masks within +/-4 per RGB channel on means, protected ink/white flowers and form shading retained; do not lighten skin or saturate blue. Transparent background, clean antialiasing with all fine hair/glasses preserved. All outline bounds must fit the native canvas with breathing room, especially the rightmost fingers. Do not replace the character with the construction figure.\n\n'''
stage_text={12:'F012 (held F012-F017): FIRST APPROACH. Both hands are still EMPTY and relaxed. Far upper arm and forearm move down/forward as a continuous chain. No digit touches either rod; closest fingertip remains clearly above the upper rod. Keep all fingers soft, not five-way spread.',
18:'F018 (held F018-F021): SECOND APPROACH. Far elbow follows forward and down, wrist and relaxed fingers follow. Hand is near the upper rod but no contact yet; leave at least 3 scene pixels between all finger skin and the 7px rod outline. Near right still empty.',
22:'F022 (held F022-F025): THUMB FIRST CONTACT. Only the far left thumb PAD gently touches the upper surface of the neck3 rod near G; other fingers remain above the shaft, not wrapped. Draw the full thumb through thenar base, joints and tip; no full grasp yet. The rod and crane remain completely stationary.',
26:'F026 (held F026-F029): INDEX HOOK. Far left index bends around the lower/front face of the upper rod against the thumb. Ring/little fingers remain soft, not clenched. Contact reads as an index/thumb opposing pair; this is not yet a full palm closure. Leave the lower/body rod untouched and visible, with at least 3 scene pixels between its outline and skin.',
30:'F030 (held F030-F033): FIRST COMPLETE LEFT GRASP. Palm settles from above, thumb pad opposes the index around the 7px upper shaft; remaining fingers curl naturally around the SAME shaft. Wrist (native approx915.7,941.4) joins the forearm naturally, palm mass mainly above the shaft. The lower/body rod stays separate, untouched and at least 3 scene pixels clear of any finger. Full grip must fit before native x1024. Do not raise the upper handle or lift the crane; F034 onward is outside this request.'}
for st in stages[1:]:
    f=st['frame'];ps=serialized[[s['frame'] for s in stages].index(f)]['points_native_xy']
    pointtext='\nConstruction anchor estimates in native pixels, not a substitute for actual image review:\n'+json.dumps({k:[round(x,3) for x in ps[k]] for k in ['S','E','W','G','B']},ensure_ascii=False)+'\n'
    text=common+"Palette priority: the LOCKED F000 (image 1) is the exact color authority. Image 2 records identity03 lineage only; do not shift the locked mother toward it. The pale proximal volume on image 3 is HIDDEN under the blouse. Never paint an exposed shoulder ball on the chest.\n\n"+stage_text[f]+pointtext
    prompt_path=ROOT/f'prompts/F{f:03d}.txt';prompt_path.write_text(text)
    args={'prompt':text,'referenced_image_paths':[str(ROOT/'inputs/locked_F000.png'),str(ROOT/'inputs/identity03_original.png'),str(ROOT/f'inputs/F{f:03d}_CONSTRUCTION.png')],'transparent_background':True}
    request={'status':'PREPARED ACTUAL INPUTS; NOT EXECUTED; ASTRA REFERENCE GATE REQUIRED','tool':'image_gen.imagegen','execution_enabled':False,'frame':f,'hold':next(int(r['hold']) for r in selected if int(r['start'])==f),'tool_arguments':args,'input_sha256':[{ 'path':str(Path(p).relative_to(REPO)), 'sha256':sha(Path(p))} for p in args['referenced_image_paths']],'prompt_file':str(prompt_path.relative_to(ROOT)),'do_not_batch':'After reference approval, execute F012 only and review actual output before any next call. All stages anchor material/identity to same locked mother, not an accumulating previous-frame color.'}
    (ROOT/f'requests/F{f:03d}_NOT_EXECUTED.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')

sources=[MOTHER,IDENTITY,ACTUAL,S12/'exposure_192f_PROPOSAL.csv',S12/'geometry/three_key_pose_proposal.json',S12/'d01_F000/qa/actual_native_landmark_estimates.json',S12/'d01_F000/same_raw_fix_20261019/scene/s12_F000_scene.js']
(ROOT/'provenance/source_manifest.json').write_text(json.dumps({'source_commit':'d6406a886286f313cb3431d081100854dae7694b','mother_locked_by_latest_parent':True,'sources':[{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')

errors=[]
for s in serialized:
    for key,expected in [('upper_arm',L1),('forearm',L2),('wrist_to_G',LG)]:errors.append(abs(s['bone_lengths_scene_proxy'][key]-expected))
assert max(errors)<1e-9
assert sha(ROOT/'inputs/locked_F000.png')==EXPECTED
requests=[json.loads((ROOT/f'requests/F{f:03d}_NOT_EXECUTED.json').read_text()) for f in [12,18,22,26,30]]
assert all(not r['execution_enabled'] for r in requests)
assert all(Path(p).is_file() for r in requests for p in r['tool_arguments']['referenced_image_paths'])
# Objective gaps for the illustrated digit capsules, not future native art.
closed=stages[-1];_,fingers,thumb=hand_shapes(30)
lower0=np.array(A['points_scene']['free_gripR']);lower1=np.array(A['points_scene']['P_body']);axis=lower1-lower0
def gap(st,rod0,rod1,include_thumb=True):
    _,fs,th=hand_shapes(st['frame']);result=[];axis=rod1-rod0
    for paths in [fs]+([[th]] if include_thumb else []):
        is_thumb=paths==[th]
        for path in paths:
            for a,b in zip(path,path[1:]):
                for t in np.linspace(0,1,101):
                    q=st['points']['W'][:2]+np.array(a)*(1-t)+np.array(b)*t
                    u=np.clip(np.dot(q-rod0,axis)/np.dot(axis,axis),0,1)
                    radius=(4.1*(1-t)+3.3*t) if is_thumb else (3.2*(1-t)+2.8*t)
                    result.append(float(np.linalg.norm(q-(rod0+u*axis))-3.5-radius))
    return min(result)
dist=[gap(closed,lower0,lower1)]
assert min(dist)>=3
early={f:gap(next(s for s in stages if s['frame']==f),end,attachment) for f in [12,18]}
assert min(early.values())>=3
st22=next(s for s in stages if s['frame']==22)
_,_,th22=hand_shapes(22);q22=st22['points']['W'][:2]+th22[-1]
axis=attachment-end;u22=np.dot(q22-end,axis)/np.dot(axis,axis)
thumb22_gap=float(np.linalg.norm(q22-(end+u22*axis))-3.5-3.3)
assert abs(thumb22_gap)<1e-9
assert gap(st22,end,attachment,False)>=1
handmax=max(q[0] for path in fingers+[thumb] for q in path)+closed['points']['W'][0]+4.1
qa={'kind':'REFERENCE GEOMETRY AND INPUT CHECK ONLY; not future art/scene approval','imagegen_calls_this_packet':0,'new_native_art':0,'new_scene_renders':0,'S24_renders':0,'selected_frames':[12,18,22,26,30],'selected_exposure_total_frames':22,'last_frame_inclusive':33,'F034_excluded':True,'approved_csv_rows_copied_without_change':True,'max_fixed_proxy_bone_length_error_px':max(errors),'open_construction_digit_to_upper_rod_clearance_scene_px':early,'F022_thumb_pad_gap_to_upper_rod_scene_px':thumb22_gap,'F022_other_digit_min_gap_scene_px':gap(st22,end,attachment,False),'closed_construction_min_lower_rod_outline_clearance_scene_px':min(dist),'closed_construction_max_hand_x_scene_px':handmax,'closed_construction_max_hand_x_native_px':float(native([handmax,0])[0]),'construction_clearances_are_not_future_art_proof':True,'all_5_requests_disabled':True,'all_15_input_references_exist':True,'mother_copy_sha256':sha(ROOT/'inputs/locked_F000.png'),'identity03_copy_sha256':sha(ROOT/'inputs/identity03_original.png'),'scene_and_shared_files_modified':0,'actual_contact_and_ink_alpha_colour_checks_pending_new_native':True}
(ROOT/'qa/geometry_and_inputs_validation.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa,indent=2))
