from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
from scipy.ndimage import distance_transform_edt
R=Path(__file__).resolve().parent.parent;P=R/'F025_result_semantic_v8';O=R/'F025_result_color_final_v2'
for x in ['candidates','masks','geometry','qa']:(O/x).mkdir(parents=True,exist_ok=True)
s=P/'candidates/S08_F025_same_raw_semantic_candidate_RGBA.png';a=np.array(Image.open(s));o=a.copy();H,W=a.shape[:2]
def maskpoly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
w=np.array(Image.open(R/'F025_input_gate/masks/F025_WHITE_allowed_BLACK_frozen.png'))>0
poly=[(1041,838),(1126,793),(1147,807),(1132,828),(1102,850),(1084,866),(1060,877),(1043,861)]
m=maskpoly(poly)&w&(a[:,:,3]>=250)&(a[:,:,0]>230)&(a[:,:,1]>155)&(a[:,:,0].astype(int)>a[:,:,1].astype(int)+20)
shade=maskpoly([(1068,866),(1090,858),(1125,837),(1130,841),(1097,869),(1072,880)]);m&=~shade;m&=distance_transform_edt(m)>=2
# One channel-level unit only on the original material's lit inner plane; black lines, alpha and underside shade stay untouched.
o[m,1]=np.minimum(o[m,1].astype(int)+1,255).astype('uint8');Image.fromarray(m.astype('uint8')*255).save(O/'masks/ONLY_new_far_forearm_lit_material_G_plus1.png');p=O/'candidates/S08_F025_same_raw_final_color_RGBA.png';Image.fromarray(o).save(p)
d=json.loads((P/'geometry/COLOR_PLANES_PENDING_REVIEW.json').read_text());d.update(candidate_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),correction_applied=True,correction={'channel':'G','integer_delta':1,'mask_pixels':int(m.sum()),'polygon':poly,'alpha_changed':0,'other_channels_changed':0,'underside_shadow_intentionally_unchanged':True})
for name,v in d['materials'].items():
 ss=maskpoly(v['025']['polygon']);rgb=o[:,:,:3].astype(float);ss&=(o[:,:,3]>245)&(rgb[:,:,0]>230)&(rgb[:,:,1]>155)&(rgb[:,:,0]>rgb[:,:,1]+20);v['025']['mean_after_G1']=rgb[ss].mean(0).tolist();v['delta_after_G1']=(rgb[ss].mean(0)-np.array(v['000']['mean'])).tolist()
(O/'geometry/COLOR_PLANES_FINAL.json').write_text(json.dumps(d,indent=2))
checks=json.loads((P/'geometry/checks.json').read_text());checks.update(sha256=d['candidate_sha256'],color_G1_only_pixels=int(m.sum()),alpha_difference_to_v8=int((o[:,:,3]!=a[:,:,3]).sum()),status='FINAL_CANDIDATE_PENDING_INDEPENDENT_INCREMENTAL_COLOR_SIGN');(O/'geometry/checks.json').write_text(json.dumps(checks,indent=2))
old=np.array(Image.open(R/'F023_FINAL_LOCKED/S08_F023_grandma_match_box_RGBA.png'))
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(o));bg.convert('RGB').save(O/'qa'/f'candidate_{tag}.png');bg.crop((900,660,1300,990)).resize((1200,990)).convert('RGB').save(O/'qa'/f'whole_arm_{tag}.png');pan=Image.new('RGB',(1600,660),col[:3]);orig=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(old));pan.paste(orig.crop((900,660,1300,990)).resize((800,660)).convert('RGB'),(0,0));pan.paste(bg.crop((900,660,1300,990)).resize((800,660)).convert('RGB'),(800,0));pan.save(O/'qa'/f'F023_F025_final_same_scale_{tag}.png')
 tint=np.array(bg);tint[m,:3]=np.rint(tint[m,:3]*.55+np.array([220,45,160])*.45).astype('uint8');Image.fromarray(tint).crop((1000,770,1180,920)).resize((900,750)).convert('RGB').save(O/'qa'/f'G1_exact_material_mask_{tag}.png')
print(json.dumps({'sha256':d['candidate_sha256'],'mask_pixels':int(m.sum()),'deltas':{k:v['delta_after_G1'] for k,v in d['materials'].items()}},indent=2))
