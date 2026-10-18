from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter
from scipy import ndimage
import numpy as np,math,json,shutil,hashlib
D=Path('astra_s07_f025_prepare_20261018_1420');P=Path('astra_s07_f022_prepare_20261018_1357');W,H=1024,1536;k=.2734375
src=Image.open(P/'candidates/F022_local_v6.png').convert('RGBA');r=np.array(src);yy,xx=np.indices((H,W));shutil.copyfile(P/'candidates/F022_local_v6.png',D/'sources/F022_LOCKED_rgba.png');Image.alpha_composite(Image.new('RGBA',(W,H),'white'),src).convert('RGB').save(D/'sources/F022_LOCKED_white.png')
def poly(p):
 m=Image.new('L',(W*3,H*3));ImageDraw.Draw(m).polygon([(x*3,y*3) for x,y in p],fill=255);return m.resize((W,H),Image.Resampling.LANCZOS)
def R(a):a=math.radians(a);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def move(im,angle,old,new):
 M=R(angle);T=np.array(new)-M@old;iv=np.linalg.inv(M);q=-iv@T;return im.transform((W,H),Image.Transform.AFFINE,(iv[0,0],iv[0,1],q[0],iv[1,0],iv[1,1],q[1]),Image.Resampling.BICUBIC)
def frag(mask):
 a=r.copy();a[:,:,3]=((a[:,:,3].astype('uint16')*np.array(mask).astype('uint16')+127)//255).astype('uint8');return Image.fromarray(a)
def component(seed):
 labs,n=ndimage.label(seed);ct=np.bincount(labs.ravel());ct[0]=0;return labs==ct.argmax()
# Actual cloth/head segmentation, not a hidden skeleton cut. Capture white flowers and dark folds by hole filling, keep pants out of the cloth.
r0,g0,b0=r[:,:,0].astype(float),r[:,:,1].astype(float),r[:,:,2].astype(float)
blue=(b0>r0+12)&(g0>r0+8)&(b0>105)&(g0>72)&(yy>770)&(yy<1190)&(r[:,:,3]>20)
cl=component(ndimage.binary_closing(blue,iterations=3));cl=ndimage.binary_dilation(ndimage.binary_fill_holes(cl),iterations=2)
cloth=Image.fromarray((cl*255).astype('uint8'));head=poly([(0,500),(480,500),(480,790),(405,790),(378,810),(337,846),(324,891),(278,875),(233,906),(0,930)]);head=ImageChops.multiply(head,src.getchannel('A'));garment=ImageChops.lighter(cloth,head)
# Near visible skin plus single jade is one connected piece; far bare hand is separate behind the leg.
skin=(r0>140)&(g0>80)&(r0>g0*1.08)&(b0<r0*.84);jade=(g0>r0*1.1)&(g0>b0*1.05)&(r0<150)
near_seed=(skin|jade)&(xx>270)&(xx<525)&(yy>975)&(yy<1305)&(r[:,:,3]>100);near=component(ndimage.binary_dilation(ndimage.binary_fill_holes(near_seed),iterations=2));near=Image.fromarray((near*255).astype('uint8'))
far_seed=skin&(xx>225)&(xx<333)&(yy>1090)&(yy<1240)&(r[:,:,3]>100);far=Image.fromarray((component(ndimage.binary_dilation(ndimage.binary_fill_holes(far_seed),iterations=2))*255).astype('uint8'))
sleeve=ImageChops.darker(cloth,poly([(300,780),(386,781),(425,806),(449,842),(472,900),(512,983),(509,1000),(477,998),(399,1006),(366,1038),(328,939),(310,892)]));body=ImageChops.subtract(garment,sleeve)
# Overlap six pixels around the elbow cut; the connection mask explicitly repairs the articulation.
up=ImageChops.darker(near,poly([(0,0),(1024,0),(1024,1180),(500,1083),(422,1063),(0,1063)]));fore=ImageChops.darker(near,poly([(0,1056),(424,1056),(504,1076),(1024,1180),(1024,1536),(0,1536)]))
for n,m in [('head_garment',garment),('body_head',body),('near_sleeve',sleeve),('near_upper_skin',up),('near_forearm_hand',fore),('far_wrist_hand',far)]:m.save(D/f'masks/{n}_source.png')
pivot=(np.array([929,670.9])-[730,375])/k;oldE=np.array([475.,1070.]);newE=np.array([571.,1000.]);bd=move(frag(body),10,pivot,pivot);sl=move(frag(sleeve),-12,oldE,newE);upper=move(frag(up),-12,oldE,newE);nf=move(frag(fore),46,oldE,newE)
# Far hand rises behind the near leg. Its visible forearm is only a guide: elbow remains occluded behind the torso/pants.
far_old=np.array([307.,1148.]);far_new=np.array([405.,1062.]);ff=move(frag(far),55,far_old,far_new)
# Fixed lower body and grounded basin, revealed pants supplied from the original seated base where available.
source_union=ImageChops.lighter(garment,ImageChops.lighter(near,far));u=ndimage.binary_dilation(np.array(source_union)>0,iterations=4);under=r.copy();under[u,3]=0;under[(xx<420)&(yy>900)&(yy<1040),3]=0;under[(xx<326)&(yy>1090)&(yy<1340),3]=0
orig=np.array(Image.open('astra_s07_f000_handoff_20261018_1245/production/F000_grandma_rgba.png').convert('RGBA'));restore=ndimage.binary_dilation(np.array(near)>0,iterations=6)&(yy>1080)&(xx>319)&(xx<550);restore=(yy>=1080)&(yy<1340)&(xx>=320)&(xx<550);under[restore]=orig[restore]
# New upper thigh/old elbow disclosure needs local cloth-volume drawing, explicitly flat guide only.
fill=Image.new('RGBA',(W,H));dr=ImageDraw.Draw(fill);dr.polygon([(334,1085),(351,1043),(403,1026),(465,1031),(568,1050),(652,1115),(566,1165),(490,1120),(426,1087)],fill=(48,54,78,255));underim=Image.alpha_composite(fill,Image.fromarray(under));underim.save(D/'preposition/fixed_lowerbody_and_basin.png')
for n,im in [('body_head',bd),('near_sleeve',sl),('near_upper_skin',upper),('near_forearm_hand',nf),('far_wrist_hand',ff)]:im.save(D/f'preposition/{n}.png')
# Keep far hand behind near palm but reveal its upper edge over its own knee, then near forearm/palm in front.
out=Image.new('RGBA',(W,H))
for im in [ff,underim,bd,sl,upper,nf]:out=Image.alpha_composite(out,im)
oa=np.array(out);oa[(xx>382)&(xx<425)&(yy>946)&(yy<980),3]=0;out=Image.fromarray(oa);out.save(D/'preposition/F025_preposition_v4_NOT_FINAL.png');wh=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),out).convert('RGB');wh.save(D/'preposition/F025_edit_target_v4.png');wh.save(D/'review/F025_preposition_v4_white.jpg',quality=98);wh.crop((270,730,920,1240)).resize((1105,867)).save(D/'review/F025_contact_connections_v4.jpg',quality=98)
# Explicit local elbow/shoulder/hand-to-knee repair; head/back interior/seat/feet/basin hard protected.
m=poly([(386,722),(494,739),(583,836),(644,965),(638,1116),(539,1218),(303,1190),(287,1004),(385,954)])
ma=np.array(m);ma[yy<730]=0;ma[(xx>660)&(yy>960)]=0;ma[(yy>1210)]=0;z=Image.new('L',(W,H));ImageDraw.Draw(z).polygon([(548,1021),(640,1081),(760,1162),(780,1206),(671,1200),(565,1152)],fill=255);ma=np.maximum(ma,np.array(z));Image.fromarray(ma).save(D/'masks/F025_connection_mask_v4_PROPOSAL.png');ov=np.array(wh);ov[ma>0]=np.rint(ov[ma>0]*.65+np.array([255,60,170])*.35).astype('uint8');Image.fromarray(ov).save(D/'review/F025_mask_guide_v4.jpg',quality=98)
nearjade=newE+R(46)@(np.array([390.181818,1197.972887])-oldE);meta={'status':'AUTHOR_INPUT_DRAFT','previous_F022_sha256':hashlib.sha256((D/'sources/F022_LOCKED_rgba.png').read_bytes()).hexdigest(),'torso_about_constructed_hip_degrees':10,'near_sleeve_upper_rigid_rotation_deg':-12,'near_forearm_hand_rigid_rotation_deg':46,'old_elbow_visible_landmark_asset':oldE.tolist(),'new_elbow_preposition_asset':newE.tolist(),'near_jade_target_asset':nearjade.tolist(),'near_jade_target_world':([730,375]+k*nearjade).tolist(),'far_wrist_guide_asset':far_new.tolist(),'basin_unchanged_rim':[802.04,752.8],'constructed_bottom':774.5,'calls':0,'warning':'F025 hands must bear with broad lower palm surfaces on the actual visible kneecaps; no gap or floating wrist. This preposition is not production. Bone points are only construction/visible landmarks, not physical measurements.'};(D/'geometry/F025_preposition_v4.json').write_text(json.dumps(meta,indent=2));print(meta)
