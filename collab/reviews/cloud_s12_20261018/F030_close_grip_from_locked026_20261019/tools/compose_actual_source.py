from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
O=Path('collab/reviews/cloud_s12_20261018/F030_close_grip_from_locked026_20261019');M=O.parent/'F026_index_repair_actual_call01_20261019'
raw=Image.open(O/'originals/F030_call01_raw.png').convert('RGBA');base=Image.open(O/'reference/LOCKED_ACTUAL_F026_UNIQUE_MOTHER.png').convert('RGBA');b=np.array(base)
# Entire1254 output board -> expected1024 plate -> native, a single uniform mapping.
s=1024/raw.width/4;offset=792.;coeff=(1/s,0,-offset/s,0,1/s,-offset/s);whole=raw.transform(base.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
# Visible newly drawn3-finger groups and their necessary common roots, one source ownership.
upper=[(651,590),(700,535),(752,482),(812,472),(846,485),(902,536),(949,580),(983,638),(987,675),(956,699),(915,682),(866,671),(818,682),(750,671),(698,657),(662,637)]
lower=[(716,759),(766,750),(826,766),(883,774),(863,798),(849,821),(852,844),(862,864),(791,875),(744,860),(713,840),(706,801)]
mask=Image.new('L',raw.size);d=ImageDraw.Draw(mask);d.polygon(upper,fill=255);d.polygon(lower,fill=255);ra=np.array(raw);sel=np.array(mask)>0;rawFG=np.zeros_like(ra);rawFG[sel]=ra[sel];rawBG=ra.copy();rawBG[sel]=0;assert np.array_equal(np.maximum(rawFG,rawBG),ra)
new=Image.fromarray(rawFG,'RGBA').transform(base.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC);a=np.array(new)
# Derivative only: immutable actual026 source PNG remains byte-for-byte unchanged.
old=np.array(Image.open(O/'geometry/old_open_three_digits_trace_native.png'))>0;back=b.copy();back[old]=0
th=np.array(Image.open(M/'masks/protected_complete_thumb_native.png'))>0;ix=np.array(Image.open(M/'layers/F026_FG_new_drawn_index.png').convert('RGBA'));im=ix[:,:,3]>0
# Source-existing thumb/index over new neighbors gives real occlusion without punching old-AA grey holes.
back[th|im]=0
front=np.zeros_like(b);front[th|im]=b[th|im];com=Image.alpha_composite(Image.fromarray(back,'RGBA'),new);com=Image.alpha_composite(com,Image.fromarray(front,'RGBA'));n=np.array(com)
contactcore=(th|im)&(b[:,:,3]>=128);n[contactcore]=b[contactcore]
edit=old|(a[:,:,3]>0);n[~edit]=b[~edit]
# Full native final partition: BG original rest / new foreground3 + original established index.
fgown=(a[:,:,3]>0)|im;fg=np.zeros_like(n);fg[fgown]=n[fgown];bg=n.copy();bg[fgown]=0
assert not np.any((fg[:,:,3]>0)&(bg[:,:,3]>0));assert np.array_equal(np.maximum(bg,fg),n);assert np.array_equal(n[~edit],b[~edit]);assert np.array_equal(n[contactcore],b[contactcore])
mask.save(O/'masks/raw_new_three_finger_and_root_ownership.png');Image.fromarray(np.uint8(old)*255).save(O/'masks/old026_open_three_digits_ownership.png');Image.fromarray(np.uint8(edit)*255).save(O/'masks/actual_three_digit_root_edit_domain.png');Image.fromarray(np.uint8(contactcore)*255).save(O/'masks/fixed_thumb_index_contact_core.png');Image.fromarray(np.uint8(fgown)*255).save(O/'masks/native_final_foreground_ownership.png')
Image.fromarray(n,'RGBA').save(O/'candidate/F030.png');Image.fromarray(bg,'RGBA').save(O/'layers/F030_BG_static026_palm.png');Image.fromarray(fg,'RGBA').save(O/'layers/F030_FG_actual_three_and_fixed_index.png');new.save(O/'diagnostics/actual_new_three_single_mapping_native.png');whole.save(O/'diagnostics/whole_actual_raw_single_mapping_NATIVE_DIAGNOSTIC.png');Image.fromarray(front,'RGBA').save(O/'diagnostics/fixed026_thumb_index_actual_context.png');Image.fromarray(rawFG,'RGBA').save(O/'layers/raw_actual_new_three_exclusive.png');Image.fromarray(rawBG,'RGBA').save(O/'layers/raw_context_NOT_ADOPTED_exclusive.png')
def crop(im):
 c=im.crop((900,875,1024,995));g=Image.new('RGBA',c.size,'#d7dbdf');g.alpha_composite(c);return g.resize((744,720),Image.Resampling.NEAREST)
a0=crop(base);a1=crop(Image.fromarray(n,'RGBA'));board=Image.new('RGB',(1488,750),'#d7dbdf');board.paste(a0,(0,30));board.paste(a1,(744,30));d=ImageDraw.Draw(board);d.text((8,9),'LOCKED026 NATIVE',fill='black');d.text((752,9),'ACTUAL030 NEW THREE / ONE BOARD MAPPING / NOT CANVAS',fill='black');board.save(O/'diagnostics/02_026_to030_actual_native_hand6x.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();record={'source_raw_SHA256':sha(O/'originals/F030_call01_raw.png'),'unique_static_source026_SHA256':sha(O/'reference/LOCKED_ACTUAL_F026_UNIQUE_MOTHER.png'),'single_whole_raw_to_native_matrix':[[s,0,offset],[0,s,offset]],'no_individual_joint_or_tip_transform':True,'no_reference_projection_pixels_adopted':True,'visible_new3_raw_ownership_polygons':[upper,lower],'candidate_SHA256':sha(O/'candidate/F030.png'),'static_source_immutable':True,'native_exclusive_union_exact':True,'all_RGBA_outside_edit_exact':True,'thumb_index_core_RGBA_exact':True,'old_thumb_index_AA_pixels_genuinely_overlapped_by_new_foreground':int(np.sum((th|im)&(b[:,:,3]>0)&(b[:,:,3]<128)&(a[:,:,3]>0))),'AA_policy':'Unmoved original thumb/index over the actual new neighbors, composited by real depth. No forced preservation of transparent old edge RGBA that would cut grey holes into real new digits. Original contact body/core exact; source geometry not shifted.','new_calls':1,'F034':'CLOSED'};(O/'provenance/single_mapping_and_native_scope.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
