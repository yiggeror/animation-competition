from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent
S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
source=S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='0a65674bee91dec491997e45c5b0a2993c91a44f64424735883a032321b9a02b'
shutil.copyfile(source,R/'sources/F036_0a65674b_ONLY_CONTINUOUS_RGB_SOURCE.png')
src=np.array(Image.open(source).convert('RGBA'));H,W=src.shape[:2];yy,xx=np.indices((H,W))
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
prop=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
feather=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png').convert('L'))>0
arm=np.array(Image.open(S/'layers/ONE_M_WHOLE_ARM_JADE.png').convert('RGBA'))[:,:,3]>0
arm&=(src[:,:,3]>0)&(yy>=470)&~near
# The old adopted-arm support includes a few cotton/occlusion pixels. Reclassify
# actual locked036 skin+jade by material, preserving all skin/ink/AA, not cloth rim.
rgb=src[:,:,:3].astype(float)
skin=(rgb[:,:,0]>rgb[:,:,2]+27)&(rgb[:,:,0]>110)&(rgb[:,:,1]>65)
jade=(rgb[:,:,1]>rgb[:,:,0]*1.04)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
rgn=(xx>=510)&(xx<=810)&(yy>=490)&(yy<=710)
seeds=nd.binary_closing((skin|jade)&rgn,iterations=2);labs,_=nd.label(nd.binary_dilation(seeds,iterations=1));skinmask=nd.binary_fill_holes(labs==labs[585,675]);skinmask=nd.binary_dilation(skinmask,iterations=1)&(src[:,:,3]>0)
# Complete blue cuff/root stays a local full-material patch; no mask below wrist.
arm=(skinmask|(arm&(yy<605)&(xx<650)))&~near
# Carry the intact same-source pinch/contact cloth context with the complete hand,
# using the exact same plateau field; no separate pasted palm or finger.
contact_context=(xx>=685)&(xx<=810)&(yy>=635)&(yy<=715)
# Semantic masks from prior packages are geometry only. All RGB below comes from src.
def poly(pts):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0
cloth=poly([(487,741),(584,741),(623,702),(674,683),(726,663),(748,684),(812,724),(915,779),(1005,879),(978,975),(913,1049),(816,1060),(643,1012),(490,920),(354,822)])&(src[:,:,3]>0)&~arm&~near
cloth|=contact_context&(src[:,:,3]>0)&~arm&~near
cloth&=~prop
for name,m in [('SOURCE_FAR_COMPLETE_ARM_SLEEVE_TO_WHOLE_HAND',arm),('SOURCE_CONTINUOUS_OPAQUE_CLOTH',cloth),('LOCK_NEAR_C1',near),('TRUE_PROP_SUPPORT_GEOMETRY_ONLY',prop)]:Image.fromarray(m.astype('uint8')*255).save(R/'masks'/f'{name}.png')
def warp_piece(mask,dx,dy,kind):
 # A single continuous field for the complete arm; whole palm/fingers are in the
 # constant-translation plateau x>=670, never separate pasted hand components.
 if kind=='arm':
  start,end=560.,670.;a=np.zeros((H,W),float)
  low=xx<=start;high=xx>=end+dx;mid=~low&~high
  sx=xx.astype(float);sx[high]=xx[high]-dx;sx[mid]=(xx[mid]+dx*start/(end-start))/(1+dx/(end-start))
  w=np.clip((sx-start)/(end-start),0,1);sy=yy-dy*w
 else:
  # Pinch/top fold follows whole hand; the lower lap/hinge gradually stays fixed.
  start,end=740.,920.;sy=yy.astype(float)
  low=yy<=start+dy;high=yy>=end;mid=~low&~high
  sy[low]=yy[low]-dy;sy[mid]=(yy[mid]-dy*end/(end-start))/(1-dy/(end-start))
  w=np.clip((end-sy)/(end-start),0,1);sx=xx-dx*w
 v=src.astype(float);v[:,:,3]*=mask;v[:,:,:3]*=v[:,:,3:4]/255
 warped=np.stack([nd.map_coordinates(v[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],2)
 al=warped[:,:,3:4]/255;warped[:,:,:3]=np.divide(warped[:,:,:3],al,out=np.zeros_like(warped[:,:,:3]),where=al>1e-6)
 return np.round(np.clip(warped,0,255)).astype('uint8')
def ongray(v):
 im=Image.fromarray(v);o=Image.new('RGBA',(W,H),(236,239,242,255));o.alpha_composite(im);return o.convert('RGB')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
results=[]
for f,dx,dy in [(42,-7.,-1.),(48,-14.,-2.)]:
 aw=warp_piece(arm,dx,dy,'arm');cw=warp_piece(cloth,dx,dy,'cloth')
 # Feather only source-cotton INTERNAL sampling boundaries into the same036
 # cotton backing, never skin, real props or the actual new outer cloth edge.
 inside=(cw[:,:,3]>0)&(src[:,:,3]>=240)&(yy>=710)&~arm&~prop
 distance=nd.distance_transform_edt(cw[:,:,3]>0);blend=np.clip(distance/12,0,1)
 cw[inside,3]=np.round(cw[inside,3]*blend[inside]).astype('uint8')
 Image.fromarray((inside&(blend<1)).astype('uint8')*255).save(R/'masks'/f'F{f:03d}_INTERNAL_SAME_COTTON_SEAM_BLEND.png')
 base=src.copy();base[arm]=0
 # Clear only withdrawn top-edge cloth foreground; interior cloth remains a same-source backing.
 csil=nd.binary_fill_holes(cloth|prop);wsil=warp_piece(csil,dx,dy,'cloth')[:,:,3]>0
 withdraw=np.zeros((H,W),bool) # retain locked036 continuous cotton as backing; never cut a moving rim strip
 # Same locked036 internal cotton, full-width backing below the moved whole pinch.
 # It closes the withdrawn old-hand negative space without creating new RGB.
 pp=np.array([725.78751656+dx,663.66135947+dy]);px,py=np.round(pp).astype(int)
 under=np.zeros_like(src);under[py+1:py+36,px-25:px+35]=src[700:735,690:750]
 support=poly([(px,py+1),(px+34,py+25),(px+34,py+35),(px-25,py+35),(px-17,py+18)])
 under[~support]=0
 out=Image.alpha_composite(Image.fromarray(base),Image.fromarray(under));out=Image.alpha_composite(out,Image.fromarray(cw));out=Image.alpha_composite(out,Image.fromarray(aw));v=np.array(out)
 # Same original props and four rods never move. Only a finite outer-feather suffix
 # can be occluded by this opaque new cloth front lip.
 allowed=feather&(xx>=790)&(xx<=878)&(yy>=775)&(yy<=840)&(cw[:,:,3]>=250)
 keep=prop&~allowed;v[keep]=src[keep];v[near]=src[near]
 # Restore all head/chest pixels above the local sleeve overlap; no whole-person drift.
 fixed=(yy<470);v[fixed]=src[fixed]
 Image.fromarray(v).save(R/'inputs'/f'F{f:03d}_ONE_COMPLETE_TARGET_TECHNICAL_NOT_NATIVE.png')
 ongray(v).save(R/f'F{f:03d}_FULL_TARGET_ON_GRAY.png')
 c=ongray(v).crop((470,455,890,875));c.resize((840,840)).save(R/'contacts'/f'F{f:03d}_WHOLE_ARM_PINCH_AND_TRUE_TAIL.png')
 Image.fromarray(allowed.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_ONLY_FINITE_REAL_OUTER_FEATHER_COVER.png')
 changed=np.any(v!=src,2)
 pinch=np.array([725.78751656,663.66135947]);oldE=np.array([635.,592.]);oldW=np.array([685.,623.]);root=np.array([565.,536.])
 def mapped(p):return (p+np.array([dx,dy])*np.clip((p[0]-560)/110,0,1)).tolist()
 results.append({'frame':f,'target_sha256':sha(R/'inputs'/f'F{f:03d}_ONE_COMPLETE_TARGET_TECHNICAL_NOT_NATIVE.png'),'whole_hand_translation':[dx,dy],'pinch_proxy':(pinch+[dx,dy]).tolist(),'far_chain_manual_proxy_not_measured_bones':{'root':mapped(root),'elbow':mapped(oldE),'wrist':mapped(oldW),'pinch':(pinch+[dx,dy]).tolist()},'near_C1_RGBA_changed':int(np.any(v[near]!=src[near],axis=1).sum()),'head_chest_top470_RGBA_changed':int(np.any(v[fixed]!=src[fixed],axis=1).sum()),'true_props_outside_finite_feather_RGBA_changed':int(np.any(v[keep]!=src[keep],axis=1).sum()),'finite_feather_material_changed_pixels':int((changed&allowed).sum()),'no_new_RGB_drawing':True,'source_composition_retained_as_cotton_backing':True,'pinch_cotton_underlayer':{'source_crop':[690,700,750,735],'target_bbox':[int(px-25),int(py+1),int(px+35),int(py+36)],'scale':1,'whole_same_source_patch_below_new_arm_and_fold':True}})
# Same local identity file for both requests: complete head and internal cloth only.
d=Image.new('RGBA',(620,700),(0,0,0,0));d.alpha_composite(Image.fromarray(src).crop((235,45,630,440)),(30,28));d.alpha_composite(Image.fromarray(src).crop((260,445,375,575)),(35,465));d.alpha_composite(Image.fromarray(src).crop((650,700,735,738)),(200,465))
ImageDraw.Draw(d).text((24,645),'IDENTITY / INTERNAL COTTON ONLY - NO POSE',font=font,fill=(25,40,55,255));d.save(R/'inputs/SHARED_LOCAL_HEAD_AND_INTERNAL_MATERIAL_ONLY.png')
json.dump({'source_sha256':sha(source),'source_commit':'565fe6d5','only_continuous_RGB_source':str(source.relative_to(B.parent.parent.parent)),'status':'TECHNICAL_INPUT_TARGETS_NOT_NEW_NATIVE_NOT_FROZEN','projection_warning':'A bounded smooth image-space deformation is only a technical target; proxy projection lengths are not real bone measurements or a native anatomy pass. Whole palm/fingers share constant translation, not separate pasted fingers/palm.','arm_field':{'fixed_through_source_x':560,'full_whole_hand_translation_from_source_x':670,'inverse':'piecewise monotone affine x; y displaced by the same smooth ramp'},'cloth_field':{'top_follows_hand_until_y':740,'lap_fixed_from_y':920},'states':results},open(R/'geometry/TWO_TARGET_SOURCE_AND_FINITE_CHECKS.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(results,ensure_ascii=False,indent=2))
