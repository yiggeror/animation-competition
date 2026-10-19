"""Batch INPUT GATE only: native-aligned volumes/contact references; no art generation/render."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,json,hashlib,shutil,csv,textwrap
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
source=S/'d03_F018_20261019/same_raw_fix_20261019/candidate/F018.png';palette=S/'d03_F018_inputs_20261019/inputs/02_locked_F000_materials_ONLY.png'
assert sha(source)=='c63f57f53bc2f4bbca59dba4310ea55c0629b354520f8d0becbe88f932ff40be';assert sha(palette)=='a6a40d2e847b9a9256f20edb46cf8467fe7487deb0dc97448674ec7c7b5e22cd'
shutil.copyfile(source,O/'inputs/01_locked_F018.png');shutil.copyfile(palette,O/'inputs/02_locked_F000_materials_ONLY.png')
BG=(241,243,242);INK=(29,43,57);BLUE=(95,180,213);GOLD=(236,179,53);FRONT=(85,130,194);H=293.;L1=.86*H;L2=.64*H
old=json.loads((S/'first_left_grasp_inputs_20261019/geometry/stages_PROPOSAL.json').read_text());reg=np.array([275.,112.]);scale=.7
upper_start=(np.array(old['fixed_upper_rod']['free_end_scene'])-reg)/scale;upper_end=(np.array(old['fixed_upper_rod']['neck3_attachment_scene'])-reg)/scale
lower_start=(np.array(old['fixed_lower_rod']['free_end_scene'])-reg)/scale;lower_end=(np.array(old['fixed_lower_rod']['body_attachment_scene'])-reg)/scale
G=(np.array(old['fixed_upper_rod']['grasp_G_scene'][:2])-reg)/scale;U=(upper_end-upper_start)/np.linalg.norm(upper_end-upper_start);N=np.array([-U[1],U[0]]);rodR=3.5/scale
thumb_radius=6.;thumb_pad=G-N*(rodR+thumb_radius)
index_pad=G+N*6.5;pads=[G-U*(8.5*j)+N*6.5 for j in range(4)]
# Complete hand volumes are measured in the actual locked018 hand's scale, not old wrist-G=.23H.
# Landmarks are manual surface estimates, not claims about unseen joints.
stages=[
 {'frame':22,'label':'THUMB PAD FIRST / OTHER DIGITS HOVER','E':[778,846],'W':[884,922],'C':[702,783],
  'palm':[[884,906],[907,898],[939,898],[962,906],[960,916],[950,928],[932,936],[909,938],[886,934]],
  'digits':[[[962,909],[985,906],[998,914],[1004,923]],[[954,919],[976,916],[990,929],[995,938]],[[947,928],[964,923],[977,932],[980,940]],[[938,934],[953,930],[962,934],[964,938]]],
  'thumb':[[932,931],[950,936],[965,942],thumb_pad.tolist()]},
 {'frame':26,'label':'INDEX WRAPS / THUMB STAYS / OTHER DIGITS LOOSE','E':[781,849],'W':[886,926],'C':[703,785],
  'palm':[[886,910],[909,902],[941,903],[967,914],[961,926],[951,934],[934,940],[911,941],[888,938]],
  'digits':[[[967,918],[985,938],[984,957],index_pad.tolist()],[[956,926],[974,924],[988,933],[992,938.5]],[[947,934],[962,928],[974,934],[978,940]],[[938,938],[950,934],[960,937],[963,940]]],
  'thumb':[[934,935],[951,939],[965,943],thumb_pad.tolist()]},
 {'frame':30,'label':'COMPLETE LEFT GRASP / RIGHT HAND STILL EMPTY','E':[783,851],'W':[888,928],'C':[704,787],
  'palm':[[888,912],[912,904],[942,905],[969,917],[963,930],[952,940],[935,944],[913,944],[890,940]],
  'digits':[[[969,921],[986,941],[984,957],pads[0].tolist()],[[958,930],[976,941],[978,957],pads[1].tolist()],[[948,937],[965,945],[968,958],pads[2].tolist()],[[939,941],[953,949],[958,961],pads[3].tolist()]],
  'thumb':[[935,938],[952,941],[965,944],thumb_pad.tolist()]}
]
S_hidden=np.array([644.,684.]);digit_L={'index':[30,24,15],'middle':[26,23,16],'ring':[25,23,15],'little':[22,19,14],'thumb':[24,18,13]}
for st in stages:
 E=np.array(st['E'],float);W=np.array(st['W'],float);Ez=np.sqrt(L1*L1-np.sum((E-S_hidden)**2));Wz=Ez-np.sqrt(L2*L2-np.sum((W-E)**2));st['S']=S_hidden.tolist();st['E_depth_proxy']=float(Ez);st['W_depth_proxy']=float(Wz);st['B']=(W+.25*(E-W)).tolist();st['bone_lengths_native_depth_proxy']={'upper':float(np.linalg.norm(np.r_[E-S_hidden,Ez])),'forearm':float(np.linalg.norm(np.r_[W-E,Wz-Ez]))}
 for name,path in zip(['index','middle','ring','little','thumb'],st['digits']+[st['thumb']]):
  lengths=np.linalg.norm(np.diff(np.array(path),axis=0),axis=1);assert np.all(lengths<=np.array(digit_L[name])+1e-8),(st['frame'],name,lengths.tolist())
 st['digit_projected_lengths_native']={name:np.linalg.norm(np.diff(np.array(path),axis=0),axis=1).tolist() for name,path in zip(['index','middle','ring','little','thumb'],st['digits']+[st['thumb']])}

def capsule(d,a,b,r0,r1,fill,T=lambda p:tuple(p),z=1.,wire=False):
 a=np.array(a,float);b=np.array(b,float);v=b-a;v/=np.linalg.norm(v);n=np.array([-v[1],v[0]]);q=[a+n*r0,b+n*r1,b-n*r1,a-n*r0]
 d.polygon([T(p) for p in q],fill=None if wire else fill,outline=INK,width=max(1,round(1.2*z)))
 for p,r in [(a,r0),(b,r1)]:
  x,y=T(p);d.ellipse((x-r*z,y-r*z,x+r*z,y+r*z),fill=None if wire else fill,outline=INK,width=max(1,round(z)))
 for t in [.28,.62]:
  p=a+t*(b-a);r=r0+t*(r1-r0);x,y=T(p);d.ellipse((x-r*.88*z,y-r*.23*z,x+r*.88*z,y+r*.23*z),outline=(216,235,242),width=max(1,round(.6*z)))
def rods(d,T,z):
 for a,b in [(upper_start,upper_end),(lower_start,lower_end)]:
  d.line([T(a),T(b)],fill=(58,41,29),width=round(10*z))
  for p in [a,b]:
   x,y=T(p);d.ellipse((x-5*z,y-5*z,x+5*z,y+5*z),fill=(58,41,29))
  d.line([T(a),T(b)],fill=(201,155,80),width=max(1,round(4.285714*z)))
  for p in [a,b]:
   x,y=T(p);r=2.142857*z;d.ellipse((x-r,y-r,x+r,y+r),fill=(201,155,80))
def path_draw(d,path,radii,color,T,z):
 for i,(a,b) in enumerate(zip(path,path[1:])):capsule(d,a,b,radii[i],radii[i+1],color,T,z)
 for p in path[:-1]:
  x,y=T(p);d.ellipse((x-1.7*z,y-1.7*z,x+1.7*z,y+1.7*z),fill=(247,250,250),outline=INK,width=max(1,round(.6*z)))
def hand(d,st,T=lambda p:tuple(p),z=1.,foreground=False):
 if not foreground:
  d.polygon([T(p) for p in st['palm']],fill=BLUE,outline=INK,width=max(1,round(1.2*z)))
  for j,path in enumerate(st['digits']):path_draw(d,path,[6.2-j*.35,5.8-j*.35,5.0-j*.30,4.6-j*.27],BLUE,T,z)
  path_draw(d,st['thumb'],[7.,6.8,6.3,thumb_radius],GOLD,T,z)
 else:
  # Source-real foreground masks are derived only after actual art; these are semantic construction labels.
  path_draw(d,st['thumb'],[7.,6.8,6.3,thumb_radius],GOLD,T,z)
  if st['frame']>=26:
   for j,path in enumerate(st['digits'] if st['frame']==30 else st['digits'][:1]):path_draw(d,path[1:],[5.8-j*.35,5.0-j*.30,4.6-j*.27],FRONT,T,z)
def volume(im,st):
 d=ImageDraw.Draw(im);E=np.array(st['E']);W=np.array(st['W']);C=np.array(st['C']);B=np.array(st['B'])
 # Full upper chain, with the hidden shoulder rendered as wire volume beneath the locked blouse.
 capsule(d,st['S'],C,30,27,(207,224,232),wire=True);capsule(d,C,E,26,25,BLUE);capsule(d,E,W,25,13,BLUE)
 x,y=B;d.ellipse((x-18,y-26,x+18,y+26),fill=(57,142,116),outline=INK,width=2);d.ellipse((x-10,y-16,x+10,y+16),fill=BLUE,outline=(36,105,86),width=1)
 hand(d,st);rods(d,lambda p:tuple(p),1.);hand(d,st,foreground=True)
 for ka,kb in [('S','E'),('E','W')]:d.line([tuple(st[ka]),tuple(st[kb])],fill=(24,70,107),width=1)
 for name in ['S','E','W']:
  x,y=st[name];d.ellipse((x-2,y-2,x+2,y+2),fill='white',outline=INK);d.text((x-18,y-20),name,font=font(15),fill=INK)
 d.text((605,650),'HIDDEN SHOULDER',font=font(13),fill=INK);d.text((606,667),'under existing blouse',font=font(12),fill=INK)
def ghost():
 a=Image.open(source).convert('RGBA');rgb=ImageOps.grayscale(a.convert('RGB')).convert('RGB');rgb=Image.blend(Image.new('RGB',a.size,'white'),rgb,.30).convert('RGBA');rgb.putalpha(a.getchannel('A'));im=Image.alpha_composite(Image.new('RGBA',a.size,(*BG,255)),rgb).convert('RGB')
 # Suppress old far exposed arm only in the REFERENCE ghost, never modify locked art.
 ImageDraw.Draw(im).polygon([(675,804),(715,748),(758,776),(839,822),(897,847),(977,852),(1023,891),(1023,978),(937,978),(889,946),(833,926),(774,895),(723,870),(682,835)],fill=BG);return im
frames=[]
for st in stages:
 f=st['frame'];im=ghost();volume(im,st);d=ImageDraw.Draw(im);d.rectangle((0,0,1024,128),fill=BG);d.text((20,17),f'F{f:03d} VOLUME + CONTACT / CONSTRUCTION ONLY',font=font(24),fill=INK);d.text((20,55),'NOT CHARACTER ART / no generated future frame',font=font(20),fill=(154,61,34));d.text((20,90),st['label'],font=font(18),fill=INK)
 d.rectangle((0,1400,1024,1536),fill=BG);d.text((20,1415),'Locked018 mother | native1024x1536 | .70+(275,112)',font=font(19),fill=INK);d.text((20,1453),'Full arm moves; head/body/near RIGHT empty hand/shoes stay.',font=font(17),fill=INK);d.text((20,1485),'Upper .86H / forearm .64H are depth proxies; check actual art.',font=font(17),fill=INK);d.text((20,1511),'Palm size follows REAL018; rod G is not a palm-bone endpoint.',font=font(17),fill=INK)
 im.save(O/f'reference/F{f:03d}_native_volume_CONSTRUCTION.png');frames.append(im)
 board=Image.new('RGB',(1600,1536),BG);board.paste(im,(0,0));dd=ImageDraw.Draw(board);dd.line((1024,0,1024,1536),fill=(180,192,197),width=2)
 dd.text((1040,20),'CONTACT DETAIL / SAME AXIS',font=font(20),fill=INK);dd.text((1040,54),'2.65X NATIVE / CONSTRUCTION ONLY',font=font(17),fill=(154,61,34));detail=im.crop((814,839,1024,1009)).resize((556,450),Image.Resampling.NEAREST);board.paste(detail,(1034,90))
 clauses=['Locked upper neck3 shaft: 7 scene px.','G=(958,782.166145) scene for all3.','Orange=thumb; dark blue=front digits.','Lower/body shaft stays CLEAR >=3 scene.','No rod/crane/cloth/box movement.','Crane remains cloth-supported through033.']
 if f==22:clauses+=['ONLY thumb PAD first touch.','All other digits hover >=3 scene.','No index hook / palm grip yet.']
 elif f==26:clauses+=['Thumb stays on SAME cross-section G.','Index wraps under/front against thumb.','Other digits soft, still above upper rod.']
 else:clauses+=['Left grasp closes around SAME shaft.','Thumb opposes curled index/middle/ring/little.','Near RIGHT hand remains empty.']
 yy=565
 for line in clauses:dd.text((1042,yy),line,font=font(16),fill=INK);yy+=32
 dd.text((1042,930),'FUTURE REAL-ART LAYER ORDER',font=font(19),fill=INK)
 for j,(title,col) in enumerate([('BACK: body / forearm / rear palm',(168,204,220)),('MIDDLE: frozen existing code rods',(201,155,80)),('FRONT: real thumb / wrapped finger pixels',(94,135,194))]):
  y=976+j*70;dd.rounded_rectangle((1040,y,1580,y+52),radius=7,fill=col,outline=INK);dd.text((1052,y+15),title,font=font(15),fill=INK)
 for j,line in enumerate(['Derive masks from ACTUAL future artwork.','Native layers must be mutually exclusive;','reconstruct the one PNG RGBA exactly.','No code fingers, no fake painted shaft.','This reference does NOT prove future contact.','022->026->030: one approved batch,','self-review each result; stop on real error.']):dd.text((1042,1221+j*35),line,font=font(16),fill=INK)
 board.save(O/f'inputs/03_F{f:03d}_VOLUME_CONTACT_CONSTRUCTION.png')
# One compact segment sheet; complete native volumes are in the three actual tool input boards.
contact=Image.new('RGB',(1680,635),BG);dd=ImageDraw.Draw(contact);dd.text((18,14),'F022 THUMB -> F026 INDEX -> F030 LEFT GRASP / CONSTRUCTION ONLY',font=font(27),fill=INK)
for i,(st,im) in enumerate(zip(stages,frames)):
 panel=im.crop((755,816,1024,1010)).resize((538,388),Image.Resampling.NEAREST);contact.paste(panel,(i*560+10,103));dd.text((i*560+17,64),f"F{st['frame']:03d} / SAME FIXED UPPER SHAFT",font=font(18),fill=INK);dd.text((i*560+15,513),['Thumb pad only; other fingers clear','Index/thumb oppose; others remain loose','Left fully closed; right still empty'][i],font=font(17),fill=INK);dd.text((i*560+15,553),'G fixed; no lift; cloth supports crane',font=font(17),fill=INK);dd.text((i*560+15,593),'Actual output must pass ink/AA contacts.',font=font(16),fill=(154,61,34))
contact.save(O/'reference/01_contact_segment_CONSTRUCTION.jpg',quality=95)
# Full exact three-image requests. Same one locked018 mother is used for identity, not earlier old poses.
common='''S12 drawn animation. Generate ONE native transparent1024x1536 RGBA grandmother on the SAME canvas and registration. This request is one stage of the approved contact segment022->026->030; never generate a collage or another stage.
Image1 is the UNIQUE LOCKED F018 continuity mother, SHA256 c63f57f53bc2f4bbca59dba4310ea55c0629b354520f8d0becbe88f932ff40be (approved commit2c265ea885f956e15915cede73288c5c4d0f33f6). Preserve its identity, full head/hair/glasses/gaze, neck/chest/pelvis, near RIGHT arm and empty hand, kneeling legs and two complete shoes. Preserve its repaired placket-tip fold and grey-blue shaded petals. Image2 is lockedF000 MATERIAL-ONLY local RGB board, not a full old pose; keep skin/hair/blue/trousers same-material means within+/-4 channels, preserving dark hair, ink, highlights and form shading. Never whiten the shaded tip or progressively brighten hair. Image3 is CONSTRUCTION ONLY: left panel is native-aligned whole-arm volume over a faded locked018 ghost; right is magnified contact and layer guidance. Ignore diagram colors, text, axes, rods and ghost suppression as painted art.
Draw the entire FAR LEFT shoulder-under-blouse, sleeve, upper arm, elbow, forearm, wrist, palm and all fingers as a connected anatomical chain. Only ONE jade bangle, proximal to far LEFT wrist; it is not the wrist joint. No isolated wrist translation, stretched forearm or shrinking palm. Keep actual018 palm scale; the rod point G is not a palm-bone endpoint. Upper.86H/forearm.64H are construction depth proxies, not proof about a generated body; hidden shoulder has10-20native px uncertainty. Fingers have thenar base and coherent knuckles/phalanges; five anatomical digits may occlude one another naturally, no starfish hand.
Frozen registration .70+(275,112), scene1920x1080. Upper neck3 shaft remains from scene(934.312497676,785.129739577) to(1497.531490504,714.664205296), outer width7scene px; grasp cross-section G=(958,782.166145436) for ALL three stages. Lower/body shaft remains from(951.261694392,798.906335746) to(1282.198690556,773.946794448), also width7. Lower shaft must remain untouched, with >=3scene px real air to ALL outer ink/AA/fingers. Near RIGHT hand stays EMPTY and well clear of BOTH shafts. Rods/crane/cloth/box/55degree puppet plane stay physically fixed; crane stays cloth-supported, no lift/body rise before034. Do NOT paint any rod, puppet, cloth, box, scenery, cast shadow or diagram into the native character. Draw a plausible native grasp around the guide; future original-pixel finger layers must pass in front of the code upper shaft while rear palm stays behind, without double fingers. Keep every contour and complete shoes/fingers inside canvas with breathing room.
'''
unique={22:'F022 held022-025 (4f): ONLY FAR LEFT THUMB PAD FIRST CONTACT at fixed upper cross-section G. Keep every other digit and palm visibly above the upper shaft with >=3scene px air including outer ink/AA. No index wrap, no closed grasp. The thumb is continuous from thenar base through joints; touch gently, not pull the rod.',26:'F026 held026-029 (4f): THUMB REMAINS AT THE SAME G. Index bends around lower/front of the UPPER shaft opposing that thumb; index curl is now a real contact. Middle/ring/little remain relaxed above the upper shaft, not closed into a fist. Wrist joins complete forearm; no contact with the lower/body shaft.',30:'F030 held030-033 (4f): COMPLETE FAR LEFT GRASP around the SAME upper shaft. Thumb opposes index; remaining digits curl naturally beside it, with rear palm mass mostly above the rod and visible front finger occlusion. Upper rod enters/exits on its existing straight axis; no sliding, grabbing the lower shaft or lifting. Near RIGHT hand remains empty.'}
for st in stages:
 f=st['frame'];prompt=common+'\n'+unique[f]+'\nNative reference estimates only: '+json.dumps({k:st[k] for k in ['S','E','W','B']},separators=(',',':'))+'. Native G='+json.dumps(G.tolist())+'. Actual images, outer ink/AA contact and complete arm continuity decide acceptance. Deliver ONLY F%03d.\n'%f
 pp=O/f'prompts/F{f:03d}.txt';pp.write_text(prompt);inputs=[O/'inputs/01_locked_F018.png',O/'inputs/02_locked_F000_materials_ONLY.png',O/f'inputs/03_F{f:03d}_VOLUME_CONTACT_CONSTRUCTION.png']
 req={'status':'BATCH_INPUT_GATE_NOT_EXECUTED','execution_enabled':False,'frame':f,'hold':4,'end_inclusive':f+3,'tool':'image_gen.imagegen','tool_arguments':{'prompt':prompt,'referenced_image_paths':[str(p.resolve()) for p in inputs],'transparent_background':True},'prompt_SHA256':sha(pp),'input_SHA256':[{'order':i+1,'path':str(p.relative_to(R)),'sha256':sha(p)} for i,p in enumerate(inputs)],'batch_policy':'After one batch reference approval: generate022 then026 then030, self-review each actual result before next; no per-frame primary approval wait for passed items. Stop/report real structural errors. All use the same locked018 identity mother and fixed000 material authority; compare continuity against preceding actual result.'}
 (O/f'requests/F{f:03d}_NOT_EXECUTED.json').write_text(json.dumps(req,indent=2)+'\n')
# Concise geometry: source, actual018 observed estimates, frozen axes, three full volume/contact definitions.
data={'source_locked018_commit':'2c265ea885f956e15915cede73288c5c4d0f33f6','locked018_SHA256':sha(source),'palette_board_SHA256':sha(palette),'H_native':H,'registration':{'scale':.7,'x':275,'y':112},'upper_rod_native':{'start':upper_start.tolist(),'end':upper_end.tolist(),'radius':rodR,'G_axis':G.tolist()},'lower_rod_native':{'start':lower_start.tolist(),'end':lower_end.tolist(),'radius':rodR},'actual018_landmark_estimates_native':{'hiddenS':[644,684],'visibleE':[770,836],'W':[875,885],'indexMCP':[954,886],'indexPIP':[981,890],'indexDIP':[998,899],'indexTip':[1006,907],'thumbPad':[956,932],'uncertainty_visible_hand_px':[5,8],'uncertainty_hiddenS_px':[10,20]},'hand_scale_note':'Palm W->indexMCP about80native px from actual018. Old .23H wrist-G is not anatomical palm length and is NOT carried as a hand-size constraint. Finger3D lengths are conservative depth proxies; actual art still decides.','fixed_digit_phalange_depth_proxy_lengths_native':digit_L,'thumb_pad_center_native_ALL3':thumb_pad.tolist(),'thumb_pad_radius_native':thumb_radius,'index_front_pad_center_native_026_030':index_pad.tolist(),'front_contact_note':'Thumb top pad tangent; front index/other pad silhouettes may overlap the shaft projection because they pass in front. They do not mean a moved shaft or a painted rod in native art.','bone_proxy_lengths_native':{'upper':L1,'forearm':L2},'cloth_support_through033':True,'F034_not_opened':True,'stages':stages}
(O/'geometry/contact_segment.json').write_text(json.dumps(data,indent=2)+'\n')
with (O/'exposure.csv').open('w') as file:
 wr=csv.writer(file,lineterminator=chr(10));wr.writerow(['frame','hold','last_frame','beat']);[wr.writerow([s['frame'],4,s['frame']+3,s['label']]) for s in stages]
print(json.dumps({'prepared_frames':[22,26,30],'imagegen_calls':0,'scene_renders':0,'mother_SHA256':sha(source),'three_actual_request_input_counts':[len(json.loads((O/f'requests/F{s["frame"]:03d}_NOT_EXECUTED.json').read_text())['input_SHA256']) for s in stages],'bone_proxy_max_length_error_native':max(abs(s['bone_lengths_native_depth_proxy']['upper']-L1)+abs(s['bone_lengths_native_depth_proxy']['forearm']-L2) for s in stages)},indent=2))
