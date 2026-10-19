"""Separate same-raw gray-hair light planes, blue R planes, and locked012 shaded tip."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_erosion,distance_transform_edt,gaussian_filter,maximum_filter,minimum_filter
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=P/'originals/F018_raw_call01.png';geom=O/'candidate/F018_geometry_only.png';mother=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png';locked=S/'d03_F018_inputs_20261019/inputs/01_locked_F012.png'
a=np.array(Image.open(raw));out=np.array(Image.open(geom));m=np.array(Image.open(mother));k=np.array(Image.open(locked));rgb=a[:,:,:3].astype(float);rr,gg,bb=rgb.transpose(2,0,1);alpha=a[:,:,3];h,w=alpha.shape
poly=lambda pts:makepoly(pts)
def makepoly(pts):
 im=Image.new('L',(w,h));ImageDraw.Draw(im).polygon([tuple(v) for v in pts],fill=255);return np.array(im)>0
def save(name,mask):Image.fromarray((np.asarray(mask)*255).astype(np.uint8)).save(O/f'masks/{name}.png')
# Hair: only crown and bun LIGHT GRAY planes. Ear-back dark region, ink and highlights stay raw.
crown=poly([(513,423),(520,378),(546,350),(589,333),(639,332),(696,337),(737,354),(752,391),(778,402),(803,431),(803,476),(783,497),(756,478),(741,439),(710,463),(670,488),(627,508),(604,517),(577,501),(548,477),(525,455)])
bun=poly([(439,472),(452,449),(480,436),(513,437),(540,460),(548,492),(566,516),(576,534),(570,554),(544,559),(512,551),(480,537),(454,518),(439,495)])
earback=poly([(545,495),(580,494),(605,510),(637,536),(622,571),(582,578),(550,559)])
gray=(abs(rr-gg)<30)&(abs(gg-bb)<20)&(rr>85)&(rr<235)&(alpha>=128);lum=rgb.mean(2)
localspread=maximum_filter(lum,3)-minimum_filter(lum,3);strands=(lum<151)|((localspread>25)&(lum<181));highlights=(rgb.max(2)>212);hairprotect=strands|highlights|earback
hairmeta={};hairchanged=np.zeros((h,w),bool)
for name,area in [('crown_light_gray',crown),('bun_light_gray',bun)]:
 editable=area&gray&~hairprotect&(lum>145)&(lum<213);weight=np.clip(distance_transform_edt(editable)/3,0,1);weight*=np.clip((lum-145)/15,0,1)*np.clip((213-lum)/10,0,1)
 mx=m[:,:,:3].astype(float);mr,mg,mb=mx.transpose(2,0,1);targetgray=(abs(mr-mg)<30)&(abs(mg-mb)<20)&(mr>85)&(mr<235)&(m[:,:,3]>=128)
 core=(weight>.99)&targetgray;assert core.sum()>800
 bias=(mx[core]-rgb[core]).mean(0)
 for ch in range(3):out[:,:,ch]=np.where(editable,np.clip(np.rint(rgb[:,:,ch]+weight*bias[ch]),0,255),out[:,:,ch]).astype(np.uint8)
 changed=np.any(out[:,:,:3]!=np.array(Image.open(geom))[:,:,:3],2)&area
 hairchanged|=changed;save(name+'_editable',editable);save(name+'_matched_core',core);save(name+'_weight',weight)
 hairmeta[name]={'editable_pixels':int(editable.sum()),'matched_core_pixels':int(core.sum()),'RGB_bias_only_on_plane':bias.tolist(),'before_core_delta_RGB':(rgb[core]-mx[core]).mean(0).tolist(),'after_core_delta_RGB':(out[core,:3].astype(float)-mx[core]).mean(0).tolist()}
save('hair_protected_dark_strands_highlights_earback',hairprotect&(crown|bun));save('hair_actual_RGB_changed',hairchanged)
# Physical blouse faces; small R corrections only, no G/B, flower or line edits.
whole=np.array(Image.open(S/'d01_F000/same_raw_fix_20261019/masks/blouse_semantic_area.png'))>0
facepolys={'far_sleeve':[(603,635),(645,657),(692,703),(729,740),(729,779),(690,816),(634,843),(594,821),(591,766)],'near_sleeve':[(436,663),(482,644),(524,648),(560,677),(578,736),(588,808),(596,869),(580,887),(446,890),(432,813),(426,728)],'collar_front':[(507,544),(605,580),(658,653),(658,781),(616,853),(566,917),(513,965),(533,1039),(493,1070),(474,1006),(496,938),(521,889),(552,841),(552,734),(521,662)]}
faces={};assigned=np.zeros((h,w),bool)
for name,pts in facepolys.items():faces[name]=poly(pts)&whole&~assigned;assigned|=faces[name]
yy,xx=np.indices((h,w));faces['lower_hem']=(yy>=970)&whole&~assigned;assigned|=faces['lower_hem'];faces['back_waist']=whole&~assigned
ref=S/'d02_F012_20261019/placket_tip_fix_20261019';tip=np.array(Image.open(ref/'masks/domain_complete_semantic_tip.png'))>0
ink=(rgb.max(2)<120)|((np.max(maximum_filter(rgb,size=(3,3,1))-minimum_filter(rgb,size=(3,3,1)),2)>38)&(rgb.min(2)<150));ink=binary_dilation(ink,iterations=1)
flowers=binary_dilation((rgb.min(2)>210)&(rgb.max(2)-rgb.min(2)<35)&whole,iterations=1)
def blue(x):r,g,b=x.transpose(2,0,1);return (r>65)&(b>r+20)&(b>g+15)&(np.max(x,2)>120)
editable=whole&blue(rgb)&~ink&~flowers&~tip&(alpha>=128);weight=np.clip(distance_transform_edt(editable)/2,0,1);num=np.zeros((h,w));den=np.zeros((h,w));bluemeta={}
for name,area in faces.items():
 mask=area&~tip&blue(rgb)&(alpha>=128);target=area&~tip&blue(m[:,:,:3].astype(float))&(m[:,:,3]>=128)
 delta=(rgb[mask].mean(0)-m[target,:3].mean(0));reduction=float(np.clip(delta[0]-2.8,0,3.0));smooth=gaussian_filter(area.astype(float),6);num+=reduction*smooth;den+=smooth
 bluemeta[name]={'whole_plane_blue_pixels':int(mask.sum()),'raw_delta_vs000_RGB':delta.tolist(),'R_reduction_max_requested':reduction};save('blue_face_'+name,area)
field=np.divide(num,den,out=np.zeros_like(num),where=den>1e-9);out[:,:,0]=np.where(editable,np.clip(np.rint(rr-field*weight),0,255),out[:,:,0]).astype(np.uint8);save('blue_R_only_edit_support',editable);save('blue_protected_ink',ink&whole);save('blue_protected_flowers',flowers)
# Static tip uses final locked012, independently fitted for lit/shaded blue and shaded flower fill.
faces_tip={name:np.array(Image.open(ref/f'masks/{name}_face.png'))>0 for name in ['lit','shade']}
lo=minimum_filter(rgb,size=(3,3,1));hi=maximum_filter(rgb,size=(3,3,1));tipink=binary_dilation((rgb.max(2)<100)|((np.max(hi-lo,2)>65)&(rgb.min(2)<80)),iterations=1)
cloth=((bb>rr+15)&(bb>gg+8)&(gg>rr+6)&(rr>60)&(bb>115))|((rr>135)&(gg>145)&(bb>155)&(abs(bb-rr)<65));edit_tip=tip&cloth&~tipink&(alpha>=128);fw=np.clip(distance_transform_edt(edit_tip)/2,0,1)
transforms={};tipmeta={}
for name,face in faces_tip.items():
 common=binary_erosion(face,iterations=1)&(alpha>=128)&(k[:,:,3]>=128)&~tipink
 sx=rgb;tx=k[:,:,:3].astype(float);sr,sg,sb=sx.transpose(2,0,1);tr,tg,tb=tx.transpose(2,0,1)
 cb=common&(sb>sr+20)&(sg>sr+8)&(tb>tr+20)&(tg>tr+8)&(sr<180)&(tr<180)
 cf=common&(sr>165)&(sg>175)&(sb>185)&(sb-sr<55)&(tr>165)&(tg>175)&(tb>185)&(tb-tr<55)
 cb=binary_erosion(cb,iterations=1);cf=binary_erosion(cf,iterations=1);assert cb.sum()>200
 s0=sx[cb].mean(0);t0=tx[cb].mean(0)
 if name=='shade':
  assert cf.sum()>100;s1=sx[cf].mean(0);t1=tx[cf].mean(0);gain=(t1-t0)/(s1-s0);bias=t0-gain*s0;assert np.all((gain>.6)&(gain<1.3))
 else:gain=np.ones(3);bias=t0-s0
 transforms[name]=(gain,bias);tipmeta[name]={'matched_blue_pixels':int(cb.sum()),'matched_flower_pixels':int(cf.sum()),'RGB_gain':gain.tolist(),'RGB_bias':bias.tolist()};save('tip_'+name+'_matched_blue',cb);save('tip_'+name+'_matched_flowers',cf)
wl=gaussian_filter(faces_tip['lit'].astype(float),2);ws=gaussian_filter(faces_tip['shade'].astype(float),2);wl=np.divide(wl,wl+ws,out=np.zeros_like(wl),where=wl+ws>0)
gain=wl[:,:,None]*transforms['lit'][0]+(1-wl[:,:,None])*transforms['shade'][0];bias=wl[:,:,None]*transforms['lit'][1]+(1-wl[:,:,None])*transforms['shade'][1];color=np.clip(np.rint(rgb+(rgb*gain+bias-rgb)*fw[:,:,None]),0,255).astype(np.uint8);out[:,:,:3]=np.where(edit_tip[:,:,None],color,out[:,:,:3]);save('tip_RGB_edit_support',edit_tip);save('tip_protected_ink',tipink&tip)
geom_a=np.array(Image.open(geom));changed=np.any(out[:,:,:3]!=geom_a[:,:,:3],2);color_domain=hairchanged|editable|edit_tip;assert not np.any(changed&~color_domain);assert np.array_equal(out[:,:,3],geom_a[:,:,3]);assert np.array_equal(out[earback],geom_a[earback]);assert not np.any(hairchanged&hairprotect)
Image.fromarray(out).save(O/'candidate/F018.png');save('color_actual_RGB_changed',changed)
report={'source_raw_SHA256':sha(raw),'geometry_only_SHA256':sha(geom),'candidate_SHA256':sha(O/'candidate/F018.png'),'hair_bright_planes_only':hairmeta,'hair_dark_earback_line_highlights_exact':True,'blue_R_only_physical_faces':bluemeta,'blue_G_B_exact_except_tip':True,'tip_independent_final012_authority_SHA256':sha(locked),'tip_plane_transforms':tipmeta,'color_alpha_exact_geometry_only':True,'RGB_changed_by_color':int(changed.sum()),'imagegen_calls':0}
(O/'qa/native_color_repair.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
