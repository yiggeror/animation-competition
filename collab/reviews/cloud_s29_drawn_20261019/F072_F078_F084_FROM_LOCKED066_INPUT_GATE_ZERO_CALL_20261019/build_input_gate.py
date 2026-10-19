"""Zero-generation technical input gate from actual locked066. NOT native drawings.
One cloth surface, real immutable props, complete arm reference targets. No scene render.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.spatial import Delaunay
import numpy as np
import hashlib, json, shutil

R=Path(__file__).resolve().parent; B=R.parent; repo=R.parents[3]
N=B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F066/reintegration'
G=B/'F054_F060_F066_FULL_TARGET_GATE_ZERO_CALL_20261019/F066'
lockedp=B/'F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019/F066_UNCHANGED_LOCKED_RGBA.png'
clothp=G/'ONE_SAME_MATERIAL_MAPPED_CLOTH_RGBA.png'
propsp=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png'
masterp=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png'
def rgba(p): return np.array(Image.open(p).convert('RGBA'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p): Image.fromarray(a).save(p)
def sm(a,p): save((a*255).astype('uint8'),p)
def poly(points):
    im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def comp(*layers):
    im=Image.new('RGBA',(1024,1536))
    for a in layers: im.alpha_composite(Image.fromarray(a))
    return np.array(im)
def gray(a): return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
Y,X=np.indices((1536,1024)); pix=np.column_stack([X.ravel(),Y.ravel()])
def sample(a,co):
    p=a.astype(float);p[:,:,:3]*=p[:,:,3:4]/255
    z=np.stack([nd.map_coordinates(p[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0) for k in range(4)],2)
    z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8)
    z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
def mesh(src,dst):
    tr=Delaunay(dst);si=tr.find_simplex(pix);valid=si>=0;ss=np.maximum(si,0)
    b2=np.einsum('ijk,ik->ij',tr.transform[ss,:2],pix-tr.transform[ss,2]);ba=np.column_stack([b2,1-b2.sum(1)])
    co=np.einsum('ij,ijk->ik',ba,src[tr.simplices[ss]]);co[~valid]=-100
    sv=src[tr.simplices];tv=dst[tr.simplices]
    sd=np.linalg.det(np.stack([sv[:,1]-sv[:,0],sv[:,2]-sv[:,0]],2));td=np.linalg.det(np.stack([tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]],2))
    ratio=td/sd; assert (ratio>0).all(),ratio.min()
    return co.reshape(1536,1024,2),dict(source_landmarks=src.tolist(),target_landmarks=dst.tolist(),triangles=tr.simplices.tolist(),inverted_triangles=int((ratio<=0).sum()),min_signed_area_ratio=float(ratio.min()))
def affine(a,M,t): return sample(a,((pix-t)@np.linalg.inv(M).T).reshape(1536,1024,2))
def segment(A,B,C,D):
    u=(B-A)/np.linalg.norm(B-A);un=np.array([-u[1],u[0]]);v=(D-C)/np.linalg.norm(D-C);vn=np.array([-v[1],v[0]])
    M=np.outer(v,u)*(np.linalg.norm(D-C)/np.linalg.norm(B-A))+np.outer(vn,un);return M,C-M@A
locked=rgba(lockedp);cloth066=rgba(clothp);props=rgba(propsp);pm=props[:,:,3]>0
near066=rgba(N/'EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png')
far066=rgba(N/'ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png')
# Never return to old048/P arms. Remove both actual066 limbs only in new references.
base=locked.copy();base[(near066[:,:,3]>0)|(far066[:,:,3]>0)|(cloth066[:,:,3]>0)|pm]=0
# The accepted flattened066 also contains historical upper-cloth contour pixels
# outside its separated canonical cotton alpha. They are obsolete when the lip
# lowers. Clear this entire upper cloth/arm overlap field; restore actual blouse
# behind it and current same-source cotton below. Never leave an old floating lip.
old_upper_overlap=(X>=500)&(Y>=620)&(Y<820)
base[old_upper_overlap]=0
sm(old_upper_overlap,R/'OBSOLETE066_UPPER_OVERLAP_CLEAR_DOMAIN.png')
blouse=rgba(N/'SAME_NATIVE_RAW_CONTINUOUS_BLOUSE_BEHIND_CLOTH_RGBA.png')
base=comp(base,blouse)
# Behind all new cotton/props. This is a conspicuously marked unknown-blouse guide.
unknown=(near066[:,:,3]>0)&(cloth066[:,:,3]<128)&(Y>625)
guide=np.zeros_like(locked);guide[unknown]=[114,168,225,255];base=comp(base,guide)
sm(unknown,R/'EXPOSED_BLOUSE_REQUIRES_NATIVE_REDRAW_MASK.png')
shutil.copyfile(lockedp,R/'LOCKED066_ACTUAL_REFERENCE_RGBA.png');shutil.copyfile(propsp,R/'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png')
shutil.copyfile(clothp,R/'LOCKED066_SAME_SOURCE_CLOTH_RGBA.png')
C2=np.array([681.098467936869,670.61030076984]); P=np.array([430.,959.])
# Actual066 front edge: y=959 at x=430, not old neck/palm coordinates.
edge={str(x):int(np.where(cloth066[:,x,3]>128)[0].max()) for x in range(340,541)}
P[1]=edge['430']; assert P[1]==959
# Dense landmarks of the actual066 sheet. Fixed near-press/lap anchors are explicit.
src=np.array([[x,y] for y in [0,470,610,670.61030076984,710,747,790,835,900,1100,1535] for x in [0,256,499,535,600,681.098467936869,750,842,950,1023]],float)
src=np.vstack([src,[C2,[420,820],[535,835],[650,840],P]])
src=np.unique(src,axis=0)
fixed_lower=(Y>=820)|(X<=499)
oldfront=np.array(Image.open(G/'FINITE_FRONT_LIP_DOMAIN_MASK.png').convert('L'))>0
panels=[];reports=[]
for f,delta in [(72,np.array([-21.,40.])),(78,np.array([-41.,75.])),(84,np.array([-41.,75.]))]:
    d=R/f'F{f:03d}';d.mkdir(exist_ok=True)
    dst=src.copy(); wx=np.maximum(0,1-np.abs(src[:,0]-C2[0])/182)**1.25
    wy=np.where(src[:,1]<=C2[1],np.clip((src[:,1]-470)/(C2[1]-470),0,1),np.clip((820-src[:,1])/(820-C2[1]),0,1))
    w=wx*wy;w[(src[:,0]<=499)|(src[:,1]>=820)]=0
    # These are contact/support anchors, held exactly, not inferred from an old pose.
    for a in [[420,820],[535,835],[650,840],P.tolist()]: w[np.linalg.norm(src-a,axis=1)<.01]=0
    dst+=w[:,None]*delta;co,meta=mesh(src,dst);cloth=sample(cloth066,co)
    # All supported lower/front material is exact066, including the future084 edge.
    cloth[fixed_lower]=cloth066[fixed_lower]
    # The upper cloth lobe folds in FRONT of the crane. This same-source domain is
    # distinct from lower support cloth behind the rigid puppets. No prop warp.
    foldbase=700+.30*(co[:,:,0]-520)
    front=(co[:,:,1]<foldbase)&(co[:,:,0]>520)&(cloth[:,:,3]>0)&(Y<808)
    front|=oldfront&(cloth[:,:,3]>0)
    lip=np.zeros_like(cloth);lip[front]=cloth[front]
    save(cloth,d/'ONE_CONTINUOUS_SAME_SOURCE_CLOTH_RGBA.png');save(lip,d/'SAME_MATERIAL_FRONT_FOLD_RGBA.png');sm(front,d/'FRONT_FOLD_OVER_TRUE_PROPS_MASK.png')
    meta.update(input_cloth_SHA256=sha(clothp),same_material_pinch_source066=C2.tolist(),same_material_pinch_target=(C2+delta).tolist(),lower_support_exact066_domain='y>=820 OR x<=499',new_flower_pixels_painted=0)
    (d/'CLOTH_SURFACE_MAPPING.json').write_text(json.dumps(meta,indent=2)+'\n')
    # Complete actual066 far limb, cuff fixed, moving entire jade/wrist/hand as one
    # translated group; intermediate bare-arm deformation is ONLY a redraw guide.
    # Actual066 diagonal cuff plane, rather than a horizontal row. This preserves
    # the entire native sleeve/blossom pattern and whole jade group without stretch.
    n=np.array([.625,.781]);n/=np.linalg.norm(n)
    dd=(X-546)*n[0]+(Y-530)*n[1];ss=np.linspace(-2000,2000,16001)
    ww=np.clip(ss/45,0,1);ww=ww*ww*(3-2*ww)
    sd=np.interp(dd,ss+float(delta@n)*ww,ss)
    wt=np.clip(sd/45,0,1);wt=wt*wt*(3-2*wt);fco=np.stack([X-wt*delta[0],Y-wt*delta[1]],2)
    far=sample(far066,fco)
    # Guarantee the whole hand/jade beyond this actual cuff-relative plane is rigid.
    rigid=far066.copy();rigid[dd<45]=0;rigid=affine(rigid,np.eye(2),delta)
    far[rigid[:,:,3]>0]=rigid[rigid[:,:,3]>0]
    near=near066.copy();hand=np.zeros_like(near);nearinfo=dict(state='EXACT066 open palm, same support',cuff=[174,615],elbow=[190,674],wrist=[455,812],palm_support=[519,833])
    if f==84:
        # Entire near arm reference from actual066; fingers are NEVER individually
        # moved. Whole mirrored actual066 far pinch hand is an anatomy PROXY ONLY.
        # It is not a new generated drawing or an approved final near-hand pose.
        C=np.array([174.,615.]);E0=np.array([190.,674.]);W0=np.array([455.,812.]);E=np.array([174.,705.])
        z=np.deg2rad(-50);M=np.array([[np.cos(z),-np.sin(z)],[np.sin(z),np.cos(z)]])@np.diag([-1.,1.]);t=P-M@C2
        W=M@np.array([642.,603.])+t
        handsrc=far066.copy();handdomain=poly([(642,576),(680,578),(730,617),(736,646),(720,674),(684,692),(655,674),(642,642),(628,609),(630,591)])
        # Skin/ink only; jade remains exclusively on the actual far wrist.
        jade=(handsrc[:,:,1]>handsrc[:,:,0]*1.04)&(handsrc[:,:,1]>handsrc[:,:,2]*1.03)
        handsrc[~handdomain|jade]=0;hand=affine(handsrc,M,t)
        up=near066.copy();up[~poly([(120,580),(230,600),(244,675),(204,712),(151,714),(120,650)])]=0
        fo=near066.copy();fo[~poly([(150,654),(205,641),(275,686),(455,776),(473,827),(435,833),(304,799),(168,714),(145,689)])]=0
        M2,t2=segment(E0,W0,E,W)
        # The actual cuff cross-section stays exact066. Deform the complete upper
        # arm below it continuously; never rotate a detached cap out of its sleeve.
        ys=np.arange(1536,dtype=float);uw=np.clip((ys-625)/49,0,1);uw=uw*uw*(3-2*uw)
        sy=np.broadcast_to(np.interp(np.arange(1536),ys+uw*(E[1]-E0[1]),ys)[:,None],Y.shape)
        uw=np.clip((sy-625)/49,0,1);uw=uw*uw*(3-2*uw)
        upnew=sample(up,np.stack([X-uw*(E[0]-E0[0]),sy],2))
        near=comp(upnew,affine(fo,M2,t2),hand)
        # Thick front lip sits above the under-hook finger; thumb remains on top.
        backfinger=(hand[:,:,3]>0)&(Y>=P[1]-3)&(X>=P[0]-18)&(X<=P[0]+17)
        sm(backfinger,d/'UNDER_EDGE_INDEX_OCCLUSION_DOMAIN_MASK.png')
        nearinfo=dict(state='NEW whole-arm / mirrored whole-pinch anatomy proxy: native redraw required',cuff=C.tolist(),elbow=E.tolist(),wrist=W.tolist(),cloth_edge_pinch=P.tolist(),whole_hand_proxy_matrix=M.tolist(),whole_hand_proxy_translation=t.tolist(),hand_proxy_source='actual066 FAR skin/ink only; mirrored whole hand, jade excluded',per_finger_transform=False,projected_upper_guide=float(np.linalg.norm(E-C)),projected_forearm_guide=float(np.linalg.norm(W-E)),not_measured_3D_bones=True)
    target=comp(base,cloth,props,lip,near,far)
    if f==84:
        lipedge=np.zeros_like(cloth);use=backfinger&(cloth[:,:,3]>0);lipedge[use]=cloth[use];target=comp(target,lipedge)
        save(lipedge,d/'REAL_FRONT_CLOTH_ABOVE_UNDERHOOK_RGBA.png')
    # Head, gaze, legs, stool are exact066 in all three technical references.
    protected=(Y<420)|(Y>=1100);target[protected]=locked[protected]
    save(far,d/'COMPLETE_FAR_ARM_JADE_HAND_TECHNICAL_GUIDE_RGBA.png');save(near,d/'COMPLETE_NEAR_ARM_HAND_TECHNICAL_GUIDE_RGBA.png')
    save(target,d/f'F{f:03d}_FULL_TECHNICAL_TARGET_NOT_NATIVE_DRAWING_RGBA.png')
    edit=nd.binary_dilation((near066[:,:,3]>0)|(far066[:,:,3]>0)|(near[:,:,3]>0)|(far[:,:,3]>0)|unknown,iterations=8)&~protected
    sm(edit,d/'COMPLETE_BOTH_ARMS_BLOUSE_NATIVE_REDRAW_MASK.png')
    # Exact original props remain present behind the occluding fold/foreground limbs.
    cover=pm&(lip[:,:,3]>128)
    sm(cover,d/'ACTUAL_TRUE_PROP_COVER_BY_FOLD_MASK.png')
    full=gray(target);annot=full.copy();ad=ImageDraw.Draw(annot)
    ad.rectangle((0,0,1024,47),fill='white');ad.text((12,8),f'F{f:03d}-{f+5:03d}: TECHNICAL INPUT ONLY / WHOLE ARMS REQUIRE NATIVE REDRAW',fill='black')
    ad.text((12,26),'Same locked066 head/gaze/props; same cotton. No new drawing or scene render.',fill='black')
    C=np.array(nearinfo['cuff']);E=np.array(nearinfo['elbow']);W=np.array(nearinfo['wrist'])
    ad.line([tuple(C),tuple(E),tuple(W)],fill='#00b7cd',width=3)
    for name,point,col in [('near cuff',C,'#007d94'),('near elbow',E,'#007d94'),('near wrist',W,'#007d94'),('SAME material C2',C2+delta,'#d52082')]:
        x,y=point;ad.ellipse((x-4,y-4,x+4,y+4),fill=col);ad.text((x+6,y-15),name,fill=col,stroke_width=1,stroke_fill='white')
    ad.line([(500,450),(548,530),(578+delta[0]*.5,574+delta[1]*.6),(642+delta[0],603+delta[1]),tuple(C2+delta)],fill='#e27b19',width=3)
    ad.ellipse((P[0]-5,P[1]-5,P[0]+5,P[1]+5),outline='#d52082',width=3);ad.text((P[0]-170,P[1]+14),'actual066 FRONT EDGE /084 pinch',fill='#b5207e',stroke_width=1,stroke_fill='white')
    if f==84: ad.text((115,1045),'Near hand is a WHOLE mirrored anatomy proxy, not final anatomy / native redraw required.',fill='#a22',stroke_width=1,stroke_fill='white')
    annot.save(d/f'F{f:03d}_BOTH_ARM_CHAINS_CONTACTS_ANNOTATED.png');full.crop((100,450,1024,1050)).save(d/'BOTH_ARMS_REAL_PROPS_CONTACTS_1TO1.png')
    # All closeups are direct crops from actual technical RGBA, never alternate poses.
    full.crop((560,620,800,820)).save(d/'FAR_PINCH_FOLD_CRANE_1TO1.png');full.crop((290,830,580,1015)).save(d/'NEAR_FRONT_EDGE_1TO1.png')
    layer=gray(comp(cloth,props,lip));layer.crop((250,650,1000,1020)).save(d/'TRUE_PUPPETS_FOUR_RODS_CLOTH_OCCLUSION_1TO1.png')
    report=dict(frame=f,exposure=[f,f+5],generation_calls=0,scene_render_calls=0,status='TECHNICAL_INPUT_PENDING_ASTRA_NATIVE_REDRAW_REQUIRED',near=nearinfo,far_same_material_pinch=(C2+delta).tolist(),far_whole_hand_jade_delta=delta.tolist(),same_cloth_source_SHA256=sha(clothp),props_source_SHA256=sha(propsp),props_geometry_changed=False,four_rods_geometry_changed=False,fold_true_prop_occlusion_pixels=int(cover.sum()),protected066_pixels_changed=int(np.any(target[protected]!=locked[protected],1).sum()),supported_lower_cloth_RGBA_changes=int(np.any(cloth[fixed_lower]!=cloth066[fixed_lower],1).sum()),cloth_inverted_triangles=meta['inverted_triangles'],near_press_exact066_RGBA=f<84,complete_native_both_arms_redraw_required=True)
    (d/'CONTACT_AND_LAYER_GATE.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report);panels.append(annot)
sheet=Image.new('RGB',(1536,800),(232,235,239));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(panels): sheet.paste(p.resize((512,768)),(512*i,32));dr.text((512*i+8,10),['072 inward/down; near presses','078 lip onto crane; near stays','084 far holds; near front-edge pinch'][i],fill='black')
sheet.save(R/'THREE_COMPLETE_TECHNICAL_TARGETS.png')
actual=gray(locked);dd=ImageDraw.Draw(actual)
for x in range(300,751,50):dd.line((x,600,x,1020),fill='#aaaaaa');dd.text((x+2,1010),str(x),fill='red')
for y in range(650,1001,50):dd.line((280,y,800,y),fill='#aaaaaa');dd.text((280,y),str(y),fill='red')
actual.crop((280,600,800,1030)).save(R/'LOCKED066_ACTUAL_CONTACT_COORDINATES_1TO1.png')
sources={str(p.relative_to(repo)):sha(p) for p in [lockedp,clothp,propsp,masterp,N/'EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png',N/'ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png']}
(R/'SOURCE_GEOMETRY_AND_ZERO_CALL_CHECK.json').write_text(json.dumps(dict(generation_calls=0,scene_render_calls=0,baseline_shared_commit='ca2deeea5b398d07ae44a8cc1f7944fce179c074',sources=sources,actual066_front_edge_y_by_x=edge,near_new_material_pinch=P.tolist(),states=reports),indent=2)+'\n')
print(json.dumps([dict(frame=r['frame'],far=r['far_same_material_pinch'],front_cover=r['fold_true_prop_occlusion_pixels'],inverted=r['cloth_inverted_triangles']) for r in reports],indent=2))
