from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter
import json
R=Path('astra_s07_xiaoman_release_20261018_1110');im=Image.open(R/'originals/F039_call_009.png').convert('RGBA')
def poly(name,pts):
 m=Image.new('L',im.size,0);ImageDraw.Draw(m).polygon(pts,fill=255);m.save(R/('masks/'+name+'.png'));return m
leg=poly('F039_call009_near_leg_source',[(502,556),(528,559),(543,620),(521,645),(469,662),(370,708),(268,745),(246,765),(233,794),(221,806),(187,807),(135,788),(96,765),(64,737),(48,713),(48,689),(62,671),(81,668),(108,675),(152,692),(186,707),(215,714),(254,706),(365,656),(457,596)])
leglayer=im.copy();leglayer.putalpha(ImageChops.multiply(im.getchannel('A'),leg));shift=Image.new('RGBA',im.size);shift.alpha_composite(leglayer,(32,-42))
legshift=Image.new('L',im.size,0);legshift.paste(leg,(32,-42));legallowed=ImageChops.lighter(leg,legshift).filter(ImageFilter.MaxFilter(25));legallowed.save(R/'masks/F039_call010_near_leg_allowed.png')
arm=poly('F039_call010_near_arm_allowed_raw',[(1054,535),(1126,533),(1200,565),(1200,628),(1246,649),(1318,623),(1342,575),(1339,526),(1366,496),(1498,475),(1505,601),(1400,689),(1307,752),(1223,745),(1114,693),(1060,649),(1039,586)])
hair=poly('F039_call010_protected_near_hair',[(1191,503),(1249,505),(1288,533),(1310,564),(1320,596),(1316,620),(1286,638),(1244,639),(1210,613),(1192,570)])
arm=ImageChops.subtract(arm,hair);arm.save(R/'masks/F039_call010_near_arm_allowed.png')
hand=poly('F039_call009_near_hand_source',[(1363,549),(1380,526),(1419,495),(1434,494),(1450,483),(1476,483),(1496,509),(1494,541),(1476,558),(1433,574),(1406,579)])
h=im.copy();h.putalpha(ImageChops.multiply(im.getchannel('A'),hand));hs=Image.new('RGBA',im.size);hs.alpha_composite(h,(-43,40))
base=im.copy();clear=ImageChops.lighter(leg,arm);base.putalpha(ImageChops.multiply(im.getchannel('A'),ImageChops.invert(clear)));base.alpha_composite(shift);base.alpha_composite(hs)
base.save(R/'reference/F039_call010_prepose_rgba.png');gray=Image.new('RGBA',im.size,(240,240,240,255));gray.alpha_composite(base);d=ImageDraw.Draw(gray);d.line([(1088,565),(1241,661),(1357,594),(1395,572)],fill=(10,135,185),width=4);d.ellipse((1236,656,1246,666),fill=(10,135,185));gray.convert('RGB').save(R/'reference/F039_call010_prepose_guide.png')
allowed=ImageChops.lighter(legallowed,arm);allowed.save(R/'masks/F039_call010_effective_allowed.png')
meta={'status':'diagnostic pixel preposition only; builtin must repair anatomy and joins','source':'originals/F039_call_009.png','registration':{'s':.2475,'t':[339.7325,512.485]},'near_leg_and_shoe_native_translation':[32,-42],'near_hand_native_translation':[-43,40],'new_near_arm_target_source':{'shoulder':[1088,565],'elbow':[1241,661],'wrist':[1357,594],'palm':[1395,572]},'invariants':['head face far arm torso skirt and far leg outside effective mask locked','native source pixels and original alpha preserved outside effective mask','no head proportional scaling','phone remains separate stationary under hair'],'required_builtin_repairs':['Reconnect near knee to skirt opening after whole near lower-leg/shoe move.','Redraw near sleeve opening, upper arm, elbow and forearm along guide into preposed hand.','Five-digit hand anatomy, continuous wrist, no guide lines.'],'allowed_mask':'masks/F039_call010_effective_allowed.png','source_masks':['masks/F039_call009_near_leg_source.png','masks/F039_call009_near_hand_source.png']};(R/'geometry/F039_call010_prepose.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
