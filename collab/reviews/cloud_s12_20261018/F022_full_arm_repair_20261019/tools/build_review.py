"""Zero-render diagnostics of returned artwork in the frozen native/scene registration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates
import json,hashlib,numpy as np
O=Path(__file__).resolve().parents[1]; S=O.parent; I=S/'F022_full_arm_repair_inputs_20261019'
raw=Image.open(O/'originals/F022_far_arm_patch_call01_raw.png').convert('RGBA'); a=np.array(raw)
source=np.array(Image.open(I/'inputs/01_FAILED_F022_unique_source.png').convert('RGBA')); domain=np.array(Image.open(I/'inputs/full_far_arm_edit_domain_GUIDE.png'))>0
props=Image.open(S/'d03_F018_20261019/same_raw_fix_20261019/actual_scene/F018_code_props_actual_layer.png').convert('RGBA'); p=np.array(props)
canvas=Image.open(S/'d03_F018_20261019/same_raw_fix_20261019/actual_scene/F018_canvas.png').convert('RGBA')
# This deliberately applies NO translation, scaling correction, bone manipulation or thumb deformation.
# Exact native registration is part of the approved output contract.
clipped=source.copy(); clipped[domain]=a[domain]; assert np.array_equal(clipped[~domain],source[~domain])
Image.fromarray(clipped).save(O/'review/REJECTED_exact_domain_composite_DIAGNOSTIC.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
plate=Image.new('RGBA',(1024,1536),(237,240,240,255)); plate=Image.alpha_composite(plate,raw)
d=ImageDraw.Draw(plate); d.rectangle((0,0,1024,140),fill=(237,240,240)); d.text((18,15),'RETURNED PATCH / ORIGINAL NATIVE REGISTRATION',font=font(26),fill=(126,30,30));d.text((18,58),'REJECTED: enlarged/misplaced complete arm; no positioning fix applied',font=font(21),fill=(126,30,30)); d.text((18,98),'Red contour = approved full-arm editable domain',font=font(21),fill=(33,51,66))
from scipy.ndimage import binary_dilation
outline=domain&binary_dilation(~domain); ov=np.zeros_like(a);ov[outline]=[219,32,48,255];plate=Image.alpha_composite(plate,Image.fromarray(ov));plate.convert('RGB').save(O/'review/returned_patch_vs_approved_domain.png')
# Same registration used by frozen actual scene: native*.70+(275,112).
y,x=np.indices((1080,1920)); srcx=(x+.5-275)/.7-.5;srcy=(y+.5-112)/.7-.5;coords=[srcy,srcx];al=a[:,:,3]/255;aa=np.clip(map_coordinates(al,coords,order=1,mode='constant',cval=0),0,1);prem=a[:,:,:3]/255*al[:,:,None];rgb=np.stack([map_coordinates(prem[:,:,k],coords,order=1,mode='constant',cval=0) for k in range(3)],2);world=np.zeros((1080,1920,4),np.uint8);world[:,:,3]=np.rint(aa*255);world[:,:,:3]=np.clip(np.rint(np.divide(rgb,aa[:,:,None],out=np.zeros_like(rgb),where=aa[:,:,None]>1e-10)*255),0,255)
context=Image.new('RGBA',(1920,1080),(237,240,240,255));context.paste(canvas.crop((1000,0,1920,1080)),(1000,0));leftp=p.copy();leftp[:,1000:,3]=0;context=Image.alpha_composite(context,Image.fromarray(leftp));context=Image.alpha_composite(context,Image.fromarray(world))
d=ImageDraw.Draw(context);d.rectangle((0,0,1920,125),fill=(237,240,240));d.text((22,18),'RETURNED RAW PATCH + ACTUAL FROZEN PROPS / DIAGNOSTIC ONLY',font=font(29),fill=(126,30,30));d.text((22,65),'No registration correction. NOT accepted art. Other fingers intersect upper shaft; thumb is left of first-touch target.',font=font(21),fill=(126,30,30));context.convert('RGB').save(O/'review/actual_props_returned_patch_DIAGNOSTIC.png')
context.convert('RGB').crop((850,700,1000,830)).resize((1500,1300),Image.Resampling.NEAREST).save(O/'review/actual_contact_DIAGNOSTIC10x.png')
# Exact alpha counts, plus conservative thumb-neighbourhood separation (not an anatomical bone measurement).
solid=a[:,:,3]>=128; outside=int(np.count_nonzero(solid&~domain)); total=int(np.count_nonzero(solid))
A=np.array([934.312497676,785.129739577]);B=np.array([1497.531490504,714.664205296]);worldxy=np.stack([x+.5,y+.5],2)
def rod(A,B):
 v=B-A;t=np.clip(((worldxy-A)@v)/(v@v),0,1);return(p[:,:,3]>0)&(np.linalg.norm(worldxy-A-t[:,:,None]*v,axis=2)<5.5)&(x>=925)&(x<=1000)
u=rod(A,B); l=rod(np.array([951.261694392,798.906335746]),np.array([1282.198690556,773.946794448])); upper_overlap=int(np.count_nonzero((world[:,:,3]>=128)&u));lower_overlap=int(np.count_nonzero((world[:,:,3]>=128)&l))
# Broad visible thumb/palm neighbourhood, explicitly stored as a diagnostic selection only.
thumb_domain=np.zeros(al.shape,bool);thumb_domain[930:1002,820:930]=True; thumb_alpha=map_coordinates(al*thumb_domain,coords,order=1,mode='constant',cval=0); ty,tx=np.nonzero(thumb_alpha>=.5);ry,rx=np.nonzero(u);q=np.stack([tx,ty],1);r=np.stack([rx,ry],1);dd=np.maximum(abs(q[:,None,:]-r[None,:,:])-1,0); thumb_neighbour_gap=float(np.sqrt(np.sum(dd*dd,2)).min())
report={'status':'STOP_MAJOR_NATIVE_REGISTRATION_AND_FIRST_CONTACT_FAILURE','raw_patch_size':list(raw.size),'raw_patch_SHA256':hashlib.sha256((O/'originals/F022_far_arm_patch_call01_raw.png').read_bytes()).hexdigest(),'actual_drawn_patch_visually_inspected':True,'alpha128_pixels_total':total,'alpha128_pixels_outside_approved_edit_domain':outside,'outside_fraction':outside/total,'domain_test_composite_outside_source_pixels_identical':True,'alpha128_upper_rod_overlap_scene_pixels':upper_overlap,'alpha128_lower_rod_overlap_scene_pixels':lower_overlap,'manual_thumb_plus_neighbor_palm_native_ROI_xyxy':[820,930,930,1002],'visible_selected_thumb_neighborhood_min_air_to_actual_upper_rod_scene':thumb_neighbour_gap,'manual_ROI_is_not_bone_or_semantic_ground_truth':True,'patch_reposition_or_resize_applied':False,'accepted_for_next_continuity':False,'repair_calls_submitted':1,'repair_outputs_returned':1,'current_S12_cumulative_calls':7,'scene_renders':0,'F026_F030_unbound':True}
assert outside/total>.5 and upper_overlap>0 and thumb_neighbour_gap>0
(O/'review/SELF_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
L=O/'provenance/call_ledger.json';ledger=json.loads(L.read_text());ledger.update(state=report['status'],accepted_for_next_continuity=False,inflight=None,F026_F030_unbound=True);L.write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps(report,indent=2))
