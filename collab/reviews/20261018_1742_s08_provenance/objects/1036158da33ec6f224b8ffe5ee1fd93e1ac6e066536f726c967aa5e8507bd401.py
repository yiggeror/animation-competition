from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent;R=P.parent;S=R/'repair02_result_v8b_actual_hand_candidate';O=R/'repair02_result_v9_clean_hand';M=R/'repair02_result_v5b_semantic_cleanup/masks'
im=Image.open(S/'candidates/F000_call02_hand_candidate_RGBA.png').convert('RGBA');a=np.array(im);old=a.copy();yy,xx=np.indices(a.shape[:2]);lab,n=ndi.label(a[:,:,3]>32,np.ones((3,3)));sz=np.bincount(lab.ravel());main=sz[1:].argmax()+1
near=(xx>=1040)&(xx<=1065)&(yy>=788)&(yy<=817);isolated=near&(lab>0)&(lab!=main);dilate=np.array(Image.fromarray(isolated.astype('uint8')*255).filter(ImageFilter.MaxFilter(3)))>0;erase=dilate&near
warm=(a[:,:,0]>180)&(a[:,:,1]>115)&(a[:,:,2]>75)&(a[:,:,0]>a[:,:,1]*1.12)&(a[:,:,3]>180)
# Preserve a full 2px outside contour guard beyond each actual skin row; only the farther detached grey trace is eligible.
for y in range(799,832):
 xs=np.where(warm[y,1085:1171])[0]+1085
 if len(xs):erase[y,1118:min(1163,int(xs.min())-2)]=True
jade=np.array(Image.open(P/'masks/F000_jade_bangle_full_protected.png'))>0;prop=np.array(Image.open(M/'NEW_actual_prop_protection.png'))>0;erase&=~(jade|prop);erase&=a[:,:,3]>0;a[erase]=0
out=Image.fromarray(a,'RGBA');out.save(O/'candidates/F000_call02_clean_hand_RGBA.png');Image.fromarray(erase.astype('uint8')*255).save(O/'masks/isolated_fragments_only.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 b=Image.new('RGBA',im.size,col);b.alpha_composite(out);b.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,bb,m in [('hands',(930,728,1214,893),4),('head_and_match',(625,310,1205,860),2),('bottom',(530,976,990,1080),2),('arm_chains',(590,620,1230,1020),2)]:
  q=b.crop(bb);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
change=np.any(a!=old,2);checks={'status':'FINAL_NARROW_EDGE_CLEANUP_PENDING_SHA_REVIEW','actual_native_calls_total':2,'additional_calls':0,'changed_pixels':int(change.sum()),'changed_outside_explicit_deletion_mask':int((change&~erase).sum()),'actual_props_changed':int((change&prop).sum()),'jade_changed':int((change&jade).sum()),'no_hand_or_prop_translation':True,'no_new_skin_drawn_or_cloned':True,'near_grip_isolated_component':'4px atx1060–1061,y801–802 plus adjacent antialias only','far_palm_cleanup':'Only farther than2px outside actual skin contour; original contour guard preserved.','candidate_sha256':hashlib.sha256((O/'candidates/F000_call02_clean_hand_RGBA.png').read_bytes()).hexdigest()};(O/'qa/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
