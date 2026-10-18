from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
import numpy as np,json,hashlib,math
O=Path(__file__).resolve().parent;R=O.parent;W,H=1920,1080;S=14/18.5
helper=R.parent/'astra_s08_lamp_mechanical_candidate_20261018_1822/collab/reviews/20261018_1822_s08_lamp_mechanical_candidate/lamp_mechanical_candidate.js'
scene=R.parent/'astra_s08_first27_scene_20261018_1900/collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js'
a={'match_head':[1230,707],'hand_rotation_clockwise_deg':0};b={'match_head':[1335,785],'hand_rotation_clockwise_deg':5}
far=Image.open(R/'F033_FINAL_LOCKED/F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png').convert('RGBA');fa=np.array(far)[:,:,3]>128
near=Image.open(R/'F033_FINAL_LOCKED/F033_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png').convert('RGBA')
def flame(p):
 x,y=p;return[(x,y+2),(x-9.3,y-10),(x-7,y-24),(x,y-32),(x+7,y-24),(x+9.3,y-10)]
def trans(im,p,ang):
 t=math.radians(ang);c,s=math.cos(t),math.sin(t);x,y=p;return im.transform((W,H),Image.Transform.AFFINE,(c,s,1230-c*x-s*y,-s,c,707+s*x-c*y),Image.Resampling.BICUBIC)
def raster(poly):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(poly,fill=255);return np.array(m)>0
# At the traversed y range the left side pipe is an exact solid vertical strip.
pipe_bounds=[1415-168*S,965.6-560*S,1415-146*S,965.6-120*S];pipe=raster([(pipe_bounds[0]-2*S,pipe_bounds[1]),(pipe_bounds[2]+2*S,pipe_bounds[1]),(pipe_bounds[2]+2*S,pipe_bounds[3]),(pipe_bounds[0]-2*S,pipe_bounds[3])])
# Raised supporting ellipse, including source4px stroke after scale.
cy=965.6+(-310-4)*S;rx=128*S;ry=16*S
m=Image.new('L',(W,H));ImageDraw.Draw(m).ellipse((1415-rx-2*S,cy-ry-2*S,1415+rx+2*S,cy+ry+2*S),fill=255);rim=np.array(m)>0
knob=(1233.9532049683,766.8943738424);pivot=(1301.4864864865,791.5459459459)
m=Image.new('L',(W,H));d=ImageDraw.Draw(m);d.line((knob,pivot),fill=255,width=6);d.ellipse((knob[0]-7,knob[1]-7,knob[0]+7,knob[1]+7),fill=255);rod=np.array(m)>0
m=Image.new('L',(W,H));ImageDraw.Draw(m).ellipse((knob[0]-5,knob[1]-5,knob[0]+5,knob[1]+5),fill=255);seat=np.array(m)>0
D={k:distance_transform_edt(~v) for k,v in [('farhand',fa),('pipe',pipe),('rim',rim),('rod',rod)]};masks={'farhand':fa,'pipe':pipe,'rim':rim,'rod':rod};sweep=np.zeros((H,W),bool);samples=[]
for i in range(101):
 t=i/100;p=(1-t)*np.array(a['match_head'])+t*np.array(b['match_head']);f=raster(flame(p));sweep|=f
 r={'t':t,'head':p.tolist()}
 for k,mm in masks.items():r[k+'_overlap_px']=int((f&mm).sum());r[k+'_clearance_px']=float(D[k][f].min())
 # Check overlap along real rigid hand travel, not only endpoint images.
 if i%5==0:
  n=np.array(trans(near,p,a['hand_rotation_clockwise_deg']*(1-t)+b['hand_rotation_clockwise_deg']*t))[:,:,3]>128
  r['near_visible_over_seat_core_px']=int((n&seat).sum())
 samples.append(r)
out={'status':'ACTUAL033_SOURCE_TO036_TARGET_FULL_SWEEP_GEOMETRY_ONLY_NOT_CANVAS','helper_path':str(helper),'helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'scene_path':str(scene),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'lamp_scale':S,'lamp_mirrored_x':True,'low_pipe_solid_scene_bounds_without_stroke':pipe_bounds,'raised_rim_bbox_with_stroke':[1415-rx-2*S,cy-ry-2*S,1415+rx+2*S,cy+ry+2*S],'samples':samples,'pixel_projection_only':True,'depth_requirement':'The near hand, match and flame must pass in front of the left support pipe before entering the lifted hood opening. The current original scene renders code lamp behind all character arms. A 2D overlap is not evidence of skin or flame physically touching metal; actual full scene must make this depth readable.','stats':{k:{'minimum_clearance':min(r[k+'_clearance_px'] for r in samples),'maximum_projection_overlap_pixels':max(r[k+'_overlap_px'] for r in samples),'samples_with_overlap':sum(r[k+'_overlap_px']>0 for r in samples)} for k in masks},'near_seat_projection_overlap_max':max(r.get('near_visible_over_seat_core_px',0) for r in samples)}
(O/'geometry/033_036_ACTUAL_HAND_FULL_SWEEP.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
im=Image.new('RGBA',(W,H),(244,242,237,255));aa=np.zeros((H,W,4),np.uint8);aa[pipe]=[146,63,53,255];aa[rim]=[124,52,46,255];aa[rod]=[58,42,34,255];im.alpha_composite(Image.fromarray(aa));im.alpha_composite(far)
sw=np.zeros_like(aa);sw[sweep]=[223,149,43,75];sw[sweep&pipe]=[202,52,150,150];sw[sweep&rim]=[202,52,150,150];im.alpha_composite(Image.fromarray(sw));d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for i in [0,25,50,75,100]:
 p=samples[i]['head'];d.line(flame(p)+[flame(p)[0]],fill=(167,96,20),width=1);d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=(94,55,22));d.text((p[0]-18,p[1]+8),str(i)+'%',font=font,fill=(33,37,41))
d.text((1080,645),'033 -> 036 FULL SWEEP, helper geometry',font=font,fill=(33,37,41));d.text((1080,665),'Magenta: pipe projection overlap. Foreground depth required.',font=font,fill=(130,37,105));d.text((1080,685),'Foreground crossing; no claim of2Dclear or continuous grip visibility.',font=font,fill=(33,37,41));im.crop((1070,630,1535,890)).resize((1395,780)).convert('RGB').save(O/'qa/033_036_FULL_SWEEP_pipe_rim_NOT_CANVAS.png')
print(json.dumps(out['stats']));print('max_seat_occlusion',out['near_seat_projection_overlap_max'])
