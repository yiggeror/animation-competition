"""Same native F012: restore only the approved small static placket tip's face lighting."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_erosion,binary_dilation,distance_transform_edt,gaussian_filter,maximum_filter,minimum_filter
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;BASE=P/'same_raw_fix_20261019'
for p in ['candidate','masks','qa','provenance','scene','actual_scene']:(O/p).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=BASE/'candidate/F012.png';mother=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png';assert sha(src)=='103ed4fb52c64b370560456ff0dde5a0820596ecfed9e28daee0f026aef7b4ff'
a=np.array(Image.open(src));m=np.array(Image.open(mother));rgb=a[:,:,:3].astype(float);out=a.copy()
def poly(v):
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(v,fill=255);return np.array(im)>0
# Physical cloth outline; rectangles are only guards, never the color selection.
domain_points=[(474,940),(497,940),(499,960),(488,970),(494,977),(491,982),(509,997),(534,1016),(534,1021),(506,1051),(489,1029),(477,1011),(466,997),(462,990),(466,978),(473,963),(476,951)]
lit_points=[(474,940),(497,940),(499,960),(488,970),(470,980),(466,977),(473,963),(476,951)]
domain=poly(domain_points);lit=poly(lit_points)&domain;shade=domain&~lit
r,g,b=rgb.transpose(2,0,1);cloth=((b>r+15)&(b>g+8)&(g>r+6)&(r>60)&(b>115))|((r>135)&(g>145)&(b>155)&(abs(b-r)<65))
# Keep ink/fold creases verbatim; do not protect the bright flower FILL that must regain its shadow.
lo=minimum_filter(rgb,size=(3,3,1));hi=maximum_filter(rgb,size=(3,3,1))
ink=(np.max(rgb,2)<100)|((np.max(hi-lo,2)>65)&(np.min(rgb,2)<80))
protect=binary_dilation(ink,iterations=1)
editable=domain&cloth&~protect&(a[:,:,3]>=128)
feather=np.clip(distance_transform_edt(editable)/2,0,1);feather[~editable]=0
# Fit physical pigment anchors independently within the SAME static face on the locked mother.
# Lit face uses a small additive shift to preserve its gradients exactly; shaded face uses a positive
# per-channel affine transform to restore BOTH blue base and shadowed flowers without moving pixels.
cal={};transforms={};anchor_masks={}
for name,face in [('lit',lit),('shade',shade)]:
 vals=[]
 for label,ar in [('source',a),('mother',m)]:
  x=ar[:,:,:3].astype(float);rr,gg,bb=x.transpose(2,0,1);core=binary_erosion(face,iterations=1)&(ar[:,:,3]>=128)&(np.min(x,2)>60)
  blue=core&(bb>rr+20)&(gg>rr+8)&(bb>gg+8)&(bb>120)&(rr<180)
  flowers=core&(rr>165)&(gg>175)&(bb>185)&(bb-rr<55)&(np.max(x,2)-np.min(x,2)<60)
  assert blue.sum()>300
  anchor_masks[f'{name}_{label}_blue']=blue;anchor_masks[f'{name}_{label}_flowers']=flowers
  vals.append((ar[blue,:3].mean(0),ar[flowers,:3].mean(0),int(blue.sum()),int(flowers.sum())))
 # The fold is static: use matched pigment interiors rather than differently thresholded
 # flower areas. Independent threshold areas overcount the newly bright flower's fringe.
 matched_blue=binary_erosion(anchor_masks[f'{name}_source_blue']&anchor_masks[f'{name}_mother_blue'],iterations=1)
 matched_flower=binary_erosion(anchor_masks[f'{name}_source_flowers']&anchor_masks[f'{name}_mother_flowers'],iterations=1)
 anchor_masks[f'{name}_matched_blue_core']=matched_blue
 anchor_masks[f'{name}_matched_flower_core']=matched_flower
 blue0=a[matched_blue,:3].mean(0);blue1=m[matched_blue,:3].mean(0)
 if name=='lit':gain=np.ones(3);bias=blue1-blue0
 else:
  assert matched_flower.sum()>150
  flower0=a[matched_flower,:3].mean(0);flower1=m[matched_flower,:3].mean(0)
  gain=(flower1-blue1)/(flower0-blue0);bias=blue1-gain*blue0
  assert np.all(gain>.65)&np.all(gain<1.0)
 transforms[name]=(gain,bias);cal[name]={'source_blue_mean_RGB':vals[0][0].tolist(),'mother_blue_mean_RGB':vals[1][0].tolist(),'source_flower_mean_RGB':vals[0][1].tolist(),'mother_flower_mean_RGB':vals[1][1].tolist(),'source_blue_pixels':vals[0][2],'mother_blue_pixels':vals[1][2],'source_flower_pixels':vals[0][3],'mother_flower_pixels':vals[1][3],'matched_blue_core_pixels':int(matched_blue.sum()),'matched_flower_core_pixels':int(matched_flower.sum()),'positive_RGB_gain':gain.tolist(),'RGB_bias':bias.tolist(),'note':'Static matching blue pigment cores calibrate additive tone; lit flower overlap is too small to fit.' if name=='lit' else 'Static matching blue and flower cores calibrate positive gain; independent threshold area bias is recorded separately.'}
blend_lit=gaussian_filter(lit.astype(float),2.0);blend_shade=gaussian_filter(shade.astype(float),2.0);den=blend_lit+blend_shade;wl=np.divide(blend_lit,den,out=np.zeros_like(den),where=den>1e-9)
gain=wl[:,:,None]*transforms['lit'][0]+(1-wl[:,:,None])*transforms['shade'][0];bias=wl[:,:,None]*transforms['lit'][1]+(1-wl[:,:,None])*transforms['shade'][1]
corrected=rgb*gain+bias
out[:,:,:3]=np.clip(np.rint(rgb+(corrected-rgb)*feather[:,:,None]),0,255).astype(np.uint8)
change=np.any(out[:,:,:3]!=a[:,:,:3],2)
assert np.array_equal(out[:,:,3],a[:,:,3]);assert not np.any(change&~domain);assert not np.any(change&protect);assert not np.any(change[:940])
# All actual skin/hair/pants material selections from the prior actual-native review remain exact.
for mat in ['skin','hair','trousers']:
 mask=np.array(Image.open(P/f'qa/masks/raw_F012_{mat}.png'))>0
 assert not np.any(change&mask),(mat,int(np.count_nonzero(change&mask)))
Image.fromarray(out).save(O/'candidate/F012.png')
for name,mask in {'domain_complete_semantic_tip':domain,'lit_face':lit,'shade_face':shade,'protected_ink_fold_creases':protect,'RGB_changed':change,**anchor_masks}.items():Image.fromarray(mask.astype(np.uint8)*255).save(O/f'masks/{name}.png')
Image.fromarray(np.rint(feather*255).astype(np.uint8)).save(O/'masks/RGB_edit_weight.png')
measure={}
for name,face in [('lit',lit),('shade',shade)]:
 means=[]
 for ar in [m,a,out]:
  x=ar[:,:,:3].astype(float);rr,gg,bb=x.transpose(2,0,1);mask=face&(ar[:,:,3]>=128)&(bb>rr+15)&(bb>gg+8)&(rr>65)&~protect
  means.append(ar[mask,:3].mean(0))
 measure[name]={'mother_blue_mean_RGB':means[0].tolist(),'before_blue_mean_RGB':means[1].tolist(),'after_blue_mean_RGB':means[2].tolist(),'before_delta_RGB':(means[1]-means[0]).tolist(),'after_delta_RGB':(means[2]-means[0]).tolist()}
# Anchor comparison uses fixed source masks for before/after, not a recolored predicate that can hide an error.
for name in ['lit','shade']:
 for material in ['blue','flowers']:
  s=anchor_masks[f'{name}_source_{material}'];t=anchor_masks[f'{name}_mother_{material}'];before=a[s,:3].mean(0);after=out[s,:3].mean(0);target=m[t,:3].mean(0)
  measure[name][material+'_fixed_source_anchor']={'before_delta_RGB':(before-target).tolist(),'after_delta_RGB':(after-target).tolist(),'source_pixels':int(s.sum()),'mother_pixels':int(t.sum()),'mother_small_sample_caveat':bool(t.sum()<30)}
 for material in ['blue','flower']:
  s=anchor_masks[f'{name}_matched_{material}_core']
  if s.sum():measure[name][material+'_matched_core']={'pixels':int(s.sum()),'before_delta_RGB':(a[s,:3].mean(0)-m[s,:3].mean(0)).tolist(),'after_delta_RGB':(out[s,:3].mean(0)-m[s,:3].mean(0)).tolist()}
yy,xx=np.nonzero(change);report={'source_commit':'1c9199121eea99f2434cc39c864eb96c1aba1819','source_candidate_SHA256':sha(src),'original_generator_raw_SHA256':'52c6faf1e5eda14c2930ca557b5d1624a4dea86853f8dd631dd950b7b0d89f2c','mother_SHA256':sha(mother),'candidate_SHA256':sha(O/'candidate/F012.png'),'imagegen_calls':0,'new_poses':0,'alpha_entire_native_exact_source':True,'all_RGB_outside_semantic_tip_exact_source':True,'ink_fold_creases_RGB_exact_source':True,'skin_hair_trousers_RGB_exact_source':True,'upper_and_middle_placket_y_less940_RGB_exact_source':True,'pose_registration_or_spatial_resampling':0,'flower_edge_pixel_locations_unchanged':'Pointwise positive affine color correction; no resampling or edge/motif warp. Shaded flower fill and its antialias colors restore face tone together.','changed_RGB_pixels':int(change.sum()),'actual_changed_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'max_RGB_reduction':np.max(rgb-out[:,:,:3].astype(float),axis=(0,1)).tolist(),'complete_semantic_tip_polygon':domain_points,'lit_face_polygon':lit_points,'face_calibration':cal,'face_measurements':measure,'edit_feather_native_px':2,'face_blend_sigma_native_px':2}
(O/'qa/native_tip_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
