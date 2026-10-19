from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_actual_call01_20261019');I=O.parent/'F026_index_repair_inputs_20261019';S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019'
raw=Image.open(O/'originals/F026_local_index_call01_raw.png').convert('RGBA');base=Image.open(I/'reference/LOCKED_F022_STATIC_BASE.png').convert('RGBA');b=np.array(base)
# One uniform similarity for the whole raw board, including index and root; never move a detached tip.
r0=np.array([869.,675.]);r1=np.array([938.,854.]);n0=np.array([960.,923.]);n1=np.array([976.52,963.83]);vr=r1-r0;vn=n1-n0;s=np.linalg.norm(vn)/np.linalg.norm(vr);ang=np.arctan2(vn[1],vn[0])-np.arctan2(vr[1],vr[0]);M=s*np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]]);t=n0-M@r0;inv=np.linalg.inv(M);tt=-inv@t;coeff=tuple(inv[0])+(tt[0],)+tuple(inv[1])+(tt[1],)
rawmask=Image.new('L',raw.size);poly=[(826,640),(872,626),(938,652),(988,699),(1028,740),(1034,820),(996,853),(968,880),(941,894),(916,892),(893,869),(891,840),(909,811),(943,793),(948,765),(931,738),(900,719),(855,708),(814,692),(800,673)];ImageDraw.Draw(rawmask).polygon(poly,fill=255)
r=np.array(raw);r[:,:,3]=np.uint8(r[:,:,3].astype(float)*np.array(rawmask)/255);rawindex=Image.fromarray(r,'RGBA');mapped=rawindex.transform(base.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
whole=raw.transform(base.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
# Restrict newly drawn palm context to the necessary root transition; entire visible finger kept.
rootdomain=Image.new('L',base.size);ImageDraw.Draw(rootdomain).polygon([(953,918),(965,915),(979,924),(1003,937),(1005,982),(963,984),(948,937)],fill=255)
m=np.array(mapped);allowed=np.array(rootdomain)>0;m[~allowed]=0
# Existing entire thumb, including ink/AA, is protected byte-for-byte.
th=np.array(Image.open(S/'masks/thumb_alpha_native.png').convert('RGBA'))[:,:,3]>0;m[th]=0
old=np.array(Image.open(I/'geometry/old_index_trace_native.png'))>0;old[th]=False
root=Image.new('L',base.size);ImageDraw.Draw(root).polygon([(955,920),(963,917),(973,923),(975,929),(961,931),(954,927)],fill=255)
protected_existing=(b[:,:,3]>0)&~(old|(np.array(root)>0));protected_existing|=th
m[protected_existing]=0
new=Image.fromarray(m,'RGBA')
Image.fromarray(np.uint8(protected_existing)*255).save(O/'masks/protected_existing_palm_other_digits_body_RGBA.png')
back=b.copy();back[old]=0
com=np.array(Image.alpha_composite(Image.fromarray(back,'RGBA'),new));edit=old|(m[:,:,3]>0);edit[th]=False;com[~edit]=b[~edit];com[th]=b[th]
# Mutually exclusive native final layers, not overlapping alpha composites: exact RGBA union.
fgmask=(m[:,:,3]>0)&~th;fg=np.zeros_like(com);fg[fgmask]=com[fgmask];bg=com.copy();bg[fgmask]=0
assert not np.any((fg[:,:,3]>0)&(bg[:,:,3]>0));assert np.array_equal(np.maximum(fg,bg),com);assert np.array_equal(com[~edit],b[~edit]);assert np.array_equal(com[th],b[th]);assert np.array_equal(com[protected_existing],b[protected_existing])
for fn,im in [('raw_index_actual_ownership.png',rawmask),('whole_raw_single_similarity_NATIVE_DIAGNOSTIC.png',whole),('new_drawn_whole_index_single_similarity.png',new)]: im.save(O/'diagnostics'/fn)
Image.fromarray(np.uint8(old)*255).save(O/'masks/old022_entire_index_ownership.png');Image.fromarray(np.uint8(edit)*255).save(O/'masks/actual_whole_index_root_edit_domain.png');Image.fromarray(np.uint8(th)*255).save(O/'masks/protected_complete_thumb_native.png');Image.fromarray(np.uint8(fgmask)*255).save(O/'masks/foreground_actual_index_ownership.png')
Image.fromarray(com,'RGBA').save(O/'candidate/F026.png');Image.fromarray(bg,'RGBA').save(O/'layers/F026_BG_locked022_palm_rear_digits.png');Image.fromarray(fg,'RGBA').save(O/'layers/F026_FG_new_drawn_index.png')
# Diagnostic native crops, clearly distinguished from later real Canvas output.
def bgc(im,crop,scale=6):
 x=im.crop(crop);z=Image.new('RGBA',x.size,'#d7dbdf');z.alpha_composite(x);return z.resize((x.width*scale,x.height*scale),Image.Resampling.NEAREST)
prev=bgc(base,(900,875,1024,990));cur=bgc(Image.fromarray(com,'RGBA'),(900,875,1024,990));board=Image.new('RGB',(prev.width+cur.width,prev.height+30),'#d7dbdf');board.paste(prev,(0,30));board.paste(cur,(prev.width,30));d=ImageDraw.Draw(board);d.text((10,8),'LOCKED022 NATIVE',fill='black');d.text((prev.width+10,8),'ACTUAL DRAWN026 + ONE WHOLE SIMILARITY / NOT CANVAS',fill='black');board.save(O/'diagnostics/02_locked022_to_actual026_native_hand6x.png')
props=Image.open(S/'actual_scene/F022_code_props_actual_layer.png').convert('RGBA');bgn=Image.fromarray(bg,'RGBA').transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC);fgn=Image.fromarray(fg,'RGBA').transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC);tmp=Image.new('RGBA',(1920,1080),'#d7dbdf');tmp.alpha_composite(bgn);tmp.alpha_composite(props);tmp.alpha_composite(fgn);tmp.crop((900,710,1010,830)).resize((770,840),Image.Resampling.NEAREST).save(O/'diagnostics/03_native_registration_frozen_props_NOT_CANVAS.png')
record={'status':'SINGLE_SIMILARITY_ACTUAL_DRAWING_CANDIDATE_NOT_YET_CANVAS','raw_size':list(raw.size),'whole_raw_to_native_matrix':[list(M[0])+[float(t[0])],list(M[1])+[float(t[1])]],'uniform_scale':float(s),'rotation_degrees':float(np.degrees(ang)),'actual_raw_anchors':{'visible_index_root_estimate':r0.tolist(),'whole_pad_volume_centre_estimate':r1.tolist()},'native_anchor_targets':{'actual022_root_estimate':n0.tolist(),'under_upper_rod_pad_volume_target':n1.tolist()},'scope':'One mapping applied to whole source drawing and whole index/root. No per-joint or tip motion, no generated reference pixels, no copied whole raw palm/thumb/body, no moved rods. Approximate joints are visual estimates, not certified hidden-bone measurements.','source_index_ownership_polygon':poly,'protected_complete_thumb_RGBA_exact':True,'outside_actual_index_root_edit_RGBA_exact':True,'exclusive_layer_union_RGBA_exact':True,'new_calls':1,'F030_calls':0}
(O/'provenance/single_mapping_and_native_scope.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
