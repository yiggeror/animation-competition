"""106 reference only: re-use complete actual102 torso / two own arm chains.
No new drawing, code person, hand/finger deformation, or imagegen.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
from scipy.ndimage import map_coordinates,binary_dilation,binary_erosion,binary_fill_holes,label
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F102_EXACT_NATIVE_ACTIVITY_actual_call01_20261020';P=R/'F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020'
g=json.loads((O/'geometry/F106_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text());src=Image.open(M/'candidate/F102.png').convert('RGBA');B=np.array(src);Y,X=np.mgrid[:1536,:1024]
def poly(points):
 m=Image.new('L',src.size);ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def part(mask):
 q=B.copy();q[~mask]=0;return Image.fromarray(q)
def warp(im,m,res=Image.Resampling.BICUBIC):
 inv=np.linalg.inv(np.vstack([np.array(m),[0,0,1]]))[:2];return im.transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),res)
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def sample_rgba(source,sx,sy):
 q=source.astype(float);aa=q[:,:,3]/255;prem=q[:,:,:3]*aa[:,:,None];a=np.clip(map_coordinates(aa,[sy,sx],order=1,mode='constant'),0,1);rgb=np.stack([map_coordinates(prem[:,:,c],[sy,sx],order=1,mode='constant') for c in range(3)],axis=2);rgb=np.divide(rgb,a[:,:,None],out=np.zeros_like(rgb),where=a[:,:,None]>0);out=np.dstack([np.clip(np.rint(rgb),0,255),np.rint(a*255)]).astype(np.uint8);out[out[:,:,3]==0]=0;return out
def joined_forearm(mask,a):
 # A small distal source-material transition joins wrist tissue to the whole
 # rigid hand. It never moves the hand/bangle or independently moves fingers.
 F=np.array(a['forearm_rigid_matrix']);H=np.array(a['whole_hand_bangle_same_rod_angle_matrix']);e=np.array(a['source_final102']['elbow']);w=np.array(a['source_final102']['wrist']);uv=(w-e)/np.linalg.norm(w-e);length=np.linalg.norm(w-e)
 yy,xx=np.where(mask&(B[:,:,3]>0));corn=np.array([[xx.min(),yy.min(),1],[xx.max(),yy.min(),1],[xx.min(),yy.max(),1],[xx.max(),yy.max(),1]]);dest=np.r_[corn@F.T,corn@H.T];x0=max(0,int(np.floor(dest[:,0].min()))-4);x1=min(1024,int(np.ceil(dest[:,0].max()))+5);y0=max(0,int(np.floor(dest[:,1].min()))-4);y1=min(1536,int(np.ceil(dest[:,1].max()))+5)
 ty,tx=np.mgrid[y0:y1,x0:x1];inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2];sx=inv[0,0]*tx+inv[0,1]*ty+inv[0,2];sy=inv[1,0]*tx+inv[1,1]*ty+inv[1,2]
 for _ in range(12):
  weight=smooth((((sx-e[0])*uv[0]+(sy-e[1])*uv[1])-(length-90))/50)
  aa=F[0,0]+weight*(H[0,0]-F[0,0]);bb=F[0,1]+weight*(H[0,1]-F[0,1]);cc=F[1,0]+weight*(H[1,0]-F[1,0]);dd=F[1,1]+weight*(H[1,1]-F[1,1]);px=tx-(F[0,2]+weight*(H[0,2]-F[0,2]));py=ty-(F[1,2]+weight*(H[1,2]-F[1,2]));det=aa*dd-bb*cc;sx=(dd*px-bb*py)/det;sy=(-cc*px+aa*py)/det
 out=np.zeros_like(B);out[y0:y1,x0:x1]=sample_rgba(np.array(part(mask)),sx,sy);return Image.fromarray(out)
fixed=np.array(Image.open(P/'masks/HARD_QUALIFIED_FINAL098_SHINS_SHOES_AIR.png').convert('L'))>0;fixed|=Y>=1320
shirt=poly([(320,0),(770,0),(770,355),(715,384),(707,419),(722,446),(726,476),(715,501),(698,522),(683,546),(675,573),(669,609),(668,663),(672,710),(699,757),(725,803),(753,852),(762,879),(744,886),(720,863),(666,843),(614,821),(571,802),(543,779),(527,750),(501,795),(469,788),(434,779),(398,761),(423,718),(456,679),(481,641),(494,608),(485,573),(461,554),(444,515),(449,464),(466,416),(482,370),(497,316),(373,348)])
Rmask=poly([(476,391),(531,388),(576,403),(599,435),(605,477),(609,521),(603,552),(609,580),(617,614),(630,646),(654,665),(707,701),(754,729),(792,744),(823,748),(843,742),(851,731),(868,720),(881,721),(894,734),(899,747),(899,768),(888,786),(869,800),(842,809),(810,811),(772,802),(722,781),(678,758),(627,729),(585,703),(560,684),(543,657),(530,624),(514,584),(505,569),(480,574),(461,551),(446,514),(451,464),(462,419)])
Rbare=poly([(508,568),(591,552),(607,591),(617,628),(631,650),(654,667),(707,701),(755,729),(795,744),(823,748),(843,742),(851,731),(868,720),(881,721),(894,734),(899,747),(899,768),(888,786),(869,800),(842,809),(810,811),(772,802),(722,781),(678,758),(627,729),(585,703),(560,684),(543,657),(530,624)])
Lmask=poly([(577,399),(617,398),(646,418),(658,446),(657,474),(653,494),(666,521),(680,549),(694,561),(713,535),(730,511),(709,509),(700,495),(698,476),(704,457),(717,443),(731,438),(745,444),(756,456),(770,462),(803,465),(824,472),(841,489),(851,509),(850,530),(841,548),(825,560),(808,556),(794,546),(778,537),(761,527),(747,522),(729,546),(705,576),(684,607),(677,628),(666,637),(651,637),(631,625),(615,603),(603,579),(591,551),(583,524),(576,494),(566,457),(568,426)])
Lbare=poly([(603,501),(648,495),(664,529),(680,550),(692,564),(713,535),(730,511),(747,513),(763,526),(743,551),(719,578),(698,604),(682,629),(667,638),(651,638),(633,626),(615,605),(603,579),(591,551)])
UT=g['whole_torso_head_rigid_matrix'];TH=g['thigh_rigid_matrix'];torso=shirt&~Rbare&~Lbare&~fixed
far_fold=(X<400)&(Y>=1075);pants=(Y>730)&(X<780)&~binary_erosion(shirt,iterations=3)&~Rmask&~Lmask&~fixed&~far_fold
# Real existing cloth groups with a narrow join. Full good knees/folds are held
# from the actual102 source below their curved transition, never a navy plate.
t1=smooth((np.arange(1536)-875)/90);t2=smooth((np.arange(1536)-995)/100);I=np.array([[1.,0.,0.],[0.,1.,0.]])
mat=(1-t1[:,None,None])*np.array(UT)+t1[:,None,None]*np.array(TH);mat=(1-t2[:,None,None])*mat+t2[:,None,None]*I;ms=np.concatenate([mat,np.tile([[[0.,0.,1.]]],(1536,1,1))],axis=1);inv=np.linalg.inv(ms)[:,:2];sx=inv[:,0,0,None]*X+inv[:,0,1,None]*Y+inv[:,0,2,None];sy=inv[:,1,0,None]*X+inv[:,1,1,None]*Y+inv[:,1,2,None]
out=Image.new('RGBA',src.size);out.alpha_composite(Image.fromarray(sample_rgba(np.array(part(pants)),sx,sy)));out.alpha_composite(part(((Y>=1095)|far_fold)&~fixed));out.alpha_composite(warp(part(torso),UT));pieces={}
for role,mask in [('L',Lmask),('R',Rmask)]:
 a=g['arms'][role];e=np.array(a['source_final102']['elbow']);w=np.array(a['source_final102']['wrist']);v=w-e;along=((X-e[0])*v[0]+(Y-e[1])*v[1])/np.linalg.norm(v);cross=((X-e[0])*(-v[1])+(Y-e[1])*v[0])/np.linalg.norm(v)
 if role=='R':hand=mask&(X>=826)&(Y>=710)&(Y<=825)
 else:
  jade=poly([(709,502),(699,489),(698,473),(704,454),(718,441),(732,439),(745,444),(755,456),(758,471),(753,490),(742,504),(727,510),(715,507)])
  palm=poly([(739,459),(758,462),(775,468),(804,468),(824,475),(839,490),(848,507),(847,531),(837,548),(821,558),(802,552),(786,539),(771,524),(755,520),(742,508),(738,489)])
  hand=mask&(jade|palm)
 bare=Rbare if role=='R' else poly([(630,585),(659,563),(692,535),(722,510),(739,502),(755,509),(771,521),(758,542),(736,569),(708,596),(688,618),(674,630),(661,635),(646,628),(633,613)])
 if role=='L':upper=mask&~hand&poly([(571,398),(611,398),(645,419),(659,450),(655,476),(650,495),(668,535),(682,564),(687,586),(681,607),(669,626),(652,626),(635,612),(618,587),(605,559),(595,534),(588,509),(578,479),(569,452),(567,424)])
 else:upper=mask&~hand&(along<18)
 fore=mask&bare&~hand&(along>-25)&(np.abs(cross)<44)
 for name,mk,m in [('upper',upper,a['upper_reference_matrix']),('forearm',fore,a['forearm_rigid_matrix']),('whole_hand',hand,a['whole_hand_bangle_same_rod_angle_matrix'])]:
  pieces[role+'_'+name]=joined_forearm(mk,a) if name=='forearm' else warp(part(mk),m)
  pieces[role+'_'+name].save(O/f'anatomy/{role}_{name}_OWN_FINAL102_SOURCE_REFERENCE.png')
for role in ['L','R']:
 for name in ['upper','forearm','whole_hand']:out.alpha_composite(pieces[role+'_'+name])
n=np.array(out)
# Only small newly uncovered rib cloth joins: same actual mother's flower cloth,
# clipped to the intended torso silhouette, no invented technical body shape.
coat_core=poly([(497,316),(559,333),(607,355),(640,379),(680,393),(707,419),(722,446),(726,476),(715,501),(698,522),(683,546),(675,573),(669,609),(668,663),(672,710),(699,757),(725,803),(753,852),(762,879),(744,886),(720,863),(666,843),(614,821),(571,802),(543,779),(527,750),(501,795),(469,788),(434,779),(398,761),(423,718),(456,679),(481,641),(494,608),(485,573),(461,554),(444,515),(449,464),(466,416),(482,370)])
cm=Image.fromarray(np.uint8(coat_core)*255);expected=np.array(warp(cm,UT,Image.Resampling.NEAREST))>0;corr=(X>475)&(X<715)&(Y>390)&(Y<855);gap=binary_dilation((n[:,:,3]<128)&corr,iterations=3)&corr&expected
cl=Image.new('RGBA',src.size);tile=src.crop((478,417,590,545))
for yy in range(390,870,128):
 for xx in range(475,720,112):cl.alpha_composite(tile,(xx,yy))
c=np.array(cl);c[~gap]=0;base=Image.fromarray(c);base.alpha_composite(out);n=np.array(base);n[fixed]=B[fixed]
activity=binary_dilation((B[:,:,3]>0)|(n[:,:,3]>0),iterations=10)&~fixed;protected=~activity;n[protected]=B[protected]
Image.fromarray(n).save(O/'anatomy/F106_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png');Image.fromarray(c).save(O/'anatomy/SMALL_SAME_SOURCE_RIB_CLOTH_REFERENCE_ONLY.png')
for name,mk in [('ALLOW_MINIMAL_NATIVE_ACTIVITY',activity),('HARD_PROTECTED_NATIVE_SUPPORT_AND_OUTSIDE',protected),('HARD_QUALIFIED_FINAL102_SHINS_SHOES_AIR',fixed)]:Image.fromarray(np.uint8(mk)*255).save(O/f'masks/{name}.png')
F=np.array(Image.open(M/'layers/F102_FG_true_front_fingers.png').convert('RGBA'));own=np.zeros((1536,1024),bool)
for role in ['L','R']:
 z=F.copy();z[Y>=670 if role=='L' else Y<670]=0;own|=np.array(warp(Image.fromarray(z),g['arms'][role]['whole_hand_bangle_same_rod_angle_matrix']))[:,:,3]>0
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'anatomy/F106_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F106_REFERENCE_FG_REAL_FRONT_FINGERS.png');assert np.array_equal(np.maximum(bg,fg),n);assert not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0));assert np.array_equal(n[protected],B[protected]);assert np.array_equal(n[fixed],B[fixed])
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(Image.fromarray(n));d=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for y,txt in [(18,'F106 / EXACT NATIVE ACTIVITY / BOTH COMPLETE ARM CHAINS'),(45,'FROM LOCKED102 / INPUT REFERENCE ONLY'),(1370,'Hip approaches above knees; waist/chest/whole head rise together.'),(1400,'Both upper lengths held. Far chain re-read at actual jade wrist.'),(1430,'Both own palms/jade stay rigid with true shafts. Knees/support held.'),(1460,'Small natural joint joins only. No new framing or technical plates.')]:d.text((18,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'inputs/01_F106_EXACT_NATIVE_ACTIVITY_TARGET.png')
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&activity;lab,num=label(holes);regions=[]
for i in range(1,num+1):
 yy,xx=np.where(lab==i)
 if len(xx)>8:regions.append({'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]})
(O/'qa/NATIVE_SOURCE_REFERENCE_READBACK.json').write_text(json.dumps({'status':'REFERENCE_ONLY_VISIBLE_CHAINS_TO_BE_REVIEWED','sole_source':'final actual102, no old106 pose reused','near_upper_projected_scale':1,'far_upper_projected_scale':1,'far_upper_note':'Actual elbow and wrist line behind jade re-read on102; palm-interior diagnostic proxy discarded. Both upper projected lengths retained.','own_complete_palms_and_bangle_rigid':True,'cross_arm_donor_blocks':False,'protected_RGBA_differences':0,'qualified_support_RGBA_differences':0,'BG_FG_overlap':0,'BG_FG_reconstruction_differences':0,'technical_skin_or_navy_guide_pixels':0,'new106_imagegen_calls':0,'actual106_person_Canvas':0,'internal_low_alpha_regions_for_actual_review':regions},indent=2)+'\n')
print('Complete106 real-source native reference ready;106 model calls0.')
