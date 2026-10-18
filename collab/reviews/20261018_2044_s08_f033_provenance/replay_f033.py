#!/usr/bin/env python3
"""Portable F033 postprocessing from six declared original PNGs only.
Reconstructs original030 body partition, AA54 input masks/preplacement, uniform raw
registration, adopted same-raw semantic v5 and material correction. No network,
model call, subprocess, final-image input, or precomputed intermediate-image input.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_fill_holes,binary_dilation,label,gaussian_filter
import PIL,numpy as np,scipy
import argparse,hashlib,io,json,math,os,platform,sys,zlib,shutil
ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--probe-read',type=Path);args=ap.parse_args()
ROOT=args.package_root.resolve();OUTPUT=args.out.resolve()
if OUTPUT.exists():raise SystemExit('Refusing to overwrite existing output directory')
manifest_path=ROOT/'REPLAY_DEPENDENCIES.json';manifest=json.loads(manifest_path.read_text())
OUTPUT.mkdir(parents=True);Image.init()
allowed_reads={manifest_path.resolve(),Path(__file__).resolve()}|{(ROOT/e['path']).resolve() for e in manifest['inputs']}
opened=set();denied=[];runtime_root=Path(sys.base_prefix).resolve()
def audit(event,arguments):
 if event.startswith('socket.') or event in ('subprocess.Popen','os.system'):
  denied.append(event);raise PermissionError('Network/process actions are outside replay scope')
 if event!='open':return
 path,mode,flags=arguments
 if not isinstance(path,(str,bytes,os.PathLike)):return
 p=Path(os.fsdecode(path)).resolve();writing=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
 if writing:
  if not p.is_relative_to(OUTPUT):denied.append(str(p));raise PermissionError('Write outside fresh output directory: '+str(p))
 elif p in allowed_reads:opened.add(str(p.relative_to(ROOT)))
 elif not (p.is_relative_to(runtime_root) or p.is_relative_to(OUTPUT)):
  denied.append(str(p));raise PermissionError('Undeclared read: '+str(p))
sys.addaudithook(audit)
if args.probe_read:args.probe_read.read_bytes();raise AssertionError('Undeclared read was not blocked')
inputs={};verified=[];checks=[]
for e in manifest['inputs']:
 p=ROOT/e['path'];payload=p.read_bytes();sha=hashlib.sha256(payload).hexdigest();assert sha==e['sha256'],e['id'];assert len(payload)==e['bytes'];inputs[e['id']]=Image.open(io.BytesIO(payload));verified.append({'id':e['id'],'path':e['path'],'sha256':sha,'bytes':len(payload)})
def check(p,expected,label):
 actual=hashlib.sha256(p.read_bytes()).hexdigest();checks.append({'stage':label,'sha256':actual,'matches':actual==expected});assert actual==expected,(label,actual,expected)
def init_stage(name):
 p=OUTPUT/name
 for q in ('masks','inputs','candidates','registered'): (p/q).mkdir(parents=True,exist_ok=True)
 return p
# Reconstruct original030 body partition from true locked030 pixels and source hand masks.
a=np.array(inputs['source030'].convert('RGBA'));alpha=a[:,:,3]>0
# Fresh030 true visible arm envelope, not previous027 trace. Both actual elbows now above981.
near=[(680,770),(770,750),(895,800),(1010,730),(1170,695),(1170,840),(1070,860),(950,920),(880,955),(810,940),(730,875)]
far=[(1017,797),(1044,782),(1077,778),(1116,789),(1154,790),(1189,736),(1263,724),(1267,780),(1228,820),(1178,858),(1112,899),(1080,922),(1046,915),(1012,887),(988,852)]
def pm(p):
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
env=pm(near)|pm(far);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue
for p in ['F030_true_near_hand_match_footprint.png','F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png']:arm|=(np.array(inputs[{'F030_true_near_hand_match_footprint.png':'near030','F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png':'far030'}[p]])>0)&alpha
box=(np.array(inputs['box030'])>0)&alpha;arm&=~box
body=a.copy();body[arm|box,3]=0
body_path=OUTPUT/'F030_body_behind_original_pixels.png';Image.fromarray(body).save(body_path);check(body_path,manifest['expected']['original030_body_partition_png_sha256'],'original030 body partition')
# Rebuild actual AA54 preplacement and all explicit edit/hand guards.
O=init_stage('input_stage');H,W=a.shape[:2]
head=(1230,707);oldhead=(1148,717);angle=7;th=math.radians(angle);c,s=math.cos(th),math.sin(th);aff=(c,s,oldhead[0]-c*head[0]-s*head[1],-s,c,oldhead[1]+s*head[0]-c*head[1])
def load(name):return np.array(inputs[{'F030_true_near_hand_match_footprint.png':'near030','F030_near_distal_hard_guard_footprint.png':'distal030','F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png':'far030','F030_fixed_table_box_footprint.png':'box030'}[name]].convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{n}.png')
near0=load('F030_true_near_hand_match_footprint.png');distal0=load('F030_near_distal_hard_guard_footprint.png');far0=load('F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png');box=load('F030_fixed_table_box_footprint.png');ni=np.zeros_like(a);ni[near0]=a[near0];n=np.array(Image.fromarray(ni).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC));nearall=n[:,:,3]>0
near=np.array(Image.fromarray(distal0.astype('uint8')*255).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.NEAREST))>0;near&=nearall;collar=nearall&~near
# Far intrinsic true hand remains archived beneath the moving foreground hand.
# Release only its occluded outer footprint in the visible composite, never the actual lever-seat core.
far_occlusion=far0&nearall;far=far0&~nearall
assert not (poly([(1227,760),(1241,760),(1241,774),(1227,774)])&nearall).any()
body=body.copy();body[body[:,:,3]==0]=0
pre=np.zeros_like(a);pre[3:,44:]=body[:-3,:-44];pre[far0]=a[far0];pre[box]=a[box]
pre=np.array(Image.alpha_composite(Image.fromarray(pre),Image.fromarray(n)))
bodyenv=poly([(665,290),(1010,290),(1074,355),(1090,586),(1105,684),(1135,788),(1166,863),(1119,934),(1035,1079),(570,1079),(597,958),(620,810),(622,657),(650,578),(643,467)])
oldalpha=binary_dilation((a[:,:,3]>0)&~(far0|box),iterations=5);newalpha=binary_dilation(pre[:,:,3]>0,iterations=7)
armenv=poly([(706,653),(806,687),(908,777),(947,821),(1084,721),(1154,748),(1144,812),(1014,894),(934,946),(865,909),(762,825),(693,753)])
fararm=poly([(973,646),(1052,659),(1117,794),(1131,797),(1171,843),(1129,902),(1063,929),(1010,873),(985,780)])
w=(bodyenv|oldalpha|newalpha|armenv|fararm|collar)&~(near|far|box)
labels,num=label(w);main=labels[800,940];islands=w&(labels!=main);w&=labels==main
# Explicitly restore true foreground hand AA backed by original opaque far hand.
# These54 pixels are source-over original hand layers, never model-painted anatomy.
lost_AA=nearall&far0&(a[:,:,3]>128)&~(near|far|box|w)
assert int(lost_AA.sum())==54
near|=lost_AA;collar&=~lost_AA
save('F033_RESTORE_true_foreground_AA_backed_by_far_hand',lost_AA)
pre[~w&~(near|far|box)]=0
for name,m in [('F033_WHITE_body_neck_head_arms_wrist_allowed',w),('F033_near_distal_palm_fingers_entire_match_guard',near),('F033_near_whole_transformed_hand_footprint',nearall),('F033_near_proximal_palmroot_release',collar),('F033_far_visible_hand_jade_TRUE_SEAT_guard',far),('F033_far_original_underlying_full_hand_SEAT_footprint',far0),('F033_far_guard_occluded_by_foreground_near_hand',far_occlusion),('F033_fixed_table_box_guard',box),('F033_removed_permission_islands',islands)]:save(name,m)
Image.fromarray(pre).save(O/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png');Image.fromarray(n).save(O/'inputs/F033_preplaced_true_near_hand_match_RGBA.png')
# Underlying complete far grip remains independently preserved, not reconstructed from an occluded final.
fa=np.zeros_like(a);fa[far0]=a[far0];Image.fromarray(fa).save(O/'inputs/F033_original_underlying_far_hand_SEAT_RGBA.png')
rod=Image.new('RGBA',(W,H));d=ImageDraw.Draw(rod);knob=(1233.9532049682696,766.8943738423919);pivot=(1301.4864864864865,791.545945945946);d.line((knob,pivot),fill=(58,42,34,255),width=5);d.ellipse((knob[0]-6.81,knob[1]-6.81,knob[0]+6.81,knob[1]+6.81),fill=(58,42,34,255));target=Image.alpha_composite(rod,Image.fromarray(pre));target.save(O/'inputs/F033_preplaced_WITH_REAL_LOW_ROD_RGBA.png')
bb=(580,280,1360,1080);size=(1170,1200)
target.crop(bb).resize(size,Image.Resampling.LANCZOS).save(O/'inputs/F033_actual_edit_target_1p5x_RGBA.png');Image.fromarray(w.astype('uint8')*255).crop(bb).resize(size,Image.Resampling.NEAREST).save(O/'inputs/F033_actual_edit_WHITE_MASK_1p5x.png')
check(O/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png',manifest['expected']['preplaced_png_sha256'],'AA54 frozen original-pixel preplacement')
check(O/'inputs/F033_actual_edit_target_1p5x_RGBA.png',manifest['expected']['actual_AA54_target_png_sha256'],'actual submitted AA54 first target image')
for name,expected in manifest['expected']['input_masks'].items():check(O/'masks'/name,expected,'input mask '+name)
G=O
# Exact executed uniform whole-raw registration and white-mask composite.
O=init_stage('registered_nominal')
raw=inputs['raw'].convert('RGBA');assert raw.size==(1239,1270);s=manifest['registration_used']['scale'];tx=manifest['registration_used']['tx'];ty=manifest['registration_used']['ty']
reg=raw.transform((1170,1200),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC);reg.save(O/'registered/F033_registered_crop_1p5x_RGBA.png')
small=reg.resize((780,800),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080));scene.paste(small,(580,280));scene.save(O/'registered/F033_registered_scene_patch_RGBA.png')
base=Image.open(G/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png').convert('RGBA');m=Image.open(G/'masks/F033_WHITE_body_neck_head_arms_wrist_allowed.png').convert('L');binary=np.array(m)>0;f=np.array(m.filter(ImageFilter.GaussianBlur(.6)),float)/255;f[~binary]=0
b=np.array(base);q=np.array(scene);ba=b[:,:,3].astype(float)/255;qa=q[:,:,3].astype(float)/255;alpha=qa*f+ba*(1-f);premul=q[:,:,:3].astype(float)*qa[:,:,None]*f[:,:,None]+b[:,:,:3].astype(float)*ba[:,:,None]*(1-f[:,:,None]);rgb=np.divide(premul,np.maximum(alpha[:,:,None],1e-10));out=np.dstack((np.rint(rgb).clip(0,255).astype('uint8'),np.rint(alpha*255).clip(0,255).astype('uint8')));out[~binary]=b[~binary]
res=Image.fromarray(out);dest=O/'candidates/S08_F033_whole_turn_arms_candidate_RGBA.png';res.save(dest)
check(O/'registered/F033_registered_scene_patch_RGBA.png',manifest['expected']['registered_scene_png_sha256'],'raw registered scene')
check(dest,manifest['expected']['registered_composite_png_sha256'],'nominal white-mask composite')
# Exact adopted semantic v5. Earlier v1-v4 are diagnostic history, not extra calls.
P=O;O=init_stage('semantic_v5');src=P/'candidates/S08_F033_whole_turn_arms_candidate_RGBA.png';a=np.array(Image.open(src).convert('RGBA'));q=np.array(Image.open(P/'registered/F033_registered_scene_patch_RGBA.png').convert('RGBA'));base=np.array(Image.open(G/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png'));W,H=1920,1080
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([(1134,836),(1141,838),(1155,836),(1158,844),(1156,858),(1148,869),(1140,863),(1137,852)],fill=255);roi=np.array(m)>0
far=np.array(Image.open(G/'masks/F033_far_visible_hand_jade_TRUE_SEAT_guard.png'))>0;near=np.array(Image.open(G/'masks/F033_near_distal_palm_fingers_entire_match_guard.png'))>0;box=np.array(Image.open(G/'masks/F033_fixed_table_box_guard.png'))>0
# The released portion is exclusively old alpha0 outside true bracelet/hand. White-domain
# continuation below it takes the same raw actual contour; no generated jade replaces original jade.
truefar=far&(base[:,:,3]>0)
lm=Image.new('L',(W,H));ImageDraw.Draw(lm).polygon([(1157,841),(1158,843),(1156,845),(1153,846),(1147,846),(1147,845),(1152,844),(1155,843)],fill=255)
old_wrist_ink=(np.array(lm)>0)&truefar&(base[:,:,:3].max(2)<145)
truefar&=~old_wrist_ink;protected=truefar|near|box
Image.fromarray(old_wrist_ink.astype('uint8')*255).save(O/'masks/RELEASE_detached_old_wrist_ink_NOT_true_jade.png')
release=roi&far&(base[:,:,3]==0)
allowed=roi&~protected
# Keep the actual native forearm skin and ink contour. Raw green-bracelet overhang outside original
# true jade is not adopted: it remains old true alpha0, separately recorded.
r,g,b=[q[:,:,k].astype(int)for k in range(3)];new_green=(g-r>12)&(g-b>7)&(q[:,:,3]>0)
allowed&=~new_green
out=a.copy();out[allowed]=q[allowed]
# Retain the original jade edge as a foreground RGBA layer. Only its partial-alpha
# lower exterior edge needs real new wrist skin beneath it, rather than empty air.
am=Image.new('L',(W,H));ImageDraw.Draw(am).polygon([(1135,838),(1148,838),(1157,839),(1157,844),(1142,845)],fill=255)
edge_AA=(np.array(am)>0)&truefar&(base[:,:,3]>0)&(base[:,:,3]<250)
yy,xx=np.where(edge_AA);skin_donor=q[yy+4,xx-4].copy();over=base[yy,xx].copy();fa=over[:,3:4].astype(float)/255;ba=skin_donor[:,3:4].astype(float)/255;oa=fa+ba*(1-fa);rgb=(over[:,:3]*fa+skin_donor[:,:3]*ba*(1-fa))/np.maximum(oa,1e-10);out[yy,xx,:3]=np.rint(rgb).clip(0,255).astype('uint8');out[yy,xx,3]=np.rint(oa[:,0]*255).clip(0,255).astype('uint8');allowed|=edge_AA
Image.fromarray(edge_AA.astype('uint8')*255).save(O/'masks/ORIGINAL_jade_outer_AA_SOURCE_OVER_same_raw_wrist_underlay.png')
Image.fromarray(release.astype('uint8')*255).save(O/'masks/RELEASE_old_far_alpha0_guard_outside_true_jade.png');Image.fromarray(allowed.astype('uint8')*255).save(O/'masks/ADOPT_same_raw_continuous_far_forearm_outer_edge.png');Image.fromarray((roi&new_green).astype('uint8')*255).save(O/'masks/EXCLUDE_native_jade_overhang_keep_original_jade.png')
dest=O/'candidates/S08_F033_same_raw_far_wrist_semantic_RGBA.png';Image.fromarray(out).save(dest)
check(dest,manifest['expected']['semantic_v5_png_sha256'],'accepted semantic v5')
for name,expected in manifest['expected']['semantic_masks'].items():check(O/'masks'/name,expected,'semantic mask '+name)
# Exact final material correction, preserving true hands and the entire alpha channel.
P=O;O=init_stage('color_final');src=dest
a=np.array(Image.open(src).convert('RGBA'));v=a.astype(float);H,W=a.shape[:2];Y,X=np.mgrid[:H,:W]
def load(p):return np.array(Image.open(p).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def ramp(x,l,h):return np.clip((x-l)/(h-l),0,1)
near=load(G/'masks/F033_near_whole_transformed_hand_footprint.png');far=load(G/'masks/F033_far_visible_hand_jade_TRUE_SEAT_guard.png');box=load(G/'masks/F033_fixed_table_box_guard.png');neararm=poly([(680,760),(786,748),(892,803),(1096,735),(1189,760),(1148,810),(1010,879),(930,933),(879,943),(818,917),(736,849)]);guards=near|far|box
r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];opaque=ramp(v[:,:,3],220,252)
skin=ramp(r,165,215)*ramp(r-g,16,30)*ramp(g-b,8,20)*ramp(100-(r-g),0,18)*opaque
head=skin*((X>=780)&(X<=1050)&(Y>=400)&(Y<=740));head[guards]=0
farregion=poly([(1010,836),(1049,806),(1092,793),(1153,810),(1171,843),(1147,880),(1100,917),(1060,926),(1016,902),(991,862)])
fararm=skin*farregion;fararm[guards|neararm]=0
blue=ramp(b-r,25,55)*ramp(b-g,16,34)*ramp(g,58,95)*ramp(205-r,0,30)*opaque*(Y>600);blue[guards]=0
hairregion=poly([(726,306),(951,290),(1058,351),(1050,487),(1007,518),(943,515),(903,514),(852,537),(794,532),(739,518)])
gray=ramp(27-(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])),0,10)*ramp(np.minimum.reduce([r,g,b]),85,130)*ramp(245-np.maximum.reduce([r,g,b]),0,25)*opaque
face_gray_protection=poly([(857,520),(880,496),(902,469),(925,445),(948,430),(972,424),(992,425),(1004,439),(1014,469),(1018,503),(1054,522),(1054,710),(798,710),(798,565)]);hair=gray*hairregion*np.clip((535-Y)/40,0,1);hair[guards|face_gray_protection]=0
mat=[('head_ear_neck_skin',head,(0,6,7)),('far_arm_skin',fararm,(0,3,6)),('blue_blouse',blue,(7,3,4)),('crown_gray_hair',hair,(3,4,2))]
out=v.copy();material_manifest=[];ov=np.zeros_like(a)
cols=[(250,80,80),(230,150,20),(30,220,100),(200,50,230)]
for (name,m,d),color in zip(mat,cols):
 # Smooth only inward; genuine ink, flowers, eye whites, alpha and protected hands do not enter.
 soft=gaussian_filter(m,.65);soft=np.minimum(soft,m);soft[guards]=0
 if name!='blue_blouse':soft[neararm]=0
 q=np.rint(soft*255).astype('uint8');Image.fromarray(q).save(O/'masks'/f'{name}_SOFT.png');out[:,:,:3]+=soft[:,:,None]*np.array(d)
 ov[q>0,:3]=color;ov[q>0,3]=np.maximum(ov[q>0,3],(q[q>0]*.45).astype('uint8'));material_manifest.append({'name':name,'max_add_RGB':d,'affected_soft_domain_pixels':int((q>0).sum()),'mask':str(O/'masks'/f'{name}_SOFT.png')})
out=np.rint(out).clip(0,255).astype('uint8');out[:,:,3]=a[:,:,3];out[guards]=a[guards];dest=O/'candidates/S08_F033_whole_turn_same_raw_final_color_RGBA.png';Image.fromarray(out).save(dest)
check(dest,manifest['expected']['final_png_sha256'],'locked final color image')
for name,expected in manifest['expected']['color_masks'].items():check(O/'masks'/name,expected,'color mask '+name)
changed=np.any(out!=a,axis=2);assert not np.any(out[:,:,3]!=a[:,:,3]);assert not (changed&guards).any();assert not (changed&neararm&(skin>0)).any()
final_dest=dest;color_changed=changed.copy();color_source=a.copy();color_out=out.copy();color_guards=guards.copy();color_neararm=neararm.copy();color_skin=skin.copy()
# Export independent foreground near hand and complete underlying far hand from originals.
# Never extract source-over near/far overlap from the final visible composite.
O=OUTPUT/'sealed';O.mkdir();C=OUTPUT/'color_final';S=OUTPUT/'semantic_v5'
src=C/'candidates/S08_F033_whole_turn_same_raw_final_color_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47'
dst=O/'S08_F033_grandma_match_box_RGBA.png';shutil.copy2(src,dst);a=np.array(Image.open(src).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def save_group(n,ar,mask):
 z=ar.copy();z[~mask]=0;Image.fromarray(z).save(O/f'{n}_RGBA.png');Image.fromarray(mask.astype('uint8')*255).save(O/f'{n}_footprint.png');return {'name':n,'footprint_pixels':int(mask.sum()),'visible_pixels':int((mask&(z[:,:,3]>0)).sum()),'alpha0_inside':int((mask&(z[:,:,3]==0)).sum()),'rgba':str(O/f'{n}_RGBA.png'),'footprint':str(O/f'{n}_footprint.png')}
near=m(G/'masks/F033_near_whole_transformed_hand_footprint.png');root=m(G/'masks/F033_near_proximal_palmroot_release.png');distal=m(G/'masks/F033_near_distal_palm_fingers_entire_match_guard.png')
# Independent foreground pixels, not final source-over pixels containing the occluded far hand.
n=np.array(Image.open(G/'inputs/F033_preplaced_true_near_hand_match_RGBA.png').convert('RGBA'));n[root]=a[root]
farfull=m(G/'masks/F033_far_original_underlying_full_hand_SEAT_footprint.png');released=m(S/'masks/RELEASE_old_far_alpha0_guard_outside_true_jade.png')|m(S/'masks/RELEASE_detached_old_wrist_ink_NOT_true_jade.png');aa=m(S/'masks/ORIGINAL_jade_outer_AA_SOURCE_OVER_same_raw_wrist_underlay.png')
f=np.array(Image.open(G/'inputs/F033_original_underlying_far_hand_SEAT_RGBA.png').convert('RGBA'));f[released]=0;farfull&=~released;farhard=farfull&~aa
box=m(G/'masks/F033_fixed_table_box_guard.png')
groups=[save_group('F033_true_near_hand_match_INDEPENDENT_FOREGROUND',n,near),save_group('F033_near_distal_hard_guard',n,distal),save_group('F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT',f,farfull),save_group('F033_fixed_table_box',a,box)]
Image.fromarray(farhard.astype('uint8')*255).save(O/'F033_far_hand_jade_SEAT_hard_guard.png');Image.fromarray(aa.astype('uint8')*255).save(O/'F033_far_original_jade_AA_requires_same_raw_skin_underlay.png')
for name,expected in manifest['expected']['sealed_pngs'].items():check(O/name,expected,'sealed independent source '+name)
F=O;O=OUTPUT/'partition';O.mkdir();(O/'frames').mkdir();(O/'masks').mkdir()
src=F/'S08_F033_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47';a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
# Fresh030 true visible arm envelope, not previous027 trace. Both actual elbows now above981.
near=[(726,774),(803,764),(913,813),(1067,744),(1256,685),(1269,781),(1202,819),(1082,850),(987,915),(922,948),(858,940),(784,879)]
far=[(1030,812),(1087,796),(1134,791),(1163,773),(1206,733),(1268,726),(1271,782),(1234,822),(1177,863),(1121,918),(1080,931),(1040,914),(1006,871)]
def pm(p):
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
env=pm(near)|pm(far);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue
for p in ['F033_true_near_hand_match_INDEPENDENT_FOREGROUND_footprint.png','F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png']:arm|=(np.array(Image.open(F/p))>0)&alpha
box=(np.array(Image.open(F/'F033_fixed_table_box_footprint.png'))>0)&alpha;arm&=~box
parts={'body':~(arm|box),'arms':arm,'table_box':box};layers={};names={'body':'F033_body_behind_original_pixels.png','arms':'F033_forearms_elbows_original_pixels.png','table_box':'F033_table_box_original_pixels.png'}
for k,m in parts.items():
 v=a.copy();v[~m,3]=0;layers[k]=v;Image.fromarray(v).save(O/'frames'/names[k]);Image.fromarray((m&alpha).astype('uint8')*255).save(O/'masks'/f'F033_{k}_binary.png');assert np.array_equal(v[:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(int) for v in layers.values()),a[:,:,3]);assert (sum(v[:,:,3]>0 for v in layers.values())).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
for name,expected in manifest['expected']['partition_pngs'].items():check(O/name,expected,'exclusive layer '+name)
dest=final_dest;changed=color_changed;a=color_source;out=color_out;guards=color_guards;neararm=color_neararm;skin=color_skin
report={'status':'PASS_EXACT_F033_REPLAY','expected_final_sha256':manifest['expected']['final_png_sha256'],'actual_final_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'output':str(dest.relative_to(OUTPUT)),'inputs':verified,'all_inputs_declared':True,'opened_input_paths':sorted(opened),'denied_attempts':denied,'stages_verified':checks,'input_count':len(inputs),'new_image_generation_calls':0,'network_calls':0,'alpha_changed_pixels':int((out[:,:,3]!=a[:,:,3]).sum()),'protected_hand_match_jade_seat_box_changed_pixels':int((changed&guards).sum()),'actual_near_arm_skin_changed_pixels':int((changed&neararm&(skin>0)).sum()),'restored_original_AA_input_pixels':int(lost_AA.sum()),'semantic_original_outer_jade_AA_source_over_pixels':int(edge_AA.sum()),'environment':{'python':sys.version,'platform':platform.platform(),'Pillow':PIL.__version__,'NumPy':np.__version__,'SciPy':scipy.__version__,'zlib':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION},'scope':'Pixel reconstruction only; no new visual approval, actual Canvas integration or AI-service regeneration claimed.'}
(OUTPUT/'REPLAY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
