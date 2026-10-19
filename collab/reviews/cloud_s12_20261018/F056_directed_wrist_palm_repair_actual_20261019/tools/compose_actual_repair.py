from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import label,binary_dilation
R=Path(__file__).resolve().parents[5];P=R/'collab/reviews/cloud_s12_20261018';D=P/'F056_directed_wrist_palm_repair_actual_20261019';M=P/'F048_F052_actual_20261019/F052';BAD=P/'F056_actual_from_locked052_20261019';G=json.loads((D/'geometry/registration_and_full_wrist_hand_target.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=np.array(Image.open(M/'candidate/F052.png').convert('RGBA'));raw=Image.open(D/'originals/F056_directed_repair_call01_raw.png').convert('RGBA');ra=np.array(raw);bad=Image.open(BAD/'originals/F056_call01_raw.png').convert('RGBA')
def coeff(A,t):
 iv=np.linalg.inv(A);return tuple(np.c_[iv,-iv@t].ravel())
# Only ONE complete repair-patch similarity. Landmarks are visible estimates, not hidden-bone measurements.
Wr=np.array([302.,520.]);Tr=np.array([985.,442.]);W=np.array(G['target_true_bare_wrist_entry_W']);T=np.array(G['true_thumb_underside_T_native']);rod=np.array(G['G_native']);normal=(T-rod)/np.linalg.norm(T-rod);Tsurface=T-.35*normal
v0=Tr-Wr;v1=Tsurface-W;c=(v1[0]+1j*v1[1])/(v0[0]+1j*v0[1]);A=np.array([[c.real,-c.imag],[c.imag,c.real]]);t=W-A@Wr
lab,n=label(ra[:,:,3]>=8);sizes=np.bincount(lab.ravel());sizes[0]=0;body=lab==sizes.argmax();own=binary_dilation(body,iterations=2)&(ra[:,:,3]>0);selected=ra.copy();selected[~own]=0;repair=np.array(Image.fromarray(selected,'RGBA').transform((1024,1536),Image.Transform.AFFINE,coeff(A,t),Image.Resampling.BICUBIC))
# Failed056 salvage shoulder/sleeve/elbow/main forearm: fixed entire-board matrix, no jade/hand pixels.
Ab=np.array(G['failed_entire_board_one_similarity']);sm=Image.new('L',bad.size);ImageDraw.Draw(sm).polygon([(130,120),(270,90),(390,180),(470,310),(580,390),(650,480),(1040,550),(1040,730),(750,730),(550,670),(420,580),(310,615),(210,480),(150,320)],fill=255);yy,xx=np.mgrid[:bad.height,:bad.width];take=(np.array(sm)>0)&(xx<=1020);sal=np.array(bad);sal[~take]=0;sal=np.array(Image.fromarray(sal,'RGBA').transform((1024,1536),Image.Transform.AFFINE,coeff(Ab[:,:2],Ab[:,2]),Image.Resampling.BICUBIC))
far=np.array(Image.open(M/'masks/native_original048_far_arm_protected.png'))>0;old=np.array(Image.open(M/'masks/native_actual_new_near_arm_adoption.png'))>0;y,x=np.mgrid[:1536,:1024];J=np.array(G['target_J_forearm_entry']);u=(W-J)/np.linalg.norm(W-J);along=(x-J[0])*u[0]+(y-J[1])*u[1]
# The only blend is a 14-native-pixel distal forearm strip at J. Hand RGBA remains actual imagegen pixels.
w=np.clip((along+6)/14,0,1);sal[far]=0;sal[along>14]=0;repair[along < -6]=0
# Blend real source colours only in the small join; retain max source alpha to avoid a translucent seam.
both=(sal[:,:,3]>0)&(repair[:,:,3]>0)&(along>=-6)&(along<=14)
aa=repair[:,:,3].astype(float)/255;bb=sal[:,:,3].astype(float)/255;wa=w*aa;wb=(1-w)*bb;den=wa+wb
mixed=repair.copy();mixed[both,:3]=np.uint8(np.rint((repair[both,:3]*wa[both,None]+sal[both,:3]*wb[both,None])/den[both,None]));mixed[both,3]=np.maximum(repair[both,3],sal[both,3]);sal[both]=0;repair=mixed
keepblue=b[:,:,2].astype(int)>=b[:,:,0].astype(int)-5;static=b.copy();static[old&~keepblue&~far]=0
out=np.array(Image.alpha_composite(Image.alpha_composite(Image.fromarray(static,'RGBA'),Image.fromarray(sal,'RGBA')),Image.fromarray(repair,'RGBA')));edit=(old&~far)|(sal[:,:,3]>0)|(repair[:,:,3]>0);out[~edit]=b[~edit];out[far]=b[far]
# One exclusive BG/FG partition: protected entire left foreground remains byte exact.
left=np.array(Image.open(M/'layers/F052_FG_original_left_fingers.png'));leftown=left[:,:,3]>0
# Real front index middle/distal surfaces in raw source, not a surrogate circle or drawn finger.
fm=Image.new('L',raw.size);ImageDraw.Draw(fm).polygon([(1014,346),(1100,316),(1150,352),(1132,470),(1080,519),(1022,510),(1000,457)],fill=255);front=np.array(fm.transform((1024,1536),Image.Transform.AFFINE,coeff(A,t),Image.Resampling.NEAREST))>0;front&=repair[:,:,3]>0;fgown=leftown|front;fg=np.zeros_like(out);fg[fgown]=out[fgown];bg=out.copy();bg[fgown]=0
assert np.array_equal(np.maximum(bg,fg),out);assert not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0));assert np.array_equal(out[~edit],b[~edit]);assert np.array_equal(out[far],b[far]);assert np.array_equal(fg[leftown],left[leftown])
for name,a in [('candidate/F056.png',out),('layers/F056_BG_person.png',bg),('layers/F056_FG_true_front_fingers.png',fg),('layers/whole_actual_repair_registered.png',repair),('layers/failed056_salvage_registered.png',sal)]:Image.fromarray(a,'RGBA').save(D/name)
for name,a in [('native_exact_edit_union.png',edit),('native_original052_far_arm_protected.png',far),('native_true_front_index_ownership.png',front),('raw_complete_patch_ownership.png',own)]:Image.fromarray(np.uint8(a)*255).save(D/'masks'/name)
q={'status':'ACTUAL056_DIRECTED_REPAIR_SINGLE_MAP_PENDING_REVIEW','mother052_SHA256':sha(M/'candidate/F052.png'),'raw_repair_SHA256':sha(D/'originals/F056_directed_repair_call01_raw.png'),'single_complete_repair_similarity':np.c_[A,t].tolist(),'scale':float(abs(c)),'rotation_degrees':float(np.angle(c,deg=True)),'source_visible_W_estimate':Wr.tolist(),'source_visible_thumb_contact_surface_estimate':Tr.tolist(),'target_bare_wrist':W.tolist(),'target_thumb_contact_surface':Tsurface.tolist(),'failed_entire_board_matrix_fixed':Ab.tolist(),'forearm_join_J':J.tolist(),'forearm_join_width_native':14,'per_finger_or_joint_transforms':0,'reference_pixels_adopted':0,'outside_edit_union_RGBA_exact':True,'protected_entire_far_arm_RGBA_exact':True,'protected_original_left_foreground_RGBA_exact':True,'exclusive_BG_FG_union_RGBA_exact':True,'candidate_SHA256':sha(D/'candidate/F056.png'),'known_raw_shape_risk':'Generated diagonal heel-of-palm skin ridge/strip and pointed heel remnant persist despite explicit redraw prompt. Retained for truthful review; not digitally cut or repainted. No second generation authorized.','near_sleeve_material':'Original blue source join artifacts remain diagnostic; no broad torso or body repaint.'};(D/'qa/single_patch_and_native_scope.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'matrix':q['single_complete_repair_similarity'],'candidate_SHA256':q['candidate_SHA256'],'no_second_call':True}))
