from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes
F=Path(__file__).resolve().parent;Q=F.parent;G=Q/'generation_001';P=Q.parent;PACK=P.parent;OLD=PACK/'continuation_042_054_generation_001';R=np.array(Image.open(G/'raw_original.png').convert('RGBA'));B=np.array(Image.open(G/'F047_scoped_actual_candidate_not_adopted.png').convert('RGBA'));H,W=B.shape[:2];yy,xx=np.indices((H,W));factor=7.2;rh,rw=R.shape[:2];ry,rx=np.indices((rh,rw));masterx=840+rx/factor;mastery=260+ry/factor
# Semantic isolation at original resolution: the upper human's alpha interval.
# The lower rod is separated by true raw transparent air, so it is not included.
mask=np.array(Image.open(P/'B047_continuous_palm_target/inputs/03_continuous_palm_wrist_jade_only_white.png').convert('L'))>127;lm=Image.fromarray(np.uint8(mask[260:420,840:1030])*255).resize((1368,1152),Image.Resampling.NEAREST);rm=np.array(lm)[:rh,:rw]>0;r,g,b=R[:,:,:3].astype(float).transpose(2,0,1);skin=(R[:,:,3]>20)&(r>150)&(g>85)&(b>g*.67)&(r>g+9);jade=(R[:,:,3]>20)&(g>r*1.05)&(g>b*1.04);eligible=(R[:,:,3]>8)&rm;selected=np.zeros((rh,rw),bool)
for x in range(max(0,int((915-840)*factor)),min(rw,int((1022-840)*factor))):
 ys=np.flatnonzero(eligible[:,x]);pieces=np.split(ys,np.where(np.diff(ys)>1)[0]+1)
 for piece in pieces:
  if len(piece) and np.any((skin|jade)[piece,x]):
   selected[max(0,int(piece[0])-2):min(rh,int(piece[-1])+3),x]=True;break
selected=binary_dilation(selected,iterations=2)&rm&(R[:,:,3]>0);handraw=R.copy();handraw[:,:,3][~selected]=0;canvas=Image.new('RGBA',(1368,1152));canvas.alpha_composite(Image.fromarray(handraw));human=np.zeros_like(B);human[260:420,840:1030]=np.array(canvas.resize((190,160),Image.Resampling.LANCZOS));Image.fromarray(human).save(F/'unchanged_native_upper_hand_layer.png')
# Exact same archived four-pixel rigid props, never shift a finger or a rod axis.
axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];prop=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(prop);domain=np.zeros((H,W),bool)
for role in ['C_N','C_B']:
 q=axes[role];m=q['slope'];c=q['intercept'];start=q['shaft_tip_master_px'];end=[952,m*952+c];pts=[tuple(v*4 for v in start),tuple(v*4 for v in end)];d.line(pts,fill='#675034',width=16);d.line(pts,fill='#b28b52',width=10);domain|=(xx>=896)&(xx<=957)&(np.abs(yy-m*xx-c)<7)
props=np.array(prop.resize((W,H),Image.Resampling.LANCZOS));patch=np.array(Image.alpha_composite(Image.fromarray(props),Image.fromarray(human)));out=B.copy();out[domain]=patch[domain]
# Keep every originally visible bare-right-hand pixel in front of its rod.
br,bg,bb=B[:,:,:3].astype(float).transpose(2,0,1);right_core=(B[:,:,3]>60)&(br>150)&(bg>85)&(bb>bg*.67)&(br>bg+9)&(xx<918)&(yy>326)&(yy<377);right=(B[:,:,3]>0)&binary_dilation(binary_fill_holes(right_core),iterations=2)&(xx<918)&(yy>326)&(yy<377);out[right]=B[right]
Image.fromarray(out).save(F/'F047_original_rods_restored_candidate.png');gray=Image.new('RGBA',(W,H),'#bdc1c4');gray.alpha_composite(Image.fromarray(out));gray.convert('RGB').save(F/'actual_full_gray.jpg',quality=96);crop=gray.crop((840,260,1030,420)).convert('RGB');crop.save(F/'actual_contacts_1x.png');crop.resize((760,640),Image.Resampling.NEAREST).save(F/'actual_contacts_4x.png');change=np.any(B!=out,2);assert not np.any(change&~domain);assert np.array_equal(B[:,:835],out[:,:835]);assert np.array_equal(B[374:460,1068:1176],out[374:460,1068:1176]);(F/'status.json').write_text(json.dumps({'status':'ZERO_CALL_ORIGINAL_RODS_RESTORED_FOR_ASTRA_FINAL_CONTACT_REVIEW','image_calls':0,'source_generation_commit':'6dd5721764bd890ab6564c41a75e99907569b9a2','source_native_hand_raw_sha256':hashlib.sha256((G/'raw_original.png').read_bytes()).hexdigest(),'human_layer':'same original raw pixels, same uniform inverse transform; only exposed prop isolation, no hand transform','CB_original_slope':axes['C_B']['slope'],'CB_original_intercept':axes['C_B']['intercept'],'CB_true_entity_width_px':4,'CB_fixed_tail_x':952,'CB_fixed_tail_y':axes['C_B']['slope']*952+axes['C_B']['intercept'],'CN_original_layer_width_px':4,'fixed_R_visible_pixels_unchanged':True,'all_changes_inside_prop_restore_corridor':True,'new_calls':0,'adopted':False,'no_048_053_054_propagation':True},ensure_ascii=False,indent=2)+'\n');print('zero-call restored CB width4 to x952; CN archived layer restored; raw hand not transformed')
