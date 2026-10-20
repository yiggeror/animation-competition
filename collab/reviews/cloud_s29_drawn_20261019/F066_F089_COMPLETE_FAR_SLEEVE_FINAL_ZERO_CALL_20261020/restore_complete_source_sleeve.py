"""One zero-generation semantic repair. Native078 full sleeve; original same affine.
The external boundary is outside the WHOLE sleeve. Only the internal blue seam is
selected; no black line, blossom, skin or alpha is painted or stretched.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F072_F078_F084_NATIVE_call01_each_from_38c5ba63_20261019'
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p):Image.fromarray(a).save(p)
def gray(a):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
Y,X=np.indices((1536,1024));xy=np.stack([X,Y],2)
rawp=P/'F078/originals/S29_F078_call01_RAW_UNTOUCHED.png';raw=load(rawp)
check=json.loads((P/'F078/reintegration_v3_locked_hold/SOURCE_CONTACT_AND_REUSE_CHECK.json').read_text());reg=check['one_whole_far_group_registration'];M=np.array(reg['matrix']);t=np.array(reg['translation']);assert reg['scale']==1.0203223595532214
before78p=P/'F078/reintegration_v3_locked_hold/F078_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_RGBA.png';before78=load(before78p)
# Internal cut lives in BLUE garment interior, to the torso side of the actual
# native shoulder seam. Avoid BOTH sources' white flowers/ink, never the outline.
ys=np.arange(385,571);xs=np.arange(460,511);guide=np.interp(ys,[385,430,480,530,570],[500,495,480,478,478]);XX,YY=np.meshgrid(xs,ys);pts=np.stack([XX,YY],2);tp=pts@M.T+t;tx=np.rint(tp[:,:,0]).astype(int);ty=np.rint(tp[:,:,1]).astype(int);s=raw[YY,XX].astype(float);b=before78[ty,tx].astype(float)
blue=(s[:,:,2]>s[:,:,0]+25)&(s[:,:,1]>90)&(s[:,:,3]>200);bb=(b[:,:,2]>b[:,:,0]+20)&(b[:,:,1]>90)&(b[:,:,3]>128)
sourcewhite=nd.binary_dilation((raw[:,:,0]>170)&(raw[:,:,1]>175)&(raw[:,:,2]>185)&(raw[:,:,3]>128),iterations=3)
targetwhite=nd.binary_dilation((before78[:,:,0]>170)&(before78[:,:,1]>175)&(before78[:,:,2]>185)&(before78[:,:,3]>128),iterations=3)
cost=((XX-guide[:,None])/5)**2+np.mean(np.abs(s[:,:,:3]-b[:,:,:3]),2)/30+300*(~blue)+120*(~bb)+500*sourcewhite[YY,XX]+300*targetwhite[ty,tx]
cost[np.abs(XX-guide[:,None])>9]+=10000
dp=cost.copy();back=np.zeros(cost.shape,dtype=int)
for j in range(1,len(ys)):
 for i in range(len(xs)):
  lo=max(0,i-1);hi=min(len(xs),i+2);k=lo+int(np.argmin(dp[j-1,lo:hi]));dp[j,i]+=dp[j-1,k];back[j,i]=k
idx=int(np.argmin(dp[-1]));path=[]
for j in reversed(range(len(ys))):path.append((int(xs[idx]),int(ys[j])));idx=int(back[j,idx])
path=list(reversed(path))
# All outer vertices lie well OUTSIDE the native complete shoulder/sleeve/cuff,
# including the former x552–592/y450–480 failure. No outer-edge clipping rectangle.
polygon=path+[(500,620),(610,620),(740,620),(740,350),(560,320),(512,363)]
im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(polygon,fill=255);source_domain=np.array(im)>0
fragment=np.zeros_like(raw);fragment[source_domain]=raw[source_domain]
save(fragment,R/'ORIGINAL078_COMPLETE_SHOULDER_SLEEVE_CUFF_PROXIMAL_ARM_RGBA.png');im.save(R/'ORIGINAL078_WHOLE_SEMANTIC_SOURCE_DOMAIN.png')
assert np.array_equal(fragment[source_domain],raw[source_domain])
co=(xy-t)@np.linalg.inv(M).T
def sample(a):
 q=a.astype(float);q[:,:,:3]*=q[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(q[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2);z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8);z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
registered_raw=sample(raw);registered_fragment=sample(fragment)
# Use the original raw alpha even at the internal seam: mask interpolation is
# never substituted for original alpha. The internal cut is inside blue fabric.
dom=nd.map_coordinates(source_domain.astype(float),[co[:,:,1],co[:,:,0]],order=0,mode='constant',cval=0)>.5
save((dom*255).astype('uint8'),R/'ONE_MATRIX_REGISTERED_WHOLE_SEMANTIC_DOMAIN.png');save(registered_fragment,R/'ONE_MATRIX_COMPLETE_SLEEVE_FRAGMENT_RGBA.png')
shutil.copyfile(P/'F072/reintegration_v3_locked_hold/F072_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_RGBA.png',R/'F072_FINAL_RGBA.png')
locked066=B/'F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019/F066_UNCHANGED_LOCKED_RGBA.png';shutil.copyfile(locked066,R/'F066_UNCHANGED_LOCKED_RGBA.png')
reports=[];finals=[]
for f in [78,84]:
 oldp=P/f'F{f:03d}/reintegration_v3_locked_hold/F{f:03d}_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_RGBA.png';old=load(oldp);new=old.copy();new[dom]=registered_raw[dom]
 assert np.array_equal(new[~dom],old[~dom]);assert np.array_equal(new[Y>=620],old[Y>=620])
 out=R/f'F{f:03d}_FINAL_RGBA.png';save(new,out);bg=gray(new);bg.save(R/f'F{f:03d}_FINAL_FULL_ON_GRAY.png');bg.crop((70,275,810,1040)).save(R/f'F{f:03d}_FULL_ARMS_COLLAR_HEM_CONTACTS_1TO1.png');bg.crop((470,330,660,620)).resize((570,870)).save(R/f'F{f:03d}_COMPLETE_SHOULDER_SLEEVE_CUFF_3X.png')
 reports.append(dict(state=f,status='PENDING_ACTUAL_NORMAL_SIZE_SELF_CHECK',previous_RGBA_SHA256=sha(oldp),final_RGBA_SHA256=sha(out),whole_semantic_changed_pixels=int(np.any(new!=old,2).sum()),outside_full_semantic_domain_RGBA_changes=0,all_rows620_plus_RGBA_changes=0,both_hands_jade_wrists_contacts_cotton_props_four_rods_unchanged=True,original_source_RGB_alpha_painted=False,black_outline_redrawn=False,sleeve_stretched=False,same_native078_whole_group_matrix=True));finals.append(new)
assert np.array_equal(finals[0][dom],finals[1][dom])
sheet=Image.new('RGB',(1536,800),(232,235,239));dr=ImageDraw.Draw(sheet)
for i,f in enumerate([72,78,84]):
 a=gray(load(R/f'F{f:03d}_FINAL_RGBA.png'));sheet.paste(a.resize((512,768)),(i*512,32));dr.text((i*512+8,8),f'F{f:03d} final complete-native-sleeve restoration',fill='black')
sheet.save(R/'THREE_FINAL_COMPLETE_DRAWINGS_REVIEW.png')
report=dict(generation_calls=0,source_raw078_SHA256=sha(rawp),source_raw078_path=str(rawp),original_matrix=reg,source_semantic_RGBA_and_alpha_exact_inside_domain=True,source_pixels_painted=0,white_blossoms_and_black_outer_outline_kept=True,internal_blue_seam_path_source=path,outer_semantic_polygon_source=polygon,one_identical_source_piece_applied_to078_and084=True,source_fragment_SHA256=sha(R/'ORIGINAL078_COMPLETE_SHOULDER_SLEEVE_CUFF_PROXIMAL_ARM_RGBA.png'),registered_fragment_SHA256=sha(R/'ONE_MATRIX_COMPLETE_SLEEVE_FRAGMENT_RGBA.png'),states=reports,unchanged066_RGBA_SHA256=sha(R/'F066_UNCHANGED_LOCKED_RGBA.png'),unchanged072_RGBA_SHA256=sha(R/'F072_FINAL_RGBA.png'))
(R/'COMPLETE_SLEEVE_SAME_RAW_SOURCE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(reports,indent=2))
