"""Zero-generation whole072 shoulder/sleeve/cuff semantic reuse, one old affine."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
from scipy import ndimage as nd
R=Path(__file__).resolve().parent;B=R.parent
P=B/'F072_F078_F084_NATIVE_call01_each_from_38c5ba63_20261019'
H=B/'F066_F089_COMPLETE_FAR_SLEEVE_FINAL_ZERO_CALL_20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:np.array(Image.open(p).convert('RGBA'))
rawp=P/'F072/originals/S29_F072_call01_RAW_UNTOUCHED.png';raw=load(rawp)
oldp=H/'F072_FINAL_RGBA.png';old=load(oldp)
reg=json.loads((P/'F072/reintegration_v3_locked_hold/SOURCE_CONTACT_AND_REUSE_CHECK.json').read_text())['one_whole_far_group_registration']
M=np.array(reg['matrix']);t=np.array(reg['translation'])
Y,X=np.indices(raw.shape[:2]);xy=np.stack([X,Y],2)
# Internal seam is wholly within blue garment, torso side of the real ink seam.
# Dynamic path avoids BOTH images' white blossoms and dark ink; never an outer crop.
ys=np.arange(380,571);xs=np.arange(455,491);guide=np.interp(ys,[380,430,480,530,570],[477,477,469,468,468]);XX,YY=np.meshgrid(xs,ys)
tp=np.stack([XX,YY],2)@M.T+t;tx=np.rint(tp[:,:,0]).astype(int);ty=np.rint(tp[:,:,1]).astype(int)
s=raw[YY,XX].astype(float);b=old[ty,tx].astype(float)
blue=(s[:,:,2]>s[:,:,0]+25)&(s[:,:,1]>90)&(s[:,:,3]>200)
bb=(b[:,:,2]>b[:,:,0]+20)&(b[:,:,1]>90)&(b[:,:,3]>128)
sw=nd.binary_dilation((raw[:,:,0]>170)&(raw[:,:,1]>175)&(raw[:,:,2]>185)&(raw[:,:,3]>128),iterations=3)
bw=nd.binary_dilation((old[:,:,0]>170)&(old[:,:,1]>175)&(old[:,:,2]>185)&(old[:,:,3]>128),iterations=3)
cost=((XX-guide[:,None])/5)**2+np.mean(np.abs(s[:,:,:3]-b[:,:,:3]),2)/30+300*(~blue)+120*(~bb)+500*sw[YY,XX]+300*bw[ty,tx]
cost[np.abs(XX-guide[:,None])>9]+=10000
dp=cost.copy();back=np.zeros(cost.shape,dtype=int)
for j in range(1,len(ys)):
 for i in range(len(xs)):
  lo=max(0,i-1);hi=min(len(xs),i+2);k=lo+int(np.argmin(dp[j-1,lo:hi]));dp[j,i]+=dp[j-1,k];back[j,i]=k
idx=int(np.argmin(dp[-1]));path=[]
for j in reversed(range(len(ys))):path.append((int(xs[idx]),int(ys[j])));idx=int(back[j,idx])
path=list(reversed(path))
# Top closure stays beyond the actual shoulder root/outer sleeve, clear of face.
polygon=path+[(490,620),(740,620),(760,400),(600,330),(530,330),(490,359)]
mask=Image.new('L',(1024,1536));ImageDraw.Draw(mask).polygon(polygon,fill=255);domsrc=np.array(mask)>0
fragment=np.zeros_like(raw);fragment[domsrc]=raw[domsrc]
assert np.array_equal(fragment[domsrc],raw[domsrc])
Image.fromarray(fragment).save(R/'ORIGINAL072_COMPLETE_SHOULDER_SLEEVE_CUFF_UPPER_ARM_RGBA.png');mask.save(R/'ORIGINAL072_WHOLE_SEMANTIC_DOMAIN.png')
co=(xy-t)@np.linalg.inv(M).T
def sample(a):
 q=a.astype(float);q[:,:,:3]*=q[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(q[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
 z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8)
 z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
registered=sample(raw);regfragment=sample(fragment)
dom=nd.map_coordinates(domsrc.astype(float),[co[:,:,1],co[:,:,0]],order=0,mode='constant',cval=0)>.5
# Finish the proximal transition before the locked elbow/wrist/jade/hand domain.
# Existing lower arm uses this exact same affine; no coordinate change anywhere.
dom&=Y<600
new=old.copy();new[dom]=registered[dom]
assert np.array_equal(new[~dom],old[~dom]) and np.array_equal(new[Y>=600],old[Y>=600])
Image.fromarray(new).save(R/'F072_COMPLETE_SLEEVE_FINAL_RGBA.png')
Image.fromarray((dom*255).astype('uint8')).save(R/'ONE_OLD_MATRIX_REGISTERED_WHOLE_SEMANTIC_DOMAIN.png')
Image.fromarray(regfragment).save(R/'ONE_OLD_MATRIX_REGISTERED_COMPLETE_SOURCE_FRAGMENT_RGBA.png')
def gray(a):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
for f in [66,78,84]:shutil.copyfile(H/(f'F{f:03d}_UNCHANGED_LOCKED_RGBA.png' if f==66 else f'F{f:03d}_FINAL_RGBA.png'),R/f'F{f:03d}_UNCHANGED_LOCKED_RGBA.png')
for f in[72,78,84]:
 p=R/('F072_COMPLETE_SLEEVE_FINAL_RGBA.png' if f==72 else f'F{f:03d}_UNCHANGED_LOCKED_RGBA.png');im=gray(load(p))
 im.save(R/f'F{f:03d}_FULL_ON_GRAY.png');im.crop((70,275,810,1040)).save(R/f'F{f:03d}_BOTH_ARMS_SHOULDERS_AXILLA_ELBOW_WRIST_1TO1.png')
 im.crop((440,330,700,730)).resize((520,800)).save(R/f'F{f:03d}_WHOLE_FAR_CHAIN_2X.png')
report={'generation_calls':0,'original_raw072':str(rawp),'original_raw072_SHA256':sha(rawp),'old072_SHA256':sha(oldp),'final072_SHA256':sha(R/'F072_COMPLETE_SLEEVE_FINAL_RGBA.png'),'one_exact_existing_whole_far_arm_matrix':reg,'source_polygon':polygon,'internal_blue_seam_path_source':path,'source_fragment_RGBA_including_alpha_exact':True,'black_outline_painted':False,'small_rectangle_gap_fill':False,'sleeve_stretched':False,'transformed_contacts_changed':False,'outside_whole_semantic_domain_changed_pixels':int(np.any(new[~dom]!=old[~dom],1).sum()),'all_y600_plus_RGBA_changes':int(np.any(new[Y>=600]!=old[Y>=600],1).sum()),'wrists_jade_hands_clamp_cotton_props_four_rods_unchanged':True,'changed_pixels':int(np.any(new!=old,2).sum()),'locked_states':[{'state':f,'SHA256':sha(R/f'F{f:03d}_UNCHANGED_LOCKED_RGBA.png')}for f in[66,78,84]],'status':'PENDING_ACTUAL_COMPLETE_IMAGE_VIEW'}
(R/'ORIGINAL072_WHOLE_SLEEVE_SAME_MATRIX_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in['source_polygon','internal_blue_seam_path_source']},ensure_ascii=False,indent=2))
