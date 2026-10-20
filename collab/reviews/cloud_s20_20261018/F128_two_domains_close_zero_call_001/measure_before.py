"""Measure two actual own poses; no pony/flower/ahoge/neck volume matching."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_opening,binary_dilation,distance_transform_edt,median_filter
F=Path(__file__).resolve().parent; P=F.parent
paths=[P/'next_F120_passive_decay_input_001/generation_001/registered_complete_new_upper_whole_skirt_two_T.png',
       P/'next_F128_mid_roll_input_001/character_four_inputs_001/generation_001/registered_complete_new_upper_whole_skirt_short_guides_UNREPAIRED.png']
polys=[[(500,150),(760,150),(760,267),(723,286),(709,311),(673,329),(631,327),(611,344),(580,348),(545,340),(507,278)],
       [(570,190),(795,190),(795,326),(766,341),(737,361),(693,352),(660,349),(637,354),(611,358),(580,337),(572,278)]]
rows=[]; card=Image.new('RGB',(740,350),'#bdc1c4')
for i,(path,poly) in enumerate(zip(paths,polys)):
    a=np.array(Image.open(path).convert('RGBA')); H,W=a.shape[:2]; yy,xx=np.indices((H,W))
    roi=Image.new('L',(W,H)); ImageDraw.Draw(roi).polygon(poly,fill=255); roi=np.array(roi)>0
    r,g,b=a[:,:,:3].astype(float).transpose(2,0,1)
    red=(r>160)&(g<80)&(b<80)
    # Opening removes the thin ahoge. Only the dominant solid main head is
    # measured; the operation is for metrics, never applied to source art.
    fg=(a[:,:,3]>160)&roi&~binary_dilation(red,iterations=2)
    fg=binary_opening(fg,iterations=4); cc,_=label(fg)
    sizes=np.bincount(cc.ravel()); fg=cc==(np.argmax(sizes[1:])+1); py,px=np.where(fg)
    hair=(a[:,:,3]>160)&(r<175)&(g<130)&(b<120)&(r>g+7)&roi
    hair=binary_opening(hair,iterations=4); cc,_=label(hair)
    sizes=np.bincount(cc.ravel()); hair=cc==(np.argmax(sizes[1:])+1); hy,hx=np.where(hair)
    white=(a[:,:,3]>160)&(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>580)&(xx<725)&(yy>340)&(yy<415)
    skin=(a[:,:,3]>160)&(r>170)&(g>100)&(b>g*.65)&(r>g+12)
    boundary=skin&(distance_transform_edt(~white)<2.6)&(xx>600)&(xx<705)&(yy>(345 if i==0 else 355))&(yy<405)
    by,bx=np.where(boundary)
    cols=[]
    for x in sorted(set(bx.tolist())):
        q=by[bx==x]; cols.append([float(x),float(q.max())])
    assert len(cols)>30
    eye,ear=([572.,286.],[650.,296.]) if i==0 else ([625.,297.],[681.,327.])
    ev=np.array(ear)-eye
    row={'frame':[120,128][i],'main_cranium_face_area':int(fg.sum()),
         'main_cranium_x_005_995':np.quantile(px,[.005,.995]).tolist(),
         'main_cranium_y_005_995':np.quantile(py,[.005,.995]).tolist(),
         'main_cranium_centroid':[float(px.mean()),float(py.mean())],
         'main_hair_area':int(hair.sum()),'hair_x_005_995':np.quantile(hx,[.005,.995]).tolist(),
         'hair_y_005_995':np.quantile(hy,[.005,.995]).tolist(),
         'neck_collar_contact_centroid':[float(bx.mean()),float(by.mean())],
         'actual_lower_neck_skin_boundary_columns':cols,
         'observed_eye_ear_centers':{'eye':eye,'ear':ear,'distance_px':float(np.linalg.norm(ev)),
                                     'angle_deg':math.degrees(math.atan2(ev[1],ev[0]))},
         'landmarks_are_visual_2D_observations_tolerance_px':2,
         'measurement_excludes_pony_flower_ahoge_and_lower_neck':True}
    rows.append(row)
    frame=[120,128][i]
    Image.fromarray(np.uint8(fg)*255).save(F/f'measured_main_cranium_face_{frame}_mask.png')
    Image.fromarray(np.uint8(hair)*255).save(F/f'measured_main_hair_{frame}_mask.png')
    bg=Image.new('RGBA',(W,H),'#bdc1c4'); bg.alpha_composite(Image.fromarray(a)); d=ImageDraw.Draw(bg)
    for p in [eye,ear,row['neck_collar_contact_centroid']]:
        x,y=p;d.ellipse((x-2,y-2,x+2,y+2),outline='#007aff',width=1)
    for x,y in cols:d.point((x,y),fill='#00b4ff')
    card.paste(bg.crop((490,130,860,480)).convert('RGB'),(i*370,0))
old,new=rows
span=lambda q,key:q[key][1]-q[key][0]
width=span(old,'main_cranium_x_005_995')/span(new,'main_cranium_x_005_995')
height=span(old,'main_cranium_y_005_995')/span(new,'main_cranium_y_005_995')
area=math.sqrt(old['main_cranium_face_area']/new['main_cranium_face_area'])
hairwidth=span(old,'hair_x_005_995')/span(new,'hair_x_005_995')
hairarea=math.sqrt(old['main_hair_area']/new['main_hair_area'])
# Geometric median in log space: two contour dimensions, independent hair
# width and two area-based linear estimates. Pose-changed ear vector is a
# crosscheck only; it does not drive feature-specific resizing.
scale=float(np.exp(np.median(np.log([width,height,area,hairwidth,hairarea]))))
report={'measurement_method':'Dominant opened actual main cranium/face silhouette; independent main-hair measurements. Pony, flower, thin ahoge and lower neck excluded. Eye/ear vector angle differs between poses, so do not resize features to match its scalar distance.',
        'states':rows,'ratios':{'main_width':width,'main_height':height,
        'main_area_linear':area,'hair_width':hairwidth,'hair_area_linear':hairarea},
        'selected_uniform_own_head_scale':scale,
        'additional_rotation_deg':0,'additional_free_head_translation_px':[0,0],
        'pivot_current_actual_neck_collar_contact':new['neck_collar_contact_centroid'],
        'neck_collar_level_128_minus120':(np.array(new['neck_collar_contact_centroid'])-old['neck_collar_contact_centroid']).tolist()}
(F/'measurements_before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
card.save(F/'120_left_128_before_right_head_neck_measurement_1x.png')
print(json.dumps({k:v for k,v in report.items() if k!='states'},ensure_ascii=False,indent=2))
