from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
R=Path('astra_s07_xiaoman_release_20261018_1110');U=Image.open(R/'sources/anim_07_xiaoman_flop.png').convert('RGB');B=Image.open(R/'sources/bg_01_room_wide_base_v2_draft.png').convert('RGB');F='/workspace/scratch/f060b5601755/astra_s03b_painted_pilot_20261018/refs/NotoSansSC-VF.ttf'
def ft(n):return ImageFont.truetype(F,n)
def t(d,p,s,n=22,c='#17384a'):d.text(p,s,font=ft(n),fill=c)
def dot(d,p,c,r=5):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=c,outline='white',width=1)
def dash(d,a,b,c='#ac7519',w=3):
 L=math.dist(a,b)
 for i in range(0,int(L),18):
  q=i/L;r=min(1,(i+9)/L);d.line((a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q,a[0]+(b[0]-a[0])*r,a[1]+(b[1]-a[1])*r),fill=c,width=w)
s=.22;tx,ty=350.72,526.76
C=lambda p:[p[0]*s+tx,p[1]*s+ty]
pts={'head_center':[635,610],'head_envelope_radii':[34,35],'head_back_contact':C([1411,493]),'near_scapula':C([1187,621]),'near_shoulder_proxy':C([1174,571]),'far_shoulder_proxy':C([985,421]),'hip_hidden_construct':[532,657],'near_knee_hidden_construct':[480,665],'far_knee_hidden_construct':[485,638],'near_heel':C([222,780]),'far_heel':C([211,648]),'near_elbow_support':[647,676],'far_elbow':C([858,397]),'far_wrist':C([731,326])}
ang=math.radians(-30);pts['near_wrist']=[647+33*math.cos(ang),676+33*math.sin(ang)];pts['near_palm']=[pts['near_wrist'][0]+11*math.cos(ang),pts['near_wrist'][1]+11*math.sin(ang)]
# Core support and finger-clearance are proposals, not proof from the unedited mother.
new={'status':'proposal_for_refreeze_not_production','scale_reference_only':{'uniform_scale':s,'translation':[tx,ty],'note':'Whole-source uniform diagnostic registration only. New supine drawing follows S01 fixed role size and turnaround; old mother pixels are not final silhouette.'},'points_world':pts,'projected_construction':{'head_envelope':[68,70],'near_upper_arm':math.dist(pts['near_shoulder_proxy'],pts['near_elbow_support']),'near_forearm':33,'near_hand_axis':11,'near_thigh':math.dist(pts['hip_hidden_construct'],pts['near_knee_hidden_construct']),'near_shin_to_heel':math.dist(pts['near_knee_hidden_construct'],pts['near_heel']),'far_upper_arm_source_projection':math.dist(pts['far_shoulder_proxy'],pts['far_elbow']),'far_forearm_source_projection':math.dist(pts['far_elbow'],pts['far_wrist'])},'arm_plan':{'F039':{'near_elbow_support':[647,676],'forearm_angle_deg':-30,'forearm_length':33},'F043':{'near_elbow_support':[647,676],'forearm_angle_deg':-48,'forearm_length':33},'F046':{'near_elbow_support':[647,676],'forearm_angle_deg':-15,'forearm_length':33},'F049':'same recovery arm with glance; actual intermediate may be added if gap visible','F053':'hand/forearm settles to mat; elbow remains consistent; next wide reuses state'},'phone_landing_proposal':{'center':[656,660],'long_axis_length':21,'depth_projected':7,'thickness':2,'screen':'black, up','status':'F008 contact target only; first generated F000 strict-side hand must agree; ensure supine forearm lifts clear in depth, no intersection.'},'change_scope_vs_old_supine':{'not_head_only':True,'old_head_back':[683.98,648.74],'new_head_back':pts['head_back_contact'],'old_near_scapula':[643.66,671.78],'new_near_scapula':pts['near_scapula'],'old_hip':[578.32,666.56],'new_hip':pts['hip_hidden_construct'],'old_near_heel':[469.96,700.4],'new_near_heel':pts['near_heel'],'old_far_heel':[467.98,676.64],'new_far_heel':pts['far_heel'],'old_arm_centerline':[27,26],'new_near_arm':[math.dist(pts['near_shoulder_proxy'],pts['near_elbow_support']),33],'note':'Torso, sleeves, skirt, leg perspective, shoe contacts, and both arm paths redrawn together. Hidden hips/knees remain constructions. No local head enlargement or anisotropic deformation.'},'review_needed':['New strict-side/scene-view profile identity and body thickness','Head-size continuity to S01/F000 at same scene scale','Elbow support and raised forearm depth clear of face/phone','Near shoe outline fits mat foreground border, not just heel point','F039 all contact points support actual flesh/cloth shape; bone center not support surface']}
(R/'geometry/supine_refreeze_proposal.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
# Context plate and detailed reference, no code body used.
def panel(label,draw_lines=False):
 base=Image.blend(B,Image.new('RGB',B.size,'white'),.55);im=U.resize((round(U.width*s),round(U.height*s)),Image.Resampling.LANCZOS);base.paste(im,(round(tx),round(ty)))
 box=(330,555,730,735);out=base.crop(box).resize((1400,630),Image.Resampling.LANCZOS);d=ImageDraw.Draw(out);P=lambda p:((p[0]-box[0])*3.5,(p[1]-box[1])*3.5)
 if draw_lines:
  for a,b in [('near_shoulder_proxy','hip_hidden_construct'),('hip_hidden_construct','near_knee_hidden_construct'),('near_knee_hidden_construct','near_heel'),('hip_hidden_construct','far_knee_hidden_construct'),('far_knee_hidden_construct','far_heel')]:dash(d,P(pts[a]),P(pts[b]),'#6a7480',3)
  for a,b in [('far_shoulder_proxy','far_elbow'),('far_elbow','far_wrist')]:dash(d,P(pts[a]),P(pts[b]),'#ad751a',4)
  for a,b in [('near_shoulder_proxy','near_elbow_support'),('near_elbow_support','near_wrist'),('near_wrist','near_palm')]:d.line(P(pts[a])+P(pts[b]),fill='#087ba4',width=5)
  for k in ['head_back_contact','near_scapula','hip_hidden_construct','near_elbow_support','near_heel','far_heel']:dot(d,P(pts[k]),'#008457',7)
  h=P(pts['head_center']);rx,ry=34*3.5,35*3.5;d.ellipse((h[0]-rx,h[1]-ry,h[0]+rx,h[1]+ry),outline='#bd4250',width=3)
  for name in ['near_elbow_support','near_wrist','near_palm']:dot(d,P(pts[name]),'#087ba4',5)
  # stroke bounds; all beyond cheek to right in screen projection
  for a,col in [(-48,'#bc5b27'),(-15,'#9569b7')]:
   r=math.radians(a);w=[647+33*math.cos(r),676+33*math.sin(r)];p=[w[0]+11*math.cos(r),w[1]+11*math.sin(r)];dash(d,P(pts['near_elbow_support']),P(w),col,3);d.line(P(w)+P(p),fill=col,width=3)
  t(d,(20,20),'蓝=F039新近臂；棕/紫=两次扇风范围；红=同S01头包络；绿=接触候选',22)
 return out
board=Image.new('RGB',(1400,1500),'white');d=ImageDraw.Draw(board);t(d,(20,10),'新躺姿建议：共同角色尺度优先，整躯干/肢体/支撑一起重画',30)
board.paste(panel('raw'),(0,60));t(d,(20,706),'上：旧母源整体0.22 +(350.72,526.76)只作对照；不是局部放头，也不是新姿态已画成。',23)
board.paste(panel('new',True),(0,756));t(d,(20,1402),'下：近右肘席面(647,676)，近臂构造约45/33；手在脸右侧，远臂仍独立摊置。',23)
t(d,(20,1441),'肩胛/臀区/脚跟随整人重新落席；须再审肉厚、裙摆、鞋轮廓和手机，不以绿点代接触成图。',22,'#ad3843')
board.save(R/'reference/05_new_supine_refreeze_proposal.jpg',quality=95)
print(json.dumps(new['change_scope_vs_old_supine'],ensure_ascii=False,indent=2))
