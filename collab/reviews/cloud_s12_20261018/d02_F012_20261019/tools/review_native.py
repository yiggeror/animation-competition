"""Read-only native QA; creates measurements/diagnostics, never modifies original art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,numpy as np,hashlib
P=Path(__file__).resolve().parents[1];S=P.parent
F0=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png';F12=P/'originals/F012_raw_call01.png'
a=np.array(Image.open(F0).convert('RGBA'));b=np.array(Image.open(F12).convert('RGBA'));Q=P/'qa';(Q/'masks').mkdir(exist_ok=True)
assert a.shape==b.shape==(1536,1024,4)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(F0)=='95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793'
def polygon(polys):
 im=Image.new('L',(1024,1536));d=ImageDraw.Draw(im)
 for pts in polys:d.polygon([tuple(v) for v in pts],fill=255)
 return np.array(im)>0
D=json.loads((S/'d01_F000/same_raw_fix_20261019/qa/source_and_region_definitions.json').read_text())
skin0=D['skin_polygons_native'];skin12=[v for v in skin0];skin12[2]=[[697,748],[748,768],[824,803],[902,824],[957,825],[1008,845],[1013,914],[958,925],[901,905],[822,886],[754,873],[680,828]]
blue=D['blouse_polygons_native'];hair=[[[444,325],[746,328],[810,459],[757,548],[635,553],[589,574],[435,546]]];pants=[[[180,1010],[463,1009],[577,1100],[642,1180],[640,1293],[525,1320],[191,1325]]]
def select(ar,name,polys):
 x=ar[:,:,:3].astype(np.int16);r,g,bl=x.transpose(2,0,1)
 if name=='skin':pred=(r>180)&(g>120)&(bl>70)&(r>g+18)&(g>bl+11)
 elif name=='blouse_blue':pred=(r>65)&(bl>r+20)&(bl>g+15)&(np.max(x,2)>120)
 elif name=='hair':pred=(abs(r-g)<30)&(abs(g-bl)<20)&(r>85)&(r<235)
 else:pred=(bl-r>8)&(bl-g>5)&(r>25)&(r<120)&(bl<160)
 return polygon(polys)&pred&(ar[:,:,3]>=128)
regions={};masks={}
for name,polys0,polys12 in [('skin',skin0,skin12),('blouse_blue',blue,blue),('hair',hair,hair),('trousers',pants,pants)]:
 ms=[select(a,name,polys0),select(b,name,polys12)];means=[]
 for label,ar,m in zip(['locked_F000','raw_F012'],[a,b],ms):
  assert m.sum()>15000;Image.fromarray(m.astype(np.uint8)*255).save(Q/f'masks/{label}_{name}.png');means.append(ar[m,:3].mean(0));masks[(label,name)]=m
 delta=means[1]-means[0];regions[name]={'mother_pixels':int(ms[0].sum()),'F012_pixels':int(ms[1].sum()),'mother_mean_RGB':means[0].tolist(),'F012_mean_RGB':means[1].tolist(),'delta_F012_minus_mother_RGB':delta.tolist(),'max_abs_channel_delta':float(np.max(abs(delta))),'within_4':bool(np.max(abs(delta))<=4)}
# Native boundary -> fixed registration -> finite code rod segment. All selected hand skin, not only one fingertip.
A=json.loads((S/'geometry/three_key_pose_proposal.json').read_text())['states'][0]['points_scene']
hand_polys={'far_left':[[[836,807],[1016,808],[1016,933],[836,933]]], 'near_right':[[[730,953],[896,953],[896,1065],[730,1065]]]}
clearances={}
for name,polys in hand_polys.items():
 m=select(b,'skin',polys);Image.fromarray(m.astype(np.uint8)*255).save(Q/f'masks/F012_{name}_hand_skin.png');yy,xx=np.nonzero(m);pts=np.stack([xx+.5,yy+.5],1)*.7+[275,112];result={}
 for rod,endkey in [('L','P_neck'),('R','P_body')]:
  start=np.array(A['free_grip'+rod]);end=np.array(A[endkey]);v=end-start;u=np.clip(((pts-start)@v)/(v@v),0,1);dist=np.linalg.norm(pts-(start+u[:,None]*v),axis=1)-3.5-.7*np.sqrt(2)/2
  idx=np.argmin(dist);result[rod]={'conservative_min_gap_to_7px_outline_scene_px':float(dist[idx]),'nearest_native_pixel':[int(xx[idx]),int(yy[idx])],'hand_skin_pixels':len(xx)}
 clearances[name]=result
assert all(v['conservative_min_gap_to_7px_outline_scene_px']>3 for h in clearances.values() for v in h.values())
# Source RGB masks are diagnostic selections, not edit masks. No original pixels are adjusted.
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(ar,color):
 im=Image.fromarray(ar,'RGBA');bg=Image.new('RGBA',im.size,(*color,255));return Image.alpha_composite(bg,im).convert('RGB')
board=Image.new('RGB',(1024,1604),'white');d=ImageDraw.Draw(board)
for row,color in enumerate([(205,208,211),(38,40,44)]):
 for col,ar in enumerate([a,b]):
  im=flat(ar,color).resize((512,768),Image.Resampling.LANCZOS);x=col*512;y=row*802;board.paste(im,(x,y+34));d.text((x+10,y+6),'LOCKED F000' if col==0 else 'RAW F012 / one call, unchanged',font=font(16),fill='black')
board.save(Q/'00_full_native_mother_F012_gray_dark.jpg',quality=95)
for file,crop in [('01_whole_far_arm_and_both_hands_actual2x.jpg',(425,635,1024,1074)),('03_fine_hair_glasses_actual2x.jpg',(420,320,815,650))]:
 w,h=(crop[2]-crop[0])*2,(crop[3]-crop[1])*2;im=Image.new('RGB',(w*2,h+35),'#cdd0d3');dd=ImageDraw.Draw(im)
 for c,ar in enumerate([a,b]):
  im.paste(flat(ar,(205,208,211)).crop(crop).resize((w,h),Image.Resampling.NEAREST),(c*w,35));dd.text((c*w+10,8),'LOCKED F000' if c==0 else 'RAW F012',font=font(20),fill='black')
 im.save(Q/file,quality=96)
# True raw drawing with measured code axes overlaid, explicitly not a rendered/relit scene.
diag=flat(b,(205,208,211));dd=ImageDraw.Draw(diag)
for rod,key in [('L','P_neck'),('R','P_body')]:
 f=(np.array(A['free_grip'+rod])-[275,112])/.7;e=(np.array(A[key])-[275,112])/.7
 dd.line([tuple(f),tuple(e)],fill=(66,45,27),width=10);dd.line([tuple(f),tuple(e)],fill=(206,164,87),width=4)
dd.rectangle((0,0,1024,120),fill=(240,241,241));dd.text((20,16),'RAW F012 + FIXED CODE ROD AXES',font=font(26),fill='black');dd.text((20,60),'REGISTRATION DIAGNOSTIC, NOT A NEW SCENE RENDER',font=font(21),fill=(151,55,30))
diag.save(Q/'02_registered_rod_clearance_DIAGNOSTIC.jpg',quality=96)
diag.crop((700,775,1024,1080)).resize((972,915),Image.Resampling.NEAREST).save(Q/'02b_both_hands_rod_gap_DIAGNOSTIC3x.jpg',quality=96)
# Actual mask overlays make the full pigment selections reviewable.
for name in ['skin','blouse_blue','hair','trousers']:
 out=Image.new('RGB',(1024,800),'white');dd=ImageDraw.Draw(out)
 for c,(lab,ar) in enumerate([('locked_F000',a),('raw_F012',b)]):
  im=flat(ar,(210,212,214)).convert('RGBA');overlay=Image.new('RGBA',im.size,(30,210,110,0));overlay.putalpha(Image.fromarray((masks[(lab,name)]*105).astype(np.uint8)));im=Image.alpha_composite(im,overlay).convert('RGB').resize((512,768));out.paste(im,(512*c,32));dd.text((512*c+10,7),f'{lab} full {name} selection',font=font(15),fill='black')
 out.save(Q/f'{name}_same_material_masks_actual.jpg',quality=94)
report={'kind':'UNMODIFIED_NATIVE_F012_REVIEW_NOT_ASTRA_LOCK','raw_SHA256':sha(F12),'mother_SHA256':sha(F0),'raw_RGBA_size':[1024,1536],'registration':{'scale':.7,'x':275,'y':112},'material_threshold_RGB_mean':4,'mask_definition':'Manual physical material polygons, per-image same-pigment predicates; alpha>=128; blue excludes white flowers/ink by color. Not global averages. Compare broad whole pigment regions, not selected safe edit cores. Exact masks saved.','skin_new_far_arm_polygon_only_motion_adjustment':skin12[2],'hair_region_polygon':hair,'trousers_region_polygon':pants,'materials':regions,'all_four_materials_pass':all(v['within_4'] for v in regions.values()),'hand_to_fixed_rod_outline_gaps':clearances,'gap_method':'Finite projected code rod segment, width7scene px; selected actual hand skin pixel centres transformed by .70+(275,112); subtract half native pixel diagonal for conservative boundary. Diagnostic overlays, not real new scene render.','imagegen_calls_this_task':1,'inflight_this_worker':0,'other_frames_generated':[],'pixel_corrections_or_transforms':0,'new_scene_renders':0,'original_art_not_modified':True,'whole_body_pixel_identity_to_mother_claimed':False,'Astra_final_approval':'PENDING_NATIVE_REVIEW_AND_COLOR_DISPOSITION'}
(Q/'actual_native_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'raw':report['raw_SHA256'],'materials':regions,'gaps':clearances},ensure_ascii=False,indent=2))
