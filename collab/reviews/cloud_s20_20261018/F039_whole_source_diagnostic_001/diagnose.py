"""Zero-call whole-native039 registration; no per-hand registration or old-palm paste."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2];F=PACK/'B04_B05_generation_002/F039'
source=F/'raw_original.png';A=np.array(Image.open(source).convert('RGBA'));T=np.array(Image.open(F/'inputs/01_unique_corrected_F039_target.png').convert('RGBA'));BAD=np.array(Image.open(F/'S20_F039_candidate.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));assert hashlib.sha256(source.read_bytes()).hexdigest()=='c3607005ebde263dda1ea9bc83016ba6bd39ec34b9a67b54ca9cfa7cadc12b11'
def support(img,box):
 x0,y0,x1,y1=box;m=img[y0:y1,x0:x1,3]>180;rows=np.flatnonzero(m.sum(1)>=3);y=int(rows[-1]);ys,xs=np.where(m&(np.arange(m.shape[0])[:,None]>=y-2));return np.array([x0+float(xs.mean()),y0+float(ys.mean())])
foot=support(A,(485,850,620,935));goal=support(T,(530,850,625,935));far=support(A,(620,830,750,930));far_goal=support(T,(625,830,705,911))
# Hidden pelvis and shoulder centers are construction estimates, not visible bone measurements.
hip=np.array([584.,518.]);hip_goal=np.array([607.225,558.125]);shoulders=np.array([[518.,348.],[623.,342.]]);shoulders_goal=np.array([[564.,382.],[654.,387.]])
center=shoulders.mean(0);center_goal=shoulders_goal.mean(0);src=np.array([hip-foot,center-foot]);dst=np.array([hip_goal-goal,center_goal-goal]);weights=np.array([.6,1.0]);z=src[:,0]+1j*src[:,1];w=dst[:,0]+1j*dst[:,1];c=(weights*w*np.conj(z)).sum()/(weights*np.abs(z)**2).sum();a,b=float(c.real),float(c.imag);Q=np.array([[a,-b],[b,a]]);translation=goal-Q@foot;scale=abs(c);angle=math.atan2(b,a)
def apply(points):return np.asarray(points)@Q.T+translation
M=np.column_stack((Q,translation));inv=np.linalg.inv(Q);pil_inv=tuple(np.column_stack((inv,-inv@translation)).ravel())

def axes(img,xrange):
 r,g,bl=img[:,:,:3].astype(float).transpose(2,0,1);wood=(img[:,:,3]>180)&(r>110)&(g>65)&(r>g+10)&(g>bl+10)&(bl<g*.76);samples=[[],[]]
 for x in xrange:
  ys=np.flatnonzero(wood[:,x]&(yy[:,x]>335)&(yy[:,x]<456))
  if len(ys)<4:continue
  cut=int(np.argmax(np.diff(ys)))+1
  if cut==0 or cut==len(ys) or ys[cut]-ys[cut-1]<10:continue
  samples[0].append([x,float(ys[:cut].mean())]);samples[1].append([x,float(ys[cut:].mean())])
 out=[]
 for v in samples:
  p=np.array(v);assert len(p)>20;pfit=np.polyfit(p[:,0],p[:,1],1);out.append({'slope':float(pfit[0]),'intercept':float(pfit[1]),'RMS_px':float(np.sqrt(np.mean((p[:,1]-np.polyval(pfit,p[:,0]))**2)))})
 return out,wood
native,wood=axes(A,range(802,851));old_axes,_=axes(T,range(805,851))
clamps=np.array([[735,native[0]['slope']*735+native[0]['intercept']],[774,native[1]['slope']*774+native[1]['intercept']]])
new_clamps=apply(clamps)
# One intact native person component. Hands/wrists remain in the same source layer.
components,_=label((A[:,:,3]>100)&(xx<865));person_id=int(components[500,570]);assert person_id>0;native_mask=binary_dilation(components==person_id,iterations=2)&(A[:,:,3]>0)
for x,y in [[735,350],[773,411],[700,360],[750,419]]:assert native_mask[y,x]
# Preserve both original real shafts in that same layer, including their ends beyond x865.
for q in native:
 dist=np.abs(yy-q['slope']*xx-q['intercept'])/np.hypot(1,q['slope']);shaft=wood&(dist<4.5)&(xx>=790)&(xx<910)&(yy>350)
 native_mask|=binary_dilation(shaft,iterations=1)&(A[:,:,3]>0)
layer=np.zeros_like(A);layer[native_mask]=A[native_mask];registered=np.array(Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,pil_inv,Image.Resampling.BICUBIC))

# Test a SINGLE rigid transform of the old039 two-shaft layer, with no scaling.
# New contact stations may slide along a rigid shaft; palms are never moved to old stations.
theta=float(np.mean([math.atan(q['slope'])+angle-math.atan(o['slope']) for q,o in zip(native,old_axes)]));R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);old_points=np.array([[740,old_axes[0]['slope']*740+old_axes[0]['intercept']],[765,old_axes[1]['slope']*765+old_axes[1]['intercept']]])
normals=[];directions=[]
for q in old_axes:
 u=np.array([1,q['slope']]);u/=np.linalg.norm(u);u=R@u;directions.append(u);normals.append([-u[1],u[0]])
N=np.array(normals);rotated_old=old_points@R.T;rt=np.linalg.solve(N,np.array([N[i]@(new_clamps[i]-rotated_old[i]) for i in range(2)]));shaftM=np.column_stack((R,rt));trial=[]
for i,(x0,x1) in enumerate([(650,884),(630,862)]):
 o=old_axes[i];ends=np.array([[x0,o['slope']*x0+o['intercept']],[x1,o['slope']*x1+o['intercept']]])@R.T+rt;u=np.array(directions[i]);actual_angle=math.atan(native[i]['slope'])+angle;trial.append({'role':['T_H','T_S'][i],'new_clamp_px':new_clamps[i].tolist(),'transverse_residual_px':float(abs(N[i]@(new_clamps[i]-rotated_old[i]-rt))),'station_slide_px':float(u@(new_clamps[i]-rotated_old[i]-rt)),'within_same_finite_shaft':bool(0<(new_clamps[i]-ends[0])@u<np.linalg.norm(ends[1]-ends[0])),'angle_vs_native_deg':math.degrees(math.atan2(u[1],u[0])-actual_angle),'estimated_edge_difference_over_36px_grip':float(18*abs(math.sin(math.atan2(u[1],u[0])-actual_angle))),'ends_px':ends.tolist()})

# Existing grandmother remains a fixed comparison plate; no code people are drawn.
gc,_=label((A[:,:,3]>100)&(xx>=865));gids={int(gc[500,1100]),int(gc[400,920])};gids.discard(0);gm=binary_dilation(np.isin(gc,list(gids)),iterations=2)&(A[:,:,3]>0);G=np.zeros_like(A);G[gm]=A[gm]
reg=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];hi=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(hi)
for role in ['C_N','C_B']:
 q=reg[role];pts=[tuple(v*4 for v in q['shaft_tip_master_px']),(952*4,(q['slope']*952+q['intercept'])*4)];d.line(pts,fill=(103,80,52,255),width=16);d.line(pts,fill=(178,139,82,255),width=10)
base=Image.alpha_composite(hi.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));result=Image.alpha_composite(base,Image.fromarray(registered));result.save(P/'F039_registered_native_diagnostic.png')
# Actual rigid-pair trial: remove only external native prop pixels, never a wrist
# or hand, then put the one tested old shaft layer behind the same native person.
human=Image.new('L',(W,H));hd=ImageDraw.Draw(human)
for points in [[(430,115),(645,115),(655,332),(650,456),(707,684),(680,709),(748,895),(748,935),(480,935),(480,848),(495,708),(430,674),(511,456),(470,390),(430,365)],[(530,336),(684,338),(711,329),(729,322),(748,326),(765,340),(766,365),(750,379),(710,382),(682,389),(536,386)],[(634,384),(685,399),(739,403),(750,389),(769,380),(789,386),(801,403),(800,426),(784,440),(750,443),(685,453),(650,435)]]:hd.polygon(points,fill=255)
human=np.array(human)>0;prop_band=np.zeros((H,W),bool)
for q in native:prop_band|=(np.abs(yy-q['slope']*xx-q['intercept'])/np.hypot(1,q['slope'])<6)&(xx>665)&(yy>330)
remove=native_mask&prop_band&~human;person_layer=layer.copy();person_layer[remove]=0
for x,y in [[735,350],[773,411],[700,360],[750,419]]:assert np.array_equal(person_layer[y,x],A[y,x])
regperson=Image.fromarray(person_layer).transform((W,H),Image.Transform.AFFINE,pil_inv,Image.Resampling.BICUBIC)
pair=Image.new('RGBA',(W*4,H*4));pd=ImageDraw.Draw(pair)
for q in trial:
 pts=[tuple(v*4 for v in p) for p in q['ends_px']];pd.line(pts,fill=(103,80,52,255),width=16);pd.line(pts,fill=(178,139,82,255),width=10)
trial_base=Image.alpha_composite(hi.resize((W,H),Image.Resampling.LANCZOS),pair.resize((W,H),Image.Resampling.LANCZOS));trial_base=Image.alpha_composite(trial_base,Image.fromarray(G));trial_result=Image.alpha_composite(trial_base,regperson);trial_result.save(P/'F039_registered_rigid_pair_trial.png')

checks={}
for name,s,t in [('support',foot,goal),('pelvis_estimate',hip,hip_goal),('shoulder_center_estimate',center,center_goal),('far_support_check_only',far,far_goal),('visible_waist_check_only',[583,458],[608,505])]:
 p=apply(s);checks[name]={'source':np.asarray(s).tolist(),'target':np.asarray(t).tolist(),'registered':p.tolist(),'residual_vector_px':(p-t).tolist(),'residual_norm_px':float(np.linalg.norm(p-t))}
shaft_ok=all(q['within_same_finite_shaft'] and q['estimated_edge_difference_over_36px_grip']<1.5 for q in trial)
meta={'status':'ZERO_CALL_WHOLE_SOURCE_DIAGNOSTIC_NOT_F039_ACCEPTANCE','new_image_calls':0,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'complete_child_one_similarity_transform':{'scale':scale,'screen_clockwise_degrees':math.degrees(angle),'matrix_source_to_registered_2x3':M.tolist(),'translation_px':translation.tolist(),'fit':'support sole fixed exactly; pelvis and shoulder-axis center weighted fit; no hand in the fit','hidden_joint_estimate_uncertainty_px':12,'per_hand_registration':False,'old_palm_paste':False,'source_body_or_head_redraw':False,'mirroring':False,'nonuniform_scaling':False},'anchors':checks,'native_clamps_source_px':clamps.tolist(),'native_clamps_registered_px':new_clamps.tolist(),'clamp_selection':'source wood axis through each original closed hand; manual along-axis x, approximate +/-3px; not old grip coordinates','native_shaft_fits':native,'old039_shaft_fits':old_axes,'same_two_shaft_rigid_layer_test':{'scale':1,'rotation_degrees':math.degrees(theta),'matrix_2x3':shaftM.tolist(),'transverse_contact_fit_only_not_puppet_scene_signoff':True,'fits_native_grip_corridors':shaft_ok,'shafts':trial},'body_diagnosis':'Native complete arms/palms survive one whole-body registration; no duplicated hands or wrist transplant. Far support differs from the old fixed-foot target and needs director judgment; this diagnostic does not force it to match.','head_neck_gap':'Original complete head/neck retained, still right profile. Required curtain-facing intermediate head direction is NOT passed; any later correction must redraw the complete head/neck only after body decision.','next_generation_authorized_here':False}
(P/'uniform_transform_and_clamps.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
meta['actual_rigid_pair_trial']={'file':'F039_registered_rigid_pair_trial.png','native_human_one_transform_unchanged':True,'native_external_prop_pixels_removed_only':int(remove.sum()),'old_palms_pasted':False,'per_hand_transform':False,'G_plate':'original039 raw; fixed in place, complete open bareR included','not_a_final_scene_puppet_registration':True};(P/'uniform_transform_and_clamps.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')

fontpath=ROOT/'assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(str(fontpath),18);small=ImageFont.truetype(str(fontpath),16);title=ImageFont.truetype(str(fontpath),23)
def gray(im):b=Image.new('RGBA',im.size,'#bdc1c4');b.alpha_composite(im);return b.convert('RGB')
window=(420,100,1030,940);board=Image.new('RGB',(1260,1270),'#eef0f2');D=ImageDraw.Draw(board);D.text((15,8),'039零调用源诊断｜全孩子一次统一注册，保留原生双臂双掌',font=title,fill='#233540')
D.text((15,48),'旧硬回贴：已退回',font=font,fill='#a43a35');D.text((650,48),'完整源统一注册＋同一刚性签层试接',font=font,fill='#185e55')
board.paste(gray(Image.fromarray(BAD)).crop(window),(15,80));board.paste(gray(trial_result).crop(window),(650,80));D=ImageDraw.Draw(board)
for name,col in [('support','#1a826e'),('pelvis_estimate','#9c5895'),('shoulder_center_estimate','#286d9d')]:
 q=checks[name];x,y=q['registered'];sx=650+x-window[0];sy=80+y-window[1];D.ellipse((sx-5,sy-5,sx+5,sy+5),fill=col,outline='white',width=1)
for x,y in apply(shoulders):D.ellipse((650+x-window[0]-3,80+y-window[1]-3,650+x-window[0]+3,80+y-window[1]+3),fill='#286d9d')
# Contact inset: native brown rods remain intact; dashed teal is the same OLD rigid pair test.
close=gray(trial_result).crop((680,330,965,500)).resize((570,340));cd=ImageDraw.Draw(close)
for tr in trial:
 e=np.array(tr['ends_px']);p0=(e[0]-[680,330])*2;p1=(e[1]-[680,330])*2;dist=np.linalg.norm(p1-p0)
 for v in np.arange(0,dist,12):
  a0=p0+(p1-p0)*(v/dist);a1=p0+(p1-p0)*(min(v+6,dist)/dist);cd.line([tuple(a0),tuple(a1)],fill='#009e83',width=2)
for x,y in new_clamps:
 x=(x-680)*2;y=(y-330)*2;cd.ellipse((x-5,y-5,x+5,y+5),outline='#015bab',width=2)
board.paste(close,(650,930));D=ImageDraw.Draw(board)
texts=[f'人：统一s={scale:.6f}，旋转{math.degrees(angle):+.3f}°',f'统一平移=({translation[0]:+.3f}, {translation[1]:+.3f})px',f'骨盆估点残差{checks["pelvis_estimate"]["residual_norm_px"]:.1f}px；肩轴中心{checks["shoulder_center_estimate"]["residual_norm_px"]:.1f}px',f'远脚相对原target差{checks["far_support_check_only"]["residual_norm_px"]:.1f}px，未强拉齐',f'两签共用刚性变换：s=1，旋转{math.degrees(theta):+.3f}°',f'真实握廊试接：{"可行" if shaft_ok else "未通过"}；青虚线=同一旧签层试接', '右侧脸仍在，头颈转幕表演未通过。', '没有旧掌回贴、逐手配准或新生图。']
for i,line in enumerate(texts):D.text((15,937+i*34),line,font=small,fill='#a43a35' if i==6 else '#293c48')
board.save(P/'F039_one_comparison.png');print(json.dumps({'body_scale':scale,'body_rotation':math.degrees(angle),'translation':translation.tolist(),'anchor_residuals':{k:v['residual_norm_px'] for k,v in checks.items()},'rigid_pair_fits_native_corridors':shaft_ok,'pair_rotation':math.degrees(theta),'pair_test':trial},ensure_ascii=False))
