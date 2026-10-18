#!/usr/bin/env python3
"""Portable F030 postprocessing replay. Does not invoke generation or network.
Preserves exact original operations, types, rounding and executed registration values.
Uses six declared PNG inputs, no final/intermediate image reads; choose a new output directory.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import map_coordinates,binary_dilation,binary_erosion,binary_fill_holes,label,gaussian_filter
import PIL,numpy as np,scipy
import argparse,hashlib,io,json,math,os,platform,sys,zlib
ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
ROOT=args.package_root.resolve();OUTPUT=args.out.resolve()
if OUTPUT.exists():raise SystemExit('Refusing to overwrite existing output directory')
manifest_path=ROOT/'REPLAY_DEPENDENCIES.json';manifest=json.loads(manifest_path.read_text())
OUTPUT.mkdir(parents=True);Image.init()
allowed={manifest_path.resolve(),Path(__file__).resolve()}|{(ROOT/e['path']).resolve() for e in manifest['inputs']}
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
 elif p in allowed:opened.add(str(p.relative_to(ROOT)))
 elif not (p.is_relative_to(runtime_root) or p.is_relative_to(OUTPUT)):
  denied.append(str(p));raise PermissionError('Undeclared read: '+str(p))
sys.addaudithook(audit)
inputs={};verified=[];checks=[]
for e in manifest['inputs']:
 p=ROOT/e['path'];payload=p.read_bytes();sha=hashlib.sha256(payload).hexdigest();assert sha==e['sha256'],e['id'];assert len(payload)==e['bytes'];inputs[e['id']]=Image.open(io.BytesIO(payload));verified.append({'id':e['id'],'path':e['path'],'sha256':sha,'bytes':len(payload)})
def check(p,expected,label):
 actual=hashlib.sha256(p.read_bytes()).hexdigest();checks.append({'stage':label,'sha256':actual,'matches':actual==expected});assert actual==expected,(label,actual,expected)
def init_stage(name):
 p=OUTPUT/name
 for q in ('masks','inputs','candidates'): (p/q).mkdir(parents=True,exist_ok=True)
 return p
# Reconstruct original027 body alpha partition, preserving all original RGB.
a=np.array(inputs['source027'].convert('RGBA'));alpha=a[:,:,3]>0
near=[(645,825),(677,805),(706,786),(735,779),(746,809),(764,851),(787,892),(831,884),(883,867),(930,850),(975,825),(1006,806),(1042,799),(1062,810),(1065,836),(1052,868),(1027,890),(994,899),(956,894),(928,912),(885,936),(843,962),(801,986),(774,999),(749,993),(727,973),(706,943),(686,906),(667,865)]
# New020 actual elbow unfolds forward; far forearm lifts to the relaxed empty hand. Not017 arm trace.
far=[(948,830),(974,798),(1025,778),(1056,785),(1085,825),(1118,806),(1182,729),(1265,724),(1282,799),(1200,842),(1162,874),(1090,925),(1010,930),(970,900)]
hand=[(1110,794),(1165,749),(1200,729),(1255,729),(1265,775),(1210,814),(1170,837),(1140,854),(1115,830)]
match=[(1044,845),(1077,788),(1093,787),(1095,808),(1060,851)]
def pm(polys):
 m=Image.new('L',(1920,1080));d=ImageDraw.Draw(m)
 for p in polys:d.polygon(p,fill=255)
 return np.array(m)>0
env=binary_dilation(pm([near,far]),iterations=6);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue;arm|=pm([hand,match])&alpha;arm|=(np.array(inputs['near027'])>0)&alpha;arm|=(np.array(inputs['far027'])>0)&alpha
arm|=(np.array(inputs['collar027'])>0)&alpha&~blue
box=(np.array(inputs['box027'])>0)&alpha;arm&=~box
body=a.copy();body[arm|box,3]=0
body_path=OUTPUT/'F027_body_behind_original_pixels.png';Image.fromarray(body).save(body_path);check(body_path,manifest['expected']['original027_body_partition_png_sha256'],'original027 body partition')
# Reconstruct actual frozen F030 preplacement and all semantic permission/guard masks.
O=init_stage('input_stage');H,W=a.shape[:2]
head=(1148,717);oldhead=(1082,797);angle=5;th=math.radians(angle);c,s=math.cos(th),math.sin(th);aff=(c,s,1082-c*1148-s*717,-s,c,797+s*1148-c*717)
source_masks={'F027_true_near_hand_match_footprint.png':'near027','F027_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png':'far027','F027_fixed_table_box_footprint.png':'box027'}
def load(name):return np.array(inputs[source_masks[name]].convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{n}.png')
near0=load('F027_true_near_hand_match_footprint.png');far0=load('F027_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png');box=load('F027_fixed_table_box_footprint.png');ni=np.zeros_like(a);ni[near0]=a[near0];n=np.array(Image.fromarray(ni).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC));nearall=n[:,:,3]>0
# Free the true proximal wrist/palm-root collar, preserving all distal palm, fingers and entire wooden match.
collar0=poly([(949,853),(972,851),(988,909),(963,918)])&near0
collar=np.array(Image.fromarray(collar0.astype('uint8')*255).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.NEAREST))>0
near=nearall&~collar
false_far_air=far0&nearall&(a[:,:,3]==0);far=far0&~false_far_air
assert not ((far0&nearall)&(a[:,:,3]>0)).any()
# Use only original body pixels as a uniformly translated identity construction anchor. The full body is white/editable.
body[body[:,:,3]==0]=0
pre=np.zeros_like(a);pre[4:,28:]=body[:-4,:-28]
pre[far]=a[far];pre[box]=a[box];pre[nearall]=n[nearall]
# Complete body/head envelope plus both natural arm routes, original-position clearance and collar joins.
bodyenv=poly([(625,295),(945,290),(1030,365),(1055,565),(1062,644),(1090,753),(1118,824),(1165,884),(1116,935),(1000,940),(995,1079),(530,1079),(562,964),(584,841),(585,649),(620,581),(604,474)])
oldalpha=binary_dilation((a[:,:,3]>0)&~(far0|box),iterations=5)
newalpha=binary_dilation(pre[:,:,3]>0,iterations=7)
armenv=poly([(685,655),(767,698),(841,785),(935,876),(1056,734),(1107,781),(1067,846),(925,976),(852,994),(755,881),(670,760)])
fararm=poly([(971,658),(1044,665),(1090,782),(1127,799),(1170,843),(1125,898),(1069,924),(1018,882),(986,786)])
w=(bodyenv|oldalpha|newalpha|armenv|fararm|collar)&~(near|far|box)
# Keep only the contiguous body/arm permission region. Isolated permission islands around
# fixed props and source alpha scraps are not authorized anatomy edits. Source originals untouched.
labels,ncomp=label(w);main_id=labels[800,900];permission_islands=w&(labels!=main_id);w&=labels==main_id
save('F030_REMOVED_isolated_permission_islands',permission_islands)
# Include full old arm/hand vacated area and clean false empty patches. Fixed alpha0 grip seat remains black.
pre[~w&~(near|far|box)]=0
for name,m in [('F030_WHITE_body_neck_head_arms_and_wrist_allowed',w),('F030_near_distal_palm_fingers_entire_match_guard',near),('F030_near_whole_transformed_hand_footprint',nearall),('F030_near_proximal_wrist_palmroot_release',collar),('F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard',far),('F030_RELEASE_original_far_empty_air_occupied_by_new_near_hand',false_far_air),('F030_fixed_table_box_guard',box)]:save(name,m)
Image.fromarray(pre).save(O/'inputs/F030_preplaced_original_body_anchor_and_truehands_NO_ROD_RGBA.png')
check(O/'inputs/F030_preplaced_original_body_anchor_and_truehands_NO_ROD_RGBA.png',manifest['expected']['preplaced_png_sha256'],'frozen original-pixel preplacement')
for name,expected in manifest['expected']['input_masks'].items():check(O/'masks'/name,expected,'input mask '+name)
G=O
# Exact uniform raw registration; no intermediate registration PNG supplied.
raw=inputs['raw'].convert('RGBA');assert raw.size==(1254,1254)
s=manifest['registration_used']['scale'];tx=manifest['registration_used']['tx'];ty=manifest['registration_used']['ty']
reg=raw.transform((1215,1200),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC)
small=reg.resize((810,800),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080));scene.paste(small,(530,280))
registered=OUTPUT/'F030_registered_scene_patch_RGBA.png';scene.save(registered);check(registered,manifest['expected']['registered_scene_png_sha256'],'native raw registration')
# Exact accepted semantic v6 computation, without comparison-preview-only dependencies.
O=init_stage('semantic_v6');raw=np.array(scene);base=pre.copy();H,W=raw.shape[:2];Y,X=np.mgrid[:H,:W];P=np.stack((X,Y),-1).astype(float)
def load(p):return np.array(Image.open(p).convert('L'))>0
def save(n,m):Image.fromarray((m.astype(float)*255).round().clip(0,255).astype('uint8')).save(O/'masks'/f'{n}.png')
E=np.array([858.,886.]);S=np.array([1060.,756.]);T=np.array([1018.14697,789.96020]);u=(S-E)/np.linalg.norm(S-E);v=np.array([-u[1],u[0]]);ut=(T-E)/np.linalg.norm(T-E);vt=np.array([-ut[1],ut[0]]);ratio=np.linalg.norm(T-E)/np.linalg.norm(S-E);A=ratio*np.outer(ut,u)+np.outer(vt,v);t=np.sum((P-E)*u,axis=-1)
# Sole foreground near-arm silhouette and its rejected native distal hand/match. Manual semantic polygon; no far-arm skin selected.
pp=poly([(699,816),(776,769),(852,831),(984,777),(1024,751),(1056,714),(1075,702),(1132,681),(1167,686),(1199,655),(1207,668),(1162,719),(1163,747),(1133,770),(1108,778),(1070,785),(1036,811),(1008,835),(974,862),(939,888),(898,913),(861,927),(847,926),(821,917),(778,893),(742,867),(717,840)])
ri=raw.astype(int);skin=(ri[:,:,0]>ri[:,:,1]+8)&(ri[:,:,1]>ri[:,:,2]+6)&(ri[:,:,3]>2)
old=binary_fill_holes(binary_dilation(skin,iterations=2)&pp)
# Match beyond the native hand is included explicitly; never reused.
old|=poly([(1150,698),(1196,655),(1208,667),(1160,719)])&(raw[:,:,3]>0)
# Whole elbow cap remains exactly original. Only source forearm before the virtual wrist plane can enter new limb.
fore=old&(t<=np.linalg.norm(S-E)+28)
source=raw.copy();source[~fore]=0
# Smoothly introduce axial shortening outside the entire round elbow cap; no whole-body transform.
def displacement(Q):
 tq=np.sum((Q-E)*u,axis=-1);z=np.clip((tq-36)/68,0,1);w=z*z*(3-2*z);aq=(Q-E)@A.T+E;return (aq-Q)*w[:,:,None]
Q=P.copy()
for k in range(20):Q=P-displacement(Q)
co=np.array([Q[:,:,1],Q[:,:,0]])
trans=np.stack([map_coordinates(source[:,:,k].astype(float),co,order=1,mode='constant') for k in range(4)],-1).round().clip(0,255).astype('uint8')
newmask=trans[:,:,3]>0
# Build diagnostic from native full-body drawing. Explicitly remove old hand/forearm only, then insert same-raw projected forearm.
out=raw.copy();out[old]=0
im=Image.fromarray(out);im.alpha_composite(Image.fromarray(trans));out=np.array(im)
nearall=load(G/'masks/F030_near_whole_transformed_hand_footprint.png');nearhard=load(G/'masks/F030_near_distal_palm_fingers_entire_match_guard.png');far=load(G/'masks/F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard.png');box=load(G/'masks/F030_fixed_table_box_guard.png');collar=load(G/'masks/F030_near_proximal_wrist_palmroot_release.png');release_aa=nearhard&binary_dilation(collar,iterations=4);nearhard &= ~release_aa
# Original true palm root is alpha-composited, not hard alpha-replaced at its artificial old crop cut.
npix=np.zeros_like(out);npix[nearall]=base[nearall];im=Image.fromarray(out);im.alpha_composite(Image.fromarray(npix));out=np.array(im);out[nearhard]=base[nearhard];save('RELEASE_false_proximal_cut_AA_guard',release_aa);save('true_distal_palm_fingers_match_guard_after_false_AA_release',nearhard)
out[far]=base[far];out[box]=base[box]
# Remove native lamp rod and preserve only accepted white permission plus original hand guards.
white=load(G/'masks/F030_WHITE_body_neck_head_arms_and_wrist_allowed.png');keep=white|nearall|far|box;out[~keep]=base[~keep]
missing=old&~newmask&~(nearall|far|box)&(base[:,:,3]>100)
# Continuous real fabric donor: one translated crop of this same raw above the near arm.
# Record true lack of donor separately rather than fill it.
cloth_source=np.zeros_like(raw);cloth_source[24:,12:]=raw[:-24,:-12]
ci=cloth_source.astype(int);cloth_valid=(ci[:,:,3]>220)&((ci[:,:,2]>ci[:,:,0]+8)|((ci[:,:,0]>220)&(ci[:,:,1]>220)&(ci[:,:,2]>220)))
chest_zone=poly([(850,825),(1003,750),(1010,784),(890,851),(850,855)])
sleeve_zone=poly([(1003,750),(1055,718),(1059,735),(1062,752),(1065,769),(1067,785),(1034,808),(1010,794)])
cloth_zone=missing & (chest_zone|sleeve_zone) & ~nearall
save('chest_real_cloth_strip_region',chest_zone&missing);save('far_sleeve_inner_continuation_region',sleeve_zone&missing)
cloth_adopt=cloth_zone&cloth_valid
out[cloth_adopt]=cloth_source[cloth_adopt]
# Separate real far-upper-arm donor under the lower wrist interface; retain the new near contour above it.
lowroi=poly([(993,835),(1019,808),(1065,812),(1068,824),(1025,828),(1001,842)])&white&~nearhard&~far
far_skin=np.zeros_like(raw);far_skin[:-6]=raw[6:];fi=far_skin.astype(int);lowroi&=(fi[:,:,0]>fi[:,:,1]+8)&(fi[:,:,1]>fi[:,:,2]+6)&(fi[:,:,3]>220)
sub=Image.fromarray(far_skin);sub.alpha_composite(Image.fromarray(trans));sub.alpha_composite(Image.fromarray(npix));sub=np.array(sub);out[lowroi]=sub[lowroi];save('lower_wrist_background_real_far_upperarm_donor',lowroi)
# Remove only the false old vertical crop-AA strip using native projected skin beneath the true palm root.
cutstrip=poly([(1007,752),(1020,750),(1038,822),(1016,827)])&(collar|release_aa)&(trans[:,:,3]>220)&~nearhard
ff=np.array(Image.fromarray(cutstrip.astype('uint8')*255).filter(ImageFilter.GaussianBlur(.45)),float)/255;ff[~cutstrip]=0
out[:,:,:3]=np.rint(out[:,:,:3]*(1-ff[:,:,None])+trans[:,:,:3]*ff[:,:,None]).astype('uint8');out[:,:,3][cutstrip]=255;save('continuous_old_wrist_cut_strip_same_projected_raw_skin',cutstrip)
# One rigid original true proximal-hand contour slice supplies the natural shallow upper wrist arc.
# It contains only original proximal skin/edge, no fingers, and is shifted(-15,+5) on a copy.
hand_donor=np.zeros_like(base);hand_donor[5:,:-15]=npix[:-5,15:]
arcroi=poly([(1009,758),(1028,748),(1035,756),(1033,767),(1022,775),(1010,777)])&(white|release_aa)&~nearhard
arc_back=np.zeros_like(raw);arc_back[24:,40:]=raw[:-24,:-40];arc=Image.fromarray(arc_back);arc.alpha_composite(Image.fromarray(hand_donor));arc=np.array(arc);out[arcroi]=arc[arcroi];save('upper_wrist_real_proximal_contour_donor_arc',arcroi)
# Remove the false internal duplicate contour above the true lower palm edge using a real adjacent projected-skin donor.
innerlow=poly([(1018,810),(1043,811),(1043,818),(1024,819),(1018,815)])&(collar|release_aa)
skin_donor=np.zeros_like(trans);skin_donor[5:,5:]=trans[:-5,:-5];innerlow &= skin_donor[:,:,3]>220
w=np.array(Image.fromarray(innerlow.astype('uint8')*255).filter(ImageFilter.GaussianBlur(.55)),float)/255;w[~innerlow]=0
out[:,:,:3]=np.rint(out[:,:,:3]*(1-w[:,:,None])+skin_donor[:,:,:3]*w[:,:,None]).astype('uint8');out[:,:,3][innerlow]=255;save('false_internal_lower_wrist_double_line_real_skin_donor',innerlow)
# Two verified interior alpha holes, supplied from adjacent actual native projected skin.
hole=np.zeros((H,W),bool)
for x,y in [(1024,812),(1023,813)]:
 hole[y,x]=True;out[y,x]=trans[y-3,x-3]
save('two_interior_native_alpha_holes_real_skin_donor',hole)
# One old cuff-stroke fragment outside the new wrist contour uses real same-raw blue cloth.
oldcuff=poly([(1006,756),(1013,754),(1013,766),(1008,770)])&~nearall
out[oldcuff]=arc_back[oldcuff];save('old_cuff_fragment_outside_wrist_real_cloth_donor',oldcuff)
# Leave all unsupported regions explicit. Never repaint a hand/finger with sampled flat color.
save('same_raw_cloth_donor_adoption',cloth_adopt)
missing &= ~cloth_adopt
# Record apparent exposed substrate separately. Do not invent skin, fabric or hide alpha gaps.
for n,m in [('native_near_forearm_and_rejected_distal_group',old),('adopted_same_raw_forearm_source',fore),('projected_near_forearm_actual_alpha',newmask),('newly_exposed_original_anchor_substrate_DIAGNOSTIC',missing)]:save(n,m)
dest=O/'candidates/F030_projected_forearm_UNCLEAN_DIAGNOSTIC_RGBA.png';Image.fromarray(out).save(dest)
check(dest,manifest['expected']['semantic_v6_png_sha256'],'accepted semantic v6 image')
for name,expected in manifest['expected']['semantic_masks'].items():check(O/'masks'/name,expected,'semantic mask '+name)
# Exact material correction; original masks regenerated, original hands/alpha preserved.
P=O;src=dest;O=init_stage('color_final')
a=np.array(Image.open(src).convert('RGBA'));v=a.astype(float);H,W=a.shape[:2];Y,X=np.mgrid[:H,:W]
def load(p):return np.array(Image.open(p).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def ramp(x,l,h):return np.clip((x-l)/(h-l),0,1)
near=load(G/'masks/F030_near_whole_transformed_hand_footprint.png');far=load(G/'masks/F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard.png');box=load(G/'masks/F030_fixed_table_box_guard.png');neararm=load(P/'masks/projected_near_forearm_actual_alpha.png');guards=near|far|box
r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];opaque=ramp(v[:,:,3],220,252)
skin=ramp(r,165,215)*ramp(r-g,16,30)*ramp(g-b,8,20)*ramp(100-(r-g),0,18)*opaque
head=skin*((X>=735)&(X<=1015)&(Y>=400)&(Y<=735));head[guards]=0
farregion=poly([(973,834),(1022,803),(1081,789),(1161,798),(1183,845),(1094,899),(1050,910),(1000,881)])
fararm=skin*farregion;fararm[guards|neararm]=0
blue=ramp(b-r,25,55)*ramp(b-g,16,34)*ramp(g,58,95)*ramp(205-r,0,30)*opaque*(Y>600);blue[guards]=0
hairregion=poly([(665,305),(929,285),(1008,356),(1010,477),(967,514),(908,510),(857,510),(795,537),(744,534),(680,519)])
gray=ramp(27-(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])),0,10)*ramp(np.minimum.reduce([r,g,b]),85,130)*ramp(245-np.maximum.reduce([r,g,b]),0,25)*opaque
hair=gray*hairregion*np.clip((535-Y)/40,0,1);hair[guards]=0
mat=[('head_ear_neck_skin',head,(0,6,11)),('far_arm_skin',fararm,(0,5,9)),('blue_blouse',blue,(6,3,4)),('crown_gray_hair',hair,(2,3,3))]
out=v.copy();material_manifest=[];ov=np.zeros_like(a)
cols=[(250,80,80),(230,150,20),(30,220,100),(200,50,230)]
for (name,m,d),color in zip(mat,cols):
 # Smooth only inward; genuine ink, flowers, eye whites, alpha and protected hands do not enter.
 soft=gaussian_filter(m,.65);soft=np.minimum(soft,m);soft[guards]=0
 q=np.rint(soft*255).astype('uint8');Image.fromarray(q).save(O/'masks'/f'{name}_SOFT.png');out[:,:,:3]+=soft[:,:,None]*np.array(d)
 ov[q>0,:3]=color;ov[q>0,3]=np.maximum(ov[q>0,3],(q[q>0]*.45).astype('uint8'));material_manifest.append({'name':name,'max_add_RGB':d,'affected_soft_domain_pixels':int((q>0).sum()),'mask':str(O/'masks'/f'{name}_SOFT.png')})
out=np.rint(out).clip(0,255).astype('uint8');out[:,:,3]=a[:,:,3];out[guards]=a[guards];dest=O/'candidates/S08_F030_whole_turn_same_raw_final_color_RGBA.png';Image.fromarray(out).save(dest)
check(dest,manifest['expected']['final_png_sha256'],'locked final color image')
for name,expected in manifest['expected']['color_masks'].items():check(O/'masks'/name,expected,'color mask '+name)
changed=np.any(out!=a,axis=2);domain=changed&neararm;bluechange=(out[:,:,2]>out[:,:,0])&(out[:,:,2]>out[:,:,1]);assert not (domain&~bluechange).any()
assert not np.any(out[:,:,3]!=a[:,:,3]);assert not (changed&guards).any()
report={'status':'PASS_EXACT_F030_REPLAY','expected_final_sha256':manifest['expected']['final_png_sha256'],'actual_final_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'output':str(dest.relative_to(OUTPUT)),'inputs':verified,'all_inputs_declared':True,'opened_input_paths':sorted(opened),'denied_attempts':denied,'stages_verified':checks,'input_count':len(inputs),'new_image_generation_calls':0,'network_calls':0,'alpha_changed_pixels':int((out[:,:,3]!=a[:,:,3]).sum()),'protected_hand_match_jade_seat_box_changed_pixels':int((changed&guards).sum()),'near_arm_extraction_domain_changed_pixels':int(domain.sum()),'near_arm_extraction_domain_changes_are_all_blue':bool(bluechange[domain].all()),'near_arm_skin_changed_pixels':int((domain&~bluechange).sum()),'environment':{'python':sys.version,'platform':platform.platform(),'Pillow':PIL.__version__,'NumPy':np.__version__,'SciPy':scipy.__version__,'zlib':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION},'scope':'Pixel reconstruction only; no new visual approval, actual Canvas integration or AI service regeneration claimed.'}
(OUTPUT/'REPLAY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
