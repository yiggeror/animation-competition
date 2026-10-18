from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math
b=Path(__file__).resolve().parents[3];o=b/'repairs/d12_local_call21';pp=b/'repairs/d12_pixel_preplace';src=Image.open(pp/'references/d12_preplace_local.png').convert('RGBA');raw=Image.open(o/'originals/S03b_d12_call21_local_original.png').convert('RGBA');s=math.sqrt(raw.width*raw.height/(src.width*src.height));inv=raw.transform(src.size,Image.Transform.AFFINE,(s,0,0,0,s,0),resample=Image.Resampling.BICUBIC)
def flat(i):
 bg=Image.new('RGBA',i.size,(230,230,230,255));bg.alpha_composite(i);return bg.convert('RGB')
a=np.array(flat(src)).astype(float);z=np.array(flat(inv)).astype(float);alpha=np.array(src)[:,:,3];ban=(np.array(Image.open(pp/'references/REPAIR_local.png'))>0)|(np.array(Image.open(pp/'references/target_hand_fruit_PROTECT_local.png'))>0);patches=[];r=11
for y in range(16,366,14):
 for x in range(220,356,14):
  if ban[y-r:y+r+1,x-r:x+r+1].any() or (alpha[y-r:y+r+1,x-r:x+r+1]>220).mean()<.95:continue
  t=a[y-r:y+r+1,x-r:x+r+1];strength=float(np.std(t.mean(axis=2)))
  if strength<20:continue
  patches.append((strength,x,y))
selected=[]
for st,x,y in sorted(patches,reverse=True):
 if all((x-q[1])**2+(y-q[2])**2>38**2 for q in selected):selected.append((st,x,y))
 if len(selected)==12:break
results=[]
for st,x,y in selected:
 t=a[y-r:y+r+1,x-r:x+r+1];tc=t-t.mean();best=(-2,0,0)
 for dy in range(-8,9):
  for dx in range(-8,9):
   patch=z[y+dy-r:y+dy+r+1,x+dx-r:x+dx+r+1]
   if patch.shape!=t.shape:continue
   pc=patch-patch.mean();den=np.sqrt((tc*tc).sum()*(pc*pc).sum());corr=float((tc*pc).sum()/den)
   if corr>best[0]:best=(corr,dx,dy)
 results.append({'source_patch_center':[x,y],'downmapped_output_offset':[best[1],best[2]],'correlation':best[0],'source_patch_luma_std':st,'patch_size':23})
# Fit uniform scale+translation from source to raw-equivalent positions; examine residuals for nonuniform drift.
X=np.array([v['source_patch_center'] for v in results],float);Y=X+np.array([v['downmapped_output_offset'] for v in results],float);good=np.array([v['correlation']>.90 for v in results]);xm=X[good].mean(axis=0);ym=Y[good].mean(axis=0);scale=float(((X[good]-xm)*(Y[good]-ym)).sum()/((X[good]-xm)**2).sum());trans=ym-scale*xm;res=Y-(X*scale+trans);fit={'additional_scale_fit':scale,'translation_fit_in_native_crop':trans.tolist(),'max_residual_native_px':float(np.linalg.norm(res[good],axis=1).max()),'high_correlation_patches':int(good.sum())}
report={'raw_size':raw.size,'source_crop_size':src.size,'requested_single_uniform_scale':s,'axis_scales_from_integer_canvas':[raw.width/src.width,raw.height/src.height],'axis_difference_percent':100*abs(raw.width/src.width-raw.height/src.height)/s,'uniform_scaled_dimensions':[src.width*s,src.height*s],'integer_dimension_rounding_residual':[raw.width-src.width*s,raw.height-src.height*s],'anchor_results':results,'registration_fit':fit,'generation_redraw_note':'Raw output redraws whole crop; only masked connection pixels may be consumed. Unaffected/hand pixels discarded regardless of apparent match.'}
(o/'logs/local_registration.json').write_text(json.dumps(report,indent=2));inv.save(o/'qa/uniform_inverse_mapped_LOCAL_QA.png');Image.blend(flat(src),flat(inv),.5).save(o/'qa/local_registration_onion50.png');d=ImageDraw.Draw(inv)
for q in results:
 x,y=q['source_patch_center'];d.rectangle((x-r,y-r,x+r,y+r),outline='red',width=1)
inv.resize((740,760)).save(o/'qa/registration_anchor_boxes_2x.png');print(json.dumps(report,indent=2))
