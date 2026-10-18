from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import map_coordinates
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'eyes03_result_lid_continuous_v3'
for d in ['candidates','masks','qa','geometry']:(O/d).mkdir(parents=True,exist_ok=True)
base=Image.open(R/'eyes03_result_frame_trace_v2/candidates/F000_eyes03_local_composite_RGBA.png').convert('RGBA');raw=np.array(Image.open(R/'eyes03_result_nominal/registered/eyes03_registered_scene_patch_RGBA.png').convert('RGBA'));b=np.array(base);h,w=b.shape[:2]
# Continuous geometric bands, not threshold-selected dark pixels. Both are old upper eyelid only.
# Donor is one coherent skin corridor in the same raw between the new upper frame and new lowered lid.
bands=[dict(name='near',x=[841,844,848,852,856,860,864,868,872,876,879],top=[530,524,520,517,515,514,513,513,513,514,516],bottom=[531,527,524,522,520,519,519,519,519,520,520],donor_top=[531,527,524,522,520,519,518,517,517,517,518],donor_bottom=[531.5,528,526,525,524,523,522,522,522,522,523]),dict(name='far',x=[921,924,928,932,936,940,943],top=[517,514,511,508,507,507,507],bottom=[521,518,515,512,511,512,512],donor_top=[519,516,514,511,509,508,508],donor_bottom=[520,517,515,513,512,512,512])]
result=b.astype(float).copy();mask=np.zeros((h,w),float);maprows=[]
for band in bands:
 x=np.array(band['x'],float); curves={k:PchipInterpolator(x,np.array(band[k],float)) for k in ['top','bottom','donor_top','donor_bottom']}
 for xx in range(int(x[0]),int(x[-1])+1):
  top,bottom=[float(curves[k](xx)) for k in ['top','bottom']]
  for yy in range(int(np.floor(top)),int(np.ceil(bottom))+1):
   # Pixel-centre coverage and narrow continuous feather at the semantic strip boundary.
   cov=max(0.,min(1., yy+.5-top, bottom+.5-yy));edge=min((xx-x[0]+.5)/1.5,(x[-1]-xx+.5)/1.5,1);alpha=cov*edge
   if alpha<=0:continue
   t=np.clip((yy-top)/max(bottom-top,1),0,1);sy=float(curves['donor_top'](xx))*(1-t)+float(curves['donor_bottom'](xx))*t
   rgb=[float(map_coordinates(raw[:,:,c].astype(float),[[sy],[xx]],order=1,mode='nearest')[0]) for c in range(3)]
   result[yy,xx,:3]=(1-alpha)*b[yy,xx,:3]+alpha*np.array(rgb);mask[yy,xx]=alpha;maprows.append([xx,yy,xx,sy,alpha])
result=np.clip(np.rint(result),0,255).astype('uint8');result[:,:,3]=b[:,:,3];out=Image.fromarray(result,'RGBA');out.save(O/'candidates/F000_same_raw_continuous_lid_cleanup_RGBA.png');Image.fromarray(np.rint(mask*255).astype('uint8')).save(O/'masks/continuous_old_lid_skin_band.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',base.size,col);bg.alpha_composite(out);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for name,bb,m in [('eyes',(806,488,970,571),6),('head_and_match',(625,310,1205,860),2),('hands',(930,728,1214,893),4)]:
  q=bg.crop(bb);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{name}_{label}.png')
changed=np.any(result!=b,2);info={'actual_native_calls_total':3,'new_calls':0,'method':'Two continuous same-raw skin corridors resampled only into old upper-eyelid bands. Explicit continuous geometric boundaries; no dark-pixel threshold, painted pixels, iris or new-eyelid change.','bands':bands,'changed_pixels':int(changed.sum()),'alpha_changes':int((result[:,:,3]!=b[:,:,3]).sum()),'outside_explicit_band_changes':int((changed&(mask==0)).sum()),'sha256':hashlib.sha256((O/'candidates/F000_same_raw_continuous_lid_cleanup_RGBA.png').read_bytes()).hexdigest()};(O/'geometry/checks.json').write_text(json.dumps(info,indent=2));(O/'geometry/continuous_same_raw_mapping.json').write_text(json.dumps(maprows));print(json.dumps(info))
