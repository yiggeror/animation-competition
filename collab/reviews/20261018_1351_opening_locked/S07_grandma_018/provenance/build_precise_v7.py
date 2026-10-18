from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,json,hashlib,shutil,math
D=Path('astra_s07_f018_prepare_20261018_1342');P=Path('astra_s07_f016_prepare_20261018_1319');W,H=1024,1536;k=.2734375
src=Image.open(P/'candidates/F016_local_v6.png').convert('RGBA');r=np.array(src);shutil.copyfile(P/'candidates/F016_local_v6.png',D/'sources/F016_LOCKED_rgba.png')
def poly(p):
 m=Image.new('L',(W*4,H*4));ImageDraw.Draw(m).polygon([(x*4,y*4) for x,y in p],fill=255);return m.resize((W,H),Image.Resampling.LANCZOS)
# Head, neck and exact visible garment envelope. This draft treats the upper body as a rigid final settle, not a new bone measurement.
cloth=poly([(0,0),(1024,0),(1024,1068),(897,1068),(897,1080),(873,1105),(866,1124),(810,1152),(799,1153),(756,1166),(676,1150),(605,1130),(540,1108),(467,1083),(430,1078),(319,1115),(293,1110),(275,1030),(0,1030)])
near=poly([(321,1081),(419,1073),(425,1168),(420,1200),(412,1248),(401,1293),(390,1320),(398,1347),(395,1360),(383,1363),(365,1392),(352,1406),(340,1410),(329,1416),(318,1416),(306,1420),(294,1421),(283,1419),(275,1412),(277,1400),(281,1392),(271,1389),(275,1378),(292,1359),(320,1338),(336,1322),(349,1307),(349,1240),(348,1189),(338,1138)])
far=poly([(329,1190),(332,1242),(320,1265),(300,1279),(283,1291),(264,1302),(248,1311),(246,1326),(242,1339),(231,1343),(229,1333),(234,1311),(240,1302),(270,1286),(292,1263),(309,1230)])
far=poly([(200,1180),(328,1180),(328,1350),(200,1350)])
near=near.filter(ImageFilter.MaxFilter(7))
basin=Image.open(P/'preposition/basin_complete_positioned.png').getchannel('A').point(lambda a:255 if a else 0).filter(ImageFilter.MaxFilter(5))
for n,m in [('head_garment',cloth),('near_arm_hand',near),('far_wrist_hand',far),('basin',basin)]:m.save(D/f'masks/F016_{n}_source.png')
mask=ImageChops.lighter(ImageChops.lighter(cloth,near),ImageChops.lighter(far,basin));mask.save(D/'masks/F016_foreground_union.png');ma=np.array(mask)
# Far arm is retained separately behind the unchanged pants; forehand stays outside their outline.
farraw=r.copy();farraw[:,:,3]=((farraw[:,:,3].astype('uint16')*np.array(far).astype('uint16')+127)//255).astype('uint8')
frontmask=cloth;fm=np.array(frontmask)
rr,gg,bb=r[:,:,0].astype(float),r[:,:,1].astype(float),r[:,:,2].astype(float)
seed=(((rr>150)&(gg>90)&(bb<rr*.82))|((gg>rr*1.15)&(gg>bb*1.05)&(rr<140)))&(np.array(near)>0)
ns=binary_dilation(binary_fill_holes(seed),iterations=2);nearclean=Image.fromarray((ns*255).astype('uint8'));nearclean.save(D/'masks/F016_near_actual_skin_jade_v7.png')
nr=r.copy();nr[:,:,3]=((nr[:,:,3].astype('uint16')*np.array(nearclean).astype('uint16')+127)//255).astype('uint8')
yy,xx=np.indices((H,W));fs=(rr>150)&(gg>90)&(bb<rr*.82)&(np.array(far)>0)&~((yy>=1290)&(xx>300));fs=binary_dilation(binary_fill_holes(fs),iterations=2);farraw[:,:,3]=((r[:,:,3].astype('uint16')*(fs*255).astype('uint16')+127)//255).astype('uint8')
f=r.copy();f[:,:,3]=((f[:,:,3].astype('uint16')*fm.astype('uint16')+127)//255).astype('uint8');foreground=Image.fromarray(f);foreground.save(D/'sources/F016_settle_foreground.png')
b=r.copy();b[:,:,3]=((b[:,:,3].astype('uint16')*(255-ma).astype('uint16')+127)//255).astype('uint8');back=Image.fromarray(b)
# Original locked lower-body layer completes only pixels revealed by the descending foreground.
under=Image.open(P/'preposition/fixed_lower_body_prefill_v2.png').convert('RGBA');back=Image.alpha_composite(under,back);ba=np.array(back);ua=np.array(under);ba[1160:1354,316:337]=ua[1160:1354,316:337];back=Image.fromarray(ba);back.save(D/'sources/F016_fixed_lowerbody_recovered.png')
dx,dy=np.array([-1.398659,4.496158])/k
moved=foreground.transform((W,H),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);moved.save(D/'candidates/F018_settle_foreground_v7.png');farraw[:,:,3]=((farraw[:,:,3].astype('uint16')*(255-np.array(under)[:,:,3]).astype('uint16')+127)//255).astype('uint8');farmoved=Image.fromarray(farraw).transform((W,H),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);pivot=(np.array([793.74,743.8])-[730,375])/k;a=math.radians(3);M=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]);T=pivot-M@pivot;iv=M.T;q=-iv@T;farmoved=farmoved.transform((W,H),Image.Transform.AFFINE,(iv[0,0],iv[0,1],q[0],iv[1,0],iv[1,1],q[1]),Image.Resampling.BICUBIC);out=Image.alpha_composite(Image.alpha_composite(farmoved,back),moved);
master=Image.open('astra_s07_f000_handoff_20261018_1245/production/basin_complete_rgba.png').convert('RGBA');bs=79.1/800/k;bt=(np.array([802.04,752.8])-[730,375])/k-bs*np.array([512,460]);bnew=master.transform((W,H),Image.Transform.AFFINE,(1/bs,0,-bt[0]/bs,0,1/bs,-bt[1]/bs),Image.Resampling.BICUBIC);out=Image.alpha_composite(out,bnew);nmoved=Image.fromarray(nr).transform((W,H),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);out=Image.alpha_composite(out,nmoved);
# Only the visible far fingers lie over the rear lip; torso-side arm remains behind the fixed pants.
ff=np.array(farmoved);ff[:1320,:,3]=0;out=Image.alpha_composite(out,Image.fromarray(ff));# Preserve the already-locked hand/rim contact pixels together, avoiding a new segmentation fringe.
whole=src.transform((W,H),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);hm=poly([(345,1320),(391,1320),(400,1350),(395,1364),(379,1411),(348,1433),(270,1433),(261,1391),(280,1365),(319,1340)]).filter(ImageFilter.GaussianBlur(1.2));ha=np.array(hm);oa=np.array(out);wa=np.array(whole);ww=ha[:,:,None]/255;oa=np.rint(oa*(1-ww)+wa*ww).astype('uint8');out=Image.fromarray(oa);hm.save(D/'masks/F018_near_contact_source_recover_v7.png');out.save(D/'candidates/F018_precise_v7.png')
for nm,col in [('white','white'),('darkgray',(64,68,74,255))]:
 im=Image.alpha_composite(Image.new('RGBA',(W,H),col),out).convert('RGB');im.save(D/f'review/F018_precise_v7_{nm}.jpg',quality=98)
 if nm=='white':im.crop((270,1030,910,1210)).resize((1280,360)).save(D/'review/F018_waist_arm_v7.jpg',quality=98);im.crop((105,1180,585,1490)).resize((960,620)).save(D/'review/F018_grip_floor_v7.jpg',quality=98)
wh=lambda q:Image.alpha_composite(Image.new('RGBA',(W,H),'white'),q).convert('RGB');sheet=Image.new('RGB',(1024,810),'white');sheet.paste(wh(src).resize((512,768)),(0,35));sheet.paste(wh(out).resize((512,768)),(512,35));dr=ImageDraw.Draw(sheet);dr.text((20,10),'F016 LOCKED',(0,0,0));dr.text((530,10),'F018 PRECISE SETTLE DRAFT',(0,0,0));sheet.save(D/'review/F016_F018_same_world_v7.jpg',quality=98);Image.blend(wh(src),wh(out),.5).save(D/'review/F016_F018_onion_v7.jpg',quality=98)
world=out.transform((1672,941),Image.Transform.AFFINE,(1/k,0,-730/k,0,1/k,-375/k),Image.Resampling.BICUBIC);bg=Image.new('RGBA',(1672,941),'white');dr=ImageDraw.Draw(bg);dr.line((720,775,1010,775),fill='#559977',width=2);dr.rectangle((899,691.9,982,699),outline='#559977',width=2);dr.line((905,699,905,775),fill='#a7cbbb',width=2);dr.line((976,699,976,775),fill='#a7cbbb',width=2);world=Image.alpha_composite(bg,world);world.convert('RGB').crop((725,550,1015,790)).resize((1160,960)).save(D/'review/F018_world_support_v7.jpg',quality=98)
diff=np.any(np.array(out)!=r,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F018_actual_diff_v7.png');meta={'status':'AUTHOR_ZERO_CALL_DRAFT_NOT_APPROVED','previous_sha':hashlib.sha256((D/'sources/F016_LOCKED_rgba.png').read_bytes()).hexdigest(),'basin_rim':[802.04,752.8],'basin_bottom_constructed':774.5,'near_contact':[806.24,760.5],'far_contact':[793.74,743.8],'rigid_upperbody_basin_group_translation_scene':[-1.398659,4.496158],'lowerbody':'Fixed. Revealed pixels recovered from original F008 lower body layer; any construction filler exposed must reject.','caveat':'This is a final upper-body settling proposal, not new measured skeleton. Need actual clothing/seat and near/far arm depth review; opaque basin master inherited bottom+0.13scene.','far_wrist_forearm_rotation_deg_about_same_material_contact':3,'new_calls':0};(D/'geometry/F018_precise_v7.json').write_text(json.dumps(meta,indent=2));print(meta)
