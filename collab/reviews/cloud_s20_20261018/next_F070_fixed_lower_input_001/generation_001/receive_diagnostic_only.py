"""Identity placement diagnostic; no pose repair, scaling, or retry."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_opening,median_filter,label

F=Path(__file__).resolve().parent;P=F.parent;PACK=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=F/'raw_original.png';R=np.array(Image.open(raw).convert('RGBA'))
source=PACK/'F067_near_leg_support_root_zero_call_001/F067_near_support_and_root_closed_candidate.png'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2]
assert R.shape==A.shape and sha(source)=='80a84871aaaa4eddd621e457fa4dae0b95494332d788119ae650ff85356e1dd8'
lowerfile=P/'fixed_complete_lower_067_roots_legs_shoes.png'
lower=np.array(Image.open(lowerfile).convert('RGBA'))
assert sha(lowerfile)==json.loads((P/'INPUT_MANIFEST.json').read_text())['fixed_lower_sha256']
yy,xx=np.indices((H,W));r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)

# Trace this original's complete NEW skirt hem; never apply the preparation
# mask as a body cut. The whole generated lower body is excluded at its actual
# garment occlusion. No knee/ankle/foot cuts and no human transformation.
yellow=(R[:,:,3]>180)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>500)&(yy<680)
core=binary_opening(yellow,iterations=2)
hem=np.full(W,np.nan)
for x in range(620,1030):
    ys=np.flatnonzero(core[:,x])
    if not len(ys):continue
    last=int(ys.max())
    # Reach the actual colored hem after the core's two-pixel inset.
    candidates=np.flatnonzero(yellow[last:min(last+9,H),x])
    if len(candidates):last+=int(candidates.max())
    q=np.arange(last,min(last+5,H));edge=int(q[np.argmin(r[q,x]+g[q,x]+b[q,x])])
    hem[x]=edge
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]);hem=median_filter(hem,size=3)
keep=(R[:,:,3]>0)&~((yy>500)&(yy>hem[xx]))
components,count=label(keep);sizes=np.bincount(components.ravel());main=int(np.argmax(sizes[1:])+1)
detached_noise=int(np.count_nonzero(keep&(components!=main)));keep=components==main
native=np.zeros_like(R);native[keep]=R[keep]
Image.fromarray(native).save(F/'native_new_complete_upper_arms_whole_skirt_T_rods.png')
Image.fromarray(np.uint8(keep)*255).save(F/'actual_native_new_upper_whole_skirt_selection.png')

# Fixed scene C rods and frozen grandma, then unchanged independent complete
# 067 lower, then the complete new upper at identity. Deliberately do not move
# the drifting upper or stretch roots to disguise the bad request result.
axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
for role in ['C_N','C_B']:
    q=axes[role];pts=[tuple(v*4 for v in q['shaft_tip_master_px']),tuple(v*4 for v in [952,q['slope']*952+q['intercept']])]
    d.line(pts,fill='#675034',width=16);d.line(pts,fill='#b28b52',width=10)
G=A.copy();G[:,:835]=0
fixedprops=np.array(props.resize((W,H),Image.Resampling.LANCZOS));fixedprops[:,835:]=0
base=Image.alpha_composite(Image.fromarray(fixedprops),Image.fromarray(G))
base=Image.alpha_composite(base,Image.fromarray(lower));out=Image.alpha_composite(base,Image.fromarray(native));B=np.array(out)
visible=np.array(Image.open(P/'source067_actual_visible_lower_reference_mask.png').convert('L'))>0
fixedmask=np.array(Image.open(P/'actual_retained_visible_whole_legs_and_shoes_mask.png').convert('L'))>0
# All actual grandma human pixels begin right of x860. x835..859 contains
# only scene C shafts, which the drifting new sleeve naturally occludes.
grandma=(xx>=860)&(A[:,:,3]>0)
# Restore the source's semantic fixed-leg antialias pixels directly. This is
# one complete retained lower domain, not a horizontal knee/ankle splice.
B[fixedmask&(native[:,:,3]==0)]=A[fixedmask&(native[:,:,3]==0)]
assert not np.any(grandma&(native[:,:,3]>0))
B[grandma]=A[grandma];out=Image.fromarray(B)
final=F/'F070_native_upper_fixed_full_lower_DIAGNOSTIC_NOT_ADOPTED.png';out.save(final)
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(out);bg.convert('RGB').save(F/'actual_full_fixed_lower_gray_DIAGNOSTIC.jpg',quality=96)
for name,box,scale in [('contacts',(320,230,880,470),3),('under_hem',(560,570,1030,760),3),('support',(480,800,795,935),2)]:
    crop=bg.crop(box).convert('RGB');crop.save(F/f'actual_{name}_1x.png');crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST).save(F/f'actual_{name}_{scale}x.png')
rawbg=Image.new('RGBA',(W,H),'#bdc1c4');rawbg.alpha_composite(Image.fromarray(R))
rawbg.crop((620,550,1040,760)).convert('RGB').save(F/'raw_actual_new_skirt_hem_1x.png')

diff=np.any(B!=A,axis=2)
white=np.array(Image.open(P/'inputs/04_new_upper_whole_skirt_white_full_legs_black_mask.png').convert('L'))>127
gated_target=np.array(Image.open(P/'inputs/01_unique_complete_F070_fixed_lower_target_REVIEW_ONLY.png').convert('RGBA'))
raw_new_black=(R[:,:,3]>0)&~white
visible_lower_unchanged=int(np.count_nonzero(np.any(lower[visible]!=A[visible],axis=1)))
visible_lower_output_changes=int(np.count_nonzero(diff&fixedmask))
grandma_changes=int(np.count_nonzero(diff&grandma))
assert np.array_equal(native[keep],R[keep]) and visible_lower_unchanged==0
assert visible_lower_output_changes==0 and grandma_changes==0
report={
 'status':'F070_ONE_RAW_NATIVE_PLACEMENT_FAILED_FIXED_LOWER_REJOIN_DIAGNOSTIC_ASTRA_GATE_PENDING',
 'new_image_calls':1,'raw_outputs':1,'retries':0,'approved_input_commit':'a877e887929bf4445547c553c27ff1399c4ea63d',
 'raw_sha256':sha(raw),'raw_size':[W,H],'final_png':final.name,'final_png_sha256':sha(final),
 'native_human_transform':'identity; no resize, translation, warp, knee/ankle splice, or generated shoe used',
 'new_skirt_extraction':'original new natural hem; not clipped to the construction mask or old skirt',
 'isolated_alpha_noise_outside_native_connected_child_removed_pixels':detached_noise,
 'new_upper_selected_RGBA_exact_original':True,
 'fixed_complete_lower_source':str(lowerfile),'fixed_complete_lower_source_sha256':sha(lowerfile),
 'fixed_complete_lower_layer_RGBA_changes':0,
 'source067_visible_lower_reference_RGBA_changes':visible_lower_unchanged,
 'actual_fixed_visible_full_legs_shoes_output_RGBA_changes':visible_lower_output_changes,
 'actual_grandma_foreground_output_RGBA_changes':grandma_changes,
 'grandma_validation_domain':'all source foreground x860+; actual grandma complete; x835..859 is scene C shafts, not grandma human',
 'raw_foreground_pixels_outside_input_white':int(raw_new_black.sum()),
 'final_pixels_changed_outside_white':int((np.any(B!=gated_target,axis=2)&~white).sum()),
 'black_domain_comparison_reference':'actual approved complete input target; black domain failures remain reported, not forced through',
 'visual_blocker':'原件整体人物明显放大、右上漂移；完整新裙摆与已锁067腿根失配，诊断接回出现露根/断口。双前臂连续，X仍在掌前；本图不能采用。',
 'adopted':False,'new_exposure_frozen':False,'further_states_prepared_or_called':False
}
(F/'receipt_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
