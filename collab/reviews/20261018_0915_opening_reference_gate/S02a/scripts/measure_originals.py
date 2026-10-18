"""Read-only asset analysis. Never rewrites or resamples a PNG."""
from pathlib import Path
from PIL import Image
from scipy.ndimage import label, find_objects
import numpy as np, json, hashlib, math
ROOT=Path(__file__).resolve().parents[1]
paths=sorted((ROOT/'originals').glob('*.png'))
all_rows=[]
for p in paths:
    im=Image.open(p); ar=np.array(im); a=ar[:,:,3]; h=np.bincount(a.ravel(),minlength=256)
    # Fixed lower-chest ROIs: white-dot A, B, independent H; no shoulder anchoring.
    rois={'A':[700,890,755,930],'B':[925,890,975,935],'H':[815,890,865,935]}
    points={}
    for name,(x0,y0,x1,y1) in rois.items():
        z=ar[y0:y1,x0:x1]
        mask=(z[:,:,0]>233)&(z[:,:,1]>227)&(z[:,:,2]>220)&(z[:,:,3]>200)
        lab,n=label(mask); counts=np.bincount(lab.ravel()); counts[0]=0; k=counts.argmax()
        yy,xx=np.nonzero(lab==k)
        points[name]={'xy':[float(xx.mean()+x0),float(yy.mean()+y0)],'area_pixels':len(xx),'roi_xyxy':[x0,y0,x1,y1]}
    lab,n=label(a>=128); cnt=np.bincount(lab.ravel()); cnt[0]=0; main=int(cnt.argmax()); objects=find_objects(lab); sl=objects[main-1]
    row={'file':p.name,'size':list(im.size),'mode':im.mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'alpha':{'min':int(a.min()),'max':int(a.max()),'zero_pixels':int(h[0]),'opaque_255_pixels':int(h[255]),'near_opaque_250_255_pixels':int(h[250:].sum()),'nonzero_pixels':int((a>0).sum()),'alpha_bbox_all_nonzero':list(im.getchannel('A').getbbox()),'main_component_bbox_alpha_ge_128':[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],'main_component_pixels_alpha_ge_128':int(cnt[main]),'outside_main_component_pixels_alpha_ge_128':int(cnt.sum()-cnt[main]),'component_count_alpha_ge_128':int(n)},'lower_chest_points':points}
    all_rows.append(row)
base=all_rows[0]['lower_chest_points']
za=complex(*base['A']['xy']);zb=complex(*base['B']['xy']);zh=complex(*base['H']['xy'])
for r in all_rows:
    q=r['lower_chest_points'];a=complex(*q['A']['xy']);b=complex(*q['B']['xy']);h=complex(*q['H']['xy'])
    c=(zb-za)/(b-a);d=za-c*a;mapped=c*h+d;res=mapped-zh
    r['AB_similarity_to_k01']={'formula':'x_master = a*x_source - b*y_source + tx; y_master = b*x_source + a*y_source + ty','a':c.real,'b':c.imag,'tx':d.real,'ty':d.imag,'scale':abs(c),'angle_deg':math.degrees(math.atan2(c.imag,c.real)),'H_mapped_xy':[mapped.real,mapped.imag],'H_residual_xy':[res.real,res.imag],'H_residual_native_pixels':abs(res),'status':'not_a_pass: A/B material stability not established; H is near-collinear with A/B; visual pattern drift and rendering defects remain'}
s=1080/941
out={'measurement_note':'Raw PNG pixel centers. Thresholded white-dot connected-component centroid; approx +/-1 pixel visual localization, not subpixel proof. No shoulders used. A/B/H visually correspond by left-center-right order in same bottom chest row; garment pattern persistence is not independently established. H is a held-out point, not used in fit; nearly collinear points cannot validate general warp. Do not claim H pass.', 'review_only_scene_fit':{'scene':[1920,1080],'source_canvas':[1672,941],'drawImage_destination_xywh':[(1920-1672*s)/2,0,1672*s,1080],'scale':s,'status':'Uniform runtime starting point for review in the later K19 close-up, not an accepted final placement and not a new native-resolution asset. Earlier framing mismatch statements apply only to the fe2/K14 board.'},'assets':all_rows}
(ROOT/'qa/measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
