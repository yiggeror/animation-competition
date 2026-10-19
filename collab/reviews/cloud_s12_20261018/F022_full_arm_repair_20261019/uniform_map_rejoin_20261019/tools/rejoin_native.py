"""Authorized zero-call same-art uniform map, precise old ownership and proximal cloth rejoin."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,binary_dilation
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];S=O.parents[1];R=S.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
arm_path=O.parent/'originals/F022_far_arm_patch_call01_raw.png';body_path=S/'batch_F022_F030_production_20261019/originals/F022_raw_call01.png';assert sha(arm_path)=='6e87f65ad06119f6483ba02bbfa072117f7fc1dcc32e4c79b374b67e7e41d543';assert sha(body_path)=='938682ddf40b13e6b72dbacbabedf9502ae73bba79944b330aae6a3bedb26234'
a=np.array(Image.open(arm_path).convert('RGBA'));b=np.array(Image.open(body_path).convert('RGBA'));H,W=b.shape[:2];y,x=np.indices((H,W));M=np.array([[.435717950246291,.061236164422429,523.198762766005],[-.061236164422429,.435717950246291,572.695273541552],[0,0,1.]])
def maskpoly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def save_mask(name,mask):Image.fromarray(mask.astype(np.uint8)*255).save(O/'masks'/name)
# Actual right edge of the original FRONT placket is retained, not cut with the broad GUIDE.
placket=[(626,615),(633,625),(637,635),(639,646),(639,660),(639,680),(637,690),(636,700),(632,715),(627,730),(623,750),(618,770),(610,790),(604,810),(597,827)]
old=maskpoly(placket+[(636,839),(696,836),(778,880),(854,927),(1023,939),(1023,610),(614,610)])
rr,gg,bb=b[:,:,:3].astype(float).transpose(2,0,1);face_skin=(rr>gg+14)&(gg>bb+8)&(rr>160)&(b[:,:,3]>=8)&(y<670);faceprotect=binary_dilation(face_skin,iterations=3)&(y<670);old&=~faceprotect;old&=(y>=615)
save_mask('old_far_arm_actual_ownership.png',old);save_mask('head_neck_skin_outline_protection.png',faceprotect)
# Front collar/placket plus entire near-right arm and body are static foreground ownership.
nearpoly=[(424,640),(525,628),(584,675),(600,811),(601,880),(655,913),(733,943),(804,941),(878,966),(900,1000),(888,1060),(746,1058),(586,1010),(470,976),(413,878)]
near=maskpoly(nearpoly);old&=~near;save_mask('old_far_arm_actual_ownership.png',old);save_mask('near_right_arm_protection.png',near)
# Material masks are selected once on both ORIGINALS. Keep source flowers, dark ink, alpha, crease gradients.
def materials(ar,region):
 r,g,z=ar[:,:,:3].astype(float).transpose(2,0,1);alpha=ar[:,:,3]>=128;white=(r>140)&(g>140)&(z>145)&(r>g*.82)&(z<r*1.30);white=binary_dilation(white,iterations=1)
 return {'blue':region&alpha&(z>g+15)&(g>r+15)&(g>60)&(r>35)&~white,'skin':region&alpha&(r>175)&(g>105)&(z>65)&(r>g+20)&(g>z+10),'jade':region&alpha&(g>r+20)&(g>z+5)&(g>55)}
newm=materials(a,np.ones((H,W),bool));oldm=materials(b,old);aligned=a.copy();reports={}
for name in ['blue','skin','jade']:
 sm=newm[name];tm=oldm[name];assert sm.sum()>100 and tm.sum()>100,(name,sm.sum(),tm.sum());sr=a[sm,:3].astype(float);tr=b[tm,:3].astype(float);sl=sr@np.array([.2126,.7152,.0722]);tl=tr@np.array([.2126,.7152,.0722]);sq=np.quantile(sl,[1/3,2/3]);tq=np.quantile(tl,[1/3,2/3]);sb=np.digitize(sl,sq);tb=np.digitize(tl,tq);anchors=np.array([sl[sb==i].mean() for i in range(3)]);weights=np.zeros((len(sl),3));weights[:,0]=np.clip((anchors[1]-sl)/(anchors[1]-anchors[0]),0,1);weights[:,2]=np.clip((sl-anchors[1])/(anchors[2]-anchors[1]),0,1);weights[:,1]=1-weights[:,0]-weights[:,2];A=np.array([weights[sb==i].mean(0) for i in range(3)]);before=np.array([sr[sb==i].mean(0) for i in range(3)]);target=np.array([tr[tb==i].mean(0) for i in range(3)]);deltas=target-before
 if np.max(abs(deltas))>4:
  offsets=np.linalg.solve(A,deltas);assert np.max(abs(offsets))<32,(name,offsets);values=np.clip(np.rint(sr+weights@offsets),0,255).astype(np.uint8);aligned[sm,:3]=values
 else:offsets=np.zeros((3,3))
 after=np.array([aligned[sm,:3][sb==i].mean(0) for i in range(3)]);reports[name]={'source_raw_pixels':int(sm.sum()),'static022_reference_pixels':int(tm.sum()),'source_fixed_plane_thresholds_L':sq.tolist(),'reference_fixed_plane_thresholds_L':tq.tolist(),'before_minus_target_RGB_by_dark_mid_lit':deltas.tolist(),'applied_RGB_offsets_at_dark_mid_lit_anchors':offsets.tolist(),'after_minus_target_RGB_by_dark_mid_lit':(after-target).tolist(),'fixed_plane_means_within4':bool(np.max(abs(after-target))<=4)};assert reports[name]['fixed_plane_means_within4'];save_mask('source_arm_'+name+'_fixed.png',sm);save_mask('static022_'+name+'_fixed.png',tm)
assert np.array_equal(aligned[:,:,3],a[:,:,3]);changedcolor=np.any(aligned[:,:,:3]!=a[:,:,:3],2);save_mask('source_arm_RGB_changed_only.png',changedcolor);Image.fromarray(aligned).save(O/'candidate/arm_material_aligned_source.png')
# Approved uniform map applies to ENTIRE arm. Only the mapped proximal cloth cap is extended upward36px.
# Inverse a monotone local mesh; all geometry below y755 is exactly the same uniform source map.
def sstep(lo,hi,z):
 t=np.clip((z-lo)/(hi-lo),0,1);return t*t*(3-2*t)
qx=x+.5;qy=y+.5
def weight(px,py):return sstep(600,620,px)*(1-sstep(665,705,px))*(1-sstep(690,755,py))
lo=np.zeros_like(qx);hi=np.ones_like(qx)
for _ in range(42):
 mid=(lo+hi)/2;ww=weight(qx-15*mid,qy+36*mid);lo=np.where(mid<ww,mid,lo);hi=np.where(mid>=ww,mid,hi)
tt=(lo+hi)/2;xp=qx-15*tt;yp=qy+36*tt;prox=(tt>1e-7)&(qy>=640)&(qy<755);xp=np.where(prox,xp,qx);yp=np.where(prox,yp,qy);q=np.stack([xp,yp,np.ones_like(x)],2);p=q@np.linalg.inv(M).T
src_al=aligned[:,:,3]/255;al=np.clip(map_coordinates(src_al,[p[:,:,1]-.5,p[:,:,0]-.5],order=1,mode='constant',cval=0),0,1);prem=aligned[:,:,:3]/255*src_al[:,:,None];rgb=np.stack([map_coordinates(prem[:,:,k],[p[:,:,1]-.5,p[:,:,0]-.5],order=1,mode='constant',cval=0) for k in range(3)],2);out=np.zeros_like(a);out[:,:,3]=np.rint(al*255);out[:,:,:3]=np.clip(np.rint(np.divide(rgb,al[:,:,None],out=np.zeros_like(rgb),where=al[:,:,None]>1e-10)*255),0,255)
# Actual new arm owns its sampled alpha. Static front-body pixels occlude it naturally.
Image.fromarray(out).save(O/'candidate/far_arm_joined_layer.png');save_mask('new_far_arm_actual_ownership.png',out[:,:,3]>0);save_mask('proximal_mesh_actual_support.png',prox&(out[:,:,3]>0));np.savez_compressed(O/'provenance/proximal_inverse_map.npz',destination_bbox_xyxy=np.array([610,640,690,755]),source_uniform_xy=np.stack([xp[640:755,610:690],yp[640:755,610:690]],2))
body=b.copy();body[old]=0;joined=np.array(Image.alpha_composite(Image.fromarray(out),Image.fromarray(body)))
# Keep protected source foreground pixels exactly, including near-hand pixels and every original support.
protected=faceprotect|near|(y<600)|(y>1080);joined[protected]=b[protected];joined[~(old|(out[:,:,3]>0))]=b[~(old|(out[:,:,3]>0))]
change=np.any(joined!=b,2);save_mask('actual_composite_RGBA_changed.png',change);assert not np.any(change&protected);Image.fromarray(joined).save(O/'candidate/F022.png');Image.fromarray(body).save(O/'candidate/static022_old_far_arm_removed.png')
# Mutually exclusive component split reconstructs final original RGBA exactly, without a synthetic finger layer.
actual_new=(out[:,:,3]>0)&(~protected)&((body[:,:,3]<255)|old);layer_new=np.zeros_like(joined);layer_static=joined.copy();layer_new[actual_new]=joined[actual_new];layer_static[actual_new]=0;assert not np.any((layer_new[:,:,3]>0)&(layer_static[:,:,3]>0));assert np.array_equal(np.maximum(layer_new,layer_static),joined);Image.fromarray(layer_new).save(O/'candidate/F022_far_arm_exclusive.png');Image.fromarray(layer_static).save(O/'candidate/F022_static_exclusive.png')
save_mask('new_arm_visible_exclusive_ownership.png',actual_new)
# Full native gray/dark views plus unannotated shoulder/whole arm crops for actual image review.
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(ar,color):return Image.alpha_composite(Image.new('RGBA',(W,H),(*color,255)),Image.fromarray(ar)).convert('RGB')
board=Image.new('RGB',(1024,1574),(235,237,237));draw=ImageDraw.Draw(board)
for i,c in enumerate([(205,209,211),(35,37,40)]):board.paste(flat(joined,c).resize((512,768)),(i*512,38));draw.text((i*512+8,10),'NATIVE F022 CANDIDATE / NOT LOCKED',font=font(16),fill='black')
# Keep same native scale on both backgrounds; separate full-frame candidate remains1024x1536.
board=board.crop((0,0,1024,806));board.save(O/'qa/02_native_gray_dark.jpg',quality=96)
for name,crop,scale in [('03_shoulder_join3x.png',(570,605,725,840),3),('04_complete_far_arm2x.png',(575,605,1024,1005),2)]:flat(joined,(205,209,211)).crop(crop).resize(((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale),Image.Resampling.NEAREST).save(O/'qa'/name)
report={'status':'NATIVE_CANDIDATE_AWAITING_ACTUAL_CANVAS','source_arm_SHA256':sha(arm_path),'source_static022_SHA256':sha(body_path),'native_candidate_SHA256':sha(O/'candidate/F022.png'),'forward_uniform_native_matrix':M.tolist(),'uniform_scale':.44,'uniform_image_coordinate_degrees':-8,'extra_whole_arm_translation_native':[0,0],'proximal_mesh':{'horizontal_native_support':[610,690],'destination_vertical_native_support':[640,755],'max_upward_displacement_native':36,'max_right_displacement_native':15,'max_vector_displacement_native':39,'lower_uniform_coordinate_y_taper':[690,755],'x_smooth_ramps':[600,620,665,705],'front_collar_placket_actual_outer_fold_trace_retained':True,'applies_only_proximal_cloth':True,'skin_wrist_all_digits_no_local_mesh':True},'protected_static_RGBA_exact':True,'old_ownership_is_broad_GUIDE':False,'exclusive_layers_RGBA_exact_reconstruction':True,'material_fixed_planes':reports,'imagegen_calls':0,'F026_F030_unbound':True};(O/'qa/native_rejoin_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='material_fixed_planes'},indent=2))
