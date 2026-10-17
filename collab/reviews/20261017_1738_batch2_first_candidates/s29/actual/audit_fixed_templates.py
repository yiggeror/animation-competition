from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
from scipy.signal import fftconvolve
from scipy.ndimage import maximum_filter,binary_erosion,distance_transform_edt,binary_fill_holes
D=Path(__file__).parent; P=D.parent
S=Image.open(P.parent/'batch2_scope/refs/g29_wrap.png').convert('RGBA'); C=Image.open(D/'C1_raw.png').convert('RGBA')
def composite(im,color=128):
 b=Image.new('RGBA',im.size,(color,color,color,255));b.alpha_composite(im);return b
sg=composite(S).convert('L');cg=composite(C).convert('L');spec=json.loads((P/'ANCHORS_AND_EXPOSURE_PLAN.json').read_text())
reports=[]
for item in spec['anchors']:
 pt=item['point'];box=item['template_xyxy_exclusive'];template=Image.open(P/item['template_file']).convert('L');assert hashlib.sha256(template.tobytes()).hexdigest()==item['template_raw_L_sha256'];assert template.tobytes()==sg.crop(box).tobytes()
 t=np.asarray(template,np.float64);x0,y0=box[:2];search=40;sx0,sy0=x0-search,y0-search
 win=np.asarray(cg,np.float64)[sy0:sy0+t.shape[0]+2*search,sx0:sx0+t.shape[1]+2*search]
 tz=t-t.mean();n=t.size;num=fftconvolve(win,tz[::-1,::-1],mode='valid');ones=np.ones(t.shape);s1=fftconvolve(win,ones,mode='valid');s2=fftconvolve(win*win,ones,mode='valid');den=np.sqrt(np.maximum(s2-s1*s1/n,1e-9))*math.sqrt((tz*tz).sum());ncc=num/den
 iy,ix=np.unravel_index(np.argmax(ncc),ncc.shape);peak=float(ncc[iy,ix]);yy,xx=np.indices(ncc.shape)
 second=[]
 for radius in [3,6,10]:
  out=np.where(np.maximum(abs(yy-iy),abs(xx-ix))>radius,ncc,-np.inf);jy,jx=np.unravel_index(np.argmax(out),out.shape);score=float(ncc[jy,jx]);second.append({'excluded_chebyshev_radius_px':radius,'second_location_index':[int(jx),int(jy)],'second_raw_point':[pt[0]+int(jx)-40,pt[1]+int(jy)-40],'second_score':score,'peak_minus_second':peak-score,'distance_from_peak_px':float(math.hypot(jx-ix,jy-iy))})
 localmask=(ncc==maximum_filter(ncc,size=5,mode='constant',cval=-np.inf))&(np.maximum(abs(yy-iy),abs(xx-ix))>6)
 local=[(float(ncc[y,x]),int(x),int(y)) for y,x in zip(*np.where(localmask))];local.sort(reverse=True)
 out={'id':item['id'],'point':pt,'template_xyxy_exclusive':box,'frozen_template_raw_sha256':item['template_raw_L_sha256'],'search_top_left':[sx0,sy0],'search_ncc_grid_wh':[ncc.shape[1],ncc.shape[0]],'peak_index_xy':[int(ix),int(iy)],'peak_raw_point':[pt[0]+int(ix)-40,pt[1]+int(iy)-40],'peak_score':peak,'peak_distance_to_nearest_search_edge_px':int(min(ix,iy,ncc.shape[1]-1-ix,ncc.shape[0]-1-iy)),'secondary_peak_audits':second,'top5_other_local_maxima_outside_radius6':[{'score':v,'index_xy':[x,y],'raw_point':[pt[0]+x-40,pt[1]+y-40],'peak_minus_score':peak-v} for v,x,y in local[:5]],'warning':'Scores below 0.90 require actual fixed-window contour inspection; peak center or small H residual alone is insufficient.'}
 reports.append(out)
 # Exact pixel crops, visualized side-by-side and with cyan/red alpha edges. No registration or restoration.
 cropbox=[pt[0]-35,pt[1]-35,pt[0]+35,pt[1]+35];panels=[]
 for title,im in [('SOURCE',S),('C1 RAW',C)]:
  z=composite(im,216).crop(cropbox).convert('RGB').resize((280,280),Image.Resampling.NEAREST);d=ImageDraw.Draw(z);d.line((132,140,148,140),fill='red');d.line((140,132,140,148),fill='red');d.text((6,6),title,fill='red');panels.append(z)
 plate=Image.new('RGB',(560,280),'white');plate.paste(panels[0]);plate.paste(panels[1],(280,0));plate.save(D/f'anchor_{item["id"]}_raw_native_compare.png',optimize=True)
 # Raw fixed-window luminance correlation visualization; values are diagnostic only.
 heat=np.uint8(np.clip((ncc+1)*127.5,0,255));Image.fromarray(heat).resize((324,324),Image.Resampling.NEAREST).save(D/f'anchor_{item["id"]}_ncc_map.png',optimize=True)
(D/'fixed_template_peak_audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
# Native alpha silhouette comparison at both feet, with no registration and excluding artificial crop borders.
def edge_dist(sa,ca):
 se=sa&~binary_erosion(sa);ce=ca&~binary_erosion(ca);border=np.ones(sa.shape,bool);border[:3]=False;border[-3:]=False;border[:,:3]=False;border[:,-3:]=False;se&=border;ce&=border
 ds=distance_transform_edt(~se);dc=distance_transform_edt(~ce);vals=np.r_[dc[se],ds[ce]]
 return {'source_edge_pixels':int(se.sum()),'candidate_edge_pixels':int(ce.sum()),'symmetric_distance_p50_p95_max_px':np.percentile(vals,[50,95,100]).tolist()}
contours={}
for name,box in [('B_front_stool_foot',[328,1290,408,1360]),('H_rear_stool_foot',[125,1215,212,1280])]:
 sa=np.asarray(S.crop(box))[:,:,3]>128;ca=np.asarray(C.crop(box))[:,:,3]>128;contours[name]={'fixed_raw_box':box,'threshold_alpha':128,**edge_dist(sa,ca)}
# Gross bare-right-hand visible contour; orange skin selection, holes filled; excludes blue cloth and dark outline.
box=[515,680,600,775]
def skin(im):
 ar=np.asarray(im.crop(box));r,g,b=ar[:,:,0].astype(int),ar[:,:,1].astype(int),ar[:,:,2].astype(int);mask=(r>170)&(g>100)&(r-g>12)&(g-b>8)&(ar[:,:,3]>128);return binary_fill_holes(mask)
contours['right_hand_visible_skin']={'fixed_raw_box':box,'purpose':'Additional right-hand outline check only, not an alignment anchor or anatomical subpixel claim','selection':'R>170 G>100 R-G>12 G-B>8 alpha>128, fill holes; crop borders excluded',**edge_dist(skin(S),skin(C))}
(D/'fixed_native_contour_checks.json').write_text(json.dumps(contours,indent=2)+'\n')
print(json.dumps({'peaks':[{'id':q['id'],'score':q['peak_score'],'margin':q['peak_distance_to_nearest_search_edge_px'],'second6':q['secondary_peak_audits'][1],'next_local_max':q['top5_other_local_maxima_outside_radius6'][:1]} for q in reports],'contours':contours},indent=2))
