from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,math,json,hashlib
D=Path('/workspace/scratch/f060b5601755/astra_s07_zero_pose_actual_20261018_1712/xiaoman_review_inputs')
O=Path(__file__).resolve().parent
load=lambda p:Image.open(p).convert('RGBA')
a=np.array(load(D/'reference/source_call02_same_canvas.png'));size=(a.shape[1],a.shape[0]);j=json.loads((D/'proposal_checks.json').read_text());static=np.array(Image.open(D/'masks/locked_static_head_blouse_near_right_arm.png'))>0;hard=np.array(Image.open(D/'masks/locked_head_body_near_right_arm.png'))>0
s=j['registration_unchanged']['s'];T=np.array([j['registration_unchanged']['tx'],j['registration_unchanged']['ty']]);pivot=np.array(j['arm_complete_rigid']['visible_sleeve_pivot_native']);arm=load(D/'layers/source_far_complete_arm.png');chain=np.array(j['arm_complete_rigid']['source_chain_native'])
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def rigid(im,R,t):
 inv=R.T;off=-inv@t
 return im.transform(size,Image.Transform.AFFINE,(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
n=j['near_complete_leg'];NR=rot(n['rotation_deg']);nt=np.array(n['destination_pivot'])-NR@np.array(n['source_pivot']);npants=rigid(load(D/'layers/source_near_pants.png'),NR,nt)
far=rigid(load(D/'layers/source_far_complete_leg.png'),np.eye(2),np.array(j['far_complete_leg']['translation_native']))
shoe=rigid(load(D/'layers/source_near_shoe_and_ankle.png'),np.eye(2),np.array(n['proposal_chain_native'][-1])-np.array(n['source_chain_native'][-1]))
def compose(deg):
 R=rot(deg);t=pivot-R@pivot;ar=rigid(arm,R,t);out=Image.new('RGBA',size);out.alpha_composite(far);out.alpha_composite(ar);out.alpha_composite(npants);out.alpha_composite(shoe);c=np.array(out);c[static]=a[static];c[hard]=a[hard];return Image.fromarray(c),ar,(chain-pivot)@R.T+pivot
existing=np.array(load(D/'reference/rigid_preposition_NOT_ART_NOT_READY.png'));replay,_,_=compose(j['arm_complete_rigid']['rotation_deg']);replaydiff=np.any(np.array(replay)!=existing,2);assert replaydiff.sum()==0, int(replaydiff.sum())
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
results={'source_commit':'e93afc911566e35ad5b1c0fb0caa1494bbf481f1','status':'ZERO_CALL_COMPARISON_ONLY_NOT_ART_NOT_READY','new_native_calls':0,'existing_short_step_replay_RGBA_changed_pixels':int(replaydiff.sum()),'registration_unchanged':j['registration_unchanged'],'angles':{}}
ims=[];details=[]
for deg in [10,14,18]:
 im,ar,ch=compose(deg);name=f'angle_{deg:02d}_PREPOSITION_NOT_ART.png';im.save(O/name);ar.save(O/f'angle_{deg:02d}_complete_far_arm_original_pixels.png');b=np.array(im);change=np.any(b!=existing,2);below=change& (np.indices(change.shape)[0]>=625)
 assert below.sum()==0
 results['angles'][str(deg)]={'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest(),'native_chain':ch.tolist(),'world_chain':(ch*s+T).tolist(),'pixels_changed_vs_current':int(change.sum()),'changes_at_y625_or_below':int(below.sum()),'head_and_near_arm_hard_domain_changed_pixels':int(np.any(b[hard]!=a[hard],1).sum()),'source_arm_proxy_segment_lengths_unchanged':True,'new_art_generated':False}
 bg=Image.new('RGBA',size,'#dde2e7');bg.alpha_composite(im);ims.append(bg.convert('RGB'));details.append(bg.convert('RGB').crop((825,290,1050,635)))
sheet=Image.new('RGB',(1500,1020),'white');dr=ImageDraw.Draw(sheet)
for i,(im,deg) in enumerate(zip(ims,[10,14,18])):
 q=im.crop((550,0,1100,1080));q=q.resize((490,962),Image.Resampling.LANCZOS);sheet.paste(q,(i*500+5,48));dr.text((i*500+12,10),f'{deg} deg / same arm length / NOT ART',font=font,fill='black')
sheet.save(O/'ANGLES_10_14_18_actual_original_pixel_comparison.jpg',quality=98)
sheet=Image.new('RGB',(1350,740),'white');dr=ImageDraw.Draw(sheet)
for i,(im,deg) in enumerate(zip(details,[10,14,18])):
 q=im.resize((450,690),Image.Resampling.NEAREST);sheet.paste(q,(i*450,40));dr.text((i*450+12,10),f'{deg} deg sleeve/elbow/jade',font=font,fill='black')
sheet.save(O/'ANGLES_10_14_18_sleeve_elbow_jade_closeup.png')
(O/'ANGLE_CHECKS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False,indent=2))
