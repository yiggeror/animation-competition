from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,binary_dilation,maximum_filter,minimum_filter
R=Path.cwd();P=R/'collab/reviews/cloud_s12_20261018/d01_F000';O=P/'same_raw_fix_20261019';raw=P/'originals/F000_raw_attempt03.png';ref=P/'inputs/identity03_original.png';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(raw)=='87f85597246e995ad4988b3a766c4f4171201851780e8c8ab5b3b0a93bf3cd61';assert sha(ref)=='ab88b69f5303229af379303a37b6e9e3c8cdb35cd05b3902b604871efb2b1671'
a=np.asarray(Image.open(raw).convert('RGBA'));b=np.asarray(Image.open(ref).convert('RGB'));rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3];out=a.copy()
def poly_mask(size,polys):
 im=Image.new('L',size,0);d=ImageDraw.Draw(im)
 for p in polys:d.polygon(p,fill=255)
 return np.asarray(im)>0
# Explicit physical material regions. Hair/jade/flowers/ink/trousers are not global colour targets.
skin_poly=[[(570,490),(617,478),(665,463),(724,429),(759,450),(777,482),(749,522),(749,551),(727,603),(711,631),(681,638),(650,620),(613,637),(598,662),(563,618),(557,566)],[(481,853),(573,854),(588,916),(680,958),(784,965),(833,981),(882,1007),(878,1052),(828,1063),(740,1049),(632,1018),(516,979)],[(699,748),(747,765),(823,797),(886,809),(945,812),(997,835),(992,894),(936,893),(878,876),(800,868),(724,855),(671,821)],[(146,1123),(219,1128),(224,1202),(139,1201)],[(181,1202),(244,1205),(245,1291),(175,1290)]]
blue_poly=[[(508,545),(605,581),(721,743),(724,777),(683,827),(593,830),(594,873),(512,900),(531,1038),(493,1068),(305,1080),(152,989),(157,950),(287,800),(359,671),(427,598)]]
skin_sem=poly_mask((1024,1536),skin_poly);blue_sem=poly_mask((1024,1536),blue_poly)
source_skin_sem=poly_mask((2048,768),[[(465,66),(498,58),(570,59),(606,84),(605,151),(575,182),(553,202),(543,219),(513,215),(487,183),(460,153)],[(393,312),(438,313),(447,448),(435,510),(389,508)],[(619,310),(660,311),(676,505),(635,514),(627,443)],[(439,697),(630,698),(630,730),(439,730)]])
source_blue_sem=poly_mask((2048,768),[[(474,181),(580,181),(637,220),(668,314),(631,331),(636,446),(432,450),(433,328),(398,310),(425,226)]])
def skin_colour(x):return (x[:,:,0]>180)&(x[:,:,1]>120)&(x[:,:,2]>70)&(x[:,:,0]>x[:,:,1]+18)&(x[:,:,1]>x[:,:,2]+11)
def blue_colour(x):return (x[:,:,0]>65)&(x[:,:,2]>x[:,:,0]+20)&(x[:,:,2]>x[:,:,1]+15)&(np.max(x,2)>120)
source_skin=source_skin_sem&skin_colour(b.astype(np.int16));source_blue=source_blue_sem&blue_colour(b.astype(np.int16))
# Protect dark ink and high-contrast dark ridges; all native alpha cores stay exact.
lo=minimum_filter(rgb,size=(3,3,1));hi=maximum_filter(rgb,size=(3,3,1));ridge=(np.max(hi-lo,2)>38)&(np.min(rgb,2)<150)
ink=(np.max(rgb,2)<120)&(alpha>=8);line_protect=binary_dilation(ink|ridge,iterations=1)
white=(np.min(rgb,2)>210)&((np.max(rgb,2)-np.min(rgb,2))<35)&(alpha>=8);flower_protect=binary_dilation(white&blue_sem,iterations=1)
raw_skin=skin_sem&skin_colour(rgb)&(alpha>=8);raw_blue=blue_sem&blue_colour(rgb)&(alpha>=8)
regions={};weights={}
for name,selection,source in [('skin',raw_skin,source_skin),('blouse_blue',raw_blue,source_blue)]:
 protect=line_protect|(flower_protect if name=='blouse_blue' else False)
 editable=selection&~protect
 weight=np.clip(distance_transform_edt(editable)/2,0,1);weight[~editable]=0
 core=editable&(weight>=1)&(alpha>=128);assert core.sum()>20000
 target=b[source].astype(np.float64).mean(0);base=rgb.astype(np.float64);delta=np.zeros(3)
 for c in range(3):
  low,high=-80.,80.
  for _ in range(42):
   mid=(low+high)/2;mean=np.clip(base[:,:,c][core]+mid,0,255).mean()
   if mean<target[c]:low=mid
   else:high=mid
  delta[c]=(low+high)/2
 # One-level adjustment keeps full pigment masks within4 as well as protected-core means.
 if name=='skin':delta[2]+=1
 if name=='blouse_blue':delta[1]+=1
 changed=np.rint(np.clip(base+weight[:,:,None]*delta,0,255)).astype(np.uint8)
 out[:,:,:3][editable]=changed[editable]
 weights[name]=weight
 Image.fromarray((weight*255).astype(np.uint8)).save(O/f'masks/{name}_edit_weight.png');Image.fromarray(core.astype(np.uint8)*255).save(O/f'masks/{name}_core_measurement.png');Image.fromarray(source.astype(np.uint8)*255).save(O/f'masks/source03_{name}_same_material.png')
 after=out[:,:,:3][core].astype(float).mean(0);before=a[:,:,:3][core].astype(float).mean(0)
 regions[name]={'source_pixels':int(source.sum()),'candidate_core_pixels':int(core.sum()),'target_source03_mean_RGB':target.tolist(),'before_core_mean_RGB':before.tolist(),'after_core_mean_RGB':after.tolist(),'mean_delta_after_vs_source':(after-target).tolist(),'additive_RGB_offset_before_clipping':delta.tolist(),'contrast_slope_in_unclipped_core':1.0,'lineart_protection':'dark ink + dark high-contrast ridge dilation1;white flower cores protected;2px transition inside editable material only'}
 assert max(abs(after-target))<=2
# Remove only detached/remote very-low-alpha residue; retain AA close to body and fine head ink.
solid=alpha>=8;dist=distance_transform_edt(~solid);yy,xx=np.indices(alpha.shape);fine_head=(xx>=420)&(xx<=810)&(yy>=320)&(yy<=590)&(np.max(rgb,2)<170)&(dist<=12)
remove=(alpha>0)&(alpha<8)&(dist>3)&~fine_head
out[:,:,3][remove]=0
# RGB beneath cleared transparent pixels is preserved, so removing alpha never repaints anything.
Image.fromarray(out).save(O/'candidate/F000.png')
changed_rgb=np.any(out[:,:,:3]!=a[:,:,:3],2);changed_alpha=out[:,:,3]!=alpha
for name,mask in [('changed_RGB',changed_rgb),('removed_low_alpha',changed_alpha),('protected_lineart',line_protect),('protected_white_flowers',flower_protect),('fine_head_low_alpha_protection',fine_head),('skin_semantic_area',skin_sem),('blouse_semantic_area',blue_sem)]:Image.fromarray(mask.astype(np.uint8)*255).save(O/f'masks/{name}.png')
pants=(np.indices(alpha.shape)[0]>980)&(np.max(rgb,2)<120)&(rgb[:,:,2]>rgb[:,:,0]+6)&(alpha>=8)
hair=Image.open(P/'material_masks/hair.png');hairmask=np.asarray(hair)>0
assert not np.any(changed_rgb&line_protect);assert not np.any(changed_rgb&pants);assert not np.any(changed_rgb&hairmask);assert np.array_equal(out[:,:,3][solid],alpha[solid]);assert not np.any(changed_rgb&~(raw_skin|raw_blue));assert np.array_equal(out[:,:,:3][~changed_rgb],a[:,:,:3][~changed_rgb]);assert np.array_equal(out[alpha>=8,3],a[alpha>=8,3])
report={'status':'SAME_RAW_MATERIAL_AND_DETACHED_LOW_ALPHA_REPAIR_PASS','source_raw_SHA256':sha(raw),'source03_SHA256':sha(ref),'candidate_SHA256':sha(O/'candidate/F000.png'),'imagegen_calls':0,'pose_or_geometry_transforms':0,'regions':regions,'RGB_changed_pixels':int(changed_rgb.sum()),'alpha_removed_pixels':int(changed_alpha.sum()),'alpha_removed_original_values':sorted(np.unique(alpha[changed_alpha]).tolist()),'alpha_ge8_exact':True,'trousers_RGB_exact':True,'hair_RGB_exact':True,'lineart_protection_RGB_exact':True,'white_flower_protection_RGB_exact':not bool(np.any(changed_rgb&flower_protect)),'RGB_outside_skin_blue_exact':True,'RGB_under_alpha_cleanup_unchanged':True,'fine_head_protected_alpha_exact':np.array_equal(out[:,:,3][fine_head],alpha[fine_head]),'alpha_rule':'Remove alpha1..7 beyond3px fromalpha>=8,except darkfinehead pixels within12px;keep corealpha and originalRGB.','native_size':[1024,1536]}
(O/'qa/material_alpha_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(O/'qa/source_and_region_definitions.json').write_text(json.dumps({'source_raw_path':str(raw.relative_to(R)),'source03_path':str(ref.relative_to(R)),'skin_polygons_native':skin_poly,'blouse_polygons_native':blue_poly,'source03_same_material_masks':'masks/source03_skin_same_material.png,masks/source03_blouse_blue_same_material.png','not_global_colour_adjustment':True},ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
