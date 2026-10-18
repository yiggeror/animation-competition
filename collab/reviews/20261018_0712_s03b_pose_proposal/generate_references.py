import json, math, hashlib, argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--master', default='collab/reviews/20261018_0428_s03_keypose_candidates/originals/S03_grandma_k07_F079_t3.30.png')
p.add_argument('--font', default='assets/fonts/NotoSansSC-VF.ttf')
args = p.parse_args()
OUT = ROOT
OUT.mkdir(exist_ok=True)
(OUT/'skeleton').mkdir(exist_ok=True)
MASTER = Path(args.master)
im = Image.open(MASTER).convert('RGBA')
font = ImageFont.truetype(args.font, 23)
small = ImageFont.truetype(args.font, 19)
S = np.array([635.,505.,0.]); E = np.array([467.,718.,0.]); W0 = np.array([335.,730.,165.])
L1 = float(np.linalg.norm(E-S)); L2 = float(np.linalg.norm(W0-E))
starts = [0,4,6,8,10,12,15,17,19,22,25,28,32,38]
holds = [4,2,2,2,2,3,2,2,3,3,3,4,6,10]
wrist = [(335,730),(390,686),(500,610),(605,535),(660,495),(681,486),(678,492),(660,519),(628,558),(595,603),(562,639),(540,663),(527,678),(525,680)]
angles = [0,9,35,65,78,80,80,74,60,46,34,26,20,18]
notes = ['收回被拒的瓜前，看自己手中瓜；保持托持','开始抬腕，肘仍低；眼跟瓜','抬送中间态；嘴开始张','继续向嘴靠近；肘内收不翻','最后接近；嘴迎向瓜，未咬','同一瓜尖贴唇；含住，尚无缺口','合嘴咬下，缺口首次出现；开始撤瓜','瓜离开嘴；一侧腮轻鼓','嚼第一下；手缓慢落，嘴闭','嚼第二下；下巴微落后合','嚼第三下；两腮转移，眼皮开始垂','眼神移向画面左侧别处，不摆头','眼皮半垂看别处；嚼势收尾','淡淡一笑“随你”，停10帧']
anchors = {'A_left_basin_rim':[558,850], 'B_right_basin_rim':[1118,850], 'H_first_button':[838,550]}
mouth = [754.,376.]
base_rig={'wrist':[335.,730.], 'palm':[265.,741.], 'tip':[239.,639.], 'rind_left':[215.,711.], 'rind_right':[337.,698.], 'rind_bottom':[282.,747.]}

def transform(pt, w, deg):
    v=np.array(pt)-np.array(base_rig['wrist']);a=math.radians(deg)
    return [float(w[0]+v[0]*math.cos(a)-v[1]*math.sin(a)),float(w[1]+v[0]*math.sin(a)+v[1]*math.cos(a))]

def solve(w):
    T=np.array([*w,165.]);v=T-S;d=float(np.linalg.norm(v));u=v/d
    assert abs(L1-L2)<d<L1+L2
    a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(L1*L1-a*a)
    p=max(0,min(1,(730-w[1])/244));D=np.array([467+70*p,718-80*p,0.])
    b=D-S-np.dot(D-S,u)*u;b/=np.linalg.norm(b)
    return S+a*u+h*b,T

keys=[]; diagrams=[]
for i,(fr,hold,w,angle,note) in enumerate(zip(starts,holds,wrist,angles,notes),1):
    el,wr=solve(w);rig={k:transform(v,w,angle) for k,v in base_rig.items()}
    key={'id':f'd{i:02d}','f':fr,'hold':hold,'t':fr/24,'note':note,'head_rot':0,'shoulder_lift':0,'shoulder_xyz':S.tolist(),'elbow_xyz':el.tolist(),'wrist_xyz':wr.tolist(),'wrist_xy':list(w),'hand_fruit_rotation_deg':angle,'hand_fruit_rigid_points':rig,'mouth_xy':mouth,'bite_present':i>=7,'bite_local_center':base_rig['tip'],'bite_radius':19,'construction_lengths':[L1,L2]}
    keys.append(key)
    canvas=Image.new('RGB',(im.width,im.height+125),'white'); base=Image.new('RGBA',im.size,'white');faded=im.copy();faded.putalpha(faded.getchannel('A').point(lambda x:int(x*.22)));base.alpha_composite(faded);canvas.paste(base.convert('RGB'),(0,0));d=ImageDraw.Draw(canvas)
    # The diagram is an anatomical construction guide, never a final character frame.
    def line(points,col,width=6):d.line([tuple(p[:2]) for p in points],fill=col,width=width)
    def point(p,label,col):
        x,y=p[:2];d.ellipse((x-7,y-7,x+7,y+7),fill=col);d.text((x+10,y-27),label,font=small,fill=col)
    line([(837,797),(835,511),(813,422)],'#777777',6)
    line([S,el,wr],'#c23a39',8)
    for p,label in [(S,'肩区*'),(el,'肘'),(wr,'腕')]:point(p,label,'#b62e2e')
    line([(1035,500),(1170,765),(1060,790),(989,785)],'#527ab5',6)
    point((835,265),'头心约','#565656');d.ellipse((715,352,795,391),outline='#a6478d',width=3)
    point(mouth,'唇接触点','#a6478d')
    line([rig['wrist'],rig['palm']],'#e19019',10);point(rig['palm'],'掌托','#b67413')
    poly=[rig['tip'],rig['rind_left'],rig['rind_bottom'],rig['rind_right'],rig['tip']]
    line(poly,'#248a40',5)
    if i>=7:
        x,y=rig['tip'];r=19;d.ellipse((x-r,y-r,x+r,y+r),fill='white',outline='#be4d4d',width=3)
        d.text((x+22,y-15),'缺口（透出后层）',font=small,fill='#be4d4d')
    else:point(rig['tip'],'瓜尖','#248a40')
    for name,p in anchors.items():
        x,y=p;d.line((x-13,y,x+13,y),fill='#168249',width=4);d.line((x,y-13,x,y+13),fill='#168249',width=4)
        d.text((x-30,y+16),name.split('_')[0],font=small,fill='#168249')
    y=im.height+5
    d.text((20,y),f'S03b d{i:02d}  F{fr:02d}–{fr+hold-1:02d}  停{hold}帧  {note}',font=font,fill='#222222')
    d.text((20,y+39),'红：固定长度3D构造的投影；橙绿：同一手/瓜刚体旋转。不是最终人物图。',font=small,fill='#444444')
    d.text((20,y+69),'*肩/肘是遮挡下人工估计；z=165是透视构造，非照片测量。脸与衣纹不按代码小人换形。',font=small,fill='#555555')
    canvas.save(OUT/'skeleton'/f'd{i:02d}_f{fr:02d}.jpg',quality=91)
    diagrams.append(canvas)

spec={'shot':'S03b','fps':24,'total_frames':48,'reference_source_commit':'a5aa5a922f3ad63e501aa36421cd8b01aab5a632','request_source_commit':'673a9fb450693cee7abceea0b3d9375980cac6e7','master':'collab/reviews/20261018_0428_s03_keypose_candidates/originals/S03_grandma_k07_F079_t3.30.png','master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'canvas':[1670,941],'anchors':anchors,'measurement_note':'k07人工二维估计肩(635,505)±25、肘(467,718)±15、腕(335,730)±10；二维投影上臂271.28/前臂132.54。不能从单张遮挡图测真实3D骨长。','construction_note':'固定3D上臂271.2803/前臂211.6436等效px；母版腕深度165为明确构造假设。逐态只改变腕目标与连续肘平面，不改骨长。投影长度可缩短。与原S18二维工具不同，不可把该z假设称实测。','master_joints_xyz':{'shoulder':S.tolist(),'elbow':E.tolist(),'wrist':W0.tolist()},'base_hand_fruit_rig':base_rig,'mouth_contact_xy':mouth,'keys':keys,'timelineFrames':[[f,i] for i,f in enumerate(starts)]}
(OUT/'S03b.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
tw,th=417,267;sheet=Image.new('RGB',(4*tw,4*th),'#dddddd')
for i,pic in enumerate(diagrams):sheet.paste(pic.resize((tw,th)),((i%4)*tw,(i//4)*th))
sheet.save(OUT/'skeleton_sheet.jpg',quality=94)
contact=Image.new('RGB',(2220,590),'white');dc=ImageDraw.Draw(contact)
for col,idx in enumerate([0,5,7]):
    contact.paste(diagrams[idx].crop((160,300,900,800)),(col*740,0));dc.text((col*740+16,514),f'd{idx+1:02d}  '+['掌心托瓜皮','瓜尖贴唇，未咬','已咬缺口，手瓜一起撤开'][col],font=font,fill='#222222')
dc.text((16,554),'同尺寸固定裁窗，仅为接触参考示意；不是真人照片，不是可直接接景的绘画。',font=small,fill='#555555')
contact.save(OUT/'contact_reference.jpg',quality=94)
errors=[]
for k in keys:
    s=np.array(k['shoulder_xyz']);e=np.array(k['elbow_xyz']);w=np.array(k['wrist_xyz']);r=k['hand_fruit_rigid_points']
    errors.extend([abs(np.linalg.norm(e-s)-L1),abs(np.linalg.norm(w-e)-L2)])
    for a,b in [('wrist','palm'),('palm','tip'),('wrist','tip')]:errors.append(abs(math.dist(r[a],r[b])-math.dist(base_rig[a],base_rig[b])))
assert sum(holds)==48 and max(errors)<1e-8
tests={'frames':48,'reference_count':14,'new_image_generation_calls':0,'max_bone_and_rigid_distance_error_px':max(errors),'d06_unbit_tip_to_mouth_distance_px':math.dist(keys[5]['hand_fruit_rigid_points']['tip'],mouth),'boundary_status':'pose proposal awaits Opus review; no generated paintings yet','not_claimed':'Fixed 3D construction does not prove visual anatomy or model obedience; all paintings need actual visual review.'}
(OUT/'checks.json').write_text(json.dumps(tests,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(tests,ensure_ascii=False,indent=2))
