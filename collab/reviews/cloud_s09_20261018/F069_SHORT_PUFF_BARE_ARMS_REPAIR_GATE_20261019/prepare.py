from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_dilation,binary_fill_holes
import numpy as np,json,hashlib,shutil,argparse
R=Path(__file__).resolve().parent;BASE=R.parent
ap=argparse.ArgumentParser();ap.add_argument('--out');arg=ap.parse_args();O=Path(arg.out) if arg.out else R
for d in ['sources','reference_native','inputs_1280x1536','masks','qa','requests','geometry']:(O/d).mkdir(parents=True,exist_ok=True)
files={'F069_ACTION_ACCEPTED_COSTUME_REVOKED.png':BASE/'F069_F073_NATIVE_batch_13e696e9_20261019/candidate/F069_ACTUAL_scene_TRANSIT_DARK.png','F073_ACTION_LIGHT_ACCEPTED_COSTUME_REVOKED.png':BASE/'F069_F073_NATIVE_batch_13e696e9_20261019/candidate/F073_ACTUAL_scene_FIRST_ON.png','F063_SHORT_PUFF_IDENTITY_ONLY.png':BASE/'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png','head_guard_seed.png':BASE/'F063_zero_call_semantic_reintegration_20261019/masks/KEEP_actual044_head_neck_complete_collar.png','skirt_guard_seed.png':BASE/'F063_zero_call_semantic_reintegration_20261019/masks/KEEP_actual044_skirt_material.png','source063_near_skin.png':BASE/'F063_zero_call_semantic_reintegration_20261019/masks/NEW_complete_near_skin_chain_FRONT_of_prop.png'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,p in files.items():
 q=R/'sources'/n
 if not q.exists():shutil.copyfile(p,q)
 if O!=R:shutil.copyfile(q,O/'sources'/n)
load=lambda n:Image.open(R/'sources'/n).convert('RGBA'); a=np.array(load('F069_ACTION_ACCEPTED_COSTUME_REVOKED.png'));s=np.array(load('F063_SHORT_PUFF_IDENTITY_ONLY.png'));sz=(a.shape[1],a.shape[0]);yy,xx=np.indices(a.shape[:2]);vis=a[:,:,3]>0
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14);big=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
def poly(p):
 z=Image.new('L',sz);ImageDraw.Draw(z).polygon(p,fill=255);return np.array(z)>0
def mask(n):return np.array(Image.open(R/'sources'/n).convert('L'))>0
def layer(z,m):return Image.fromarray(np.where(m[:,:,None],z,0).astype('uint8'))
def warm(z):
 v=z.astype(int);return (v[:,:,0]>145)&(v[:,:,0]>v[:,:,1]+15)&(v[:,:,1]>v[:,:,2]+9)&(v[:,:,2]>65)&(v[:,:,3]>=16)
w=warm(a);lab,_=label(w); near=binary_fill_holes(lab==lab[585,1040]);far=binary_fill_holes(lab==lab[650,1210]);near=binary_dilation(near,iterations=2)&vis;far=binary_dilation(far,iterations=2)&vis
# Preserve complete action palms/digits and genuine AA; artificial proximal extraction edges remain editable.
nearhand=near&(((xx-982)*.84-(yy-638)*.54)>=0);farhand=far.copy();hands=nearhand|farhand
prop=poly([(849,596),(899,583),(1000,570),(1090,543),(1156,534),(1182,510),(1224,496),(1248,498),(1265,528),(1270,573),(1267,611),(1254,630),(1207,643),(1160,634),(1135,624),(1060,642),(982,650),(897,650),(847,636)])&vis&~w
# Material classification only removes yellow cloth accidentally falling inside the prop outline.
av=a.astype(int);gold=(av[:,:,0]>60)&(av[:,:,0]>av[:,:,2]+48)&(av[:,:,1]>av[:,:,2]+29)&(av[:,:,1]>av[:,:,0]*.50)&(av[:,:,2]<120);prop &=~gold
fixed=hands|prop
chest=poly([(700,554),(917,554),(949,579),(938,598),(901,603),(859,595),(797,591),(744,579)])&vis&~fixed
fixed |= chest
head=mask('head_guard_seed.png')&vis;skirt=mask('skirt_guard_seed.png')&vis
waist=(yy>=774)&(yy<=792)&(xx>=675)&(xx<=930)&vis;skirt |= waist
old=poly([(580,485),(694,478),(765,541),(820,587),(914,617),(939,664),(934,753),(864,784),(770,785),(678,751),(621,705),(578,655)])|poly([(922,620),(1042,616),(1132,641),(1162,686),(1150,755),(1059,801),(991,809),(943,767),(910,699)])
old &=~(head|skirt|fixed)
# Actual short-puff material, never source063 skin or hand. Far occluded material is UNKNOWN.
sw=warm(s);sl,_=label(sw);sf=binary_dilation(binary_fill_holes(sl==sl[765,1000]),iterations=2)&(s[:,:,3]>0);ns=mask('source063_near_skin.png')
pn=poly([(619,487),(681,485),(717,531),(752,579),(777,633),(779,665),(751,705),(709,718),(663,701),(623,685),(597,660),(585,605),(582,548)])
pf=poly([(929,674),(971,669),(1008,690),(1032,714),(1011,744),(972,774),(937,761),(918,733)])
puffs=(pn|pf)&(s[:,:,3]>0)&~(ns|sf|sw)
pufflayer=layer(s,puffs)
# Fresh smooth tapered outlines; no old long-sleeve contour, cloth folds, wrist cuff or round joint disk.
def bezier_outline(start,segments):
 pts=[start];p=np.array(start,dtype=float)
 for c1,c2,q in segments:
  c1=np.array(c1);c2=np.array(c2);q=np.array(q)
  for t in np.linspace(0,1,24)[1:]:pts.append(tuple((1-t)**3*p+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*q))
  p=q
 return pts
nearpts=bezier_outline((684,654),[((714,656),(748,683),(788,701)),((847,681),(926,638),(977,613)),((986,623),(995,642),(1000,656)),((940,686),(868,735),(815,760)),((772,765),(711,722),(675,688)),((673,677),(677,664),(684,654))])
farpts=bezier_outline((952,740),[((959,760),(986,793),(1015,805)),((1054,790),(1100,736),(1128,696)),((1125,682),(1119,668),(1113,658)),((1075,689),(1040,744),(1015,767)),((999,770),(985,749),(977,721)),((965,725),(956,733),(952,740))])
farvol=Image.new('RGBA',sz);d=ImageDraw.Draw(farvol);d.polygon(farpts,fill=(130,188,216,255),outline='#315c74',width=2)
nearvol=Image.new('RGBA',sz);d=ImageDraw.Draw(nearvol);d.polygon(nearpts,fill=(151,203,226,255),outline='#315c74',width=2)
base=a.copy();base[old]=0;A=Image.fromarray(base);A.alpha_composite(farvol);A.alpha_composite(pufflayer);A.alpha_composite(nearvol);A.alpha_composite(pufflayer);az=np.array(A);az[fixed|head|skirt]=a[fixed|head|skirt];A=Image.fromarray(az)
new=(np.array(farvol)[:,:,3]>0)|(np.array(nearvol)[:,:,3]>0)|puffs
roots=poly([(581,482),(727,482),(791,623),(780,715),(650,721),(580,665)])|poly([(909,638),(1028,641),(1058,733),(1008,795),(932,775),(905,704)])
white=binary_dilation(old|new|roots,iterations=8)&~(fixed|head|skirt)
# Keep the new wrist entrance fully redrawable right up to actual preserved palms.
B=Image.fromarray(white.astype('uint8')*255).convert('RGBA');C=A.copy();dc=ImageDraw.Draw(C)
for chain,col in [([(705,666),(800,730),(982,638)],'#925ab3'), ([(970,742),(1015,780),(1105,680)],'#d24e94')]:
 dc.line(chain,fill=col,width=3)
 for x,y in chain:dc.rectangle((x-3,y-3,x+3,y+3),fill=col)
for im in [A,C]:
 dr=ImageDraw.Draw(im);dr.text((565,15),'F069 SHORT PUFF + BARE ARMS / SOFT NOT_ART / DARK',font=font,fill='#397694')
 dr.text((595,800),'Fresh tapered bare arms: NO cloth folds, NO wrist cuffs.',font=font,fill='#397694')
D=Image.new('RGBA',(1280,1536));dd=ImageDraw.Draw(D);dd.text((35,25),'IDENTITY / SHORT PUFF EDGES / REAL SKIN & CLOTH ONLY',font=big,fill='#315c74')
# Both complete sleeve ends plus a small adjacent bare-skin area, not any full hand gesture.
for box,dest,scale,txt in [((584,480,785,718),(40,85),2.5,'NEAR: short puff ends on upper arm'),((916,670,1033,783),(650,85),3.3,'FAR: short cuff + adjacent bare skin'),((810,705,866,733),(65,880),4,'Bare skin / ink internal sample'),((787,572,834,599),(650,880),4,'Blouse internal cloth sample')]:
 z=load('F063_SHORT_PUFF_IDENTITY_ONLY.png').crop(box);z=z.resize((round(z.width*scale),round(z.height*scale)),Image.Resampling.LANCZOS);D.alpha_composite(z,dest);dd.text((dest[0],dest[1]+z.height+12),txt,font=font,fill='#315c74')
dd.text((40,1390),'No old grip, receiving-hand pose or full mother figure supplied.',font=big,fill='#315c74')
crop=(550,0,1320,924);inputs={}
for letter,im in [('A',A),('B',B),('C',C)]:
 im.crop(crop).save(O/f'reference_native/{letter}_F069_770x924_NOT_ART.png');p=O/f'inputs_1280x1536/{letter}_F069_SHORT_PUFF_BARE_ARMS_PREPARED_NOT_CALLED.png';im.crop(crop).resize((1280,1536),Image.Resampling.NEAREST if letter=='B' else Image.Resampling.LANCZOS).save(p);inputs[letter]=p
p=O/'inputs_1280x1536/D_F069_SHORT_PUFF_IDENTITY_NO_HAND_GESTURE.png';D.save(p);inputs['D']=p
for n,m in [('COMPLETE_old_new_short_sleeve_bare_arm_WHITE',white),('KEEP_actual069_complete_palms_all_digits',hands),('KEEP_actual069_visible_prop_slider',prop),('KEEP_actual069_valid_nonediting_chest',chest),('REMOVE_old_long_sleeve_semantic',old),('SOURCE063_short_puff_cloth_ONLY',puffs),('KEEP_actual069_head_collar',head),('KEEP_actual069_stable_skirt',skirt)]:Image.fromarray(m.astype('uint8')*255).save(O/f'masks/{n}.png')
for tone,col in [('gray',(215,224,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1280,820),(229,236,242))
 for j,l in enumerate('ABCD'):
  z=Image.open(inputs[l]).convert('RGBA');bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);sheet.paste(bg.resize((320,384)).convert('RGB'),(j*320,0))
 z=A.crop((575,480,1285,815));bg=Image.new('RGBA',z.size,col);bg.alpha_composite(z);bg.resize((1280,604)).convert('RGB').save(O/f'qa/F069_both_short_puffs_bare_arms_{tone}_NOT_ART.png');sheet.paste(bg.resize((848,400)).convert('RGB'),(216,406));sheet.save(O/f'qa/F069_four_inputs_{tone}_NOT_ART.png')
prompt='''Repair only the clothing identity and the complete two bare-arm connections in image A. Keep its 1280x1536 transparent canvas, composition, accepted F069 hand placements, true torch size, grip station, black slider and supporting far palm. This is TRANSIT, still completely dark. B is the complete editing-region reference, C repeats the same soft construction, and D contains only correct short-puff identity and internal real materials.

Draw TWO genuinely SHORT puff sleeves. Their concrete gathered lower edges end on the proximal upper arms, well above both elbows, as D shows. From each short cuff draw a complete natural BARE upper arm, elbow, tapered bare forearm and natural wrist into its existing complete palm. Remove the entire old long-sleeve and wrist-cuff silhouettes, all distal yellow cloth, cuff folds and elastic wrist bands. Do not recolor the old long sleeves as skin, trace their bulky envelope, or copy the blue guide as capsules, round joints, armor or fabric. The blue shapes are NOT_ART fresh placement references only: redraw natural skin contours, anatomical taper and source ink. Preserve clear ownership: the far arm emerges from its own far sleeve behind the near arm. Both sleeve roots and chest-side joins must be coherent, without flesh bridges, detached wrists, holes or doubled contours.

Preserve the already accepted near complete palm, all gripping fingers and thumb action at the actual slider; preserve the complete far supporting palm, all fingers and its actual pad support beneath the front torch. Do not move the torch, slider, hands or supporting contact to solve the sleeves. Reconstruct the full wrist entrances continuously, rather than adding isolated wrist patches. Preserve the head, face, neck, collar, nonedited chest and skirt. The editing band includes old and new sleeve/arm silhouettes and the vacated cloth; complete the naturally exposed blouse where needed. No beam or ON light, new costume, extra hand or following state. Return one coherent transparent F069 drawing, without guide colors, text, haze or background. F073 is not requested here.'''
(O/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');args={'prompt':prompt+'\n','referenced_image_paths':[str(R/'inputs_1280x1536'/p.name)for p in inputs.values()],'transparent_background':True,'requested_outputs':1,'status':'INPUT_GATE_ONLY_NOT_CALLED'};(O/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,indent=2)+'\n')
check={'status':'INPUT_GATE_ONLY_NOT_ART_NOT_CALLED','sources':{n:sha(R/'sources'/n)for n in files},'mapping':{'native_crop':crop,'tool':[1280,1536],'uniform':128/77,'inverse':'77/128+[550,0]'},'actual069_palms_all_digits_source_RGBA_changes':int(np.any(np.array(A)!=a,axis=2)[hands].sum()),'actual069_visible_prop_slider_source_RGBA_changes':int(np.any(np.array(A)!=a,axis=2)[prop].sum()),'white_actual_guards_overlap':int((white&(hands|prop|head|skirt)).sum()),'valid_source_chest_guard_pixels':int(chest.sum()),'alpha0_guard_pixels':int(((hands|prop|head|skirt)&~vis).sum()),'new_contours':'Fresh smooth taper; no reused long sleeve contour, no round joint disks, no faux final skin painting. Source063 contributes short-puff cloth only; no source063 hands or full pose.','future073':'Only after actual repaired069 arms accepted: carry its complete short sleeves and bare arms as coherent source layer; preserve accepted073 thumb/slider TRANSIT-to-ON delta and actual lens/beam layers. Do not skin-color original long sleeves. No073 candidate constructed.','calls':0,'soft_chains':{'near':[[705,666],[800,730],[982,638]],'far':[[970,742],[1015,780],[1105,680]]}}
(O/'geometry/short_puff_bare_arm_input_checks.json').write_text(json.dumps(check,indent=2)+'\n');(O/'README.md').write_text('F069 short-puff / two bare-arm input gate only. NO GENERATION. Accepted action source069 is preserved in full palms/all digits, true prop and slider; its costume signature is revoked. A has one new opaque tapered NOT_ART bare-arm target and real correct063 short-puff cloth fragments; no old063 hand gesture is supplied. B covers complete old/new long-to-short sleeve, bare arms, wrist entrances and root/chest-side joins. D shows both correct short sleeve edges and a little adjacent real bare skin, no full hand. Blue contours are soft redraw guides, never finished skin or reusable anatomy. Fresh natural bare upperarms/forearms must replace all long-sleeve/wrist-cuff outlines, rather than dyeing sleeves. Hands/torch remain current069 composed pixels, not old pure-prop overlays.073 depends on accepted repaired069 complete arms while retaining its own thumb/slider and light increments. Actual drawing and natural cuff/wrist continuity remain unverified until a future authorized result.\n')
manifest={str(p.relative_to(O)):sha(p)for p in sorted(O.rglob('*'))if p.is_file()and p.name!='manifest.json'};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(check,indent=2))
