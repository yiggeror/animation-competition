from pathlib import Path
from PIL import Image, ImageDraw
from scipy import ndimage as nd
import numpy as np
import json, hashlib

R=Path(__file__).resolve().parent; B=R.parent
G=B/'F036_SINGLE_CLEAN_CLOTH_MASTER_INPUT_GATE_ZERO_CALL_20261019'
U=B/'F036_SINGLE_CLEAN_CLOTH_MASTER_NATIVE_CALL01_20261019'
S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
def rgba(p): return np.array(Image.open(p).convert('RGBA'))
def mask(p): return np.array(Image.open(p).convert('L'))>0
def poly(points):
    m=Image.new('L',(1024,1536));ImageDraw.Draw(m).polygon(points,fill=255)
    return np.array(m)>0
def save_mask(name,m): Image.fromarray((m*255).astype('uint8')).save(R/name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gray(a):
    im=Image.new('RGBA',(1024,1536),(236,239,242,255));im.alpha_composite(Image.fromarray(a));return im.convert('RGB')

raw=rgba(U/'RAW_UNTOUCHED.png');old=rgba(S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png')
guide=rgba(G/'01_F036_COMPLETE_CLOTH_TARGET_TECHNICAL.png');original=rgba(G/'HARD_PROTECTED_ORIGINAL_CLOTH_RGBA.png')
face=mask(G/'WHOLE_LOCKED036_CLOTH_DOMAIN.png');genuine=mask(G/'HARD_PROTECTED_ORIGINAL_CLOTH_MASK.png')
human=mask(G/'HUMAN_BLACK_PROTECTION_GEOMETRY.png');white=mask(G/'02_ONLY_SOURCE_GAPS_WHITE_PROTECTED_BLACK.png')
yy,xx=np.indices(face.shape)
# One upper supported fold remains wholly outside the repair.  The join follows
# its actual shallow crease, below the flower groups; no rectangular source gaps
# participate in this new source selection.
upper=poly([(495,630),(780,630),(780,742),(744,741),(709,739),(670,739),(630,741),(592,740),(554,738),(518,733),(495,731)])&face&genuine
# Keep the original silhouette ink/AA and both contact notches.  RGB joins are
# inside the cotton; alpha is never crossfaded, so there is no transparent band.
edge=face&~nd.binary_erosion(face,iterations=2)&genuine
pinches=(((xx-499)**2+(yy-747)**2<=7**2)|((xx-725.78751656)**2+(yy-663.66135947)**2<=8**2))&genuine&face
# Main ridge endpoints and genuine ink on the existing ridge are fixed.  The
# middle of this fold face comes from the same single raw, not patch fragments.
ridge_line=Image.new('L',(1024,1536));ImageDraw.Draw(ridge_line).line([(725.7875,663.6614),(741,710),(769,756),(806,795),(842,835),(884,878)],fill=255,width=2)
dark=(original[:,:,0]<45)&(original[:,:,1]<65)&(original[:,:,2]<95)
ridge=(np.array(ridge_line)>0)&genuine&dark
anchors=(((xx-725.78751656)**2+(yy-663.66135947)**2<5**2)|((xx-884)**2+(yy-878)**2<3**2))&genuine&face
# The locked036 real front-lip/outer-feather T pixels are authoritative.
feather=mask(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png')
front=rgba(S/'layers/ONE_M_ACTUAL_SOFT_LIP_FRONT.png')
t=feather&(front[:,:,3]>=250)&face&(np.max(np.abs(old.astype('int16')-front.astype('int16')),2)<=2)
original[t]=old[t]
hard=edge|pinches|ridge|anchors|t
keep=upper|hard

# Carry the raw right up to the old silhouette.  Any subpixel edge shortfall is
# extended only from the nearest actual raw opaque pixel, never a texture tile.
valid=raw[:,:,3]>=250
distance,indices=nd.distance_transform_edt(~valid,return_indices=True)
raw_rgb=raw[:,:,:3].copy();edge_extend=face&~valid&~keep
raw_rgb[edge_extend]=raw[indices[0][edge_extend],indices[1][edge_extend],:3]
cloth=np.zeros_like(raw);cloth[face,:3]=raw_rgb[face];cloth[face,3]=guide[face,3]

# A short opaque color join in low-texture cotton, not an RGBA fade.  Whole
# bright motif components belong to one side, avoiding cut petals/double motifs.
dist=nd.distance_transform_edt(~keep)
w=np.clip(dist/9.0,0,1)
join=(w>0)&(w<1)&face&genuine
bright=((raw_rgb.max(2)>150)|(original[:,:,:3].max(2)>150))&genuine&face
labels,n=nd.label(nd.binary_dilation(bright,iterations=2))
for k in np.unique(labels[join&bright]):
    if k==0:continue
    c=labels==k
    # A motif touching the hard geometric anchors remains original in full.
    value=0.0 if np.any(c&hard) else float(np.median(w[c&face])>=0.5)
    w[c&face&genuine]=value
w[keep]=0;w[~genuine]=1
blend=face&genuine&(w<1)
cloth[blend,:3]=np.rint(original[blend,:3]*(1-w[blend,None])+raw_rgb[blend]*w[blend,None]).astype('uint8')
cloth[hard]=original[hard]
assert not np.any((cloth[:,:,3]>0)&human)

Image.fromarray(cloth).save(R/'F036_COMPLETE_FOLD_CLOTH_RGBA.png')
gray(cloth).save(R/'F036_COMPLETE_FOLD_CLOTH_ON_GRAY.png')
gray(cloth).crop((240,625,1024,1100)).save(R/'F036_NEW_CLOTH_NORMAL_SIZE.png')
save_mask('PRESERVED_ORIGINAL_UPPER_FOLD.png',upper)
save_mask('HARD_CONTOUR_PINCH_RIDGE_T_MASK.png',hard)
save_mask('SAME_RAW_COMPLETE_FOLD_DOMAIN.png',face&~keep)
save_mask('OPAQUE_LOW_TEXTURE_COLOR_JOIN.png',blend&~keep)
props=rgba(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')[:,:,3]>0
candidate=old.copy();candidate[face]=cloth[face];candidate[props]=old[props]
Image.fromarray(candidate).save(R/'F036_SAME_RAW_REINTEGRATED_RGBA.png')
gray(candidate).save(R/'F036_SAME_RAW_REINTEGRATED_ON_GRAY.png')
overlay=Image.blend(gray(old),gray(candidate),0.5)
overlay.crop((240,625,1024,1100)).save(R/'F036_OLD_AND_NEW_HALF_OVERLAY_NORMAL_SIZE.png')
sheet=Image.new('RGB',(1568,505),(236,239,242));d=ImageDraw.Draw(sheet)
sheet.paste(gray(cloth).crop((240,625,1024,1100)),(0,30));sheet.paste(overlay.crop((240,625,1024,1100)),(784,30))
d.text((8,8),'NEW COMPLETE FOLDS | ONE EXISTING RAW | 1:1',fill='black');d.text((792,8),'OLD036 / NEW036 HALF OVERLAY | 1:1',fill='black')
sheet.save(R/'NEW_CLOTH_AND_OLD036_OVERLAY_1TO1.png')
changed=np.any(candidate!=old,2)
report={'generation_calls':0,'unique_texture_raw':str(U/'RAW_UNTOUCHED.png'),'raw_SHA256':sha(U/'RAW_UNTOUCHED.png'),'old036_SHA256':sha(S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'),'cloth_SHA256':sha(R/'F036_COMPLETE_FOLD_CLOTH_RGBA.png'),'candidate_SHA256':sha(R/'F036_SAME_RAW_REINTEGRATED_RGBA.png'),'one_complete_fold_repair_attempt':1,'face_pixels':int(face.sum()),'original_upper_fold_pixels':int(upper.sum()),'hard_geometry_pixels':int(hard.sum()),'hard_RGBA_changes':int(np.any(cloth[hard]!=original[hard],1).sum()),'same_raw_fold_pixels':int((face&~keep).sum()),'low_texture_opaque_color_join_pixels':int((blend&~keep).sum()),'edge_extension_pixels':int(edge_extend.sum()),'maximum_edge_extension_distance':float(distance[edge_extend].max()) if edge_extend.any() else 0,'cloth_alpha_equal_locked_domain':bool(np.array_equal(cloth[:,:,3],guide[:,:,3])),'human_RGBA_changes':int((changed&human).sum()),'true_prop_RGBA_changes':int((changed&props).sum()),'RGBA_changes_outside_original_cloth_domain':int((changed&~face).sum()),'visual_gate':'PENDING_ACTUAL_NORMAL_SIZE_REVIEW'}
(R/'F036_COMPOSITION_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
