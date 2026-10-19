from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019';P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019';W,H=1024,1536;yy,xx=np.indices((H,W))
def load(p):return np.array(Image.open(p).convert('RGBA'))
def poly(points):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def save_mask(name,m):Image.fromarray(m.astype('uint8')*255).save(R/name)
srcp=S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png';src=load(srcp);oldp=B/'F030_REPAIR_NATIVE_call01_20261019/originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png';old=load(oldp)
backp=S/'layers/ONE_M_ACTUAL_COTTON_BACK.png';frontp=S/'layers/ONE_M_ACTUAL_SOFT_LIP_FRONT.png';back,front=load(backp),load(frontp)
props=load(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')[:,:,3]>0
badbase=np.array(Image.open(P/'masks/GENERATED_PROP_CONTEXT_REPLACEMENT_ONLY.png').convert('L'))>0
nearcoarse=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
rgb=src[:,:,:3].astype(float)
skin=(rgb[:,:,0]>190)&(rgb[:,:,1]>105)&(rgb[:,:,2]>95)&(rgb[:,:,0]>rgb[:,:,1]+15)
near_seed=nd.binary_closing(skin&nearcoarse,iterations=2);labs,_=nd.label(near_seed);count=np.bincount(labs.ravel());count[0]=0
near=nd.binary_dilation(nd.binary_fill_holes(labs==count.argmax()),iterations=3)&nearcoarse
jade=(rgb[:,:,1]>rgb[:,:,0]*1.04)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
farroi=(xx>=500)&(xx<=820)&(yy>=480)&(yy<=710)
far_seed=nd.binary_closing((skin|jade)&farroi,iterations=2);labs,_=nd.label(nd.binary_dilation(far_seed,iterations=1));count=np.bincount(labs.ravel());count[0]=0
far=nd.binary_dilation(nd.binary_fill_holes(labs==count.argmax()),iterations=2)&(src[:,:,3]>0)
human=near|far
# Existing source030 full-cloth perimeter plus the actual036 separated surfaces;
# no contour, pose, pinch or M is displaced to make a new state.
outline=[[510,693],[590,718],[642,700],[695,661],[710,649],[734,658],[766,682],[811,711],[900,750],[960,807],[1001,867],[1005,903],[958,1025],[903,1067],[850,1012],[780,1018],[688,999],[623,966],[582,961],[530,990],[451,967],[350,932],[272,900],[257,877],[303,840],[349,806],[403,772],[461,741]]
face=(poly(outline)|(back[:,:,3]>=128)|(front[:,:,3]>=128))&(src[:,:,3]>0)&~human
baseok=poly(outline)&~badbase&~nearcoarse&(old[:,:,3]>=250)
pool=np.zeros_like(src);pool[baseok]=old[baseok]
pool=np.array(Image.alpha_composite(Image.fromarray(pool),Image.fromarray(back)));pool=np.array(Image.alpha_composite(Image.fromarray(pool),Image.fromarray(front)))
native=(back[:,:,3]>=250)|(front[:,:,3]>=250)
underrect=np.zeros((H,W),bool);underrect[792:830,790:875]=True
forbidden=(badbase|underrect)&~native
tail_legacy=poly([[755,738],[807,739],[872,791],[878,830],[788,817],[756,783]])
prop_context=nd.binary_dilation(props,iterations=2)|tail_legacy
# Existing VISIBLE036 fabric is the hard source. Under fixed props, genuine
# separated source pixels may be recovered at their own original coordinates.
visible=face&~prop_context&~human&~forbidden
trusted_under=np.zeros((H,W),bool) # Hidden material is opened, not guessed from contextual prop-bearing layers.
prgb=pool[:,:,:3].astype(float)
noncotton=((prgb[:,:,0]>prgb[:,:,2]*1.25)&(prgb[:,:,1]>prgb[:,:,2]*1.12)&(prgb[:,:,0]>90))|((prgb[:,:,1]>prgb[:,:,0]*1.10)&(prgb[:,:,1]>prgb[:,:,2]*1.10)&(prgb[:,:,1]>45))
trusted_under&=~noncotton
# Any warm/green remnants inside selected raw cloth are unknown material,
# never protected as navy cotton or fed as a competing puppet/hand reference.
src_bad=((rgb[:,:,0]>rgb[:,:,2]+10)&(rgb[:,:,1]>rgb[:,:,2]+3)&(rgb[:,:,0]>55))|((rgb[:,:,1]>rgb[:,:,0]+6)&(rgb[:,:,1]>rgb[:,:,2]+6)&(rgb[:,:,1]>40))
# Three C1 remnants were independently seen and traced byte-for-byte to raw030
# contextual puppet/rod pixels (BACK/FRONT alpha0), not to cotton fold ink.
# Open their actual colored/ink pixels plus one AA pixel, not the whole ROI.
residue_rois=((xx>=465)&(xx<=480)&(yy>=752)&(yy<=765))|((xx>=497)&(xx<=526)&(yy>=731)&(yy<=743))
brown=(rgb[:,:,0]>rgb[:,:,2]+8)&(rgb[:,:,1]>rgb[:,:,2]+2)&(rgb[:,:,0]>12)
hookroi=(xx>=503)&(xx<=518)&(yy>=757)&(yy<=775)
hookink=(rgb[:,:,0]<80)&(rgb[:,:,1]<90)&(rgb[:,:,2]<100)&(rgb[:,:,2]<rgb[:,:,1]*1.35)&(rgb[:,:,2]<rgb[:,:,0]+22)
c1_residue=nd.binary_dilation((residue_rois&brown)|(hookroi&hookink),iterations=1)&face
src_bad|=c1_residue
interior=nd.binary_erosion(face,iterations=3)
visible&=~src_bad&((src[:,:,3]>=250)|~interior)
hard=visible|trusted_under;white=face&~hard
hardrgba=np.zeros_like(src);hardrgba[visible]=src[visible];hardrgba[trusted_under&~visible]=pool[trusted_under&~visible]
# TECHNICAL inpaint volume guide only. Use smooth blue tone from genuine local
# cloth; no source patch/tile, mirrored texture or random flower is synthesized.
hrgb=hardrgba[:,:,:3].astype(float)
navy=hard&(hrgb[:,:,2]>hrgb[:,:,0]+12)&(hrgb[:,:,0]<110)&(hrgb[:,:,1]<140)
assert navy.any()
_,indices=nd.distance_transform_edt(~navy,return_indices=True)
tone=hrgb[indices[0],indices[1]]
tone=np.stack([nd.gaussian_filter(tone[:,:,k],sigma=10) for k in range(3)],2)
guide=np.zeros_like(src);guide[face,:3]=np.clip(tone[face],0,255).round().astype('uint8');guide[face,3]=255
# Bridge only absent portions of the already-locked central ridge and thick lip.
crease_paths=[[(725.7875,663.6614),(741,710),(769,756),(806,795),(842,835),(884,878)],[(792,791),(814,804),(840,819),(865,840),(889,862)]]
fold=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(fold)
for points in crease_paths:
 draw.line(points,fill=(19,32,58,255),width=2,joint='curve')
f=np.array(fold);sel=white&(f[:,:,3]>0);guide[sel]=f[sel]
guide[hard]=hardrgba[hard]
Image.fromarray(guide).save(R/'01_F036_COMPLETE_CLOTH_TARGET_TECHNICAL.png')
Image.fromarray(hardrgba).save(R/'HARD_PROTECTED_ORIGINAL_CLOTH_RGBA.png')
save_mask('02_ONLY_SOURCE_GAPS_WHITE_PROTECTED_BLACK.png',white)
save_mask('HARD_PROTECTED_ORIGINAL_CLOTH_MASK.png',hard)
save_mask('HUMAN_BLACK_PROTECTION_GEOMETRY.png',human)
save_mask('WHOLE_LOCKED036_CLOTH_DOMAIN.png',face)
assert not (white&hard).any() and not (white&human).any()
assert np.array_equal(guide[visible],src[visible])
assert np.array_equal(guide[trusted_under&~visible],pool[trusted_under&~visible])
assert (guide[interior,3]>=250).all() # Original outer-edge AA is retained exactly.
crop=(240,625,1024,1100);panelw,panelh=784,475
g=Image.new('RGBA',(W,H),(236,239,242,255));g.alpha_composite(Image.fromarray(guide))
sheet=Image.new('RGB',(panelw*2,panelh+58),(236,239,242));sheet.paste(g.crop(crop).convert('RGB'),(0,28));sheet.paste(Image.fromarray(white.astype('uint8')*255).convert('RGB').crop(crop),(panelw,28));d=ImageDraw.Draw(sheet)
d.text((8,8),'F036 COMPLETE CLOTH TARGET | 1:1 | TECHNICAL GUIDE ONLY',fill='black');d.text((panelw+8,8),'WHITE: SOURCE GAPS ONLY | BLACK: ORIGINAL PIXELS / HUMANS',fill='black');d.text((8,panelh+35),'C1=(499,747); far pinch=(725.7875,663.6614). Frozen036 contour / ridge / lip. ZERO GENERATION - REVIEW FIRST.',fill='black')
sheet.save(R/'F036_COMPLETE_TARGET_AND_ONLY_GAPS_WHITE_1TO1.png')
meta={'status':'INPUT_GATE_ONLY_PENDING_ASTRA_ONE_CALL_APPROVAL','new_generation_calls':0,'source_locked036_sha256':hashlib.sha256(srcp.read_bytes()).hexdigest(),'source_M_exact':json.loads((S/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json').read_text())['single_similarity'],'C1':[499,747],'far_pinch':[725.78751656,663.66135947],'outer_cloth_domain':'source030 full-cloth perimeter plus actual036 BACK/FRONT extent, clipped to existing source alpha and physical human protection','outline_source030_native':outline,'central_ridge_and_thick_lip_bridges_only_inside_white':crease_paths,'white_pixels':int(white.sum()),'hard_protected_pixels':int(hard.sum()),'visible_locked036_hard_pixels':int(visible.sum()),'recovered_genuine_original_coordinate_cloth_under_props_pixels':0,'visible_locked036_RGBA_changes_on_hard_pixels':int(np.any(guide[visible]!=src[visible],1).sum()),'hard_white_overlap':int((white&hard).sum()),'human_white_overlap':int((white&human).sum()),'holes_inside_complete_visible_cloth_domain':int((guide[interior,3]<250).sum()),'original_edge_AA_below250_retained':int(((guide[:,:,3]<250)&face&~interior).sum()),'no_new_flowers_or_tiled_patch_in_guide':True,'guide_fill_is_native_drawing':False,'guide_fill_method':'smooth local navy volume interpolation and two locked-fold guide paths only in missing source, no texture duplication','generator_input_contains_person_or_prop_RGB':False,'no_generation_request_submitted':True,'future_hard_preservation_rule':'After the one approved cloth generation, use new pixels only inside02 white mask; restore HARD_PROTECTED_ORIGINAL_CLOTH_RGBA exactly. No person/prop RGB is part of the cloth generation target.','SHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.glob('*.png'))}}
(R/'PREPARATION_CHECK.json').write_text(json.dumps(meta,indent=2)+'\n')
meta['C1_non_cotton_residue_source_trace']=[{'xy':[x,y],'locked036_RGBA':src[y,x].tolist(),'raw030_RGBA':old[y,x].tolist(),'BACK_alpha':int(back[y,x,3]),'FRONT_alpha':int(front[y,x,3]),'now_white':bool(white[y,x])} for x,y in [(468,756),(501,737),(509,766)]]
meta['C1_residue_only_pixels_opened_including_one_AA_margin']=int(c1_residue.sum())
(R/'PREPARATION_CHECK.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({k:meta[k] for k in ['status','white_pixels','hard_protected_pixels','visible_locked036_RGBA_changes_on_hard_pixels','hard_white_overlap','human_white_overlap','holes_inside_complete_visible_cloth_domain']},indent=2))
