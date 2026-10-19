"""Three explicit same-raw semantic repairs. No model, pose, or scene work."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy import ndimage as ndi
from scipy.interpolate import PchipInterpolator
import numpy as np
import hashlib,json

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
SRC1=BASE/'generation_001/S20_F000_call001_raw.png'
SRC3=BASE/'generation_003_correct_pose/S20_F000_call003_correct_pose_raw.png'
BEFORE=BASE/'generation_003_correct_pose/S20_F000_call003_white_composite_candidate.png'
for n in ['masks','weights','qa']:(ROOT/n).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC1)=='de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330'
assert sha(SRC3)=='6eb8ed6145da4cf9a053993c383ae66f80b474d1a4f8b131a89cfd9e3fd6b204'
assert sha(BEFORE)=='8d628e5fa1d5c8d69aaea749c37cd2b9b1fe14b971d6b38f8efa4a37f8add433'
A=np.array(Image.open(SRC1).convert('RGBA')).astype(float)
B=np.array(Image.open(SRC3).convert('RGBA')).astype(float)
C=np.array(Image.open(BEFORE).convert('RGBA')).astype(float)
assert A.shape==B.shape==C.shape==(941,1672,4)
Y,X=np.mgrid[:941,:1672]
def box(b):
    x0,y0,x1,y1=b
    return (X>=x0)&(X<x1)&(Y>=y0)&(Y<y1)
def poly(points):
    im=Image.new('L',(1672,941));ImageDraw.Draw(im).polygon(points,fill=255)
    return np.array(im)>0
def mask_save(name,m):Image.fromarray(np.where(m,255,0).astype('uint8')).save(ROOT/'masks'/name)
def weight_save(name,m):Image.fromarray(np.rint(np.clip(m,0,1)*255).astype('uint8')).save(ROOT/'weights'/name)
def skin(a):
    return (a[:,:,3]>40)&(a[:,:,0]>170)&(a[:,:,0]>a[:,:,1]+24)&(a[:,:,1]>a[:,:,2]+13)
def smooth(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)

LBOX=[970,358,1018,410];RBOX=[974,416,1031,470];TBOX=[1018,398,1200,520]
Lp=poly([(887,280),(941,280),(962,295),(976,322),(977,341),
         (969,355),(953,360),(934,354),(912,353),(891,337)])
Rp=poly([(897,426),(911,418),(935,412),(948,414),(964,420),(978,422),
         (978,456),(968,462),(957,468),(945,474),(932,475),(920,472),(910,463),(900,454)])
Rp |= np.array(Image.open(BASE/'arm_correction_002_no_oldarms/masks_local/protect_R_palm.png'))>0
Rp |= box([974,416,979,470])
jade_core=(C[:,:,3]>8)&(C[:,:,1]>C[:,:,0]+9)&(C[:,:,1]>C[:,:,2]+4)&box([950,320,1000,382])
jade=ndi.binary_dilation(jade_core,iterations=2)&box([950,320,1000,382])
rods=np.array(Image.open(BASE/'arm_correction_002_no_oldarms/masks_local/protect_four_front_rods.png'))>0
true_protect=Lp|Rp|jade|rods|(X<835)
mask_save('true_L_palm.png',Lp);mask_save('true_R_palm.png',Rp)
mask_save('true_jade_with_ink_AA.png',jade);mask_save('palms_jade_four_front_rods_child.png',true_protect)

# 1: Small contour remap of the real003 wrist edge, fixed to the old true wrist.
# Premultiplied sampling avoids importing invisible RGB fringes.
def sample_edge(raw,xrange,top,bottom,oldtop,oldbottom):
    out=raw.copy()
    for x in xrange:
        yy=np.arange(941,dtype=float)
        old_h=max(oldbottom[x]-oldtop[x],1)
        new_h=max(bottom[x]-top[x],1)
        mapped=oldtop[x]+(yy-top[x])*old_h/new_h
        aa=raw[:,x,3]/255
        alpha=ndi.map_coordinates(aa,[mapped],order=1,mode='nearest')
        prem=raw[:,x,:3]*aa[:,None]
        color=np.stack([ndi.map_coordinates(prem[:,i],[mapped],order=1,mode='nearest') for i in range(3)],axis=1)
        color=np.divide(color,alpha[:,None],out=np.zeros_like(color),where=alpha[:,None]>1e-6)
        out[:,x,:3]=color;out[:,x,3]=alpha*255
    return out

def bounds(raw,xs,yrange):
    lo=np.zeros(1672);hi=np.zeros(1672)
    for x in xs:
        ys=np.array(list(yrange));q=ys[raw[ys,x,3]>=128]
        assert len(q)
        lo[x]=q[0]-.5;hi[x]=q[-1]+.5
    return lo,hi

xs=range(970,1018)
oldlo,oldhi=bounds(B,xs,range(358,410))
newlo=oldlo.copy();newhi=oldhi.copy()
curve=PchipInterpolator([970,974,979,985,992,1004,1017],
                        [372.5,372.5,374.1,377.4,382.5,390.5,398.5])
for x in xs:newhi[x]=float(curve(x))
Ldata=sample_edge(B,xs,newlo,newhi,oldlo,oldhi)
LM=box(LBOX)&~true_protect
# Only the wrist/forearm and the old tiny exposed tail below it are editable.
# Transparent space beyond the clean contour is explicitly cleared locally.
for x in xs:Ldata[np.arange(941)>newhi[x]+1.1,x]=0
common=box([974,358,987,373])&skin(A)&skin(B)&~jade&(A[:,:,3]>240)&(B[:,:,3]>240)
deltaL=np.median(A[common,:3]-B[common,:3],axis=0) if common.any() else np.zeros(3)
skinL=skin(Ldata)&LM
mixL=1-smooth((X-978)/40)
Ldata[:,:,:3][skinL]+=deltaL[None,:]*mixL[skinL,None]

# 2: Keep the true low palm; join its whole short forearm to the 003 body edge.
chest=(C[:,:,3]>100)&(C[:,:,2]>C[:,:,1]+10)&(C[:,:,1]>C[:,:,0]+8)&box([1018,410,1031,470])
chest=ndi.binary_dilation(chest,iterations=1)&box([1018,410,1031,470])
RM=box(RBOX)&~true_protect&~chest
RM &= X<1027
xr=range(978,1027)
rlo,rhi=bounds(B,xr,range(416,470))
rtop=rlo.copy();rbot=rhi.copy()
tc=PchipInterpolator([978,988,1003,1015,1026],[428.1,427.9,426.6,425.5,424.5])
bc=PchipInterpolator([978,986,1002,1015,1026],[462.1,462.7,463.8,464.6,465.5])
for x in xr:rtop[x]=float(tc(x));rbot[x]=float(bc(x))
Rdata=sample_edge(B,xr,rtop,rbot,rlo,rhi)
# A continuous subpixel matte uses the real003 edge ink / inner skin colors.
# It avoids alternating alpha teeth from integer threshold-boundary remapping.
edge_samples=[]
for x in range(982,1024):
    for yy in [int(round(rlo[x]+.5)),int(round(rhi[x]-.5))]:
        for sy in range(yy-1,yy+2):
            if B[sy,x,3]>128 and B[sy,x,0]<190:edge_samples.append(B[sy,x,:3])
inkR=np.median(np.array(edge_samples),axis=0)
for x in xr:
    yy=np.arange(941,dtype=float)
    v=np.minimum(yy-rtop[x],rbot[x]-yy)
    coverage=np.clip(v+.5,0,1)
    bodyfrac=smooth((v-.1)/1.25)
    old_h=max(rhi[x]-rlo[x],1);new_h=max(rbot[x]-rtop[x],1)
    mapped=np.clip(rlo[x]+(yy-rtop[x])*old_h/new_h,rlo[x]+2.3,rhi[x]-2.3)
    inner=np.stack([ndi.map_coordinates(B[:,x,k],[mapped],order=1,mode='nearest') for k in range(3)],axis=1)
    Rdata[:,x,:3]=inkR[None,:]*(1-bodyfrac[:,None])+inner*bodyfrac[:,None]
    Rdata[:,x,3]=coverage*253
    Rdata[coverage==0,x]=0
hand_sample=box([969,434,978,455])&skin(A)&skin(B)&(A[:,:,3]>240)&(B[:,:,3]>240)
deltaR=np.median(A[hand_sample,:3]-B[hand_sample,:3],axis=0)
mixR=1-smooth((X-978)/49)
skinR=skin(Rdata)&RM
Rdata[:,:,:3][skinR]+=deltaR[None,:]*mixR[skinR,None]

# 3: One whole visible garment piece, protecting arms/cuffs and outer contour.
skin_guard=ndi.binary_dilation(skin(C),iterations=3)
opaque_interior=ndi.binary_erosion(C[:,:,3]>=240,iterations=3)
cuff=poly([(1090,360),(1195,375),(1195,403),(1160,410),(1090,385)])
TM=box(TBOX)&opaque_interior&~skin_guard&~cuff&~true_protect
labels,n=ndi.label(TM)
seed=labels[490,1100];assert seed>0
TM=labels==seed
assert not (TM&skin(C)).any()

# Old001 contributes only confirmed lower blue/white cloth at same coordinates.
old_skin_guard=ndi.binary_dilation(skin(A),iterations=4)
old_material=((A[:,:,1]>A[:,:,0]+5)&(A[:,:,2]>A[:,:,1]+5))|\
             ((A[:,:,:3].min(axis=2)>180))|\
             ((A[:,:,0]<100)&(A[:,:,1]<145)&(A[:,:,2]<190))
confirmed001=TM&(Y>=456)&(A[:,:,3]>=240)&~old_skin_guard&old_material
w001=smooth((Y-448)/57)*confirmed001
# Do not import the old half-hidden button at the former arm edge.
w001[box([1035,448,1051,480])]=0
# Preserve the real lower vertical fold, at its original x coordinate.
fold001=confirmed001&box([1051,456,1057,520])
w001[fold001]=1

flower_records=[]
flower_masks=[]
for role,donor,center_rule in [('003_upper',B,lambda cy:cy<465),('001_lower',A,lambda cy:cy>=465)]:
    white=(donor[:,:,:3].min(axis=2)>185)&(donor[:,:,0]>185)&box(TBOX)&TM
    grouped=ndi.binary_dilation(white,iterations=3)
    lab,num=ndi.label(grouped)
    for j in range(1,num+1):
        comp=(lab==j)&white
        yy,xx=np.where(comp)
        if len(xx)<5:continue
        cy=float(yy.mean())
        if not center_rule(cy):continue
        fm=ndi.binary_dilation(comp,iterations=2)&TM
        if role=='001_lower':fm &= confirmed001
        flower_masks.append((role,fm))
        flower_records.append({'source':role,'white_pixels':int(comp.sum()),
            'source_bbox_xyxy':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
            'AA_mask_pixels':int(fm.sum()),'source_coordinates_unchanged':True})
        w001[fm]=1 if role=='001_lower' else 0

D=B[:,:,:3]*(1-w001[:,:,None])+A[:,:,:3]*w001[:,:,None]
# Normalized broad fabric field smooths the y469 cut without smearing flowers.
fabric=TM&(D[:,:,0]>90)&(D[:,:,0]<190)&(D[:,:,1]>D[:,:,0]+6)&(D[:,:,2]>D[:,:,1]+7)
den=ndi.gaussian_filter(fabric.astype(float),sigma=(10,12))
bg=np.zeros_like(D)
for k in range(3):bg[:,:,k]=ndi.gaussian_filter(D[:,:,k]*fabric,sigma=(10,12))/np.maximum(den,1e-6)
bright=np.max(D-bg,axis=2)
dark=np.max(bg-D,axis=2)
feature=np.maximum(smooth((bright-9)/25),smooth((dark-12)/28))
for role,fm in flower_masks:feature[fm]=1
band=np.sin(np.clip((Y-430)/75,0,1)*np.pi)**2
band[(Y<=430)|(Y>=505)]=0
cloth=D*(1-(band*(1-feature))[:,:,None])+bg*(band*(1-feature))[:,:,None]
# Fade in the same-coordinate secondary fold rather than retaining a hard cap.
fold_strength=smooth((Y-470)/25)
cloth[fold001]=bg[fold001]*(1-fold_strength[fold001,None])+A[:,:,:3][fold001]*fold_strength[fold001,None]
# Connect the actual003 primary fold through the old horizontal boundary.
# Only the003 upper fold profile moves subpixel;001 lower texture stays at its
# original coordinates. This is part of the single whole-garment operation.
fold_profile_moves=[]
profile_rows=[]
for sy in range(433,456):
    xx0=np.arange(1038,1049)
    center=int(xx0[np.argmin(B[sy,xx0,:3].mean(axis=1))])
    offsets=np.arange(-4,5)
    row=B[sy,center+offsets,:3]
    blue=(row[0]+row[-1])/2
    profile_rows.append(row-blue)
real003_ink_profile=np.median(np.stack(profile_rows),axis=0)
for y in range(448,480):
    xx=np.arange(1038,1050)
    lum=B[y,xx,:3].mean(axis=1)
    weights=np.maximum(np.percentile(lum,80)-lum-10,0)
    if weights.sum()<1:continue
    old_center=float((weights*xx).sum()/weights.sum())
    desired_center=1042+float(smooth((y-448)/32))
    shift=old_center-desired_center
    mapped=xx+shift
    # Copy the actual003 stroke cross-section through weak/cut rows; original
    # blue cloth remains the base, and001 lower line/pattern never moves.
    profile_delta=np.stack([np.interp(xx-desired_center,np.arange(-4,5),real003_ink_profile[:,k],left=0,right=0) for k in range(3)],axis=1)
    for i,x in enumerate(xx):
        if TM[y,x]:cloth[y,x]=np.clip(bg[y,x]+profile_delta[i],0,255)
    fold_profile_moves.append({'y':y,'source003_center_x':old_center,'joined_center_x':desired_center,'source001_shifted':False})
# Whole white flowers, including AA, always come from one actual source.
for role,fm in flower_masks:cloth[fm]=(B if role=='003_upper' else A)[:,:,:3][fm]
# Exact lower connection to original001 cloth, y505–519, inside the semantic piece.
lower_exact=TM&(Y>=505)&confirmed001
cloth[lower_exact]=A[:,:,:3][lower_exact]
strength=smooth(ndi.distance_transform_edt(TM)/5)
Tdata=C.copy();Tdata[:,:,:3]=C[:,:,:3]*(1-strength[:,:,None])+cloth*strength[:,:,None]
Tdata[lower_exact]=A[lower_exact]
# Keep complete source flower pixels rather than feathering through a petal.
for role,fm in flower_masks:Tdata[fm]=(B if role=='003_upper' else A)[fm]

OUT=C.copy();OUT[LM]=Ldata[LM];OUT[RM]=Rdata[RM];OUT[TM]=Tdata[TM]
OUT=np.rint(np.clip(OUT,0,255)).astype('uint8')
union=LM|RM|TM
assert not (LM&RM).any() and not (LM&TM).any() and not (RM&TM).any()
assert not (union&true_protect).any()
assert np.array_equal(OUT[~union],C.astype('uint8')[~union])
assert np.array_equal(OUT[true_protect],C.astype('uint8')[true_protect])
outpath=ROOT/'S20_F000_call003_semantic_repair_candidate.png'
Image.fromarray(OUT).save(outpath)
mask_save('01_near_L_wrist.png',LM);mask_save('02_far_R_forearm.png',RM)
mask_save('03_visible_front_cloth.png',TM);mask_save('all_three_semantic_union.png',union)
mask_save('protect_outside_semantics.png',~union)
mask_save('cloth_001_confirmed_source_only.png',confirmed001&(w001>0))
mask_save('shirt_new_arms_cuffs_guard.png',skin_guard|cuff)
weight_save('cloth_001_contribution.png',w001*TM)
weight_save('cloth_blue_background_transition.png',band*(1-feature)*TM)
weight_save('cloth_semantic_edge_feather.png',strength)

delta=np.any(OUT!=C,axis=2)
report={'baseline_commit':'92e74891c29d3453488d8fdc4d73297ece159b15',
    'source001_SHA256':sha(SRC1),'source003_SHA256':sha(SRC3),'before_SHA256':sha(BEFORE),
    'candidate_SHA256':sha(outpath),'canvas':[1672,941],'new_model_calls':0,
    'ROIs_half_open':{'L':LBOX,'R':RBOX,'cloth':TBOX},
    'mask_counts':{'L':int(LM.sum()),'R':int(RM.sum()),'cloth':int(TM.sum()),'union':int(union.sum())},
    'changed_counts':{'L':int((delta&LM).sum()),'R':int((delta&RM).sum()),'cloth':int((delta&TM).sum()),
        'outside_union':int((delta&~union).sum()),'protected_palms_jade_rods_child':int((delta&true_protect).sum())},
    'source_skin_to_cloth_pixels':int(((w001>0)&old_skin_guard).sum()),
    'source001_cloth_donor_min_y':int(Y[w001>0].min()),
    'source001_coordinates_unchanged':True,'lower001_y505_519_exact_pixels':int(lower_exact.sum()),
    'color_offset_near_L_from_real_wrist':deltaL.tolist(),'color_offset_far_R_from_real_palm':deltaR.tolist(),
    'R_edge_ink_from_actual003':inkR.tolist(),
    'upper003_fold_profile_join':fold_profile_moves,
    'upper003_real_ink_profile_source_rows':[433,455],
    'flower_components':flower_records,
    'methods':{'L':'Real003 premultiplied edge sampling, monotone true-wrist boundary and local skin-color join; remove only authorized wrist tail.',
        'R':'Real003 whole short forearm edge remap and skin join to fixed original palm; chest excluded.',
        'cloth':'One visible garment semantic piece;003 upper, confirmed001 lower same-coordinate cloth. Broad blue-fabric transition; whole flower components retained; original fold retained; exact lower505–519 connection.'},
    'not_done':['new image generation','neck color changes','global alpha cleanup','later poses','scene/camera/EDL/audio changes'],
    'production_ready':False}
(ROOT/'repair_provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['candidate_SHA256','mask_counts','changed_counts','source_skin_to_cloth_pixels','color_offset_near_L_from_real_wrist','color_offset_far_R_from_real_palm']},ensure_ascii=False,indent=2))

def gray(im):
    bg=Image.new('RGBA',im.size,(140,140,140,255));bg.alpha_composite(im.convert('RGBA'));return bg.convert('RGB')
beforegray=gray(Image.fromarray(C.astype('uint8')));aftergray=gray(Image.fromarray(OUT))
aftergray.save(ROOT/'qa/repaired_full_gray.png')
font=ImageFont.truetype(str(ROOT.parents[4]/'assets/fonts/NotoSansSC-VF.ttf'),25)
for tag,bounds_ in [('near_L',(960,345,1030,415)),('far_R',(960,405,1040,480)),('cloth',(1000,385,1220,535))]:
    w=(bounds_[2]-bounds_[0])*4;h=(bounds_[3]-bounds_[1])*4
    board=Image.new('RGB',(2*(w+18),h+65),'#f0f2f4');d=ImageDraw.Draw(board)
    for i,(title,im) in enumerate([('修复前',beforegray),('三语义修复后',aftergray)]):
        x=5+i*(w+18);d.text((x,8),title,font=font,fill='#263743');board.paste(im.crop(bounds_).resize((w,h),Image.Resampling.NEAREST),(x,60))
    board.save(ROOT/'qa'/(tag+'_before_after.png'))
overlay=np.array(beforegray).astype(float)
for mask,color in [(LM,[230,80,70]),(RM,[80,180,120]),(TM,[75,130,230])]:overlay[mask]=overlay[mask]*.5+np.array(color)*.5
Image.fromarray(np.rint(overlay).astype('uint8')).save(ROOT/'qa/three_semantic_masks_overlay.png')
