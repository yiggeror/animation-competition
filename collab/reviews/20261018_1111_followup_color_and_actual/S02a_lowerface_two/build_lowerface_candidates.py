from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent
LUMA=np.array([.2126,.7152,.0722])
SPEC={
 'S02a_F023':{'base':'astra_s02a_semantic_masks_20261018_1042/candidates/S02a_F023.png','mouth_y':698,'chin_y':755,'refs':[('focus',.5),('tense',.5)]},
 'S02a_F044':{'base':'astra_s02a_semantic_masks_20261018_1042/candidates/S02a_F044.png','mouth_y':697,'chin_y':760,'refs':[('F041',.5),('relief',.5)]}
}
REFS={
 'focus':{'path':'astra_s05a_draw_20261018_0956/inputs/S02a_k01_focus.png','mouth_y':664,'chin_y':729},
 'tense':{'path':'astra_s02a_opening_draw_20261018/inputs/S02a_k02_tense.png','mouth_y':715,'chin_y':774},
 'F041':{'path':'astra_s02a_opening_draw_20261018/final/S02a_F041.png','mouth_y':704,'chin_y':766},
 'relief':{'path':'astra_s02a_opening_draw_20261018/inputs/S02a_k03_relief.png','mouth_y':694,'chin_y':754}
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return np.array(Image.open(W/p).convert('RGBA'))
def face_mask(a):
 y=a[:,:,:3]@LUMA;yy,xx=np.indices(y.shape);roi=(xx>640)&(xx<1040)&(yy>600)&(yy<790)
 labels,n=ndi.label((y>100)&(a[:,:,3]>240)&roi);m=labels==labels[715,840]
 assert m.sum()>20000
 assert not m[780,840],'Face leaked into neck'
 return m

def geometry(m):
 left=np.zeros(m.shape[0]);right=np.zeros(m.shape[0]);rows=np.where(m.any(1))[0]
 for y in rows:
  xs=np.where(m[y])[0];left[y]=xs.min();right[y]=xs.max()
 valid=np.where(right>left)[0];left=np.interp(np.arange(len(left)),valid,left[valid]);right=np.interp(np.arange(len(right)),valid,right[valid]);return left,right

def smooth_chroma(a,m):
 rgb=a[:,:,:3].astype(float);lum=rgb@LUMA;ch=rgb-lum[:,:,None];den=ndi.gaussian_filter(m.astype(float),sigma=9)
 return np.stack([ndi.gaussian_filter(ch[:,:,c]*m,sigma=9)/np.maximum(den,1e-8) for c in range(3)],axis=2)

refdata={}
for n,s in REFS.items():
 a=read(s['path']);m=face_mask(a);refdata[n]=(a,m,geometry(m),smooth_chroma(a,m));s['sha256']=sha(W/s['path'])
report={'purpose':'Preserve the existing S02a shot lower-face cool-shadow continuity. Not a claim that the whole character is fully neutralized.','parameters':{'face_geometry':'Own original dark-jaw bounded connected face domain, seed (840,715), x640..1040/y600..790 ROI; skin hue/saturation not used','gradient_start_y':708,'gradient_end':'per-state chin_y-4','gradient':'smoothstep(u)=3u^2-2u^3, zero first derivative at both endpoints','jaw_feather':'inside-only clip((distance to face exterior-0.5)/1.5,0,1)','reference_field':'Gaussian sigma9 normalized by each reference actual face mask, then map color field by mouth/chin vertical landmarks and per-row jaw width. Average neighboring reference chroma fields. Geometry is used only to sample color, no source pixel relocation.','luminance':'Retain each base pixel Rec.709 Y prime; gamut-limit chroma only if needed','protected':'Mouth and all y<=708, eyes/nose, black jaw line, all alpha, existing neck/collars, mask exterior'},'references':REFS,'assets':[]}
for n,s in SPEC.items():
 a=read(s['base']);shutil.copy2(W/s['base'],R/'source_copies'/f'{n}.png');rgb=a[:,:,:3].astype(float);lum=rgb@LUMA;m=face_mask(a);left,right=geometry(m);yy,xx=np.indices(lum.shape)
 u=np.clip((yy-708)/(s['chin_y']-4-708),0,1);grad=u*u*(3-2*u);edge=np.clip((ndi.distance_transform_edt(m)-.5)/1.5,0,1);weight=grad*edge
 # Explicitly protect previously frozen neck and both collars.
 for k in ['neck','collar_left','collar_right']:
  frozen=np.array(Image.open(W/'astra_s02a_semantic_masks_20261018_1042/masks'/f'{n}__{k}__binary.png'))>0;assert not np.any((weight>0)&frozen)
 sample=np.zeros(rgb.shape)
 relx=(xx-left[:,None])/np.maximum(right-left,1)[:,None]
 for ref_name,ref_weight in s['refs']:
  ra,rm,(rl,rr),rc=refdata[ref_name];rs=REFS[ref_name]
  ry=rs['mouth_y']+(yy-s['mouth_y'])*(rs['chin_y']-rs['mouth_y'])/(s['chin_y']-s['mouth_y'])
  l=np.interp(ry[:,0],np.arange(len(rl)),rl);r=np.interp(ry[:,0],np.arange(len(rr)),rr);rx=l[:,None]+relx*(r-l)[:,None]
  for ch in range(3):sample[:,:,ch]+=ref_weight*ndi.map_coordinates(rc[:,:,ch],[ry,rx],order=1,mode='nearest')
 # Remove numerical luma from interpolated chroma; target Y is always source Y.
 sample-=np.sum(sample*LUMA,axis=2)[:,:,None]
 scale=np.ones(lum.shape)
 for ch in range(3):
  pos=sample[:,:,ch]>0;neg=sample[:,:,ch]<0
  scale[pos]=np.minimum(scale[pos],(255-lum[pos])/sample[:,:,ch][pos]);scale[neg]=np.minimum(scale[neg],-lum[neg]/sample[:,:,ch][neg])
 target=lum[:,:,None]+sample*np.clip(scale,0,1)[:,:,None]
 out=a.copy();out[:,:,:3]=np.round(rgb+(target-rgb)*weight[:,:,None]).clip(0,255).astype('uint8')
 support=weight>0;changed=np.any(out!=a,axis=2);assert not np.any(changed&~support);assert np.array_equal(a[:,:,3],out[:,:,3]);assert not np.any(changed&(lum<=100));assert not np.any(changed&(yy<=708))
 assert np.abs(out[:,:,:3]@LUMA-lum).max()<.501
 Image.fromarray(out).save(R/'candidates'/f'{n}__lowerface_cool_candidate.png');Image.fromarray(m.astype('uint8')*255).save(R/'masks'/f'{n}__own_face_domain.png');Image.fromarray(support.astype('uint8')*255).save(R/'masks'/f'{n}__lowerface_support.png');Image.fromarray(np.round(weight*255).astype('uint8')).save(R/'masks'/f'{n}__gradient_weight.png');ys,xs=np.where(support); x0,y0,x1,y1=int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1; box=(slice(y0,y1),slice(x0,x1)); np.savez_compressed(R/'masks'/f'{n}__exact_chroma_application.npz',weight=weight[box],target_chroma=(sample*np.clip(scale,0,1)[:,:,None])[box],xyxy=np.array([x0,y0,x1,y1]))
 vis=rgb.copy();vis=vis*(1-.48*weight[:,:,None])+np.array([40,190,255])*(.48*weight[:,:,None]);overlay=Image.fromarray(np.round(vis).astype('uint8'))
 sheet=Image.new('RGB',(2100,715),'white');d=ImageDraw.Draw(sheet)
 for i,(lab,im) in enumerate([('BASE: fixed neck/collars; original warm lower face',Image.fromarray(a)),('EXPLICIT MASK: fades in below y708; jaw-contained',overlay),('CANDIDATE: local source-Y preserving cool continuity',Image.fromarray(out))]):
  bg=Image.new('RGBA',im.size,(60,60,60,255));bg.alpha_composite(im.convert('RGBA'));crop=bg.convert('RGB').crop((620,570,1050,820)).resize((700,407));sheet.paste(crop,(700*i,28));d.text((700*i+8,8),lab,fill='black');full=bg.convert('RGB').crop((550,420,1130,880)).resize((350,277));sheet.paste(full,(700*i+175,438))
 sheet.save(R/'qa'/f'{n}__before_mask_after.png')
 ys,xs=np.where(support);report['assets'].append({'name':n,'base_path':s['base'],'base_sha256':sha(W/s['base']),'output_sha256':sha(R/'candidates'/f'{n}__lowerface_cool_candidate.png'),'refs':s['refs'],'mouth_y':s['mouth_y'],'chin_y':s['chin_y'],'support_bbox':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'support_pixels':int(support.sum()),'changed_pixels':int(changed.sum()),'checks':{'outside_support_changed':0,'alpha_changed':0,'neck_collar_overlap':0,'mouth_eye_upperface_changed':0,'black_jaw_changed':0,'max_luma_difference':float(np.abs(out[:,:,:3]@LUMA-lum).max())}})
(R/'candidate_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['assets'],indent=2))
