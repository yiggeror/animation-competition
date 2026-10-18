#!/usr/bin/env python3
"""Actual057 rigid-pixel062 scaffold. No generation, paint, stretch or old-hip reuse."""
from pathlib import Path
import json, math, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation,label

O=Path(__file__).resolve().parent
OLD=O.parent
B=OLD.parent
SRC=O/'sources'
for name in ['reference','layers','masks','qa','geometry']:(O/name).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png'
assert sha(source)=='93939f3e148c0a957ef418c677e60cc3fd27cf6b6844f91d500c8a3508b76720'
im=Image.open(source).convert('RGBA');a=np.array(im);size=im.size
old=json.loads((SRC/'geometry/F062_constraints_and_sources.json').read_text())
gate=json.loads((OLD/'hip_gate_minimal_v3/hip_gate_notes.json').read_text())
reg=old['registration_unchanged'];s=reg['s'];off=np.array([reg['tx'],reg['ty']]);world=lambda q:(np.array(q)*s+off).tolist()
body_delta=np.array(gate['original_upper_body_delta_world'])/s
nh=np.array(gate['source_near_hip_candidate_native']);nk=np.array(gate['source_knee_native']);na=np.array(gate['source_ankle_native'])
NH=np.array(gate['F062_optional_hip_native']);NK=np.array(gate['F062_optional_knee_native'])
norm=lambda q:float(np.linalg.norm(q))
near_lengths=[norm(nk-nh),norm(na-nk)]
assert np.allclose(near_lengths,[norm(NK-NH),norm(na-NK)],atol=1e-8)

def loadmask(name):return np.array(Image.open(SRC/'masks'/name).convert('L'))>0
source_masks={n:loadmask('F057_source_'+n+'.png') for n in ['body_head_blouse','near_complete_arm','far_complete_arm_jade_hand','near_shoe_ankle_FIXED','far_shoe_ankle']}
near_pants=loadmask('F057_source_near_thigh.png')|loadmask('F057_source_near_shin.png')
far_pants=loadmask('F057_source_far_thigh.png')|loadmask('F057_source_far_shin.png')
yy,xx=np.indices(a.shape[:2])
blouse=loadmask('F057_actual_complete_blouse_material.png')
assert not np.any(blouse&(near_pants|far_pants|source_masks['near_complete_arm']|source_masks['far_complete_arm_jade_hand']))
assert not np.any(source_masks['body_head_blouse']&(yy>=635)&(a[:,:,3]>0))
real_arm_source={};arm_fragment_counts={}
for name in ['near_complete_arm','far_complete_arm_jade_hand']:
    arm=source_masks[name];labs,n=label(arm&(a[:,:,3]>=20))
    counts=np.bincount(labs.ravel());counts[0]=0;main=labs==int(counts.argmax())
    real_arm_source[name]=arm&binary_dilation(main,iterations=3)
    arm_fragment_counts[name]=int((arm&~real_arm_source[name]).sum())

# Far-leg cloth is a manual back-layer shape proposal, not a newly frozen hip.
# Preserve only the existing relative pelvis side offset; the withdrawn744
# point is never used as a current absolute joint or segment length.
relative_far=np.array([-7./s,1./s])
fh=nh+relative_far;FH=NH+relative_far
fk=np.array(old['far_chain']['source_native'][1]);fa=np.array(old['far_chain']['source_native'][2])
far_shoe_delta=np.array([73.,-23.])/s;FA=fa+far_shoe_delta
far_lengths=[norm(fk-fh),norm(fa-fk)]
def ik(h,ank,L1,L2):
    v=ank-h;distance=norm(v)
    assert abs(L1-L2)<=distance<=L1+L2
    u=v/distance;n=np.array([-u[1],u[0]])
    along=(L1*L1-L2*L2+distance*distance)/(2*distance)
    height=math.sqrt(max(0,L1*L1-along*along))
    return max([h+u*along+n*height,h+u*along-n*height],key=lambda q:q[0])
FK=ik(FH,FA,*far_lengths)

def R(angle):return np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
def segment(u,v,uu,vv):
    ang=math.atan2(*(vv-uu)[::-1])-math.atan2(*(v-u)[::-1]);r=R(ang)
    assert abs(norm(v-u)-norm(vv-uu))<1e-8
    return r,uu-r@u,ang
split=(xx-nk[0])*(nk[0]-nh[0])+(yy-nk[1])*(nk[1]-nh[1])<=0
source_masks['near_thigh']=near_pants&split;source_masks['near_shin']=near_pants&~split
split=(xx-fk[0])*(fk[0]-fh[0])+(yy-fk[1])*(fk[1]-fh[1])<=0
source_masks['far_thigh']=far_pants&split;source_masks['far_shin']=far_pants&~split
assert sum(z.astype(int) for z in source_masks.values()).max()==1
assert np.array_equal(np.logical_or.reduce(list(source_masks.values())),a[:,:,3]>0)
def layer(mask):
    z=a.copy();z[~mask]=0;return Image.fromarray(z)
def rigid(z,r,t):
    inv=r.T;offset=-inv@t
    assert np.allclose(r.T@r,np.eye(2),atol=1e-12)
    return z.transform(size,Image.Transform.AFFINE,(*inv[0],offset[0],*inv[1],offset[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
transforms={'body_head_blouse':(np.eye(2),body_delta),'near_shoe_ankle_FIXED':(np.eye(2),np.zeros(2)),'far_shoe_ankle':(np.eye(2),far_shoe_delta)}
for n,u,v,uu,vv in [('near_thigh',nh,nk,NH,NK),('near_shin',nk,na,NK,na),('far_thigh',fh,fk,FH,FK),('far_shin',fk,fa,FK,FA)]:transforms[n]=segment(u,v,uu,vv)[:2]
arm_chains={}
for side,name,angle in [('near','near_complete_arm',-8.),('far','far_complete_arm_jade_hand',8.)]:
    chain=np.array(old['arms'][side+'_source_native']);r=R(math.radians(angle));t=chain[0]+body_delta-r@chain[0];transforms[name]=(r,t);arm_chains[side]=[r@q+t for q in chain]
layers={}
for name,mask in source_masks.items():
    z=layer(mask);r,t=transforms[name]
    if name!='near_shoe_ankle_FIXED':z=rigid(z,r,t)
    layers[name]=z;z.save(O/'layers'/('F062_'+name+'.png'))
    Image.fromarray(mask.astype('uint8')*255).save(O/'masks'/('SOURCE_'+name+'.png'))
order=['far_thigh','far_shin','far_shoe_ankle','near_thigh','near_shin','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']
canvas=Image.new('RGBA',size)
for name in order:canvas.alpha_composite(layers[name])
out=np.array(canvas);out[source_masks['near_shoe_ankle_FIXED']]=a[source_masks['near_shoe_ankle_FIXED']]
canvas=Image.fromarray(out);cp=O/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png';canvas.save(cp)
alphas={n:np.array(z)[:,:,3] for n,z in layers.items()}

def poly(points):
    z=Image.new('L',size);ImageDraw.Draw(z).polygon([tuple(map(float,p)) for p in points],fill=255);return np.array(z)>0
def capsule(points,r):
    z=Image.new('L',size);d=ImageDraw.Draw(z);ps=[tuple(map(float,p)) for p in points];d.line(ps,fill=255,width=2*r+1)
    for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return np.array(z)>0
def visible(name):
    i=order.index(name);front=np.zeros(a.shape[:2],bool)
    for n in order[i+1:]:front|=alphas[n]>0
    return (alphas[name]>0)&~front
visible_near_foot=visible('near_shoe_ankle_FIXED');visible_far_foot=visible('far_shoe_ankle')
visible_feet=visible_near_foot|visible_far_foot
# Exterior AA guard only extends into genuinely empty space, never front pants.
foot_guard=visible_feet|(binary_dilation(visible_feet,iterations=2)&(out[:,:,3]==0))
# Finite actual-foot QA: the detached little black L above the far ankle is
# old pant-cut ink, not shoe/skin. Release only that disconnected fragment;
# keep every actual shoe contour and warm ankle pixel with its AA.
farz=np.array(layers['far_shoe_ankle']);labs,n=label(farz[:,:,3]>=128);counts=np.bincount(labs.ravel());counts[0]=0
far_main=labs==counts.argmax()
rr=farz[:,:,:3].astype(int);warm=(farz[:,:,3]>20)&(rr[:,:,0]>150)&(rr[:,:,0]>rr[:,:,1])&(rr[:,:,1]>rr[:,:,2])&((rr[:,:,0]-rr[:,:,2])>25)
far_cut_roi=(xx>=912)&(xx<=922)&(yy>=889)&(yy<=901)
old_far_cuff_ink=visible_far_foot&far_cut_roi&~binary_dilation(far_main,iterations=3)&~binary_dilation(warm,iterations=2)
foot_cut_cleanup=binary_dilation(old_far_cuff_ink,iterations=1)&far_cut_roi&~binary_dilation(far_main,iterations=3)&~binary_dilation(warm,iterations=2)
foot_guard&=~foot_cut_cleanup
arm_visible=visible('near_complete_arm')|visible('far_complete_arm_jade_hand')
real_arm_moved=np.zeros(a.shape[:2],bool)
for name,material in real_arm_source.items():
    r,t=transforms[name];real_arm_moved|=np.array(rigid(layer(material),r,t))[:,:,3]>0
detached_arm_layer_fragments=arm_visible&~real_arm_moved
sleeve_release=np.zeros(a.shape[:2],bool)
for side in ['near','far']:
    root=arm_chains[side][0];sleeve_release|=capsule([root+[-17,-2],root+[17,13]],14)
body_material=alphas['body_head_blouse']>0
body_guard=body_material&~sleeve_release
arm_guard=arm_visible&real_arm_moved&~sleeve_release
guards=foot_guard|body_guard|arm_guard
pants_dest=(alphas['near_thigh']>0)|(alphas['near_shin']>0)|(alphas['far_thigh']>0)|(alphas['far_shin']>0)
# Complete old/new material silhouettes + turn volume, not knee rectangles.
old_pants_moved=np.array(rigid(layer(near_pants|far_pants),np.eye(2),body_delta))[:,:,3]>0
near_domain=capsule([NH,NK,na],49)
far_domain=capsule([FH,FK,FA],49)
hips=capsule([NH+[-65,-25],NH+[45,-25]],35)
semantic=binary_dilation(pants_dest|old_pants_moved,iterations=8)|near_domain|far_domain|hips|sleeve_release|binary_dilation(detached_arm_layer_fragments,iterations=3)|foot_cut_cleanup
edit=semantic&~guards
crop=(650,280,1120,1060);crop_domain=(xx>=crop[0])&(xx<crop[2])&(yy>=crop[1])&(yy<crop[3])
outside=edit&~crop_domain;outside_material=int((outside&(out[:,:,3]>20)).sum())
assert outside_material==0
edit&=crop_domain
for name,z in [('F062_full_pants_and_sleeves_WHITE_EDIT_PENDING',edit),('HARD_visible_complete_shoes_ankles',foot_guard),('HARD_complete_head_blouse_except_sleeve',body_guard),('HARD_visible_complete_arms_except_sleeve',arm_guard),('sleeve_release',sleeve_release),('complete_old_new_pants_semantic',semantic&~sleeve_release)]:Image.fromarray(z.astype('uint8')*255).save(O/'masks'/(name+'.png'))
canvas.crop(crop).save(O/'reference/F062_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(O/'masks/F062_crop_WHITE_EDIT_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,color=(211,220,228,255)):
    q=Image.new('RGBA',size,color);q.alpha_composite(z);return q
guide=bg(canvas).convert('RGB');gd=ImageDraw.Draw(guide)
for points,col in [([NH,NK,na],'#008caf'),([FH,FK,FA],'#b77432')]:
    pts=[tuple(q) for q in points];gd.line(pts,fill=col,width=3)
    for x,y in pts:gd.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
floor=1022;gd.line((750,floor,1060,floor),fill='#2c6f80',width=2)
gd.text((35,30),'062真实像素预摆｜非画稿｜不代表调用通过',font=font,fill='#263846')
gd.text((35,58),'近髋/膝按77ab代理；头衣原节拍、近鞋踝原位；裤根/整腿待真绘',font=font,fill='#263846')
gd.text((35,86),'远髋棕点仅新手工层次提示，未冻结；远鞋整片+73/-23world',font=font,fill='#9b5624')
guide.save(O/'qa/F062_calibrated_chain_and_actual_support.png')
wash=Image.new('RGBA',size,(227,38,123,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*100));ov=bg(canvas);ov.alpha_composite(wash);ov.save(O/'qa/F062_complete_semantic_domain_overlay.png');ov.crop(crop).save(O/'qa/F062_crop_and_edit_domain_PENDING.png')
sheet=Image.new('RGB',(1680,1060),(238,242,245));dr=ImageDraw.Draw(sheet)
for i,(label,z) in enumerate([('锁057真实源',bg(im)),('062像素预摆／非画稿',bg(canvas)),('髋膝踝代理／非解剖实测',guide)]):
    panel=z.crop((560,0,1120,1050)).resize((550,1031),Image.Resampling.LANCZOS);sheet.paste(panel.convert('RGB'),(i*560,28));dr.text((i*560+8,3),label,font=font,fill='#263846')
sheet.save(O/'qa/F057_F062_actual_pixels_and_chain_comparison.png')
footqa=Image.new('RGB',(1200,420),(218,226,232));dr=ImageDraw.Draw(footqa)
for i,(label,z) in enumerate([('057完整承重鞋踝',layer(source_masks['near_shoe_ankle_FIXED'])),('062原位同RGBA',layers['near_shoe_ankle_FIXED']),('062远鞋过步原片平移',layers['far_shoe_ankle'])]):
    cropbox=(760,875,1020,1045);q=bg(z).crop(cropbox).resize((390,255));footqa.paste(q.convert('RGB'),(i*400,35));dr.text((i*400+5,4),label,font=font,fill='#263846')
footqa.save(O/'qa/actual_fixed_near_and_swing_far_feet.png')
soles={}
for name in ['near_shoe_ankle_FIXED','far_shoe_ankle']:
    ys,xs=np.where(alphas[name]>=128);bottom=int(ys.max());soles[name]={'native_alpha128_bottom':bottom,'world_alpha128_bottom':bottom*s+off[1]}
near_mat=source_masks['near_shoe_ankle_FIXED']
report={'status':'NEW_HIP_CALIBRATED_F062_PIXEL_PREFLIGHT_PENDING_PARENT_ACTUAL_REVIEW_NOT_CALL_APPROVED','source_sha256':sha(source),'source':str(source),'proposal_sha256':sha(cp),'registration':reg,'near_source_chain_native':[q.tolist()for q in [nh,nk,na]],'near062_chain_native':[q.tolist()for q in [NH,NK,na]],'near_lengths_world_source':[v*s for v in near_lengths],'near_lengths_world_target':[norm(NK-NH)*s,norm(na-NK)*s],'hip_proxy_not_anatomical_measurement':True,'hip_down_from_uniform_world':gate['optional_hip_down_from_uniform_world'],'hip_down_from_source_world':gate['optional_hip_down_from_source_world'],'head_blouse_delta_world':gate['original_upper_body_delta_world'],'near_shoe_RGBA_changes':int(np.any(out[near_mat]!=a[near_mat],axis=1).sum()),'shoe_roll_or_slide':False,'far_shoe_delta_world':[73,-23],'far_source_shape_proxy_native':[q.tolist()for q in [fh,fk,fa]],'far062_shape_proxy_native':[q.tolist()for q in [FH,FK,FA]],'far_proxy_is_unfrozen_manual_shape_guide':True,'far_proxy_definition':'Near77ab hip plus former frozen side-relative offset[-7,+1]world only; no withdrawn744 absolute hip or lengths reused. Full far pants editable.','actual_shoe_bottoms':soles,'original_material_partition_exact_once':True,'blouse_material_assigned_to_pants_or_arm':0,'body_source_alpha_below635':0,'layer_order_back_to_front':order,'mask':{'pixels':int(edit.sum()),'crop_xyxy':crop,'head_blouse_overlap':int((edit&body_guard).sum()),'visible_complete_arm_overlap':int((edit&arm_guard).sum()),'visible_complete_shoes_ankles_overlap':int((edit&foot_guard).sum()),'outside_crop':int((edit&~crop_domain).sum()),'omitted_outside_crop_material_alpha20':outside_material,'full_visible_pants_not_editable_except_guard':int((pants_dest&~edit&~guards).sum())},'limits':['Pixel-piece knee/hip/ankle/sleeve cuts remain technical preposition, not final art.','Whole old/new pants and background cleanup are editable, not knee-only patches.','Hidden far-foot pixels never lock foreground pants. Complete visible arms protected except sleeve connections.','No new image request, recolor, limb stretch, changedhead timing, rolling/sliding shoe or11state reconstruction.','Parent actual-view gate and any remaining far-shape authority must be resolved before generation.']}
report['arm_source_isolated_nonmaterial_fragment_counts']=arm_fragment_counts
report['finite_footcut_review']={'old_far_pant_cut_ink_released_from_guard':int(old_far_cuff_ink.sum()),'local_cleanup_semantic_pixels':int(foot_cut_cleanup.sum()),'native_region':[912,889,922,901],'actual_shoe_main_contour_and_all_warm_skin_with_AA_still_protected':True,'near_original_shoe_layer_RGBA_untouched':True,'note':'Only detached black L visible above far ankle in actualfootQA; no broad shoe threshold/recolor/pose change.'}
report['arm_fragment_note']='Arm source layers retain original fragments for honest technical display; disconnected nonmaterial fragments beyond3px of main opaque limb are released to cleanup, never hard-protected as complete arm.'
report['mask']['all_pant_layer_alpha_outside_crop_or_guard']=report['mask'].pop('full_visible_pants_not_editable_except_guard')
visible_pants=np.logical_or.reduce([visible(n) for n in ['near_thigh','near_shin','far_thigh','far_shin']])
report['mask']['actual_visible_pants_alpha20_missing_edit_except_guard']=int((visible_pants&(out[:,:,3]>20)&~edit&~guards).sum())
report['mask']['isolated_arm_layer_AA_over_actual_body_guard']=int((detached_arm_layer_fragments&body_guard).sum())
report['mask']['pants_side_isolated_ink_AA_still_hardprotected']=int((detached_arm_layer_fragments&~body_guard&guards).sum())
report['mask']['detached_arm_layer_fragments_not_editable_and_visible']=int((detached_arm_layer_fragments&~edit&~guards).sum())
report['reproduction_inputs_snapshot']='sources/snapshot_manifest.json (byte-exact copies of all formerly uncommitted dependencies)'
report['committed_external_inputs']=['e3d2202 locked057 PNG; SHA checked by script','77ab772 next3_preflight_61sol/hip_gate_minimal_v3/hip_gate_notes.json']
report['limits'][-1]='This062 shape guide and operation input require the requested Astra actual-image gate; manual farhip is a shape hint, not a new anatomical measurement or separate authorization blocker.'
(O/'geometry/preparation_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(O/'README.md').write_text('本目录为062新髋代理校准后独立像素预摆和完整语义罩，未通过调用门。\n\n仅采用锁057原RGBA作刚体分片预摆；近髋/膝/踝按77ab返回的新代理。旧791腰口/744髋点不复用。头衣保原节拍，近鞋踝原位；远鞋沿既有+73/-23world事件。\n\n棕色远髋仅手工形体层次提示：由当前近髋加原左右相对偏移建立，不是已冻结的新骨架。整远裤及旧/新边均白区，必须真实绘图审形体。\n\n完整蓝衣/白花先归体衣，真实鞋/踝按可见层保护，完整双臂除小袖根连接均黑保护。所有分片切口不能当成画稿通过。无生成、无旧文件覆盖。\n')
print(json.dumps({'proposal':str(cp),'sha256':sha(cp),'mask':report['mask'],'actual_shoe_bottoms':soles},ensure_ascii=False))
