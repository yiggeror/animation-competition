from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import distance_transform_edt,map_coordinates
R=Path('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812');G=R/'F027_from_F025_input_gate_v3_5refs_1925';B=R/'F027_call14_result_wrist_registered';O=R/'F027_call14_result_v6_semantic'
for n in ['candidates','qa','masks','geometry']:(O/n).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(G/'source_snapshot/S08_F025_grandma_match_box_RGBA.png'));pre=np.array(Image.open(G/'inputs/F027_scene_preplaced_NO_ROD_RGBA.png'));o=np.array(Image.open(B/'candidates/S08_F027_same_raw_candidate_RGBA.png'));q=np.zeros_like(a);q[660:990,900:1320]=np.array(Image.open(B/'registered/F027_registered_scene_patch_RGBA.png'));H,W=a.shape[:2];yy,xx=np.indices((H,W));w=np.array(Image.open(G/'masks/F027_WHITE_allowed_BLACK_frozen.png'))>0
near=np.array(Image.open(G/'masks/F027_near_HAND_MATCH_guard.png'))>0;far=np.array(Image.open(G/'masks/F027_far_CLOSED_HAND_JADE_AND_ALPHA0_SEAT_guard.png'))>0
oldnear=np.array(Image.open(G/'source_snapshot/F025_true_near_hand_match_footprint.png'))>0
ops=[]
def poly(pts):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(pts,fill=255);return (np.array(m)>0)&w
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/(n+'.png'));ops.append({'operation':n,'pixels':int(m.sum())})
def shift(b,dx,dy):
 out=np.zeros_like(b);y0=max(0,dy);y1=min(H,H+dy);x0=max(0,dx);x1=min(W,W+dx);out[y0:y1,x0:x1]=b[y0-dy:y1-dy,x0-dx:x1-dx];return out
def paste(m,s,t):
 y,x=np.where(m);v=s[y,x];before=o[y,x].copy();t=t[y,x] if isinstance(t,np.ndarray) else np.full(len(y),t);oa=o[y,x,3]/255.;na=v[:,3]/255.;al=oa*(1-t)+na*t;rgb=o[y,x,:3]*oa[:,None]*(1-t[:,None])+v[:,:3]*na[:,None]*t[:,None];o[y,x,:3]=np.rint(rgb/np.maximum(al[:,None],1e-9)).clip(0,255).astype('uint8');o[y,x,3]=np.rint(al*255).astype('uint8'); edge=(oa<0.96)|(na<0.96);choose=edge&(t>=0.5);keep=edge&~choose;o[y[choose],x[choose]]=v[choose];o[y[keep],x[keep]]=before[keep]
# Source025 sleeve-to-upperarm is already accepted. Keep original pixels, never copy vacated near hand.
m=poly([(940,840),(978,808),(1026,779),(1055,779),(1057,820),(1025,842),(975,860)])&~oldnear;o[m]=a[m];save('RESTORE_LOCKED025_real_upperarm_below_cuff_excluding_old_near_hand',m)
# Genuine proximal wrist skin accompanies the fixed near hand by the same integer translation.
m=poly([(916,844),(940,830),(971,836),(981,910),(950,929),(918,924)]);s=shift(a,6,3);k=np.clip((xx-919)/29,0,1);paste(m,s,k);save('JOIN_original025_near_wrist_collar_rigid_plus6_plus3',m)
# Remove only duplicated raw upper-hand line in the vacated strip, using same raw clean far-forearm skin.
m=poly([(974,831),(1000,815),(1024,809),(1049,815),(1053,825),(1021,834),(987,848)])&~near&~far;y,x=np.where(m);sx=np.rint(1080+(x-974)*0.35).astype(int);sy=np.rint(842+(y-809)*0.30).astype(int);v=q[sy,sx];good=(v[:,3]>245)&(v[:,0]>v[:,1]+20)
# All source clone pixels must be genuine opaque skin; no fill from transparency.
assert good.all(),(int((~good).sum()),(int(x[~good][0]),int(y[~good][0])))
k=np.minimum(distance_transform_edt(m)[y,x]/1.2,1);o[y,x,:3]=np.rint(o[y,x,:3]*(1-k[:,None])+v[:,:3]*k[:,None]).astype('uint8');o[y,x,3]=255;save('CLEAR_duplicate_upper_hand_line_same_call14_clean_skin_texture_patch_only',m)
# Genuine025 proximal skin collar follows the exact hand/jade translation. Only white collar can change.
m=poly([(1090,807),(1129,792),(1164,830),(1140,865),(1111,873),(1090,849)]);s=shift(a,-8,16);jade=np.array(Image.open(G/'masks/F027_true_jade_material_AND_outline_hard_guard.png'))>0;k=np.clip((12-distance_transform_edt(~jade))/6,0,1);paste(m,s,k);save('JOIN_original025_far_proximal_skin_collar_rigid_minus8_plus16',m)
# Only duplicated generated match/wood in true air, outside the true near-hand guard.
m=poly([(1047,834),(1070,783),(1095,783),(1095,821),(1060,843)])&~near&~far;o[m]=0;save('CLEAR_duplicate_raw_match_in_air_outside_true_match_guard',m)
# Exact original body/air under proximal near wrist; no new blue slivers.
m=poly([(911,902),(933,900),(949,912),(935,940),(911,940)])&((xx<934)|(yy>920));o[m]=a[m];save('RESTORE_original025_body_air_under_near_wrist',m)
m=poly([(915,853),(940,830),(972,827),(972,854),(938,870)])&~oldnear;o[m]=a[m];save('RESTORE_original025_near_forearm_upper_crossover_no_raw_extra_line',m)
m=poly([(900,845),(947,828),(947,894),(900,920)])&~oldnear;o[m]=a[m];save('RESTORE_true025_proximal_near_forearm_no_extra_native_line',m)
m=poly([(920,910),(943,908),(943,930),(920,940)]);o[m]=a[m];save('CLEAR_shifted_blue_tail_to_original_body_air',m)
# Small interior stray native line, never any protected finger line.
m=poly([(969,837),(982,834),(985,843),(972,850)]);y,x=np.where(m);v=q[y+30,x-35];assert (v[:,3]>245).all();k=np.minimum(distance_transform_edt(m)[y,x]/1.2,1);o[y,x,:3]=np.rint(o[y,x,:3]*(1-k[:,None])+v[:,:3]*k[:,None]).astype('uint8');save('CLEAR_single_stray_raw_interior_line_same_raw_skin_minus35_plus30',m)
# Short22px lower skin-collar transition, from original025 pixels into its+6,+3 rigid hand position.
# Only this tiny connector is resampled; protected hand and whole forearm are never warped.
m=poly([(923,897),(945,897),(945,919),(923,919)]);y,x=np.where(m);t=np.clip((x-923)/22,0,1);t=t*t*(3-2*t);sx=x-6*t;sy=y-3*t
v=np.stack([map_coordinates(a[:,:,c].astype(float),[sy,sx],order=1,mode='constant',cval=0) for c in range(4)],axis=1).round().clip(0,255).astype('uint8');blue=(v[:,2].astype(int)>v[:,0]+15)&(v[:,1]>v[:,0]);v[blue]=a[y[blue],x[blue]];o[y,x]=v;save('STITCH_22px_near_lower_skin_collar_original025_to_plus6_plus3_no_hand_warp',m)
# Guard restoration includes complete distal alpha-zero grip seat but excludes released proximal skin collar.
o[~w]=pre[~w]
p=O/'candidates/S08_F027_same_raw_semantic_candidate_RGBA.png';Image.fromarray(o).save(p)
rod=Image.open(G/'inputs/F027_TRUE_LOW_ROD_separate_CONTEXT_LAYER.png');im=Image.alpha_composite(rod,Image.fromarray(o))
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),im)
 for n,bb,z in [('whole_arm',(900,660,1320,990),3),('near_wrist',(910,820,1050,930),6),('jade_wrist',(1080,780,1190,875),7),('upperarm_depth',(930,775,1100,875),5)]:bg.crop(bb).resize(((bb[2]-bb[0])*z,(bb[3]-bb[1])*z),Image.Resampling.NEAREST).convert('RGB').save(O/'qa'/(n+'_'+tag+'.png'))
 bg.crop((570,270,1450,1030)).resize((1100,950),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/('fullbody_'+tag+'.png'))
 old=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(a));pair=Image.new('RGB',(1680,700),col[:3]);pair.paste(old.crop((900,660,1320,990)).resize((840,660)),(0,40));pair.paste(bg.crop((900,660,1320,990)).resize((840,660)),(840,40));d=ImageDraw.Draw(pair);d.text((10,10),'LOCKED025',fill=(160,130,50));d.text((850,10),'027 SAME RAW SEMANTIC CANDIDATE - NOT LOCKED',fill=(160,130,50));pair.save(O/'qa'/('025_027_compare_'+tag+'.png'))
ch=np.any(o!=pre,2);checks={'outside_white_changed':int((ch&~w).sum())}
for name in ['far_CLOSED_HAND_JADE_AND_ALPHA0_SEAT_guard','near_HAND_MATCH_guard','actual_blue_cloth_guard','fixed_table_box_guard']:
 m=np.array(Image.open(G/'masks'/('F027_'+name+'.png')))>0;checks[name+'_changed']=int((ch&m).sum())
rep={'status':'SAME_RAW_SEMANTIC_CANDIDATE_NOT_LOCKED','candidate_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_call':14,'raw_sha256':'d3364d4e471f9259d2eaf79aea70ed69d4d6d33add96a76a0a0d8ebee2e13e17','uniform_registration':{'scale':1260/1415,'tx':0,'ty':(990-1112*1260/1415)/2+21},'new_native_calls':0,'operations':ops,'checks':checks};(O/'geometry/checks.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
