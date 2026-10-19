from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib,shutil,math
R=Path(__file__).resolve().parent;B=R.parent;N=B/'F060_F062_NATIVE_from_APPROVED6940a80f_20261019';G=B/'F060_F062_SHORT_PUFF_LOCKED069_INPUT_GATE_20261019';P=B/'F069_FINAL_reference_GATE_0abc3fd9_20261019/sources'
for d in ['sources','layers','masks','candidate','qa','geometry']:(R/d).mkdir(parents=True,exist_ok=True)
files={'REAL_PROP_original_NO_HUMAN.png':P/'PROP_original.png','F063_LOCKED0abc.png':B/'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png','F058_LOCKED044.png':B/'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png','HEAD_actual_source.png':G/'sources/head_guard.png','SKIRT_actual_source.png':G/'sources/skirt_guard.png','F060_RAW14e9.png':N/'F060/originals/F060_call01_RAW.png','F062_RAW714b.png':N/'F062/originals/F062_call01_RAW.png','original_bridge_geometry.json':G/'geometry/source_geometry_and_checks.json'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,p in files.items():shutil.copyfile(p,R/'sources'/name)
load=lambda n:Image.open(R/'sources'/n).convert('RGBA');src=load('F063_LOCKED0abc.png');s=np.array(src);sz=src.size;yy,xx=np.indices(s.shape[:2]);head=np.array(Image.open(R/'sources/HEAD_actual_source.png').convert('L'))>0;skirt=np.array(Image.open(R/'sources/SKIRT_actual_source.png').convert('L'))>0
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15)
def poly(pts):
 z=Image.new('L',sz);ImageDraw.Draw(z).polygon(pts,fill=255);return np.array(z)>0
def warm(a):
 v=a.astype(int);return (v[:,:,0]>145)&(v[:,:,0]>v[:,:,1]+15)&(v[:,:,1]>v[:,:,2]+9)&(v[:,:,2]>65)&(v[:,:,3]>=16)
def clean_head_skirt(raw):
 z=raw.resize((770,924),Image.Resampling.LANCZOS);w=Image.new('RGBA',sz);w.alpha_composite(z,(550,0));a=np.array(w);v=a.astype(int);vis=v[:,:,3]>0;skin=warm(a)
 gold=(v[:,:,0]>70)&(v[:,:,0]>v[:,:,2]+50)&(v[:,:,1]>v[:,:,2]+30)&(v[:,:,2]<120)
 # Clear entire returned head/hair material, including outside the old source mask, then place the real source head.
 headEnvelope=poly([(530,0),(1050,0),(1050,495),(920,495),(890,477),(830,480),(747,472),(677,473),(668,495),(605,496),(530,480)])
 rawhead=headEnvelope&vis&~gold
 white=(v[:,:,:3].min(2)>195)&((v[:,:,:3].max(2)-v[:,:,:3].min(2))<45)&vis&(yy>=440)&(yy<585)&(xx>=650)&(xx<950);la,num=label(white);counts=np.bincount(la.ravel());ids=(np.argsort(counts[1:])[-2:]+1).tolist()if num else[];collar=binary_dilation(np.isin(la,ids),iterations=3)&vis
 # Returned yellow skirt/material is wholly replaced as a semantic layer, while the actual bare arm below the belt stays.
 skinlabels,skinN=label(skin);sizes=np.bincount(skinlabels.ravel());armids=[]
 for ki in range(1,skinN+1):
  if sizes[ki]<800:continue
  ys,xs=np.where(skinlabels==ki)
  if ys.mean()>580 and ys.max()>700:armids.append(ki)
 actual_arm=binary_dilation(np.isin(skinlabels,armids),iterations=3)&vis;skirtzone=(yy>=777)&(xx>=530)&(xx<1120)&~actual_arm
 skirtlabels,skirtN=label((s[:,:,3]>0)&(yy>=777));skirtid=np.argmax(np.bincount(skirtlabels.ravel())[1:])+1;complete_skirt=skirtlabels==skirtid
 c=a.copy();c[rawhead|collar|skirtzone]=0;c[head|complete_skirt]=s[head|complete_skirt]
 return w,Image.fromarray(c),{'raw_head_hair_and_collar_cleared_pixels':int((rawhead|collar).sum()),'raw_skirt_semantic_cleared_pixels':int(skirtzone.sum()),'source_head_skirt_RGBA_changes':int(np.any(c!=s,axis=2)[head|complete_skirt].sum()),'complete_skirt_white_flower_and_AA_source_pixels_retained':int(complete_skirt.sum())}
whole60,clean60,cleanchecks60=clean_head_skirt(load('F060_RAW14e9.png'));whole62,clean62,cleanchecks62=clean_head_skirt(load('F062_RAW714b.png'));a=np.array(whole62)
# Actual dark front lens component (white reflections filled). It fixes one translation, not a part fit.
raw=np.array(load('F062_RAW714b.png'));v=raw.astype(int);ry,rx=np.indices(raw.shape[:2]);lens=(rx>=880)&(rx<1060)&(ry>=620)&(ry<840)&(v[:,:,3]>=128)&(v[:,:,:3].max(2)<145)&((v[:,:,:3].max(2)-v[:,:,:3].min(2))<35);la,num=label(lens);seed=la[722,973];assert seed>0;actual_lens=binary_fill_holes(la==seed);ly,lx=np.where(actual_lens);rawmouth=np.array([lx.mean(),ly.mean()]);mouth=rawmouth*(770/1145)+[550,0]
# Keep the approved52deg rotation and original scale1, align the actual visible mouth center once.
th=math.radians(52);M=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]);source_mouth=np.array([1133.03882756,285.65702322]);t=mouth-M@source_mouth;iv=M.T;it=-iv@t
prop=load('REAL_PROP_original_NO_HUMAN.png');newprop=prop.transform(sz,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0);newprop.save(R/'layers/ONE_REAL_PROP_R52_SCALE1_actual_mouth_registration.png')
sourceG=np.array([1134.519,470.]);Ts=np.array([1134.,665.]);Ls=np.array([1135.,289.]);targetG=M@sourceG+t;T=M@Ts+t;L=M@Ls+t
# All current gripping-hand skin/ink/AA is kept, including fingers and the actual proximal wrist; not the full forearm.
skin=warm(a);la,num=label(skin);k=la[620,1050];assert k>0;near=binary_dilation(binary_fill_holes(la==k),iterations=3)&(a[:,:,3]>0);hand=near&(((xx-985)*.9-(yy-675)*.4)>=0)
# Clear only the current generated visible lamp (not human skin), to avoid a second competing lamp outline.
v=a.astype(int);gold=(v[:,:,0]>70)&(v[:,:,0]>v[:,:,2]+50)&(v[:,:,1]>v[:,:,2]+30)&(v[:,:,2]<120)
oldlampROI=poly([(975,570),(1030,540),(1130,490),(1170,425),(1200,422),(1255,505),(1222,560),(1134,617),(1080,658),(1000,685),(978,646)])
oldlamp=oldlampROI&(a[:,:,3]>0)&~binary_dilation(skin,iterations=3)&~gold
c=np.array(clean62);c[oldlamp]=0;base=Image.fromarray(c);base.alpha_composite(newprop);c=np.array(base);c[hand]=a[hand];diag=Image.fromarray(c)
# Unknown true pipe surface behind the historical excluded hand: mark only, never create RGB.
pa=np.array(prop);unknownsrc=(xx>=1095)&(xx<=1175)&(yy>=370)&(yy<=552)&(pa[:,:,3]==0);ui=Image.fromarray(unknownsrc.astype('uint8')*255).transform(sz,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.NEAREST,fillcolor=0);unknown=np.array(ui)>0;visible_unknown=unknown&~hand
for name,z in [('F060_complete_head_skirt_source_REVIEW.png',clean60),('F062_complete_head_skirt_source_BEFORE_layer_change.png',clean62),('F062_REAL_WHOLE_PROP_front_of_forearm_behind_actual_fingers_DIAGNOSTIC.png',diag)]:z.save(R/'candidate'/name)
for name,z in [('KEEP_F062_actual_complete_near_hand_fingers.png',hand),('REMOVE_F062_generated_visible_lamp_NO_skin.png',oldlamp),('UNKNOWN_historical_hand_hidden_prop_no_RGB_fill.png',unknown),('UNKNOWN_not_covered_by_actual_current_hand.png',visible_unknown)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/name)
for tone,col in [('gray',(215,224,231,255)),('dark',(35,43,52,255))]:
 def bg(z):
  w=Image.new('RGBA',z.size,col);w.alpha_composite(z);return w.convert('RGB')
 bg(diag).save(R/f'qa/F062_full_actual_layer_diagnostic_{tone}.png');bg(clean60).save(R/f'qa/F060_full_clean_head_skirt_{tone}.png');board=Image.new('RGB',(1440,600),(229,237,243));d=ImageDraw.Draw(board)
 for j,(title,z)in enumerate([('062 native whole / no restored tail',whole62),('ONE real prop in front of forearm',diag),('same body, unchanged actual hand',clean62)]):
  board.paste(bg(z.crop((850,440,1295,810))).resize((480,400)),(j*480,35));d.text((j*480+5,7),title,font=font,fill='#35495d')
 board.save(R/f'qa/F062_before_after_layer_ownership_{tone}.png')
 states=[('058 LOCKED',load('F058_LOCKED044.png')),('060 raw projection overlap / not proven contact',clean60),('062 ONE rigid real prop diagnostic',diag),('063 LOCKED',src)];sheet=Image.new('RGB',(1600,700),(229,237,243));d=ImageDraw.Draw(sheet)
 for j,(name,z)in enumerate(states):
  pane=bg(z.crop((550,0,1320,924))).resize((400,480));sheet.paste(pane,(j*400,30));d.text((j*400+5,6),name,font=font,fill='#35495d');sheet.paste(bg(z.crop((700,350,1300,820))).resize((400,313)),(j*400,385))
 sheet.save(R/f'qa/F058_F060_F062_F063_SAME_SCALE_{tone}.png')
checks={'status':'ZERO_CALL_SINGLE_RIGID_PROP_LAYER_DIAGNOSTIC_PENDING_ROOT','source_SHA256':{n:sha(R/'sources'/n)for n in files},'physical_prop_source':'PROP_original, historical hand removed; visible source only, not complete hidden RGB','one_prop_transform':{'scale':1,'rotation_deg':52,'M':M.tolist(),'t':t.tolist(),'actual_raw_lens_filled_centroid':rawmouth.tolist(),'actual_native_mouth_centroid':mouth.tolist(),'source_real_mouth_centroid':source_mouth.tolist(),'source_mouth_index_authority':'parent earlier actualFE70 dark lens area center; actual ellipse read is a proxy, not physical3D measurement','target_G_source_station_projection':targetG.tolist(),'target_T_source_endface_center':T.tolist(),'target_L_source_endface_center':L.tolist(),'source_axis_length':376.00132978488244,'source_hand_pixel_adopted':0},'complete_current_near_hand_RGBA_changes':int(np.any(c!=a,axis=2)[hand].sum()),'known_prop_layer_order':'current far arm -> current near forearm -> one rigid real physical lamp -> complete current hand/fingers','historical_hand_hidden_possible_tube_unknown_pixels_after_transform':int(unknown.sum()),'unknown_not_covered_by_current_hand_pixels':int(visible_unknown.sum()),'no_unknown_RGB_created':True,'F060_head_skirt_cleanup':cleanchecks60,'F062_head_skirt_cleanup':cleanchecks62,'F060_actual_correction':'Projection overlap alone does not prove physical collision. Prior contact/HOLD interpretation withdrawn under Astra actual review; raw unmodified, no new request.','calls':0,'git':0,'candidate_SHA256':sha(R/'candidate/F062_REAL_WHOLE_PROP_front_of_forearm_behind_actual_fingers_DIAGNOSTIC.png')}
(R/'geometry/one_rigid_source_transform_and_limits.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
