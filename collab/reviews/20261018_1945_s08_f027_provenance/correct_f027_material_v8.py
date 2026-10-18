from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,shutil
from scipy.ndimage import distance_transform_edt
R=Path('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812');G=R/'F027_from_F025_input_gate_v3_5refs_1925';S=R/'F027_call14_result_v6_semantic';O=R/'F027_call14_result_v8_color_final'
for n in ['candidates','qa','masks','geometry']:(O/n).mkdir(parents=True,exist_ok=True)
p=S/'candidates/S08_F027_same_raw_semantic_candidate_RGBA.png';a=np.array(Image.open(p));b=a.copy();H,W=a.shape[:2];yy,xx=np.indices((H,W));q=np.zeros_like(a);q[660:990,900:1320]=np.array(Image.open(R/'F027_call14_result_wrist_registered/registered/F027_registered_scene_patch_RGBA.png'))
w=np.array(Image.open(G/'masks/F027_WHITE_allowed_BLACK_frozen.png'))>0;jade=np.array(Image.open(G/'masks/F027_true_jade_material_AND_outline_hard_guard.png'))>0
hard=np.zeros((H,W),bool)
for f in ['F027_near_HAND_MATCH_guard.png','F027_far_CLOSED_HAND_JADE_AND_ALPHA0_SEAT_guard.png','F027_actual_blue_cloth_guard.png','F027_fixed_table_box_guard.png']:hard|=np.array(Image.open(G/'masks'/f))>0
# Explicit protect actual original025 proximal skin-collar contribution, not just visible jade.
collar=np.array(Image.open(S/'masks/JOIN_original025_far_proximal_skin_collar_rigid_minus8_plus16.png'))>0;oldcollar=collar&(distance_transform_edt(~jade)<12)
roi=Image.new('L',(W,H));ImageDraw.Draw(roi).polygon([(1045,832),(1118,801),(1155,820),(1148,856),(1095,904),(1040,904)],fill=255);roi=np.array(roi)>0
rgb=a[:,:,:3].astype(float);same_raw=np.all(a==q,axis=2);eligible=roi&w&~hard&~oldcollar&same_raw&(a[:,:,3]>245)&(rgb[:,:,0]>225)&(rgb[:,:,1]>155)&(rgb[:,:,0]>rgb[:,:,1]+20)
# Apply the same bounded G1/B4 material offset to both native light and lower-turn skin planes. Preserve their original luminance/color contrast; only fade near protected boundaries.
soft=np.clip(distance_transform_edt(eligible)/3,0,1);soft[~eligible]=0
b[:,:,1]=np.clip(a[:,:,1].astype(int)+np.rint(soft).astype(int),0,255).astype('uint8');b[:,:,2]=np.clip(a[:,:,2].astype(int)+np.rint(4*soft).astype(int),0,255).astype('uint8')
change=np.any(b!=a,2);assert not (change&(~w|hard|oldcollar)).any();assert np.array_equal(b[:,:,[0,3]],a[:,:,[0,3]])
Image.fromarray(np.rint(soft*255).astype('uint8')).save(O/'masks/ONLY_new_call14_far_LIGHT_AND_TURN_skin_SOFT_G1_B4.png');Image.fromarray((change*255).astype('uint8')).save(O/'masks/ACTUAL_changed_RGB_pixels.png');Image.fromarray((oldcollar*255).astype('uint8')).save(O/'masks/PROTECTED_original025_far_skin_collar.png');shadow=roi&(a[:,:,3]>245)&(rgb[:,:,0]>210)&(rgb[:,:,0]>rgb[:,:,1]+20)&(rgb[:,:,1]<=188);Image.fromarray((shadow*255).astype('uint8')).save(O/'masks/DIAGNOSTIC_actual_lower_turn_dark_material.png')
out=O/'candidates/S08_F027_same_raw_final_color_RGBA.png';Image.fromarray(b).save(out)
col=json.loads((S/'geometry/COLOR_PLANES_DIAGNOSTIC_NOT_CORRECTED.json').read_text());after={}
for name,entry in col['samples'].items():
 if not name.startswith('027'):continue
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(entry['polygon'],fill=255);m=np.array(m)>0;r=b[:,:,:3].astype(float);m&=(b[:,:,3]>245)&(r[:,:,0]>230)&(r[:,:,1]>155)&(r[:,:,0]>r[:,:,1]+20);v=r[m];after[name]={'count':len(v),'before':entry['mean'],'after':v.mean(0).tolist(),'delta_to000_corresponding':(v.mean(0)-np.array(col['samples']['000_'+name[4:]]['mean'])).tolist(),'delta_to025_corresponding':(v.mean(0)-np.array(col['samples']['025_'+name[4:]]['mean'])).tolist()}
report={'status':'FINAL_COLOR_CANDIDATE_PENDING_DUAL_GATE','candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'previous_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_raw_sha256':'d3364d4e471f9259d2eaf79aea70ed69d4d6d33add96a76a0a0d8ebee2e13e17','native_calls_added':0,'changes':'Only newcall14farforearm light AND lower-turn skin share G+0..1 B+0..4. Soft boundary to original025 collar/guard/ink. R andalpha unchanged; no separate shadow lifting.','actual_changed_pixels':int(change.sum()),'soft_nonzero_pixels':int((soft>0).sum()),'G_changed_pixels':int((b[:,:,1]!=a[:,:,1]).sum()),'B_changed_pixels':int((b[:,:,2]!=a[:,:,2]).sum()),'R_changes':int((b[:,:,0]!=a[:,:,0]).sum()),'alpha_changes':int((b[:,:,3]!=a[:,:,3]).sum()),'guard_changes':int((change&hard).sum()),'old025_collar_changes':int((change&oldcollar).sum()),'actual_lower_turn_dark_pixels':int(shadow.sum()),'actual_lower_turn_dark_changes':int((change&shadow).sum()),'note':'Cyan diagnostic polygon includes some brighter transition pixels. Both real material planes receive the SAME channel offset; no independent shadow brightness compensation. Core plane contrast is preserved.','measurements':after}
(O/'geometry/COLOR_BEFORE_AFTER_AND_CHECKS.json').write_text(json.dumps(report,indent=2))
rod=Image.open(G/'inputs/F027_TRUE_LOW_ROD_separate_CONTEXT_LAYER.png');old=Image.open(G/'source_snapshot/S08_F025_grandma_match_box_RGBA.png')
for tag,colr in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),colr),Image.alpha_composite(rod,Image.fromarray(b)))
 for n,bb,z in [('whole_arm',(900,660,1320,990),3),('near_wrist',(910,820,1050,930),6),('jade_wrist',(1080,780,1190,875),7),('upperarm_depth',(930,775,1100,875),5)]:bg.crop(bb).resize(((bb[2]-bb[0])*z,(bb[3]-bb[1])*z),Image.Resampling.NEAREST).convert('RGB').save(O/'qa'/(n+'_'+tag+'.png'))
 bg.crop((570,270,1450,1030)).resize((1100,950),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/('fullbody_'+tag+'.png'))
 oldbg=Image.alpha_composite(Image.new('RGBA',(W,H),colr),old);pair=Image.new('RGB',(1680,700),colr[:3]);pair.paste(oldbg.crop((900,660,1320,990)).resize((840,660)),(0,40));pair.paste(bg.crop((900,660,1320,990)).resize((840,660)),(840,40));dr=ImageDraw.Draw(pair);dr.text((10,10),'LOCKED025',fill=(170,140,70));dr.text((850,10),'027 FINAL COLOR CANDIDATE',fill=(170,140,70));pair.save(O/'qa'/('025_027_compare_'+tag+'.png'))
mask_overlay=np.zeros_like(a);mask_overlay[:,:,0]=30;mask_overlay[:,:,1]=180;mask_overlay[:,:,2]=200;mask_overlay[:,:,3]=np.rint(soft*130).astype('uint8');base=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),Image.fromarray(b));base.alpha_composite(Image.fromarray(mask_overlay));base.crop((1035,795,1165,920)).resize((780,750),Image.Resampling.NEAREST).convert('RGB').save(O/'qa/SOFT_material_mask_overlay.png')
board=Image.new('RGB',(1560,790),(244,242,237));
for idx,ar in enumerate([a,b]):
 im=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),Image.fromarray(ar));board.paste(im.crop((1035,795,1165,920)).resize((780,750),Image.Resampling.NEAREST).convert('RGB'),(780*idx,40))
ImageDraw.Draw(board).text((10,10),'BEFORE - samecall14',fill=(20,30,40));ImageDraw.Draw(board).text((790,10),'AFTER - new light AND turn skin share G1 B4 soft',fill=(20,30,40));board.save(O/'qa/COLOR_before_after.png')
print(json.dumps(report,indent=2))
